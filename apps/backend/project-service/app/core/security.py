"""
Security utilities for SkillForge AI Project Service
Mock implementation - à adapter selon votre système d'authentification
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# Mock security - À remplacer par votre système d'authentification réel
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Mock fonction pour récupérer l'utilisateur actuel.
    À remplacer par votre logique d'authentification réelle.
    """
    
    # Mock validation du token
    token = credentials.credentials
    
    # En production, vous devriez :
    # 1. Valider le JWT token
    # 2. Vérifier l'expiration
    # 3. Récupérer les infos utilisateur depuis la base ou le service user
    
    if not token or token == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user data - à remplacer par vos données réelles
    mock_user = {
        "id": "550e8400-e29b-41d4-a716-446655440000",  # UUID mock
        "email": "user@example.com",
        "username": "testuser",
        "is_active": True,
        "roles": ["user"],
        "company_id": "660e8400-e29b-41d4-a716-446655440000"
    }
    
    return mock_user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Récupère l'utilisateur actuel s'il est actif."""
    
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Récupère l'utilisateur actuel s'il est admin."""
    
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Vérifie un token JWT et retourne les données utilisateur.
    Mock implementation - à remplacer par votre logique réelle.
    """
    
    if not token or token == "invalid":
        return None
    
    # En production :
    # 1. Décoder le JWT
    # 2. Vérifier la signature
    # 3. Vérifier l'expiration
    # 4. Retourner les claims
    
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "roles": ["user"]
    }