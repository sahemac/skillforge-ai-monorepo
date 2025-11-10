# Guide - Déploiement Canary

## Vue d'ensemble

Le déploiement canary est une stratégie de déploiement progressif qui permet de déployer une nouvelle version en production en exposant d'abord un petit pourcentage d'utilisateurs, puis en augmentant progressivement ce pourcentage tout en surveillant les métriques.

**Avantages**:
- ✅ Réduction des risques en production
- ✅ Détection rapide des problèmes
- ✅ Rollback automatique sur erreurs
- ✅ Validation progressive avec vrai trafic utilisateur

**Quand l'utiliser**:
- Changements importants d'architecture
- Nouvelles features à risque
- Modifications critiques de performance
- Après une période de stabilité sans déploiements

## Workflow Canary

**Fichier**: `.github/workflows/canary-deployment.yml`

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Préparation                                        │
│ • Identification du service                                 │
│ • Récupération révision actuelle                           │
│ • Affichage du plan canary                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Déploiement nouvelle révision (0% trafic)         │
│ • Build et push nouvelle image                             │
│ • Déploiement Cloud Run avec --no-traffic                  │
│ • Tag canary appliqué                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Canary 10% ⏸ Approval required                    │
│ • Router 10% du trafic vers canary                         │
│ • Monitoring 5 minutes                                      │
│ • Vérification erreurs (seuil: 10 erreurs/min)            │
│ • Auto-rollback si seuil dépassé                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Canary 50% ⏸ Approval required                    │
│ • Router 50% du trafic vers canary                         │
│ • Monitoring 5 minutes                                      │
│ • Vérification erreurs (seuil: 10 erreurs/min)            │
│ • Auto-rollback si seuil dépassé                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Canary 100% ⏸ Approval required                   │
│ • Router 100% du trafic vers canary                        │
│ • Health check final                                        │
│ • Déploiement canary terminé                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ✅ Complet!
```

## Utilisation

### Déclencher un déploiement canary

**Via GitHub Actions UI**:
1. Aller sur Actions → Canary Deployment
2. Cliquer "Run workflow"
3. Sélectionner le service (shell, user-service, company-service)
4. Confirmer

**Via GitHub CLI**:
```bash
gh workflow run canary-deployment.yml \
  -f service=shell
```

**Via API GitHub**:
```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/canary-deployment.yml/dispatches \
  -d '{"ref":"main","inputs":{"service":"shell"}}'
```

### Services disponibles

| Service | Nom pour workflow | Description |
|---------|-------------------|-------------|
| Frontend Shell | `shell` | Application frontend principale |
| User Service API | `user-service` | API de gestion utilisateurs |
| Company Service API | `company-service` | API de gestion entreprises |

## Monitoring pendant le canary

### Métriques surveillées

**Automatiquement** (par le workflow):
- Nombre d'erreurs dans les logs Cloud Logging
- Seuil: > 10 erreurs par minute déclenche rollback

**Manuellement** (à surveiller):
1. **Latence**:
   ```bash
   # Via gcloud
   gcloud monitoring time-series list \
     --filter='metric.type="run.googleapis.com/request_latencies"'
   ```

2. **Taux d'erreur**:
   ```bash
   # Via logs
   gcloud logging read \
     "resource.type=cloud_run_revision \
      AND resource.labels.service_name=skillforge-frontend-shell-production \
      AND severity>=ERROR" \
     --limit=50 \
     --format=json
   ```

3. **Requests per second**:
   ```bash
   gcloud monitoring time-series list \
     --filter='metric.type="run.googleapis.com/request_count"'
   ```

### Dashboard Cloud Monitoring

Accédez au dashboard:
```
https://console.cloud.google.com/monitoring/dashboards?project=skillforge-ai-mvp-25
```

Métriques clés à surveiller:
- Request latency (p50, p95, p99)
- Error rate
- CPU utilization
- Memory utilization
- Request count

## Rollback

### Automatique

Le workflow effectue un rollback automatique si:
- > 10 erreurs par minute détectées
- Health check échoue
- Timeout de monitoring dépassé

### Manuel

#### Option 1: Via le script helper

```bash
cd /path/to/repo
./scripts/canary-rollback.sh skillforge-frontend-shell-production
```

Le script:
1. Affiche le split de trafic actuel
2. Identifie la révision stable précédente
3. Demande confirmation
4. Effectue le rollback
5. Vérifie le health check

#### Option 2: Via gcloud CLI

```bash
# 1. Lister les révisions
gcloud run revisions list \
  --service=skillforge-frontend-shell-production \
  --region=europe-west1 \
  --format="table(metadata.name,status.conditions[0].status,metadata.creationTimestamp)"

