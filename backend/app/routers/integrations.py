from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.integrations.jellyfin import fetch_jellyfin_titles
from app.models import Title

router = APIRouter()

@router.post("/jellyfin/sync")
async def sync_jellyfin_links(
    db: AsyncSession = Depends(get_db),
):
    # Fetch jellyfin data
    jellyfin_data = await fetch_jellyfin_titles()
    items = jellyfin_data.get("Items", [])
    
    # Map Jellyfin TMDB IDs to their Internal IDs
    jellyfin_map = {}
    for item in items:
        p_ids = item.get("ProviderIds", {})
        tmdb_id = p_ids.get("Tmdb")
        if tmdb_id:
            try:
                jellyfin_map[int(tmdb_id)] = item.get("Id")
            except ValueError:
                continue

    # Find local titles that exist in the Jellyfin map
    stmt = select(Title).where(Title.tmdb_id.in_(jellyfin_map.keys()))
    result = await db.execute(stmt)
    local_titles = result.scalars().all()

    # Perform the update and track changes
    updated_count = 0
    for title in local_titles:
        new_jf_id = jellyfin_map.get(title.tmdb_id)
        
        if title.jellyfin_id != new_jf_id:
            title.jellyfin_id = new_jf_id
            updated_count += 1

    # Prepare statistics
    total_in_jellyfin = jellyfin_data.get('TotalRecordCount', 0)
    total_matched_locally = len(local_titles)
    already_linked_count = total_matched_locally - updated_count

    if updated_count > 0:
        await db.commit()

    return {
        "message": "Sync completed successfully",
        "details": {
            "newly_linked": updated_count,
            "already_linked": already_linked_count,
            "total_matched_in_library": total_matched_locally,
            "jellyfin_library_size": total_in_jellyfin
        }
    }