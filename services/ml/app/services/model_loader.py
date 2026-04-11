import joblib
import json
import numpy as np
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parents[2] / "app" / "models"


def forecast_trend(model: dict, periods: int = 6) -> list:
    import pandas as pd
    last_month = pd.to_datetime(model["last_month_str"] + "-01")
    forecasts  = []
    for i in range(1, periods + 1):
        future_month = last_month + pd.DateOffset(months=i)
        x_idx        = model["last_index"] + i
        month_num    = future_month.month
        log_trend    = model["intercept"] + model["slope"] * x_idx
        seasonal_adj = model["seasonal_by_month"].get(month_num, 0.0)
        log_forecast = log_trend + seasonal_adj
        forecasts.append({
            "month":     future_month.strftime("%Y-%m"),
            "predicted": round(float(np.expm1(log_forecast)), 0),
        })
    return forecasts


class ModelStore:
    def __init__(self):
        self.valuation_model    = None
        self.valuation_meta     = None
        self.valuation_scaler   = None
        self.label_encoders     = None
        self.fraud_model        = None
        self.fraud_scaler       = None
        self.fraud_city_encoder = None
        self.fraud_meta         = None
        self.trend_meta         = None
        self.trend_models       = {}
        self.loaded             = False

    def load_all(self):
        print(f"Loading ML models from: {MODELS_DIR}")

        self.valuation_model  = joblib.load(MODELS_DIR / "valuation_v1.pkl")
        self.valuation_meta   = joblib.load(MODELS_DIR / "valuation_meta_v1.pkl")
        self.valuation_scaler = joblib.load(MODELS_DIR / "scaler.pkl")
        self.label_encoders   = joblib.load(MODELS_DIR / "label_encoders.pkl")
        print("  valuation_v1.pkl + scaler + encoders loaded")

        self.fraud_model        = joblib.load(MODELS_DIR / "fraud_v1.pkl")
        self.fraud_scaler       = joblib.load(MODELS_DIR / "fraud_scaler_v1.pkl")
        self.fraud_city_encoder = joblib.load(MODELS_DIR / "fraud_city_encoder_v1.pkl")
        with open(MODELS_DIR / "fraud_meta_v1.json") as f:
            self.fraud_meta = json.load(f)
        print("  fraud_v1.pkl loaded")

        with open(MODELS_DIR / "trend_meta.json") as f:
            self.trend_meta = json.load(f)
        trend_dir = MODELS_DIR / "trend_models"
        for pkl_file in trend_dir.glob("*.pkl"):
            data = joblib.load(pkl_file)
            if isinstance(data, dict) and "model" in data:
                self.trend_models[pkl_file.stem] = data["model"]
            else:
                self.trend_models[pkl_file.stem] = data
        print(f"  trend models loaded: {len(self.trend_models)}")

        self.loaded = True
        print("All models loaded successfully.")


model_store = ModelStore()
