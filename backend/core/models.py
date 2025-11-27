from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    ForeignKey,
    Float,
    Boolean,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class AirportLocation(Base):
    __tablename__ = "airport_locations"

    id = Column(Integer, primary_key=True, index=True)
    airport_code = Column(String(3), unique=True, nullable=False, index=True)
    airport_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    flights_departure = relationship("FlightInfo", foreign_keys="FlightInfo.departure_airport_id", back_populates="departure_airport")
    flights_arrival = relationship("FlightInfo", foreign_keys="FlightInfo.arrival_airport_id", back_populates="arrival_airport")


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id = Column(Integer, primary_key=True, index=True)
    aircraft_name = Column(String, unique=True, nullable=False)
    aircraft_code = Column(String(10), unique=True, nullable=False)
    total_seats = Column(Integer, nullable=False)
    seating_plan = Column(JSON, nullable=False)
    max_crew = Column(Integer, nullable=False)
    max_passengers = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    flights = relationship("FlightInfo", back_populates="vehicle_type")
    menu = relationship("Menu", uselist=False, back_populates="vehicle_type")


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type_id = Column(Integer, ForeignKey("vehicle_types.id"), nullable=False, unique=True)
    menu_items = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    vehicle_type = relationship("VehicleType", back_populates="menu")


class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, index=True)
    airline_code = Column(String(2), unique=True, nullable=False)
    airline_name = Column(String, unique=True, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    flights = relationship("FlightInfo", back_populates="airline")
    shared_flights_primary = relationship("SharedFlight", foreign_keys="SharedFlight.primary_airline_id", back_populates="primary_airline")
    shared_flights_secondary = relationship("SharedFlight", foreign_keys="SharedFlight.secondary_airline_id", back_populates="secondary_airline")


class FlightInfo(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(6), nullable=False, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    flight_duration_minutes = Column(Integer, nullable=False)
    flight_distance_km = Column(Float, nullable=False)
    departure_airport_id = Column(Integer, ForeignKey("airport_locations.id"), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey("airport_locations.id"), nullable=False)
    vehicle_type_id = Column(Integer, ForeignKey("vehicle_types.id"), nullable=False)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    airline = relationship("Airline", back_populates="flights")
    departure_airport = relationship("AirportLocation", foreign_keys=[departure_airport_id], back_populates="flights_departure")
    arrival_airport = relationship("AirportLocation", foreign_keys=[arrival_airport_id], back_populates="flights_arrival")
    vehicle_type = relationship("VehicleType", back_populates="flights")
    flight_crew = relationship("FlightCrew", back_populates="flight")
    cabin_crew = relationship("CabinCrew", back_populates="flight")
    passengers = relationship("Passenger", back_populates="flight")
    shared_flight_info = relationship("SharedFlight", uselist=False, back_populates="primary_flight")
    connecting_flight = relationship("ConnectingFlight", uselist=False, back_populates="flight")


class SharedFlight(Base):
    __tablename__ = "shared_flights"

    id = Column(Integer, primary_key=True, index=True)
    primary_flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False, unique=True)
    primary_airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    secondary_airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    secondary_flight_number = Column(String(6), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    primary_flight = relationship("FlightInfo", back_populates="shared_flight_info")
    primary_airline = relationship("Airline", foreign_keys=[primary_airline_id], back_populates="shared_flights_primary")
    secondary_airline = relationship("Airline", foreign_keys=[secondary_airline_id], back_populates="shared_flights_secondary")
    connecting_flights = relationship("ConnectingFlight", back_populates="shared_flight")


class ConnectingFlight(Base):
    __tablename__ = "connecting_flights"

    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False, unique=True)
    shared_flight_id = Column(Integer, ForeignKey("shared_flights.id"), nullable=False)
    connecting_flight_number = Column(String(6), nullable=False)
    connecting_airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    flight = relationship("FlightInfo", back_populates="connecting_flight")
    shared_flight = relationship("SharedFlight", back_populates="connecting_flights")


class PilotLanguage(Base):
    __tablename__ = "pilot_languages"

    id = Column(Integer, primary_key=True, index=True)
    pilot_id = Column(Integer, ForeignKey("flight_crew.id"), nullable=False)
    language = Column(String, nullable=False)

    pilot = relationship("FlightCrew", back_populates="languages")


class FlightCrew(Base):
    __tablename__ = "flight_crew"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    nationality = Column(String, nullable=False)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    seniority_level = Column(String, nullable=False)
    max_allowed_distance_km = Column(Float, nullable=False)
    vehicle_type_restriction_id = Column(Integer, ForeignKey("vehicle_types.id"), nullable=True)
    hours_flown = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)

    flight = relationship("FlightInfo", back_populates="flight_crew")
    vehicle_type_restriction = relationship("VehicleType")
    languages = relationship("PilotLanguage", back_populates="pilot")


class CabinCrew(Base):
    __tablename__ = "cabin_crew"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    certifications = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)

    flight = relationship("FlightInfo", back_populates="cabin_crew")


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    passport_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=True)

    flight = relationship("FlightInfo", back_populates="passengers")

class FlightCrewAssignment(Base):
    __tablename__ = "flight_crew_assignment"

    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    crew_id = Column(Integer, ForeignKey("flight_crew.id"), nullable=False)
    role = Column(String, nullable=True)
    assigned_at = Column(DateTime, server_default=func.now())

    crew = relationship("FlightCrew", back_populates="assignments")
    flight = relationship("FlightInfo")


