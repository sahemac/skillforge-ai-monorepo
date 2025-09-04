"""
Company endpoint tests for SkillForge AI User Service
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.conftest import CompanyFactory, UserFactory, assert_response_error, assert_company_response


class TestCompanyCreation:
    """Test company creation endpoint."""
    
    def test_create_company_success(self, authenticated_client):
        """Test successful company creation."""
        client, user = authenticated_client
        
        company_data = CompanyFactory.build()
        
        response = client.post("/api/v1/companies/", json=company_data)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert_company_response(response_data, company_data["name"])
        assert response_data["owner_id"] == str(user.id)
        assert response_data["slug"] is not None
        assert response_data["is_active"] is True
    
    def test_create_company_unauthorized(self, client: TestClient):
        """Test company creation without authentication fails."""
        company_data = CompanyFactory.build()
        
        response = client.post("/api/v1/companies/", json=company_data)
        
        assert response.status_code == 403  # No auth header
    
    def test_create_company_custom_slug(self, authenticated_client):
        """Test company creation with custom slug."""
        client, user = authenticated_client
        
        company_data = CompanyFactory.build(
            name="Test Company",
            slug="custom-slug"
        )
        
        response = client.post("/api/v1/companies/", json=company_data)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["slug"] == "custom-slug"
    
    def test_create_company_duplicate_slug(self, authenticated_client):
        """Test company creation with duplicate slug fails."""
        client, user = authenticated_client
        
        # Create first company
        company_data1 = CompanyFactory.build(
            name="Company One",
            slug="test-slug"
        )
        client.post("/api/v1/companies/", json=company_data1)
        
        # Try to create second company with same slug
        company_data2 = CompanyFactory.build(
            name="Company Two",
            slug="test-slug"
        )
        
        response = client.post("/api/v1/companies/", json=company_data2)
        
        assert_response_error(response, 400, "slug already exists")
    
    def test_create_company_invalid_data(self, authenticated_client):
        """Test company creation with invalid data fails."""
        client, user = authenticated_client
        
        company_data = CompanyFactory.build(
            name="",  # Empty name
            website="invalid-url"  # Invalid URL
        )
        
        response = client.post("/api/v1/companies/", json=company_data)
        
        assert response.status_code == 422


class TestMyCompanies:
    """Test user's companies endpoint."""
    
    def test_get_my_companies_success(self, authenticated_client, create_test_company):
        """Test getting user's companies."""
        client, user = authenticated_client
        
        # Create a company for the user
        import asyncio
        
        async def create_company():
            await create_test_company(user)
        
        asyncio.run(create_company())
        
        response = client.get("/api/v1/companies/my-companies")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "companies" in response_data
        assert "total" in response_data
        assert len(response_data["companies"]) >= 1
        assert response_data["companies"][0]["owner_id"] == str(user.id)
    
    def test_get_my_companies_empty(self, authenticated_client):
        """Test getting user's companies when none exist."""
        client, user = authenticated_client
        
        response = client.get("/api/v1/companies/my-companies")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["total"] == 0
        assert len(response_data["companies"]) == 0


