import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
warnings.filterwarnings("ignore")

np.random.seed(42)

OUTPUT_DIR = Path("ml/data/synthetic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── CITY CONFIGURATIONS ────────────────────────────────────────────────────────
CITIES = {
    "Nairobi": {
        "currency": "KES",
        "country": "Kenya",
        "bounds": {"lat": (-1.40, -1.15), "lng": (36.70, 37.05)},
        "cbd": (-1.2841, 36.8155),
        "neighbourhoods": {
            "Karen":       {"tier": 1, "infra": 9.2, "transit": 6.5},
            "Runda":       {"tier": 1, "infra": 9.5, "transit": 5.8},
            "Westlands":   {"tier": 1, "infra": 8.8, "transit": 8.5},
            "Kilimani":    {"tier": 2, "infra": 8.2, "transit": 8.0},
            "Lavington":   {"tier": 2, "infra": 8.5, "transit": 7.2},
            "Ngong Road":  {"tier": 2, "infra": 7.5, "transit": 7.8},
            "Kasarani":    {"tier": 3, "infra": 6.2, "transit": 7.5},
            "Eastleigh":   {"tier": 3, "infra": 5.8, "transit": 8.2},
            "Mukuru":      {"tier": 3, "infra": 4.5, "transit": 6.8},
            "Githurai":    {"tier": 3, "infra": 5.2, "transit": 7.0},
        },
        "price_base": {
            "apartment": {"monthly": 35000, "sale": 8000000},
            "house":     {"monthly": 65000, "sale": 15000000},
            "land":      {"monthly": None,  "sale": 5000000},
            "commercial":{"monthly": 80000, "sale": 20000000},
            "bedsitter": {"monthly": 12000, "sale": 2000000},
        }
    },
    "Mombasa": {
        "currency": "KES",
        "country": "Kenya",
        "bounds": {"lat": (-4.10, -3.95), "lng": (39.55, 39.75)},
        "cbd": (-4.0435, 39.6682),
        "neighbourhoods": {
            "Nyali":       {"tier": 1, "infra": 8.5, "transit": 6.0},
            "Shanzu":      {"tier": 1, "infra": 8.0, "transit": 5.5},
            "Bamburi":     {"tier": 2, "infra": 7.2, "transit": 6.8},
            "Mtwapa":      {"tier": 2, "infra": 6.8, "transit": 6.5},
            "Likoni":      {"tier": 3, "infra": 5.5, "transit": 7.0},
            "Kisauni":     {"tier": 3, "infra": 5.2, "transit": 6.2},
        },
        "price_base": {
            "apartment": {"monthly": 22000, "sale": 5000000},
            "house":     {"monthly": 40000, "sale": 9000000},
            "land":      {"monthly": None,  "sale": 3000000},
            "commercial":{"monthly": 50000, "sale": 12000000},
            "bedsitter": {"monthly": 8000,  "sale": 1200000},
        }
    },
    "Kampala": {
        "currency": "UGX",
        "country": "Uganda",
        "bounds": {"lat": (0.20, 0.45), "lng": (32.50, 32.75)},
        "cbd": (0.3163, 32.5822),
        "neighbourhoods": {
            "Kololo":      {"tier": 1, "infra": 9.0, "transit": 6.5},
            "Nakasero":    {"tier": 1, "infra": 8.8, "transit": 7.0},
            "Ntinda":      {"tier": 2, "infra": 7.5, "transit": 7.5},
            "Bukoto":      {"tier": 2, "infra": 7.8, "transit": 7.2},
            "Kireka":      {"tier": 3, "infra": 5.5, "transit": 6.8},
            "Naalya":      {"tier": 3, "infra": 6.0, "transit": 6.5},
        },
        "price_base": {
            "apartment": {"monthly": 1200000,  "sale": 250000000},
            "house":     {"monthly": 2500000,  "sale": 500000000},
            "land":      {"monthly": None,     "sale": 200000000},
            "commercial":{"monthly": 3000000,  "sale": 700000000},
            "bedsitter": {"monthly": 500000,   "sale": 80000000},
        }
    },
    "Lagos": {
        "currency": "NGN",
        "country": "Nigeria",
        "bounds": {"lat": (6.35, 6.70), "lng": (3.15, 3.55)},
        "cbd": (6.4550, 3.3841),
        "neighbourhoods": {
            "Lekki":       {"tier": 1, "infra": 8.5, "transit": 6.0},
            "Victoria Island":{"tier": 1, "infra": 9.2, "transit": 7.5},
            "Ikoyi":       {"tier": 1, "infra": 9.0, "transit": 7.0},
            "Yaba":        {"tier": 2, "infra": 7.2, "transit": 8.5},
            "Surulere":    {"tier": 2, "infra": 7.0, "transit": 8.0},
            "Ikeja":       {"tier": 2, "infra": 7.5, "transit": 8.2},
            "Mushin":      {"tier": 3, "infra": 5.0, "transit": 7.8},
            "Agege":       {"tier": 3, "infra": 4.8, "transit": 7.5},
        },
        "price_base": {
            "apartment": {"monthly": 150000,   "sale": 35000000},
            "house":     {"monthly": 300000,   "sale": 70000000},
            "land":      {"monthly": None,     "sale": 25000000},
            "commercial":{"monthly": 400000,   "sale": 90000000},
            "bedsitter": {"monthly": 60000,    "sale": 10000000},
        }
    },
    "Accra": {
        "currency": "GHS",
        "country": "Ghana",
        "bounds": {"lat": (5.50, 5.75), "lng": (-0.30, 0.00)},
        "cbd": (5.5502, -0.2174),
        "neighbourhoods": {
            "East Legon":  {"tier": 1, "infra": 8.8, "transit": 6.5},
            "Cantonments": {"tier": 1, "infra": 9.0, "transit": 7.0},
            "Airport Hills":{"tier": 2, "infra": 8.0, "transit": 7.5},
            "Tema":        {"tier": 2, "infra": 7.5, "transit": 7.0},
            "Adenta":      {"tier": 3, "infra": 6.0, "transit": 6.8},
            "Ashaiman":    {"tier": 3, "infra": 5.2, "transit": 6.5},
        },
        "price_base": {
            "apartment": {"monthly": 3000,  "sale": 600000},
            "house":     {"monthly": 6000,  "sale": 1200000},
            "land":      {"monthly": None,  "sale": 400000},
            "commercial":{"monthly": 8000,  "sale": 1800000},
            "bedsitter": {"monthly": 1200,  "sale": 180000},
        }
    },
    "Dar es Salaam": {
        "currency": "TZS",
        "country": "Tanzania",
        "bounds": {"lat": (-7.00, -6.65), "lng": (39.15, 39.45)},
        "cbd": (-6.7924, 39.2083),
        "neighbourhoods": {
            "Msasani":     {"tier": 1, "infra": 8.5, "transit": 6.0},
            "Oyster Bay":  {"tier": 1, "infra": 9.0, "transit": 5.8},
            "Kinondoni":   {"tier": 2, "infra": 7.2, "transit": 7.5},
            "Mikocheni":   {"tier": 2, "infra": 7.5, "transit": 7.2},
            "Mbagala":     {"tier": 3, "infra": 5.5, "transit": 6.5},
            "Temeke":      {"tier": 3, "infra": 5.2, "transit": 6.8},
        },
        "price_base": {
            "apartment": {"monthly": 800000,   "sale": 150000000},
            "house":     {"monthly": 1500000,  "sale": 300000000},
            "land":      {"monthly": None,     "sale": 100000000},
            "commercial":{"monthly": 2000000,  "sale": 400000000},
            "bedsitter": {"monthly": 350000,   "sale": 50000000},
        }
    },
}

PROPERTY_TYPES = ["apartment", "house", "land", "commercial", "bedsitter"]
TYPE_WEIGHTS   = [0.38, 0.28, 0.10, 0.08, 0.16]

FURNISHING_OPTIONS = ["furnished", "semi_furnished", "unfurnished"]
FURNISHING_WEIGHTS = [0.25, 0.35, 0.40]

PRICE_PERIODS = ["monthly", "yearly", "once"]

AMENITIES = ["wifi","parking","pool","gym","security","water",
             "electricity","generator","borehole","cctv","balcony","pet_friendly"]

BEDROOM_DIST = {
    "apartment": ([0,1,2,3,4], [0.05,0.20,0.40,0.28,0.07]),
    "house":     ([2,3,4,5,6], [0.10,0.35,0.35,0.15,0.05]),
    "land":      ([0],         [1.00]),
    "commercial":([0],         [1.00]),
    "bedsitter": ([0,1],       [0.70,0.30]),
}


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lng2 - lng1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def tier_multiplier(tier):
    return {1: 1.8, 2: 1.0, 3: 0.55}[tier]


def generate_price(city_cfg, prop_type, neighbourhood, bedrooms, floor_area, furnishing, period):
    base = city_cfg["price_base"][prop_type]
    nb   = city_cfg["neighbourhoods"][neighbourhood]
    tier = nb["tier"]
    tm   = tier_multiplier(tier)

    if period == "once" or prop_type == "land":
        price_base = base["sale"]
    else:
        price_base = base["monthly"]

    if price_base is None:
        price_base = base["sale"]

    bed_mult  = 1 + (bedrooms * 0.15)
    area_mult = 1 + ((floor_area - 60) / 200) if floor_area > 0 else 1
    furn_mult = {"furnished": 1.25, "semi_furnished": 1.10, "unfurnished": 1.0}[furnishing]
    infra_mult = 0.85 + (nb["infra"] / 10) * 0.30

    price = price_base * tm * bed_mult * area_mult * furn_mult * infra_mult
    price = np.random.lognormal(np.log(price), 0.18)
    return max(round(price, -2), 1000)


def generate_coordinates(city_cfg, neighbourhood):
    bounds = city_cfg["bounds"]
    cbd    = city_cfg["cbd"]
    nb     = city_cfg["neighbourhoods"][neighbourhood]
    tier   = nb["tier"]

    lat_range = bounds["lat"][1] - bounds["lat"][0]
    lng_range = bounds["lng"][1] - bounds["lng"][0]

    if tier == 1:
        lat = cbd[0] + np.random.uniform(-lat_range*0.25, lat_range*0.25)
        lng = cbd[1] + np.random.uniform(-lng_range*0.25, lng_range*0.25)
    elif tier == 2:
        lat = cbd[0] + np.random.uniform(-lat_range*0.40, lat_range*0.40)
        lng = cbd[1] + np.random.uniform(-lng_range*0.40, lng_range*0.40)
    else:
        lat = bounds["lat"][0] + np.random.uniform(0, lat_range)
        lng = bounds["lng"][0] + np.random.uniform(0, lng_range)

    lat = np.clip(lat, bounds["lat"][0], bounds["lat"][1])
    lng = np.clip(lng, bounds["lng"][0], bounds["lng"][1])
    return round(lat, 6), round(lng, 6)


def generate_amenity_count(tier, prop_type):
    base = {1: 5, 2: 3, 3: 1}[tier]
    if prop_type in ["land"]:
        return 0
    return min(12, max(0, int(np.random.poisson(base))))


print("Generating 50,000 property records...")
records = []
N = 50000

city_names = list(CITIES.keys())
city_weights = [0.30, 0.12, 0.12, 0.20, 0.13, 0.13]

for i in range(N):
    city_name = np.random.choice(city_names, p=city_weights)
    city_cfg  = CITIES[city_name]
    nb_names  = list(city_cfg["neighbourhoods"].keys())
    nb_name   = np.random.choice(nb_names)
    nb_cfg    = city_cfg["neighbourhoods"][nb_name]

    prop_type  = np.random.choice(PROPERTY_TYPES, p=TYPE_WEIGHTS)
    bed_opts, bed_wts = BEDROOM_DIST[prop_type]
    bedrooms   = np.random.choice(bed_opts, p=bed_wts)
    bathrooms  = max(1, int(np.random.poisson(max(1, bedrooms * 0.7))))
    floor_area = 0 if prop_type in ["land"] else round(
        np.random.lognormal(np.log(max(30, bedrooms * 35)), 0.3), 1
    )
    furnishing = np.random.choice(FURNISHING_OPTIONS, p=FURNISHING_WEIGHTS)
    if prop_type in ["land", "commercial"]:
        furnishing = "unfurnished"

    period_probs = [0.65, 0.15, 0.20] if prop_type != "land" else [0.0, 0.0, 1.0]
    price_period = np.random.choice(PRICE_PERIODS, p=period_probs)

    lat, lng = generate_coordinates(city_cfg, nb_name)
    cbd_lat, cbd_lng = city_cfg["cbd"]
    dist_cbd = round(haversine(lat, lng, cbd_lat, cbd_lng), 2)

    price = generate_price(city_cfg, prop_type, nb_name, bedrooms, floor_area, furnishing, price_period)

    infra_score   = round(nb_cfg["infra"] + np.random.uniform(-0.5, 0.5), 2)
    transit_score = round(nb_cfg["transit"] + np.random.uniform(-0.5, 0.5), 2)
    amenity_count = generate_amenity_count(nb_cfg["tier"], prop_type)

    listing_month = np.random.randint(1, 25)
    account_age   = int(np.random.exponential(180))
    listing_count = max(1, int(np.random.poisson(2)))

    records.append({
        "id":                    i,
        "city":                  city_name,
        "neighbourhood":         nb_name,
        "country":               city_cfg["country"],
        "currency":              city_cfg["currency"],
        "property_type":         prop_type,
        "bedrooms":              bedrooms,
        "bathrooms":             bathrooms,
        "floor_area_sqm":        floor_area,
        "furnishing":            furnishing,
        "price":                 price,
        "price_period":          price_period,
        "latitude":              lat,
        "longitude":             lng,
        "distance_to_cbd_km":    dist_cbd,
        "infrastructure_score":  np.clip(infra_score, 1, 10),
        "transit_access_score":  np.clip(transit_score, 1, 10),
        "amenity_count":         amenity_count,
        "listing_month":         listing_month,
        "account_age_days":      account_age,
        "listing_count":         listing_count,
        "tier":                  nb_cfg["tier"],
        "is_fraud":              0,
    })

df = pd.DataFrame(records)
print(f"Base dataset: {len(df):,} records")

# ── INJECT FRAUD SAMPLES ───────────────────────────────────────────────────────
print("Injecting fraud samples (5%)...")
fraud_indices = np.random.choice(df.index, size=2500, replace=False)

for idx in fraud_indices:
    city = df.loc[idx, "city"]
    nb   = df.loc[idx, "neighbourhood"]
    nb_median = df[
        (df["city"] == city) &
        (df["neighbourhood"] == nb) &
        (df["price_period"] == df.loc[idx, "price_period"])
    ]["price"].median()

    if pd.notna(nb_median):
        df.loc[idx, "price"] = round(nb_median * np.random.uniform(0.35, 0.55), -2)

    df.loc[idx, "account_age_days"] = np.random.randint(1, 6)
    df.loc[idx, "listing_count"]    = np.random.randint(6, 15)
    df.loc[idx, "is_fraud"]         = 1

print(f"Fraud samples: {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.1f}%)")

# ── SAVE MAIN DATASET ──────────────────────────────────────────────────────────
df.to_csv(OUTPUT_DIR / "properties_raw.csv", index=False)
print(f"Saved: properties_raw.csv")

# ── NEIGHBOURHOOD MEDIANS ──────────────────────────────────────────────────────
medians = df[df["is_fraud"] == 0].groupby(
    ["city", "neighbourhood", "property_type", "price_period"]
)["price"].median().reset_index()
medians.columns = ["city", "neighbourhood", "property_type", "price_period", "median_price"]
medians.to_csv(OUTPUT_DIR / "neighbourhood_medians.csv", index=False)

medians_dict = {}
for _, row in medians.iterrows():
    key = f"{row.city}|{row.neighbourhood}|{row.property_type}|{row.price_period}"
    medians_dict[key] = row.median_price
with open(OUTPUT_DIR / "neighbourhood_medians.json", "w") as f:
    json.dump(medians_dict, f, indent=2)
print(f"Saved: neighbourhood_medians.csv + .json")

# ── PRICE HISTORY (24 months per neighbourhood) ────────────────────────────────
print("Generating 24-month price history...")
history_records = []
months = pd.date_range("2024-01-01", periods=24, freq="MS")

for city_name, city_cfg in CITIES.items():
    for nb_name, nb_cfg in city_cfg["neighbourhoods"].items():
        base_price = city_cfg["price_base"]["apartment"]["monthly"]
        if base_price is None:
            continue
        tm = tier_multiplier(nb_cfg["tier"])
        base = base_price * tm

        trend     = np.random.uniform(0.003, 0.012)
        seasonal  = np.random.uniform(0.05, 0.15)
        noise_std = 0.04

        for m_idx, month in enumerate(months):
            is_peak = 1 if month.month in [1, 2, 9, 10] else 0
            price = base * (1 + trend * m_idx) * (1 + seasonal * is_peak)
            price = price * np.random.lognormal(0, noise_std)
            history_records.append({
                "city":          city_name,
                "neighbourhood": nb_name,
                "month":         month.strftime("%Y-%m"),
                "median_price":  round(price, -2),
                "currency":      city_cfg["currency"],
            })

history_df = pd.DataFrame(history_records)
history_df.to_csv(OUTPUT_DIR / "price_history.csv", index=False)
print(f"Saved: price_history.csv ({len(history_df):,} rows)")

# ── SUMMARY ────────────────────────────────────────────────────────────────────
print("\n── Dataset Summary ──────────────────────────────────────────")
print(f"Total records:     {len(df):,}")
print(f"Clean records:     {(df.is_fraud==0).sum():,}")
print(f"Fraud records:     {(df.is_fraud==1).sum():,}")
print(f"Cities:            {df.city.nunique()}")
print(f"Neighbourhoods:    {df.neighbourhood.nunique()}")
print(f"Property types:    {df.property_type.value_counts().to_dict()}")
print(f"Price history rows:{len(history_df):,}")
print("────────────────────────────────────────────────────────────")
print("Done.")
