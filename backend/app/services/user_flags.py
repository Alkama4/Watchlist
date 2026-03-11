from fastapi import HTTPException
from typing import Any
from sqlalchemy import select, update, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone
from app.models import (
    Season,
    TitleType,
    Title,
    Episode,
    UserTitleDetails,
    UserEpisodeDetails
)


# ---------- GENERIC SETTERS ----------

async def set_user_title_value(
    db: AsyncSession,
    user_id: int,
    title_id: int,
    **kwargs: Any
):
    stmt = insert(UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        **kwargs
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_=kwargs
    )

    await db.execute(stmt)


# ---------- WATCH COUNTS ----------

async def _sync_tv_title_watch_count(db: AsyncSession, user_id: int, title_id: int, now: datetime):
    """
    Recalculates the title's watch count based on released, non-Season-0 episodes.
    Matches the lowest watch count among those valid episodes.
    """
    # Use an Outer Join to catch episodes the user hasn't watched yet (watch_count = NULL -> 0)
    min_watch_stmt = (
        select(func.min(func.coalesce(UserEpisodeDetails.watch_count, 0)))
        .select_from(Episode)
        .join(Season, Episode.season_id == Season.season_id)
        .outerjoin(
            UserEpisodeDetails,
            (Episode.episode_id == UserEpisodeDetails.episode_id) &
            (UserEpisodeDetails.user_id == user_id)
        )
        .where(
            Episode.title_id == title_id,
            Episode.air_date <= now.date(),
            Season.season_number > 0
        )
    )
    
    min_count = await db.scalar(min_watch_stmt)
    min_count = min_count or 0  # Fallback to 0 if there are no valid episodes at all

    update_stmt = (
        update(UserTitleDetails)
        .where(
            UserTitleDetails.user_id == user_id,
            UserTitleDetails.title_id == title_id
        )
        .values(watch_count=min_count)
    )
    await db.execute(update_stmt)


async def set_title_watch_count(
    db: AsyncSession,
    user_id: int,
    title_id: int,
    watch_count: int
):
    now = datetime.now(timezone.utc)
    title_type = await db.scalar(select(Title.title_type).where(Title.title_id == title_id))

    if title_type == TitleType.movie:
        await set_user_title_value(
            db, 
            user_id, 
            title_id, 
            last_watched_at=now, 
            in_library=True,
            watch_count=watch_count
        )
    else:
        await set_user_title_value(
            db, 
            user_id, 
            title_id, 
            last_watched_at=now, 
            in_library=True,
            # Don't set watch_count here. Let "_sync_tv_title_watch_count" handle it.
        )

        ep_stmt = (
            select(Episode.episode_id)
            .join(Season, Episode.season_id == Season.season_id)
            .where(
                Episode.title_id == title_id,
                Episode.air_date <= now.date(),
                Season.season_number > 0
            )
        )
        episode_ids = list(await db.scalars(ep_stmt))

        if episode_ids:
            # Bulk upsert all valid episodes
            episodes_data = [
                {
                    "user_id": user_id, 
                    "episode_id": ep_id, 
                    "watch_count": watch_count, 
                    "last_watched_at": now
                }
                for ep_id in episode_ids
            ]
            ep_upsert_stmt = insert(UserEpisodeDetails).values(episodes_data).on_conflict_do_update(
                index_elements=["user_id", "episode_id"],
                set_={
                    "watch_count": watch_count,
                    "last_watched_at": now
                }
            )
            await db.execute(ep_upsert_stmt)

        # Sync title watch_count based on episode watch counts
        await _sync_tv_title_watch_count(db, user_id, title_id, now)

    await db.commit()


async def set_season_watch_count(
    db: AsyncSession,
    user_id: int,
    season_id: int,
    watch_count: int
):
    now = datetime.now(timezone.utc)

    title_id = await db.scalar(select(Season.title_id).where(Season.season_id == season_id))
    if not title_id:
        raise HTTPException(400, "Couldn't find the parent title for the season.")

    await set_user_title_value(
        db, 
        user_id, 
        title_id, 
        last_watched_at=now, 
        in_library=True
    )

    ep_stmt = select(Episode.episode_id).where(
        Episode.season_id == season_id,
        Episode.air_date <= now.date()
    )
    episode_ids = list(await db.scalars(ep_stmt))

    if episode_ids:
        # Bulk update episodes
        episodes_data = [
            {
                "user_id": user_id, 
                "episode_id": ep_id, 
                "watch_count": watch_count, 
                "last_watched_at": now
            }
            for ep_id in episode_ids
        ]
        ep_upsert_stmt = insert(UserEpisodeDetails).values(episodes_data).on_conflict_do_update(
            index_elements=["user_id", "episode_id"],
            set_={"watch_count": watch_count, "last_watched_at": now}
        )
        await db.execute(ep_upsert_stmt)

    # Sync title watch_count based on episode watch counts
    await _sync_tv_title_watch_count(db, user_id, title_id, now)
    
    await db.commit()


async def set_episode_watch_count(
    db: AsyncSession,
    user_id: int,
    episode_id: int,
    watch_count: int
):
    now = datetime.now(timezone.utc)

    title_id = await db.scalar(select(Episode.title_id).where(Episode.episode_id == episode_id))
    if not title_id:
        raise HTTPException(400, "Couldn't find the parent title for the episode.")

    await set_user_title_value(
        db, 
        user_id, 
        title_id, 
        last_watched_at=now, 
        in_library=True
    )

    ep_upsert_stmt = insert(UserEpisodeDetails).values(
        user_id=user_id,
        episode_id=episode_id,
        watch_count=watch_count,
        last_watched_at=now
    ).on_conflict_do_update(
        index_elements=["user_id", "episode_id"],
        set_={"watch_count": watch_count, "last_watched_at": now}
    )
    await db.execute(ep_upsert_stmt)

    # Sync title watch_count based on episode watch counts
    await _sync_tv_title_watch_count(db, user_id, title_id, now)

    await db.commit()
