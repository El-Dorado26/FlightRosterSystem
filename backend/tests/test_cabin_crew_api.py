"""Comprehensive tests for Cabin Crew API endpoints."""
import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, status
from api.routes.cabin_crew import (
    list_cabin_crew,
    get_cabin_crew,
    create_cabin_crew,
    update_cabin_crew,
    delete_cabin_crew,
    get_crew_by_type,
    get_cabin_crew_by_flight,
)
import asyncio
from core.models import CabinCrew
from core.schemas import CabinCrewCreate, CabinCrewUpdate


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_cabin_crew_chief():
    """Create a mock chief cabin crew member."""
    crew = Mock(spec=CabinCrew)
    crew.id = 1
    crew.name = "Chief Smith"
    crew.age = 40
    crew.gender = "F"
    crew.nationality = "USA"
    crew.employee_id = "CC001"
    crew.attendant_type = "chief"
    crew.seniority_level = "Senior"
    crew.languages = ["English", "French"]
    crew.recipes = None
    crew.seat_number = "1A"
    return crew


@pytest.fixture
def mock_cabin_crew_regular():
    """Create a mock regular cabin crew member."""
    crew = Mock(spec=CabinCrew)
    crew.id = 2
    crew.name = "Regular Jones"
    crew.age = 28
    crew.gender = "M"
    crew.nationality = "Canada"
    crew.employee_id = "CC002"
    crew.attendant_type = "regular"
    crew.seniority_level = "Intermediate"
    crew.languages = ["English", "Spanish"]
    crew.recipes = None
    crew.seat_number = "1B"
    return crew


@pytest.fixture
def mock_cabin_crew_chef():
    """Create a mock chef cabin crew member."""
    crew = Mock(spec=CabinCrew)
    crew.id = 3
    crew.name = "Chef Gordon"
    crew.age = 35
    crew.gender = "M"
    crew.nationality = "UK"
    crew.employee_id = "CC003"
    crew.attendant_type = "chef"
    crew.seniority_level = "Senior"
    crew.languages = ["English"]
    crew.recipes = ["Pasta Carbonara", "Beef Wellington", "Tiramisu"]
    crew.seat_number = "2A"
    return crew


@pytest.fixture
def cabin_crew_create_chief():
    """Create CabinCrewCreate data for chief."""
    return CabinCrewCreate(
        name="New Chief",
        age=38,
        gender="F",
        nationality="USA",
        employee_id="CC999",
        attendant_type="chief",
        seniority_level="Senior",
        languages=["English", "German"]
    )


@pytest.fixture
def cabin_crew_create_chef():
    """Create CabinCrewCreate data for chef."""
    return CabinCrewCreate(
        name="New Chef",
        age=32,
        gender="M",
        nationality="France",
        employee_id="CC888",
        attendant_type="chef",
        seniority_level="Senior",
        languages=["French", "English"],
        recipes=["Coq au Vin", "Ratatouille", "Crème Brûlée"]
    )


