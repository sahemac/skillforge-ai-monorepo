"""
Authentication endpoint tests for SkillForge AI User Service
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.conftest import UserFactory, assert_response_error


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_success(self, client: TestClient, mock_email_service):
        """Test successful user registration."""
        user_data = UserFactory.build()
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["email"] == user_data["email"]
        assert response_data["username"] == user_data["username"]
        assert response_data["first_name"] == user_data["first_name"]
        assert response_data["last_name"] == user_data["last_name"]
        assert "hashed_password" not in response_data
    
    def test_register_duplicate_email(self, client: TestClient, create_test_user, mock_email_service):
        """Test registration with duplicate email fails."""
        # Create existing user
        existing_user_data = UserFactory.build(email="test@example.com")
        client.post("/api/v1/auth/register", json=existing_user_data)
        
        # Try to register with same email
        duplicate_data = UserFactory.build(email="test@example.com", username="different")
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert_response_error(response, 400, "already exists")
    
    def test_register_duplicate_username(self, client: TestClient, mock_email_service):
        """Test registration with duplicate username fails."""
        # Create existing user
        existing_user_data = UserFactory.build(username="testuser")
        client.post("/api/v1/auth/register", json=existing_user_data)
        
        # Try to register with same username
        duplicate_data = UserFactory.build(email="different@example.com", username="testuser")
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert_response_error(response, 400, "already taken")
    
    def test_register_password_mismatch(self, client: TestClient):
        """Test registration with mismatched passwords fails."""
        user_data = UserFactory.build(confirm_password="DifferentPassword123!")
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert_response_error(response, 422)
    
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password fails."""
        user_data = UserFactory.build(password="weak", confirm_password="weak")
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert_response_error(response, 400, "Password validation failed")
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email fails."""
        user_data = UserFactory.build(email="invalid-email")
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    def test_register_terms_not_accepted(self, client: TestClient):
        """Test registration without accepting terms fails."""
        user_data = UserFactory.build(terms_accepted=False)
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert_response_error(response, 422)


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client: TestClient, create_test_user):
        """Test successful user login."""
        user = None
        # Need to use asyncio to create user in sync test
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user()
        
        asyncio.run(create_user())
        
        login_data = {
            "email": user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
        assert "expires_in" in response_data
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert_response_error(response, 401, "Incorrect email or password")
    
    def test_login_wrong_password(self, client: TestClient, create_test_user):
        """Test login with wrong password fails."""
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user()
        
        asyncio.run(create_user())
        
        login_data = {
            "email": user.email,
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert_response_error(response, 401, "Incorrect email or password")
    
    def test_login_remember_me(self, client: TestClient, create_test_user):
        """Test login with remember me option."""
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user()
        
        asyncio.run(create_user())
        
        login_data = {
            "email": user.email,
            "password": "TestPassword123!",
            "remember_me": True
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # With remember me, token should have longer expiry
        assert response_data["expires_in"] > 3600  # More than 1 hour


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, client: TestClient, create_test_user):
        """Test successful token refresh."""
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user()
        
        asyncio.run(create_user())
        
        # First login to get tokens
        login_data = {
            "email": user.email,
            "password": "TestPassword123!"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        login_data_response = login_response.json()
        
        # Use refresh token to get new tokens
        refresh_data = {
            "refresh_token": login_data_response["refresh_token"]
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
        
        # New tokens should be different
        assert response_data["access_token"] != login_data_response["access_token"]
        assert response_data["refresh_token"] != login_data_response["refresh_token"]
    
    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token fails."""
        refresh_data = {
            "refresh_token": "invalid_token"
        }
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert_response_error(response, 401, "Invalid refresh token")


class TestLogout:
    """Test logout endpoints."""
    
    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        client, user = authenticated_client
        
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_logout_all_success(self, authenticated_client):
        """Test successful logout from all sessions."""
        client, user = authenticated_client
        
        response = client.post("/api/v1/auth/logout-all")
        
        assert response.status_code == 200
        assert "logged out from" in response.json()["message"]
    
    def test_logout_without_auth(self, client: TestClient):
        """Test logout without authentication fails."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 403  # No authorization header


class TestEmailVerification:
    """Test email verification endpoints."""
    
    def test_request_verification_success(self, client: TestClient, create_test_user, mock_email_service):
        """Test successful verification request."""
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user_data = UserFactory.build(email="verify@example.com")
            user = await create_test_user(user_data)
            return user
        
        user = asyncio.run(create_user())
        
        request_data = {
            "email": user.email
        }
        
        response = client.post("/api/v1/auth/verify-email-request", json=request_data)
        
        assert response.status_code == 200
        assert "verification link has been sent" in response.json()["message"]
    
    def test_request_verification_nonexistent_email(self, client: TestClient, mock_email_service):
        """Test verification request with non-existent email."""
        request_data = {
            "email": "nonexistent@example.com"
        }
        
        response = client.post("/api/v1/auth/verify-email-request", json=request_data)
        
        # Should return success to prevent email enumeration
        assert response.status_code == 200
        assert "verification link has been sent" in response.json()["message"]


class TestPasswordReset:
    """Test password reset endpoints."""
    
    def test_request_password_reset_success(self, client: TestClient, create_test_user, mock_email_service):
        """Test successful password reset request."""
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user()
        
        asyncio.run(create_user())
        
        request_data = {
            "email": user.email
        }
        
        response = client.post("/api/v1/auth/password-reset-request", json=request_data)
        
        assert response.status_code == 200
        assert "password reset link has been sent" in response.json()["message"]
    
    def test_request_password_reset_nonexistent_email(self, client: TestClient, mock_email_service):
        """Test password reset request with non-existent email."""
        request_data = {
            "email": "nonexistent@example.com"
        }
        
        response = client.post("/api/v1/auth/password-reset-request", json=request_data)
        
        # Should return success to prevent email enumeration
        assert response.status_code == 200
        assert "password reset link has been sent" in response.json()["message"]