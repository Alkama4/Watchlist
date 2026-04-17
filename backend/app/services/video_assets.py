import json
import re
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set
from rapidfuzz import fuzz
from pymediainfo import MediaInfo
from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Season, Title, Episode, VideoAsset, VideoType, TitleType

# Regex patterns
TITLE_REGEX = re.compile(r"^(.*)\s\((\d{4})\)")
SEASON_REGEX = re.compile(r"(?i)(season\s*\d+|s\d+)")
EPISODE_REGEX = re.compile(r"[Ss](\d+)[Ee](\d+)")
RES_REGEX = re.compile(r"(2160p|1080p|720p|4k)", re.IGNORECASE)
HDR_REGEX = re.compile(r"(HDR)", re.IGNORECASE)


# --------- COORDINATING METHOD ---------

async def sync_all_video_assets(db: AsyncSession) -> Dict[str, Any]:
    unconnected = []
    config_raw = os.environ.get("VIDEO_ASSET_CONFIG", "[]")
    libraries = json.loads(config_raw)
    
    active_library_paths = []
    total_added_links = 0

    for lib in libraries:
        lib_path = lib['path']
        active_library_paths.append(lib_path)
        
        # Safely convert string to Enum, handle None/null
        raw_type = lib.get('type')
        content_type = TitleType(raw_type) if raw_type else None
            
        results, added = await _scan_directory(
            db=db, 
            directory_path=lib_path, 
            content_type=content_type
        )
        unconnected.extend(results)
        total_added_links += added

    pruned_count = await _prune_removed_libraries(db, active_library_paths)

    total_links_stmt = select(func.count()).select_from(VideoAsset)
    total_links = (await db.execute(total_links_stmt)).scalar() or 0

    total_titles_stmt = (
        select(func.count(func.distinct(func.coalesce(VideoAsset.title_id, Episode.title_id))))
        .select_from(VideoAsset)
        .outerjoin(Episode, VideoAsset.episode_id == Episode.episode_id)
    )
    total_titles_with_links = (await db.execute(total_titles_stmt)).scalar() or 0
    
    return {
        "total_links": total_links,
        "total_titles_with_links": total_titles_with_links,
        "added_links": total_added_links,
        "removed_links": pruned_count,
        "unlinked_files": unconnected,
    }


# --------- PRUNING RECORDS ---------
async def _prune_removed_libraries(db: AsyncSession, active_paths: List[str]):
    stmt = select(VideoAsset)
    result = await db.execute(stmt)
    db_assets = result.scalars().all()

    safe_active_paths = [
        (Path(p).as_posix() + "/") for p in active_paths
    ]
    
    pruned_count = 0
    for asset in db_assets:
        normalized_db_path = Path(asset.file_path).as_posix()
        is_active = any(
            normalized_db_path.startswith(safe_path) 
            for safe_path in safe_active_paths
        )

        if not is_active:
            await db.delete(asset)
            pruned_count += 1

    if pruned_count > 0:
        await db.commit()

    return pruned_count


async def _prune_stale_assets(db: AsyncSession, root_path: str, seen_paths: Set[str]):
    search_path = os.path.join(root_path, '')
    stmt = select(VideoAsset).where(VideoAsset.file_path.like(f"{search_path}%"))
    result = await db.execute(stmt)
    db_assets = result.scalars().all()

    pruned_count = 0
    for asset in db_assets:
        if asset.file_path not in seen_paths:
            await db.delete(asset)
            pruned_count += 1
    
    if pruned_count > 0:
        await db.commit()
        

# --------- SCANNING AND STORING ---------

