from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.routers.auth import get_current_user
from app.services.tmdb_collections import fetch_collection_with_user_details
from app.models import User
from app.schemas import TMDBCollectionOut

router = APIRouter()


@router.get("/tmdb/{tmdb_collection_id}", response_model=TMDBCollectionOut)
async def get_tmdb_collection_details(
    tmdb_collection_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = await fetch_collection_with_user_details(
        db=db,
        tmdb_collection_id=tmdb_collection_id,
        user_id=user.user_id
    )
    return results
