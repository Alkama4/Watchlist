from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.integrations.tmdb import fetch_genres
from app.models import (
    Genre,
    TitleGenre
)

async def update_genres(db: AsyncSession, force_update: bool) -> None:
    if not force_update:
        exists = await db.scalar(select(Genre.tmdb_genre_id).limit(1))
        if exists:
            return

    genres = await fetch_genres()

    if not genres:
        raise RuntimeError("No genres fetched from TMDB")

    records = [
        {
            "tmdb_genre_id": genre["id"],
            "genre_name": genre["name"],
        }
        for genre in genres
    ]

    insert_stmt = insert(Genre).values(records)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=["tmdb_genre_id"],
        set_={
            "genre_name": insert_stmt.excluded.genre_name,
        },
    )

    await db.execute(stmt)
    await db.commit()


async def store_title_genres(db: AsyncSession, genres: list, title_id: int):
    records = [
        {
            "genre_id": genre["id"],
            "title_id": title_id
        }
        for genre in genres
    ]

    stmt = insert(TitleGenre).values(records).on_conflict_do_nothing(
        index_elements=["title_id", "genre_id"]
    )

    await db.execute(stmt)
    await db.commit()
