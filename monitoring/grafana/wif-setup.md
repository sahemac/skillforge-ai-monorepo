# 🔐 Grafana Workload Identity Federation Setup

**Date**: 2025-01-23  
**Auteur**: Kouemou Sah Jean Emac  
**Objectif**: Configurer Grafana sans clés JSON

---

## 🎯 SOLUTION WIF POUR GRAFANA

### **Problème Actuel**
```yaml
Erreur: Key creation is not allowed on this service account
Contrainte: constraints/iam.disableServiceAccountKeyCreation
Solution: Workload Identity Federation (WIF)
```

### **Configuration WIF pour Grafana Cloud**

#### **1. Créer Workload Identity Pool**
```bash
# Créer le pool d'identité
gcloud iam workload-identity-pools create grafana-pool \
    --location="global" \
    --description="Workload Identity Pool for Grafana" \
    --display-name="Grafana WIF Pool" \
    --project=skillforge-ai-mvp-25

# Créer le provider pour Grafana Cloud
gcloud iam workload-identity-pools providers create-oidc grafana-provider \
    --location="global" \
    --workload-identity-pool="grafana-pool" \
    --issuer-uri="https://grafana.com" \
    --allowed-audiences="grafana.com" \
    --attribute-mapping="google.subject=assertion.sub" \
    --project=skillforge-ai-mvp-25
```

#### **2. Lier Service Account à WIF**
```bash
# Permettre au service account d'être utilisé via WIF
gcloud iam service-accounts add-iam-policy-binding \
    --role roles/iam.workloadIdentityUser \
    --member "principalSet://iam.googleapis.com/projects/584748485117/locations/global/workloadIdentityPools/grafana-pool/*" \
    grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

#### **3. Configuration dans Grafana Cloud**
```yaml
# Informations pour Grafana Cloud Data Source
Type: Google Cloud Monitoring
Authentication Method: Workload Identity Federation
Project ID: skillforge-ai-mvp-25
Pool ID: projects/584748485117/locations/global/workloadIdentityPools/grafana-pool/providers/grafana-provider
Service Account Email: grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com
```

---

## 🚀 CONFIGURATION ALTERNATIVE - SOLUTION IMMÉDIATE

### **Option 1: Utiliser votre compte personnel**
```yaml
# Pour démarrage rapide, utiliser votre compte Google
Account: sah@emacsah.com
Permissions: Owner (déjà configuré)
Limitation: Pas optimal pour production
```

### **Option 2: API Key temporaire (si autorisée)**
```bash
# Demander à l'admin d'autoriser temporairement
gcloud organizations policies list --filter="constraint:constraints/iam.disableServiceAccountKeyCreation"
# Puis créer la clé manuellement via Console
```

---

## 📊 ÉTAT ACTUEL DU MONITORING

### **Service Account créé ✅**
```yaml
Email: grafana-monitoring@skillforge-ai-mvp-25.iam.gserviceaccount.com
Roles:
  - roles/monitoring.viewer ✅
  - roles/logging.viewer ✅
Status: Fonctionnel mais sans clé JSON
```

### **Métriques disponibles**
```yaml
Cloud Run Metrics:
  - CPU/Memory utilization: ✅ Disponible
  - Request count/latency: ✅ Disponible
  - Error rates: ✅ Disponible

Load Balancer Metrics:
  - Request volume: ✅ Disponible  
  - Backend health: ✅ Disponible
  - SSL status: ✅ Disponible

Database Metrics:
  - Connection count: ✅ Disponible
  - Query performance: ✅ Disponible
```

---

## 🔧 CONFIGURATION ÉTAPE PAR ÉTAPE

### **Étape 1: Test de connectivité (Immédiat)**
```bash
# Tester l'accès aux métriques avec votre compte
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=5 --project=skillforge-ai-mvp-25

gcloud monitoring metrics list \
  --filter="resource.type=cloud_run_revision" \
  --project=skillforge-ai-mvp-25
```

### **Étape 2: Configuration Grafana Cloud**
1. **Se connecter à https://sahemac.grafana.net**
2. **Aller dans Configuration > Data Sources**
3. **Ajouter Google Cloud Monitoring:**
   ```yaml
   Authentication: Service Account Key
   Project: skillforge-ai-mvp-25
   Key File: [Upload temporaire avec votre clé personnelle]
   ```

### **Étape 3: Dashboards de base**
```yaml
Dashboards à importer:
  - Google Cloud Platform Overview (ID: 1860)
  - Cloud Run Monitoring (ID: 13865)
  - PostgreSQL Database (ID: 9628)
```

### **Étape 4: Alertes critiques**
```yaml
Alertes à configurer:
  - Service down (Health check failures)
  - High error rate (>5% for 2 minutes)
  - High latency (P95 > 1s for 5 minutes)
  - Resource exhaustion (CPU/Memory > 85%)
```

---

## 🧪 TESTS DE VALIDATION

### **1. Test des métriques**
```bash
# Vérifier les métriques Cloud Run
gcloud monitoring metrics list \
  --filter="metric.type:run.googleapis.com" \
  --project=skillforge-ai-mvp-25

# Vérifier les logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=3 --project=skillforge-ai-mvp-25
```

### **2. Test de l'accès Grafana**
```url
Grafana Cloud: https://sahemac.grafana.net
Test Query: rate(run_googleapis_com_request_count[5m])
Expected: Graphique avec données Cloud Run
```

---

## ⚡ SOLUTION IMMÉDIATE RECOMMANDÉE

### **Pour débloquer rapidement:**

1. **Utiliser votre compte Google personnel** dans Grafana Cloud temporairement
2. **Configurer les dashboards essentiels** 
3. **Mettre en place les alertes critiques**
4. **Migrer vers WIF** plus tard quand vous aurez le temps

### **Commandes à exécuter maintenant:**
```bash
# 1. Tester l'accès aux données
gcloud auth application-default login
gcloud monitoring metrics list --limit=5 --project=skillforge-ai-mvp-25

# 2. Vérifier les logs Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=user-service-staging" --limit=5 --project=skillforge-ai-mvp-25

# 3. Accéder à Grafana Cloud
echo "Aller sur https://sahemac.grafana.net"
echo "Configurer Data Source avec votre compte Google"
```

---

**Auteur**: Kouemou Sah Jean Emac  
**Date**: 2025-01-23  
**Status**: Solution WIF + Alternative immédiate  
**Prochaine étape**: Configuration Grafana Cloud manuelle