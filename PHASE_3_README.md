## Phase 3 — AI & Data Science Layer

### What This Phase Is About

This is the brain of AfriProp. Every other service is plumbing — this phase is what
makes the platform intelligent. Three machine learning models are built, trained,
evaluated, and served as REST endpoints that any service in the platform can call.

When a landlord creates a listing, the valuation model tells them if their price is
right. When a tenant browses, the recommendation engine surfaces properties they are
likely to contact. When a listing is submitted, the fraud model scores it before it
goes live. When an investor opens their dashboard, the trend model shows where prices
are heading over the next 6 months.

All three models are trained on a carefully engineered synthetic dataset that mirrors
real African property market dynamics — log-normal price distributions, city-specific
pricing tiers, neighbourhood infrastructure scores, and injected fraud samples.

---

### The Three Models

#### Model 1 — Property Valuation (XGBoost Regressor)

**What it does:**
Takes a set of property features and returns an estimated market value with a
confidence interval. Powers the "AI Estimated Value" badge on every listing page.

**Input features:**
```
bedrooms, bathrooms, floor_area_sqm, property_type,
city, neighbourhood, latitude, longitude,
distance_to_cbd_km, distance_to_school_km,
distance_to_hospital_km, transit_access_score,
infrastructure_score, amenity_count,
furnishing, listing_month, currency
```

**Output:**
```json
{
  "estimated_value": 2500000,
  "confidence_low": 2100000,
  "confidence_high": 2900000,
  "currency": "KES",
  "price_per_sqm": 33333,
  "model_version": "valuation_v1"
}
```

**Algorithm:** XGBoost Regressor (primary) vs Random Forest (baseline comparison)

**Evaluation metrics:** RMSE, MAE, R², MAPE

**Target R² score:** > 0.80 on held-out test set

**Why XGBoost:** Handles mixed feature types (numeric + categorical), robust to
outliers in price data, fast inference for real-time API calls, and produces
feature importance scores we can show in the dashboard.

---

#### Model 2 — Price Trend Forecasting (Facebook Prophet)

**What it does:**
Takes a city + neighbourhood combination and forecasts median property prices
over the next 6 months. Powers the price trend chart on the neighbourhood
insight page and the investor dashboard.

**Input:**
```json
{
  "city": "Nairobi",
  "neighbourhood": "Westlands",
  "forecast_months": 6
}
```

**Output:**
```json
{
  "neighbourhood": "Westlands",
  "current_median_price": 45000,
  "forecast": [
    {"month": "2026-05", "predicted": 46200, "lower": 43000, "upper": 49400},
    {"month": "2026-06", "predicted": 47100, "lower": 43800, "upper": 50400},
    {"month": "2026-07", "predicted": 48300, "lower": 44500, "upper": 52100},
    {"month": "2026-08", "predicted": 49000, "lower": 45000, "upper": 53000},
    {"month": "2026-09", "predicted": 49800, "lower": 45200, "upper": 54400},
    {"month": "2026-10", "predicted": 50500, "lower": 45500, "upper": 55500}
  ],
  "trend": "rising",
  "trend_pct": 8.2,
  "model_version": "trend_v1"
}
```

**Algorithm:** Facebook Prophet with monthly seasonality and custom regressors

**Additional regressors:** Inflation rate index, population growth index,
infrastructure development score per neighbourhood

**Why Prophet:** Handles missing data gracefully, captures seasonality automatically
(rental demand peaks in January and September in East Africa), produces interpretable
uncertainty intervals, and requires minimal hyperparameter tuning.

---

#### Model 3 — Fraud & Anomaly Detection (Isolation Forest)

**What it does:**
Scores every new listing for suspicious signals before it goes live. Returns a
fraud score between 0 and 1, and a list of specific flags explaining why.
Listings scoring above 0.7 are held for manual admin review automatically.

**Input:**
```json
{
  "price": 5000,
  "city": "Nairobi",
  "neighbourhood": "Westlands",
  "bedrooms": 3,
  "floor_area_sqm": 120,
  "landlord_account_age_days": 2,
  "has_title_deed": false,
  "description_similarity_score": 0.91,
  "image_phash_duplicate": true,
  "phone_listing_count": 7
}
```

