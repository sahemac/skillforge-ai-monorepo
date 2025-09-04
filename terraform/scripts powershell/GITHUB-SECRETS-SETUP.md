# 🔐 Configuration des Secrets GitHub - SkillForge AI

## Vue d'ensemble

Ce document décrit la configuration complète des secrets GitHub requis pour le pipeline Terraform automatisé de SkillForge AI.

## 🔑 Secrets Requis

### Secrets Principaux

| Secret | Type | Description | Environnement |
|--------|------|-------------|---------------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Repository | URL du Workload Identity Provider | All |
| `GCP_SERVICE_ACCOUNT` | Repository | Email du Service Account Google Cloud | All |
| `SLACK_WEBHOOK` | Repository | Webhook URL pour notifications Slack | All |
| `TEAMS_WEBHOOK` | Repository | Webhook URL pour notifications Teams | All |

### Secrets d'Environnement

| Secret | Environnement | Description |
|--------|---------------|-------------|
| `TF_VAR_jwt_secret` | staging | JWT Secret pour l'environnement staging |
| `TF_VAR_jwt_secret` | production | JWT Secret pour l'environnement production |
| `TF_VAR_postgres_password` | staging | Mot de passe PostgreSQL staging |
| `TF_VAR_postgres_password` | production | Mot de passe PostgreSQL production |

## 🛠️ Configuration Étape par Étape

### 1. Configuration Google Cloud

#### A. Créer un Service Account

```bash
# 1. Créer le service account
gcloud iam service-accounts create terraform-ci-cd \
    --description="Service account for Terraform CI/CD pipeline" \
    --display-name="Terraform CI/CD"

# 2. Assigner les rôles nécessaires
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/editor"

gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountAdmin"
```

#### B. Configurer Workload Identity Federation

```bash
# 1. Créer le Workload Identity Pool
gcloud iam workload-identity-pools create "github-actions" \
    --project="skillforge-ai-mvp-25" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# 2. Créer le Provider
gcloud iam workload-identity-pools providers create-oidc "github" \
    --project="skillforge-ai-mvp-25" \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --display-name="GitHub provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Autoriser le repository GitHub
gcloud iam service-accounts add-iam-policy-binding \
    --project="skillforge-ai-mvp-25" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/584748485117/locations/global/workloadIdentityPools/github-actions/attribute.repository/VOTRE-USERNAME/skillforge-ai-monorepo" \
    terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

#### C. Récupérer les Valeurs pour les Secrets

```bash
# Workload Identity Provider URL
echo "projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github"

# Service Account Email
echo "terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com"
```

### 2. Configuration GitHub Repository Secrets

#### A. Accéder aux Settings

1. Aller sur `https://github.com/VOTRE-USERNAME/skillforge-ai-monorepo`
2. Cliquer sur **Settings** → **Secrets and variables** → **Actions**

#### B. Ajouter les Repository Secrets

```bash
# 1. GCP_WORKLOAD_IDENTITY_PROVIDER
Name: GCP_WORKLOAD_IDENTITY_PROVIDER
Value: projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github

# 2. GCP_SERVICE_ACCOUNT
Name: GCP_SERVICE_ACCOUNT
Value: terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com

# 3. SLACK_WEBHOOK (optionnel)
Name: SLACK_WEBHOOK
Value: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# 4. TEAMS_WEBHOOK (optionnel)
Name: TEAMS_WEBHOOK
Value: https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK
```

### 3. Configuration des Environments GitHub

#### A. Créer l'Environment Staging

1. **Settings** → **Environments** → **New environment**
2. Nom: `staging`
3. **Protection rules**: 
   - ✅ Required reviewers: Ajouter vous-même
   - ✅ Wait timer: 0 minutes
   - ✅ Deployment branches: `develop` et `main`

**Environment secrets pour staging:**
```bash
Name: TF_VAR_jwt_secret
Value: [GÉNÉRER UN SECRET JWT FORT - 64+ caractères]

Name: TF_VAR_postgres_password  
Value: [GÉNÉRER UN MOT DE PASSE FORT - 32+ caractères]
```

#### B. Créer l'Environment Production

1. **Settings** → **Environments** → **New environment**
2. Nom: `production`
3. **Protection rules**:
   - ✅ Required reviewers: Ajouter tous les mainteneurs
   - ✅ Wait timer: 30 minutes
   - ✅ Deployment branches: Selected branches → `main` uniquement

**Environment secrets pour production:**
```bash
Name: TF_VAR_jwt_secret
Value: [DIFFÉRENT DE STAGING - 64+ caractères]

Name: TF_VAR_postgres_password
Value: [DIFFÉRENT DE STAGING - 32+ caractères]
```

## 🔧 Scripts d'Automatisation

### Script de Génération des Secrets

