from typing import Any, List, Optional

from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from app.services.languages import LanguageContext, fill_translated_fields_dynamically, get_user_language_context
from app.integrations import tmdb
from app.services.images import select_best_image, store_image_details
from app.services.titles.search_internal import run_title_search
from app.schemas import (
    TMDBCollectionCardOut,
    TMDBCollectionCardUserDetailsOut,
    TitleHeroOut,
    TitleHeroUserDetailsOut,
    TMDBCollectionOut,
    TMDBCollectionUserDetailsOut,
    TitleListOut,
    TitleQueryIn,
)
from app.models import(
    SortBy,
    SortDirection,
    TMDBCollection,
    TMDBCollectionTranslation,
    TMDBCollectionUserDetails,
    Title,
    TitleType,
)


######## STORING ########

async def init_tmdb_collection(db: AsyncSession, tmdb_collection_info: dict):
    tmdb_collection_id = tmdb_collection_info.get("id")
    
    stmt = insert(TMDBCollection).values(
        tmdb_collection_id=tmdb_collection_id,
        name_original=tmdb_collection_info.get("name")
    ).on_conflict_do_nothing()

    await db.execute(stmt)


async def coordinate_tmdb_collection_fetching(
    db: AsyncSession,
    tmdb_collection_id: int,
    locale_ctx: LanguageContext,
    original_tmdb_id: int
):
    from app.services.titles.store import coordinate_title_fetching

    tmdb_data = await tmdb.fetch_tmdb_collection(
        tmdb_collection_id,
        locale_ctx.preferred_iso_639_1,
        locale_ctx.iso_639_1_comma_str
    )

    await _store_tmdb_collection(db=db, tmdb_data=tmdb_data)
    await store_image_details(db=db, tmdb_collection_id=tmdb_collection_id, images=tmdb_data.get("images", {}))
    await _store_tmdb_collection_translation(db=db, tmdb_data=tmdb_data, locale_ctx=locale_ctx)

    # Fetch missing movies from the collection, but don't add to users library
    for movie in tmdb_data.get("parts"):
        if movie["id"] != original_tmdb_id:
            result = await db.execute(
                select(Title).where(Title.tmdb_id == movie["id"])
            )
            existing_title = result.scalar_one_or_none()
            if not existing_title:
                await coordinate_title_fetching(
                    db=db,
                    title_type=TitleType.movie,
                    tmdb_id=movie["id"],
                    locale_ctx=locale_ctx,
                    fetch_collection=False # IMPORTANT, DO NOT REMOVE
                                           # Prevents recursion from happening
                )


async def _store_tmdb_collection(
    db: AsyncSession,
    tmdb_data: dict,
):
    stmt = insert(TMDBCollection).values(
        tmdb_collection_id=tmdb_data["id"],
        name_original=tmdb_data.get("original_name"),
        original_language=tmdb_data.get("original_language")
    ).on_conflict_do_update(
        index_elements=["tmdb_collection_id"],
        set_={
            "name_original": tmdb_data.get("original_name"),
            "original_language": tmdb_data.get("original_language")
        }
    )
    await db.execute(stmt)


async def _store_tmdb_collection_translation(
    db: AsyncSession,
    tmdb_data: dict,
    locale_ctx: LanguageContext
):
    # Pick the best images for the language
    chosen_images = {
        "poster": select_best_image(tmdb_data.get("images", {}).get("posters") or [], [locale_ctx.preferred_iso_639_1, None]),
        "backdrop": select_best_image(tmdb_data.get("images", {}).get("backdrops") or [], [None, locale_ctx.preferred_iso_639_1])
    }

    stmt = insert(TMDBCollectionTranslation).values(
        tmdb_collection_id=tmdb_data["id"],
        iso_639_1=locale_ctx.preferred_iso_639_1,
        name=tmdb_data.get("name"),
        overview=tmdb_data.get("overview"),
        default_poster_image_path=chosen_images["poster"],
        default_backdrop_image_path=chosen_images["backdrop"]
    ).on_conflict_do_update(
        index_elements=["tmdb_collection_id", "iso_639_1"],
        set_={
            "name": tmdb_data.get("name"),
            "overview": tmdb_data.get("overview"),
            "default_poster_image_path": chosen_images["poster"],
            "default_backdrop_image_path": chosen_images["backdrop"]
        }
    )
    await db.execute(stmt)


######## READING ########

async def fetch_tmdb_collection_with_user_details(
    db: AsyncSession,
    tmdb_collection_id: int,
    user_id: int
) -> TMDBCollectionOut:
    locale_ctx = await get_user_language_context(db=db, user_id=user_id)

    stmt = (
        select(TMDBCollection)
        .where(TMDBCollection.tmdb_collection_id == tmdb_collection_id)
        .options(
            # Load Collection Translation
            selectinload(TMDBCollection.translations.and_(
                TMDBCollectionTranslation.iso_639_1.in_(locale_ctx.iso_639_1_list)
            )),
            # Load Collection User Details
            selectinload(TMDBCollection.user_details.and_(
                TMDBCollectionUserDetails.user_id == user_id
            ))
        )
    )

    result = await db.execute(stmt)
    collection = result.scalar_one_or_none()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    user_col = collection.user_details[0] if collection.user_details else None
    if not user_col:
        user_col = TMDBCollectionUserDetails(
            user_id=user_id, 
            tmdb_collection_id=tmdb_collection_id
        )
        db.add(user_col)
    
    user_col.last_viewed_at = datetime.now(timezone.utc)
    await db.commit()

    title_list = await run_title_search(
        db=db,
        user_id=user_id,
        locale_ctx=locale_ctx,
        title_schema=TitleHeroOut,
        user_title_details_schema=TitleHeroUserDetailsOut,
        q=TitleQueryIn(
            tmdb_collection_ids=[tmdb_collection_id],
            in_library=None,
            sort_by=SortBy.release_date,
            sort_direction=SortDirection.asc,
            page_size=0
        )
    )

    return _build_tmdb_collection_out(collection, locale_ctx, title_list)


