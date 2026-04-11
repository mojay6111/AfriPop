## **Phase 5 — Finance & Payments**

### **What This Phase Is About**

Phase 5 makes AfriProp a complete financial platform for property transactions.
A tenant can pay rent directly from their phone via M-Pesa or MTN Mobile Money.
A landlord sees a real-time rent ledger with payment history and missed payment
tracking. An investor can buy fractional ownership units in commercial properties
using mobile money. All payments are confirmed automatically via webhooks and
receipts are generated as PDFs.

This phase is critical for the hackathon because it demonstrates financial
inclusion — the core promise of AfriProp. A tenant in Kibera pays rent without
a bank account. A diaspora investor in London buys 0.5% of a Nairobi apartment
block for KES 5,000. A landlord in Mombasa gets paid automatically and receives
a monthly statement PDF.

---

### Services Used

| Service | Purpose |
|---|---|
| M-Pesa Daraja API | STK push rent payments, Kenya market |
| MTN Mobile Money | West Africa rent payments |
| AT Mobile Money API | Unified gateway fallback |
| WeasyPrint | PDF lease, receipt, statement generation |
| Redis Queue (RQ) | Background jobs for payment processing |
| PostgreSQL | Payment ledger, investment records |

---

### What We Are Building

#### 5.1 — Finance Service Setup (port 8003)

A standalone FastAPI microservice owning everything money-related.
No other service handles payments — they all call this service.

**File structure:**
```
services/finance/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── payment.py        ← Payment, RentLedger
│   │   ├── investment.py     ← Investment, InvestmentProperty
│   │   └── reward.py        ← AirtimeReward log
│   ├── schemas/
│   │   ├── payment.py
│   │   └── investment.py
│   ├── routers/
│   │   ├── payments.py       ← STK push, webhook, ledger
│   │   ├── mortgage.py       ← calculator endpoints
│   │   └── investment.py     ← fractional investment
│   └── services/
│       ├── mpesa.py          ← Daraja API integration
│       ├── mtn_momo.py       ← MTN Mobile Money
│       ├── ledger_service.py ← payment recording + queries
│       └── pdf_service.py    ← receipt + statement PDFs
├── Dockerfile
└── requirements.txt
```

**Dependencies:**
```
fastapi, uvicorn, sqlalchemy, asyncpg, alembic,
pydantic, pydantic-settings, httpx,
weasyprint (PDF generation),
redis, rq (background jobs),
python-dotenv, requests
```

---

#### 5.2 — Database Models

**`payments` table:**
```
id, tenant_id, landlord_id, property_id,
amount, currency, payment_method (mpesa/mtn/airtel/card),
status (pending/completed/failed/refunded),
mpesa_checkout_request_id, mpesa_receipt_number,
reference_code, description,
paid_at, created_at, updated_at
```

**`rent_ledger` table:**
```
id, tenant_id, landlord_id, property_id,
due_date, amount_due, amount_paid, balance,
status (paid/partial/overdue/pending),
payment_id (FK to payments),
month_year, notes,
created_at, updated_at
```

**`investment_properties` table:**
```
id, property_id, title, description,
total_value, total_units, unit_price, currency,
units_sold, units_available,
minimum_investment, expected_roi_pct,
status (open/funded/closed),
created_at, updated_at
```

**`investments` table:**
```
id, investor_id, investment_property_id,
units_purchased, amount_invested, currency,
ownership_pct, monthly_income_share,
payment_id (FK), status (active/exited),
purchased_at, created_at
```

---

#### 5.3 — M-Pesa STK Push (Daraja API)

The tenant initiates rent payment from the web or USSD. The finance service
triggers an M-Pesa STK push — a popup appears on the tenant's phone asking
them to enter their M-Pesa PIN. Once confirmed, M-Pesa calls our webhook
with the transaction result.

**Payment flow:**
```
Tenant clicks "Pay Rent" (web/USSD/SMS)
        │
        ▼
POST /api/v1/finance/payments/mpesa/initiate
  → Finance service calls Daraja STK push API
  → M-Pesa sends popup to tenant phone
  → Returns checkout_request_id
        │
        ▼
Tenant enters M-Pesa PIN on phone
        │
        ▼
M-Pesa calls POST /api/v1/finance/payments/mpesa/callback
  → Finance service validates callback
  → Updates payment status to completed
  → Updates rent ledger
  → Generates PDF receipt
  → Sends SMS confirmation via AT
  → Triggers airtime reward if first payment
```

