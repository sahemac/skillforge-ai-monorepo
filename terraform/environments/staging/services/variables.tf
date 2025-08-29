# terraform/environments/staging/services/variables.tf

variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region for the service."
  type        = string
}

variable "connector_id" {
  description = "The ID of the VPC Access Connector."
  type        = string
}

variable "service_name" {
  description = "The name of the service (e.g., user-service)."
  type        = string
}