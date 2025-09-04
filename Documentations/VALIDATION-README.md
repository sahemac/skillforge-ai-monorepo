# 🔍 Guide de Validation - User-Service SkillForge AI

Ce guide explique comment valider complètement le User-Service avant commit GitHub.

## 📋 Prérequis

### 1. Cloud SQL Proxy
Assurez-vous que `cloud-sql-proxy` est en cours d'exécution :

```bash
# Lancer cloud-sql-proxy (remplacez PROJECT, REGION, INSTANCE)
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# Ou avec authentication
cloud_sql_proxy -instances=skillforge-ai-mvp-25:europe-west1:skillforge-db=tcp:5432
```

### 2. Variables d'Environnement
La configuration de test utilise :
- **Database URL** : `postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db`
- **API URL** : `http://127.0.0.1:8000`

### 3. Python & Dépendances
- Python 3.8+
- pip installé
- Dépendances dans `requirements.txt`

## 🚀 Méthodes de Validation

### Méthode 1 : Script PowerShell (Recommandé)

```powershell
# Lancer la validation complète avec installation automatique
.\run_validation.ps1
```

**Avantages** :
- ✅ Installation automatique des dépendances
- ✅ Vérifications préalables
- ✅ Interface utilisateur claire
- ✅ Gestion des erreurs

### Méthode 2 : Script Python Direct

```bash
# Installation manuelle des dépendances
pip install -r requirements.txt
pip install asyncpg httpx psutil pytest pytest-cov

# Lancer la validation
python validate_service.py
```

### Méthode 3 : Test Rapide (Diagnostic)

```bash
# Test rapide des prérequis seulement
python quick_test.py
```

**Utilisation** : Diagnostic rapide avant validation complète

## 📊 Tests Effectués

### 1. 📡 **Connexion PostgreSQL**
- ✅ Test de connectivité à `127.0.0.1:5432`
- ✅ Vérification version PostgreSQL
- ✅ Test des permissions utilisateur
- ✅ Métriques de performance connexion

### 2. 📋 **Migrations Alembic**
- ✅ Exécution `alembic upgrade head`
- ✅ Vérification historique migrations
- ✅ Validation révisions appliquées
- ✅ Test rollback potentiel

### 3. 🗄️ **Schéma Base de Données**
- ✅ Vérification tables attendues :
  - `users`, `user_settings`, `user_sessions`
  - `company_profiles`, `team_members`, `subscriptions`
  - `alembic_version`
- ✅ Analyse colonnes et types
- ✅ Vérification index et contraintes
- ✅ Détection tables manquantes/supplémentaires

### 4. 🧪 **Tests Unitaires**
- ✅ Exécution `pytest -v --cov=app`
- ✅ Couverture de code (objectif 80%+)
- ✅ Tests authentication, users, companies
- ✅ Validation temps d'exécution

### 5. 🚀 **Serveur Uvicorn**
- ✅ Démarrage serveur sur port 8000
- ✅ Test health check
- ✅ Vérification PID et processus
- ✅ Temps de démarrage

### 6. 🌐 **Endpoints Critiques**
- ✅ `GET /health` - Health check
- ✅ `GET /docs` - Documentation Swagger
- ✅ `POST /api/v1/auth/register` - Inscription
- ✅ `POST /api/v1/auth/login` - Connexion
- ✅ `GET /api/v1/users/me` - Protection auth

### 7. 📊 **Validation Données**
- ✅ Comptage enregistrements tables
- ✅ Vérification intégrité données
- ✅ Validation emails, timestamps
- ✅ Contrôle contraintes FK

## 📄 Rapport de Validation

Le script génère automatiquement `test-validation-report.md` contenant :

### 📊 **Métriques Globales**
- Tests totaux / réussis / échoués
- Taux de succès
- Durée totale validation

### 🔍 **Détails par Test**
- Statut (PASS/FAIL/WARN/SKIP)
- Métriques spécifiques
- Messages d'erreur détaillés
- Recommandations

