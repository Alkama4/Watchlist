import asyncio
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


async def fetch_movie(tmdb_id: int, iso_639_1: str, user_image_languages: str) -> dict:
    return await tmdb_get(
        f"/movie/{tmdb_id}",
        params={
            "append_to_response": "images,releases,videos",
            "include_image_language": user_image_languages,
            "language": iso_639_1,
        },
    )


async def fetch_tv(tmdb_id: int, iso_639_1: str, user_image_languages: str) -> dict:
    return await tmdb_get(
        f"/tv/{tmdb_id}",
        params={
            "append_to_response": "images,content_ratings,videos,external_ids",
            "include_image_language": user_image_languages,
            "language": iso_639_1,
        },
    )


async def fetch_tv_season(tmdb_id: int, season_number: int, iso_639_1: str, user_image_languages: str) -> dict:
    return await tmdb_get(
        f"/tv/{tmdb_id}/season/{season_number}",
        params={
            "append_to_response": "images",
            "include_image_language": user_image_languages,
            "language": iso_639_1
        }
    )


async def search_multi(query: str, page: int):
    return await tmdb_get(
        f"/search/multi",
        params={
            "query": query,
            "page": page
        }
    )


async def fetch_movie_genres() -> list[dict]:
    data = await tmdb_get(
        "/genre/movie/list",
        params={
            "language": "en-US"
        })
    return data["genres"]


async def fetch_tv_genres() -> list[dict]:
    data = await tmdb_get(
        "/genre/tv/list",
        params={
            "language": "en-US"
        })
    return data["genres"]


async def fetch_genres() -> list[dict]:
    movie_genres, tv_genres = await asyncio.gather(
        fetch_movie_genres(),
        fetch_tv_genres(),
    )

    deduped = {
        genre["id"]: genre
        for genre in movie_genres + tv_genres
    }

    return list(deduped.values())
