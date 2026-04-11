# **Phase 4 — Africa's Talking Integration**

### **What This Phase Is About**

Phase 4 makes AfriProp accessible to every African regardless of device or internet
access. A landlord in rural Kenya with a Nokia feature phone can list a property via
USSD. A tenant in Lagos can search for apartments by sending an SMS. A property
investor in Accra can hear market prices read aloud over a voice call. All of this
runs through Africa's Talking APIs, routing into the same backend services built in
Phases 2 and 3.

This phase is the most impactful from a judge's perspective — it demonstrates that
AfriProp is not just another web app, but a platform designed for the African
reality where 60% of internet access is mobile, feature phones are still common,
and SMS remains the most reliable communication channel.

---

### **Africa's Talking Services Used**

| AT Service           | AfriProp Feature                                                                  | Channel                      |
| -------------------- | --------------------------------------------------------------------------------- | ---------------------------- |
| SMS API (inbound)    | Property search by keyword, listing submission, rent commands                     | Feature phones + smartphones |
| SMS API (outbound)   | Rent reminders, OTP verification, payment confirmations, listing alerts           | System-triggered             |
| USSD API             | Full property search menu, rent payment trigger, AI valuation, affordable housing | Feature phones (no internet) |
| Voice API (inbound)  | IVR property listings read aloud, connect to agent                                | Any phone                    |
| Voice API (outbound) | Automated rent payment confirmation calls                                         | System-triggered             |
| Airtime API          | Reward landlords and tenants for verified actions                                 | Programmatic disbursement    |

---

### Architecture of This Phase

```
User (any phone)
      │
      ├── SMS  ──────────────────────────────────────────────┐
      ├── USSD (*384*PROP#) ─────────────────────────────────┤
      └── Voice call ────────────────────────────────────────┤
                                                             │
                                              Africa's Talking
                                              (webhook POST)
                                                             │
                                    ┌────────────────────────▼────────────┐
                                    │   channels service (port 8006)      │
                                    │   ├── sms_inbound.py                │
                                    │   ├── ussd.py (Redis session state) │
                                    │   ├── voice.py (XML responses)      │
                                    │   └── airtime.py                    │
                                    └────────────────────────┬────────────┘
                                                             │
                              ┌──────────────┬──────────────┼──────────────┐
                              │              │              │              │
                        property        gateway           ml           notify
                        service         service          service        service
                        (search)       (auth/OTP)     (valuation)    (SMS out)
```

---

### Step-by-Step Build Plan

---

#### Step 1 — Africa's Talking Account & Sandbox Setup

Before writing any code, set up the AT sandbox environment:

1. Register at africastalking.com and create a sandbox app
2. Get sandbox API key and username (`sandbox`)
3. Set up ngrok to expose local port 8006 to the internet
   (AT webhooks need a public URL to call back)
4. Configure AT sandbox:
   - SMS shortcode: set callback URL to `https://YOUR_NGROK/api/v1/channels/sms/inbound`
   - USSD: create a service with code `*384*PROP#`, set callback to `https://YOUR_NGROK/api/v1/channels/ussd`
   - Voice: set callback to `https://YOUR_NGROK/api/v1/channels/voice/inbound`
5. Update `.env` with real AT sandbox credentials
6. Test with AT simulator on the dashboard

---

#### Step 2 — Channels Service Setup (port 8006)

Create the standalone channels service that receives all AT webhook callbacks
and routes them to the appropriate handler.

**File structure:**

```
services/channels/
├── app/
│   ├── main.py              ← FastAPI app, all routers registered
│   ├── config.py            ← points to root .env
│   ├── routers/
│   │   ├── sms_inbound.py   ← handles incoming SMS from AT webhook
│   │   ├── ussd.py          ← handles USSD session state machine
│   │   ├── voice.py         ← handles IVR flow, returns AT XML
│   │   └── airtime.py       ← disburse airtime rewards
│   └── services/
│       ├── sms_parser.py    ← parse "HOUSE 3BR NAIROBI" into structured query
│       ├── ussd_session.py  ← Redis session management for USSD state
│       ├── at_client.py     ← Africa's Talking SDK wrapper
│       ├── property_client.py ← HTTP client calling property service
│       └── ml_client.py     ← HTTP client calling ML service
├── Dockerfile
└── requirements.txt
```

**Dependencies:**

```
fastapi, uvicorn, redis, httpx, africastalking,
pydantic, pydantic-settings, python-dotenv
```

