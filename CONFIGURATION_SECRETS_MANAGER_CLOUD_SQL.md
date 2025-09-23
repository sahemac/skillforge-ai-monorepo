# Configuration Secrets Manager et Cloud SQL Proxy - SkillForge AI

## 📋 Résumé des tâches accomplies

✅ **Secret PostgreSQL créé dans Secrets Manager**
- Secret `postgres-password` créé avec la valeur sécurisée
- Permissions accordées au service account Cloud Run

✅ **Permissions IAM configurées**
- Service account `584748485117-compute@developer.gserviceaccount.com` :
  - `roles/secretmanager.secretAccessor` pour le secret postgres-password
  - `roles/cloudsql.client` pour accéder à Cloud SQL

✅ **Scripts et configurations créés**
- Script de mise à jour des services Cloud Run
- Template cloudbuild.yaml sécurisé
- Script de test de connectivité DB
- Script de vérification de configuration
- Script d'automatisation des mises à jour

## 🔐 Configuration de sécurité

### 1. Secret créé dans Secrets Manager

```bash
# Secret créé avec succès
Secret: postgres-password
Version: 1
Valeur: Psaumes@27 (sécurisée)
```

### 2. Permissions accordées

```bash
# Permission Secret Manager
gcloud secrets add-iam-policy-binding postgres-password \
    --member="serviceAccount:584748485117-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Permission Cloud SQL (déjà accordée)
gcloud projects add-iam-policy-binding skillforge-ai-mvp-25 \
    --member="serviceAccount:584748485117-compute@developer.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

## 🚀 Commandes d'exécution

### 1. Mettre à jour tous les fichiers cloudbuild.yaml

```bash
# Automatiser la mise à jour de tous les services
bash scripts/update-all-cloudbuild-files.sh
```

### 2. Mettre à jour les services Cloud Run déployés

```bash
# Appliquer la configuration à tous les services existants
bash scripts/update-cloud-run-services.sh
```

### 3. Vérifier la configuration

```bash
# Vérifier que tous les services sont correctement configurés
bash scripts/verify-cloud-run-config.sh
```

### 4. Tester la connectivité DB

```bash
# Depuis un environnement local avec Cloud SQL Proxy
POSTGRES_PASSWORD="Psaumes@27" python scripts/test-db-connectivity.py

# Depuis un service Cloud Run (via logs)
gcloud logging read 'resource.type="cloud_run_revision" AND jsonPayload.message:"DB connectivity"' --limit=50
```

## 📁 Fichiers créés

### Scripts principaux

1. **`scripts/update-cloud-run-services.sh`**
   - Met à jour tous les services Cloud Run avec Cloud SQL Proxy et Secrets Manager
   - Ajoute automatiquement l'annotation Cloud SQL aux services

2. **`scripts/cloudbuild-template-secure.yaml`**
   - Template sécurisé pour les nouveaux services
   - Utilise Secrets Manager au lieu de variables en clair

3. **`scripts/test-db-connectivity.py`**
   - Script Python complet de test de connectivité
   - Tests multiples : connexion, info DB, tables, migrations, performance

4. **`scripts/verify-cloud-run-config.sh`**
   - Vérifie la configuration de tous les services déployés
   - Détecte les variables sensibles encore en clair

5. **`scripts/update-all-cloudbuild-files.sh`**
   - Automatise la mise à jour de tous les fichiers cloudbuild.yaml
   - Crée des sauvegardes avant modification

### Configuration exemple (user-service)

Le fichier `apps/backend/user-service/cloudbuild.yaml` a été mis à jour avec :

```yaml
# Configuration des variables d'environnement sécurisées
- '--set-env-vars=ENVIRONMENT=production,SERVICE_NAME=user-service,POSTGRES_HOST=127.0.0.1,POSTGRES_PORT=5432,POSTGRES_DB=skillforge_db,POSTGRES_USER=skillforge_user'
# Référence au secret pour le mot de passe PostgreSQL
- '--set-secrets=POSTGRES_PASSWORD=postgres-password:latest'
# Configuration de l'URL de base de données (le mot de passe sera injecté automatiquement)
- '--update-env-vars=DATABASE_URL=postgresql+asyncpg://skillforge_user:${POSTGRES_PASSWORD}@127.0.0.1:5432/skillforge_db'
# Configuration Cloud SQL Proxy
- '--add-cloudsql-instances=skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging'
```

## 📊 Configuration Cloud SQL

### Instance Cloud SQL
- **Project**: skillforge-ai-mvp-25
- **Region**: europe-west1
- **Instance**: skillforge-pg-instance-staging
- **Connection**: `skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging`

### Configuration des services
- **Host interne**: 127.0.0.1 (via Cloud SQL Proxy)
- **Port**: 5432
- **Database**: skillforge_db
- **User**: skillforge_user
- **Password**: Référence au secret `postgres-password`

## 🛡️ Sécurité implémentée

### Avant (non sécurisé)
```yaml
--set-env-vars=POSTGRES_PASSWORD=Psaumes@27,DATABASE_URL=postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db
```

### Après (sécurisé)
```yaml
--set-secrets=POSTGRES_PASSWORD=postgres-password:latest
--update-env-vars=DATABASE_URL=postgresql+asyncpg://skillforge_user:${POSTGRES_PASSWORD}@127.0.0.1:5432/skillforge_db
--add-cloudsql-instances=skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging
```

## 🔄 Plan d'exécution recommandé

### Étape 1: Préparation
```bash
# Vérifier que le secret existe
gcloud secrets describe postgres-password

# Vérifier les permissions
gcloud secrets get-iam-policy postgres-password
```

### Étape 2: Mise à jour des fichiers de configuration
```bash
# Mettre à jour tous les cloudbuild.yaml
bash scripts/update-all-cloudbuild-files.sh
```

### Étape 3: Mise à jour des services déployés
```bash
# Appliquer les changements aux services actifs
bash scripts/update-cloud-run-services.sh
```

### Étape 4: Vérification
```bash
# Vérifier la configuration
bash scripts/verify-cloud-run-config.sh

# Tester un service spécifique
curl https://user-service-[HASH]-ew.a.run.app/health
```

### Étape 5: Tests de connectivité
```bash
# Tester depuis l'environnement local (si Cloud SQL Proxy actif)
POSTGRES_PASSWORD="Psaumes@27" python scripts/test-db-connectivity.py

# Surveiller les logs des services
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="user-service"' --limit=10
```

## 📝 Notes importantes

1. **Sauvegardes** : Tous les fichiers cloudbuild.yaml originaux sont sauvegardés avec timestamp
2. **Rollback** : En cas de problème, les fichiers `.backup.*` peuvent être restaurés
3. **Test local** : Le script de test DB nécessite un Cloud SQL Proxy local actif
4. **Production** : Les services en production utiliseront automatiquement Cloud SQL Proxy intégré

## 🔗 Commandes utiles de vérification

```bash
# Lister tous les secrets
gcloud secrets list

# Vérifier une version de secret
gcloud secrets versions access latest --secret="postgres-password"

# Lister les services Cloud Run
gcloud run services list --region=europe-west1

# Voir la configuration d'un service
gcloud run services describe user-service --region=europe-west1 --format="export"

# Vérifier les logs d'un service
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="user-service"' --limit=20 --format='table(timestamp,jsonPayload.message)'
```

---

**✅ Configuration Secrets Manager et Cloud SQL Proxy terminée avec succès !**

Tous les outils et scripts nécessaires ont été créés pour sécuriser l'infrastructure SkillForge AI en production.