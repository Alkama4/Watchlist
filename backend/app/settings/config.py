import enum
from pydantic import BaseModel
from typing import Any, Dict, Type, Callable
from app.models import (
    SortBy,
    SortDirection
)

# Here is where we define the settings that the application has.
# Commented out settings are setting ideas to add to the settings.

######## Default settings using enums and typed fields ########
class DefaultSettings(BaseModel):
    sort_by: SortBy = SortBy.tmdb_score
    sort_direction: SortDirection = SortDirection.desc
    items_per_page: int = 25
    # locale: default to auto, where it is detected by browser, or just en-US? propably en-US if we are using for TMDB queries as well.
    # fallback_locale: as name states, default en-US
    # what to do when fallback local is no found either?
    # auto_remove_from_watchlist: automatically set the tag in_watchlist to false after adding to the watchcount.
    # color_theme: pure-black, midnight,...

    class Config:
        extra = "forbid"

    @classmethod
    def definitions(cls) -> Dict[str, Dict[str, Any]]:
        """Returns metadata for all settings: type and default value"""
        defs = {}
        for field_name, field in cls.model_fields.items():
            defs[field_name] = {
                "type": field.annotation,
                "default": getattr(cls(), field_name)
            }
        return defs

DEFAULT_SETTINGS = DefaultSettings()

######## Type validators mapping ########
TYPE_MAP: Dict[Type | str, Callable] = {
    int: int,
    float: float,
    bool: lambda v: v.lower() in ("true", "1", "yes"),
    SortBy: SortBy,
    SortDirection: SortDirection,
}

REVERSE_TYPE_MAP = {
    v.__name__: v for v in TYPE_MAP.values() if isinstance(v, type) and issubclass(v, enum.Enum)}