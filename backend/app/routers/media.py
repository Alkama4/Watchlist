import os
import asyncio
import aiofiles
import httpx
import shutil
from PIL import Image
from typing import List, Optional
from pydantic import Field
from fastapi import APIRouter, HTTPException, Query, Request, Response, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, distinct, Float
from sqlalchemy.orm import selectinload
from app.services.video_assets import sync_all_video_assets
from app.services.languages import LanguageContext, get_user_language_context, pick_translation
from app.dependencies import get_db
from app.models import Episode, Season, Title, TitleFolder, User, VideoAsset, TitleUserDetails
from app.enums import TitleType, VideoType, SortBy, SortDirection
from app.schemas import EpisodeAuditDetail, EpisodeMinimalOut, FolderRequest, MovieVariantDetail, QualitySummary, TitleAuditDetailOut, TitleFolderCountsOut, TitleMinimalOut, VideoAssetExpandedOut, TitleFoldersResponseOut, TitleAuditOut, VideoAssetOut
from app.routers.auth import get_current_user
from app.config import DEFAULT_MAX_QUERY_LIMIT

router = APIRouter()

TMDB_IMAGE_BASE_PATH = "https://image.tmdb.org/t/p"
LOCAL_IMAGE_BASE_PATH = os.environ["IMAGE_STORAGE_PATH"]

BUCKETS = [400, 800, 1600]  # original handled separately

http_client = httpx.AsyncClient(timeout=None)

def pick_bucket(long_side: int):
    for b in BUCKETS:
        if long_side <= b:
            return b
    return None

async def _resize_image(original_path: str, target_path: str, long_side: int):
    loop = asyncio.get_event_loop()

    def _resize():
        with Image.open(original_path) as img:
            if img.format == 'SVG':
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(original_path, target_path)
                return

            width, height = img.size
            if width >= height:
                new_width = long_side
                new_height = int(height * (long_side / width))
            else:
                new_height = long_side
                new_width = int(width * (long_side / height))
            
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)

            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Check if image has transparency
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                # Keep as PNG to preserve transparency
                img_resized.save(target_path, "PNG", optimize=True)
            else:
                # Convert to RGB and save as progressive JPEG
                if img_resized.mode != "RGB":
                    img_resized = img_resized.convert("RGB")
                img_resized.save(target_path, "JPEG", progressive=True, quality=85)

    await loop.run_in_executor(None, _resize)

async def _download_original(image_path: str, local_path: str):
    url = f"{TMDB_IMAGE_BASE_PATH}/original/{image_path}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Image not found")
        async with aiofiles.open(local_path, "wb") as f:
            await f.write(resp.content)

async def _make_progressive(input_path: str, output_path: str):
    """Re-saves an image appropriately: PNG for transparency, Progressive JPEG otherwise."""
    def _process():
        with Image.open(input_path) as img:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if (img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)):
                # Keep as PNG to preserve transparency
                img.save(output_path, "PNG", optimize=True)
            else:
                # Convert to RGB and save as progressive JPEG
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(output_path, "JPEG", progressive=True, quality=95)
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _process)

async def _proxy_image(image_path: str, size: int):
    url = f"{TMDB_IMAGE_BASE_PATH}/{'original' if size == 'original' else 'w500'}/{image_path}"
    
    req = http_client.build_request("GET", url)
    resp = await http_client.send(req, stream=True)

    if resp.status_code != 200:
        await resp.aclose()
        raise HTTPException(status_code=resp.status_code, detail="TMDB error")

    return StreamingResponse(
        resp.aiter_bytes(), 
        media_type=resp.headers.get("Content-Type", "image/jpeg"),
        background=resp.aclose
    )

