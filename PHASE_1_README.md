## What is built by end of Phase 1

**Infrastructure layer — 4 Docker services running:**
- **PostgreSQL + PostGIS** — main database, stores users, properties, leases. PostGIS adds geo-spatial power for radius searches later.
- **MongoDB** — ready for ML feature storage and audit logs.
- **Redis** — ready for USSD session state and caching.
- **MinIO** — ready for property image and document storage.

**Gateway service — the brain of the platform:**
- Single entry point for all requests — every service, every channel (web, SMS, USSD) talks to this first.
- **`/health`** — tells you the service is alive.
- **`/api/v1/auth/register`** — creates a user, hashes their password, generates a 6-digit OTP, attempts to send it via Africa's Talking SMS.
- **`/api/v1/auth/verify-otp`** — confirms the OTP, marks the user as verified in the database.
- **`/api/v1/auth/login`** — checks credentials, returns a signed JWT token.
- **Swagger docs at `/docs`** — interactive API documentation, judges can test endpoints directly here.

---

## How it connects to the bigger picture

```
User (web/mobile/SMS)
        │
        ▼
  Gateway :8000          ← we are here
  ├── /auth/register     ← working
  ├── /auth/verify-otp   ← working  
  ├── /auth/login        ← working, returns JWT
  └── /webhooks/at/*     ← ready to receive AT callbacks
        │
        ▼
  PostgreSQL             ← users table live
  Redis                  ← standing by for USSD sessions
  MongoDB                ← standing by for ML data
  MinIO                  ← standing by for images
```

---

## Useful commands from here forward

**Start everything:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp
make up                          # start all Docker services
cd services/gateway && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Check all containers healthy:**
```bash
make ps
```

**Check what's in the users table:**
```bash
docker exec afriprop_postgres psql -U afriprop -d afriprop -c "SELECT id, phone, full_name, role, is_verified FROM users;"
```

**Test register:**
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","phone":"+254700000002","password":"test1234","role":"tenant"}' \
  | python3 -m json.tool
```

**Test login:**
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"+254700000001","password":"test1234"}' \
  | python3 -m json.tool
```

**Test a protected route (replace TOKEN):**
```bash
curl -s http://localhost:8000/api/v1/auth/ping \
  -H "Authorization: Bearer TOKEN" \
  | python3 -m json.tool
```

**View Swagger docs:**
```
http://localhost:8000/docs
```

**Git log to see progress:**
```bash
git log --oneline
```

---

## What's next — Phase 2

We build the **Property Service** — the core of the platform:
- Property listings CRUD
- Image upload to MinIO
- Geo-search (find properties within X km)
- Duplicate listing detection

That's what makes this a real estate platform rather than just an auth system. Ready?