# Notice de Sécurité - Configuration Staging

## ⚠️ **ATTENTION - Service Public**

### **Configuration actuelle**
- **Environnement** : Staging
- **Accès** : Public (pas d'authentification IAP)
- **URL** : https://api.emacsah.com
- **Statut** : Ouvert pour tests

### **Implications**
- ✅ **Avantage** : Tests faciles pour tous les utilisateurs
- ⚠️ **Risque** : Données accessibles publiquement
- ⚠️ **Limite** : Pas de traçabilité utilisateur

### **Recommandations**

#### **Pour le développement/tests**
1. **Ne pas stocker de données sensibles** en staging
2. **Utiliser des données de test** uniquement  
3. **Limiter les endpoints sensibles** (admin, delete, etc.)
4. **Monitoring renforcé** des accès

#### **Pour la production**
1. **Réactiver IAP** obligatoire
2. **Authentification stricte** requise
3. **Audit complet** des accès

### **Configuration recommandée par environnement**

| Environnement | IAP | Accès | Usage |
|---------------|-----|-------|-------|
| **Development** | ❌ Désactivé | Public | Développement local |
| **Staging** | ⚠️ **Actuellement désactivé** | Public | Tests, démos |
| **Production** | ✅ **Obligatoire** | Authentifié | Utilisateurs finaux |

### **Commandes de réactivation IAP (si besoin)**

```bash
# Console GCP → Identity-Aware Proxy
# HTTPS Resources → user-service-backend-staging → Toggle ON

# Ou via commande (nécessite reconfiguration OAuth):
gcloud compute backend-services update user-service-backend-staging \
  --global \
  --iap=enabled,oauth2-client-id=CLIENT_ID,oauth2-client-secret=SECRET
```

### **Monitoring de sécurité**

#### **Alertes recommandées**
- Accès anormalement élevé
- Tentatives d'accès aux endpoints admin
- Erreurs 4xx/5xx en masse

#### **Logs à surveiller**
```bash
# Logs d'accès Load Balancer
gcloud logging read 'resource.type="http_load_balancer"' --limit=100

# Logs applicatifs Cloud Run  
gcloud logging read 'resource.type="cloud_run_revision"' --limit=100
```

---
**Mise à jour** : 8 septembre 2025  
**Responsable** : Équipe DevOps