---

#### Step 3 — SMS Inbound Command Handler

Users text a shortcode and get instant responses. The system parses natural
language property queries from SMS text.

**Supported inbound commands:**

| User texts                   | System does                        | Response                                  |
| ---------------------------- | ---------------------------------- | ----------------------------------------- |
| `HOUSE 3BR NAIROBI`          | Searches property service          | Top 3 listings with price + neighbourhood |
| `SEARCH APARTMENT LAGOS 2BR` | Searches with filters              | Top 3 results                             |
| `VALE 3BR WESTLANDS 120SQM`  | Calls ML valuation endpoint        | AI estimated value                        |
| `LIST`                       | Starts listing submission dialogue | Step-by-step SMS conversation             |
| `RENT DUE`                   | Checks tenant payment status       | Balance and due date                      |
| `HELP`                       | Returns command menu               | Full list of SMS commands                 |

**SMS parser logic:**

- Tokenise the incoming message by spaces
- Identify keywords: property type, bedroom count, city, neighbourhood, area
- Map to structured search parameters
- Call property service search endpoint
- Format top 3 results into 160-character SMS segments

**Outbound SMS triggers (system-initiated):**

- Rent due reminder: 3 days before, day of, 3 days after due date
- OTP verification: 6-digit code with 10-minute expiry
- Payment confirmation: receipt after mobile money payment
- Listing alert: new property matching saved search
- Lease expiry warning: 30 days and 7 days before end date
- Maintenance update: status change on work order

---

#### Step 4 — USSD Session State Machine

The USSD channel is the most technically complex part of this phase. Every USSD
session is stateless from AT's side — they send a new POST for every menu
selection. We maintain state in Redis with a 180-second TTL matching AT's timeout.

**Dial code:** `*384*PROP#`

**Full menu tree:**

```
*384*PROP#
│
├── 1. Search property
│   ├── Select city (1=Nairobi 2=Mombasa 3=Kampala 4=Lagos 5=Accra 6=Dar)
│   ├── Select type (1=Apartment 2=House 3=Bedsitter 4=Commercial)
│   ├── Select bedrooms (1=1BR 2=2BR 3=3BR 4=4BR+)
│   ├── Enter max budget (type amount)
│   └── → Returns top 3 results + SMS link for full details
│
├── 2. My listings (landlord)
│   ├── 1. View my listings (count + status summary)
│   ├── 2. Check rent payments (who has paid this month)
│   └── 3. Report maintenance issue (enter description)
│
├── 3. Pay rent
│   ├── Enter property code
│   ├── Confirm amount shown
│   └── → Triggers M-Pesa STK push to user's number
│
├── 4. AI valuation
│   ├── Select city
│   ├── Select neighbourhood
│   ├── Enter bedrooms
│   ├── Enter floor area (sqm)
│   └── → Returns AI estimated value with range
│
├── 5. Affordable housing
│   ├── Select city
│   ├── Enter monthly income
│   └── → Returns matching government housing programs
│
└── 6. Help / contact agent
    └── → Returns SMS with agent contact list for selected city
```

**USSD session data stored in Redis:**

```json
{
  "session_id": "AT_SESSION_ID",
  "phone": "+254700000001",
  "step": "select_type",
  "flow": "search",
  "data": {
    "city": "Nairobi",
    "type": null,
    "bedrooms": null,
    "budget": null
  },
  "created_at": 1712345678,
  "ttl": 180
}
```

**USSD response format:**

- `CON` prefix = continue session (show next menu)
- `END` prefix = terminate session (show final message)

---

#### Step 5 — Voice IVR Flow

Inbound calls are handled by the Voice API. The service returns XML (Africa's
Talking Voice XML) that tells AT what to say and what keypad inputs to listen for.

**Inbound call flow:**

```
User dials AT virtual number
  → AT calls webhook POST /api/v1/channels/voice/inbound
  → Service returns XML: "Welcome to AfriProp. Press 1 for listings,
                          Press 2 for valuation, Press 3 for an agent."
  → User presses 1
  → AT calls webhook again with digit=1
  → Service returns listings for user's city (detected from phone prefix)
     read aloud via TTS: "Listing 1: 2 bedroom apartment in Westlands,
                          45,000 shillings per month. Press 1 to hear next.
                          Press 2 to get SMS with details."
```

**Outbound call flow (payment confirmation):**

