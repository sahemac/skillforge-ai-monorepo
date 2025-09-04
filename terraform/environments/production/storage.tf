# terraform/environments/staging/storage.tf

# Crée le dépôt Artifact Registry pour nos images Docker
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = var.docker_repo_name
  format        = "DOCKER"
  description   = "Docker repository for SkillForge ${var.environment} environment"

  labels = local.common_labels
}

# Crée le bucket pour les uploads des utilisateurs
resource "google_storage_bucket" "user_uploads" {
  name                        = local.user_uploads_bucket
  location                    = var.storage_location
  uniform_bucket_level_access = true
  force_destroy              = false
  
  # Support for hierarchical namespace (Data Lake buckets)
  hierarchical_namespace {
    enabled = false  # Standard bucket behavior
  }

  labels = local.common_labels

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Crée le bucket pour les fichiers statiques du Front-End
resource "google_storage_bucket" "frontend_assets" {
  name                        = local.frontend_assets_bucket
  location                    = var.storage_location
  uniform_bucket_level_access = true
  force_destroy              = false
  
  # Support for hierarchical namespace (Data Lake buckets)
  hierarchical_namespace {
    enabled = false  # Standard bucket behavior
  }

  labels = local.common_labels

  # Configure le bucket pour l'hébergement de site web statique
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html" # Pour les SPAs qui gèrent le routage
  }

  cors {
    origin          = ["https://${local.api_domain}"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}