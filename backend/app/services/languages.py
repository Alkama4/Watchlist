from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Title, UserTitleDetails, UserSetting
from app.settings.config import DEFAULT_SETTINGS

async def get_preferred_locale(
    db: AsyncSession, 
    user_id: int, 
    title_id: int = None, 
    tmdb_id: int = None, 
    title_type: str = None
) -> str:
    """
    Determines locale with fallback: 
    Title Preference -> User Global -> System Default.
    Accepts either internal title_id OR (tmdb_id + title_type).
    """
    
    # 1. Check Specific Title Preference
    if title_id or (tmdb_id and title_type):
        stmt = select(UserTitleDetails.chosen_language).join(
            Title, UserTitleDetails.title_id == Title.title_id
        )
        
        # Apply filters based on what we have
        filters = [UserTitleDetails.user_id == user_id]
        
        if title_id:
            filters.append(UserTitleDetails.title_id == title_id)
        else:
            filters.append(Title.tmdb_id == tmdb_id)
            filters.append(Title.title_type == title_type)
        
        stmt = stmt.where(*filters, UserTitleDetails.chosen_language.is_not(None))
        
        result = await db.execute(stmt)

        specific_locale = result.scalar_one_or_none()
        if specific_locale:
            return specific_locale

    # 2. Check User Global Preference ("locales" is stored as "en-US,fi-FI")
    stmt = select(UserSetting.value).where(
        UserSetting.user_id == user_id, 
        UserSetting.key == "locales"
    )
    result = await db.execute(stmt)
    user_locales_raw = result.scalar_one_or_none()
    
    if user_locales_raw:
        locales = [l.strip() for l in user_locales_raw.split(",") if l.strip()]
        if locales:
            return locales[0]

    # 3. Fallback to System Default
    return DEFAULT_SETTINGS.locales[0] if DEFAULT_SETTINGS.locales else "en-US"


async def get_user_languages(
    db: AsyncSession, 
    user_id: int, 
    as_string: bool = True
) -> list[str | None] | str:
    """
    Fetches unique language codes (iso_639_1) for user.
    By default returns a comma seperated string list with the languages and "null".
    If set to list returns just a list of the languages.
    """
    stmt = select(UserSetting.value).where(
        UserSetting.user_id == user_id, 
        UserSetting.key == "locales"
    )
    result = await db.execute(stmt)
    raw_val = result.scalar_one_or_none()

    locales_list = [l.strip() for l in raw_val.split(",") if l.strip()] if raw_val else DEFAULT_SETTINGS.locales

    languages = []
    for locale in locales_list:
        lang = locale.split("-")[0].lower()
        if lang not in languages:
            languages.append(lang)

    if as_string:
        return ",".join(languages + ["null"])
    
    return languages
