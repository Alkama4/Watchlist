from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from app import models, schemas
from app.dependencies import get_db
from app.integrations import tmdb
from app.routers.auth import get_current_user

router = APIRouter()


# ---------- DB STORAGE ----------

async def store_movie(db: AsyncSession, tmdb_data: dict) -> models.Title:
    release_date_str = tmdb_data.get("release_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    movie = models.Title(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["imdb_id"],
        type=models.TitleType.movie,
        name=tmdb_data["title"],
        name_original=tmdb_data["original_title"],
        tagline=tmdb_data["tagline"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        # imdb_vote_average
        # imdb_vote_count
        # age_rating
        overview=tmdb_data["overview"],
        movie_runtime=tmdb_data["runtime"],
        movie_revenue=tmdb_data["revenue"],
        movie_budget=tmdb_data["budget"],
        release_date=release_date,
        original_language=tmdb_data["original_language"],
        origin_country=tmdb_data["origin_country"][0],
        homepage=tmdb_data["homepage"],
    )
    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie.title_id


async def store_tv(db: AsyncSession, tmdb_data: dict) -> models.Title:
    tv = models.Title(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["external_ids"]["imdb_id"],
        type=models.TitleType.tv,
        name=tmdb_data["name"],
        name_original=tmdb_data["original_name"],
        tagline=tmdb_data["tagline"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        overview=tmdb_data["overview"],
        original_language=tmdb_data["original_language"],
        origin_country=",".join(tmdb_data["origin_country"]),
        homepage=tmdb_data["homepage"],
    )
    db.add(tv)
    await db.commit()
    await db.refresh(tv)
    return tv.title_id


async def fetch_and_store_tv_seasons_and_episodes(
    db: AsyncSession,
    title_id: int,
    tmdb_data: dict,
):
    for season in tmdb_data["seasons"]:
        season_data = await tmdb.fetch_tv_season(
            tmdb_data["id"],
            season["season_number"],
        )

        db_season = models.Season(
            title_id=title_id,
            season_number=season["season_number"],
            season_name=season["name"],
            tmdb_vote_average=season["vote_average"],
            overview=season["overview"]
        )
        db.add(db_season)
        db.refresh(db_season)
        await db.flush()

        for ep in season_data["episodes"]:
            air_date_str = ep.get("air_date")
            air_date = datetime.strptime(air_date_str, "%Y-%m-%d").date() if air_date_str else None

            db.add(models.Episode(
                season_id=db_season.season_id,
                title_id=title_id,
                episode_number=ep["episode_number"],
                episode_name=ep["name"],
                tmdb_vote_average=ep["vote_average"],
                tmdb_vote_count=ep["vote_count"],
                overview=ep["overview"],
                air_date=air_date,
                runtime=ep["runtime"]
            ))

    await db.commit()


async def add_title_to_user_watchlist(
    db: AsyncSession,
    title_id: int,
    user: models.User
):
    stmt = insert(models.UserTitleDetails).values(
        user_id=user.user_id,
        title_id=title_id,
        in_watchlist=True
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={"in_watchlist": True}
    )

    await db.execute(stmt)
    await db.commit()


async def remove_title_from_user_watchlist(
    db: AsyncSession,
    title_id: int,
    user: models.User
):
    stmt = (
        update(models.UserTitleDetails)
        .where(
            (models.UserTitleDetails.user_id == user.user_id) 
            & (models.UserTitleDetails.title_id == title_id)
        )
        .values(in_watchlist=False)
    )

    await db.execute(stmt)
    await db.commit()


async def add_title_to_user_favourites(
    db: AsyncSession,
    title_id: int,
    user: models.User
):
    stmt = insert(models.UserTitleDetails).values(
        user_id=user.user_id,
        title_id=title_id,
        in_watchlist=True,
        is_favourite=True
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={
            "in_watchlist": True,
            "is_favourite": True,
        }
    )

    await db.execute(stmt)
    await db.commit()


async def remove_title_from_user_favourites(
    db: AsyncSession,
    title_id: int,
    user: models.User
):
    stmt = (
        update(models.UserTitleDetails)
        .where(
            (models.UserTitleDetails.user_id == user.user_id) 
            & (models.UserTitleDetails.title_id == title_id)
        )
        .values(is_favourite=False)
    )

    await db.execute(stmt)
    await db.commit()


async def add_title_to_users_watch_next(
    db: AsyncSession,
    title_id: int,
    user: models.User
):
    stmt = insert(models.UserTitleDetails).values(
        user_id=user.user_id,
        title_id=title_id,
        in_watchlist=True,
        watch_next=True
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_={
            "in_watchlist": True,
            "watch_next": True,
        }
    )

    await db.execute(stmt)
    await db.commit()


async def remove_title_from_users_watch_next(
    db: AsyncSession,
    title_id: int,
    user: models.User
):
    stmt = (
        update(models.UserTitleDetails)
        .where(
            (models.UserTitleDetails.user_id == user.user_id) 
            & (models.UserTitleDetails.title_id == title_id)
        )
        .values(watch_next=False)
    )

    await db.execute(stmt)
    await db.commit()



# ---------- ROUTER ----------

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

    await add_title_to_user_watchlist(db=db, title_id=title_id, user=user)

    return {
        "title_id": title_id,
        "in_watchlist": True,
    }


@router.put("/{title_id}/watchlist")
async def add_existing_title_to_watchlist(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await add_title_to_user_watchlist(db, title_id, user)
    return {"title_id": title_id, "in_watchlist": True}


@router.delete("/{title_id}/watchlist")
async def remove_existing_title_from_watchlist(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await remove_title_from_user_watchlist(db, title_id, user)
    return {"title_id": title_id, "in_watchlist": False}


@router.put("/{title_id}/favourite")
async def add_title_to_favourites(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await add_title_to_user_favourites(db, title_id, user)
    return {"title_id": title_id, "is_favourite": True, "in_watchlist": True}


@router.delete("/{title_id}/favourite")
async def remove_title_from_favourites(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await remove_title_from_user_favourites(db, title_id, user)
    return {"title_id": title_id, "is_favourite": False}


@router.put("/{title_id}/watch-next")
async def add_title_to_watch_next(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await add_title_to_users_watch_next(db, title_id, user)
    return {"title_id": title_id, "watch_next": True, "in_watchlist": True}


@router.delete("/{title_id}/watch-next")
async def remove_title_from_watch_next(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await remove_title_from_users_watch_next(db, title_id, user)
    return {"title_id": title_id, "watch_next": False}
