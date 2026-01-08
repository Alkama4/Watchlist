from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[schemas.UserSettingOut])
async def get_user_settings(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.UserSetting).where(models.UserSetting.user_id == current_user.user_id)
    )
    return result.scalars().all()


@router.put("/{key}", response_model=schemas.UserSettingOut)
async def update_user_setting(
    key: str,
    setting_update: schemas.UserSettingIn,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Make sure the setting exists
    base_setting = await db.get(models.Setting, key)
    if not base_setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    # Check if the user already has a value
    user_setting = await db.get(models.UserSetting, (current_user.user_id, key))
    if not user_setting:
        user_setting = models.UserSetting(
            user_id=current_user.user_id,
            key=key,
            value=setting_update.value
        )
    else:
        user_setting.value = setting_update.value

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)
    return user_setting
