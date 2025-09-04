# Terraform - Commandes Rapides SkillForge AI

## 🚀 Déploiement Rapide

### Staging
```bash
cd terraform/environments/staging
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Production
```bash
cd terraform/environments/production
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

## 🔍 Validation et Debug

### Valider tous les environnements
```bash
# Linux/Mac
./validate-environments.sh

# Windows
.\validate-environments.ps1
```

### Validation manuelle
```bash
cd terraform/environments/staging
terraform fmt -check -diff    # Vérifier le format
terraform validate            # Vérifier la syntaxe
terraform plan -detailed-exitcode  # Plan détaillé
```

## 🛠️ Maintenance

### Formater le code
```bash
terraform fmt -recursive
```

### Voir l'état
```bash
terraform show
terraform state list
```

### Voir les outputs
```bash
terraform output
terraform output -json
```

## 🔄 Mise à jour

### Mettre à jour les providers
```bash
terraform init -upgrade
```

### Rafraîchir l'état
```bash
terraform refresh
```

## ⚠️ Dépannage

### Erreurs communes et solutions

**❌ Backend non initialisé**
```bash
terraform init
```

**❌ Variables manquantes**
```bash
# Vérifier terraform.tfvars
terraform plan -var-file="terraform.tfvars"
```

**❌ Ressources en conflit**
```bash
terraform import google_storage_bucket.example bucket-name
```

**❌ État corrompu**
```bash
terraform state pull > backup.tfstate
terraform state rm resource.name
```

## 📊 Monitoring et Outputs

### Voir les ressources importantes
```bash
terraform output load_balancer_ip
terraform output api_domain
terraform output database_connection_name
```

### URLs utiles après déploiement
- **API Staging**: https://api.emacsah.com
- **API Production**: https://api.skillforge.emacsah.com
- **Dashboard GCP**: https://console.cloud.google.com/

## 🔐 Secrets et Sécurité

### Créer les secrets requis
```bash
# Staging
echo "your-jwt-secret" | gcloud secrets create jwt-secret-key-staging --data-file=-
echo "your-db-password" | gcloud secrets create postgres-password-staging --data-file=-

# Production
echo "your-jwt-secret" | gcloud secrets create jwt-secret-key-production --data-file=-
echo "your-db-password" | gcloud secrets create postgres-password-production --data-file=-
```

### Vérifier les permissions
```bash
gcloud projects get-iam-policy skillforge-ai-mvp-25
```

## 📝 Variables importantes

### Staging vs Production
| Variable | Staging | Production |
|----------|---------|------------|
| `database_tier` | `db-g1-small` | `db-standard-2` |
| `redis_memory_size_gb` | `1` | `4` |
| `cloud_run_max_instances` | `5` | `100` |
| `ssl_certificate_domains` | `["api.emacsah.com"]` | `["api.skillforge.emacsah.com"]` |

## 🔄 Workflow Recommandé

1. **Develop** → Test local
2. **Staging** → `terraform plan && terraform apply`
3. **Validate** → Tests d'intégration sur staging
4. **Production** → `terraform plan && terraform apply`
5. **Monitor** → Vérifier les métriques et alertes

---

*Aide-mémoire mis à jour le 2 septembre 2025*