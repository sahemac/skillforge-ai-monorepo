# API Gateway Module

This Terraform module creates a complete Google Cloud API Gateway setup for the SkillForge AI platform, providing a unified entry point for all microservices.

## Features

- **Complete API Gateway Setup**: Creates API, API Config, and Gateway resources
- **OpenAPI 3.0 Specification**: Comprehensive API documentation with all service routes
- **Security**: JWT authentication, API key support, IAP integration, Cloud Armor protection
- **Rate Limiting**: Configurable rate limits with automatic IP banning
- **Monitoring**: Built-in dashboards and alerting for performance monitoring
- **Logging**: Centralized logging with automatic log rotation
- **CORS Support**: Configurable Cross-Origin Resource Sharing
- **Service Integration**: Seamless integration with Cloud Run services

## Usage

```hcl
module "api_gateway" {
  source = "./modules/api-gateway"
  
  project_id  = var.project_id
  environment = var.environment
  region      = var.region
  
  # Service URLs (required)
  user_service_url         = module.user_service.service_url
  auth_service_url         = "https://auth-service-url"
  company_service_url      = "https://company-service-url"
  subscription_service_url = "https://subscription-service-url"
  payment_service_url      = "https://payment-service-url"
  notification_service_url = "https://notification-service-url"
  analytics_service_url    = "https://analytics-service-url"
  content_service_url      = "https://content-service-url"
  search_service_url       = "https://search-service-url"
  storage_service_url      = "https://storage-service-url"
  workflow_service_url     = "https://workflow-service-url"
  audit_service_url        = "https://audit-service-url"
  
  # Optional: Rate limiting
  rate_limit_requests_per_minute = 1000
  rate_limit_requests_per_day    = 50000
  
  # Optional: Security
  enable_iap = true
  iap_oauth_client_id     = "your-oauth-client-id"
  iap_oauth_client_secret = "your-oauth-client-secret"
  
  # Optional: CORS
  cors_allowed_origins = [
    "https://app.skillforge.ai",
    "https://admin.skillforge.ai"
  ]
  
  # Optional: Monitoring and Logging
  enable_monitoring = true
  enable_logging    = true
  
  labels = {
    environment = var.environment
    project     = "skillforge-ai"
    team        = "platform"
  }
}
```

## Service Routes

The API Gateway routes requests to the following services:

| Service | Base Path | Description |
|---------|-----------|-------------|
| User Service | `/api/v1/users/*` | User management and profiles |
| Auth Service | `/api/v1/auth/*` | Authentication and authorization |
| Company Service | `/api/v1/companies/*` | Company and organization management |
| Subscription Service | `/api/v1/subscriptions/*` | Subscription and billing management |
| Payment Service | `/api/v1/payments/*` | Payment processing |
| Notification Service | `/api/v1/notifications/*` | Notification management |
| Analytics Service | `/api/v1/analytics/*` | Analytics and reporting |
| Content Service | `/api/v1/content/*` | Content management |
| Search Service | `/api/v1/search/*` | Search functionality |
| Storage Service | `/api/v1/storage/*` | File storage and management |
| Workflow Service | `/api/v1/workflows/*` | Workflow automation |
| Audit Service | `/api/v1/audit/*` | Audit logging and compliance |

## Authentication

The API supports multiple authentication methods:

1. **JWT Bearer Tokens**: For user authentication
   - Header: `Authorization: Bearer <token>`

2. **API Keys**: For service-to-service communication
   - Header: `X-API-Key: <key>` 
   - Query parameter: `?api_key=<key>`

3. **IAP (Identity-Aware Proxy)**: Additional security layer (optional)

## Security Features

- **Rate Limiting**: Configurable per-minute and per-day limits
- **Cloud Armor**: Protection against DDoS, SQL injection, and XSS attacks
- **CORS**: Configurable cross-origin resource sharing
- **IAP Integration**: Optional Identity-Aware Proxy for additional authentication
- **Service Account**: Dedicated service account with minimal required permissions

## Monitoring and Alerting

The module includes:

- **Monitoring Dashboard**: Real-time metrics for request count and latency
- **Alert Policies**: 
  - High error rate (>5%)
  - High latency (>2 seconds)
