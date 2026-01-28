import os
import asyncio
from PIL import Image
import aiofiles
import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
import subprocess
import json

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


# VIDEO_PATH = "C:\\Users\\aleks\\Desktop\\large_test_file.mkv"
VIDEO_PATH = "C:\\Users\\aleks\\Desktop\\small_test_file.mkv"

@router.api_route("/video", methods=["GET", "HEAD"])
async def stream_video(request: Request):
    if not os.path.exists(VIDEO_PATH):
        raise HTTPException(status_code=404)

    file_size = os.path.getsize(VIDEO_PATH)
    range_header = request.headers.get("range")

    start = 0
    end = file_size - 1

    if range_header:
        units, _, value = range_header.partition("=")
        if units != "bytes":
            range_header = None
        elif "," in value:
            # Multi-range not supported → ignore per common practice
            range_header = None
        else:
            start_str, _, end_str = value.partition("-")

            if start_str == "":
                if not end_str:
                    range_header = None
                else:
                    length = int(end_str)
                    start = max(file_size - length, 0)
                    end = file_size - 1
            else:
                start = int(start_str)
                if end_str:
                    end = int(end_str)

            if start < 0 or start > end or end >= file_size:
                range_header = None

    is_range = range_header is not None
    chunk_size = end - start + 1

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": "video/x-matroska",
    }

    if is_range:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    if request.method == "HEAD":
        return Response(status_code=206 if is_range else 200, headers=headers)

    def iter_file():
        with open(VIDEO_PATH, "rb") as f:
            f.seek(start)
            remaining = chunk_size
            while remaining > 0:
                data = f.read(min(1024 * 1024, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data

    return StreamingResponse(
        iter_file(),
        status_code=206 if is_range else 200,
        headers=headers,
    )
