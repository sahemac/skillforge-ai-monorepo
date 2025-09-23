# Plan d'Implémentation API Gateway - SkillForge AI

**Date:** 21 septembre 2025  
**Version:** 1.0.0  
**Projet:** SkillForge AI Monorepo  
**Composant:** API Gateway GCP  

## 1. Vue d'Ensemble

### 1.1 Objectif
Implémenter une API Gateway centralisée sur Google Cloud Platform pour unifier l'accès à tous les services backend et frontend de SkillForge AI.

### 1.2 Inventaire des Services

#### Services Existants (1)
1. **user-service** - Service utilisateur avec authentification intégrée

#### Services à Créer (11)
1. **auth-service** - Service d'authentification dédié (extraction depuis user-service)
2. **company-service** - Gestion des entreprises
3. **subscription-service** - Gestion des abonnements
4. **payment-service** - Traitement des paiements
5. **notification-service** - Notifications (email, SMS, push)
6. **analytics-service** - Analytique et métriques
7. **content-service** - Gestion du contenu
8. **search-service** - Recherche et indexation
9. **storage-service** - Stockage de fichiers
10. **workflow-service** - Orchestration des workflows
11. **audit-service** - Journalisation et audit

### 1.3 Architecture Cible

```
Internet
    │
    ▼
┌─────────────────┐
│   CloudFlare    │
│      CDN        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load Balancer  │
│   (GCP HTTPS)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │ ◄── Point Central
│  (GCP API GW)   │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌─────────┐ ┌──────┐ ┌──────┐ ┌──────┐
│  Cloud  │ │Cloud │ │Cloud │ │ ...  │
│   Run   │ │ Run  │ │ Run  │ │      │
│ Service │ │ Svc2 │ │ Svc3 │ │      │
└─────────┘ └──────┘ └──────┘ └──────┘
```

## 2. Fonctionnement de l'API Gateway

### 2.1 Composants Principaux

#### A. Gateway Configuration
- **Type:** Google Cloud API Gateway
- **Region:** europe-west1
- **Version API:** v1 (avec versioning)
- **Protocol:** HTTPS only

#### B. Routage des Requêtes
```yaml
Routes:
  # Services Backend
  /api/v1/users/*     → user-service
  /api/v1/auth/*      → auth-service (futur)
  /api/v1/companies/* → company-service (futur)
  /api/v1/payments/*  → payment-service (futur)
  
  # Micro-frontends
  /app/auth/*         → auth-frontend
  /app/dashboard/*    → dashboard-frontend
  /app/admin/*        → admin-frontend
  
  # Static Assets
  /assets/*           → Cloud Storage
  /media/*            → Cloud Storage
```

#### C. Authentification Centralisée
- **IAP Integration:** Maintien de Google Identity-Aware Proxy
- **JWT Validation:** Validation centralisée des tokens
- **Rate Limiting:** Limitation globale par IP/User
- **CORS Management:** Configuration centralisée

### 2.2 Flux de Requêtes

1. **Requête entrante** → CloudFlare CDN
2. **SSL Termination** → Load Balancer HTTPS
3. **Authentication** → IAP Verification
4. **Rate Limiting** → Check quotas
5. **Routing** → API Gateway rules
6. **Service Call** → Target Cloud Run service
7. **Response** → Aggregation si nécessaire
8. **Caching** → CDN cache headers

## 3. Impacts sur l'Architecture Actuelle

### 3.1 Changements Requis

#### Infrastructure (Terraform)
```
terraform/
├── modules/
│   ├── api-gateway/           # NOUVEAU
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── openapi.yaml
│   ├── cloud-run/              # MODIFIÉ
│   │   └── main.tf            # Remove public access
│   └── load-balancer/          # MODIFIÉ
│       └── main.tf            # Route to API Gateway
```

#### Services Backend
```
apps/backend/
├── user-service/               # MODIFIÉ
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py     # Add API_GATEWAY_URL
│   │   └── main.py           # Remove CORS, add Gateway headers
│   └── Dockerfile             # No public exposure
├── auth-service/              # NOUVEAU (extraction)
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
└── [autres services...]       # FUTURS
```

#### Configuration GitHub Actions
```
.github/workflows/
├── deploy-api-gateway.yml     # NOUVEAU
├── deploy-user-service.yml    # MODIFIÉ (via Gateway)
└── deploy-auth-service.yml    # NOUVEAU
```

### 3.2 Fichiers à Créer

1. **terraform/modules/api-gateway/main.tf**
   - Resource google_api_gateway_api
   - Resource google_api_gateway_api_config
   - Resource google_api_gateway_gateway

2. **terraform/modules/api-gateway/openapi.yaml**
   - OpenAPI 3.0 specification
   - Service routing definitions
   - Security schemes

3. **terraform/modules/api-gateway/variables.tf**
   - project_id, region, environment
   - service_urls mapping

4. **terraform/modules/api-gateway/outputs.tf**
   - gateway_url, api_id, config_id

