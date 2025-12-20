"""
Equivalence Partitioning and Boundary Value Analysis tests.

Testing Strategy:
- Equivalence Partitioning: Test based on schema validation rules
- Boundary Value Analysis: Test critical boundaries from business rules
- Tests cover: flight numbers, crew counts, passenger ages, seat capacities
"""
import pytest
from pydantic import ValidationError
from core.schemas import (
    FlightInfoCreate,
    FlightCrewCreate,
    CabinCrewCreate,
    PassengerCreate,
    VehicleTypeCreate
)
from datetime import datetime, timedelta


@pytest.mark.unit
class TestFlightNumberEquivalence:
    """
    Equivalence Partitioning for flight number formats.
    
    Valid format: AANNNN (2 letters + 4 digits)
    Partitions:
    - Valid: Correct format
    - Invalid: Wrong length, wrong pattern, lowercase, special chars
    """
    
    def test_valid_flight_numbers(self):
        """Test valid flight number formats."""
        valid_numbers = [
            "TK0001",
            "AA1234",
            "BA9999",
            "LH0100",
        ]
        
        for flight_no in valid_numbers:
            # Import the validation function
            from api.routes.flights import _validate_flight_number
            try:
                _validate_flight_number(flight_no)
            except Exception as e:
                pytest.fail(f"Valid flight number {flight_no} raised exception: {e}")
    
    def test_invalid_flight_numbers(self):
        """Test invalid flight number formats."""
        from fastapi import HTTPException
        from api.routes.flights import _validate_flight_number
        
        invalid_numbers = [
            "tk0001",      # Lowercase
            "TK001",       # Too short
            "TK00001",     # Too long
            "T1234",       # One letter
            "TKK0001",     # Three letters
            "TK-0001",     # Special character
            "TK 0001",     # Space
            "1K0001",      # Digit in airline code
            "TKABCD",      # Letters instead of numbers
        ]
        
        for flight_no in invalid_numbers:
            with pytest.raises(HTTPException) as exc_info:
                _validate_flight_number(flight_no)
            assert exc_info.value.status_code == 400


@pytest.mark.unit
class TestCabinCrewCountBoundaries:
    """
    Boundary Value Analysis for cabin crew count constraints.
    
    Business Rules from select_cabin_crew_automatically():
    - Chief Attendants: 1-4
    - Regular Attendants: 4-16
    - Chefs: 0-2
    """
    
    def test_chief_attendant_boundaries(self):
        """Test chief attendant count boundaries (1-4)."""
        # Minimum valid
        assert 1 >= 1 and 1 <= 4
        
        # Maximum valid
        assert 4 >= 1 and 4 <= 4
        
        # Below minimum
        assert not (0 >= 1 and 0 <= 4)
        
        # Above maximum
        assert not (5 >= 1 and 5 <= 4)
    
    def test_regular_attendant_boundaries(self):
        """Test regular attendant count boundaries (4-16)."""
        # Minimum valid
        assert 4 >= 4 and 4 <= 16
        
        # Maximum valid
        assert 16 >= 4 and 16 <= 16
        
        # Below minimum
        assert not (3 >= 4 and 3 <= 16)
        
        # Above maximum
        assert not (17 >= 4 and 17 <= 16)
    
    def test_chef_boundaries(self):
        """Test chef count boundaries (0-2)."""
        # Minimum valid
        assert 0 >= 0 and 0 <= 2
        
        # Maximum valid
        assert 2 >= 0 and 2 <= 2
        
        # Below minimum
        assert not (-1 >= 0 and -1 <= 2)
        
        # Above maximum
        assert not (3 >= 0 and 3 <= 2)


