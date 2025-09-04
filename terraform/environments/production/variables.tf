# terraform/environments/staging/variables.tf

# ================================
# PROJECT & ENVIRONMENT VARIABLES
# ================================

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
}

variable "project_number" {
  description = "The GCP project number (used for IAM bindings)"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
}

variable "region" {
  description = "Primary GCP region for resources"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "Primary GCP zone within the region"
  type        = string
  default     = "europe-west1-b"
}

# ================================
# NAMING VARIABLES
# ================================

variable "project_prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "skillforge"
}

variable "organization_domain" {
  description = "Organization domain for DNS and certificates"
  type        = string
}

variable "api_subdomain" {
  description = "API subdomain for the load balancer"
  type        = string
  default     = "api"
}

# ================================
# NETWORK VARIABLES
# ================================

variable "vpc_cidr" {
  description = "CIDR range for the main VPC subnet"
  type        = string
  default     = "10.0.0.0/24"
}

variable "vpc_connector_cidr" {
  description = "CIDR range for the VPC Access Connector"
  type        = string
  default     = "10.8.0.0/28"
}

variable "private_services_cidr_prefix" {
  description = "CIDR prefix length for private services (Cloud SQL, Redis)"
  type        = number
  default     = 16
}

# ================================
# DATABASE VARIABLES
# ================================

variable "database_tier" {
  description = "Machine type for Cloud SQL instance"
  type        = string
  default     = "db-g1-small"
}

variable "database_version" {
  description = "PostgreSQL version for Cloud SQL"
  type        = string
  default     = "POSTGRES_16"
}

variable "database_name" {
  description = "Name of the main database"
  type        = string
  default     = "skillforge_db"
}

variable "database_user" {
  description = "Name of the main database user"
  type        = string
  default     = "skillforge_user"
}

variable "database_backup_enabled" {
  description = "Enable automated backups for Cloud SQL"
  type        = bool
  default     = true
}

# ================================
# REDIS VARIABLES
# ================================

variable "redis_memory_size_gb" {
  description = "Memory size in GB for Redis instance"
  type        = number
  default     = 1
}

variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

# ================================
# DOCKER REGISTRY VARIABLES
# ================================

variable "docker_repo_name" {
  description = "Name of the Docker repository in Artifact Registry"
  type        = string
}

# ================================
# SERVICE VARIABLES
# ================================

variable "service_account_prefix" {
  description = "Prefix for service account names"
  type        = string
  default     = "sa"
}

variable "cloud_run_port" {
  description = "Port for Cloud Run services"
  type        = number
  default     = 8000
}

variable "cloud_run_cpu_limit" {
  description = "CPU limit for Cloud Run services"
  type        = string
  default     = "1"
}

variable "cloud_run_memory_limit" {
  description = "Memory limit for Cloud Run services"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of instances for Cloud Run services"
  type        = number
  default     = 10
}

variable "cloud_run_min_instances" {
  description = "Minimum number of instances for Cloud Run services"
  type        = number
  default     = 0
}

# ================================
# STORAGE VARIABLES
# ================================

variable "storage_location" {
  description = "Location for Cloud Storage buckets"
  type        = string
  default     = "EUROPE-WEST1"
}

# ================================
# SECRETS VARIABLES
# ================================

variable "jwt_secret_name" {
  description = "Name of the JWT secret in Secret Manager"
  type        = string
  default     = "jwt-secret-key"
}

variable "postgres_password_secret_name" {
  description = "Name of the PostgreSQL password secret in Secret Manager"
  type        = string
  default     = "postgres-password"
}

# ================================
# LOAD BALANCER VARIABLES
# ================================

variable "global_ip_name" {
  description = "Name of the global static IP address"
  type        = string
}

variable "ssl_certificate_domains" {
  description = "List of domains for the SSL certificate"
  type        = list(string)
}

# ================================
# MONITORING VARIABLES
# ================================

variable "monitoring_notification_email" {
  description = "Email address for monitoring notifications"
  type        = string
  default     = ""
}

variable "enable_monitoring_alerts" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

# ================================
# COMPUTED/DERIVED VARIABLES
# ================================

locals {
  # Environment-specific naming
  name_suffix = var.environment
  
  # Full domain name for API
  api_domain = "${var.api_subdomain}.${var.organization_domain}"
  
  # Resource naming patterns
  vpc_name                = "${var.project_prefix}-vpc-${local.name_suffix}"
  subnet_name            = "${var.project_prefix}-subnet-${local.name_suffix}"
  vpc_connector_name     = "${var.project_prefix}-vpc-connector-${local.name_suffix}"
  
  # Database names
  database_instance_name = "${var.project_prefix}-pg-instance-${local.name_suffix}"
  
  # Redis names
  redis_instance_name = "${var.project_prefix}-redis-instance-${local.name_suffix}"
  
  # Storage bucket names
  user_uploads_bucket = "${var.project_id}-user-uploads-${local.name_suffix}"
  frontend_assets_bucket = "${var.project_id}-frontend-assets-${local.name_suffix}"
  
  # Secret names with environment
  jwt_secret_full_name = "${var.jwt_secret_name}-${local.name_suffix}"
  postgres_password_full_name = "${var.postgres_password_secret_name}-${local.name_suffix}"
  
  # Load balancer names
  ssl_cert_name = "${var.project_prefix}-ssl-cert-${local.name_suffix}"
  urlmap_name = "${var.project_prefix}-urlmap-${local.name_suffix}"
  https_proxy_name = "${var.project_prefix}-https-proxy-${local.name_suffix}"
  https_forwarding_name = "${var.project_prefix}-https-forwarding-${local.name_suffix}"
  redirect_urlmap_name = "${var.project_prefix}-redirect-${local.name_suffix}"
  http_proxy_name = "${var.project_prefix}-http-proxy-${local.name_suffix}"
  http_forwarding_name = "${var.project_prefix}-http-forwarding-${local.name_suffix}"
  
  # Private services access
  private_service_access_name = "private-service-access-${local.name_suffix}"
  
  # Common tags
  common_labels = {
    environment = var.environment
    project     = var.project_prefix
    managed_by  = "terraform"
  }
}