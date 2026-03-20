from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.services.languages import get_user_language_context
from app.schemas import (
    EpisodeOut,
    GenreElement,
    AgeRatingElement,
    SeasonOut,
    UserEpisodeDetailsOut,
    UserSeasonDetailsOut,
    UserTitleDetailsOut,
    TitleOut,
    VideoAssetOut
)
from app.models import (
    Episode,
    Title,
    Season,
    TitleTranslation,
    SeasonTranslation,
    EpisodeTranslation,
    UserTitleDetails,
    UserSeasonDetails,
    UserEpisodeDetails,
    TitleGenre
)


async def fetch_title_with_user_details(db: AsyncSession, title_id: int, user_id: int) -> TitleOut:
    locale_ctx = await get_user_language_context(db=db, user_id=user_id, title_id=title_id)

    # Execute the "Mega Query"
    stmt = (
        select(Title)
        .where(Title.title_id == title_id)
        .options(
            # Load Title Translation & User Details
            selectinload(Title.translations.and_(
                TitleTranslation.iso_639_1 == locale_ctx.preferred_iso_639_1
            )),
            selectinload(Title.user_details.and_(UserTitleDetails.user_id == user_id)),
            selectinload(Title.genres).selectinload(TitleGenre.genre),
            selectinload(Title.age_ratings),
            selectinload(Title.video_assets),
            
            # Load Seasons + filtered children
            selectinload(Title.seasons.and_(Season.season_number != 0)).options(
                selectinload(Season.translations.and_(
                    SeasonTranslation.iso_639_1 == locale_ctx.preferred_iso_639_1
                )),
                selectinload(Season.user_details.and_(UserSeasonDetails.user_id == user_id)),
                
                # Load Episodes + filtered children
                selectinload(Season.episodes).options(
                    selectinload(Episode.translations.and_(
                        EpisodeTranslation.iso_639_1 == locale_ctx.preferred_iso_639_1
                    )),
                    selectinload(Episode.user_details.and_(UserEpisodeDetails.user_id == user_id)),
                    selectinload(Episode.video_assets)
                )
            )
        )
    )

    result = await db.execute(stmt)
    title = result.scalar_one_or_none()
    
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    # Handle User Title Logic
    user_title = title.user_details[0] if title.user_details else None
    if not user_title:
        user_title = UserTitleDetails(user_id=user_id, title_id=title_id)
        db.add(user_title)
    
    user_title.last_viewed_at = datetime.now(timezone.utc)
    await db.commit()

    return _build_title_out(title, locale_ctx)


def _build_title_out(title: Title, locale_ctx) -> TitleOut:
    # Map Title Base Fields
    title_dict = {
        field: getattr(title, field)
        for field in TitleOut.model_fields
        if hasattr(title, field) and field not in {"genres", "user_details", "seasons", "age_ratings", "video_assets"}
    }
    
    # Apply Title Translation fields
    translation = title.translations[0] if title.translations else None
    title_dict.update({
        k: v for k, v in vars(translation).items() 
        if k in TitleOut.model_fields and v is not None
    })

    # Apply Title User Details
    user_detail = title.user_details[0] if title.user_details else None
    title_dict["user_details"] = UserTitleDetailsOut.model_validate(user_detail) if user_detail else None
    
    # Map Genres, Ratings & Video Assets
    title_dict["genres"] = [GenreElement.model_validate(tg.genre, from_attributes=True) for tg in title.genres]
    title_dict["age_ratings"] = [AgeRatingElement.model_validate(r, from_attributes=True) for r in title.age_ratings]
    title_dict["video_assets"] = [
        VideoAssetOut.model_validate(va, from_attributes=True) for va in title.video_assets
    ] if title.video_assets else None

    title_dict["display_locale"] = locale_ctx.preferred_locale

    # Sort the seasons
    title.seasons.sort(key=lambda s: s.season_number)

    # Map Seasons
    seasons_out = []
    for s in title.seasons:
        s_dict = {
            field: getattr(s, field)
            for field in SeasonOut.model_fields
            if hasattr(s, field) and field not in {"user_details", "episodes"}
        }
        
        s_trans = s.translations[0] if s.translations else None
        s_dict["season_name"] = s_trans.name if s_trans else f"Season {s.season_number}"
        s_dict["overview"] = s_trans.overview if s_trans else None

        s_dict["default_poster_image_path"] = (
            s_trans.default_poster_image_path if s_trans else None
        )
        
        s_user = s.user_details[0] if s.user_details else None
        s_dict["user_details"] = UserSeasonDetailsOut.model_validate(s_user) if s_user else None
        
        # Sort the episodes
        s.episodes.sort(key=lambda e: (e.episode_number or 0))
        
        # Map episodes
        episodes_out = []
        for e in s.episodes:
            # Added "video_assets" to the exclusion set here too
            e_dict = {
                field: getattr(e, field)
                for field in EpisodeOut.model_fields
                if hasattr(e, field) and field not in {"user_details", "video_assets"}
            }
            
            e_trans = e.translations[0] if e.translations else None
            e_dict["episode_name"] = e_trans.name if e_trans else f"Episode {e.episode_number}"
            e_dict["overview"] = e_trans.overview if e_trans else None
            
            e_user = e.user_details[0] if e.user_details else None
            e_dict["user_details"] = UserEpisodeDetailsOut.model_validate(e_user) if e_user else None

            # Map Episode-level Video Assets
            e_dict["video_assets"] = [
                VideoAssetOut.model_validate(va, from_attributes=True) for va in e.video_assets
            ] if e.video_assets else None

            episodes_out.append(EpisodeOut(**e_dict))
        
        s_dict["episodes"] = episodes_out
        seasons_out.append(SeasonOut(**s_dict))
    
    title_dict["seasons"] = seasons_out

    return TitleOut(**title_dict)
