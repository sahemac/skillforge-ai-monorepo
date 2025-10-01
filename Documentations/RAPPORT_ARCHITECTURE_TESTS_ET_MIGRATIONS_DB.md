# Rapport d'Architecture : Tests de Base de Données et Migrations

## Date : 1er Octobre 2025
## Service : user-service
## Contexte : Intégration PostgreSQL pour Tests CI/CD

---

## 1. Résumé Exécutif

### Problème Initial
Les tests du service `user-service` échouaient systématiquement dans le workflow GitHub Actions avec l'erreur :
```
relation 'users' does not exist
```

### Solution Implémentée
Mise en place d'une **base de données PostgreSQL temporaire** dans le workflow CI/CD, avec création automatique du schéma avant l'exécution des tests.

### Résultat
✅ Infrastructure de tests fonctionnelle avec PostgreSQL temporaire
✅ Tables créées automatiquement : `['users', 'user_settings', 'user_sessions']`
✅ Isolation totale : aucun impact sur staging/production

---

## 2. Architecture des Tests vs Migrations : Différence Critique

### 2.1 Tests de Base de Données (Phase 1 du Workflow)

**Objectif** : Valider la LOGIQUE du code, PAS le schéma de la base de données

**Infrastructure** :
- Base de données : **PostgreSQL 15-alpine (temporaire)**
- Cycle de vie : **Créée et détruite à chaque run du workflow**
- Données : **Aucune donnée persistante**
- Schéma : **Créé via SQLModel.metadata.create_all()**

**Workflow d'exécution** :
```
1. GitHub Actions démarre le service PostgreSQL (Docker container)
2. Fixture test_db_setup exécute _setup_test_database()
3. SQLModel.metadata.create_all() crée les tables
4. Tests s'exécutent
5. Container PostgreSQL est détruit
6. Toutes les données sont perdues
```

**Localisation dans le code** :
- Fichier : `apps/backend/user-service/app/tests/conftest.py`
- Fonction : `_setup_test_database()` (lignes 86-109)
- Fixture : `test_db_setup` (lignes 132-137)

