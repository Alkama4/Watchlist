from typing import List, Optional, Dict
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.services.languages import get_user_title_locale
from app.services.ids import get_title_id_by_season_id
from app.models import (
    SeasonTranslation,
    TitleTranslation,
    UserEpisodeDetails,
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
    Selects the best image based on vote_average, trying ISO codes in order,
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
    season_id: int = None
) -> ImageListsOut:
    
    if not title_id:
        locale_title_id = await get_title_id_by_season_id(db=db, season_id=season_id)
    else:
        locale_title_id = title_id
    title_locale = await get_user_title_locale(db=db, user_id=user_id, title_id=locale_title_id)
    chosen_iso_639_1 = title_locale.split("-")[0]
    
    # 1. Configuration Mapping
    CONFIG = {
        "title_id": {
            "val": title_id,
            "model": TitleTranslation,
            "user_model": UserTitleDetails,
            "pk": TitleTranslation.title_id,
            "user_pk": UserTitleDetails.title_id,
            "path_fields": ["default_poster_image_path", "default_backdrop_image_path", "default_logo_image_path"],
            "user_fields": ["chosen_poster_image_path", "chosen_backdrop_image_path", "chosen_logo_image_path"]
        },
        "season_id": {
            "val": season_id,
            "model": SeasonTranslation,
            "user_model": UserSeasonDetails,
            "pk": SeasonTranslation.season_id,
            "user_pk": UserSeasonDetails.season_id,
            "path_fields": ["default_poster_image_path"],
            "user_fields": ["chosen_poster_image_path"]
        }
    }

    active_key = next((k for k, v in CONFIG.items() if v["val"] is not None), None)
    if not active_key:
        raise ValueError("One of title_id, season_id, or episode_id must be provided.")
    
    cfg = CONFIG[active_key]
    val = cfg["val"]

    # 2. Build the Query
    stmt = select(cfg["model"]).where(cfg["pk"] == val)

    if hasattr(cfg["model"], "iso_639_1"):
        stmt = stmt.where(cfg["model"].iso_639_1 == chosen_iso_639_1)

    if cfg["user_model"]:
        stmt = stmt.add_columns(cfg["user_model"]).outerjoin(
            cfg["user_model"], 
            (cfg["user_pk"] == val) & (cfg["user_model"].user_id == user_id)
        )
    
    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return ImageListsOut(**{active_key: val}, posters=ImageListOut(total_count=0), 
                             backdrops=ImageListOut(total_count=0), logos=ImageListOut(total_count=0))

    main_obj = row[0]
    user_details = row[1] if len(row) > 1 else None

    # 3. Collect Defaults and Choices
    defaults = {getattr(main_obj, field, None) for field in cfg["path_fields"]}
    user_choices = set()
    if user_details:
        user_choices = {getattr(user_details, field, None) for field in cfg["user_fields"]}

    # 4. Fetch Linked Images
    img_stmt = (
        select(Image)
        .join(ImageLink, Image.file_path == ImageLink.file_path)
        .where(getattr(ImageLink, active_key) == val)
        .order_by(Image.vote_average.desc())
    )
    img_res = await db.execute(img_stmt)
    images = img_res.scalars().all()

    # 5. Categorization Logic
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


async def set_user_image_choice(
    db: AsyncSession, 
    user_id: int, 
    image_type: ImageType, 
    image_path: Optional[str], 
    title_id: Optional[int] = None, 
    season_id: Optional[int] = None, 
    episode_id: Optional[int] = None
):
    """
    Set the chosen image paths in user title/season/episode details tables
    after running validation checks on if the request is coherent.
    """
    
    if image_path is not None:
        # Build query to check if the image exists AND is linked to this specific entity
        # AND matches the intended ImageType
        validation_stmt = (
            select(Image)
            .join(ImageLink, Image.file_path == ImageLink.file_path)
            .where(
                Image.file_path == image_path,
                Image.type == image_type  # Constraint: Must match the enum type
            )
        )

        if title_id:
            validation_stmt = validation_stmt.where(ImageLink.title_id == title_id)
        elif season_id:
            validation_stmt = validation_stmt.where(ImageLink.season_id == season_id)
        elif episode_id:
            validation_stmt = validation_stmt.where(ImageLink.episode_id == episode_id)

        result = await db.execute(validation_stmt)
        valid_image = result.scalar_one_or_none()

        if not valid_image:
            raise HTTPException(
                status_code=400, 
                detail="Invalid image choice. The image must exist, match the requested type, "
                       "and be linked to this specific title/season/episode."
            )

    if title_id:
        target_config = {
            "model": UserTitleDetails,
            "id_field": "title_id",
            "id_val": title_id,
            "col_map": {
                ImageType.poster: "chosen_poster_image_path",
                ImageType.backdrop: "chosen_backdrop_image_path",
                ImageType.logo: "chosen_logo_image_path"
            }
        }
    elif season_id:
        target_config = {
            "model": UserSeasonDetails,
            "id_field": "season_id",
            "id_val": season_id,
            "col_map": {
                ImageType.poster: "chosen_poster_image_path"
            }
        }
    elif episode_id:
        target_config = {
            "model": UserEpisodeDetails,
            "id_field": "episode_id",
            "id_val": episode_id,
            "col_map": {
                ImageType.backdrop: "chosen_backdrop_image_path"
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Must provide title_id, season_id, or episode_id")

    # Determine target column
    target_col = target_config["col_map"].get(image_type)
    if not target_col:
        raise HTTPException(
            status_code=400, 
            detail=f"Image type '{image_type}' is not valid for this media entity."
        )

    model = target_config["model"]
    id_field = target_config["id_field"]
    id_val = target_config["id_val"]

    data_values = {
        "user_id": user_id,
        id_field: id_val,
        **{target_col: image_path}
    }

    stmt = insert(model).values(data_values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", id_field],
        set_={target_col: image_path}
    )

    await db.execute(stmt)
    await db.commit()
    
    return {
        "status": "success",
        "image_path": image_path,
        "updated_field": target_col
    }
