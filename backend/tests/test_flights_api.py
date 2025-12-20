"""Comprehensive tests for Flight Information API endpoints."""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from api.routes.flights import (
    list_flights,
    get_flight,
    create_flight,
    update_flight,
    delete_flight,
    list_airlines,
    create_airline,
    list_airports,
    create_airport,
)
from core.models import FlightInfo, Airline, AirportLocation, VehicleType
from core.schemas import (
    FlightInfoCreate,
    FlightInfoUpdate,
    AirlineCreate,
    AirportLocationCreate,
)


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_airline():
    """Create a mock airline."""
    airline = Mock(spec=Airline)
    airline.id = 1
    airline.airline_code = "TK"
    airline.airline_name = "Turkish Airlines"
    airline.country = "Turkey"
    return airline


@pytest.fixture
def mock_airport_departure():
    """Create a mock departure airport."""
    airport = Mock(spec=AirportLocation)
    airport.id = 1
    airport.airport_code = "IST"
    airport.airport_name = "Istanbul Airport"
    airport.city = "Istanbul"
    airport.country = "Turkey"
    return airport


@pytest.fixture
def mock_airport_arrival():
    """Create a mock arrival airport."""
    airport = Mock(spec=AirportLocation)
    airport.id = 2
    airport.airport_code = "JFK"
    airport.airport_name = "John F. Kennedy International"
    airport.city = "New York"
    airport.country = "USA"
    return airport


@pytest.fixture
def mock_vehicle_type():
    """Create a mock vehicle type."""
    vehicle = Mock(spec=VehicleType)
    vehicle.id = 1
    vehicle.aircraft_name = "Boeing 787"
    vehicle.aircraft_code = "B787"
    vehicle.total_seats = 250
    vehicle.max_crew = 10
    vehicle.max_passengers = 250
    return vehicle


@pytest.fixture
def mock_flight():
    """Create a mock flight."""
    flight = Mock(spec=FlightInfo)
    flight.id = 1
    flight.flight_number = "TK0001"
    flight.airline_id = 1
    flight.date = datetime.now()
    flight.departure_time = datetime.now() + timedelta(hours=2)
    flight.arrival_time = datetime.now() + timedelta(hours=12)
    flight.flight_duration_minutes = 600
    flight.flight_distance_km = 8500.0
    flight.departure_airport_id = 1
    flight.arrival_airport_id = 2
    flight.vehicle_type_id = 1
    flight.status = "scheduled"
    return flight


@pytest.fixture
def flight_create_data():
    """Create FlightInfoCreate data."""
    return FlightInfoCreate(
        flight_number="TK0100",
        airline_id=1,
        date=datetime.now(),
        departure_time=datetime.now() + timedelta(hours=2),
        arrival_time=datetime.now() + timedelta(hours=12),
        flight_duration_minutes=600,
        flight_distance_km=8500.0,
        departure_airport_id=1,
        arrival_airport_id=2,
        vehicle_type_id=1,
        status="scheduled"
    )


