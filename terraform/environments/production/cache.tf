# terraform/environments/staging/cache.tf

# Réserve une plage d'adresses IP pour les services managés Google
resource "google_compute_global_address" "private_service_access" {
  name          = local.private_service_access_name
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  ip_version    = "IPV4"
  prefix_length = var.private_services_cidr_prefix
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
  name               = local.redis_instance_name
  tier               = var.redis_tier
  memory_size_gb     = var.redis_memory_size_gb
  location_id        = var.zone
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  authorized_network = google_compute_network.vpc_main.id

  labels = local.common_labels

  # S'assure que la connexion de peering est établie avant de créer l'instance Redis
  depends_on = [google_service_networking_connection.main_peering]
}