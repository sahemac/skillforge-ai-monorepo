# terraform/environments/staging/services/variables.tf

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_number" {
  description = "The GCP project number"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
}

variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "connector_id" {
  description = "VPC Access Connector ID"
  type        = string
}

variable "docker_repo_name" {
  description = "Name of the Docker repository"
  type        = string
}

variable "jwt_secret_name" {
  description = "Name of the JWT secret"
  type        = string
}

variable "postgres_password_secret_name" {
  description = "Name of the PostgreSQL password secret"
  type        = string
}

variable "cloud_run_port" {
  description = "Port for Cloud Run service"
  type        = number
  default     = 8000
}

variable "cloud_run_cpu_limit" {
  description = "CPU limit for Cloud Run service"
  type        = string
  default     = "1"
}

variable "cloud_run_memory_limit" {
  description = "Memory limit for Cloud Run service"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "cloud_run_min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "service_account_prefix" {
  description = "Prefix for service account names"
  type        = string
  default     = "sa"
}

# Local variables
locals {
  service_account_name = "${var.service_account_prefix}-${var.service_name}-${var.environment}"
  cloud_run_service_name = "${var.service_name}-${var.environment}"
  jwt_secret_full_name = "${var.jwt_secret_name}-${var.environment}"
  postgres_password_full_name = "${var.postgres_password_secret_name}-${var.environment}"
  
  docker_image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.docker_repo_name}/${var.service_name}:latest"
  
  common_labels = {
    environment = var.environment
    service     = var.service_name
    managed_by  = "terraform"
  }
}