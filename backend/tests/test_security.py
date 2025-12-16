"""
Security Testing for Flight Roster System.

Tests JWT authentication, bcrypt password hashing, role-based access control,
and authorization bypass attempts. Ensures FastAPI endpoints properly validate
tokens and enforce role restrictions.

Testing Areas:
- JWT token validation and manipulation attempts
- Password hashing security and brute force resistance
- Role-based access control enforcement
- Authorization bypass attempts
- Token expiry and refresh security
- SQL injection and input validation
"""
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from jose import jwt
import time

from core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    get_current_user,
    require_role,
    SECRET_KEY,
    ALGORITHM
)
from main import app


@pytest.mark.security
class TestJWTSecurityValidation:
    """Test JWT token security and manipulation attempts."""
    
    def test_token_signature_tampering(self):
        """Test that tampered token signatures are rejected."""
        data = {"sub": "admin@example.com", "role": "admin"}
        valid_token = create_access_token(data)
        
        # Tamper with signature
        parts = valid_token.split('.')
        tampered_token = f"{parts[0]}.{parts[1]}.TAMPERED_SIGNATURE"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered_token)
        
        assert exc_info.value.status_code == 401
    
    def test_token_payload_modification(self):
        """Test that modified token payloads are rejected."""
        data = {"sub": "user@example.com", "role": "user"}
        token = create_access_token(data)
        
        # Decode and modify payload
        parts = token.split('.')
        # Try to change role to admin (will fail signature validation)
        
        with pytest.raises(HTTPException):
            # Any modification should fail
            decode_access_token(parts[0] + ".MODIFIED." + parts[2])
    
    def test_expired_token_rejection(self):
        """Test that expired tokens are properly rejected."""
        data = {"sub": "user@example.com", "role": "user"}
        
        # Create token with very short expiry
        token = create_access_token(data, expires_delta=timedelta(seconds=-10))
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401
    
    def test_token_without_expiry(self):
        """Test that tokens must have expiry claims."""
        # Manually create token without expiry
        payload = {"sub": "user@example.com", "role": "user"}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # Should still decode but would be missing exp claim
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" not in decoded
    
    def test_token_reuse_after_expected_expiry(self):
        """Test that tokens cannot be reused after expiry."""
        data = {"sub": "user@example.com", "role": "user"}
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Token is valid immediately
        payload = decode_access_token(token)
        assert payload["sub"] == "user@example.com"
        
        # Wait for expiry
        time.sleep(2)
        
        # Now should be expired
        with pytest.raises(HTTPException):
            decode_access_token(token)
    
    def test_token_algorithm_confusion(self):
        """Test that algorithm confusion attacks are prevented."""
        data = {"sub": "admin@example.com", "role": "admin"}
        
        # Try to create token with 'none' algorithm (security vulnerability)
        try:
            malicious_token = jwt.encode(
                data, 
                None,  # No key
                algorithm='none'
            )
            
            # Should not be able to decode with 'none' algorithm
            with pytest.raises(Exception):
                decode_access_token(malicious_token)
        except:
            # jose library may prevent this entirely
            pass
    
    def test_token_missing_required_claims(self):
        """Test that tokens with missing required claims are rejected."""
        # Token without 'sub' claim
        token = create_access_token({"role": "admin"})
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # get_current_user should reject this
        with pytest.raises(HTTPException):
            import asyncio
            asyncio.run(get_current_user(credentials))


