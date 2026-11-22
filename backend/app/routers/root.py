from fastapi import APIRouter, Depends
from sqlalchemy import func, case, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.titles.search_internal import run_title_search
from app.services.languages import get_user_language_context
from app.services.genres import update_genres
from app.services.tmdb_collections import fetch_tmdb_collection_cards
from app.schemas import (
    CollectionsOverViewOut,
    TitleListOut,
    TitleQueryIn,
    TitleCardOut,
    TitleCardUserDetailsOut,
    TitleHeroOut,
    TitleHeroUserDetailsOut,
)
from app.models import (
    Title,
    TitleUserDetails,
    User
)
from app.enums import (
    SortBy,
    SortDirection,
    TitleListStyle,
    TitleType
)
router = APIRouter()


async def fetch_title_lists(configs: list, user: User, db: AsyncSession):
    # Fetch the fallback iso here so we don't have to do it for each query
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    lists = []

    for list_config in configs:
        title_list = await run_title_search(
            db,
            user.user_id,
            TitleQueryIn(**list_config["filters"]),
            TitleHeroOut if list_config["style"] is TitleListStyle.hero else TitleCardOut,
            TitleHeroUserDetailsOut if list_config["style"] is TitleListStyle.hero else TitleCardUserDetailsOut,
            locale_ctx
        )
        title_list.header = list_config["header"]
        title_list.style = list_config["style"]

        if (len(title_list.titles) > 0):
            lists.append(title_list)
            
    return lists


@router.get("/home", response_model=list[TitleListOut])
async def get_home_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    configs = [
        {
            "header": "Latest titles",
            "style": TitleListStyle.hero,
            "filters": {
                "sort_by": SortBy.random,
                "is_released": True,
                "watch_status": "not_watched",
                "page_size": 5,
            }
        },
        {
            "header": "In Progress",
            "style": TitleListStyle.banner,
            "filters": {
                "watch_status": "partial",
                "title_type": TitleType.tv,
                "in_watchlist": True,
                "sort_by": SortBy.last_viewed_at,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Recently added Movies",
            "style": TitleListStyle.poster,
            "filters": {
                "title_type": TitleType.movie,
                "sort_by": SortBy.added_at,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Recently added TV-shows",
            "style": TitleListStyle.poster,
            "filters": {
                "title_type": TitleType.tv,
                "sort_by": SortBy.added_at,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
    ]

    return await fetch_title_lists(configs, user, db)


@router.get("/explore", response_model=list[TitleListOut])
async def get_home_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    configs = [
        {
            "header": "Most recent releases",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "sort_by": SortBy.release_date,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Highest rated",
            "style": TitleListStyle.banner,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": SortBy.tmdb_score,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Recently Added",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "sort_by": SortBy.added_at,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Random picks",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": SortBy.random,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Most popular",
            "style": TitleListStyle.banner,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": SortBy.popularity,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Quick movies",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "title_type": "movie",
                "sort_by": SortBy.runtime,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
        {
            "header": "Hidden Gems",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "min_tmdb_rating": 7,
                "sort_by": SortBy.popularity,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
        {
            "header": "Classics from 90s & 00s",
            "style": TitleListStyle.poster,
            "filters": {
                "release_year_min": 1990,
                "release_year_max": 2009,
                "min_tmdb_rating": 7,
                "sort_by": SortBy.popularity,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Critically Acclaimed",
            "style": TitleListStyle.banner,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "min_tmdb_rating": 8,
                "sort_by": SortBy.popularity,
                "sort_direction": SortDirection.desc,
                "page_size": 25
            }
        },
        {
            "header": "Titles you've forgotten",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": SortBy.last_viewed_at,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
        {
            "header": "Time for a rewatch?",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "title_type": TitleType.movie,
                "watch_status": "completed",
                "sort_by": SortBy.last_viewed_at,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
        {
            "header": "Dive back in",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "title_type": TitleType.tv,
                "watch_status": "completed",
                "sort_by": SortBy.last_viewed_at,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
        {
            "header": "Bottom of the barrel",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "min_tmdb_rating": 1,
                "sort_by": SortBy.tmdb_score,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
        {
            "header": "Upcoming",
            "style": TitleListStyle.poster,
            "filters": {
                "is_released": False,
                "sort_by": SortBy.release_date,
                "sort_direction": SortDirection.asc,
                "page_size": 25
            }
        },
    ]

    return await fetch_title_lists(configs, user, db)


@router.get("/collections", response_model=CollectionsOverViewOut)
async def get_collections_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    # ------- Search counts -------
    stats_stmt = (
        select(
            func.count(case((TitleUserDetails.is_favourite == True, 1))).label("is_favourite"),
            func.count(case((TitleUserDetails.in_watchlist == True, 1))).label("in_watchlist"),
            func.count(Title.jellyfin_id).label("has_jellyfin_link"),
            func.count(case((Title.jellyfin_id != None, 1))).label("has_video_assets") 
        )
        .join(TitleUserDetails, Title.title_id == TitleUserDetails.title_id)
        .where(TitleUserDetails.user_id == user.user_id)
    )

    stats_result = await db.execute(stats_stmt)
    stats_row = stats_result.one()

    smart_collection_sizes = {
        "is_favourite": stats_row.is_favourite,
        "in_watchlist": stats_row.in_watchlist,
        "has_jellyfin_link": stats_row.has_jellyfin_link,
        "has_video_assets": stats_row.has_video_assets
    }

    # ------- User collections -------
    user_collections = None

    # ------- TMDB collections -------
    tmdb_collections = await fetch_tmdb_collection_cards(
        db=db,
        user_id=user.user_id,
        locale_ctx=locale_ctx
    )

    return CollectionsOverViewOut(
        smart_collection_sizes=smart_collection_sizes,
        tmdb_collections=tmdb_collections,
        user_collections=user_collections
    )


@router.put("/genres")
async def update_genres_from_tmdb(db: AsyncSession = Depends(get_db)):
    """
    Manually force refresh all genres from TMDB.
    The genres are always fetched on server boot if they are missing.
    """
    await update_genres(db=db, force_update=True)
    return {"status": "ok", "message": "Genres updated successfully"}
