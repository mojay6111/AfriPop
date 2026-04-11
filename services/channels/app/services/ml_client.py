import httpx
from app.config import settings

BASE_URL = settings.ML_SERVICE_URL


async def get_valuation(
    city: str,
    neighbourhood: str,
    bedrooms: int,
    floor_area_sqm: float,
    property_type: str = "apartment",
    furnishing: str = "unfurnished",
    price_period: str = "monthly",
    tier: int = 2,
) -> dict:
    payload = {
        "city":            city,
        "neighbourhood":   neighbourhood,
        "bedrooms":        bedrooms,
        "bathrooms":       max(1, bedrooms - 1),
        "floor_area_sqm":  floor_area_sqm,
        "property_type":   property_type,
        "furnishing":      furnishing,
        "price_period":    price_period,
        "tier":            tier,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.post(
                f"{BASE_URL}/api/v1/ml/valuation",
                json=payload
            )
            return r.json()
    except Exception as e:
        print(f"ML valuation failed: {e}")
        return {}


async def get_trend(city: str, neighbourhood: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{BASE_URL}/api/v1/ml/trends",
                json={"city": city, "neighbourhood": neighbourhood}
            )
            return r.json()
    except Exception as e:
        print(f"ML trend failed: {e}")
        return {}


def format_valuation_sms(result: dict, city: str, bedrooms: int) -> str:
    if not result:
        return "Valuation service unavailable. Try again later."
    value    = result.get("estimated_value", 0)
    low      = result.get("confidence_low", 0)
    high     = result.get("confidence_high", 0)
    currency = result.get("currency", "KES")
    return (
        f"AfriProp AI Valuation\n"
        f"{bedrooms}BR in {city}:\n"
        f"Est: {currency} {value:,.0f}\n"
        f"Range: {currency} {low:,.0f} - {high:,.0f}"
    )
