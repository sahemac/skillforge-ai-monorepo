#!/usr/bin/env python3
"""
Test de connexion PostgreSQL direct pour diagnostic
"""

import asyncio
import sys

async def test_connection():
    try:
        import asyncpg
        print("Module asyncpg disponible")
        
        # Test de connexion
        print("Tentative de connexion...")
        conn = await asyncio.wait_for(
            asyncpg.connect("postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"),
            timeout=10.0
        )
        
        print("Connexion reussie!")
        
        # Test requête
        result = await conn.fetchval("SELECT 'Connection test successful' as message")
        print(f"Requête test: {result}")
        
        # Info serveur
        version = await conn.fetchval("SELECT version()")
        print(f"Version PostgreSQL: {version}")
        
        await conn.close()
        print("Connexion fermee proprement")
        
        return True
        
    except asyncio.TimeoutError:
        print("ERREUR: Timeout de connexion (>10s)")
        print("Cause probable: cloud-sql-proxy ne fonctionne pas ou instance inaccessible")
        return False
    except ImportError:
        print("ERREUR: Module asyncpg non installe")
        print("Solution: pip install asyncpg")
        return False
    except Exception as e:
        print(f"ERREUR: {type(e).__name__}: {e}")
        
        # Diagnostics spécifiques
        error_str = str(e).lower()
        if "getaddrinfo failed" in error_str:
            print("DIAGNOSTIC: Problème de résolution DNS/réseau")
            print("- Vérifiez que cloud-sql-proxy fonctionne")
            print("- Vérifiez que l'instance Cloud SQL a une IP publique")
        elif "connection refused" in error_str:
            print("DIAGNOSTIC: Connexion refusée")
            print("- Le port 5432 n'est pas accessible")
            print("- cloud-sql-proxy n'écoute pas sur ce port")
        elif "authentication failed" in error_str:
            print("DIAGNOSTIC: Échec d'authentification")
            print("- Vérifiez le nom d'utilisateur et mot de passe")
        elif "database" in error_str and "not exist" in error_str:
            print("DIAGNOSTIC: Base de données inexistante")
            print("- Vérifiez le nom de la base de données")
        
        return False

if __name__ == "__main__":
    print("TEST DE CONNEXION POSTGRESQL DIRECT")
    print("=" * 50)
    
    success = asyncio.run(test_connection())
    
    if success:
        print("\nSUCCESS: La connexion PostgreSQL fonctionne!")
        sys.exit(0)
    else:
        print("\nERREUR: La connexion PostgreSQL a échoué")
        sys.exit(1)