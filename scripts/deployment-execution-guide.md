# 🚀 Guide d'Exécution - Déploiement Massif SkillForge AI Backend

## 📋 Vue d'Ensemble

Cette stratégie déploie **21 services backend** en **5 batches optimisés** avec monitoring en temps réel et validation automatique.

### 🎯 Objectifs
- Déploiement parallèle par batches pour optimiser les performances
- Configuration sécurisée avec `ingress=internal-and-cloud-load-balancing`
- Monitoring et validation automatique
- Gestion des dépendances entre services

---

## 📊 Plan de Déploiement par Batches

### 🔴 BATCH 1 - SERVICES CRITIQUES CORE (4 services)
**Priorité**: Maximum - Aucune dépendance
```
- subscription-service     (gestion abonnements)
- payment-service         (paiements critiques)
- notification-service    (communications)
- storage-service         (stockage fichiers)
```

### 🟡 BATCH 2 - SERVICES FONCTIONNELS (4 services)
**Priorité**: Haute - Dépendent du Batch 1
```
- content-service         (contenu cours)
- search-service          (recherche)
- project-service         (projets utilisateurs)
- audit-service           (compliance/security)
```

### 🟢 BATCH 3 - SERVICES AVANCÉS (4 services)
**Priorité**: Moyenne - Dépendent des Batches 1&2
```
- matching-service        (matchmaking)
- workflow-service        (orchestration)
- portfolio-service       (portfolios)
- evaluation-service      (évaluations)
```

### 🔵 BATCH 4 - SERVICES COMMUNICATION (3 services)
**Priorité**: Moyenne - Indépendants
```
- chat-messaging-service  (messagerie)
- realtime-collaboration-service (temps réel)
- scheduling-service      (planification)
```

### 🟣 BATCH 5 - SERVICES INTELLIGENCE (5 services)
**Priorité**: Basse - Dépendent de tous les autres
```
- recommendation-service  (IA recommendations)
- ai-orchestrator-service (IA orchestration)
- gamification-service    (gamification)
- localization-service    (i18n)
- integration-service     (intégrations externes)
```

---

## 🛠️ Scripts Disponibles

### 1. **Correction des Configurations**
```bash
# Corriger tous les cloudbuild.yaml avec les bonnes valeurs
bash scripts/fix-cloudbuild-configs.sh
```

### 2. **Déploiement par Batch**
```bash
# Déployer un batch spécifique
bash scripts/batch-deploy-commands.sh 1    # Batch 1 uniquement
bash scripts/batch-deploy-commands.sh 2    # Batch 2 uniquement
bash scripts/batch-deploy-commands.sh all  # Tous les batches en séquence
```

### 3. **Monitoring et Validation**
```bash
# Dashboard en temps réel
bash scripts/monitor-and-validate-deployments.sh monitor

# Validation complète
bash scripts/monitor-and-validate-deployments.sh validate

# Test de santé d'un service
bash scripts/monitor-and-validate-deployments.sh health-check subscription-service
```

### 4. **Correction des Settings Ingress**
```bash
# Correction massive des ingress settings
bash scripts/fix-ingress-settings-massive.sh
```

---

## 🚀 Procédure d'Exécution Recommandée

### Phase 1: Préparation
```bash
# 1. Corriger les configurations
bash scripts/fix-cloudbuild-configs.sh

# 2. Créer les dossiers de logs
mkdir -p logs

# 3. Vérifier l'authentification GCP
gcloud auth list
gcloud config set project skillforge-ai-mvp-25
```

### Phase 2: Déploiement Progressif
```bash
# 1. Démarrer le monitoring (terminal séparé)
bash scripts/monitor-and-validate-deployments.sh monitor

# 2. Déployer par batches avec monitoring
bash scripts/batch-deploy-commands.sh 1
# Attendre validation, puis continuer

bash scripts/batch-deploy-commands.sh 2
# Attendre validation, puis continuer

# Et ainsi de suite...
```

### Phase 3: Validation Finale
```bash
# 1. Validation complète
bash scripts/monitor-and-validate-deployments.sh validate

# 2. Correction des ingress si nécessaire
bash scripts/fix-ingress-settings-massive.sh

# 3. Dashboard final
bash scripts/monitor-and-validate-deployments.sh dashboard
```

---

## ⚡ Déploiement Express (Tout en Une)

Pour un déploiement complet automatisé:

```bash
# Correction + Déploiement + Validation
bash scripts/fix-cloudbuild-configs.sh && \
bash scripts/batch-deploy-commands.sh all && \
bash scripts/fix-ingress-settings-massive.sh && \
bash scripts/monitor-and-validate-deployments.sh validate
```

---

## 🔧 Configuration Critique

### Settings Cloud Run Obligatoires
- **Ingress**: `internal-and-cloud-load-balancing` (SÉCURITÉ)
- **Registry**: `europe-west1-docker.pkg.dev/skillforge-ai-mvp-25/skillforge-ai-registry`
- **Port**: `8000`
- **Memory**: `1Gi`
- **CPU**: `1`
- **Region**: `europe-west1`

### Variables d'Environnement Standardisées
```yaml
ENVIRONMENT: production
SERVICE_NAME: ${_SERVICE_NAME}
POSTGRES_HOST: 127.0.0.1
POSTGRES_PORT: 5432
POSTGRES_DB: skillforge_db
POSTGRES_USER: skillforge_user
POSTGRES_PASSWORD: Psaumes@27
DATABASE_URL: postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db
```

---

## 📈 Monitoring et Métriques

### Dashboard en Temps Réel
Le script de monitoring affiche:
- Status de chaque service par batch
- Progression des builds actifs
- Taux de réussite global
- Tests de santé HTTP
- Logs récents

### Validation Automatique
Chaque service est validé sur:
- ✅ Existence et statut "Ready"
- ✅ Configuration ingress correcte
- ✅ Test de santé HTTP (/health et /)
- ✅ Logs sans erreurs critiques

---

## 🚨 Gestion des Échecs

### En Cas d'Échec de Build
1. Consulter les logs: `cat logs/build_[service].log`
2. Corriger le problème dans le code source
3. Relancer le build: `bash scripts/batch-deploy-commands.sh [batch]`

### En Cas d'Échec de Validation
1. Vérifier les logs Cloud Run
2. Tester manuellement les endpoints
3. Corriger les configurations si nécessaire
4. Utiliser les commandes de correction automatique

---

## 📋 Checklist Post-Déploiement

- [ ] Tous les services affichent "Ready: True"
- [ ] Ingress = "internal-and-cloud-load-balancing"
- [ ] Tests de santé HTTP passent
- [ ] Aucune erreur critique dans les logs
- [ ] Services accessible via leurs URLs
- [ ] Base de données PostgreSQL connectée
- [ ] Monitoring actif et fonctionnel

---

## 🎯 Résultats Attendus

**Services Déployés**: 21 services backend
**Temps Estimé**: 45-60 minutes (avec monitoring)
**Taux de Réussite Cible**: 100%
**Configuration**: Production-ready avec sécurité optimale

---

*Stratégie créée pour SkillForge AI - Déploiement Massif Backend Services*