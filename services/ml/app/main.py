from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import valuation, fraud, trends, recommendations
from app.services.model_loader import model_store
from app.config import settings
import numpy as np
import pandas as pd


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_store.load_all()
    print(f"AfriProp ML Service starting — ENV: {settings.ENV}")
    yield
    print("AfriProp ML Service shutting down")


app = FastAPI(
    title="AfriProp ML Service",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(valuation.router,       prefix="/api/v1/ml", tags=["valuation"])
app.include_router(fraud.router,           prefix="/api/v1/ml", tags=["fraud"])
app.include_router(trends.router,          prefix="/api/v1/ml", tags=["trends"])
app.include_router(recommendations.router, prefix="/api/v1/ml", tags=["recommendations"])


@app.get("/health", tags=["health"])
async def health():
    return {
        "status":        "ok",
        "service":       "ml",
        "models_loaded": model_store.loaded,
        "trend_models":  len(model_store.trend_models),
    }


@app.get("/api/v1/ml/models/status", tags=["status"])
async def model_status():
    return {
        "valuation": {"loaded": model_store.valuation_model is not None, "version": "valuation_v1"},
        "fraud":     {"loaded": model_store.fraud_model is not None,     "version": "fraud_v1"},
        "trends":    {"loaded": len(model_store.trend_models) > 0,       "count": len(model_store.trend_models)},
        "encoders":  {"loaded": model_store.label_encoders is not None},
    }


@app.get("/api/v1/ml/debug/valuation", tags=["debug"])
async def debug_valuation():
    """Debug endpoint to test valuation model directly."""
    encoders = model_store.label_encoders
    features = model_store.valuation_meta["features"]

    city_enc          = int(encoders["city"].transform(["Nairobi"])[0])
    neighbourhood_enc = int(encoders["neighbourhood"].transform(["Westlands"])[0])

    row = {
        "bedrooms": 3, "bathrooms": 2, "floor_area_sqm": 120.0,
        "total_rooms": 5, "bed_bath_ratio": 1.5, "is_furnished": 1,
        "distance_to_cbd_km": 3.5, "city_enc": city_enc,
        "neighbourhood_enc": neighbourhood_enc,
        "infrastructure_score": 8.8, "transit_access_score": 8.5,
        "amenity_count": 6, "desirability_score": 8.15, "tier": 1,
        "property_type_apartment": 0, "property_type_house": 1,
        "property_type_commercial": 0, "property_type_bedsitter": 0,
        "furnishing_furnished": 1, "furnishing_semi_furnished": 0,
        "furnishing_unfurnished": 0,
        "price_period_monthly": 1, "price_period_yearly": 0, "price_period_once": 0,
        "season_peak": 1, "season_normal": 0,
    }

    X        = pd.DataFrame([[row[f] for f in features]], columns=features)
    log_pred = float(model_store.valuation_model.predict(X)[0])
    residual_std = model_store.valuation_meta["residual_std"]

    return {
        "city_enc":          city_enc,
        "neighbourhood_enc": neighbourhood_enc,
        "log_pred":          log_pred,
        "estimated_value":   float(np.expm1(log_pred)),
        "confidence_low":    float(np.expm1(log_pred - 1.96 * residual_std)),
        "confidence_high":   float(np.expm1(log_pred + 1.96 * residual_std)),
        "residual_std":      residual_std,
        "features_used":     features,
    }
