from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import (
    Title,
    UserTitleDetails,
    ImageLink,
    ImageType,
    Image
)
from app.schemas import (
    ImageListsOut,
    ImageOut
)


def select_best_image(images: List[Dict], iso_639_1_list: List[Optional[str]]) -> Optional[str]:
    """
    Selects the best image based on vote_average * vote_count, trying ISO codes in order,
    and returns the file path of that image.
    
    :param images: List of image dictionaries.
    :param iso_639_1_list: Ordered list of language codes to try (use None for "no-language").
    :return: The file path of the best image or None if no match.
    """
    for iso in iso_639_1_list:
        # If iso is None, look only at images whose iso_639_1 field is actually missing/None
        if iso is None:
            candidates = [img for img in images if img.get("iso_639_1") is None]
        else:
            candidates = [img for img in images if img.get("iso_639_1") == iso]

        if candidates:
            best_image = max(candidates, key=lambda img: (img.get("vote_average") or 0))
            return best_image.get("file_path")
    return None


async def store_image_details(
    db: AsyncSession, 
    title_id: int = None, 
    season_id: int = None, 
    episode_id: int = None, 
    images: dict = None
):
    if not images:
        return

    type_map = {
        "backdrops": ImageType.backdrop,
        "posters": ImageType.poster,
        "logos": ImageType.logo,
    }

    # Use dictionaries keyed by unique identifiers to prevent batch duplicates
    image_data_map = {}
    link_data_map = {}

    for key, img_type in type_map.items():
        for img in images.get(key, []):
            path = img["file_path"]
            
            if path not in image_data_map:
                image_data_map[path] = {
                    "file_path": path,
                    "type": img_type,
                    "width": img.get("width"),
                    "height": img.get("height"),
                    "iso_3166_1": img.get("iso_3166_1"),
                    "iso_639_1": img.get("iso_639_1"),
                    "vote_average": img.get("vote_average"),
                    "vote_count": img.get("vote_count")
                }

            episode_id = img.get("episode_id")
            
            # Create a unique key for the link to prevent duplicates in the batch
            link_key = (path, title_id, season_id, episode_id)
            
            if link_key not in link_data_map:
                link_data_map[link_key] = {
                    "file_path": path,
                    "title_id": title_id,
                    "season_id": season_id,
                    "episode_id": episode_id
                }

    # Convert maps back to lists for SQLAlchemy
    image_records = list(image_data_map.values())
    link_records = list(link_data_map.values())

    if image_records:
        image_stmt = insert(Image).values(image_records)
        image_stmt = image_stmt.on_conflict_do_update(
            index_elements=["file_path"],
            set_={
                "vote_average": image_stmt.excluded.vote_average,
                "vote_count": image_stmt.excluded.vote_count,
                "width": image_stmt.excluded.width,
                "height": image_stmt.excluded.height,
            }
        )
        await db.execute(image_stmt)

    if link_records:
        link_stmt = insert(ImageLink).values(link_records)
        link_stmt = link_stmt.on_conflict_do_nothing(
            constraint="uix_image_link_identity" 
        )
        await db.execute(link_stmt)

    await db.commit()


async def fetch_title_images(db: AsyncSession, title_id: int, user_id: int) -> ImageListsOut:
    stmt = (
        select(Title, UserTitleDetails)
        .outerjoin(UserTitleDetails, (UserTitleDetails.title_id == Title.title_id) & (UserTitleDetails.user_id == user_id))
        .where(Title.title_id == title_id)
    )
    title_res = await db.execute(stmt)
    row = title_res.first()
    
    if not row:
        return ImageListsOut(title_id=title_id)

    title_obj, user_details = row

    # Store paths for quick comparison
    defaults = {
        title_obj.default_poster_image_path,
        title_obj.default_backdrop_image_path,
        title_obj.default_logo_image_path
    }
    user_choices = set()
    if user_details:
        user_choices = {
            user_details.chosen_poster_image_path,
            user_details.chosen_backdrop_image_path,
            user_details.chosen_logo_image_path
        }

    # Fetch all images linked to this title
    img_stmt = (
        select(Image)
        .join(ImageLink, Image.file_path == ImageLink.file_path)
        .where(ImageLink.title_id == title_id)
        .order_by(Image.vote_average.desc())
    )
    img_res = await db.execute(img_stmt)
    images = img_res.scalars().all()

    response = ImageListsOut(title_id=title_id)

    for img in images:
        img_data = ImageOut(
            file_path=img.file_path,
            type=img.type,
            width=img.width,
            height=img.height,
            iso_3166_1=img.iso_3166_1,
            iso_639_1=img.iso_639_1,
            vote_average=float(img.vote_average) if img.vote_average else 0.0,
            vote_count=img.vote_count,
            is_default=img.file_path in defaults,
            is_user_choise=img.file_path in user_choices
        )

        if img.type == ImageType.poster:
            response.posters.append(img_data)
        elif img.type == ImageType.backdrop:
            response.backdrops.append(img_data)
        elif img.type == ImageType.logo:
            response.logos.append(img_data)

    return response