**Output:**
```json
{
  "fraud_score": 0.87,
  "risk_level": "high",
  "flags": [
    "price_anomaly",
    "duplicate_image",
    "new_account",
    "duplicate_description"
  ],
  "recommendation": "hold_for_review",
  "model_version": "fraud_v1"
}
```

**Algorithm:** Isolation Forest (primary) + rule-based scoring layer on top

**Fraud signals detected:**
- Price more than 2 standard deviations below neighbourhood median
- Image pHash duplicate detected against existing listings
- Description cosine similarity > 0.85 against existing listing
- Landlord account age < 7 days
- More than 5 active listings from same phone number
- Title deed not uploaded for properties above KES 20,000/month
- Listing coordinates mismatch with stated city/neighbourhood

**Why Isolation Forest:** Unsupervised — works without labelled fraud data,
which is scarce in African markets. Efficient on high-dimensional feature
vectors. Combined with the rule-based layer, gives both statistical and
logical fraud detection.

---

### Step-by-Step Process

#### Step 1 — Synthetic Dataset Generation

**Script:** `ml/scripts/generate_synthetic_data.py`

**What it does:**
Generates 50,000 realistic property records using statistical distributions
that mirror real African property market dynamics.

**Cities and pricing tiers:**
```
Nairobi    — KES  15,000 – 500,000/month (rental), KES 2M – 50M (sale)
Mombasa    — KES  10,000 – 200,000/month
Kampala    — UGX 300,000 – 8,000,000/month
Lagos      — NGN  80,000 – 2,000,000/month
Accra      — GHS  500 – 15,000/month
Dar es Salaam — TZS 200,000 – 5,000,000/month
```

**Price distribution:** Log-normal per city × property type × neighbourhood tier.
Log-normal is used because property prices are always positive and naturally
right-skewed — a few very expensive properties, many mid-range ones.

**Neighbourhood tiers per city:**
```
Tier 1 (premium)  — Westlands, Karen, Runda, Lekki, East Legon
Tier 2 (mid)      — Kilimani, Ngong Road, Yaba, Tema
Tier 3 (budget)   — Eastlands, Mukuru, Surulere, Adenta
```

**Feature generation:**
- Bedroom count: weighted random (bedsitter 15%, 1BR 25%, 2BR 35%, 3BR 20%, 4BR+ 5%)
- Geo-coordinates: sampled within real city bounding boxes with neighbourhood-level offset
- Distance to CBD: calculated from coordinates using Haversine
- Infrastructure score: 0–10, tier-based with random noise
- Transit access score: 0–10, correlated with distance to CBD
- Amenity count: correlated with price tier
- Listing month: uniform across 24 months for seasonality training

**Fraud sample injection (5% of dataset = 2,500 records):**
- Price set to 40–60% below neighbourhood median
- Description copied from another record with minor word substitution
- Account age set to 1–5 days
- Coordinates slightly mismatched from stated neighbourhood

**Output files:**
```
ml/data/synthetic/properties_raw.csv        — 50,000 records
ml/data/synthetic/fraud_samples.csv         — 2,500 fraud records flagged
ml/data/synthetic/neighbourhood_medians.csv — median price per neighbourhood
ml/data/synthetic/price_history.csv         — 24-month price history per neighbourhood
```

---

#### Step 2 — Data Exploration

**Notebook:** `ml/notebooks/01_data_exploration.ipynb`

**What we examine:**
- Price distribution per city (histogram + box plot)
- Correlation matrix of all numeric features
- Missing value analysis
- Outlier detection (IQR method on price)
- Neighbourhood price rankings
- Seasonal patterns in listing counts and prices
- Class balance check for fraud labels

**Expected outputs:**
- Price distributions are log-normal ✓
- Bedrooms and floor area are positively correlated with price ✓
- Infrastructure score has moderate positive correlation with price ✓
- Fraud samples cluster in low-price, high-similarity, new-account space ✓

---

#### Step 3 — Feature Engineering

**Notebook:** `ml/notebooks/02_feature_engineering.ipynb`

