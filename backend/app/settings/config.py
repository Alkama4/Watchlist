import enum
from typing import List, Any, Dict, Type, Callable, Union
from pydantic import BaseModel, Field, field_validator
from app.models import SortBy, SortDirection

def parse_list(v: Any) -> List[str]:
    if isinstance(v, list): return v
    if isinstance(v, str) and v.strip():
        return [item.strip() for item in v.split(",") if item.strip()]
    return []

class DefaultSettings(BaseModel):
    sort_by: SortBy = SortBy.tmdb_score
    sort_direction: SortDirection = SortDirection.desc
    items_per_page: int = 25
    locales: List[str] = Field(default_factory=lambda: ["en-US"])

    class Config:
        extra = "forbid"

    @field_validator("locales", mode="before")
    @classmethod
    def validate_locales(cls, v):
        return parse_list(v)

    def get_definitions(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "type": field.annotation,
                "default": getattr(self, name)
            }
            for name, field in self.model_fields.items()
        }

DEFAULT_SETTINGS = DefaultSettings()

# Single source of truth for type conversion
TYPE_MAP: Dict[Any, Callable] = {
    int: int,
    float: float,
    bool: lambda v: str(v).lower() in ("true", "1", "yes"),
    SortBy: SortBy,
    SortDirection: SortDirection,
    List[str]: parse_list,
}

REVERSE_TYPE_MAP = {
    v.__name__: v for v in TYPE_MAP.values() if isinstance(v, type) and issubclass(v, enum.Enum)}
