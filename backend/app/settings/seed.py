from sqlalchemy import select
from app.models import Setting

DEFAULT_SETTINGS = [
    ("sort_by", "enum", "default"),
    ("sort_direction", "enum", "default"),
    ("items_per_page", "int", "25"),
]

async def init_settings(db):
    for key, value_type, default in DEFAULT_SETTINGS:
        result = await db.execute(
            select(Setting).where(Setting.key == key)
        )
        if not result.scalar_one_or_none():
            db.add(
                Setting(
                    key=key,
                    value_type=value_type,
                    default_value=default
                )
            )
    await db.commit()
