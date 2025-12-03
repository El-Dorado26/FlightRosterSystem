from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate
from core.database import get_db
from core import models

router = APIRouter()


@router.get("/", response_model=List[CabinCrewResponse])
async def list_cabin_crew(db: Session = Depends(get_db)):
    """
    Get all cabin crew members.
    
    Returns complete information including:
    - Attendant ID (unique system ID)
    - Personal info (name, age, gender, nationality, languages)
    - Attendant type (chief, regular, chef)
    - Recipes (for chefs: 2-4 dish types)
    - Vehicle restrictions (list of vehicle type IDs they can work on)
    """
    return db.query(models.CabinCrew).all()


@router.get("/{crew_id}", response_model=CabinCrewResponse)
async def get_cabin_crew(crew_id: int, db: Session = Depends(get_db)):
    """
    Get a specific cabin crew member by ID.
    
    Provides detailed information about one attendant including their
    type, languages, recipes (if chef), and vehicle restrictions.
    """
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")
    return crew


@router.post("/", response_model=CabinCrewResponse, status_code=201)
async def create_cabin_crew(crew: CabinCrewCreate, db: Session = Depends(get_db)):
    """
    Create a new cabin crew member.
    
    Attendant types:
    - chief: 1-4 per flight (senior attendants)
    - regular: 4-16 per flight (junior attendants)
    - chef: 0-2 per flight (cooks with 2-4 recipes each)
    
    Required fields:
    - name, age, gender, nationality, employee_id
    - attendant_type: must be 'chief', 'regular', or 'chef'
    - languages: list of known languages
    - recipes: required if attendant_type is 'chef' (2-4 dish types)
    - vehicle_restrictions: optional list of vehicle type IDs
    """
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
    return db_crew


@router.put("/{crew_id}", response_model=CabinCrewResponse)
async def update_cabin_crew(crew_id: int, crew: CabinCrewUpdate, db: Session = Depends(get_db)):
    """
    Update a cabin crew member's information.
    
    Can update: name, age, gender, nationality, attendant_type,
    languages, recipes, vehicle_restrictions, flight assignment.
    """
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
    return db_crew


@router.delete("/{crew_id}")
async def delete_cabin_crew(crew_id: int, db: Session = Depends(get_db)):
    """Delete a cabin crew member."""
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")
    
    db.delete(crew)
    db.commit()
    return {"detail": "Cabin crew member deleted successfully"}


@router.get("/type/{attendant_type}", response_model=List[CabinCrewResponse])
async def get_crew_by_type(attendant_type: str, db: Session = Depends(get_db)):
    """
    Get all cabin crew members of a specific type.
    
    Types: chief, regular, chef
    """
    valid_types = ["chief", "regular", "chef"]
    if attendant_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
        )
    
    return db.query(models.CabinCrew).filter(
        models.CabinCrew.attendant_type == attendant_type
    ).all()


@router.get("/vehicle/{vehicle_type_id}", response_model=List[CabinCrewResponse])
async def get_crew_by_vehicle(vehicle_type_id: int, db: Session = Depends(get_db)):
    """
    Get cabin crew members qualified for a specific vehicle type.
    
    Returns attendants who either have no vehicle restrictions or
    have the specified vehicle type in their allowed list.
    """
    all_crew = db.query(models.CabinCrew).all()
    
    qualified_crew = [
        crew for crew in all_crew
        if crew.vehicle_restrictions is None or 
           vehicle_type_id in crew.vehicle_restrictions
    ]
    
    return qualified_crew