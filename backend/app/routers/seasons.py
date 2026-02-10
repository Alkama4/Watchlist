from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.images import fetch_image_details
from app.schemas import (
    ImageListsOut
)
from app.models import (
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
