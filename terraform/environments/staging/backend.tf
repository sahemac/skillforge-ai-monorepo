# terraform/environments/staging/backend.tf

terraform {
  backend "gcs" {
    # Note: bucket name cannot use variables in backend configuration
    # This must be updated manually for each environment
    bucket = "skillforge-ai-mvp-25-tfstate"
    prefix = "staging" # Un sous-dossier pour l'état de l'environnement staging
  }
  
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "= 7.1.1"
    }
  }
}


