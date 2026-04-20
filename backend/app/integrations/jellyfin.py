import httpx
import os

JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY")
JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_SERVER_ID = os.getenv("JELLYFIN_SERVER_ID")


async def jellyfin_get(path: str, params: dict | None = None) -> dict:
    # If we setup a seperate toggle for enable/disable jellyfin raise a
    # error for incomplete setup, but for now just return None.

    if not JELLYFIN_URL or not JELLYFIN_API_KEY:
        return None

    # missing_vars = [name for name, val in {
    #     "JELLYFIN_API_KEY": JELLYFIN_API_KEY, 
    #     "JELLYFIN_URL": JELLYFIN_URL
    # }.items() if not val]

    # if missing_vars:
    #     raise RuntimeError(f"Missing required configuration: {', '.join(missing_vars)}")

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

def build_jellyfin_map(jellyfin_response: dict) -> dict[str, str]:
    items = jellyfin_response.get("Items", [])
    return {
        item.get("ProviderIds", {}).get("Imdb"): item.get("Id")
        for item in items
        if item.get("ProviderIds", {}).get("Imdb")
    }

def resolve_jellyfin_id(jellyfin_map: dict, imdb_id: str) -> str | None:
    return jellyfin_map.get(imdb_id)
