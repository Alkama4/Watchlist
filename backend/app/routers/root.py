from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import models
from app.dependencies import get_db
from app.routers.auth import get_current_user

router = APIRouter()


@router.get("/home")
async def get_home_overview(
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return a curated overview of titles for the authenticated user.

    This endpoint aggregates multiple server-defined queries
    and returns them in a single response.
    """

    return {}
