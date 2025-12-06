from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Passenger(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    passport_number: str

class CabinCrew(BaseModel):
    id: int
    name: str
    employee_id: str
    role: str  # e.g., flight attendant, purser
    certifications: list[str]

class FlightCrew(BaseModel):
    id: int
    name: str
    employee_id: str
    role: str  # e.g., pilot, co-pilot
    license_number: str
    hours_flown: int

class FlightInfo(BaseModel):
    id: int
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    aircraft_type: str
    status: str  # e.g., scheduled, delayed, cancelled