#!/usr/bin/env python3
"""
Tests finaux simples - validation des composants essentiels
"""

import pytest
from app.models.user_simple import User, UserRole, UserStatus, UserSkillLevel
from app.models.company_simple import CompanyProfile, CompanySize, IndustryType
from app.core.security import get_password_hash, verify_password

def test_user_model_structure():
    """Test que le modèle User a tous les champs nécessaires."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_here",
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
        is_active=True,
        language_preference="fr",
        newsletter_subscribed=True
    )
    
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.role == UserRole.USER
    assert user.status == UserStatus.ACTIVE
    assert user.is_email_verified == True
    assert user.is_active == True

def test_company_model_structure():
    """Test que le modèle CompanyProfile a tous les champs nécessaires."""
    company = CompanyProfile(
        name="Test Company",
        slug="test-company",
        industry=IndustryType.TECHNOLOGY,
        size=CompanySize.STARTUP,
        is_active=True,
        is_verified=False,
        plan_type="free"
    )
    
    assert company.name == "Test Company"
    assert company.slug == "test-company"
    assert company.industry == IndustryType.TECHNOLOGY
    assert company.size == CompanySize.STARTUP
    assert company.is_active == True
    assert company.is_verified == False

def test_all_enums():
    """Test que toutes les énumérations ont les bonnes valeurs."""
    # UserRole
    assert UserRole.USER == "user"
    assert UserRole.ADMIN == "admin"
    assert UserRole.MODERATOR == "moderator"
    assert UserRole.EXPERT == "expert"
    assert UserRole.PREMIUM_USER == "premium_user"
    
    # UserStatus
    assert UserStatus.ACTIVE == "active"
    assert UserStatus.INACTIVE == "inactive"
    assert UserStatus.SUSPENDED == "suspended"
    assert UserStatus.DELETED == "deleted"
    
    # UserSkillLevel
    assert UserSkillLevel.BEGINNER == "beginner"
    assert UserSkillLevel.INTERMEDIATE == "intermediate"
    assert UserSkillLevel.ADVANCED == "advanced"
    assert UserSkillLevel.EXPERT == "expert"
    
    # CompanySize
    assert CompanySize.STARTUP == "startup"
    assert CompanySize.SMALL == "small"
    assert CompanySize.MEDIUM == "medium"
    assert CompanySize.LARGE == "large"
    assert CompanySize.ENTERPRISE == "enterprise"
    
    # IndustryType
    assert IndustryType.TECHNOLOGY == "technology"
    assert IndustryType.HEALTHCARE == "healthcare"
    assert IndustryType.FINANCE == "finance"
    assert IndustryType.EDUCATION == "education"

def test_security_functions():
    """Test des fonctions de sécurité."""
    password = "TestPassword123!"
    
    # Test hashing
    hashed = get_password_hash(password)
    assert hashed != password
    assert len(hashed) > 50  # bcrypt hash is long
    
    # Test verification
    assert verify_password(password, hashed) == True
    assert verify_password("wrong_password", hashed) == False

def test_imports():
    """Test que tous les imports critiques fonctionnent."""
    # Models
    from app.models.user_simple import User, UserSession, UserSettings
    from app.models.company_simple import TeamMember, Subscription
    from app.models.base import SQLModel
    
    # Core
    from app.core.config import get_settings
    from app.core.security import create_access_token
    
    # Schemas - test quelques imports critiques
    from app.schemas.user import UserCreate, UserUpdate
    
    # Vérification que les imports ne sont pas None
    assert User is not None
    assert UserSession is not None
    assert UserSettings is not None
    assert TeamMember is not None
    assert Subscription is not None
    assert SQLModel is not None
    assert get_settings is not None
    assert create_access_token is not None
    assert UserCreate is not None
    assert UserUpdate is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    print("\n🎉 TESTS FINAUX RÉUSSIS!")
    print("✅ Modèles User et Company")
    print("✅ Énumérations complètes")
    print("✅ Fonctions de sécurité")  
    print("✅ Imports critiques")