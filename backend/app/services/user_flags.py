from fastapi import HTTPException
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


# ---------- GENERIC SETTERS ----------

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


# ---------- WATCH COUNTS ----------

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
        last_watched_at=now,
        in_library=True
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={
            "watch_count": watch_count,
            "last_watched_at": now,
            "in_library": True
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
    

async def set_season_watch_count(
    db: AsyncSession,
    user_id: int,
    season_id: int,
    watch_count: int
):
    now = datetime.now(timezone.utc)

    title_id = await db.scalar(
        select(Episode.title_id)
        .where(Episode.season_id == season_id)
        .limit(1)
    )

    if not title_id:
        raise HTTPException(400, "Couldn't find the parent title for the season.")

    title_stmt = insert(UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        last_watched_at=now,
        in_library=True
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={
            "last_watched_at": now,
            "in_library": True
        }
    )
    await db.execute(title_stmt)

    episode_ids = await db.scalars(
        select(Episode.episode_id)
        .where(
            Episode.season_id == season_id,
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


async def set_episode_watch_count(
    db: AsyncSession,
    user_id: int,
    episode_id: int,
    watch_count: int
):
    now = datetime.now(timezone.utc)

    title_id = await db.scalar(
        select(Episode.title_id)
        .where(Episode.episode_id == episode_id)
    )

    if not title_id:
        raise HTTPException(400, "Couldn't find the parent title for the episode.")

    title_stmt = insert(UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        last_watched_at=now,
        in_library=True
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={
            "last_watched_at": now,
            "in_library": True
        }
    )
    await db.execute(title_stmt)

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
