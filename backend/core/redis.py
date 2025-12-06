import os
from upstash_redis import Redis

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

def get_redis():
    return redis


def set_cache(key: str, value: str, ex: int = None) -> bool:
    """
    Set a value in Redis cache.
    """
    try:
        if ex:
            redis.setex(key, ex, value)
        else:
            redis.set(key, value)
        return True
    except Exception as e:
        print(f"Error setting cache: {e}")
        return False


def get_cache(key: str) -> str | None:
    """
    Get a value from Redis cache.
    """
    try:
        value = redis.get(key)
        return value
    except Exception as e:
        print(f"Error getting cache: {e}")
        return None


def delete_cache(key: str) -> bool:
    """
    Delete a value from Redis cache.
    """
    try:
        redis.delete(key)
        return True
    except Exception as e:
        print(f"Error deleting cache: {e}")
        return False


def clear_cache(pattern: str = "*") -> bool:
    """
    Clear cache by pattern.
    """
    try:
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False


def exists(key: str) -> bool:
    """
    Check if a key exists in Redis.
    """
    try:
        return redis.exists(key) > 0
    except Exception as e:
        print(f"Error checking key existence: {e}")
        return False