### 📈 **Métriques Performance**
- Temps connexion DB
- Temps démarrage serveur  
- Temps réponse endpoints
- Couverture tests

### 🎯 **Recommandations**
- Actions correctives
- Optimisations suggérées
- Prochaines étapes

## 🚦 Statuts de Validation

### ✅ **PASS** - Test Réussi
- Fonctionnalité OK
- Métriques dans les seuils
- Prêt pour production

### ❌ **FAIL** - Test Échoué  
- Erreur critique
- **Action requise** avant commit
- Bloquer le déploiement

### ⚠️ **WARN** - Avertissement
- Fonctionnalité partielle
- Optimisation recommandée
- Peut procéder avec prudence

### ⏭️ **SKIP** - Test Ignoré
- Prérequis non disponibles
- Dépendance manquante
- Non critique

## 🔧 Résolution de Problèmes

### Erreur : "Connection refused"
```
❌ Erreur connexion PostgreSQL: connection refused
```

**Solutions** :
1. Vérifier cloud-sql-proxy : `ps aux | grep cloud_sql_proxy`
2. Tester port : `telnet 127.0.0.1 5432`  
3. Vérifier credentials database

### Erreur : "Module not found"
```
❌ Import manquant: No module named 'asyncpg'
```

**Solutions** :
```bash
pip install asyncpg httpx psutil
# ou
pip install -r requirements.txt
```

### Erreur : "Port already in use"
```
⚠️ Port 8000 déjà utilisé
```

**Solutions** :
```bash
# Trouver le processus
lsof -i :8000
# Ou sur Windows
netstat -ano | findstr :8000

# Tuer le processus
kill -9 PID
```

### Erreur : "Tests timeout"
```
❌ Tests timeout après 5 minutes
```

**Solutions** :
1. Vérifier performance DB
2. Réduire scope des tests
3. Augmenter timeout dans script

### Erreur : "Alembic migration failed"
```
❌ Erreur Alembic: target database not up to date
```

**Solutions** :
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head

# Ou générer nouvelle migration
alembic revision --autogenerate -m "fix schema"
```

## 🎯 Critères de Validation

### ✅ **Validation Réussie** 
- Tous les tests PASS
- Couverture tests ≥ 80%
- Temps réponse < 1s
- 0 erreur critique

**➡️ Action** : Commit autorisé

### ❌ **Validation Échouée**
- ≥ 1 test FAIL
- Erreurs critiques détectées  
- Couverture < 60%

**➡️ Action** : Correction obligatoire

### ⚠️ **Validation Partielle**
- Tests WARN seulement
- Couverture 60-80%
- Performance dégradée

**➡️ Action** : Commit avec prudence

## 📅 Utilisation dans le Workflow

### 1. **Avant Développement**
```bash
# Test rapide des prérequis
python quick_test.py
```

### 2. **Pendant Développement**
```bash
# Tests unitaires seulement
python -m pytest app/tests/ -v
```

### 3. **Avant Commit**
```bash
# Validation complète
.\run_validation.ps1
```

### 4. **En cas d'Échec**
```bash
# 1. Lire le rapport
cat test-validation-report.md

# 2. Corriger les erreurs

# 3. Re-valider
.\run_validation.ps1
```

### 5. **Après Validation Réussie**
```bash
# Commit safe
git add .
git commit -m "feat: user-service validated and ready"
git push origin feature/user-service
```

## 🔗 Intégration CI/CD

Ce script de validation peut être intégré dans le pipeline CI/CD :

```yaml
# .github/workflows/user-service-validation.yml
- name: Validate User Service
  run: |
    cd apps/backend/user-service
    python validate_service.py
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## 📞 Support

En cas de problème avec la validation :

1. **Consulter le rapport** : `test-validation-report.md`
2. **Logs détaillés** : Sortie console du script
3. **Tests individuels** : `python -m pytest app/tests/test_specific.py -v`
4. **Contact** : DevOps Team SkillForge AI

---

**🚀 Objectif** : Garantir la qualité et la fiabilité du User-Service avant tout déploiement

**🎯 Résultat** : Service validé, testé et prêt pour la production