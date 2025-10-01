# Solution complète pour corriger l'erreur 404 sur api.emacsah.com

## Problème diagnostiqué

L'erreur 404 sur api.emacsah.com était causée par **deux problèmes distincts** :

1. **Authentification GCP cassée** dans les workflows GitHub Actions
2. **Configuration Load Balancer incorrecte** pointant vers le mauvais service

## Solutions implémentées ✅

### 1. Correction de l'authentification GCP Workload Identity Federation

**Problème** : Audience mismatch dans tous les workflows
```
ERROR: The audience in ID Token [https://github.com/sahemac] does not match the expected audience https://github.com/sahemac/skillforge-ai-monorepo
```

**Solution appliquée** :
- ✅ Corrigé l'audience dans `deploy-service.yml` (5 occurrences)
- ✅ Corrigé l'audience dans `frontend-deploy.yml` (2 occurrences)
- ✅ Corrigé l'audience dans `run-alembic-migration.yml` (1 occurrence)
- ✅ Corrigé l'audience dans `run-python-tests.yml` (1 occurrence)

**Nouvelle audience** : `https://github.com/sahemac/skillforge-ai-monorepo`

### 2. Correction du repository Docker

**Problème** : Repository inexistant
```
ERROR: name unknown: Repository "skillforge-ai-registry" not found
```

**Solution appliquée** :
- ✅ Changé `REPOSITORY: skillforge-ai-registry` → `REPOSITORY: skillforge-docker-repo-staging`
- ✅ Correspond aux repositories utilisés dans les cloudbuild.yaml individuels

### 3. Déploiement réussi du user-service

**Résultat** :
- ✅ Authentification GCP fonctionne
- ✅ Build Docker réussit (1m40s)
- ✅ Déploiement Cloud Run completé
- ✅ Service `staging-user-service` déployé

## Action finale requise 🔧

### Corriger la configuration du Load Balancer

Le service est déployé mais le load balancer pointe encore vers le mauvais service par défaut.

**Commande à exécuter** (avec authentification GCP) :
```bash
gcloud compute url-maps import skillforge-urlmap-staging \
    --source=skillforge-urlmap-fixed.yaml \
    --global \
    --quiet
```

**Ou utiliser le script** :
```bash
./fix-api-domain.sh
```

### Configuration Load Balancer

**Avant** (`skillforge-urlmap-updated.yaml`) :
- `defaultService` = `skillforge-shell-backend-staging` ❌
- `api.emacsah.com/` → va vers Shell service (404)

**Après** (`skillforge-urlmap-fixed.yaml`) :
- `defaultService` = `user-service-backend-staging` ✅
- `api.emacsah.com/` → va vers User service (page de connexion)

## Architecture confirmée

- **skillforge-ai.emacsah.com** → Frontend (utilisateurs & compagnies)
- **api.emacsah.com** → Backend (administrateurs système)

## Fichiers créés/modifiés

### Pages et scripts
- ✅ `apps/backend/user-service/static/login.html` - Interface de connexion admin
- ✅ `skillforge-urlmap-fixed.yaml` - Configuration load balancer corrigée
- ✅ `fix-api-domain.sh` - Script d'application de la correction

### Workflows corrigés
- ✅ `.github/workflows/deploy-service.yml`
- ✅ `.github/workflows/frontend-deploy.yml`
- ✅ `.github/workflows/run-alembic-migration.yml`
- ✅ `.github/workflows/run-python-tests.yml`

## Test final après correction load balancer

Une fois la commande `gcloud compute url-maps import` exécutée :

```bash
# Devrait montrer la page de connexion au lieu de 404
curl -I https://api.emacsah.com/

# Devrait montrer les endpoints API
curl -I https://api.emacsah.com/health
curl -I https://api.emacsah.com/api/v1/docs
```

## Commits liés

1. `3dff082` - Configuration load balancer fixée
2. `6324840` - Correction authentification GCP
3. `24a105a` - Correction repository Docker

La solution est **99% complète** - il ne reste que l'application de la configuration load balancer.