**Configuration du workflow** :
```yaml
# .github/workflows/deploy-service.yml

services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_USER: skillforge_test
      POSTGRES_PASSWORD: test_password_secure_123
      POSTGRES_DB: skillforge_test_db
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

**Variables d'environnement des tests** :
```yaml
DATABASE_URL: postgresql+asyncpg://skillforge_test:test_password_secure_123@localhost:5432/skillforge_test_db
ENVIRONMENT: testing
```

### 2.2 Migrations de Base de Données (Phase 3 du Workflow)

**Objectif** : Modifier le SCHÉMA de la base de données de production/staging

**Infrastructure** :
- Base de données : **Cloud SQL PostgreSQL (persistant)**
- Cycle de vie : **Permanente, données critiques**
- Données : **Données de production/staging**
- Schéma : **Modifié via Alembic migrations**

**Workflow d'exécution** :
```
1. Service déployé sur Cloud Run
2. Cloud SQL Proxy établit la connexion sécurisée
3. Alembic lit les migrations dans apps/backend/user-service/alembic/versions/
4. Alembic applique les migrations sur la base réelle
5. Schéma modifié de manière PERMANENTE
6. Données utilisateurs conservées
```

**Localisation** :
- Migrations : `apps/backend/user-service/alembic/versions/`
- Configuration : `apps/backend/user-service/alembic.ini`
- Script : `apps/backend/user-service/scripts/migrate.sh`

**Variables d'environnement de migration** :
```bash
DATABASE_URL: postgresql+asyncpg://[USER]:[PASSWORD]@/[DB]?host=/cloudsql/[CONNECTION_NAME]
ENVIRONMENT: staging|production
```

### 2.3 Tableau Comparatif : Tests vs Migrations

| Aspect | Tests (Phase 1) | Migrations (Phase 3) |
|--------|----------------|----------------------|
| **Base de données** | PostgreSQL temporaire (Docker) | Cloud SQL (GCP) |
| **Durée de vie** | Quelques minutes | Permanente |
| **Données** | Aucune / test fixtures | Données réelles utilisateurs |
| **Schéma** | Créé via SQLModel | Modifié via Alembic |
| **Risque** | ZÉRO - DB détruite après | CRITIQUE - données de prod |
| **Objectif** | Valider le code | Évoluer le schéma |
| **Connexion** | localhost:5432 | Cloud SQL Proxy |
| **Rollback** | Non nécessaire | Critique en cas d'erreur |
| **Quand** | Avant chaque déploiement | Après déploiement réussi |

---

## 3. Architecture des Phases du Workflow

### Phase 1 : Tests (Bloque le Déploiement)
```
┌─────────────────────────────────────────┐
│  GitHub Actions Runner (Ubuntu 24.04)   │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ PostgreSQL 15-alpine (Container)   │ │
│  │ - Port: 5432                       │ │
│  │ - User: skillforge_test            │ │
│  │ - DB: skillforge_test_db           │ │
│  │ - Ephemeral (détruit après tests)  │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Python Test Runner                 │ │
│  │ 1. _setup_test_database()          │ │
│  │ 2. SQLModel.metadata.create_all()  │ │
│  │ 3. pytest exécute les tests        │ │
│  │ 4. _teardown_test_database()       │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Résultat: ✅ Tests passent → Continue  │
│           ❌ Tests échouent → STOP      │
└─────────────────────────────────────────┘
```

### Phase 2 : Build & Deploy
```
┌─────────────────────────────────────────┐
│  Tests ✅ → Build Docker Image          │
│           → Push to Artifact Registry   │
│           → Deploy to Cloud Run         │
└─────────────────────────────────────────┘
```

### Phase 3 : Migrations (Après Déploiement)
```
┌─────────────────────────────────────────┐
│  Cloud Run Instance                     │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Cloud SQL Proxy                    │ │
│  │ - Connexion sécurisée              │ │
│  │ - Unix socket                      │ │
│  └────────────────────────────────────┘ │
│             ↓                            │
│  ┌────────────────────────────────────┐ │
│  │ Cloud SQL PostgreSQL               │ │
│  │ - Instance: skillforge-db-staging  │ │
│  │ - Données: PRODUCTION/STAGING      │ │
│  │ - Schéma: Modifié par Alembic      │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Alembic Migration Runner           │ │
│  │ 1. Connexion via Cloud SQL Proxy   │ │
│  │ 2. Lecture des migrations          │ │
│  │ 3. Alembic upgrade head            │ │
│  │ 4. Schéma mis à jour               │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 4. Corrections Techniques Appliquées

### 4.1 Problème : Tables Non Créées

**Symptôme** :
```
ERROR: relation "users" does not exist
```

**Cause** :
Le fixture `test_db_setup` avec `async def` et `scope="session"` n'était pas exécuté par pytest-asyncio malgré `autouse=True`.

**Solution** :
Conversion du fixture en fonction synchrone qui exécute le code async via `loop.run_until_complete()`.

**Code corrigé** :
```python
# apps/backend/user-service/app/tests/conftest.py

def _setup_test_database():
    """Synchronously set up test database schema - RUNS BEFORE ANY TESTS."""
    print("[TEST DB SETUP] Creating database tables...")

    try:
        # Run the async setup in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def create_tables():
            async with test_engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

        loop.run_until_complete(create_tables())
        loop.close()

        print("[TEST DB SETUP] Database tables created successfully")
        print(f"[TEST DB SETUP] Models registered: {list(SQLModel.metadata.tables.keys())}")
    except Exception as e:
        print(f"[TEST DB SETUP ERROR] Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        raise

@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    """Set up test database schema - runs once per test session."""
    _setup_test_database()
    yield
    _teardown_test_database()
```

**Résultat** :
```
[TEST DB SETUP] Creating database tables...
[TEST DB SETUP] Database URL: postgresql+asyncpg://skillforge_test:test_password_secure_123...
[TEST DB SETUP] Database tables created successfully
[TEST DB SETUP] Models registered: ['users', 'user_settings', 'user_sessions']
```

### 4.2 Problème : Imports de Modules Company Manquants

**Symptôme** :
```
ImportError: cannot import name 'companies_router'
ModuleNotFoundError: No module named 'app.crud.company'
```