```bash
#!/bin/bash
# generate-secrets.sh

echo "🔐 Génération des secrets pour SkillForge AI"

echo ""
echo "JWT Secret (Staging):"
openssl rand -base64 48

echo ""
echo "JWT Secret (Production):"
openssl rand -base64 48

echo ""
echo "PostgreSQL Password (Staging):"
openssl rand -base64 32

echo ""
echo "PostgreSQL Password (Production):"
openssl rand -base64 32

echo ""
echo "⚠️  IMPORTANT: Sauvegardez ces valeurs dans un gestionnaire de mots de passe sécurisé"
```

### Script de Configuration GCP

Créer le fichier `setup-gcp-auth.sh` :

```bash
#!/bin/bash
# setup-gcp-auth.sh

PROJECT_ID="skillforge-ai-mvp-25"
PROJECT_NUMBER="584748485117"
REPO_NAME="VOTRE-USERNAME/skillforge-ai-monorepo"  # MODIFIER CETTE VALEUR

echo "🚀 Configuration de l'authentification GCP pour GitHub Actions"

# Créer le service account
echo "1️⃣ Création du service account..."
gcloud iam service-accounts create terraform-ci-cd \
    --project=$PROJECT_ID \
    --description="Service account for Terraform CI/CD pipeline" \
    --display-name="Terraform CI/CD"

# Assigner les rôles
echo "2️⃣ Attribution des rôles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-ci-cd@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:terraform-ci-cd@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Créer Workload Identity Pool
echo "3️⃣ Création du Workload Identity Pool..."
gcloud iam workload-identity-pools create "github-actions" \
    --project=$PROJECT_ID \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Créer le Provider
echo "4️⃣ Création du Provider OIDC..."
gcloud iam workload-identity-pools providers create-oidc "github" \
    --project=$PROJECT_ID \
    --location="global" \
    --workload-identity-pool="github-actions" \
    --display-name="GitHub provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# Autoriser le repository
echo "5️⃣ Autorisation du repository GitHub..."
gcloud iam service-accounts add-iam-policy-binding \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/$REPO_NAME" \
    terraform-ci-cd@$PROJECT_ID.iam.gserviceaccount.com

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "🔑 Valeurs pour les secrets GitHub:"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER: projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/providers/github"
echo "GCP_SERVICE_ACCOUNT: terraform-ci-cd@$PROJECT_ID.iam.gserviceaccount.com"
```

## ✅ Checklist de Vérification

### Avant le Premier Run

- [ ] Service Account GCP créé avec les bonnes permissions
- [ ] Workload Identity Federation configuré
- [ ] Repository secrets configurés dans GitHub
- [ ] Environments `staging` et `production` créés
- [ ] Environment secrets configurés
- [ ] Repository username modifié dans le script d'autorisation

### Tests de Validation

```bash
# 1. Tester l'authentification GCP
gcloud auth list

# 2. Vérifier les permissions du service account
gcloud projects get-iam-policy skillforge-ai-mvp-25 \
    --flatten="bindings[].members" \
    --format='table(bindings.role)' \
    --filter="bindings.members:terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com"

# 3. Tester Workload Identity
gcloud iam workload-identity-pools describe github-actions \
    --project=skillforge-ai-mvp-25 \
    --location=global
```

## 🚨 Sécurité et Bonnes Pratiques

### Rotation des Secrets

- **JWT Secrets**: Rotation tous les 90 jours
- **Passwords**: Rotation tous les 60 jours
- **Service Account Keys**: Ne pas utiliser - utiliser Workload Identity uniquement

### Monitoring

- Activer les logs d'audit GCP
- Surveiller l'utilisation du service account
- Alertes sur les échecs d'authentification

### Backup

```bash
# Sauvegarder la configuration Workload Identity
gcloud iam workload-identity-pools describe github-actions \
    --project=skillforge-ai-mvp-25 \
    --location=global \
    --format=export > workload-identity-backup.yaml
```

## 🆘 Dépannage

### Problèmes d'Authentification

```bash
# Vérifier les bindings IAM
gcloud iam service-accounts get-iam-policy \
    terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com

# Tester l'impersonation
gcloud auth print-access-token \
    --impersonate-service-account=terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

### Erreurs Courantes

1. **"Permission denied"**: Vérifier les rôles IAM
2. **"Workload Identity not found"**: Vérifier la configuration du pool
3. **"Repository not authorized"**: Vérifier le nom du repository dans l'autorisation

## 📞 Support

En cas de problème:

1. Vérifier les logs GitHub Actions
2. Consulter les logs d'audit GCP
3. Utiliser `gcloud auth login` pour tester localement
4. Contacter l'équipe DevOps avec les logs détaillés

---

**Dernière mise à jour**: 3 septembre 2025
**Version**: 1.0.0
**Auteur**: Claude Code Assistant