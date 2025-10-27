from fastapi import FastAPI
from services.cabin_crew import router as cabin_router
from services.flight_crew import router as flight_router
from services.flight_info import router as info_router
from services.passenger import router as passenger_router

app = FastAPI(title="Flight Roster System Backend", description="Main backend for Flight Roster System")

app.include_router(cabin_router, prefix="/cabin-crew", tags=["Cabin Crew"])
app.include_router(flight_router, prefix="/flight-crew", tags=["Flight Crew"])
app.include_router(info_router, prefix="/flight-info", tags=["Flight Info"])
app.include_router(passenger_router, prefix="/passenger", tags=["Passenger"])

@app.get("/")
async def root():
    return {"message": "Welcome to Main System Backend"}
