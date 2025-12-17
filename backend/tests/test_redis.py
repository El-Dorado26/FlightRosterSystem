"""
Unit tests for core/redis.py module.

Testing Strategy:
- Unit Testing: Isolated function testing with mocked Redis client
- Equivalence Partitioning: Valid keys, invalid keys, empty values, non-empty values
- Boundary Value Analysis: Edge cases like empty strings, None values, large TTL values
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.redis import (
    set_cache,
    get_cache,
    delete_cache,
    clear_cache,
    exists,
    build_cache_key,
    redis
)


@pytest.mark.unit
class TestBuildCacheKey:
    """Test the build_cache_key utility function."""
    
    def test_build_cache_key_with_single_param(self):
        """Test building a cache key with a single parameter."""
        result = build_cache_key("flight:{flight_id}", flight_id=123)
        assert result == "flight:123"
    
    def test_build_cache_key_with_multiple_params(self):
        """Test building a cache key with multiple parameters."""
        result = build_cache_key(
            "flight:{flight_id}:crew:{crew_id}",
            flight_id=123,
            crew_id=456
        )
        assert result == "flight:123:crew:456"
    
    def test_build_cache_key_with_string_values(self):
        """Test building a cache key with string values."""
        result = build_cache_key("user:{username}", username="john_doe")
        assert result == "user:john_doe"
    
    def test_build_cache_key_empty_template(self):
        """Test building a cache key with empty template."""
        result = build_cache_key("", flight_id=123)
        assert result == ""
    
    def test_build_cache_key_no_placeholders(self):
        """Test building a cache key with no placeholders."""
        result = build_cache_key("static_key", flight_id=123)
        assert result == "static_key"
    
    def test_build_cache_key_special_characters(self):
        """Test building a cache key with special characters."""
        result = build_cache_key(
            "flight:{code}",
            code="TK-0100"
        )
        assert result == "flight:TK-0100"
    
    def test_build_cache_key_missing_param_raises_error(self):
        """Test that missing parameters raise KeyError."""
        with pytest.raises(KeyError):
            build_cache_key("flight:{flight_id}", wrong_param=123)


@pytest.mark.unit
class TestSetCache:
    """Test the set_cache function."""
    
    @patch('core.redis.redis')
    def test_set_cache_without_expiry(self, mock_redis):
        """Test setting cache without expiration time."""
        mock_redis.set.return_value = True
        
        result = set_cache("test_key", "test_value")
        
        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value")
        mock_redis.setex.assert_not_called()
    
    @patch('core.redis.redis')
    def test_set_cache_with_expiry(self, mock_redis):
        """Test setting cache with expiration time."""
        mock_redis.setex.return_value = True
        
        result = set_cache("test_key", "test_value", ex=300)
        
        assert result is True
        mock_redis.setex.assert_called_once_with("test_key", 300, "test_value")
        mock_redis.set.assert_not_called()
    
    @patch('core.redis.redis')
    def test_set_cache_with_zero_expiry(self, mock_redis):
        """Test setting cache with zero expiry (treated as no expiry)."""
        mock_redis.set.return_value = True
        
        result = set_cache("test_key", "test_value", ex=0)
        
        # ex=0 is falsy, so should use set() not setex()
        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value")
    
    @patch('core.redis.redis')
    def test_set_cache_empty_value(self, mock_redis):
        """Test setting cache with empty string value."""
        mock_redis.set.return_value = True
        
        result = set_cache("test_key", "")
        
        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "")
    
    @patch('core.redis.redis')
    def test_set_cache_handles_exception(self, mock_redis):
        """Test set_cache handles exceptions gracefully."""
        mock_redis.set.side_effect = Exception("Redis connection error")
        
        result = set_cache("test_key", "test_value")
        
        assert result is False
    
    @patch('core.redis.redis')
    def test_set_cache_with_large_ttl(self, mock_redis):
        """Boundary test: Large TTL value."""
        mock_redis.setex.return_value = True
        
        result = set_cache("test_key", "test_value", ex=86400 * 365)  # 1 year
        
        assert result is True
        mock_redis.setex.assert_called_once()


@pytest.mark.unit
class TestGetCache:
    """Test the get_cache function."""
    
    @patch('core.redis.redis')
    def test_get_cache_existing_key(self, mock_redis):
        """Test getting an existing cache value."""
        mock_redis.get.return_value = "cached_value"
        
        result = get_cache("test_key")
        
        assert result == "cached_value"
        mock_redis.get.assert_called_once_with("test_key")
    
    @patch('core.redis.redis')
    def test_get_cache_non_existing_key(self, mock_redis):
        """Test getting a non-existing cache value."""
        mock_redis.get.return_value = None
        
        result = get_cache("non_existing_key")
        
        assert result is None
        mock_redis.get.assert_called_once_with("non_existing_key")
    
    @patch('core.redis.redis')
    def test_get_cache_empty_string_value(self, mock_redis):
        """Test getting cache with empty string value."""
        mock_redis.get.return_value = ""
        
        result = get_cache("test_key")
        
        assert result == ""
    
    @patch('core.redis.redis')
    def test_get_cache_handles_exception(self, mock_redis):
        """Test get_cache handles exceptions gracefully."""
        mock_redis.get.side_effect = Exception("Redis connection error")
        
        result = get_cache("test_key")
        
        assert result is None
    
    @patch('core.redis.redis')
    def test_get_cache_special_characters_in_key(self, mock_redis):
        """Test getting cache with special characters in key."""
        mock_redis.get.return_value = "value"
        
        result = get_cache("flight:TK-0100:crew:123")
        
        assert result == "value"


@pytest.mark.unit
class TestDeleteCache:
    """Test the delete_cache function."""
    
    @patch('core.redis.redis')
    def test_delete_cache_existing_key(self, mock_redis):
        """Test deleting an existing cache key."""
        mock_redis.delete.return_value = 1
        
        result = delete_cache("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    @patch('core.redis.redis')
    def test_delete_cache_non_existing_key(self, mock_redis):
        """Test deleting a non-existing cache key."""
        mock_redis.delete.return_value = 0
        
        result = delete_cache("non_existing_key")
        
        assert result is True  # Function returns True even if key doesn't exist
        mock_redis.delete.assert_called_once_with("non_existing_key")
    
    @patch('core.redis.redis')
    def test_delete_cache_handles_exception(self, mock_redis):
        """Test delete_cache handles exceptions gracefully."""
        mock_redis.delete.side_effect = Exception("Redis connection error")
        
        result = delete_cache("test_key")
        
        assert result is False


@pytest.mark.unit
class TestClearCache:
    """Test the clear_cache function."""
    
    @patch('core.redis.redis')
    def test_clear_cache_with_pattern(self, mock_redis):
        """Test clearing cache with a specific pattern."""
        mock_redis.keys.return_value = ["flight:1", "flight:2", "flight:3"]
        mock_redis.delete.return_value = 3
        
        result = clear_cache("flight:*")
        
        assert result is True
        mock_redis.keys.assert_called_once_with("flight:*")
        mock_redis.delete.assert_called_once_with("flight:1", "flight:2", "flight:3")
    
    @patch('core.redis.redis')
    def test_clear_cache_default_pattern(self, mock_redis):
        """Test clearing cache with default pattern (all keys)."""
        mock_redis.keys.return_value = ["key1", "key2"]
        mock_redis.delete.return_value = 2
        
        result = clear_cache()
        
        assert result is True
        mock_redis.keys.assert_called_once_with("*")
        mock_redis.delete.assert_called_once_with("key1", "key2")
    
    @patch('core.redis.redis')
    def test_clear_cache_no_matching_keys(self, mock_redis):
        """Test clearing cache when no keys match the pattern."""
        mock_redis.keys.return_value = []
        
        result = clear_cache("non_existing:*")
        
        assert result is True
        mock_redis.keys.assert_called_once_with("non_existing:*")
        mock_redis.delete.assert_not_called()
    
    @patch('core.redis.redis')
    def test_clear_cache_handles_exception(self, mock_redis):
        """Test clear_cache handles exceptions gracefully."""
        mock_redis.keys.side_effect = Exception("Redis connection error")
        
        result = clear_cache("pattern:*")
        
        assert result is False
    
    @patch('core.redis.redis')
    def test_clear_cache_delete_raises_exception(self, mock_redis):
        """Test clear_cache handles delete exceptions gracefully."""
        mock_redis.keys.return_value = ["key1", "key2"]
        mock_redis.delete.side_effect = Exception("Delete failed")
        
        result = clear_cache("pattern:*")
        
        assert result is False


@pytest.mark.unit
class TestExists:
    """Test the exists function."""
    
    @patch('core.redis.redis')
    def test_exists_key_present(self, mock_redis):
        """Test checking if a key exists (key is present)."""
        mock_redis.exists.return_value = 1
        
        result = exists("test_key")
        
        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")
    
    @patch('core.redis.redis')
    def test_exists_key_absent(self, mock_redis):
        """Test checking if a key exists (key is absent)."""
        mock_redis.exists.return_value = 0
        
        result = exists("non_existing_key")
        
        assert result is False
        mock_redis.exists.assert_called_once_with("non_existing_key")
    
    @patch('core.redis.redis')
    def test_exists_multiple_keys_present(self, mock_redis):
        """Test exists when multiple keys with same name exist."""
        mock_redis.exists.return_value = 2
        
        result = exists("test_key")
        
        assert result is True  # Any value > 0 should return True
    
    @patch('core.redis.redis')
    def test_exists_handles_exception(self, mock_redis):
        """Test exists handles exceptions gracefully."""
        mock_redis.exists.side_effect = Exception("Redis connection error")
        
        result = exists("test_key")
        
        assert result is False


@pytest.mark.unit
class TestIntegrationScenarios:
    """Integration scenarios testing multiple redis functions together."""
    
    @patch('core.redis.redis')
    def test_set_get_delete_workflow(self, mock_redis):
        """Test complete workflow: set -> get -> delete."""
        # Set cache
        mock_redis.set.return_value = True
        assert set_cache("workflow_key", "workflow_value") is True
        
        # Get cache
        mock_redis.get.return_value = "workflow_value"
        assert get_cache("workflow_key") == "workflow_value"
        
        # Delete cache
        mock_redis.delete.return_value = 1
        assert delete_cache("workflow_key") is True
        
        # Verify get returns None after delete
        mock_redis.get.return_value = None
        assert get_cache("workflow_key") is None
    
    @patch('core.redis.redis')
    def test_set_exists_clear_workflow(self, mock_redis):
        """Test workflow: set -> exists -> clear."""
        # Set multiple keys
        mock_redis.set.return_value = True
        assert set_cache("user:1", "data1") is True
        assert set_cache("user:2", "data2") is True
        
        # Check existence
        mock_redis.exists.return_value = 1
        assert exists("user:1") is True
        
        # Clear with pattern
        mock_redis.keys.return_value = ["user:1", "user:2"]
        mock_redis.delete.return_value = 2
        assert clear_cache("user:*") is True
        
        # Verify keys no longer exist
        mock_redis.exists.return_value = 0
        assert exists("user:1") is False
    
    @patch('core.redis.redis')
    def test_build_key_and_cache_operations(self, mock_redis):
        """Test building cache keys and using them in operations."""
        # Build cache key
        cache_key = build_cache_key("flight:{flight_id}", flight_id=100)
        assert cache_key == "flight:100"
        
        # Use the built key in cache operations
        mock_redis.set.return_value = True
        assert set_cache(cache_key, "flight_data") is True
        
        mock_redis.get.return_value = "flight_data"
        assert get_cache(cache_key) == "flight_data"


@pytest.mark.unit
class TestEquivalencePartitioning:
    """Tests using equivalence partitioning strategy."""
    
    @patch('core.redis.redis')
    def test_valid_key_formats(self, mock_redis):
        """Test various valid key formats."""
        mock_redis.set.return_value = True
        
        valid_keys = [
            "simple_key",
            "key:with:colons",
            "key-with-dashes",
            "key_with_underscores",
            "key123",
            "CamelCaseKey",
        ]
        
        for key in valid_keys:
            assert set_cache(key, "value") is True
    
    @patch('core.redis.redis')
    def test_ttl_equivalence_classes(self, mock_redis):
        """Test different TTL value classes."""
        mock_redis.setex.return_value = True
        mock_redis.set.return_value = True
        
        # Short TTL (seconds)
        assert set_cache("key1", "val", ex=60) is True
        
        # Medium TTL (minutes)
        assert set_cache("key2", "val", ex=3600) is True
        
        # Long TTL (days)
        assert set_cache("key3", "val", ex=86400) is True
        
        # No TTL
        assert set_cache("key4", "val") is True


@pytest.mark.unit
class TestBoundaryValueAnalysis:
    """Tests using boundary value analysis strategy."""
    
    @patch('core.redis.redis')
    def test_ttl_boundary_values(self, mock_redis):
        """Test TTL boundary values."""
        mock_redis.setex.return_value = True
        mock_redis.set.return_value = True
        
        # Minimum positive TTL
        assert set_cache("key", "val", ex=1) is True
        
        # Zero TTL (boundary - treated as no expiry)
        assert set_cache("key", "val", ex=0) is True
        
        # Very large TTL
        assert set_cache("key", "val", ex=2147483647) is True  # Max int32
    
    @patch('core.redis.redis')
    def test_empty_and_single_char_keys(self, mock_redis):
        """Test boundary cases for key lengths."""
        mock_redis.set.return_value = True
        
        # Single character key
        assert set_cache("a", "value") is True
        
        # Empty key (valid in Redis)
        assert set_cache("", "value") is True
    
    @patch('core.redis.redis')
    def test_pattern_boundary_cases(self, mock_redis):
        """Test boundary cases for pattern matching."""
        mock_redis.keys.return_value = []
        
        # Wildcard only
        assert clear_cache("*") is True
        
        # Empty pattern (will be treated as literal)
        assert clear_cache("") is True
