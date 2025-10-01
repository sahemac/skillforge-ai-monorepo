# Configuration des Endpoints - User Service

## Date : 1er Octobre 2025
## Service : user-service
## Version : 1.0.0

---

## Vue d'Ensemble

Le service `user-service` expose **26 endpoints** répartis en 3 catégories principales :
1. **Infrastructure** (5 endpoints) - Health checks, métriques, root
2. **Authentication** (9 endpoints) - Inscription, login, tokens, email, password
3. **Users Management** (13 endpoints) - Profils, paramètres, administration

---

## 1. Infrastructure & Monitoring Endpoints

### 1.1 Root & Service Info

#### `GET /`
**Description** : Page de connexion HTML (login.html) ou informations du service
**Authentification** : Non requise
**Response** :
```html
<!-- login.html si disponible -->
<!-- Sinon JSON : -->
{
  "service": "skillforge-ai-user-service",
  "version": "1.0.0",
  "status": "healthy",
  "environment": "staging|production|development"
}
```

#### `GET /api`
**Description** : Informations générales sur l'API
**Authentification** : Non requise
**Response** :
```json
{
  "service": "skillforge-ai-user-service",
  "version": "1.0.0",
  "status": "healthy",
  "environment": "staging"
}
```

### 1.2 Health Checks

#### `GET /health`
**Description** : Health check complet avec vérification de tous les services
**Authentification** : Non requise
**Vérifie** :
- Database connection
- Redis cache
- SMTP service
- Metrics system

**Response** :
```json
{
  "status": "healthy|unhealthy",
  "timestamp": 1696185600.123,
  "service": "user-service",
  "version": "1.0.0",
  "environment": "staging",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15.2
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 2.5
    },
    "smtp": {
      "status": "healthy",
      "response_time_ms": 50.3
    },
    "metrics": {
      "status": "healthy",
      "response_time_ms": 1.1
    }
  }
}
```

**Utilisé par** :
- Load balancers (Cloud Run health checks)
- Monitoring systems (Prometheus, Grafana)
- CI/CD validation après déploiement

### 1.3 Metrics

#### `GET /metrics`
**Description** : Endpoint Prometheus pour métriques de performance
**Authentification** : Non requise
**Format** : Prometheus text format
**Response** :
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/v1/users/me",status="200"} 1234

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 500
http_request_duration_seconds_bucket{le="0.5"} 950
...
```

**Métriques collectées** :
- Nombre total de requêtes HTTP par endpoint
- Durée des requêtes (histogramme)
- Taux d'erreurs par status code
- Nombre d'utilisateurs actifs
- Opérations de cache (hits/misses)

#### `GET /cache/info`
**Description** : Informations sur le cache Redis
**Authentification** : Admin seulement (non implémenté actuellement)
**Response** :
```json
{
  "connected": true,
  "redis_version": "7.0.5",
  "memory_used": "2.5MB",
  "total_keys": 1234
}
```

---

## 2. Authentication Endpoints (`/api/v1/auth`)

Tous les endpoints d'authentification sont préfixés par `/api/v1/auth`.

### 2.1 Registration

#### `POST /api/v1/auth/register`
**Description** : Inscription d'un nouvel utilisateur
**Authentification** : Non requise
**Rate Limit** : 60 requêtes/minute par IP
**Request Body** :
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "terms_accepted": true,
  "privacy_policy_accepted": true
}
```

**Validations** :
- Email unique
- Username unique (3-30 caractères)
- Password : min 8 caractères, majuscule, minuscule, chiffre, caractère spécial
- Terms et privacy policy doivent être acceptés

**Response** : `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "role": "learner",
  "status": "active",
  "is_email_verified": false,
  "created_at": "2025-10-01T12:00:00Z"
}
```

**Erreurs** :
- `400 Bad Request` - Email/username déjà utilisé, mot de passe faible
- `422 Unprocessable Entity` - Validation schema échouée
- `429 Too Many Requests` - Rate limit dépassé

### 2.2 Login

