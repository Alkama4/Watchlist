from fastapi import HTTPException
from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.services.languages import LanguageContext, check_translation_availability, fill_translated_fields_dynamically, get_user_language_context
from app.services.titles.store import coordinate_title_fetching
from app.services.tmdb_collections import fetch_tmdb_collection_cards
from app.schemas import (
    EpisodeOut,
    GenreElement,
    AgeRatingElement,
    SeasonOut,
    EpisodeUserDetailsOut,
    SeasonUserDetailsOut,
    TMDBCollectionCardOut,
    TitleUserDetailsOut,
    TitleOut,
    VideoAssetOut
)
from app.models import (
    Episode,
    Title,
    Season,
    TitleFolder,
    TitleTranslation,
    SeasonTranslation,
    EpisodeTranslation,
    TitleType,
    TitleUserDetails,
    SeasonUserDetails,
    EpisodeUserDetails,
    TitleGenre,
    VideoAsset
)


async def fetch_title_with_user_details(db: AsyncSession, title_id: int, user_id: int) -> TitleOut:
    locale_ctx = await get_user_language_context(db=db, user_id=user_id, title_id=title_id)

    # Use the helper to "warm up" the database
    await _ensure_primary_translation(
        db=db, 
        title_id=title_id, 
        user_id=user_id, 
        primary_iso=locale_ctx.preferred_iso_639_1
    )

    # Execute the "Mega Query" 
    stmt = (
        select(Title)
        .where(Title.title_id == title_id)
        .options(
            # Load Title Translation & User Details
            selectinload(Title.translations.and_(
                TitleTranslation.iso_639_1.in_(locale_ctx.iso_639_1_list)
            )),
            selectinload(Title.user_details.and_(TitleUserDetails.user_id == user_id)),
            selectinload(Title.genres).selectinload(TitleGenre.genre),
            selectinload(Title.age_ratings),
            selectinload(Title.title_folder).selectinload(
                TitleFolder.video_assets.and_(VideoAsset.episode_id == None)
            ),
            
            # Load Seasons + filtered children
            selectinload(Title.seasons.and_(Season.season_number != 0)).options(
                selectinload(Season.translations.and_(
                    SeasonTranslation.iso_639_1.in_(locale_ctx.iso_639_1_list)
                )),
                selectinload(Season.user_details.and_(SeasonUserDetails.user_id == user_id)),
                
                # Load Episodes + filtered children
                selectinload(Season.episodes).options(
                    selectinload(Episode.translations.and_(
                        EpisodeTranslation.iso_639_1.in_(locale_ctx.iso_639_1_list)
                    )),
                    selectinload(Episode.user_details.and_(EpisodeUserDetails.user_id == user_id)),
                    selectinload(Episode.video_assets)
                )
            )
        )
    )

    result = await db.execute(stmt)
    title = result.scalar_one_or_none()
    
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    # Handle User Title Logic & Commit
    user_title = title.user_details[0] if title.user_details else None
    if not user_title:
        user_title = TitleUserDetails(user_id=user_id, title_id=title_id)
        db.add(user_title)
    
    user_title.last_viewed_at = datetime.now(timezone.utc)
    await db.commit()

    tmdb_collection_card = None
    if title.title_type == TitleType.movie:
        cards = await fetch_tmdb_collection_cards(
            db=db,
            user_id=user_id,
            locale_ctx=locale_ctx,
            tmdb_collection_ids=[title.tmdb_collection_id]
        )
        tmdb_collection_card = cards[0] if cards else None

    return _build_title_out(title, locale_ctx, tmdb_collection_card)


async def _ensure_primary_translation(db: AsyncSession, title_id: int, user_id: int, primary_iso: str):
    """
    Checks if a translation exists for the primary ISO. 
    If not, fetches title info and triggers the coordinator.
    """
    exists = await check_translation_availability(db, title_id, primary_iso)
    
    if not exists:
        # Get the bare minimum info needed for the coordinator
        stmt = select(Title.title_type, Title.tmdb_id).where(Title.title_id == title_id)
        res = await db.execute(stmt)
        info = res.one_or_none()
        
        if info:
            # This is the synchronous wait for external data
            await coordinate_title_fetching(
                db=db, 
                title_type=info.title_type, 
                tmdb_id=info.tmdb_id, 
                user_id=user_id
            )


