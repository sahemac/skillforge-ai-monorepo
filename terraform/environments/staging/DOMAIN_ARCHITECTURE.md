# SkillForge AI - Domain Architecture Strategy

## 🎯 Stratégie : Modular Monolith → Micro-services

Cette architecture permet de :
- ✅ **Démarrer simple** avec un frontend monolithique
- ✅ **Migrer progressivement** vers des micro-frontends
- ✅ **Garder la flexibilité** pour l'évolution future

---

## 🌐 Architecture de Domaines

### **Configuration Actuelle (Phase 1 - Monolithe)**

```
┌─────────────────────────────────────────────────────────┐
│  skillforge-ai.emacsah.com (34.149.174.205)            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend Monolithique (Shell)                          │
│  ├── /                  → Landing Page                  │
│  ├── /mission          → Mission Page                   │
│  ├── /contact          → Contact Page                   │
│  ├── /login            → Login (dans shell)             │
│  ├── /register         → Register (dans shell)          │
│  └── /dashboard        → Dashboard (dans shell)         │
│                                                          │
│  Backend Services API                                   │
│  ├── /api/v1/users/*   → User Service                   │
│  ├── /api/v1/auth/*    → Auth (user-service)            │
│  └── /api/v1/companies/* → Company Service              │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  api.emacsah.com                                        │
│  (Redirige vers skillforge-ai.emacsah.com/api/v1/)     │
└─────────────────────────────────────────────────────────┘
```

### **Configuration Future (Phase 2 - Micro-services)**

