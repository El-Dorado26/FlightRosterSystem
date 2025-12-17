"""
Pytest configuration and shared fixtures for the test suite.
"""
import pytest
from unittest.mock import Mock, MagicMock
import os


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["UPSTASH_REDIS_REST_URL"] = "http://test-redis.example.com"
    os.environ["UPSTASH_REDIS_REST_TOKEN"] = "test-token"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["MONGODB_URL"] = "mongodb://test:27017"
    os.environ["SECRET_KEY"] = "test-secret-key"
    yield
    

@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing."""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.exists.return_value = 0
    mock_redis.keys.return_value = []
    return mock_redis
