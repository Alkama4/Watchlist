from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.integrations import tmdb
from app.routers.auth import get_current_user
from app.services.titles.read import fetch_title_with_user_details
from app.services.titles.search_internal import run_title_search
from app.services.titles.search_tmdb import run_and_process_tmdb_search
from app.services.titles.store import coordinate_title_fetching
from app.services.titles.user_flags import set_user_title_value, set_title_watch_count
from app.services.titles.preset_searches import fetch_similar_titles
from app.services.images import fetch_image_details, set_user_image_choice
from app.services.languages import check_translation_availability
from app.schemas import (
    LocaleString,
    ImageListsOut,
    ImagePreferenceIn,
    TitleIn,
    TitleLocaleIn,
    TitleWatchCountIn,
    TitleIsFavouriteIn,
    TitleInWatchlistIn,
    TitleNotesIn,
    TMDBTitleQueryIn,
    TitleQueryIn,
    CardTitleOut,
    CardUserTitleDetailsOut,
    TitleListOut,
    TitleOut
)
from app.models import (
    ImageType,
    User,
    Title
)

router = APIRouter()


# ---------- SEARCH AND ADD NEW ----------

@router.post("/search", response_model=TitleListOut)
async def search_for_titles(
    data: TitleQueryIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await run_title_search(
        db, user.user_id, data, CardTitleOut, CardUserTitleDetailsOut
    )


@router.post("/search/tmdb", response_model=TitleListOut)
async def search_for_titles_from_tmdb(
    data: TMDBTitleQueryIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await run_and_process_tmdb_search(db, user.user_id, data)


@router.post("/library")
async def add_new_title_to_library(
    data: TitleIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Title).where(Title.tmdb_id == data.tmdb_id)
    )

    title = existing.scalar_one_or_none()
    if title:
        title_id = title.title_id
    else:
        title_id = await coordinate_title_fetching(
            db=db,
            title_type=data.title_type,
            tmdb_id=data.tmdb_id,
            user_id=user.user_id
        )

    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        in_library=True
    )

    return {
        "title_id": title_id,
        "in_library": True,
    }


# ---------- SPECIFIC TITLE ----------

@router.get("/{title_id}", response_model=TitleOut)
async def get_title_details(
    title_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    title = await fetch_title_with_user_details(db, title_id, user.user_id)
    return title


@router.put("/{title_id}")
async def update_title_details(
    title_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch the existing title by internal ID
    result = await db.execute(select(Title).where(Title.title_id == title_id))
    title = result.scalar_one_or_none()

    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    
    updated_title_id = await coordinate_title_fetching(
        db=db,
        title_type=title.title_type,
        tmdb_id=title.tmdb_id,
        user_id=user.user_id
    )

    return {"title_id": updated_title_id, "updated": True}


# ---------- TITLE USER DETAILS ----------

@router.put("/{title_id}/library")
async def add_existing_title_to_library(
    title_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        in_library=True
    )
    return {"title_id": title_id, "in_library": True}


@router.delete("/{title_id}/library")
async def remove_existing_title_from_library(
    title_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        in_library=False
    )
    return {"title_id": title_id, "in_library": False}


@router.put("/{title_id}/favourite")
async def update_title_favourite_flag(
    title_id: int,
    data: TitleIsFavouriteIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        is_favourite=data.is_favourite,
        in_library=True
    )
    return {
        "title_id": title_id,
        "is_favourite": data.is_favourite,
        "in_library": True
    }


@router.put("/{title_id}/watchlist")
async def update_title_watchlist_flag(
    title_id: int,
    data: TitleInWatchlistIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        in_watchlist=data.in_watchlist,
        in_library=True
    )
    return {
        "title_id": title_id,
        "in_watchlist": data.in_watchlist,
        "in_library": True
    }


@router.put("/{title_id}/watch_count")
async def update_title_watch_count(
    title_id: int,
    data: TitleWatchCountIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_title_watch_count(
        db,
        user.user_id,
        title_id,
        watch_count=data.watch_count,
    )
    return {
        "title_id": title_id,
        "watch_count": data.watch_count,
        "in_library": True
    }


@router.put("/{title_id}/notes")
async def update_title_notes(
    title_id: int,
    data: TitleNotesIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        notes=data.notes,
        in_library=True
    )
    return {
        "title_id": title_id,
        "notes": data.notes,
        "in_library": True
    }


@router.put("/{title_id}/locale")
async def set_title_language_for_user(
    title_id: int,
    data: TitleLocaleIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sets the locale as the prefererred locale for the user and title.
    If the translation doesn't yet exist, it is fetched and stored.
    """
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        chosen_locale=data.locale,
        in_library=True
    )

    translation_exists = await check_translation_availability(
        db=db,
        title_id=title_id,
        iso_639_1=data.locale.split("-")[0]
    )

    if (not translation_exists):
        result = await db.execute(select(Title).where(Title.title_id == title_id))
        title = result.scalar_one_or_none()

        if not title:
            raise HTTPException(status_code=404, detail="Title not found")
        
        await coordinate_title_fetching(
            db=db,
            title_type=title.title_type,
            tmdb_id=title.tmdb_id,
            user_id=user.user_id
        )

    return {
        "title_id": title_id,
        "locale": data.locale,
        "in_library": True
    }


# ---------- IMAGES ----------

@router.get("/{title_id}/images", response_model=ImageListsOut)
async def get_all_title_images(
    title_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_data = await fetch_image_details(db=db, title_id=title_id, user_id=user.user_id)
    return image_data


@router.put("/{title_id}/images/{image_type}")
async def set_title_image_preference(
    title_id: int,
    image_type: ImageType,
    data: ImagePreferenceIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await set_user_image_choice(
        db=db,
        user_id=user.user_id,
        image_type=image_type,
        image_path=data.image_path,
        title_id=title_id
    )


# ---------- MISC/DISCOVERY ----------

@router.get("/{title_id}/similar", response_model=TitleListOut)
async def get_similar_titles(
    title_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    title = await fetch_similar_titles(db, title_id, user.user_id)
    return title
