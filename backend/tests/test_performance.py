"""
Performance Testing for Flight Roster System.

Tests Redis caching effectiveness, database load reduction, response times,
and query optimization. Validates that caching actually improves performance
under realistic query patterns.

Testing Areas:
- Redis cache hit/miss rates
- Response time improvements with caching
- Database query reduction
- Cache TTL effectiveness
- Memory usage optimization
- Query pattern performance
"""
import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import asyncio

from core.redis import (
    set_cache,
    get_cache,
    delete_cache,
    clear_cache,
    exists,
    build_cache_key
)


@pytest.mark.performance
class TestCacheEffectiveness:
    """Test Redis caching effectiveness and performance improvements."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        clear_cache()
        yield
        clear_cache()
    
    def test_cache_hit_performance(self):
        """Test that cache hits are significantly faster than cache misses."""
        key = build_cache_key("test", "performance")
        data = {"large_data": list(range(1000))}
        
        # First access (cache miss) - simulate database query
        miss_start = time.time()
        cached_data = get_cache(key)
        if cached_data is None:
            # Simulate database query time
            time.sleep(0.01)  # 10ms simulated DB query
            set_cache(key, data, ex=300)
        miss_time = time.time() - miss_start
        
        # Second access (cache hit)
        hit_start = time.time()
        cached_data = get_cache(key)
        hit_time = time.time() - hit_start
        
        # Cache hit should be significantly faster
        assert cached_data is not None
        assert hit_time < miss_time, \
            f"Cache hit ({hit_time:.4f}s) not faster than miss ({miss_time:.4f}s)"
        
        # Cache hit should be at least 2x faster
        speedup = miss_time / hit_time
        assert speedup > 2, f"Cache speedup only {speedup:.2f}x"
    
    def test_cache_miss_rate_calculation(self):
        """Test cache miss rate tracking."""
        keys = [build_cache_key("test", f"item_{i}") for i in range(10)]
        
        # Populate some keys
        for i in range(5):
            set_cache(keys[i], {"data": i}, ex=300)
        
        hits = 0
        misses = 0
        
        # Query all keys
        for key in keys:
            result = get_cache(key)
            if result is not None:
                hits += 1
            else:
                misses += 1
        
        # Should have 50% hit rate
        hit_rate = hits / (hits + misses)
        assert hit_rate == 0.5, f"Expected 50% hit rate, got {hit_rate*100}%"
    
    def test_cache_memory_efficiency(self):
        """Test that caching uses memory efficiently."""
        # Store various data sizes
        test_cases = [
            ("small", {"id": 1}, 1),
            ("medium", {"data": list(range(100))}, 100),
            ("large", {"data": list(range(1000))}, 1000),
        ]
        
        for name, data, expected_size in test_cases:
            key = build_cache_key("memory", name)
            
            # Set cache
            set_cache(key, data, ex=300)
            
            # Retrieve and verify
            cached = get_cache(key)
            assert cached is not None
            
            if "data" in cached:
                assert len(cached["data"]) == expected_size
    
    def test_cache_ttl_effectiveness(self):
        """Test that cache TTL properly expires entries."""
        key = build_cache_key("ttl", "test")
        data = {"value": "test"}
        
        # Set cache with 1 second TTL
        set_cache(key, data, ex=1)
        
        # Should exist immediately
        assert exists(key)
        assert get_cache(key) is not None
        
        # Wait for expiry
        time.sleep(1.5)
        
        # Should be expired
        assert not exists(key)
        assert get_cache(key) is None
    
    def test_cache_warmup_performance(self):
        """Test performance of cache warmup operations."""
        num_items = 100
        
        # Measure warmup time
        start = time.time()
        for i in range(num_items):
            key = build_cache_key("warmup", f"item_{i}")
            set_cache(key, {"id": i, "data": f"item_{i}"}, ex=300)
        warmup_time = time.time() - start
        
        # Should complete reasonably fast
        assert warmup_time < 5.0, f"Cache warmup too slow: {warmup_time:.2f}s"
        
        # Verify all items cached
        cached_count = 0
        for i in range(num_items):
            key = build_cache_key("warmup", f"item_{i}")
            if exists(key):
                cached_count += 1
        
        assert cached_count == num_items


@pytest.mark.performance
class TestDatabaseLoadReduction:
    """Test that caching reduces database load."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        clear_cache()
        yield
        clear_cache()
    
    def test_repeated_query_caching(self):
        """Test that repeated queries hit cache instead of database."""
        key = build_cache_key("flights", "list")
        
        # Track database calls
        db_calls = []
        
        def simulate_db_query():
            db_calls.append(datetime.now())
            return [{"id": 1}, {"id": 2}, {"id": 3}]
        
        # First query - database call
        cached = get_cache(key)
        if cached is None:
            data = simulate_db_query()
            set_cache(key, data, ex=300)
        
        assert len(db_calls) == 1, "First query should hit database"
        
        # Subsequent queries - cache hits
        for _ in range(5):
            cached = get_cache(key)
            if cached is None:
                data = simulate_db_query()
                set_cache(key, data, ex=300)
        
        # Should only have one database call
        assert len(db_calls) == 1, \
            f"Expected 1 DB call, got {len(db_calls)} (cache not working)"
    
    def test_cache_invalidation_triggers_refresh(self):
        """Test that cache invalidation triggers database refresh."""
        key = build_cache_key("flights", "specific", 1)
        
        db_calls = []
        
        def get_data():
            db_calls.append(True)
            return {"id": 1, "status": "active"}
        
        # First query
        cached = get_cache(key)
        if cached is None:
            data = get_data()
            set_cache(key, data, ex=300)
        
        assert len(db_calls) == 1
        
        # Invalidate cache
        delete_cache(key)
        
        # Next query should hit database again
        cached = get_cache(key)
        if cached is None:
            data = get_data()
            set_cache(key, data, ex=300)
        
        assert len(db_calls) == 2, "Cache invalidation should trigger refresh"
    
    def test_selective_cache_invalidation(self):
        """Test that invalidating specific keys doesn't affect others."""
        keys = {
            "flights": build_cache_key("flights", "all"),
            "cabin_crew": build_cache_key("cabin-crew", "all"),
            "passengers": build_cache_key("passengers", "all")
        }
        
        # Cache all resources
        for resource, key in keys.items():
            set_cache(key, {resource: [1, 2, 3]}, ex=300)
        
        # Verify all cached
        for key in keys.values():
            assert exists(key)
        
        # Invalidate only flights
        delete_cache(keys["flights"])
        
        # Flights should be invalidated
        assert not exists(keys["flights"])
        
        # Others should still be cached
        assert exists(keys["cabin_crew"])
        assert exists(keys["passengers"])


