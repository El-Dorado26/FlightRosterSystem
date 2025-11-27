from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


# ============ Airport Location Schemas ============

class AirportLocationBase(BaseModel):
    airport_code: str = Field(..., max_length=3)
    airport_name: str
    city: str
    country: str


class AirportLocationCreate(AirportLocationBase):
    pass


class AirportLocationResponse(AirportLocationBase):
    id: int
    created_at: Optional[datetime]


# ============ Vehicle Type Schemas ============

class VehicleTypeBase(BaseModel):
    aircraft_name: str
    aircraft_code: str
    total_seats: int
    seating_plan: Dict[str, Any]
    max_crew: int
    max_passengers: int


class VehicleTypeCreate(VehicleTypeBase):
    pass


class VehicleTypeResponse(VehicleTypeBase):
    id: int
    created_at: Optional[datetime]


# ============ Menu Schemas ============

class MenuBase(BaseModel):
    vehicle_type_id: int
    menu_items: List[Dict[str, Any]]


class MenuCreate(MenuBase):
    pass


class MenuResponse(MenuBase):
    id: int
    created_at: Optional[datetime]


# ============ Airline Schemas ============

class AirlineBase(BaseModel):
    airline_code: str
    airline_name: str
    country: str


class AirlineCreate(AirlineBase):
    pass


class AirlineResponse(AirlineBase):
    id: int
    created_at: Optional[datetime]


# ============ Pilot Language Schemas ============

class PilotLanguageBase(BaseModel):
    pilot_id: int
    language: str


class PilotLanguageResponse(PilotLanguageBase):
    id: int


# ============ Flight Crew (Pilot) Schemas ============

class FlightCrewBase(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    employee_id: str
    role: Optional[str] = None
    license_number: str
    seniority_level: str
    max_allowed_distance_km: Optional[float] = None
    vehicle_type_restriction_id: Optional[int] = None
    hours_flown: Optional[int] = None
    languages: Optional[List[str]] = None


class FlightCrewCreate(FlightCrewBase):
    pass


class FlightCrewUpdate(BaseModel):
    seniority_level: Optional[str] = None
    hours_flown: Optional[int] = None
    role: Optional[str] = None
    max_allowed_distance_km: Optional[float] = None


class FlightCrewResponse(FlightCrewBase):
    id: int
    created_at: Optional[datetime]


# ============ Flight Crew Assignment Schemas ============

class FlightCrewAssignmentBase(BaseModel):
    flight_id: int
    crew_id: int
    role: Optional[str] = None


class FlightCrewAssignmentCreate(FlightCrewAssignmentBase):
    pass


class FlightCrewAssignmentResponse(FlightCrewAssignmentBase):
    id: int
    assigned_at: Optional[datetime]


# ============ Flight Information Schemas ============

class FlightInfoBase(BaseModel):
    flight_number: str
    airline_id: int
    departure_time: datetime
    flight_duration_minutes: int
    flight_distance_km: float
    departure_airport_id: int
    arrival_airport_id: int
    vehicle_type_id: int
    status: Optional[str] = "scheduled"


class FlightInfoCreate(FlightInfoBase):
    pass


class FlightInfoUpdate(BaseModel):
    flight_number: Optional[str] = None
    airline_id: Optional[int] = None
    departure_time: Optional[datetime] = None
    flight_duration_minutes: Optional[int] = None
    flight_distance_km: Optional[float] = None
    departure_airport_id: Optional[int] = None
    arrival_airport_id: Optional[int] = None
    vehicle_type_id: Optional[int] = None
    status: Optional[str] = None


class FlightInfoResponse(FlightInfoBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ============ Shared Flight Schemas ============

class SharedFlightBase(BaseModel):
    primary_flight_id: int
    primary_airline_id: int
    secondary_airline_id: int
    secondary_flight_number: str


class SharedFlightCreate(SharedFlightBase):
    pass


class SharedFlightResponse(SharedFlightBase):
    id: int
    created_at: Optional[datetime]


class ConnectingFlightBase(BaseModel):
    flight_id: int
    shared_flight_id: int
    connecting_flight_number: str
    connecting_airline_id: int


class ConnectingFlightCreate(ConnectingFlightBase):
    pass


class ConnectingFlightResponse(ConnectingFlightBase):
    id: int
    created_at: Optional[datetime]


# ============ Passenger Schemas ============
class PassengerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    flight_id: Optional[int] = None
    seat_number: Optional[str] = None
    parent_id: Optional[int] = None


class PassengerCreate(PassengerBase):
    pass


class PassengerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    seat_number: Optional[str] = None


class PassengerResponse(PassengerBase):
    id: int
    created_at: Optional[datetime]



# ============ Cabin Crew Schemas ============
class CabinCrewBase(BaseModel):
    name: str
    role: Optional[str] = None
    flight_id: Optional[int] = None


class CabinCrewCreate(CabinCrewBase):
    pass


class CabinCrewUpdate(BaseModel): 
    name: Optional[str] = None
    role: Optional[str] = None
    flight_id: Optional[int] = None


class CabinCrewResponse(CabinCrewBase):
    id: int
    created_at: Optional[datetime]