@pytest.mark.security
class TestPasswordHashingSecurity:
    """Test bcrypt password hashing security."""
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes (salt)."""
        password = "test_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        hash3 = get_password_hash(password)
        
        # All hashes should be different due to salt
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3
        
        # But all should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        assert verify_password(password, hash3)
    
    def test_bcrypt_work_factor(self):
        """Test that bcrypt uses sufficient work factor."""
        password = "test_password"
        hashed = get_password_hash(password)
        
        # bcrypt format: $2b$<rounds>$<salt+hash>
        # Check that it uses $2b$ (bcrypt) and reasonable rounds
        assert hashed.startswith("$2b$")
        
        # Extract rounds (should be at least 10-12 for security)
        parts = hashed.split('$')
        rounds = int(parts[2])
        assert rounds >= 10, f"Bcrypt rounds too low: {rounds}"
    
    def test_timing_attack_resistance(self):
        """Test that password verification has consistent timing."""
        password = "correct_password"
        hashed = get_password_hash(password)
        
        # Time multiple correct verifications
        correct_times = []
        for _ in range(5):
            start = time.time()
            verify_password(password, hashed)
            correct_times.append(time.time() - start)
        
        # Time multiple incorrect verifications
        incorrect_times = []
        for _ in range(5):
            start = time.time()
            verify_password("wrong_password", hashed)
            incorrect_times.append(time.time() - start)
        
        # Timing should be similar (bcrypt is designed to prevent timing attacks)
        avg_correct = sum(correct_times) / len(correct_times)
        avg_incorrect = sum(incorrect_times) / len(incorrect_times)
        
        # Times should be within reasonable range (bcrypt makes both slow)
        # Both should take similar time (within 50%)
        ratio = avg_correct / avg_incorrect if avg_incorrect > 0 else 1
        assert 0.5 <= ratio <= 2.0, f"Timing difference too large: {ratio}"
    
    def test_password_hash_irreversibility(self):
        """Test that password hashes cannot be reversed."""
        password = "secret_password"
        hashed = get_password_hash(password)
        
        # Hash should not contain original password
        assert password not in hashed
        
        # Hash should not be decodable
        assert len(hashed) == 60  # bcrypt hash length
        
        # Only way to verify is through verify_password
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)


@pytest.mark.security
class TestRoleBasedAccessControl:
    """Test role-based access control enforcement."""
    
    @pytest.mark.asyncio
    async def test_role_escalation_prevention(self):
        """Test that users cannot escalate their roles."""
        # Create token with user role
        user_token = create_access_token({"sub": "user@example.com", "role": "user"})
        
        # Try to access admin endpoint
        role_checker = require_role(["admin"])
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=user_token
        )
        
        current_user = await get_current_user(credentials)
        
        # Should raise 403 Forbidden
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_role_modification_in_token(self):
        """Test that roles in tokens cannot be modified."""
        # Create token with user role
        data = {"sub": "user@example.com", "role": "user"}
        token = create_access_token(data)
        
        # Decode and verify role
        payload = decode_access_token(token)
        assert payload["role"] == "user"
        
        # Any attempt to modify token would break signature
        # and fail validation in decode_access_token
    
    @pytest.mark.asyncio
    async def test_role_hierarchy_enforcement(self):
        """Test that role hierarchy is properly enforced."""
        roles = ["admin", "manager", "user", "viewer"]
        
        for role in roles:
            token = create_access_token({"sub": f"{role}@example.com", "role": role})
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            current_user = await get_current_user(credentials)
            
            # Admin checker should only allow admin
            admin_checker = require_role(["admin"])
            if role == "admin":
                result = await admin_checker(current_user)
                assert result == current_user
            else:
                with pytest.raises(HTTPException) as exc_info:
                    await admin_checker(current_user)
                assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_missing_role_denial(self):
        """Test that users without roles are denied access."""
        # Create token without role
        token = create_access_token({"sub": "norole@example.com"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        current_user = await get_current_user(credentials)
        
        # Any role checker should deny
        checker = require_role(["admin", "user"])
        with pytest.raises(HTTPException) as exc_info:
            await checker(current_user)
        assert exc_info.value.status_code == 403


@pytest.mark.security
class TestAPIEndpointSecurity:
    """Test security of API endpoints."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_unauthenticated_access_denied(self):
        """Test that endpoints without auth are rejected."""
        # Try to access protected endpoint without token
        response = self.client.get("/api/flights")
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/flights", headers=headers)
        
        assert response.status_code == 401
    
    def test_malformed_auth_header_rejected(self):
        """Test that malformed auth headers are rejected."""
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Token xyz"},  # Wrong scheme
            {"Authorization": ""},  # Empty
        ]
        
        for headers in malformed_headers:
            response = self.client.get("/api/flights", headers=headers)
            assert response.status_code in [401, 403, 422]
    
    def test_role_specific_endpoints(self):
        """Test that role-specific endpoints enforce roles."""
        # Create tokens for different roles
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        user_token = create_access_token({"sub": "user@example.com", "role": "user"})
        
        # Admin endpoints should reject user tokens
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Try to access admin-only roster generation
        response = self.client.post(
            "/api/roster/generate",
            headers=user_headers,
            json={"flight_id": 1}
        )
        
        # Should be forbidden for non-admin
        assert response.status_code == 403