@pytest.mark.unit
class TestListFlights:
    """Test the list_flights endpoint."""
    
    @patch('api.routes.flights.get_cache')
    @patch('api.routes.flights.set_cache')
    async def test_list_all_flights_cache_miss(self, mock_set_cache, mock_get_cache,
                                                mock_db_session, mock_flight):
        """Test listing all flights with cache miss."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.options.return_value = query_mock
        query_mock.all.return_value = [mock_flight]
        
        result = await list_flights(db=mock_db_session)
        
        assert len(result) == 1
        assert result[0].flight_number == "TK0001"
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.flights.get_cache')
    async def test_list_flights_cache_hit(self, mock_get_cache, mock_db_session):
        """Test listing flights with cache hit."""
        cached_data = [{
            "id": 1,
            "flight_number": "TK0001",
            "status": "scheduled"
        }]
        mock_get_cache.return_value = json.dumps(cached_data)
        
        result = await list_flights(db=mock_db_session)
        
        assert len(result) == 1
        mock_get_cache.assert_called_once()
        mock_db_session.query.assert_not_called()


@pytest.mark.unit
class TestGetFlight:
    """Test the get_flight endpoint."""
    
    @patch('api.routes.flights.get_cache')
    @patch('api.routes.flights.set_cache')
    async def test_get_flight_by_id_cache_miss(self, mock_set_cache, mock_get_cache,
                                                mock_db_session, mock_flight):
        """Test getting a flight by ID with cache miss."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight
        
        result = await get_flight(flight_id=1, db=mock_db_session)
        
        assert result.flight_number == "TK0001"
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.flights.get_cache')
    async def test_get_flight_not_found(self, mock_get_cache, mock_db_session):
        """Test getting a non-existent flight."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.options.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_flight(flight_id=999, db=mock_db_session)
        
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestCreateFlight:
    """Test the create_flight endpoint."""
    
    @patch('api.routes.flights.delete_cache')
    async def test_create_flight_success(self, mock_delete_cache, mock_db_session,
                                        flight_create_data):
        """Test successful flight creation."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None  # No duplicate
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_flight(flight=flight_create_data, db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_delete_cache.assert_called()
    
    async def test_create_flight_duplicate_flight_number(self, mock_db_session,
                                                         flight_create_data, mock_flight):
        """Test creating flight with duplicate flight number."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight  # Duplicate exists
        
        with pytest.raises(HTTPException) as exc_info:
            await create_flight(flight=flight_create_data, db=mock_db_session)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail).lower()
    
    async def test_create_flight_invalid_flight_number_format(self, mock_db_session):
        """Test creating flight with invalid flight number format."""
        invalid_data = FlightInfoCreate(
            flight_number="INVALID123",  # Should be AANNNN format
            airline_id=1,
            date=datetime.now(),
            departure_time=datetime.now() + timedelta(hours=2),
            arrival_time=datetime.now() + timedelta(hours=12),
            flight_duration_minutes=600,
            flight_distance_km=8500.0,
            departure_airport_id=1,
            arrival_airport_id=2,
            vehicle_type_id=1,
            status="scheduled"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await create_flight(flight=invalid_data, db=mock_db_session)
        
        assert exc_info.value.status_code == 400


@pytest.mark.unit
class TestUpdateFlight:
    """Test the update_flight endpoint."""
    
    @patch('api.routes.flights.delete_cache')
    async def test_update_flight_status(self, mock_delete_cache, mock_db_session,
                                       mock_flight):
        """Test updating flight status."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight
        
        update_data = FlightInfoUpdate(status="delayed")
        
        result = await update_flight(flight_id=1, flight=update_data, db=mock_db_session)
        
        assert mock_flight.status == "delayed"
        mock_db_session.commit.assert_called_once()
        mock_delete_cache.assert_called()
    
    @patch('api.routes.flights.delete_cache')
    async def test_update_flight_not_found(self, mock_delete_cache, mock_db_session):
        """Test updating a non-existent flight."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        update_data = FlightInfoUpdate(status="delayed")
        
        with pytest.raises(HTTPException) as exc_info:
            await update_flight(flight_id=999, flight=update_data, db=mock_db_session)
        
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestDeleteFlight:
    """Test the delete_flight endpoint."""
    
    @patch('api.routes.flights.delete_cache')
    async def test_delete_flight_success(self, mock_delete_cache, mock_db_session,
                                        mock_flight):
        """Test successful flight deletion."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight
        
        await delete_flight(flight_id=1, db=mock_db_session)
        
        mock_db_session.delete.assert_called_once_with(mock_flight)
        mock_db_session.commit.assert_called_once()
        mock_delete_cache.assert_called()
    
    async def test_delete_flight_not_found(self, mock_db_session):
        """Test deleting a non-existent flight."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_flight(flight_id=999, db=mock_db_session)
        
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestAirlineEndpoints:
    """Test airline CRUD endpoints."""
    
    async def test_list_airlines(self, mock_db_session, mock_airline):
        """Test listing all airlines."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.all.return_value = [mock_airline]
        
        result = await list_airlines(db=mock_db_session)
        
        assert len(result) == 1
        assert result[0].airline_code == "TK"
    
    async def test_create_airline_success(self, mock_db_session):
        """Test successful airline creation."""
        airline_data = AirlineCreate(
            airline_code="BA",
            airline_name="British Airways",
            country="UK"
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None  # No duplicate
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_airline(airline=airline_data, db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    async def test_create_airline_duplicate_code(self, mock_db_session, mock_airline):
        """Test creating airline with duplicate code."""
        airline_data = AirlineCreate(
            airline_code="TK",
            airline_name="Another Airline",
            country="Turkey"
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_airline  # Duplicate exists
        
        with pytest.raises(HTTPException) as exc_info:
            await create_airline(airline=airline_data, db=mock_db_session)
        
        assert exc_info.value.status_code == 400


@pytest.mark.unit
class TestAirportEndpoints:
    """Test airport CRUD endpoints."""
    
    async def test_list_airports(self, mock_db_session, mock_airport_departure):
        """Test listing all airports."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.all.return_value = [mock_airport_departure]
        
        result = await list_airports(db=mock_db_session)
        
        assert len(result) == 1
        assert result[0].airport_code == "IST"
    
    async def test_create_airport_success(self, mock_db_session):
        """Test successful airport creation."""
        airport_data = AirportLocationCreate(
            airport_code="LHR",
            airport_name="London Heathrow",
            city="London",
            country="UK"
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None  # No duplicate
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_airport(airport=airport_data, db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


@pytest.mark.integration
class TestFlightAPIIntegration:
    """Integration tests for flight API with realistic scenarios."""
    
    def test_flight_lifecycle(self, mock_db_session, flight_create_data):
        """Test complete flight lifecycle: create, update, delete."""
        # This would be tested with actual TestClient in test_api_integration.py
        pass
    
    def test_search_flights_by_date_range(self):
        """Test searching flights within date range."""
        pass
    
    def test_filter_flights_by_status(self):
        """Test filtering flights by status."""
        pass
