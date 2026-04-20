import json
import re
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set
from rapidfuzz import fuzz
from pymediainfo import MediaInfo
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Season, Title, Episode, VideoAsset, VideoType

# Regex patterns
TITLE_REGEX = re.compile(r"^(.*)\s\((\d{4})\)")
EPISODE_REGEX = re.compile(r"[Ss](\d+)[Ee](\d+)")

# --------- COORDINATING METHOD ---------

async def sync_all_video_assets(db: AsyncSession) -> Dict[str, int]:
    """
    Coordinates the two-phase sync process:
    1. Scan disk and ensure db is a 1:1 reflection of files.
    2. Attempt to link unmapped files to titles/episodes in the db.
    """
    config_raw = os.environ.get("VIDEO_ASSET_CONFIG", "[]")
    libraries = json.loads(config_raw)
    
    active_library_paths = []
    
    metrics = {
        "added_video_assets_count": 0,
        "removed_video_assets_count": 0,
        "added_links_count": 0,
        "removed_links_count": 0
    }

    # Scan disk data to DB
    for lib in libraries:
        lib_path = lib['path']
        active_library_paths.append(lib_path)
            
        dir_metrics = await _sync_directory_to_db(db=db, directory_path=lib_path)
        
        metrics["added_video_assets_count"] += dir_metrics["added_assets"]
        metrics["removed_video_assets_count"] += dir_metrics["removed_assets"]
        metrics["removed_links_count"] += dir_metrics["removed_links"]

    # Prune removed libraries
    pruned_assets, pruned_links = await _prune_removed_libraries(db, active_library_paths)
    metrics["removed_video_assets_count"] += pruned_assets
    metrics["removed_links_count"] += pruned_links

    # Link synced data to titles
    added_links = await link_video_assets(db)
    metrics["added_links_count"] += added_links
    
    return metrics


# --------- DISK SCANNING & METADATA ---------

async def _sync_directory_to_db(db: AsyncSession, directory_path: str) -> Dict[str, int]:
    """Scans the disk, reads mediainfo, and creates/updates unlinked VideoAsset records."""
    root = Path(directory_path)
    metrics = {"added_assets": 0, "removed_assets": 0, "removed_links": 0}
    
    if not root.exists():
        return metrics

    seen_file_paths: Set[str] = set()

    for folder in root.iterdir():
        if not folder.is_dir(): continue

        valid_files = [f for f in folder.rglob("*") if f.suffix.lower() in ['.mkv', '.mp4', '.avi']]
        if not valid_files:
            continue

        # Fetch existing assets for this folder to compare mtimes
        str_paths = [str(f.absolute()) for f in valid_files]
        stmt = select(VideoAsset).where(VideoAsset.file_path.in_(str_paths))
        asset_map = {a.file_path: a for a in (await db.execute(stmt)).scalars().all()}

        # Prep files needing metadata parsing
        files_to_scan = []
        file_mtimes = {}
        for f in valid_files:
            path_str = str(f.absolute())
            mtime = f.stat().st_mtime
            file_mtimes[path_str] = mtime
            asset = asset_map.get(path_str)
            if not asset or getattr(asset, 'mtime', 0) < mtime:
                files_to_scan.append(path_str)

        # Process metadata asynchronously
        parsed_metadata_map = {}
        if files_to_scan:
            async def _parse_worker(path: str):
                return path, await asyncio.to_thread(_extract_media_info, path)
            results = await asyncio.gather(*[_parse_worker(p) for p in files_to_scan])
            parsed_metadata_map = {p: meta for p, meta in results}

        # Upsert records
        for file in valid_files:
            path_str = str(file.absolute())
            metadata = parsed_metadata_map.get(path_str)
            
            # Determine base video type
            rel_parts = file.relative_to(folder).parts[:-1]
            if EPISODE_REGEX.search(file.name):
                v_type = VideoType.episode
            elif rel_parts:
                v_type = VideoType.featurette
            else:
                v_type = VideoType.movie

            is_new = await _upsert_base_media_asset(
                db=db, 
                existing_asset=asset_map.get(path_str),
                v_type=v_type, 
                file_path=file,
                folder_path=folder,
                current_mtime=file_mtimes[path_str],
                metadata=metadata
            )
            
            seen_file_paths.add(path_str)
            if is_new: metrics["added_assets"] += 1

    # Prune stale files that were deleted from disk
    stale_assets, stale_links = await _prune_stale_assets(db, directory_path, seen_file_paths)
    metrics["removed_assets"] += stale_assets
    metrics["removed_links"] += stale_links
    
    return metrics


