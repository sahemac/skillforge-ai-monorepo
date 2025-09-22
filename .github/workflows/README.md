# SkillForge AI - GitHub Actions Workflows

Ce répertoire contient tous les workflows GitHub Actions pour automatiser le déploiement, la sécurité et la gestion de SkillForge AI.

## 📋 Vue d'ensemble des Workflows

### 1. 🚀 Frontend Deployment (`frontend-deploy.yml`)
**Déploie automatiquement les 5 applications frontend avec une stratégie matrix**

**Déclencheurs :**
- Push sur `main` ou `develop` avec modifications dans `apps/frontend/**`
- Pull Request sur `main` ou `develop`
- Déclenchement manuel avec options personnalisées

**Fonctionnalités clés :**
- ✅ Détection intelligente des changements
- ✅ Matrix strategy pour 5 apps (shell, auth, admin, company, learner)
- ✅ Build & test (lint, type-check, tests unitaires)
- ✅ Docker build & push vers `gcr.io/skillforge-ai-mvp-25`
- ✅ Déploiement Cloud Run avec health checks
- ✅ Rollout graduel en production (10% → 50% → 100%)
- ✅ Rollback automatique en cas d'échec
- ✅ Notifications Slack

**Services déployés :**
- `skillforge-frontend-shell-{environment}`
- `skillforge-frontend-auth-{environment}`
- `skillforge-frontend-admin-{environment}`
- `skillforge-frontend-company-{environment}`
- `skillforge-frontend-learner-{environment}`

### 2. 🔧 Backend Deployment (`backend-deploy.yml`)
**Déploie les services backend avec tests et migrations**

**Déclencheurs :**
- Push sur `main` ou `develop` avec modifications dans `apps/backend/**`
- Pull Request sur `main` ou `develop`
- Déclenchement manuel avec options

**Fonctionnalités clés :**
- ✅ Tests unitaires avec PostgreSQL et Redis
- ✅ Migrations de base de données automatisées
- ✅ Scans de sécurité (Bandit, Safety, Semgrep)
- ✅ Docker build optimisé multi-stage
- ✅ Déploiement Cloud Run sécurisé
- ✅ Health checks et tests de connectivité
- ✅ Rollout graduel en production

**Services déployés :**
- `skillforge-user-service-{environment}`
- `skillforge-company-service-{environment}`

### 3. 🏗️ Infrastructure Deployment (`infrastructure-deploy.yml`)
**Gère l'infrastructure avec Terraform**

**Déclencheurs :**
- Push sur `main` ou `develop` avec modifications dans `infrastructure/**`
- Pull Request (plan seulement)
- Déclenchement manuel avec actions personnalisées

**Fonctionnalités clés :**
- ✅ Validation Terraform (fmt, validate)
- ✅ Scans de sécurité (tfsec, Checkov, Terrascan)
- ✅ Plan automatique et apply conditionnel
- ✅ Gestion des états Terraform sécurisée
- ✅ Tests post-déploiement
- ✅ Documentation automatique

**Actions supportées :**
- `plan` : Génère un plan Terraform
- `apply` : Applique les changements
- `destroy` : Détruit l'infrastructure (manuel uniquement)

### 4. 🔐 Environment Setup (`environment-setup.yml`)
**Gère les configurations et secrets d'environnement**

**Déclencheurs :**
- Déclenchement manuel
- Validation quotidienne automatique (2h UTC)

**Fonctionnalités clés :**
- ✅ Validation des secrets requis
- ✅ Test de connectivité (DB, Redis)
- ✅ Rotation automatique des secrets
- ✅ Audit de sécurité IAM
- ✅ Mise à jour des variables d'environnement
- ✅ Nettoyage des anciennes versions

**Actions supportées :**
- `validate` : Vérifie la configuration
- `update` : Met à jour les variables
- `rotate-secrets` : Fait tourner les secrets

