# terraform/environments/staging/backend.tf

terraform {
  backend "gcs" {
    bucket = "skillforge-ai-mvp-25-tfstate"
    prefix = "staging" # Un sous-dossier pour l'état de l'environnement staging
  }
}