from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import auth, webhooks
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "gateway", "version": "1.0.0"}
