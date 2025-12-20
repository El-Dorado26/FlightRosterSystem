"""Comprehensive tests for Roster API endpoints.

This test module covers the roster.py routes that previously had only 19% coverage.
Tests include roster generation, crew availability, roster CRUD operations, and export functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException

from api.routes.roster import (
    generate_roster,
    get_available_flight_crew,
    get_available_cabin_crew,
    list_rosters,
    get_roster,
    export_roster_json,
    download_roster_json,
    delete_roster,
)
from core.schemas import RosterCreate


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_vehicle_type():
    """Create a mock vehicle type."""
    vehicle = MagicMock()
    vehicle.id = 1
    vehicle.aircraft_name = "Boeing 737"
    vehicle.aircraft_code = "B737"
    vehicle.total_seats = 180
    vehicle.max_crew = 6
    vehicle.seating_plan = {
        "rows": [
            {"row_number": 1, "seats": [{"seat": "A", "type": "business"}, {"seat": "B", "type": "business"}]},
            {"row_number": 2, "seats": [{"seat": "A", "type": "standard"}, {"seat": "B", "type": "standard"}]},
        ]
    }
    return vehicle


@pytest.fixture
def mock_airline():
    """Create a mock airline."""
    airline = MagicMock()
    airline.id = 1
    airline.airline_name = "Turkish Airlines"
    airline.airline_code = "TK"
    return airline


@pytest.fixture
def mock_airport():
    """Create a mock airport."""
    airport = MagicMock()
    airport.id = 1
    airport.airport_code = "IST"
    airport.airport_name = "Istanbul Airport"
    airport.city = "Istanbul"
    airport.country = "Turkey"
    return airport


@pytest.fixture
def mock_flight(mock_vehicle_type, mock_airline, mock_airport):
    """Create a mock flight."""
    flight = MagicMock()
    flight.id = 1
    flight.flight_number = "TK1234"
    flight.vehicle_type = mock_vehicle_type
    flight.airline = mock_airline
    flight.departure_airport = mock_airport
    flight.arrival_airport = mock_airport
    flight.departure_time = datetime.now()
    flight.arrival_time = datetime.now()
    flight.date = datetime.now().date()
    return flight


@pytest.fixture
def mock_flight_crew():
    """Create mock flight crew members."""
    captain = MagicMock()
    captain.id = 1
    captain.name = "John Captain"
    captain.age = 45
    captain.gender = "Male"
    captain.nationality = "Turkish"
    captain.employee_id = "EMP001"
    captain.role = "Captain"
    captain.seniority_level = "Senior"
    captain.license_number = "LIC001"
    captain.languages = [MagicMock(language="English"), MagicMock(language="Turkish")]
    captain.vehicle_type_restriction_id = None

    first_officer = MagicMock()
    first_officer.id = 2
    first_officer.name = "Jane Officer"
    first_officer.age = 35
    first_officer.gender = "Female"
    first_officer.nationality = "Turkish"
    first_officer.employee_id = "EMP002"
    first_officer.role = "First Officer"
    first_officer.seniority_level = "Junior"
    first_officer.license_number = "LIC002"
    first_officer.languages = [MagicMock(language="English")]
    first_officer.vehicle_type_restriction_id = None

    return [captain, first_officer]


@pytest.fixture
def mock_cabin_crew():
    """Create mock cabin crew members."""
    chief = MagicMock()
    chief.id = 1
    chief.name = "Chief Attendant"
    chief.age = 40
    chief.gender = "Female"
    chief.nationality = "Turkish"
    chief.employee_id = "CAB001"
    chief.attendant_type = "chief"
    chief.languages = ["English", "Turkish"]
    chief.recipes = []
    chief.vehicle_restrictions = None
    chief.flight_id = None

    regular_attendants = []
    for i in range(4):
        attendant = MagicMock()
        attendant.id = 10 + i
        attendant.name = f"Attendant {i+1}"
        attendant.age = 30 + i
        attendant.gender = "Female"
        attendant.nationality = "Turkish"
        attendant.employee_id = f"CAB{10+i}"
        attendant.attendant_type = "regular"
        attendant.languages = ["English"]
        attendant.recipes = []
        attendant.vehicle_restrictions = None
        attendant.flight_id = None
        regular_attendants.append(attendant)

    return [chief] + regular_attendants


@pytest.fixture
def mock_passengers():
    """Create mock passengers."""
    passengers = []
    for i in range(5):
        passenger = MagicMock()
        passenger.id = i + 1
        passenger.name = f"Passenger {i+1}"
        passenger.email = f"passenger{i+1}@example.com"
        passenger.phone = f"+9055012345{i:02d}"
        passenger.passport_number = f"PASS{i+1:04d}"
        passenger.seat_number = None if i < 3 else f"{i}A"  # Some already have seats
        passengers.append(passenger)
    return passengers


@pytest.fixture
def roster_create_data():
    """Create RosterCreate data for testing."""
    return RosterCreate(
        flight_id=1,
        roster_name="Test Roster",
        generated_by="test_user",
        auto_select_crew=True,
        auto_assign_seats=True,
        database_type="sql"
    )


@pytest.fixture
def mock_roster():
    """Create a mock roster."""
    roster = MagicMock()
    roster.id = 1
    roster.flight_id = 1
    roster.roster_name = "Test Roster"
    roster.generated_by = "test_user"
    roster.generated_at = datetime.now()
    roster.database_type = "sql"
    roster.roster_data = {"flight_info": {"id": 1}}
    roster.metadata = {"total_passengers": 10}
    return roster


# ============================================================================
# GENERATE ROSTER TESTS
# ============================================================================

@pytest.mark.unit
class TestGenerateRoster:
    """Test the generate_roster endpoint."""

    @patch("api.routes.roster.delete_cache")
    @patch("api.routes.roster.build_cache_key")
    @patch("api.routes.roster.validate_crew_selection")
    @patch("api.routes.roster.select_cabin_crew_automatically")
    @patch("api.routes.roster.select_flight_crew_automatically")
    @patch("api.routes.roster.assign_seats_to_passengers")
    @patch("api.routes.roster.get_crew_statistics")
    def test_generate_roster_auto_crew_sql(
        self,
        mock_crew_stats,
        mock_assign_seats,
        mock_select_flight_crew,
        mock_select_cabin_crew,
        mock_validate,
        mock_build_cache,
        mock_delete_cache,
        mock_db_session,
        mock_flight,
        mock_flight_crew,
        mock_cabin_crew,
        mock_passengers,
        roster_create_data
    ):
        """Test roster generation with auto crew selection for SQL storage."""
        # Setup mocks
        mock_flight.vehicle_type.seating_plan = {"rows": []}
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_flight
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_passengers

        mock_select_flight_crew.return_value = mock_flight_crew
        mock_select_cabin_crew.return_value = mock_cabin_crew
        mock_validate.return_value = (True, [])
        mock_assign_seats.return_value = {1: "1A", 2: "1B", 3: "2A"}
        mock_crew_stats.return_value = {"total_flight_crew": 2, "total_cabin_crew": 5}

        # Execute
        result = asyncio.run(generate_roster(roster_create_data, mock_db_session))

        # Verify
        assert result.roster_name == "Test Roster"
        mock_select_flight_crew.assert_called_once()
        mock_select_cabin_crew.assert_called_once()
        mock_validate.assert_called_once()
        mock_db_session.commit.assert_called()

    def test_generate_roster_flight_not_found(
        self, mock_db_session, roster_create_data
    ):
        """Test roster generation when flight is not found."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(generate_roster(roster_create_data, mock_db_session))

        assert exc_info.value.status_code == 404
        assert "Flight not found" in str(exc_info.value.detail)

    def test_generate_roster_no_vehicle_type(
        self, mock_db_session, roster_create_data, mock_flight
    ):
        """Test roster generation when flight has no vehicle type."""
        mock_flight.vehicle_type = None
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_flight

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(generate_roster(roster_create_data, mock_db_session))

        assert exc_info.value.status_code == 400
        assert "vehicle type" in str(exc_info.value.detail).lower()

    @patch("api.routes.roster.validate_crew_selection")
    @patch("api.routes.roster.select_cabin_crew_automatically")
    @patch("api.routes.roster.select_flight_crew_automatically")
    def test_generate_roster_manual_crew_no_ids(
        self,
        mock_select_flight_crew,
        mock_select_cabin_crew,
        mock_validate,
        mock_db_session,
        mock_flight
    ):
        """Test manual crew selection without providing crew IDs."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_flight

        roster_data = RosterCreate(
            flight_id=1,
            roster_name="Test Roster",
            generated_by="test_user",
            auto_select_crew=False,  # Manual selection
            auto_assign_seats=True,
            database_type="sql",
            flight_crew_ids=None  # No crew IDs provided
        )

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(generate_roster(roster_data, mock_db_session))

        assert exc_info.value.status_code == 400
        assert "flight_crew_ids required" in str(exc_info.value.detail)

    @patch("api.routes.roster.validate_crew_selection")
    @patch("api.routes.roster.select_cabin_crew_automatically")
    @patch("api.routes.roster.select_flight_crew_automatically")
    def test_generate_roster_validation_fails(
        self,
        mock_select_flight_crew,
        mock_select_cabin_crew,
        mock_validate,
        mock_db_session,
        mock_flight,
        mock_flight_crew,
        mock_cabin_crew,
        roster_create_data
    ):
        """Test roster generation when crew validation fails."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_flight
        mock_select_flight_crew.return_value = mock_flight_crew
        mock_select_cabin_crew.return_value = mock_cabin_crew
        mock_validate.return_value = (False, ["Missing Captain", "Not enough cabin crew"])

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(generate_roster(roster_create_data, mock_db_session))

        assert exc_info.value.status_code == 400
        assert "validation failed" in str(exc_info.value.detail).lower()

    @patch("api.routes.roster.delete_cache")
    @patch("api.routes.roster.build_cache_key")
    @patch("api.routes.roster.validate_crew_selection")
    @patch("api.routes.roster.select_cabin_crew_automatically")
    @patch("api.routes.roster.select_flight_crew_automatically")
    @patch("api.routes.roster.assign_seats_to_passengers")
    @patch("api.routes.roster.get_crew_statistics")
    @patch("api.routes.roster.save_roster_to_mongodb")
    def test_generate_roster_mongodb_storage(
        self,
        mock_save_mongo,
        mock_crew_stats,
        mock_assign_seats,
        mock_select_flight_crew,
        mock_select_cabin_crew,
        mock_validate,
        mock_build_cache,
        mock_delete_cache,
        mock_db_session,
        mock_flight,
        mock_flight_crew,
        mock_cabin_crew,
        mock_passengers
    ):
        """Test roster generation with MongoDB storage."""
        mock_db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_flight
        mock_db_session.query.return_value.filter.return_value.all.return_value = mock_passengers

        mock_select_flight_crew.return_value = mock_flight_crew
        mock_select_cabin_crew.return_value = mock_cabin_crew
        mock_validate.return_value = (True, [])
        mock_assign_seats.return_value = {}
        mock_crew_stats.return_value = {}
        mock_save_mongo.return_value = "64a1b2c3d4e5f6g7h8i9j0k1"

        roster_data = RosterCreate(
            flight_id=1,
            roster_name="MongoDB Roster",
            generated_by="test_user",
            auto_select_crew=True,
            auto_assign_seats=True,
            database_type="nosql"
        )

        result = asyncio.run(generate_roster(roster_data, mock_db_session))

        assert result["database_type"] == "nosql"
        mock_save_mongo.assert_called_once()


