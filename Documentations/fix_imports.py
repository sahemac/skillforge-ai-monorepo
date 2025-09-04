#!/usr/bin/env python3
"""
Script pour corriger tous les imports de l'ancien user.py vers user_simple.py
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Corrige les imports dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les imports
        original_content = content
        
        # from app.models.user import XXX -> from app.models.user_simple import XXX
        content = re.sub(
            r'from app\.models\.user import',
            'from app.models.user_simple import',
            content
        )
        
        # from .user import XXX -> from .user_simple import XXX
        content = re.sub(
            r'from \.user import',
            'from .user_simple import',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"CORRIGÉ: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"ERREUR dans {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    base_path = Path(__file__).parent
    files_to_fix = [
        "app/api/dependencies.py",
        "app/tests/conftest.py", 
        "app/api/v1/endpoints/auth.py",
        "app/schemas/user.py",
        "app/api/v1/endpoints/companies.py",
        "app/crud/user.py",
        "app/api/v1/endpoints/users.py"
    ]
    
    print("CORRECTION DES IMPORTS USER -> USER_SIMPLE")
    print("=" * 50)
    
    corrected = 0
    
    for file_path in files_to_fix:
        full_path = base_path / file_path
        if full_path.exists():
            if fix_imports_in_file(full_path):
                corrected += 1
        else:
            print(f"IGNORÉ (inexistant): {file_path}")
    
    print(f"\n{corrected} fichiers corrigés")
    print("Vous pouvez maintenant relancer: python validate_service.py")

if __name__ == "__main__":
    main()