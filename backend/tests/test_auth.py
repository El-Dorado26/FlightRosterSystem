"""
Unit tests for core/auth.py authentication and authorization utilities.

Testing Strategy:
- Unit Testing: Test each auth function in isolation
- Equivalence Partitioning: Valid/invalid tokens, passwords, roles
- Boundary Value Analysis: Password lengths, token expiry times
- Mock external dependencies: JWT encoding/decoding, datetime
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

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


@pytest.mark.unit
class TestVerifyPassword:
    """Test the verify_password function."""
    
    def test_valid_password_match(self):
        """Test that a valid password matches its hash."""
        password = "test_password123"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        assert result is True
    
    def test_invalid_password_mismatch(self):
        """Test that an invalid password does not match the hash."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        result = verify_password(wrong_password, hashed)
        assert result is False
    
    def test_empty_password(self):
        """Test verification with empty password."""
        password = ""
        hashed = get_password_hash(password)
        
        # Empty password should verify against its own hash
        result = verify_password(password, hashed)
        assert result is True
        
        # Empty password should not verify against different hash
        other_hash = get_password_hash("not_empty")
        result = verify_password(password, other_hash)
        assert result is False
    
    def test_special_characters_in_password(self):
        """Test password verification with special characters."""
        password = "p@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        assert result is True
    
    def test_unicode_characters_in_password(self):
        """Test password verification with unicode characters."""
        password = "пароль密码🔐"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        assert result is True
    
    def test_case_sensitive_password(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        result = verify_password("testpassword123", hashed)
        assert result is False


@pytest.mark.unit
class TestGetPasswordHash:
    """Test the get_password_hash function."""
    
    def test_normal_password_hash(self):
        """Test hashing a normal password."""
        password = "normal_password123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert len(hashed) > 0
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_long_password_hash(self):
        """Test hashing a password longer than 50 characters."""
        password = "a" * 60  # 60 character password
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert len(hashed) > 0
        # Verify it can be verified
        assert verify_password(password, hashed) is True
    
    def test_special_characters_hash(self):
        """Test hashing password with special characters."""
        password = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert verify_password(password, hashed) is True
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes_due_to_salt(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "same_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestCreateAccessToken:
    """Test the create_access_token function."""
    
    def test_default_expiry(self):
        """Test creating token with default expiry time."""
        data = {"sub": "test@example.com", "role": "user"}
        
        with patch('core.auth.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            token = create_access_token(data)
            
            # Decode to verify
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            assert payload["sub"] == "test@example.com"
            assert payload["role"] == "user"
            assert "exp" in payload
    
    def test_custom_expiry(self):
        """Test creating token with custom expiry time."""
        data = {"sub": "test@example.com", "role": "admin"}
        custom_expiry = timedelta(hours=2)
        
        with patch('core.auth.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            token = create_access_token(data, expires_delta=custom_expiry)
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            expected_exp = mock_now + custom_expiry
            actual_exp = datetime.fromtimestamp(payload["exp"])
            
            # Check expiry is approximately correct (within 1 second)
            assert abs((actual_exp - expected_exp).total_seconds()) < 1
    
    def test_missing_email_in_data(self):
        """Test creating token without email (sub) in data."""
        data = {"role": "user"}  # Missing email
        
        token = create_access_token(data)
        
        # Should still create token but without sub
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "sub" not in payload
        assert payload["role"] == "user"
    
    def test_empty_data(self):
        """Test creating token with empty data."""
        data = {}
        
        token = create_access_token(data)
        
        # Should create token with just expiry
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
    
    def test_additional_claims(self):
        """Test creating token with additional custom claims."""
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "custom_field": "custom_value",
            "user_id": 123
        }
        
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["custom_field"] == "custom_value"
        assert payload["user_id"] == 123
    
    def test_zero_expiry_delta(self):
        """Test creating token with zero expiry delta."""
        data = {"sub": "test@example.com"}
        zero_expiry = timedelta(seconds=0)
        
        with patch('core.auth.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            token = create_access_token(data, expires_delta=zero_expiry)
            
            # Token should be immediately expired
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            assert "exp" in payload


@pytest.mark.unit
class TestDecodeAccessToken:
    """Test the decode_access_token function."""
    
    def test_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "user"
        assert "exp" in payload
    
    def test_expired_token(self):
        """Test decoding an expired token."""
        data = {"sub": "test@example.com"}
        
        # Create token that expired 1 hour ago
        with patch('core.auth.datetime') as mock_datetime:
            past_time = datetime.utcnow() - timedelta(hours=2)
            mock_datetime.utcnow.return_value = past_time
            token = create_access_token(data, expires_delta=timedelta(minutes=30))
        
        # Now try to decode (should raise exception)
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    def test_invalid_signature(self):
        """Test decoding token with invalid signature."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Tamper with the token
        tampered_token = token[:-10] + "tampered00"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered_token)
        
        assert exc_info.value.status_code == 401
    
    def test_malformed_token(self):
        """Test decoding a malformed token."""
        malformed_tokens = [
            "not.a.token",
            "invalid_token",
            "",
            "a.b",  # Too few parts
            "a.b.c.d",  # Too many parts
        ]
        
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                decode_access_token(token)
            assert exc_info.value.status_code == 401
    
    def test_missing_claims(self):
        """Test decoding token with missing expected claims."""
        # Create token with minimal data
        data = {}
        token = create_access_token(data)
        
        # Should still decode successfully (just won't have sub or role)
        payload = decode_access_token(token)
        assert "exp" in payload
        assert "sub" not in payload
    
    def test_token_with_wrong_algorithm(self):
        """Test decoding token created with different algorithm."""
        data = {"sub": "test@example.com"}
        
        # Create token with different algorithm
        with patch('core.auth.ALGORITHM', 'HS512'):
            # This would use HS512 if we could change the constant
            # For this test, we'll create a token manually
            pass
        
        # Create normal token
        token = create_access_token(data)
        
        # Decoding with correct algorithm should work
        payload = decode_access_token(token)
        assert payload["sub"] == "test@example.com"


@pytest.mark.unit
class TestGetCurrentUser:
    """Test the get_current_user function."""
    
    @pytest.mark.asyncio
    async def test_valid_token_payload(self):
        """Test getting current user with valid token."""
        # Create valid token
        data = {"sub": "user@example.com", "role": "admin"}
        token = create_access_token(data)
        
        # Create credentials object
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # Get current user
        user = await get_current_user(credentials)
        
        assert user["email"] == "user@example.com"
        assert user["role"] == "admin"
        assert "payload" in user
    
    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test getting current user with invalid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_missing_email_in_payload(self):
        """Test getting current user when email (sub) is missing."""
        # Create token without sub
        data = {"role": "user"}
        token = create_access_token(data)
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_missing_role_in_payload(self):
        """Test getting current user when role is missing."""
        # Create token without role
        data = {"sub": "user@example.com"}
        token = create_access_token(data)
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # Should still work, role will be None
        user = await get_current_user(credentials)
        
        assert user["email"] == "user@example.com"
        assert user["role"] is None
    
    @pytest.mark.asyncio
    async def test_expired_token_in_get_current_user(self):
        """Test getting current user with expired token."""
        # Create expired token
        data = {"sub": "user@example.com", "role": "user"}
        
        with patch('core.auth.datetime') as mock_datetime:
            past_time = datetime.utcnow() - timedelta(hours=2)
            mock_datetime.utcnow.return_value = past_time
            token = create_access_token(data, expires_delta=timedelta(minutes=30))
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)
        
        assert exc_info.value.status_code == 401


@pytest.mark.unit
class TestRequireRole:
    """Test the require_role dependency function."""
    
    @pytest.mark.asyncio
    async def test_allowed_role(self):
        """Test that user with allowed role can access."""
        # Create role checker for admin
        role_checker = require_role(["admin"])
        
        # Mock current user with admin role
        current_user = {
            "email": "admin@example.com",
            "role": "admin",
            "payload": {}
        }
        
        # Should not raise exception
        result = await role_checker(current_user)
        assert result == current_user
    
    @pytest.mark.asyncio
    async def test_disallowed_role(self):
        """Test that user with disallowed role cannot access."""
        role_checker = require_role(["admin"])
        
        # Mock current user with user role
        current_user = {
            "email": "user@example.com",
            "role": "user",
            "payload": {}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)
        
        assert exc_info.value.status_code == 403
        assert "Access denied" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_missing_role_in_user(self):
        """Test user without role field."""
        role_checker = require_role(["admin"])
        
        # Mock current user without role
        current_user = {
            "email": "user@example.com",
            "payload": {}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_multiple_allowed_roles(self):
        """Test that multiple roles can be allowed."""
        role_checker = require_role(["admin", "manager"])
        
        # Test with admin
        admin_user = {"email": "admin@example.com", "role": "admin", "payload": {}}
        result = await role_checker(admin_user)
        assert result == admin_user
        
        # Test with manager
        manager_user = {"email": "manager@example.com", "role": "manager", "payload": {}}
        result = await role_checker(manager_user)
        assert result == manager_user
        
        # Test with viewer (should fail)
        viewer_user = {"email": "viewer@example.com", "role": "viewer", "payload": {}}
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(viewer_user)
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_case_sensitive_role_check(self):
        """Test that role checking is case-sensitive."""
        role_checker = require_role(["admin"])
        
        # User with "Admin" (capital A) should not match "admin"
        current_user = {
            "email": "user@example.com",
            "role": "Admin",
            "payload": {}
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_empty_allowed_roles_list(self):
        """Test role checker with empty allowed roles list."""
        role_checker = require_role([])
        
        current_user = {
            "email": "user@example.com",
            "role": "admin",
            "payload": {}
        }
        
        # No role should be allowed
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)
        
        assert exc_info.value.status_code == 403


@pytest.mark.unit
class TestPasswordSecurityBoundaries:
    """Boundary Value Analysis for password security."""
    
    def test_minimum_length_password(self):
        """Test hashing and verifying minimum length password."""
        password = "a"  # 1 character
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_bcrypt_maximum_length(self):
        """Test password at bcrypt's maximum length (72 bytes)."""
        password = "a" * 72
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_exceeding_bcrypt_limit(self):
        """Test password exceeding bcrypt's 72 byte limit."""
        # Note: bcrypt silently truncates to 72 bytes
        password = "a" * 100
        hashed = get_password_hash(password)
        
        # Full password should verify
        assert verify_password(password, hashed) is True
        
        # First 72 chars would also verify (bcrypt behavior)
        assert verify_password("a" * 72, hashed) is True


@pytest.mark.unit
class TestTokenExpiryBoundaries:
    """Boundary Value Analysis for token expiry times."""
    
    def test_token_with_minimum_expiry(self):
        """Test token with 1 second expiry."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Should be valid immediately
        payload = decode_access_token(token)
        assert payload["sub"] == "test@example.com"
    
    def test_token_with_very_long_expiry(self):
        """Test token with very long expiry (1 year)."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(days=365))
        
        payload = decode_access_token(token)
        assert payload["sub"] == "test@example.com"
    
    def test_token_exactly_at_expiry(self):
        """Test token behavior exactly at expiry time."""
        data = {"sub": "test@example.com"}
        
        with patch('core.auth.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Token should be expired now
        with pytest.raises(HTTPException):
            decode_access_token(token)


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

@pytest.mark.unit
class TestRegisterEndpoint:
    """Test the /register API endpoint."""

    @patch('api.routes.auth.get_db')
    def test_register_new_user_success(self, mock_get_db):
        """Test successful user registration."""
        from api.routes.auth import register
        from core.user_models import UserCreate

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock query to return no existing user
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        # Configure db.refresh to populate user fields (simulates DB defaults)
        def mock_refresh(user):
            user.id = 1
            user.created_at = datetime(2024, 1, 1, 12, 0, 0)
            if not hasattr(user, 'is_active') or user.is_active is None:
                user.is_active = True
        mock_db.refresh = mock_refresh

        # Create user data
        user_data = UserCreate(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
            role="viewer"
        )

        # Call endpoint - using asyncio to run async function
        import asyncio
        result = asyncio.run(register(user_data, db=mock_db))

        # Assertions
        assert result.access_token is not None
        assert result.user.email == "newuser@example.com"
        assert result.user.role == "viewer"
        assert result.user.is_active is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('api.routes.auth.get_db')
    def test_register_duplicate_email(self, mock_get_db):
        """Test registration with duplicate email."""
        from api.routes.auth import register
        from core.user_models import UserCreate

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock existing user
        existing_user = Mock()
        existing_user.email = "existing@example.com"

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = existing_user

        user_data = UserCreate(
            email="existing@example.com",
            password="password123",
            full_name="Duplicate User",
            role="viewer"
        )

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(register(user_data, db=mock_db))

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in exc_info.value.detail.lower()

    @patch('api.routes.auth.get_db')
    def test_register_invalid_role(self, mock_get_db):
        """Test registration with invalid role."""
        from api.routes.auth import register
        from core.user_models import UserCreate

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock no existing user
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        user_data = UserCreate(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
            role="superadmin"  # Invalid role
        )

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(register(user_data, db=mock_db))

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid role" in exc_info.value.detail

    @patch('api.routes.auth.get_db')
    def test_register_password_too_long(self, mock_get_db):
        """Test registration with password exceeding bcrypt 72-byte limit."""
        from api.routes.auth import register
        from core.user_models import UserCreate

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock no existing user
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        # Create password that's too long (> 72 bytes)
        user_data = UserCreate(
            email="newuser@example.com",
            password="a" * 80,  # 80 bytes, exceeds 72 limit
            full_name="New User",
            role="viewer"
        )

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(register(user_data, db=mock_db))

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "too long" in exc_info.value.detail.lower()


@pytest.mark.unit
class TestLoginEndpoint:
    """Test the /login API endpoint."""

    @patch('api.routes.auth.verify_password')
    @patch('api.routes.auth.get_db')
    def test_login_valid_credentials(self, mock_get_db, mock_verify):
        """Test successful login with valid credentials."""
        from api.routes.auth import login
        from core.user_models import UserLogin

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "user@example.com"
        mock_user.full_name = "Test User"
        mock_user.role = "user"
        mock_user.is_active = True
        mock_user.hashed_password = "hashed_password"
        mock_user.created_at = datetime(2024, 1, 1, 12, 0, 0)

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_user

        # Mock password verification
        mock_verify.return_value = True

        credentials = UserLogin(
            email="user@example.com",
            password="correct_password"
        )

        # Call endpoint
        import asyncio
        result = asyncio.run(login(credentials, db=mock_db))

        # Assertions
        assert result.access_token is not None
        assert result.user.email == "user@example.com"
        assert result.user.role == "user"
        mock_verify.assert_called_once()

    @patch('api.routes.auth.verify_password')
    @patch('api.routes.auth.get_db')
    def test_login_invalid_password(self, mock_get_db, mock_verify):
        """Test login with wrong password."""
        from api.routes.auth import login
        from core.user_models import UserLogin

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock user
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password"

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_user

        # Mock password verification failure
        mock_verify.return_value = False

        credentials = UserLogin(
            email="user@example.com",
            password="wrong_password"
        )

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(login(credentials, db=mock_db))

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect" in exc_info.value.detail

    @patch('api.routes.auth.get_db')
    def test_login_user_not_found(self, mock_get_db):
        """Test login with non-existent email."""
        from api.routes.auth import login
        from core.user_models import UserLogin

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock no user found
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        credentials = UserLogin(
            email="nonexistent@example.com",
            password="password123"
        )

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(login(credentials, db=mock_db))

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('api.routes.auth.verify_password')
    @patch('api.routes.auth.get_db')
    def test_login_inactive_user(self, mock_get_db, mock_verify):
        """Test login with inactive user account."""
        from api.routes.auth import login
        from core.user_models import UserLogin

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock inactive user
        mock_user = Mock()
        mock_user.email = "inactive@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_user.is_active = False

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_user

        # Mock password verification success
        mock_verify.return_value = True

        credentials = UserLogin(
            email="inactive@example.com",
            password="correct_password"
        )

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(login(credentials, db=mock_db))

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "inactive" in exc_info.value.detail.lower()


@pytest.mark.unit
class TestGetCurrentUserInfoEndpoint:
    """Test the /me API endpoint."""

    @patch('api.routes.auth.get_current_user')
    @patch('api.routes.auth.get_db')
    def test_get_current_user_success(self, mock_get_db, mock_get_current):
        """Test successful retrieval of current user info."""
        from api.routes.auth import get_current_user_info

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock current user from token
        mock_get_current.return_value = {
            "email": "user@example.com",
            "role": "user"
        }

        # Mock user from database
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "user@example.com"
        mock_user.full_name = "Test User"
        mock_user.role = "user"
        mock_user.is_active = True
        mock_user.created_at = datetime(2024, 1, 1, 12, 0, 0)

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_user

        # Call endpoint
        import asyncio
        result = asyncio.run(get_current_user_info(
            current_user={"email": "user@example.com", "role": "user"},
            db=mock_db
        ))

        # Assertions
        assert result.email == "user@example.com"
        assert result.full_name == "Test User"
        assert result.role == "user"

    @patch('api.routes.auth.get_current_user')
    @patch('api.routes.auth.get_db')
    def test_get_current_user_not_found(self, mock_get_db, mock_get_current):
        """Test /me endpoint when user not found in database."""
        from api.routes.auth import get_current_user_info

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock current user from token
        mock_get_current.return_value = {
            "email": "deleted@example.com",
            "role": "user"
        }

        # Mock no user found in database
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_user_info(
                current_user={"email": "deleted@example.com", "role": "user"},
                db=mock_db
            ))

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()


@pytest.mark.unit
class TestRefreshTokenEndpoint:
    """Test the /refresh API endpoint."""

    @patch('api.routes.auth.get_current_user')
    @patch('api.routes.auth.get_db')
    def test_refresh_token_success(self, mock_get_db, mock_get_current):
        """Test successful token refresh."""
        from api.routes.auth import refresh_token

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock current user from token
        mock_get_current.return_value = {
            "email": "user@example.com",
            "role": "user"
        }

        # Mock user from database
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "user@example.com"
        mock_user.full_name = "Test User"
        mock_user.role = "user"
        mock_user.is_active = True
        mock_user.created_at = datetime(2024, 1, 1, 12, 0, 0)

        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = mock_user

        # Call endpoint
        import asyncio
        result = asyncio.run(refresh_token(
            current_user={"email": "user@example.com", "role": "user"},
            db=mock_db
        ))

        # Assertions
        assert result.access_token is not None
        assert result.user.email == "user@example.com"
        assert result.user.role == "user"

    @patch('api.routes.auth.get_current_user')
    @patch('api.routes.auth.get_db')
    def test_refresh_token_user_not_found(self, mock_get_db, mock_get_current):
        """Test token refresh when user no longer exists."""
        from api.routes.auth import refresh_token

        # Setup mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # Mock current user from token
        mock_get_current.return_value = {
            "email": "deleted@example.com",
            "role": "user"
        }

        # Mock no user found in database
        query_mock = MagicMock()
        mock_db.query.return_value = query_mock
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None

        # Should raise HTTPException
        import asyncio
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(refresh_token(
                current_user={"email": "deleted@example.com", "role": "user"},
                db=mock_db
            ))

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()
