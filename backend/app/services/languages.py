from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Title, TitleTranslation, UserTitleDetails, UserSetting
from app.settings.config import DEFAULT_SETTINGS
from dataclasses import dataclass

@dataclass
class LanguageContext:
    preferred_locale: str              # e.g., "en-US"
    preferred_iso_639_1: str           # e.g., "en"
    preferred_iso_3166_1: str          # e.g., "US"
    iso_639_1_list: list[str]          # e.g., ["en", "fi"]
    iso_3166_1_list: list[str]         # e.g., ["US", "FI"]
    iso_639_1_comma_str: str           # e.g., "en,fi,null"

async def get_user_language_context(
    db: AsyncSession, 
    user_id: int, 
    title_id: int = None, 
    tmdb_id: int = None, 
    title_type: str = None
) -> LanguageContext:
    # 1. Fetch Global Settings
    stmt = select(UserSetting.value).where(
        UserSetting.user_id == user_id, 
        UserSetting.key == "locales"
    )
    res = await db.execute(stmt)
    raw_val = res.scalar_one_or_none()
    
    # Start with global locales or system default
    base_locales = [l.strip() for l in raw_val.split(",") if l.strip()] if raw_val else list(DEFAULT_SETTINGS.locales)

    # 2. Fetch Title Specific Preference
    specific_locale = None
    if title_id or (tmdb_id and title_type):
        stmt = select(UserTitleDetails.chosen_locale).join(
            Title, UserTitleDetails.title_id == Title.title_id
        )
        filters = [UserTitleDetails.user_id == user_id]
        if title_id:
            filters.append(UserTitleDetails.title_id == title_id)
        else:
            filters.append(Title.tmdb_id == tmdb_id)
            filters.append(Title.title_type == title_type)
        
        stmt = stmt.where(*filters, UserTitleDetails.chosen_locale.is_not(None))
        res = await db.execute(stmt)
        specific_locale = res.scalar_one_or_none()

    # 3. Build Logic
    full_locales = ([specific_locale] + base_locales) if specific_locale else base_locales
    
    # Determine the single primary locale
    primary_locale = full_locales[0]
    primary_parts = primary_locale.split("-")
    primary_iso_639_1 = primary_parts[0].lower()
    primary_iso_3166_1 = primary_parts[1].upper() if len(primary_parts) > 1 else ""

    # Generate unique ISO lists
    iso_639_1_list = []
    iso_3166_1_list = []
    
    for loc in full_locales:
        parts = loc.split("-")
        lang = parts[0].lower()
        region = parts[1].upper() if len(parts) > 1 else None
        
        if lang not in iso_639_1_list:
            iso_639_1_list.append(lang)
        if region and region not in iso_3166_1_list:
            iso_3166_1_list.append(region)

    return LanguageContext(
        preferred_locale=primary_locale,
        preferred_iso_639_1=primary_iso_639_1,
        preferred_iso_3166_1=primary_iso_3166_1,
        iso_639_1_list=iso_639_1_list,
        iso_3166_1_list=iso_3166_1_list,
        iso_639_1_comma_str=",".join(iso_639_1_list + ["null"])
    )


async def check_translation_availability(
    db: AsyncSession, 
    title_id: int,
    iso_639_1: str
):
    stmt = select(TitleTranslation).where(
        TitleTranslation.title_id == title_id,
        TitleTranslation.iso_639_1 == iso_639_1,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
    

async def get_users_global_preferred_locale(db: AsyncSession, user_id: int) -> str:
    stmt = select(UserSetting.value).where(
        UserSetting.user_id == user_id, 
        UserSetting.key == "locales"
    )
    result = await db.execute(stmt)
    user_locales_raw = result.scalar_one_or_none()
    
    if user_locales_raw:
        locales = [l.strip() for l in user_locales_raw.split(",") if l.strip()]
        if locales:
            # Return just the "en" from "en-US"
            return locales[0]

    # Fallback to system default
    return DEFAULT_SETTINGS.locales[0]


def get_best_translation(translations, preferred_isos: list[str]):
    """Picks the first translation that matches the prioritized ISO list."""
    for iso in preferred_isos:
        for trans in translations:
            if trans.iso_639_1 == iso:
                return trans
    return None


def fill_translated_fields_dynamically(target_dict: dict, translations: list, preferred_isos: list[str], model_class):
    """
    Dynamically discovers columns from the Translation Model (TitleTranslation, etc.)
    and applies fallback logic to target_dict.
    """
    mapper = inspect(model_class)
    all_columns = [column.key for column in mapper.attrs if hasattr(column, 'columns')]
    excluded = {"title_id", "season_id", "episode_id", "iso_639_1"}
    fields = [f for f in all_columns if f not in excluded]

    # Initialize all discovered fields to None in target_dict if missing
    for field in fields:
        if field not in target_dict:
            target_dict[field] = None

    for iso in preferred_isos:
        trans = next((t for t in translations if t.iso_639_1 == iso), None)
        if not trans:
            continue
            
        for field in fields:
            val = getattr(trans, field, None)
            current_val = target_dict.get(field)
            
            # Fill if current is None or empty string
            if (current_val is None or (isinstance(current_val, str) and not current_val.strip())):
                if val is not None and (not isinstance(val, str) or val.strip()):
                    target_dict[field] = val
    