```
Payment webhook received from M-Pesa
  → Finance service triggers outbound AT voice call to tenant
  → TTS reads: "Your rent payment of KES 45,000 for Westlands property
                has been received. Thank you."
```

**AT Voice XML response structure:**

```xml
<Response>
  <GetDigits timeout="30" finishOnKey="#">
    <Say>Welcome to AfriProp. Press 1 for property listings.
         Press 2 for AI valuation. Press 3 to speak to an agent.</Say>
  </GetDigits>
</Response>
```

---

#### Step 6 — Airtime Rewards

Programmatic airtime disbursement as incentives for platform engagement.

**Reward triggers:**

| Action                                  | Reward  | Amount |
| --------------------------------------- | ------- | ------ |
| Landlord completes profile verification | Airtime | KES 20 |
| Tenant submits verified review          | Airtime | KES 10 |
| Agent closes 3 verified transactions    | Airtime | KES 50 |
| First USSD property search              | Airtime | KES 5  |

**AT Airtime API call:**

```python
airtime.send(
    phone_number="+254700000001",
    currency_code="KES",
    amount=20
)
```

Airtime disbursement is logged in the database with timestamp, phone, amount,
and trigger reason for audit purposes.

---

#### Step 7 — ngrok Setup for Local Development

Africa's Talking webhooks require a publicly accessible URL. During local
development, ngrok tunnels your local port to the internet.

**Setup:**

```bash
# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Expose channels service port
ngrok http 8006
```

**Copy the ngrok HTTPS URL** and set it in the AT dashboard as the callback
URL for SMS, USSD, and Voice. Update `.env`:

```
AT_CALLBACK_BASE_URL=https://YOUR_NGROK_SUBDOMAIN.ngrok-free.app
```

Restart ngrok each session — the URL changes unless you have a paid ngrok account.
Use a fixed subdomain in production by deploying to a public server.

---

#### Step 8 — Webhook Security

Africa's Talking signs its webhook callbacks with a username header.
Validate every incoming webhook to prevent spoofing.

**Validation middleware:**

- Check `X-AT-Signature` header on every inbound request
- Reject requests without valid signature with 401
- Log rejected requests for security monitoring

---

#### Step 9 — End-to-End Testing Plan

Test each channel in the AT sandbox before going live:

**SMS testing:**

- Use AT sandbox simulator to send inbound SMS
- Verify `HOUSE 3BR NAIROBI` returns 3 formatted listings
- Verify `VALE 3BR WESTLANDS 120SQM` returns ML valuation
- Verify `HELP` returns full command menu

**USSD testing:**

- Use AT USSD simulator at sandbox.africastalking.com
- Walk through full search flow: city → type → bedrooms → budget → results
- Verify Redis session persists between menu hops
- Verify session expires correctly at 180 seconds
- Test edge cases: invalid input, session timeout, empty results

**Voice testing:**

- Use AT voice simulator to trigger inbound call
- Verify TTS reads listings correctly
- Verify digit capture works (press 1, 2, 3)
- Test outbound call trigger from payment webhook

**Airtime testing:**

- Trigger reward action in sandbox
- Verify airtime API call succeeds
- Verify disbursement logged in database

---

#### What Judges Will See From This Phase

- Live USSD demo: dial `*384*PROP#`, navigate to search, get real listings
  back from the property service database
- Live SMS demo: text `HOUSE 2BR NAIROBI` to shortcode, get 3 real listings
  back within seconds
- Live valuation via USSD: enter property details through menu,
  get AI-estimated value from the ML service
- Airtime reward triggered live and confirmed in AT dashboard
- Redis session state shown persisting between USSD menu hops
- Code showing webhook validation and error handling

---

#### Useful Commands

**Start channels service:**

```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/channels
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```

**Start ngrok tunnel:**

```bash
ngrok http 8006
```

**Test SMS webhook manually:**

```bash
curl -s -X POST http://localhost:8006/api/v1/channels/sms/inbound \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "from=%2B254700000001&to=SHORTCODE&text=HOUSE+2BR+NAIROBI&date=2026-04-10" \
  | python3 -m json.tool
```

**Test USSD webhook manually:**

```bash
# Initial dial
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=TEST123&phoneNumber=%2B254700000001&text=&serviceCode=*384*PROP%23"

# Select option 1 (search)
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sessionId=TEST123&phoneNumber=%2B254700000001&text=1&serviceCode=*384*PROP%23"
```