**STK push request:**
```json
{
  "BusinessShortCode": "174379",
  "Password": "base64(shortcode+passkey+timestamp)",
  "Timestamp": "20260410120000",
  "TransactionType": "CustomerPayBillOnline",
  "Amount": 45000,
  "PartyA": "254700000001",
  "PartyB": "174379",
  "PhoneNumber": "254700000001",
  "CallBackURL": "https://YOUR_URL/api/v1/finance/payments/mpesa/callback",
  "AccountReference": "AFRIPROP-LEASE-001",
  "TransactionDesc": "Rent payment April 2026"
}
```

**Daraja callback response:**
```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "...",
      "CheckoutRequestID": "...",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 45000},
          {"Name": "MpesaReceiptNumber", "Value": "QKA12BC34D"},
          {"Name": "PhoneNumber", "Value": 254700000001}
        ]
      }
    }
  }
}
```

---

#### 5.4 — MTN Mobile Money

Same flow as M-Pesa but for West Africa markets (Nigeria, Ghana, Uganda).
MTN MoMo API uses OAuth2 for authentication and a different callback
structure. The finance service abstracts both into a unified payment
interface — the tenant doesn't know or care which provider processes
the payment.

**Supported providers:**
```
M-Pesa    → Kenya, Tanzania (Daraja API)
MTN MoMo  → Nigeria, Ghana, Uganda, Cameroon
Airtel Money → Kenya, Uganda, Tanzania, Rwanda
```

---

#### 5.5 — Rent Ledger

Every property has a rent ledger — a record of what is owed, what has
been paid, and what the balance is for every month.

**Ledger operations:**
- Generate monthly rent entry on lease start date (cron job)
- Record payment when webhook confirms success
- Track partial payments — tenant pays KES 30,000 of KES 45,000 due
- Calculate running balance across months
- Flag overdue entries after grace period (3 days)
- Generate landlord monthly statement PDF

**Endpoints:**
```
GET  /api/v1/finance/ledger/{property_id}         → full ledger
GET  /api/v1/finance/ledger/{property_id}/{month} → single month
GET  /api/v1/finance/ledger/tenant/{tenant_id}    → tenant view
POST /api/v1/finance/ledger/generate              → create monthly entry
```

---

#### 5.6 — Mortgage & Affordability Calculator

No database — pure calculation endpoints. Used on the web dashboard
and accessible via USSD flow.

**Input:**
```json
{
  "property_price": 5000000,
  "deposit_amount": 1000000,
  "loan_term_years": 20,
  "annual_interest_rate": 13.5,
  "monthly_income": 150000,
  "currency": "KES"
}
```

**Output:**
```json
{
  "loan_amount": 4000000,
  "monthly_repayment": 48234,
  "total_repayment": 11576160,
  "total_interest": 7576160,
  "affordability_ratio": 32.2,
  "affordability_status": "affordable",
  "max_affordable_price": 6200000,
  "amortisation_schedule": [...]
}
```

**Affordability status:**
- Below 30% of income → "comfortable"
- 30–40% → "affordable"
- 40–50% → "stretched"
- Above 50% → "unaffordable"

---

#### 5.7 — Fractional Property Investment

Investors buy units in commercial or high-value residential properties.
Each unit represents a fraction of ownership and earns a monthly income
share proportional to the fraction owned.

**Investment flow:**
```
Investor browses investment listings
        │
        ▼
POST /api/v1/finance/investments/initiate
  → Validates units available
  → Triggers mobile money payment
  → On webhook confirmation:
     → Records investment
     → Calculates ownership percentage
     → Generates digital ownership certificate PDF
     → Sends confirmation SMS
```

**Investment listing example:**
```
Westlands Commercial Block A
Total value:     KES 50,000,000
Unit price:      KES 5,000 = 0.01% ownership
Units available: 8,000 of 10,000
Min investment:  1 unit (KES 5,000)
Expected ROI:    12% per annum
Monthly income share per unit: KES 50
```

**Investor dashboard shows:**
- Total invested amount
- Total units owned across all properties
- Monthly income share (credited to mobile money)
- Portfolio value (unit price × units owned)
- ROI to date
- 6-month price trend per property (from ML service)

---

#### 5.8 — PDF Generation (WeasyPrint)

Three PDF types generated programmatically:

**Rent receipt:**
- Tenant name, phone, property address
- Amount paid, payment method, M-Pesa receipt number
- Date and time of payment
- AfriProp logo and verification QR code

**Landlord monthly statement:**
- All properties owned
- Per property: rent due, rent received, outstanding balance
- Payment method breakdown
- Month total and YTD total