5. **apps/backend/auth-service/** (Nouveau service)
   - Structure complète FastAPI
   - JWT management extrait
   - Session handling

6. **.github/workflows/deploy-api-gateway.yml**
   - Terraform deployment workflow
   - OpenAPI validation
   - Gateway configuration update

### 3.3 Fichiers à Modifier

1. **terraform/environments/staging/main.tf**
   - Ajouter module API Gateway
   - Modifier les backends Cloud Run

2. **terraform/environments/production/main.tf**
   - Même structure que staging

3. **apps/backend/user-service/app/core/config.py**
   - Ajouter API_GATEWAY_URL
   - Modifier CORS settings

4. **apps/backend/user-service/app/main.py**
   - Retirer CORS middleware
   - Ajouter Gateway headers validation

5. **apps/backend/user-service/app/core/iap_middleware.py**
   - Adapter pour Gateway context
   - Ajouter bypass pour internal calls

## 4. Plan d'Implémentation

### Phase 1: Configuration de Base (Semaine 1)

#### Jour 1-2: Infrastructure Terraform
- [ ] Créer module api-gateway
- [ ] Définir OpenAPI spec v1
- [ ] Configurer routing basique

#### Jour 3-4: Integration User Service
- [ ] Modifier user-service config
- [ ] Tester routing via Gateway
- [ ] Valider IAP integration

#### Jour 5: Monitoring & Testing
- [ ] Configurer Cloud Logging
- [ ] Ajouter métriques
- [ ] Tests end-to-end

### Phase 2: Extraction Auth Service (Semaine 2)

#### Jour 1-2: Création Auth Service
- [ ] Extraire code auth de user-service
- [ ] Créer structure service
- [ ] Configurer database

#### Jour 3-4: Integration Gateway
- [ ] Ajouter routes auth dans OpenAPI
- [ ] Déployer auth-service
- [ ] Migrer endpoints

#### Jour 5: Migration & Tests
- [ ] Migrer clients vers nouveaux endpoints
- [ ] Tests de régression
- [ ] Documentation API

## 5. Livrables Attendus

### 5.1 Infrastructure
1. **API Gateway Déployée**
   - URL: https://api-gateway-staging.emacsah.com
   - Version: v1
   - Endpoints documentés

2. **Terraform Modules**
   - Module api-gateway réutilisable
   - Configuration staging/production
   - Variables environnement

3. **OpenAPI Specification**
   - Format: OpenAPI 3.0
   - Toutes les routes documentées
   - Schémas de sécurité

### 5.2 Services
1. **User Service Modifié**
   - Sans exposition publique
   - Headers Gateway validés
   - CORS désactivé

2. **Auth Service Créé**
   - JWT management
   - Session handling
   - Rate limiting

3. **Workflows CI/CD**
   - Deploy API Gateway
   - Deploy Auth Service
   - Tests automatisés

### 5.3 Documentation
1. **Architecture Diagram**
   - Flux de données
   - Components interaction
   - Security boundaries

2. **API Documentation**
   - Endpoints catalogue
   - Authentication guide
   - Migration guide

3. **Runbook Opérationnel**
   - Deployment procedures
   - Rollback strategy
   - Monitoring alerts

## 6. Métriques de Succès

### Performance
- **Latence:** < 50ms overhead Gateway
- **Throughput:** > 10,000 req/sec
- **Availability:** 99.9% SLA

### Sécurité
- **IAP Integration:** 100% endpoints protégés
- **Rate Limiting:** Actif sur tous les endpoints
- **JWT Validation:** Centralisée

### Opérationnel
- **Deployment Time:** < 10 minutes
- **Rollback Time:** < 5 minutes
- **Alert Coverage:** 100% critical paths

## 7. Risques et Mitigations

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Latence supplémentaire | Moyen | Faible | CDN caching, optimisation routes |
| Configuration complexe | Haut | Moyen | IaC, tests automatisés |
| Breaking changes | Haut | Faible | Versioning API strict |
| Coûts supplémentaires | Faible | Moyen | Monitoring usage, quotas |

## 8. Prochaines Étapes

1. **Immédiat:**
   - Créer branche feature/api-gateway
   - Initialiser module Terraform
   - Définir OpenAPI spec v1

2. **Court terme (1 semaine):**
   - Déployer Gateway staging
   - Intégrer user-service
   - Valider avec tests E2E

3. **Moyen terme (2 semaines):**
   - Extraire auth-service
   - Migrer tous les endpoints
   - Déployer en production

## 9. Références

### Documentation Technique
- [Google Cloud API Gateway](https://cloud.google.com/api-gateway/docs)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Cloud Run Integration](https://cloud.google.com/api-gateway/docs/quickstart-console)

### Fichiers Projet
- `terraform/modules/api-gateway/` - Configuration IaC
- `docs/api/openapi.yaml` - Spécification API
- `.github/workflows/deploy-api-gateway.yml` - CI/CD

---

**Document de Référence**  
Ce document servira de source de vérité pour l'implémentation de l'API Gateway et toutes les modifications futures de l'architecture.

**Prochaine Action:** Validation du plan et début de l'implémentation du module Terraform API Gateway.