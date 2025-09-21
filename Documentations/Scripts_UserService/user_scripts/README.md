# Scripts de Développement - SkillForge AI User Service

Ce dossier contient tous les scripts de développement, test, migration et validation créés durant le développement du user-service.

## 🗂️ Organisation

### 📁 `migration/`
Scripts de migration et gestion de base de données:
- `migrate_to_postgresql.py` - Migration principale vers PostgreSQL Cloud SQL
- `create_initial_migration.py` - Création de la migration initiale Alembic
- `recreate_postgresql_tables.py` - Recréation des tables PostgreSQL
- `recreate_db_with_proper_models.py` - Recréation avec modèles définitifs
- `run_migration.py` - Exécution des migrations Alembic

### 📁 `testing/`
Scripts de test et validation:
- `test_*.py` - Scripts de test des endpoints et fonctionnalités
- `check_*.py` - Scripts de vérification du schéma et déploiement
- `copy_postgresql_users_to_sqlite.py` - Copie des utilisateurs entre bases
- `diagnose_cloud_sql.py` - Diagnostic Cloud SQL

### 📁 `deployment/`
Scripts de déploiement et configuration:
- `deploy_*.py` - Scripts de déploiement sur différents environnements
- `setup_*.py` - Scripts de configuration initiale
- `create_*.py` - Scripts de création d'utilisateurs et tables
- `final_deployment.py` - Déploiement final

### 📁 `validation/`
Scripts de validation et tests finaux:
- `validate_postgresql_endpoints.py` - Validation des endpoints PostgreSQL

## ✅ Status de Validation

### Migration PostgreSQL
- ✅ **Migration complète réussie**
- ✅ **5 utilisateurs de test créés**
- ✅ **Authentification validée (5/5)**
- ✅ **Connexion Cloud SQL opérationnelle**

### Sécurité
- ✅ **Variables d'environnement implémentées**
- ✅ **Mots de passe sécurisés**
- ✅ **Configuration production-ready**

### Architecture
- ✅ **Modèles définitifs déployés**
- ✅ **API endpoints fonctionnels**
- ✅ **Base PostgreSQL prête**

## 🚀 Utilisation

Ces scripts sont **archivés** et ne doivent plus être utilisés en production.

### Pour référence uniquement:
```bash
# Exemple d'utilisation (ARCHIVE)
cd documentations/user_scripts/migration/
python migrate_to_postgresql.py
```

### Production:
```bash
# Utiliser uniquement l'application principale
uvicorn app.main:app --reload
```

## 📝 Notes

- **Créé le:** 2025-09-19
- **Contexte:** Développement et migration PostgreSQL
- **Status:** Archivé - Validation complète
- **Maintenir:** Non (scripts à usage unique)

---

**⚠️ Important:** Ces scripts sont conservés pour documentation et historique. L'application finale utilise uniquement le code dans `app/`.