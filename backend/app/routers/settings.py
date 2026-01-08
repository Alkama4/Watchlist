from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.SettingOut])
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Setting))
    return result.scalars().all()


@router.get("/{key}", response_model=schemas.SettingOut)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    setting = await db.get(models.Setting, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


