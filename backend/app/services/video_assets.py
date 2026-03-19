import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set
from rapidfuzz import fuzz
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

        match = TITLE_REGEX.match(folder.name)
        if not match:
            unmapped_items.append({
                "path": str(folder),
                "failure_reason": "Name doesn't match the required 'Title (Year)' format.",
                "context": {"folder_name": folder.name}
            })
            continue

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

        if not candidates:
            unmapped_items.append({
                "path": str(folder),
                "failure_reason": f"No titles of type '{content_type}' found in DB for the exact year {target_year}.",
                "context": {
                    "target_name": folder_name_raw,
                    "target_year": target_year,
                    "requested_type": content_type
                }
            })
            continue

        matched_title = None
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
                
                s_full = fuzz.ratio(target_name_norm, db_name_norm)
                s_part = fuzz.partial_ratio(target_name_norm, db_name_norm)
                score = max(s_full, s_part)

                if score > best_fuzzy_score:
                    best_fuzzy_score = score
                    if score > 80:
                        matched_title = candidate

            if matched_title and best_fuzzy_score == 100:
                break

        if not matched_title or (best_fuzzy_score < 80):
            unmapped_items.append({
                "path": str(folder),
                "failure_reason": f"No confident {content_type} match found in the database.",
                "context": {
                    "target_name_norm": target_name_norm,
                    "target_year": target_year,
                    "best_fuzzy_score": best_fuzzy_score,
                    "type_filter": content_type
                }
            })
        else:
        
            failed_files, found_paths, added_count = await _process_title_folder(db, matched_title, folder)
            unmapped_items.extend(failed_files)
            seen_file_paths.update(found_paths)
            added_in_dir += added_count

    await _prune_stale_assets(db, directory_path, seen_file_paths)

    return unmapped_items, added_in_dir


def _normalize_string(s: str) -> str:
    if not s: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()


async def _process_title_folder(db: AsyncSession, title: Title, folder_path: Path) -> Tuple[List[Dict[str, Any]], Set[str], int]:
    unmapped_files: List[Dict[str, Any]] = []
    processed_paths: Set[str] = set()
    added_count = 0
    
    for file in folder_path.rglob("*"):
        if file.suffix.lower() not in ['.mkv', '.mp4', '.avi']:
            continue
        
        v_type = VideoType.movie if title.title_type == TitleType.movie else VideoType.episode
        
        rel_parts = file.relative_to(folder_path).parts[:-1]
        if rel_parts:
            has_season_folder = any(SEASON_REGEX.search(part) for part in rel_parts)
            if not has_season_folder:
                v_type = VideoType.featurette

        if v_type == VideoType.episode:
            episode_id, error_msg = await _match_episode_to_db(db, title, file)
            if not episode_id:
                unmapped_files.append({
                    "path": str(file),
                    "failure_reason": error_msg,
                    "context": {
                        "title_id": title.title_id,
                        "title_name": title.name_original,
                        "file_name": file.name
                    }
                })
                continue 
            
        
            path_str, is_new = await _upsert_media_asset(db, None, episode_id, v_type, file)
            processed_paths.add(path_str)
            if is_new: added_count += 1
        else:
        
            path_str, is_new = await _upsert_media_asset(db, title.title_id, None, v_type, file)
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


async def _upsert_media_asset(db: AsyncSession, title_id, episode_id, v_type, file_path: Path) -> Tuple[str, bool]:
    str_path = str(file_path.absolute())
    stmt = select(VideoAsset).where(VideoAsset.file_path == str_path)
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()
    
    hdr_match = HDR_REGEX.search(file_path.name)
    res_match = RES_REGEX.search(file_path.name)
    resolution = None
    if res_match:
        val = res_match.group(1).lower()
        if val == "4k":
            resolution = "2160p"
        else:
            resolution = val
    
    is_new = False
    if not asset:
        asset = VideoAsset(
            file_path=str_path,
            file_name=file_path.name,
            title_id=title_id,
            episode_id=episode_id,
            video_type=v_type,
            resolution=resolution if resolution else None,
            is_hdr=True if hdr_match else False
        )
        db.add(asset)
        is_new = True
    else:
        asset.file_name = file_path.name 
        asset.resolution = resolution if resolution else asset.resolution
        asset.is_hdr = True if hdr_match else asset.is_hdr

    await db.commit()
    return str_path, is_new
