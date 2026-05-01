Here's everything you need to bring the full platform back up:

**Step 1 — Navigate to project root and start Docker:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp
make up
```

Wait 30 seconds then verify all containers are healthy:
```bash
make ps
```

---

**Step 2 — Start all 5 services in separate terminals:**

**Terminal 1 — Gateway (port 8000):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/gateway
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Property service (port 8001):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/property
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Terminal 3 — ML service (port 8004):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/ml
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8004
```

**Terminal 4 — Channels service (port 8006):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/channels
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8006
```

**Terminal 5 — Finance service (port 8003):**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp/services/finance
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003
```

---

**Step 3 — Verify all services are alive (run in a 6th terminal):**
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
curl -s http://localhost:8001/health | python3 -m json.tool
curl -s http://localhost:8003/health | python3 -m json.tool
curl -s http://localhost:8004/health | python3 -m json.tool
curl -s http://localhost:8006/health | python3 -m json.tool
```

---

**Step 4 — Run the demo seed script:**
```bash
cd /mnt/d/DS_PROJECTS/AfriProp
python3 database/seeds/demo_seed.py
```
