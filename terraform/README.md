# Terraform Infrastructure - SkillForge AI

Ce document explique comment gérer l'infrastructure SkillForge AI avec Terraform en mode multi-environnements.

## 📋 Vue d'Ensemble

### Structure du Projet

```
terraform/
├── environments/
│   ├── _bootstrap/              # Initialisation backend Terraform
│   │   └── bootstrap.tf
│   ├── staging/                 # Infrastructure STAGING
│   │   ├── backend.tf          # Configuration backend GCS
│   │   ├── provider.tf         # Configuration provider GCP
│   │   ├── variables.tf        # Définition des variables
│   │   ├── terraform.tfvars    # Valeurs staging (ne pas commiter)
│   │   ├── main.tf             # Ressources principales
│   │   ├── network.tf          # VPC, sous-réseaux, firewall
│   │   ├── database.tf         # Cloud SQL PostgreSQL
│   │   ├── cache.tf            # Redis Memorystore
│   │   ├── storage.tf          # Buckets et registres
│   │   ├── load_balancer.tf    # Load balancer et SSL
│   │   ├── monitoring.tf       # Dashboards et alertes
│   │   └── services/           # Services Cloud Run
│   │       ├── variables.tf    # Variables du module services
│   │       ├── user_service.tf # Configuration user-service
│   │       └── outputs.tf      # Outputs du module
│   └── production/             # Infrastructure PRODUCTION
│       └── [même structure que staging]
└── README.md                   # Ce document
```

### Approche Multi-Environnements

- **Isolation complète** : Chaque environnement a son propre état Terraform
- **Configuration par variables** : Même code, valeurs différentes via `terraform.tfvars`
- **Naming automatique** : Suffixes d'environnement générés automatiquement
- **Sécurité** : Fichiers `.tfvars` exclus du versioning

---

## 🚀 Guide de Déploiement

### Prérequis

1. **Terraform installé** (≥ 1.0)
   ```bash
   terraform --version
   ```

2. **Google Cloud SDK configuré**
   ```bash
   gcloud auth application-default login
   gcloud config set project skillforge-ai-mvp-25
   ```

3. **Backend Bootstrap réalisé** (une seule fois)
   ```bash
   cd terraform/environments/_bootstrap
   terraform init
   terraform apply
   ```

### Déploiement Staging

1. **Navigation vers staging**
   ```bash
   cd terraform/environments/staging
   ```

2. **Vérification des variables**
   
   Ouvrir `terraform.tfvars` et vérifier les valeurs :
   ```hcl
   project_id     = "skillforge-ai-mvp-25"
   environment    = "staging"
   organization_domain = "emacsah.com"
   # ... autres variables
   ```

3. **Initialisation**
   ```bash
   terraform init
   ```

4. **Planification**
   ```bash
   terraform plan
   ```

5. **Application**
   ```bash
   terraform apply
   ```

### Déploiement Production

1. **Navigation vers production**
   ```bash
   cd terraform/environments/production
   ```

2. **Vérification des variables de production**
   
   Ouvrir `terraform.tfvars` et ajuster pour production :
   ```hcl
   project_id     = "skillforge-ai-mvp-25"
   environment    = "production"
   ssl_certificate_domains = ["api.skillforge.emacsah.com"]
   database_tier  = "db-standard-2"  # Plus puissant en prod
   # ... autres variables
   ```

3. **Initialisation**
   ```bash
   terraform init
   ```

4. **Plan avec comparaison**
   ```bash
   terraform plan -out=production.tfplan
   ```

5. **Application**
   ```bash
   terraform apply production.tfplan
   ```

---

## 🔧 Configuration des Variables

### Variables Obligatoires

Ces variables **doivent** être définies dans chaque `terraform.tfvars` :

```hcl
# Projet GCP
project_id                = "skillforge-ai-mvp-25"
project_number           = "584748485117"
environment              = "staging" # ou "production"

# DNS et domaines
organization_domain      = "emacsah.com"
global_ip_name          = "skillforge-global-ip"
ssl_certificate_domains = ["api.emacsah.com"]

# Docker
docker_repo_name        = "skillforge-docker-repo-staging"
```

