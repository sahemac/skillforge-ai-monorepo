# 🚀 SkillForge AI - Alembic Migration Workflows

Système de migration automatisé pour les microservices SkillForge AI avec workflows GitHub Actions réutilisables.

## 📋 Vue d'ensemble

Ce système fournit une solution complète pour les migrations de base de données automatisées avec :
- ✅ Script universel de migration pour tous les microservices
- ✅ Workflows GitHub Actions modulaires et réutilisables
- ✅ Gestion d'erreurs et rollback automatique
- ✅ Health checks et validation post-migration
- ✅ Logging détaillé et artifacts

## 🏗️ Architecture

```
.github/workflows/
├── run-alembic-migration.yml      # Workflow réutilisable pour migrations
├── run-python-tests.yml           # Tests unitaires optimisés
├── build-push-docker.yml          # Build et push Docker
├── deploy-to-cloud-run.yml        # Déploiement Cloud Run
├── deploy-user-service.yml        # Pipeline complet user-service
└── setup-environment-secrets.yml  # Guide configuration secrets

scripts/
└── migrate.sh                     # Script universel de migration
```

## 🔧 Utilisation

### 1. Configuration des secrets

Configurez ces secrets dans GitHub Repository Settings → Secrets and variables → Actions :

**Base de données :**
- `DATABASE_URL_STAGING`: `postgresql+asyncpg://user:pass@host:port/db_staging`
- `DATABASE_URL_PRODUCTION`: `postgresql+asyncpg://user:pass@host:port/db_prod`

**Google Cloud :**
- `GCP_PROJECT_ID`: ID du projet GCP
- `GCP_WIF_PROVIDER`: Provider Workload Identity Federation
- `GCP_CICD_SERVICE_ACCOUNT`: Compte de service CI/CD

### 2. Pipeline automatique

Le pipeline `deploy-user-service.yml` s'exécute automatiquement sur :
- Push sur `develop` branch avec changements dans `apps/backend/user-service/**`
- Déclenchement manuel via GitHub Actions UI

### 3. Utilisation manuelle du script

```bash
# Migration pour user-service en staging
./scripts/migrate.sh user-service staging

# Migration pour company-service en production
./scripts/migrate.sh company-service production
```

## 🔄 Pipeline de déploiement

1. **Tests unitaires** - Validation du code
2. **Build Docker** - Construction et scan sécurité de l'image
3. **Migration DB** - Application des migrations Alembic
4. **Déploiement** - Déploiement sur Cloud Run
5. **Validation** - Health checks et post-validation

## 🛠️ Fonctionnalités avancées

### Gestion d'erreurs et rollback
- Backup automatique de la révision actuelle
- Rollback automatique en cas d'échec
- Logging détaillé pour le debugging

### Options de déploiement manuel
```yaml
# Dans GitHub Actions UI
skip_migration: true     # Skip migration step
environment: production  # Target environment
```

### Health checks
- Validation de connectivité base de données
- Tests post-migration
- Monitoring du service déployé

## 📁 Structure des microservices

Chaque microservice doit avoir cette structure :
```
apps/backend/SERVICE_NAME/
├── alembic.ini              # Configuration Alembic
├── alembic/
│   ├── env.py              # Environnement Alembic
│   └── versions/           # Fichiers de migration
├── app/
│   └── models/             # Modèles SQLModel
├── requirements.txt         # Dépendances Python
└── main.py                 # Point d'entrée FastAPI
```

## 🔍 Monitoring et logging

### Logs de migration
- Fichiers de log détaillés : `/tmp/migrate-SERVICE-TIMESTAMP.log`
- Upload automatique des logs comme artifacts GitHub
- Retention : 30 jours

### Notifications
- ✅ Succès avec résumé complet
- ❌ Échec avec étapes de résolution
- 📊 Rapport détaillé dans GitHub Step Summary

## 🚨 Résolution de problèmes

### Migration échoue
1. Vérifiez les logs dans les artifacts GitHub Actions
2. Validez la connectivité base de données
3. Testez la migration localement
4. Utilisez `skip_migration: true` si nécessaire

### Rollback manuel
```bash
cd apps/backend/user-service
alembic downgrade REVISION_ID
```

### Debugging connectivité
```bash
# Test connexion PostgreSQL
python3 -c "
import asyncio
import asyncpg
from urllib.parse import urlparse

url = 'your_database_url_here'
parsed = urlparse(url)
# Connexion et test...
"
```

## 🔄 Extension pour nouveaux microservices

1. **Créez la structure Alembic** :
```bash
cd apps/backend/NEW_SERVICE
alembic init alembic
```

2. **Configurez `alembic.ini`** avec votre DATABASE_URL

3. **Créez un workflow de déploiement** basé sur `deploy-user-service.yml`

4. **Testez avec le script universel** :
```bash
./scripts/migrate.sh NEW_SERVICE staging
```

## 📚 Bonnes pratiques

### Sécurité
- ✅ Mots de passe forts et uniques par environnement
- ✅ Connexions SSL/TLS activées
- ✅ Comptes utilisateurs avec permissions minimales
- ✅ Rotation régulière des mots de passe

### Migrations
- ✅ Testez toujours localement avant push
- ✅ Migrations réversibles quand possible
- ✅ Sauvegarde avant migrations critiques
- ✅ Monitoring post-migration

### CI/CD
- ✅ Tests unitaires obligatoires
- ✅ Scan sécurité des images Docker
- ✅ Déploiement conditionnel après migration
- ✅ Notifications détaillées

## 🔗 Workflows réutilisables

Tous les workflows sont conçus pour être réutilisés :

```yaml
# Utilisation du workflow de migration
- name: Run Migration
  uses: ./.github/workflows/run-alembic-migration.yml
  with:
    service_name: 'your-service'
    environment: 'staging'
  secrets:
    DATABASE_URL: ${{ secrets.DATABASE_URL_STAGING }}
```

## 📞 Support

Pour questions et problèmes :
1. Consultez les logs dans GitHub Actions artifacts
2. Vérifiez la configuration des secrets
3. Testez localement avec le script `migrate.sh`
4. Consultez les guides de résolution de problèmes

---

**Créé avec ❤️ pour SkillForge AI**  
*Architecture modulaire • Sécurité renforcée • Déploiements fiables*