from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from datetime import datetime
from app import models, schemas
from app.dependencies import get_db
from app.integrations import tmdb
from app.routers.auth import get_current_user

router = APIRouter()


# ---------- DB STORAGE ----------

async def store_movie(db: AsyncSession, tmdb_data: dict) -> int:
    release_date_str = tmdb_data.get("release_date")
    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

    stmt = insert(models.Title).values(
        tmdb_id=tmdb_data["id"],
        imdb_id=tmdb_data["imdb_id"],
        type=models.TitleType.movie,
        name=tmdb_data["title"],
        name_original=tmdb_data["original_title"],
        tagline=tmdb_data["tagline"],
        tmdb_vote_average=tmdb_data["vote_average"],
        tmdb_vote_count=tmdb_data["vote_count"],
        ##### These aren't from TMDB #####
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
    ).on_conflict_do_update(
        index_elements=["tmdb_id"],
        set_={
            "name": tmdb_data["title"],
            "name_original": tmdb_data["original_title"],
            "tagline": tmdb_data["tagline"],
            "tmdb_vote_average": tmdb_data["vote_average"],
            "tmdb_vote_count": tmdb_data["vote_count"],
            "overview": tmdb_data["overview"],
            "movie_runtime": tmdb_data["runtime"],
            "movie_revenue": tmdb_data["revenue"],
            "movie_budget": tmdb_data["budget"],
            "release_date": release_date,
            "original_language": tmdb_data["original_language"],
            "origin_country": tmdb_data["origin_country"][0],
            "homepage": tmdb_data["homepage"],
        }
    ).returning(models.Title.title_id)

    result = await db.execute(stmt)
    title_id = result.scalar_one()
    await db.commit()

    await store_image_details(db=db, title_id=title_id, images=tmdb_data["images"])

    return title_id


async def store_tv(db: AsyncSession, tmdb_data: dict) -> int:
    stmt = insert(models.Title).values(
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
    ).on_conflict_do_update(
        index_elements=["tmdb_id"],
        set_={
            "name": tmdb_data["name"],
            "name_original": tmdb_data["original_name"],
            "tagline": tmdb_data["tagline"],
            "tmdb_vote_average": tmdb_data["vote_average"],
            "tmdb_vote_count": tmdb_data["vote_count"],
            "overview": tmdb_data["overview"],
            "original_language": tmdb_data["original_language"],
            "origin_country": ",".join(tmdb_data["origin_country"]),
            "homepage": tmdb_data["homepage"],
        }
    ).returning(models.Title.title_id)

    result = await db.execute(stmt)
    title_id = result.scalar_one()
    await db.commit()

    await store_image_details(db=db, title_id=title_id, images=tmdb_data["images"])

    # Fetch seasons and episodes
    await fetch_and_store_tv_seasons_and_episodes(db, title_id, tmdb_data)
    return title_id


async def fetch_and_store_tv_seasons_and_episodes(db: AsyncSession, title_id: int, tmdb_data: dict):
    for season in tmdb_data.get("seasons", []):
        # Fetch full season data
        season_data = await tmdb.fetch_tv_season(tmdb_data["id"], season["season_number"])

        # Upsert season
        stmt = insert(models.Season).values(
            title_id=title_id,
            season_number=season["season_number"],
            season_name=season.get("name"),
            tmdb_vote_average=season.get("vote_average"),
            overview=season.get("overview")
        ).on_conflict_do_update(
            index_elements=["title_id", "season_number"],
            set_={
                "season_name": season.get("name"),
                "tmdb_vote_average": season.get("vote_average"),
                "overview": season.get("overview")
            }
        ).returning(models.Season.season_id)

        result = await db.execute(stmt)
        season_id = result.scalar_one()
        await db.flush()

        # Store season images
        await store_image_details(db=db, season_id=season_id, images=season_data.get("images", {}))

        # Accumulate episode images
        episode_images = []

        for ep in season_data.get("episodes", []):
            air_date_str = ep.get("air_date")
            air_date = datetime.strptime(air_date_str, "%Y-%m-%d").date() if air_date_str else None

            # Upsert episode
            stmt = insert(models.Episode).values(
                season_id=season_id,
                title_id=title_id,
                episode_number=ep["episode_number"],
                episode_name=ep.get("name"),
                tmdb_vote_average=ep.get("vote_average"),
                tmdb_vote_count=ep.get("vote_count"),
                overview=ep.get("overview"),
                air_date=air_date,
                runtime=ep.get("runtime")
            ).on_conflict_do_update(
                index_elements=["season_id", "episode_number"],
                set_={
                    "episode_name": ep.get("name"),
                    "tmdb_vote_average": ep.get("vote_average"),
                    "tmdb_vote_count": ep.get("vote_count"),
                    "overview": ep.get("overview"),
                    "air_date": air_date,
                    "runtime": ep.get("runtime")
                }
            ).returning(models.Episode.episode_id)

            result = await db.execute(stmt)
            episode_id = result.scalar_one()

            # Collect episode backdrop if available
            still_path = ep.get("still_path")
            if still_path:
                episode_images.append({
                    "file_path": still_path,
                    "episode_id": episode_id,
                    "type": models.ImageType.backdrop
                })

        # Batch store episode images
        if episode_images:
            await store_image_details(db=db, images={"backdrops": episode_images})

    await db.commit()