### Variables Optionnelles avec Défauts

Ces variables ont des valeurs par défaut mais peuvent être surchargées :

```hcl
# Réseau
region                  = "europe-west1"  # default
vpc_cidr               = "10.0.0.0/24"   # default
vpc_connector_cidr     = "10.8.0.0/28"   # default

# Base de données
database_tier          = "db-g1-small"   # staging default
database_version       = "POSTGRES_16"   # default
database_backup_enabled = true           # default

# Cloud Run
cloud_run_max_instances = 10             # default
cloud_run_min_instances = 0              # default
cloud_run_cpu_limit    = "1"             # default
cloud_run_memory_limit = "512Mi"         # default
```

### Différences Staging vs Production

| Ressource | Staging | Production |
|-----------|---------|------------|
| **Base de données** | `db-g1-small` | `db-standard-2` |
| **Redis** | `1GB BASIC` | `4GB STANDARD_HA` |
| **SSL Domaine** | `api.emacsah.com` | `api.skillforge.emacsah.com` |
| **Cloud Run CPU** | `1 core` | `2 cores` |
| **Cloud Run Mémoire** | `512Mi` | `1Gi` |
| **Scaling max** | `5 instances` | `100 instances` |
| **Instances min** | `0` (scale-to-zero) | `2` (always warm) |

---

## 🔒 Sécurité et Secrets

### Secrets Manager

Les secrets sont gérés via Google Secret Manager :

```bash
# Créer les secrets (une seule fois par environnement)
gcloud secrets create postgres-password-staging --data-file=-
gcloud secrets create jwt-secret-key-staging --data-file=-

gcloud secrets create postgres-password-production --data-file=-
gcloud secrets create jwt-secret-key-production --data-file=-
```

### Fichiers Sensibles

**⚠️ IMPORTANT** : Ces fichiers ne doivent **jamais** être commitées :

```bash
# Ajouter au .gitignore
echo "terraform.tfvars" >> .gitignore
echo "*.tfplan" >> .gitignore
echo ".terraform/" >> .gitignore
```

### Permissions IAM

Chaque service a son propre Service Account avec permissions minimales :

- `sa-user-service-staging` : Accès Cloud SQL + Secrets spécifiques
- `sa-user-service-production` : Mêmes permissions, environnement production

---

## 🌐 Ressources Créées

### Infrastructure de Base

| Ressource | Nom Staging | Nom Production |
|-----------|-------------|----------------|
| **VPC** | `skillforge-vpc-staging` | `skillforge-vpc-production` |
| **Subnet** | `skillforge-subnet-staging` | `skillforge-subnet-production` |
| **Cloud SQL** | `skillforge-pg-instance-staging` | `skillforge-pg-instance-production` |
| **Redis** | `skillforge-redis-instance-staging` | `skillforge-redis-instance-production` |
| **Docker Registry** | `skillforge-docker-repo-staging` | `skillforge-docker-repo-production` |

### Services Applicatifs

| Service | Staging | Production |
|---------|---------|------------|
| **User Service** | `user-service-staging` | `user-service-production` |
| **Service Account** | `sa-user-service-staging` | `sa-user-service-production` |

### Stockage

| Bucket | Usage | Staging | Production |
|--------|--------|---------|------------|
| **Frontend Assets** | Site web statique | `...-frontend-assets-staging` | `...-frontend-assets-production` |
| **User Uploads** | Fichiers utilisateurs | `...-user-uploads-staging` | `...-user-uploads-production` |

---

## 🔄 Workflow de Déploiement

### Processus Recommandé

1. **Développement Local** → Test sur environnement personnel
2. **Staging** → Tests d'intégration et validation
3. **Production** → Déploiement final après validation

### Commandes Utiles

```bash
# Voir l'état actuel
terraform show

# Lister les ressources
terraform state list

# Détruire l'infrastructure (ATTENTION!)
terraform destroy  # Uniquement pour staging/test

# Formater le code
terraform fmt -recursive

# Valider la configuration
terraform validate

# Voir les outputs
terraform output
```

### Promotion Staging → Production