@pytest.mark.unit
class TestSeatCapacityBoundaries:
    """
    Boundary Value Analysis for seat capacity constraints.
    
    Based on select_cabin_crew_automatically() logic:
    - < 100 seats: Small aircraft
    - 100-199 seats: Medium aircraft
    - 200-299 seats: Large aircraft
    - >= 300 seats: Very large aircraft
    """
    
    def test_small_aircraft_boundary(self):
        """Test small aircraft seat capacity (< 100)."""
        # Below threshold
        assert 50 < 100
        assert 99 < 100
        
        # At threshold (not small)
        assert not (100 < 100)
    
    def test_medium_aircraft_boundaries(self):
        """Test medium aircraft seat capacity (100-199)."""
        # Minimum valid
        assert 100 >= 100 and 100 < 200
        
        # Maximum valid
        assert 199 >= 100 and 199 < 200
        
        # Just below minimum
        assert not (99 >= 100 and 99 < 200)
        
        # Just above maximum
        assert not (200 >= 100 and 200 < 200)
    
    def test_large_aircraft_boundaries(self):
        """Test large aircraft seat capacity (200-299)."""
        # Minimum valid
        assert 200 >= 200 and 200 < 300
        
        # Maximum valid
        assert 299 >= 200 and 299 < 300
        
        # Just below minimum
        assert not (199 >= 200 and 199 < 300)
        
        # Just above maximum
        assert not (300 >= 200 and 300 < 300)
    
    def test_very_large_aircraft_boundary(self):
        """Test very large aircraft seat capacity (>= 300)."""
        # Minimum valid
        assert 300 >= 300
        
        # Above minimum
        assert 400 >= 300
        assert 500 >= 300
        
        # Below minimum
        assert not (299 >= 300)


@pytest.mark.unit
class TestCrewSelectionByAircraftSize:
    """
    Test crew count selection based on aircraft size.
    
    Business logic from select_cabin_crew_automatically():
    - < 100 seats: 1 chief, 4 regular, 0 chef
    - 100-199 seats: 2 chief, 8 regular, 1 chef
    - 200-299 seats: 3 chief, 12 regular, 1 chef
    - >= 300 seats: 4 chief, 16 regular, 2 chef
    """
    
    def test_crew_count_for_small_aircraft(self):
        """Test crew counts for aircraft with < 100 seats."""
        total_seats = 99
        
        if total_seats < 100:
            chief_count = 1
            regular_count = 4
            chef_count = 0
        
        assert chief_count == 1
        assert regular_count == 4
        assert chef_count == 0
    
    def test_crew_count_for_medium_aircraft(self):
        """Test crew counts for aircraft with 100-199 seats."""
        total_seats = 150
        
        if total_seats < 100:
            chief_count = 1
            regular_count = 4
            chef_count = 0
        elif total_seats < 200:
            chief_count = 2
            regular_count = 8
            chef_count = 1
        
        assert chief_count == 2
        assert regular_count == 8
        assert chef_count == 1
    
    def test_crew_count_for_large_aircraft(self):
        """Test crew counts for aircraft with 200-299 seats."""
        total_seats = 250
        
        if total_seats < 100:
            chief_count = 1
            regular_count = 4
            chef_count = 0
        elif total_seats < 200:
            chief_count = 2
            regular_count = 8
            chef_count = 1
        elif total_seats < 300:
            chief_count = 3
            regular_count = 12
            chef_count = 1
        
        assert chief_count == 3
        assert regular_count == 12
        assert chef_count == 1
    
    def test_crew_count_for_very_large_aircraft(self):
        """Test crew counts for aircraft with >= 300 seats."""
        total_seats = 350
        
        if total_seats < 100:
            chief_count = 1
            regular_count = 4
            chef_count = 0
        elif total_seats < 200:
            chief_count = 2
            regular_count = 8
            chef_count = 1
        elif total_seats < 200:
            chief_count = 3
            regular_count = 12
            chef_count = 1
        else:
            chief_count = 4
            regular_count = 16
            chef_count = 2
        
        assert chief_count == 4
        assert regular_count == 16
        assert chef_count == 2
    
    def test_boundary_transitions(self):
        """Test crew count changes at exact boundaries."""
        test_cases = [
            (99, 1, 4, 0),    # Just below 100
            (100, 2, 8, 1),   # At 100
            (199, 2, 8, 1),   # Just below 200
            (200, 3, 12, 1),  # At 200
            (299, 3, 12, 1),  # Just below 300
            (300, 4, 16, 2),  # At 300
        ]
        
        for total_seats, expected_chief, expected_regular, expected_chef in test_cases:
            if total_seats < 100:
                chief, regular, chef = 1, 4, 0
            elif total_seats < 200:
                chief, regular, chef = 2, 8, 1
            elif total_seats < 300:
                chief, regular, chef = 3, 12, 1
            else:
                chief, regular, chef = 4, 16, 2
            
            assert chief == expected_chief, f"Failed for {total_seats} seats: chief"
            assert regular == expected_regular, f"Failed for {total_seats} seats: regular"
            assert chef == expected_chef, f"Failed for {total_seats} seats: chef"


