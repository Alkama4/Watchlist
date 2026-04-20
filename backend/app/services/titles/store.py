from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from typing import Optional
from app.integrations import tmdb
from app.integrations.jellyfin import build_jellyfin_map, fetch_jellyfin_titles, resolve_jellyfin_id
from app.services.images import select_best_image, store_image_details
from app.services.genres import store_title_genres
from app.services.languages import LanguageContext, get_user_language_context
from app.services.tmdb_collections import coordinate_tmdb_collection_fetching, init_tmdb_collection
from app.services.video_assets import link_video_assets
from app.models import (
    EpisodeTranslation,
    SeasonTranslation,
    TitleTranslation,
    TitleType,
    Title,
    Season,
    Episode,
    TitleAgeRatings
)


async def coordinate_title_fetching(
    db: AsyncSession, 
    title_type: str, 
    tmdb_id: int, 
    user_id: Optional[int] = None, 
    locale_ctx: Optional[LanguageContext] = None,
    is_root_level_call: bool = True,
    jellyfin_map: Optional[dict] = None,
    title_ids_to_link: Optional[list[int]] = None
):
    # Check what was provided and what needs to be setup
    if title_ids_to_link is None:
        title_ids_to_link = []
    
    if jellyfin_map is None:
        raw_titles = await fetch_jellyfin_titles()
        jellyfin_map = build_jellyfin_map(raw_titles) if raw_titles else {}

    if locale_ctx is None:
        if user_id is None:
            raise ValueError("user_id is required if locale_ctx is not provided.")
            
        locale_ctx = await get_user_language_context(
            db=db, 
            user_id=user_id, 
            tmdb_id=tmdb_id, 
            title_type=title_type
        )

    # Do the actual fetching and storing
    if title_type == TitleType.movie:
        tmdb_data = await tmdb.fetch_movie(
            tmdb_id, 
            locale_ctx.preferred_iso_639_1, 
            locale_ctx.iso_639_1_comma_str
        )
        title_id = await _store_movie(
            db=db,
            tmdb_data=tmdb_data,
            locale_ctx=locale_ctx,
            jellyfin_map=jellyfin_map,
            is_root_level_call=is_root_level_call,
            title_ids_to_link=title_ids_to_link
        )
    elif title_type == TitleType.tv:
        tmdb_data = await tmdb.fetch_tv(
            tmdb_id, 
            locale_ctx.preferred_iso_639_1, 
            locale_ctx.iso_639_1_comma_str
        )
        title_id = await _store_tv(
            db=db,
            tmdb_data=tmdb_data,
            locale_ctx=locale_ctx,
            jellyfin_map=jellyfin_map
        )
    else:
        raise ValueError(f"Invalid title type: {title_type}")
    
    # Finalize links and such
    if title_id not in title_ids_to_link:
        title_ids_to_link.append(title_id)
    
    if is_root_level_call:
        print(f"LINKING ALL FOUND TITLES: {title_ids_to_link}")
        await link_video_assets(db=db, candidate_title_ids=title_ids_to_link)
    
    return title_id