**Transformations applied:**
- Log-transform price (target variable) — normalises the right skew
- One-hot encode: city, property_type, furnishing
- Label encode: neighbourhood (too many categories for OHE)
- Scale: floor_area_sqm, distance_to_cbd_km, infrastructure_score (StandardScaler)
- Create: price_per_sqm, bedroom_bathroom_ratio, amenity_density_score
- Bin: listing_month into season (Jan-Mar=Q1, Apr-Jun=Q2, Jul-Sep=Q3, Oct-Dec=Q4)

**Train/validation/test split:**
```
Train:      70% — 35,000 records
Validation: 15% — 7,500 records
Test:       15% — 7,500 records
```
Split is stratified by city to ensure all cities are represented in every split.

**Saved artifacts:**
```
ml/data/processed/X_train.csv
ml/data/processed/X_val.csv
ml/data/processed/X_test.csv
ml/data/processed/y_train.csv
ml/data/processed/y_val.csv
ml/data/processed/y_test.csv
ml/data/processed/feature_names.json
ml/data/processed/scaler.pkl
ml/data/processed/label_encoders.pkl
```

---

#### Step 4 — Train Valuation Model

**Notebook:** `ml/notebooks/03_valuation_model.ipynb`

**Training process:**
1. Load processed features from Step 3
2. Train baseline: Linear Regression — sets the floor to beat
3. Train Random Forest — intermediate complexity benchmark
4. Train XGBoost with default params
5. Hyperparameter tune XGBoost with RandomizedSearchCV:
   ```
   n_estimators: [100, 300, 500]
   max_depth: [4, 6, 8]
   learning_rate: [0.01, 0.05, 0.1]
   subsample: [0.7, 0.8, 1.0]
   colsample_bytree: [0.7, 0.8, 1.0]
   ```
6. Evaluate best model on held-out test set
7. Generate confidence interval using quantile regression wrapper
8. Plot feature importance — shows which features drive valuation most
9. Plot predicted vs actual prices (scatter plot)
10. Save model

**Expected results:**
```
Linear Regression:  R² ~ 0.65
Random Forest:      R² ~ 0.78
XGBoost (tuned):    R² ~ 0.85
```

**Saved artifacts:**
```
services/ml/app/models/valuation_v1.pkl
ml/reports/valuation_feature_importance.png
ml/reports/valuation_predicted_vs_actual.png
ml/reports/valuation_metrics.json
```

---

#### Step 5 — Train Fraud Detection Model

**Notebook:** `ml/notebooks/04_fraud_detection.ipynb`

**Training process:**
1. Load dataset with fraud labels (0=clean, 1=fraud)
2. Engineer fraud-specific features:
   - `price_deviation_score` — how many std devs below neighbourhood median
   - `description_similarity_max` — highest cosine similarity to any other listing
   - `account_age_days` — landlord account age
   - `listing_density` — listings per phone number
   - `coord_neighbourhood_mismatch` — binary flag
3. Train Isolation Forest on clean listings only (unsupervised)
4. Score all listings — fraud samples should score high
5. Tune contamination parameter (expected % of outliers = 0.05)
6. Add rule-based layer on top of Isolation Forest score
7. Evaluate: precision, recall, F1, confusion matrix, ROC-AUC
8. Plot: anomaly score distribution for clean vs fraud samples

**Expected results:**
```
Precision:  > 0.82
Recall:     > 0.78
F1:         > 0.80
ROC-AUC:    > 0.88
```

**Saved artifacts:**
```
services/ml/app/models/fraud_v1.pkl
ml/reports/fraud_confusion_matrix.png
ml/reports/fraud_roc_curve.png
ml/reports/fraud_score_distribution.png
ml/reports/fraud_metrics.json
```

---

#### Step 6 — Train Price Trend Model

**Notebook:** `ml/notebooks/05_price_trends.ipynb`

**Training process:**
1. Load 24-month price history per neighbourhood from synthetic dataset
2. Aggregate: median price per neighbourhood per month
3. For each neighbourhood, fit a Prophet model:
   - Weekly seasonality: disabled (monthly data)
   - Yearly seasonality: enabled
   - Custom seasonality: East African rental peaks (Jan, Sep)
   - Regressors: inflation_index, infrastructure_score
4. Generate 6-month forecast with uncertainty intervals
5. Evaluate on held-out last 3 months (backtesting)
6. Calculate trend direction and percentage change
7. Save one model per neighbourhood

**Evaluation metrics:** MAE, RMSE on backtested months, coverage of uncertainty interval

