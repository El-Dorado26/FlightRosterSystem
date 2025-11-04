from fastapi import APIRouter, HTTPException
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
    return flight_crew_db


@router.get("/{crew_id}", response_model=FlightCrewResponse)
async def get_flight_crew(crew_id: int):
    for crew in flight_crew_db:
        if crew.get("id") == crew_id:
            crew_copy = crew.copy()
            crew_copy["languages"] = [
                lang for lang in pilot_languages_db
                if lang.get("pilot_id") == crew_id
            ]
            return crew_copy
    raise HTTPException(status_code=404, detail="Flight crew member not found")


@router.post("/", response_model=FlightCrewResponse)
async def create_flight_crew(crew: FlightCrewCreate):
    if crew.seniority_level not in ["senior", "junior", "trainee"]:
        raise HTTPException(
            status_code=400,
            detail="Seniority level must be 'senior', 'junior', or 'trainee'"
        )

    new_crew = crew.model_dump(exclude={"languages"})
    new_crew["id"] = len(flight_crew_db) + 1
    flight_crew_db.append(new_crew)

    for language in crew.languages:
        lang_entry = {
            "id": len(pilot_languages_db) + 1,
            "pilot_id": new_crew["id"],
            "language": language
        }
        pilot_languages_db.append(lang_entry)

    new_crew["languages"] = [
        {"id": lang["id"], "pilot_id": lang["pilot_id"], "language": lang["language"]}
        for lang in pilot_languages_db
        if lang["pilot_id"] == new_crew["id"]
    ]
    return new_crew


@router.put("/{crew_id}", response_model=FlightCrewResponse)
async def update_flight_crew(crew_id: int, crew: FlightCrewUpdate):
    for i, c in enumerate(flight_crew_db):
        if c.get("id") == crew_id:
            if crew.seniority_level and crew.seniority_level not in ["senior", "junior", "trainee"]:
                raise HTTPException(
                    status_code=400,
                    detail="Seniority level must be 'senior', 'junior', or 'trainee'"
                )
            updates = crew.model_dump(exclude_unset=True)
            flight_crew_db[i].update(updates)
            updated_crew = flight_crew_db[i].copy()
            updated_crew["languages"] = [
                lang for lang in pilot_languages_db
                if lang.get("pilot_id") == crew_id
            ]
            return updated_crew
    raise HTTPException(status_code=404, detail="Flight crew member not found")


@router.delete("/{crew_id}")
async def delete_flight_crew(crew_id: int):
    global pilot_languages_db
    for i, c in enumerate(flight_crew_db):
        if c.get("id") == crew_id:
            flight_crew_db.pop(i)
            pilot_languages_db = [
                lang for lang in pilot_languages_db
                if lang.get("pilot_id") != crew_id
            ]
            return {"message": "Flight crew member deleted"}
    raise HTTPException(status_code=404, detail="Flight crew member not found")


@router.post("/{crew_id}/languages", response_model=PilotLanguageResponse)
async def add_language_to_pilot(crew_id: int, language: str):
    for crew in flight_crew_db:
        if crew.get("id") == crew_id:
            lang_entry = {
                "id": len(pilot_languages_db) + 1,
                "pilot_id": crew_id,
                "language": language
            }
            pilot_languages_db.append(lang_entry)
            return lang_entry
    raise HTTPException(status_code=404, detail="Flight crew member not found")


@router.get("/{crew_id}/languages", response_model=List[PilotLanguageResponse])
async def get_pilot_languages(crew_id: int):
    for crew in flight_crew_db:
        if crew.get("id") == crew_id:
            return [
                lang for lang in pilot_languages_db
                if lang.get("pilot_id") == crew_id
            ]
    raise HTTPException(status_code=404, detail="Flight crew member not found")


@router.get("/seniority/{level}")
async def get_pilots_by_seniority(level: str):
    if level not in ["senior", "junior", "trainee"]:
        raise HTTPException(
            status_code=400,
            detail="Seniority level must be 'senior', 'junior', or 'trainee'"
        )
    return [
        crew for crew in flight_crew_db
        if crew.get("seniority_level") == level
    ]