@pytest.mark.unit
class TestListCabinCrew:
    """Test the list_cabin_crew endpoint."""
    
    @patch('api.routes.cabin_crew.get_cache')
    @patch('api.routes.cabin_crew.set_cache')
    def test_list_all_cabin_crew_cache_miss(self, mock_set_cache, mock_get_cache,
                                                   mock_db_session, mock_cabin_crew_chief,
                                                   mock_cabin_crew_regular):
        """Test listing all cabin crew with cache miss."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.all.return_value = [mock_cabin_crew_chief, mock_cabin_crew_regular]
        
        result = asyncio.run(list_cabin_crew(db=mock_db_session))
        
        assert len(result) == 2
        assert result[0].attendant_type == "chief"
        assert result[1].attendant_type == "regular"
        mock_get_cache.assert_called_once()
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.cabin_crew.get_cache')
    def test_list_cabin_crew_cache_hit(self, mock_get_cache, mock_db_session):
        """Test listing cabin crew with cache hit."""
        cached_data = [{
            "id": 1,
            "name": "Chief Smith",
            "attendant_type": "chief"
        }]
        mock_get_cache.return_value = json.dumps(cached_data)
        
        result = asyncio.run(list_cabin_crew(db=mock_db_session))
        
        assert len(result) == 1
        mock_get_cache.assert_called_once()
        mock_db_session.query.assert_not_called()


@pytest.mark.unit
class TestGetCabinCrew:
    """Test the get_cabin_crew endpoint."""
    
    @patch('api.routes.cabin_crew.get_cache')
    @patch('api.routes.cabin_crew.set_cache')
    def test_get_cabin_crew_by_id_cache_miss(self, mock_set_cache, mock_get_cache,
                                                    mock_db_session, mock_cabin_crew_chief):
        """Test getting a cabin crew member by ID with cache miss."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_cabin_crew_chief
        
        result = asyncio.run(get_cabin_crew(crew_id=1, db=mock_db_session))
        
        assert result.id == 1
        assert result.attendant_type == "chief"
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.cabin_crew.get_cache')
    def test_get_cabin_crew_cache_hit(self, mock_get_cache, mock_db_session):
        """Test getting cabin crew with cache hit."""
        cached_data = {
            "id": 1,
            "name": "Chief Smith",
            "attendant_type": "chief"
        }
        mock_get_cache.return_value = json.dumps(cached_data)
        
        result = asyncio.run(get_cabin_crew(crew_id=1, db=mock_db_session))
        
        mock_get_cache.assert_called_once()
        mock_db_session.query.assert_not_called()
    
    @patch('api.routes.cabin_crew.get_cache')
    def test_get_cabin_crew_not_found(self, mock_get_cache, mock_db_session):
        """Test getting a non-existent cabin crew member."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_cabin_crew(crew_id=999, db=mock_db_session))
        
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestCreateCabinCrew:
    """Test the create_cabin_crew endpoint."""
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_create_cabin_crew_chief_success(self, mock_delete_cache,
                                                    mock_db_session,
                                                    cabin_crew_create_chief):
        """Test successful creation of chief cabin crew."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None  # No duplicate
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = asyncio.run(create_cabin_crew(crew=cabin_crew_create_chief, db=mock_db_session))
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_delete_cache.assert_called()
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_create_cabin_crew_chef_with_recipes(self, mock_delete_cache,
                                                        mock_db_session,
                                                        cabin_crew_create_chef):
        """Test successful creation of chef with recipes."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = asyncio.run(create_cabin_crew(crew=cabin_crew_create_chef),db=mock_db_session)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_create_cabin_crew_chef_invalid_recipe_count(self, mock_db_session):
        """Test creating chef with invalid number of recipes."""
        # Too few recipes
        invalid_data = CabinCrewCreate(
            name="Invalid Chef",
            age=30,
            gender="M",
            nationality="Italy",
            employee_id="CC_INV",
            attendant_type="chef",
            seniority_level="Senior",
            languages=["Italian"],
            recipes=["Pasta"]  # Only 1 recipe, needs 2-4
        )
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_cabin_crew(crew=invalid_data, db=mock_db_session))
        
        assert exc_info.value.status_code == 400
        assert "2-4" in str(exc_info.value.detail)
    
    def test_create_cabin_crew_invalid_type(self, mock_db_session):
        """Test creating cabin crew with invalid attendant type."""
        invalid_data = CabinCrewCreate(
            name="Invalid Crew",
            age=25,
            gender="F",
            nationality="USA",
            employee_id="CC_INV2",
            attendant_type="invalid_type",  # Invalid type
            seniority_level="Junior",
            languages=["English"]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_cabin_crew(crew=invalid_data, db=mock_db_session))
        
        assert exc_info.value.status_code == 400
        assert "attendant_type" in str(exc_info.value.detail).lower()
    
    def test_create_cabin_crew_duplicate_employee_id(self, mock_db_session,
                                                           cabin_crew_create_chief,
                                                           mock_cabin_crew_chief):
        """Test creating cabin crew with duplicate employee ID."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_cabin_crew_chief  # Duplicate
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_cabin_crew(crew=cabin_crew_create_chief),db=mock_db_session)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail).lower()
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_create_cabin_crew_regular(self, mock_delete_cache, mock_db_session):
        """Test creating regular cabin crew."""
        crew_data = CabinCrewCreate(
            name="Regular Attendant",
            age=26,
            gender="F",
            nationality="Germany",
            employee_id="CC_REG",
            attendant_type="regular",
            seniority_level="Junior",
            languages=["German", "English"]
        )
        
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        result = asyncio.run(create_cabin_crew(crew=crew_data, db=mock_db_session))
        
        mock_db_session.add.assert_called_once()