**Cause** :
Les fonctionnalités company ont été déplacées vers `company-service` mais les imports subsistaient.

**Solution** :
Suppression de tous les imports company dans :
- `apps/backend/user-service/app/api/v1/__init__.py`
- `apps/backend/user-service/app/api/v1/endpoints/__init__.py`
- `apps/backend/user-service/app/crud/__init__.py`
- `apps/backend/user-service/app/schemas/__init__.py`
- `apps/backend/user-service/app/api/dependencies.py`

### 4.3 Problème : Email Service en Mode Test

**Symptôme** :
```
[Errno 11003] getaddrinfo failed
```

**Cause** :
Le service email tentait de se connecter à SMTP pendant les tests.

**Solution** :
Ajout d'un check `ENVIRONMENT=testing` dans `app/utils/email.py` :

```python
def send_email(...) -> bool:
    """Send email."""
    # Skip actual sending in test environment
    if settings.ENVIRONMENT == "testing":
        logger.info(f"[TEST MODE] Would send email to {to_email} with subject: {subject}")
        return True
    # ... rest of implementation
```

---

## 5. Configuration Réseau et Sécurité

### 5.1 Tests (Réseau Local)

**Connexion** :
```
Test Runner ──────► localhost:5432 ──────► PostgreSQL Container
             TCP/IP              localhost
```

**Sécurité** :
- Pas de connexion externe
- Credentials temporaires (test_password_secure_123)
- Aucune exposition sur internet
- Isolation via Docker network

### 5.2 Migrations (Réseau GCP)

**Connexion** :
```
Cloud Run ──────► Cloud SQL Proxy ──────► Cloud SQL Instance
          Unix Socket           Private IP (IAM Auth)
```

**Sécurité** :
- IAM authentication
- VPC privé
- Pas d'IP publique
- Connexion chiffrée TLS
- Cloud SQL Proxy avec workload identity

---

## 6. Pourquoi NE PAS Utiliser Cloud SQL pour les Tests ?

### ❌ Problèmes avec Cloud SQL pour Tests

1. **Risque de corruption de données**
   - Les tests pourraient modifier accidentellement des données de staging
   - Impossible de garantir l'isolation complète

2. **Coût**
   - Cloud SQL Proxy consomme des ressources
   - Connexions concurrentes coûteuses
   - Tests exécutés plusieurs fois par jour

3. **Performance**
   - Latence réseau GCP
   - Temps de connexion Cloud SQL Proxy
   - Tests devraient être rapides

4. **Complexité**
   - Configuration IAM nécessaire
   - Gestion des secrets
   - Debugging difficile

5. **Isolation**
   - Impossible de paralléliser les tests
   - Risque de collision de données entre runs simultanés

### ✅ Avantages de PostgreSQL Temporaire

1. **Isolation parfaite** - Chaque run = nouvelle DB
2. **Performance** - Connexion localhost ultra-rapide
3. **Simplicité** - Aucune configuration IAM
4. **Coût** - Gratuit (ressources GitHub Actions)
5. **Sécurité** - Aucune exposition de credentials de prod
6. **Parallélisation** - Chaque test peut avoir sa propre DB

---

## 7. Diagramme de Flux Complet