async def _upsert_base_media_asset(
    db: AsyncSession, 
    existing_asset: Optional[VideoAsset], 
    v_type: VideoType, 
    file_path: Path,
    folder_path: Path,
    current_mtime: float,
    metadata: Optional[Dict[str, Any]]
) -> bool:
    """Updates physical file properties. Leaves linking completely untouched."""
    str_path = str(file_path.absolute())
    str_folder_path = str(folder_path.absolute())
    is_new = False
    
    asset = existing_asset

    if not asset:
        asset = VideoAsset(
            file_path=str_path,
            file_name=file_path.name,
            title_folder_path=str_folder_path,
            title_folder_name=folder_path.name,
            video_type=v_type
            # Notice: title_id and episode_id are implicitly None here
        )
        db.add(asset)
        is_new = True
    else:
        asset.file_name = file_path.name 
        asset.title_folder_path = str_folder_path
        asset.title_folder_name = folder_path.name 
        asset.video_type = v_type

    if metadata is not None:
        asset.filesize_bytes = metadata.get("filesize_bytes")
        asset.duration_ms = metadata.get("duration_ms")
        asset.codec = metadata.get("codec")
        asset.bit_depth = metadata.get("bit_depth")
        asset.frame_rate = metadata.get("frame_rate")
        asset.resolution = metadata.get("resolution")
        asset.hdr_type = metadata.get("hdr_type")
        asset.mtime = current_mtime

    await db.commit()
    return is_new


def _extract_media_info(file_path: str) -> dict:
    try:
        mi = MediaInfo.parse(file_path, parse_speed=0)
        general = mi.general_tracks[0] if mi.general_tracks else None
        video = mi.video_tracks[0] if mi.video_tracks else None

        if not general and not video: return {}

        bit_depth = None
        if video and video.bit_depth:
            digits = ''.join(filter(str.isdigit, str(video.bit_depth)))
            bit_depth = int(digits) if digits else None

        frame_rate = None
        if video and video.frame_rate:
            try: frame_rate = float(video.frame_rate)
            except ValueError: pass

        return {
            "resolution": f"{video.width}x{video.height}" if video and video.width else None,
            "hdr_type": video.hdr_format if video else None,
            "filesize_bytes": general.file_size if general else None,
            "duration_ms": general.duration if general else None,
            "codec": video.format if video else None,
            "bit_depth": bit_depth,
            "frame_rate": frame_rate
        }
    except Exception:
        return {}


# --------- TITLE AND VIDEO ASSET LINKING ---------

