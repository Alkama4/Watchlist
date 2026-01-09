from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, tuple_, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload, aliased
from datetime import datetime, date
from app import models, schemas
from app.dependencies import get_db
from app.integrations import tmdb
from app.routers.auth import get_current_user
from app.config import DEFAULT_MAX_QUERY_LIMIT
from app.settings.config import DEFAULT_SETTINGS

router = APIRouter()


# ---------- DB STORAGE ----------

def _select_best_image(images: List[Dict], iso_639_1_list: List[Optional[str]]) -> Optional[str]:
    """
    Selects the best image based on vote_average * vote_count, trying ISO codes in order,
    and returns the file path of that image.
    
    :param images: List of image dictionaries.
    :param iso_639_1_list: Ordered list of language codes to try (use None for no language filter).
    :return: The file path of the best image or None if no match.
    """
    for iso in iso_639_1_list:
        candidates = [img for img in images if iso is None or img.get("iso_639_1") == iso]
        if candidates:
            best_image = max(candidates, key=lambda img: (img.get("vote_average") or 0) * (img.get("vote_count") or 0))
            return best_image.get("file_path")
    return None


async def store_movie(db: AsyncSession, tmdb_data: dict) -> int:
    release_date_str = tmdb_data.get("release_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    # Insert or upsert the title without default images
    stmt = insert(models.Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["imdb_id"],
        type=models.TitleType.movie,
        name=tmdb_data["title"],
        name_original=tmdb_data["original_title"],
        tagline=tmdb_data["tagline"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        ##### These aren't from TMDB #####
        # imdb_vote_average
        # imdb_vote_count
        # age_rating
        overview=tmdb_data["overview"],
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
            "name": tmdb_data["title"],
            "name_original": tmdb_data["original_title"],
            "tagline": tmdb_data["tagline"],
            "tmdb_vote_average": tmdb_data["vote_average"],
            "tmdb_vote_count": tmdb_data["vote_count"],
            "overview": tmdb_data["overview"],
            "movie_runtime": tmdb_data["runtime"],
            "movie_revenue": tmdb_data["revenue"],
            "movie_budget": tmdb_data["budget"],
            "release_date": release_date,
            "original_language": tmdb_data["original_language"],
            "origin_country": ",".join(tmdb_data["origin_country"]),
            "homepage": tmdb_data["homepage"]
        }
    ).returning(models.Title.title_id)

    result = await db.execute(stmt)
    title_id = result.scalar_one()
    await db.flush()  # flush to get the ID

    # Store all images
    await store_image_details(db=db, title_id=title_id, images=tmdb_data.get("images", {}))

    # Pick the best images for defaults
    chosen_images = {
        "poster": _select_best_image(tmdb_data.get("images", {}).get("posters") or [], ["en", "fi", None]),
        "backdrop": _select_best_image(tmdb_data.get("images", {}).get("backdrops") or [], [None, "en", "fi"]),
        "logo": _select_best_image(tmdb_data.get("images", {}).get("logos") or [], ["en", "fi", None])
    }

    # Update title with default images
    await db.execute(
        update(models.Title)
        .where(models.Title.title_id == title_id)
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
    stmt = insert(models.Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["external_ids"]["imdb_id"],
        type=models.TitleType.tv,
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
    ).returning(models.Title.title_id)

    result = await db.execute(stmt)
    title_id = result.scalar_one()
    await db.flush()

    # Store all images for the title
    await store_image_details(db=db, title_id=title_id, images=tmdb_data.get("images", {}))

    # Pick the best images for default paths
    title_images = tmdb_data.get("images", {})
    chosen_images = {
        "poster": _select_best_image(title_images.get("posters") or [], ["en", "fi", None]),
        "backdrop": _select_best_image(title_images.get("backdrops") or [], [None, "en", "fi"]),
        "logo": _select_best_image(title_images.get("logos") or [], ["en", "fi", None])
    }

    # Update title with default image paths
    await db.execute(
        update(models.Title)
        .where(models.Title.title_id == title_id)
        .values(
            default_poster_image_path=chosen_images["poster"],
            default_backdrop_image_path=chosen_images["backdrop"],
            default_logo_image_path=chosen_images["logo"]
        )
    )

    # Fetch seasons and episodes
    await fetch_and_store_tv_seasons_and_episodes(db, title_id, tmdb_data)

    await db.commit()
    return title_id


async def fetch_and_store_tv_seasons_and_episodes(db: AsyncSession, title_id: int, tmdb_data: dict):
    for season in tmdb_data.get("seasons", []):
        season_data = await tmdb.fetch_tv_season(tmdb_data["id"], season["season_number"])

        # Upsert season without default poster
        stmt = insert(models.Season).values(
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
        ).returning(models.Season.season_id)

        result = await db.execute(stmt)
        season_id = result.scalar_one()
        await db.flush()

        # Store season images
        await store_image_details(db=db, season_id=season_id, images=season_data.get("images", {}))

        # Update season with default poster now that images exist
        poster_image_path = _select_best_image(season_data.get("images", {}).get("posters"), ["en", "fi", None])
        if poster_image_path:
            await db.execute(
                update(models.Season)
                .where(models.Season.season_id == season_id)
                .values(default_poster_image_path=poster_image_path)
            )

        # Upsert episodes
        episode_images = []
        for ep in season_data.get("episodes", []):
            air_date_str = ep.get("air_date")
            air_date = datetime.strptime(air_date_str, "%Y-%m-%d").date() if air_date_str else None

            stmt = insert(models.Episode).values(
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
            ).returning(models.Episode.episode_id)

            result = await db.execute(stmt)
            episode_id = result.scalar_one()

            # Collect episode backdrop for later
            still_path = ep.get("still_path")
            if still_path:
                episode_images.append({
                    "file_path": still_path,
                    "episode_id": episode_id,
                    "type": models.ImageType.backdrop
                })

        # Store episode images
        if episode_images:
            await store_image_details(db=db, images={"backdrops": episode_images})

        # Update episodes with default_backdrop_image_path if needed
        for ep in season_data.get("episodes", []):
            if ep.get("still_path"):
                await db.execute(
                    update(models.Episode)
                    .where(models.Episode.episode_number == ep["episode_number"], 
                           models.Episode.season_id == season_id)
                    .values(default_backdrop_image_path=ep["still_path"])
                )

    await db.commit()


async def store_image_details(db: AsyncSession, title_id: int = None, season_id: int = None, episode_id: int = None, images: dict = None):
    if not images:
        return

    type_fk_map = {
        "backdrops": {"type": models.ImageType.backdrop, "fk": {"title_id": title_id, "season_id": None}},
        "posters": {"type": models.ImageType.poster, "fk": {"title_id": title_id, "season_id": season_id}},
        "logos": {"type": models.ImageType.logo, "fk": {"title_id": title_id, "season_id": None}},
    }

    image_records = []

    for key, meta in type_fk_map.items():
        for img in images.get(key, []):
            record = {
                "file_path": img["file_path"],
                "type": meta["type"],
                "title_id": meta["fk"]["title_id"],
                "season_id": meta["fk"]["season_id"],
                "episode_id": img.get("episode_id"),
                "width": img.get("width"),
                "height": img.get("height"),
                "iso_3166_1": img.get("iso_3166_1"),
                "iso_639_1": img.get("iso_639_1"),
                "vote_average": img.get("vote_average"),
                "vote_count": img.get("vote_count")
            }
            image_records.append(record)

    if not image_records:
        return

    insert_stmt = insert(models.Image).values(image_records)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=["file_path"],
        set_={
            "vote_average": insert_stmt.excluded.vote_average,
            "vote_count": insert_stmt.excluded.vote_count
        }
    )

    await db.execute(stmt)
    await db.commit()


# ---------- SET FLAGS ----------

async def set_user_title_flags(
    db: AsyncSession,
    user_id: int,
    title_id: int,
    **flags: bool
):
    stmt = insert(models.UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        **flags
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_=flags
    )

    await db.execute(stmt)
    await db.commit()


# ---------- READING TITLES ----------

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


# ---------- TITLE SEARCH LOGIC ----------

def _base_title_query(user_id: int, utd):
    stmt = (
        select(models.Title, utd)
        .outerjoin(
            utd,
            and_(
                utd.title_id == models.Title.title_id,
                utd.user_id == user_id,
            )
        ).where(utd.in_library == True)
    )

    return stmt


def _apply_filters(stmt, utd, q: schemas.TitleQueryIn):

    # TODO: setup a smarter search. get rid of special chars and split by space and just try to fit the sections to the name or original name

    # TODO: setup remaining missing filters that are in the TitleQueryIn schema

    if q.query:
        stmt = stmt.where(models.Title.name.ilike(f"%{q.query}%"))

    if q.title_type:
        stmt = stmt.where(models.Title.type == q.title_type)

    if q.is_favourite is not None:
        stmt = stmt.where(utd.is_favourite == q.is_favourite)

    if q.in_watchlist is not None:
        stmt = stmt.where(utd.in_watchlist == q.in_watchlist)

    if q.release_year_min:
        stmt = stmt.where(func.extract("year", models.Title.release_date) >= q.release_year_min)

    if q.release_year_max:
        stmt = stmt.where(func.extract("year", models.Title.release_date) <= q.release_year_max)

    if q.min_tmdb_rating:
        stmt = stmt.where(models.Title.tmdb_vote_average >= q.min_tmdb_rating)

    if q.min_imdb_rating:
        stmt = stmt.where(models.Title.imdb_vote_average >= q.min_imdb_rating)

    return stmt


async def _get_user_sort_settings(user_id: int, db) -> dict:
    result = await db.execute(
        select(models.UserSetting)
        .where(
            models.UserSetting.user_id == user_id,
            models.UserSetting.key.in_(["sort_by", "sort_direction"])
        )
    )
    rows = result.scalars().all()
    return {row.key: row.value for row in rows}


async def _apply_sorting_with_user_settings(
    stmt, q: schemas.TitleQueryIn, user_id: int, db, utd
):
    sort_by = q.sort_by
    sort_dir = q.sort_direction

    # Load user settings only if the caller asked for "default"
    if sort_by is models.SortBy.default or sort_dir is models.SortDirection.default:
        user_settings = await _get_user_sort_settings(user_id, db)

        if sort_by is models.SortBy.default:
            sort_by = models.SortBy(user_settings.get(
                "sort_by", DEFAULT_SETTINGS.sort_by
            ))

        if sort_dir is models.SortDirection.default:
            sort_dir = models.SortDirection(user_settings.get(
                "sort_direction", DEFAULT_SETTINGS.sort_direction
            ))

    # mapping from enum to column
    sort_map = {
        models.SortBy.tmdb_score: models.Title.tmdb_vote_average,
        models.SortBy.imdb_score: models.Title.imdb_vote_average,
        models.SortBy.popularity: models.Title.tmdb_vote_count,
        models.SortBy.title_name: models.Title.name,
        models.SortBy.runtime: models.Title.movie_runtime,
        models.SortBy.release_date: models.Title.release_date,
        models.SortBy.last_viewed_at: utd.last_viewed_at,
        models.SortBy.random: func.random()
    }

    col = sort_map.get(sort_by, models.Title.tmdb_vote_average)
    stmt = stmt.order_by(
        col.desc() if sort_dir is models.SortDirection.desc else col.asc()
    )
    return stmt


def _add_subqueries(stmt):
    season_count_subq = (
        select(func.count(models.Season.season_id))
        .where(models.Season.title_id == models.Title.title_id)
        .scalar_subquery()
    )

    episode_count_subq = (
        select(func.count(models.Episode.episode_id))
        .join(models.Season, models.Season.season_id == models.Episode.season_id)
        .where(models.Season.title_id == models.Title.title_id)
        .scalar_subquery()
    )

    return stmt.add_columns(
        season_count_subq.label("show_season_count"),
        episode_count_subq.label("show_episode_count")
    )


def _apply_pagination(stmt, q: schemas.TitleQueryIn):
    page = q.page_number or 1
    size = q.page_size or DEFAULT_MAX_QUERY_LIMIT
    return stmt.limit(size).offset((page - 1) * size), page, size


def _build_title_list_out(rows, total, page, size) -> schemas.TitleListOut:
    titles = []

    for title, user_details, season_count, episode_count in rows:
        out = schemas.CompactTitleOut.model_validate(title, from_attributes=True)
        out.show_season_count = season_count
        out.show_episode_count = episode_count

        if user_details:
            out.user_details = schemas.CompactUserTitleDetailsOut.model_validate(
                user_details, from_attributes=True
            )

        titles.append(out)

    return schemas.TitleListOut(
        titles=titles,
        page_number=page,
        page_size=size,
        total_items=total,
        total_pages=(total + size - 1) // size
    )


async def run_title_search(
    db,
    user_id: int,
    q: schemas.TitleQueryIn
) -> schemas.TitleListOut:
    
    utd = aliased(models.UserTitleDetails)

    base_stmt = _base_title_query(user_id, utd)
    base_stmt = _apply_filters(base_stmt, utd, q)

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = await _apply_sorting_with_user_settings(base_stmt, q, user_id, db, utd)
    stmt = _add_subqueries(stmt)
    stmt, page, size = _apply_pagination(stmt, q)

    rows = (await db.execute(stmt)).all()
    return _build_title_list_out(rows, total, page, size)


# ---------- TITLE SEARCH LOGIC ----------

async def fetch_existing_titles_with_user(
    db: AsyncSession,
    user_id: int,
    tmdb_items: list[tuple[int, models.TitleType]],
):
    utd = aliased(models.UserTitleDetails)

    stmt = (
        select(models.Title, utd)
        .outerjoin(
            utd,
            and_(
                utd.title_id == models.Title.title_id,
                utd.user_id == user_id,
            )
        )
        .where(
            tuple_(models.Title.tmdb_id, models.Title.type).in_(tmdb_items)
        )
    )

    rows = (await db.execute(stmt)).all()

    return {
        (title.tmdb_id, title.type): (title, user_details)
        for title, user_details in rows
    }


async def run_and_process_tmdb_search(
    db: AsyncSession,
    user_id: int,
    data: schemas.TMDBTitleQueryIn,
) -> schemas.TitleListOut:
    
    response = await tmdb.search_multi(
        query=data.query,
        page=data.page
    )

    compact_titles = []

    tmdb_keys = [
        (r["id"], models.TitleType[r["media_type"]])
        for r in response["results"]
        if r.get("media_type") in ("movie", "tv")
    ]

    existing_map = await fetch_existing_titles_with_user(
        db,
        user_id,
        tmdb_keys,
    )

    for r in response["results"]:
        if r.get("media_type") not in ("movie", "tv"):
            continue

        key = (r["id"], models.TitleType[r["media_type"]])
        title, utd = existing_map.get(key, (None, None))

        compact_titles.append({
            "title_id": title.title_id if title else None,
            "tmdb_id": r["id"],
            "type": r["media_type"],
            "name": r.get("title") or r.get("name"),
            "release_date": r.get("release_date") or r.get("first_air_date"),
            "tmdb_vote_average": r.get("vote_average"),
            "tmdb_vote_count": r.get("vote_count"),
            "default_poster_image_path": r.get("poster_path"),
            "default_backdrop_image_path": r.get("backdrop_path"),
            "user_details": (
                schemas.CompactUserTitleDetailsOut.model_validate(
                    utd, from_attributes=True
                )
                if utd else None
            ),
        })

    return {
        "titles": compact_titles,
        "page_number": response.get("page"),
        "page_size": 20,
        "total_items": response.get("total_results"),
        "total_pages": response.get("total_pages")
    }


# ---------- ROUTER ENDPOINTS ----------

@router.post("/")
async def add_new_title_to_watchlist(
    data: schemas.TitleIn,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(models.Title).where(models.Title.tmdb_id == data.tmdb_id)
    )

    title = existing.scalar_one_or_none()
    if title:
        title_id = title.title_id
    else:
        try:
            # Fetch the title
            if data.title_type is schemas.TitleType.movie:
                tmdb_data = await tmdb.fetch_movie(data.tmdb_id)
            elif data.title_type is schemas.TitleType.tv:
                tmdb_data = await tmdb.fetch_tv(data.tmdb_id)
            else:
                raise ValueError("Invalid title type")

            # Store
            if data.title_type is schemas.TitleType.movie:
                title_id = await store_movie(db, tmdb_data)
            else:
                title_id = await store_tv(db, tmdb_data)
                await fetch_and_store_tv_seasons_and_episodes(db, title_id, tmdb_data)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_library=True
    )

    return {
        "title_id": title_id,
        "in_library": True,
    }