@router.get("/image/{size}/{image_path:path}")
async def get_image(
    size: str, 
    image_path: str, 
    store: bool = Query(True)
):
    """
    Valid size values: `400`, `800`, `1600` & `original`.
    
    If store=false:
    - Checks local storage first to save bandwidth.
    - If not found, proxies directly from TMDB without saving.
    - Note: This mode is intended for search result posters; quality is forced to w500.
    """

    # Determine local pathing
    if size == "original":
        bucket = None
        target_folder = os.path.join(LOCAL_IMAGE_BASE_PATH, "original")
    else:
        try:
            requested_size = int(size)
            bucket = pick_bucket(requested_size)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid size")
        
        target_folder = os.path.join(LOCAL_IMAGE_BASE_PATH, str(bucket) if bucket else "original")

    local_file_path = os.path.join(target_folder, image_path)

    # Serve from files
    if os.path.exists(local_file_path):
        return FileResponse(local_file_path)

    # Passthrough
    if not store:
        return await _proxy_image(image_path, size)

    # Store originial
    if size == "original":
        temp_original = local_file_path + ".tmp"
        await _download_original(image_path, temp_original)
        
        if image_path.lower().endswith('.svg'):
            os.replace(temp_original, local_file_path)
        else:
            await _make_progressive(temp_original, local_file_path)
            os.remove(temp_original)
            
        return FileResponse(local_file_path)

    # Store resized
    else:
        original_path = os.path.join(LOCAL_IMAGE_BASE_PATH, "original", image_path)
        if not os.path.exists(original_path):
            await _download_original(image_path, original_path)
        
        await _resize_image(original_path, local_file_path, bucket)
        return FileResponse(local_file_path)


@router.get("/video/{video_asset_id}/{title}")
@router.get("/video/{video_asset_id}")
async def stream_video(
    video_asset_id: int, 
    request: Request, 
    title: str = None,  # Not used here, players/browsers pick it up from the url
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch the file path from the database
    stmt = select(VideoAsset.file_path).where(VideoAsset.video_asset_id == video_asset_id)
    result = await db.execute(stmt)
    video_path = result.scalar_one_or_none()

    if not video_path:
        raise HTTPException(status_code=404, detail="Video asset record not found")

    # 2. Check if the physical file exists
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file missing on disk")

    file_size = os.path.getsize(video_path)
    range_header = request.headers.get("range")

    start = 0
    end = file_size - 1

    # Byte-range logic
    if range_header:
        units, _, value = range_header.partition("=")
        if units == "bytes" and "," not in value:
            start_str, _, end_str = value.partition("-")
            
            if start_str == "" and end_str:
                length = int(end_str)
                start = max(file_size - length, 0)
            else:
                start = int(start_str) if start_str else 0
                if end_str:
                    end = int(end_str)

            if start < 0 or start > end or end >= file_size:
                range_header = None

    is_range = range_header is not None
    chunk_size = end - start + 1

    ext = os.path.splitext(video_path)[1].lower()
    if ext == ".mkv":
        content_type = "video/x-matroska"
    elif ext == ".webm":
        content_type = "video/webm"
    else:
        content_type = "video/mp4"

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": content_type
    }

    if is_range:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    if request.method == "HEAD":
        return Response(status_code=206 if is_range else 200, headers=headers)

    # Helper generator to stream the file
    def iter_file():
        with open(video_path, "rb") as f:
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


@router.post("/video_assets/sync")
async def synchronize_video_assets_relationships_with_titles(
    db: AsyncSession = Depends(get_db),
):
    details = await sync_all_video_assets(db)
    return {
        "message": "Sync completed successfully.",
        "details": details
    }

