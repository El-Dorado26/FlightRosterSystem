"""Tests for core database module.

This test module covers the database.py module which has 55% coverage.
Tests the DatabaseManager class methods.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import os


# ============================================================================
# DATABASE MANAGER TESTS
# ============================================================================

class TestDatabaseManager:
    """Test the DatabaseManager class."""

    @patch("core.database.SessionLocal")
    def test_get_session(self, mock_session_local):
        """Test get_session returns a valid session."""
        from core.database import DatabaseManager
        
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        session = DatabaseManager.get_session()

        assert session == mock_session
        mock_session_local.assert_called_once()

    @patch("core.database.SessionLocal")
    def test_close_session(self, mock_session_local):
        """Test close_session properly closes the session."""
        from core.database import DatabaseManager
        
        mock_session = MagicMock()

        DatabaseManager.close_session(mock_session)

        mock_session.close.assert_called_once()

    @patch("core.database.SessionLocal")
    def test_commit_and_refresh(self, mock_session_local):
        """Test commit_and_refresh commits and refreshes an object."""
        from core.database import DatabaseManager
        
        mock_session = MagicMock()
        mock_obj = MagicMock()

        result = DatabaseManager.commit_and_refresh(mock_session, mock_obj)

        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_obj)
        assert result == mock_obj

    @patch("core.database.SessionLocal")
    def test_safe_commit_success(self, mock_session_local):
        """Test safe_commit returns True on success."""
        from core.database import DatabaseManager
        
        mock_session = MagicMock()

        result = DatabaseManager.safe_commit(mock_session)

        assert result is True
        mock_session.commit.assert_called_once()

    @patch("core.database.SessionLocal")
    def test_safe_commit_failure(self, mock_session_local):
        """Test safe_commit handles errors and rolls back."""
        from core.database import DatabaseManager
        
        mock_session = MagicMock()
        mock_session.commit.side_effect = Exception("Database error")

        result = DatabaseManager.safe_commit(mock_session)

        assert result is False
        mock_session.rollback.assert_called_once()


class TestGetDb:
    """Test the get_db generator function."""

    @patch("core.database.SessionLocal")
    def test_get_db_yields_session(self, mock_session_local):
        """Test get_db yields a database session."""
        from core.database import get_db
        
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        gen = get_db()
        session = next(gen)

        assert session == mock_session

    @patch("core.database.SessionLocal")
    def test_get_db_closes_session(self, mock_session_local):
        """Test get_db closes session after use."""
        from core.database import get_db
        
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        gen = get_db()
        next(gen)
        
        # Simulate exiting the context
        try:
            next(gen)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()


class TestInitDatabase:
    """Test the init_database function."""

    @patch("core.database.create_tables")
    @patch.dict(os.environ, {"SKIP_DB": "true"})
    def test_init_database_skip(self, mock_create_tables):
        """Test init_database skips when SKIP_DB is true."""
        from core.database import init_database
        
        init_database()

        mock_create_tables.assert_not_called()

    @patch("core.database.create_tables")
    @patch.dict(os.environ, {"SKIP_DB": "false"})
    def test_init_database_creates_tables(self, mock_create_tables):
        """Test init_database creates tables when SKIP_DB is false."""
        from core.database import init_database
        
        init_database()

        mock_create_tables.assert_called_once()


class TestCreateTables:
    """Test the create_tables function."""

    @patch("core.database.Base")
    @patch("core.database.engine")
    def test_create_tables(self, mock_engine, mock_base):
        """Test create_tables creates all tables."""
        from core.database import create_tables
        
        create_tables()

        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)
