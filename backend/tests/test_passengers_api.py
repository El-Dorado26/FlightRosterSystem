import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, status
from api.routes.passengers import (
    list_passengers,
    get_passenger,
    create_passenger,
    update_passenger,
    delete_passenger,
)
from core.models import Passenger
from core.schemas import PassengerCreate, PassengerUpdate


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_passenger():
    """Create a mock passenger object."""
    passenger = Mock(spec=Passenger)
    passenger.id = 1
    passenger.name = "John Doe"
    passenger.email = "john.doe@example.com"
    passenger.phone = "+1234567890"
    passenger.passport_number = "AB123456"
    passenger.flight_id = 1
    passenger.seat_number = "12A"
    passenger.parent_id = None
    passenger.age = 30
    return passenger


@pytest.fixture
def mock_passenger_2():
    """Create a second mock passenger object."""
    passenger = Mock(spec=Passenger)
    passenger.id = 2
    passenger.name = "Jane Smith"
    passenger.email = "jane.smith@example.com"
    passenger.phone = "+0987654321"
    passenger.passport_number = "CD789012"
    passenger.flight_id = 1
    passenger.seat_number = "12B"
    passenger.parent_id = None
    passenger.age = 25
    return passenger


@pytest.fixture
def passenger_create_data():
    """Create a PassengerCreate object for adult."""
    return PassengerCreate(
        name="New Passenger",
        email="new@example.com",
        phone="+1122334455",
        passport_number="XY987654",
        age=30,
        gender="Male",
        nationality="US",
        seat_type="Economy"
    )


@pytest.fixture
def passenger_update_data():
    """Create a PassengerUpdate object."""
    return PassengerUpdate(
        name="Updated Passenger",
        email="updated@example.com"
    )

