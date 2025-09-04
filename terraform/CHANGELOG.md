# Changelog - Infrastructure Terraform SkillForge AI

## [v2.1.0] - 2025-09-02

### 🔧 Corrections et améliorations

**Provider Version Update**
- Mise à jour provider Google Cloud de `~> 5.0` vers `~> 6.0`
- Résolution des erreurs `hierarchical_namespace` sur Storage Buckets
- Support explicite pour les nouvelles fonctionnalités provider Google

**Configuration Buckets Storage**
- Ajout explicite de `hierarchical_namespace { enabled = false }`
- Support des Data Lake buckets (désactivé par défaut)
- Meilleure compatibilité avec les versions récentes du provider

**Scripts d'automatisation**
- `fix-provider-version.sh` : Script bash de correction automatique
- `fix-provider-version.ps1` : Script PowerShell pour Windows
- `validate-environments.sh/ps1` : Scripts de validation multi-environnements

## [v2.0.0] - 2025-09-02

### 🚀 Refactoring complet multi-environnements

**Architecture**
- Structure complète multi-environnements (staging/production)
- Élimination de 100% du hard-coding
- Variables formalisées avec types et descriptions
- Configuration par fichiers `.tfvars` spécifiques

**Nouvelles variables**
- 40+ variables configurables
- Support des différences staging vs production
- Variables obligatoires vs optionnelles
- Locals pour naming automatique

**Améliorations sécurité**
- Labels standardisés sur toutes les ressources compatibles
- Configuration IAM granulaire
- Database flags optimisés pour monitoring
- Deletion protection activée sur ressources critiques

**Load Balancer**
- Configuration avancée avec CDN pour production
- Support multi-domaines via variables
- Redirections HTTP→HTTPS automatiques
- Configuration IAP préparée

**Monitoring**
- Canaux de notification configurables
- Alertes conditionnelles par environnement
- Dashboard avec noms dynamiques
- Support email et autres canaux

**Documentation**
- README complet avec guides de déploiement
- Guide de dépannage détaillé
- Scripts de validation automatique
- Guide des commandes rapides

### ⚠️ Breaking Changes

- Refactoring complet des noms de ressources
- Migration requise pour ressources existantes
- Fichiers `.tfvars` requis pour chaque environnement
- Backend configuration manuelle par environnement

## [v1.0.0] - 2025-08-30

### 🎯 Version initiale

**Infrastructure de base**
- Configuration Terraform staging basique
- Services Cloud Run, Cloud SQL, Redis
- Load Balancer avec SSL managé
- Monitoring basique

**Limitations v1.0**
- Hard-coding des valeurs
- Un seul environnement
- Configuration manuelle requise
- Documentation limitée

---

## Migration Guide

### De v1.0 vers v2.0+

1. **Sauvegarde de l'état**
   ```bash
   terraform state pull > backup-v1.tfstate
   ```

2. **Migration des variables**
   ```bash
   # Créer terraform.tfvars pour chaque environnement
   cp terraform.tfvars.example terraform.tfvars
   # Adapter les valeurs
   ```

3. **Réinitialisation**
   ```bash
   rm -rf .terraform/
   terraform init
   ```

4. **Validation**
   ```bash
   terraform plan -var-file="terraform.tfvars"
   ```

### Résolution problèmes provider

Si erreurs `hierarchical_namespace` ou version provider :

```bash
# Automatique
./fix-provider-version.sh staging

# Manuel 
rm -rf .terraform/ && terraform init
```

---

## Support

- **Documentation**: `README.md`
- **Scripts**: `validate-environments.sh/ps1`
- **Dépannage**: Section troubleshooting du README
- **Issues**: GitHub repository issues

---

*Changelog maintenu depuis septembre 2025*