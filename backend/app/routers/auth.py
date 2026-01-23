from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError
from datetime import datetime, timedelta, timezone
from app import models
from app.dependencies import get_db
from app.security import hash_password, verify_password
from app.security import create_access_token, decode_access_token
from app.security import create_refresh_token, hash_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
from app.schemas import (
    UserIn,
    UserOut,
    UserUpdate,
    UserDelete,
    PasswordUpdate
)

router = APIRouter()
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


####### Endpoints #######

@router.post("/register", response_model=UserOut)
async def register(
    user: UserIn, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.User).filter(models.User.username == user.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = models.User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login")
async def login(
    user: UserIn, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(db_user.user_id)

    refresh_token = create_refresh_token()
    refresh_token_db = models.RefreshToken(
        user_id=db_user.user_id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(refresh_token_db)
    await db.commit()

    # Set HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # secure=True,       # True if using HTTPS
        samesite="lax",      # or "strict"
        max_age=60*60*24*REFRESH_TOKEN_EXPIRE_DAYS   # e.g., 7 days
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh(
    response: Response, 
    refresh_token: str = Cookie(None), 
    db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    token_hash = hash_refresh_token(refresh_token)

    result = await db.execute(
        select(models.RefreshToken).where(
            models.RefreshToken.token_hash == token_hash,
            models.RefreshToken.revoked_at.is_(None),
            models.RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # rotate token
    stored_token.revoked_at = datetime.now(timezone.utc)

    new_refresh = create_refresh_token()
    db.add(models.RefreshToken(
        user_id=stored_token.user_id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    ))

    access_token = create_access_token(stored_token.user_id)
    await db.commit()

    # set new cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        # secure=True,
        samesite="lax",
        max_age=60*60*24*7
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.RefreshToken).where(
            models.RefreshToken.user_id == current_user.user_id,
            models.RefreshToken.revoked_at.is_(None),
            models.RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.revoked_at = datetime.now(timezone.utc)
        db.add(token)
    await db.commit()

    # remove cookie
    response.delete_cookie("refresh_token")

    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def read_me(current_user = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
async def update_profile(
    update: UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.username = update.username
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me")
async def delete_account(
    response: Response,
    data: UserDelete,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )

    await db.delete(current_user)
    await db.commit()

    response.delete_cookie("refresh_token")

    return {"detail": "Account deleted successfully"}


@router.post("/me/password")
async def change_password(
    passwords: PasswordUpdate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(passwords.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    current_user.hashed_password = hash_password(passwords.new_password)
    db.add(current_user)
    await db.commit()

    return {"detail": "Password updated successfully"}
