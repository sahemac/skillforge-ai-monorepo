# 🧹 Nettoyage et Configuration des Secrets GitHub

## ⚠️ Secrets en double détectés

### Secrets à GARDER (valeurs correctes) :

| Secret | Valeur |
|--------|--------|
| **GCP_PROJECT_ID** | `skillforge-ai-mvp-25` |
| **GCP_WIF_PROVIDER** | `projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github` |
| **GCP_CICD_SERVICE_ACCOUNT** | Le service account que vous utilisez (format: `name@skillforge-ai-mvp-25.iam.gserviceaccount.com`) |
| **DATABASE_URL_STAGING** | Votre URL PostgreSQL staging |

### Secrets à SUPPRIMER (doublons) :
- ❌ **GCP_WORKLOAD_IDENTITY_PROVIDER** → Supprimer, utiliser GCP_WIF_PROVIDER
- ❌ **WORKLOAD_IDENTITY_PROVIDER** → Supprimer, utiliser GCP_WIF_PROVIDER  
- ❌ **GCP_SERVICE_ACCOUNT** → Supprimer, utiliser GCP_CICD_SERVICE_ACCOUNT

## 📋 Actions à effectuer dans GitHub :

1. **Aller dans** : Settings → Secrets and variables → Actions

2. **Mettre à jour** :
   - **GCP_WIF_PROVIDER** = `projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github`
   - **GCP_PROJECT_ID** = `skillforge-ai-mvp-25`

3. **Supprimer les doublons** :
   - Supprimer GCP_WORKLOAD_IDENTITY_PROVIDER
   - Supprimer WORKLOAD_IDENTITY_PROVIDER
   - Supprimer GCP_SERVICE_ACCOUNT (garder seulement GCP_CICD_SERVICE_ACCOUNT)

## 🔧 Vérification de la configuration

Après nettoyage, vous devez avoir exactement ces 4 secrets :
- ✅ GCP_PROJECT_ID
- ✅ GCP_WIF_PROVIDER
- ✅ GCP_CICD_SERVICE_ACCOUNT
- ✅ DATABASE_URL_STAGING

## 🎯 Test de validation

Après nettoyage, exécuter :
```bash
# Dans GitHub Actions, lancer le workflow
Test - Secrets Configuration
```

Le workflow devrait maintenant s'authentifier correctement avec le bon pool WIF.