**Saved artifacts:**
```
services/ml/app/models/trend_models/    — one .pkl per neighbourhood
ml/reports/trend_westlands.png
ml/reports/trend_karen.png
ml/reports/trend_metrics.json
```

---

#### Step 7 — Model Serialisation

**Script:** `ml/scripts/export_models.py`

All models saved using `joblib` with version suffix:
```
services/ml/app/models/valuation_v1.pkl     — XGBoost pipeline
services/ml/app/models/fraud_v1.pkl         — Isolation Forest + rules
services/ml/app/models/scaler_v1.pkl        — StandardScaler for inference
services/ml/app/models/encoders_v1.pkl      — Label encoders for inference
services/ml/app/models/trend_models/        — Prophet models per neighbourhood
services/ml/app/models/neighbourhood_medians.json — for fraud price deviation calc
```

---

#### Step 8 — ML FastAPI Service

**Service:** `services/ml/` running on port **8004**

**Startup:** Loads all model files into memory once at startup.
All prediction endpoints are synchronous (model inference is CPU-bound,
not I/O-bound) wrapped in FastAPI's thread pool executor.

**Endpoints:**

```
POST  /api/v1/ml/valuation       — predict property market value
POST  /api/v1/ml/fraud           — score listing for fraud signals
POST  /api/v1/ml/trends          — forecast neighbourhood price trend
GET   /api/v1/ml/models/status   — show all loaded models + versions
GET   /health                    — service alive check
```

**Internal structure:**
```
services/ml/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/                  ← serialised .pkl files live here
│   ├── routers/
│   │   ├── valuation.py
│   │   ├── fraud.py
│   │   ├── trends.py
│   │   └── status.py
│   └── services/
│       ├── model_loader.py      ← loads all models at startup
│       ├── valuation_service.py ← inference logic for valuation
│       ├── fraud_service.py     ← inference logic for fraud
│       └── trend_service.py     ← inference logic for trends
├── Dockerfile
└── requirements.txt
```

---

#### Step 9 — Integration with Property Service

Once the ML service is running, the property service calls it automatically:

- On `POST /api/v1/properties/` — calls `/ml/valuation` and `/ml/fraud`,
  stores estimated value and fraud score on the listing
- On `GET /api/v1/properties/{id}` — returns `ai_estimated_value` in the response
- Fraud score above 0.7 — automatically sets `needs_review: true`

---

#### Step 10 — Model Accuracy Report

**Script:** `ml/scripts/evaluate_models.py`

Generates `ml/reports/model_accuracy_report.html` — a single HTML page with:
- Valuation model: R², RMSE, MAE, predicted vs actual scatter plot,
  feature importance bar chart
- Fraud model: precision, recall, F1, confusion matrix heatmap, ROC curve,
  anomaly score distribution
- Trend model: backtesting MAE per neighbourhood, sample forecast charts

This report is what you show judges to prove the AI is real and working.

---

### Dependencies for This Phase

```
xgboost==2.1.1
scikit-learn==1.5.2
prophet==1.1.5
pandas==2.2.3
numpy==1.26.4
matplotlib==3.9.2
seaborn==0.13.2
joblib==1.4.2
jupyter==1.1.1
ipykernel==6.29.5
plotly==5.24.1
```

---

### What Judges Will See From This Phase

- Live API call: submit property features → get AI valuation with confidence range
- Live API call: submit suspicious listing → get fraud score 0.87 with flags listed
- Live API call: request Westlands trend → get 6-month forecast chart data
- Jupyter notebooks showing full training process with evaluation metrics
- HTML accuracy report proving model performance
- Feature importance chart showing the model learned real signals
  (floor area and neighbourhood matter more than listing month — as expected)
- Confusion matrix showing fraud model catches 80%+ of injected fraud samples

---

### Key Technical Decisions

**Synthetic data over scraped data** — scraping African property sites is unreliable,
rate-limited, and produces inconsistent formats. A well-engineered synthetic dataset
with realistic distributions is more reproducible, fully documented, and avoids legal
and ethical concerns. It also lets us control class balance for fraud detection.

**XGBoost over neural networks** — property valuation is a tabular regression problem.
XGBoost consistently outperforms neural networks on tabular data with fewer than
500,000 rows. It also trains in seconds, not hours, produces interpretable feature
importance, and requires no GPU.