**Check Redis USSD sessions:**

```bash
docker exec afriprop_redis redis-cli keys "ussd:*"
docker exec afriprop_redis redis-cli get "ussd:TEST123"
```

**Check AT sandbox credentials in .env:**

```bash
grep AT_ .env
```

You're right on both counts. Let me be honest:

---

**What we built is backend only — middleware layer.**

We built the webhook handlers that AT will call. The channels service receives AT callbacks and responds correctly. But we have not:

1. **Logged into the AT dashboard** — no sandbox app configured
2. **Set up ngrok** — no public URL for AT to call back
3. **Configured callback URLs** in AT dashboard for SMS, USSD, Voice
4. **Tested with real AT simulator** — all our tests were direct curl calls simulating what AT would send
5. **Sent a real SMS** — the `send_sms()` calls in our handlers use sandbox credentials that haven't been validated end-to-end
6. **Tested on a real phone** — no actual USSD session on a real device

**What works right now:**
- The webhook handler logic is correct
- The USSD state machine works
- The SMS parser works
- The property and ML service calls work
- The AT XML voice responses are correctly formatted

**What needs to happen for real AT integration:**
- ngrok running and exposing port 8006
- AT sandbox dashboard configured with those ngrok URLs
- AT simulator used to fire real test webhooks
- Real phone number tested with sandbox

This is Step 7 and Step 9 from our plan — we skipped them to build all the code first, which is the right order. The code is ready. The AT configuration is next.


### ✅ Phase 4 — Completed (Backend Layer)

#### What Was Achieved

Phase 4 builds the channels service — a standalone FastAPI microservice on port
8006 that acts as the webhook receiver for all Africa's Talking callbacks. Every
inbound SMS, USSD session, and voice call from AT hits this service first, gets
processed, calls the property or ML service, and returns a formatted response.

The backend logic is fully built and tested. Full AT dashboard configuration and
real device testing are the next step (see Pending section below).

---

#### What Is Built

**Channels service (port 8006)** with four routers:

`POST /api/v1/channels/sms/inbound` — receives inbound SMS from AT, parses
the command, calls the property or ML service, and sends back a formatted
SMS response. Handles: SEARCH, HOUSE, VALE, LIST, RENT, HELP commands.

`POST /api/v1/channels/ussd` — handles the full USSD session state machine.
Redis stores session state between menu hops with a 175-second TTL. Six
complete flows: property search, my listings, pay rent, AI valuation,
affordable housing, and help. Returns `CON` to continue the session or
`END` to terminate it.

`POST /api/v1/channels/voice/inbound` — handles inbound voice calls.
Returns AT-compatible XML with `<GetDigits>` and `<Say>` tags. Detects
caller's country from phone prefix and returns listings for their city.
Three options: hear listings, get AI valuation instructions, connect to agent.

`POST /api/v1/channels/airtime/reward` — disburses airtime rewards
programmatically via AT Airtime API. Five reward triggers with defined
amounts: profile verified (KES 20), review submitted (KES 10), agent
3 transactions (KES 50), first USSD search (KES 5).

---

#### Services Built

`at_client.py` — initialises AT SDK once at startup, exposes `send_sms()`,
`send_sms_bulk()`, `send_airtime()` functions used across all routers.

`sms_parser.py` — parses natural language SMS commands into structured
search parameters. Handles city aliases (NBI→Nairobi, MSA→Mombasa),
property type aliases, bedroom extraction (2BR→2), and budget parsing.

`ussd_session.py` — Redis-backed session manager. `get_session()`,
`save_session()`, `update_session()`, `clear_session()` with automatic
175-second TTL expiry matching AT's 180-second session limit.

`property_client.py` — async HTTP client calling the property service
search endpoint. Formats results into 160-character SMS segments.

`ml_client.py` — async HTTP client calling the ML valuation and trend
endpoints. Formats AI valuation results for SMS and USSD screens.

---

#### Confirmed Working (curl tests)

All tests were direct curl calls simulating what AT sends to our webhook:

```
SMS HOUSE 2BR NAIROBI  → 2 real listings from DB, formatted for SMS     ✔
SMS HELP               → full command menu                               ✔
USSD text=""           → main menu (6 options)                          ✔
USSD text=1            → city selection menu                            ✔
USSD text=1*1          → property type menu                             ✔
USSD text=1*1*1*2      → budget entry prompt                            ✔
USSD text=1*1*1*2*50000→ END with real Nairobi listings from DB         ✔
USSD text=4*1*2*120    → END with KES 63,500 AI valuation from ML       ✔
Voice press 1          → AT XML with 2 listings read aloud              ✔
Voice initial call     → AT XML welcome menu                            ✔
```

