# Variables for monitoring module

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "europe-west1"
}

variable "environment" {
  description = "Environment (staging, production, etc.)"
  type        = string
}

variable "notification_channels" {
  description = "List of notification channel IDs for alerts"
  type        = list(string)
  default     = []
}

variable "service_id" {
  description = "Service ID for SLOs"
  type        = string
}

variable "dashboard_labels" {
  description = "Labels to apply to dashboards"
  type        = map(string)
  default     = {}
}

variable "alert_labels" {
  description = "Labels to apply to alert policies"
  type        = map(string)
  default     = {}
}

variable "enable_slos" {
  description = "Whether to create SLOs"
  type        = bool
  default     = true
}

variable "error_rate_threshold" {
  description = "Threshold for error rate alerts (errors per second)"
  type        = number
  default     = 10
}

variable "response_time_threshold" {
  description = "Threshold for response time alerts (seconds)"
  type        = number
  default     = 2.0
}

variable "cache_hit_ratio_threshold" {
  description = "Minimum cache hit ratio before alerting"
  type        = number
  default     = 0.7
}

variable "auth_failure_threshold" {
  description = "Threshold for authentication failure alerts (failures per second)"
  type        = number
  default     = 20
}

variable "db_error_threshold" {
  description = "Threshold for database error alerts (errors per second)"
  type        = number
  default     = 5
}