# Sécurité - SkillForge AI User Service

## ⚠️ Configuration Sécurisée Requise

### 🔐 Variables d'Environnement Obligatoires

**JAMAIS** exposer les secrets dans le code source. Utilisez exclusivement les variables d'environnement:

```bash
# Configuration minimale pour PostgreSQL
export POSTGRES_PASSWORD="your-secure-password"
export SECRET_KEY="your-secret-key"

# Configuration complète
export DATABASE_URL="postgresql+asyncpg://skillforge_user:${POSTGRES_PASSWORD}@localhost:5432/skillforge_db"
export POSTGRES_USER="skillforge_user"
export POSTGRES_PASSWORD="your-secure-password"
export POSTGRES_DB="skillforge_db"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
```

### 🛡️ Déploiement Sécurisé

#### Développement Local
```bash
# 1. Copier le template
cp .env.example .env

# 2. Modifier .env avec vos valeurs
# ATTENTION: .env est dans .gitignore

# 3. Démarrer avec les variables d'environnement
source .env
python migrate_to_postgresql.py
```

#### Production
```bash
# Google Cloud Run
gcloud run deploy user-service \
  --set-env-vars="POSTGRES_PASSWORD=from-secret-manager" \
  --set-env-vars="SECRET_KEY=from-secret-manager"

# Docker
docker run -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
           -e SECRET_KEY="$SECRET_KEY" \
           skillforge-user-service

# Kubernetes
kubectl create secret generic db-credentials \
  --from-literal=password="$POSTGRES_PASSWORD"
```

### 🔒 Sécurité des Mots de Passe

#### Génération Sécurisée
```bash
# Secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Mot de passe PostgreSQL (Cloud SQL)
openssl rand -base64 32
```

#### Gestion des Secrets
- **Google Cloud**: Secret Manager
- **AWS**: Systems Manager Parameter Store
- **Azure**: Key Vault
- **Kubernetes**: Secrets
- **Docker**: Docker Secrets

### 📋 Checklist de Sécurité

#### ✅ Configuration
- [ ] Mots de passe via variables d'environnement uniquement
- [ ] `.env` dans `.gitignore`
- [ ] `SECRET_KEY` unique et sécurisé
- [ ] `POSTGRES_PASSWORD` depuis un gestionnaire de secrets

#### ✅ Base de Données
- [ ] Connexions SSL en production
- [ ] Utilisateur dédié avec permissions minimales
- [ ] Sauvegarde chiffrée
- [ ] Logs d'audit activés

#### ✅ API
- [ ] HTTPS obligatoire en production
- [ ] Rate limiting activé
- [ ] CORS configuré correctement
- [ ] Validation d'entrée stricte

### 🚨 Erreurs de Sécurité à Éviter

#### ❌ JAMAIS
```python
# JAMAIS de mots de passe en dur
password = "Psaumes@27"
url = "postgresql://user:password@host/db"

# JAMAIS de secrets dans le code
DATABASE_URL = "postgresql://skillforge_user:secret@localhost/db"
```

#### ✅ TOUJOURS
```python
# Variables d'environnement
password = os.getenv("POSTGRES_PASSWORD")
if not password:
    raise ValueError("POSTGRES_PASSWORD is required")

# URL construite de manière sécurisée
from urllib.parse import quote_plus
encoded_password = quote_plus(password)
url = f"postgresql://{user}:{encoded_password}@{host}/{db}"
```

### 📞 Contact Sécurité

En cas de découverte de vulnérabilité:
1. **NE PAS** créer d'issue publique GitHub
2. Contacter directement l'équipe sécurité
3. Fournir les détails en privé

### 🔄 Rotation des Secrets

#### Fréquence Recommandée
- `SECRET_KEY`: 90 jours
- `POSTGRES_PASSWORD`: 30 jours
- `SMTP_PASSWORD`: 60 jours

#### Procédure
1. Générer nouveau secret
2. Mettre à jour variables d'environnement
3. Redéployer service
4. Valider fonctionnement
5. Révoquer ancien secret

---

**Note**: Ce document doit être mis à jour à chaque changement de configuration sécuritaire.