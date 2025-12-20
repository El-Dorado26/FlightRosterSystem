"""
Unit tests for core/mongodb.py MongoDB integration utilities.

Testing Strategy:
- Unit Testing: Test each MongoDB function in isolation
- Mock external dependencies: pymongo MongoClient, Collection operations
- Equivalence Partitioning: Valid/invalid ObjectIds, different query scenarios
- Error handling: Connection failures, invalid data, missing documents
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId


@pytest.mark.unit
class TestMongoDBConnection:
    """Test MongoDB connection management functions."""

    @patch('core.mongodb.MongoClient')
    @patch('core.mongodb.MONGODB_URI', 'mongodb://localhost:27017')
    def test_get_mongodb_client_first_call(self, mock_mongo_client):
        """Test creating MongoDB client on first call."""
        from core.mongodb import get_mongodb_client, _mongo_client

        # Reset global client
        import core.mongodb
        core.mongodb._mongo_client = None

        mock_client_instance = Mock()
        mock_mongo_client.return_value = mock_client_instance

        result = get_mongodb_client()

        assert result == mock_client_instance
        mock_mongo_client.assert_called_once_with('mongodb://localhost:27017')

    @patch('core.mongodb.MongoClient')
    def test_get_mongodb_client_cached(self, mock_mongo_client):
        """Test that subsequent calls return cached client."""
        from core.mongodb import get_mongodb_client

        # Set up cached client
        import core.mongodb
        cached_client = Mock()
        core.mongodb._mongo_client = cached_client

        result = get_mongodb_client()

        assert result == cached_client
        # Should not create new client
        mock_mongo_client.assert_not_called()

    @patch('core.mongodb.get_mongodb_client')
    @patch('core.mongodb.MONGODB_DATABASE', 'test_database')
    def test_get_mongodb_database_first_call(self, mock_get_client):
        """Test getting database on first call."""
        from core.mongodb import get_mongodb_database

        # Reset global database
        import core.mongodb
        core.mongodb._mongo_db = None

        mock_client = MagicMock()
        mock_database = Mock()
        mock_client.__getitem__.return_value = mock_database
        mock_get_client.return_value = mock_client

        result = get_mongodb_database()

        assert result == mock_database
        mock_client.__getitem__.assert_called_once_with('test_database')

    @patch('core.mongodb.get_mongodb_client')
    def test_get_mongodb_database_cached(self, mock_get_client):
        """Test that subsequent calls return cached database."""
        from core.mongodb import get_mongodb_database

        # Set up cached database
        import core.mongodb
        cached_db = Mock()
        core.mongodb._mongo_db = cached_db

        result = get_mongodb_database()

        assert result == cached_db
        mock_get_client.assert_not_called()

    @patch('core.mongodb.get_mongodb_database')
    def test_get_rosters_collection(self, mock_get_db):
        """Test getting rosters collection."""
        from core.mongodb import get_rosters_collection

        mock_db = MagicMock()
        mock_collection = Mock()
        mock_db.__getitem__.return_value = mock_collection
        mock_get_db.return_value = mock_db

        result = get_rosters_collection()

        assert result == mock_collection
        mock_db.__getitem__.assert_called_once_with('rosters')

    @patch('core.mongodb.get_mongodb_client')
    def test_test_mongodb_connection_success(self, mock_get_client):
        """Test successful MongoDB connection test."""
        from core.mongodb import test_mongodb_connection

        mock_client = Mock()
        mock_admin = Mock()
        mock_client.admin = mock_admin
        mock_admin.command.return_value = {'ok': 1}
        mock_get_client.return_value = mock_client

        result = test_mongodb_connection()

        assert result is True
        mock_admin.command.assert_called_once_with('ping')

    @patch('core.mongodb.get_mongodb_client')
    def test_test_mongodb_connection_failure(self, mock_get_client):
        """Test MongoDB connection test failure."""
        from core.mongodb import test_mongodb_connection

        mock_client = Mock()
        mock_admin = Mock()
        mock_client.admin = mock_admin
        mock_admin.command.side_effect = Exception("Connection failed")
        mock_get_client.return_value = mock_client

        result = test_mongodb_connection()

        assert result is False

    def test_close_mongodb_connection_with_client(self):
        """Test closing existing MongoDB connection."""
        from core.mongodb import close_mongodb_connection

        # Set up active client
        import core.mongodb
        mock_client = Mock()
        core.mongodb._mongo_client = mock_client
        core.mongodb._mongo_db = Mock()

        close_mongodb_connection()

        mock_client.close.assert_called_once()
        assert core.mongodb._mongo_client is None
        assert core.mongodb._mongo_db is None

    def test_close_mongodb_connection_no_client(self):
        """Test closing when no client exists."""
        from core.mongodb import close_mongodb_connection

        # Reset globals
        import core.mongodb
        core.mongodb._mongo_client = None
        core.mongodb._mongo_db = None

        # Should not raise exception
        close_mongodb_connection()


@pytest.mark.unit
class TestMongoDBCRUDOperations:
    """Test MongoDB CRUD operations for rosters."""

    @patch('core.mongodb.get_rosters_collection')
    def test_save_roster_to_mongodb_success(self, mock_get_collection):
        """Test successfully saving a roster to MongoDB."""
        from core.mongodb import save_roster_to_mongodb

        mock_collection = Mock()
        mock_result = Mock()
        mock_result.inserted_id = ObjectId('507f1f77bcf86cd799439011')
        mock_collection.insert_one.return_value = mock_result
        mock_get_collection.return_value = mock_collection

        roster_data = {
            "flight_id": 1,
            "crew_data": [],
            "passenger_data": []
        }

        result = save_roster_to_mongodb(roster_data)

        assert result == '507f1f77bcf86cd799439011'
        mock_collection.insert_one.assert_called_once_with(roster_data)

    @patch('core.mongodb.get_rosters_collection')
    def test_get_roster_from_mongodb_success(self, mock_get_collection):
        """Test successfully retrieving a roster from MongoDB."""
        from core.mongodb import get_roster_from_mongodb

        mock_collection = Mock()
        roster_id = '507f1f77bcf86cd799439011'

        mock_roster = {
            "_id": ObjectId(roster_id),
            "flight_id": 1,
            "crew_data": []
        }
        mock_collection.find_one.return_value = mock_roster
        mock_get_collection.return_value = mock_collection

        result = get_roster_from_mongodb(roster_id)

        assert result is not None
        assert result["id"] == roster_id
        assert "_id" not in result
        assert result["flight_id"] == 1

    @patch('core.mongodb.get_rosters_collection')
    def test_get_roster_from_mongodb_not_found(self, mock_get_collection):
        """Test retrieving non-existent roster."""
        from core.mongodb import get_roster_from_mongodb

        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_get_collection.return_value = mock_collection

        result = get_roster_from_mongodb('507f1f77bcf86cd799439011')

        assert result is None

    @patch('core.mongodb.get_rosters_collection')
    def test_get_roster_from_mongodb_invalid_id(self, mock_get_collection):
        """Test retrieving roster with invalid ObjectId."""
        from core.mongodb import get_roster_from_mongodb

        mock_collection = Mock()
        mock_collection.find_one.side_effect = Exception("Invalid ObjectId")
        mock_get_collection.return_value = mock_collection

        result = get_roster_from_mongodb('invalid_id')

        assert result is None

    @patch('core.mongodb.get_rosters_collection')
    def test_list_rosters_from_mongodb_no_filter(self, mock_get_collection):
        """Test listing all rosters without filters."""
        from core.mongodb import list_rosters_from_mongodb

        mock_collection = Mock()
        mock_rosters = [
            {
                "_id": ObjectId('507f1f77bcf86cd799439011'),
                "flight_id": 1,
                "generated_at": "2024-01-01"
            },
            {
                "_id": ObjectId('507f1f77bcf86cd799439012'),
                "flight_id": 2,
                "generated_at": "2024-01-02"
            }
        ]

        # Mock the query chain
        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_rosters
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        result = list_rosters_from_mongodb()

        assert len(result) == 2
        assert result[0]["id"] == '507f1f77bcf86cd799439011'
        assert result[1]["id"] == '507f1f77bcf86cd799439012'
        assert "_id" not in result[0]
        assert "_id" not in result[1]
        mock_collection.find.assert_called_once_with({})
        mock_cursor.sort.assert_called_once_with("generated_at", -1)
        mock_cursor.limit.assert_called_once_with(100)

    @patch('core.mongodb.get_rosters_collection')
    def test_list_rosters_from_mongodb_with_flight_filter(self, mock_get_collection):
        """Test listing rosters filtered by flight_id."""
        from core.mongodb import list_rosters_from_mongodb

        mock_collection = Mock()
        mock_rosters = [
            {
                "_id": ObjectId('507f1f77bcf86cd799439011'),
                "flight_id": 5,
                "generated_at": "2024-01-01"
            }
        ]

        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_rosters
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        result = list_rosters_from_mongodb(flight_id=5)

        assert len(result) == 1
        assert result[0]["flight_id"] == 5
        mock_collection.find.assert_called_once_with({"flight_id": 5})

    @patch('core.mongodb.get_rosters_collection')
    def test_list_rosters_from_mongodb_with_limit(self, mock_get_collection):
        """Test listing rosters with custom limit."""
        from core.mongodb import list_rosters_from_mongodb

        mock_collection = Mock()
        mock_rosters = []

        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_rosters
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        result = list_rosters_from_mongodb(limit=50)

        mock_cursor.limit.assert_called_once_with(50)

    @patch('core.mongodb.get_rosters_collection')
    def test_delete_roster_from_mongodb_success(self, mock_get_collection):
        """Test successfully deleting a roster."""
        from core.mongodb import delete_roster_from_mongodb

        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_result
        mock_get_collection.return_value = mock_collection

        roster_id = '507f1f77bcf86cd799439011'
        result = delete_roster_from_mongodb(roster_id)

        assert result is True
        mock_collection.delete_one.assert_called_once()

    @patch('core.mongodb.get_rosters_collection')
    def test_delete_roster_from_mongodb_not_found(self, mock_get_collection):
        """Test deleting non-existent roster."""
        from core.mongodb import delete_roster_from_mongodb

        mock_collection = Mock()
        mock_result = Mock()
        mock_result.deleted_count = 0
        mock_collection.delete_one.return_value = mock_result
        mock_get_collection.return_value = mock_collection

        result = delete_roster_from_mongodb('507f1f77bcf86cd799439011')

        assert result is False

    @patch('core.mongodb.get_rosters_collection')
    def test_delete_roster_from_mongodb_invalid_id(self, mock_get_collection):
        """Test deleting with invalid ObjectId."""
        from core.mongodb import delete_roster_from_mongodb

        mock_collection = Mock()
        mock_collection.delete_one.side_effect = Exception("Invalid ObjectId")
        mock_get_collection.return_value = mock_collection

        result = delete_roster_from_mongodb('invalid_id')

        assert result is False


@pytest.mark.unit
class TestMongoDBEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch('core.mongodb.get_rosters_collection')
    def test_save_empty_roster_data(self, mock_get_collection):
        """Test saving roster with minimal data."""
        from core.mongodb import save_roster_to_mongodb

        mock_collection = Mock()
        mock_result = Mock()
        mock_result.inserted_id = ObjectId('507f1f77bcf86cd799439011')
        mock_collection.insert_one.return_value = mock_result
        mock_get_collection.return_value = mock_collection

        roster_data = {}
        result = save_roster_to_mongodb(roster_data)

        assert result == '507f1f77bcf86cd799439011'

    @patch('core.mongodb.get_rosters_collection')
    def test_list_rosters_empty_result(self, mock_get_collection):
        """Test listing when no rosters exist."""
        from core.mongodb import list_rosters_from_mongodb

        mock_collection = Mock()
        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        result = list_rosters_from_mongodb()

        assert result == []

    @patch('core.mongodb.get_rosters_collection')
    def test_list_rosters_with_flight_filter_and_limit(self, mock_get_collection):
        """Test listing with both flight_id filter and custom limit."""
        from core.mongodb import list_rosters_from_mongodb

        mock_collection = Mock()
        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = []
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        result = list_rosters_from_mongodb(flight_id=10, limit=25)

        mock_collection.find.assert_called_once_with({"flight_id": 10})
        mock_cursor.limit.assert_called_once_with(25)


@pytest.mark.unit
class TestMongoDBObjectIdHandling:
    """Test ObjectId conversion and handling."""

    @patch('core.mongodb.get_rosters_collection')
    def test_object_id_to_string_conversion(self, mock_get_collection):
        """Test that ObjectId is properly converted to string."""
        from core.mongodb import get_roster_from_mongodb

        mock_collection = Mock()
        original_id = ObjectId('507f1f77bcf86cd799439011')

        mock_roster = {
            "_id": original_id,
            "data": "test"
        }
        mock_collection.find_one.return_value = mock_roster
        mock_get_collection.return_value = mock_collection

        result = get_roster_from_mongodb('507f1f77bcf86cd799439011')

        # Check conversion
        assert isinstance(result["id"], str)
        assert result["id"] == '507f1f77bcf86cd799439011'

    @patch('core.mongodb.get_rosters_collection')
    def test_multiple_object_ids_conversion(self, mock_get_collection):
        """Test ObjectId conversion in list results."""
        from core.mongodb import list_rosters_from_mongodb

        mock_collection = Mock()
        mock_rosters = [
            {"_id": ObjectId('507f1f77bcf86cd799439011'), "data": "1"},
            {"_id": ObjectId('507f1f77bcf86cd799439012'), "data": "2"},
            {"_id": ObjectId('507f1f77bcf86cd799439013'), "data": "3"}
        ]

        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_rosters
        mock_collection.find.return_value = mock_cursor
        mock_get_collection.return_value = mock_collection

        result = list_rosters_from_mongodb()

        # Check all conversions
        for i, roster in enumerate(result):
            assert isinstance(roster["id"], str)
            assert "_id" not in roster
