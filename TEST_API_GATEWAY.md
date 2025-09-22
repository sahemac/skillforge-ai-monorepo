# Test API Gateway SkillForge AI

## 🚀 Instructions de Test

### Prérequis Vérifiés ✅
- Terraform installé ✅
- user-service déployé et fonctionnel ✅
- Configuration API Gateway créée ✅

### Étapes de Déploiement

#### 1. Navigation vers le répertoire staging
```cmd
cd C:\Users\DELL\Documents\GitHub\skillforge-ai-monorepo\terraform\environments\staging
```

#### 2. Initialisation Terraform
```cmd
terraform init
```

#### 3. Validation de la configuration
```cmd
terraform validate
```

#### 4. Planification du déploiement
```cmd
terraform plan
```

#### 5. Application des changements
```cmd
terraform apply
```
> Tapez `yes` quand demandé

### 🧪 Tests de Validation

Une fois le déploiement terminé, Terraform affichera les URLs de test. Utilisez ces commandes pour tester :

#### 1. Test de santé de l'API Gateway
```cmd
curl -I https://[API_GATEWAY_URL]/health
```

#### 2. Test de santé du user-service via Gateway
```cmd
curl -I https://[API_GATEWAY_URL]/api/v1/auth/health
```

#### 3. Test des endpoints avec authentification
```cmd
curl https://[API_GATEWAY_URL]/api/v1/users
```

#### 4. Test de login (sans auth)
```cmd
curl -X POST https://[API_GATEWAY_URL]/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"password\"}"
```

### 📊 Résultats Attendus

#### ✅ Succès
- **Health check**: Status 200 ou 302 (redirection OAuth)
- **API endpoints**: Status 401 (authentification requise) ou 200 si authentifié
- **Login endpoint**: Status 200/400 selon les credentials

#### ❌ Problèmes Possibles
- **404**: Service non trouvé → Vérifier le routage
- **500**: Erreur backend → Vérifier les logs user-service
- **502/503**: Gateway down → Vérifier le déploiement

### 🔍 Debugging

#### Vérifier les logs de l'API Gateway
```cmd
gcloud logging read "resource.type=api AND resource.labels.service=skillforge-api-staging" --limit=20 --project=skillforge-ai-mvp-25
```

#### Vérifier les logs du user-service
```cmd
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=user-service-staging" --limit=20 --project=skillforge-ai-mvp-25
```

#### Vérifier l'état de l'API Gateway
```cmd
gcloud api-gateway gateways list --location=europe-west1 --project=skillforge-ai-mvp-25
```

### 🎯 Objectifs du Test

1. **Validation du déploiement** : L'API Gateway se déploie sans erreur
2. **Routage fonctionnel** : Les requêtes sont correctement routées vers user-service
3. **Authentification** : Les endpoints protégés requièrent une authentification
4. **Health checks** : Les endpoints de santé répondent correctement
5. **Performance** : Latence acceptable (< 200ms)

### 📋 Checklist de Test

- [ ] `terraform init` - succès
- [ ] `terraform validate` - succès  
- [ ] `terraform plan` - pas d'erreurs
- [ ] `terraform apply` - déploiement réussi
- [ ] URL API Gateway générée
- [ ] Health check `/health` - répond
- [ ] Health check `/api/v1/auth/health` - répond
- [ ] Endpoint `/api/v1/users` - requiert auth
- [ ] Endpoint `/api/v1/auth/login` - accessible

### 🔄 Nettoyage (Optionnel)

Pour supprimer l'API Gateway après test :
```cmd
terraform destroy
```

---

## 🎯 Résultat Attendu

Si tout fonctionne, vous devriez avoir :
- **URL API Gateway** : `https://skillforge-api-staging-[PROJECT_ID].ew.gateway.dev`
- **Routage fonctionnel** vers user-service
- **Base solide** pour ajouter les autres services

Une fois validé, nous pourrons déployer la version complète avec les 23 services !