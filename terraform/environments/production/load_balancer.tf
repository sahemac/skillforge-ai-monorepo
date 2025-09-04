# terraform/environments/staging/load_balancer.tf

# Utilise l'IP statique déjà créée manuellement
data "google_compute_global_address" "skillforge_ip" {
  name = var.global_ip_name
}

# Certificat SSL managé par Google
resource "google_compute_managed_ssl_certificate" "skillforge_ssl" {
  name = local.ssl_cert_name
  
  managed {
    domains = var.ssl_certificate_domains
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Network Endpoint Group pour Cloud Run
resource "google_compute_region_network_endpoint_group" "user_service_neg" {
  name                  = "user-service-neg-${var.environment}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = module.user_service.service_name
  }
  
  description = "NEG for user service in ${var.environment}"
}

# Backend service pointant vers Cloud Run
resource "google_compute_backend_service" "user_service_backend" {
  name        = "user-service-backend-${var.environment}"
  protocol    = "HTTP"
  port_name   = "http"
  timeout_sec = 30
  
  enable_cdn = var.environment == "production" ? true : false

  backend {
    group = google_compute_region_network_endpoint_group.user_service_neg.id
  }

  # Configuration pour Identity-Aware Proxy sera faite manuellement
  
  log_config {
    enable      = true
    sample_rate = var.environment == "production" ? 0.1 : 1.0
  }
}

# Cloud Armor Security Policy sera configuré manuellement si nécessaire

# URL Map pour le routing
resource "google_compute_url_map" "skillforge_urlmap" {
  name            = local.urlmap_name
  default_service = google_compute_backend_service.user_service_backend.id

  dynamic "host_rule" {
    for_each = var.ssl_certificate_domains
    content {
      hosts        = [host_rule.value]
      path_matcher = "allpaths"
    }
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.user_service_backend.id

    path_rule {
      paths   = ["/api/v1/*"]
      service = google_compute_backend_service.user_service_backend.id
    }

    path_rule {
      paths   = ["/health", "/metrics"]
      service = google_compute_backend_service.user_service_backend.id
    }
  }
}

# HTTP(S) Load Balancer
resource "google_compute_target_https_proxy" "skillforge_https_proxy" {
  name             = local.https_proxy_name
  url_map          = google_compute_url_map.skillforge_urlmap.id
  ssl_certificates = [google_compute_managed_ssl_certificate.skillforge_ssl.id]
}

# Forwarding rule HTTPS
resource "google_compute_global_forwarding_rule" "skillforge_https_forwarding" {
  name       = local.https_forwarding_name
  target     = google_compute_target_https_proxy.skillforge_https_proxy.id
  port_range = "443"
  ip_address = data.google_compute_global_address.skillforge_ip.address
  
  depends_on = [google_compute_managed_ssl_certificate.skillforge_ssl]
}

# URL Map pour redirection HTTP vers HTTPS
resource "google_compute_url_map" "skillforge_redirect" {
  name = local.redirect_urlmap_name
  
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# Proxy HTTP pour redirection
resource "google_compute_target_http_proxy" "skillforge_http_proxy" {
  name    = local.http_proxy_name
  url_map = google_compute_url_map.skillforge_redirect.id
}

# Forwarding rule HTTP (redirection vers HTTPS)
resource "google_compute_global_forwarding_rule" "skillforge_http_forwarding" {
  name       = local.http_forwarding_name
  target     = google_compute_target_http_proxy.skillforge_http_proxy.id
  port_range = "80"
  ip_address = data.google_compute_global_address.skillforge_ip.address
}