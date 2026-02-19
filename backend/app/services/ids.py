from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Season

async def get_title_id_by_season_id(db: AsyncSession, season_id: int) -> int | None:
    """Returns the title_id associated with a specific season_id."""
    stmt = select(Season.title_id).where(Season.season_id == season_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
