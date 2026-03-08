from sqlalchemy.ext.asyncio import AsyncSession
from app.services.titles.search_internal import run_title_search
from app.schemas import TitleListOut, TitleQueryIn, CardTitleOut, CardUserTitleDetailsOut
from app.models import SortBy


async def fetch_similar_titles(
    db: AsyncSession,
    title_id: int,
    user_id: str,
) -> TitleListOut:
    search_options = {
        "header": "Similar titles",
        "filters": {
            "exclude_title_ids": [title_id],
            "reference_title_id": title_id,
            "sort_by": SortBy.similarity,
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
