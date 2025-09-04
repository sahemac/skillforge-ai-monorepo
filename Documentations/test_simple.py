#!/usr/bin/env python3
"""
Test simple pour vérifier la configuration de base
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

def test_simple():
    """Test très simple sans dependencies"""
    app = FastAPI()
    
    @app.get("/test")
    def read_test():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 200
    assert response.json() == {"message": "test"}

def test_import_models():
    """Test import des modèles"""
    from app.models.user_simple import User, UserRole, UserStatus, UserSkillLevel
    from app.models.company_simple import CompanyProfile, CompanySize, IndustryType
    
    assert User is not None
    assert UserRole.USER == "user"
    assert UserStatus.ACTIVE == "active"
    assert UserSkillLevel.BEGINNER == "beginner"

if __name__ == "__main__":
    test_simple()
    test_import_models()
    print("Tests simples OK!")