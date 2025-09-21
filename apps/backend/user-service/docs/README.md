# SkillForge AI - User Service

**Version**: 1.0.0  
**Environment**: Production Ready  
**Status**: ✅ Operational with IAP Authentication  

## 🏗️ Architecture Overview

The User Service is a FastAPI-based microservice responsible for user management, authentication, and company management within the SkillForge AI platform.

### Key Features

- ✅ **IAP Authentication**: Google Identity-Aware Proxy integration
- ✅ **PostgreSQL Database**: Production-ready with Alembic migrations  
- ✅ **Redis Caching**: Optional performance optimization
- ✅ **Prometheus Metrics**: Comprehensive monitoring
- ✅ **Rate Limiting**: API protection with SlowAPI
- ✅ **Security Middleware**: CORS, trusted hosts, IAP validation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis (optional)
- Google Cloud SQL Proxy (for production)

### Environment Setup

```bash
# Set required environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/skillforge_db"
export POSTGRES_PASSWORD="your_password"
export ENVIRONMENT="development"
```

### Running the Service

```bash
# Local development
cd apps/backend/user-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# With production database
POSTGRES_PASSWORD="your_password" uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📊 Monitoring & Health Checks

### Health Endpoints

- **`GET /health`**: Service health with database and cache status
- **`GET /`**: Root endpoint with service information  
- **`GET /metrics`**: Prometheus metrics (if enabled)

### Validation Scripts

- **`scripts/validation/validate_service.py`**: Comprehensive service validation
- **`scripts/testing/integration_tests.py`**: Integration test suite

## 🏗️ Project Structure

```
apps/backend/user-service/
├── app/
│   ├── api/v1/                 # API routes and endpoints
│   ├── core/                   # Core functionality (config, database, etc.)
│   ├── crud/                   # Database operations
│   ├── models/                 # SQLModel data models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── tests/                  # Unit tests
│   └── utils/                  # Utility functions
├── scripts/
│   ├── validation/             # Service validation scripts
│   └── testing/               # Integration test scripts
├── docs/                      # Documentation
├── alembic/                   # Database migrations
└── requirements.txt           # Python dependencies
```

## 🔐 Security & Authentication

### IAP Integration

The service integrates with Google Identity-Aware Proxy for authentication:

- **Middleware**: `app.core.iap_middleware.IAPMiddleware`
- **JWT Validation**: Validates Google IAP tokens
- **User Context**: Extracts user information from IAP headers

### API Authentication

All API endpoints (except health checks) require IAP authentication:

1. User accesses domain (e.g., `api.emacsah.com`)
2. IAP redirects to Google OAuth if not authenticated  
3. After OAuth, IAP forwards request with JWT token
4. Middleware validates JWT and extracts user info
5. Request proceeds to API endpoint

## 📈 Performance & Monitoring

### Metrics Collection

- **Request latency**: Response time tracking
- **Request count**: API usage statistics  
- **Error rates**: Success/failure tracking
- **Database metrics**: Connection pool status
- **Cache metrics**: Redis performance (if enabled)

### Monitoring Integration

- **Prometheus**: `/metrics` endpoint for scraping
- **Grafana**: Dashboard configuration available
- **Structured Logging**: JSON format with correlation IDs

## 🚀 Deployment

### Production Deployment

The service is deployed on Google Cloud Run with:

- **Image**: Built via GitHub Actions
- **Environment**: `staging` and `production`
- **Database**: Google Cloud SQL (PostgreSQL)
- **Authentication**: Google IAP
- **Monitoring**: Google Cloud Monitoring + Grafana

### CI/CD Pipeline

1. **Code Push** → GitHub Actions triggered
2. **Tests** → Unit tests and validation
3. **Build** → Docker image creation  
4. **Deploy** → Cloud Run deployment
5. **Validate** → Health checks and monitoring

## 🧪 Testing

### Unit Tests

```bash
cd apps/backend/user-service
python -m pytest app/tests/ -v
```

### Integration Tests

```bash
# Start service first
python scripts/testing/integration_tests.py
```

### Service Validation

```bash
python scripts/validation/validate_service.py
```

## 📚 API Documentation

- **Interactive Docs**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

## 🔧 Configuration

Key configuration options in `app/core/config.py`:

- **Database settings**: PostgreSQL connection
- **Cache settings**: Redis configuration
- **Security settings**: CORS, trusted hosts
- **Monitoring settings**: Metrics and logging
- **IAP settings**: Authentication configuration

## 🤝 Contributing

1. Follow the existing code structure
2. Add unit tests for new features
3. Update documentation as needed
4. Ensure all validation scripts pass
5. Test with IAP authentication

## 📞 Support

For issues or questions:

- Check health endpoints first
- Run validation scripts
- Check logs and metrics
- Review IAP authentication flow

---

**Last Updated**: January 2025  
**Maintainer**: SkillForge AI Development Team