# 2. Identifier la révision stable
STABLE_REVISION="skillforge-frontend-shell-production-00042-abc"

# 3. Rollback
gcloud run services update-traffic skillforge-frontend-shell-production \
  --region=europe-west1 \
  --to-revisions=$STABLE_REVISION=100

# 4. Vérifier
gcloud run services describe skillforge-frontend-shell-production \
  --region=europe-west1 \
  --format="table(status.traffic[].revisionName,status.traffic[].percent)"
```

#### Option 3: Via Console GCP

1. Aller sur [Cloud Run Console](https://console.cloud.google.com/run)
2. Sélectionner le service
3. Onglet "Revisions"
4. Cliquer sur la révision stable
5. "Manage traffic" → Router 100% vers cette révision

## Bonnes pratiques

### Avant le canary

- [ ] Code testé et validé en staging
- [ ] E2E tests passés
- [ ] Équipe disponible pour monitoring
- [ ] Documentation des changements
- [ ] Plan de rollback préparé
- [ ] Backup base de données effectué (si migrations)

### Pendant le canary

- [ ] Surveiller le dashboard Cloud Monitoring
- [ ] Vérifier les logs en temps réel
- [ ] Tester manuellement les fonctionnalités critiques
- [ ] Être prêt à rollback rapidement
- [ ] Documenter tout comportement anormal

### Après le canary

- [ ] Vérifier métriques sur 24h
- [ ] Documenter les observations
- [ ] Post-mortem si incidents
- [ ] Mise à jour documentation si nécessaire

## Scénarios courants

### Scénario 1: Déploiement réussi

```
1. Canary lancé manuellement
2. 10% → OK après 5 min → Approbation
3. 50% → OK après 5 min → Approbation
4. 100% → Health check OK
5. ✅ Déploiement terminé
```

**Durée totale**: ~20-25 minutes

### Scénario 2: Erreurs détectées à 10%

```
1. Canary lancé
2. 10% → Erreurs détectées (> 10/min)
3. ❌ Auto-rollback déclenché
4. Trafic 100% sur version stable
5. Investigation et correction
```

**Actions**:
- Consulter les logs d'erreurs
- Identifier la cause racine
- Corriger en staging
- Réessayer le canary

### Scénario 3: Problème découvert à 50%

```
1. Canary lancé
2. 10% → OK → Approbation
3. 50% → Problème de performance observé manuellement
4. Pause du workflow (ne pas approuver 100%)
5. Rollback manuel effectué
```

**Actions**:
```bash
# Rollback manuel immédiat
./scripts/canary-rollback.sh skillforge-frontend-shell-production

# Ou via gcloud
gcloud run services update-traffic skillforge-frontend-shell-production \
  --region=europe-west1 \
  --to-revisions=STABLE_REVISION=100
```

## Troubleshooting

### Le workflow est bloqué à l'approbation

**Cause**: Environnement GitHub non configuré ou pas d'approbateurs

**Solution**:
1. Aller sur Settings → Environments → `production-canary-10`
2. Configurer les reviewers requis
3. Sauvegarder et réessayer

### Auto-rollback se déclenche immédiatement

**Cause**: Seuil d'erreurs trop bas ou logs mal configurés

**Solution**:
1. Vérifier les logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision \
     AND severity>=ERROR" --limit=50
   ```