async def store_image_details(db: AsyncSession, title_id: int = None, season_id: int = None, episode_id: int = None, images: dict = None):
    if not images:
        return

    type_fk_map = {
        "backdrops": {"type": models.ImageType.backdrop, "fk": {"title_id": title_id, "season_id": None}},
        "posters": {"type": models.ImageType.poster, "fk": {"title_id": title_id, "season_id": season_id}},
        "logos": {"type": models.ImageType.logo, "fk": {"title_id": title_id, "season_id": None}},
    }

    image_records = []

    for key, meta in type_fk_map.items():
        for img in images.get(key, []):
            record = {
                "file_path": img["file_path"],
                "type": meta["type"],
                "title_id": meta["fk"]["title_id"],
                "season_id": meta["fk"]["season_id"],
                "episode_id": img.get("episode_id"),
                "width": img.get("width"),
                "height": img.get("height"),
                "iso_3166_1": img.get("iso_3166_1"),
                "iso_639_1": img.get("iso_639_1"),
                "vote_average": img.get("vote_average"),
                "vote_count": img.get("vote_count")
            }
            image_records.append(record)

    if not image_records:
        return

    insert_stmt = insert(models.Image).values(image_records)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=["file_path"],
        set_={
            "vote_average": insert_stmt.excluded.vote_average,
            "vote_count": insert_stmt.excluded.vote_count
        }
    )

    await db.execute(stmt)
    await db.commit()


# ---------- SET FLAGS ----------

async def set_user_title_flags(
    db: AsyncSession,
    user_id: int,
    title_id: int,
    **flags: bool
):
    stmt = insert(models.UserTitleDetails).values(
        user_id=user_id,
        title_id=title_id,
        **flags
    ).on_conflict_do_update(
        index_elements=["user_id", "title_id"],
        set_=flags
    )

    await db.execute(stmt)
    await db.commit()


# ---------- FETCHING TITLES ----------

async def fetch_title_with_user_details(db: AsyncSession, title_id: int, user_id: int) -> schemas.TitleOut:
    # Fetch title with seasons and episodes
    result = await db.execute(
        select(models.Title)
        .where(models.Title.title_id == title_id)
        .options(
            selectinload(models.Title.seasons.and_(models.Season.season_number != 0))
            .selectinload(models.Season.episodes)
        )
    )
    title = result.scalar_one_or_none()
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    # Fetch all user-specific details in bulk
    user_title = await db.get(models.UserTitleDetails, {"user_id": user_id, "title_id": title_id})
    
    season_ids = [s.season_id for s in title.seasons]
    episode_ids = [e.episode_id for s in title.seasons for e in s.episodes]

    season_details_map = {
        d.season_id: d
        for d in (await db.execute(
            select(models.UserSeasonDetails)
            .where(models.UserSeasonDetails.user_id == user_id)
            .where(models.UserSeasonDetails.season_id.in_(season_ids))
        )).scalars()
    }

    episode_details_map = {
        d.episode_id: d
        for d in (await db.execute(
            select(models.UserEpisodeDetails)
            .where(models.UserEpisodeDetails.user_id == user_id)
            .where(models.UserEpisodeDetails.episode_id.in_(episode_ids))
        )).scalars()
    }

    return build_title_out(title, user_title, season_details_map, episode_details_map)


def build_title_out(
    title: models.Title,
    user_title: Optional[models.UserTitleDetails],
    season_details_map: dict[int, models.UserSeasonDetails],
    episode_details_map: dict[int, models.UserEpisodeDetails],
) -> schemas.TitleOut:
    # Base TitleOut
    title_out = schemas.TitleOut.model_validate(title)

    # Attach user title details
    title_out.user_details = schemas.UserTitleDetailsOut.model_validate(user_title, from_attributes=True) if user_title else None

    # Attach user season and episode details
    for season in title_out.seasons:
        season.user_details = schemas.UserSeasonDetailsOut.model_validate(
            season_details_map.get(season.season_id)
        ) if season_details_map.get(season.season_id) else None

        for episode in season.episodes:
            episode.user_details = schemas.UserEpisodeDetailsOut.model_validate(
                episode_details_map.get(episode.episode_id)
            ) if episode_details_map.get(episode.episode_id) else None

    return title_out


# ---------- ROUTER ENDPOINTS ----------

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

    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_watchlist=True
    )

    return {
        "title_id": title_id,
        "in_watchlist": True,
    }


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
            await fetch_and_store_tv_seasons_and_episodes(db, updated_title_id, tmdb_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid title type")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"title_id": updated_title_id, "updated": True}


@router.put("/{title_id}/watchlist")
async def add_existing_title_to_watchlist(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_watchlist=True
    )
    return {"title_id": title_id, "in_watchlist": True}


@router.delete("/{title_id}/watchlist")
async def remove_existing_title_from_watchlist(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        in_watchlist=False
    )
    return {"title_id": title_id, "in_watchlist": False}


@router.put("/{title_id}/favourite")
async def add_title_to_favourites(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        is_favourite=True,
        in_watchlist=True
    )
    return {"title_id": title_id, "is_favourite": True, "in_watchlist": True}


@router.delete("/{title_id}/favourite")
async def remove_title_from_favourites(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        is_favourite=False
    )
    return {"title_id": title_id, "is_favourite": False}


@router.put("/{title_id}/watch-next")
async def add_title_to_watch_next(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        watch_next=True,
        in_watchlist=True
    )
    return {"title_id": title_id, "watch_next": True, "in_watchlist": True}


@router.delete("/{title_id}/watch-next")
async def remove_title_from_watch_next(
    title_id: int,
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await set_user_title_flags(
        db,
        user.user_id,
        title_id,
        watch_next=False
    )
    return {"title_id": title_id, "watch_next": False}
