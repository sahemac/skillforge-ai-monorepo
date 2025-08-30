# terraform/environments/staging/variables.tf
variable "project_id" {
  type        = string
  description = "The GCP project ID to deploy to."
  default     = "skillforge-ai-mvp-25"
}

variable "project_number" {
  type        = string
  description = "The GCP project number (numeric ID) for secret references."
  default     = "584748485117"
}

variable "region" {
  type        = string
  description = "The primary GCP region for resources."
  default     = "europe-west1"
}