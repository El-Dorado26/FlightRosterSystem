"""Comprehensive tests for Flight Crew (Pilot) API endpoints."""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from api.routes.flight_crew import (
    list_flight_crew,
    get_flight_crew,
    create_flight_crew,
    update_flight_crew,
    delete_flight_crew,
)
from core.models import FlightCrew, VehicleType
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


@pytest.mark.unit
class TestLanguageManagement:
    """Test language management endpoints."""

    def test_add_language_to_pilot_success(self, mock_db_session, mock_flight_crew):
        """Test successfully adding a language to a pilot."""
        from api.routes.flight_crew import add_language_to_pilot
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call for crew check, second call for existing language check
        query_mock.first.side_effect = [mock_flight_crew, None]

        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()

        result = asyncio.run(add_language_to_pilot(crew_id=1, language="Spanish", db=mock_db_session))

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_add_duplicate_language(self, mock_db_session, mock_flight_crew):
        """Test adding a language that pilot already knows."""
        from api.routes.flight_crew import add_language_to_pilot
        from core.models import PilotLanguage
        import asyncio

        existing_lang = Mock(spec=PilotLanguage)
        existing_lang.language = "Spanish"

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call returns crew, second returns existing language
        query_mock.first.side_effect = [mock_flight_crew, existing_lang]

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(add_language_to_pilot(crew_id=1, language="Spanish", db=mock_db_session))

        assert exc_info.value.status_code == 400
        assert "already knows" in str(exc_info.value.detail).lower()

    def test_add_language_pilot_not_found(self, mock_db_session):
        """Test adding language to non-existent pilot."""
        from api.routes.flight_crew import add_language_to_pilot
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(add_language_to_pilot(crew_id=999, language="French", db=mock_db_session))

        assert exc_info.value.status_code == 404

    def test_remove_language_from_pilot_success(self, mock_db_session, mock_flight_crew):
        """Test successfully removing a language from a pilot."""
        from api.routes.flight_crew import remove_language_from_pilot
        from core.models import PilotLanguage
        import asyncio

        pilot_lang = Mock(spec=PilotLanguage)
        pilot_lang.language = "French"

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call returns crew, second returns language
        query_mock.first.side_effect = [mock_flight_crew, pilot_lang]

        mock_db_session.delete = Mock()
        mock_db_session.commit = Mock()

        result = asyncio.run(remove_language_from_pilot(crew_id=1, language="French", db=mock_db_session))

        mock_db_session.delete.assert_called_once_with(pilot_lang)
        assert result["removed_language"] == "French"

    def test_remove_nonexistent_language(self, mock_db_session, mock_flight_crew):
        """Test removing a language pilot doesn't know."""
        from api.routes.flight_crew import remove_language_from_pilot
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call returns crew, second returns None (language not found)
        query_mock.first.side_effect = [mock_flight_crew, None]

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(remove_language_from_pilot(crew_id=1, language="Italian", db=mock_db_session))

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    def test_get_pilot_languages_success(self, mock_db_session, mock_flight_crew):
        """Test getting all languages for a pilot."""
        from api.routes.flight_crew import get_pilot_languages
        from core.models import PilotLanguage
        import asyncio

        lang1 = Mock(spec=PilotLanguage)
        lang1.language = "English"
        lang2 = Mock(spec=PilotLanguage)
        lang2.language = "French"

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call for crew check, second call for languages
        query_mock.first.return_value = mock_flight_crew
        query_mock.all.return_value = [lang1, lang2]

        result = asyncio.run(get_pilot_languages(crew_id=1, db=mock_db_session))

        assert len(result) == 2
        assert result[0].language == "English"
        assert result[1].language == "French"

    def test_get_pilot_languages_empty(self, mock_db_session, mock_flight_crew):
        """Test getting languages for pilot with no languages."""
        from api.routes.flight_crew import get_pilot_languages
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_flight_crew
        query_mock.all.return_value = []

        result = asyncio.run(get_pilot_languages(crew_id=1, db=mock_db_session))

        assert result == []


