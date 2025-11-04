"""Flight Info routes with full API specification compliance."""
from fastapi import APIRouter, HTTPException
from typing import List

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

# Mock in-memory databases
flights_db: List[dict] = []
airlines_db: List[dict] = []
airports_db: List[dict] = []
vehicles_db: List[dict] = []
shared_flights_db: List[dict] = []
connecting_flights_db: List[dict] = []


# ============ Airline Endpoints ============

@router.get("/airlines", response_model=List[AirlineResponse])
async def list_airlines():
    """Get all airlines."""
    return airlines_db


@router.post("/airlines", response_model=AirlineResponse)
async def create_airline(airline: AirlineCreate):
    """Create a new airline."""
    new_airline = airline.model_dump()
    new_airline["id"] = len(airlines_db) + 1
    airlines_db.append(new_airline)
    return new_airline


# ============ Airport Location Endpoints ============

@router.get("/airports", response_model=List[AirportLocationResponse])
async def list_airports():
    """Get all airport locations."""
    return airports_db


@router.post("/airports", response_model=AirportLocationResponse)
async def create_airport(airport: AirportLocationCreate):
    """Create a new airport location (AAA format code)."""
    # Validate airport code format (AAA)
    if len(airport.airport_code) != 3 or not airport.airport_code.isupper():
        raise HTTPException(status_code=400, detail="Airport code must be 3 uppercase letters (AAA format)")
    
    new_airport = airport.model_dump()
    new_airport["id"] = len(airports_db) + 1
    airports_db.append(new_airport)
    return new_airport


# ============ Vehicle Type Endpoints ============

@router.get("/vehicles", response_model=List[VehicleTypeResponse])
async def list_vehicle_types():
    """Get all vehicle types (must have at least 3 different aircraft types)."""
    return vehicles_db


@router.post("/vehicles", response_model=VehicleTypeResponse)
async def create_vehicle_type(vehicle: VehicleTypeCreate):
    """Create a new vehicle type."""
    new_vehicle = vehicle.model_dump()
    new_vehicle["id"] = len(vehicles_db) + 1
    vehicles_db.append(new_vehicle)
    return new_vehicle


# ============ Flight Endpoints ============

@router.get("/", response_model=List[FlightInfoResponse])
async def list_flights():
    """Get all flights (AANNNN format flight numbers, with duration and distance)."""
    return flights_db


@router.get("/{flight_id}", response_model=FlightInfoResponse)
async def get_flight(flight_id: int):
    """Get a specific flight by ID with source/destination airport info and vehicle details."""
    for flight in flights_db:
        if flight.get("id") == flight_id:
            return flight
    raise HTTPException(status_code=404, detail="Flight not found")


@router.post("/", response_model=FlightInfoResponse)
async def create_flight(flight: FlightInfoCreate):
    """Create a new flight (AANNNN format, with airline, airports, vehicle type, duration, distance)."""
    # Validate flight number format (AANNNN)
    fn = flight.flight_number
    if len(fn) != 6 or not fn[:2].isalpha() or not fn[2:].isdigit():
        raise HTTPException(status_code=400, detail="Flight number must be in AANNNN format (e.g., AA1234)")
    
    new_flight = flight.model_dump()
    new_flight["id"] = len(flights_db) + 1
    flights_db.append(new_flight)
    return new_flight


@router.put("/{flight_id}", response_model=FlightInfoResponse)
async def update_flight(flight_id: int, flight: FlightInfoUpdate):
    """Update a flight's status, duration, or distance."""
    for i, f in enumerate(flights_db):
        if f.get("id") == flight_id:
            updates = flight.model_dump(exclude_unset=True)
            flights_db[i].update(updates)
            return flights_db[i]
    raise HTTPException(status_code=404, detail="Flight not found")


@router.delete("/{flight_id}")
async def delete_flight(flight_id: int):
    """Delete a flight."""
    for i, f in enumerate(flights_db):
        if f.get("id") == flight_id:
            flights_db.pop(i)
            return {"message": "Flight deleted"}
    raise HTTPException(status_code=404, detail="Flight not found")


# ============ Shared Flight Endpoints ============

@router.get("/{flight_id}/shared", response_model=SharedFlightResponse)
async def get_shared_flight(flight_id: int):
    """Get shared flight info if this flight is shared with another airline."""
    for shared in shared_flights_db:
        if shared.get("primary_flight_id") == flight_id:
            return shared
    raise HTTPException(status_code=404, detail="This flight is not a shared flight")


@router.post("/{flight_id}/shared", response_model=SharedFlightResponse)
async def create_shared_flight(flight_id: int, shared: SharedFlightCreate):
    """Create shared flight info (airlines can share flights, e.g., codeshare)."""
    # Validate secondary flight number format
    fn = shared.secondary_flight_number
    if len(fn) != 6 or not fn[:2].isalpha() or not fn[2:].isdigit():
        raise HTTPException(status_code=400, detail="Flight number must be in AANNNN format")
    
    new_shared = shared.model_dump()
    new_shared["id"] = len(shared_flights_db) + 1
    shared_flights_db.append(new_shared)
    return new_shared


# ============ Connecting Flight Endpoints ============

@router.get("/{flight_id}/connecting", response_model=ConnectingFlightResponse)
async def get_connecting_flight(flight_id: int):
    """Get connecting flight info (only for shared flights)."""
    for conn in connecting_flights_db:
        if conn.get("flight_id") == flight_id:
            return conn
    raise HTTPException(status_code=404, detail="No connecting flight for this flight")


@router.post("/{flight_id}/connecting", response_model=ConnectingFlightResponse)
async def create_connecting_flight(flight_id: int, connecting: ConnectingFlightCreate):
    """Add connecting flight information (shared flights only)."""
    # Validate flight number format
    fn = connecting.connecting_flight_number
    if len(fn) != 6 or not fn[:2].isalpha() or not fn[2:].isdigit():
        raise HTTPException(status_code=400, detail="Flight number must be in AANNNN format")
    
    new_connecting = connecting.model_dump()
    new_connecting["id"] = len(connecting_flights_db) + 1
    connecting_flights_db.append(new_connecting)
    return new_connecting
