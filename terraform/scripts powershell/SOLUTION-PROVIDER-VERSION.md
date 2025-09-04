# 🚨 SOLUTION COMPLÈTE - Erreur Provider Version

## Problème Identifié

```
Error: Resource instance managed by newer provider version
The current state of google_storage_bucket.* was created by a newer provider version than is currently selected.
```

## Cause Racine

Les buckets de stockage ont été créés avec une version du provider Google Cloud plus récente (probablement lors d'une session précédente), et maintenant Terraform utilise une version mise en cache plus ancienne.

## 🔧 SOLUTION ÉTAPE PAR ÉTAPE

### Option 1: Solution Automatique (Recommandée)

```powershell
# Windows PowerShell
cd terraform
.\force-upgrade-provider.ps1 staging
```

```bash
# Linux/Mac
cd terraform
./force-upgrade-provider.sh staging
```

### Option 2: Solution Manuelle Détaillée

#### Étape 1: Sauvegarde de l'État Actuel
```bash
cd terraform/environments/staging
terraform state pull > backup-state-manuel.json
```

#### Étape 2: Nettoyage COMPLET
```bash
# IMPORTANT: Supprimer TOUT le cache
rm -rf .terraform/
rm -f .terraform.lock.hcl
rm -f terraform.tfstate
rm -f terraform.tfstate.backup
rm -f *.tfplan
```

#### Étape 3: Vérifier la Version du Provider
Ouvrir `backend.tf` et s'assurer que:
```hcl
terraform {
  backend "gcs" {
    bucket = "skillforge-ai-mvp-25-tfstate"
    prefix = "staging"
  }
  
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"  # DOIT être 6.0 ou plus récent
    }
  }
}
```

#### Étape 4: Réinitialisation avec Upgrade Forcé
```bash
# Force la mise à jour vers la dernière version 6.x
terraform init -upgrade
```

#### Étape 5: Réconciliation de l'État
```bash
# Rafraîchir l'état avec la nouvelle version du provider
terraform refresh -var-file="terraform.tfvars"
```

#### Étape 6: Vérification
```bash
# Devrait fonctionner sans erreurs
terraform plan -var-file="terraform.tfvars"
```

## 📝 Checklist de Vérification

### Fichiers à Vérifier

✅ **backend.tf** (staging & production)
```hcl
version = "~> 6.0"  # PAS 5.0 !
```

✅ **storage.tf** (staging & production)
```hcl
resource "google_storage_bucket" "user_uploads" {
  # Support for hierarchical namespace
  hierarchical_namespace {
    enabled = false
  }
}
```

✅ **.terraform.lock.hcl**
```hcl
provider "registry.terraform.io/hashicorp/google" {
  version     = "6.x.x"  # Doit être 6.x
  constraints = "~> 6.0"
}
```

### Commandes de Diagnostic

```bash
# Vérifier la version du provider actuellement utilisée
terraform version

# Vérifier l'état de lock
cat .terraform.lock.hcl | grep version

# Lister les providers installés
ls -la .terraform/providers/registry.terraform.io/hashicorp/google/
```

## ⚠️ Points d'Attention

1. **Ne jamais** downgrader le provider si les ressources ont été créées avec une version plus récente
2. **Toujours** sauvegarder l'état avant toute manipulation
3. **Vérifier** que staging ET production utilisent la même version du provider

## 🔄 Synchronisation des Environnements

Après avoir résolu le problème en staging:

```bash
# Copier la configuration vers production
cp terraform/environments/staging/backend.tf terraform/environments/production/
cp terraform/environments/staging/storage.tf terraform/environments/production/

# Nettoyer et réinitialiser production
cd terraform/environments/production
rm -rf .terraform/
terraform init -upgrade
```

## 💡 Prévention Future

### 1. Toujours utiliser `-upgrade` lors des init
```bash
terraform init -upgrade
```

### 2. Vérifier les versions avant de commiter
```bash
grep version backend.tf
cat .terraform.lock.hcl | grep version
```

### 3. Synchroniser les versions entre environnements
```bash
# Script de vérification
for env in staging production; do
  echo "=== $env ==="
  grep "version.*google" terraform/environments/$env/backend.tf
done
```

## 🚑 Récupération d'Urgence

Si tout échoue:

```bash
# 1. Restaurer l'état sauvegardé
terraform state push backup-state-manuel.json

# 2. Forcer la recréation des buckets (DANGER!)
terraform state rm google_storage_bucket.user_uploads
terraform state rm google_storage_bucket.frontend_assets
terraform apply -var-file="terraform.tfvars"
```

## 📞 Support

Si le problème persiste après ces étapes:

1. Vérifier les logs détaillés:
```bash
export TF_LOG=DEBUG
terraform plan -var-file="terraform.tfvars" 2> debug.log
```

2. Vérifier l'état GCS distant:
```bash
gsutil cp gs://skillforge-ai-mvp-25-tfstate/staging/default.tfstate .
cat default.tfstate | grep provider_version
```

3. Contacter le support avec:
- Le fichier `debug.log`
- La sortie de `terraform version`
- Le contenu de `.terraform.lock.hcl`

---

**Dernière mise à jour**: 3 septembre 2025
**Version Provider Recommandée**: ~> 6.0 (6.49.2 ou plus récent)