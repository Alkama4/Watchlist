from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from app.integrations import tmdb
from app.services.images import select_best_image, store_image_details
from app.services.genres import store_title_genres
from app.services.languages import get_preferred_locale, get_user_languages
from app.models import (
    TitleTranslation,
    TitleType,
    ImageType,
    Title,
    Season,
    Episode,
    TitleAgeRatings
)


async def coordinate_title_fetching(db: AsyncSession, title_type: str, tmdb_id: int, user_id: int):
    try:
        # Figure out the locale
        locale = await get_preferred_locale(db=db, user_id=user_id, tmdb_id=tmdb_id, title_type=title_type)
        user_image_languages = await get_user_languages(db=db, user_id=user_id)

        # Fetch the title
        if title_type is TitleType.movie:
            tmdb_data = await tmdb.fetch_movie(tmdb_id, locale, user_image_languages)
        elif title_type is TitleType.tv:
            tmdb_data = await tmdb.fetch_tv(tmdb_id, locale, user_image_languages)
        else:
            raise ValueError("Invalid title type")

        # Store
        if title_type is TitleType.movie:
            title_id = await _store_movie(db, tmdb_data, user_id, locale)
        else:
            title_id = await _store_tv(db, tmdb_data, user_id, locale, user_image_languages)

        return title_id

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _store_movie(db: AsyncSession, tmdb_data: dict, user_id: int, locale: str) -> int:
    release_date_str = tmdb_data.get("release_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    # Insert or upsert the title without default images
    stmt = insert(Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["imdb_id"],
        title_type=TitleType.movie,
        name_original=tmdb_data["original_title"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        ##### These aren't from TMDB #####
        # imdb_vote_average
        # imdb_vote_count
        # age_rating
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
    await _store_title_translation(db=db, title_id=title_id, tmdb_data=tmdb_data, locale=locale)
    await store_image_details(db=db, title_id=title_id, images=tmdb_data.get("images", {}))
    await store_title_genres(db=db, title_id=title_id, genres=tmdb_data.get("genres", []))
    await _store_movie_age_ratings(db=db, title_id=title_id, ratings=tmdb_data.get("releases", {}).get("countries", []))

    # Pick the best images for defaults
    languages = await get_user_languages(db=db, user_id=user_id, as_string=False)
    chosen_images = {
        "poster": select_best_image(tmdb_data.get("images", {}).get("posters") or [], languages + [None]),
        "backdrop": select_best_image(tmdb_data.get("images", {}).get("backdrops") or [], [None] + languages),
        "logo": select_best_image(tmdb_data.get("images", {}).get("logos") or [], languages + [None])
    }

    # Update title with default images
    await db.execute(
        update(Title)
        .where(Title.title_id == title_id)
        .values(
            default_poster_image_path=chosen_images["poster"],
            default_backdrop_image_path=chosen_images["backdrop"],
            default_logo_image_path=chosen_images["logo"]
        )
    )

    await db.commit()
    return title_id


async def store_tv(db: AsyncSession, tmdb_data: dict) -> int:
    release_date_str = tmdb_data.get("first_air_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    # Insert or upsert the title without default images
    stmt = insert(Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["external_ids"]["imdb_id"],
        title_type=TitleType.tv,
        name=tmdb_data["name"],
        name_original=tmdb_data["original_name"],
        tagline=tmdb_data["tagline"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        overview=tmdb_data["overview"],
        release_date=release_date,
        original_language=tmdb_data["original_language"],
        origin_country=",".join(tmdb_data["origin_country"]),
        homepage=tmdb_data["homepage"]
    ).on_conflict_do_update(
        index_elements=["tmdb_id"],
        set_={
            "name": tmdb_data["name"],
            "name_original": tmdb_data["original_name"],
            "tagline": tmdb_data["tagline"],
            "tmdb_vote_average": tmdb_data["vote_average"],
            "tmdb_vote_count": tmdb_data["vote_count"],
            "overview": tmdb_data["overview"],
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
    await store_title_genres(db=db, title_id=title_id, genres=tmdb_data.get("genres", []))
    await _store_tv_age_ratings(db=db, title_id=title_id, ratings=tmdb_data.get("content_ratings", {}).get("results", []))

    # Pick the best images for default paths
    title_images = tmdb_data.get("images", {})
    chosen_images = {
        "poster": select_best_image(title_images.get("posters") or [], ["en", "fi", None]),
        "backdrop": select_best_image(title_images.get("backdrops") or [], [None, "en", "fi"]),
        "logo": select_best_image(title_images.get("logos") or [], ["en", "fi", None])
    }

    # Update title with default image paths
    await db.execute(
        update(Title)
        .where(Title.title_id == title_id)
        .values(
            default_poster_image_path=chosen_images["poster"],
            default_backdrop_image_path=chosen_images["backdrop"],
            default_logo_image_path=chosen_images["logo"]
        )
    )

    # Fetch seasons and episodes
    await _fetch_and_store_tv_seasons_and_episodes(db, title_id, tmdb_data)

    await db.commit()
    return title_id


async def _fetch_and_store_tv_seasons_and_episodes(db: AsyncSession, title_id: int, tmdb_data: dict):
    for season in tmdb_data.get("seasons", []):
        season_data = await tmdb.fetch_tv_season(tmdb_data["id"], season["season_number"])

        # Upsert season without default poster
        stmt = insert(Season).values(
            title_id=title_id,
            season_number=season["season_number"],
            season_name=season.get("name"),
            tmdb_vote_average=season.get("vote_average"),
            overview=season.get("overview")
        ).on_conflict_do_update(
            index_elements=["title_id", "season_number"],
            set_={
                "season_name": season.get("name"),
                "tmdb_vote_average": season.get("vote_average"),
                "overview": season.get("overview")
            }
        ).returning(Season.season_id)

        result = await db.execute(stmt)
        season_id = result.scalar_one()
        await db.flush()

        # Store season images
        await store_image_details(db=db, season_id=season_id, images=season_data.get("images", {}))

        # Update season with default poster now that images exist
        poster_image_path = select_best_image(season_data.get("images", {}).get("posters"), ["en", "fi", None])
        if poster_image_path:
            await db.execute(
                update(Season)
                .where(Season.season_id == season_id)
                .values(default_poster_image_path=poster_image_path)
            )

        # Upsert episodes
        episode_images = []
        for ep in season_data.get("episodes", []):
            air_date_str = ep.get("air_date")
            air_date = datetime.strptime(air_date_str, "%Y-%m-%d").date() if air_date_str else None

            stmt = insert(Episode).values(
                season_id=season_id,
                title_id=title_id,
                episode_number=ep["episode_number"],
                episode_name=ep.get("name"),
                tmdb_vote_average=ep.get("vote_average"),
                tmdb_vote_count=ep.get("vote_count"),
                overview=ep.get("overview"),
                air_date=air_date,
                runtime=ep.get("runtime")
            ).on_conflict_do_update(
                index_elements=["season_id", "episode_number"],
                set_={
                    "episode_name": ep.get("name"),
                    "tmdb_vote_average": ep.get("vote_average"),
                    "tmdb_vote_count": ep.get("vote_count"),
                    "overview": ep.get("overview"),
                    "air_date": air_date,
                    "runtime": ep.get("runtime")
                }
            ).returning(Episode.episode_id)

            result = await db.execute(stmt)
            episode_id = result.scalar_one()

            # Collect episode backdrop for later
            still_path = ep.get("still_path")
            if still_path:
                episode_images.append({
                    "file_path": still_path,
                    "episode_id": episode_id,
                    "type": ImageType.backdrop
                })

        # Store episode images
        if episode_images:
            await store_image_details(db=db, images={"backdrops": episode_images})

        # Update episodes with default_backdrop_image_path if needed
        for ep in season_data.get("episodes", []):
            if ep.get("still_path"):
                await db.execute(
                    update(Episode)
                    .where(Episode.episode_number == ep["episode_number"], 
                           Episode.season_id == season_id)
                    .values(default_backdrop_image_path=ep["still_path"])
                )

    await db.commit()


async def _store_title_translation(db: AsyncSession, title_id: int, tmdb_data: dict, locale: str):
    parts = locale.split("-")
    iso_639 = parts[0]
    iso_3166 = parts[1] if len(parts) > 1 else ""

    stmt = insert(TitleTranslation).values(
        title_id=title_id,
        iso_3166_1=iso_3166,
        iso_639_1=iso_639,
        name=tmdb_data["title"] or tmdb_data["name"], 
        tagline=tmdb_data["tagline"],
        overview=tmdb_data["overview"]
    ).on_conflict_do_update(
        index_elements=["title_id", "iso_3166_1", "iso_639_1"],
        set_={
            "name": tmdb_data["title"] or tmdb_data["name"],
            "tagline": tmdb_data["tagline"],
            "overview": tmdb_data["overview"]
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