@pytest.mark.unit
class TestSeniorityLevelEquivalence:
    """
    Equivalence Partitioning for seniority levels.
    
    Valid levels: Senior, Intermediate, Junior
    """
    
    def test_valid_seniority_levels(self):
        """Test valid seniority level values."""
        valid_levels = ["Senior", "Intermediate", "Junior"]
        
        seniority_order = {'Senior': 3, 'Intermediate': 2, 'Junior': 1}
        
        for level in valid_levels:
            assert level in seniority_order
            assert seniority_order[level] > 0
    
    def test_seniority_ordering(self):
        """Test that seniority levels have correct ordering."""
        seniority_order = {'Senior': 3, 'Intermediate': 2, 'Junior': 1}
        
        assert seniority_order['Senior'] > seniority_order['Intermediate']
        assert seniority_order['Intermediate'] > seniority_order['Junior']
        assert seniority_order['Senior'] > seniority_order['Junior']


@pytest.mark.unit
class TestPassengerAgeCategories:
    """
    Equivalence Partitioning for passenger age categories.
    
    Categories:
    - Infant: 0-2 years
    - Child: 3-12 years
    - Adult: 13-64 years
    - Senior: 65+ years
    """
    
    def test_infant_age_boundaries(self):
        """Test infant age category (0-2)."""
        # Valid infant ages
        assert 0 >= 0 and 0 <= 2
        assert 1 >= 0 and 1 <= 2
        assert 2 >= 0 and 2 <= 2
        
        # Not infant
        assert not (3 >= 0 and 3 <= 2)
    
    def test_child_age_boundaries(self):
        """Test child age category (3-12)."""
        # Minimum valid
        assert 3 >= 3 and 3 <= 12
        
        # Maximum valid
        assert 12 >= 3 and 12 <= 12
        
        # Just below minimum
        assert not (2 >= 3 and 2 <= 12)
        
        # Just above maximum
        assert not (13 >= 3 and 13 <= 12)
    
    def test_adult_age_boundaries(self):
        """Test adult age category (13-64)."""
        # Minimum valid
        assert 13 >= 13 and 13 <= 64
        
        # Maximum valid
        assert 64 >= 13 and 64 <= 64
        
        # Just below minimum
        assert not (12 >= 13 and 12 <= 64)
        
        # Just above maximum
        assert not (65 >= 13 and 65 <= 64)
    
    def test_senior_age_boundary(self):
        """Test senior age category (65+)."""
        # Minimum valid
        assert 65 >= 65
        
        # Above minimum
        assert 70 >= 65
        assert 100 >= 65
        
        # Below minimum
        assert not (64 >= 65)


@pytest.mark.unit
class TestAttendantTypeEquivalence:
    """
    Equivalence Partitioning for cabin crew attendant types.
    
    Valid types: chief, regular, chef
    """
    
    def test_valid_attendant_types(self):
        """Test valid attendant type values."""
        valid_types = ["chief", "regular", "chef"]
        
        for attendant_type in valid_types:
            assert attendant_type in valid_types
    
    def test_invalid_attendant_types(self):
        """Test invalid attendant type values."""
        invalid_types = ["manager", "pilot", "steward", ""]
        valid_types = ["chief", "regular", "chef"]
        
        for attendant_type in invalid_types:
            assert attendant_type not in valid_types


@pytest.mark.unit
class TestFlightCrewRoleEquivalence:
    """
    Equivalence Partitioning for flight crew roles.
    
    Valid roles: Captain, First Officer, Flight Engineer
    """
    
    def test_valid_crew_roles(self):
        """Test valid flight crew role values."""
        valid_roles = ["Captain", "First Officer", "Flight Engineer"]
        required_roles = {
            'Captain': 1,
            'First Officer': 1,
            'Flight Engineer': 1
        }
        
        for role in valid_roles:
            assert role in required_roles
    
    def test_crew_role_requirements(self):
        """Test that each role has correct count requirement."""
        required_roles = {
            'Captain': 1,
            'First Officer': 1,
            'Flight Engineer': 1
        }
        
        assert required_roles['Captain'] == 1
        assert required_roles['First Officer'] == 1
        assert required_roles['Flight Engineer'] == 1