---

#### Pending — AT Dashboard Configuration

The following steps complete the real AT integration and must be done
before the hackathon demo:

**1. ngrok setup:**
```bash
# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Expose channels service
ngrok http 8006
# Copy the HTTPS URL e.g. https://abc123.ngrok-free.app
```

**2. AT sandbox dashboard — set callback URLs:**
```
SMS callback:   https://YOUR_NGROK/api/v1/channels/sms/inbound
USSD callback:  https://YOUR_NGROK/api/v1/channels/ussd
Voice callback: https://YOUR_NGROK/api/v1/channels/voice/inbound
```

**3. Update .env:**
```
AT_USERNAME=sandbox
AT_API_KEY=your-real-sandbox-key
AT_SHORTCODE=your-shortcode
```

**4. Test with AT simulator:**
- Go to sandbox.africastalking.com
- Use SMS simulator: send `HOUSE 2BR NAIROBI` to your shortcode
- Use USSD simulator: dial `*384*PROP#` and navigate full search flow
- Use voice simulator: trigger inbound call and press digits

**5. Test on real device:**
- AT sandbox supports real phone testing with sandbox credentials
- Dial `*384*PROP#` from a registered sandbox number
- Send SMS to shortcode from registered sandbox number

---

#### Useful Commands

**Start channels service:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/channels
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```

**Start ngrok (run in separate terminal):**
```bash
ngrok http 8006
```

**Test SMS inbound manually:**
```bash
# Property search
curl -s -X POST http://localhost:8006/api/v1/channels/sms/inbound \
  -d "from=%2B254700000001&to=AFRIPROP&text=HOUSE+2BR+NAIROBI" \
  | python3 -m json.tool

# AI valuation via SMS
curl -s -X POST http://localhost:8006/api/v1/channels/sms/inbound \
  -d "from=%2B254700000001&to=AFRIPROP&text=VALE+2BR+WESTLANDS+80SQM" \
  | python3 -m json.tool

# Help menu
curl -s -X POST http://localhost:8006/api/v1/channels/sms/inbound \
  -d "from=%2B254700000001&to=AFRIPROP&text=HELP" \
  | python3 -m json.tool
```

**Test full USSD search flow manually:**
```bash
# Step 1: Initial dial
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST001&phoneNumber=%2B254700000001&text=&serviceCode=*384*PROP%23"

# Step 2: Select search (1)
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST001&phoneNumber=%2B254700000001&text=1&serviceCode=*384*PROP%23"

# Step 3: Select Nairobi (1)
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST001&phoneNumber=%2B254700000001&text=1*1&serviceCode=*384*PROP%23"

# Step 4: Select apartment (1)
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST001&phoneNumber=%2B254700000001&text=1*1*1&serviceCode=*384*PROP%23"

# Step 5: Select 2 bedrooms (2)
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST001&phoneNumber=%2B254700000001&text=1*1*1*2&serviceCode=*384*PROP%23"

# Step 6: Enter budget
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST001&phoneNumber=%2B254700000001&text=1*1*1*2*50000&serviceCode=*384*PROP%23"
```

**Test USSD AI valuation flow:**
```bash
curl -s -X POST http://localhost:8006/api/v1/channels/ussd \
  -d "sessionId=TEST002&phoneNumber=%2B254700000001&text=4*1*2*120&serviceCode=*384*PROP%23"
```

**Test voice IVR:**
```bash
# Initial call
curl -s -X POST http://localhost:8006/api/v1/channels/voice/inbound \
  -d "isActive=1&callerNumber=%2B254700000001&sessionId=VOICE001"

# Press 1 for listings
curl -s -X POST http://localhost:8006/api/v1/channels/voice/inbound \
  -d "isActive=1&callerNumber=%2B254700000001&sessionId=VOICE001&dtmfDigits=1"
```

**Check Redis USSD sessions:**
```bash
docker exec afriprop_redis redis-cli keys "ussd:*"
docker exec afriprop_redis redis-cli get "ussd:TEST001"
```

**Swagger docs:** `http://localhost:8006/docs`
```