async def link_video_assets(
    db: AsyncSession, 
    candidate_title_ids: Optional[List[int]] = None
) -> int:
    """
    Attempts to match video assets to titles via DB properties.
    If specific_folder_name is provided, it only evaluates that folder.
    If candidate_title_ids is provided, it bypasses the year filter and only 
    attempts to match against those specific titles.
    """
    # Grab ALL video assets
    stmt = select(VideoAsset)
        
    result = await db.execute(stmt)
    assets_to_check = result.scalars().all()
    
    if not assets_to_check:
        return 0

    # Group assets by folder name to minimize database queries
    folder_groups: Dict[str, List[VideoAsset]] = {}
    for asset in assets_to_check:
        folder_groups.setdefault(asset.title_folder_name, []).append(asset)

    links_modified = 0

    for folder_name, assets in folder_groups.items():
        match = TITLE_REGEX.match(folder_name)
        if not match: continue

        folder_name_raw, year_str = match.groups()
        target_name_norm = _normalize_string(folder_name_raw)

        # Fetch candidate Titles
        title_stmt = select(Title).options(selectinload(Title.translations))
        
        if candidate_title_ids:
            # Contextual Run: Only check the newly added/updated titles
            title_stmt = title_stmt.where(Title.title_id.in_(candidate_title_ids))
        else:
            # Standard Run: Narrow down search space by year
            target_year = int(year_str)
            title_stmt = title_stmt.where(extract('year', Title.release_date) == target_year)

        candidates = (await db.execute(title_stmt)).scalars().all()
        matched_title = _fuzzy_match_title(candidates, target_name_norm)
        
        if matched_title:
            for asset in assets:
                changed = False
                
                # Check if the title_id actually needs updating
                if asset.title_id != matched_title.title_id:
                    asset.title_id = matched_title.title_id
                    changed = True
                
                # If it's an episode, attempt to link the episode_id
                if asset.video_type == VideoType.episode:
                    ep_match = EPISODE_REGEX.search(asset.file_name)
                    if ep_match:
                        s_num, e_num = map(int, ep_match.groups())
                        ep_stmt = (
                            select(Episode.episode_id)
                            .join(Season)
                            .where(
                                Episode.title_id == matched_title.title_id,
                                Season.season_number == s_num,
                                Episode.episode_number == e_num
                            )
                        )
                        ep_id = (await db.execute(ep_stmt)).scalar_one_or_none()
                        
                        if ep_id and asset.episode_id != ep_id:
                            asset.episode_id = ep_id
                            changed = True

                # Only increment counter if we actually overwrote old data or linked new data
                if changed:
                    links_modified += 1

    if links_modified > 0:
        await db.commit()

    return links_modified


def _fuzzy_match_title(candidates: List[Title], target_name_norm: str) -> Optional[Title]:
    """Helper to handle the fuzzy matching logic for titles."""
    best_fuzzy_score = 0
    matched_title = None

    for candidate in candidates:
        names_to_check = [("Original", candidate.name_original)]
        for trans in candidate.translations:
            if trans.name:
                names_to_check.append((f"Translation ({trans.iso_639_1})", trans.name))

        for _, raw_name in names_to_check:
            db_name_norm = _normalize_string(raw_name)
            if db_name_norm == target_name_norm:
                return candidate # Instant 100% match
            
            score = max(fuzz.ratio(target_name_norm, db_name_norm), 
                        fuzz.partial_ratio(target_name_norm, db_name_norm))
            if score > best_fuzzy_score and score > 80:
                best_fuzzy_score = score
                matched_title = candidate

    return matched_title


def _normalize_string(s: str) -> str:
    if not s: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()


# --------- PRUNING RECORDS ---------

async def _prune_removed_libraries(db: AsyncSession, active_paths: List[str]) -> Tuple[int, int]:
    stmt = select(VideoAsset)
    result = await db.execute(stmt)
    db_assets = result.scalars().all()

    safe_active_paths = [(Path(p).as_posix() + "/") for p in active_paths]
    
    pruned_assets = 0
    pruned_links = 0
    
    for asset in db_assets:
        normalized_db_path = Path(asset.file_path).as_posix()
        is_active = any(normalized_db_path.startswith(sp) for sp in safe_active_paths)

        if not is_active:
            if asset.title_id or asset.episode_id:
                pruned_links += 1
            await db.delete(asset)
            pruned_assets += 1

    if pruned_assets > 0:
        await db.commit()

    return pruned_assets, pruned_links


async def _prune_stale_assets(db: AsyncSession, root_path: str, seen_paths: Set[str]) -> Tuple[int, int]:
    search_path = os.path.join(root_path, '')
    stmt = select(VideoAsset).where(VideoAsset.file_path.like(f"{search_path}%"))
    result = await db.execute(stmt)
    db_assets = result.scalars().all()

    pruned_assets = 0
    pruned_links = 0
    
    for asset in db_assets:
        if asset.file_path not in seen_paths:
            if asset.title_id or asset.episode_id:
                pruned_links += 1
            await db.delete(asset)
            pruned_assets += 1
    
    if pruned_assets > 0:
        await db.commit()
        
    return pruned_assets, pruned_links