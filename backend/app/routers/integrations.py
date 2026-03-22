from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.integrations.jellyfin import fetch_jellyfin_titles
from app.models import Title

router = APIRouter()

@router.post("/jellyfin/sync")
async def sync_jellyfin_links(db: AsyncSession = Depends(get_db)):
    try:
        jellyfin_data = await fetch_jellyfin_titles()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    items = jellyfin_data.get("Items", [])
    
    jellyfin_map = {}
    for item in items:
        p_ids = item.get("ProviderIds", {})
        tmdb_id_str = p_ids.get("Tmdb")
        if tmdb_id_str:
            try:
                jellyfin_map[int(tmdb_id_str)] = item.get("Id")
            except ValueError:
                continue

    stmt = select(Title).where(
        or_(
            Title.tmdb_id.in_(jellyfin_map.keys()),
            Title.jellyfin_id.is_not(None)
        )
    )
    result = await db.execute(stmt)
    titles_to_check = result.scalars().all()

    updated_count = 0
    removed_count = 0
    
    for title in titles_to_check:
        new_jf_id = jellyfin_map.get(title.tmdb_id)
        
        if title.jellyfin_id != new_jf_id:
            if new_jf_id is None:
                removed_count += 1
            else:
                updated_count += 1
                
            title.jellyfin_id = new_jf_id

    if updated_count > 0 or removed_count > 0:
        await db.commit()

    return {
        "message": "Sync completed successfully.",
        "details": {
            "newly_linked_or_updated": updated_count,
            "removed_links": removed_count,
            "total_titles_processed": len(titles_to_check),
            "jellyfin_library_size": jellyfin_data.get('TotalRecordCount', 0)
        }
    }