**Prophet over LSTM for trends** — LSTM requires large sequential datasets per
neighbourhood to generalise well. Prophet handles short time series (24 months)
gracefully, incorporates domain knowledge via custom seasonality, and produces
calibrated uncertainty intervals out of the box.

**Isolation Forest for fraud** — we have no labelled fraud data from real African
property markets. Isolation Forest is unsupervised — it learns what normal looks like
and flags deviations. The rule-based layer on top adds interpretability, giving specific
flag names rather than just a score.

**joblib over pickle** — joblib is faster and more memory-efficient for large numpy
arrays inside sklearn and XGBoost models. It also handles multiprocessing better
when the API serves concurrent requests.




### ✅ Phase 3 — Completed

#### What Was Achieved

Phase 3 is the intelligence layer of AfriProp. Three machine learning models were
built from scratch — data generation, exploration, feature engineering, training,
evaluation, and deployment as live REST endpoints. Every model runs in production
inside a dedicated FastAPI service on port 8004 and loads into memory at startup
for fast inference.

---

#### Dataset

50,000 synthetic property records were generated across 6 African cities — Nairobi,
Mombasa, Kampala, Lagos, Accra, and Dar es Salaam — covering 42 neighbourhoods with
realistic log-normal price distributions, tier-based neighbourhood scoring, and
geo-coordinates within real city bounding boxes. 2,500 fraud samples (5%) were
injected with known anomaly signals: prices 40-60% below market, new accounts,
high listing density, and mismatched coordinates.

A separate 24-month price history dataset (1,008 rows) was generated for the trend
model — one monthly median price per neighbourhood per month with realistic upward
trends (0.3-0.8% monthly) and East African seasonal peaks in January and September.

---

#### Model 1 — Property Valuation (XGBoost)

Predicts the estimated market value of a property given its features. Powers the
"AI Estimated Value" badge on every listing page and the mortgage affordability
calculator. The model was trained without `log_price_per_sqm` to prevent data
leakage — a landlord asking for a valuation does not already know the price.

Four models were compared: Linear Regression, Ridge Regression, Random Forest, and
XGBoost. XGBoost won on every metric. The target variable is log-transformed price,
normalised within city and price period groups to handle six different currencies.
Features are scaled with StandardScaler fitted on training data only.

Key finding: `price_period_once` (sale vs rental) is the strongest predictor at
feature importance 0.83, followed by `city_enc` at 0.07. This makes intuitive sense
— a sale property is always 50-200x more expensive than a monthly rental for the
same unit.

```
Algorithm:   XGBoost Regressor
Features:    26 (no data leakage)
Test R²:     0.9960
Test MAPE:   15.63%
Confidence:  95% interval via residual std = 0.1725
```

---

#### Model 2 — Fraud Detection (Isolation Forest + Rules)

Scores every new listing before it goes live. Returns a fraud score 0-1, a risk
level, a list of named flags, and a recommendation (approve / flag_for_check /
hold_for_review). Listings scoring above 0.55 are automatically held for admin
review.

The model is a hybrid of two approaches. Isolation Forest is trained only on clean
listings — it learns what normal looks like and flags deviations. The rule-based
layer adds interpretability — named flags like `price_anomaly`, `new_account`,
and `below_market_60pct` give admins specific reasons to act on. The combined score
weights Isolation Forest at 55% and rules at 45%.

This approach was chosen because no labelled fraud data exists for African property
markets. Isolation Forest is unsupervised — it needs only clean examples to learn
the normal distribution of listings.

```
Algorithm:   Isolation Forest (unsupervised) + rule-based scoring
Features:    14 fraud-specific features
ROC-AUC:     0.9914
Fraud F1:    0.76
Precision:   0.69 (31% false positives go to manual review — intentional)
Recall:      0.84 (catches 84% of injected fraud samples)
Threshold:   0.55
```

---

#### Model 3 — Price Trend Forecasting (Linear Trend + Seasonal Decomposition)

Forecasts median property prices 6 months ahead for any of the 42 neighbourhoods.
Powers the price trend chart on the neighbourhood insight page and the investor
dashboard ROI projections.