### 5. 🛡️ Security Validation (`security-validation.yml`)
**Effectue des scans de sécurité complets**

**Déclencheurs :**
- Push sur toutes les branches
- Pull Request
- Scan quotidien automatique (3h UTC)
- Déclenchement manuel avec options

**Scans inclus :**
- ✅ **Dépendances** : npm audit, Safety, Bandit
- ✅ **Code** : CodeQL, Trivy, ESLint Security
- ✅ **Conteneurs** : Trivy, Docker Scout
- ✅ **Infrastructure** : tfsec, Checkov, Terrascan
- ✅ **Secrets** : TruffleHog, GitLeaks, detect-secrets
- ✅ **Conformité** : GDPR, headers de sécurité

## 🔧 Configuration Requise

### Secrets GitHub (Repository/Environment)

#### Authentification Google Cloud
```
WIF_PROVIDER=projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
WIF_SERVICE_ACCOUNT=github-actions@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

#### Base de données et Cache
```
DATABASE_URL=postgresql://user:password@host:port/dbname
REDIS_URL=redis://host:port
```

#### Application
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

#### Infrastructure
```
TF_STATE_BUCKET=skillforge-terraform-state
```

#### Notifications
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Variables d'Environnement GitHub

#### Staging
```
VITE_API_URL=https://api-staging.skillforge-ai.com
VITE_AUTH_DOMAIN=auth-staging.skillforge-ai.com
VITE_ENVIRONMENT=staging
```

#### Production
```
VITE_API_URL=https://api.skillforge-ai.com
VITE_AUTH_DOMAIN=auth.skillforge-ai.com
VITE_ENVIRONMENT=production
```

## 🚀 Utilisation

### Déploiement Frontend
```bash
# Déployer automatiquement lors d'un push
git push origin develop  # → déploie en staging
git push origin main     # → déploie en production

# Déploiement manuel
# Aller dans Actions → Frontend Applications Deployment → Run workflow
# Choisir l'environnement et les apps à déployer
```

### Déploiement Backend
```bash
# Déploiement automatique avec migrations
git push origin develop  # → staging avec migrations
git push origin main     # → production avec rollout graduel

# Déploiement manuel sans migrations
# Actions → Backend Services Deployment → Run workflow
# Cocher "run_migrations: false"
```

### Gestion Infrastructure
```bash
# Plan automatique sur PR
git checkout -b feature/new-infrastructure
# Modifier infrastructure/
git push origin feature/new-infrastructure
# → Crée une PR avec plan Terraform

# Apply manuel
# Actions → Infrastructure Deployment → Run workflow
# Action: "apply", Auto approve: true
```

### Rotation des Secrets
```bash
# Actions → Environment Configuration → Run workflow
# Environment: production
# Action: rotate-secrets
```

### Scans de Sécurité
```bash
# Scan complet manuel
# Actions → Security Validation → Run workflow
# Scan type: "full"

