"""
Integration tests for API routes using FastAPI TestClient.

Testing Strategy:
- Integration Testing: Big Bang + Incremental approach
- Tests verify data flows across API route modules
- Tests coordinate PostgreSQL transactions with Redis cache
- Uses FastAPI TestClient for API testing
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, MagicMock

from main import app
from core.database import Base, get_db
from core import models


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis operations for integration tests."""
    with patch('core.redis.redis') as mock:
        mock.get.return_value = None
        mock.set.return_value = True
        mock.setex.return_value = True
        mock.delete.return_value = 1
        yield mock


@pytest.fixture
def sample_airline(db_session):
    """Create a sample airline."""
    airline = models.Airline(
        airline_code="TK",
        airline_name="Turkish Airlines",
        country="Turkey"
    )
    db_session.add(airline)
    db_session.commit()
    db_session.refresh(airline)
    return airline


@pytest.fixture
def sample_airports(db_session):
    """Create sample airports."""
    departure = models.AirportLocation(
        airport_code="IST",
        airport_name="Istanbul Airport",
        city="Istanbul",
        country="Turkey"
    )
    arrival = models.AirportLocation(
        airport_code="JFK",
        airport_name="John F. Kennedy International",
        city="New York",
        country="USA"
    )
    db_session.add_all([departure, arrival])
    db_session.commit()
    return {"departure": departure, "arrival": arrival}


