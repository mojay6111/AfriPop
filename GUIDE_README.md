# AfriProp — Property Intelligence Platform
> A full-stack, multi-channel real estate technology platform built for the African market.
> Combining AI-driven property intelligence with SMS, USSD, Voice, and Web access channels
> to make property search, management, and investment accessible to every African — 
> with or without internet.

---

## Table of Contents
1. [Project Vision](#project-vision)
2. [Core Problem Statement](#core-problem-statement)
3. [Solution Overview](#solution-overview)
4. [Architecture Overview](#architecture-overview)
5. [Phase 1 — Foundation](#phase-1--foundation-setup--core-api)
6. [Phase 2 — Property Core](#phase-2--property-core)
7. [Phase 3 — AI & Data Science](#phase-3--ai--data-science-layer)
8. [Phase 4 — Africa's Talking Integration](#phase-4--africas-talking-integration)
9. [Phase 5 — Finance & Payments](#phase-5--finance--payments)
10. [Phase 6 — Web & Mobile Frontend](#phase-6--web--mobile-frontend)
11. [Phase 7 — CRM, Maintenance & Social Housing](#phase-7--crm-maintenance--social-housing)
12. [Phase 8 — CI/CD & Deployment](#phase-8--cicd--deployment)
13. [Dataset & Training Strategy](#dataset--training-strategy)
14. [Africa's Talking Services Map](#africas-talking-services-map)
15. [Tech Stack Summary](#tech-stack-summary)
16. [Environment Setup (WSL/Ubuntu)](#environment-setup-wslubuntu)
17. [Contributing](#contributing)

---

## Project Vision

AfriProp is not just a property listing website. It is a full property intelligence ecosystem designed
specifically for African markets — where internet penetration is uneven, land registries are fragmented,
mobile money dominates payments, and trust in property transactions is a major barrier.

The platform serves four distinct user types:
- **Tenants** — searching for rentals via web, mobile, SMS, or USSD
- **Landlords/Sellers** — listing, managing, and monetising their properties
- **Real estate agents** — managing leads, clients, and transactions through a CRM
- **Investors** — tracking fractional ownership, ROI, and market trends

---

## Core Problem Statement

| Problem | Impact |
|---|---|
| Lack of verified, centralised property listings | Fraud, wasted time, poor decision-making |
| No affordable access channel for feature phone users | Millions excluded from the market |
| Opaque property pricing | Buyers and tenants overpay; sellers underprice |
| Fragmented lease and rent management | Disputes, missed payments, no paper trail |
| Limited access to property financing | Low-income earners locked out of ownership |
| Weak title verification systems | Land fraud, double-selling, ownership disputes |
| No data-driven investment intelligence | Investors rely on guesswork |

---

## Solution Overview

AfriProp addresses all seven problems above through five integrated pillars:

1. **Multi-channel access** — Web, Mobile App, SMS, USSD, Voice IVR, WhatsApp
2. **AI-powered property intelligence** — Valuation, price forecasting, fraud detection, recommendations
3. **End-to-end property management** — Listings, tenants, leases, maintenance, payments
4. **Financial inclusion** — Mobile money integration, mortgage calculator, fractional investment
5. **Trust infrastructure** — Title verification, KYC, identity check, anti-fraud scoring

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        ACCESS CHANNELS                          │
│  Web App │ Mobile App │ SMS/USSD │ WhatsApp │ Voice IVR │ CRM   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│              API GATEWAY (FastAPI + JWT Auth)                    │
│         Rate limiting · Routing · Webhook handler               │
└──────────┬───────────┬──────────┬──────────┬────────────────────┘
           │           │          │          │
    ┌──────▼──┐  ┌─────▼───┐ ┌───▼────┐ ┌──▼──────────┐
    │Property │  │ Tenant  │ │Finance │ │  AI/ML      │
    │Service  │  │Service  │ │Service │ │  Service    │
    └──────┬──┘  └─────┬───┘ └───┬────┘ └──┬──────────┘
           │           │          │          │
┌──────────▼───────────▼──────────▼──────────▼──────────────────┐
│                         DATA LAYER                              │
│  PostgreSQL+PostGIS │ MongoDB │ Redis │ S3/MinIO │ Kafka/ETL    │
└─────────────────────────────────────────────────────────────────┘
           │
┌──────────▼─────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                        │
│  Africa's Talking │ M-Pesa/MTN MoMo │ Land Registry │ Maps     │
└────────────────────────────────────────────────────────────────┘
```

---

## Phase 1 — Foundation Setup & Core API

**Goal:** Set up the entire development environment, project skeleton, database, Docker,
and a working API gateway with authentication.

### 1.1 Development Environment (WSL/Ubuntu)
- Install and configure WSL2 with Ubuntu 22.04
- Install: Python 3.11, Node.js 20 LTS, Docker + Docker Compose, Git, PostgreSQL client
- Set up SSH keys for GitHub
- Configure VS Code with WSL remote extension
- Install Postman or Bruno for API testing

### 1.2 Repository & Project Structure
- Initialise monorepo with Git
- Set up `.env` file structure for all services
- Configure `.gitignore` for Python, Node, Docker secrets
- Write base `docker-compose.yml` for all services

### 1.3 Database Setup
- PostgreSQL 15 with PostGIS extension (for geo-spatial queries)
- MongoDB (for ML feature store and audit logs)
- Redis (for session management and USSD state)
- MinIO (S3-compatible local object storage for images/documents)
- Write base Alembic migration scripts for PostgreSQL

### 1.4 API Gateway Service
- FastAPI application with versioned routing (`/api/v1/`)
- JWT authentication middleware
- Role-based access control (tenant, landlord, agent, admin, investor)
- Rate limiting per IP and per API key
- Africa's Talking webhook receiver endpoint
- Health check endpoint (`/health`)
- Swagger/OpenAPI docs auto-generated

### 1.5 User & Auth Service
- User registration with email + phone number
- Phone OTP verification via Africa's Talking SMS
- JWT access token + refresh token flow
- Password reset via SMS OTP
- User profile management
- Role assignment system

**Deliverables:**
- [ ] All Docker services running via `docker-compose up`
- [ ] `/health` returns 200
- [ ] User can register, verify OTP, and receive JWT
- [ ] Swagger docs accessible at `localhost:8000/docs`

---

## Phase 2 — Property Core

**Goal:** Build the full property listing, search, and management system.

### 2.1 Property Listings Service
- Property model: type, bedrooms, bathrooms, floor area, furnishing, amenities
- Geo-location: latitude/longitude, neighbourhood, city, country
- PostGIS radius search — "find properties within 5km of coordinates"
- Property status: available, rented, sold, under_offer
- Listing verification flag (verified vs unverified)
- Landlord/agent linkage

### 2.2 Media Management
- Image upload to MinIO/S3 (max 10 images per listing)
- Image compression pipeline (Pillow)
- Virtual tour URL embedding (YouTube/Matterport link)
- Document upload: title deed, floor plan (PDF)
- Image watermarking for verified listings

### 2.3 Property Search & Filtering
- Full-text search on listing title and description (PostgreSQL `tsvector`)
- Filter by: city, neighbourhood, price range, bedrooms, property type, amenities
- Sort by: price, date listed, distance from point, AI valuation match score
- Saved searches with SMS/email alert on new match
- Map-based search with clustered markers

### 2.4 Property Verification Module
- Landlord identity verification (national ID upload + cross-check)
- Title deed parsing and validation
- Integration hook for land registry API (Kenya, Nigeria, Ghana)
- Duplicate listing detection (image hash comparison + description similarity)
- Verified badge system

### 2.5 Rental & Lease Management
- Tenant application workflow
- Lease agreement generation (PDF from template)
- Lease start/end dates with automated renewal alerts
- Rent payment schedule generation
- Maintenance request tracking per property
- Eviction notice workflow

**Deliverables:**
- [ ] CRUD endpoints for properties working
- [ ] Geo search returning properties within radius
- [ ] Image upload storing files in MinIO
- [ ] Lease PDF generated from template
- [ ] Duplicate listing detection flagging test cases

---

## Phase 3 — AI & Data Science Layer

**Goal:** Build, train, and serve three machine learning models as REST endpoints.

### 3.1 Dataset Strategy

**Sources:**
- Scraped public listings from local property sites (BeautifulSoup/Scrapy) — Kenya, Nigeria, Ghana
- Synthetic data generation using statistical distributions derived from known market data
- OpenStreetMap data for amenity proximity features (schools, hospitals, transit stops)
- Government open data for neighbourhood income/infrastructure indices
- Historical exchange rates and CPI for inflation-adjusted prices

**Feature Engineering:**
- Price per square metre by neighbourhood
- Distance to nearest: CBD, school, hospital, matatu/bus stage, shopping mall
- Neighbourhood infrastructure score (road quality, water, electricity reliability)
- Days on market before renting/selling
- Seasonal listing patterns

### 3.2 Property Valuation Model

**Algorithm:** XGBoost Regressor (primary) with Random Forest as baseline

**Features:**
```
bedrooms, bathrooms, floor_area_sqm, property_type,
city_encoded, neighbourhood_encoded, lat, lng,
distance_to_cbd_km, distance_to_school_km,
distance_to_hospital_km, transit_access_score,
infrastructure_score, listing_month, amenities_count
```

**Target:** `estimated_market_value_ksh`

**Evaluation Metrics:** RMSE, MAE, R², MAPE

**Output:** `{ "estimated_value": 2500000, "confidence_low": 2100000, "confidence_high": 2900000, "currency": "KES" }`

### 3.3 Price Trend Forecasting Model

**Algorithm:** Facebook Prophet (primary), LSTM (experimental)

**Input:** Historical median price per neighbourhood per month (24-month window)

**Additional regressors:** Inflation rate, central bank base rate, population growth index

**Output:** 6-month price forecast with upper/lower confidence bands

**Use:** Dashboard chart — "Prices in Westlands are projected to rise 8% over 6 months"

### 3.4 Fraud & Anomaly Detection Model

**Algorithm:** Isolation Forest + rule-based scoring

**Signals:**
- Price more than 2 standard deviations below neighbourhood median
- Duplicate images detected (perceptual hash — pHash)
- Duplicate description text (cosine similarity > 0.85)
- Landlord account age < 7 days
- Multiple listings from same phone number with different names
- Title deed OCR text mismatch with stated owner name

**Output:** `{ "fraud_score": 0.87, "flags": ["price_anomaly", "duplicate_image"], "recommendation": "manual_review" }`

### 3.5 Recommendation Engine

**Algorithm:** Collaborative filtering (Surprise library) + content-based fallback

**Input:** User search history, saved listings, viewed listings, contact requests made

**Output:** Personalised listing recommendations sorted by predicted interest score

### 3.6 ML Service API

- FastAPI ML service at port 8001
- Endpoints:
  - `POST /predict/valuation` — takes property features, returns estimated value
  - `POST /predict/price-trend` — takes neighbourhood + months, returns forecast
  - `POST /detect/fraud` — takes listing data, returns fraud score
  - `POST /recommend` — takes user_id, returns ranked listing IDs
- Models serialised with `joblib` and loaded at startup
- Model versioning: models stored as `model_valuation_v1.pkl`
- Jupyter notebooks for training in `/ml/notebooks/`

**Deliverables:**
- [ ] Training notebook runs end-to-end with synthetic dataset
- [ ] Valuation model achieves R² > 0.80 on test set
- [ ] Fraud model flags known bad listings in test set
- [ ] All four ML endpoints responding correctly
- [ ] Model accuracy report generated as HTML

---

## Phase 4 — Africa's Talking Integration

**Goal:** Make the platform accessible via SMS, USSD, Voice, and WhatsApp
for users with no smartphone or internet access.

### 4.1 SMS Channel

**Inbound (user texts to shortcode):**

| User texts | System response |
|---|---|
| `HOUSE 3BR NAIROBI` | Top 3 listings with price, location, contact |
| `LIST` | Step-by-step listing submission via SMS dialogue |
| `RENT DUE` | Landlord gets payment status of all tenants |
| `VALE 3BR KILIMANI 80SQM` | AI valuation estimate returned by SMS |
| `HELP` | Menu of available commands |

**Outbound (system-triggered SMS):**
- Rent due reminder (3 days before, day of, 3 days after)
- New listing alert matching saved search
- Lease expiry warning (30 days, 7 days)
- OTP for registration and login
- Payment confirmation after mobile money rent payment
- Maintenance request status update

### 4.2 USSD Channel

**Dial code:** `*384*PROP#` (example)

**Session flow (stored in Redis, 180-second timeout):**

```
*384*PROP#
└── 1. Search property
    ├── 1. City (Nairobi / Mombasa / Kisumu / Other)
    ├── 2. Type (House / Apartment / Land / Commercial)
    ├── 3. Bedrooms (1 / 2 / 3 / 4+)
    ├── 4. Max budget (enter amount in KES)
    └── → Returns: Top 3 results with price + SMS link
└── 2. My listings (landlord)
    ├── 1. View my listings (count + status)
    ├── 2. Check rent payments
    └── 3. Submit maintenance issue
└── 3. Pay rent
    ├── Enter property code
    ├── Confirm amount
    └── → Triggers M-Pesa STK push
└── 4. Valuation estimate
    ├── City → Neighbourhood → Bedrooms → Size (sqm)
    └── → Returns AI estimated value
└── 5. Help / Contact agent
```

### 4.3 Voice IVR Channel

- Inbound call to AT virtual number
- Text-to-speech reads top 3 listings for caller's city (detected from number prefix)
- Keypad input: Press 1 to hear next listing, Press 2 to get SMS with details, Press 3 to connect to agent
- Outbound call for rent payment confirmation (automated call reads payment receipt)

### 4.4 Airtime & Mobile Data Rewards
- Landlords who complete profile verification receive KES 20 airtime
- Tenants who submit verified reviews receive KES 10 airtime
- Agents who close 3 verified transactions receive mobile data bundle
- All disbursed programmatically via AT Airtime API

### 4.5 WhatsApp Channel (AT Chat API)
- Keyword-triggered bot: `LIST`, `SEARCH`, `RENT`, `VALE`
- Rich message cards with property image, price, and contact button
- Lease document delivery via WhatsApp PDF attachment
- Rent payment confirmation message with receipt

**Deliverables:**
- [ ] SMS inbound command handler working on AT sandbox
- [ ] USSD menu navigates all 5 flows correctly
- [ ] Redis session persists between USSD hops
- [ ] Voice IVR reads back listing on inbound call
- [ ] Airtime disbursed successfully in AT sandbox test

---

## Phase 5 — Finance & Payments

**Goal:** Enable mobile money rent payments, mortgage calculations, and fractional investment.

### 5.1 Mobile Money Rent Payment
- M-Pesa STK Push (Daraja API) — tenant pays rent directly from phone
- MTN Mobile Money integration (West Africa markets)
- Airtel Money integration
- AT Mobile Money API as unified gateway
- Payment webhook confirmation → auto-update rent ledger
- Split payments: partial rent recording with balance tracking
- Automatic receipt generation (SMS + PDF)

### 5.2 Rent Ledger
- Per-tenant, per-property payment history
- Missed payment tracking with automated escalation
- Landlord monthly statement (PDF export)
- Tenant payment score (good payer badge)

### 5.3 Mortgage & Affordability Calculator
- Input: property price, deposit amount, loan term (years), interest rate
- Output: monthly repayment, total interest paid, affordability ratio vs income
- Compare: two banks side by side
- Integrate current rates from partner banks (manual update initially, API later)
- Share calculation result via SMS or WhatsApp

### 5.4 Fractional Property Investment
- Investment listings: commercial properties, rental blocks open to fractional buy-in
- Minimum investment unit (e.g. KES 5,000 = 0.1% ownership)
- Investor dashboard: portfolio value, monthly rental income share, ROI
- Investment payment via mobile money
- Digital ownership certificate (PDF)
- Crowd-funding progress bar per property

### 5.5 Credit & Affordability Scoring
- Tenant credit score from: payment history on platform, CRB Africa check, mobile money transaction patterns (with consent)
- Landlord risk score: listing quality, verified titles, response rate
- Output used by Finance service for loan eligibility pre-check

**Deliverables:**
- [ ] M-Pesa STK push triggers on rent payment attempt
- [ ] Webhook confirms payment and updates ledger
- [ ] Mortgage calculator returns correct amortisation table
- [ ] Fractional investment unit purchase recorded
- [ ] Rent ledger PDF exported correctly

---

## Phase 6 — Web & Mobile Frontend

**Goal:** Build the user-facing web application and mobile app.

### 6.1 Web Application (Next.js 14)
- Home page with search bar + featured listings map
- Property listing page with image gallery, AI valuation badge, virtual tour embed
- Search results page with map view + list view toggle
- Filters sidebar (price, type, bedrooms, amenities, verified only)
- Tenant dashboard: lease status, payment history, maintenance requests
- Landlord dashboard: portfolio overview, rent collection, tenant list
- Investor dashboard: portfolio, ROI chart (Chart.js), market trend forecast
- Admin panel: user management, listing moderation, fraud review queue
- Mortgage calculator page
- Neighbourhood insight page (price trends chart + amenity map)

### 6.2 Mobile App (React Native / Expo)
- GPS-powered "near me" property search
- Camera upload for property photos
- Push notifications (rent reminders, new matches, maintenance updates)
- In-app mobile money payment trigger
- Offline-capable saved listings
- Biometric login (fingerprint/face)
- Swipe-to-save listing (Tinder-style for property browsing)

### 6.3 UI/UX Design Principles
- Mobile-first responsive design
- Support low-bandwidth mode (image lazy loading, text-first rendering)
- WCAG 2.1 AA accessibility compliance
- Swahili / French / Hausa language toggle (i18n with next-intl)
- Dark mode support
- Colour palette: trust-building blues and greens with warm orange accents

**Deliverables:**
- [ ] Home page renders with listings from API
- [ ] Map search shows pinned properties
- [ ] Tenant can view lease and payment history
- [ ] Landlord can see rent collection dashboard
- [ ] Mobile app builds and runs on Android via Expo Go

---

## Phase 7 — CRM, Maintenance & Social Housing

**Goal:** Build agent-facing tools and social impact features.

### 7.1 Agent CRM
- Lead capture from listing enquiries (web, SMS, WhatsApp)
- Lead pipeline: New → Contacted → Viewing Scheduled → Offer Made → Closed
- Client communication log (SMS + call history via AT)
- Commission tracker per closed deal
- Agent performance dashboard: listings, closed deals, response time score
- Calendar integration for property viewings

### 7.2 Facility & Maintenance Management
- Tenant submits maintenance request (web, mobile, or SMS: `FIX LEAK 3B`)
- Work order generation with priority level
- Vendor assignment (plumber, electrician, painter — from vendor directory)
- Status updates via SMS to tenant and landlord
- Cost tracking and approval workflow
- Preventive maintenance schedule (e.g. annual roof inspection reminder)

### 7.3 Social Housing & Affordable Housing Module
- Database of government housing programs (Kenya, Nigeria, Ghana, Rwanda)
- Eligibility checker: income level, family size → matching programs
- Application assistance workflow
- Integration with county/state housing board portals where APIs exist
- USSD-accessible: `*384*PROP# → 6. Affordable housing`
- Notification when new affordable units become available in user's city

### 7.4 Sustainability Module
- Energy efficiency rating per property (A–G scale, based on landlord input)
- Solar installation vendor directory
- Carbon footprint estimate per building
- Green building badge for qualifying properties
- Filter: "Show only energy-efficient properties"

**Deliverables:**
- [ ] Agent can manage leads through full pipeline
- [ ] Maintenance request submitted via SMS reaches landlord dashboard
- [ ] Affordable housing program eligibility check works
- [ ] Energy rating appears on property listing

---

## Phase 8 — CI/CD & Deployment

**Goal:** Automate testing, building, and deployment of all services.

### 8.1 Testing Strategy
- Unit tests: `pytest` for all Python services (min 70% coverage)
- Integration tests: API endpoint tests with `httpx` test client
- Frontend tests: `Jest` + `React Testing Library`
- ML model tests: assert predictions within expected range on known inputs
- AT channel tests: mock AT sandbox responses in test suite
- Load testing: `Locust` for API gateway stress test

### 8.2 GitHub Actions CI Pipeline
- On every push to `main` or `develop`:
  - Run `pytest` for all backend services
  - Run `jest` for frontend
  - Build Docker images for changed services
  - Push images to GitHub Container Registry (GHCR)
  - Deploy to staging environment

### 8.3 Docker & Containerisation
- Each service has its own `Dockerfile`
- Base `docker-compose.yml` for local development
- `docker-compose.prod.yml` for production overrides
- Environment variables managed with `.env` files (never committed)
- Health checks on all containers

### 8.4 Production Deployment Options
- **Option A (cheapest for hackathon):** Railway.app — one-click Docker deploy, free tier
- **Option B:** Render.com — managed Postgres + Redis + web service free tier
- **Option C:** DigitalOcean Droplet (Ubuntu) — full control, ~$6/month
- **Option D:** AWS EC2 t3.micro + RDS free tier (most enterprise-looking for judges)

### 8.5 Monitoring & Observability
- Structured JSON logging (Python `loguru`)
- Sentry for error tracking (free tier)
- Uptime monitoring: BetterUptime or UptimeRobot (free)
- Simple metrics dashboard: Prometheus + Grafana (Docker service)

**Deliverables:**
- [ ] `docker-compose up` starts all services cleanly
- [ ] GitHub Actions pipeline runs green on push
- [ ] Staging URL accessible publicly
- [ ] Sentry capturing errors from production

---

## Dataset & Training Strategy

### Synthetic Dataset Generation Plan

Since real historical African property data is scarce, generate a realistic training set:

```
Target: 50,000 property records
Cities: Nairobi, Mombasa, Kampala, Lagos, Accra, Dar es Salaam
Property types: apartment, house, land, commercial, bedsitter
```

**Script approach:** Python script using `Faker` + statistical distributions:
- Bedroom count: weighted random (bedsitter 20%, 1BR 25%, 2BR 30%, 3BR 20%, 4BR+ 5%)
- Price distribution: log-normal per city/neighbourhood (matches real estate pricing reality)
- Geo-coordinates: sampled within known city bounding boxes
- Amenity proximity: calculated from real OpenStreetMap POI data
- Fraud samples: 5% of dataset manually injected with anomaly signals

**Real data supplement:**
- Scrape public listing summaries from buyrentkenya.com, propertypro.ng, meqasa.com (respect robots.txt, anonymise)
- Kenya National Bureau of Statistics housing data (public domain)
- World Bank open data: urbanisation, income distribution

---

## Africa's Talking Services Map

| Service | Platform feature | AT API used |
|---|---|---|
| SMS OTP | User registration/login | SMS API |
| SMS search results | Feature phone property search | SMS API |
| SMS rent reminder | Tenant payment alerts | SMS API (scheduled) |
| USSD property search | No-internet property discovery | USSD API |
| USSD rent payment trigger | M-Pesa STK push via USSD | USSD API + AT Mobile Money |
| Voice IVR listings | Spoken property listings | Voice API (TTS) |
| Voice payment confirmation | Outbound confirmation call | Voice API (outbound) |
| WhatsApp listing card | Rich property preview | AT Chat API |
| Airtime reward | Landlord/tenant incentive | Airtime API |
| Mobile data bundle | Agent performance reward | Mobile Data API |

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend API | Python 3.11, FastAPI, SQLAlchemy, Alembic |
| ML/Data Science | scikit-learn, XGBoost, Prophet, pandas, numpy, Jupyter |
| Databases | PostgreSQL 15 + PostGIS, MongoDB, Redis |
| Object Storage | MinIO (local) / AWS S3 (production) |
| Message Queue | Redis Queue (RQ) for background jobs |
| Web Frontend | Next.js 14, TypeScript, Tailwind CSS, Leaflet.js (maps) |
| Mobile App | React Native (Expo) |
| AT Integration | africa-is-talking Python SDK |
| Payments | M-Pesa Daraja API, AT Mobile Money API |
| PDF Generation | WeasyPrint (leases, receipts, reports) |
| Image Processing | Pillow, imagehash (pHash for duplicate detection) |
| Containerisation | Docker, Docker Compose |
| CI/CD | GitHub Actions, GHCR |
| Monitoring | Sentry, Prometheus, Grafana, Loguru |
| Testing | pytest, httpx, Jest, Locust |
| Environment | WSL2 + Ubuntu 22.04, VS Code |

---

## Environment Setup (WSL/Ubuntu)

### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Install Docker
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
newgrp docker

# Install Git
sudo apt install git -y

# Install PostgreSQL client (for connecting to Docker DB)
sudo apt install postgresql-client -y

# Install useful dev tools
sudo apt install curl wget jq httpie tree -y
```

### WSL-Specific Notes
- Always run Docker Desktop on the Windows side with "Use WSL 2 based engine" enabled
- Access the app from Windows browser at `http://localhost:PORT` — WSL ports forward automatically
- Store all project files inside WSL filesystem (`~/projects/`) NOT on `/mnt/c/` — file I/O is significantly faster
- Use VS Code with the "Remote - WSL" extension to edit files directly in WSL
- For Africa's Talking webhooks during local development, use `ngrok` to expose your local port:

```bash
# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Expose local port 8000 to the internet for AT callbacks
ngrok http 8000
```

### Clone & Start

```bash
git clone https://github.com/YOUR_USERNAME/afriprop.git
cd afriprop
cp .env.example .env          # fill in your credentials
docker-compose up --build     # start all services
```

---

## What You Should Not Leave Out

The following are easy to forget but will be asked about by judges:

1. **Data privacy policy** — GDPR/Kenya Data Protection Act compliance statement
2. **robots.txt and scraping ethics** — document that scraped data is anonymised
3. **API rate limiting** — protect against abuse on all public endpoints
4. **USSD session timeout handling** — 180-second AT limit; Redis TTL must match
5. **Multi-currency support** — KES, NGN, GHS, UGX, TZS from day one, not an afterthought
6. **Offline-first mobile strategy** — cached listings for poor connectivity
7. **Accessibility** — screen reader support, high-contrast mode
8. **Model retraining pipeline** — how and when does the AI model update with new data
9. **Webhook security** — validate AT webhook signatures to prevent spoofing
10. **Demo data seeder** — a script that populates the DB with realistic demo data for the hackathon demo
11. **i18n from the start** — Swahili, French, Hausa as first-class language options
12. **Landlord/tenant dispute resolution workflow** — a basic flagging and escalation system
13. **Environmental variables never hardcoded** — all secrets in `.env`, all `.env` in `.gitignore`
14. **Postman/Bruno collection** — export your API collection for judges to test
15. **Video demo** — record a 3-minute walkthrough covering: web search, USSD flow, AI valuation, rent payment

---

## Contributing

```
main          — stable, demo-ready code only
develop       — integration branch
feature/*     — individual feature branches
fix/*         — bug fix branches
ml/*          — model training and experimentation
```

Pull request checklist:
- [ ] Tests pass locally
- [ ] No secrets committed
- [ ] Docstrings added to new functions
- [ ] `.env.example` updated if new env vars added
- [ ] README updated if new service or dependency added

---

*Built for the Real Estate Solutions Hackathon — Africa's Talking × PropTech Africa*
*WSL2 Ubuntu 22.04 · Docker · FastAPI · Next.js · scikit-learn · Africa's Talking APIs*

# Folder structure
```
afriprop/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # run tests on push
│       └── deploy.yml                # build + deploy on merge to main
│
├── services/
│   ├── gateway/                      # API gateway service (port 8000)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── middleware/
│   │   │   │   ├── auth.py           # JWT validation
│   │   │   │   └── rate_limit.py
│   │   │   ├── routers/
│   │   │   │   ├── auth.py
│   │   │   │   └── webhooks.py       # AT webhook receiver
│   │   │   └── config.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── property/                     # property CRUD + search (port 8001)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   │   ├── property.py
│   │   │   │   └── media.py
│   │   │   ├── routers/
│   │   │   │   ├── listings.py
│   │   │   │   ├── search.py
│   │   │   │   └── verification.py
│   │   │   ├── services/
│   │   │   │   ├── geo_search.py     # PostGIS queries
│   │   │   │   ├── media.py          # image upload + compression
│   │   │   │   └── duplicate.py      # pHash fraud check
│   │   │   └── schemas/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── tenant/                       # tenant + lease management (port 8002)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   │   ├── tenant.py
│   │   │   │   ├── lease.py
│   │   │   │   └── maintenance.py
│   │   │   ├── routers/
│   │   │   │   ├── tenants.py
│   │   │   │   ├── leases.py
│   │   │   │   └── maintenance.py
│   │   │   └── services/
│   │   │       ├── lease_pdf.py      # WeasyPrint lease generation
│   │   │       └── screening.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── finance/                      # payments + mortgage + investment (port 8003)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   │   ├── payment.py
│   │   │   │   ├── investment.py
│   │   │   │   └── ledger.py
│   │   │   ├── routers/
│   │   │   │   ├── payments.py
│   │   │   │   ├── mortgage.py
│   │   │   │   └── investment.py
│   │   │   └── services/
│   │   │       ├── mpesa.py          # Daraja STK push
│   │   │       ├── mtn_momo.py
│   │   │       └── receipt_pdf.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── ml/                           # AI/ML inference service (port 8004)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/
│   │   │   │   ├── valuation.py
│   │   │   │   ├── fraud.py
│   │   │   │   ├── trends.py
│   │   │   │   └── recommendations.py
│   │   │   ├── models/               # serialised model files
│   │   │   │   ├── valuation_v1.pkl
│   │   │   │   ├── fraud_v1.pkl
│   │   │   │   └── trend_v1.pkl
│   │   │   └── services/
│   │   │       └── model_loader.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── notify/                       # notifications (port 8005)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/
│   │   │   │   └── notify.py
│   │   │   └── services/
│   │   │       ├── sms.py            # AT SMS outbound
│   │   │       ├── push.py           # mobile push notifications
│   │   │       └── scheduler.py      # cron rent reminders
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── channels/                     # AT channel handlers (port 8006)
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   │   ├── sms_inbound.py    # parse inbound SMS commands
│       │   │   ├── ussd.py           # USSD session state machine
│       │   │   ├── voice.py          # IVR flow handler
│       │   │   └── whatsapp.py       # AT Chat API handler
│       │   └── services/
│       │       ├── ussd_session.py   # Redis session management
│       │       ├── sms_parser.py     # parse "HOUSE 3BR NAIROBI"
│       │       └── ivr_builder.py    # build AT voice XML responses
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
│
├── ml/
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_valuation_model.ipynb
│   │   ├── 04_fraud_detection.ipynb
│   │   ├── 05_price_trends.ipynb
│   │   └── 06_recommendations.ipynb
│   ├── data/
│   │   ├── raw/                      # scraped/downloaded data (gitignored)
│   │   ├── processed/                # cleaned features (gitignored)
│   │   └── synthetic/                # generated training data
│   ├── scripts/
│   │   ├── generate_synthetic_data.py
│   │   ├── scrape_listings.py
│   │   ├── train_valuation.py
│   │   ├── train_fraud.py
│   │   └── evaluate_models.py
│   └── reports/
│       └── model_accuracy.html       # auto-generated after training
│
├── web/                              # Next.js 14 frontend
│   ├── src/
│   │   ├── app/                      # Next.js app router
│   │   │   ├── page.tsx              # home page
│   │   │   ├── search/
│   │   │   ├── property/[id]/
│   │   │   ├── dashboard/
│   │   │   │   ├── tenant/
│   │   │   │   ├── landlord/
│   │   │   │   ├── agent/
│   │   │   │   └── investor/
│   │   │   ├── mortgage/
│   │   │   └── admin/
│   │   ├── components/
│   │   │   ├── Map/
│   │   │   ├── PropertyCard/
│   │   │   ├── SearchBar/
│   │   │   ├── ValuationBadge/
│   │   │   ├── MortgageCalculator/
│   │   │   └── Charts/
│   │   ├── lib/
│   │   │   ├── api.ts                # typed API client
│   │   │   └── auth.ts
│   │   ├── i18n/
│   │   │   ├── en.json
│   │   │   ├── sw.json               # Swahili
│   │   │   └── fr.json
│   │   └── types/
│   ├── public/
│   ├── tests/
│   ├── Dockerfile
│   ├── next.config.ts
│   └── package.json
│
├── mobile/                           # React Native / Expo app
│   ├── src/
│   │   ├── screens/
│   │   │   ├── HomeScreen.tsx
│   │   │   ├── SearchScreen.tsx
│   │   │   ├── PropertyScreen.tsx
│   │   │   ├── DashboardScreen.tsx
│   │   │   └── PaymentScreen.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── navigation/
│   ├── app.json
│   └── package.json
│
├── infra/
│   ├── docker/
│   │   └── nginx/
│   │       └── nginx.conf            # reverse proxy config
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
│
├── database/
│   ├── migrations/                   # Alembic migration files
│   ├── seeds/
│   │   └── demo_seed.py             # populates DB with demo data
│   └── schema.sql                    # reference schema diagram
│
├── docs/
│   ├── api/                          # exported Postman collection
│   ├── architecture/
│   │   └── diagram.png
│   ├── ussd_flows.md
│   ├── sms_commands.md
│   └── data_privacy.md
│
├── scripts/
│   ├── setup_wsl.sh                  # one-shot WSL environment setup
│   ├── seed_db.sh
│   └── run_tests.sh
│
├── docker-compose.yml                # local dev — all services
├── docker-compose.prod.yml           # production overrides
├── .env.example                      # template — copy to .env
├── .gitignore
├── Makefile                          # shortcuts: make up, make test, make seed
└── README.md
```

---

## What you are leaving out — checklist

Beyond what's in the README, here are things easy to skip that will cost you:

**Technical gaps:**
- A `Makefile` with commands like `make up`, `make test`, `make seed`, `make ngrok` — saves enormous time during the hackathon demo
- A `demo_seed.py` that populates 50+ realistic listings, 3 tenants, 2 landlords, and 1 agent with payment history — judges will test the UI and it must not be empty
- USSD session timeout handling — AT kills sessions at 180 seconds, your Redis TTL must match exactly
- Webhook signature verification — Africa's Talking signs its callbacks; validate the `X-AT-Signature` header or it's a security hole
- `ngrok` setup documented — without this you cannot receive AT callbacks on local dev

**Presentation gaps:**
- A recorded 3-minute demo video — many hackathons allow async demo submission, always have one ready
- A Postman collection exported as JSON in `/docs/api/` — judges who are developers will import it and test your endpoints directly
- A one-page pitch summary (what it does, who it serves, how it makes money) — even technical hackathons ask this
- Cost estimates — show judges you know what it costs to run: AT SMS per message, M-Pesa transaction fee, hosting cost per month

**Data science gaps:**
- A confusion matrix and feature importance chart for your fraud model — print these in the notebook, screenshot for the presentation
- Baseline comparison — show your XGBoost valuation model beats a simple linear regression baseline; this proves the ML is adding value
- A `model_card.md` — one-page document explaining what each model does, what data it was trained on, and its known limitations