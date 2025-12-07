from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate
from core.database import get_db
from core import models
import csv
from fastapi.responses import JSONResponse, StreamingResponse
from io import StringIO

router = APIRouter()

# Redis imports
from core.redis import redis_get, redis_set


# ============================
# GET ALL CABIN CREW (WITH REDIS CACHE)
# ============================
@router.get("/", response_model=List[CabinCrewResponse])
async def list_cabin_crew(db: Session = Depends(get_db)):
    cache_key = "cabin_crew_all"

    # Try cache first
    cached_data = redis_get(cache_key)
    if cached_data:
        return cached_data

    # If no cache, pull from DB
    data = db.query(models.CabinCrew).all()

    # Save data to cache
    redis_set(cache_key, data)

    return data


# ============================
# GET ONE CABIN CREW MEMBER
# ============================
@router.get("/{crew_id}", response_model=CabinCrewResponse)
async def get_cabin_crew(crew_id: int, db: Session = Depends(get_db)):
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")
    return crew


# ============================
# CREATE CABIN CREW MEMBER
# ============================
@router.post("/", response_model=CabinCrewResponse, status_code=201)
async def create_cabin_crew(crew: CabinCrewCreate, db: Session = Depends(get_db)):
    valid_types = ["chief", "regular", "chef"]
    if crew.attendant_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attendant_type. Must be one of: {', '.join(valid_types)}"
        )

    if crew.attendant_type == "chef":
        if not crew.recipes or len(crew.recipes) < 2 or len(crew.recipes) > 4:
            raise HTTPException(
                status_code=400,
                detail="Chefs must have 2-4 dish recipes"
            )

    existing = db.query(models.CabinCrew).filter(
        models.CabinCrew.employee_id == crew.employee_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    db_crew = models.CabinCrew(**crew.model_dump())
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)

    # Invalidate cache
    redis_set("cabin_crew_all", None)

    return db_crew


# ============================
# UPDATE CABIN CREW MEMBER
# ============================
@router.put("/{crew_id}", response_model=CabinCrewResponse)
async def update_cabin_crew(crew_id: int, crew: CabinCrewUpdate, db: Session = Depends(get_db)):
    db_crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not db_crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")

    update_data = crew.model_dump(exclude_unset=True)

    if "attendant_type" in update_data:
        valid_types = ["chief", "regular", "chef"]
        if update_data["attendant_type"] not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid attendant_type. Must be one of: {', '.join(valid_types)}"
            )

    if update_data.get("attendant_type") == "chef" or (db_crew.attendant_type == "chef" and "recipes" in update_data):
        recipes = update_data.get("recipes", db_crew.recipes)
        if not recipes or len(recipes) < 2 or len(recipes) > 4:
            raise HTTPException(
                status_code=400,
                detail="Chefs must have 2-4 dish recipes"
            )

    for key, value in update_data.items():
        setattr(db_crew, key, value)

    db.commit()
    db.refresh(db_crew)

    # Invalidate cache
    redis_set("cabin_crew_all", None)

    return db_crew


# ============================
# DELETE CABIN CREW MEMBER
# ============================
@router.delete("/{crew_id}")
async def delete_cabin_crew(crew_id: int, db: Session = Depends(get_db)):
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")

    db.delete(crew)
    db.commit()

    # Invalidate cache
    redis_set("cabin_crew_all", None)

    return {"detail": "Cabin crew member deleted successfully"}


# ============================
# GET CREW BY TYPE
# ============================
@router.get("/type/{attendant_type}", response_model=List[CabinCrewResponse])
async def get_crew_by_type(attendant_type: str, db: Session = Depends(get_db)):
    valid_types = ["chief", "regular", "chef"]
    if attendant_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
        )

    crew = db.query(models.CabinCrew).filter(models.CabinCrew.attendant_type == attendant_type).all()
    return crew
