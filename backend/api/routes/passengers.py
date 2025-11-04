"""Passenger routes."""
from fastapi import APIRouter, HTTPException
from typing import List

from core.schemas import PassengerResponse, PassengerCreate, PassengerUpdate

router = APIRouter()

# Placeholder for mock data (will be replaced with DB queries)
passengers_db: List[dict] = []

@router.get("/", response_model=List[PassengerResponse])
async def list_passengers():
    """Get all passengers."""
    return passengers_db

@router.get("/{passenger_id}", response_model=PassengerResponse)
async def get_passenger(passenger_id: int):
    """Get a specific passenger by ID."""
    for passenger in passengers_db:
        if passenger.get("id") == passenger_id:
            return passenger
    raise HTTPException(status_code=404, detail="Passenger not found")

@router.post("/", response_model=PassengerResponse)
async def create_passenger(passenger: PassengerCreate):
    """Create a new passenger."""
    new_passenger = passenger.model_dump()
    new_passenger["id"] = len(passengers_db) + 1
    passengers_db.append(new_passenger)
    return new_passenger

@router.put("/{passenger_id}", response_model=PassengerResponse)
async def update_passenger(passenger_id: int, passenger: PassengerUpdate):
    """Update a passenger."""
    for i, p in enumerate(passengers_db):
        if p.get("id") == passenger_id:
            updates = passenger.model_dump(exclude_unset=True)
            passengers_db[i].update(updates)
            return passengers_db[i]
    raise HTTPException(status_code=404, detail="Passenger not found")

@router.delete("/{passenger_id}")
async def delete_passenger(passenger_id: int):
    """Delete a passenger."""
    for i, p in enumerate(passengers_db):
        if p.get("id") == passenger_id:
            passengers_db.pop(i)
            return {"message": "Passenger deleted"}
    raise HTTPException(status_code=404, detail="Passenger not found")
