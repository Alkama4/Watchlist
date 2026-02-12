from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.images import fetch_image_details, set_user_image_choice
from app.schemas import (
    ImageListsOut,
    ImagePreferenceIn
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

# @router.put("/{title_id}/watch_count")
# async def update_title_watch_count(
#     title_id: int,
#     data: TitleWatchCountIn,
#     user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     await set_title_watch_count(
#         db,
#         user.user_id,
#         title_id,
#         watch_count=data.watch_count,
#     )
#     return {
#         "title_id": title_id,
#         "watch_count": data.watch_count,
#         "in_library": True
#     }
