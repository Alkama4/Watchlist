from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app import models, schemas


async def fetch_title_with_user_details(db: AsyncSession, title_id: int, user_id: int) -> schemas.TitleOut:
    # Fetch title with seasons and episodes
    result = await db.execute(
        select(models.Title)
        .where(models.Title.title_id == title_id)
        .options(
            selectinload(models.Title.seasons.and_(models.Season.season_number != 0))
                .selectinload(models.Season.episodes),
            selectinload(models.Title.genres)
                .selectinload(models.TitleGenre.genre)
        )
    )
    title = result.scalar_one_or_none()
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    
    # Fetch user-specific details
    user_title = await db.get(models.UserTitleDetails, {"user_id": user_id, "title_id": title_id})
        
    # Init user details if missing
    if not user_title:
        user_title = models.UserTitleDetails(user_id=user_id, title_id=title_id)
        db.add(user_title)

    # Update the last viewed timestamp
    user_title.last_viewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user_title)

    # Map the data
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

    return _build_title_out(
        title, 
        user_title, 
        season_details_map, 
        episode_details_map
    )


def _build_title_out(
    title: models.Title,
    user_title: Optional[models.UserTitleDetails],
    season_details_map: dict[int, models.UserSeasonDetails],
    episode_details_map: dict[int, models.UserEpisodeDetails],
) -> schemas.TitleOut:
    # Build a dict of attributes that exist on the SQLAlchemy instance
    title_data = {
        field: getattr(title, field)
        for field in schemas.TitleOut.model_fields
        if hasattr(title, field) and field not in {"genres", "user_details"}
    }

    # Create the Pydantic model (no genres yet)
    title_out = schemas.TitleOut.model_validate(title_data)

    # Populate the genre names
    title_out.genres = [
        schemas.GenreElement.model_validate(tg.genre, from_attributes=True)
        for tg in title.genres
    ]

    # Attach user details, season/episode details
    title_out.user_details = (
        schemas.UserTitleDetailsOut.model_validate(user_title, from_attributes=True)
        if user_title
        else None
    )

    for season in title_out.seasons:
        season.user_details = (
            schemas.UserSeasonDetailsOut.model_validate(
                season_details_map.get(season.season_id)
            )
            if season_details_map.get(season.season_id)
            else None
        )
        for episode in season.episodes:
            episode.user_details = (
                schemas.UserEpisodeDetailsOut.model_validate(
                    episode_details_map.get(episode.episode_id)
                )
                if episode_details_map.get(episode.episode_id)
                else None
            )

    return title_out
