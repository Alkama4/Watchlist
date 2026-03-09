from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.schemas import (
    WatchCountIn
)
from app.models import (
    User,
    UserEpisodeDetails
)

router = APIRouter()


@router.put("/{episode_id}/watch_count")
async def set_season_image_preference(
    episode_id: int,
    data: WatchCountIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    print(data)
    print(data.watch_count)
    
    stmt = insert(UserEpisodeDetails).values(
        user_id=user.user_id,
        episode_id=episode_id,
        watch_count=data.watch_count,
        last_watched_at=now
    ).on_conflict_do_update(
        index_elements=["user_id", "episode_id"],
        set_={
            "watch_count": data.watch_count,
            "last_watched_at": now
        }
    )
    await db.execute(stmt)
    await db.commit()
    return {
        "episode_id": episode_id,
        "watch_count": data.watch_count
    }

    # TODO: Decide. Do we want to add the title to library here?