@pytest.mark.performance
class TestResponseTimeOptimization:
    """Test response time improvements with caching."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        clear_cache()
        yield
        clear_cache()
    
    def test_cold_vs_warm_cache_performance(self):
        """Test performance difference between cold and warm cache."""
        key = build_cache_key("perf", "test")
        data = {"large_dataset": [{"id": i, "data": f"item_{i}"} for i in range(100)]}
        
        # Cold cache (miss)
        cold_times = []
        for _ in range(3):
            clear_cache()  # Ensure cold
            start = time.time()
            cached = get_cache(key)
            if cached is None:
                time.sleep(0.01)  # Simulate DB query
                set_cache(key, data, ex=300)
            cold_times.append(time.time() - start)
        
        # Warm cache (hit)
        warm_times = []
        set_cache(key, data, ex=300)  # Warm up
        for _ in range(10):
            start = time.time()
            cached = get_cache(key)
            warm_times.append(time.time() - start)
        
        avg_cold = sum(cold_times) / len(cold_times)
        avg_warm = sum(warm_times) / len(warm_times)
        
        # Warm cache should be faster
        assert avg_warm < avg_cold, \
            f"Warm cache ({avg_warm:.4f}s) not faster than cold ({avg_cold:.4f}s)"
        
        improvement = ((avg_cold - avg_warm) / avg_cold) * 100
        assert improvement > 20, \
            f"Performance improvement only {improvement:.1f}% (expected >20%)"
    
    def test_concurrent_cache_access_performance(self):
        """Test cache performance under concurrent access."""
        key = build_cache_key("concurrent", "test")
        data = {"value": "test_data"}
        
        # Pre-populate cache
        set_cache(key, data, ex=300)
        
        # Simulate concurrent reads
        start = time.time()
        results = []
        for _ in range(50):
            result = get_cache(key)
            results.append(result)
        total_time = time.time() - start
        
        # All reads should succeed
        assert all(r is not None for r in results)
        
        # Should complete quickly
        assert total_time < 1.0, f"Concurrent access too slow: {total_time:.2f}s"
        
        # Average per-request time
        avg_time = total_time / 50
        assert avg_time < 0.02, f"Average request time too high: {avg_time:.4f}s"
    
    def test_cache_key_lookup_performance(self):
        """Test that cache key lookups are fast."""
        # Create many cache entries
        num_entries = 100
        for i in range(num_entries):
            key = build_cache_key("lookup", f"item_{i}")
            set_cache(key, {"id": i}, ex=300)
        
        # Test lookup performance
        lookup_times = []
        for i in range(num_entries):
            key = build_cache_key("lookup", f"item_{i}")
            start = time.time()
            result = get_cache(key)
            lookup_times.append(time.time() - start)
        
        avg_lookup = sum(lookup_times) / len(lookup_times)
        max_lookup = max(lookup_times)
        
        # Lookups should be fast
        assert avg_lookup < 0.01, f"Average lookup too slow: {avg_lookup:.4f}s"
        assert max_lookup < 0.05, f"Max lookup too slow: {max_lookup:.4f}s"


@pytest.mark.performance
class TestQueryPatternPerformance:
    """Test performance under realistic query patterns."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        clear_cache()
        yield
        clear_cache()
    
    def test_read_heavy_workload(self):
        """Test performance with read-heavy workload (typical for roster viewing)."""
        # Simulate 10 cached items
        items = {}
        for i in range(10):
            key = build_cache_key("roster", f"flight_{i}")
            data = {"flight_id": i, "crew": [1, 2, 3, 4]}
            set_cache(key, data, ex=300)
            items[i] = key
        
        # Simulate read-heavy pattern (90% reads, 10% writes)
        operations = []
        start = time.time()
        
        for _ in range(100):
            import random
            if random.random() < 0.9:  # 90% reads
                flight_id = random.randint(0, 9)
                result = get_cache(items[flight_id])
                operations.append(("read", result is not None))
            else:  # 10% writes
                flight_id = random.randint(0, 9)
                set_cache(items[flight_id], {"updated": True}, ex=300)
                operations.append(("write", True))
        
        total_time = time.time() - start
        
        # Should complete quickly
        assert total_time < 2.0, f"Read-heavy workload too slow: {total_time:.2f}s"
        
        # Most reads should be cache hits
        read_ops = [op for op in operations if op[0] == "read"]
        hit_rate = sum(1 for op in read_ops if op[1]) / len(read_ops)
        assert hit_rate > 0.8, f"Cache hit rate too low: {hit_rate*100:.1f}%"
    
    def test_filter_query_caching(self):
        """Test caching effectiveness for filtered queries."""
        # Simulate different filter combinations
        filter_combinations = [
            {"airline_id": 1},
            {"airline_id": 1, "status": "active"},
            {"airline_id": 2},
            {"date": "2024-01-01"},
        ]
        
        query_times = {}
        
        for filters in filter_combinations:
            key = build_cache_key("flights", "filtered", **filters)
            
            # First query (miss)
            start = time.time()
            cached = get_cache(key)
            if cached is None:
                time.sleep(0.015)  # Simulate DB query with filters
                result = {"filters": filters, "results": [1, 2, 3]}
                set_cache(key, result, ex=300)
            first_time = time.time() - start
            
            # Second query (hit)
            start = time.time()
            cached = get_cache(key)
            second_time = time.time() - start
            
            query_times[str(filters)] = {
                "first": first_time,
                "second": second_time,
                "improvement": (first_time - second_time) / first_time * 100
            }
        
        # All cached queries should be faster
        for filters, times in query_times.items():
            assert times["second"] < times["first"], \
                f"Cached query not faster for {filters}"
            assert times["improvement"] > 20, \
                f"Improvement only {times['improvement']:.1f}% for {filters}"
    
    def test_pagination_caching_strategy(self):
        """Test caching effectiveness for paginated results."""
        page_size = 20
        total_pages = 5
        
        # Cache each page
        page_times = []
        for page in range(1, total_pages + 1):
            key = build_cache_key("flights", "page", page, page_size)
            
            start = time.time()
            cached = get_cache(key)
            if cached is None:
                time.sleep(0.01)  # Simulate DB query
                data = {"page": page, "items": list(range((page-1)*page_size, page*page_size))}
                set_cache(key, data, ex=300)
            page_times.append(time.time() - start)
        
        # Re-access pages (should be cached)
        cached_times = []
        for page in range(1, total_pages + 1):
            key = build_cache_key("flights", "page", page, page_size)
            start = time.time()
            cached = get_cache(key)
            cached_times.append(time.time() - start)
        
        # Cached access should be consistently fast
        avg_cached = sum(cached_times) / len(cached_times)
        assert avg_cached < 0.005, f"Cached pagination too slow: {avg_cached:.4f}s"


