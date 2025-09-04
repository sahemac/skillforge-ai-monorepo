# terraform/environments/staging/services/user_service.tf

resource "google_service_account" "service_sa" {
  account_id   = local.service_account_name
  display_name = "Service Account for ${var.service_name} (${title(var.environment)})"
}

resource "google_project_iam_member" "db_access" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.service_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "db_password_access" {
  secret_id = local.postgres_password_full_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.service_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "jwt_access" {
  secret_id = local.jwt_secret_full_name
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.service_sa.email}"
}

resource "google_cloud_run_v2_service" "service" {
  name     = local.cloud_run_service_name
  location = var.region
  
  labels = local.common_labels

  template {
    service_account = google_service_account.service_sa.email
    
    labels = local.common_labels

    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }

    containers {
      image = local.docker_image

      ports {
        container_port = var.cloud_run_port
      }

      resources {
        limits = {
          cpu    = var.cloud_run_cpu_limit
          memory = var.cloud_run_memory_limit
        }
      }

      env {
        name = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name = "SERVICE_NAME"
        value = var.service_name
      }

      env {
        name = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = local.jwt_secret_full_name
            version = "latest"
          }
        }
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = local.postgres_password_full_name
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

# Pas de binding IAM ici - l'authentification se fait via IAP sur le Load Balancer