#### `POST /api/v1/auth/login`
**Description** : Connexion utilisateur
**Authentification** : Non requise
**Rate Limit** : 60 requêtes/minute par IP
**Request Body** :
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "remember_me": false
}
```

**Response** : `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "role": "learner"
  }
}
```

**Fonctionnalités** :
- Crée une session utilisateur
- `remember_me=true` : refresh token valide 30 jours
- `remember_me=false` : refresh token valide 7 jours
- Incrémente failed_login_attempts si échec
- Bloque le compte après 5 tentatives échouées

**Erreurs** :
- `401 Unauthorized` - Credentials invalides
- `403 Forbidden` - Compte bloqué ou inactif
- `429 Too Many Requests` - Rate limit dépassé

### 2.3 Token Management

#### `POST /api/v1/auth/refresh`
**Description** : Rafraîchir l'access token
**Authentification** : Refresh token requis
**Request Body** :
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** : `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Erreurs** :
- `401 Unauthorized` - Refresh token invalide ou expiré
- `403 Forbidden` - Session révoquée

### 2.4 Logout

#### `POST /api/v1/auth/logout`
**Description** : Déconnexion (invalide la session courante)
**Authentification** : Bearer token requis
**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** : `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

**Actions** :
- Invalide la session courante
- Révoque le refresh token associé
- Conserve les autres sessions actives

#### `POST /api/v1/auth/logout-all`
**Description** : Déconnexion de toutes les sessions
**Authentification** : Bearer token requis

**Response** : `200 OK`
```json
{
  "message": "Successfully logged out from all devices",
  "sessions_revoked": 3
}
```

**Actions** :
- Invalide TOUTES les sessions de l'utilisateur
- Révoque tous les refresh tokens
- Force reconnexion sur tous les appareils

### 2.5 Email Verification

#### `POST /api/v1/auth/verify-email-request`
**Description** : Demander l'envoi d'un email de vérification
**Authentification** : Bearer token requis
**Request Body** :
```json
{
  "email": "user@example.com"
}
```

**Response** : `200 OK`
```json
{
  "message": "Verification email sent",
  "expires_in": 86400
}
```

**Actions** :
- Génère un token de vérification (valide 24h)
- Envoie un email avec lien de vérification
- Rate limited : 3 emails par heure

**Erreurs** :
- `400 Bad Request` - Email déjà vérifié
- `404 Not Found` - Utilisateur non trouvé
- `429 Too Many Requests` - Trop d'emails envoyés

#### `POST /api/v1/auth/verify-email`
**Description** : Confirmer la vérification de l'email
**Authentification** : Non requise
**Request Body** :
```json
{
  "token": "verification_token_here"
}
```

**Response** : `200 OK`
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_email_verified": true
  }
}
```

**Actions** :
- Marque l'email comme vérifié
- Peut débloquer des fonctionnalités premium

**Erreurs** :
- `400 Bad Request` - Token invalide ou expiré

### 2.6 Password Reset

#### `POST /api/v1/auth/password-reset-request`
**Description** : Demander la réinitialisation du mot de passe
**Authentification** : Non requise
**Rate Limit** : 3 requêtes/heure par email
**Request Body** :
```json
{
  "email": "user@example.com"
}
```

**Response** : `200 OK`
```json
{
  "message": "Password reset email sent if account exists"
}
```

**Note** : Retourne toujours succès pour éviter l'énumération d'emails

**Actions** :
- Génère un token de reset (valide 1h)
- Envoie un email avec lien de reset
- Rate limited : 3 emails par heure

