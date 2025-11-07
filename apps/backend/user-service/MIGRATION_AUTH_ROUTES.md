# Migration des Routes d'Authentification

**Date de migration:** 2025-11-07
**Raison:** Séparation des préoccupations dans l'architecture microservices

---

## Changements

### Routes Retirées du user-service

Les routes d'authentification suivantes ont été **supprimées** du user-service:

| Méthode | Route | Description | Nouveau Service |
|---------|-------|-------------|-----------------|
| POST | `/api/v1/auth/register` | Inscription utilisateur | auth-service |
| POST | `/api/v1/auth/login` | Connexion utilisateur | auth-service |
| POST | `/api/v1/auth/refresh` | Rafraîchir token | auth-service |
| POST | `/api/v1/auth/logout` | Déconnexion | auth-service |
| POST | `/api/v1/auth/logout-all` | Déconnexion tous appareils | auth-service |
| POST | `/api/v1/auth/verify-email-request` | Demande vérification email | auth-service |
| POST | `/api/v1/auth/verify-email` | Vérification email | auth-service |
| POST | `/api/v1/auth/password-reset-request` | Demande reset password | auth-service |
| POST | `/api/v1/auth/password-reset-confirm` | Confirmation reset | auth-service |

---

## Impact sur les Clients

### Clients Internes

Les clients internes doivent maintenant appeler **auth-service** directement:

**Avant (user-service):**
```python
response = httpx.post(
    "http://user-service:8000/api/v1/auth/login",
    json={"username": "user@example.com", "password": "pass"}
)
```

**Après (auth-service):**
```python
response = httpx.post(
    "http://auth-service:8001/api/v1/auth/login",
    json={"username": "user@example.com", "password": "pass"}
)
```

### Clients Externes (via API Gateway)

**Aucun changement requis** pour les clients externes utilisant l'API Gateway.

Le routage API Gateway a été configuré pour diriger `/api/v1/auth/*` vers auth-service:

```yaml
"/api/v1/auth/login":
  x-google-backend:
    address: "${auth_service_url}"
```

---

## Routes Maintenues dans user-service

Le user-service conserve uniquement les routes de gestion des utilisateurs:

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/users/me` | Profil utilisateur connecté |
| PUT | `/api/v1/users/me` | Modifier profil |
| POST | `/api/v1/users/me/change-password` | Changer mot de passe |
| GET | `/api/v1/users/me/settings` | Paramètres utilisateur |
| PUT | `/api/v1/users/me/settings` | Modifier paramètres |
| DELETE | `/api/v1/users/me` | Supprimer compte |
| GET | `/api/v1/users/{id}/public` | Profil public |
| GET | `/api/v1/users/public` | Liste utilisateurs publique |
| GET | `/api/v1/users/` | Liste tous utilisateurs (admin) |
| GET | `/api/v1/users/{id}` | Détails utilisateur (admin) |
| PUT | `/api/v1/users/{id}/role` | Modifier rôle (admin) |
| PUT | `/api/v1/users/{id}/status` | Modifier statut (admin) |
| DELETE | `/api/v1/users/{id}` | Supprimer utilisateur (admin) |

---

## Bénéfices de la Migration

### 1. Séparation des Responsabilités
- **auth-service**: Responsable uniquement de l'authentification
- **user-service**: Responsable uniquement de la gestion des utilisateurs

### 2. Scalabilité Indépendante
- auth-service peut scaler indépendamment selon la charge d'authentification
- user-service peut scaler selon les besoins de gestion des profils

### 3. Déploiements Indépendants
- Modifications d'authentification sans redéployer user-service
- Modifications de profil sans redéployer auth-service

### 4. Sécurité Améliorée
- Isolation des fonctionnalités critiques d'authentification
- Contrôle d'accès plus granulaire

### 5. Maintenance Simplifiée
- Code base plus petit et focalisé
- Tests plus ciblés
- Debugging facilité

---

## Fichiers Modifiés

### user-service

1. **app/api/v1/endpoints/__init__.py**
   - Retiré import de `auth_router`
   - Ajouté note de migration

2. **app/api/v1/__init__.py**
   - Retiré `include_router` pour auth
   - Ajouté commentaire explicatif

3. **app/api/v1/endpoints/auth.py**
   - Renommé en `auth.py.deprecated`
   - Conservé pour référence historique

### API Gateway

Routes `/api/v1/auth/*` configurées pour pointer vers auth-service.

---

## Rollback (en cas de problème)

Si un rollback est nécessaire:

```bash
# 1. Restaurer les fichiers
cd apps/backend/user-service/app/api/v1/endpoints
git checkout HEAD~1 -- __init__.py
cd ../
git checkout HEAD~1 -- __init__.py

# 2. Redéployer
git commit -m "rollback: Restore auth routes in user-service"
git push
```

---

## Timeline

- **2025-11-07**: Migration effectuée
- **2025-11-14**: Période de grâce (7 jours)
- **2025-11-21**: Suppression définitive du fichier auth.py.deprecated

---

## Contact

Pour toute question sur cette migration:
- Voir: `INTEGRATION_MICROSERVICES_SUMMARY.md`
- Voir: `RAPPORT_VALIDATION_MICROSERVICES.md`

---

**Status:** ✅ **Migration Complétée**