# ============================================================================
# GET AVAILABLE CREW TESTS
# ============================================================================

@pytest.mark.unit
class TestGetAvailableFlightCrew:
    """Test the get_available_flight_crew endpoint."""

    def test_get_available_flight_crew_success(
        self, mock_db_session, mock_flight, mock_flight_crew
    ):
        """Test successfully retrieving available flight crew."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_flight
        mock_db_session.query.return_value.all.return_value = mock_flight_crew

        result = asyncio.run(get_available_flight_crew(1, mock_db_session))

        assert len(result) == 2
        assert result[0]["name"] == "John Captain"

    def test_get_available_flight_crew_flight_not_found(self, mock_db_session):
        """Test when flight is not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_available_flight_crew(999, mock_db_session))

        assert exc_info.value.status_code == 404

    def test_get_available_flight_crew_no_vehicle_type(
        self, mock_db_session, mock_flight
    ):
        """Test when flight has no vehicle type."""
        mock_flight.vehicle_type = None
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_flight

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_available_flight_crew(1, mock_db_session))

        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestGetAvailableCabinCrew:
    """Test the get_available_cabin_crew endpoint."""

    def test_get_available_cabin_crew_success(
        self, mock_db_session, mock_flight, mock_cabin_crew
    ):
        """Test successfully retrieving available cabin crew."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_flight
        
        # Setup query chain for cabin crew
        query_mock = MagicMock()
        query_mock.filter.return_value.all.return_value = mock_cabin_crew
        mock_db_session.query.return_value = query_mock
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_flight

        result = asyncio.run(get_available_cabin_crew(1, mock_db_session))

        assert isinstance(result, list)

    def test_get_available_cabin_crew_flight_not_found(self, mock_db_session):
        """Test when flight is not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_available_cabin_crew(999, mock_db_session))

        assert exc_info.value.status_code == 404


