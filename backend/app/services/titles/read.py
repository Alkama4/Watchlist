from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app import models, schemas


async def fetch_title_with_user_details(db: AsyncSession, title_id: int, user_id: int) -> schemas.TitleOut:
    # Fetch title with seasons and episodes
    result = await db.execute(
        select(models.Title)
        .where(models.Title.title_id == title_id)
        .options(
            selectinload(models.Title.seasons.and_(models.Season.season_number != 0))
            .selectinload(models.Season.episodes)
        )
    )
    title = result.scalar_one_or_none()
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    # Fetch all user-specific details in bulk
    user_title = await db.get(models.UserTitleDetails, {"user_id": user_id, "title_id": title_id})
    
    season_ids = [s.season_id for s in title.seasons]
    episode_ids = [e.episode_id for s in title.seasons for e in s.episodes]

    season_details_map = {
        d.season_id: d
        for d in (await db.execute(
            select(models.UserSeasonDetails)
            .where(models.UserSeasonDetails.user_id == user_id)
            .where(models.UserSeasonDetails.season_id.in_(season_ids))
        )).scalars()
    }

    episode_details_map = {
        d.episode_id: d
        for d in (await db.execute(
            select(models.UserEpisodeDetails)
            .where(models.UserEpisodeDetails.user_id == user_id)
            .where(models.UserEpisodeDetails.episode_id.in_(episode_ids))
        )).scalars()
    }

    return build_title_out(title, user_title, season_details_map, episode_details_map)


def build_title_out(
    title: models.Title,
    user_title: Optional[models.UserTitleDetails],
    season_details_map: dict[int, models.UserSeasonDetails],
    episode_details_map: dict[int, models.UserEpisodeDetails],
) -> schemas.TitleOut:
    # Base TitleOut
    title_out = schemas.TitleOut.model_validate(title)

    # Attach user title details
    title_out.user_details = schemas.UserTitleDetailsOut.model_validate(user_title, from_attributes=True) if user_title else None

    # Attach user season and episode details
    for season in title_out.seasons:
        season.user_details = schemas.UserSeasonDetailsOut.model_validate(
            season_details_map.get(season.season_id)
        ) if season_details_map.get(season.season_id) else None

        for episode in season.episodes:
            episode.user_details = schemas.UserEpisodeDetailsOut.model_validate(
                episode_details_map.get(episode.episode_id)
            ) if episode_details_map.get(episode.episode_id) else None

    return title_out
