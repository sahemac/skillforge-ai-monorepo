# terraform/environments/staging/provider.tf

provider "google" {
  project = "skillforge-ai-mvp-25"
  region  = "europe-west1"
}