2. Ajuster le seuil dans le workflow si nécessaire
3. Vérifier que les erreurs ne sont pas des false positives

### Canary URL inaccessible

**Cause**: Tag canary pas correctement appliqué

**Solution**:
```bash
# Vérifier les tags
gcloud run services describe skillforge-frontend-shell-production \
  --region=europe-west1 \
  --format="value(status.traffic[].tag)"

# Réappliquer le tag
gcloud run services update-traffic skillforge-frontend-shell-production \
  --region=europe-west1 \
  --update-tags=canary=NEW_REVISION
```

### Split de trafic incorrect

**Cause**: Commande gcloud mal formée

**Solution**:
```bash
# Vérifier le split actuel
gcloud run services describe skillforge-frontend-shell-production \
  --region=europe-west1 \
  --format="table(status.traffic[].revisionName,status.traffic[].percent)"

# Corriger manuellement
gcloud run services update-traffic skillforge-frontend-shell-production \
  --region=europe-west1 \
  --to-revisions=REVISION1=10,REVISION2=90
```

## Monitoring avancé

### Alertes personnalisées

Créer des alertes Cloud Monitoring:

```bash
# Alerte sur taux d'erreur élevé
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Canary Error Rate High" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

### Logs structurés

Rechercher des patterns spécifiques:

```bash
# Erreurs 5xx
gcloud logging read \
  "resource.type=cloud_run_revision \
   AND httpRequest.status>=500 \
   AND httpRequest.status<600" \
  --limit=100 \
  --format=json

# Latence élevée
gcloud logging read \
  "resource.type=cloud_run_revision \
   AND httpRequest.latency>2s" \
  --limit=100
```

### Métriques custom

Si vous avez des métriques custom dans votre application:

```bash
gcloud monitoring time-series list \
  --filter='metric.type="custom.googleapis.com/your_metric"' \
  --interval-start-time="5 minutes ago"
```

## Checklist déploiement canary

### Pré-déploiement
- [ ] Tests passés en staging
- [ ] Documentation changements préparée
- [ ] Équipe alertée et disponible
- [ ] Dashboard monitoring ouvert
- [ ] Plan de rollback documenté
- [ ] Backup base de données (si nécessaire)

### Canary 10%
- [ ] Workflow approuvé
- [ ] Pas d'erreurs dans les logs
- [ ] Latence normale
- [ ] Tests manuels fonctionnalités critiques
- [ ] Métriques CPU/Memory normales

### Canary 50%
- [ ] 10% réussi sans problèmes
- [ ] Workflow approuvé
- [ ] Monitoring continu (5 min)
- [ ] Vérification dashboard
- [ ] Tests charge si nécessaire

### Canary 100%
- [ ] 50% réussi sans problèmes
- [ ] Workflow approuvé
- [ ] Health check final OK
- [ ] Documentation mise à jour
- [ ] Équipe notifiée du succès

### Post-déploiement
- [ ] Monitoring 24h
- [ ] Vérification métriques
- [ ] Feedback utilisateurs
- [ ] Post-mortem si incidents
- [ ] Leçons apprises documentées

## Ressources

- [CI/CD Architecture](./CI_CD_ARCHITECTURE.md)
- [Production Deployment](./PRODUCTION_DEPLOYMENT.md)
- [Cloud Run Traffic Management](https://cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration)
- [Canary Deployments Best Practices](https://cloud.google.com/architecture/application-deployment-and-testing-strategies)

## Support

Pour toute question sur les déploiements canary:
- **Slack**: #devops channel
- **Documentation**: Ce guide
- **Incidents**: Créer une issue avec label `canary-deployment`
