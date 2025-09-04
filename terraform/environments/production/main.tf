# terraform/environments/staging/main.tf
# Créer le secret pour la clé JWT (il ne doit être créé qu'une seule fois)
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = local.jwt_secret_full_name
  
  labels = local.common_labels
  
  replication {
    auto {}
  }
}

# Appeler notre module de service pour créer le user-service
module "user_service" {
  source = "./services" # Chemin vers notre module
  
  # Configuration de base
  project_id                      = var.project_id
  project_number                 = var.project_number
  region                         = var.region
  environment                    = var.environment
  
  # Configuration du service
  service_name                   = "user-service"
  connector_id                   = google_vpc_access_connector.main_connector.id
  
  # Configuration Docker
  docker_repo_name               = var.docker_repo_name
  
  # Configuration des secrets
  jwt_secret_name                = var.jwt_secret_name
  postgres_password_secret_name  = var.postgres_password_secret_name
  
  # Configuration Cloud Run
  cloud_run_port                 = var.cloud_run_port
  cloud_run_cpu_limit            = var.cloud_run_cpu_limit
  cloud_run_memory_limit         = var.cloud_run_memory_limit
  cloud_run_max_instances        = var.cloud_run_max_instances
  cloud_run_min_instances        = var.cloud_run_min_instances
  
  # Préfixe service account
  service_account_prefix         = var.service_account_prefix
}