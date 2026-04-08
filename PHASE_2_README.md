## Phase 2 — Property Service: Full Outline

---

### What this service is

A standalone FastAPI service running on port **8001** that owns everything related to properties — creating them, searching them, storing their images, verifying them, and detecting fraud. Every other service (channels, ML, tenant, finance) will call this service to get property data.

---

### What we are building, piece by piece

**2.1 — Property Database Models**

Three tables in PostgreSQL:

`properties` table — the core listing:
```
id, landlord_id (FK to users), title, description,
property_type (apartment/house/land/commercial/bedsitter),
status (available/rented/sold/under_offer),
bedrooms, bathrooms, floor_area_sqm, furnishing,
price, price_period (monthly/yearly/once),
currency (KES/NGN/GHS/UGX/TZS),
address, city, neighbourhood, country,
latitude, longitude, location (PostGIS POINT),
is_verified, is_featured, view_count,
created_at, updated_at
```

`property_images` table — images per listing:
```
id, property_id (FK), url, is_primary,
file_size, width, height, phash (for duplicate detection),
uploaded_at
```

`property_amenities` table — what the property has:
```
id, property_id (FK), amenity (wifi/parking/pool/gym/
security/water/electricity/generator/borehole/
cctv/furnished/pet_friendly/balcony)
```

---

**2.2 — Property CRUD Endpoints**

```
POST   /api/v1/properties/              → create listing (landlord/agent only)
GET    /api/v1/properties/              → list all (paginated)
GET    /api/v1/properties/{id}          → get single listing + images + amenities
PUT    /api/v1/properties/{id}          → update listing (owner only)
DELETE /api/v1/properties/{id}          → soft delete (owner/admin only)
GET    /api/v1/properties/my/listings   → landlord's own listings
PATCH  /api/v1/properties/{id}/status   → change status (available/rented/sold)
```

---

**2.3 — Image Upload & Management**

```
POST   /api/v1/properties/{id}/images        → upload images (max 10)
DELETE /api/v1/properties/{id}/images/{img}  → delete single image
PATCH  /api/v1/properties/{id}/images/{img}/primary → set as primary image
```

Pipeline per upload:
- Validate file type (JPEG, PNG, WEBP only)
- Validate file size (max 5MB per image)
- Compress with Pillow (max 1200px width, 85% quality)
- Generate perceptual hash (pHash) for duplicate detection
- Upload to MinIO bucket
- Store URL + metadata in `property_images` table
- If it's the first image, auto-set as primary

---

**2.4 — Property Search & Filtering**

```
GET /api/v1/properties/search?city=Nairobi&type=apartment&bedrooms=2&min_price=10000&max_price=50000&amenities=wifi,parking&verified=true&sort=price_asc&page=1&limit=20
```

Filter parameters:
- `city`, `neighbourhood`, `country`
- `property_type`
- `bedrooms`, `bathrooms` (min/max)
- `min_price`, `max_price`, `currency`
- `amenities` (comma-separated list)
- `verified` (boolean)
- `furnished` (boolean)

Sort options:
- `price_asc`, `price_desc`
- `newest`, `oldest`
- `most_viewed`

Pagination: `page` + `limit` with total count in response

Full-text search:
```
GET /api/v1/properties/search?q=modern+apartment+westlands
```
Uses PostgreSQL `tsvector` on title + description + neighbourhood.

---

**2.5 — Geo Search (PostGIS)**

```
GET /api/v1/properties/nearby?lat=-1.2921&lng=36.8219&radius_km=5
```

- Takes a coordinate and radius
- Returns all available properties within that radius
- Results sorted by distance (nearest first)
- Distance in km included in each result
- Used by the mobile app's "near me" feature and USSD location search

---

**2.6 — Property Verification**

```
POST  /api/v1/properties/{id}/verify          → admin marks as verified
POST  /api/v1/properties/{id}/submit-title    → landlord uploads title deed PDF
GET   /api/v1/properties/{id}/verification    → get verification status + notes
```

Verification states: `unverified` → `pending_review` → `verified` / `rejected`

What gets checked:
- Landlord identity (is their profile complete, phone verified)
- Title deed uploaded
- Admin manual review flag
- Verified badge applied to listing

---

**2.7 — Duplicate Detection**

Runs automatically on every new listing submission:

- **Image pHash check** — perceptual hash of uploaded images compared against all existing images. Similarity threshold: if hash distance < 10, flag as duplicate image.
- **Description similarity** — cosine similarity on listing description using TF-IDF. If similarity > 0.85 against existing listing, flag.
- **Same landlord + same address** — exact match check.
- **Result:** `fraud_flags` list attached to property. If any flag triggers, `needs_review` status set. Admin reviews before listing goes live.

---

**2.8 — Saved Searches & Alerts**

```
POST  /api/v1/search/save          → save a search with filters
GET   /api/v1/search/saved         → list user's saved searches
DELETE /api/v1/search/saved/{id}   → delete saved search
```

- When a new property is listed, the system checks all saved searches
- If the new property matches a saved search, it queues an SMS/push notification
- Matching runs as a background job via Redis Queue

---

**2.9 — Property Service Internal Setup**

Same pattern as gateway:
- Own `requirements.txt`
- Own `Dockerfile`
- Own `config.py` pointing to root `.env`
- Own `database.py` with async SQLAlchemy
- Alembic for migrations (not auto-create like gateway)
- Added to `docker-compose.yml` as a new service
- Gateway will proxy property requests to this service

