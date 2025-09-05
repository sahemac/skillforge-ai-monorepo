#!/usr/bin/env python3
"""
Simple test to verify all dependencies are properly installed
"""
import sys

def test_core_imports():
    """Test that core dependencies can be imported."""
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import sqlmodel
        print("✅ SQLModel imported successfully")
    except ImportError as e:
        print(f"❌ SQLModel import failed: {e}")
        return False

    try:
        import asyncpg
        print("✅ AsyncPG imported successfully")
    except ImportError as e:
        print(f"❌ AsyncPG import failed: {e}")
        return False

    try:
        import pytest
        print("✅ Pytest imported successfully")
    except ImportError as e:
        print(f"❌ Pytest import failed: {e}")
        return False

    try:
        import jwt
        print("✅ PyJWT imported successfully")
    except ImportError as e:
        print(f"❌ PyJWT import failed: {e}")
        return False

    try:
        from jose import jwt as jose_jwt
        print("✅ Python-jose JWT imported successfully")
    except ImportError as e:
        print(f"❌ Python-jose import failed: {e}")
        return False

    try:
        import httpx
        print("✅ HTTPX imported successfully")
    except ImportError as e:
        print(f"❌ HTTPX import failed: {e}")
        return False

    try:
        import pydantic
        print("✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False

    try:
        from pydantic_settings import BaseSettings
        print("✅ Pydantic Settings imported successfully")
    except ImportError as e:
        print(f"❌ Pydantic Settings import failed: {e}")
        return False

    try:
        import email_validator
        print("✅ Email Validator imported successfully")
    except ImportError as e:
        print(f"❌ Email Validator import failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🔍 Testing dependency imports...")
    if test_core_imports():
        print("\n✅ All core dependencies imported successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some dependencies failed to import")
        sys.exit(1)