@router.get("/video_assets/title_folders", response_model=TitleFoldersResponseOut)
async def get_list_of_video_asset_title_folders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id) # <-- ADDED

    # Subquery remains exactly the same
    episodes_per_title = (
        select(
            Episode.title_id,
            func.count(Episode.episode_id).label("total_episode_meta_count")
        )
        .join(Season, Episode.season_id == Season.season_id)
        .where(Season.season_number != 0)
        .group_by(Episode.title_id)
        .subquery()
    )

    stmt = (
        select(
            TitleFolder,
            func.count(VideoAsset.video_asset_id).label("file_count"),
            func.count(VideoAsset.video_asset_id).filter(VideoAsset.video_type == VideoType.movie).label("movie_count"),
            func.count(VideoAsset.video_asset_id).filter(VideoAsset.video_type == VideoType.featurette).label("featurette_count"),
            func.count(VideoAsset.video_asset_id).filter(VideoAsset.video_type == VideoType.episode).label("episodes_count"),
            func.count(distinct(VideoAsset.episode_id)).label("unique_episodes_linked_count"),
            
            func.count(VideoAsset.video_asset_id).filter(
                or_(
                    TitleFolder.title_id.is_(None),
                    and_(
                        VideoAsset.video_type == VideoType.episode,
                        VideoAsset.episode_id.is_(None)
                    )
                )
            ).label("unlinked_count"),
            
            func.coalesce(episodes_per_title.c.total_episode_meta_count, 0).label("title_episode_count")
        )
        .outerjoin(VideoAsset, TitleFolder.title_folder_id == VideoAsset.title_folder_id)
        .outerjoin(episodes_per_title, TitleFolder.title_id == episodes_per_title.c.title_id)
        .options(
            selectinload(TitleFolder.title).selectinload(Title.translations)
        )
        .group_by(
            TitleFolder.title_folder_id,
            episodes_per_title.c.total_episode_meta_count
        )
        .order_by(TitleFolder.title_id.is_(None).asc(), TitleFolder.title_folder_name.asc())
    )

    result = await db.execute(stmt)
    rows = result.all()
    
    linked_folders, unlinked_folders = [], []
    metrics = {"total": 0, "movies": 0, "episodes": 0, "featurettes": 0, "linked": 0, "unlinked": 0}

    for row in rows:
        folder = row.TitleFolder
        metrics["total"] += row.file_count
        metrics["movies"] += row.movie_count
        metrics["episodes"] += row.episodes_count
        metrics["featurettes"] += row.featurette_count
        metrics["unlinked"] += row.unlinked_count
        metrics["linked"] += (row.file_count - row.unlinked_count)

        # <-- ADDED: Build the linked_title object
        title_out = None
        if folder.title:
            title_out = TitleMinimalOut(
                title_id=folder.title.title_id,
                name=pick_translation(folder.title.translations, locale_ctx.iso_639_1_list, "name")
            )

        folder_data = {
            "title_folder_id": folder.title_folder_id,
            "title_folder_path": folder.title_folder_path,
            "title_folder_name": folder.title_folder_name,
            "linked_title": title_out,  # <-- ADDED
            "is_linked": folder.title_id is not None,
            "counts": {
                "file_count": row.file_count,
                "movie_count": row.movie_count,
                "featurette_count": row.featurette_count,
                "episodes_count": row.episodes_count,
                "unlinked_count": row.unlinked_count,
                "title_episode_count": row.title_episode_count,
                "unique_episodes_linked": row.unique_episodes_linked_count,
            }
        }

        if folder.title_id is not None:
            linked_folders.append(folder_data)
        else:
            unlinked_folders.append(folder_data)

    return {
        "linked_folders": linked_folders,
        "unlinked_folders": unlinked_folders,
        "counts": {
            "total_video_assets": metrics["total"],
            "total_movies": metrics["movies"],
            "total_episodes": metrics["episodes"],
            "total_featurettes": metrics["featurettes"],
            "total_linked_video_assets": metrics["linked"],
            "total_unlinked_video_assets": metrics["unlinked"],
        }
    }

