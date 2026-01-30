from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.titles.search_internal import run_title_search
from app.schemas import TitleListOut, TitleQueryIn, CardTitleOut, CardUserTitleDetailsOut
from app.models import SortBy, TitleGenre


async def fetch_similar_titles(
    db: AsyncSession,
    title_id: int,
    user_id: str,
) -> TitleListOut:

    result = await db.execute(
        select(TitleGenre.genre_id)
        .where(TitleGenre.title_id == title_id)
    )
    genre_ids = [row.genre_id for row in result.all()]

    search_options = {
        "header": "Similar titles",
        "filters": {
            "exclude_title_ids": [title_id],
            "genres_include": genre_ids,
            "sort_by": SortBy.last_viewed_at,
        }
    }

    similar_titles = await run_title_search(
        db,
        user_id,
        TitleQueryIn(**search_options["filters"]),
        CardTitleOut,
        CardUserTitleDetailsOut
    )
    similar_titles.header = search_options["header"]

    return similar_titles
