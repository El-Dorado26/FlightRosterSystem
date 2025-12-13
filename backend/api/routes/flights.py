import re
from typing import List
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from core.database import get_db
from core import models
from core.schemas import (
    FlightInfoResponse,
    FlightInfoCreate,
    FlightInfoUpdate,
    AirlineResponse,
    AirlineCreate,
    AirportLocationResponse,
    AirportLocationCreate,
    VehicleTypeResponse,
    VehicleTypeCreate,
    SharedFlightResponse,
    SharedFlightCreate,
    ConnectingFlightResponse,
    ConnectingFlightCreate,
)

router = APIRouter()

#Regex
FLIGHT_NO_RE = re.compile(r"^[A-Z]{2}\d{4}$")   # AANNNN
AIRPORT_CODE_RE = re.compile(r"^[A-Z]{3}$")     # AAA


def _validate_flight_number(flight_number: str) -> None:
    if not FLIGHT_NO_RE.match(flight_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid flight number format. Expected AANNNN",
        )


def _validate_airport_code(code: str) -> None:
    if not AIRPORT_CODE_RE.match(code):
        raise HTTPException(
            status_code=400,
            detail="Invalid airport code format. Expected 3 letters (AAA).",
        )

#Airline Endpoints

"""Get all airlines."""
@router.get("/airlines", response_model=List[AirlineResponse])
async def list_airlines(db: Session = Depends(get_db)):
    return db.query(models.Airline).all()

