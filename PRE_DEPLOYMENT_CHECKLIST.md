# Checklist Pré-Déploiement - SkillForge AI Microservices

**Date:** 2025-11-07
**Services:** auth-service, company-service, user-service
**Environnement cible:** Staging

---

## Actions à Exécuter AVANT le Déploiement

### 1. Réauthentification GCloud

```bash
# Ouvrir une nouvelle fenêtre de terminal et exécuter:
gcloud auth login

# Vérifier l'authentification
gcloud auth list

# Confirmer le projet
gcloud config get-value project
# Devrait retourner: skillforge-ai-mvp-25
```

### 2. Vérification des Service Accounts

**Service Accounts requis:**
- `auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com`
- `company-service@skillforge-ai-mvp-25.iam.gserviceaccount.com`
- `user-service@skillforge-ai-mvp-25.iam.gserviceaccount.com`

**Commandes de vérification:**

```bash
# Lister tous les service accounts
gcloud iam service-accounts list --project=skillforge-ai-mvp-25

# Si un service account est manquant, le créer:
gcloud iam service-accounts create auth-service \
    --display-name="Auth Service Account" \
    --project=skillforge-ai-mvp-25

gcloud iam service-accounts create company-service \
    --display-name="Company Service Account" \
    --project=skillforge-ai-mvp-25

gcloud iam service-accounts create user-service \
    --display-name="User Service Account" \
    --project=skillforge-ai-mvp-25
```

**Permissions requises pour chaque service account:**

```bash
# Pour chaque service, ajouter les permissions nécessaires
# Exemple pour auth-service (répéter pour company-service et user-service):

# Cloud SQL Client
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Secret Manager Secret Accessor
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Logging Writer
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

# Monitoring Metric Writer
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"

# Cloud Run Invoker (pour communication inter-services)
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
```

### 3. Vérification des Secrets

**Secrets requis:**
- `DATABASE_URL` - URL de connexion PostgreSQL
- `SECRET_KEY` - Clé secrète pour JWT
- `SMTP_PASSWORD` - Mot de passe SMTP pour envoi d'emails

**Commandes de vérification:**

```bash
# Lister tous les secrets
gcloud secrets list --project=skillforge-ai-mvp-25

# Vérifier chaque secret individuellement
gcloud secrets versions access latest --secret="DATABASE_URL" --project=skillforge-ai-mvp-25
gcloud secrets versions access latest --secret="SECRET_KEY" --project=skillforge-ai-mvp-25
gcloud secrets versions access latest --secret="SMTP_PASSWORD" --project=skillforge-ai-mvp-25
```

**Si un secret est manquant, le créer:**

```bash
# Exemple pour DATABASE_URL
echo -n "postgresql+asyncpg://user:password@/dbname?host=/cloudsql/instance" | \
    gcloud secrets create DATABASE_URL \
    --data-file=- \
    --replication-policy="automatic" \
    --project=skillforge-ai-mvp-25

# Exemple pour SECRET_KEY (générer une clé aléatoire sécurisée)
openssl rand -base64 32 | \
    gcloud secrets create SECRET_KEY \
    --data-file=- \
    --replication-policy="automatic" \
    --project=skillforge-ai-mvp-25

# Exemple pour SMTP_PASSWORD
echo -n "votre_mot_de_passe_smtp" | \
    gcloud secrets create SMTP_PASSWORD \
    --data-file=- \
    --replication-policy="automatic" \
    --project=skillforge-ai-mvp-25
```

**Donner accès aux service accounts:**

```bash
# Pour chaque secret et chaque service account
gcloud secrets add-iam-policy-binding DATABASE_URL \
    --member="serviceAccount:auth-service@skillforge-ai-mvp-25.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=skillforge-ai-mvp-25

# Répéter pour company-service et user-service
```

### 4. Vérification de l'Instance Cloud SQL

```bash
# Vérifier que l'instance existe
gcloud sql instances describe skillforge-pg-instance-staging \
    --project=skillforge-ai-mvp-25

# Vérifier les bases de données
gcloud sql databases list \
    --instance=skillforge-pg-instance-staging \
    --project=skillforge-ai-mvp-25

# Vérifier que la base de données 'skillforge_db' existe
# Si elle n'existe pas:
gcloud sql databases create skillforge_db \
    --instance=skillforge-pg-instance-staging \
    --project=skillforge-ai-mvp-25
```

### 5. Vérification des Workflows GitHub Actions

```bash
# Vérifier que les workflows existent
ls -la .github/workflows/deploy-auth-service.yml
ls -la .github/workflows/deploy-company-service.yml
ls -la .github/workflows/deploy-user-service.yml

# Vérifier que le workflow réutilisable existe
ls -la .github/workflows/deploy-service.yml
```

### 6. Vérification des Secrets GitHub

Les secrets suivants doivent être configurés dans GitHub:

```bash
# Via l'interface GitHub ou via CLI:
gh secret list

# Secrets requis:
# - GCP_PROJECT_ID
# - GCP_WIF_PROVIDER
# - GCP_CICD_SERVICE_ACCOUNT
# - DATABASE_URL_STAGING
# - DATABASE_URL_PRODUCTION
# - JWT_SECRET_KEY
# - API_SECRET_KEY
```

**Si manquants, les créer:**

```bash
gh secret set GCP_PROJECT_ID --body "skillforge-ai-mvp-25"
gh secret set GCP_WIF_PROVIDER --body "projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/YOUR_POOL/providers/YOUR_PROVIDER"
# etc...
```

