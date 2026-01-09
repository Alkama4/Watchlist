import enum
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.dependencies import get_db
from app.settings.config import REVERSE_TYPE_MAP

router = APIRouter()


def build_enum_choices(setting: models.Setting):
    if setting.value_type not in REVERSE_TYPE_MAP:
        return None

    enum_cls = REVERSE_TYPE_MAP[setting.value_type]
    choices = []
    for option in enum_cls:
        if option.name == "default":
            continue
        label = option.name.replace("_", " ").title()
        choices.append(schemas.EnumChoice(value=option.value, label=label))
    return choices


@router.get("/", response_model=list[schemas.SettingOut])
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Setting))
    settings = result.scalars().all()

    # attach enum choices dynamically
    out = []
    for s in settings:
        enum_choices = build_enum_choices(s)
        out.append(schemas.SettingOut(
            key=s.key,
            value_type=s.value_type,
            default_value=s.default_value,
            enum_choices=enum_choices
        ))
    return out


@router.get("/{key}", response_model=schemas.SettingOut)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    setting = await db.get(models.Setting, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    enum_choices = build_enum_choices(setting)
    return schemas.SettingOut(
        key=setting.key,
        value_type=setting.value_type,
        default_value=setting.default_value,
        enum_choices=enum_choices
    )
