from fastapi import HTTPException
from typing import Any
from app.settings.config import TYPE_MAP
import enum

def validate_setting_value(raw: Any, expected_type: Any) -> Any:
    """Validate and convert a raw value (usually string from DB) to its Python type."""
    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return None

    converter = TYPE_MAP.get(expected_type)
    if not converter:
        raise HTTPException(status_code=400, detail=f"No converter for type '{expected_type}'")

    try:
        # If it's an Enum, we handle the lookup
        if isinstance(converter, type) and issubclass(converter, enum.Enum):
            # Try to match by value (e.g., "tmdb_score")
            return converter(raw)
        
        # Otherwise, use the mapped function (int, parse_list, etc.)
        return converter(raw)
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=400, 
            detail=f"Value '{raw}' is not a valid {expected_type}"
        )
    