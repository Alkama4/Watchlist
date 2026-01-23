from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.settings.validate import validate_setting_value
from app.settings.config import DEFAULT_SETTINGS
from app.schemas import (
    UserSettingOut,
    UserSettingIn
)
from app.models import (
    User,
    Setting,
    UserSetting
)

router = APIRouter()


# --- Get user settings ---
@router.get("/", response_model=list[UserSettingOut])
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserSetting).where(UserSetting.user_id == current_user.user_id)
    )
    return result.scalars().all()


# --- Update user setting ---
@router.put("/{key}", response_model=UserSettingOut)
async def update_user_setting(
    key: str,
    setting_update: UserSettingIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    base_setting = await db.get(Setting, key)
    if not base_setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    # Determine the type from Pydantic defaults
    expected_type = DEFAULT_SETTINGS.definitions()[key]["type"]
    validate_setting_value(setting_update.value, expected_type)

    user_setting = await db.get(UserSetting, (current_user.user_id, key))
    if not user_setting:
        user_setting = UserSetting(
            user_id=current_user.user_id,
            key=key,
            value=setting_update.value
        )
    else:
        user_setting.value = setting_update.value

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)
    return user_setting
