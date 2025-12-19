import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from main import app
from core.database import get_db
from core import models

# ---------------------------------------------------------------------
# Redis MOCK
# ---------------------------------------------------------------------

@pytest.fixture
def mock_redis():
    with patch('core.redis.redis') as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        mock.setex.return_value = True
        mock.delete.return_value = 1
        yield mock


# ---------------------------------------------------------------------
# Test DB setup (in-memory SQLite + StaticPool)
# ---------------------------------------------------------------------


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try: yield session
    finally: session.close()

@pytest.fixture()
def client(db_session, mock_redis):
    def override_get_db(): yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

BASE_PATH = "/passenger/"

# ---------------------------------------------------------------------
# Helper: create passenger directly via DB
# ---------------------------------------------------------------------

def create_passenger(db, seat="1A", flight_id=1, parent_id=None):
    passenger = models.Passenger(
        name="John Doe",
        age=30,
        gender="Male",
        nationality="TR",
        email="john@example.com",
        phone="123456789",
        passport_number="P123456",
        seat_type="Economy",
        flight_id=flight_id,
        seat_number=seat,
        parent_id=parent_id,
    )
    db.add(passenger)
    db.commit()
    db.refresh(passenger)
    return passenger

# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_list_passengers_empty(client):
    response = client.get(BASE_PATH)
    assert response.status_code == 200
    assert response.json() == []

def test_create_passenger_success(client):
    payload = {
        "name": "Alice",
        "email": "alice@test.com",
        "phone": "555",
        "passport_number": "A123",
        "age": 25,
        "gender": "Female",
        "nationality": "US",
        "seat_type": "Economy",
        "flight_id": 1,        
        "seat_number": "2A"    
    }
    response = client.post(BASE_PATH, json=payload)
    assert response.status_code == 201

def test_get_passenger_by_id(client, db_session):
    passenger = create_passenger(db_session)
    response = client.get(f"{BASE_PATH}{passenger.id}")
    assert response.status_code == 200

def test_get_passenger_not_found(client):
    response = client.get(f"{BASE_PATH}9999")
    assert response.status_code == 404

def test_seat_already_taken(client, db_session):
    create_passenger(db_session, seat="3C", flight_id=10)
    payload = {
        "name": "Bob", 
        "email": "bob@test.com", 
        "phone": "444", 
        "passport_number": "B456", 
        "age": 40, 
        "gender": "Male", 
        "nationality": "UK", 
        "seat_type": "Business",
        "flight_id": 10,
        "seat_number": "3C"
    }
    response = client.post(BASE_PATH, json=payload)
    assert response.status_code == 400

def test_parent_not_found(client):
    payload = {
        "name": "Child", 
        "email": "child@test.com", 
        "phone": "111", 
        "passport_number": "C789", 
        "age": 10, 
        "gender": "Male", 
        "nationality": "TR", 
        "seat_type": "Economy",
        "flight_id": 1,
        "seat_number": "4D",
        "parent_id": 999
    }
    response = client.post(BASE_PATH, json=payload)
    assert response.status_code == 404

def test_update_passenger_seat(client, db_session):
    passenger = create_passenger(db_session, seat="5A")
    response = client.put(f"{BASE_PATH}{passenger.id}", json={}, params={"seat_number": "6B"})
    assert response.status_code == 200

def test_delete_passenger(client, db_session):
    passenger = create_passenger(db_session)
    response = client.delete(f"{BASE_PATH}{passenger.id}")
    assert response.status_code == 204
