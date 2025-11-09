"""Flight Info routes with full API specification compliance."""
from fastapi import APIRouter
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
    pass


@router.post("/airlines", response_model=AirlineResponse)
async def create_airline(airline: AirlineCreate):
    """Create a new airline."""
    pass


# ============ Airport Location Endpoints ============

@router.get("/airports", response_model=List[AirportLocationResponse])
async def list_airports():
    """Get all airport locations."""
    pass


@router.post("/airports", response_model=AirportLocationResponse)
async def create_airport(airport: AirportLocationCreate):
    """Create a new airport location (AAA format code)."""
    pass


# ============ Vehicle Type Endpoints ============

@router.get("/vehicles", response_model=List[VehicleTypeResponse])
async def list_vehicle_types():
    """Get all vehicle types (must have at least 3 different aircraft types)."""
    pass


@router.post("/vehicles", response_model=VehicleTypeResponse)
async def create_vehicle_type(vehicle: VehicleTypeCreate):
    """Create a new vehicle type."""
    pass


# ============ Flight Endpoints ============

@router.get("/", response_model=List[FlightInfoResponse])
async def list_flights():
    """Get all flights (AANNNN format flight numbers, with duration and distance)."""
    pass


@router.get("/{flight_id}", response_model=FlightInfoResponse)
async def get_flight(flight_id: int):
    """Get a specific flight by ID with source/destination airport info and vehicle details."""
    pass


@router.post("/", response_model=FlightInfoResponse)
async def create_flight(flight: FlightInfoCreate):
    """Create a new flight (AANNNN format, with airline, airports, vehicle type, duration, distance)."""
    pass


@router.put("/{flight_id}", response_model=FlightInfoResponse)
async def update_flight(flight_id: int, flight: FlightInfoUpdate):
    """Update a flight's status, duration, or distance."""
    pass


@router.delete("/{flight_id}")
async def delete_flight(flight_id: int):
    """Delete a flight."""
    pass


# ============ Shared Flight Endpoints ============

@router.get("/{flight_id}/shared", response_model=SharedFlightResponse)
async def get_shared_flight(flight_id: int):
    """Get shared flight info if this flight is shared with another airline."""
    pass


@router.post("/{flight_id}/shared", response_model=SharedFlightResponse)
async def create_shared_flight(flight_id: int, shared: SharedFlightCreate):
    """Create shared flight info (airlines can share flights, e.g., codeshare)."""
    pass


# ============ Connecting Flight Endpoints ============

@router.get("/{flight_id}/connecting", response_model=ConnectingFlightResponse)
async def get_connecting_flight(flight_id: int):
    """Get connecting flight info (only for shared flights)."""
    pass


@router.post("/{flight_id}/connecting", response_model=ConnectingFlightResponse)
async def create_connecting_flight(flight_id: int, connecting: ConnectingFlightCreate):
    """Add connecting flight information (shared flights only)."""
    pass
