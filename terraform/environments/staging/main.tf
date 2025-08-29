# terraform/environments/staging/main.tf

# Créer le secret pour la clé JWT (il ne doit être créé qu'une seule fois)
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret-key-staging"

  replication {
    auto {} # <--- SYNTAXE FINALE ET CORRECTE
  }
}

# Appeler notre module de service pour créer le user-service
module "user_service" {
  source = "./services" # Chemin vers notre module

  # On passe les valeurs pour les variables que le module attend
  project_id   = var.project_id
  region       = var.region
  connector_id = google_vpc_access_connector.main_connector.id
  service_name = "user-service"
}