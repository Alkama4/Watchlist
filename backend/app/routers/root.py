from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.titles.search_internal import run_title_search
from app.services.genres import update_genres
from app.schemas import (
    TitleQueryIn,
    HomeOverviewOut
)
from app.models import (
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

    # ------ Hero cards ------
    hero_cards_options = {
        "header": "Latest titles",
        "filters": {
            "sort_by": "release_date",
            "is_released": True,
            "page_size": 5
        }
    }    
    hero_cards = await run_title_search(
        db,
        user.user_id,
        TitleQueryIn(**hero_cards_options["filters"])
    )
    hero_cards.header = hero_cards_options["header"]

    # ------ Normal cards ------
    normal_cards_lists_options = [
        {
            "header": "Continue watching",
            "filters": {
                "watch_status": "partial",
                "title_type": "tv",
                "sort_by": "last_viewed_at",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Random picks",
            "filters": {
                "watch_status": "not_watched",
                "sort_by": "random",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Highest rated",
            "filters": {
                "watch_status": "not_watched",
                "sort_by": "tmdb_score",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Most popular",
            "filters": {
                "watch_status": "not_watched",
                "sort_by": "popularity",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Your Favourites",
            "filters": {
                "is_favourite": True,
                "sort_by": "last_viewed_at",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Your Watchlist",
            "filters": {
                "in_watchlist": True,
                "sort_by": "last_viewed_at",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Short movies you have time for",
            "filters": {
                "title_type": "movie",
                "sort_by": "runtime",
                "sort_direction": "asc"
            }
        },
        {
            "header": "Just released",
            "filters": {
                "is_released": True,
                "sort_by": "release_date",
                "sort_direction": "desc"
            }
        },
        {
            "header": "Upcoming",
            "filters": {
                "is_released": False,
                "sort_by": "release_date",
                "sort_direction": "asc"
            }
        },
        {
            "header": "Titles you've forgotten",
            "filters": {
                "watch_status": "not_watched",
                "sort_by": "last_viewed_at",
                "sort_direction": "asc"
            }
        },
        {
            "header": "Time for a rewatch?",
            "filters": {
                "watch_status": "completed",
                "sort_by": "last_viewed_at",
                "sort_direction": "asc"
            }
        },
    ]
    normal_cards = []
    for normal_card_list in normal_cards_lists_options:
        title_list = await run_title_search(
            db,
            user.user_id,
            TitleQueryIn(**normal_card_list["filters"])
        )
        title_list.header = normal_card_list["header"]

        if (len(title_list.titles) > 0):
            normal_cards.append(title_list)

    return HomeOverviewOut(
        hero_cards=hero_cards,
        normal_cards=normal_cards
    )


@router.put("/genres")
async def update_genres_from_tmdb(db: AsyncSession = Depends(get_db)):
    """
    Manually force refresh all genres from TMDB.
    The genres are always fetched on server boot if they are missing.
    """
    await update_genres(db=db, force_update=True)
    return {"status": "ok", "message": "Genres updated successfully"}