async def _store_movie(
    db: AsyncSession,
    tmdb_data: dict,
    locale_ctx: LanguageContext,
    jellyfin_map: Optional[dict] = None,
    is_root_level_call: bool = True,
    title_ids_to_link: Optional[list[int]] = None
) -> int:
    release_date_str = tmdb_data.get("release_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    jellyfin_id = resolve_jellyfin_id(jellyfin_map, tmdb_data["imdb_id"])

    tmdb_collection_info = tmdb_data.get("belongs_to_collection") or {}
    tmdb_collection_id = tmdb_collection_info.get("id")
    if tmdb_collection_id:
        await init_tmdb_collection(db, tmdb_collection_info)

    # Insert or upsert the title without default images
    stmt = insert(Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["imdb_id"],
        tmdb_collection_id=tmdb_collection_id,
        jellyfin_id=jellyfin_id,
        title_type=TitleType.movie,
        name_original=tmdb_data["original_title"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        ##### These aren't from TMDB #####
        # imdb_vote_average
        # imdb_vote_count
        ##### These aren't from TMDB #####
        movie_runtime=tmdb_data["runtime"],
        movie_revenue=tmdb_data["revenue"],
        movie_budget=tmdb_data["budget"],
        release_date=release_date,
        original_language=tmdb_data["original_language"],
        origin_country=",".join(tmdb_data["origin_country"]),
        homepage=tmdb_data["homepage"]
    ).on_conflict_do_update(
        index_elements=["tmdb_id"],
        set_={
            "jellyfin_id": jellyfin_id,
            "name_original": tmdb_data["original_title"],
            "tmdb_vote_average": tmdb_data["vote_average"],
            "tmdb_vote_count": tmdb_data["vote_count"],
            "movie_runtime": tmdb_data["runtime"],
            "movie_revenue": tmdb_data["revenue"],
            "movie_budget": tmdb_data["budget"],
            "release_date": release_date,
            "original_language": tmdb_data["original_language"],
            "origin_country": ",".join(tmdb_data["origin_country"]),
            "homepage": tmdb_data["homepage"]
        }
    ).returning(Title.title_id)

    result = await db.execute(stmt)
    title_id = result.scalar_one()
    await db.flush()  # flush to get the ID

    # Store less straight forward stuff using helpers
    await store_image_details(db=db, title_id=title_id, images=tmdb_data.get("images", {}))
    await _store_title_translation(db=db, title_id=title_id, tmdb_data=tmdb_data, locale_ctx=locale_ctx)
    await store_title_genres(db=db, title_id=title_id, genres=tmdb_data.get("genres", []))
    await _store_movie_age_ratings(db=db, title_id=title_id, ratings=tmdb_data.get("releases", {}).get("countries", []))

    if tmdb_collection_id and is_root_level_call:
        await coordinate_tmdb_collection_fetching(
            db, tmdb_collection_id, locale_ctx, tmdb_data["id"], jellyfin_map, title_ids_to_link
        )

    await db.commit()
    return title_id


async def _store_tv(
    db: AsyncSession,
    tmdb_data: dict,
    locale_ctx: LanguageContext,
    jellyfin_map: Optional[dict] = None
) -> int:
    release_date_str = tmdb_data.get("first_air_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    jellyfin_id = resolve_jellyfin_id(jellyfin_map, tmdb_data["external_ids"]["imdb_id"])

    # Insert or upsert the title without default images
    stmt = insert(Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["external_ids"]["imdb_id"],
        jellyfin_id=jellyfin_id,
        title_type=TitleType.tv,
        name_original=tmdb_data["original_name"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        release_date=release_date,
        original_language=tmdb_data["original_language"],
        origin_country=",".join(tmdb_data["origin_country"]),
        homepage=tmdb_data["homepage"]
    ).on_conflict_do_update(
        index_elements=["tmdb_id"],
        set_={
            "jellyfin_id": jellyfin_id,
            "name_original": tmdb_data["original_name"],
            "tmdb_vote_average": tmdb_data["vote_average"],
            "tmdb_vote_count": tmdb_data["vote_count"],
            "release_date": release_date,
            "original_language": tmdb_data["original_language"],
            "origin_country": ",".join(tmdb_data["origin_country"]),
            "homepage": tmdb_data["homepage"]
        }
    ).returning(Title.title_id)

    result = await db.execute(stmt)
    title_id = result.scalar_one()
    await db.flush()

    # Store less straight forward stuff using helpers
    await store_image_details(db=db, title_id=title_id, images=tmdb_data.get("images", {}))
    await _store_title_translation(db=db, title_id=title_id, tmdb_data=tmdb_data, locale_ctx=locale_ctx)
    await store_title_genres(db=db, title_id=title_id, genres=tmdb_data.get("genres", []))
    await _store_tv_age_ratings(db=db, title_id=title_id, ratings=tmdb_data.get("content_ratings", {}).get("results", []))

    # Fetch seasons and episodes
    await _fetch_and_store_tv_seasons_and_episodes(
        db=db,
        title_id=title_id,
        tmdb_data=tmdb_data,
        locale_ctx=locale_ctx
    )

    await db.commit()
    return title_id


async def _fetch_and_store_tv_seasons_and_episodes(
    db: AsyncSession,
    title_id: int,
    tmdb_data: dict,
    locale_ctx: LanguageContext
):
    for season in tmdb_data.get("seasons", []):
        season_data = await tmdb.fetch_tv_season(
            tmdb_data["id"],
            season["season_number"],
            locale_ctx.preferred_iso_639_1,
            locale_ctx.iso_639_1_comma_str
        )

        # Store Season
        stmt = insert(Season).values(
            title_id=title_id,
            season_number=season["season_number"],
            tmdb_vote_average=season.get("vote_average"),
        ).on_conflict_do_update(
            index_elements=["title_id", "season_number"],
            set_={"tmdb_vote_average": season.get("vote_average")}
        ).returning(Season.season_id)

        result = await db.execute(stmt)
        season_id = result.scalar_one()
        await db.flush()

        # Store Season Images & Translations (The "heavy" assets)
        await store_image_details(db=db, season_id=season_id, images=season_data.get("images", {}))
        await _store_season_translation(
            db=db, 
            season_id=season_id, 
            season_data=season_data, 
            iso_639_1=locale_ctx.preferred_iso_639_1
        )

        # Store Episodes
        for ep in season_data.get("episodes", []):
            air_date_str = ep.get("air_date")
            air_date = datetime.strptime(air_date_str, "%Y-%m-%d").date() if air_date_str else None

            # Upsert episode and get ID for translation helper
            ep_stmt = insert(Episode).values(
                season_id=season_id,
                title_id=title_id,
                episode_number=ep["episode_number"],
                tmdb_vote_average=ep.get("vote_average"),
                tmdb_vote_count=ep.get("vote_count"),
                air_date=air_date,
                runtime=ep.get("runtime"),
                default_backdrop_image_path=ep.get("still_path") # Simple string storage
            ).on_conflict_do_update(
                index_elements=["season_id", "episode_number"],
                set_={
                    "tmdb_vote_average": ep.get("vote_average"),
                    "tmdb_vote_count": ep.get("vote_count"),
                    "air_date": air_date,
                    "runtime": ep.get("runtime"),
                    "default_backdrop_image_path": ep.get("still_path")
                }
            ).returning(Episode.episode_id)

            ep_result = await db.execute(ep_stmt)
            episode_id = ep_result.scalar_one()

            # Store Episode Translation
            await _store_episode_translation(
                db=db,
                episode_id=episode_id,
                episode_data=ep,
                iso_639_1=locale_ctx.preferred_iso_639_1
            )
            
    await db.commit()


async def _store_title_translation(
    db: AsyncSession,
    title_id: int,
    tmdb_data: dict,
    locale_ctx: LanguageContext
):
    # Pick the best images for the language
    chosen_images = {
        "poster": select_best_image(tmdb_data.get("images", {}).get("posters") or [], [locale_ctx.preferred_iso_639_1, None]),
        "backdrop": select_best_image(tmdb_data.get("images", {}).get("backdrops") or [], [None, locale_ctx.preferred_iso_639_1]),
        "logo": select_best_image(tmdb_data.get("images", {}).get("logos") or [], [locale_ctx.preferred_iso_639_1, None])
    }

    stmt = insert(TitleTranslation).values(
        title_id=title_id,
        iso_639_1=locale_ctx.preferred_iso_639_1,
        name=tmdb_data.get("title") or tmdb_data.get("name"), 
        tagline=tmdb_data["tagline"],
        overview=tmdb_data["overview"],
        default_poster_image_path=chosen_images["poster"],
        default_backdrop_image_path=chosen_images["backdrop"],
        default_logo_image_path=chosen_images["logo"]
    ).on_conflict_do_update(
        index_elements=["title_id", "iso_639_1"],
        set_={
            "name": tmdb_data.get("title") or tmdb_data.get("name"),
            "tagline": tmdb_data["tagline"],
            "overview": tmdb_data["overview"],
            "default_poster_image_path": chosen_images["poster"],
            "default_backdrop_image_path": chosen_images["backdrop"],
            "default_logo_image_path": chosen_images["logo"]
        }
    )
    await db.execute(stmt)


async def _store_season_translation(
    db: AsyncSession,
    season_id: int,
    season_data: dict,
    iso_639_1: str
):
    default_poster_image_path = select_best_image(season_data.get("images", {}).get("posters") or [], [iso_639_1, None])

    stmt = insert(SeasonTranslation).values(
        season_id=season_id,
        iso_639_1=iso_639_1,
        name=season_data.get("name"),
        overview=season_data.get("overview"),
        default_poster_image_path=default_poster_image_path
    ).on_conflict_do_update(
        index_elements=["season_id", "iso_639_1"],
        set_={
            "name": season_data.get("name"),
            "overview": season_data.get("overview"),
            "default_poster_image_path": default_poster_image_path
        }
    )

    await db.execute(stmt)


async def _store_episode_translation(
    db: AsyncSession,
    episode_id: int,
    episode_data: dict,
    iso_639_1: str
):
    stmt = insert(EpisodeTranslation).values(
        episode_id=episode_id,
        iso_639_1=iso_639_1,
        name=episode_data.get("name"),
        overview=episode_data.get("overview")
    ).on_conflict_do_update(
        index_elements=["episode_id", "iso_639_1"],
        set_={
            "name": episode_data.get("name"),
            "overview": episode_data.get("overview")
        }
    )

    await db.execute(stmt)


async def _store_movie_age_ratings(db: AsyncSession, title_id: int, ratings: list):
    if not ratings:
        return

    def _oldest_per_country(ratings):
        by_country = {}

        for r in ratings:
            country = r["iso_3166_1"]
            date = r.get("release_date")

            if not date:
                continue

            if country not in by_country or date < by_country[country]["release_date"]:
                by_country[country] = r

        return list(by_country.values())

    ratings = _oldest_per_country(ratings)

    stmt = insert(TitleAgeRatings).values([
        {
            "title_id": title_id,
            "iso_3166_1": r["iso_3166_1"],
            "rating": r["certification"],
            "descriptors": ", ".join(r.get("descriptors", []))
        }
        for r in ratings
    ]).on_conflict_do_update(
        index_elements=["title_id", "iso_3166_1"],
        set_={
            "rating": insert(TitleAgeRatings).excluded.rating,
            "descriptors": insert(TitleAgeRatings).excluded.descriptors,
        }
    )

    await db.execute(stmt)


async def _store_tv_age_ratings(db: AsyncSession, title_id: int, ratings: list):
    if not ratings:
        return
    
    # Some titles seem to have accidental duplicate data,
    # causing duplicate key errors, so we need to sanitize the data.
    def _dedupe_countries(ratings):
        by_country = {}
        for r in ratings:
            country = r["iso_3166_1"]
            if country not in by_country:
                by_country[country] = r
        return list(by_country.values())

    ratings = _dedupe_countries(ratings)
    
    stmt = insert(TitleAgeRatings).values([
        {
            "title_id": title_id,
            "iso_3166_1": r["iso_3166_1"],
            "rating": r["rating"],
            "descriptors": ", ".join(r.get("descriptors", []))
        }
        for r in ratings
    ]).on_conflict_do_update(
        index_elements=["title_id", "iso_3166_1"],
        set_={
            "rating": insert(TitleAgeRatings).excluded.rating,
            "descriptors": insert(TitleAgeRatings).excluded.descriptors,
        }
    )

    await db.execute(stmt)