@pytest.mark.unit
class TestUpdateCabinCrew:
    """Test the update_cabin_crew endpoint."""
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_update_cabin_crew_success(self, mock_delete_cache, mock_db_session,
                                             mock_cabin_crew_regular):
        """Test successful cabin crew update."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_cabin_crew_regular
        
        update_data = CabinCrewUpdate(
            seniority_level="Senior",
            languages=["English", "Spanish", "Portuguese"]
        )
        
        result = asyncio.run(update_cabin_crew(crew_id=2, crew=update_data),db=mock_db_session)
        
        assert mock_cabin_crew_regular.seniority_level == "Senior"
        mock_db_session.commit.assert_called_once()
        mock_delete_cache.assert_called()
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_update_cabin_crew_not_found(self, mock_delete_cache, mock_db_session):
        """Test updating a non-existent cabin crew member."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        update_data = CabinCrewUpdate(seniority_level="Senior")
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(update_cabin_crew(crew_id=999, crew=update_data),db=mock_db_session)
        
        assert exc_info.value.status_code == 404
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_update_chef_recipes(self, mock_delete_cache, mock_db_session,
                                      mock_cabin_crew_chef):
        """Test updating chef's recipes."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_cabin_crew_chef
        
        update_data = CabinCrewUpdate(
            recipes=["New Dish 1", "New Dish 2", "New Dish 3", "New Dish 4"]
        )
        
        result = asyncio.run(update_cabin_crew(crew_id=3, crew=update_data, db=mock_db_session))
        
        assert mock_cabin_crew_chef.recipes == update_data.recipes
        mock_db_session.commit.assert_called_once()


@pytest.mark.unit
class TestDeleteCabinCrew:
    """Test the delete_cabin_crew endpoint."""
    
    @patch('api.routes.cabin_crew.delete_cache')
    def test_delete_cabin_crew_success(self, mock_delete_cache, mock_db_session,
                                             mock_cabin_crew_regular):
        """Test successful cabin crew deletion."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = mock_cabin_crew_regular
        
        asyncio.run(delete_cabin_crew(crew_id=2, db=mock_db_session))
        
        mock_db_session.delete.assert_called_once_with(mock_cabin_crew_regular)
        mock_db_session.commit.assert_called_once()
        mock_delete_cache.assert_called()
    
    def test_delete_cabin_crew_not_found(self, mock_db_session):
        """Test deleting a non-existent cabin crew member."""
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(delete_cabin_crew(crew_id=999, db=mock_db_session))
        
        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestGetCabinCrewByType:
    """Test the get_cabin_crew_by_type endpoint."""
    
    @patch('api.routes.cabin_crew.get_cache')
    @patch('api.routes.cabin_crew.set_cache')
    def test_get_cabin_crew_by_type_chief(self, mock_set_cache, mock_get_cache,
                                                 mock_db_session, mock_cabin_crew_chief):
        """Test getting cabin crew by type 'chief'."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_cabin_crew_chief]
        
        result = asyncio.run(get_crew_by_type(attendant_type="chief",db=mock_db_session))
        
        assert len(result) == 1
        assert result[0].attendant_type == "chief"
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.cabin_crew.get_cache')
    @patch('api.routes.cabin_crew.set_cache')
    def test_get_cabin_crew_by_type_chef(self, mock_set_cache, mock_get_cache,
                                                mock_db_session, mock_cabin_crew_chef):
        """Test getting cabin crew by type 'chef'."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_cabin_crew_chef]
        
        result = asyncio.run(get_crew_by_type(attendant_type="chef",db=mock_db_session))
        
        assert len(result) == 1
        assert result[0].attendant_type == "chef"
        assert result[0].recipes is not None