"""Create a new airline."""
@router.post("/airlines", response_model=AirlineResponse, status_code=201)
async def create_airline(airline: AirlineCreate, db: Session = Depends(get_db)):
    code = airline.airline_code.upper()

    #Airline Code unique or not
    existing = (
        db.query(models.Airline)
        .filter(models.Airline.airline_code == code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Airline code already exists")

    data = airline.model_dump()
    data["airline_code"] = code
    db_airline = models.Airline(**data)
    db.add(db_airline)
    db.commit()
    db.refresh(db_airline)
    return db_airline

#Airport Location Endpoints

"""Get all airport locations."""
@router.get("/airports", response_model=List[AirportLocationResponse])
async def list_airports(db: Session = Depends(get_db)):
    return db.query(models.AirportLocation).all()

"""Create a new airport location (AAA format code)."""
@router.post("/airports", response_model=AirportLocationResponse, status_code=201)
async def create_airport(
    airport: AirportLocationCreate,
    db: Session = Depends(get_db),
):
    code = airport.airport_code.upper()
    _validate_airport_code(code)

    existing = (
        db.query(models.AirportLocation)
        .filter(models.AirportLocation.airport_code == code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Airport with this code already exists")

    data = airport.model_dump()
    data["airport_code"] = code
    db_airport = models.AirportLocation(**data)
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    return db_airport

#Vehicle Type Endpoints

@router.get("/vehicles", response_model=List[VehicleTypeResponse])
async def list_vehicle_types(db: Session = Depends(get_db)):
    """
    Get all vehicle types.

    Each type represents an aircraft with total seat count, seating_plan (JSON),
    max crew and max passengers.
    """
    return db.query(models.VehicleType).all()

"""Create a new vehicle type (aircraft)."""
@router.post("/vehicles", response_model=VehicleTypeResponse, status_code=201)
async def create_vehicle_type(
    vehicle: VehicleTypeCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(models.VehicleType)
        .filter(models.VehicleType.aircraft_code == vehicle.aircraft_code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle type with this code already exists")

    db_vehicle = models.VehicleType(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

#Flight Endpoints

@router.get("/", response_model=List[FlightInfoResponse])
async def list_flights(db: Session = Depends(get_db)):
    """
    Get all flights (lightweight - basic info only).

    Returns flights with:
    - Flight number (AANNNN)
    - Date/time, duration (minutes), distance (km)
    - Source/destination airports
    - Vehicle type with seating plan
    
    For full details including crew and passengers, use GET /{flight_id}
    """
    flights = db.query(models.FlightInfo).options(
        joinedload(models.FlightInfo.vehicle_type),
        joinedload(models.FlightInfo.airline),
        joinedload(models.FlightInfo.departure_airport),
        joinedload(models.FlightInfo.arrival_airport),
        joinedload(models.FlightInfo.shared_flight_info).joinedload(models.SharedFlight.primary_airline),
        joinedload(models.FlightInfo.shared_flight_info).joinedload(models.SharedFlight.secondary_airline),
        joinedload(models.FlightInfo.connecting_flight)
        # Note: Not loading flight_crew, cabin_crew, passengers for performance
        # Use GET /{flight_id} endpoint for full details
    ).all()
    return flights

"""Get a specific flight by ID with source/destination airport info and vehicle details."""
@router.get("/{flight_id}", response_model=FlightInfoResponse)
async def get_flight(flight_id: int, db: Session = Depends(get_db)):
    start_time = time.time()
    
    flight = (
        db.query(models.FlightInfo)
        .options(
            joinedload(models.FlightInfo.vehicle_type),
            joinedload(models.FlightInfo.airline),
            joinedload(models.FlightInfo.departure_airport),
            joinedload(models.FlightInfo.arrival_airport),
            joinedload(models.FlightInfo.shared_flight_info).joinedload(models.SharedFlight.primary_airline),
            joinedload(models.FlightInfo.shared_flight_info).joinedload(models.SharedFlight.secondary_airline),
            joinedload(models.FlightInfo.connecting_flight),
            joinedload(models.FlightInfo.flight_crew).joinedload(models.FlightCrew.languages),
            joinedload(models.FlightInfo.cabin_crew),
            joinedload(models.FlightInfo.passengers)
        )
        .filter(models.FlightInfo.id == flight_id)
        .first()
    )
    
    query_time = time.time() - start_time
    print(f"Flight query took {query_time:.3f}s")
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    # Manually fetch crew assignments if not loaded via relationships
    # This ensures we get crew that are assigned via FlightCrewAssignment table
    if not flight.flight_crew:
        crew_start = time.time()
        assigned_crew = (
            db.query(models.FlightCrew)
            .join(models.FlightCrewAssignment)
            .filter(models.FlightCrewAssignment.flight_id == flight_id)
            .options(joinedload(models.FlightCrew.languages))
            .all()
        )
        flight.flight_crew = assigned_crew
        print(f"Crew assignment query took {time.time() - crew_start:.3f}s")
    
    print(f"Total response time: {time.time() - start_time:.3f}s")
    return flight


@router.post("/", response_model=FlightInfoResponse, status_code=201)
async def create_flight(flight: FlightInfoCreate, db: Session = Depends(get_db)):
    """
    Create a new flight.

    Validates:
    - flight_number format AANNNN
    - Referenced airline, airports and vehicle type exist
    """
    number = flight.flight_number.upper()
    _validate_flight_number(number)

    # Foreign key
    if not db.query(models.Airline).filter(models.Airline.id == flight.airline_id).first():
        raise HTTPException(status_code=400, detail="airline_id does not exist")
    if not db.query(models.AirportLocation).filter(models.AirportLocation.id == flight.departure_airport_id).first():
        raise HTTPException(status_code=400, detail="departure_airport_id does not exist")
    if not db.query(models.AirportLocation).filter(models.AirportLocation.id == flight.arrival_airport_id).first():
        raise HTTPException(status_code=400, detail="arrival_airport_id does not exist")
    if not db.query(models.VehicleType).filter(models.VehicleType.id == flight.vehicle_type_id).first():
        raise HTTPException(status_code=400, detail="vehicle_type_id does not exist")

    data = flight.model_dump()
    data["flight_number"] = number

    db_flight = models.FlightInfo(**data)
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

"""Update a flight's status, duration, or distance."""
@router.put("/{flight_id}", response_model=FlightInfoResponse)
async def update_flight(
    flight_id: int,
    flight_update: FlightInfoUpdate,
    db: Session = Depends(get_db),
):
    flight = (
        db.query(models.FlightInfo)
        .filter(models.FlightInfo.id == flight_id)
        .first()
    )
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    update_data = flight_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(flight, key, value)

    db.commit()
    db.refresh(flight)
    return flight

"""Delete a flight (and cascade-linked shared/connecting info via DB FKs)."""
@router.delete("/{flight_id}")
async def delete_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = (
        db.query(models.FlightInfo)
        .filter(models.FlightInfo.id == flight_id)
        .first()
    )
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    db.delete(flight)
    db.commit()
    return {"detail": "Flight deleted"}

#Shared Flight Endpoints
"""Get shared flight info if this flight is shared with another airline."""
@router.get("/{flight_id}/shared", response_model=SharedFlightResponse)
async def get_shared_flight(flight_id: int, db: Session = Depends(get_db)):
    shared = (
        db.query(models.SharedFlight)
        .filter(models.SharedFlight.primary_flight_id == flight_id)
        .first()
    )
    if not shared:
        raise HTTPException(status_code=404, detail="Shared flight info not found")
    return shared


@router.post(
    "/{flight_id}/shared",
    response_model=SharedFlightResponse,
    status_code=201,
)
async def create_shared_flight(
    flight_id: int,
    shared: SharedFlightCreate,
    db: Session = Depends(get_db),
):
    """
    Create shared flight info (code-share).

    Path param flight_id, overrides body primary_flight_id.
    """
    #Is there a flight?
    flight = (
        db.query(models.FlightInfo)
        .filter(models.FlightInfo.id == flight_id)
        .first()
    )
    if not flight:
        raise HTTPException(status_code=404, detail="Primary flight not found")

    #Shared existing already?
    existing = (
        db.query(models.SharedFlight)
        .filter(models.SharedFlight.primary_flight_id == flight_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Shared flight already exists for this flight")

    # Is there airlines?
    if not db.query(models.Airline).filter(models.Airline.id == shared.primary_airline_id).first():
        raise HTTPException(status_code=400, detail="primary_airline_id does not exist")
    if not db.query(models.Airline).filter(models.Airline.id == shared.secondary_airline_id).first():
        raise HTTPException(status_code=400, detail="secondary_airline_id does not exist")

    _validate_flight_number(shared.secondary_flight_number.upper())

    data = shared.model_dump()
    data["primary_flight_id"] = flight_id
    data["secondary_flight_number"] = data["secondary_flight_number"].upper()

    db_shared = models.SharedFlight(**data)
    db.add(db_shared)
    db.commit()
    db.refresh(db_shared)
    return db_shared

#Connecting Flight Endpoints

"""Get connecting flight info (only for shared flights)."""
@router.get("/{flight_id}/connecting", response_model=ConnectingFlightResponse)
async def get_connecting_flight(flight_id: int, db: Session = Depends(get_db)):
    conn = (
        db.query(models.ConnectingFlight)
        .filter(models.ConnectingFlight.flight_id == flight_id)
        .first()
    )
    if not conn:
        raise HTTPException(status_code=404, detail="Connecting flight info not found")
    return conn


@router.post(
    "/{flight_id}/connecting",
    response_model=ConnectingFlightResponse,
    status_code=201,
)
async def create_connecting_flight(
    flight_id: int,
    connecting: ConnectingFlightCreate,
    db: Session = Depends(get_db),
):
    """
    Add connecting flight information (shared flights only).

    Path paramdaki flight_id, body’deki flight_id’yi override eder.
    """
    #Flight?
    flight = (
        db.query(models.FlightInfo)
        .filter(models.FlightInfo.id == flight_id)
        .first()
    )
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    #Shared flight?
    if not db.query(models.SharedFlight).filter(
        models.SharedFlight.id == connecting.shared_flight_id
    ).first():
        raise HTTPException(status_code=400, detail="shared_flight_id does not exist")

    #Connecting airline?
    if not db.query(models.Airline).filter(
        models.Airline.id == connecting.connecting_airline_id
    ).first():
        raise HTTPException(status_code=400, detail="connecting_airline_id does not exist")

    _validate_flight_number(connecting.connecting_flight_number.upper())

    #Is there connections already?
    existing = (
        db.query(models.ConnectingFlight)
        .filter(models.ConnectingFlight.flight_id == flight_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Connecting flight already exists for this flight")

    data = connecting.model_dump()
    data["flight_id"] = flight_id
    data["connecting_flight_number"] = data["connecting_flight_number"].upper()

    db_conn = models.ConnectingFlight(**data)
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)


#################################################################################################################################
from fastapi.responses import JSONResponse

@router.get("/flights/{flight_id}/roster/json", response_class=JSONResponse)
async def export_flight_roster_json(flight_id: int, db: Session = Depends(get_db)):
    """
    Export flight roster as JSON.
    """
    flight = db.query(models.FlightInfo).filter(models.FlightInfo.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    crew_members = db.query(models.FlightCrew).join(models.FlightCrewAssignment).filter(
        models.FlightCrewAssignment.flight_id == flight_id
    ).all()
    
    # Build export data
    export_data = {
        "flight_number": flight.flight_number,
        "date": str(flight.date),  # or datetime formatting
        "departure_airport": flight.departure_airport_id,
        "arrival_airport": flight.arrival_airport_id,
        "vehicle_type": flight.vehicle_type_id,
        "crew": [
            {
                "id": c.id,
                "name": c.name,
                "role": c.role,
                "seniority_level": c.seniority_level,
                "languages": [lang.language for lang in c.languages]
            }
            for c in crew_members
        ]
    }

    return JSONResponse(content=export_data)

import csv
from fastapi.responses import StreamingResponse
from io import StringIO

@router.get("/flights/{flight_id}/roster/csv")
async def export_flight_roster_csv(flight_id: int, db: Session = Depends(get_db)):
    """
    Export flight roster as CSV file.
    """
    # Get flight info
    flight = db.query(models.FlightInfo).filter(models.FlightInfo.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # Get crew members assigned
    crew_members = db.query(models.FlightCrew).join(models.FlightCrewAssignment).filter(
        models.FlightCrewAssignment.flight_id == flight_id
    ).all()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Crew ID", "Name", "Role", "Seniority Level", "Languages"
    ])
    
    # Write crew data
    for c in crew_members:
        writer.writerow([
            c.id,
            c.name,
            c.role,
            c.seniority_level,
            ", ".join([lang.language for lang in c.languages])
        ])
    
    output.seek(0)
    
    # Return as downloadable CSV
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=flight_{flight.flight_number}_roster.csv"}
    )
#########################################################################################################################

    
    return db_conn