```bash
# 1. Valider staging
cd terraform/environments/staging
terraform plan -detailed-exitcode

# 2. Ajuster les variables production
cd ../production
# Modifier terraform.tfvars pour production

# 3. Planifier production
terraform plan -out=prod-deployment.tfplan

# 4. Review et approbation manuelle
# 5. Appliquer
terraform apply prod-deployment.tfplan
```

---

## 🛠️ Dépannage

### Erreurs Communes

**❌ Backend non initialisé**
```bash
Error: Backend initialization required
```
**✅ Solution :**
```bash
terraform init
```

**❌ Variables manquantes**
```bash
Error: No value for required variable
```
**✅ Solution :** Vérifier `terraform.tfvars`

**❌ Ressources en conflit**
```bash
Error: Resource already exists
```
**✅ Solution :**
```bash
terraform import google_storage_bucket.example bucket-name
```

**❌ Provider version trop ancienne**
```bash
Error: Resource instance managed by newer provider version
Warning: Failed to decode resource from state: unsupported attribute "hierarchical_namespace"
```
**✅ Solution automatique :**
```bash
# Linux/Mac
./fix-provider-version.sh staging

# Windows PowerShell
.\fix-provider-version.ps1 staging
```

**✅ Solution manuelle :**
```bash
# 1. Sauvegarde
terraform state pull > backup.tfstate

# 2. Nettoyage 
rm -rf .terraform/
rm -f .terraform.lock.hcl

# 3. Réinitialisation
terraform init

# 4. Test
terraform plan -var-file="terraform.tfvars"
```

### Logs et Debugging

```bash
# Activer les logs détaillés
export TF_LOG=DEBUG
terraform plan

# Logs spécifiques au provider Google
export TF_LOG_PROVIDER=DEBUG
```

### État Corrompu

```bash
# Sauvegarder l'état
terraform state pull > backup.tfstate

# Supprimer une ressource de l'état (sans la détruire)
terraform state rm google_compute_instance.example

# Importer une ressource existante
terraform import google_compute_instance.example instance-id
```

---

## 📈 Monitoring et Alertes

### Dashboards Créés

- **Dashboard Principal** : Vue d'ensemble des services
- **Métriques Cloud SQL** : Performances base de données
- **Métriques Cloud Run** : Latence, erreurs, scaling

### Alertes Configurées

- **Erreurs 5xx** > 1% pendant 5 minutes → PagerDuty
- **CPU Cloud SQL** > 90% pendant 15 minutes → Email
- **Budget GCP** > seuil mensuel → Email

---

## 🚀 Prochaines Étapes

### Améliorations Recommandées

1. **Modules Terraform** : Créer des modules réutilisables
   ```
   terraform/modules/
   ├── cloud-run-service/
   ├── postgres-database/
   └── monitoring-stack/
   ```

2. **Pipeline CI/CD Terraform**
   ```yaml
   # .github/workflows/terraform-plan.yml
   name: Terraform Plan
   on: [pull_request]
   # Automatiser terraform plan sur les PR
   ```

3. **Tests d'Infrastructure**
   ```bash
   # Utiliser Terratest ou Terraform Cloud
   go test ./test/
   ```

4. **État Remote Locking**
   ```bash
   # Activer le locking avec Cloud Storage
   terraform {
     backend "gcs" {
       bucket = "terraform-state-bucket"
       prefix = "env"
     }
   }
   ```

### Environnements Additionnels

```bash
# Créer environnement de développement
cp -r terraform/environments/staging terraform/environments/development
# Ajuster les variables pour dev (instances plus petites)
```

---

## 📚 Références

- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Terraform Examples](https://cloud.google.com/docs/terraform)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Infrastructure as Code Guide](https://cloud.google.com/architecture/infrastructure-as-code-terraform)

---

## 🤝 Support

Pour questions ou support :
1. **Documentation** : Consulter ce README
2. **Logs Terraform** : Activer `TF_LOG=DEBUG`
3. **Issues** : Créer une issue dans le repository
4. **DevOps Team** : devops-alerts@emacsah.com

---

*Documentation mise à jour le 2 septembre 2025*