```
┌─────────────────────────────────────────────────────────┐
│  skillforge-ai.emacsah.com                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Pages Publiques (Shell)                               │
│  ├── /                  → Landing                       │
│  ├── /mission          → Mission                        │
│  └── /contact          → Contact                        │
│                                                          │
│  Micro-Frontends Dédiés                                │
│  ├── /admin/*          → Admin Frontend                 │
│  ├── /learner/*        → Learner Frontend               │
│  ├── /company/*        → Company Frontend               │
│  └── /auth/*           → Auth Frontend (optionnel)      │
│                                                          │
│  Backend Services API                                   │
│  ├── /api/v1/users/*   → User Service                   │
│  ├── /api/v1/auth/*    → Auth Service                   │
│  ├── /api/v1/companies/* → Company Service              │
│  ├── /api/v1/projects/* → Project Service               │
│  └── /api/v1/matching/* → Matching Service (AI)         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Mapping des Routes

### **Routes Actives (Phase 1)**

| Route Pattern | Service | Type | Status |
|--------------|---------|------|--------|
| `/` | shell-frontend | Frontend | ✅ Active |
| `/mission` | shell-frontend | Frontend | ✅ Active |
| `/contact` | shell-frontend | Frontend | ✅ Active |
| `/login` | shell-frontend | Frontend | ✅ Active |
| `/register` | shell-frontend | Frontend | ✅ Active |
| `/api/v1/users/*` | user-service | Backend | ✅ Active |
| `/api/v1/auth/*` | user-service | Backend | ✅ Active |
| `/api/v1/companies/*` | company-service | Backend | ✅ Active |

### **Routes Futures (Phase 2 - Commentées)**

| Route Pattern | Service | Type | Status |
|--------------|---------|------|--------|
| `/admin/*` | admin-frontend | Frontend | ⏳ Prêt (commenté) |
| `/learner/*` | learner-frontend | Frontend | ⏳ Prêt (commenté) |
| `/company/*` | company-frontend | Frontend | ⏳ Prêt (commenté) |
| `/api/v1/projects/*` | project-service | Backend | ⏳ Prêt (commenté) |
| `/api/v1/matching/*` | matching-service | Backend | ⏳ Prêt (commenté) |

---

## 🔄 Plan de Migration

### **Étape 1 : Monolithe (Actuel)**
```bash
# Frontend
Shell (React) → Gère TOUTES les pages

# Backend
user-service → /api/v1/users/*, /api/v1/auth/*
company-service → /api/v1/companies/*
```

### **Étape 2 : Split Frontend par Rôle**
```bash
# Créer les micro-frontends
apps/frontend/admin/     # Dashboard admin
apps/frontend/learner/   # Dashboard apprenant
apps/frontend/company/   # Dashboard entreprise

# Décommenter dans url-map-config.yaml :
- /admin/* → admin-frontend
- /learner/* → learner-frontend
- /company/* → company-frontend
```

### **Étape 3 : Split Backend par Domaine**
```bash
# Créer les services backend
project-service    → /api/v1/projects/*
matching-service   → /api/v1/matching/*
portfolio-service  → /api/v1/portfolios/*

# Décommenter dans url-map-config.yaml
```

---

## 🛠️ Comment Activer une Nouvelle Route

### **Exemple : Activer le Frontend Admin**

1. **Créer le frontend admin**
```bash
# apps/frontend/admin déjà dans la structure
pnpm create vite admin --template react-ts
```

2. **Déployer sur Cloud Run**
```bash
# Via workflow ou manuel
gcloud run deploy skillforge-frontend-admin-staging
```

3. **Créer le backend service dans GCP**
```bash
gcloud compute backend-services create skillforge-admin-backend-staging \
  --global \
  --protocol=HTTP \
  --health-checks=skillforge-health-check
```

4. **Décommenter dans url-map-config.yaml**
```yaml
# Enlever les # devant
- paths:
    - /admin
    - /admin/*
  service: .../skillforge-admin-backend-staging
```

5. **Appliquer la configuration**
```bash
gcloud compute url-maps import skillforge-urlmap-staging \
  --source=terraform/environments/staging/url-map-config.yaml
```

---

## ✅ Avantages de Cette Architecture

### **Phase Monolithe (Maintenant)**
- ✅ Déploiement simple et rapide
- ✅ Pas de CORS à gérer
- ✅ Partage facile de composants
- ✅ Development velocity élevée
- ✅ Debugging simplifié

### **Phase Micro-services (Futur)**
- ✅ Teams autonomes par frontend
- ✅ Déploiements indépendants
- ✅ Scaling granulaire
- ✅ Technologies différentes possibles
- ✅ Isolation des failures

### **Transition Progressive**
- ✅ Pas de "big bang" migration
- ✅ Feature flags possibles
- ✅ Rollback facile
- ✅ Tests en production (A/B)

---

## 🔒 Sécurité et Certificats SSL

### **Certificat Actuel**
```
Nom: skillforge-ssl-cert-multi-staging
Type: MANAGED (Google-managed)
Domaines:
  ✅ skillforge-ai.emacsah.com
  ✅ api.emacsah.com
Status: ACTIVE
Expiration: Auto-renewal (managed)
```

### **Recommandation Future**
Lorsque vous aurez plus de micro-frontends, considérez :
- Wildcard SSL : `*.skillforge-ai.emacsah.com`
- Ou certificat multi-domaine étendu

---

## 📊 Performance et Caching

### **Configuration Actuelle**
- Cloud CDN: À configurer
- Cache-Control headers: À configurer par service
- Static assets: Vite build output optimisé

### **Recommandations**
```nginx
# Frontend assets (shell)
/assets/* → Cache: 1 year (immutable)
/*.js, /*.css → Cache: 1 year (immutable)
/index.html → Cache: no-cache (toujours fresh)

# API responses
/api/v1/* → Cache: no-cache (dynamic)
```

---

## 🎯 Prochaines Étapes

1. **Appliquer la configuration URL Map** ✅
2. **Tester les routes actuelles** ✅
3. **Configurer Cloud CDN** (optionnel)
4. **Monitorer avec Cloud Monitoring**
5. **Préparer les micro-frontends** (quand nécessaire)

---

## 📝 Notes Importantes

- **DNS** : `skillforge-ai.emacsah.com` doit pointer vers `34.149.174.205`
- **SSL** : Certificat auto-renouvelé par Google
- **Load Balancer** : Configuration path-based (pas host-based)
- **Health Checks** : À configurer pour chaque backend service
