from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app import models


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
