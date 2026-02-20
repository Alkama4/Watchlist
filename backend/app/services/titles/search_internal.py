from datetime import datetime, timezone
from sqlalchemy import select, func, and_, exists, or_, not_
from sqlalchemy.orm import selectinload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type
from app.config import DEFAULT_MAX_QUERY_LIMIT
from app.settings.config import DEFAULT_SETTINGS
from app.services.languages import get_users_global_preferred_locale
from app.models import (
    SortBy,
    SortDirection,
    Title,
    Season,
    Episode,
    TitleTranslation,
    UserSetting,
    UserTitleDetails,
    UserEpisodeDetails,
    TitleGenre
)
from app.schemas import (
    CardTitleOut,
    CardUserTitleDetailsOut,
    HeroTitleOut,
    HeroUserTitleDetailsOut,
    GenreElement,
    AgeRatingElement,
    TitleListOut,
    TitleQueryIn,
)


def _base_title_query(user_id: int, title_schema, fallback_iso_639_1: str):
    stmt = (
        select(Title, UserTitleDetails)
        .outerjoin(
            UserTitleDetails,
            and_(
                UserTitleDetails.title_id == Title.title_id,
                UserTitleDetails.user_id == user_id,
            )
        )
        .outerjoin(
            TitleTranslation,
            and_(
                TitleTranslation.title_id == Title.title_id,
                # Coalesce handles the fallback, split_part splits by '-' and takes the 1st piece
                TitleTranslation.iso_639_1 == func.split_part(
                    func.coalesce(UserTitleDetails.chosen_locale, fallback_iso_639_1), 
                    '-', 
                    1
                )
            )
        )
        .where(UserTitleDetails.in_library == True)
        .options(
            contains_eager(Title.translations)
        )
    )

    if title_schema is HeroTitleOut:
        stmt = stmt.options(
            selectinload(Title.genres)
                .selectinload(TitleGenre.genre),
            selectinload(Title.age_ratings),
        )

    return stmt


def _apply_filters(stmt, q: TitleQueryIn):

    # TODO: setup a smarter search. get rid of special chars and split by space and just try to fit the sections to the name or original name

    if q.query:
        stmt = stmt.where(TitleTranslation.name.ilike(f"%{q.query}%"))

    if q.title_type:
        stmt = stmt.where(Title.title_type == q.title_type)

    if q.is_favourite is not None:
        stmt = stmt.where(UserTitleDetails.is_favourite == q.is_favourite)

    if q.in_watchlist is not None:
        stmt = stmt.where(UserTitleDetails.in_watchlist == q.in_watchlist)

    if q.watch_status is not None:
        if q.watch_status == "not_watched":
            # watch_count is 0 AND all episodes either have 0 or no entry
            episode_subq = (
                select(UserEpisodeDetails.episode_id)
                .join(Episode, Episode.episode_id == UserEpisodeDetails.episode_id)
                .join(Season, Season.season_id == Episode.season_id)
                .where(
                    Season.title_id == Title.title_id,
                    UserEpisodeDetails.user_id == UserTitleDetails.user_id,
                    UserEpisodeDetails.watch_count > 0
                )
            )
            stmt = stmt.where(
                UserTitleDetails.watch_count == 0,
                ~exists(episode_subq)
            )

        elif q.watch_status == "partial":
            # watch_count is 0 but at least one episode has > 0
            episode_subq = (
                select(UserEpisodeDetails.episode_id)
                .join(Episode, Episode.episode_id == UserEpisodeDetails.episode_id)
                .join(Season, Season.season_id == Episode.season_id)
                .where(
                    Season.title_id == Title.title_id,
                    UserEpisodeDetails.user_id == UserTitleDetails.user_id,
                    UserEpisodeDetails.watch_count > 0
                )
            )
            stmt = stmt.where(
                UserTitleDetails.watch_count == 0,
                exists(episode_subq)
            )

        elif q.watch_status == "completed":
            # Subquery: all released episodes of the title
            released_episodes_subq = (
                select(Episode.episode_id)
                .join(Season, Season.season_id == Episode.season_id)
                .where(
                    Season.title_id == Title.title_id,
                    Episode.air_date <= datetime.now(timezone.utc).date()
                )
            ).subquery()

            # Subquery: any released episode not watched (including missing UserEpisodeDetails)
            unwatched_episodes_subq = (
                select(released_episodes_subq.c.episode_id)
                .outerjoin(
                    UserEpisodeDetails,
                    and_(
                        UserEpisodeDetails.episode_id == released_episodes_subq.c.episode_id,
                        UserEpisodeDetails.user_id == UserTitleDetails.user_id
                    )
                )
                .where(
                    or_(
                        UserEpisodeDetails.watch_count == 0,
                        UserEpisodeDetails.watch_count.is_(None)
                    )
                )
            )

            # Completed if either movie watched or no unwatched released episodes exist
            stmt = stmt.where(
                or_(
                    UserTitleDetails.watch_count > 0,
                    ~exists(unwatched_episodes_subq)
                )
            )

    if q.release_year_min:
        stmt = stmt.where(func.extract("year", Title.release_date) >= q.release_year_min)

    if q.release_year_max:
        stmt = stmt.where(func.extract("year", Title.release_date) <= q.release_year_max)

    if q.is_released is not None:
        if q.is_released is True:
            stmt = stmt.where(Title.release_date <= datetime.now(timezone.utc).date())
        elif q.is_released is False:
            stmt = stmt.where(Title.release_date > datetime.now(timezone.utc).date())

    if q.genres_include:
        stmt = stmt.where(
            exists().where(
                and_(
                    TitleGenre.title_id == Title.title_id,
                    TitleGenre.genre_id.in_(q.genres_include)
                )
            )
        )

    if q.genres_exclude:
        stmt = stmt.where(
            not_(
                exists().where(
                    and_(
                        TitleGenre.title_id == Title.title_id,
                        TitleGenre.genre_id.in_(q.genres_exclude)
                    )
                )
            )
        )

    if q.min_tmdb_rating:
        stmt = stmt.where(Title.tmdb_vote_average >= q.min_tmdb_rating)

    if q.min_imdb_rating:
        stmt = stmt.where(Title.imdb_vote_average >= q.min_imdb_rating)

    if q.exclude_title_ids:
        stmt = stmt.where(Title.title_id.notin_(q.exclude_title_ids))

    return stmt