async def _scan_directory(
    db: AsyncSession, 
    directory_path: str, 
    content_type: Optional[TitleType] = None
) -> Tuple[List[Dict[str, Any]], int]:
    root = Path(directory_path)
    if not root.exists():
        return [{"path": directory_path, "failure_reason": "Directory does not exist"}], 0

    seen_file_paths: Set[str] = set()
    unmapped_items = []
    added_in_dir = 0

    for folder in root.iterdir():
        if not folder.is_dir(): continue

        matched_title = None
        match = TITLE_REGEX.match(folder.name)
        
        if match:
            folder_name_raw, year_str = match.groups()
            target_year = int(year_str)
            target_name_norm = _normalize_string(folder_name_raw)

            stmt = (
                select(Title)
                .where(extract('year', Title.release_date) == target_year)
                .options(selectinload(Title.translations))
            )
            if content_type:
                stmt = stmt.where(Title.title_type == content_type)

            result = await db.execute(stmt)
            candidates = result.scalars().all()

            best_fuzzy_score = 0
            for candidate in candidates:
                names_to_check = [("Original", candidate.name_original)]
                for trans in candidate.translations:
                    if trans.name:
                        names_to_check.append((f"Translation ({trans.iso_639_1})", trans.name))

                for source, raw_name in names_to_check:
                    db_name_norm = _normalize_string(raw_name)
                    if db_name_norm == target_name_norm:
                        matched_title = candidate
                        best_fuzzy_score = 100
                        break
                    
                    score = max(fuzz.ratio(target_name_norm, db_name_norm), 
                                fuzz.partial_ratio(target_name_norm, db_name_norm))
                    if score > best_fuzzy_score and score > 80:
                        best_fuzzy_score = score
                        matched_title = candidate
                
                if matched_title and best_fuzzy_score == 100:
                    break

        # If no match was found, we track it for the report, but we NO LONGER 'continue'
        if not matched_title:
            unmapped_items.append({
                "path": str(folder),
                "failure_reason": "No matching Title found in database.",
                "context": {"folder_name": folder.name}
            })

        # Process the folder regardless of whether matched_title is a Title object or None
        failed_files, found_paths, added_count = await _process_title_folder(
            db,
            matched_title,
            folder
        )
        unmapped_items.extend(failed_files)
        seen_file_paths.update(found_paths)
        added_in_dir += added_count

    await _prune_stale_assets(db, directory_path, seen_file_paths)
    return unmapped_items, added_in_dir


def _normalize_string(s: str) -> str:
    if not s: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()


async def _process_title_folder(
    db: AsyncSession,
    title: Optional[Title],
    folder_path: Path,
) -> Tuple[List[Dict[str, Any]], Set[str], int]:
    
    unmapped_files: List[Dict[str, Any]] = []
    processed_paths: Set[str] = set()
    added_count = 0
    
    valid_files = [f for f in folder_path.rglob("*") if f.suffix.lower() in ['.mkv', '.mp4', '.avi']]
    if not valid_files:
        return unmapped_files, processed_paths, added_count

    # Batch fetch existing assets
    str_paths = [str(f.absolute()) for f in valid_files]
    stmt = select(VideoAsset).where(VideoAsset.file_path.in_(str_paths))
    result = await db.execute(stmt)
    asset_map = {a.file_path: a for a in result.scalars().all()}

    # Metadata scanning prep
    files_to_scan = []
    file_mtimes = {}
    for f in valid_files:
        path_str = str(f.absolute())
        mtime = f.stat().st_mtime
        file_mtimes[path_str] = mtime
        asset = asset_map.get(path_str)
        if not asset or getattr(asset, 'mtime', 0) < mtime:
            files_to_scan.append(path_str)

    parsed_metadata_map = {}
    if files_to_scan:
        async def _parse_worker(path: str):
            return path, await asyncio.to_thread(_extract_media_info, path)
        results = await asyncio.gather(*[_parse_worker(p) for p in files_to_scan])
        parsed_metadata_map = {p: meta for p, meta in results}

    for file in valid_files:
        path_str = str(file.absolute())
        metadata = parsed_metadata_map.get(path_str)
        
        # Determine type and IDs
        ep_id = None
        t_id = title.title_id if title else None
        
        rel_parts = file.relative_to(folder_path).parts[:-1]
        has_ep_pattern = EPISODE_REGEX.search(file.name)
        if has_ep_pattern:
            # If the file name contains ExxSxx -> episode.
            v_type = VideoType.episode
        elif rel_parts:
            # If its in a subfolder -> featurette.
            v_type = VideoType.featurette
        else:
            # Else it must be a movie since its in root
            # directory (and didn't match episode regex).
            v_type = VideoType.movie

        # Handle IDs based on matched Title
        t_id = title.title_id if title else None
        ep_id = None

        if v_type == VideoType.episode and title:
            ep_id, _ = await _match_episode_to_db(db, title, file)

        is_new = await _upsert_media_asset(
            db=db, 
            existing_asset=asset_map.get(path_str),
            title_id=t_id, 
            episode_id=ep_id, 
            v_type=v_type, 
            file_path=file,
            folder_path=folder_path,
            current_mtime=file_mtimes[path_str],
            metadata=metadata
        )
        
        processed_paths.add(path_str)
        if is_new: added_count += 1
            
    return unmapped_files, processed_paths, added_count


