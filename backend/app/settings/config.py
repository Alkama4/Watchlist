import enum
from pydantic import BaseModel
from app import models
from typing import Any, Dict, Type, Callable


######## Default settings using enums and typed fields ########
class DefaultSettings(BaseModel):
    sort_by: models.SortBy = models.SortBy.tmdb_score
    sort_direction: models.SortDirection = models.SortDirection.desc
    items_per_page: int = 25

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
    models.SortBy: models.SortBy,
    models.SortDirection: models.SortDirection,
}

REVERSE_TYPE_MAP = {
    v.__name__: v for v in TYPE_MAP.values() if isinstance(v, type) and issubclass(v, enum.Enum)}