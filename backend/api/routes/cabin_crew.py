"""Cabin Crew routes."""
from fastapi import APIRouter, HTTPException
from typing import List

from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate

router = APIRouter()

# Placeholder for mock data (will be replaced with DB queries)
cabin_crew_db: List[dict] = []

@router.get("/", response_model=List[CabinCrewResponse])
async def list_cabin_crew():
    """Get all cabin crew members."""
    return cabin_crew_db

@router.get("/{crew_id}", response_model=CabinCrewResponse)
async def get_cabin_crew(crew_id: int):
    """Get a specific cabin crew member by ID."""
    for crew in cabin_crew_db:
        if crew.get("id") == crew_id:
            return crew
    raise HTTPException(status_code=404, detail="Cabin crew member not found")

@router.post("/", response_model=CabinCrewResponse)
async def create_cabin_crew(crew: CabinCrewCreate):
    """Create a new cabin crew member."""
    new_crew = crew.model_dump()
    new_crew["id"] = len(cabin_crew_db) + 1
    cabin_crew_db.append(new_crew)
    return new_crew

@router.put("/{crew_id}", response_model=CabinCrewUpdate)
async def update_cabin_crew(crew_id: int, crew: CabinCrewUpdate):
    """Update a cabin crew member."""
    for i, c in enumerate(cabin_crew_db):
        if c.get("id") == crew_id:
            updates = crew.model_dump(exclude_unset=True)
            cabin_crew_db[i].update(updates)
            return cabin_crew_db[i]
    raise HTTPException(status_code=404, detail="Cabin crew member not found")

@router.delete("/{crew_id}")
async def delete_cabin_crew(crew_id: int):
    """Delete a cabin crew member."""
    for i, c in enumerate(cabin_crew_db):
        if c.get("id") == crew_id:
            cabin_crew_db.pop(i)
            return {"message": "Cabin crew member deleted"}
    raise HTTPException(status_code=404, detail="Cabin crew member not found")