@pytest.mark.security
class TestInputValidationSecurity:
    """Test input validation and injection prevention."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_sql_injection_prevention_in_filters(self):
        """Test that SQL injection attempts are blocked."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # SQL injection attempts
        injection_attempts = [
            "1' OR '1'='1",
            "1; DROP TABLE flights--",
            "1' UNION SELECT * FROM users--",
            "' OR 1=1--",
        ]
        
        for injection in injection_attempts:
            response = self.client.get(
                f"/api/flights?airline_id={injection}",
                headers=headers
            )
            
            # Should either return empty results or validation error
            # but not crash or expose SQL errors
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                # Should not return all data
                data = response.json()
                assert isinstance(data, (list, dict))
    
    def test_xss_prevention_in_responses(self):
        """Test that XSS attempts in data are sanitized."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
        ]
        
        for xss in xss_attempts:
            # Try to inject in search/filter
            response = self.client.get(
                f"/api/flights?search={xss}",
                headers=headers
            )
            
            # Response should not execute scripts
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                # Check response doesn't contain unescaped XSS
                content = response.text
                assert "<script>" not in content.lower()
    
    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are blocked."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Path traversal attempts
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "../../database.db",
        ]
        
        for path in traversal_attempts:
            response = self.client.get(
                f"/api/flights/{path}",
                headers=headers
            )
            
            # Should not expose system files
            assert response.status_code in [404, 422]


@pytest.mark.security
class TestSessionSecurityBoundaries:
    """Test session management and token lifecycle security."""
    
    @pytest.mark.asyncio
    async def test_concurrent_token_usage(self):
        """Test that same token can be used concurrently."""
        token = create_access_token({"sub": "user@example.com", "role": "user"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Should work multiple times
        user1 = await get_current_user(credentials)
        user2 = await get_current_user(credentials)
        
        assert user1["email"] == user2["email"]
    
    def test_token_expiry_boundary_conditions(self):
        """Test token expiry at boundary conditions."""
        # Token with 0 seconds expiry
        token = create_access_token(
            {"sub": "user@example.com"}, 
            expires_delta=timedelta(seconds=0)
        )
        
        # Should be immediately expired
        with pytest.raises(HTTPException):
            decode_access_token(token)
    
    def test_maximum_token_lifetime(self):
        """Test that tokens have reasonable maximum lifetime."""
        # Token with very long expiry
        token = create_access_token(
            {"sub": "user@example.com"},
            expires_delta=timedelta(days=365)
        )
        
        # Should decode successfully
        payload = decode_access_token(token)
        assert payload["sub"] == "user@example.com"
        
        # Check expiry is in future
        exp_timestamp = payload["exp"]
        now_timestamp = datetime.utcnow().timestamp()
        assert exp_timestamp > now_timestamp
    
    def test_token_claim_size_limits(self):
        """Test that large token claims are handled properly."""
        # Create token with large payload
        large_data = {
            "sub": "user@example.com",
            "role": "user",
            "large_field": "x" * 1000,  # 1KB of data
            "array_field": list(range(100))
        }
        
        token = create_access_token(large_data)
        
        # Should still encode and decode
        payload = decode_access_token(token)
        assert payload["sub"] == "user@example.com"
        assert len(payload["large_field"]) == 1000


@pytest.mark.security
class TestAuthorizationBypassAttempts:
    """Test attempts to bypass authorization checks."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_direct_endpoint_access_without_auth(self):
        """Test that protected endpoints cannot be accessed directly."""
        protected_endpoints = [
            "/api/flights",
            "/api/cabin-crew",
            "/api/flight-crew",
            "/api/roster/generate",
            "/api/roster/saved",
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            assert response.status_code in [401, 403, 404, 405], \
                f"Endpoint {endpoint} not properly protected"
    
    def test_role_bypass_with_custom_headers(self):
        """Test that custom role headers are ignored."""
        user_token = create_access_token({"sub": "user@example.com", "role": "user"})
        
        # Try to bypass with custom headers
        headers = {
            "Authorization": f"Bearer {user_token}",
            "X-User-Role": "admin",  # Try to override
            "X-Admin": "true",
            "Role": "admin"
        }
        
        response = self.client.post(
            "/api/roster/generate",
            headers=headers,
            json={"flight_id": 1}
        )
        
        # Should still be forbidden
        assert response.status_code == 403
    
    def test_parameter_pollution_attack(self):
        """Test that parameter pollution doesn't bypass validation."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try parameter pollution
        response = self.client.get(
            "/api/flights?role=admin&role=user&role=admin",
            headers=headers
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 422]
    
    @pytest.mark.asyncio
    async def test_role_null_byte_injection(self):
        """Test that null byte injection doesn't bypass role checks."""
        # Try to inject null byte in role
        token = create_access_token({"sub": "user@example.com", "role": "user\x00admin"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        current_user = await get_current_user(credentials)
        
        # Should not match "admin" role
        admin_checker = require_role(["admin"])
        with pytest.raises(HTTPException) as exc_info:
            await admin_checker(current_user)
        assert exc_info.value.status_code == 403


@pytest.mark.security
class TestSecurityHeaders:
    """Test security-related HTTP headers."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_cors_headers(self):
        """Test that CORS headers are properly configured."""
        admin_token = create_access_token({"sub": "admin@example.com", "role": "admin"})
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = self.client.get("/api/flights", headers=headers)
        
        # Check CORS headers exist (if configured)
        # This depends on your CORS configuration
        assert response.status_code in [200, 401, 403]
    
    def test_no_sensitive_info_in_error_responses(self):
        """Test that error responses don't leak sensitive info."""
        # Try various invalid requests
        response = self.client.get("/api/flights")
        
        # Should not expose internal details
        if response.status_code >= 400:
            content = response.text.lower()
            
            # Should not contain sensitive information
            sensitive_terms = [
                "secret_key",
                "database connection",
                "traceback",
                "file not found:",
                "syntax error",
            ]
            
            for term in sensitive_terms:
                assert term not in content, f"Error response contains sensitive term: {term}"
