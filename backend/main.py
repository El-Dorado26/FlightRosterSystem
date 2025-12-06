import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from core.redis import redis
from api.routes.cabin_crew import router as cabin_router
from api.routes.flight_crew import router as flight_crew_router
from api.routes.flights import router as flights_router
from api.routes.passengers import router as passengers_router
from api.routes.auth import router as auth_router
from core.database import init_database

#backend diagnostics
def setup_logging():
    """Configure logging for the Flight Roster System."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    app_logger = logging.getLogger("flight_roster")
    app_logger.setLevel(logging.INFO)

    print(f"Logging configured with level: {log_level}")

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI): #Things to do before and after starting the backend
    logger.info("Starting Flight Roster System API...")
    await run_in_threadpool(init_database) #Connect to the database
    logger.info("Database initialized successfully!")

    try:
        redis.set("app_startup", "true")
        logger.info("Redis connection established successfully!")
    except Exception as e:
        logger.warning(f"Redis connection warning: {e}")
    
    logger.info("Flight Roster System API is ready to serve requests!")
    yield
    logger.info("Shutting down Flight Roster System API...")

app = FastAPI(
    title="Flight Roster System API",
    description="Backend API for managing flights, crews, and passengers",
    version="1.0.0",
    lifespan=lifespan
)
#Frontend (ReactJS) to talk to with the Backend (FastAPI).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Connected each API to the main backend.
# Once all endpoints are complete, these routers will be pluged directly into the main backend.
#Endpoints for each API: a specific URL that performs one action in the API.
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(flights_router, prefix="/flight-info", tags=["Flights"])
app.include_router(flight_crew_router, prefix="/flight-crew", tags=["Flight Crew"])
app.include_router(cabin_router, prefix="/cabin-crew", tags=["Cabin Crew"])
app.include_router(passengers_router, prefix="/passenger", tags=["Passengers"])

@app.get("/")
async def root():
    return {"message": "Welcome to Flight Roster System API", "version": "1.0.0"}

# Redis health check endpoint
@app.get("/redis-health")
async def redis_health():
    """Check Redis connection status."""
    try:
        redis.set("health_check", "ok")
        value = redis.get("health_check")
        return {
            "status": "healthy",
            "redis": "connected",
            "test_value": value
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "error": str(e)
        }
    
# check if the backend running
@app.get("/health")
async def health():
    return {"status": "healthy"}
#Starts the server 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
