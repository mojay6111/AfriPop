from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.models import payment, investment
from app.routers import payments, mortgage, investment as investment_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"AfriProp Finance Service starting — ENV: {settings.ENV}")
    yield
    print("AfriProp Finance Service shutting down")


app = FastAPI(
    title="AfriProp Finance Service",
    description="Payments, rent ledger, mortgage calculator, fractional investment",
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

app.include_router(payments.router,         prefix="/api/v1/finance/payments",    tags=["payments"])
app.include_router(mortgage.router,         prefix="/api/v1/finance/mortgage",    tags=["mortgage"])
app.include_router(investment_router.router,prefix="/api/v1/finance/investments", tags=["investments"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "finance", "version": "1.0.0"}
