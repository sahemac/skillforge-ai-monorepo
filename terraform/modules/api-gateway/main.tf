# API Gateway Module for SkillForge AI - Test Version
# Simplified for testing with user-service only

locals {
  api_id = "skillforge-api-${var.environment}"
  api_config_id = "${local.api_id}-config-${substr(md5(file("${path.module}/openapi-test.yaml")), 0, 8)}"
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
  display_name = "SkillForge API ${var.environment} (Test)"
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    version     = "test"
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
  display_name  = "SkillForge API Config ${var.environment} (Test)"

  openapi_documents {
    document {
      path     = "openapi-test.yaml"
      contents = base64encode(templatefile("${path.module}/openapi-test.yaml", {
        project_id       = var.project_id
        environment      = var.environment
        user_service_url = var.user_service_url
      }))
    }
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    version     = "test"
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
  display_name = "SkillForge Gateway ${var.environment} (Test)"

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    version     = "test"
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