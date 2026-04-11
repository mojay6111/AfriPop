from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from app.services.model_loader import model_store

router = APIRouter()


class ValuationRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    bedrooms: int
    bathrooms: int
    floor_area_sqm: float
    property_type: str
    furnishing: str
    price_period: str
    city: str
    neighbourhood: str
    distance_to_cbd_km: float = 5.0
    infrastructure_score: float = 7.0
    transit_access_score: float = 7.0
    amenity_count: int = 3
    tier: int = 2
    listing_month: int = 1


class ValuationResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    estimated_value: float
    confidence_low: float
    confidence_high: float
    currency: str
    model_version: str


CURRENCY_MAP = {
    "Nairobi": "KES", "Mombasa": "KES",
    "Kampala": "UGX", "Lagos": "NGN",
    "Accra": "GHS", "Dar es Salaam": "TZS",
}


def encode_label(encoder, value: str) -> int:
    classes = list(encoder.classes_)
    return int(encoder.transform([value])[0]) if value in classes else 0


@router.post("/valuation", response_model=ValuationResponse)
async def predict_valuation(req: ValuationRequest):
    if not model_store.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")

    encoders = model_store.label_encoders
    meta     = model_store.valuation_meta
    scaler   = model_store.valuation_scaler
    season   = "peak" if req.listing_month in [1, 2, 9, 10] else "normal"

    city_enc          = encode_label(encoders["city"],         req.city)
    neighbourhood_enc = encode_label(encoders["neighbourhood"], req.neighbourhood)

    row = {
        "bedrooms":                  req.bedrooms,
        "bathrooms":                 req.bathrooms,
        "floor_area_sqm":            req.floor_area_sqm,
        "total_rooms":               req.bedrooms + req.bathrooms,
        "bed_bath_ratio":            req.bedrooms / max(req.bathrooms, 1),
        "is_furnished":              int(req.furnishing == "furnished"),
        "distance_to_cbd_km":        req.distance_to_cbd_km,
        "city_enc":                  city_enc,
        "neighbourhood_enc":         neighbourhood_enc,
        "infrastructure_score":      req.infrastructure_score,
        "transit_access_score":      req.transit_access_score,
        "amenity_count":             req.amenity_count,
        "desirability_score": (
            req.infrastructure_score * 0.5 +
            req.transit_access_score * 0.3 +
            req.amenity_count        * 0.2
        ),
        "tier":                      req.tier,
        "property_type_apartment":   int(req.property_type == "apartment"),
        "property_type_house":       int(req.property_type == "house"),
        "property_type_commercial":  int(req.property_type == "commercial"),
        "property_type_bedsitter":   int(req.property_type == "bedsitter"),
        "furnishing_furnished":      int(req.furnishing == "furnished"),
        "furnishing_semi_furnished": int(req.furnishing == "semi_furnished"),
        "furnishing_unfurnished":    int(req.furnishing == "unfurnished"),
        "price_period_monthly":      int(req.price_period == "monthly"),
        "price_period_yearly":       int(req.price_period == "yearly"),
        "price_period_once":         int(req.price_period == "once"),
        "season_peak":               int(season == "peak"),
        "season_normal":             int(season == "normal"),
    }

    features     = meta["features"]
    numeric_cols = meta["numeric_cols"]

    X = pd.DataFrame([[row[f] for f in features]], columns=features)
    X[numeric_cols] = scaler.transform(X[numeric_cols])

    log_pred     = float(model_store.valuation_model.predict(X)[0])
    residual_std = meta["residual_std"]

    estimated = float(np.expm1(log_pred))
    low       = float(np.expm1(log_pred - 1.96 * residual_std))
    high      = float(np.expm1(log_pred + 1.96 * residual_std))
    currency  = CURRENCY_MAP.get(req.city, "KES")

    return ValuationResponse(
        estimated_value=round(estimated, -2),
        confidence_low=round(low, -2),
        confidence_high=round(high, -2),
        currency=currency,
        model_version="valuation_v1",
    )