class TestCompanyRetrieval:
    """Test company retrieval endpoints."""
    
    def test_get_company_by_id_owner(self, authenticated_client, create_test_company):
        """Test getting company by ID as owner."""
        client, user = authenticated_client
        
        company = None
        import asyncio
        
        async def create_company():
            nonlocal company
            company = await create_test_company(user)
        
        company = asyncio.run(create_company())
        
        response = client.get(f"/api/v1/companies/{company.id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert_company_response(response_data, company.name)
        assert response_data["id"] == str(company.id)
    
    def test_get_company_by_id_not_found(self, authenticated_client):
        """Test getting non-existent company fails."""
        client, user = authenticated_client
        
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        
        response = client.get(f"/api/v1/companies/{fake_uuid}")
        
        assert_response_error(response, 404, "Company not found")
    
    def test_get_company_by_id_no_access(self, authenticated_client, create_test_user, create_test_company):
        """Test getting company without access fails."""
        client, user = authenticated_client
        
        # Create another user and their company
        other_user = None
        other_company = None
        import asyncio
        
        async def create_other_user_company():
            nonlocal other_user, other_company
            other_user = await create_test_user(UserFactory.build(email="other@example.com", username="other"))
            other_company = await create_test_company(other_user)
        
        asyncio.run(create_other_user_company())
        
        response = client.get(f"/api/v1/companies/{other_company.id}")
        
        assert_response_error(response, 403, "Access to company denied")


class TestCompanyUpdates:
    """Test company update endpoints."""
    
    def test_update_company_success(self, authenticated_client, create_test_company):
        """Test successful company update."""
        client, user = authenticated_client
        
        company = None
        import asyncio
        
        async def create_company():
            nonlocal company
            company = await create_test_company(user)
        
        company = asyncio.run(create_company())
        
        update_data = {
            "name": "Updated Company Name",
            "description": "Updated description",
            "website": "https://updated-website.com"
        }
        
        response = client.put(f"/api/v1/companies/{company.id}", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["name"] == "Updated Company Name"
        assert response_data["description"] == "Updated description"
        assert response_data["website"] == "https://updated-website.com"
    
    def test_update_company_not_owner(self, authenticated_client, create_test_user, create_test_company):
        """Test updating company as non-owner fails."""
        client, user = authenticated_client
        
        # Create another user and their company
        other_user = None
        other_company = None
        import asyncio
        
        async def create_other_user_company():
            nonlocal other_user, other_company
            other_user = await create_test_user(UserFactory.build(email="other@example.com", username="other"))
            other_company = await create_test_company(other_user)
        
        asyncio.run(create_other_user_company())
        
        update_data = {
            "name": "Hacked Name"
        }
        
        response = client.put(f"/api/v1/companies/{other_company.id}", json=update_data)
        
        assert_response_error(response, 403, "Only company owner can update profile")


class TestCompanyDeletion:
    """Test company deletion endpoint."""
    
    def test_delete_company_success(self, authenticated_client, create_test_company):
        """Test successful company deletion."""
        client, user = authenticated_client
        
        company = None
        import asyncio
        
        async def create_company():
            nonlocal company
            company = await create_test_company(user)
        
        company = asyncio.run(create_company())
        
        response = client.delete(f"/api/v1/companies/{company.id}")
        
        assert response.status_code == 204
        
        # Company should no longer be accessible
        response = client.get(f"/api/v1/companies/{company.id}")
        assert_response_error(response, 403, "Access to company denied")
    
    def test_delete_company_not_owner(self, authenticated_client, create_test_user, create_test_company):
        """Test deleting company as non-owner fails."""
        client, user = authenticated_client
        
        # Create another user and their company
        other_user = None
        other_company = None
        import asyncio
        
        async def create_other_user_company():
            nonlocal other_user, other_company
            other_user = await create_test_user(UserFactory.build(email="other@example.com", username="other"))
            other_company = await create_test_company(other_user)
        
        asyncio.run(create_other_user_company())
        
        response = client.delete(f"/api/v1/companies/{other_company.id}")
        
        assert_response_error(response, 403, "Only company owner can delete company")


class TestPublicCompanyProfiles:
    """Test public company profile endpoints."""
    
    def test_get_public_company_profile_success(self, client: TestClient, create_test_user, create_test_company):
        """Test getting public company profile."""
        user = None
        company = None
        import asyncio
        
        async def create_user_company():
            nonlocal user, company
            user = await create_test_user()
            company = await create_test_company(user)
        
        asyncio.run(create_user_company())
        
        response = client.get(f"/api/v1/companies/public/{company.id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Should contain public fields only
        assert "billing_email" not in response_data
        assert "settings" not in response_data
        assert "name" in response_data
        assert "description" in response_data
        assert "industry" in response_data
    
    def test_get_company_by_slug_success(self, client: TestClient, create_test_user, create_test_company):
        """Test getting company by slug."""
        user = None
        company = None
        import asyncio
        
        async def create_user_company():
            nonlocal user, company
            user = await create_test_user()
            company = await create_test_company(user, CompanyFactory.build(slug="test-company"))
        
        asyncio.run(create_user_company())
        
        response = client.get(f"/api/v1/companies/slug/{company.slug}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["slug"] == company.slug
        assert response_data["name"] == company.name
    
    def test_search_public_companies(self, client: TestClient, create_test_user, create_test_company):
        """Test searching public companies."""
        # Create some test companies
        import asyncio
        
        async def create_companies():
            user1 = await create_test_user(UserFactory.build(email="user1@example.com", username="user1"))
            user2 = await create_test_user(UserFactory.build(email="user2@example.com", username="user2"))
            
            await create_test_company(user1, CompanyFactory.build(name="Tech Company", industry="technology"))
            await create_test_company(user2, CompanyFactory.build(name="Health Corp", industry="healthcare"))
        
        asyncio.run(create_companies())
        
        response = client.get("/api/v1/companies/public/search")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "companies" in response_data
        assert "total" in response_data
        assert len(response_data["companies"]) >= 2
    
    def test_search_public_companies_with_filters(self, client: TestClient, create_test_user, create_test_company):
        """Test searching public companies with filters."""
        import asyncio
        
        async def create_companies():
            user1 = await create_test_user(UserFactory.build(email="user1@example.com", username="user1"))
            await create_test_company(user1, CompanyFactory.build(name="Tech Startup", industry="technology", company_size="startup"))
        
        asyncio.run(create_companies())
        
        response = client.get("/api/v1/companies/public/search?industry=technology&company_size=startup")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert len(response_data["companies"]) >= 1
        for company in response_data["companies"]:
            assert company["industry"] == "technology"
            assert company["company_size"] == "startup"


class TestTeamManagement:
    """Test team management endpoints."""
    
    def test_get_team_members_success(self, authenticated_client, create_test_company):
        """Test getting team members."""
        client, user = authenticated_client
        
        company = None
        import asyncio
        
        async def create_company():
            nonlocal company
            company = await create_test_company(user)
        
        company = asyncio.run(create_company())
        
        response = client.get(f"/api/v1/companies/{company.id}/members")
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert "members" in response_data
        assert "total" in response_data
    
    def test_invite_team_member_success(self, authenticated_client, create_test_user, create_test_company):
        """Test inviting team member."""
        client, user = authenticated_client
        
        # Create company and another user to invite
        company = None
        invite_user = None
        import asyncio
        
        async def setup():
            nonlocal company, invite_user
            company = await create_test_company(user)
            invite_user = await create_test_user(UserFactory.build(email="invite@example.com", username="invitee"))
        
        asyncio.run(setup())
        
        invite_data = {
            "email": invite_user.email,
            "role": "member",
            "title": "Developer",
            "message": "Welcome to the team!"
        }
        
        response = client.post(f"/api/v1/companies/{company.id}/members", json=invite_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["role"] == "member"
        assert response_data["title"] == "Developer"
        assert response_data["user_id"] == str(invite_user.id)
    
    def test_invite_nonexistent_user(self, authenticated_client, create_test_company):
        """Test inviting non-existent user fails."""
        client, user = authenticated_client
        
        company = None
        import asyncio
        
        async def create_company():
            nonlocal company
            company = await create_test_company(user)
        
        company = asyncio.run(create_company())
        
        invite_data = {
            "email": "nonexistent@example.com",
            "role": "member"
        }
        
        response = client.post(f"/api/v1/companies/{company.id}/members", json=invite_data)
        
        assert_response_error(response, 404, "User not found")
    
    def test_invite_existing_member(self, authenticated_client, create_test_user, create_test_company):
        """Test inviting existing member fails."""
        client, user = authenticated_client
        
        company = None
        invite_user = None
        import asyncio
        
        async def setup():
            nonlocal company, invite_user
            company = await create_test_company(user)
            invite_user = await create_test_user(UserFactory.build(email="invite@example.com", username="invitee"))
            
            # First invitation
            from app.crud import team_member
            from app.api.dependencies import get_db
            async with get_db() as db:
                await team_member.add_member(
                    db,
                    company_id=company.id,
                    user_id=invite_user.id,
                    role="member"
                )
        
        asyncio.run(setup())
        
        invite_data = {
            "email": invite_user.email,
            "role": "admin"
        }
        
        response = client.post(f"/api/v1/companies/{company.id}/members", json=invite_data)
        
        assert_response_error(response, 400, "already a team member")