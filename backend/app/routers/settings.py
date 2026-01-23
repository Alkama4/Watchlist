from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.dependencies import get_db
from app.settings.config import REVERSE_TYPE_MAP
from app.schemas import (
    EnumChoice,
    SettingOut
)
from app.models import (
    Setting
)

router = APIRouter()


def format_label(value: str) -> str:
    return value.replace("_", " ").title()

def build_enum_choices(setting: Setting):
    if setting.value_type not in REVERSE_TYPE_MAP:
        return None

    enum_cls = REVERSE_TYPE_MAP[setting.value_type]
    choices = []

    for option in enum_cls:
        if option.name == "default":
            continue
        elif option.value == setting.default_value:
            label = f"{format_label(option.name)} (Default)"
        else:
            label = format_label(option.name)

        choices.append(
            EnumChoice(
                value=option.value,
                label=label
            )
        )

    return choices


@router.get("/", response_model=list[SettingOut])
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting))
    settings = result.scalars().all()

    # attach enum choices dynamically
    out = []
    for s in settings:
        enum_choices = build_enum_choices(s)
        out.append(SettingOut(
            key=s.key,
            value_type=s.value_type,
            default_value=s.default_value,
            enum_choices=enum_choices,
            label=format_label(s.key)
        ))
    return out


@router.get("/{key}", response_model=SettingOut)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    setting = await db.get(Setting, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    enum_choices = build_enum_choices(setting)
    return SettingOut(
        key=setting.key,
        value_type=setting.value_type,
        default_value=setting.default_value,
        enum_choices=enum_choices
    )
