# terraform/environments/staging/network.tf

# Crée le réseau VPC principal
resource "google_compute_network" "vpc_main" {
  name                    = "skillforge-vpc-staging"
  auto_create_subnetworks = false # Nous gérons les sous-réseaux manuellement
}

# Crée un sous-réseau dans la région europe-west1
resource "google_compute_subnetwork" "subnet_main" {
  name          = "skillforge-subnet-staging"
  ip_cidr_range = "10.0.0.0/24"
  region        = "europe-west1"
  network       = google_compute_network.vpc_main.id
}

# Règle de pare-feu pour autoriser tout le trafic interne au VPC
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-traffic"
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

  source_ranges = ["10.0.0.0/24"] # Autorise le trafic depuis notre propre sous-réseau
}

# Crée le connecteur qui fait le pont entre Cloud Run et notre VPC.
resource "google_vpc_access_connector" "main_connector" {
  name             = "vpc-connector-staging"
  region           = "europe-west1"
  network          = google_compute_network.vpc_main.name
  ip_cidr_range    = "10.8.0.0/28"
  min_throughput   = 200 # <--- LIGNE AJOUTÉE ICI
  max_throughput   = 300 # <--- LIGNE AJOUTÉE ICI
}
