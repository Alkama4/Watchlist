from sqlalchemy import select
import enum
from app import models
from app.settings.config import DEFAULT_SETTINGS

async def init_settings(db):
    for key, meta in DEFAULT_SETTINGS.definitions().items():
        result = await db.execute(select(models.Setting).where(models.Setting.key == key))
        if not result.scalar_one_or_none():
            default = meta["default"]
            if isinstance(default, enum.Enum):
                default = default.value  # store enum value, not str(enum)
            db.add(
                models.Setting(
                    key=key,
                    value_type=meta["type"].__name__,
                    default_value=str(default)
                )
            )
    await db.commit()