- **Centralized Logging**: All API Gateway logs stored in Cloud Storage

## Variables

### Required Variables

| Name | Type | Description |
|------|------|-------------|
| `project_id` | string | GCP project ID |
| `environment` | string | Environment name (staging, production) |
| `user_service_url` | string | URL for the user service |
| `auth_service_url` | string | URL for the auth service |
| `company_service_url` | string | URL for the company service |
| `subscription_service_url` | string | URL for the subscription service |
| `payment_service_url` | string | URL for the payment service |
| `notification_service_url` | string | URL for the notification service |
| `analytics_service_url` | string | URL for the analytics service |
| `content_service_url` | string | URL for the content service |
| `search_service_url` | string | URL for the search service |
| `storage_service_url` | string | URL for the storage service |
| `workflow_service_url` | string | URL for the workflow service |
| `audit_service_url` | string | URL for the audit service |

### Optional Variables

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `region` | string | `"europe-west1"` | GCP region |
| `api_id` | string | `"skillforge-api"` | API Gateway API ID |
| `display_name` | string | `"SkillForge AI API"` | Display name for the API |
| `rate_limit_requests_per_minute` | number | `1000` | Rate limit per minute |
| `rate_limit_requests_per_day` | number | `10000` | Rate limit per day |
| `enable_iap` | bool | `false` | Enable Identity-Aware Proxy |
| `enable_monitoring` | bool | `true` | Enable monitoring |
| `enable_logging` | bool | `true` | Enable logging |
| `cors_allowed_origins` | list(string) | `["*"]` | Allowed CORS origins |
| `labels` | map(string) | `{}` | Resource labels |

## Outputs

| Name | Description |
|------|-------------|
| `gateway_url` | The URL of the API Gateway |
| `api_id` | The ID of the API |
| `config_id` | The ID of the API config |
| `gateway_id` | The ID of the API Gateway |
| `service_account_email` | Email of the API Gateway service account |
| `default_hostname` | Default hostname of the API Gateway |

## Prerequisites

Before using this module, ensure:

1. **APIs Enabled**: The module automatically enables required APIs
2. **Service URLs**: All backend service URLs must be accessible
3. **Permissions**: Sufficient permissions to create API Gateway resources
4. **DNS**: If using custom domains, ensure proper DNS configuration

## Examples

### Basic Setup

```hcl
module "api_gateway" {
  source = "./modules/api-gateway"
  
  project_id  = "skillforge-ai-prod"
  environment = "production"
  
  user_service_url = "https://user-service-prod-xyz.a.run.app"
  # ... other service URLs
}
```

### Production Setup with Security

```hcl
module "api_gateway" {
  source = "./modules/api-gateway"
  
  project_id  = "skillforge-ai-prod"
  environment = "production"
  
  # Service URLs
  user_service_url = "https://user-service-prod-xyz.a.run.app"
  # ... other service URLs
  
  # Enhanced security
  enable_iap = true
  iap_oauth_client_id     = var.iap_client_id
  iap_oauth_client_secret = var.iap_client_secret
  
  # Stricter rate limiting
  rate_limit_requests_per_minute = 500
  rate_limit_requests_per_day    = 10000
  
  # Specific CORS origins
  cors_allowed_origins = [
    "https://app.skillforge.ai",
    "https://admin.skillforge.ai"
  ]
  
  labels = {
    environment = "production"
    team        = "platform"
    cost-center = "engineering"
  }
}
```

## Troubleshooting

### Common Issues

1. **Service Unreachable**: Ensure all service URLs are correct and accessible
2. **Authentication Errors**: Verify service account permissions
3. **CORS Issues**: Check allowed origins configuration
4. **Rate Limiting**: Monitor rate limit settings and adjust as needed

### Debugging

- Check API Gateway logs in Cloud Logging
- Use the monitoring dashboard for performance insights
- Verify OpenAPI specification in the Google Cloud Console

## Contributing

When modifying this module:

1. Update the OpenAPI specification for new endpoints
2. Add appropriate security rules for new services
3. Update monitoring and alerting as needed
4. Test thoroughly in staging before production deployment