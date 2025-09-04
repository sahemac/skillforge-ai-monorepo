# 🚀 Guide de Configuration Rapide - Pipeline Terraform

## ⚡ Actions Immédiates (Pendant que GCP se répare)

### 1. Configuration GitHub - À FAIRE MAINTENANT

Les secrets ont été générés avec succès. Configurez GitHub immédiatement :

#### A. Créer les Environments GitHub

1. Allez sur **votre repository GitHub**
2. **Settings** → **Environments** → **New environment**
3. Créez `staging`:
   - Protection rules: ✅ Required reviewers (vous-même)
   - Deployment branches: `develop` et `main`
4. Créez `production`:
   - Protection rules: ✅ Required reviewers + ✅ Wait timer (30 min)
   - Deployment branches: `main` seulement

#### B. Ajouter les Environment Secrets

**Dans l'environment `staging`:**
```
Name: TF_VAR_jwt_secret
Value: elrJxPx8kEhSrZTkSVL5kB+ldq0Khgyi143DTSAsSAdIs/CaFVg2ocoL9Cnzoq0E

Name: TF_VAR_postgres_password
Value: /OeuzN5Xj+Q3MsT4AVUj3tTn0x5XSkUvkiSLyxfwcN8=
```

**Dans l'environment `production`:**
```
Name: TF_VAR_jwt_secret
Value: sX7sNX4k/j65iNG5x/Pn3a0eDbL+88s7Tt9jIt9dqSgttNU1umVm9MM5VrpCSI6v

Name: TF_VAR_postgres_password
Value: qHnYEtQHfBYV3ATG8czX46+JgFA0iLFi+AMY/3f9h+U=
```

### 2. Correction de l'Authentification GCP

Exécutez ces commandes **dans l'ordre** :

```powershell
# 1. Ré-authentification complète
gcloud auth login --force

# 2. Application Default Credentials
gcloud auth application-default login

# 3. Définir le projet actif
gcloud config set project skillforge-ai-mvp-25

# 4. Vérifier l'authentification
gcloud auth list
```

### 3. Nettoyage des Ressources Partielles (si nécessaire)

Si des ressources ont été créées partiellement :

```powershell
# Supprimer le service account (si existant)
gcloud iam service-accounts delete terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com --quiet

# Supprimer le workload identity pool (si existant)  
gcloud iam workload-identity-pools delete github-actions --location=global --quiet
```

### 4. Nouvelle Tentative avec le Bon Paramètre

Une fois l'authentification réparée :

```powershell
# Trouver votre nom d'utilisateur GitHub
git remote get-url origin

# Puis lancer avec le bon format : USERNAME/REPO
.\setup-github-secrets.ps1 -RepoName "VOTRE-USERNAME/skillforge-ai-monorepo"
```

## 🔍 Diagnostic des Problèmes

### Problème 1: Authentication Failed
```
ERROR: Reauthentication failed. cannot prompt during non-interactive execution
```
**Solution**: `gcloud auth login --force`

### Problème 2: Permission Denied
```
ERROR: You do not have permission to access project
```
**Solution**: Vérifiez que `sah@emacsah.com` a les droits Owner/Editor sur `skillforge-ai-mvp-25`

### Problème 3: Repository Parameter
```
Repository: staging (au lieu de USERNAME/REPO)
```
**Solution**: Utiliser `-RepoName "USERNAME/skillforge-ai-monorepo"`

## ✅ Checklist de Vérification

- [ ] GitHub Environments créés (staging + production)
- [ ] Environment Secrets configurés avec les valeurs générées
- [ ] GCloud réauthentifié avec `gcloud auth login --force`
- [ ] Application Default Credentials configurées
- [ ] Projet GCP actif défini sur `skillforge-ai-mvp-25`
- [ ] Script relancé avec le bon paramètre de repository

## 🚀 Test du Pipeline (Une fois tout configuré)

1. **Test local d'abord** :
```powershell
.\test-pipeline-local.ps1 -Environment staging
```

2. **Test avec PR** :
```bash
git checkout -b test-terraform-pipeline
echo "# Test change" >> README.md
git add .
git commit -m "test: trigger terraform pipeline"
git push origin test-terraform-pipeline
```

3. **Créer une PR** et vérifier que le pipeline s'exécute

## 🎯 Objectif Immédiat

**PRIORITÉ 1** : Configurez GitHub (étape 1) - les secrets sont prêts !
**PRIORITÉ 2** : Réparez l'authentification GCP (étapes 2-4)

Le pipeline peut commencer à fonctionner partiellement même sans la config GCP complète, car les secrets d'environnement sont déjà générés et prêts.

---

**⏰ Temps estimé** : 15 minutes pour GitHub + 10 minutes pour GCP
**🎯 Résultat** : Pipeline Terraform complètement fonctionnel