#### `POST /api/v1/auth/password-reset-confirm`
**Description** : Confirmer la réinitialisation du mot de passe
**Authentification** : Non requise
**Request Body** :
```json
{
  "token": "reset_token_here",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Response** : `200 OK`
```json
{
  "message": "Password reset successfully"
}
```

**Actions** :
- Vérifie le token de reset
- Valide le nouveau mot de passe
- Hash et sauvegarde le nouveau password
- Invalide toutes les sessions actives

**Erreurs** :
- `400 Bad Request` - Token invalide/expiré, mot de passe faible
- `422 Unprocessable Entity` - Passwords ne correspondent pas

---

## 3. Users Management Endpoints (`/api/v1/users`)

Tous les endpoints users sont préfixés par `/api/v1/users`.

### 3.1 Current User (Profil Utilisateur Connecté)

#### `GET /api/v1/users/me`
**Description** : Récupérer le profil de l'utilisateur connecté
**Authentification** : Bearer token requis
**Headers** :
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** : `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Full-stack developer",
  "role": "learner",
  "status": "active",
  "is_email_verified": true,
  "is_active": true,
  "experience_level": "intermediate",
  "country": "FR",
  "timezone": "Europe/Paris",
  "language_preference": "fr",
  "newsletter_subscribed": true,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-10-01T12:00:00Z"
}
```

#### `PUT /api/v1/users/me`
**Description** : Mettre à jour le profil de l'utilisateur connecté
**Authentification** : Bearer token requis
**Request Body** (tous les champs optionnels) :
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Full-stack developer passionate about AI",
  "experience_level": "advanced",
  "country": "FR",
  "timezone": "Europe/Paris",
  "language_preference": "fr"
}
```

**Champs non modifiables** :
- `email` (utiliser verification flow)
- `username` (unique et permanent)
- `role` (seul admin peut modifier)
- `status` (seul admin peut modifier)

**Response** : `200 OK` - Retourne le profil mis à jour

**Erreurs** :
- `401 Unauthorized` - Token invalide
- `422 Unprocessable Entity` - Validation échouée

#### `POST /api/v1/users/me/change-password`
**Description** : Changer le mot de passe de l'utilisateur connecté
**Authentification** : Bearer token requis
**Request Body** :
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**Response** : `200 OK`
```json
{
  "message": "Password changed successfully"
}
```

**Actions** :
- Vérifie le mot de passe actuel
- Valide le nouveau mot de passe (force, longueur)
- Hash et sauvegarde
- Invalide toutes les autres sessions

**Erreurs** :
- `400 Bad Request` - Mot de passe actuel incorrect
- `422 Unprocessable Entity` - Nouveau mot de passe invalide

#### `DELETE /api/v1/users/me`
**Description** : Supprimer le compte de l'utilisateur connecté
**Authentification** : Bearer token requis
**Query Parameters** :
- `confirm=true` (requis)

**Response** : `204 No Content`

**Actions** :
- Soft delete (marque `is_active=false`)
- Invalide toutes les sessions
- Garde les données pour 30 jours (RGPD)
- Après 30 jours : hard delete automatique

**Erreurs** :
- `400 Bad Request` - `confirm` non fourni
- `401 Unauthorized` - Token invalide

### 3.2 User Settings

#### `GET /api/v1/users/me/settings`
**Description** : Récupérer les paramètres de l'utilisateur
**Authentification** : Bearer token requis

**Response** : `200 OK`
```json
{
  "user_id": "uuid",
  "theme": "dark",
  "language": "fr",
  "timezone": "Europe/Paris",
  "email_notifications": true,
  "push_notifications": false,
  "newsletter_subscribed": true,
  "privacy_settings": {
    "profile_visibility": "public",
    "show_email": false,
    "show_activity": true
  },
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-10-01T12:00:00Z"
}
```

#### `PUT /api/v1/users/me/settings`
**Description** : Mettre à jour les paramètres de l'utilisateur
**Authentification** : Bearer token requis
**Request Body** (tous les champs optionnels) :
```json
{
  "theme": "dark",
  "language": "fr",
  "timezone": "Europe/Paris",
  "email_notifications": true,
  "push_notifications": false,
  "newsletter_subscribed": false,
  "privacy_settings": {
    "profile_visibility": "private",
    "show_email": false,
    "show_activity": false
  }
}
```

**Response** : `200 OK` - Retourne les settings mis à jour

### 3.3 Public User Profiles

#### `GET /api/v1/users/{user_id}/public`
**Description** : Récupérer le profil public d'un utilisateur
**Authentification** : Non requise
**Path Parameters** :
- `user_id` (UUID)

