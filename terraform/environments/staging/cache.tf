# terraform/environments/staging/cache.tf

# Réserve une plage d'adresses IP pour les services managés Google
resource "google_compute_global_address" "private_service_access" {
  name          = "private-service-access-staging"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  ip_version    = "IPV4"
  prefix_length = 16
  network       = google_compute_network.vpc_main.id
}

# Crée la connexion de peering entre notre VPC et les services Google
resource "google_service_networking_connection" "main_peering" {
  network                 = google_compute_network.vpc_main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_access.name]
}

# Crée l'instance Redis
resource "google_redis_instance" "main_redis" {
  name               = "skillforge-redis-instance-staging"
  tier               = "BASIC" # Tier de base pour le staging
  memory_size_gb     = 1
  location_id        = "europe-west1-b"
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  authorized_network = google_compute_network.vpc_main.id

  # S'assure que la connexion de peering est établie avant de créer l'instance Redis
  depends_on = [google_service_networking_connection.main_peering]
}