from fastapi import APIRouter
from typing import List

from core.schemas import (
    FlightCrewResponse,
    FlightCrewCreate,
    FlightCrewUpdate,
    PilotLanguageResponse,
)

router = APIRouter()

flight_crew_db: List[dict] = []
pilot_languages_db: List[dict] = []


@router.get("/", response_model=List[FlightCrewResponse])
async def list_flight_crew():
    """Get all flight crew members."""
    pass


@router.get("/{crew_id}", response_model=FlightCrewResponse)
async def get_flight_crew(crew_id: int):
    """Get a specific flight crew member by ID."""
    pass


@router.post("/", response_model=FlightCrewResponse)
async def create_flight_crew(crew: FlightCrewCreate):
    """Create a new flight crew member."""
    pass


@router.put("/{crew_id}", response_model=FlightCrewResponse)
async def update_flight_crew(crew_id: int, crew: FlightCrewUpdate):
    """Update a flight crew member."""
    pass


@router.delete("/{crew_id}")
async def delete_flight_crew(crew_id: int):
    """Delete a flight crew member."""
    pass


@router.post("/{crew_id}/languages", response_model=PilotLanguageResponse)
async def add_language_to_pilot(crew_id: int, language: str):
    """Add a language to a pilot's profile."""
    pass


@router.delete("/{crew_id}/languages/{language}")
async def remove_language_from_pilot(crew_id: int, language: str):
    """Remove a language from a pilot's profile."""
    pass


@router.get("/{crew_id}/languages", response_model=List[PilotLanguageResponse])
async def get_pilot_languages(crew_id: int):
    """Get all languages spoken by a pilot."""
    pass


@router.get("/seniority/{level}")
async def get_pilots_by_seniority(level: str):
    """Get all pilots by seniority level (senior, junior, trainee)."""
    pass
