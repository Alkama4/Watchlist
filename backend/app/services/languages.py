from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Title, TitleTranslation, UserTitleDetails, UserSetting
from app.settings.config import DEFAULT_SETTINGS
from dataclasses import dataclass

@dataclass
class LanguageContext:
    preferred_locale: str          # e.g., "en-US"
    preferred_iso_639_1: str       # e.g., "en"
    languages_list: list[str]      # e.g., ["en", "fi"]
    languages_str: str             # e.g., "en,fi,null"

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
    # The 'active' list has the specific locale at the front if it exists
    full_locales = ([specific_locale] + base_locales) if specific_locale else base_locales
    
    # Determine the single primary locale (First one in the prioritized list)
    primary_locale = full_locales[0]
    primary_iso = primary_locale.split("-")[0].lower()

    # Generate unique ISO list for image fetching
    languages = []
    for loc in full_locales:
        lang = loc.split("-")[0].lower()
        if lang not in languages:
            languages.append(lang)

    return LanguageContext(
        preferred_locale=primary_locale,
        preferred_iso_639_1=primary_iso,
        languages_list=languages,
        languages_str=",".join(languages + ["null"])
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
    
