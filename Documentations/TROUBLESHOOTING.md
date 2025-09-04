# 🔧 Guide de Dépannage - Validation User-Service

## ✅ Script PowerShell Corrigé

Le script `run_validation.ps1` a été corrigé et fonctionne maintenant correctement.

### 🚀 Utilisation

```powershell
# Méthode recommandée
.\run_validation.ps1

# Ou directement
python validate_service.py

# Test rapide
python quick_test.py
```

## 🔍 Diagnostic des Problèmes

### 1. Python non trouvé

**Erreur** :
```
ERREUR Python non trouve
```

**Solutions** :
```powershell
# Vérifier Python installé
python --version
python3 --version
py --version

# Si non installé, télécharger depuis python.org
# Puis ajouter au PATH système
```

### 2. cloud-sql-proxy non détecté

**Avertissement** :
```
WARN cloud-sql-proxy non detecte
WARN Port 5432 non accessible
```

**Solutions** :
```bash
# Démarrer cloud-sql-proxy
cloud_sql_proxy -instances=skillforge-ai-mvp-25:europe-west1:skillforge-db=tcp:5432

# Vérifier que le proxy fonctionne
netstat -an | findstr :5432
# Ou sur Linux/Mac
netstat -an | grep :5432

# Tester la connexion
telnet 127.0.0.1 5432
```

### 3. Modules Python manquants

**Erreur** :
```
Installation asyncpg...
Installation httpx...
```

**Solutions** :
```bash
# Installation manuelle si échec
pip install asyncpg httpx psutil sqlmodel

# Ou avec requirements.txt
pip install -r requirements.txt

# Vérifier l'installation
python -c "import asyncpg, httpx, psutil"
```

### 4. Tests de validation échouent

**Erreur dans validate_service.py** :

**Solutions par type d'erreur** :

#### A. Connexion PostgreSQL
```bash
# Test manuel de connexion
python -c "
import asyncio
import asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db')
    print('Connexion OK')
    await conn.close()
asyncio.run(test())
"
```

#### B. Migrations Alembic
```bash
# Test migrations manuel
cd apps/backend/user-service
export DATABASE_URL="postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
alembic upgrade head
```

#### C. Tests unitaires
```bash
# Lancer tests manuellement
python -m pytest app/tests/ -v --tb=short
```

#### D. Serveur uvicorn
```bash
# Test serveur manuel
export DATABASE_URL="postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
python -m uvicorn main:app --reload --port 8000
# Puis dans un autre terminal
curl http://127.0.0.1:8000/health
```

## 🛠️ Configuration cloud-sql-proxy

### Étapes de configuration

1. **Installer cloud-sql-proxy** :
```bash
# Windows (avec gcloud SDK)
gcloud components install cloud_sql_proxy

# Linux/Mac
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy
```

2. **Authentification GCP** :
```bash
# Authentification utilisateur
gcloud auth login
gcloud auth application-default login

# Ou avec service account key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

3. **Lancer le proxy** :
```bash
# Format général
cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432

# Exemple pour SkillForge AI
cloud_sql_proxy -instances=skillforge-ai-mvp-25:europe-west1:skillforge-db=tcp:5432

# Avec options avancées
cloud_sql_proxy \
  -instances=skillforge-ai-mvp-25:europe-west1:skillforge-db=tcp:5432 \
  -credential_file=/path/to/service-account.json \
  -log_debug_stdout
```

4. **Vérifier la connexion** :
```bash
# Test connexion directe
psql -h 127.0.0.1 -p 5432 -U skillforge_user -d skillforge_db

# Test avec mot de passe
# Password: Psaumes@27
```

## 📋 Checklist de Validation

Avant de lancer `.\run_validation.ps1`, vérifiez :

- [ ] **Python 3.8+** installé et dans le PATH
- [ ] **cloud-sql-proxy** en cours d'exécution sur port 5432  
- [ ] **Connexion internet** pour télécharger les dépendances
- [ ] **Permissions PowerShell** pour exécuter des scripts
- [ ] **Répertoire correct** : `apps/backend/user-service/`
- [ ] **Fichiers présents** : `main.py`, `validate_service.py`

### Commandes de vérification rapide :

```powershell
# Dans PowerShell
python --version                    # Doit afficher Python 3.8+
netstat -an | findstr :5432        # Doit montrer LISTENING
Test-Path ".\main.py"               # Doit retourner True
Test-Path ".\validate_service.py"   # Doit retourner True
```

## 🚀 Séquence de Démarrage Recommandée

### 1. Terminal 1 - Démarrer cloud-sql-proxy :
```bash
cloud_sql_proxy -instances=skillforge-ai-mvp-25:europe-west1:skillforge-db=tcp:5432
```

### 2. Terminal 2 - Lancer la validation :
```powershell
cd apps/backend/user-service
.\run_validation.ps1
```

### 3. Suivre les résultats :
- ✅ **SUCCÈS** → Commit autorisé
- ❌ **ÉCHEC** → Consulter `test-validation-report.md`

## 🔄 Flux de Debug

Si la validation échoue :

1. **Lire le rapport** : `test-validation-report.md`
2. **Identifier l'erreur** : PostgreSQL, Alembic, Tests, API, etc.
3. **Test manuel** de la partie qui échoue
4. **Corriger** le problème identifié  
5. **Relancer** la validation
6. **Répéter** jusqu'au succès

## 📞 Support d'Urgence

Si rien ne fonctionne :

### Test minimal de connectivité :
```python
# test_minimal.py
import asyncio
import asyncpg

async def test_basic():
    try:
        print("Test connexion...")
        conn = await asyncpg.connect(
            "postgresql://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
        )
        print("✅ Connexion réussie")
        
        result = await conn.fetchval("SELECT 'Hello from SkillForge DB'")
        print(f"✅ Requête réussie: {result}")
        
        await conn.close()
        print("✅ Connexion fermée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic())
```

```bash
python test_minimal.py
```

Si ce test passe, le problème est dans le script de validation. Si il échoue, le problème est dans la configuration cloud-sql-proxy ou la base de données.

---

**🎯 Objectif** : Avoir une validation qui passe à 100% avant commit GitHub