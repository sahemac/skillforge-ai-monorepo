# terraform/environments/staging/database.tf

# Référence au secret que nous avons créé manuellement.
data "google_secret_manager_secret_version" "postgres_password" {
  secret = "postgres-password-staging"
}

# Crée l'instance principale de PostgreSQL
resource "google_sql_database_instance" "main_postgres" {
  name             = "skillforge-pg-instance-staging"
  database_version = "POSTGRES_16"
  region           = "europe-west1"

  # S'assure que la connexion réseau est établie AVANT d'essayer de créer la BDD
  depends_on = [google_service_networking_connection.main_peering]

  settings {
    tier    = "db-g1-small" # <--- MODIFIÉ ICI pour un type compatible
    edition = "ENTERPRISE"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_main.id
    }

    backup_configuration {
      enabled = true
    }
  }
}

# Crée la base de données "skillforge_db" à l'intérieur de l'instance
resource "google_sql_database" "main_db" {
  name     = "skillforge_db"
  instance = google_sql_database_instance.main_postgres.name
}

# Crée l'utilisateur applicatif pour la base de données
resource "google_sql_user" "app_user" {
  name     = "skillforge_user"
  instance = google_sql_database_instance.main_postgres.name
  password = data.google_secret_manager_secret_version.postgres_password.secret_data
}