from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import (
    Episode,
    Season,
    Title,
    UserSeasonDetails,
    UserTitleDetails,
    ImageLink,
    ImageType,
    Image
)
from app.schemas import (
    ImageListOut,
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


async def fetch_image_details(
    db: AsyncSession, 
    user_id: int, 
    title_id: int = None, 
    season_id: int = None, 
    episode_id: int = None
) -> ImageListsOut:
    
    # 1. Configuration Mapping
    # Maps the provided ID type to its specific Models and known default/choice fields
    CONFIG = {
        "title_id": {
            "val": title_id,
            "model": Title,
            "user_model": UserTitleDetails,
            "pk": Title.title_id,
            "user_pk": UserTitleDetails.title_id,
            "path_fields": ["default_poster_image_path", "default_backdrop_image_path", "default_logo_image_path"],
            "user_fields": ["chosen_poster_image_path", "chosen_backdrop_image_path", "chosen_logo_image_path"]
        },
        "season_id": {
            "val": season_id,
            "model": Season,
            "user_model": UserSeasonDetails,
            "pk": Season.season_id,
            "user_pk": UserSeasonDetails.season_id,
            "path_fields": ["default_poster_image_path"],
            "user_fields": ["chosen_poster_image_path"]
        },
        "episode_id": {
            "val": episode_id,
            "model": Episode, # Assuming Episode model exists
            "user_model": None, # Add UserEpisodeDetails if you have it
            "pk": Episode.episode_id,
            "user_pk": None,
            "path_fields": ["default_poster_image_path"],
            "user_fields": []
        }
    }

    # Determine which context we are in
    active_key = next((k for k, v in CONFIG.items() if v["val"] is not None), None)
    if not active_key:
        raise ValueError("One of title_id, season_id, or episode_id must be provided.")
    
    cfg = CONFIG[active_key]
    val = cfg["val"]

    # 2. Fetch Main Object and User Details
    stmt = select(cfg["model"])
    if cfg["user_model"]:
        stmt = stmt.add_columns(cfg["user_model"]).outerjoin(
            cfg["user_model"], 
            (cfg["user_pk"] == cfg["pk"]) & (cfg["user_model"].user_id == user_id)
        )
    
    stmt = stmt.where(cfg["pk"] == val)
    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return ImageListsOut(**{active_key: val}, posters=ImageListOut(total_count=0), 
                             backdrops=ImageListOut(total_count=0), logos=ImageListOut(total_count=0))

    # row might be (Object,) or (Object, UserDetails)
    main_obj = row[0]
    user_details = row[1] if len(row) > 1 else None

    # 3. Collect Defaults and Choices using getattr
    defaults = {getattr(main_obj, field, None) for field in cfg["path_fields"]}
    user_choices = set()
    if user_details:
        user_choices = {getattr(user_details, field, None) for field in cfg["user_fields"]}

    # 4. Fetch Linked Images
    # Dynamically filter ImageLink by the active ID (e.g., ImageLink.title_id == val)
    img_stmt = (
        select(Image)
        .join(ImageLink, Image.file_path == ImageLink.file_path)
        .where(getattr(ImageLink, active_key) == val)
        .order_by(Image.vote_average.desc())
    )
    img_res = await db.execute(img_stmt)
    images = img_res.scalars().all()

    # 5. Categorization Logic (Same as before)
    categories = {
        ImageType.poster: {"imgs": [], "locales": set()},
        ImageType.backdrop: {"imgs": [], "locales": set()},
        ImageType.logo: {"imgs": [], "locales": set()},
    }

    for img in images:
        current_locale = (f"{img.iso_639_1}-{img.iso_3166_1}" 
                         if img.iso_639_1 and img.iso_3166_1 
                         else img.iso_639_1 or img.iso_3166_1)
        
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
            is_user_choice=img.file_path in user_choices
        )

        cat = categories.get(img.type)
        if cat:
            cat["imgs"].append(img_data)
            cat["locales"].add(current_locale)

    def build_list_out(img_type: ImageType) -> ImageListOut:
        data = categories[img_type]
        sorted_locales = sorted(list(data["locales"]), key=lambda x: (x is not None, x))
        return ImageListOut(total_count=len(data["imgs"]), available_locale=sorted_locales, images=data["imgs"])

    return ImageListsOut(
        **{active_key: val},
        posters=build_list_out(ImageType.poster),
        backdrops=build_list_out(ImageType.backdrop),
        logos=build_list_out(ImageType.logo)
    )