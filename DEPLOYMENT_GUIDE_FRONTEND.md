# Guide de Déploiement des Services Frontend SkillForge AI

## Architecture Module Federation

L'architecture micro-frontend utilise Module Federation avec:
- **Shell** (Host): Application principale qui charge les modules remotes
- **Auth** (Remote): Module d'authentification
- **Learner** (Remote): Interface apprenants
- **Company** (Remote): Interface entreprises
- **Admin** (Remote): Interface administration

## Configuration des Services Cloud Run

### URLs des Services Déployés

```bash
# Services Frontend SkillForge AI (déployés)
SHELL_URL="https://skillforge-shell-koi53iwqbq-ew.a.run.app"
AUTH_URL="https://skillforge-auth-koi53iwqbq-ew.a.run.app"
LEARNER_URL="https://skillforge-learner-koi53iwqbq-ew.a.run.app"
COMPANY_URL="https://skillforge-company-koi53iwqbq-ew.a.run.app"
ADMIN_URL="https://skillforge-admin-koi53iwqbq-ew.a.run.app"
```

### Configuration Module Federation

Après déploiement des applications remotes, mettre à jour `apps/frontend/shell/vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        auth: 'https://skillforge-auth-XXXXX-ew.a.run.app/assets/remoteEntry.js',
        learner: 'https://skillforge-learner-XXXXX-ew.a.run.app/assets/remoteEntry.js',
        company: 'https://skillforge-company-XXXXX-ew.a.run.app/assets/remoteEntry.js',
        admin: 'https://skillforge-admin-XXXXX-ew.a.run.app/assets/remoteEntry.js',
      },
      // ... reste de la configuration
    }),
  ],
});
```

## Scripts de Déploiement

### 1. Déploiement avec Cloud Build
```bash
# Déployer une application
./scripts/deploy-frontend-cloudbuild.sh <app-name>

# Exemple
./scripts/deploy-frontend-cloudbuild.sh auth
```

### 2. Déploiement avec Docker Local
```bash
# Nécessite Docker Desktop
./scripts/deploy-frontend-simple.sh <app-name>
```

### 3. Déploiement Complet
```bash
# Tous les services en une fois
./scripts/deploy-frontend-services.sh
```

## Ordre de Déploiement Recommandé

1. **Applications Remotes d'abord** (dans n'importe quel ordre):
   ```bash
   ./scripts/deploy-frontend-cloudbuild.sh auth
   ./scripts/deploy-frontend-cloudbuild.sh learner
   ./scripts/deploy-frontend-cloudbuild.sh company
   ./scripts/deploy-frontend-cloudbuild.sh admin
   ```

2. **Mettre à jour la configuration Shell** avec les vraies URLs

3. **Déployer l'application Shell**:
   ```bash
   ./scripts/deploy-frontend-cloudbuild.sh shell
   ```

## Configuration Cloud Run

### Spécifications par Service

| Service | CPU | Memory | Min/Max Instances | Port |
|---------|-----|--------|-------------------|------|
| shell   | 1   | 512Mi  | 0/10             | 80   |
| auth    | 1   | 512Mi  | 0/10             | 80   |
| learner | 1   | 512Mi  | 0/10             | 80   |
| company | 1   | 512Mi  | 0/10             | 80   |
| admin   | 1   | 512Mi  | 0/10             | 80   |

### Variables d'Environnement

```bash
# Pour shell (host)
NODE_ENV=production
APP_TYPE=shell
MODULE_FEDERATION_HOST=true

# Pour les remotes (auth, learner, company, admin)
NODE_ENV=production
APP_TYPE=<app-name>
MODULE_FEDERATION_REMOTE=true
```

## Configuration Nginx (dans les Dockerfiles)

### CORS pour Module Federation
```nginx
# Configuration CORS pour module federation
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
add_header Access-Control-Allow-Headers "Content-Type, Authorization";

# Gestion spécifique des fichiers de module federation
location /assets/remoteEntry.js {
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, OPTIONS";
    add_header Access-Control-Allow-Headers "Content-Type";
    expires 1h;
    add_header Cache-Control "public, max-age=3600";
}
```

## Load Balancer Integration

### Backend Services
Créer des backend services pour chaque application:

