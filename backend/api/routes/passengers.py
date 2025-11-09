"""Passenger routes."""
from fastapi import APIRouter
from typing import List

from core.schemas import PassengerResponse, PassengerCreate, PassengerUpdate

router = APIRouter()

# Placeholder for mock data (will be replaced with DB queries)
passengers_db: List[dict] = []

@router.get("/", response_model=List[PassengerResponse])
async def list_passengers():
    """Get all passengers."""
    pass

@router.get("/{passenger_id}", response_model=PassengerResponse)
async def get_passenger(passenger_id: int):
    """Get a specific passenger by ID."""
    pass

@router.post("/", response_model=PassengerResponse)
async def create_passenger(passenger: PassengerCreate):
    """Create a new passenger."""
    pass

@router.put("/{passenger_id}", response_model=PassengerResponse)
async def update_passenger(passenger_id: int, passenger: PassengerUpdate):
    """Update a passenger."""
    pass

@router.delete("/{passenger_id}")
async def delete_passenger(passenger_id: int):
    """Delete a passenger."""
    pass
