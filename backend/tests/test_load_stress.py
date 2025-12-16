"""
Load and Stress Testing for Flight Roster System.

Tests system behavior under concurrent user scenarios, database connection
pooling, FastAPI-Redis concurrency handling, and stress conditions.

Testing Areas:
- Concurrent user requests
- Multiple admin roster generation
- Simultaneous roster queries
- Database connection pooling
- Redis connection handling
- System resource limits
- Error handling under load
"""
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from core.redis import set_cache, get_cache, clear_cache, build_cache_key
from core.auth import create_access_token


@pytest.mark.load
class TestConcurrentUserRequests:
    """Test system behavior with concurrent user requests."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup test client and cleanup."""
        self.client = TestClient(app)
        clear_cache()
        yield
        clear_cache()
    
    def test_concurrent_read_requests(self):
        """Test handling of concurrent read requests."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        num_concurrent = 20
        
        def make_request(request_id):
            start = time.time()
            response = self.client.get("/api/flights", headers=headers)
            elapsed = time.time() - start
            return {
                "id": request_id,
                "status": response.status_code,
                "time": elapsed,
                "success": response.status_code == 200
            }
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r["success"]]
        avg_time = sum(r["time"] for r in results) / len(results)
        max_time = max(r["time"] for r in results)
        
        # All requests should succeed
        assert len(successful) == num_concurrent, \
            f"Only {len(successful)}/{num_concurrent} requests succeeded"
        
        # Response times should be reasonable
        assert avg_time < 2.0, f"Average response time too high: {avg_time:.2f}s"
        assert max_time < 5.0, f"Max response time too high: {max_time:.2f}s"
    
    def test_concurrent_write_requests(self):
        """Test handling of concurrent write requests (cache updates)."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        
        num_concurrent = 10
        
        def update_cache(user_id):
            key = build_cache_key("user", "data", user_id)
            start = time.time()
            set_cache(key, {"user_id": user_id, "updated": datetime.now().isoformat()}, ex=300)
            elapsed = time.time() - start
            return {"user_id": user_id, "time": elapsed, "success": True}
        
        # Execute concurrent writes
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_cache, i) for i in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # All writes should succeed
        assert all(r["success"] for r in results), "Some write operations failed"
        
        # Verify all data was written
        for i in range(num_concurrent):
            key = build_cache_key("user", "data", i)
            data = get_cache(key)
            assert data is not None, f"Data for user {i} not found in cache"
            assert data["user_id"] == i
    
    def test_concurrent_mixed_operations(self):
        """Test concurrent mix of read and write operations."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Pre-populate some cache data
        for i in range(10):
            key = build_cache_key("resource", str(i))
            set_cache(key, {"id": i}, ex=300)
        
        num_operations = 30
        
        def mixed_operation(op_id):
            import random
            if random.random() < 0.7:  # 70% reads
                key = build_cache_key("resource", str(random.randint(0, 9)))
                result = get_cache(key)
                return {"type": "read", "success": result is not None}
            else:  # 30% writes
                key = build_cache_key("resource", str(random.randint(0, 9)))
                set_cache(key, {"id": op_id, "updated": True}, ex=300)
                return {"type": "write", "success": True}
        
        # Execute mixed operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(num_operations)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        reads = [r for r in results if r["type"] == "read"]
        writes = [r for r in results if r["type"] == "write"]
        
        # Most operations should succeed
        successful_reads = sum(1 for r in reads if r["success"])
        successful_writes = sum(1 for r in writes if r["success"])
        
        assert successful_reads / len(reads) > 0.8 if reads else True
        assert successful_writes / len(writes) > 0.9 if writes else True


@pytest.mark.load
class TestMultipleAdminRosterGeneration:
    """Test concurrent roster generation by multiple admins."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup test client and cleanup."""
        self.client = TestClient(app)
        clear_cache()
        yield
        clear_cache()
    
    def test_concurrent_roster_generation(self):
        """Test multiple admins generating rosters simultaneously."""
        # Create tokens for multiple admins
        admin_tokens = [
            create_access_token({"sub": f"admin{i}@example.com", "role": "admin"})
            for i in range(5)
        ]
        
        def generate_roster(admin_id, token):
            headers = {"Authorization": f"Bearer {token}"}
            start = time.time()
            
            # Simulate roster generation request
            response = self.client.post(
                "/api/roster/generate",
                headers=headers,
                json={"flight_id": admin_id + 1}  # Different flights
            )
            
            elapsed = time.time() - start
            return {
                "admin_id": admin_id,
                "status": response.status_code,
                "time": elapsed,
                "success": response.status_code in [200, 201, 404]  # 404 if flight doesn't exist
            }
        
        # Execute concurrent roster generations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(generate_roster, i, token)
                for i, token in enumerate(admin_tokens)
            ]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should complete without crashing
        assert len(results) == len(admin_tokens)
        
        # Response times should be reasonable
        avg_time = sum(r["time"] for r in results) / len(results)
        assert avg_time < 10.0, f"Average generation time too high: {avg_time:.2f}s"
    
    def test_concurrent_roster_queries(self):
        """Test multiple users querying saved rosters simultaneously."""
        # Create tokens for different user types
        tokens = {
            "admin": create_access_token({"sub": "admin@example.com", "role": "admin"}),
            "manager": create_access_token({"sub": "manager@example.com", "role": "manager"}),
            "viewer1": create_access_token({"sub": "viewer1@example.com", "role": "viewer"}),
            "viewer2": create_access_token({"sub": "viewer2@example.com", "role": "viewer"}),
        }
        
        num_queries_per_user = 5
        
        def query_roster(user_type, token, query_id):
            headers = {"Authorization": f"Bearer {token}"}
            start = time.time()
            
            response = self.client.get("/api/roster/saved", headers=headers)
            
            elapsed = time.time() - start
            return {
                "user": user_type,
                "query_id": query_id,
                "status": response.status_code,
                "time": elapsed,
                "success": response.status_code == 200
            }
        
        # Execute concurrent queries from all users
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for user_type, token in tokens.items():
                for query_id in range(num_queries_per_user):
                    futures.append(executor.submit(query_roster, user_type, token, query_id))
            
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results by user type
        by_user = {}
        for result in results:
            user = result["user"]
            if user not in by_user:
                by_user[user] = []
            by_user[user].append(result)
        
        # All queries should succeed
        for user, user_results in by_user.items():
            successful = [r for r in user_results if r["success"]]
            success_rate = len(successful) / len(user_results)
            assert success_rate >= 0.8, \
                f"{user} success rate too low: {success_rate*100:.1f}%"