```bash
# Exemple pour auth
gcloud compute network-endpoint-groups create skillforge-auth-backend-neg \
    --region=europe-west1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=skillforge-auth

gcloud compute backend-services create skillforge-auth-backend \
    --global \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --protocol=HTTPS

gcloud compute backend-services add-backend skillforge-auth-backend \
    --global \
    --network-endpoint-group=skillforge-auth-backend-neg \
    --network-endpoint-group-region=europe-west1
```

### Path Matching
Configuration du routage dans le Load Balancer:

```bash
# Shell (application principale)
/*  -> skillforge-shell

# Modules remotes
/auth/*     -> skillforge-auth
/learner/*  -> skillforge-learner
/company/*  -> skillforge-company
/admin/*    -> skillforge-admin
```

## Tests de Connectivité

### Health Checks
```bash
# Test des endpoints health
curl https://skillforge-auth-XXXXX-ew.a.run.app/health
curl https://skillforge-learner-XXXXX-ew.a.run.app/health
curl https://skillforge-company-XXXXX-ew.a.run.app/health
curl https://skillforge-admin-XXXXX-ew.a.run.app/health
curl https://skillforge-shell-XXXXX-ew.a.run.app/health
```

### Test Module Federation
```bash
# Test des remoteEntry.js
curl https://skillforge-auth-XXXXX-ew.a.run.app/assets/remoteEntry.js
curl https://skillforge-learner-XXXXX-ew.a.run.app/assets/remoteEntry.js
curl https://skillforge-company-XXXXX-ew.a.run.app/assets/remoteEntry.js
curl https://skillforge-admin-XXXXX-ew.a.run.app/assets/remoteEntry.js
```

## Procédures de Rollback

### Rollback d'un Service
```bash
# Revenir à la révision précédente
gcloud run services update-traffic skillforge-<app-name> \
    --to-revisions=PREVIOUS=100 \
    --region=europe-west1

# Exemple
gcloud run services update-traffic skillforge-auth \
    --to-revisions=PREVIOUS=100 \
    --region=europe-west1
```

### Rollback Complet
```bash
# Script de rollback pour tous les services
for app in shell auth learner company admin; do
    echo "Rolling back $app..."
    gcloud run services update-traffic "skillforge-$app" \
        --to-revisions=PREVIOUS=100 \
        --region=europe-west1
done
```

## Monitoring et Logs

### Logs Cloud Run
```bash
# Voir les logs d'un service
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=skillforge-auth" \
    --limit=50 \
    --format="table(timestamp,textPayload)"
```

### Métriques
- Latency des requêtes
- Nombre d'instances actives
- Utilisation CPU/Memory
- Erreurs 4xx/5xx

## URLs de Production

Services déployés avec succès:

```bash
# Services Frontend SkillForge AI - DÉPLOYÉS
export SKILLFORGE_SHELL_URL="https://skillforge-shell-koi53iwqbq-ew.a.run.app"
export SKILLFORGE_AUTH_URL="https://skillforge-auth-koi53iwqbq-ew.a.run.app"
export SKILLFORGE_LEARNER_URL="https://skillforge-learner-koi53iwqbq-ew.a.run.app"
export SKILLFORGE_COMPANY_URL="https://skillforge-company-koi53iwqbq-ew.a.run.app"
export SKILLFORGE_ADMIN_URL="https://skillforge-admin-koi53iwqbq-ew.a.run.app"

# Module Federation Remote URLs - CONFIGURÉS
export AUTH_REMOTE_ENTRY="$SKILLFORGE_AUTH_URL/assets/remoteEntry.js"
export LEARNER_REMOTE_ENTRY="$SKILLFORGE_LEARNER_URL/assets/remoteEntry.js"
export COMPANY_REMOTE_ENTRY="$SKILLFORGE_COMPANY_URL/assets/remoteEntry.js"
export ADMIN_REMOTE_ENTRY="$SKILLFORGE_ADMIN_URL/assets/remoteEntry.js"
```

## Troubleshooting

### Problèmes Courants

1. **Erreur CORS**: Vérifier la configuration nginx dans les Dockerfiles
2. **Module non trouvé**: Vérifier les URLs des remoteEntry.js
3. **Build échoué**: Vérifier les permissions Cloud Build
4. **Service non accessible**: Vérifier les paramètres Cloud Run

### Debug Commands
```bash
# Vérifier le statut des services
gcloud run services list --region=europe-west1

# Vérifier les révisions
gcloud run revisions list --service=skillforge-auth --region=europe-west1

# Vérifier les logs de build
gcloud builds list --limit=10
```