from sqlalchemy import select
import enum
from app.settings.config import DEFAULT_SETTINGS
from app.models import Setting

async def init_settings(db):
    definitions = DEFAULT_SETTINGS.get_definitions()
    
    for key, meta in definitions.items():
        # Get the default value as a string for storage
        raw_default = meta["default"]
        if isinstance(raw_default, enum.Enum):
            string_default = raw_default.value
        elif isinstance(raw_default, list):
            string_default = ",".join(raw_default)
        else:
            string_default = str(raw_default)

        # Check if setting exists
        result = await db.execute(select(Setting).where(Setting.key == key))
        existing_setting = result.scalar_one_or_none()

        if existing_setting:
            # Update the metadata in case config.py changed
            existing_setting.value_type = str(meta["type"])
            existing_setting.default_value = string_default
        else:
            # Create new entry
            db.add(
                Setting(
                    key=key,
                    value_type=str(meta["type"]),
                    default_value=string_default
                    # value=None (User hasn't overridden it yet)
                )
            )
            
    await db.commit()
    