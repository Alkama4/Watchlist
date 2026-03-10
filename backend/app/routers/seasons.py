from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.images import fetch_image_details, set_user_image_choice
from app.services.user_flags import set_season_watch_count
from app.schemas import (
    ImageListsOut,
    ImagePreferenceIn,
    WatchCountIn
)
from app.models import (
    ImageType,
    User
)

router = APIRouter()


# ---------- SPECIFIC SEASON ----------

@router.get("/{season_id}/images", response_model=ImageListsOut)
async def get_all_season_images(
    season_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_data = await fetch_image_details(db=db, season_id=season_id, user_id=user.user_id)
    return image_data


@router.put("/{season_id}/images/{image_type}")
async def set_season_image_preference(
    season_id: int,
    image_type: ImageType,
    data: ImagePreferenceIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await set_user_image_choice(
        db=db,
        user_id=user.user_id,
        image_type=image_type,
        image_path=data.image_path,
        season_id=season_id
    )


# ---------- SET SEASON USER DETAILS ----------

@router.put("/{season_id}/watch_count")
async def update_season_watch_count(
    season_id: int,
    data: WatchCountIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_season_watch_count(
        db,
        user.user_id,
        season_id,
        watch_count=data.watch_count,
    )
    return {
        "season_id": season_id,
        "watch_count": data.watch_count,
        "in_library": True
    }
