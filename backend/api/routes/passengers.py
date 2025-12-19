"""Passenger routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from core.models import Passenger
from core.schemas import PassengerResponse, PassengerCreate, PassengerUpdate
from core.redis import get_cache, set_cache, delete_cache, build_cache_key
import json

router = APIRouter()

PASSENGER_LIST_CACHE_KEY = "passengers:all"
PASSENGER_CACHE_KEY_TEMPLATE = "passenger:{passenger_id}"
FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE = "passengers:flight:{flight_id}"
PASSENGER_TTL = 1000


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
    cache_key = build_cache_key(FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE, flight_id=flight_id) if flight_id else PASSENGER_LIST_CACHE_KEY
    
    try:
        cached = get_cache(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve passengers from cache: {e}")
    
    query = db.query(Passenger)
    if flight_id:
        query = query.filter(Passenger.flight_id == flight_id)
    passengers = query.all()
    
    try:
        passengers_data = [PassengerResponse.model_validate(p).model_dump(mode='json') for p in passengers]
        set_cache(cache_key, json.dumps(passengers_data), ex=PASSENGER_TTL)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache passengers: {e}")
    
    return passengers


@router.get("/{passenger_id}", response_model=PassengerResponse)
def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Get a specific passenger by ID."""
    cache_key = build_cache_key(PASSENGER_CACHE_KEY_TEMPLATE, passenger_id=passenger_id)
    
    try:
        cached = get_cache(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to retrieve passenger {passenger_id} from cache: {e}")
    
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Passenger not found")
    
    try:
        passenger_data = PassengerResponse.model_validate(passenger).model_dump(mode='json')
        set_cache(cache_key, json.dumps(passenger_data), ex=PASSENGER_TTL)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to cache passenger {passenger_id}: {e}")
    
    return passenger


@router.post("/", response_model=PassengerResponse, status_code=status.HTTP_201_CREATED)
def create_passenger(
    passenger: PassengerCreate,
    db: Session = Depends(get_db)
):
    """Create a new passenger with data from PassengerCreate schema."""
    flight_id = passenger.flight_id
    seat_number = passenger.seat_number

    # Seat validation
    if not check_seat_availability(db, flight_id, seat_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seat {seat_number} is already taken on flight {flight_id}"
        )

    # Parent validation
    if passenger.parent_id:
        parent = db.query(Passenger).filter(Passenger.id == passenger.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent passenger {passenger.parent_id} not found"
            )
        if parent.flight_id != flight_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent and child must be on the same flight"
            )

    new_passenger = Passenger(**passenger.model_dump())
    
    db.add(new_passenger)
    db.commit()
    db.refresh(new_passenger)
    
    try:
        delete_cache(PASSENGER_LIST_CACHE_KEY)
        delete_cache(build_cache_key(FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE, flight_id=flight_id))
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

    update_data = passenger.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_passenger, field, value)

    db.commit()
    db.refresh(existing_passenger)
    
    try:
        delete_cache(PASSENGER_LIST_CACHE_KEY)
        delete_cache(build_cache_key(PASSENGER_CACHE_KEY_TEMPLATE, passenger_id=passenger_id))
        delete_cache(build_cache_key(FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE, flight_id=existing_passenger.flight_id))
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
        delete_cache(build_cache_key(PASSENGER_CACHE_KEY_TEMPLATE, passenger_id=passenger_id))
        delete_cache(build_cache_key(FLIGHT_PASSENGERS_CACHE_KEY_TEMPLATE, flight_id=flight_id))
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

    passenger_list = [p.__dict__.copy() for p in passengers]
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
        row.pop("_sa_instance_state", None)

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




