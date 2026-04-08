from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.models import property
from app.routers import listings, images, verification
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"AfriProp Property Service starting — ENV: {settings.ENV}")
    yield
    print("AfriProp Property Service shutting down")


app = FastAPI(
    title="AfriProp Property Service",
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

app.include_router(listings.router, prefix="/api/v1/properties", tags=["listings"])
app.include_router(images.router, prefix="/api/v1/properties", tags=["images"])
app.include_router(verification.router, prefix="/api/v1/properties", tags=["verification"])


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "property", "version": "1.0.0"}
