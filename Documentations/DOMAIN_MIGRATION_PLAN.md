# 🚀 Plan de Migration Domaine - ZÉRO Interruption

*Généré le: 2025-01-23*  
*Objectif: Ajouter skillforge-ai.emacsah.com sans impact sur api.emacsah.com*

---

## 📊 Résumé des Impacts

### ✅ **AUCUN IMPACT NÉGATIF sur l'existant**
- **api.emacsah.com** continue de fonctionner **EXACTEMENT** pareil
- **user-service** : Aucune modification de code requise
- **Base de données** : Aucun changement
- **Infrastructure GCP** : Réutilise tout l'existant

### ➕ **IMPACTS POSITIFS uniquement**
- Nouveau domaine **skillforge-ai.emacsah.com** disponible
- Séparation claire frontend/backend
- Architecture scalable pour futurs services

---

## 🔧 Modifications Requises (MINIMALES)

### **1. Terraform Variables** (SEULE modification infrastructure)

**Fichier**: `terraform/environments/staging/terraform.tfvars`

```hcl
# AVANT
ssl_certificate_domains = [
  "api.emacsah.com"
]

# APRÈS  
ssl_certificate_domains = [
  "api.emacsah.com",
  "skillforge-ai.emacsah.com"
]
```

### **2. Backend CORS** (Variable d'environnement)

**Cloud Run Service** : Ajouter dans les variables d'environnement

```bash
# AVANT
BACKEND_CORS_ORIGINS=["https://api.emacsah.com"]

# APRÈS
BACKEND_CORS_ORIGINS=["https://api.emacsah.com", "https://skillforge-ai.emacsah.com"]
```

### **3. DNS Record** (Automatique via Terraform)

Le record DNS sera créé automatiquement lors du `terraform apply`.

---

## 📋 Plan d'Exécution par Phases

### **Phase 1 : Préparation (5 minutes)**
```bash
# 1. Backup de la configuration actuelle
cd terraform/environments/staging
cp terraform.tfvars terraform.tfvars.backup

# 2. Modification du fichier terraform.tfvars
# Ajouter "skillforge-ai.emacsah.com" dans ssl_certificate_domains
```

### **Phase 2 : Terraform Plan (2 minutes)**
```bash
# 3. Vérifier les changements
terraform plan -var-file=terraform.tfvars

# Résultat attendu :
# + DNS record pour skillforge-ai.emacsah.com
# ~ SSL certificate (modification pour ajouter domaine)
# ~ URL Map (ajout host rule)
```

### **Phase 3 : Application (10-15 minutes)**
```bash
# 4. Appliquer les changements
terraform apply -var-file=terraform.tfvars

# ⚠️ Durant cette phase :
# - api.emacsah.com reste 100% fonctionnel
# - Certificat SSL se renouvelle (quelques minutes)
# - DNS se propage (immédiat)
```

### **Phase 4 : Validation (5 minutes)**
```bash
# 5. Tester les deux domaines
curl https://api.emacsah.com/health
curl https://skillforge-ai.emacsah.com (404 attendu - normal)

# 6. Vérifier certificat SSL
openssl s_client -connect skillforge-ai.emacsah.com:443 -servername skillforge-ai.emacsah.com
```

### **Phase 5 : Configuration Backend (2 minutes)**
```bash
# 7. Mettre à jour CORS dans Cloud Run
gcloud run services update user-service-staging \
  --region=europe-west1 \
  --set-env-vars="BACKEND_CORS_ORIGINS=[\"https://api.emacsah.com\", \"https://skillforge-ai.emacsah.com\"]"
```

---

## ⚠️ Points d'Attention

### **Temps d'Arrêt**
- **API Backend** : **0 seconde** d'interruption
- **SSL Certificate** : Renouvellement transparent (~5 minutes)
- **DNS Propagation** : Immédiat (record A simple)

