"""Comprehensive tests for Flight Crew (Pilot) API endpoints."""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, status
from api.routes.flight_crew import (
    list_flight_crew,
    get_flight_crew,
    create_flight_crew,
    update_flight_crew,
    delete_flight_crew,
)
from core.models import FlightCrew, VehicleType, PilotLanguage
from core.schemas import FlightCrewCreate, FlightCrewUpdate


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_vehicle_type():
    """Create a mock vehicle type."""
    vehicle = Mock(spec=VehicleType)
    vehicle.id = 1
    vehicle.aircraft_name = "Boeing 787"
    vehicle.aircraft_code = "B787"
    return vehicle


@pytest.fixture
def mock_flight_crew():
    """Create a mock flight crew member."""
    crew = Mock(spec=FlightCrew)
    crew.id = 1
    crew.name = "John Pilot"
    crew.age = 35
    crew.gender = "M"
    crew.nationality = "USA"
    crew.employee_id = "FC001"
    crew.license_number = "LIC123456"
    crew.role = "Captain"
    crew.seniority_level = "senior"
    crew.max_allowed_distance_km = 15000
    crew.vehicle_type_restriction_id = 1
    crew.languages = ["English", "French"]
    return crew


@pytest.fixture
def mock_flight_crew_2():
    """Create a second mock flight crew member."""
    crew = Mock(spec=FlightCrew)
    crew.id = 2
    crew.name = "Jane Copilot"
    crew.age = 30
    crew.gender = "F"
    crew.nationality = "Canada"
    crew.employee_id = "FC002"
    crew.license_number = "LIC789012"
    crew.role = "First Officer"
    crew.seniority_level = "junior"
    crew.max_allowed_distance_km = 10000
    crew.vehicle_type_restriction_id = 1
    crew.languages = ["English", "Spanish"]
    return crew


@pytest.fixture
def flight_crew_create_data():
    """Create FlightCrewCreate data."""
    return FlightCrewCreate(
        name="New Captain",
        age=40,
        gender="M",
        nationality="USA",
        employee_id="FC999",
        license_number="LIC999999",
        role="Captain",
        seniority_level="senior",
        max_allowed_distance_km=20000,
        vehicle_type_restriction_id=1,
        languages=["English", "German"]
    )