# ============================================================================
# LIST ROSTERS TESTS
# ============================================================================

@pytest.mark.unit
class TestListRosters:
    """Test the list_rosters endpoint."""

    @patch("api.routes.roster.list_rosters_from_mongodb")
    def test_list_all_rosters(
        self, mock_list_mongo, mock_db_session, mock_roster
    ):
        """Test listing all rosters from both SQL and MongoDB."""
        mock_db_session.query.return_value.order_by.return_value.all.return_value = [mock_roster]
        mock_list_mongo.return_value = [
            {
                "id": "mongo123",
                "flight_id": 2,
                "roster_name": "MongoDB Roster",
                "generated_by": "admin",
                "generated_at": datetime.now(),
            }
        ]

        result = asyncio.run(list_rosters(db=mock_db_session))

        assert len(result) == 2

    def test_list_rosters_sql_only(self, mock_db_session, mock_roster):
        """Test listing only SQL rosters."""
        query_mock = MagicMock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = [mock_roster]
        mock_db_session.query.return_value = query_mock

        result = asyncio.run(list_rosters(database_type="sql", db=mock_db_session))

        assert len(result) >= 1

    @patch("api.routes.roster.list_rosters_from_mongodb")
    def test_list_rosters_nosql_only(self, mock_list_mongo, mock_db_session):
        """Test listing only MongoDB rosters."""
        mock_list_mongo.return_value = [
            {
                "id": "mongo123",
                "flight_id": 1,
                "roster_name": "MongoDB Roster",
                "generated_by": "admin",
                "generated_at": datetime.now(),
            }
        ]

        result = asyncio.run(list_rosters(database_type="nosql", db=mock_db_session))

        assert len(result) == 1
        assert result[0]["database_type"] == "nosql"

    @patch("api.routes.roster.list_rosters_from_mongodb")
    def test_list_rosters_by_flight_id(
        self, mock_list_mongo, mock_db_session, mock_roster
    ):
        """Test filtering rosters by flight_id."""
        query_mock = MagicMock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = [mock_roster]
        mock_db_session.query.return_value = query_mock

        mock_list_mongo.return_value = []

        result = asyncio.run(list_rosters(flight_id=1, db=mock_db_session))

        assert all(r["flight_id"] == 1 for r in result if "flight_id" in r)

    @patch("api.routes.roster.list_rosters_from_mongodb")
    def test_list_rosters_mongodb_error(
        self, mock_list_mongo, mock_db_session, mock_roster
    ):
        """Test graceful handling when MongoDB is unavailable."""
        query_mock = MagicMock()
        query_mock.order_by.return_value.all.return_value = [mock_roster]
        mock_db_session.query.return_value = query_mock

        mock_list_mongo.side_effect = Exception("MongoDB connection failed")

        result = asyncio.run(list_rosters(db=mock_db_session))

        # Should still return SQL rosters
        assert len(result) >= 1