async def _match_episode_to_db(db: AsyncSession, title: Title, file_path: Path) -> Tuple[Optional[int], Optional[str]]:
    match = EPISODE_REGEX.search(file_path.name)
    if not match:
        return None, "Missing SxxExx pattern in filename."
    
    s_num, e_num = map(int, match.groups())
    stmt = (
        select(Episode.episode_id)
        .join(Season)
        .where(
            Episode.title_id == title.title_id,
            Season.season_number == s_num,
            Episode.episode_number == e_num
        )
    )
    result = await db.execute(stmt)
    ep_id = result.scalar_one_or_none()
    
    if not ep_id:
        return None, f"S{s_num:02}E{e_num:02} not found in DB for this title."
        
    return ep_id, None


async def _upsert_media_asset(
    db: AsyncSession, 
    existing_asset: Optional[VideoAsset], 
    title_id: Optional[int], 
    episode_id: Optional[int], 
    v_type: VideoType, 
    file_path: Path,
    folder_path: Path,
    current_mtime: float,
    metadata: Optional[Dict[str, Any]]
) -> bool:
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
            title_id=title_id,
            episode_id=episode_id,
            video_type=v_type
        )
        db.add(asset)
        is_new = True
    else:
        # Sync even if existing, as title_id/episode_id might have been matched since last scan
        asset.file_name = file_path.name 
        asset.title_folder_path = str_folder_path
        asset.title_folder_name = folder_path.name 
        asset.title_id = title_id
        asset.episode_id = episode_id
        asset.video_type = v_type

    if metadata is not None:
        asset.filesize_bytes = metadata.get("filesize_bytes")
        asset.duration_ms = metadata.get("duration_ms")
        asset.codec = metadata.get("codec")
        asset.bit_depth = metadata.get("bit_depth")
        asset.frame_rate = metadata.get("frame_rate")
        
        if metadata.get("resolution"):
            asset.resolution = metadata["resolution"]
        else:
            res_match = RES_REGEX.search(file_path.name)
            if res_match:
                asset.resolution = "2160p" if res_match.group(1).lower() == "4k" else res_match.group(1).lower()
        
        asset.hdr_type = metadata.get("hdr_type")
        asset.mtime = current_mtime

    await db.commit()
    return is_new


def _extract_media_info(file_path: str) -> dict:
    """Reads file headers using libmediainfo. Runs synchronously."""
    try:
        print(f"Reading metadata for {file_path}")
        mi = MediaInfo.parse(file_path, parse_speed=0)
        general = mi.general_tracks[0] if mi.general_tracks else None
        video = mi.video_tracks[0] if mi.video_tracks else None

        if not general and not video:
            return {}

        bit_depth = None
        if video and video.bit_depth:
            digits = ''.join(filter(str.isdigit, str(video.bit_depth)))
            bit_depth = int(digits) if digits else None

        frame_rate = None
        if video and video.frame_rate:
            try:
                frame_rate = float(video.frame_rate)
            except ValueError:
                pass

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