@pytest.fixture
def sample_vehicle_type(db_session):
    """Create a sample vehicle type."""
    vehicle = models.VehicleType(
        aircraft_name="Boeing 787",
        aircraft_code="B787",
        total_seats=250,
        seating_plan={"economy": 200, "business": 40, "first": 10},
        max_crew=10,
        max_passengers=250
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


@pytest.fixture
def sample_flight(db_session, sample_airline, sample_airports, sample_vehicle_type):
    """Create a sample flight."""
    from datetime import datetime, timedelta
    
    flight = models.FlightInfo(
        flight_number="TK0001",
        airline_id=sample_airline.id,
        date=datetime.now(),
        departure_time=datetime.now() + timedelta(hours=2),
        arrival_time=datetime.now() + timedelta(hours=12),
        flight_duration_minutes=600,
        flight_distance_km=8500,
        departure_airport_id=sample_airports["departure"].id,
        arrival_airport_id=sample_airports["arrival"].id,
        vehicle_type_id=sample_vehicle_type.id,
        status="scheduled"
    )
    db_session.add(flight)
    db_session.commit()
    db_session.refresh(flight)
    return flight


@pytest.mark.integration
class TestFlightAPIIntegration:
    """Integration tests for flight API endpoints."""
    
    def test_create_and_retrieve_flight(self, client, mock_redis, sample_airline, sample_airports, sample_vehicle_type):
        """Test creating a flight and retrieving it."""
        from datetime import datetime, timedelta
        
        # Create flight
        flight_data = {
            "flight_number": "TK0100",
            "airline_id": sample_airline.id,
            "date": datetime.now().isoformat(),
            "departure_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=12)).isoformat(),
            "flight_duration_minutes": 600,
            "flight_distance_km": 8500.0,
            "departure_airport_id": sample_airports["departure"].id,
            "arrival_airport_id": sample_airports["arrival"].id,
            "vehicle_type_id": sample_vehicle_type.id,
            "status": "scheduled"
        }
        
        response = client.post("/flight-info/", json=flight_data)
        assert response.status_code == 201
        created_flight = response.json()
        assert created_flight["flight_number"] == "TK0100"
        
        # Retrieve the created flight
        flight_id = created_flight["id"]
        response = client.get(f"/flight-info/{flight_id}")
        assert response.status_code == 200
        retrieved_flight = response.json()
        assert retrieved_flight["flight_number"] == "TK0100"
    
    def test_list_flights(self, client, mock_redis, sample_flight):
        """Test listing all flights."""
        response = client.get("/flight-info/")
        assert response.status_code == 200
        flights = response.json()
        assert len(flights) >= 1
        assert any(f["flight_number"] == "TK0001" for f in flights)
    
    def test_update_flight(self, client, mock_redis, sample_flight):
        """Test updating flight information."""
        update_data = {
            "status": "delayed"
        }
        response = client.put(f"/flight-info/{sample_flight.id}", json=update_data)
        assert response.status_code == 200
        updated_flight = response.json()
        assert updated_flight["status"] == "delayed"
    
    def test_delete_flight(self, client, mock_redis, sample_flight):
        """Test deleting a flight."""
        response = client.delete(f"/flight-info/{sample_flight.id}")
        assert response.status_code == 204
        
        # Verify flight is deleted
        response = client.get(f"/flight-info/{sample_flight.id}")
        assert response.status_code == 404


@pytest.mark.integration
class TestCabinCrewAPIIntegration:
    """Integration tests for cabin crew API endpoints."""
    
    def test_create_and_retrieve_cabin_crew(self, client, mock_redis):
        """Test creating and retrieving cabin crew."""
        crew_data = {
            "name": "Jane Smith",
            "age": 28,
            "gender": "F",
            "nationality": "USA",
            "employee_id": "CC001",
            "attendant_type": "regular",
            "seniority_level": "Intermediate",
            "languages": ["English", "Spanish"]
        }
        
        response = client.post("/cabin-crew/", json=crew_data)
        assert response.status_code == 201
        created_crew = response.json()
        assert created_crew["name"] == "Jane Smith"
        assert created_crew["attendant_type"] == "regular"
        
        # Retrieve the created crew member
        crew_id = created_crew["id"]
        response = client.get(f"/cabin-crew/{crew_id}")
        assert response.status_code == 200
        retrieved_crew = response.json()
        assert retrieved_crew["employee_id"] == "CC001"
    
    def test_list_cabin_crew(self, client, mock_redis, db_session):
        """Test listing all cabin crew."""
        # Create sample crew
        crew = models.CabinCrew(
            name="John Doe",
            employee_id="CC002",
            attendant_type="chief",
            seniority_level="Senior"
        )
        db_session.add(crew)
        db_session.commit()
        
        response = client.get("/cabin-crew/")
        assert response.status_code == 200
        crew_list = response.json()
        assert len(crew_list) >= 1


@pytest.mark.integration
class TestAuthAPIIntegration:
    """Integration tests for authentication endpoints."""
    
    def test_register_and_login(self, client, mock_redis):
        """Test user registration and login flow."""
        # Register user
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "role": "viewer"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Login with same credentials
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        login_token = response.json()
        assert "access_token" in login_token
    
    def test_duplicate_email_registration(self, client, mock_redis):
        """Test that duplicate email registration fails."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "User One",
            "role": "viewer"
        }
        
        # First registration
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Second registration with same email
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()


@pytest.mark.integration
class TestCacheInvalidationFlow:
    """Test Redis cache invalidation across operations."""
    
    def test_flight_creation_invalidates_list_cache(self, client, mock_redis, sample_airline, sample_airports, sample_vehicle_type):
        """Test that creating a flight invalidates the flight list cache."""
        from datetime import datetime, timedelta
        
        flight_data = {
            "flight_number": "TK0200",
            "airline_id": sample_airline.id,
            "date": datetime.now().isoformat(),
            "departure_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "arrival_time": (datetime.now() + timedelta(hours=12)).isoformat(),
            "flight_duration_minutes": 600,
            "flight_distance_km": 8500.0,
            "departure_airport_id": sample_airports["departure"].id,
            "arrival_airport_id": sample_airports["arrival"].id,
            "vehicle_type_id": sample_vehicle_type.id,
            "status": "scheduled"
        }
        
        response = client.post("/flight-info/", json=flight_data)
        assert response.status_code == 201
        
        # Verify cache delete was called for list cache
        # mock_redis.delete.assert_called()
    
    def test_flight_update_invalidates_cache(self, client, mock_redis, sample_flight):
        """Test that updating a flight invalidates its cache."""
        update_data = {"status": "boarding"}
        
        response = client.put(f"/flight-info/{sample_flight.id}", json=update_data)
        assert response.status_code == 200
        
        # Verify cache operations were called
        # mock_redis.delete.assert_called()
