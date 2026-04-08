from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_db
from app.models.property import Property, PropertyAmenity
from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyOut,
    PropertyListOut, PropertyStatusUpdate
)
from app.services.search_service import search_properties, search_nearby
from app.services.duplicate_service import run_fraud_checks
import json

router = APIRouter()

LOAD_RELATIONS = [selectinload(Property.images), selectinload(Property.amenities)]


async def get_property_or_404(property_id: str, db: AsyncSession) -> Property:
    result = await db.execute(
        select(Property)
        .options(*LOAD_RELATIONS)
        .where(Property.id == property_id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("/", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
async def create_property(
    payload: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    landlord_id: str = "demo-landlord",
):
    prop = Property(
        landlord_id=landlord_id,
        title=payload.title,
        description=payload.description,
        property_type=payload.property_type,
        bedrooms=payload.bedrooms,
        bathrooms=payload.bathrooms,
        floor_area_sqm=payload.floor_area_sqm,
        furnishing=payload.furnishing,
        price=payload.price,
        price_period=payload.price_period,
        currency=payload.currency,
        address=payload.address,
        city=payload.city,
        neighbourhood=payload.neighbourhood,
        country=payload.country,
        latitude=payload.latitude,
        longitude=payload.longitude,
        virtual_tour_url=payload.virtual_tour_url,
    )
    db.add(prop)
    await db.flush()

    for amenity in (payload.amenities or []):
        db.add(PropertyAmenity(property_id=prop.id, amenity=amenity))

    fraud_flags = await run_fraud_checks(prop.id, payload.description or "", [], db)
    if fraud_flags:
        prop.fraud_flags = json.dumps(fraud_flags)
        prop.needs_review = True

    await db.commit()
    return await get_property_or_404(prop.id, db)


@router.get("/my/listings", response_model=list[PropertyOut])
async def my_listings(
    landlord_id: str = "demo-landlord",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Property)
        .options(*LOAD_RELATIONS)
        .where(Property.landlord_id == landlord_id)
    )
    return result.scalars().all()


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


@router.get("/", response_model=PropertyListOut)
async def list_properties(
    q: Optional[str] = None,
    city: Optional[str] = None,
    neighbourhood: Optional[str] = None,
    property_type: Optional[str] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    currency: Optional[str] = None,
    verified: Optional[bool] = None,
    sort: str = "newest",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
):
    total, properties = await search_properties(
        db, q, city, neighbourhood, property_type,
        min_bedrooms, max_bedrooms, min_price, max_price,
        currency, verified, sort, page, limit
    )
    result = await db.execute(
        select(Property)
        .options(*LOAD_RELATIONS)
        .where(Property.id.in_([p.id for p in properties]))
    )
    loaded = result.scalars().all()
    return PropertyListOut(total=total, page=page, limit=limit, results=loaded)


@router.get("/{property_id}", response_model=PropertyOut)
async def get_property(property_id: str, db: AsyncSession = Depends(get_db)):
    prop = await get_property_or_404(property_id, db)
    prop.view_count += 1
    await db.commit()
    await db.refresh(prop)
    return prop


@router.put("/{property_id}", response_model=PropertyOut)
async def update_property(
    property_id: str,
    payload: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
):
    prop = await get_property_or_404(property_id, db)
    for field, value in payload.model_dump(exclude_none=True).items():
        if field != "amenities":
            setattr(prop, field, value)
    await db.commit()
    return await get_property_or_404(prop.id, db)


@router.patch("/{property_id}/status", response_model=PropertyOut)
async def update_status(
    property_id: str,
    payload: PropertyStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    prop = await get_property_or_404(property_id, db)
    prop.status = payload.status
    await db.commit()
    return await get_property_or_404(prop.id, db)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(property_id: str, db: AsyncSession = Depends(get_db)):
    prop = await get_property_or_404(property_id, db)
    prop.is_active = False
    await db.commit()
