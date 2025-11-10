# Documentation des Workflows CI/CD SkillForge AI

Ce document décrit l'ensemble des workflows GitHub Actions utilisés pour le CI/CD de SkillForge AI.

## Vue d'ensemble

Notre infrastructure CI/CD est organisée en workflows optimisés qui se déclenchent automatiquement sur les branches appropriées:
- **develop**: Environnement de développement
- **feature/monolith-migration**: Environnement de staging
- **main**: Environnement de production

## Index des Workflows

### Workflows Principaux

1. **Backend Services Deployment** (`backend-deploy-optimized.yml`)
   - Déploiement automatisé des services backend
   - Tests, build Docker, déploiement Cloud Run
   - [Documentation détaillée](./docs/BACKEND_DEPLOYMENT.md)

2. **Frontend Applications Deployment** (`frontend-deploy.yml`)
   - Déploiement des applications frontend
   - Build Vite, création d'images Docker, déploiement Cloud Run
   - [Documentation détaillée](./docs/FRONTEND_DEPLOYMENT.md)

3. **Security Validation & Compliance** (`security-validation-optimized.yml`)
   - Validation de sécurité OWASP
   - Scan de vulnérabilités
   - [Documentation détaillée](./docs/SECURITY_VALIDATION.md)

### Workflows Spécialisés

4. **Deploy Auth Service** (`deploy-auth-service.yml`)
   - Déploiement spécifique du service d'authentification
   
5. **Deploy Project Service** (`deploy-project-service.yml`)
   - Déploiement spécifique du service de projets

6. **Infrastructure Deployment** (`infrastructure-deploy.yml`)
   - Déploiement de l'infrastructure Terraform

7. **Alembic Migration** (`run-alembic-migration.yml`)
   - Exécution des migrations de base de données

8. **Python Tests** (`run-python-tests.yml`)
   - Tests unitaires et d'intégration Python

## Workflows Disponibles

| Workflow | Fichier | Déclenchement | Environnement |
|----------|---------|---------------|---------------|
| Backend Deployment | `backend-deploy-optimized.yml` | Push sur feature/monolith-migration | Staging |
| Frontend Deployment | `frontend-deploy.yml` | Push sur feature/monolith-migration | Staging |
| Security Validation | `security-validation-optimized.yml` | Push sur feature/monolith-migration | Tous |
| Auth Service | `deploy-auth-service.yml` | Manuel ou push sur apps/backend/auth-service/** | Staging |
| Project Service | `deploy-project-service.yml` | Manuel ou push sur apps/backend/project-service/** | Staging |
| Infrastructure | `infrastructure-deploy.yml` | Manuel | Staging/Production |
| Alembic Migration | `run-alembic-migration.yml` | Manuel | Staging/Production |
| Python Tests | `run-python-tests.yml` | Pull Request | Tous |

## Conventions

### Secrets GitHub
Tous les workflows utilisent les secrets suivants:
- `GCP_PROJECT_ID`: ID du projet GCP
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: Provider d'identité Workload Identity
- `GCP_SERVICE_ACCOUNT_EMAIL`: Email du service account
- `SLACK_WEBHOOK_URL` (optionnel): Webhook pour notifications Slack

### Labels et Environnements
Tous les services déployés utilisent les labels suivants:
- `app`: Nom de l'application
- `component`: Nom du composant  
- `environment`: staging/production
- `version`: Hash du commit Git

### Stratégie de déploiement
- **Feature branches**: Déploiement en staging uniquement
- **Develop branch**: Déploiement en développement
- **Main branch**: Déploiement en production (nécessite validation manuelle)

## Monitoring et Logs

Tous les workflows envoient des logs structurés vers:
- Google Cloud Logging
- GitHub Actions logs
- Slack (notifications d'erreur)

## Structure des Fichiers

```
.github/workflows/
├── README.md                           # Ce fichier
├── docs/                              # Documentation détaillée
│   ├── BACKEND_DEPLOYMENT.md          # Guide backend
│   ├── FRONTEND_DEPLOYMENT.md         # Guide frontend
│   ├── SECURITY_VALIDATION.md         # Guide sécurité
│   └── TROUBLESHOOTING.md             # Dépannage
├── backend-deploy-optimized.yml        # Workflow backend principal
├── frontend-deploy.yml                 # Workflow frontend principal
├── security-validation-optimized.yml   # Workflow sécurité
├── deploy-auth-service.yml            # Service auth
├── deploy-project-service.yml         # Service projets
├── infrastructure-deploy.yml          # Infrastructure Terraform
├── run-alembic-migration.yml          # Migrations DB
└── run-python-tests.yml               # Tests Python
```

## Documentation Détaillée

Consultez les guides détaillés dans le dossier [docs/](./docs/):

- **[Backend Deployment](./docs/BACKEND_DEPLOYMENT.md)**: Configuration et déploiement des services backend
- **[Frontend Deployment](./docs/FRONTEND_DEPLOYMENT.md)**: Configuration et déploiement des applications frontend
- **[Security Validation](./docs/SECURITY_VALIDATION.md)**: Tests de sécurité et compliance
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)**: Résolution des problèmes courants

## Contribution

Pour ajouter ou modifier un workflow:
1. Créer le fichier YAML dans `.github/workflows/`
2. Documenter dans le dossier `docs/`
3. Mettre à jour ce README
4. Tester sur une feature branch
5. Créer une Pull Request

## Support

Pour toute question sur les workflows:
- Consultez la documentation détaillée dans `docs/`
- Vérifiez les logs GitHub Actions
- Consultez les logs Google Cloud Logging
