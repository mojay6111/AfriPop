from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from app.models.property import Property, PropertyStatus
from typing import Optional
import math


async def search_properties(
    db: AsyncSession,
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
    page: int = 1,
    limit: int = 20,
):
    filters = [Property.is_active == True, Property.status == PropertyStatus.available]

    if city:
        filters.append(func.lower(Property.city) == city.lower())
    if neighbourhood:
        filters.append(func.lower(Property.neighbourhood).contains(neighbourhood.lower()))
    if property_type:
        filters.append(Property.property_type == property_type)
    if min_bedrooms is not None:
        filters.append(Property.bedrooms >= min_bedrooms)
    if max_bedrooms is not None:
        filters.append(Property.bedrooms <= max_bedrooms)
    if min_price is not None:
        filters.append(Property.price >= min_price)
    if max_price is not None:
        filters.append(Property.price <= max_price)
    if currency:
        filters.append(Property.currency == currency.upper())
    if verified:
        filters.append(Property.verification_status == "verified")
    if q:
        filters.append(
            or_(
                func.lower(Property.title).contains(q.lower()),
                func.lower(Property.description).contains(q.lower()),
                func.lower(Property.neighbourhood).contains(q.lower()),
            )
        )

    sort_map = {
        "newest": Property.created_at.desc(),
        "oldest": Property.created_at.asc(),
        "price_asc": Property.price.asc(),
        "price_desc": Property.price.desc(),
        "most_viewed": Property.view_count.desc(),
    }
    order = sort_map.get(sort, Property.created_at.desc())

    count_q = select(func.count()).select_from(Property).where(and_(*filters))
    count_result = await db.execute(count_q)
    total = count_result.scalar()

    offset = (page - 1) * limit
    result = await db.execute(
        select(Property).where(and_(*filters)).order_by(order).offset(offset).limit(limit)
    )
    properties = result.scalars().all()
    return total, properties


def haversine_distance(lat1, lng1, lat2, lng2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def search_nearby(
    db: AsyncSession,
    lat: float,
    lng: float,
    radius_km: float = 5.0,
    limit: int = 20,
):
    result = await db.execute(
        select(Property).where(
            and_(
                Property.is_active == True,
                Property.status == PropertyStatus.available,
                Property.latitude != None,
                Property.longitude != None,
            )
        )
    )
    all_props = result.scalars().all()
    nearby = []
    for prop in all_props:
        dist = haversine_distance(lat, lng, prop.latitude, prop.longitude)
        if dist <= radius_km:
            nearby.append((prop, round(dist, 2)))
    nearby.sort(key=lambda x: x[1])
    return nearby[:limit]
