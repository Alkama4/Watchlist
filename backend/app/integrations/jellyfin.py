import httpx
import os

JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")
JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_SERVER_ID = os.getenv("JELLYFIN_SERVER_ID")


async def jellyfin_get(path: str, params: dict | None = None) -> dict:
    if not JELLYFIN_API_KEY:
        raise RuntimeError("JELLYFIN_API_KEY not set")

    url = f"{JELLYFIN_URL}{path}"
    headers = {
        "Authorization": f'MediaBrowser Token="{JELLYFIN_API_KEY}"',
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        raise RuntimeError(resp.text)

    return resp.json()


async def fetch_jellyfin_titles() -> dict:
    return await jellyfin_get(
        f"/Items",
        params={
            "IncludeItemTypes": "Movie,Series",
            "Recursive": "true",
            "Fields": "ProviderIds",
        },
    )

async def fetch_jellyfin_id_by_imdb(imdb_id: str) -> str | None:
    """Returns the Jellyfin internal ID for a given IMDB ID, or None if not found."""
    data = await fetch_jellyfin_titles()
    items = data.get("Items", [])
    for item in items:
        provider_ids = item.get("ProviderIds", {})
        if provider_ids.get("Imdb") == imdb_id:
            return item.get("Id")
    return None