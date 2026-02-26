from fastapi import APIRouter
from app.integrations.jellyfin import JELLYFIN_URL, JELLYFIN_SERVER_ID
from app.schemas import ConfigJellyfinOut

router = APIRouter()


@router.get("/jellyfin", response_model=ConfigJellyfinOut)
def sync_jellyfin_links():
    return {
        "base_url": JELLYFIN_URL,
        "server_id": JELLYFIN_SERVER_ID
    }