@pytest.mark.unit
class TestSeniorityFiltering:
    """Test seniority level filtering endpoints."""

    def test_get_pilots_by_seniority_senior(self, mock_db_session, mock_flight_crew):
        """Test filtering pilots by senior level."""
        from api.routes.flight_crew import get_pilots_by_seniority
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]

        result = asyncio.run(get_pilots_by_seniority(level="senior", db=mock_db_session))

        assert len(result) == 1
        assert result[0].seniority_level == "senior"

    def test_get_pilots_by_seniority_junior(self, mock_db_session, mock_flight_crew_2):
        """Test filtering pilots by junior level."""
        from api.routes.flight_crew import get_pilots_by_seniority
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew_2]

        result = asyncio.run(get_pilots_by_seniority(level="junior", db=mock_db_session))

        assert len(result) == 1
        assert result[0].seniority_level == "junior"

    def test_get_pilots_by_invalid_seniority(self, mock_db_session):
        """Test filtering with invalid seniority level."""
        from api.routes.flight_crew import get_pilots_by_seniority
        import asyncio

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_pilots_by_seniority(level="invalid_level", db=mock_db_session))

        assert exc_info.value.status_code == 400
        assert "invalid seniority level" in str(exc_info.value.detail).lower()


@pytest.mark.unit
class TestCrewAssignment:
    """Test crew assignment endpoints with business rules."""

    def test_assign_pilot_to_flight_success(self, mock_db_session, mock_flight_crew):
        """Test successfully assigning a pilot to a flight."""
        from api.routes.flight_crew import assign_pilot_to_flight
        from core.schemas import FlightCrewAssignmentCreate
        import asyncio

        assignment_data = FlightCrewAssignmentCreate(
            flight_id=100,
            crew_id=1,
            role="Captain"
        )

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.join.return_value = query_mock
        # First call: pilot exists
        # Second call: not already assigned
        # Third call: get assigned crew (empty for first assignment)
        query_mock.first.side_effect = [mock_flight_crew, None]
        query_mock.all.return_value = []

        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()

        result = asyncio.run(assign_pilot_to_flight(assignment=assignment_data, db=mock_db_session))

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_assign_pilot_already_assigned(self, mock_db_session, mock_flight_crew):
        """Test assigning a pilot who is already assigned to the flight."""
        from api.routes.flight_crew import assign_pilot_to_flight
        from core.schemas import FlightCrewAssignmentCreate
        from core.models import FlightCrewAssignment
        import asyncio

        assignment_data = FlightCrewAssignmentCreate(
            flight_id=100,
            crew_id=1,
            role="Captain"
        )

        existing_assignment = Mock(spec=FlightCrewAssignment)

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        # First call: pilot exists, second call: already assigned
        query_mock.first.side_effect = [mock_flight_crew, existing_assignment]

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(assign_pilot_to_flight(assignment=assignment_data, db=mock_db_session))

        assert exc_info.value.status_code == 400
        assert "already assigned" in str(exc_info.value.detail).lower()

    def test_assign_trainee_exceeds_limit(self, mock_db_session):
        """Test that flight cannot have more than 2 trainees."""
        from api.routes.flight_crew import assign_pilot_to_flight
        from core.schemas import FlightCrewAssignmentCreate
        import asyncio

        # Create trainee pilot
        trainee = Mock(spec=FlightCrew)
        trainee.id = 3
        trainee.seniority_level = "trainee"

        # Two existing trainees
        trainee1 = Mock(spec=FlightCrew)
        trainee1.seniority_level = "trainee"
        trainee2 = Mock(spec=FlightCrew)
        trainee2.seniority_level = "trainee"

        assignment_data = FlightCrewAssignmentCreate(
            flight_id=100,
            crew_id=3,
            role="Trainee Pilot"
        )

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.join.return_value = query_mock
        # First: pilot exists, second: not assigned, third: get assigned crew
        query_mock.first.side_effect = [trainee, None]
        query_mock.all.return_value = [trainee1, trainee2]

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(assign_pilot_to_flight(assignment=assignment_data, db=mock_db_session))

        assert exc_info.value.status_code == 400
        assert "at most 2 trainees" in str(exc_info.value.detail).lower()

    def test_validate_flight_crew_requirements_valid(self, mock_db_session):
        """Test validating flight crew that meets all requirements."""
        from api.routes.flight_crew import validate_flight_crew_requirements
        import asyncio

        # Create crew with proper composition
        senior_pilot = Mock(spec=FlightCrew)
        senior_pilot.seniority_level = "senior"
        junior_pilot = Mock(spec=FlightCrew)
        junior_pilot.seniority_level = "junior"

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [senior_pilot, junior_pilot]

        result = asyncio.run(validate_flight_crew_requirements(flight_id=100, db=mock_db_session))

        assert result["valid"] is True
        assert result["requirements"]["has_senior"] is True
        assert result["requirements"]["has_junior"] is True
        assert result["requirements"]["trainee_count_valid"] is True

    def test_validate_flight_crew_missing_senior(self, mock_db_session):
        """Test validation fails when missing senior pilot."""
        from api.routes.flight_crew import validate_flight_crew_requirements
        import asyncio

        # Only junior pilots
        junior1 = Mock(spec=FlightCrew)
        junior1.seniority_level = "junior"
        junior2 = Mock(spec=FlightCrew)
        junior2.seniority_level = "junior"

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [junior1, junior2]

        result = asyncio.run(validate_flight_crew_requirements(flight_id=100, db=mock_db_session))

        assert result["valid"] is False
        assert result["requirements"]["has_senior"] is False
        assert "senior pilot" in result["message"].lower()

    def test_validate_flight_crew_too_many_trainees(self, mock_db_session):
        """Test validation fails with too many trainees."""
        from api.routes.flight_crew import validate_flight_crew_requirements
        import asyncio

        senior = Mock(spec=FlightCrew)
        senior.seniority_level = "senior"
        junior = Mock(spec=FlightCrew)
        junior.seniority_level = "junior"
        trainee1 = Mock(spec=FlightCrew)
        trainee1.seniority_level = "trainee"
        trainee2 = Mock(spec=FlightCrew)
        trainee2.seniority_level = "trainee"
        trainee3 = Mock(spec=FlightCrew)
        trainee3.seniority_level = "trainee"

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [senior, junior, trainee1, trainee2, trainee3]

        result = asyncio.run(validate_flight_crew_requirements(flight_id=100, db=mock_db_session))

        assert result["valid"] is False
        assert result["requirements"]["trainee_count_valid"] is False
        assert "too many trainees" in result["message"].lower()

    def test_get_flight_crew_assignments(self, mock_db_session, mock_flight_crew, mock_flight_crew_2):
        """Test getting all crew assigned to a flight."""
        from api.routes.flight_crew import get_flight_crew_assignments
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew, mock_flight_crew_2]

        result = asyncio.run(get_flight_crew_assignments(flight_id=100, db=mock_db_session))

        assert len(result) == 2
        assert result[0].employee_id == "FC001"
        assert result[1].employee_id == "FC002"

    def test_get_flight_crew_assignments_empty(self, mock_db_session):
        """Test getting crew for flight with no assignments."""
        from api.routes.flight_crew import get_flight_crew_assignments
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = []

        result = asyncio.run(get_flight_crew_assignments(flight_id=100, db=mock_db_session))

        assert result == []

    def test_unassign_pilot_from_flight_success(self, mock_db_session):
        """Test successfully removing a pilot from a flight."""
        from api.routes.flight_crew import unassign_pilot_from_flight
        from core.models import FlightCrewAssignment
        import asyncio

        assignment = Mock(spec=FlightCrewAssignment)

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = assignment

        mock_db_session.delete = Mock()
        mock_db_session.commit = Mock()

        result = asyncio.run(unassign_pilot_from_flight(flight_id=100, crew_id=1, db=mock_db_session))

        mock_db_session.delete.assert_called_once_with(assignment)
        assert result["flight_id"] == 100
        assert result["crew_id"] == 1

    def test_unassign_pilot_not_found(self, mock_db_session):
        """Test removing non-existent assignment."""
        from api.routes.flight_crew import unassign_pilot_from_flight
        import asyncio

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(unassign_pilot_from_flight(flight_id=100, crew_id=999, db=mock_db_session))

        assert exc_info.value.status_code == 404
        assert "no assignment found" in str(exc_info.value.detail).lower()