**Response** : `200 OK`
```json
{
  "id": "uuid",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Full-stack developer",
  "experience_level": "advanced",
  "country": "FR",
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Note** : N'expose que les informations publiques (pas d'email, pas de rôle)

**Erreurs** :
- `404 Not Found` - Utilisateur non trouvé ou profil privé

#### `GET /api/v1/users/public`
**Description** : Lister les profils publics (avec filtres et pagination)
**Authentification** : Non requise
**Query Parameters** :
- `page` (default: 1)
- `size` (default: 20, max: 100)
- `search` (recherche dans username, first_name, last_name)
- `country` (filtrer par pays)
- `experience_level` (filtrer par niveau)

**Response** : `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "bio": "Full-stack developer",
      "experience_level": "advanced",
      "country": "FR"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

### 3.4 Admin User Management

**Tous les endpoints admin nécessitent** :
- Bearer token avec `role=admin` ou `is_superuser=true`
- Sinon : `403 Forbidden`

#### `GET /api/v1/users/`
**Description** : Lister tous les utilisateurs (admin)
**Authentification** : Admin/Superuser requis
**Query Parameters** :
- `page` (default: 1)
- `size` (default: 20, max: 100)
- `role` (filtrer par rôle : learner, company, admin)
- `status` (filtrer par status : active, inactive, suspended)
- `verified` (filtrer par email vérifié : true/false)
- `search` (recherche dans email, username, nom)
- `sort_by` (trier par : created_at, email, username)
- `sort_order` (asc/desc, default: desc)

**Response** : `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "role": "learner",
      "status": "active",
      "is_email_verified": true,
      "is_active": true,
      "created_at": "2025-01-01T12:00:00Z",
      "last_login": "2025-10-01T10:30:00Z"
    }
  ],
  "total": 1234,
  "page": 1,
  "size": 20,
  "pages": 62
}
```

#### `GET /api/v1/users/{user_id}`
**Description** : Récupérer les détails complets d'un utilisateur (admin)
**Authentification** : Admin/Superuser requis
**Path Parameters** :
- `user_id` (UUID)

**Response** : `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Full-stack developer",
  "role": "learner",
  "status": "active",
  "is_email_verified": true,
  "is_active": true,
  "experience_level": "advanced",
  "country": "FR",
  "timezone": "Europe/Paris",
  "language_preference": "fr",
  "newsletter_subscribed": true,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-10-01T12:00:00Z",
  "last_login": "2025-10-01T10:30:00Z",
  "failed_login_attempts": 0,
  "account_locked_until": null
}
```

**Erreurs** :
- `403 Forbidden` - Non admin
- `404 Not Found` - Utilisateur non trouvé

#### `PUT /api/v1/users/{user_id}/role`
**Description** : Modifier le rôle d'un utilisateur (admin)
**Authentification** : Admin/Superuser requis
**Path Parameters** :
- `user_id` (UUID)

**Request Body** :
```json
{
  "role": "learner|company|admin"
}
```

**Response** : `200 OK` - Retourne l'utilisateur mis à jour

**Actions** :
- Change le rôle de l'utilisateur
- Invalide les sessions actives (force reconnexion)
- Log l'action dans l'audit trail

**Erreurs** :
- `400 Bad Request` - Rôle invalide
- `403 Forbidden` - Non admin ou tentative de modifier un superuser
- `404 Not Found` - Utilisateur non trouvé

**Sécurité** :
- Un admin ne peut pas modifier un superuser
- Un admin ne peut pas se promouvoir lui-même superuser

#### `PUT /api/v1/users/{user_id}/status`
**Description** : Modifier le statut d'un utilisateur (admin)
**Authentification** : Admin/Superuser requis
**Path Parameters** :
- `user_id` (UUID)

**Request Body** :
```json
{
  "status": "active|inactive|suspended",
  "reason": "Violation of terms of service"
}
```

**Response** : `200 OK` - Retourne l'utilisateur mis à jour

**Actions** :
- `suspended` : Bloque l'accès, invalide les sessions
- `inactive` : Soft delete, garde les données
- `active` : Réactive le compte

**Erreurs** :
- `400 Bad Request` - Status invalide
- `403 Forbidden` - Non admin ou tentative de suspendre un admin/superuser
- `404 Not Found` - Utilisateur non trouvé

#### `DELETE /api/v1/users/{user_id}`
**Description** : Supprimer un utilisateur (admin)
**Authentification** : Superuser uniquement
**Path Parameters** :
- `user_id` (UUID)

