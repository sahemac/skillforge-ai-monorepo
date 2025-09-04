"""
User endpoint tests for SkillForge AI User Service
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.conftest import UserFactory, assert_response_error, assert_user_response


class TestCurrentUser:
    """Test current user endpoints."""
    
    def test_get_current_user_success(self, authenticated_client):
        """Test getting current user profile."""
        client, user = authenticated_client
        
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 200
        response_data = response.json()
        assert_user_response(response_data, user.email)
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication fails."""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 403  # No auth header
    
    def test_update_current_user_success(self, authenticated_client):
        """Test updating current user profile."""
        client, user = authenticated_client
        
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio"
        }
        
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["first_name"] == "Updated"
        assert response_data["last_name"] == "Name"
        assert response_data["full_name"] == "Updated Name"
        assert response_data["bio"] == "Updated bio"
    
    def test_update_current_user_invalid_data(self, authenticated_client):
        """Test updating current user with invalid data fails."""
        client, user = authenticated_client
        
        update_data = {
            "bio": "x" * 1001  # Too long
        }
        
        response = client.put("/api/v1/users/me", json=update_data)
        
        assert response.status_code == 422


class TestPasswordChange:
    """Test password change endpoint."""
    
    def test_change_password_success(self, authenticated_client):
        """Test successful password change."""
        client, user = authenticated_client
        
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
    
    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password fails."""
        client, user = authenticated_client
        
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!"
        }
        
        response = client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert_response_error(response, 400, "Current password is incorrect")
    
    def test_change_password_mismatch(self, authenticated_client):
        """Test password change with mismatched new passwords fails."""
        client, user = authenticated_client
        
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "confirm_new_password": "DifferentPassword123!"
        }
        
        response = client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert response.status_code == 422
    
    def test_change_password_weak_new(self, authenticated_client):
        """Test password change with weak new password fails."""
        client, user = authenticated_client
        
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "weak",
            "confirm_new_password": "weak"
        }
        
        response = client.post("/api/v1/users/me/change-password", json=password_data)
        
        assert_response_error(response, 400, "Password validation failed")


class TestUserSettings:
    """Test user settings endpoints."""
    
    def test_get_user_settings_success(self, authenticated_client):
        """Test getting user settings."""
        client, user = authenticated_client
        
        response = client.get("/api/v1/users/me/settings")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Check for default settings
        assert response_data["theme"] == "light"
        assert response_data["language"] == "en"
        assert response_data["email_notifications"] is True
    
    def test_update_user_settings_success(self, authenticated_client):
        """Test updating user settings."""
        client, user = authenticated_client
        
        update_data = {
            "theme": "dark",
            "language": "es",
            "email_notifications": False,
            "profile_visibility": "private"
        }
        
        response = client.put("/api/v1/users/me/settings", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["theme"] == "dark"
        assert response_data["language"] == "es"
        assert response_data["email_notifications"] is False
        assert response_data["profile_visibility"] == "private"
    
    def test_update_user_settings_invalid_theme(self, authenticated_client):
        """Test updating user settings with invalid theme fails."""
        client, user = authenticated_client
        
        update_data = {
            "theme": "invalid_theme"
        }
        
        response = client.put("/api/v1/users/me/settings", json=update_data)
        
        assert response.status_code == 422


class TestAccountDeletion:
    """Test account deletion endpoint."""
    
    def test_delete_current_user_success(self, authenticated_client):
        """Test successful account deletion."""
        client, user = authenticated_client
        
        response = client.delete("/api/v1/users/me")
        
        assert response.status_code == 204
        
        # User should no longer be able to access their profile
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401  # Should be unauthorized


class TestPublicUserProfiles:
    """Test public user profile endpoints."""
    
    def test_get_public_user_profile_success(self, client: TestClient, create_test_user):
        """Test getting public user profile."""
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user()
        
        user = asyncio.run(create_user())
        
        response = client.get(f"/api/v1/users/{user.id}/public")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Should contain public fields only
        assert "email" not in response_data
        assert "username" in response_data
        assert "first_name" in response_data
        assert "bio" in response_data
        assert "skills" in response_data
    
    def test_get_public_user_profile_not_found(self, client: TestClient):
        """Test getting non-existent public user profile fails."""
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        
        response = client.get(f"/api/v1/users/{fake_uuid}/public")
        
        assert_response_error(response, 404, "User not found")
    
    def test_get_public_users_list(self, client: TestClient, create_test_user):
        """Test getting public users list."""
        # Create some test users
        import asyncio
        
        async def create_users():
            await create_test_user(UserFactory.build(email="user1@example.com", username="user1"))
            await create_test_user(UserFactory.build(email="user2@example.com", username="user2"))
        
        asyncio.run(create_users())
        
        response = client.get("/api/v1/users/public")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "users" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "size" in response_data
        assert len(response_data["users"]) >= 2
    
    def test_get_public_users_search(self, client: TestClient, create_test_user):
        """Test searching public users."""
        import asyncio
        
        async def create_users():
            await create_test_user(UserFactory.build(
                email="john@example.com", 
                username="john", 
                first_name="John",
                last_name="Doe"
            ))
        
        asyncio.run(create_users())
        
        response = client.get("/api/v1/users/public?q=John")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert len(response_data["users"]) >= 1
        assert any("john" in user["username"].lower() or 
                 "john" in (user["first_name"] or "").lower() 
                 for user in response_data["users"])


class TestAdminUserEndpoints:
    """Test admin user management endpoints."""
    
    def test_get_users_list_admin(self, authenticated_admin_client):
        """Test getting users list as admin."""
        client, admin_user = authenticated_admin_client
        
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "users" in response_data
        assert "total" in response_data
        assert len(response_data["users"]) >= 1  # At least the admin user
    
    def test_get_users_list_non_admin(self, authenticated_client):
        """Test getting users list as non-admin fails."""
        client, user = authenticated_client
        
        response = client.get("/api/v1/users/")
        
        assert_response_error(response, 403, "Not enough permissions")
    
    def test_get_user_by_id_admin(self, authenticated_admin_client, create_test_user):
        """Test getting user by ID as admin."""
        client, admin_user = authenticated_admin_client
        
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user(UserFactory.build(email="target@example.com"))
        
        user = asyncio.run(create_user())
        
        response = client.get(f"/api/v1/users/{user.id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Admin should see additional fields
        assert "failed_login_attempts" in response_data
        assert "metadata" in response_data
        assert response_data["email"] == user.email
    
    def test_update_user_role_admin(self, authenticated_admin_client, create_test_user):
        """Test updating user role as admin."""
        client, admin_user = authenticated_admin_client
        
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user(UserFactory.build(email="target@example.com"))
        
        user = asyncio.run(create_user())
        
        role_update = {
            "role": "moderator"
        }
        
        response = client.put(f"/api/v1/users/{user.id}/role", json=role_update)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["role"] == "moderator"
    
    def test_update_user_status_admin(self, authenticated_admin_client, create_test_user):
        """Test updating user status as admin."""
        client, admin_user = authenticated_admin_client
        
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user(UserFactory.build(email="target@example.com"))
        
        user = asyncio.run(create_user())
        
        status_update = {
            "status": "suspended",
            "is_active": False
        }
        
        response = client.put(f"/api/v1/users/{user.id}/status", json=status_update)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["status"] == "suspended"
        assert response_data["is_active"] is False
    
    def test_delete_user_admin(self, authenticated_admin_client, create_test_user):
        """Test deleting user as admin."""
        client, admin_user = authenticated_admin_client
        
        user = None
        import asyncio
        
        async def create_user():
            nonlocal user
            user = await create_test_user(UserFactory.build(email="target@example.com"))
        
        user = asyncio.run(create_user())
        
        response = client.delete(f"/api/v1/users/{user.id}")
        
        assert response.status_code == 204
    
    def test_admin_cannot_change_own_role(self, authenticated_admin_client):
        """Test admin cannot change their own role."""
        client, admin_user = authenticated_admin_client
        
        role_update = {
            "role": "user"
        }
        
        response = client.put(f"/api/v1/users/{admin_user.id}/role", json=role_update)
        
        assert_response_error(response, 400, "Cannot change your own role")