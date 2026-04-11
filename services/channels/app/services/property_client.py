import httpx
from app.config import settings

BASE_URL = settings.PROPERTY_SERVICE_URL


async def search_properties(
    city: str = None,
    property_type: str = None,
    min_bedrooms: int = None,
    max_price: float = None,
    limit: int = 3,
) -> list:
    params = {"limit": limit}
    if city:           params["city"]         = city
    if property_type:  params["property_type"] = property_type
    if min_bedrooms:   params["min_bedrooms"]  = min_bedrooms
    if max_price:      params["max_price"]     = max_price

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{BASE_URL}/api/v1/properties/", params=params)
            data = r.json()
            return data.get("results", [])
    except Exception as e:
        print(f"Property search failed: {e}")
        return []


async def get_property(property_id: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{BASE_URL}/api/v1/properties/{property_id}")
            return r.json()
    except Exception as e:
        print(f"Get property failed: {e}")
        return {}


def format_listing_sms(prop: dict, index: int) -> str:
    price     = f"{prop.get('price', 0):,.0f}"
    currency  = prop.get("currency", "KES")
    bedrooms  = prop.get("bedrooms", 0)
    prop_type = prop.get("property_type", "property")
    nb        = prop.get("neighbourhood", "")
    city      = prop.get("city", "")
    period    = prop.get("price_period", "monthly")
    return (
        f"{index}. {bedrooms}BR {prop_type} in {nb}, {city}\n"
        f"   {currency} {price}/{period}\n"
        f"   ID: {prop.get('id', '')[:8]}"
    )