@router.post("/search", response_model=schemas.TitleListOut)
async def search_for_titles(
    data: schemas.TitleQueryIn,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await run_title_search(db, user.user_id, data)


@router.post("/search/tmdb", response_model=schemas.TitleListOut)
async def search_for_titles_from_tmdb(
    data: schemas.TMDBTitleQueryIn,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await run_and_process_tmdb_search(db, user.user_id, data)


@router.get("/{title_id}", response_model=schemas.TitleOut)
async def get_title_details(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    title = await fetch_title_with_user_details(db, title_id, user.user_id)
    return title


@router.put("/{title_id}")
async def update_title_details(
    title_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Fetch the existing title by internal ID
    result = await db.execute(select(models.Title).where(models.Title.title_id == title_id))
    title = result.scalar_one_or_none()

    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    try:
        # Fetch updated TMDB data based on the type
        if title.type == models.TitleType.movie:
            tmdb_data = await tmdb.fetch_movie(title.tmdb_id)
            updated_title_id = await store_movie(db, tmdb_data)
        elif title.type == models.TitleType.tv:
            tmdb_data = await tmdb.fetch_tv(title.tmdb_id)
            updated_title_id = await store_tv(db, tmdb_data)
            await fetch_and_store_tv_seasons_and_episodes(db, updated_title_id, tmdb_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid title type")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"title_id": updated_title_id, "updated": True}


@router.put("/{title_id}/library")
async def add_existing_title_to_library(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_library=True
    )
    return {"title_id": title_id, "in_library": True}


@router.delete("/{title_id}/library")
async def remove_existing_title_from_library(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_library=False
    )
    return {"title_id": title_id, "in_library": False}


@router.put("/{title_id}/favourite")
async def add_title_to_favourites(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        is_favourite=True,
        in_library=True
    )
    return {"title_id": title_id, "is_favourite": True, "in_library": True}


@router.delete("/{title_id}/favourite")
async def remove_title_from_favourites(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        is_favourite=False
    )
    return {"title_id": title_id, "is_favourite": False}


@router.put("/{title_id}/watchlist")
async def add_title_to_watchlist(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_library=True,
        in_watchlist=True
    )
    return {"title_id": title_id, "in_library": True, "in_watchlist": True}


@router.delete("/{title_id}/watchlist")
async def remove_title_from_watchlist(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        watchlist=False
    )
    return {"title_id": title_id, "watchlist": False}
