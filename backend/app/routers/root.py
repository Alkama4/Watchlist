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
    TitleQueryIn,
    TitleCardOut,
    TitleCardUserDetailsOut,
    TitleHeroOut,
    TitleHeroUserDetailsOut,
    HomeOverviewOut
)
from app.models import (
    Title,
    TitleUserDetails,
    User
)

router = APIRouter()


@router.get("/home", response_model=HomeOverviewOut)
async def get_home_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return a curated overview of titles for the authenticated user.
    """

    # Fetch the fallback iso here so we don't have to do it for each query
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    # ------ Hero cards ------
    hero_cards_options = {
        "header": "Latest titles",
        "filters": {
            "sort_by": "release_date",
            "sort_direction": "desc",
            "is_released": True,
            "page_size": 5
        }
    }
    hero_cards = await run_title_search(
        db,
        user.user_id,
        TitleQueryIn(**hero_cards_options["filters"]),
        TitleHeroOut,
        TitleHeroUserDetailsOut,
        locale_ctx
    )
    hero_cards.header = hero_cards_options["header"]

    # ------ Normal cards ------
    normal_cards_lists_options = [
        {
            "header": "Continue watching",
            "filters": {
                "watch_status": "partial",
                "title_type": "tv",
                "in_watchlist": True,
                "sort_by": "last_viewed_at",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Random picks",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": "random",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Highest rated",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": "tmdb_score",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Most popular",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": "popularity",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Quick movies",
            "filters": {
                "is_released": True,
                "title_type": "movie",
                "sort_by": "runtime",
                "sort_direction": "asc",
                "page_size": 25
            }
        },
        {
            "header": "Hidden Gems",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "min_tmdb_rating": 7,
                "sort_by": "popularity",
                "sort_direction": "asc",
                "page_size": 25
            }
        },
        {
            "header": "Classics from 90s & 00s",
            "filters": {
                "release_year_min": 1990,
                "release_year_max": 2009,
                "min_tmdb_rating": 7,
                "sort_by": "popularity",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Critically Acclaimed",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "min_tmdb_rating": 8,
                "sort_by": "popularity",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Recently Added",
            "filters": {
                "is_released": True,
                "sort_by": "added_at",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Titles you've forgotten",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "sort_by": "last_viewed_at",
                "sort_direction": "asc",
                "page_size": 25
            }
        },
        {
            "header": "Bottom of the barrel",
            "filters": {
                "is_released": True,
                "watch_status": "not_watched",
                "min_tmdb_rating": 1,
                "sort_by": "tmdb_score",
                "sort_direction": "asc",
                "page_size": 25
            }
        },
        {
            "header": "Dive back in",
            "filters": {
                "is_released": True,
                "watch_status": "completed",
                "sort_by": "last_viewed_at",
                "sort_direction": "asc",
                "page_size": 25
            }
        },
        {
            "header": "Just released",
            "filters": {
                "is_released": True,
                "sort_by": "release_date",
                "sort_direction": "desc",
                "page_size": 25
            }
        },
        {
            "header": "Upcoming",
            "filters": {
                "is_released": False,
                "sort_by": "release_date",
                "sort_direction": "asc",
                "page_size": 25
            }
        },
    ]
    normal_cards = []
    for normal_card_list in normal_cards_lists_options:
        title_list = await run_title_search(
            db,
            user.user_id,
            TitleQueryIn(**normal_card_list["filters"]),
            TitleCardOut,
            TitleCardUserDetailsOut,
            locale_ctx
        )
        title_list.header = normal_card_list["header"]

        if (len(title_list.titles) > 0):
            normal_cards.append(title_list)

    return HomeOverviewOut(
        hero_cards=hero_cards,
        normal_cards=normal_cards
    )


@router.get("/collections", response_model=CollectionsOverViewOut)
async def get_home_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    # ------- Search counts -------
    stats_stmt = (
        select(
            func.count(case((TitleUserDetails.is_favourite == True, 1))).label("is_favourite"),
            func.count(case((TitleUserDetails.in_watchlist == True, 1))).label("in_watchlist"),
            func.count(Title.jellyfin_id).label("jellyfin_link"),
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
        "jellyfin_link": stats_row.jellyfin_link,
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
