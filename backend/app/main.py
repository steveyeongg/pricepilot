from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler
from app.routers import products, search, analytics, alerts, roi

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="PricePilot API",
    description="Dynamic Pricing & Competitor Intelligence for Malaysian Markets",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(search.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(roi.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "PricePilot"}
