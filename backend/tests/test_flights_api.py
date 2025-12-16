import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import get_db
from core import models

# Use a dedicated SQLite file DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_flights_api.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """
    For each test:
    - Drop all tables (if exist)
    - Re-create all tables
    This keeps tests isolated from each other.
    """
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    # You can optionally drop_all here again if you want a clean file between tests.
    # models.Base.metadata.drop_all(bind=engine)


def override_get_db():
    """
    Override the application's DB dependency with our test DB session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# This must match the prefix used in main.py:
# app.include_router(flights_router, prefix="/flight-info", tags=["Flights"])
BASE_PATH = "/flight-info"


# ---------------------------------------------------------------------------
# Helper functions to create required base data
# ---------------------------------------------------------------------------

def create_sample_airline():
    """
    Create a sample airline record and return its ID.
    Fields must match AirlineCreate in schemas.py.
    """
    payload = {
        "airline_code": "TA",
        "airline_name": "Test Airline",
        "country": "Türkiye",
    }
    response = client.post(f"{BASE_PATH}/airlines", json=payload)
    assert response.status_code == 201
    data = response.json()
    return data["id"]


def create_sample_airports():
    """
    Create a departure and an arrival airport and return their IDs.
    Fields must match AirportLocationCreate in schemas.py.
    """
    dep_payload = {
        "airport_code": "IST",
        "airport_name": "Istanbul Airport",
        "city": "Istanbul",
        "country": "Türkiye",
    }
    arr_payload = {
        "airport_code": "ESB",
        "airport_name": "Esenboga Airport",
        "city": "Ankara",
        "country": "Türkiye",
    }

    r1 = client.post(f"{BASE_PATH}/airports", json=dep_payload)
    r2 = client.post(f"{BASE_PATH}/airports", json=arr_payload)

    assert r1.status_code == 201
    assert r2.status_code == 201

    dep_id = r1.json()["id"]
    arr_id = r2.json()["id"]
    return dep_id, arr_id


def create_sample_vehicle_type():
    """
    Create a sample vehicle (aircraft) and return its ID.
    Fields must match VehicleTypeCreate / VehicleTypeBase in schemas.py:
    - aircraft_name
    - aircraft_code
    - total_seats
    - seating_plan (Dict)
    - max_crew
    - max_passengers
    """
    payload = {
        "aircraft_name": "Airbus A320",
        "aircraft_code": "A320",
        "total_seats": 180,
        "seating_plan": {},  # can be refined later, empty dict is valid JSON
        "max_crew": 8,
        "max_passengers": 180,
    }
    response = client.post(f"{BASE_PATH}/vehicles", json=payload)
    assert response.status_code == 201
    data = response.json()
    return data["id"]


def create_sample_flight():
    """
    Create a full valid flight and return its JSON representation.
    Fields must match FlightInfoCreate / FlightInfoBase in schemas.py:
    - flight_number
    - airline_id
    - date
    - departure_time
    - arrival_time
    - flight_duration_minutes
    - flight_distance_km
    - departure_airport_id
    - arrival_airport_id
    - vehicle_type_id
    - status
    """
    airline_id = create_sample_airline()
    dep_id, arr_id = create_sample_airports()
    vehicle_id = create_sample_vehicle_type()

    payload = {
        "flight_number": "TA1234",  # valid AANNNN format
        "airline_id": airline_id,
        "date": "2025-12-31T00:00:00",
        "departure_time": "2025-12-31T10:00:00",
        "arrival_time": "2025-12-31T11:30:00",
        "flight_duration_minutes": 90,
        "flight_distance_km": 450.0,
        "departure_airport_id": dep_id,
        "arrival_airport_id": arr_id,
        "vehicle_type_id": vehicle_id,
        "status": "scheduled",
    }

    response = client.post(f"{BASE_PATH}/", json=payload)
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# list_flights tests
# ---------------------------------------------------------------------------

def test_list_flights_empty_db_returns_empty_list():
    """
    When there are no flights in the DB, /flight-info/ should return an empty list.
    """
    response = client.get(f"{BASE_PATH}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []


def test_list_flights_after_creation_returns_flight():
    """
    After creating a flight, /flight-info/ should return it in the list.
    """
    created = create_sample_flight()

    response = client.get(f"{BASE_PATH}/")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == created["id"]
    assert data[0]["flight_number"] == "TA1234"


# ---------------------------------------------------------------------------
# get_flight tests
# ---------------------------------------------------------------------------

def test_get_flight_existing():
    """
    /flight-info/{id} should return the correct flight when it exists.
    """
    created = create_sample_flight()
    flight_id = created["id"]

    response = client.get(f"{BASE_PATH}/{flight_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == flight_id
    assert data["flight_number"] == "TA1234"


def test_get_flight_not_found():
    """
    /flight-info/{id} should return 404 when the flight does not exist.
    """
    response = client.get(f"{BASE_PATH}/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# create_flight tests
# ---------------------------------------------------------------------------

def test_create_flight_invalid_flight_number_format():
    """
    create_flight should reject flight numbers that do not match AANNNN format.
    """
    airline_id = create_sample_airline()
    dep_id, arr_id = create_sample_airports()
    vehicle_id = create_sample_vehicle_type()

    payload = {
        "flight_number": "1234TA",  # invalid format
        "airline_id": airline_id,
        "date": "2025-12-31T00:00:00",
        "departure_time": "2025-12-31T10:00:00",
        "arrival_time": "2025-12-31T11:30:00",
        "flight_duration_minutes": 90,
        "flight_distance_km": 450.0,
        "departure_airport_id": dep_id,
        "arrival_airport_id": arr_id,
        "vehicle_type_id": vehicle_id,
        "status": "scheduled",
    }

    response = client.post(f"{BASE_PATH}/", json=payload)
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "Invalid flight number format" in detail


# ---------------------------------------------------------------------------
# update_flight tests
# ---------------------------------------------------------------------------

def test_update_flight_duration_and_status():
    """
    update_flight should allow partial updates (duration, status, etc.).
    """
    created = create_sample_flight()
    flight_id = created["id"]

    payload = {
        "flight_duration_minutes": 120,
        "status": "delayed",
    }

    response = client.put(f"{BASE_PATH}/{flight_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["flight_duration_minutes"] == 120
    assert data["status"] == "delayed"


def test_update_flight_not_found():
    """
    Updating a non-existing flight should return 404.
    """
    payload = {"status": "cancelled"}
    response = client.put(f"{BASE_PATH}/999999", json=payload)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# delete_flight tests
# ---------------------------------------------------------------------------

def test_delete_flight_existing():
    """
    delete_flight should remove an existing flight and return a success message.
    """
    created = create_sample_flight()
    flight_id = created["id"]

    response = client.delete(f"{BASE_PATH}/{flight_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Flight deleted"

    # Verify that subsequent GET returns 404
    response2 = client.get(f"{BASE_PATH}/{flight_id}")
    assert response2.status_code == 404


def test_delete_flight_not_found():
    """
    Deleting a non-existing flight should return 404.
    """
    response = client.delete(f"{BASE_PATH}/999999")
    assert response.status_code == 404