@pytest.mark.performance
class TestCacheScalability:
    """Test cache performance under scale."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        clear_cache()
        yield
        clear_cache()
    
    def test_large_dataset_caching(self):
        """Test caching performance with large datasets."""
        sizes = [10, 100, 500, 1000]
        performance_metrics = {}
        
        for size in sizes:
            key = build_cache_key("large", f"size_{size}")
            data = {"items": [{"id": i, "data": f"item_{i}"} for i in range(size)]}
            
            # Measure set time
            start = time.time()
            set_cache(key, data, ex=300)
            set_time = time.time() - start
            
            # Measure get time
            start = time.time()
            retrieved = get_cache(key)
            get_time = time.time() - start
            
            performance_metrics[size] = {
                "set": set_time,
                "get": get_time,
                "total": set_time + get_time
            }
            
            # Verify data integrity
            assert retrieved is not None
            assert len(retrieved["items"]) == size
        
        # Performance should scale reasonably
        # Larger datasets can take longer, but should be sub-linear growth
        for size in sizes:
            assert performance_metrics[size]["set"] < 1.0, \
                f"Set time too high for {size} items: {performance_metrics[size]['set']:.3f}s"
            assert performance_metrics[size]["get"] < 0.5, \
                f"Get time too high for {size} items: {performance_metrics[size]['get']:.3f}s"
    
    def test_cache_key_collision_avoidance(self):
        """Test that cache keys don't collide under various parameters."""
        # Create keys with similar parameters
        keys = [
            build_cache_key("flights", "1"),
            build_cache_key("flights", 1),
            build_cache_key("flights", "01"),
            build_cache_key("flight", "1"),
            build_cache_key("flights", "1", "extra"),
        ]
        
        # All keys should be unique
        assert len(keys) == len(set(keys)), "Cache key collision detected"
        
        # Store different data in each
        for i, key in enumerate(keys):
            set_cache(key, {"index": i}, ex=300)
        
        # Verify each key has correct data
        for i, key in enumerate(keys):
            data = get_cache(key)
            assert data["index"] == i, f"Data mismatch for key {key}"
    
    def test_cache_memory_limits(self):
        """Test behavior approaching cache memory limits."""
        # Store many items to test memory handling
        num_items = 200
        stored_keys = []
        
        for i in range(num_items):
            key = build_cache_key("memory_test", f"item_{i}")
            data = {"id": i, "data": "x" * 100}  # Small payload
            set_cache(key, data, ex=300)
            stored_keys.append(key)
        
        # Verify a sample of items still exist
        sample_size = min(50, num_items)
        import random
        sample_keys = random.sample(stored_keys, sample_size)
        
        existing_count = sum(1 for key in sample_keys if exists(key))
        
        # Most sampled items should still exist
        # (some may have been evicted if memory limits reached)
        existence_rate = existing_count / sample_size
        assert existence_rate > 0.7, \
            f"Too many items evicted: {existence_rate*100:.1f}% remain"


