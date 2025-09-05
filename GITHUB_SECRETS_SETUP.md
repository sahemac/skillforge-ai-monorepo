# 🔐 Configuration des Secrets GitHub pour SkillForge AI

## Problème d'authentification Google Cloud résolu

L'erreur d'authentification Google Cloud indique un problème de configuration du Workload Identity Federation.

### Erreur observée
```
google-github-actions/auth failed with: failed to generate Google Cloud federated token for //iam.googleapis.com/***: {"error":"invalid_grant","error_description":"The audience in ID Token [https://iam.googleapis.com/***] does not match the expected audience https://github.com/sahemac/skillforge-ai-monorepo."}
```

## 🛠️ Solution : Configuration des secrets GitHub

### Secrets requis dans GitHub Repository Settings → Secrets and variables → Actions :

#### 1. Workload Identity Federation
```bash
# Nom du secret: GCP_WORKLOAD_IDENTITY_PROVIDER
# Valeur: Format complet du provider WIF
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID
```

#### 2. Service Account
```bash
# Nom du secret: GCP_SERVICE_ACCOUNT
# Valeur: Email du service account
SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com
```

#### 3. Service Account CI/CD (si différent)
```bash
# Nom du secret: GCP_CICD_SERVICE_ACCOUNT
# Valeur: Email du service account pour CI/CD
cicd-service-account@PROJECT_ID.iam.gserviceaccount.com
```

#### 4. Project ID
```bash
# Nom du secret: GCP_PROJECT_ID
# Valeur: ID du projet Google Cloud
your-project-id
```

#### 5. Database URLs
```bash
# Nom du secret: DATABASE_URL_STAGING
# Valeur: Connexion PostgreSQL staging
postgresql+asyncpg://usernme:password@host:port/database_staging

# Nom du secret: DATABASE_URL_PRODUCTION
# Valeur: Connexion PostgreSQL production
postgresql+asyncpg://username:password@host:port/database_production
```

## 🔧 Vérification de la configuration Workload Identity Federation

### 1. Créer le Workload Identity Pool (si nécessaire)
```bash
gcloud iam workload-identity-pools create "github-pool" \
    --project="YOUR_PROJECT_ID" \
    --location="global" \
    --display-name="GitHub Actions Pool"
```

### 2. Créer le Provider
```bash
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project="YOUR_PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"
```

### 3. Obtenir l'ID complet du provider
```bash
gcloud iam workload-identity-pools providers describe "github-provider" \
    --project="YOUR_PROJECT_ID" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --format="value(name)"
```

### 4. Configurer les permissions du Service Account
```bash
# Permettre au repository GitHub d'utiliser le service account
gcloud iam service-accounts add-iam-policy-binding \
    --project="YOUR_PROJECT_ID" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/sahemac/skillforge-ai-monorepo" \
    SERVICE_ACCOUNT_EMAIL@PROJECT_ID.iam.gserviceaccount.com
```

## 🎯 Points importants

### Audience correcte
L'audience dans le Workload Identity Federation doit correspondre exactement à :
```
https://github.com/sahemac/skillforge-ai-monorepo
```

### Permissions du Service Account
Le service account doit avoir les rôles :
- `roles/run.admin` - Pour déployer sur Cloud Run
- `roles/storage.admin` - Pour accéder à Container Registry/Artifact Registry
- `roles/iam.serviceAccountUser` - Pour utiliser d'autres service accounts
- `roles/cloudsql.client` - Pour accéder à Cloud SQL (si applicable)

### Test de la configuration
```bash
# Tester localement avec gcloud
gcloud auth application-default login
gcloud auth list

# Vérifier les permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

## 🚨 Troubleshooting

### Si l'erreur persiste :
1. **Vérifier le nom du repository** : Doit être exactement `sahemac/skillforge-ai-monorepo`
2. **Vérifier l'ID du projet** : Utiliser l'ID du projet, pas le nom
3. **Régénérer les secrets** : Supprimer et recréer tous les secrets GitHub
4. **Vérifier les rôles IAM** : S'assurer que le service account a les bonnes permissions

### Commandes de diagnostic :
```bash
# Lister les pools Workload Identity
gcloud iam workload-identity-pools list --location="global"

# Vérifier les providers
gcloud iam workload-identity-pools providers list \
    --location="global" \
    --workload-identity-pool="github-pool"

# Tester l'authentification
gcloud auth print-access-token
```

## 📞 Support
Si les erreurs d'authentification persistent après cette configuration :
1. Vérifier que tous les secrets GitHub sont correctement définis
2. S'assurer que le Workload Identity Federation est configuré pour le bon repository
3. Valider que le service account a toutes les permissions requises
4. Contacter l'équipe DevOps si nécessaire

---
**Note** : Ces configurations sont critiques pour la sécurité. Ne jamais partager les secrets ou les configurer dans le code source.