def _build_tmdb_collection_out(
    collection: TMDBCollection,
    locale_ctx: LanguageContext,
    title_list: TitleListOut
) -> TMDBCollectionOut:
    # Filter out relationships that need custom mapping (titles, user_details, etc.)
    col_dict = {
        field: getattr(collection, field)
        for field in TMDBCollectionOut.model_fields
        if field not in {"titles", "user_details"} and hasattr(collection, field)
    }
    
    # Fill translated fields (name, overview, default_poster_image_path, etc.)
    fill_translated_fields_dynamically(
        col_dict, 
        collection.translations, 
        locale_ctx.iso_639_1_list, 
        TMDBCollectionTranslation
    )
    
    # Absolute fallback for the collection name
    if not col_dict.get("name"):
        col_dict["name"] = collection.name_original

    # Map User Details
    user_detail = collection.user_details[0] if collection.user_details else None
    col_dict["user_details"] = (
        TMDBCollectionUserDetailsOut.model_validate(user_detail, from_attributes=True) 
        if user_detail
        else TMDBCollectionUserDetailsOut()
    )
    
    col_dict["titles"] = title_list.titles

    col_dict["display_locale"] = locale_ctx.preferred_locale

    return TMDBCollectionOut(**col_dict)


######## READING CARDS ########

async def fetch_tmdb_collection_cards(
    db: AsyncSession,
    user_id: int,
    locale_ctx: LanguageContext,
    tmdb_collection_ids: Optional[List[int]] = None
) -> List[TMDBCollectionCardOut]:
    if not locale_ctx:
        locale_ctx = await get_user_language_context(db=db, user_id=user_id)

    stmt = (
        select(TMDBCollection)
        .options(
            selectinload(TMDBCollection.translations.and_(
                TMDBCollectionTranslation.iso_639_1.in_(locale_ctx.iso_639_1_list)
            )),
            selectinload(TMDBCollection.user_details.and_(
                TMDBCollectionUserDetails.user_id == user_id
            ))
        )
    )

    if tmdb_collection_ids:
        stmt = stmt.where(TMDBCollection.tmdb_collection_id.in_(tmdb_collection_ids))

    # Expanded aggregate query for all missing fields
    stats_stmt = (
        select(
            Title.tmdb_collection_id,
            func.count(Title.title_id).label("total"),
            func.min(Title.release_date).label("first_release"),
            func.max(Title.release_date).label("last_release"),
            func.sum(Title.movie_runtime).label("runtime"),
            func.avg(Title.tmdb_vote_average).filter(Title.tmdb_vote_average > 0).label("vote_avg")
        )
        .group_by(Title.tmdb_collection_id)
    )
    
    if tmdb_collection_ids:
        stats_stmt = stats_stmt.where(Title.tmdb_collection_id.in_(tmdb_collection_ids))

    result = await db.execute(stmt)
    collections = result.scalars().all()
    
    stats_result = await db.execute(stats_stmt)
    # Map the collection ID to the full stats row
    stats_map = {row.tmdb_collection_id: row for row in stats_result}

    return [
        _build_tmdb_collection_card_out(
            col, 
            locale_ctx, 
            stats_map.get(col.tmdb_collection_id)
        )
        for col in collections
    ]


def _build_tmdb_collection_card_out(
    collection: TMDBCollection,
    locale_ctx: LanguageContext,
    stats: Optional[Any] = None  # Receives the result row from stats_stmt
) -> TMDBCollectionCardOut:
    # Fields to exclude from direct attribute copying (handled manually or via translation)
    excluded_fields = {
        "user_details", "title_count", "first_release_date", 
        "last_release_date", "total_runtime", "tmdb_vote_average"
    }

    col_dict = {
        field: getattr(collection, field)
        for field in TMDBCollectionCardOut.model_fields
        if field not in excluded_fields and hasattr(collection, field)
    }

    # Fill translations (name, overview, default_poster_image_path, etc.)
    fill_translated_fields_dynamically(
        col_dict,
        collection.translations,
        locale_ctx.iso_639_1_list,
        TMDBCollectionTranslation
    )

    # Fallback for name
    if not col_dict.get("name"):
        col_dict["name"] = collection.name_original

    # Map User Details
    user_detail = collection.user_details[0] if collection.user_details else None
    col_dict["user_details"] = (
        TMDBCollectionCardUserDetailsOut.model_validate(user_detail, from_attributes=True)
        if user_detail
        else TMDBCollectionCardUserDetailsOut()
    )

    # Map Aggregate Statistics
    if stats:
        col_dict["title_count"] = stats.total
        col_dict["first_release_date"] = stats.first_release
        col_dict["last_release_date"] = stats.last_release
        col_dict["total_runtime"] = stats.runtime
        # Round the average to 1 decimal place if it exists
        col_dict["tmdb_vote_average"] = round(float(stats.vote_avg), 1) if stats.vote_avg else None
    else:
        col_dict["title_count"] = 0

    return TMDBCollectionCardOut(**col_dict)