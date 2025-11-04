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
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Vehicle Type Schemas ============

class VehicleTypeBase(BaseModel):
    aircraft_name: str
    aircraft_code: str
    total_seats: int
    seating_plan: Dict[str, int]
    max_crew: int
    max_passengers: int


class VehicleTypeCreate(VehicleTypeBase):
    pass


class VehicleTypeResponse(VehicleTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Menu Schemas ============

class MenuBase(BaseModel):
    vehicle_type_id: int
    menu_items: List[Dict[str, Any]]


class MenuCreate(MenuBase):
    pass


class MenuResponse(MenuBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Airline Schemas ============

class AirlineBase(BaseModel):
    airline_code: str = Field(..., max_length=2)
    airline_name: str
    country: str


class AirlineCreate(AirlineBase):
    pass


class AirlineResponse(AirlineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Pilot Language Schemas ============

class PilotLanguageBase(BaseModel):
    language: str


class PilotLanguageResponse(PilotLanguageBase):
    id: int
    pilot_id: int

    class Config:
        from_attributes = True


# ============ Flight Crew (Pilot) Schemas ============

class FlightCrewBase(BaseModel):
    name: str
    age: int
    gender: str
    nationality: str
    employee_id: str
    role: str
    license_number: str
    seniority_level: str
    max_allowed_distance_km: float
    vehicle_type_restriction_id: Optional[int] = None
    hours_flown: int = 0


class FlightCrewCreate(FlightCrewBase):
    languages: List[str] = []


class FlightCrewUpdate(BaseModel):
    hours_flown: Optional[int] = None
    role: Optional[str] = None
    seniority_level: Optional[str] = None
    max_allowed_distance_km: Optional[float] = None


class FlightCrewResponse(FlightCrewBase):
    id: int
    flight_id: Optional[int] = None
    created_at: datetime
    languages: List[PilotLanguageResponse] = []

    class Config:
        from_attributes = True


# ============ Flight Info Schemas ============

class FlightInfoBase(BaseModel):
    flight_number: str = Field(..., max_length=6)
    airline_id: int
    departure_time: datetime
    flight_duration_minutes: int
    flight_distance_km: float
    departure_airport_id: int
    arrival_airport_id: int
    vehicle_type_id: int
    status: str = "scheduled"


class FlightInfoCreate(FlightInfoBase):
    pass


class FlightInfoUpdate(BaseModel):
    status: Optional[str] = None
    flight_duration_minutes: Optional[int] = None
    flight_distance_km: Optional[float] = None


class FlightInfoResponse(FlightInfoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    airline: Optional[AirlineResponse] = None
    departure_airport: Optional[AirportLocationResponse] = None
    arrival_airport: Optional[AirportLocationResponse] = None
    vehicle_type: Optional[VehicleTypeResponse] = None

    class Config:
        from_attributes = True


# ============ Shared Flight Schemas ============

class SharedFlightBase(BaseModel):
    primary_flight_id: int
    primary_airline_id: int
    secondary_airline_id: int
    secondary_flight_number: str = Field(..., max_length=6)


class SharedFlightCreate(SharedFlightBase):
    pass


class SharedFlightResponse(SharedFlightBase):
    id: int
    created_at: datetime
    primary_airline: Optional[AirlineResponse] = None
    secondary_airline: Optional[AirlineResponse] = None

    class Config:
        from_attributes = True


# ============ Connecting Flight Schemas ============

class ConnectingFlightBase(BaseModel):
    flight_id: int
    shared_flight_id: int
    connecting_flight_number: str = Field(..., max_length=6)
    connecting_airline_id: int


class ConnectingFlightCreate(ConnectingFlightBase):
    pass


class ConnectingFlightResponse(ConnectingFlightBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Cabin Crew Schemas ============

class CabinCrewBase(BaseModel):
    name: str
    employee_id: str
    role: str
    certifications: str = ""


class CabinCrewCreate(CabinCrewBase):
    pass


class CabinCrewUpdate(BaseModel):
    certifications: Optional[str] = None
    role: Optional[str] = None


class CabinCrewResponse(CabinCrewBase):
    id: int
    flight_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Passenger Schemas ============

class PassengerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    passport_number: str


class PassengerCreate(PassengerBase):
    pass


class PassengerUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class PassengerResponse(PassengerBase):
    id: int
    flight_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Flight Crew Schemas ============

class FlightCrewBase(BaseModel):
    """Base flight crew schema."""
    name: str
    employee_id: str
    role: str  # pilot, co-pilot
    license_number: str
    hours_flown: int = 0


class FlightCrewCreate(FlightCrewBase):
    """Schema for creating flight crew."""
    pass


class FlightCrewUpdate(BaseModel):
    """Schema for updating flight crew."""
    hours_flown: Optional[int] = None
    role: Optional[str] = None


class FlightCrewResponse(FlightCrewBase):
    """Schema for flight crew response."""
    id: int
    flight_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Cabin Crew Schemas ============

class CabinCrewBase(BaseModel):
    """Base cabin crew schema."""
    name: str
    employee_id: str
    role: str  # flight attendant, purser
    certifications: str = ""


class CabinCrewCreate(CabinCrewBase):
    """Schema for creating cabin crew."""
    pass


class CabinCrewUpdate(BaseModel):
    """Schema for updating cabin crew."""
    certifications: Optional[str] = None
    role: Optional[str] = None


class CabinCrewResponse(CabinCrewBase):
    """Schema for cabin crew response."""
    id: int
    flight_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Passenger Schemas ============

class PassengerBase(BaseModel):
    """Base passenger schema."""
    name: str
    email: str
    phone: Optional[str] = None
    passport_number: str


class PassengerCreate(PassengerBase):
    """Schema for creating a passenger."""
    pass


class PassengerUpdate(BaseModel):
    """Schema for updating a passenger."""
    email: Optional[str] = None
    phone: Optional[str] = None


class PassengerResponse(PassengerBase):
    """Schema for passenger response."""
    id: int
    flight_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True