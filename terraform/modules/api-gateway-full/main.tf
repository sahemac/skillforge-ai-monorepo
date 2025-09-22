# API Gateway Module for SkillForge AI - Production Version
# Complete implementation with all 23 services

locals {
  api_id = "skillforge-api-${var.environment}"
  api_config_id = "${local.api_id}-config-${substr(md5(file("${path.module}/openapi-production.yaml")), 0, 8)}"
  gateway_id = "skillforge-gateway-${var.environment}"
}

# Enable required APIs
resource "google_project_service" "api_gateway" {
  project = var.project_id
  service = "apigateway.googleapis.com"
  
  disable_dependent_services = true
}

resource "google_project_service" "service_control" {
  project = var.project_id
  service = "servicecontrol.googleapis.com"
  
  disable_dependent_services = true
}

resource "google_project_service" "service_management" {
  project = var.project_id
  service = "servicemanagement.googleapis.com"
  
  disable_dependent_services = true
}

# API Gateway API
resource "google_api_gateway_api" "main" {
  provider     = google-beta
  project      = var.project_id
  api_id       = local.api_id
  display_name = "SkillForge API ${var.environment} (Production)"
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    version     = "production"
  }
  
  depends_on = [
    google_project_service.api_gateway,
    google_project_service.service_control,
    google_project_service.service_management
  ]
}

# API Gateway Config
resource "google_api_gateway_api_config" "main" {
  provider      = google-beta
  project       = var.project_id
  api           = google_api_gateway_api.main.api_id
  api_config_id = local.api_config_id
  display_name  = "SkillForge API Config ${var.environment} (Production)"

  openapi_documents {
    document {
      path     = "openapi-production.yaml"
      contents = base64encode(templatefile("${path.module}/openapi-production.yaml", {
        project_id = var.project_id
        environment = var.environment
        
        # Core Services
        user_service_url = var.user_service_url
        
        # Business Services  
        company_service_url = var.company_service_url
        subscription_service_url = var.subscription_service_url
        payment_service_url = var.payment_service_url
        notification_service_url = var.notification_service_url
        analytics_service_url = var.analytics_service_url
        content_service_url = var.content_service_url
        search_service_url = var.search_service_url
        storage_service_url = var.storage_service_url
        workflow_service_url = var.workflow_service_url
        audit_service_url = var.audit_service_url
        
        # Extended Services
        ai_orchestrator_service_url = var.ai_orchestrator_service_url
        chat_messaging_service_url = var.chat_messaging_service_url
        recommendation_service_url = var.recommendation_service_url
        scheduling_service_url = var.scheduling_service_url
        evaluation_service_url = var.evaluation_service_url
        matching_service_url = var.matching_service_url
        project_service_url = var.project_service_url
        portfolio_service_url = var.portfolio_service_url
        gamification_service_url = var.gamification_service_url
        localization_service_url = var.localization_service_url
        realtime_collaboration_service_url = var.realtime_collaboration_service_url
      }))
    }
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    version     = "production"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Deployment
resource "google_api_gateway_gateway" "main" {
  provider     = google-beta
  project      = var.project_id
  region       = var.region
  gateway_id   = local.gateway_id
  api_config   = google_api_gateway_api_config.main.id
  display_name = "SkillForge Gateway ${var.environment} (Production)"

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    version     = "production"
  }
}

# Service Account for API Gateway
resource "google_service_account" "api_gateway" {
  project      = var.project_id
  account_id   = "api-gateway-${var.environment}"
  display_name = "API Gateway Service Account ${var.environment}"
  description  = "Service account for API Gateway to invoke backend services"
}

# Grant API Gateway the ability to invoke Cloud Run services
resource "google_project_iam_member" "api_gateway_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.api_gateway.email}"
}

# IAP Integration for Authentication
resource "google_iap_web_iam_member" "api_gateway_users" {
  count   = length(var.authorized_users)
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "user:${var.authorized_users[count.index]}"
}

# Monitoring and Alerting
resource "google_monitoring_alert_policy" "api_gateway_high_latency" {
  display_name = "API Gateway High Latency - ${var.environment}"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "API Gateway latency > 1s"
    
    condition_threshold {
      filter          = "resource.type=\"api\" AND resource.labels.service=\"${local.api_id}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 1.0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "api_gateway_error_rate" {
  display_name = "API Gateway High Error Rate - ${var.environment}"
  project      = var.project_id
  combiner     = "OR"
  
  conditions {
    display_name = "API Gateway error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"api\" AND resource.labels.service=\"${local.api_id}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}