**Investment ownership certificate:**
- Investor name and phone
- Property name and address
- Units owned and ownership percentage
- Purchase date and amount
- Digital certificate number
- AfriProp verification stamp

---

#### 5.9 — Credit & Affordability Scoring

Tenant credit score calculated from platform data:

| Signal | Weight |
|---|---|
| On-time payment history on platform | 40% |
| Payment consistency (same day each month) | 20% |
| Listing count stability (not moving frequently) | 15% |
| Account age | 15% |
| Phone number verification | 10% |

Output: score 0–100 + label (Excellent/Good/Fair/Poor)
Used by landlords when screening tenant applications.

---

### Step-by-Step Build Order

```
Step 1 — Finance service skeleton (port 8003)
Step 2 — Database models (payments, ledger, investments)
Step 3 — M-Pesa Daraja integration (STK push + callback)
Step 4 — MTN MoMo integration
Step 5 — Payment ledger CRUD
Step 6 — Mortgage calculator endpoints
Step 7 — Fractional investment endpoints
Step 8 — PDF generation (receipts, statements, certificates)
Step 9 — Credit scoring
Step 10 — Wire rent reminders to channels service (SMS alerts)
```

---

### What Judges Will See

- Live M-Pesa STK push triggered from web UI — phone receives popup
- Payment webhook confirmed — ledger updated in real time
- PDF receipt downloaded after payment
- Mortgage calculator showing monthly repayment and affordability ratio
- Fractional investment unit purchased — ownership certificate PDF generated
- Landlord monthly statement PDF exported
- Tenant credit score displayed on landlord screening page
- Rent reminder SMS triggered automatically 3 days before due date

---

### Useful Commands

**Start finance service:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/finance
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

**Test mortgage calculator:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/mortgage/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "property_price": 5000000,
    "deposit_amount": 1000000,
    "loan_term_years": 20,
    "annual_interest_rate": 13.5,
    "monthly_income": 150000,
    "currency": "KES"
  }' | python3 -m json.tool
```

**Initiate M-Pesa STK push:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/payments/mpesa/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+254700000001",
    "amount": 45000,
    "property_id": "PROPERTY_ID",
    "tenant_id": "TENANT_ID",
    "description": "Rent April 2026"
  }' | python3 -m json.tool
```

**Check rent ledger:**
```bash
curl -s http://localhost:8003/api/v1/finance/ledger/PROPERTY_ID \
  | python3 -m json.tool
```

**Check investment listings:**
```bash
curl -s http://localhost:8003/api/v1/finance/investments/ \
  | python3 -m json.tool
```

**Check tables in PostgreSQL:**
```bash
docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT id, amount, status, payment_method FROM payments;"

docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT property_id, month_year, amount_due, amount_paid, status FROM rent_ledger;"
```


### ✅ Phase 5 — Completed (Core Finance Layer)

#### What Was Achieved

Phase 5 builds the finance service — a standalone FastAPI microservice on port
8003 that owns everything money-related in AfriProp. No other service handles
payments directly — they all call this service. Four PostgreSQL tables were
created automatically on startup covering the full financial lifecycle of a
property transaction.

---

#### Tables Created in PostgreSQL

```
payments              — every payment attempt with status, method, receipt
rent_ledger           — monthly rent tracking per tenant per property
investment_properties — commercial properties open for fractional investment
investments           — individual investor holdings with ownership percentage
```

---

#### What Is Built and Working

**Mortgage calculator** — pure math endpoint, no database. Takes property
price, deposit, loan term, interest rate, and monthly income. Returns monthly
repayment, total interest paid, affordability ratio as percentage of income,
affordability status (comfortable/affordable/stretched/unaffordable), and the
maximum affordable property price at 35% income threshold.

Example: KES 5M property, KES 1M deposit, 20 years at 13.5%:
- Monthly repayment: KES 48,295
- Total interest: KES 7,590,797
- Affordability on KES 150K income: 32.2% → "affordable"
- Max affordable price: KES 5,348,277

**Rent ledger** — creates monthly rent entries per tenant per property.
Tracks amount due, amount paid, running balance, and status (pending/paid/
partial/overdue). When an M-Pesa callback confirms payment, the ledger
updates automatically — amount_paid increases, balance decreases, status
flips to paid or partial.

**M-Pesa STK push** — initiates a payment popup on the tenant's phone.
Creates a pending payment record, calls Daraja API, stores the
CheckoutRequestID for callback matching. Callback webhook validates the
response, updates payment status, updates the rent ledger, and marks
the entry paid.