def _build_title_out(title: Title, locale_ctx: LanguageContext, tmdb_collection_card: TMDBCollectionCardOut) -> TitleOut:
    # Base Fields
    title_dict = {
        field: getattr(title, field)
        for field in TitleOut.model_fields
        if hasattr(title, field) and field not in {"genres", "user_details", "seasons", "age_ratings", "video_assets"}
    }
    
    # Field-Level Fallback for Title
    fill_translated_fields_dynamically(
        title_dict, 
        title.translations, 
        locale_ctx.iso_639_1_list, 
        TitleTranslation
    )
    
    # Absolute fallback for Name
    if not title_dict.get("name"):
        title_dict["name"] = title.original_title

    # Apply Title User Details
    user_detail = title.user_details[0] if title.user_details else None
    title_dict["user_details"] = (
        TitleUserDetailsOut.model_validate(user_detail)
        if user_detail
        else TitleUserDetailsOut()
    )

    # Map Genres, Ratings & Video Assets
    title_dict["genres"] = [GenreElement.model_validate(tg.genre, from_attributes=True) for tg in title.genres]
    title_dict["age_ratings"] = [AgeRatingElement.model_validate(r, from_attributes=True) for r in title.age_ratings]
    
    folder = title.title_folder
    if folder and folder.video_assets:
        title_dict["video_assets"] = [
            VideoAssetOut.model_validate(va, from_attributes=True) 
            for va in folder.video_assets
        ]
    else:
        title_dict["video_assets"] = None

    # Other simple fields
    title_dict["display_locale"] = locale_ctx.preferred_locale
    title_dict["tmdb_collection_card"] = tmdb_collection_card

    # Map Seasons
    title.seasons.sort(key=lambda s: s.season_number)
    seasons_out = []
    for s in title.seasons:
        s_dict = {
            field: getattr(s, field)
            for field in SeasonOut.model_fields
            if hasattr(s, field) and field not in {"user_details", "episodes"}
        }

        fill_translated_fields_dynamically(s_dict, s.translations, locale_ctx.iso_639_1_list, SeasonTranslation)
        s_dict["season_name"] = s_dict.pop("name", None) or f"Season {s.season_number}"
        
        s_user = s.user_details[0] if s.user_details else None
        s_dict["user_details"] = (
            SeasonUserDetailsOut.model_validate(s_user)
            if s_user
            else SeasonUserDetailsOut()
        )
        
        # Sort the episodes
        s.episodes.sort(key=lambda e: (e.episode_number or 0))
        
        # 4. Map episodes
        episodes_out = []
        for e in s.episodes:
            e_dict = {
                field: getattr(e, field)
                for field in EpisodeOut.model_fields
                if hasattr(e, field) and field not in {"user_details", "video_assets"}
            }

            fill_translated_fields_dynamically(e_dict, e.translations, locale_ctx.iso_639_1_list, EpisodeTranslation)
            e_dict["episode_name"] = e_dict.pop("name", None) or f"Episode {e.episode_number}"

            e_user = e.user_details[0] if e.user_details else None
            e_dict["user_details"] = (
                EpisodeUserDetailsOut.model_validate(e_user)
                if e_user
                else EpisodeUserDetailsOut()
            )
            
            e_dict["video_assets"] = [
                VideoAssetOut.model_validate(va, from_attributes=True) for va in e.video_assets
            ] if e.video_assets else None

            episodes_out.append(EpisodeOut(**e_dict))
        
        s_dict["episodes"] = episodes_out
        seasons_out.append(SeasonOut(**s_dict))
    
    title_dict["seasons"] = seasons_out
    
    return TitleOut(**title_dict)