```
┌─────────────────────────────────────────────────────────────────────┐
│                       GITHUB ACTIONS WORKFLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ PHASE 1: TESTS (PostgreSQL Temporaire)                     │   │
│  │                                                             │   │
│  │  1. Start PostgreSQL Container (ephemeral)                 │   │
│  │  2. Wait for health check                                  │   │
│  │  3. Run _setup_test_database()                             │   │
│  │     - Create tables via SQLModel.metadata.create_all()     │   │
│  │  4. Execute pytest                                          │   │
│  │  5. Tests validate CODE logic                              │   │
│  │  6. Container destroyed                                     │   │
│  │                                                             │   │
│  │  DATABASE: localhost:5432 (Docker)                         │   │
│  │  SCHEMA:   Created from models                             │   │
│  │  DATA:     None (empty)                                    │   │
│  │  RISK:     ZERO                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                               │                                    │
│                               │ Tests ✅ PASS                      │
│                               ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ PHASE 2: BUILD & DEPLOY                                    │   │
│  │                                                             │   │
│  │  1. Build Docker image                                      │   │
│  │  2. Push to Artifact Registry                               │   │
│  │  3. Deploy to Cloud Run                                     │   │
│  └────────────────────────────────────────────────────────────┘   │
│                               │                                    │
│                               │ Deploy ✅ SUCCESS                  │
│                               ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ PHASE 3: MIGRATIONS (Cloud SQL Staging/Production)         │   │
│  │                                                             │   │
│  │  1. Cloud Run connects via Cloud SQL Proxy                 │   │
│  │  2. Alembic reads migration files                           │   │
│  │  3. alembic upgrade head                                    │   │
│  │  4. SCHEMA modified on REAL database                        │   │
│  │                                                             │   │
│  │  DATABASE: Cloud SQL (GCP)                                 │   │
│  │  SCHEMA:   Modified via Alembic migrations                 │   │
│  │  DATA:     REAL user data (staging/production)             │   │
│  │  RISK:     CRITICAL - requires rollback strategy           │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Commandes de Diagnostic

### 8.1 Vérifier que les Tables sont Créées (Local)

```bash
cd apps/backend/user-service
DATABASE_URL="postgresql+asyncpg://skillforge_test:test_password_secure_123@localhost:5432/skillforge_test_db" \
pytest -v -s app/tests/test_auth.py::TestUserRegistration::test_register_success
```

Les logs devraient montrer :
```
[TEST DB SETUP] Creating database tables...
[TEST DB SETUP] Database tables created successfully
[TEST DB SETUP] Models registered: ['users', 'user_settings', 'user_sessions']
```

### 8.2 Vérifier la Connexion Cloud SQL (Cloud Run)

```bash
# Depuis un terminal Cloud Run
psql "$DATABASE_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
```

### 8.3 Voir l'Historique des Migrations

```bash
cd apps/backend/user-service
alembic history
```

### 8.4 Vérifier la Version Actuelle du Schéma

```bash
cd apps/backend/user-service
DATABASE_URL="<staging_url>" alembic current
```

---

## 9. Questions Fréquentes (FAQ)

### Q1 : Pourquoi les tests ne peuvent-ils pas utiliser SQLite au lieu de PostgreSQL ?

**R** : SQLite est parfait pour les tests locaux (rapide, simple), mais PostgreSQL a des comportements spécifiques :
- Types de données différents (JSONB, UUID, Array)
- Contraintes et indexes différents
- Comportement des transactions différent
- Fonctions SQL spécifiques à PostgreSQL

Utiliser PostgreSQL en tests garantit que le code fonctionne exactement comme en production.

### Q2 : Les tests modifient-ils les données de staging ?

**R** : **NON**. Absolument pas. Les tests utilisent une base de données PostgreSQL **temporaire** dans un container Docker qui est :
- Créé au début du workflow
- Détruit à la fin du workflow
- Complètement isolé de staging/production

### Q3 : Puis-je exécuter les tests localement ?

**R** : Oui, de deux façons :

**Méthode 1 : SQLite (rapide)** :
```bash
cd apps/backend/user-service
pytest
```
Le conftest.py utilise automatiquement SQLite si `DATABASE_URL` n'est pas défini.

**Méthode 2 : PostgreSQL local (identique au CI/CD)** :
```bash
docker run -d --name test-postgres \
  -e POSTGRES_USER=skillforge_test \
  -e POSTGRES_PASSWORD=test_password_secure_123 \
  -e POSTGRES_DB=skillforge_test_db \
  -p 5432:5432 postgres:15-alpine

cd apps/backend/user-service
DATABASE_URL="postgresql+asyncpg://skillforge_test:test_password_secure_123@localhost:5432/skillforge_test_db" \
pytest

docker rm -f test-postgres
```

### Q4 : Que se passe-t-il si une migration échoue ?

**R** : Alembic garde une trace des migrations appliquées dans la table `alembic_version`. Si une migration échoue :
1. La transaction est annulée (rollback)
2. Le schéma reste à l'état précédent
3. Le déploiement continue (car migrations != tests)
4. L'équipe doit corriger la migration manuellement

### Q5 : Comment créer une nouvelle migration ?

```bash
cd apps/backend/user-service