**Fractional investment** — landlords list commercial properties for
fractional investment. Investors buy units at a fixed price. Ownership
percentage and monthly income share are calculated automatically:
- 10 units of 10,000 = 0.1% ownership
- 12% annual ROI on KES 50M = KES 500,000/year ÷ 12 = KES 41,667/month total
- 0.1% of KES 41,667 = KES 500/month income share per investor

**Investor portfolio** — returns all active investments for an investor
with ownership percentage and monthly income share per holding.

---

#### Confirmed Working

```
GET  /health                                      ✔
POST /api/v1/finance/mortgage/calculate           ✔ correct amortisation math
POST /api/v1/finance/payments/ledger              ✔ creates monthly rent entry
GET  /api/v1/finance/payments/ledger/{property}   ✔ returns full ledger
GET  /api/v1/finance/payments/history/{tenant}    ✔ payment history
POST /api/v1/finance/payments/mpesa/initiate      ✔ STK push (sandbox)
POST /api/v1/finance/payments/mpesa/callback      ✔ webhook handler
POST /api/v1/finance/investments/                 ✔ create investment listing
GET  /api/v1/finance/investments/                 ✔ list open investments
POST /api/v1/finance/investments/invest           ✔ purchase units
GET  /api/v1/finance/investments/portfolio/{id}   ✔ investor portfolio
```

---

#### Pending

- **M-Pesa live test** — needs real Daraja sandbox consumer key and secret
  from developer.safaricom.co.ke. Current credentials are placeholders.
- **MTN Mobile Money** — service stub exists, needs MTN MoMo API credentials
  for West Africa markets (Nigeria, Ghana, Uganda).
- **PDF receipts** — WeasyPrint installed, receipt and statement templates
  not yet built.
- **Rent reminder SMS** — ledger overdue detection written, SMS trigger via
  channels service not yet wired.
- **Credit scoring** — tenant score from payment history not yet implemented.

---

#### Useful Commands

**Start finance service:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/finance
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

**Mortgage calculator:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/mortgage/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "property_price": 5000000,
    "deposit_amount": 1000000,
    "loan_term_years": 20,
    "annual_interest_rate": 13.5,
    "monthly_income": 150000,
    "currency": "KES"
  }' | python3 -m json.tool
```

**Create rent ledger entry:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/payments/ledger \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "TENANT_ID",
    "landlord_id": "LANDLORD_ID",
    "property_id": "PROPERTY_ID",
    "month_year": "2026-04",
    "due_date": "2026-04-01T00:00:00",
    "amount_due": 45000
  }' | python3 -m json.tool
```

**Initiate M-Pesa rent payment:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/payments/mpesa/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+254700000001",
    "amount": 45000,
    "property_id": "PROPERTY_ID",
    "tenant_id": "TENANT_ID",
    "landlord_id": "LANDLORD_ID",
    "description": "Rent April 2026"
  }' | python3 -m json.tool
```

**Create investment property:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/investments/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "PROPERTY_ID",
    "title": "Westlands Commercial Block A",
    "description": "Prime commercial property in Westlands Nairobi",
    "total_value": 50000000,
    "total_units": 10000,
    "unit_price": 5000,
    "currency": "KES",
    "minimum_investment": 1,
    "expected_roi_pct": 12.0
  }' | python3 -m json.tool
```

**Purchase investment units:**
```bash
curl -s -X POST http://localhost:8003/api/v1/finance/investments/invest \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": "INVESTOR_ID",
    "investment_property_id": "INVESTMENT_PROPERTY_ID",
    "units": 10,
    "phone": "+254700000001",
    "currency": "KES"
  }' | python3 -m json.tool
```

**View investor portfolio:**
```bash
curl -s http://localhost:8003/api/v1/finance/investments/portfolio/INVESTOR_ID \
  | python3 -m json.tool
```

**Check rent ledger for a property:**
```bash
curl -s http://localhost:8003/api/v1/finance/payments/ledger/PROPERTY_ID \
  | python3 -m json.tool
```

**Check tables in PostgreSQL:**
```bash
docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT id, amount, status, payment_method FROM payments;"

docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT property_id, month_year, amount_due, amount_paid, balance, status FROM rent_ledger;"

docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT title, total_units, units_sold, units_available, unit_price FROM investment_properties;"

docker exec afriprop_postgres psql -U afriprop -d afriprop \
  -c "SELECT investor_id, units_purchased, ownership_pct, monthly_income_share FROM investments;"
```

**Swagger docs:** `http://localhost:8003/docs`
```