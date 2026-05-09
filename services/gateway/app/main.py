from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import auth, webhooks
from app.config import settings
from app.database import engine, Base
from app.models import user
import httpx

PROPERTY_URL = "http://localhost:8001"
ML_URL       = "http://localhost:8004"
FINANCE_URL  = "http://localhost:8003"
CHANNELS_URL = "http://localhost:8006"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"AfriProp Gateway starting — ENV: {settings.ENV}")
    yield
    print("AfriProp Gateway shutting down")


app = FastAPI(
    title="AfriProp API Gateway",
    description="Central gateway for the AfriProp property intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/v1/auth",     tags=["auth"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "gateway", "version": "1.0.0"}


async def proxy(request: Request, base_url: str) -> dict:
    path    = request.url.path
    query   = request.url.query
    url     = f"{base_url}{path}" + (f"?{query}" if query else "")
    method  = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    body    = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=method, url=url,
            headers=headers, content=body
        )
        try:
            return response.json()
        except Exception:
            return {"raw": response.text}


@app.api_route("/api/v1/properties/{path:path}",
               methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_property(path: str, request: Request):
    return await proxy(request, PROPERTY_URL)


@app.api_route("/api/v1/ml/{path:path}",
               methods=["GET","POST"])
async def proxy_ml(path: str, request: Request):
    return await proxy(request, ML_URL)


@app.api_route("/api/v1/finance/{path:path}",
               methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy_finance(path: str, request: Request):
    return await proxy(request, FINANCE_URL)


@app.api_route("/api/v1/channels/{path:path}",
               methods=["GET","POST"])
async def proxy_channels(path: str, request: Request):
    return await proxy(request, CHANNELS_URL)
