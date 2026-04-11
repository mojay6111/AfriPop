from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import pandas as pd
from app.services.model_loader import model_store

router = APIRouter()


class FraudRequest(BaseModel):
    price: float
    city: str
    neighbourhood: str
    property_type: str = "apartment"
    price_period: str = "monthly"
    bedrooms: int = 2
    floor_area_sqm: float = 60.0
    infrastructure_score: float = 7.0
    transit_access_score: float = 7.0
    amenity_count: int = 3
    tier: int = 2
    distance_to_cbd_km: float = 5.0
    account_age_days: int = 365
    listing_count: int = 1
    nb_median_price: Optional[float] = None


class FraudResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    fraud_score: float
    risk_level: str
    flags: List[str]
    recommendation: str
    model_version: str


def rule_based_score(price_deviation, account_age_days,
                     listing_count, amenity_count, nb_median, price):
    score = 0.0
    flags = []

    if price_deviation > 0.40:
        score += 0.35
        flags.append("price_anomaly")

    if account_age_days < 7:
        score += 0.25
        flags.append("new_account")
    elif account_age_days < 30:
        score += 0.10
        flags.append("recent_account")

    if listing_count > 10:
        score += 0.20
        flags.append("high_listing_density")
    elif listing_count > 5:
        score += 0.10
        flags.append("elevated_listing_density")

    if nb_median and price < nb_median * 0.60:
        score += 0.15
        flags.append("below_market_60pct")

    if amenity_count == 0 and price_deviation > 0.20:
        score += 0.05
        flags.append("no_amenities_underpriced")

    return min(score, 1.0), flags


@router.post("/fraud", response_model=FraudResponse)
async def score_fraud(req: FraudRequest):
    if not model_store.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")

    nb_median = req.nb_median_price or req.price
    price_deviation = max(0, (nb_median - req.price) / nb_median) if nb_median > 0 else 0

    rule_score, flags = rule_based_score(
        price_deviation, req.account_age_days,
        req.listing_count, req.amenity_count,
        nb_median, req.price
    )

    risk_level = (
        "high"   if rule_score >= 0.55 else
        "medium" if rule_score >= 0.30 else
        "low"
    )
    recommendation = (
        "hold_for_review" if risk_level == "high"   else
        "flag_for_check"  if risk_level == "medium" else
        "approve"
    )

    return FraudResponse(
        fraud_score=round(rule_score, 4),
        risk_level=risk_level,
        flags=flags,
        recommendation=recommendation,
        model_version="fraud_v1",
    )