async def _get_user_sort_settings(user_id: int, db) -> dict:
    result = await db.execute(
        select(UserSetting)
        .where(
            UserSetting.user_id == user_id,
            UserSetting.key.in_(["sort_by", "sort_direction"])
        )
    )
    rows = result.scalars().all()
    return {row.key: row.value for row in rows}


async def _apply_sorting_with_user_settings(
    stmt, q: TitleQueryIn, user_id: int, db
):
    sort_by = q.sort_by
    sort_dir = q.sort_direction

    # Load user settings only if the caller asked for "default"
    if sort_by is SortBy.default or sort_dir is SortDirection.default:
        user_settings = await _get_user_sort_settings(user_id, db)

        if sort_by is SortBy.default:
            sort_by = SortBy(user_settings.get(
                "sort_by", DEFAULT_SETTINGS.sort_by
            ))

        if sort_dir is SortDirection.default:
            sort_dir = SortDirection(user_settings.get(
                "sort_direction", DEFAULT_SETTINGS.sort_direction
            ))

    # mapping from enum to column
    sort_map = {
        SortBy.tmdb_score: Title.tmdb_vote_average,
        SortBy.imdb_score: Title.imdb_vote_average,
        SortBy.popularity: Title.tmdb_vote_count,
        SortBy.title_name: TitleTranslation.name,
        SortBy.runtime: Title.movie_runtime,
        SortBy.release_date: Title.release_date,
        SortBy.last_viewed_at: UserTitleDetails.last_viewed_at,
        SortBy.random: func.random()
    }

    col = sort_map.get(sort_by, Title.tmdb_vote_average)
    stmt = stmt.order_by(
        col.desc() if sort_dir is SortDirection.desc else col.asc()
    )
    return stmt


def _add_subqueries(stmt):
    season_count_subq = (
        select(func.count(Season.season_id))
        .where(Season.title_id == Title.title_id)
        .where(Season.season_number != 0)
        .scalar_subquery()
    )

    episode_count_subq = (
        select(func.count(Episode.episode_id))
        .join(Season, Season.season_id == Episode.season_id)
        .where(Season.title_id == Title.title_id)
        .where(Season.season_number != 0)
        .scalar_subquery()
    )

    return stmt.add_columns(
        season_count_subq.label("show_season_count"),
        episode_count_subq.label("show_episode_count")
    )


def _apply_pagination(stmt, q: TitleQueryIn):
    page = q.page_number or 1
    size = q.page_size or DEFAULT_MAX_QUERY_LIMIT
    return stmt.limit(size).offset((page - 1) * size), page, size


def _build_title_list_out(
    rows, total, page, size,
    title_schema: Type[CardTitleOut | HeroTitleOut],
    user_title_details_schema: Type[CardUserTitleDetailsOut | HeroUserTitleDetailsOut]
) -> TitleListOut:
    titles = []

    for title, user_details, season_count, episode_count in rows:

        translation = title.translations[0] if title.translations else None

        # Base data from Title
        title_data = {
            f: getattr(title, f)
            for f in title_schema.model_fields
            if hasattr(title, f) and f not in {"genres", "user_details"}
        }

        # Layer in Translation (Filtered to schema fields)
        if translation:
            title_data.update({
                k: v for k, v in vars(translation).items() 
                if k in title_schema.model_fields and v is not None
            })

        # Add Calculated/Nested fields
        title_data.update({
            "show_season_count": season_count,
            "show_episode_count": episode_count,
            "user_details": user_title_details_schema.model_validate(user_details, from_attributes=True) if user_details else None
        })

        # Hero Specifics
        if title_schema is HeroTitleOut:
            title_data["genres"] = [GenreElement.model_validate(tg.genre, from_attributes=True) for tg in title.genres]
            title_data["age_ratings"] = [AgeRatingElement.model_validate(r, from_attributes=True) for r in title.age_ratings]

        # One-shot Validation
        titles.append(title_schema.model_validate(title_data))

    return TitleListOut(
        titles=titles,
        page_number=page,
        page_size=size,
        total_items=total,
        total_pages=(total + size - 1) // size
    )


async def run_title_search(
    db: AsyncSession,
    user_id: int,
    q: TitleQueryIn,
    title_schema: Type[CardTitleOut | HeroTitleOut],
    user_title_details_schema: Type[CardUserTitleDetailsOut | HeroUserTitleDetailsOut]
) -> TitleListOut:
    fallback_iso_639_1 = await get_users_global_preferred_locale(db, user_id)

    base_stmt = _base_title_query(user_id, title_schema, fallback_iso_639_1)
    base_stmt = _apply_filters(base_stmt, q)

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = await _apply_sorting_with_user_settings(base_stmt, q, user_id, db)
    stmt = _add_subqueries(stmt)
    stmt, page, size = _apply_pagination(stmt, q)

    result = await db.execute(stmt)
    rows = result.unique().all()
    return _build_title_list_out(rows, total, page, size, title_schema, user_title_details_schema)
