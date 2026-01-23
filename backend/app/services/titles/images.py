from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models import (
    ImageType,
    Image
)


def select_best_image(images: List[Dict], iso_639_1_list: List[Optional[str]]) -> Optional[str]:
    """
    Selects the best image based on vote_average * vote_count, trying ISO codes in order,
    and returns the file path of that image.
    
    :param images: List of image dictionaries.
    :param iso_639_1_list: Ordered list of language codes to try (use None for no language filter).
    :return: The file path of the best image or None if no match.
    """
    for iso in iso_639_1_list:
        candidates = [img for img in images if iso is None or img.get("iso_639_1") == iso]
        if candidates:
            best_image = max(candidates, key=lambda img: (img.get("vote_average") or 0))
            return best_image.get("file_path")
    return None


async def store_image_details(db: AsyncSession, title_id: int = None, season_id: int = None, episode_id: int = None, images: dict = None):
    if not images:
        return

    type_fk_map = {
        "backdrops": {"type": ImageType.backdrop, "fk": {"title_id": title_id, "season_id": None}},
        "posters": {"type": ImageType.poster, "fk": {"title_id": title_id, "season_id": season_id}},
        "logos": {"type": ImageType.logo, "fk": {"title_id": title_id, "season_id": None}},
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

    insert_stmt = insert(Image).values(image_records)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=["file_path"],
        set_={
            "vote_average": insert_stmt.excluded.vote_average,
            "vote_count": insert_stmt.excluded.vote_count
        }
    )

    await db.execute(stmt)
    await db.commit()