# Générer automatiquement à partir des modèles
DATABASE_URL="<staging_url>" alembic revision --autogenerate -m "Add user preferences table"

# Ou créer manuellement
alembic revision -m "Add custom index"
```

### Q6 : Les tests ralentissent-ils le workflow ?

**R** : Impact minimal :
- Start PostgreSQL container : ~5-10 secondes
- Création du schéma : ~1-2 secondes
- Exécution des tests : variable (actuellement ~30 secondes)
- Total overhead : ~15 secondes par rapport à SQLite

C'est un compromis acceptable pour garantir la fiabilité.

---

## 10. Prochaines Étapes (Hors Scope de ce Rapport)

### 10.1 Corrections des Tests

Les tests suivants nécessitent des corrections (problèmes de test, PAS d'infrastructure) :

1. **Erreur bcrypt "password too long"** :
   - Cause : Mots de passe de test > 72 bytes
   - Solution : Tronquer les mots de passe dans les fixtures
   - Fichiers : `conftest.py`, tests individuels

2. **Erreur 'async_generator' object has no attribute 'add'** :
   - Cause : Fixture `create_test_user` mal structurée
   - Solution : Corriger le fixture pour retourner directement l'objet User
   - Fichier : `apps/backend/user-service/app/tests/conftest.py:202-243`

### 10.2 Améliorations Futures

1. **Tests de migrations** :
   - Tester que les migrations s'appliquent correctement
   - Tester les rollbacks
   - Vérifier l'intégrité des données après migration

2. **Tests de charge de base de données** :
   - Performance des requêtes
   - Indexes optimaux
   - Connection pooling

3. **Tests d'intégration avec autres services** :
   - Tester les appels entre user-service et company-service
   - Vérifier la cohérence des données

---

## 11. Références

### Fichiers Modifiés

1. `.github/workflows/deploy-service.yml`
   - Ajout du service PostgreSQL temporaire
   - Configuration de DATABASE_URL pour les tests

2. `apps/backend/user-service/app/tests/conftest.py`
   - Correction du fixture test_db_setup
   - Ajout de _setup_test_database() et _teardown_test_database()

3. `apps/backend/user-service/app/utils/email.py`
   - Ajout du mode test pour skip SMTP

4. `apps/backend/user-service/app/api/v1/__init__.py`
   - Suppression des imports company

5. `apps/backend/user-service/app/schemas/__init__.py`
   - Suppression des exports company

### Documentation Externe

- [PostgreSQL Docker Official Image](https://hub.docker.com/_/postgres)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Cloud SQL Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy)

---

## 12. Conclusion

### Résumé de l'Architecture

L'architecture mise en place sépare clairement deux responsabilités distinctes :

1. **Tests de Base de Données** (Phase 1) :
   - Objectif : Valider la LOGIQUE du code
   - Infrastructure : PostgreSQL temporaire (Docker)
   - Risque : ZÉRO (base jetable)
   - Bloque : Le déploiement si échec

2. **Migrations de Base de Données** (Phase 3) :
   - Objectif : Modifier le SCHÉMA de production/staging
   - Infrastructure : Cloud SQL (GCP)
   - Risque : CRITIQUE (données réelles)
   - Exécute : Après déploiement réussi

### État Actuel

✅ **Infrastructure de tests fonctionnelle** :
- PostgreSQL temporaire configuré
- Tables créées automatiquement
- Isolation complète de staging/production

⚠️ **Tests individuels nécessitent corrections** :
- Erreurs bcrypt (mots de passe trop longs)
- Fixtures async_generator mal structurés

### Impact Business

Cette architecture garantit :
- **Sécurité** : Aucun risque de corruption de données de production pendant les tests
- **Fiabilité** : Les tests valident le code dans un environnement identique à la production
- **Performance** : Tests rapides grâce à PostgreSQL local
- **Coût** : Pas de consommation de ressources GCP pour les tests

---

**Document rédigé par** : Claude Code (Anthropic AI Assistant)
**Date de dernière mise à jour** : 1er Octobre 2025
**Version** : 1.0
