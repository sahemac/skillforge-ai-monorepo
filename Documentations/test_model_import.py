#!/usr/bin/env python3
"""
Test simple d'import du modèle User pour diagnostiquer l'erreur
"""

import sys
import traceback

print("Test import du modèle User")
print("=" * 50)

try:
    print("1. Import SQLModel...")
    from sqlmodel import SQLModel, Field, Column
    print("   OK")
    
    print("2. Import SQLAlchemy JSON...")
    from sqlalchemy import JSON
    print("   OK")
    
    print("3. Import base models...")
    from app.models.base import UUIDMixin, TimestampMixin
    print("   OK")
    
    print("4. Test création d'un modèle simple avec JSON...")
    class TestModel(SQLModel, table=True):
        __tablename__ = "test"
        id: int = Field(primary_key=True)
        data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    print("   OK - Modèle simple avec JSON fonctionne")
    
    print("5. Import du modèle User simplifié...")
    from app.models.user_simple import User
    print("   OK - User simplifié importé avec succès!")
    
    print("6. Test import via __init__.py...")
    from app.models import User as UserViaInit
    print("   OK - User via __init__ importé avec succès!")
    
except Exception as e:
    print(f"\n   ERREUR: {e}")
    print("\nTraceback complet:")
    traceback.print_exc()
    
    # Analyser l'erreur
    if "issubclass() arg 1 must be a class" in str(e):
        print("\nPROBLÈME IDENTIFIÉ:")
        print("SQLModel essaie de traiter un type qui n'est pas une classe.")
        print("Cela arrive souvent avec les types Optional[dict] ou List.")
        print("\nSOLUTIONS POSSIBLES:")
        print("1. Utiliser sa_column=Column(JSON) sans le type dict")
        print("2. Utiliser sa_column_kwargs={'type': JSON}")
        print("3. Créer un type Pydantic personnalisé pour les champs JSON")