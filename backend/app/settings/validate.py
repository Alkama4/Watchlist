from fastapi import HTTPException
from typing import Optional
from app.settings.config import TYPE_MAP
import enum

def validate_setting_value(raw: Optional[str], expected_type: type) -> Optional[str]:
    """Validate and convert a raw string value according to expected_type"""
    if raw is None or raw.strip() == "":
        return None

    validator = TYPE_MAP.get(expected_type)
    if not validator:
        raise HTTPException(status_code=400, detail=f"Unknown setting type '{expected_type}'")

    # primitive types (int, float, bool)
    if isinstance(validator, type):
        try:
            return validator(raw)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid value '{raw}' for type '{expected_type}'")

    # enums
    if issubclass(validator, enum.Enum):
        try:
            return validator[raw].value
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid enum value '{raw}' for type '{expected_type}'")

    # custom validator
    try:
        return validator(raw)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid value '{raw}' for type '{expected_type}'")
