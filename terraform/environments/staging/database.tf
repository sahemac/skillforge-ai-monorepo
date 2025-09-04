# terraform/environments/staging/database.tf

# Référence au secret que nous avons créé manuellement.
data "google_secret_manager_secret_version" "postgres_password" {
  secret = local.postgres_password_full_name
}

# Crée l'instance principale de PostgreSQL
resource "google_sql_database_instance" "main_postgres" {
  name             = local.database_instance_name
  database_version = var.database_version
  region           = var.region

  # S'assure que la connexion réseau est établie AVANT d'essayer de créer la BDD
  depends_on = [google_service_networking_connection.main_peering]

  settings {
    tier    = var.database_tier
    edition = "ENTERPRISE"
    
    user_labels = local.common_labels

    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.vpc_main.id
    }

    backup_configuration {
      enabled = var.database_backup_enabled
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }
    
    insights_config {
      query_insights_enabled  = true
      query_string_length    = 1024
      record_application_tags = false
      record_client_address   = false
    }
  }

  deletion_protection = true
}

# Crée la base de données principale à l'intérieur de l'instance
resource "google_sql_database" "main_db" {
  name     = var.database_name
  instance = google_sql_database_instance.main_postgres.name
}

# Crée l'utilisateur applicatif pour la base de données
resource "google_sql_user" "app_user" {
  name     = var.database_user
  instance = google_sql_database_instance.main_postgres.name
  password = data.google_secret_manager_secret_version.postgres_password.secret_data
}