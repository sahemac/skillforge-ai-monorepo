# Guide d'application manuelle de l'IAP

## Problème actuel
- `https://api.emacsah.com` retourne 403 Forbidden
- Les modifications IAP Terraform doivent être appliquées

## Solution : Appliquer les modifications IAP

### Option 1 : Via Terraform local (Recommandé)

```bash
# 1. Se déplacer dans l'environnement staging
cd terraform/environments/staging

# 2. Vérifier les modifications
terraform plan -var-file="terraform.tfvars"

# 3. Appliquer les modifications IAP
terraform apply -var-file="terraform.tfvars"
```

### Option 2 : Via GitHub Actions

1. **Commit les modifications** :
   ```bash
   git add .
   git commit -m "Add IAP configuration for staging environment"
   git push
   ```

2. **Déclencher le workflow Terraform** :
   - Aller sur GitHub Actions
   - Sélectionner le workflow "Terraform"
   - Cliquer "Run workflow" pour staging

### Option 3 : Configuration manuelle via GCP Console

Si Terraform pose problème, configurer IAP manuellement :

#### **3.1 Activer IAP sur le Load Balancer**

1. **Console GCP** → **Identity-Aware Proxy**
2. **HTTPS Resources** → Trouver `user-service-backend-staging`
3. **Activer IAP** → Configurer OAuth consent screen
4. **OAuth consent screen** :
   - Application name: "SkillForge AI Staging"
   - Support email: `sah@emacsah.com`

#### **3.2 Configurer les utilisateurs autorisés**

1. **IAP** → **user-service-backend-staging** 
2. **Add Principal** → `sah@emacsah.com`
3. **Role** : `IAP-secured Web App User`
4. **Save**

#### **3.3 Tester l'accès**

```bash
curl -I https://api.emacsah.com/health
# Devrait retourner 302 avec redirect vers accounts.google.com
```

## Vérification post-application

### Test 1: Accès non authentifié (attendu: 302/401)
```bash
curl -I https://api.emacsah.com/health
```

### Test 2: Accès via navigateur
1. Aller sur `https://api.emacsah.com/health`
2. Devrait rediriger vers Google OAuth
3. Se connecter avec `sah@emacsah.com`
4. Accès autorisé au service

### Test 3: Validation automatique
Déclencher le workflow `validate-iap.yml` pour tests automatiques.

## Ressources appliquées

Les modifications Terraform ajoutent :

1. **google_iap_brand** - OAuth consent screen
2. **google_iap_client** - Client IAP
3. **google_compute_backend_service.iap{}** - Configuration IAP
4. **google_iap_web_backend_service_iam_binding** - Permissions utilisateur

## Résolution du 403 Forbidden

Le 403 actuel est **normal** car :
- IAP est activé mais pas encore configuré via Terraform
- Le service rejette l'accès non authentifié
- Une fois appliqué, IAP redirigera vers OAuth (302)

**Après application : 403 → 302 → OAuth → Accès autorisé** ✅