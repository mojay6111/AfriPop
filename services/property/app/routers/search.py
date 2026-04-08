from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.property import NearbyResult
from app.services.search_service import search_nearby

router = APIRouter()


@router.get("/nearby")
async def nearby_properties(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=5.0, le=50.0),
    limit: int = Query(default=20, le=50),
    db: AsyncSession = Depends(get_db),
):
    results = await search_nearby(db, lat, lng, radius_km, limit)
    return {
        "count": len(results),
        "radius_km": radius_km,
        "results": [
            {"distance_km": dist, "property": prop}
            for prop, dist in results
        ],
    }
