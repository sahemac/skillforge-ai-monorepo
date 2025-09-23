# 🔐 Guide de Sécurisation des Credentials Grafana

**Date**: 2025-01-23  
**Auteur**: Configuration automatisée  
**Statut**: Critical Security Fix  

---

## 🚨 PROBLÈME IDENTIFIÉ

Le fichier `grafana-sa-key.json` contenait un token OAuth temporaire qui a été exposé publiquement sur GitHub. Cette situation compromise la sécurité du projet.

### Risques identifiés :
- ✅ **Token OAuth exposé** - Maintenant invalidé et remplacé
- ✅ **Credentials temporaires** - Remplacés par un template sécurisé
- ✅ **Accès non autorisé** - Mitigé par la régénération des clés

---

## 🛠️ SOLUTION IMPLÉMENTÉE

### 1. Configuration .gitignore renforcée

Le fichier `.gitignore` a été mis à jour avec des patterns robustes :

```gitignore
# CRITICAL: Service Account Keys and OAuth Tokens - NEVER commit these
**/*-sa-key.json
**/service-account-key.json
**/grafana-sa-key.json
**/grafana-oauth-token.txt
**/*-oauth-token.txt
**/*-service-account.json
*.pem
*.p12
*.pfx
gcp-key.json
google-credentials.json

# CRITICAL: Terraform backup files - NEVER commit these
terraform.tfstate
terraform.tfstate.backup
*.tfvars
.terraform/
.terraform.lock.hcl

# CRITICAL: Database credentials and connection strings
.env.local
.env.production
.env.staging
.env.development
DATABASE_URL
POSTGRES_PASSWORD
POSTGRES_USER
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
DB_PASSWORD
DB_USER
DB_HOST
DB_PORT
DB_NAME
CONNECTION_STRING
```

### 2. Template de Service Account sécurisé

Le fichier `grafana-sa-key.json` a été remplacé par un template avec instructions :

```json
{
  "_comment": "TEMPLATE - Ce fichier doit être remplacé par un vrai service account",
  "_instructions": [
    "1. Exécutez: ./scripts/setup-grafana-service-account.sh",
    "2. Ou créez manuellement un service account avec les permissions monitoring.viewer",
    "3. Ce fichier sera automatiquement généré avec les bonnes credentials"
  ],
  "_required_permissions": [
    "roles/monitoring.viewer",
    "roles/monitoring.metricWriter", 
    "roles/logging.viewer"
  ]
}
```

### 3. Script automatisé de configuration

Le script `./scripts/setup-grafana-service-account.sh` permet de :
- Créer un nouveau service account avec permissions minimales
- Générer une clé JSON sécurisée
- Configurer automatiquement Grafana
- Sauvegarder l'ancienne configuration

---

## 📋 ÉTAPES DE RÉCUPÉRATION

### Étape 1: Exécuter le script de configuration

```bash
# Naviguer vers le répertoire racine du projet
cd /path/to/skillforge-ai-monorepo

# Exécuter le script de configuration
./scripts/setup-grafana-service-account.sh
```

### Étape 2: Vérifier la configuration Grafana

1. **Connexion à Grafana Cloud** : https://sahemac.grafana.net
2. **Configuration > Data Sources**
3. **Modifiez "Google Cloud Monitoring"**
4. **Authentification** : "Google JWT File" 
5. **Uploadez** le nouveau fichier `monitoring/grafana/grafana-sa-key.json`
6. **Testez** la connexion

### Étape 3: Valider le monitoring

```bash
# Vérifier que le fichier est généré
ls -la monitoring/grafana/grafana-sa-key.json

# Vérifier que le service account existe
gcloud iam service-accounts describe grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com

# Vérifier les permissions
gcloud projects get-iam-policy skillforge-ai-mvp-25 \
  --flatten="bindings[].members" \
  --filter="bindings.members:grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com"
```

---

## 🔒 BONNES PRATIQUES DE SÉCURITÉ

### 1. Gestion des credentials

- ✅ **Jamais de credentials dans Git** - Utilisez `.gitignore` et variables d'environnement
- ✅ **Rotation régulière** - Renouvelez les clés tous les 90 jours
- ✅ **Permissions minimales** - Accordez uniquement les rôles nécessaires
- ✅ **Monitoring des accès** - Surveillez l'utilisation des service accounts

### 2. Configuration locale

```bash
# Variables d'environnement pour développement local
export GOOGLE_APPLICATION_CREDENTIALS="./monitoring/grafana/grafana-sa-key.json"
export GCP_PROJECT_ID="skillforge-ai-mvp-25"

# Pour les scripts de déploiement
export GRAFANA_SA_KEY_PATH="./monitoring/grafana/grafana-sa-key.json"
```

### 3. Alternative avec Workload Identity

Pour une sécurité renforcée en production, considérez l'utilisation de Workload Identity :

```yaml
# kubernetes/grafana-workload-identity.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    iam.gke.io/gcp-service-account: grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com
  name: grafana-monitoring
  namespace: monitoring
```

---

## 🚨 ALERTES DE SÉCURITÉ

### Surveillance des credentials

Ajoutez ces alertes dans Grafana pour surveiller l'utilisation des service accounts :

```yaml
# Alert: Service Account Key Usage
- alert: UnauthorizedServiceAccountUsage
  expr: increase(gcp_iam_service_account_key_usage_total[5m]) > 100
  labels:
    severity: warning
    component: security
  annotations:
    summary: "Utilisation anormalement élevée du service account Grafana"

# Alert: Failed Authentication Attempts  
- alert: GrafanaAuthFailures
  expr: increase(grafana_api_auth_failures_total[5m]) > 10
  labels:
    severity: critical
    component: security
  annotations:
    summary: "Échecs d'authentification répétés sur Grafana"
```

---

## 📝 CHECKLIST DE VALIDATION

- [ ] Script `setup-grafana-service-account.sh` exécuté avec succès
- [ ] Nouveau fichier `grafana-sa-key.json` généré avec de vraies credentials
- [ ] Grafana Cloud connecté avec le nouveau service account
- [ ] Data sources Google Cloud Monitoring et Logging fonctionnels
- [ ] Dashboards affichent les métriques correctement
- [ ] Alertes configurées et fonctionnelles
- [ ] Ancien token OAuth révoqué dans Google Cloud Console
- [ ] Git ne tracke plus les fichiers de credentials sensibles

---

## 🔄 MAINTENANCE CONTINUE

### Rotation des clés (tous les 90 jours)

```bash
# Script de rotation à exécuter trimestriellement
./scripts/rotate-grafana-credentials.sh

# Ou manuellement :
# 1. Générer nouvelle clé
gcloud iam service-accounts keys create new-grafana-sa-key.json \
  --iam-account=grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com

# 2. Mettre à jour Grafana
# 3. Supprimer ancienne clé
gcloud iam service-accounts keys delete OLD_KEY_ID \
  --iam-account=grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

### Audit de sécurité

```bash
# Vérifier les permissions du service account
gcloud iam service-accounts get-iam-policy \
  grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com

# Lister toutes les clés actives
gcloud iam service-accounts keys list \
  --iam-account=grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com

# Vérifier les logs d'accès
gcloud logging read "protoPayload.serviceName=iam.googleapis.com AND protoPayload.resourceName:grafana-monitoring" \
  --limit=50 --format=json
```

---

**IMPORTANT** : Ce guide de sécurité doit être suivi à la lettre pour garantir l'intégrité du système de monitoring. Toute déviation de ces procédures doit être documentée et approuvée.

**Contact** : sah@emacsah.com pour questions de sécurité urgentes.