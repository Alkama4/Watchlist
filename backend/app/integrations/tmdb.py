import httpx
import os

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")


async def tmdb_get(path: str, params: dict | None = None) -> dict:
    if not TMDB_ACCESS_TOKEN:
        raise RuntimeError("TMDB_ACCESS_TOKEN not set")

    url = f"{TMDB_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        raise RuntimeError(resp.text)

    return resp.json()


async def fetch_movie(tmdb_id: int) -> dict:
    return await tmdb_get(
        f"/movie/{tmdb_id}",
        params={
            "append_to_response": "images,releases,videos",
            "language": "en-US",
        },
    )


async def fetch_tv(tmdb_id: int) -> dict:
    return await tmdb_get(
        f"/tv/{tmdb_id}",
        params={
            "append_to_response": "images,content_ratings,videos,external_ids",
            "language": "en-US",
        },
    )


async def fetch_tv_season(tmdb_id: int, season_number: int) -> dict:
    return await tmdb_get(
        f"/tv/{tmdb_id}/season/{season_number}",
        params={
            "append_to_response": "images",
            "language": "en-US"
        }
    )
