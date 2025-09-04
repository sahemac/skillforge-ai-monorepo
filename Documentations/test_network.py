#!/usr/bin/env python3
"""
Test réseau et connectivité basique
"""

import socket
import subprocess
import sys
import time

def test_port_connectivity():
    """Test si le port 5432 répond"""
    print("1. Test connectivité port 5432...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 5432))
        sock.close()
        
        if result == 0:
            print("   SUCCESS: Port 5432 accessible")
            return True
        else:
            print(f"   ERROR: Port 5432 inaccessible (code: {result})")
            return False
    except Exception as e:
        print(f"   ERROR: Exception: {e}")
        return False

def test_raw_connection():
    """Test connexion socket brute"""
    print("\n2. Test connexion socket brute...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print("   Connexion à 127.0.0.1:5432...")
        sock.connect(('127.0.0.1', 5432))
        
        print("   Connexion établie!")
        
        # Envoyer un message PostgreSQL basique
        # Message de démarrage PostgreSQL
        startup_msg = b'\x00\x00\x00\x08\x04\xd2\x16\x2f'
        sock.send(startup_msg)
        
        # Essayer de recevoir une réponse
        try:
            response = sock.recv(1024)
            print(f"   Réponse reçue: {len(response)} bytes")
            if response:
                print("   SUCCESS: Le serveur répond (probablement PostgreSQL)")
                return True
        except socket.timeout:
            print("   TIMEOUT: Pas de réponse du serveur")
        
        sock.close()
        return False
        
    except socket.gaierror as e:
        print(f"   ERROR: Résolution DNS échouée: {e}")
        return False
    except socket.timeout:
        print("   ERROR: Timeout de connexion")
        return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_netstat():
    """Vérifier ce qui écoute sur le port 5432"""
    print("\n3. Test netstat pour voir qui écoute sur 5432...")
    
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["netstat", "-an"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            listening_5432 = [line for line in lines if ':5432' in line and 'LISTENING' in line]
            
            if listening_5432:
                print("   Processus écoutant sur port 5432:")
                for line in listening_5432:
                    print(f"   {line.strip()}")
                return True
            else:
                print("   ERROR: Aucun processus n'écoute sur le port 5432")
                return False
        
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_proxy_logs():
    """Instructions pour vérifier les logs du proxy"""
    print("\n4. Vérification logs cloud-sql-proxy...")
    print("   Dans le terminal du cloud-sql-proxy, vérifiez:")
    print("   - Y a-t-il des messages d'erreur?")
    print("   - Voyez-vous des tentatives de connexion?")
    print("   - Le proxy affiche-t-il des erreurs d'authentification?")
    print()

if __name__ == "__main__":
    print("TEST RÉSEAU ET CONNECTIVITÉ")
    print("=" * 40)
    
    results = []
    
    results.append(test_port_connectivity())
    results.append(test_raw_connection())  
    results.append(test_netstat())
    test_proxy_logs()
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nRÉSULTATS: {passed}/{total} tests réussis")
    
    if passed == total:
        print("SUCCESS: La connectivité réseau fonctionne")
        print("Le problème est probablement dans la configuration PostgreSQL")
    else:
        print("ERROR: Problème de connectivité réseau")
        print("cloud-sql-proxy ne fonctionne pas correctement")