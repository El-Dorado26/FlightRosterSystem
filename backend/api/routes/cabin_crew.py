"""Cabin Crew routes."""
from fastapi import APIRouter
from typing import List

from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate

router = APIRouter()

# Placeholder for mock data (will be replaced with DB queries)
cabin_crew_db: List[dict] = []

@router.get("/", response_model=List[CabinCrewResponse])
async def list_cabin_crew():
    """Get all cabin crew members."""
    pass

@router.get("/{crew_id}", response_model=CabinCrewResponse)
async def get_cabin_crew(crew_id: int):
    """Get a specific cabin crew member by ID."""
    pass

@router.post("/", response_model=CabinCrewResponse)
async def create_cabin_crew(crew: CabinCrewCreate):
    """Create a new cabin crew member."""
    pass

@router.put("/{crew_id}", response_model=CabinCrewUpdate)
async def update_cabin_crew(crew_id: int, crew: CabinCrewUpdate):
    """Update a cabin crew member."""
    pass

@router.delete("/{crew_id}")
async def delete_cabin_crew(crew_id: int):
    """Delete a cabin crew member."""
    pass
