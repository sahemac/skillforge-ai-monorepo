# SkillForge Shared Models

**Single Source of Truth** for database models across all SkillForge AI microservices.

## Purpose

This package contains shared SQLModel/SQLAlchemy models to prevent duplication across services and ensure schema consistency.

## Architecture

```
┌─────────────────────────────────────────┐
│   PostgreSQL (skillforge_db)            │
│   ┌─────────────────────────────────┐   │
│   │  users (user-service owns)      │   │
│   │  user_settings                  │   │
│   │  user_sessions                  │   │
│   │  two_factor_auth (auth owns)    │   │
│   │  companies (company-service)    │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         ↑              ↑              ↑
         │              │              │
   auth-service   user-service   company-service
   (imports)      (imports)      (imports)
      READ           READ/WRITE      READ
```

## Ownership Rules

- **user-service**: Owns `users`, `user_settings`, `user_sessions` tables (READ/WRITE)
- **auth-service**: Owns `two_factor_auth` table (READ/WRITE), reads `users` (READ-ONLY)
- **company-service**: Owns `companies` table (READ/WRITE), reads `users` (READ-ONLY)

## Installation

```bash
# From monorepo root
pip install -e packages/shared-models
```

## Usage

```python
from skillforge_models import User, UserSettings, UserSession, TwoFactorAuth

# All services use the same model definitions
```

## Migration Strategy

Each service maintains its own Alembic migrations for tables it **owns**.

- user-service migrations: Create/alter users, user_settings, user_sessions
- auth-service migrations: Create/alter two_factor_auth
- company-service migrations: Create/alter companies

## Updates

When updating shared models:
1. Update model in `skillforge_models/`
2. Create migration in the **owning service**
3. Other services will see schema changes via shared import
