# donnes moi l'ensemble des valeurs necessaires a r...

| Variable | Service(s) concerné(s) | Description et Exemple de Valeur (Locale) |
| --- | --- | --- |
| POSTGRES_USER | PostgreSQL, Tous les services Back-End | Nom de l'utilisateur pour la base de données locale. skillforge_user est une bonne valeur par défaut. |
| POSTGRES_PASSWORD | PostgreSQL, Tous les services Back-End | Mot de passe pour l'utilisateur PostgreSQL local. Doit être changé pour une valeur complexe (ex: Th1sIsMyS3cr3tP@ss). |
| POSTGRES_DB | PostgreSQL, Tous les services Back-End | Nom de la base de données qui sera créée au premier lancement. skillforge_db est la valeur standard. |
| POSTGRES_PORT | Docker Compose | Port de votre machine locale qui sera mappé sur le port de la base de données dans le conteneur. 5432 est le standard. |
| DATABASE_URL | Tous les services Back-End, Alembic | L'URL de connexion complète utilisée par SQLAlchemy. Le format est fixe, seul le mot de passe est injecté. |
| REDIS_HOST | Services utilisant Redis | Nom d'hôte du service Redis, tel que défini dans docker-compose.yml. redis-cache est une bonne valeur. |
| REDIS_PORT | Services utilisant Redis | Port standard de Redis. 6379. |
| JWT_SECRET_KEY | Services d'authentification | Clé secrète critique pour signer les jetons. Doit être générée avec openssl rand -hex 32 et être unique pour chaque développeur. |
| JWT_ALGORITHM | Services d'authentification | Algorithme de signature. HS256 est utilisé en local. La production utilisera RS256. |
| ACCESS_TOKEN_EXPIRE_MINUTES | Services d'authentification | Durée de vie d'un jeton JWT. 60 minutes est un bon compromis entre sécurité et expérience utilisateur. |
| VITE_API_BASE_URL | Front-End | L'URL que le code JavaScript du navigateur utilisera pour joindre le Back-End. http://localhost:8000. |
| GCP_PROJECT_ID | Outils CLI, Code utilisant les SDKs GCP | L'ID de votre projet GCP de développement. Essentiel pour que les SDKs sachent à quel projet s'adresser. |
| GCS_BUCKET_UPLOADS | Services gérant les fichiers | Nom du bucket GCS où les fichiers sont stockés. En local, peut pointer vers un bucket de test. |