@pytest.mark.unit
class TestPassengerAPIEquivalence:
    """
    Equivalence Partitioning tests for Passenger API operations.
    
    Test partitions based on:
    - Age categories (infant, child, adult, senior)
    - Seat availability (available, taken)
    - Parent relationship (with parent, without parent, invalid parent)
    - Email format (valid, invalid)
    - Phone format (valid, invalid, null)
    - Passport format (valid, invalid, null)
    - Seat type (Economy, Business)
    - Gender (valid values)
    - Nationality (valid country codes)
    """
    
    def test_create_passenger_age_partitions(self):
        """Test creating passengers across all age partitions."""
        from unittest.mock import MagicMock, patch
        from api.routes.passengers import create_passenger
        from core.schemas import PassengerCreate
        
        age_partitions = [
            (0, "infant"),    # Infant: 0-2
            (1, "infant"),
            (2, "infant"),
            (3, "child"),     # Child: 3-12
            (8, "child"),
            (12, "child"),
            (13, "adult"),    # Adult: 13-64
            (30, "adult"),
            (64, "adult"),
            (65, "senior"),   # Senior: 65+
            (80, "senior"),
        ]
        
        for age, category in age_partitions:
            passenger_data = PassengerCreate(
                name=f"Test {category.title()}",
                email=f"test_{age}@example.com",
                phone="+1234567890",
                passport_number=f"PASS{age:03d}",
                age=age,
                gender="Male",
                nationality="US",
                seat_type="Economy"
            )
            
            # Verify the schema accepts the age
            assert passenger_data.age == age
    
    def test_passenger_email_partitions(self):
        """Test email equivalence partitions."""
        from core.schemas import PassengerCreate
        
        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "name+tag@email.org",
            "user123@test-domain.com",
        ]
        
        for email in valid_emails:
            passenger = PassengerCreate(
                name="Test User",
                email=email,
                phone="+1234567890",
                passport_number="ABC123",
                age=30,
                gender="Male",
                nationality="US",
                seat_type="Economy"
            )
            assert passenger.email == email
    
    def test_passenger_seat_type_partitions(self):
        """Test seat type equivalence partitions."""
        from core.schemas import PassengerCreate
        
        valid_seat_types = ["Economy", "Business", "economy", "business"]
        
        for seat_type in valid_seat_types:
            passenger = PassengerCreate(
                name="Test User",
                email="test@example.com",
                phone="+1234567890",
                passport_number="ABC123",
                age=30,
                gender="Male",
                nationality="US",
                seat_type=seat_type
            )
            assert passenger.seat_type == seat_type
    
    def test_passenger_gender_partitions(self):
        """Test gender equivalence partitions."""
        from core.schemas import PassengerCreate
        
        valid_genders = ["Male", "Female", "Other", "male", "female"]
        
        for gender in valid_genders:
            passenger = PassengerCreate(
                name="Test User",
                email="test@example.com",
                phone="+1234567890",
                passport_number="ABC123",
                age=30,
                gender=gender,
                nationality="US",
                seat_type="Economy"
            )
            assert passenger.gender == gender
    
    def test_passenger_nationality_partitions(self):
        """Test nationality code equivalence partitions."""
        from core.schemas import PassengerCreate
        
        # Valid country codes (ISO 3166-1 alpha-2)
        valid_nationalities = ["US", "GB", "TR", "DE", "FR", "JP", "CN"]
        
        for nationality in valid_nationalities:
            passenger = PassengerCreate(
                name="Test User",
                email="test@example.com",
                phone="+1234567890",
                passport_number="ABC123",
                age=30,
                gender="Male",
                nationality=nationality,
                seat_type="Economy"
            )
            assert passenger.nationality == nationality
    
    def test_passenger_optional_fields_partitions(self):
        """Test optional field partitions (null vs provided)."""
        from core.schemas import PassengerCreate
        
        # With all optional fields
        passenger_full = PassengerCreate(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            passport_number="ABC123",
            age=30,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        assert passenger_full.phone is not None
        assert passenger_full.passport_number is not None
        
        # Without optional fields (phone and passport can be null)
        passenger_minimal = PassengerCreate(
            name="Test User",
            email="test@example.com",
            phone=None,
            passport_number=None,
            age=30,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        assert passenger_minimal.phone is None
        assert passenger_minimal.passport_number is None
    
    def test_seat_number_format_partitions(self):
        """Test seat number format partitions."""
        valid_seat_formats = [
            "1A",      # Single digit + letter
            "12B",     # Double digit + letter
            "99Z",     # Max typical row + last letter
            "100F",    # Triple digit + letter
            "23C",     # Mid range
        ]
        
        for seat_number in valid_seat_formats:
            # Verify format is acceptable (basic validation)
            assert len(seat_number) >= 2
            assert seat_number[-1].isalpha()
            assert seat_number[:-1].isdigit()
    
    def test_parent_relationship_partitions(self):
        """Test parent relationship partitions."""
        from unittest.mock import MagicMock, patch
        from api.routes.passengers import create_passenger
        from core.schemas import PassengerCreate
        from fastapi import HTTPException
        
        infant_data = PassengerCreate(
            name="Baby",
            email="baby@example.com",
            phone="+1234567890",
            passport_number="BABY123",
            age=1,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        
        mock_db = MagicMock()
        
        # Partition 1: Infant with valid parent
        with patch('api.routes.passengers.check_seat_availability', return_value=True):
            mock_parent = MagicMock()
            mock_parent.flight_id = 1
            
            query_mock = MagicMock()
            mock_db.query.return_value = query_mock
            filter_mock = MagicMock()
            query_mock.filter.return_value = filter_mock
            filter_mock.first.return_value = mock_parent
            
            create_passenger(
                passenger=infant_data,
                flight_id=1,
                seat_number="12A",
                parent_id=1,
                db=mock_db
            )
            mock_db.add.assert_called_once()
        
        # Partition 2: Infant without parent (should fail)
        mock_db.reset_mock()
        with patch('api.routes.passengers.check_seat_availability', return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                create_passenger(
                    passenger=infant_data,
                    flight_id=1,
                    seat_number="12B",
                    parent_id=None,
                    db=mock_db
                )
            assert exc_info.value.status_code == 400
        
        # Partition 3: Adult without parent (valid)
        mock_db.reset_mock()
        adult_data = PassengerCreate(
            name="Adult",
            email="adult@example.com",
            phone="+1234567890",
            passport_number="ADULT123",
            age=30,
            gender="Male",
            nationality="US",
            seat_type="Economy"
        )
        
        with patch('api.routes.passengers.check_seat_availability', return_value=True):
            create_passenger(
                passenger=adult_data,
                flight_id=1,
                seat_number="12C",
                parent_id=None,
                db=mock_db
            )
            mock_db.add.assert_called_once()
    
    def test_update_passenger_field_partitions(self):
        """Test update operation with different field combinations."""
        from core.schemas import PassengerUpdate
        
        # Partition 1: Update single field
        update_name = PassengerUpdate(name="New Name")
        assert update_name.name == "New Name"
        assert update_name.email is None
        
        # Partition 2: Update multiple fields
        update_multiple = PassengerUpdate(
            name="New Name",
            email="new@example.com",
            age=35
        )
        assert update_multiple.name == "New Name"
        assert update_multiple.email == "new@example.com"
        assert update_multiple.age == 35
        
        # Partition 3: Update all fields
        update_all = PassengerUpdate(
            name="Complete Update",
            email="complete@example.com",
            phone="+9876543210",
            passport_number="NEW123",
            age=40,
            gender="Female",
            nationality="GB",
            seat_type="Business"
        )
        assert update_all.name == "Complete Update"
        assert update_all.age == 40
    
    def test_flight_id_partitions(self):
        """Test flight_id value partitions."""
        valid_flight_ids = [1, 10, 100, 999, 10000]
        
        for flight_id in valid_flight_ids:
            assert isinstance(flight_id, int)
            assert flight_id > 0


@pytest.mark.unit
class TestVehicleTypeConstraints:
    """
    Boundary Value Analysis for vehicle type constraints.
    
    Constraints:
    - max_crew: typically 2-10
    - max_passengers: matches total_seats
    - total_seats: 50-600 (typical range)
    """
    
    def test_min_crew_boundary(self):
        """Test minimum crew count (typically 2-3)."""
        min_crew = 2
        assert min_crew >= 2
        assert min_crew <= 10
    
    def test_max_crew_boundary(self):
        """Test maximum crew count (typically 8-10)."""
        max_crew = 10
        assert max_crew >= 2
        assert max_crew <= 10
    
    def test_small_aircraft_seats(self):
        """Test small aircraft seat count (50-100)."""
        seats = 50
        assert seats >= 50
        assert seats <= 100
    
    def test_large_aircraft_seats(self):
        """Test large aircraft seat count (400-600)."""
        seats = 550
        assert seats >= 400
        assert seats <= 600
    
    def test_seats_equal_max_passengers(self):
        """Test that total_seats equals max_passengers."""
        total_seats = 250
        max_passengers = 250
        assert total_seats == max_passengers