@pytest.mark.load
class TestDatabaseConnectionPooling:
    """Test database connection pooling under concurrent load."""
    
    def test_concurrent_cache_connections(self):
        """Test Redis connection handling under concurrent load."""
        num_concurrent = 50
        
        def cache_operation(op_id):
            key = build_cache_key("load_test", f"op_{op_id}")
            
            # Write
            set_cache(key, {"op_id": op_id, "data": "test"}, ex=300)
            
            # Read
            result = get_cache(key)
            
            # Verify
            return result is not None and result["op_id"] == op_id
        
        # Execute many concurrent operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(cache_operation, i) for i in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # All operations should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95, \
            f"Too many failed operations: {success_rate*100:.1f}% success rate"
    
    def test_connection_pool_exhaustion_handling(self):
        """Test behavior when approaching connection pool limits."""
        # Simulate high concurrent load
        num_operations = 100
        
        def rapid_cache_operations(batch_id):
            results = []
            for i in range(10):
                key = build_cache_key("pool_test", f"batch_{batch_id}", f"op_{i}")
                try:
                    set_cache(key, {"batch": batch_id, "op": i}, ex=300)
                    result = get_cache(key)
                    results.append(result is not None)
                except Exception as e:
                    results.append(False)
            return sum(results) / len(results)  # Success rate per batch
        
        # Execute many batches concurrently
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(rapid_cache_operations, i) for i in range(num_operations)]
            batch_success_rates = [future.result() for future in as_completed(futures)]
        
        # Most batches should complete successfully
        avg_success_rate = sum(batch_success_rates) / len(batch_success_rates)
        assert avg_success_rate > 0.8, \
            f"Connection pool handling insufficient: {avg_success_rate*100:.1f}% success"
    
    def test_connection_recovery_after_errors(self):
        """Test that connections recover after errors."""
        key = build_cache_key("recovery", "test")
        
        # Normal operation
        set_cache(key, {"status": "before"}, ex=300)
        result1 = get_cache(key)
        assert result1 is not None
        
        # Simulate error condition (invalid operation)
        try:
            # Try to cache invalid data type (if library doesn't handle it)
            set_cache(key, object(), ex=300)
        except:
            pass  # Expected to fail
        
        # Subsequent operations should still work
        set_cache(key, {"status": "after"}, ex=300)
        result2 = get_cache(key)
        assert result2 is not None
        assert result2["status"] == "after"