**Query Parameters** :
- `hard_delete=true` (optionnel, default: false)

**Response** : `204 No Content`

**Actions** :
- `hard_delete=false` : Soft delete (marque is_active=false)
- `hard_delete=true` : Suppression définitive (CASCADE)

**Erreurs** :
- `403 Forbidden` - Non superuser ou tentative de supprimer un admin/superuser
- `404 Not Found` - Utilisateur non trouvé

**Sécurité** :
- Seul un superuser peut supprimer
- Un superuser ne peut pas supprimer un autre superuser
- Hard delete nécessite confirmation explicite

---

## 4. Sécurité et Authentification

### 4.1 JWT Tokens

**Access Token** :
- Durée de vie : 1 heure
- Utilisation : Authentification des requêtes API
- Stockage : Memory (jamais en localStorage)
- Contenu :
```json
{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "role": "learner",
  "type": "access",
  "exp": 1696189200,
  "iat": 1696185600
}
```

**Refresh Token** :
- Durée de vie : 7 jours (sans remember_me) ou 30 jours (avec remember_me)
- Utilisation : Renouveler l'access token
- Stockage : HttpOnly cookie (recommandé)
- Révocable : Oui (table user_sessions)

### 4.2 Rate Limiting

**Endpoints publics** :
- Registration : 60 req/minute par IP
- Login : 60 req/minute par IP
- Password reset : 3 req/heure par email

**Endpoints authentifiés** :
- GET : 1000 req/minute par utilisateur
- POST/PUT : 100 req/minute par utilisateur
- DELETE : 10 req/minute par utilisateur

**Headers de réponse** :
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1696185660
```

### 4.3 CORS

**Origines autorisées** (configurable via BACKEND_CORS_ORIGINS) :
- `https://skillforge-ai.com`
- `https://*.skillforge-ai.com`
- `http://localhost:3000` (dev uniquement)
- `http://localhost:5173` (dev uniquement)

**Headers autorisés** :
- `Authorization`
- `Content-Type`
- `Accept`
- `Origin`
- `X-Requested-With`

**Méthodes autorisées** :
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`

**Credentials** : Autorisés (`allow_credentials: true`)

### 4.4 IAP (Identity-Aware Proxy)

Pour les déploiements GCP Cloud Run avec IAP :

**Headers vérifiés** :
- `X-Goog-IAP-JWT-Assertion` : JWT signé par Google
- `X-Goog-Authenticated-User-Email` : Email de l'utilisateur IAP

**Configuration** :
```python
IAPMiddleware(
    project_number="584748485117",
    backend_service_id="user-service-backend-staging"
)
```

**Environnements** :
- `production` : IAP obligatoire
- `staging` : IAP obligatoire
- `development` : IAP désactivé

---

## 5. Middlewares et Ordre d'Exécution

Les middlewares sont appliqués dans cet ordre (du plus externe au plus interne) :

1. **CorrelationMiddleware** : Ajoute X-Correlation-ID
2. **LoggingMiddleware** : Log toutes les requêtes/réponses
3. **IAPMiddleware** : Vérifie l'authentification IAP (production/staging)
4. **PrometheusMiddleware** : Collecte les métriques
5. **TrustedHostMiddleware** : Valide les hosts autorisés
6. **CORSMiddleware** : Gère les requêtes cross-origin
7. **ProcessTimeMiddleware** : Ajoute X-Process-Time header
8. **RateLimitMiddleware** : Applique les limites de taux

---

## 6. Headers Standard des Réponses

Toutes les réponses incluent :

```
X-Process-Time: 0.045
X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## 7. Codes de Status HTTP

### Succès (2xx)
- `200 OK` : Requête réussie
- `201 Created` : Ressource créée (registration)
- `204 No Content` : Suppression réussie

### Erreurs Client (4xx)
- `400 Bad Request` : Données invalides
- `401 Unauthorized` : Authentification requise ou invalide
- `403 Forbidden` : Permissions insuffisantes
- `404 Not Found` : Ressource non trouvée
- `422 Unprocessable Entity` : Validation Pydantic échouée
- `429 Too Many Requests` : Rate limit dépassé

