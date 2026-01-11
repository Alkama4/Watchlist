from sqlalchemy import select, tuple_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from app import models, schemas
from app.integrations import tmdb


async def _fetch_existing_titles_with_user(
    db: AsyncSession,
    user_id: int,
    tmdb_items: list[tuple[int, models.TitleType]],
):
    utd = aliased(models.UserTitleDetails)

    stmt = (
        select(models.Title, utd)
        .outerjoin(
            utd,
            and_(
                utd.title_id == models.Title.title_id,
                utd.user_id == user_id,
            )
        )
        .where(
            tuple_(models.Title.tmdb_id, models.Title.type).in_(tmdb_items)
        )
    )

    rows = (await db.execute(stmt)).all()

    return {
        (title.tmdb_id, title.type): (title, user_details)
        for title, user_details in rows
    }


async def run_and_process_tmdb_search(
    db: AsyncSession,
    user_id: int,
    data: schemas.TMDBTitleQueryIn,
) -> schemas.TitleListOut:
    
    response = await tmdb.search_multi(
        query=data.query,
        page=data.page
    )

    compact_titles = []

    tmdb_keys = [
        (r["id"], models.TitleType[r["media_type"]])
        for r in response["results"]
        if r.get("media_type") in ("movie", "tv")
    ]

    existing_map = await _fetch_existing_titles_with_user(
        db,
        user_id,
        tmdb_keys,
    )

    for r in response["results"]:
        if r.get("media_type") not in ("movie", "tv"):
            continue

        key = (r["id"], models.TitleType[r["media_type"]])
        title, utd = existing_map.get(key, (None, None))

        compact_titles.append({
            "title_id": title.title_id if title else None,
            "tmdb_id": r["id"],
            "type": r["media_type"],
            "name": r.get("title") or r.get("name"),
            "release_date": r.get("release_date") or r.get("first_air_date"),
            "tmdb_vote_average": r.get("vote_average"),
            "tmdb_vote_count": r.get("vote_count"),
            "default_poster_image_path": r.get("poster_path"),
            "default_backdrop_image_path": r.get("backdrop_path"),
            "user_details": (
                schemas.CompactUserTitleDetailsOut.model_validate(
                    utd, from_attributes=True
                )
                if utd else None
            ),
        })

    return {
        "titles": compact_titles,
        "page_number": response.get("page"),
        "page_size": 20,
        "total_items": response.get("total_results"),
        "total_pages": response.get("total_pages")
    }