# ============================================================================
# GET ROSTER TESTS
# ============================================================================

@pytest.mark.unit
class TestGetRoster:
    """Test the get_roster endpoint."""

    def test_get_roster_sql(self, mock_db_session, mock_roster):
        """Test retrieving a SQL roster by ID."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_roster

        result = asyncio.run(get_roster("1", mock_db_session))

        assert result["id"] == 1
        assert result["roster_name"] == "Test Roster"

    @patch("api.routes.roster.get_roster_from_mongodb")
    def test_get_roster_mongodb(self, mock_get_mongo, mock_db_session):
        """Test retrieving a MongoDB roster by ObjectId."""
        mongo_roster = {
            "id": "64a1b2c3d4e5f6a7b8c9d0e1",
            "flight_id": 1,
            "roster_name": "MongoDB Roster",
            "generated_at": datetime.now(),
        }
        mock_get_mongo.return_value = mongo_roster

        result = asyncio.run(get_roster("64a1b2c3d4e5f6a7b8c9d0e1", mock_db_session))

        assert result["roster_name"] == "MongoDB Roster"

    @patch("api.routes.roster.get_roster_from_mongodb")
    def test_get_roster_not_found(self, mock_get_mongo, mock_db_session):
        """Test when roster is not found."""
        mock_get_mongo.return_value = None
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_roster("999", mock_db_session))

        assert exc_info.value.status_code == 404


# ============================================================================
# EXPORT ROSTER TESTS
# ============================================================================

@pytest.mark.unit
class TestExportRosterJson:
    """Test the export_roster_json endpoint."""

    def test_export_roster_json_success(self, mock_db_session, mock_roster):
        """Test exporting roster as JSON."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_roster

        result = asyncio.run(export_roster_json(1, mock_db_session))

        assert result.status_code == 200

    def test_export_roster_json_not_found(self, mock_db_session):
        """Test export when roster not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(export_roster_json(999, mock_db_session))

        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestDownloadRosterJson:
    """Test the download_roster_json endpoint."""

    def test_download_roster_json_success(self, mock_db_session, mock_roster):
        """Test downloading roster as JSON file."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_roster

        result = asyncio.run(download_roster_json(1, mock_db_session))

        assert result.media_type == "application/json"
        assert "attachment" in result.headers.get("content-disposition", "")

    def test_download_roster_json_not_found(self, mock_db_session):
        """Test download when roster not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(download_roster_json(999, mock_db_session))

        assert exc_info.value.status_code == 404


# ============================================================================
# DELETE ROSTER TESTS
# ============================================================================

@pytest.mark.unit
class TestDeleteRoster:
    """Test the delete_roster endpoint."""

    def test_delete_roster_sql_success(self, mock_db_session, mock_roster):
        """Test deleting a SQL roster."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_roster

        result = asyncio.run(delete_roster("1", mock_db_session))

        assert result is None
        mock_db_session.delete.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("api.routes.roster.delete_roster_from_mongodb")
    def test_delete_roster_mongodb_success(self, mock_delete_mongo, mock_db_session):
        """Test deleting a MongoDB roster."""
        mock_delete_mongo.return_value = True

        result = asyncio.run(delete_roster("64a1b2c3d4e5f6a7b8c9d0e1", mock_db_session))

        assert result is None
        mock_delete_mongo.assert_called_once()

    @patch("api.routes.roster.delete_roster_from_mongodb")
    def test_delete_roster_not_found(self, mock_delete_mongo, mock_db_session):
        """Test deleting when roster not found."""
        mock_delete_mongo.return_value = False
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(delete_roster("999", mock_db_session))

        assert exc_info.value.status_code == 404