@pytest.mark.unit
class TestExportEndpoints:
    """Test export endpoints for flight crew data."""

    def test_export_flight_crew_json_all(self, mock_db_session, mock_flight_crew, mock_flight_crew_2):
        """Test exporting all flight crew as JSON."""
        from api.routes.flight_crew import export_flight_crew_json
        import asyncio

        # Set up __dict__ for JSON export
        mock_flight_crew.__dict__ = {
            "id": 1,
            "name": "John Pilot",
            "employee_id": "FC001",
            "role": "Captain",
            "seniority_level": "senior",
            "_sa_instance_state": "should_be_removed"
        }
        mock_flight_crew_2.__dict__ = {
            "id": 2,
            "name": "Jane Copilot",
            "employee_id": "FC002",
            "role": "First Officer",
            "seniority_level": "junior",
            "_sa_instance_state": "should_be_removed"
        }

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew, mock_flight_crew_2]

        result = asyncio.run(export_flight_crew_json(db=mock_db_session))

        assert result is not None

    def test_export_flight_crew_json_with_filters(self, mock_db_session, mock_flight_crew):
        """Test exporting flight crew JSON with filters."""
        from api.routes.flight_crew import export_flight_crew_json
        import asyncio

        # Set up __dict__ for JSON export
        mock_flight_crew.__dict__ = {
            "id": 1,
            "name": "John Pilot",
            "employee_id": "FC001",
            "role": "Captain",
            "seniority_level": "senior",
            "_sa_instance_state": "should_be_removed"
        }

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]

        result = asyncio.run(export_flight_crew_json(
            vehicle_type="Boeing 787",
            seniority_level="senior",
            min_allowed_range=10000,
            db=mock_db_session
        ))

        assert result is not None

    def test_export_flight_crew_csv_all(self, mock_db_session, mock_flight_crew, mock_flight_crew_2):
        """Test exporting all flight crew as CSV."""
        from api.routes.flight_crew import export_flight_crew_csv
        import asyncio

        # Set up __dict__ for CSV export
        mock_flight_crew.__dict__ = {
            "id": 1,
            "name": "John Pilot",
            "employee_id": "FC001",
            "role": "Captain",
            "seniority_level": "senior",
            "_sa_instance_state": "should_be_removed"
        }

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]

        result = asyncio.run(export_flight_crew_csv(db=mock_db_session))

        assert result is not None
        assert result.media_type == "text/csv"

    def test_export_flight_crew_csv_with_filters(self, mock_db_session, mock_flight_crew):
        """Test exporting flight crew CSV with filters."""
        from api.routes.flight_crew import export_flight_crew_csv
        import asyncio

        mock_flight_crew.__dict__ = {
            "id": 1,
            "name": "John Pilot",
            "employee_id": "FC001",
            "seniority_level": "senior",
            "_sa_instance_state": "should_be_removed"
        }

        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.join.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_flight_crew]

        result = asyncio.run(export_flight_crew_csv(
            seniority_level="senior",
            min_allowed_range=15000,
            db=mock_db_session
        ))

        assert result is not None
