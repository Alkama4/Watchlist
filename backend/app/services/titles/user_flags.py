from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone
from app.models import (
    TitleType,
    Title,
    Episode,
    UserTitleDetails,
    UserEpisodeDetails
)


async def set_user_title_value(
    db: AsyncSession,
    user_id: int,
    title_id: int,
    **flags: bool
):
    stmt = insert(UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        **flags
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_=flags
    )

    await db.execute(stmt)
    await db.commit()


async def set_title_watch_count(
    db: AsyncSession,
    user_id: int,
    title_id: int,
    watch_count: int
):
    now = datetime.now(timezone.utc)

    stmt = insert(UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        watch_count=watch_count,
        last_watched_at=now
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={
            "watch_count": watch_count,
            "last_watched_at": now
        }
    )

    await db.execute(stmt)

    title_type = await db.scalar(
        select(Title.title_type)
        .where(Title.title_id == title_id)
    )

    if title_type == TitleType.tv:
        episode_ids = await db.scalars(
            select(Episode.episode_id)
            .where(
                Episode.title_id == title_id,
                Episode.air_date <= now.date()
            )
        )

        for episode_id in episode_ids:
            ep_stmt = insert(UserEpisodeDetails).values(
                user_id=user_id,
                episode_id=episode_id,
                watch_count=watch_count,
                last_watched_at=now
            ).on_conflict_do_update(
                index_elements=["user_id", "episode_id"],
                set_={
                    "watch_count": watch_count,
                    "last_watched_at": now
                }
            )
            await db.execute(ep_stmt)

    await db.commit()
    