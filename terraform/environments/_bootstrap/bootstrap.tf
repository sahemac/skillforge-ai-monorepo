# terraform/environments/_bootstrap/bootstrap.tf

# Configure le fournisseur Google Cloud.
provider "google" {
  project = "skillforge-ai-mvp-25"
  region  = "europe-west1"
}

# Crée un bucket GCS unique pour stocker l'état de Terraform.
# Le nom doit être globalement unique.
resource "google_storage_bucket" "tfstate" {
  name                        = "skillforge-ai-mvp-25-tfstate"
  location                    = "EUROPE-WEST1"
  force_destroy               = false # Sécurité pour ne pas le supprimer accidentellement.
  uniform_bucket_level_access = true  # <--- LIGNE AJOUTÉE ICI

  # Active le versioning pour garder un historique des états.
  versioning {
    enabled = true
  }
}