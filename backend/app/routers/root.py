from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.titles.search_internal import run_title_search

router = APIRouter()


@router.get("/home", response_model=schemas.HomeOverviewOut)
async def get_home_overview(
    user: models.User = Depends(get_current_user),
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
            "page_size": 5
        }
    }    
    hero_cards = await run_title_search(
        db,
        user.user_id,
        schemas.TitleQueryIn(**hero_cards_options["filters"])
    )
    hero_cards.header = hero_cards_options["header"]

    # ------ Normal cards ------
    normal_cards_lists_options = [
        {
            "header": "Your Favourites",
            "filters": {
                "is_favourite": True,
                "sort_by": "last_viewed_at"
            }
        },
        {
            "header": "Your Watchlist",
            "filters": {
                "in_watchlist": True,
                "sort_by": "last_viewed_at"
            }
        },
        {
            "header": "Unwatched movies",
            "filters": {
                "watch_status": "not_watched",
                "title_type": "movie",
                "sort_by": "random"
            }
        }
    ]
    normal_cards = []
    for normal_card_list in normal_cards_lists_options:
        title_list = await run_title_search(
            db,
            user.user_id,
            schemas.TitleQueryIn(**normal_card_list["filters"])
        )
        title_list.header = normal_card_list["header"]
        normal_cards.append(title_list)

    return schemas.HomeOverviewOut(
        hero_cards=hero_cards,
        normal_cards=normal_cards
    )
