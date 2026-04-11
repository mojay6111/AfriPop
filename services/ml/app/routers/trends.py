from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from app.services.model_loader import model_store, forecast_trend

router = APIRouter()


class TrendRequest(BaseModel):
    city: str
    neighbourhood: str
    forecast_months: int = 6


class MonthForecast(BaseModel):
    month: str
    predicted: float


class TrendResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    city: str
    neighbourhood: str
    current_median: float
    forecast: List[MonthForecast]
    trend: str
    trend_pct: float
    model_version: str


def make_safe_key(city: str, neighbourhood: str) -> str:
    return f"{city}_{neighbourhood}".replace(" ", "_").replace("|", "_")


@router.post("/trends", response_model=TrendResponse)
async def predict_trend(req: TrendRequest):
    if not model_store.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")

    safe_key   = make_safe_key(req.city, req.neighbourhood)
    model_data = model_store.trend_models.get(safe_key)

    if not model_data:
        available = list(model_store.trend_models.keys())[:5]
        raise HTTPException(
            status_code=404,
            detail=f"No trend model for {req.city}|{req.neighbourhood}. "
                   f"Sample available: {available}"
        )

    forecasts = forecast_trend(model_data, periods=req.forecast_months)

    nb_meta = next(
        (n for n in model_store.trend_meta["neighbourhoods"]
         if n["city"] == req.city and n["neighbourhood"] == req.neighbourhood),
        None
    )

    trend_pct = nb_meta["trend_pct"]  if nb_meta else 0
    trend     = nb_meta["trend"]      if nb_meta else "unknown"

    # Get current median from first forecast entry working backwards
    # Use the model intercept + last_index to reconstruct current price
    current_log   = model_data["intercept"] + model_data["slope"] * model_data["last_index"]
    current_median = round(float(np.expm1(current_log)), 0)

    return TrendResponse(
        city=req.city,
        neighbourhood=req.neighbourhood,
        current_median=current_median,
        forecast=[MonthForecast(**f) for f in forecasts],
        trend=trend,
        trend_pct=trend_pct,
        model_version="trend_linear_v1",
    )