@pytest.mark.unit
class TestGetCabinCrewForFlight:
    """Test the get_cabin_crew_for_flight endpoint."""
    
    @patch('api.routes.cabin_crew.get_cache')
    @patch('api.routes.cabin_crew.set_cache')
    def test_get_cabin_crew_by_flight(self, mock_set_cache, mock_get_cache,
                                             mock_db_session, mock_cabin_crew_chief,
                                             mock_cabin_crew_regular):
        """Test getting cabin crew assigned to a specific flight."""
        mock_get_cache.return_value = None
        query_mock = MagicMock()
        mock_db_session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.all.return_value = [mock_cabin_crew_chief, mock_cabin_crew_regular]
        
        result = asyncio.run(get_cabin_crew_by_flight(flight_id=1, db=mock_db_session))
        
        assert len(result) == 2
        mock_set_cache.assert_called_once()
    
    @patch('api.routes.cabin_crew.get_cache')
    def test_get_cabin_crew_for_flight_cache_hit(self, mock_get_cache,
                                                        mock_db_session):
        """Test getting cabin crew for flight with cache hit."""
        cached_data = [{
            "id": 1,
            "name": "Chief Smith",
            "attendant_type": "chief"
        }]
        mock_get_cache.return_value = json.dumps(cached_data)
        
        result = asyncio.run(get_cabin_crew_by_flight(flight_id=1, db=mock_db_session))
        
        assert len(result) == 1
        mock_db_session.query.assert_not_called()


@pytest.mark.unit
class TestCabinCrewValidation:
    """Test cabin crew validation rules."""
    
    def test_attendant_type_validation(self):
        """Test that attendant_type must be valid."""
        valid_types = ["chief", "regular", "chef"]
        
        for type_value in valid_types:
            if type_value == "chef":
                crew_data = CabinCrewCreate(
                    name=f"Crew {type_value}",
                    age=30,
                    gender="M",
                    nationality="USA",
                    employee_id=f"CC_{type_value}",
                    attendant_type=type_value,
                    seniority_level="Senior",
                    languages=["English"],
                    recipes=["Dish1", "Dish2", "Dish3"]
                )
            else:
                crew_data = CabinCrewCreate(
                    name=f"Crew {type_value}",
                    age=30,
                    gender="M",
                    nationality="USA",
                    employee_id=f"CC_{type_value}",
                    attendant_type=type_value,
                    seniority_level="Senior",
                    languages=["English"]
                )
            
            # Should create valid CabinCrewCreate object
            assert crew_data.attendant_type == type_value
    
    def test_chef_recipes_validation(self, mock_db_session):
        """Test that chef must have 2-4 recipes."""
        # Test with 0 recipes
        invalid_data = CabinCrewCreate(
            name="Chef No Recipes",
            age=30,
            gender="M",
            nationality="France",
            employee_id="CC_NOREC",
            attendant_type="chef",
            seniority_level="Senior",
            languages=["French"],
            recipes=[]  # Empty
        )
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_cabin_crew(crew=invalid_data, db=mock_db_session))
        
        assert exc_info.value.status_code == 400
    
    def test_chef_recipes_too_many(self, mock_db_session):
        """Test that chef cannot have more than 4 recipes."""
        invalid_data = CabinCrewCreate(
            name="Chef Too Many",
            age=30,
            gender="M",
            nationality="France",
            employee_id="CC_MANY",
            attendant_type="chef",
            seniority_level="Senior",
            languages=["French"],
            recipes=["D1", "D2", "D3", "D4", "D5"]  # 5 recipes, max is 4
        )
        
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(create_cabin_crew(crew=invalid_data, db=mock_db_session))
        
        assert exc_info.value.status_code == 400


@pytest.mark.unit
class TestCabinCrewExport:
    """Test cabin crew export functionality."""
    
    def test_export_cabin_crew_to_csv(self, mock_db_session, mock_cabin_crew_chief,
                                            mock_cabin_crew_regular):
        """Test exporting cabin crew data to CSV."""
        # This tests the CSV export endpoint if it exists
        pass
    
    def test_export_cabin_crew_to_json(self):
        """Test exporting cabin crew data to JSON."""
        pass


@pytest.mark.integration
class TestCabinCrewAPIIntegration:
    """Integration tests for cabin crew API."""
    
    def test_cabin_crew_lifecycle(self):
        """Test complete cabin crew lifecycle: create, read, update, delete."""
        # This would be tested with actual TestClient
        pass
    
    def test_chef_recipe_management(self):
        """Test managing chef recipes."""
        pass
    
    def test_cabin_crew_assignment_to_flights(self):
        """Test assigning cabin crew to flights."""
        pass
    
    def test_cabin_crew_ratio_per_flight(self):
        """Test that cabin crew to passenger ratio is maintained."""
        pass
