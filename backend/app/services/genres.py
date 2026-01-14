from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app import models
from app.integrations.tmdb import fetch_genres


async def update_genres(db: AsyncSession, force_update: bool) -> None:
    if not force_update:
        exists = await db.scalar(select(models.Genre.genre_id).limit(1))
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

    insert_stmt = insert(models.Genre).values(records)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=["tmdb_genre_id"],
        set_={
            "genre_name": insert_stmt.excluded.genre_name,
        },
    )

    await db.execute(stmt)
    await db.commit()
