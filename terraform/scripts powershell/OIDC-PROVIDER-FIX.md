# 🔧 Correction Provider OIDC - Workload Identity

## 🚨 Problème Identifié

L'erreur `INVALID_ARGUMENT: The attribute condition must reference one of the provider's claims` indique un problème dans la configuration de l'attribute mapping du Provider OIDC.

## ⚡ Solution Rapide

### Option 1: Script de Correction Automatique

```powershell
# Utilisez votre vrai nom d'utilisateur GitHub
.\fix-oidc-provider.ps1 -RepoName "VOTRE-USERNAME/skillforge-ai-monorepo"
```

### Option 2: Correction Manuelle

#### 1. Supprimer le Provider défectueux

```powershell
gcloud iam workload-identity-pools providers delete "github" `
    --project="skillforge-ai-mvp-25" `
    --location="global" `
    --workload-identity-pool="github-actions" `
    --quiet
```

#### 2. Créer le Provider avec la bonne configuration

```powershell
gcloud iam workload-identity-pools providers create-oidc "github" `
    --project="skillforge-ai-mvp-25" `
    --location="global" `
    --workload-identity-pool="github-actions" `
    --display-name="GitHub Actions Provider" `
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor,attribute.ref=assertion.ref" `
    --issuer-uri="https://token.actions.githubusercontent.com" `
    --quiet
```

#### 3. Reconfigurer l'autorisation

```powershell
# Remplacez VOTRE-USERNAME par votre nom d'utilisateur GitHub réel
$repoName = "VOTRE-USERNAME/skillforge-ai-monorepo"
$serviceAccount = "terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com"
$projectNumber = "584748485117"

gcloud iam service-accounts add-iam-policy-binding `
    --project="skillforge-ai-mvp-25" `
    --role="roles/iam.workloadIdentityUser" `
    --member="principalSet://iam.googleapis.com/projects/$projectNumber/locations/global/workloadIdentityPools/github-actions/attribute.repository/$repoName" `
    $serviceAccount
```

## 🔍 Vérification

Testez la configuration :

```powershell
# Vérifier le Provider OIDC
gcloud iam workload-identity-pools providers describe "github" `
    --project="skillforge-ai-mvp-25" `
    --location="global" `
    --workload-identity-pool="github-actions"

# Vérifier les autorisations du Service Account
gcloud iam service-accounts get-iam-policy `
    terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

## 🎯 Valeurs Finales pour GitHub

Une fois corrigé, utilisez ces valeurs dans GitHub Repository Secrets :

```yaml
GCP_WORKLOAD_IDENTITY_PROVIDER: projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github
GCP_SERVICE_ACCOUNT: terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

## 🚀 Test du Pipeline

1. **Ajoutez les secrets dans GitHub**
2. **Testez localement** :
   ```powershell
   .\test-pipeline-local.ps1 -Environment staging
   ```
3. **Créez une PR** avec un changement dans `/terraform/` pour tester l'authentification

## 📋 Commandes de Diagnostic

Si vous rencontrez encore des problèmes :

```powershell
# Lister tous les providers
gcloud iam workload-identity-pools providers list `
    --workload-identity-pool="github-actions" `
    --location="global" `
    --project="skillforge-ai-mvp-25"

# Vérifier l'état du pool
gcloud iam workload-identity-pools describe "github-actions" `
    --location="global" `
    --project="skillforge-ai-mvp-25"

# Lister les service accounts
gcloud iam service-accounts list --project="skillforge-ai-mvp-25"
```

## 🎉 Résultat Attendu

Après correction, vous devriez voir :
- ✅ Provider OIDC créé sans erreur
- ✅ Autorisation du repository configurée  
- ✅ Pipeline GitHub Actions fonctionnel avec authentification GCP

---

**💡 Astuce** : Le script `fix-oidc-provider.ps1` fait tout automatiquement et inclut des configurations de fallback en cas d'erreur.