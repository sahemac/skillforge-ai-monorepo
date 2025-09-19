# Documentation et Ressources de Développement

Ce dossier contient toute la documentation et les ressources créées durant le développement du SkillForge AI User Service.

## 📁 Structure

### `dev_docs/`
Documentation technique de développement :
- `CLOUD_SQL_SETUP.md` - Guide de configuration Cloud SQL
- `deployment_status_summary.md` - Rapport de statut de déploiement
- `RUN_TESTS_WITH_CLOUD_SQL.md` - Instructions de test avec Cloud SQL

### `user_scripts/` 
Scripts de développement organisés par catégorie :
- `migration/` - Scripts de migration PostgreSQL (5 scripts)
- `testing/` - Scripts de test et validation (12 scripts)  
- `deployment/` - Scripts de déploiement (9 scripts)
- `validation/` - Scripts de validation finale (1 script)

### `test_data/`
Données et bases de test SQLite :
- `*.db` - Bases de données SQLite de test
- `*.json` - Données de test utilisateurs et entreprises

## 🚫 Exclusion Git

Tous les dossiers sont exclus du repository via `.gitignore` :
```gitignore
documentations/user_scripts/
documentations/dev_docs/
documentations/test_data/
```

## ✅ Status

- **Migration PostgreSQL** : ✅ Complète et validée
- **API Endpoints** : ✅ Fonctionnels  
- **Sécurité** : ✅ Variables d'environnement configurées
- **Tests** : ✅ 5/5 utilisateurs PostgreSQL validés

## 📝 Notes

- **Créé** : 2025-09-19
- **Usage** : Archive de développement
- **Maintenance** : Non (ressources temporaires)

---

**⚠️ Ces ressources sont archivées. L'application de production utilise uniquement les fichiers à la racine du projet.**