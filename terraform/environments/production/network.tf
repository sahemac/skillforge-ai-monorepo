# terraform/environments/staging/network.tf

# Crée le réseau VPC principal
resource "google_compute_network" "vpc_main" {
  name                    = local.vpc_name
  auto_create_subnetworks = false # Nous gérons les sous-réseaux manuellement
  
  labels = local.common_labels
}

# Crée un sous-réseau dans la région principale
resource "google_compute_subnetwork" "subnet_main" {
  name          = local.subnet_name
  ip_cidr_range = var.vpc_cidr
  region        = var.region
  network       = google_compute_network.vpc_main.id
}

# Règle de pare-feu pour autoriser tout le trafic interne au VPC
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-traffic-${var.environment}"
  network = google_compute_network.vpc_main.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [var.vpc_cidr] # Autorise le trafic depuis notre propre sous-réseau
}

# Crée le connecteur qui fait le pont entre Cloud Run et notre VPC.
resource "google_vpc_access_connector" "main_connector" {
  name             = local.vpc_connector_name
  region           = var.region
  network          = google_compute_network.vpc_main.name
  ip_cidr_range    = var.vpc_connector_cidr
  min_throughput   = 200
  max_throughput   = 300
}
