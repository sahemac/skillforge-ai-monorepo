# Variables for API Gateway Test Module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "user_service_url" {
  description = "URL for the user service"
  type        = string
}

variable "custom_domain" {
  description = "Custom domain for API Gateway (optional)"
  type        = string
  default     = ""
}

variable "dns_zone_name" {
  description = "DNS zone name for custom domain"
  type        = string
  default     = "emacsah.com"
}

variable "dns_zone_id" {
  description = "DNS zone ID for custom domain"
  type        = string
  default     = ""
}

variable "notification_channels" {
  description = "Notification channels for monitoring alerts"
  type        = list(string)
  default     = []
}