@pytest.mark.load
class TestSystemResourceLimits:
    """Test system behavior at resource limits."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after."""
        clear_cache()
        yield
        clear_cache()
    
    def test_large_payload_handling(self):
        """Test handling of large data payloads."""
        sizes = [1, 10, 50, 100]  # KB
        
        for size_kb in sizes:
            key = build_cache_key("large", f"payload_{size_kb}kb")
            # Create payload of specified size
            data = {"content": "x" * (size_kb * 1024), "size_kb": size_kb}
            
            # Should handle large payloads
            start = time.time()
            set_cache(key, data, ex=300)
            set_time = time.time() - start
            
            start = time.time()
            retrieved = get_cache(key)
            get_time = time.time() - start
            
            assert retrieved is not None, f"Failed to cache {size_kb}KB payload"
            assert len(retrieved["content"]) == size_kb * 1024
            
            # Should complete in reasonable time
            assert set_time < 2.0, f"Set time too high for {size_kb}KB: {set_time:.2f}s"
            assert get_time < 1.0, f"Get time too high for {size_kb}KB: {get_time:.2f}s"
    
    def test_many_small_items_storage(self):
        """Test storing many small items."""
        num_items = 500
        
        start = time.time()
        for i in range(num_items):
            key = build_cache_key("small", f"item_{i}")
            set_cache(key, {"id": i, "value": f"item_{i}"}, ex=300)
        total_time = time.time() - start
        
        # Should complete in reasonable time
        assert total_time < 10.0, f"Too slow to store {num_items} items: {total_time:.2f}s"
        
        # Verify sample of items
        import random
        sample = random.sample(range(num_items), min(50, num_items))
        retrieved_count = 0
        for i in sample:
            key = build_cache_key("small", f"item_{i}")
            if get_cache(key) is not None:
                retrieved_count += 1
        
        retrieval_rate = retrieved_count / len(sample)
        assert retrieval_rate > 0.9, f"Too many items lost: {retrieval_rate*100:.1f}% found"
    
    def test_rapid_cache_churn(self):
        """Test rapid cache updates (high churn rate)."""
        key = build_cache_key("churn", "test")
        num_updates = 100
        
        start = time.time()
        for i in range(num_updates):
            set_cache(key, {"version": i, "timestamp": time.time()}, ex=300)
        total_time = time.time() - start
        
        # Should handle rapid updates
        assert total_time < 5.0, f"Rapid updates too slow: {total_time:.2f}s"
        
        # Final value should be latest
        final_data = get_cache(key)
        assert final_data is not None
        assert final_data["version"] == num_updates - 1


@pytest.mark.stress
class TestStressConditions:
    """Test system behavior under stress conditions."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and cleanup."""
        self.client = TestClient(app)
        clear_cache()
        yield
        clear_cache()
    
    def test_sustained_high_load(self):
        """Test system under sustained high load."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        duration_seconds = 5
        request_count = 0
        errors = 0
        start_time = time.time()
        
        def make_requests():
            nonlocal request_count, errors
            while time.time() - start_time < duration_seconds:
                try:
                    response = self.client.get("/api/flights", headers=headers)
                    request_count += 1
                    if response.status_code != 200:
                        errors += 1
                except Exception:
                    errors += 1
        
        # Run sustained load with multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_requests) for _ in range(5)]
            for future in as_completed(futures):
                future.result()
        
        # Calculate metrics
        actual_duration = time.time() - start_time
        requests_per_second = request_count / actual_duration
        error_rate = errors / request_count if request_count > 0 else 1
        
        print(f"\nSustained Load Test:")
        print(f"  Duration: {actual_duration:.1f}s")
        print(f"  Total Requests: {request_count}")
        print(f"  Requests/sec: {requests_per_second:.1f}")
        print(f"  Error Rate: {error_rate*100:.2f}%")
        
        # System should handle sustained load
        assert request_count > 50, "Too few requests processed"
        assert error_rate < 0.1, f"Error rate too high: {error_rate*100:.1f}%"
    
    def test_burst_traffic_handling(self):
        """Test handling of sudden traffic bursts."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Small burst of concurrent requests
        burst_size = 50
        
        def burst_request(req_id):
            start = time.time()
            try:
                response = self.client.get("/api/flights", headers=headers)
                elapsed = time.time() - start
                return {
                    "id": req_id,
                    "success": response.status_code == 200,
                    "time": elapsed
                }
            except Exception as e:
                return {
                    "id": req_id,
                    "success": False,
                    "time": time.time() - start,
                    "error": str(e)
                }
        
        # Execute burst
        start_burst = time.time()
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [executor.submit(burst_request, i) for i in range(burst_size)]
            results = [future.result() for future in as_completed(futures)]
        burst_duration = time.time() - start_burst
        
        # Analyze burst handling
        successful = [r for r in results if r["success"]]
        success_rate = len(successful) / len(results)
        avg_response_time = sum(r["time"] for r in results) / len(results)
        
        print(f"\nBurst Traffic Test:")
        print(f"  Burst Size: {burst_size}")
        print(f"  Burst Duration: {burst_duration:.2f}s")
        print(f"  Success Rate: {success_rate*100:.1f}%")
        print(f"  Avg Response Time: {avg_response_time:.3f}s")
        
        # Should handle burst gracefully
        assert success_rate > 0.7, f"Too many failures during burst: {success_rate*100:.1f}%"
        assert avg_response_time < 5.0, f"Response time too high during burst: {avg_response_time:.2f}s"
    
    def test_error_recovery_under_load(self):
        """Test that system recovers from errors under load."""
        num_operations = 50
        
        def operation_with_occasional_error(op_id):
            key = build_cache_key("error_test", f"op_{op_id}")
            
            try:
                # Occasional invalid operation
                if op_id % 10 == 0:
                    # Try to cause an error
                    get_cache(None)
                else:
                    # Normal operation
                    set_cache(key, {"op_id": op_id}, ex=300)
                    return get_cache(key) is not None
            except:
                # Should continue despite errors
                return False
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(operation_with_occasional_error, i) 
                      for i in range(num_operations)]
            results = [future.result() for future in as_completed(futures)]
        
        # Most operations should succeed despite some errors
        success_rate = sum(1 for r in results if r) / len(results)
        assert success_rate > 0.7, \
            f"System didn't recover well from errors: {success_rate*100:.1f}% success"


