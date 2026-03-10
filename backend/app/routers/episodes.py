from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.user_flags import set_episode_watch_count
from app.schemas import WatchCountIn
from app.models import User

router = APIRouter()


@router.put("/{episode_id}/watch_count")
async def update_episode_watch_count(
    episode_id: int,
    data: WatchCountIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_episode_watch_count(
        db=db,
        user_id=user.user_id,
        episode_id=episode_id,
        watch_count=data.watch_count
    )
    return {
        "episode_id": episode_id,
        "watch_count": data.watch_count,
        "in_library": True
    }