@pytest.mark.unit
class TestListPassengers:
    """Test the list_passengers endpoint."""
    
    @patch('api.routes.passengers.get_cache')
    @patch('api.routes.passengers.set_cache')
    def test_list_all_passengers(self, mock_set_cache, mock_get_cache, 
                                 mock_db_session, mock_passenger, mock_passenger_2):
        """Test listing all passengers (cache miss)."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.all.return_value = [mock_passenger, mock_passenger_2]
        
        result = list_passengers(db=mock_db_session)
        
        assert len(result) == 2
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.passengers.get_cache')
    def test_list_passengers_cache_hit(self, mock_get_cache, mock_db_session):
        """Test listing passengers with cache hit."""
        cached_data = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "passport_number": "AB123456",
                "flight_id": 1,
                "seat_number": "12A",
                "parent_id": None,
                "age": 30
            }
        ]
        mock_get_cache.return_value = json.dumps(cached_data)
        
        result = list_passengers(db=mock_db_session)
        
        assert len(result) == 1
        assert result[0]["name"] == "John Doe"
        mock_db_session.query.assert_not_called()
    
    @patch('api.routes.passengers.get_cache')
    @patch('api.routes.passengers.set_cache')
    def test_list_passengers_by_flight(self, mock_set_cache, mock_get_cache,
                                      mock_db_session, mock_passenger):
        """Test listing passengers filtered by flight_id."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = [mock_passenger]
        
        result = list_passengers(flight_id=1, db=mock_db_session)
        
        assert len(result) == 1
        query_mock.filter.assert_called_once()
    
    @patch('api.routes.passengers.get_cache')
    @patch('api.routes.passengers.set_cache')
    def test_list_passengers_pagination(self, mock_set_cache, mock_get_cache,
                                       mock_db_session, mock_passenger, mock_passenger_2):
        """Test listing multiple passengers (pagination scenario)."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.all.return_value = [mock_passenger, mock_passenger_2]
        
        result = list_passengers(db=mock_db_session)
        
        assert len(result) == 2
        assert isinstance(result, list)


@pytest.mark.unit
class TestGetPassenger:
    """Test the get_passenger endpoint."""
    
    @patch('api.routes.passengers.get_cache')
    def test_get_passenger_not_found(self, mock_get_cache, mock_db_session):
        """Test getting a non-existent passenger."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_passenger(passenger_id=999, db=mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestCreatePassenger:
    """Test the create_passenger endpoint."""
    
    @patch('api.routes.passengers.delete_cache')
    @patch('api.routes.passengers.check_seat_availability')
    def test_create_adult_passenger(self, mock_check_seat, mock_delete_cache,
                                   mock_db_session, passenger_create_data):
        """Test creating an adult passenger."""
        mock_check_seat.return_value = True
        
        create_passenger(
            passenger=passenger_create_data,
            flight_id=1,
            seat_number="12A",
            db=mock_db_session
        )
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert mock_delete_cache.call_count >= 2
    
    @patch('api.routes.passengers.check_seat_availability')
    def test_create_infant_with_parent(self, mock_check_seat,
                                       mock_db_session, mock_passenger):
        """Test creating an infant passenger with valid parent."""
        mock_check_seat.return_value = True
        
        infant_data = PassengerCreate(
            name="Baby Passenger",
            email="baby@example.com",
            phone="+1234567890",
            passport_number="BABY123",
            age=1,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_passenger
        
        create_passenger(
            passenger=infant_data,
            flight_id=1,
            seat_number="12B",
            parent_id=1,
            db=mock_db_session
        )
        
        mock_db_session.add.assert_called_once()
    
    @patch('api.routes.passengers.check_seat_availability')
    def test_create_infant_without_parent_fails(self, mock_check_seat,
                                                mock_db_session):
        """Test creating an infant (age 0-2) without a parent fails."""
        mock_check_seat.return_value = True
        
        infant_data = PassengerCreate(
            name="Baby Passenger",
            email="baby@example.com",
            phone="+1234567890",
            passport_number="BABY123",
            age=1,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_passenger(
                passenger=infant_data,
                flight_id=1,
                seat_number="12A",
                parent_id=None,
                db=mock_db_session
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "parent" in exc_info.value.detail.lower() or "infant" in exc_info.value.detail.lower()
    
    @patch('api.routes.passengers.check_seat_availability')
    def test_create_passenger_invalid_age(self, mock_check_seat, mock_db_session):
        """Test creating passenger with invalid age fails."""
        mock_check_seat.return_value = True
        
        invalid_age_data = PassengerCreate(
            name="Invalid Age",
            email="invalid@example.com",
            phone="+1234567890",
            passport_number="INV123",
            age=-5,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        
        with pytest.raises((HTTPException, ValueError)):
            create_passenger(
                passenger=invalid_age_data,
                flight_id=1,
                seat_number="12A",
                db=mock_db_session
            )
    
    @patch('api.routes.passengers.check_seat_availability')
    def test_create_passenger_seat_taken(self, mock_check_seat, mock_db_session,
                                        passenger_create_data):
        """Test creating passenger with already taken seat fails."""
        mock_check_seat.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            create_passenger(
                passenger=passenger_create_data,
                flight_id=1,
                seat_number="12A",
                db=mock_db_session
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already taken" in exc_info.value.detail.lower()
    
    @patch('api.routes.passengers.check_seat_availability')
    def test_create_passenger_invalid_parent(self, mock_check_seat,
                                            mock_db_session, passenger_create_data):
        """Test creating passenger with non-existent parent fails."""
        mock_check_seat.return_value = True
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            create_passenger(
                passenger=passenger_create_data,
                flight_id=1,
                seat_number="12B",
                parent_id=999,
                db=mock_db_session
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "parent" in exc_info.value.detail.lower()

@pytest.mark.unit
class TestUpdatePassenger:
    """Test the update_passenger endpoint."""
    
    @patch('api.routes.passengers.delete_cache')
    def test_update_passenger_details(self, mock_delete_cache, mock_db_session,
                                     mock_passenger, passenger_update_data):
        """Test updating passenger basic details."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_passenger
        
        update_passenger(
            passenger_id=1,
            passenger=passenger_update_data,
            db=mock_db_session
        )
        
        mock_db_session.commit.assert_called_once()
        assert mock_delete_cache.call_count >= 3
    
    @patch('api.routes.passengers.delete_cache')
    @patch('api.routes.passengers.check_seat_availability')
    def test_update_passenger_assign_seat(self, mock_check_seat, mock_delete_cache,
                                         mock_db_session, mock_passenger,
                                         passenger_update_data):
        """Test assigning a new seat to passenger."""
        mock_check_seat.return_value = True
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_passenger
        
        update_passenger(
            passenger_id=1,
            passenger=passenger_update_data,
            seat_number="15C",
            db=mock_db_session
        )
        
        assert mock_passenger.seat_number == "15C"
        mock_db_session.commit.assert_called_once()
    
    def test_update_passenger_age_validation(self, mock_db_session, mock_passenger):
        """Test updating passenger with invalid age fails."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_passenger
        
        invalid_update = PassengerUpdate(age=-10)
        
        with pytest.raises((HTTPException, ValueError)):
            update_passenger(
                passenger_id=1,
                passenger=invalid_update,
                db=mock_db_session
            )
    
    @patch('api.routes.passengers.delete_cache')
    def test_update_passenger_cache_invalidation(self, mock_delete_cache,
                                                 mock_db_session, mock_passenger,
                                                 passenger_update_data):
        """Test that updating invalidates cache."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_passenger
        
        update_passenger(
            passenger_id=1,
            passenger=passenger_update_data,
            db=mock_db_session
        )
        
        # Should invalidate list, individual, and flight-specific caches
        assert mock_delete_cache.call_count >= 3
    
    def test_update_passenger_not_found(self, mock_db_session, passenger_update_data):
        """Test updating non-existent passenger fails."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            update_passenger(
                passenger_id=999,
                passenger=passenger_update_data,
                db=mock_db_session
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.unit
class TestDeletePassenger:
    """Test the delete_passenger endpoint."""
    
    @patch('api.routes.passengers.delete_cache')
    def test_delete_passenger_success(self, mock_delete_cache, mock_db_session,
                                     mock_passenger):
        """Test successfully deleting a passenger."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_passenger
        
        delete_passenger(passenger_id=1, db=mock_db_session)
        
        mock_db_session.delete.assert_called_once_with(mock_passenger)
        mock_db_session.commit.assert_called_once()
        assert mock_delete_cache.call_count >= 3
    
    def test_delete_passenger_not_found(self, mock_db_session):
        """Test deleting non-existent passenger fails."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            delete_passenger(passenger_id=999, db=mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND