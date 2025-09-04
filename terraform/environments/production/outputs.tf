# terraform/environments/staging/outputs.tf

# ================================
# LOAD BALANCER OUTPUTS
# ================================

output "load_balancer_ip" {
  description = "IP address of the load balancer"
  value       = data.google_compute_global_address.skillforge_ip.address
}

output "api_domain" {
  description = "API domain URL"
  value       = "https://${local.api_domain}"
}

output "ssl_certificate_name" {
  description = "Name of the SSL certificate"
  value       = google_compute_managed_ssl_certificate.skillforge_ssl.name
}

# ================================
# NETWORK OUTPUTS
# ================================

output "vpc_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.vpc_main.name
}

output "vpc_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.vpc_main.id
}

output "subnet_name" {
  description = "Name of the main subnet"
  value       = google_compute_subnetwork.subnet_main.name
}

output "vpc_connector_id" {
  description = "ID of the VPC Access Connector"
  value       = google_vpc_access_connector.main_connector.id
}

# ================================
# DATABASE OUTPUTS
# ================================

output "database_instance_name" {
  description = "Name of the Cloud SQL instance"
  value       = google_sql_database_instance.main_postgres.name
}

output "database_connection_name" {
  description = "Connection name of the Cloud SQL instance"
  value       = google_sql_database_instance.main_postgres.connection_name
}

output "database_private_ip" {
  description = "Private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.main_postgres.private_ip_address
  sensitive   = true
}

# ================================
# REDIS OUTPUTS
# ================================

output "redis_instance_name" {
  description = "Name of the Redis instance"
  value       = google_redis_instance.main_redis.name
}

output "redis_host" {
  description = "Host IP of the Redis instance"
  value       = google_redis_instance.main_redis.host
  sensitive   = true
}

output "redis_port" {
  description = "Port of the Redis instance"
  value       = google_redis_instance.main_redis.port
}

# ================================
# STORAGE OUTPUTS
# ================================

output "docker_repository_url" {
  description = "URL of the Docker repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.docker_repo_name}"
}

output "user_uploads_bucket_name" {
  description = "Name of the user uploads bucket"
  value       = google_storage_bucket.user_uploads.name
}

output "frontend_assets_bucket_name" {
  description = "Name of the frontend assets bucket"
  value       = google_storage_bucket.frontend_assets.name
}

output "frontend_assets_url" {
  description = "URL of the frontend assets bucket"
  value       = "https://storage.googleapis.com/${google_storage_bucket.frontend_assets.name}"
}

# ================================
# SERVICES OUTPUTS
# ================================

output "user_service_name" {
  description = "Name of the user service"
  value       = module.user_service.service_name
}

output "user_service_url" {
  description = "URL of the user service"
  value       = module.user_service.service_url
}

output "user_service_account_email" {
  description = "Email of the user service account"
  value       = module.user_service.service_account_email
}

# ================================
# SECRETS OUTPUTS
# ================================

output "jwt_secret_name" {
  description = "Name of the JWT secret"
  value       = google_secret_manager_secret.jwt_secret.secret_id
}

# ================================
# ENVIRONMENT INFO
# ================================

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}