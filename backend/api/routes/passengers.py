"""Passenger routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.models import Passenger
from core.schemas import PassengerResponse, PassengerCreate, PassengerUpdate
from core.redis import get_cache, set_cache, delete_cache
import json

router = APIRouter()

PASSENGER_LIST_CACHE_KEY = "passengers:all"
PASSENGER_CACHE_KEY_TEMPLATE = "passenger:{passenger_id}"
FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE = "passengers:flight:{flight_id}"
PASSENGER_TTL = 300


def _build_passenger_cache_key(passenger_id: int) -> str:
    return PASSENGER_CACHE_KEY_TEMPLATE.format(passenger_id=passenger_id)

def _build_flight_passengers_cache_key(flight_id: int) -> str:
    return FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE.format(flight_id=flight_id)


# Helper Functions

def check_seat_availability(db: Session, flight_id: int, seat_number: str) -> bool:
    """Ensure the seat is not already taken on the flight."""
    exists = db.query(Passenger).filter(
        Passenger.flight_id == flight_id,
        Passenger.seat_number == seat_number
    ).first()
    return exists is None

# CRUD Endpoints

@router.get("/", response_model=List[PassengerResponse])
def list_passengers(flight_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all passengers, optionally filtered by flight."""
    cache_key = _build_flight_passengers_cache_key(flight_id) if flight_id else PASSENGER_LIST_CACHE_KEY
    
    try:
        cached = get_cache(cache_key)
        if cached:
            print(f"[CACHE HIT] Retrieved passengers from Redis (flight_id={flight_id})")
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve passengers from cache: {e}")
    
    print(f"[CACHE MISS] Querying database for passengers (flight_id={flight_id})")
    query = db.query(Passenger)
    if flight_id:
        query = query.filter(Passenger.flight_id == flight_id)
    passengers = query.all()
    
    try:
        passengers_data = [PassengerResponse.model_validate(p).model_dump(mode='json') for p in passengers]
        set_cache(cache_key, json.dumps(passengers_data), ttl=PASSENGER_TTL)
        print(f"[CACHE SET] Stored {len(passengers)} passengers in Redis with TTL={PASSENGER_TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache passengers: {e}")
    
    return passengers


@router.get("/{passenger_id}", response_model=PassengerResponse)
def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Get a specific passenger by ID."""
    cache_key = _build_passenger_cache_key(passenger_id)
    
    try:
        cached = get_cache(cache_key)
        if cached:
            print(f"[CACHE HIT] Retrieved passenger {passenger_id} from Redis")
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve passenger {passenger_id} from cache: {e}")
    
    print(f"[CACHE MISS] Querying database for passenger {passenger_id}")
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passenger not found")
    
    try:
        passenger_data = PassengerResponse.model_validate(passenger).model_dump(mode='json')
        set_cache(cache_key, json.dumps(passenger_data), ttl=PASSENGER_TTL)
        print(f"[CACHE SET] Stored passenger {passenger_id} in Redis with TTL={PASSENGER_TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache passenger {passenger_id}: {e}")
    
    return passenger


@router.post("/", response_model=PassengerResponse, status_code=status.HTTP_201_CREATED)
def create_passenger(
    passenger: PassengerCreate,
    flight_id: int,
    seat_number: str,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Create a new passenger with optional parent-child booking."""
    # Seat validation
    if not check_seat_availability(db, flight_id, seat_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seat {seat_number} is already taken on flight {flight_id}"
        )

    # Parent validation
    if parent_id:
        parent = db.query(Passenger).filter(Passenger.id == parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent passenger {parent_id} not found"
            )
        if parent.flight_id != flight_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent and child must be on the same flight"
            )

    new_passenger = Passenger(
        name=passenger.name,
        email=passenger.email,
        phone=passenger.phone,
        passport_number=passenger.passport_number,
        flight_id=flight_id,
        seat_number=seat_number,
        parent_id=parent_id
    )
    db.add(new_passenger)
    db.commit()
    db.refresh(new_passenger)
    
    try:
        delete_cache(PASSENGER_LIST_CACHE_KEY)
        delete_cache(_build_flight_passengers_cache_key(flight_id))
    except Exception:
        pass
    
    return new_passenger


@router.put("/{passenger_id}", response_model=PassengerResponse)
def update_passenger(
    passenger_id: int,
    passenger: PassengerUpdate,
    seat_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update a passenger's details or seat."""
    existing_passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not existing_passenger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passenger not found")

    # Seat change validation
    if seat_number:
        if not check_seat_availability(db, existing_passenger.flight_id, seat_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seat {seat_number} is already taken on flight {existing_passenger.flight_id}"
            )
        existing_passenger.seat_number = seat_number

    # Update other fields
    for field, value in passenger.dict(exclude_unset=True).items():
        setattr(existing_passenger, field, value)

    db.commit()
    db.refresh(existing_passenger)
    
    try:
        delete_cache(PASSENGER_LIST_CACHE_KEY)
        delete_cache(_build_passenger_cache_key(passenger_id))
        delete_cache(_build_flight_passengers_cache_key(existing_passenger.flight_id))
    except Exception:
        pass
    
    return existing_passenger


@router.delete("/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Delete a passenger."""
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passenger not found")
    
    flight_id = passenger.flight_id
    db.delete(passenger)
    db.commit()
    
    try:
        delete_cache(PASSENGER_LIST_CACHE_KEY)
        delete_cache(_build_passenger_cache_key(passenger_id))
        delete_cache(_build_flight_passengers_cache_key(flight_id))
    except Exception:
        pass
    
    return

import csv
from io import StringIO
from fastapi.responses import JSONResponse, StreamingResponse



@router.get("/export/json", response_class=JSONResponse)
def export_passengers_json(flight_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Export passengers as JSON, optionally filtered by flight."""
    query = db.query(Passenger)
    if flight_id:
        query = query.filter(Passenger.flight_id == flight_id)
    passengers = query.all()

    # Convert to list of dicts
    passenger_list = [p.__dict__.copy() for p in passengers]
    # Remove SQLAlchemy internal key
    for p in passenger_list:
        p.pop("_sa_instance_state", None)

    return JSONResponse(content=passenger_list)


@router.get("/export/csv")
def export_passengers_csv(flight_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Export passengers as CSV, optionally filtered by flight."""
    query = db.query(Passenger)
    if flight_id:
        query = query.filter(Passenger.flight_id == flight_id)
    passengers = query.all()

    output = StringIO()
    writer = None

    for p in passengers:
        row = p.__dict__.copy()
        row.pop("_sa_instance_state", None)  # remove internal SQLAlchemy field

        if writer is None:
            writer = csv.DictWriter(output, fieldnames=row.keys())
            writer.writeheader()
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=passengers.csv"}
    )
#####################################################################




