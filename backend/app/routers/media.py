import os
import io
import asyncio
from PIL import Image
import aiofiles
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

TMDB_IMAGE_BASE_PATH = "https://image.tmdb.org/t/p/original/"
LOCAL_IMAGE_BASE_PATH = os.environ["IMAGE_STORAGE_PATH"]

BUCKETS = [400, 800, 1600]  # original handled separately

def pick_bucket(long_side: int):
    for b in BUCKETS:
        if long_side <= b:
            return b
    return None

async def resize_image(original_path: str, target_path: str, long_side: int):
    loop = asyncio.get_event_loop()

    def _resize():
        with Image.open(original_path) as img:
            width, height = img.size
            if width >= height:
                new_width = long_side
                new_height = int(height * (long_side / width))
            else:
                new_height = long_side
                new_width = int(width * (long_side / height))
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            img_resized.save(target_path, "JPEG")

    await loop.run_in_executor(None, _resize)

async def download_original(image_path: str, local_path: str):
    url = f"{TMDB_IMAGE_BASE_PATH}{image_path}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Image not found")
        async with aiofiles.open(local_path, "wb") as f:
            await f.write(resp.content)

@router.get("/image/{size}/{image_path:path}")
async def get_image(size: str, image_path: str):
    """
    Valid size values: `400`, `800`, `1600` & `original`. If value doesn't match it will be rounded up.
    """

    # Determine bucket
    if size == "original":
        bucket = None
        target_folder = os.path.join(LOCAL_IMAGE_BASE_PATH, "original")
    else:
        try:
            requested_size = int(size)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid size")
        
        bucket = pick_bucket(requested_size)
        if bucket is None:
            target_folder = os.path.join(LOCAL_IMAGE_BASE_PATH, "original")
        else:
            target_folder = os.path.join(LOCAL_IMAGE_BASE_PATH, str(bucket))

    local_file_path = os.path.join(target_folder, image_path)

    # Serve if exists
    if os.path.exists(local_file_path):
        return FileResponse(local_file_path, media_type="image/jpeg")

    # Ensure original exists
    original_path = os.path.join(LOCAL_IMAGE_BASE_PATH, "original", image_path)
    if not os.path.exists(original_path):
        await download_original(image_path, original_path)

    # Resize if bucketed
    if bucket is not None:
        await resize_image(original_path, local_file_path, bucket)
        return FileResponse(local_file_path, media_type="image/jpeg")

    # Otherwise serve original
    return FileResponse(original_path, media_type="image/jpeg")