Prophet was initially used but produced catastrophic forecasts (MAPE 449%) because
24 monthly data points are insufficient for Prophet to learn yearly seasonality
without overfitting. Linear regression on log-transformed price with calendar-month
seasonal factors proved far more appropriate and stable for this data quantity —
reducing MAPE from 449% to 1.63%.

One model is trained and saved per neighbourhood — 42 `.pkl` files total. Each file
contains the fitted slope, intercept, R², and seasonal adjustment factors per
calendar month. The FastAPI service loads all 42 into memory at startup.

```
Algorithm:   Linear trend + seasonal decomposition (one model per neighbourhood)
Models:      42 (one per neighbourhood)
Backtest MAPE: 1.63% (3-month hold-out)
Average R²:  0.6490
Rising neighbourhoods:  42 / 42 (synthetic data generated with positive trend)
```

---

#### ML Service

All three models are served by a single FastAPI service on port 8004. Models load
into memory at startup — zero cold start per request. The service is completely
independent of the other services and can be scaled separately.

```
Port:        8004
Startup:     loads all models into memory once
Endpoints:   4 (valuation, fraud, trends, recommend)
Model files: valuation_v1.pkl, fraud_v1.pkl, 42x trend .pkl files
```

---

#### Key Technical Decisions

Prophet was replaced with linear trend decomposition after backtesting revealed
449% MAPE — model complexity must match data quantity. 24 data points is insufficient
for Prophet's yearly seasonality fitting.

The valuation model excludes `log_price_per_sqm` despite it being the strongest
predictor (correlation 0.97 with target). Including it would be data leakage — a
landlord requesting a valuation does not already know the price per sqm. The honest
model achieves R²=0.9960 without it.

All models were retrained inside the service venv using XGBoost 2.1.1 to avoid
version mismatch errors when loading pickled models. Always train and serve with
the same library versions.

---

#### Useful Commands

**Start the ML service:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/ml
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8004
```

**Check all models loaded:**
```bash
curl -s http://localhost:8004/health | python3 -m json.tool
curl -s http://localhost:8004/api/v1/ml/models/status | python3 -m json.tool
```

**Valuation — predict property market value:**
```bash
curl -s -X POST http://localhost:8004/api/v1/ml/valuation \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 3, "bathrooms": 2, "floor_area_sqm": 120.0,
    "property_type": "house", "furnishing": "furnished",
    "price_period": "monthly", "city": "Nairobi",
    "neighbourhood": "Westlands", "distance_to_cbd_km": 3.5,
    "infrastructure_score": 8.8, "transit_access_score": 8.5,
    "amenity_count": 6, "tier": 1, "listing_month": 9
  }' | python3 -m json.tool
```

**Fraud detection — score a suspicious listing:**
```bash
# Obvious fraud (score should be 1.0)
curl -s -X POST http://localhost:8004/api/v1/ml/fraud \
  -H "Content-Type: application/json" \
  -d '{
    "price": 5000, "city": "Nairobi", "neighbourhood": "Westlands",
    "nb_median_price": 75000, "account_age_days": 2,
    "listing_count": 12, "amenity_count": 0
  }' | python3 -m json.tool

# Clean listing (score should be 0.0)
curl -s -X POST http://localhost:8004/api/v1/ml/fraud \
  -H "Content-Type: application/json" \
  -d '{
    "price": 42000, "city": "Nairobi", "neighbourhood": "Westlands",
    "nb_median_price": 45000, "account_age_days": 180,
    "listing_count": 2, "amenity_count": 5
  }' | python3 -m json.tool
```

**Price trend — 6-month neighbourhood forecast:**
```bash
curl -s -X POST http://localhost:8004/api/v1/ml/trends \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Nairobi",
    "neighbourhood": "Westlands",
    "forecast_months": 6
  }' | python3 -m json.tool
```

**Run the data generation script (regenerates all synthetic data):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp
python3 ml/scripts/generate_synthetic_data.py
```

**Retrain valuation model in service venv (avoids version mismatch):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/ml
source venv/bin/activate
python3 ml/scripts/train_valuation.py
```

**Check model files:**
```bash
ls services/ml/app/models/
ls services/ml/app/models/trend_models/ | wc -l
```

**Swagger docs:** `http://localhost:8004/docs`
```