# Scan ciblé
# Actions → Security Validation → Run workflow
# Scan type: "dependencies-only"
```

## 📊 Monitoring et Alertes

### Notifications Slack
Toutes les workflows envoient des notifications Slack avec :
- ✅ Statut du déploiement
- 🔗 Liens vers les services déployés
- 📊 Métriques de performance
- 🚨 Alertes en cas d'échec

### Artifacts et Rapports
Chaque workflow génère des artifacts :
- **Rapports de sécurité** (JSON, SARIF)
- **Plans Terraform**
- **Logs de déploiement**
- **Rapports de conformité**

### Health Checks
Les déploiements incluent des health checks automatiques :
- ✅ Endpoints `/health`
- ✅ Connectivité base de données
- ✅ Performance response time
- ✅ Tests d'intégration API

## 🔐 Sécurité et Bonnes Pratiques

### Workload Identity Federation
- ❌ **Pas de clés JSON** stockées comme secrets
- ✅ **WIF** pour l'authentification Google Cloud
- ✅ **Permissions minimales** pour chaque service account

### Secrets Management
- ✅ **Google Secret Manager** pour les secrets sensibles
- ✅ **Rotation automatique** des secrets
- ✅ **Audit trail** complet
- ✅ **Versions multiples** avec cleanup

### Container Security
- ✅ **Images multi-stage** optimisées
- ✅ **Utilisateurs non-root**
- ✅ **Scans de vulnérabilités** automatiques
- ✅ **Signatures d'images** (production)

### Network Security
- ✅ **Private Google Access**
- ✅ **IAP** pour les services internes
- ✅ **Headers de sécurité** configurés
- ✅ **HTTPS** obligatoire

## 🐛 Troubleshooting

### Échecs de Déploiement

1. **Health Check Failed**
   ```bash
   # Vérifier les logs Cloud Run
   gcloud run services logs read SERVICE_NAME --region=europe-west1
   
   # Vérifier la configuration
   gcloud run services describe SERVICE_NAME --region=europe-west1
   ```

2. **Database Connection Issues**
   ```bash
   # Vérifier Cloud SQL Proxy
   gcloud sql instances describe skillforge-pg-instance-staging
   
   # Tester la connectivité
   gcloud sql connect skillforge-pg-instance-staging --user=postgres
   ```

3. **Secrets Access Issues**
   ```bash
   # Vérifier les permissions Secret Manager
   gcloud secrets get-iam-policy SECRET_NAME
   
   # Lister les versions de secrets
   gcloud secrets versions list SECRET_NAME
   ```

### Échecs de Sécurité

1. **Vulnérabilités Détectées**
   - Consulter les rapports dans les artifacts
   - Mettre à jour les dépendances
   - Appliquer les patches de sécurité

2. **Secrets Détectés**
   - Révoquer immédiatement les secrets exposés
   - Nettoyer l'historique Git si nécessaire
   - Mettre à jour `.secrets.baseline`

3. **Policy Violations**
   - Réviser les configurations Terraform
   - Appliquer les recommandations tfsec/Checkov
   - Mettre à jour les policies d'entreprise

## 📈 Performance et Optimisation

### Cache Strategy
- ✅ **npm cache** pour les dépendances Node.js
- ✅ **pip cache** pour les dépendances Python
- ✅ **Docker layer cache** pour les builds
- ✅ **Terraform cache** pour les plans

### Parallel Execution
- ✅ **Matrix strategy** pour les déploiements multiples
- ✅ **Jobs parallèles** pour les scans de sécurité
- ✅ **Artifact sharing** optimisé

### Resource Optimization
- ✅ **Auto-scaling** Cloud Run (0 → max instances)
- ✅ **Resource limits** appropriés par environnement
- ✅ **Cleanup** automatique des anciennes versions

## 🔄 Maintenance

### Tâches Quotidiennes Automatisées
- 🔐 Validation des secrets (2h UTC)
- 🛡️ Scans de sécurité (3h UTC)
- 🧹 Cleanup des artifacts anciens

### Tâches Mensuelles Recommandées
- 🔄 Rotation des secrets de production
- 📊 Révision des rapports de sécurité
- 🗂️ Cleanup des anciennes révisions Cloud Run
- 📖 Mise à jour de la documentation

### Tâches Trimestrielles
- 🔍 Audit complet de sécurité
- 📋 Révision des permissions IAM
- 🏗️ Optimisation des coûts infrastructure
- 🚀 Mise à jour des versions des outils

## 🆘 Support et Contact

Pour toute question ou problème :

1. **Vérifier les logs** dans GitHub Actions
2. **Consulter les artifacts** générés
3. **Checker les notifications** Slack
4. **Créer une issue** avec les détails du problème

---

**Créé par :** SkillForge AI DevOps Team  
**Dernière mise à jour :** $(date)  
**Version :** 1.0.0