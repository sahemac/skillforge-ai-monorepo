# terraform/environments/staging/load_balancer.tf

# Utilise l'IP statique déjà créée manuellement
data "google_compute_global_address" "skillforge_ip" {
  name = "skillforge-global-ip"
}

# Certificat SSL managé par Google
resource "google_compute_managed_ssl_certificate" "skillforge_ssl" {
  name = "skillforge-ssl-cert"
  
  managed {
    domains = ["api.emacsah.com"]
  }
}

# Network Endpoint Group pour Cloud Run
resource "google_compute_region_network_endpoint_group" "user_service_neg" {
  name                  = "user-service-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = module.user_service.service_name
  }
}

# Backend service pointant vers Cloud Run
resource "google_compute_backend_service" "user_service_backend" {
  name        = "user-service-backend"
  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 30

  backend {
    group = google_compute_region_network_endpoint_group.user_service_neg.id
  }
}

# URL Map pour le routing
resource "google_compute_url_map" "skillforge_urlmap" {
  name            = "skillforge-urlmap"
  default_service = google_compute_backend_service.user_service_backend.id

  host_rule {
    hosts        = ["api.emacsah.com"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.user_service_backend.id
  }
}

# HTTP(S) Load Balancer
resource "google_compute_target_https_proxy" "skillforge_https_proxy" {
  name             = "skillforge-https-proxy"
  url_map          = google_compute_url_map.skillforge_urlmap.id
  ssl_certificates = [google_compute_managed_ssl_certificate.skillforge_ssl.id]
}

# Forwarding rule HTTPS
resource "google_compute_global_forwarding_rule" "skillforge_https_forwarding" {
  name       = "skillforge-https-forwarding"
  target     = google_compute_target_https_proxy.skillforge_https_proxy.id
  port_range = "443"
  ip_address = data.google_compute_global_address.skillforge_ip.address
}

# URL Map pour redirection HTTP vers HTTPS
resource "google_compute_url_map" "skillforge_redirect" {
  name = "skillforge-redirect"
  
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# Proxy HTTP pour redirection
resource "google_compute_target_http_proxy" "skillforge_http_proxy" {
  name    = "skillforge-http-proxy"
  url_map = google_compute_url_map.skillforge_redirect.id
}

# Forwarding rule HTTP (redirection vers HTTPS)
resource "google_compute_global_forwarding_rule" "skillforge_http_forwarding" {
  name       = "skillforge-http-forwarding"  
  target     = google_compute_target_http_proxy.skillforge_http_proxy.id
  port_range = "80"
  ip_address = data.google_compute_global_address.skillforge_ip.address
}

# Output de l'IP pour configuration DNS
output "load_balancer_ip" {
  description = "IP address of the load balancer"
  value       = data.google_compute_global_address.skillforge_ip.address
}