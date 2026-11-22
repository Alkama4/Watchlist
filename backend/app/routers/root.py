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


@router.get("/home", response_model=list[TitleListOut])
async def get_home_overview(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch the fallback iso here so we don't have to do it for each query
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    list_configs = [
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
            "header": "Continue watching",
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

    cards = []
    for list_config in list_configs:
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
            cards.append(title_list)

    return cards


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
