from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from pydantic import BaseModel, Field, field_validator, model_validator


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

    class Config:
        from_attributes = True


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
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


# ============ Pilot Language Schemas ============

class PilotLanguageBase(BaseModel):
    pilot_id: int
    language: str


class PilotLanguageResponse(PilotLanguageBase):
    id: int

    class Config:
        from_attributes = True


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
    seat_number: Optional[str] = None
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
    flight_id: Optional[int] = None

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    @classmethod
    def convert_languages(cls, data):
        # If data is an ORM model object
        if hasattr(data, '__dict__'):
            obj = data
            # Convert languages relationship to list of strings
            if hasattr(obj, 'languages') and obj.languages is not None:
                # Check if it's a relationship (list of PilotLanguage objects)
                if obj.languages and len(obj.languages) > 0:
                    if hasattr(obj.languages[0], 'language'):
                        languages = [lang.language for lang in obj.languages]
                    else:
                        languages = obj.languages
                else:
                    languages = []
            else:
                languages = None
            
            return {
                'id': obj.id,
                'name': obj.name,
                'age': obj.age,
                'gender': obj.gender,
                'nationality': obj.nationality,
                'employee_id': obj.employee_id,
                'role': obj.role,
                'license_number': obj.license_number,
                'seniority_level': obj.seniority_level,
                'max_allowed_distance_km': obj.max_allowed_distance_km,
                'vehicle_type_restriction_id': obj.vehicle_type_restriction_id,
                'hours_flown': obj.hours_flown,
                'seat_number': getattr(obj, 'seat_number', None),
                'languages': languages,
                'created_at': obj.created_at,
                'flight_id': getattr(obj, 'flight_id', None),
            }
        return data


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

    class Config:
        from_attributes = True


# ============ Flight Information Schemas ============

class FlightInfoBase(BaseModel):
    flight_number: str
    airline_id: int
    date: datetime
    departure_time: datetime
    arrival_time: datetime
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
    date: Optional[datetime] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
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
    vehicle_type: Optional[VehicleTypeResponse] = None
    airline: Optional[AirlineResponse] = None
    departure_airport: Optional[AirportLocationResponse] = None
    arrival_airport: Optional[AirportLocationResponse] = None
    shared_flight_info: Optional["SharedFlightResponse"] = None
    connecting_flight: Optional["ConnectingFlightResponse"] = None
    flight_crew: Optional[List["FlightCrewResponse"]] = None
    cabin_crew: Optional[List["CabinCrewResponse"]] = None
    passengers: Optional[List["PassengerResponse"]] = None

    class Config:
        from_attributes = True


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
    primary_airline: Optional[AirlineResponse] = None
    secondary_airline: Optional[AirlineResponse] = None
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


# ============ Passenger Schemas ============
class PassengerBase(BaseModel):
    name: str
    age: int
    gender: str
    nationality: str
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    seat_type: str  # business or economy
    flight_id: Optional[int] = None
    seat_number: Optional[str] = None
    parent_id: Optional[int] = None  # For infants (age 0-2)
    affiliated_passenger_ids: Optional[List[int]] = None  # List of 1-2 passenger IDs for neighboring seats


class PassengerCreate(PassengerBase):
    pass


class PassengerUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    seat_type: Optional[str] = None
    seat_number: Optional[str] = None
    parent_id: Optional[int] = None
    affiliated_passenger_ids: Optional[List[int]] = None


class PassengerResponse(PassengerBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True



# ============ Cabin Crew Schemas ============
class CabinCrewBase(BaseModel):
    name: str
    age: int
    gender: str
    nationality: str
    employee_id: str
    attendant_type: str  # chief, regular, chef
    languages: List[str]
    recipes: Optional[List[str]] = None  # For chefs: 2-4 dish recipes
    vehicle_restrictions: Optional[List[int]] = None  # Vehicle type IDs
    seat_number: Optional[str] = None


class CabinCrewCreate(CabinCrewBase):
    pass


class CabinCrewUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    attendant_type: Optional[str] = None
    languages: Optional[List[str]] = None
    recipes: Optional[List[str]] = None
    vehicle_restrictions: Optional[List[int]] = None
    flight_id: Optional[int] = None


class CabinCrewResponse(CabinCrewBase):
    id: int
    flight_id: Optional[int] = None
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ Roster Schemas ============

class RosterCreate(BaseModel):
    flight_id: int
    roster_name: str
    generated_by: Optional[str] = None
    database_type: str = "sql"
    auto_select_crew: bool = True  # If True, automatically select crew
    flight_crew_ids: Optional[List[int]] = None  # Manual crew selection
    cabin_crew_ids: Optional[List[int]] = None  # Manual crew selection
    auto_assign_seats: bool = True  # If True, automatically assign seats to passengers


class RosterResponse(BaseModel):
    id: Union[int, str]  # int for SQL, str for MongoDB ObjectId
    flight_id: int
    roster_name: str
    generated_at: datetime
    generated_by: Optional[str]
    database_type: str
    roster_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class RosterListResponse(BaseModel):
    id: Union[int, str]  # int for SQL, str for MongoDB ObjectId
    flight_id: int
    roster_name: str
    generated_at: datetime
    generated_by: Optional[str]
    database_type: str
    
    class Config:
        from_attributes = True
