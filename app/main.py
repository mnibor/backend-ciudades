"""Application entry point: lifespan, health check and router wiring."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import cities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cities")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")
    yield


app = FastAPI(
    title="Cities API",
    version="1.0.0",
    description=(
        "A minimal FastAPI demo exposing a full CRUD (create, list, read, "
        "update, delete) over a single `cities` table backed by PostgreSQL. "
        "It is intentionally small so the whole stack can be demonstrated "
        "end to end in a short video."
    ),
    lifespan=lifespan,
)

app.include_router(cities.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Cities API", "docs": "/docs"}
