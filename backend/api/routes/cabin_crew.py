from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate
from core.database import get_db
from core import models
from core.redis import get_cache, set_cache, delete_cache, build_cache_key
import json
from fastapi.responses import JSONResponse, StreamingResponse
from io import StringIO

router = APIRouter()

CABIN_CREW_LIST_CACHE_KEY = "cabin_crew:all"
CABIN_CREW_CACHE_KEY_TEMPLATE = "cabin_crew:{crew_id}"
FLIGHT_CABIN_CREW_CACHE_KEY_TEMPLATE = "cabin_crew:flight:{flight_id}"
CABIN_CREW_TYPE_CACHE_KEY_TEMPLATE = "cabin_crew:type:{attendant_type}"
CABIN_CREW_TTL = 300


# ============================
# GET ALL CABIN CREW (WITH REDIS CACHE)
# ============================
@router.get("/", response_model=List[CabinCrewResponse])
async def list_cabin_crew(db: Session = Depends(get_db)):
    try:
        cached = get_cache(CABIN_CREW_LIST_CACHE_KEY)
        if cached:
            print(f"[CACHE HIT] Retrieved cabin crew list from Redis")
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve cabin crew from cache: {e}")
    
    print(f"[CACHE MISS] Querying database for cabin crew list")
    data = db.query(models.CabinCrew).all()
    
    try:
        crew_data = [CabinCrewResponse.model_validate(c).model_dump(mode='json') for c in data]
        set_cache(CABIN_CREW_LIST_CACHE_KEY, json.dumps(crew_data), ex=CABIN_CREW_TTL)
        print(f"[CACHE SET] Stored {len(data)} cabin crew in Redis with TTL={CABIN_CREW_TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache cabin crew: {e}")
    
    return data


# ============================
# GET ONE CABIN CREW MEMBER
# ============================
@router.get("/{crew_id}", response_model=CabinCrewResponse)
async def get_cabin_crew(crew_id: int, db: Session = Depends(get_db)):
    cache_key = build_cache_key(CABIN_CREW_CACHE_KEY_TEMPLATE, crew_id=crew_id)
    
    try:
        cached = get_cache(cache_key)
        if cached:
            print(f"[CACHE HIT] Retrieved cabin crew {crew_id} from Redis")
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve cabin crew {crew_id} from cache: {e}")
    
    print(f"[CACHE MISS] Querying database for cabin crew {crew_id}")
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")
    
    try:
        crew_data = CabinCrewResponse.model_validate(crew).model_dump(mode='json')
        set_cache(cache_key, json.dumps(crew_data), ex=CABIN_CREW_TTL)
        print(f"[CACHE SET] Stored cabin crew {crew_id} in Redis with TTL={CABIN_CREW_TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache cabin crew {crew_id}: {e}")
    
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

    try:
        delete_cache(CABIN_CREW_LIST_CACHE_KEY)
        if crew.attendant_type:
            delete_cache(build_cache_key(CABIN_CREW_TYPE_CACHE_KEY_TEMPLATE, attendant_type=crew.attendant_type))
    except Exception:
        pass

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

    try:
        delete_cache(CABIN_CREW_LIST_CACHE_KEY)
        delete_cache(build_cache_key(CABIN_CREW_CACHE_KEY_TEMPLATE, crew_id=crew_id))
        if db_crew.attendant_type:
            delete_cache(build_cache_key(CABIN_CREW_TYPE_CACHE_KEY_TEMPLATE, attendant_type=db_crew.attendant_type))
    except Exception:
        pass

    return db_crew


# ============================
# DELETE CABIN CREW MEMBER
# ============================
@router.delete("/{crew_id}")
async def delete_cabin_crew(crew_id: int, db: Session = Depends(get_db)):
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Cabin crew member not found")

    attendant_type = crew.attendant_type
    db.delete(crew)
    db.commit()

    try:
        delete_cache(CABIN_CREW_LIST_CACHE_KEY)
        delete_cache(build_cache_key(CABIN_CREW_CACHE_KEY_TEMPLATE, crew_id=crew_id))
        if attendant_type:
            delete_cache(build_cache_key(CABIN_CREW_TYPE_CACHE_KEY_TEMPLATE, attendant_type=attendant_type))
    except Exception:
        pass

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
    
    cache_key = build_cache_key(CABIN_CREW_TYPE_CACHE_KEY_TEMPLATE, attendant_type=attendant_type)
    
    try:
        cached = get_cache(cache_key)
        if cached:
            print(f"[CACHE HIT] Retrieved cabin crew by type '{attendant_type}' from Redis")
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve cabin crew by type from cache: {e}")
    
    print(f"[CACHE MISS] Querying database for cabin crew by type '{attendant_type}'")
    crew = db.query(models.CabinCrew).filter(models.CabinCrew.attendant_type == attendant_type).all()
    
    try:
        crew_data = [CabinCrewResponse.model_validate(c).model_dump(mode='json') for c in crew]
        set_cache(cache_key, json.dumps(crew_data), ex=CABIN_CREW_TTL)
        print(f"[CACHE SET] Stored {len(crew)} cabin crew by type '{attendant_type}' in Redis with TTL={CABIN_CREW_TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache cabin crew by type: {e}")
    
    return crew


@router.get("/flight/{flight_id}", response_model=List[CabinCrewResponse])
async def get_cabin_crew_by_flight(flight_id: int, db: Session = Depends(get_db)):
    """
    Get all cabin crew members assigned to a specific flight.
    
    Returns cabin crew members who are assigned to the given flight ID.
    """
    cache_key = build_cache_key(FLIGHT_CABIN_CREW_CACHE_KEY_TEMPLATE, flight_id=flight_id)
    
    try:
        cached = get_cache(cache_key)
        if cached:
            print(f"[CACHE HIT] Retrieved cabin crew for flight {flight_id} from Redis")
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve cabin crew for flight from cache: {e}")
    
    print(f"[CACHE MISS] Querying database for cabin crew for flight {flight_id}")
    flight = db.query(models.FlightInfo).filter(models.FlightInfo.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    cabin_crew = db.query(models.CabinCrew).filter(
        models.CabinCrew.flight_id == flight_id
    ).all()
    
    try:
        crew_data = [CabinCrewResponse.model_validate(c).model_dump(mode='json') for c in cabin_crew]
        set_cache(cache_key, json.dumps(crew_data), ex=CABIN_CREW_TTL)
        print(f"[CACHE SET] Stored {len(cabin_crew)} cabin crew for flight {flight_id} in Redis with TTL={CABIN_CREW_TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache cabin crew for flight: {e}")
    
    return cabin_crew
