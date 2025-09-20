# 🔧 Migration Troubleshooting Guide

*Généré le: 2025-01-23*
*Service: SkillForge User Service*

## 🚨 Problèmes Récents Corrigés

### 1. **Sécurité - Mots de passe exposés**
- ❌ **Problème**: Vraies credentials dans les exemples de documentation
- ✅ **Solution**: Remplacement par des placeholders sécurisés
- 📁 **Fichier**: `run_migrations.py` ligne 174

### 2. **Erreur Pydantic - POSTGRES_PORT vide**
- ❌ **Problème**: `ValidationError: Input should be a valid integer, unable to parse string as an integer [input_value='']`
- ✅ **Solution**: POSTGRES_PORT fixé à `"5432"` au lieu d'expression conditionnelle
- 📁 **Fichier**: `.github/workflows/run-alembic-migration.yml` ligne 181

### 3. **Erreur DNS CI/CD - "Name or service not known"**
- ❌ **Problème**: Cloud SQL Proxy non accessible dans l'environnement CI/CD
- ✅ **Solutions ajoutées**:
  - Test de connectivité avant migration
  - Diagnostic réseau détaillé
  - Vérification du processus proxy
  - Logging amélioré dans `run_migrations.py`

### 4. **Nom de fichier incorrect**
- ❌ **Problème**: Workflow appelait `run_migration.py` (sans 's')
- ✅ **Solution**: Correction vers `run_migrations.py`

## 🔍 Diagnostics Ajoutés

### Workflow CI/CD
```yaml
# Test de connectivité avant migration
if timeout 10 bash -c 'until nc -z localhost 5432; do sleep 1; done'; then
  echo "✅ Cloud SQL Proxy connection successful"
else
  echo "❌ Cannot connect to Cloud SQL Proxy"
  ps aux | grep cloud-sql-proxy
  netstat -tuln | grep 5432
  exit 1
fi
```

### Script de Migration
```python
# Diagnostic réseau détaillé
try:
    socket.gethostbyname(host)  # Test DNS
    sock.connect_ex((host, port))  # Test TCP
except Exception as debug_e:
    logger.error(f"DEBUG: {debug_e}")
```

## 📋 Checklist de Résolution

### ✅ **Corrigé**
- [x] Sécurité des credentials dans la documentation
- [x] Validation Pydantic POSTGRES_PORT
- [x] Nom de fichier script migration
- [x] Diagnostics de connectivité CI/CD
- [x] Logging détaillé des erreurs réseau

### 🔄 **À Tester**
- [ ] Déploiement CI/CD complet
- [ ] Migration sur Cloud SQL via proxy
- [ ] Fallback vers DATABASE_URL si Secret Manager échoue

## 🎯 **Prochaines Étapes Recommandées**

1. **Test du workflow corrigé** : Déclencher une nouvelle exécution
2. **Monitoring des logs** : Vérifier les nouveaux diagnostics
3. **Validation Secret Manager** : S'assurer que le secret `postgres-password` existe
4. **Test manuel** : Vérifier Cloud SQL Proxy en local si nécessaire

## 🔗 **Liens Utiles**

- **Workflow Migration**: `.github/workflows/run-alembic-migration.yml`
- **Script Migration**: `apps/backend/user-service/run_migrations.py`
- **Configuration Alembic**: `apps/backend/user-service/alembic/env.py`
- **Terraform Cloud SQL**: `terraform/modules/cloud_sql/`

---
*Guide généré suite aux corrections de sécurité et connectivité*