### **Rollback**
Si problème détecté :
```bash
# Retour arrière immédiat
cp terraform.tfvars.backup terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### **Monitoring**
Surveiller pendant la migration :
- **api.emacsah.com/health** : Doit rester accessible
- **Logs Cloud Run** : Vérifier aucune erreur CORS
- **Certificat SSL** : Vérification auto GCP

---

## 🎯 Architecture Finale

```
IP 34.149.174.205 (skillforge-global-ip)
├── api.emacsah.com/*
│   └── user-service (Cloud Run) ✅ EXISTANT
│       ├── /api/v1/auth/*
│       ├── /api/v1/users/*
│       └── /health
│
└── skillforge-ai.emacsah.com/* ⭐ NOUVEAU
    └── [Frontend à déployer]
        ├── / → Landing page
        ├── /auth/* → Micro-frontend auth
        ├── /learner/* → Micro-frontend learner
        ├── /company/* → Micro-frontend company
        └── /admin/* → Micro-frontend admin
```

---

## ✅ Validation Post-Migration

### **Tests Automatiques**
```bash
# Backend API (doit fonctionner)
curl -f https://api.emacsah.com/health || echo "❌ API FAILED"

# Frontend domain (404 attendu jusqu'au déploiement frontend)
curl -s -o /dev/null -w "%{http_code}" https://skillforge-ai.emacsah.com
# Résultat attendu : 404 ou 502 (normal sans frontend)

# SSL Certificate
echo | openssl s_client -servername skillforge-ai.emacsah.com -connect skillforge-ai.emacsah.com:443 2>/dev/null | openssl x509 -noout -text | grep "DNS:.*skillforge-ai.emacsah.com"
```

### **Checklist Validation**
- [ ] **api.emacsah.com/health** répond 200 OK
- [ ] **skillforge-ai.emacsah.com** résout vers 34.149.174.205
- [ ] **Certificat SSL** inclut les deux domaines
- [ ] **Logs Cloud Run** sans erreurs CORS
- [ ] **Load Balancer** route correctement

---

## 🎉 Résultat

Après cette migration **SANS INTERRUPTION**, vous aurez :

✅ **api.emacsah.com** → Backend API (inchangé)  
✅ **skillforge-ai.emacsah.com** → Prêt pour frontend  
✅ **Architecture scalable** pour croissance SaaS  
✅ **SSL automatique** sur les deux domaines  
✅ **Même IP statique** pour les deux services  

**Temps total** : ~25 minutes  
**Interruption** : 0 seconde  
**Risque** : Très faible (rollback immédiat possible)  

---

*Migration planifiée pour minimiser les risques et assurer la continuité de service*



Outputs:

api_domain = "https://api.emacsah.com"
database_connection_name = "skillforge-ai-mvp-25:europe-west1:skillforge-pg-instance-staging"
database_instance_name = "skillforge-pg-instance-staging"
database_private_ip = <sensitive>
docker_repository_url = "europe-west1-docker.pkg.dev/skillforge-ai-mvp-25/skillforge-docker-repo-staging"
environment = "staging"
frontend_assets_bucket_name = "skillforge-ai-mvp-25-frontend-assets-staging"
frontend_assets_url = "https://storage.googleapis.com/skillforge-ai-mvp-25-frontend-assets-staging"
jwt_secret_name = "jwt-secret-key-staging"
load_balancer_ip = "34.149.174.205"
project_id = "skillforge-ai-mvp-25"
redis_host = <sensitive>
redis_instance_name = "skillforge-redis-instance-staging"
redis_port = 6379
region = "europe-west1"
ssl_certificate_name = "skillforge-ssl-cert-multi-staging"
subnet_name = "skillforge-subnet-staging"
user_service_account_email = "sa-user-service-staging@skillforge-ai-mvp-25.iam.gserviceaccount.com"
user_service_name = "user-service-staging"
user_service_url = "https://user-service-staging-koi53iwqbq-ew.a.run.app"
user_uploads_bucket_name = "skillforge-ai-mvp-25-user-uploads-staging"
vpc_connector_id = "projects/skillforge-ai-mvp-25/locations/europe-west1/connectors/vpc-conn-staging"
vpc_id = "projects/skillforge-ai-mvp-25/global/networks/skillforge-vpc-staging"
vpc_name = "skillforge-vpc-staging"