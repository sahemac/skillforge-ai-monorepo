#!/usr/bin/env python3
"""
Debug du modèle User pour identifier le champ problématique
"""

import traceback
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON
from enum import Enum
import uuid

print("DEBUG MODÈLE USER")
print("=" * 50)

# Import des mixins
try:
    from app.models.base import UUIDMixin, TimestampMixin
    print("OK - Mixins importés")
except Exception as e:
    print(f"ERREUR Mixins: {e}")
    # Définir localement pour le test
    class TimestampMixin:
        created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
        updated_at: Optional[datetime] = Field(default=None, nullable=True)
    
    class UUIDMixin:
        id: uuid.UUID = Field(
            default_factory=uuid.uuid4,
            primary_key=True,
            index=True,
            nullable=False
        )
    print("OK - Mixins définis localement")

# Test des enums
print("\nTest des enums...")
try:
    class UserRole(str, Enum):
        ADMIN = "admin"
        USER = "user"
        MODERATOR = "moderator"
        EXPERT = "expert"
    print("OK - UserRole défini")
    
    class UserStatus(str, Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        SUSPENDED = "suspended"
        DELETED = "deleted"
    print("OK - UserStatus défini")
except Exception as e:
    print(f"ERREUR Enums: {e}")

# Test modèle progressif
print("\nTest modèle User progressif...")

try:
    class UserBase(SQLModel, UUIDMixin, TimestampMixin, table=True):
        __tablename__ = "users_test"
        
        # Champs de base seulement
        email: str = Field(unique=True, index=True, nullable=False)
        username: Optional[str] = Field(default=None, unique=True, index=True)
        first_name: Optional[str] = Field(default=None, max_length=100)
        last_name: Optional[str] = Field(default=None, max_length=100)
    
    print("OK - Modèle de base créé")
    
except Exception as e:
    print(f"ERREUR Modèle base: {e}")
    traceback.print_exc()

# Test avec enum
try:
    class UserWithEnum(SQLModel, UUIDMixin, TimestampMixin, table=True):
        __tablename__ = "users_enum_test"
        
        email: str = Field(unique=True, index=True, nullable=False) 
        role: UserRole = Field(default=UserRole.USER, nullable=False)
        status: UserStatus = Field(default=UserStatus.ACTIVE, nullable=False)
    
    print("OK - Modèle avec enum créé")
    
except Exception as e:
    print(f"ERREUR Modèle avec enum: {e}")
    traceback.print_exc()

# Test avec JSON simple
try:
    class UserWithJSON(SQLModel, UUIDMixin, TimestampMixin, table=True):
        __tablename__ = "users_json_test"
        
        email: str = Field(unique=True, index=True, nullable=False)
        preferences: str = Field(default="{}", sa_column=Column(JSON))
    
    print("OK - Modèle avec JSON créé")
    
except Exception as e:
    print(f"ERREUR Modèle avec JSON: {e}")
    traceback.print_exc()

print("\nDEBUG TERMINÉ")