### Erreurs Serveur (5xx)
- `500 Internal Server Error` : Erreur serveur générique
- `503 Service Unavailable` : Service temporairement indisponible

---

## 8. Pagination Standard

Tous les endpoints de listing utilisent cette pagination :

**Query Parameters** :
```
?page=1&size=20
```

**Response** :
```json
{
  "items": [...],
  "total": 1234,
  "page": 1,
  "size": 20,
  "pages": 62
}
```

**Limites** :
- `size` minimum : 1
- `size` maximum : 100
- `size` par défaut : 20

---

## 9. Documentation OpenAPI

**Swagger UI** : `GET /api/v1/docs`
**ReDoc** : `GET /api/v1/redoc`
**OpenAPI JSON** : `GET /api/v1/openapi.json`

---

## 10. Résumé des Endpoints

### Infrastructure (5 endpoints)
```
GET  /                      - Root / Login page
GET  /api                   - Service info
GET  /health                - Health check
GET  /metrics               - Prometheus metrics
GET  /cache/info            - Cache information
```

### Authentication (9 endpoints)
```
POST /api/v1/auth/register                  - Register new user
POST /api/v1/auth/login                     - Login
POST /api/v1/auth/refresh                   - Refresh access token
POST /api/v1/auth/logout                    - Logout current session
POST /api/v1/auth/logout-all                - Logout all sessions
POST /api/v1/auth/verify-email-request      - Request email verification
POST /api/v1/auth/verify-email              - Confirm email verification
POST /api/v1/auth/password-reset-request    - Request password reset
POST /api/v1/auth/password-reset-confirm    - Confirm password reset
```

### Users Management (13 endpoints)
```
GET    /api/v1/users/me                     - Get current user profile
PUT    /api/v1/users/me                     - Update current user profile
POST   /api/v1/users/me/change-password     - Change password
DELETE /api/v1/users/me                     - Delete own account

GET    /api/v1/users/me/settings            - Get user settings
PUT    /api/v1/users/me/settings            - Update user settings

GET    /api/v1/users/{user_id}/public       - Get public user profile
GET    /api/v1/users/public                 - List public user profiles

GET    /api/v1/users/                       - List all users (admin)
GET    /api/v1/users/{user_id}              - Get user details (admin)
PUT    /api/v1/users/{user_id}/role         - Update user role (admin)
PUT    /api/v1/users/{user_id}/status       - Update user status (admin)
DELETE /api/v1/users/{user_id}              - Delete user (superuser)
```

**Total : 27 endpoints**

---

## 11. Configuration des Routes dans le Code

### Fichier principal : `app/main.py`
- Inclut `api_router` avec préfixe `/api/v1`
- Configure tous les middlewares
- Définit les endpoints infrastructure (/health, /metrics, etc.)

### Routeur API v1 : `app/api/v1/__init__.py`
```python
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["authentication"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)
```

### Endpoints Auth : `app/api/v1/endpoints/auth.py`
- 9 endpoints d'authentification
- Rate limiting sur endpoints sensibles
- Gestion des tokens JWT

### Endpoints Users : `app/api/v1/endpoints/users.py`
- 13 endpoints de gestion utilisateurs
- Permissions différenciées (user, admin, superuser)
- Pagination et filtres

---

## 12. Vérification de la Configuration

### ✅ Endpoints Configurés
Tous les endpoints sont correctement configurés et inclus dans le routeur principal.

### ✅ Middlewares
Tous les middlewares de sécurité sont en place :
- CORS
- Rate limiting
- IAP (production/staging)
- Logging
- Metrics

### ✅ Authentification
- JWT tokens (access + refresh)
- Sessions persistées en base
- Révocation de tokens

### ✅ Permissions
- User (profil personnel)
- Admin (gestion utilisateurs)
- Superuser (suppression)

### ✅ Documentation
- OpenAPI/Swagger UI disponible
- Schémas Pydantic pour validation
- Types de réponse documentés

---

**Document généré par** : Claude Code (Anthropic AI Assistant)
**Date** : 1er Octobre 2025
**Version** : 1.0.0
