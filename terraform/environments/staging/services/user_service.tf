# terraform/environments/staging/services/user_service.tf

resource "google_service_account" "service_sa" {
  account_id   = "sa-${var.service_name}-staging"
  display_name = "Service Account for ${var.service_name} (Staging)"
}

resource "google_project_iam_member" "db_access" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.service_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "db_password_access" {
  secret_id = "postgres-password-staging"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.service_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "jwt_access" {
  secret_id = "jwt-secret-key-staging"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.service_sa.email}"
}

resource "google_cloud_run_v2_service" "service" {
  name     = "${var.service_name}-staging"
  location = var.region
  # Ajouter cette ligne pour permettre la suppression
  deletion_protection = false

  template {
    service_account = google_service_account.service_sa.email

    containers {
      image = "europe-west1-docker.pkg.dev/${var.project_id}/skillforge-docker-repo-staging/${var.service_name}:latest"

      # Configuration pour Load Balancer
      ports {
        container_port = 8000
      }

      env {
        name = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = "projects/${var.project_id}/secrets/jwt-secret-key-staging"
            version = "latest"
          }
        }
      }
    }

    vpc_access {
      connector = var.connector_id
      egress    = "ALL_TRAFFIC"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# ✅ SUPPRIMÉ : La ressource IAM "allUsers" qui causait l'erreur
# L'accès se fera uniquement via le Load Balancer
# Ceci est plus sécurisé et respecte les politiques organisationnelles