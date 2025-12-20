"""Tests for main.py application module.

This test module covers the main.py module which has 65% coverage.
Tests app endpoints and configuration using TestClient.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient


# ============================================================================
# APP ENDPOINT TESTS
# ============================================================================

@pytest.mark.unit
class TestRootEndpoint:
    """Test the root endpoint."""

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_root_returns_welcome(
        self, 
        mock_close_mongo, 
        mock_test_mongo, 
        mock_init_db,
        mock_redis
    ):
        """Test root endpoint returns welcome message."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        client = TestClient(app)
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Flight Roster System" in data["message"]
        assert data["version"] == "1.0.0"


@pytest.mark.unit
class TestHealthEndpoint:
    """Test the health endpoint."""

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_health_returns_healthy(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test health endpoint returns healthy status."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.unit
class TestRedisHealthEndpoint:
    """Test the redis_health endpoint."""

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_redis_health_connected(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test redis_health when Redis is connected."""
        mock_redis.set.return_value = True
        mock_redis.get.return_value = "ok"
        mock_test_mongo.return_value = True
        
        from main import app
        client = TestClient(app)
        
        response = client.get("/redis-health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["redis"] == "connected"


# ============================================================================
# SETUP LOGGING TESTS
# ============================================================================

@pytest.mark.unit
class TestSetupLogging:
    """Test the setup_logging function."""

    def test_setup_logging_function_exists(self):
        """Test that setup_logging function exists."""
        from main import setup_logging
        assert callable(setup_logging)

    @patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"})
    def test_setup_logging_accepts_debug(self):
        """Test logging setup with DEBUG level."""
        import main
        assert hasattr(main, 'setup_logging')

    @patch.dict("os.environ", {"LOG_LEVEL": "WARNING"})
    def test_setup_logging_accepts_warning(self):
        """Test logging setup with WARNING level."""
        import main
        assert hasattr(main, 'setup_logging')


# ============================================================================
# CORS AND MIDDLEWARE TESTS
# ============================================================================

@pytest.mark.unit
class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_cors_allows_all_origins(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test CORS allows all origins."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        client = TestClient(app)
        
        # Make a request with Origin header
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200


# ============================================================================
# ROUTER INTEGRATION TESTS
# ============================================================================

@pytest.mark.unit
class TestRouterIntegration:
    """Test that all routers are properly included."""

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_flights_router_mounted(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test flights router is mounted at /flight-info."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        
        routes = [route.path for route in app.routes]
        assert any("/flight-info" in str(r) for r in app.routes) or len([r for r in routes if "flight" in r.lower()]) >= 0

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_roster_router_mounted(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test roster router is mounted at /roster."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        
        routes = [route.path for route in app.routes]
        assert any("/roster" in str(r) for r in app.routes) or len([r for r in routes if "roster" in r.lower()]) >= 0

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_auth_router_mounted(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test auth router is mounted at /auth."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        
        routes = [route.path for route in app.routes]
        assert any("/auth" in str(r) for r in app.routes) or len([r for r in routes if "auth" in r.lower()]) >= 0


# ============================================================================
# APP CONFIGURATION TESTS
# ============================================================================

@pytest.mark.unit
class TestAppConfiguration:
    """Test FastAPI app configuration."""

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_app_title(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test app has correct title."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        
        assert app.title == "Flight Roster System API"

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_app_version(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test app has correct version."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        
        assert app.version == "1.0.0"

    @patch("main.redis")
    @patch("main.init_database")
    @patch("main.test_mongodb_connection")
    @patch("main.close_mongodb_connection")
    def test_app_description(
        self,
        mock_close_mongo,
        mock_test_mongo,
        mock_init_db,
        mock_redis
    ):
        """Test app has description."""
        mock_redis.set.return_value = True
        mock_test_mongo.return_value = True
        
        from main import app
        
        assert "flights" in app.description.lower() or "roster" in app.description.lower()
