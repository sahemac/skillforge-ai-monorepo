# Migration Automatique - SkillForge User Service

## Vue d'ensemble

Le système de migration automatique supporte plusieurs environnements et méthodes de connexion :

### 🏗️ Environnements

1. **Développement local** : SQLite (fallback)
2. **Développement avec PostgreSQL** : PostgreSQL local via proxy optionnel
3. **CI/CD (GitHub Actions)** : Cloud SQL via Cloud SQL Proxy
4. **Production (Cloud Run)** : Cloud SQL via unix socket natif

## 📁 Fichiers de configuration

### Scripts de migration
- `run_migrations.py` - Script principal de migration automatique
- `scripts/run_migrations_cicd.sh` - Script pour environnement CI/CD
- `alembic/env.py` - Configuration Alembic améliorée

### Workflows GitHub Actions
- `.github/workflows/run-alembic-migration.yml` - Workflow de migration automatique
- `.github/workflows/deploy-user-service.yml` - Workflow de déploiement principal

## 🔧 Configuration par environnement

### Local avec SQLite (développement)
```bash
# Aucune configuration requise, utilise SQLite par défaut
python run_migrations.py
```

### Local avec PostgreSQL 
```bash
# Via variables d'environnement
POSTGRES_PASSWORD="Psaumes@27" python run_migrations.py

# Ou via URL complète
DATABASE_URL="postgresql+asyncpg://skillforge_user:password@localhost:5432/skillforge_db" python run_migrations.py
```

### CI/CD (GitHub Actions)
Le workflow utilise automatiquement :
1. **Cloud SQL Proxy** sur port 5432
2. **Secret Manager** pour récupérer le mot de passe
3. **Fallback** sur DATABASE_URL des secrets GitHub

### Production (Cloud Run)
Configuration automatique via unix socket :
```bash
# Variables d'environnement Cloud Run
CLOUD_SQL_CONNECTION_NAME="skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging"
POSTGRES_USER="skillforge_user"
POSTGRES_PASSWORD="<from-secret-manager>"
POSTGRES_DB="skillforge_db"
```

## 🔐 Gestion des secrets

### Secret Manager (recommandé)
```bash
# Le workflow récupère automatiquement depuis :
gcloud secrets versions access latest --secret="postgres-password" --project="skillforge-ai-mvp-25"
```

### GitHub Secrets (fallback)
- `DATABASE_URL_STAGING`
- `DATABASE_URL_PRODUCTION`
- `GCP_PROJECT_ID`
- `GCP_WIF_PROVIDER`
- `GCP_CICD_SERVICE_ACCOUNT`

## 🚀 Workflow CI/CD

### Architecture de déploiement
```
1. Tests unitaires
2. Build Docker image
3. Migration base de données (avec Cloud SQL Proxy)
4. Déploiement Cloud Run (avec unix socket natif)
5. Validation IAP
```

### Migration automatique dans le pipeline
1. **Authentification GCP** via Workload Identity Federation
2. **Installation Cloud SQL Proxy** (version 2.11.0)
3. **Récupération mot de passe** depuis Secret Manager
4. **Démarrage proxy** sur port 5432
5. **Exécution migrations** via `run_migrations.py`
6. **Vérification statut** avec `alembic current`
7. **Nettoyage proxy**

## 📊 Points critiques

### Pourquoi Cloud SQL Proxy en CI/CD ?
- **GitHub Actions** s'exécute AVANT le déploiement Cloud Run
- **Pas d'accès** aux unix sockets Cloud SQL depuis GitHub Actions
- **Nécessité** d'une connexion réseau via proxy

### Connexion native en production
- **Cloud Run** a accès direct via unix socket
- **Plus performant** et sécurisé
- **Pas de proxy** nécessaire

## 🧪 Tests et vérification

### Test local
```bash
cd apps/backend/user-service
python run_migrations.py
```

### Test avec PostgreSQL local
```bash
# Démarrer PostgreSQL local ou cloud-sql-proxy
POSTGRES_PASSWORD="Psaumes@27" python run_migrations.py
```

### Vérification statut migration
```bash
# Version async (pour l'application)
DATABASE_URL="postgresql+asyncpg://..." alembic current

# Version sync (pour Alembic)
DATABASE_URL="postgresql://..." alembic current
```

## 🔄 Workflow de déploiement

### Déclenchement automatique
- **Push** sur branche `develop`
- **Changements** dans `apps/backend/user-service/**`
- **Manuel** via `workflow_dispatch`

### Contrôles disponibles
- `skip_migration: true` - Ignorer la migration
- `environment: staging|production` - Environnement cible

### Monitoring
- **Logs** disponibles dans les artifacts
- **Status migration** dans le résumé GitHub Actions
- **Health checks** post-déploiement

## 🛠️ Dépannage

### Erreurs communes

1. **Connexion refusée**
   - Vérifier que Cloud SQL Proxy est démarré
   - Vérifier les permissions du service account

2. **Mot de passe manquant**
   - Vérifier Secret Manager : `postgres-password`
   - Vérifier GitHub Secrets : `DATABASE_URL_STAGING`

3. **Migration échoue**
   - Vérifier syntaxe SQL dans les fichiers migration
   - Vérifier état actuel : `alembic current`

### Commands utiles
```bash
# État actuel
alembic current -v

# Historique
alembic history

# Migration manuelle
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📝 Architecture des fichiers

```
apps/backend/user-service/
├── run_migrations.py              # Script principal
├── scripts/
│   └── run_migrations_cicd.sh     # Script CI/CD
├── alembic/
│   ├── env.py                     # Config Alembic
│   └── versions/
│       └── 001_initial_migration.py
└── MIGRATION_AUTOMATIQUE.md       # Cette documentation
```

## ✅ Résumé de la configuration

- ✅ **Migration automatique** configurée
- ✅ **Support multi-environnement** (local, CI/CD, production)
- ✅ **Cloud SQL Proxy** pour CI/CD
- ✅ **Unix socket natif** pour Cloud Run
- ✅ **Secret Manager** intégré
- ✅ **Fallback** sur GitHub Secrets
- ✅ **Tests** et vérifications automatiques
- ✅ **Logging** et monitoring
- ✅ **Nettoyage** automatique des ressources

Le système est maintenant prêt pour un déploiement automatique sécurisé en production ! 🎉