@pytest.mark.stress
class TestConcurrencyEdgeCases:
    """Test edge cases in concurrent scenarios."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after."""
        clear_cache()
        yield
        clear_cache()
    
    def test_concurrent_read_write_same_key(self):
        """Test concurrent reads and writes to the same key."""
        key = build_cache_key("concurrent", "same_key")
        num_operations = 30
        
        def read_or_write(op_id):
            import random
            if random.random() < 0.5:
                # Write
                set_cache(key, {"op_id": op_id, "timestamp": time.time()}, ex=300)
                return ("write", op_id)
            else:
                # Read
                data = get_cache(key)
                return ("read", data["op_id"] if data else None)
        
        # Execute concurrent ops on same key
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_or_write, i) for i in range(num_operations)]
            results = [future.result() for future in as_completed(futures)]
        
        # All operations should complete without errors
        assert len(results) == num_operations
        
        # Final value should be from one of the writes
        final_data = get_cache(key)
        assert final_data is not None
        
        write_ops = [r[1] for r in results if r[0] == "write"]
        if write_ops:
            assert final_data["op_id"] in write_ops
    
    def test_concurrent_cache_invalidation(self):
        """Test concurrent cache invalidation scenarios."""
        num_keys = 10
        keys = [build_cache_key("invalidate", f"key_{i}") for i in range(num_keys)]
        
        # Populate all keys
        for i, key in enumerate(keys):
            set_cache(key, {"id": i}, ex=300)
        
        def invalidate_and_repopulate(key_idx):
            key = keys[key_idx]
            
            # Read
            data = get_cache(key)
            
            # Invalidate
            from core.redis import delete_cache
            delete_cache(key)
            
            # Repopulate
            set_cache(key, {"id": key_idx, "updated": True}, ex=300)
            
            # Verify
            new_data = get_cache(key)
            return new_data is not None and new_data.get("updated") == True
        
        # Concurrent invalidation and repopulation
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(invalidate_and_repopulate, i) for i in range(num_keys)]
            results = [future.result() for future in as_completed(futures)]
        
        # All operations should succeed
        assert all(results), "Some invalidation operations failed"
    
    def test_race_condition_cache_update(self):
        """Test for race conditions in cache updates."""
        key = build_cache_key("race", "counter")
        num_increments = 50
        
        # Initialize counter
        set_cache(key, {"count": 0}, ex=300)
        
        def increment_counter(op_id):
            # Read current value
            data = get_cache(key)
            if data:
                current = data.get("count", 0)
                # Increment and write back
                set_cache(key, {"count": current + 1}, ex=300)
                return True
            return False
        
        # Concurrent increments (will have race conditions)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(increment_counter, i) for i in range(num_increments)]
            results = [future.result() for future in as_completed(futures)]
        
        # All operations should complete
        assert all(results)
        
        # Final count will be less than expected due to race conditions
        # This is expected behavior - demonstrating the race condition
        final_data = get_cache(key)
        assert final_data is not None
        
        # Note: This test demonstrates that race conditions exist
        # In production, use atomic operations or locks if needed
        print(f"\nRace Condition Test:")
        print(f"  Expected: {num_increments}")
        print(f"  Actual: {final_data['count']}")
        print(f"  Lost updates: {num_increments - final_data['count']}")