@router.post("/video_assets/title_folder/assets", response_model=List[VideoAssetExpandedOut])
async def get_folder_assets(
    request_data: FolderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    stmt = (
        select(VideoAsset)
        .where(VideoAsset.title_folder_id == request_data.title_folder_id)
        .options(
            selectinload(VideoAsset.title_folder),
            selectinload(VideoAsset.episode).selectinload(Episode.translations),
            selectinload(VideoAsset.episode).selectinload(Episode.season).selectinload(Season.translations),
        )
        .order_by(VideoAsset.video_type.asc(), VideoAsset.file_name.asc())
    )
    result = await db.execute(stmt)
    assets = result.scalars().all()

    return [_build_expanded_out(asset, locale_ctx) for asset in assets]


def _build_expanded_out(asset: VideoAsset, locale_ctx: LanguageContext) -> VideoAssetExpandedOut:
    episode_out = None
    if asset.episode:
        ep = asset.episode
        season = ep.season
        episode_out = EpisodeMinimalOut(
            episode_id=ep.episode_id,
            episode_number=ep.episode_number,
            episode_name=pick_translation(ep.translations, locale_ctx.iso_639_1_list, "name"),
            season_number=season.season_number,
            season_name=pick_translation(season.translations, locale_ctx.iso_639_1_list, "name"),
        )

    is_linked = bool(
        asset.episode_id is not None or
        (asset.title_folder.title_id is not None and asset.video_type in [VideoType.movie, VideoType.featurette])
    )

    asset_data = {
        k: v for k, v in asset.__dict__.items()
        if not k.startswith("_sa") and k != "episode"
    }

    return VideoAssetExpandedOut(
        **asset_data,
        linked_episode=episode_out,
        is_linked=is_linked
    )


from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, or_, and_, Float
from sqlalchemy.orm import selectinload


def build_quality_summary(
    resolutions_raw: List[Optional[str]],
    hdr_types_raw: List[Optional[str]],
    file_count: int,
    is_tv: bool,
) -> QualitySummary:
    """Computes high-level quality attributes and pre-formats display labels."""
    resolutions = [r for r in set(resolutions_raw) if r]
    hdr_types = [h for h in set(hdr_types_raw) if h]

    if not resolutions:
        return QualitySummary(
            resolutions=[],
            hdr_types=[],
            is_uniform=True,
            primary_display="No Video Files",
        )

    # Resolution hierarchy helper
    res_rank = {"4K": 4, "2160p": 4, "1080p": 3, "720p": 2, "480p": 1, "SD": 1}
    sorted_res = sorted(
        resolutions, key=lambda x: res_rank.get(x, 0), reverse=True
    )
    max_res = sorted_res[0]
    hdr_suffix = f" {hdr_types[0]}" if hdr_types else ""

    if is_tv:
        is_uniform = len(resolutions) <= 1 and len(hdr_types) <= 1
        primary_display = (
            f"{max_res}{hdr_suffix}"
            if is_uniform
            else f"{max_res} (Mixed Quality)"
        )
    else:
        is_uniform = file_count <= 1
        primary_display = (
            f"{max_res}{hdr_suffix}"
            if is_uniform
            else f"{max_res}{hdr_suffix} ({file_count} versions)"
        )

    return QualitySummary(
        resolutions=sorted_res,
        hdr_types=hdr_types,
        is_uniform=is_uniform,
        primary_display=primary_display,
    )


@router.get("/video_assets/audit", response_model=List[TitleAuditOut])
async def get_video_assets_audit(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    min_size_gb: Optional[float] = None,
    asset_status: Optional[str] = None,
    in_watchlist: Optional[bool] = None,
    title_type: Optional[TitleType] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[SortDirection] = SortDirection.default,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(20, ge=0),
):
    locale_ctx = await get_user_language_context(db=db, user_id=user.user_id)

    # 1. Total metadata episodes subquery (excluding S0 / specials)
    episodes_per_title = (
        select(
            Episode.title_id,
            func.count(Episode.episode_id).label("total_episode_meta_count"),
        )
        .join(Season, Episode.season_id == Season.season_id)
        .where(Season.season_number != 0)
        .group_by(Episode.title_id)
        .subquery()
    )

    # 2. Main aggregation query
    stmt = (
        select(
            TitleFolder,
            func.coalesce(func.sum(VideoAsset.filesize_bytes), 0).label(
                "total_size_bytes"
            ),
            func.array_agg(distinct(VideoAsset.resolution)).label(
                "resolutions"
            ),
            func.array_agg(distinct(VideoAsset.hdr_type)).label("hdr_types"),
            func.count(distinct(VideoAsset.video_asset_id)).label("file_count"),
            func.count(distinct(VideoAsset.video_asset_id))
            .filter(VideoAsset.video_type == VideoType.movie)
            .label("movie_count"),
            func.count(distinct(VideoAsset.video_asset_id))
            .filter(VideoAsset.video_type == VideoType.featurette)
            .label("featurette_count"),
            func.count(distinct(VideoAsset.video_asset_id))
            .filter(VideoAsset.video_type == VideoType.episode)
            .label("episodes_count"),
            func.count(distinct(VideoAsset.episode_id)).label(
                "unique_episodes_linked_count"
            ),
            func.count(distinct(VideoAsset.video_asset_id))
            .filter(
                or_(
                    TitleFolder.title_id.is_(None),
                    and_(
                        VideoAsset.video_type == VideoType.episode,
                        VideoAsset.episode_id.is_(None),
                    ),
                )
            )
            .label("unlinked_count"),
            func.coalesce(
                episodes_per_title.c.total_episode_meta_count, 0
            ).label("title_episode_count"),
            func.bool_or(TitleUserDetails.in_watchlist).label(
                "is_in_watchlist"
            ),
            func.max(TitleUserDetails.watch_count).label("watch_count"),
        )
        .outerjoin(
            VideoAsset,
            TitleFolder.title_folder_id == VideoAsset.title_folder_id,
        )
        .outerjoin(Title, TitleFolder.title_id == Title.title_id)
        .outerjoin(
            TitleUserDetails,
            and_(
                Title.title_id == TitleUserDetails.title_id,
                TitleUserDetails.user_id == user.user_id,
            ),
        )
        .outerjoin(
            episodes_per_title,
            TitleFolder.title_id == episodes_per_title.c.title_id,
        )
        .options(
            selectinload(TitleFolder.title).selectinload(Title.translations)
        )
        .group_by(
            TitleFolder.title_folder_id,
            episodes_per_title.c.total_episode_meta_count,
        )
    )

    # 3. Apply Filters
    if min_size_gb is not None:
        stmt = stmt.having(
            func.sum(VideoAsset.filesize_bytes) >= (min_size_gb * (1024**3))
        )

    if asset_status == "missing_all":
        stmt = stmt.where(func.count(VideoAsset.video_asset_id) == 0)
    elif asset_status == "incomplete":
        stmt = stmt.where(
            func.count(VideoAsset.video_asset_id) > 0,
            func.count(distinct(VideoAsset.episode_id))
            < episodes_per_title.c.total_episode_meta_count,
        )
    elif asset_status == "complete":
        stmt = stmt.where(
            func.count(VideoAsset.video_asset_id) > 0,
            func.count(distinct(VideoAsset.episode_id))
            == episodes_per_title.c.total_episode_meta_count,
        )

    if in_watchlist is not None:
        stmt = stmt.having(
            func.coalesce(func.bool_or(TitleUserDetails.in_watchlist), False)
            == in_watchlist
        )

    if title_type:
        stmt = stmt.where(Title.title_type == title_type)

    # 4. Sorting & Pagination
    is_desc = sort_direction == SortDirection.desc
    total_size_expr = func.coalesce(func.sum(VideoAsset.filesize_bytes), 0)
    completion_expr = func.coalesce(
        func.count(distinct(VideoAsset.episode_id)).cast(Float)
        / func.nullif(episodes_per_title.c.total_episode_meta_count, 0).cast(
            Float
        ),
        0.0,
    )

    if sort_by == "size":
        stmt = stmt.order_by(
            total_size_expr.desc() if is_desc else total_size_expr.asc()
        )
    elif sort_by == "completion":
        stmt = stmt.order_by(
            completion_expr.desc() if is_desc else completion_expr.asc()
        )
    else:
        stmt = stmt.order_by(
            TitleFolder.title_folder_name.desc()
            if is_desc
            else TitleFolder.title_folder_name.asc()
        )

    if page_size > 0:
        offset = (page_number - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

    result = await db.execute(stmt)
    rows = result.all()

    # 5. Build Response Output
    audit_results = []
    for row in rows:
        folder = row.TitleFolder
        total_bytes = row.total_size_bytes or 0
        total_episodes = row.title_episode_count or 0
        linked_episodes = row.unique_episodes_linked_count or 0

        completion_pct = (
            (linked_episodes / total_episodes * 100) if total_episodes > 0 else 100.0
        )
        is_tv = folder.title and folder.title.title_type == TitleType.tv

        quality = build_quality_summary(
            resolutions_raw=row.resolutions or [],
            hdr_types_raw=row.hdr_types or [],
            file_count=row.file_count or 0,
            is_tv=is_tv,
        )

        audit_results.append(
            TitleAuditOut(
                title_folder_id=folder.title_folder_id,
                title_folder_path=folder.title_folder_path,
                title_folder_name=folder.title_folder_name,
                linked_title=(
                    TitleMinimalOut(
                        title_id=folder.title.title_id,
                        name=pick_translation(
                            folder.title.translations,
                            locale_ctx.iso_639_1_list,
                            "name",
                        ),
                        type=folder.title.title_type,
                    )
                    if folder.title
                    else None
                ),
                is_linked=folder.title_id is not None,
                counts=TitleFolderCountsOut(
                    file_count=row.file_count,
                    movie_count=row.movie_count,
                    featurette_count=row.featurette_count,
                    episodes_count=row.episodes_count,
                    unlinked_count=row.unlinked_count,
                    title_episode_count=row.title_episode_count,
                    unique_episodes_linked=row.unique_episodes_linked_count,
                ),
                total_size_bytes=total_bytes,
                total_size_gb=round(total_bytes / (1024**3), 2),
                completion_percentage=round(completion_pct, 2),
                missing_episodes_count=max(0, total_episodes - linked_episodes),
                quality_summary=quality,
                is_in_watchlist=bool(row.is_in_watchlist),
                watch_count=row.watch_count or 0,
            )
        )

    return audit_results


@router.get(
    "/video_assets/audit/{title_folder_id}/details",
    response_model=TitleAuditDetailOut,
)
async def get_video_asset_audit_details(
    title_folder_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lazy-load endpoint for expanding row details (Movie variants or TV Show episode matrix)."""
    # Load Folder + VideoAssets + Title + Seasons + Episodes
    stmt = (
        select(TitleFolder)
        .where(TitleFolder.title_folder_id == title_folder_id)
        .options(
            selectinload(TitleFolder.video_assets),
            selectinload(TitleFolder.title)
            .selectinload(Title.seasons)
            .selectinload(Season.episodes),
        )
    )
    result = await db.execute(stmt)
    folder = result.scalar_one_or_none()

    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    title = folder.title
    is_tv = title and title.title_type == TitleType.tv

    # Case A: Movie or Unlinked Folder -> Return Movie/File Variants
    if not is_tv:
        movie_variants = [
            MovieVariantDetail(
                video_asset_id=asset.video_asset_id,
                file_name=asset.file_name,
                video_type=asset.video_type,
                resolution=asset.resolution,
                hdr_type=asset.hdr_type,
                filesize_gb=round((asset.filesize_bytes or 0) / (1024**3), 2),
                codec=asset.codec,
            )
            for asset in folder.video_assets
        ]
        return TitleAuditDetailOut(
            title_folder_id=title_folder_id,
            title_type="movie",
            movie_variants=movie_variants,
        )

    # Case B: TV Show -> Group by Season and map Episode Video Assets
    assets_by_episode_id: Dict[int, List[VideoAssetOut]] = {}
    for asset in folder.video_assets:
        if asset.episode_id:
            assets_by_episode_id.setdefault(asset.episode_id, []).append(
                VideoAssetOut(
                    video_asset_id=asset.video_asset_id,
                    file_name=asset.file_name,
                    file_path=asset.file_path,
                    video_type=asset.video_type,
                    resolution=asset.resolution,
                    hdr_type=asset.hdr_type,
                    filesize_bytes=asset.filesize_bytes or 0,
                    filesize_gb=round(
                        (asset.filesize_bytes or 0) / (1024**3), 2
                    ),
                    codec=asset.codec,
                    bit_depth=asset.bit_depth,
                    frame_rate=asset.frame_rate,
                )
            )

    seasons_dict: Dict[int, List[EpisodeAuditDetail]] = {}
    sorted_seasons = sorted(
        [s for s in title.seasons if s.season_number != 0],
        key=lambda s: s.season_number,
    )

    for season in sorted_seasons:
        ep_details = []
        sorted_episodes = sorted(
            season.episodes, key=lambda e: e.episode_number
        )
        for ep in sorted_episodes:
            ep_assets = assets_by_episode_id.get(ep.episode_id, [])
            ep_details.append(
                EpisodeAuditDetail(
                    episode_id=ep.episode_id,
                    season_number=season.season_number,
                    episode_number=ep.episode_number,
                    title=getattr(ep, "name", f"Episode {ep.episode_number}"),
                    is_missing=len(ep_assets) == 0,
                    assets=ep_assets,
                )
            )
        seasons_dict[season.season_number] = ep_details

    return TitleAuditDetailOut(
        title_folder_id=title_folder_id,
        title_type="tv",
        seasons=seasons_dict,
    )