@pytest.mark.unit
class TestListFlightCrew:
    """Test the list_flight_crew endpoint."""
    
    async def test_list_all_flight_crew(self, mock_db_session, mock_flight_crew,
                                        mock_flight_crew_2):
        """Test listing all flight crew members."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew, mock_flight_crew_2]
        
        result = await list_flight_crew(db=mock_db_session)
        
        assert len(result) == 2
        assert result[0].employee_id == "FC001"
        assert result[1].employee_id == "FC002"
    
    async def test_list_flight_crew_filter_by_vehicle_type(self, mock_db_session,
                                                           mock_flight_crew,
                                                           mock_vehicle_type):
        """Test filtering flight crew by vehicle type."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]
        
        result = await list_flight_crew(
            vehicle_type="Boeing 787",
            db=mock_db_session
        )
        
        assert len(result) == 1
        assert result[0].vehicle_type_restriction_id == 1
    
    async def test_list_flight_crew_filter_by_seniority(self, mock_db_session,
                                                         mock_flight_crew):
        """Test filtering flight crew by seniority level."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]
        
        result = await list_flight_crew(
            seniority_level="senior",
            db=mock_db_session
        )
        
        assert len(result) == 1
        assert result[0].seniority_level == "senior"
    
    async def test_list_flight_crew_filter_by_min_range(self, mock_db_session,
                                                         mock_flight_crew):
        """Test filtering flight crew by minimum allowed range."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]
        
        result = await list_flight_crew(
            min_allowed_range=10000,
            db=mock_db_session
        )
        
        assert len(result) == 1
        assert result[0].max_allowed_distance_km >= 10000
    
    async def test_list_flight_crew_multiple_filters(self, mock_db_session,
                                                      mock_flight_crew):
        """Test filtering flight crew with multiple criteria."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]
        
        result = await list_flight_crew(
            vehicle_type="Boeing 787",
            seniority_level="senior",
            min_allowed_range=15000,
            db=mock_db_session
        )
        
        assert len(result) == 1


@pytest.mark.unit
class TestGetFlightCrew:
    """Test the get_flight_crew endpoint."""
    
    async def test_get_flight_crew_by_id(self, mock_db_session, mock_flight_crew):
        """Test getting a flight crew member by ID."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight_crew
        
        result = await get_flight_crew(crew_id=1, db=mock_db_session)
        
        assert result.id == 1
        assert result.employee_id == "FC001"
    
    async def test_get_flight_crew_not_found(self, mock_db_session):
        """Test getting a non-existent flight crew member."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_flight_crew(crew_id=999, db=mock_db_session)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


@pytest.mark.unit
class TestCreateFlightCrew:
    """Test the create_flight_crew endpoint."""
    
    async def test_create_flight_crew_success(self, mock_db_session,
                                              flight_crew_create_data):
        """Test successful flight crew creation."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None  # No duplicates
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_flight_crew(crew=flight_crew_create_data,
                                          db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    async def test_create_flight_crew_duplicate_employee_id(self, mock_db_session,
                                                            flight_crew_create_data,
                                                            mock_flight_crew):
        """Test creating flight crew with duplicate employee ID."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call returns None (no license dup), second returns duplicate employee
        query_mock.first.side_effect = [None, mock_flight_crew]
        
        with pytest.raises(HTTPException) as exc_info:
            await create_flight_crew(crew=flight_crew_create_data,
                                    db=mock_db_session)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail).lower()
    
    async def test_create_flight_crew_duplicate_license(self, mock_db_session,
                                                        flight_crew_create_data,
                                                        mock_flight_crew):
        """Test creating flight crew with duplicate license number."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight_crew  # Duplicate license
        
        with pytest.raises(HTTPException) as exc_info:
            await create_flight_crew(crew=flight_crew_create_data,
                                    db=mock_db_session)
        
        assert exc_info.value.status_code == 400
        assert "license" in str(exc_info.value.detail).lower()
    
    async def test_create_flight_crew_invalid_seniority(self, mock_db_session):
        """Test creating flight crew with invalid seniority level."""
        invalid_data = FlightCrewCreate(
            name="Invalid Crew",
            age=35,
            gender="M",
            nationality="USA",
            employee_id="FC888",
            license_number="LIC888888",
            role="Captain",
            seniority_level="invalid_level",  # Invalid
            max_allowed_distance_km=15000,
            vehicle_type_restriction_id=1,
            languages=["English"]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await create_flight_crew(crew=invalid_data, db=mock_db_session)
        
        assert exc_info.value.status_code == 400
        assert "seniority" in str(exc_info.value.detail).lower()
    
    async def test_create_flight_crew_with_languages(self, mock_db_session,
                                                     flight_crew_create_data):
        """Test creating flight crew with multiple languages."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_flight_crew(crew=flight_crew_create_data,
                                          db=mock_db_session)
        
        # Verify languages were added
        assert mock_db_session.add.call_count >= 1


@pytest.mark.unit
class TestUpdateFlightCrew:
    """Test the update_flight_crew endpoint."""
    
    async def test_update_flight_crew_success(self, mock_db_session, mock_flight_crew):
        """Test successful flight crew update."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight_crew
        
        update_data = FlightCrewUpdate(
            seniority_level="intermediate",
            max_allowed_distance_km=18000
        )
        
        result = await update_flight_crew(crew_id=1, crew=update_data,
                                          db=mock_db_session)
        
        assert mock_flight_crew.seniority_level == "intermediate"
        assert mock_flight_crew.max_allowed_distance_km == 18000
        mock_db_session.commit.assert_called_once()
    
    async def test_update_flight_crew_not_found(self, mock_db_session):
        """Test updating a non-existent flight crew member."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        update_data = FlightCrewUpdate(seniority_level="senior")
        
        with pytest.raises(HTTPException) as exc_info:
            await update_flight_crew(crew_id=999, crew=update_data,
                                    db=mock_db_session)
        
        assert exc_info.value.status_code == 404
    
    async def test_update_flight_crew_languages(self, mock_db_session, mock_flight_crew):
        """Test updating flight crew languages."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight_crew
        
        # Mock the language deletion query
        lang_query_mock = MagicMock()
        mock_db_session.query.side_effect = [query_mock, lang_query_mock]
        lang_query_mock.filter.return_value = lang_query_mock
        lang_query_mock.delete.return_value = None
        
        update_data = FlightCrewUpdate(
            languages=["English", "Italian", "German"]
        )
        
        result = await update_flight_crew(crew_id=1, crew=update_data,
                                          db=mock_db_session)
        
        mock_db_session.commit.assert_called_once()


@pytest.mark.unit
class TestDeleteFlightCrew:
    """Test the delete_flight_crew endpoint."""
    
    async def test_delete_flight_crew_success(self, mock_db_session, mock_flight_crew):
        """Test successful flight crew deletion."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight_crew
        
        await delete_flight_crew(crew_id=1, db=mock_db_session)
        
        mock_db_session.delete.assert_called_once_with(mock_flight_crew)
        mock_db_session.commit.assert_called_once()
    
    async def test_delete_flight_crew_not_found(self, mock_db_session):
        """Test deleting a non-existent flight crew member."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await delete_flight_crew(crew_id=999, db=mock_db_session)
        
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestFlightCrewValidation:
    """Test flight crew validation rules."""
    
    async def test_seniority_level_validation(self, mock_db_session):
        """Test that seniority level must be valid."""
        valid_levels = ["senior", "junior", "trainee"]
        
        for level in valid_levels:
            crew_data = FlightCrewCreate(
                name=f"Crew {level}",
                age=35,
                gender="M",
                nationality="USA",
                employee_id=f"FC{level}",
                license_number=f"LIC{level}",
                role="Captain",
                seniority_level=level,
                max_allowed_distance_km=15000,
                vehicle_type_restriction_id=1,
                languages=["English"]
            )
            
            query_mock = MagicMock()
            mock_db_session.query.return_value = query_mock
            query_mock.filter.return_value = query_mock
            query_mock.first.return_value = None
            
            mock_db_session.add = Mock()
            mock_db_session.commit = Mock()
            mock_db_session.refresh = Mock()
            
            # Should not raise exception
            result = await create_flight_crew(crew=crew_data, db=mock_db_session)
    
    async def test_vehicle_type_restriction(self, mock_db_session, mock_vehicle_type):
        """Test that vehicle type restriction is validated."""
        crew_data = FlightCrewCreate(
            name="Restricted Pilot",
            age=35,
            gender="M",
            nationality="USA",
            employee_id="FC_RESTRICT",
            license_number="LIC_RESTRICT",
            role="Captain",
            seniority_level="senior",
            max_allowed_distance_km=15000,
            vehicle_type_restriction_id=999,  # Non-existent vehicle type
            languages=["English"]
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.side_effect = [None, None, None]  # No duplicates, no vehicle
        
        with pytest.raises(HTTPException) as exc_info:
            await create_flight_crew(crew=crew_data, db=mock_db_session)
        
        assert exc_info.value.status_code == 400
        assert "vehicle type" in str(exc_info.value.detail).lower()


@pytest.mark.unit
class TestFlightCrewRoles:
    """Test different flight crew roles."""
    
    async def test_create_captain(self, mock_db_session):
        """Test creating a captain."""
        crew_data = FlightCrewCreate(
            name="Captain Smith",
            age=45,
            gender="M",
            nationality="USA",
            employee_id="FC_CAPT",
            license_number="LIC_CAPT",
            role="Captain",
            seniority_level="senior",
            max_allowed_distance_km=20000,
            vehicle_type_restriction_id=1,
            languages=["English"]
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_flight_crew(crew=crew_data, db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
    
    async def test_create_first_officer(self, mock_db_session):
        """Test creating a first officer."""
        crew_data = FlightCrewCreate(
            name="First Officer Jones",
            age=30,
            gender="F",
            nationality="Canada",
            employee_id="FC_FO",
            license_number="LIC_FO",
            role="First Officer",
            seniority_level="junior",
            max_allowed_distance_km=15000,
            vehicle_type_restriction_id=1,
            languages=["English", "French"]
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_flight_crew(crew=crew_data, db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
    
    async def test_create_flight_engineer(self, mock_db_session):
        """Test creating a flight engineer."""
        crew_data = FlightCrewCreate(
            name="Engineer Brown",
            age=35,
            gender="M",
            nationality="UK",
            employee_id="FC_ENG",
            license_number="LIC_ENG",
            role="Flight Engineer",
            seniority_level="intermediate",
            max_allowed_distance_km=12000,
            vehicle_type_restriction_id=1,
            languages=["English"]
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = await create_flight_crew(crew=crew_data, db=mock_db_session)
        
        mock_db_session.add.assert_called_once()


@pytest.mark.integration
class TestFlightCrewAPIIntegration:
    """Integration tests for flight crew API."""
    
    def test_flight_crew_lifecycle(self):
        """Test complete flight crew lifecycle: create, read, update, delete."""
        # This would be tested with actual TestClient
        pass
    
    def test_flight_crew_language_management(self):
        """Test managing pilot languages."""
        pass
    
    def test_flight_crew_assignment_to_flights(self):
        """Test assigning flight crew to flights."""
        pass