---

## Décision Stratégique: Routes d'Authentification Dupliquées

### Problème Identifié

Le `user-service` contient encore des routes d'authentification:
- `/api/v1/auth/register`
- `/api/v1/auth/login`
- `/api/v1/auth/refresh`
- `/api/v1/auth/logout`

Ces routes font doublon avec l'`auth-service`.

### Options Disponibles

#### Option A: Supprimer les routes d'auth du user-service (RECOMMANDÉ)

**Avantages:**
- Architecture propre et claire
- Un seul service responsable de l'authentification
- Évite les incohérences

**Inconvénients:**
- Breaking change pour les clients existants
- Nécessite migration des clients

**Actions:**
1. Supprimer le fichier `apps/backend/user-service/app/api/v1/endpoints/auth.py`
2. Retirer l'import dans `apps/backend/user-service/app/api/v1/__init__.py`
3. Documenter la migration dans les release notes

#### Option B: Maintenir pour compatibilité ascendante

**Avantages:**
- Pas de breaking change
- Compatibilité avec clients existants

**Inconvénients:**
- Code dupliqué
- Maintenance double
- Risque d'incohérence

**Actions:**
1. Marquer les routes comme dépréciées dans la documentation
2. Ajouter des warnings dans les logs
3. Planifier la suppression dans une version future

#### Option C: Proxy vers auth-service (COMPROMIS)

**Avantages:**
- Compatibilité maintenue
- Pas de duplication de logique
- Migration transparente

**Inconvénients:**
- Latence ajoutée (un hop supplémentaire)
- Complexité de configuration

**Actions:**
1. Modifier les endpoints auth du user-service pour faire des appels HTTP vers auth-service
2. Ajouter gestion d'erreur robuste
3. Documenter le comportement de proxy

### Recommandation Finale

**OPTION A** est recommandée pour une architecture microservices propre et maintenable.

---

## Processus de Déploiement

### Déploiement Automatique via GitHub Actions

**1. Merger vers develop:**

```bash
# Si vous êtes sur feature/monolith-migration
git checkout develop
git merge feature/monolith-migration
git push origin develop
```

Cela déclenchera automatiquement les workflows de déploiement.

**2. Déploiement Manuel via GitHub Interface:**

1. Aller sur https://github.com/sahemac/skillforge-ai-monorepo/actions
2. Sélectionner le workflow (ex: "Deploy - Auth Service")
3. Cliquer sur "Run workflow"
4. Sélectionner la branche (develop)
5. Choisir l'environnement (staging)
6. Cliquer sur "Run workflow"

### Vérifications Post-Déploiement

**1. Vérifier que les services sont déployés:**

```bash
gcloud run services list --project=skillforge-ai-mvp-25 --platform=managed --region=europe-west1
```

**2. Tester les health checks:**

```bash
# Auth Service
curl https://auth-service-skillforge-ai-mvp-25.europe-west1.run.app/health

# Company Service
curl https://company-service-skillforge-ai-mvp-25.europe-west1.run.app/health

# User Service
curl https://user-service-skillforge-ai-mvp-25.europe-west1.run.app/health
```

**3. Vérifier les logs:**

```bash
# Auth Service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=auth-service" \
    --project=skillforge-ai-mvp-25 \
    --limit=50 \
    --format=json

# Company Service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=company-service" \
    --project=skillforge-ai-mvp-25 \
    --limit=50 \
    --format=json

# User Service
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=user-service" \
    --project=skillforge-ai-mvp-25 \
    --limit=50 \
    --format=json
```

**4. Tester un flux complet:**

```bash
# 1. Enregistrer un utilisateur via l'API Gateway
curl -X POST https://YOUR_API_GATEWAY_URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User",
    "user_type": "learner"
  }'

# 2. Se connecter
curl -X POST https://YOUR_API_GATEWAY_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "SecurePassword123!"
  }'

# 3. Utiliser le token pour accéder à un endpoint protégé
curl -X GET https://YOUR_API_GATEWAY_URL/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Rollback en Cas de Problème

Si un déploiement pose problème:

```bash
# Lister les révisions
gcloud run revisions list \
    --service=auth-service \
    --region=europe-west1 \
    --project=skillforge-ai-mvp-25

# Revenir à une révision précédente
gcloud run services update-traffic auth-service \
    --to-revisions=REVISION_NAME=100 \
    --region=europe-west1 \
    --project=skillforge-ai-mvp-25
```

---

## Checklist Finale

- [ ] GCloud authentifié
- [ ] Service accounts vérifiés/créés
- [ ] Permissions des service accounts configurées
- [ ] Secrets vérifiés/créés
- [ ] Permissions des secrets configurées
- [ ] Instance Cloud SQL vérifiée
- [ ] Base de données 'skillforge_db' existe
- [ ] Workflows GitHub existent
- [ ] Secrets GitHub configurés
- [ ] Décision prise sur les routes d'auth dupliquées
- [ ] Tests locaux passés
- [ ] Branche feature/monolith-migration à jour
- [ ] Prêt pour le déploiement

---

## Contact et Support

En cas de problème:
1. Vérifier les logs Cloud Logging
2. Vérifier le statut des services Cloud Run
3. Vérifier les métriques Cloud Monitoring
4. Consulter la documentation: RAPPORT_VALIDATION_MICROSERVICES.md

---

**Document généré le:** 2025-11-07
**Maintenu par:** Équipe DevOps SkillForge AI
