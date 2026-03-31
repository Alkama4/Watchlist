from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.services.languages import LanguageContext
from app.integrations import tmdb
from app.services.images import select_best_image, store_image_details
from app.models import(
    TMDBCollection,
    TMDBCollectionTranslation
)

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
    locale_ctx: LanguageContext
):
    tmdb_data = await tmdb.fetch_tmdb_collection(tmdb_collection_id, locale_ctx.preferred_iso_639_1, locale_ctx.iso_639_1_comma_str)
    print(tmdb_data)
    await _store_tmdb_collection(db=db, tmdb_data=tmdb_data)
    await store_image_details(db=db, tmdb_collection_id=tmdb_collection_id, images=tmdb_data.get("images", {}))
    await _store_tmdb_collection_translation(db=db, tmdb_data=tmdb_data, locale_ctx=locale_ctx)

    # Loop through 'parts' (movies) and store


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
