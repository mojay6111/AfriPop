from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import sms_inbound, ussd, voice, airtime
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"AfriProp Channels Service starting — ENV: {settings.ENV}")
    print(f"AT Username: {settings.AT_USERNAME}")
    print(f"Property service: {settings.PROPERTY_SERVICE_URL}")
    print(f"ML service: {settings.ML_SERVICE_URL}")
    yield
    print("AfriProp Channels Service shutting down")


app = FastAPI(
    title="AfriProp Channels Service",
    description="SMS, USSD, Voice and Airtime integration via Africa's Talking",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sms_inbound.router, prefix="/api/v1/channels", tags=["sms"])
app.include_router(ussd.router,        prefix="/api/v1/channels", tags=["ussd"])
app.include_router(voice.router,       prefix="/api/v1/channels", tags=["voice"])
app.include_router(airtime.router,     prefix="/api/v1/channels", tags=["airtime"])


@app.get("/health", tags=["health"])
async def health():
    return {
        "status":   "ok",
        "service":  "channels",
        "version":  "1.0.0",
        "channels": ["sms", "ussd", "voice", "airtime"],
    }