@pytest.mark.performance
@pytest.mark.slow
class TestCachePerformanceBenchmarks:
    """Comprehensive performance benchmarks for caching system."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        clear_cache()
        yield
        clear_cache()
    
    def test_throughput_benchmark(self):
        """Benchmark cache throughput (operations per second)."""
        num_operations = 1000
        key = build_cache_key("benchmark", "throughput")
        data = {"value": "test_data"}
        
        # Benchmark writes
        start = time.time()
        for i in range(num_operations):
            set_cache(f"{key}_{i}", data, ex=300)
        write_time = time.time() - start
        write_ops_per_sec = num_operations / write_time
        
        # Benchmark reads
        start = time.time()
        for i in range(num_operations):
            get_cache(f"{key}_{i}")
        read_time = time.time() - start
        read_ops_per_sec = num_operations / read_time
        
        print(f"\nCache Throughput Benchmark:")
        print(f"  Writes: {write_ops_per_sec:.0f} ops/sec")
        print(f"  Reads:  {read_ops_per_sec:.0f} ops/sec")
        
        # Should achieve reasonable throughput
        assert write_ops_per_sec > 100, \
            f"Write throughput too low: {write_ops_per_sec:.0f} ops/sec"
        assert read_ops_per_sec > 500, \
            f"Read throughput too low: {read_ops_per_sec:.0f} ops/sec"
    
    def test_latency_percentiles(self):
        """Test cache operation latency percentiles."""
        num_operations = 100
        latencies = []
        
        # Warm up cache
        key = build_cache_key("latency", "test")
        set_cache(key, {"data": "test"}, ex=300)
        
        # Measure latencies
        for _ in range(num_operations):
            start = time.time()
            get_cache(key)
            latency = (time.time() - start) * 1000  # Convert to ms
            latencies.append(latency)
        
        # Calculate percentiles
        latencies.sort()
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        print(f"\nCache Latency Percentiles:")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        
        # Latency targets
        assert p50 < 10, f"P50 latency too high: {p50:.2f}ms"
        assert p95 < 50, f"P95 latency too high: {p95:.2f}ms"
        assert p99 < 100, f"P99 latency too high: {p99:.2f}ms"
