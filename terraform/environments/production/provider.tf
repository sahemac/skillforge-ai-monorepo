# terraform/environments/staging/provider.tf

provider "google" {
  project = var.project_id
  region  = var.region
}