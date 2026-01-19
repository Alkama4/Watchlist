from sqlalchemy import select, func, and_
from sqlalchemy.orm import aliased, selectinload
from app import models, schemas
from app.config import DEFAULT_MAX_QUERY_LIMIT
from app.settings.config import DEFAULT_SETTINGS


def _base_title_query(user_id: int, utd):
    stmt = (
        select(models.Title, utd)
            .outerjoin(
                utd,
                and_(
                    utd.title_id == models.Title.title_id,
                    utd.user_id == user_id,
                )
            )
            .where(utd.in_library == True)

            # Load the many‑to‑many link and the Genre it points to
            .options(
                selectinload(models.Title.genres)
                    .selectinload(models.TitleGenre.genre)
            )
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

    if q.is_released is not None:
        if q.is_released is True:
            stmt = stmt.where(models.Title.release_date <= datetime.now(timezone.utc).date())
        elif q.is_released is False:
            stmt = stmt.where(models.Title.release_date > datetime.now(timezone.utc).date())

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
        # Build a dict that omits the relationship fields
        data = {
            f: getattr(title, f)
            for f in schemas.CompactTitleOut.model_fields
            if hasattr(title, f) and f not in {"genres", "user_details"}
        }

        out = schemas.CompactTitleOut.model_validate(data)

        # Convert the TitleGenre, Genre chain into plain names
        out.genres = [tg.genre.genre_name for tg in title.genres] or []

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