---

### File structure we will create

```
services/property/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── property.py        ← Property, PropertyImage, PropertyAmenity
│   │   └── saved_search.py    ← SavedSearch
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── property.py        ← request/response shapes
│   │   └── search.py          ← search filter shapes
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── listings.py        ← CRUD endpoints
│   │   ├── search.py          ← search + geo endpoints
│   │   ├── images.py          ← upload/manage images
│   │   └── verification.py    ← verify listings
│   └── services/
│       ├── __init__.py
│       ├── property_service.py  ← business logic
│       ├── image_service.py     ← Pillow + MinIO + pHash
│       ├── search_service.py    ← filter + full-text + geo queries
│       └── duplicate_service.py ← fraud detection logic
├── tests/
├── Dockerfile
└── requirements.txt
```

---

### Dependencies we will install

```
fastapi, uvicorn, sqlalchemy, asyncpg, alembic,
pydantic, pydantic-settings,
pillow (image processing),
imagehash (perceptual hashing),
scikit-learn (TF-IDF for description similarity),
minio (object storage client),
python-multipart (file uploads),
geoalchemy2 (PostGIS integration),
python-jose, passlib (JWT validation from gateway),
redis, rq (background jobs)
```

---

### What to expect from this phase

- A landlord registers, logs in, creates a property listing with images
- A tenant searches by city + bedrooms + price range and gets paginated results
- The mobile app calls `/nearby` with GPS coords and gets properties on a map
- A USSD user's search query hits the same search endpoint
- Duplicate listings are automatically flagged before going live
- Verified badge appears on clean listings



```markdown
### ✅ Phase 2 — Completed

#### What Was Achieved

The property service is a fully independent FastAPI microservice running on port 8001
with its own database connection, models, and business logic. It handles everything
property-related so the gateway stays lean and each service owns its domain.

Three PostgreSQL tables were created automatically on startup:
- `properties` — the core listing: type, price, location, status, fraud flags
- `property_images` — compressed images with dimensions and perceptual hash per listing
- `property_amenities` — amenities linked to each property (wifi, parking, pool, etc.)

Fraud detection runs on every new listing before it goes live. Two signals are checked:
duplicate images using perceptual hashing (pHash, threshold distance < 10) and duplicate
descriptions using TF-IDF cosine similarity (threshold > 0.85). If either triggers,
the listing is flagged with `needs_review: true` and held for admin review.

Images are compressed to max 1200px width at 85% JPEG quality using Pillow before being
stored in MinIO. The bucket is set to public so image URLs work directly in the browser
and mobile app without authentication.

Geo search uses the Haversine formula to calculate straight-line distance between two
coordinates. A tenant's GPS location from the mobile app hits `/nearby` with a radius
and gets back properties sorted nearest first — no PostGIS query needed.

Soft delete is used throughout — properties are never hard deleted from the database.
`is_active=False` preserves the audit trail and prevents broken references from leases
and payment records that will be built in later phases.

---

#### Useful Commands

**Start the property service:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/property
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Create a listing:**
```bash
curl -s -X POST http://localhost:8001/api/v1/properties/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Modern 2BR Apartment in Westlands",
    "description": "Spacious apartment with great natural light and secure parking.",
    "property_type": "apartment",
    "bedrooms": 2, "bathrooms": 1, "floor_area_sqm": 75.0,
    "furnishing": "semi_furnished", "price": 45000,
    "price_period": "monthly", "currency": "KES",
    "city": "Nairobi", "neighbourhood": "Westlands", "country": "Kenya",
    "latitude": -1.2676, "longitude": 36.8114,
    "amenities": ["wifi", "parking", "security"]
  }' | python3 -m json.tool
```

**Search by city and bedrooms:**
```bash
curl -s "http://localhost:8001/api/v1/properties/?city=Nairobi&min_bedrooms=2" \
  | python3 -m json.tool
```

**Search by price range:**
```bash
curl -s "http://localhost:8001/api/v1/properties/?min_price=20000&max_price=60000&sort=price_asc" \
  | python3 -m json.tool
```

**Full text search:**
```bash
curl -s "http://localhost:8001/api/v1/properties/?q=westlands+apartment" \
  | python3 -m json.tool
```

**Nearby geo search (replace lat/lng with real GPS coords):**
```bash
curl -s "http://localhost:8001/api/v1/properties/nearby?lat=-1.2676&lng=36.8114&radius_km=5" \
  | python3 -m json.tool
```

**Upload an image to a listing:**
```bash
curl -s -X POST "http://localhost:8001/api/v1/properties/{PROPERTY_ID}/images" \
  -F "file=@your_image.jpg" | python3 -m json.tool
```

**Change listing status:**
```bash
curl -s -X PATCH "http://localhost:8001/api/v1/properties/{PROPERTY_ID}/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "rented"}' | python3 -m json.tool
```

**Check listings in the database:**
```bash
docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT id, title, city, price, needs_review FROM properties;"
```

**Check uploaded images in MinIO:**
```bash
docker exec afriprop_minio mc ls local/afriprop-media
```

**Restore MinIO public access if reset:**
```bash
docker exec afriprop_minio mc alias set local http://localhost:9000 afriprop changeme123
docker exec afriprop_minio mc anonymous set public local/afriprop-media
```

**Swagger docs:** `http://localhost:8001/docs`
```