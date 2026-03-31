from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import(
    TMDBCollection
)

async def init_tmdb_collection(db: AsyncSession, tmdb_collection_info: dict):
    tmdb_collection_id = tmdb_collection_info.get("id")
    
    stmt = insert(TMDBCollection).values(
        tmdb_collection_id=tmdb_collection_id,
        name_original=tmdb_collection_info.get("name")
    ).on_conflict_do_nothing()

    await db.execute(stmt)
