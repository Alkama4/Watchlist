from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.dependencies import get_db
from app.integrations import tmdb
from app.routers.auth import get_current_user
from app.services.titles.read import fetch_title_with_user_details
from app.services.titles.search_internal import run_title_search
from app.services.titles.search_tmdb import run_and_process_tmdb_search
from app.services.titles.store import store_movie, store_tv
from app.services.titles.user_flags import set_user_title_value, set_title_watch_count

router = APIRouter()


# ---------- SEARCH AND ADD NEW ----------

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


@router.post("/library")
async def add_new_title_to_library(
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

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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
        else:
            raise HTTPException(status_code=400, detail="Invalid title type")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"title_id": updated_title_id, "updated": True}


# ---------- SET TITLE USER DETAILS ----------

@router.put("/{title_id}/library")
async def add_existing_title_to_library(
    title_id: int,
    user: models.User = Depends(get_current_user),
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
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_value(
        db,
        user.user_id,
        title_id,
        in_library=False
    )
    return {"title_id": title_id, "in_library": False}


@router.put("/{title_id}/watch_count")
async def update_title_watch_count(
    title_id: int,
    data: schemas.TitleWatchCountIn,
    user: models.User = Depends(get_current_user),
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


@router.put("/{title_id}/favourite")
async def update_title_favourite_flag(
    title_id: int,
    data: schemas.TitleIsFavouriteIn,
    user: models.User = Depends(get_current_user),
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
    data: schemas.TitleInWatchlistIn,
    user: models.User = Depends(get_current_user),
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


@router.put("/{title_id}/notes")
async def update_title_notes(
    title_id: int,
    data: schemas.TitleNotesIn,
    user: models.User = Depends(get_current_user),
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
