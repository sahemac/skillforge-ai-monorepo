# terraform/environments/staging/storage.tf

# Crée le dépôt Artifact Registry pour nos images Docker
resource "google_artifact_registry_repository" "docker_repo" {
  location      = "europe-west1"
  repository_id = "skillforge-docker-repo-staging"
  format        = "DOCKER"
  description   = "Docker repository for SkillForge staging environment"
}

# Crée le bucket pour les uploads des utilisateurs
resource "google_storage_bucket" "user_uploads" {
  name                        = "skillforge-ai-mvp-25-user-uploads-staging"
  location                    = "EUROPE-WEST1"
  uniform_bucket_level_access = true
}

# Crée le bucket pour les fichiers statiques du Front-End
resource "google_storage_bucket" "frontend_assets" {
  name                        = "skillforge-ai-mvp-25-frontend-assets-staging"
  location                    = "EUROPE-WEST1"
  uniform_bucket_level_access = true

  # Configure le bucket pour l'hébergement de site web statique
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html" # Pour les SPAs qui gèrent le routage
  }
}