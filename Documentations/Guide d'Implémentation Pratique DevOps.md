### Guide d'Implémentation et Runbook de la Plateforme SkillForge AI

  - Version : 1.0
  - Date : 24 juin 2025
  - Propriétaire : Ingénieur DevOps


  - 


### Partie 1 : Initialisation de l'Environnement Global (Jour 0)

1.1. Introduction

Ce document est un guide pratique destiné à l'ingénieur DevOps ou au fondateur technique pour mettre en place l'infrastructure fondamentale du projet SkillForge AI. Les opérations décrites dans cette section sont généralement effectuées une seule fois au tout début du projet. Elles créent le socle sur lequel tout le reste sera construit.

Prérequis :

  - Disposer d'un compte Google Cloud avec une organisation et un compte de facturation actifs.
  - Avoir les droits nécessaires pour créer des projets et gérer les permissions IAM.
  - Avoir la CLI gcloud installée et authentifiée.
1.2. Création et Configuration du Projet Google Cloud

creation du compte cloud identity et de l’organisation (car j’utilise un compte gmail personnel): mon utilisateur compte admin de cloud identity est : sah@emacsah.com, le nom de l’organisation est SkillForge AI. tout ceci est a configurer a partir de : inscription a cloud identity free

Nous allons créer un projet GCP dédié qui hébergera toutes nos ressources.

  1. Définir les variables d'environnement : Ouvrez un terminal et définissez les variables suivantes pour simplifier les commandes.
# Remplacez par l'ID de votre organisation GCP (ex: 123456789012)

export ORGANIZATION_ID="<ID_ORGANISATION_GCP>"



# Remplacez par l'ID de votre compte de facturation (ex: 01A2B3-C4D5E6-F7G8H9)

export BILLING_ACCOUNT_ID="<ID_COMPTE_FACTURATION>"



# Choisissez un ID unique pour le projet.

export PROJECT_ID="skillforge-ai-mvp"





2. Créer le projet GCP :



gcloud projects create ${PROJECT_ID} --organization=${ORGANIZATION_ID}

3. Lier le compte de facturation :



gcloud billing projects link ${PROJECT_ID} --billing-account=${BILLING_ACCOUNT_ID}



4. Définir le projet comme défaut pour la CLI gcloud :

gcloud config set project ${PROJECT_ID}



5. Activer les APIs nécessaires : C'est une étape cruciale pour autoriser l'utilisation des services dont nous aurons besoin.



gcloud services enable \

  iam.googleapis.com \

  cloudresourcemanager.googleapis.com \

  secretmanager.googleapis.com \

  artifactregistry.googleapis.com \

  run.googleapis.com \

  sqladmin.googleapis.com \

  redis.googleapis.com \

  container.googleapis.com \

  cloudbuild.googleapis.com \

  iamcredentials.googleapis.com



1.3. Création et Configuration du Dépôt GitHub

  1. Création du Dépôt :
  1. Création des Branches Initiales :
git checkout -b develop

git push -u origin develop

# Revenez sur la branche main

git checkout main



  1. Configuration des Règles de Protection de Branche :
1.4. Configuration de l'Authentification CI/CD (GitHub Actions ↔ GCP)

Nous allons configurer une connexion sécurisée et sans mot de passe pour permettre à GitHub Actions de déployer sur GCP, en utilisant Workload Identity Federation.

  1. Créer un Compte de Service pour la CI/CD sur GCP :
gcloud iam service-accounts create sa-github-actions-cicd \

  --display-name="Service Account for GitHub Actions CI/CD"



   2. Donner les Permissions au Compte de Service : Pour l'initialisation du projet, nous lui donnons un rôle large. Ces permissions seront affinées plus tard.



gcloud projects add-iam-policy-binding ${PROJECT_ID} \

--member="serviceAccount:sa-github-actions-cicd@${PROJECT_ID}.iam.gserviceaccount.com" \

  --role="roles/owner"



   3. Créer un "Workload Identity Pool" et un Fournisseur :



# Créer le Pool

gcloud iam workload-identity-pools create skillforge-pool \

  --location="global" \

  --display-name="SkillForge Identity Pool"



# Obtenir l'ID complet du Pool

export POOL_ID=$(gcloud iam workload-identity-pools describe skillforge-pool --location="global" --format="value(name)")



# Créer le Fournisseur OIDC pour GitHub

gcloud iam workload-identity-pools providers create-oidc github-provider \

  --location="global" \

  --workload-identity-pool="skillforge-pool" \

  --issuer-uri="https://token.actions.githubusercontent.com" \

  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"





 4. Lier le Dépôt GitHub au Compte de Service GCP : C'est l'étape finale qui autorise les actions de votre dépôt à usurper l'identité du compte de service GCP.



gcloud iam service-accounts add-iam-policy-binding "sa-github-actions-cicd@${PROJECT_ID}.iam.gserviceaccount.com" \

  --role="roles/iam.workloadIdentityUser" \

  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/VOTRE_ORGANISATION_GITHUB/skillforge-ai-monorepo"



(Remplacez VOTRE_ORGANISATION_GITHUB par le nom de votre organisation ou utilisateur GitHub).



 5. Obtenir l'ID du Fournisseur pour les Workflows :

  - Exécutez cette commande et conservez la sortie. Vous en aurez besoin pour vos fichiers de workflow GitHub Actions.
gcloud iam workload-identity-pools providers describe github-provider \

  --location="global" \

  --workload-identity-pool="skillforge-pool" \

  --format="value(name)"





### Partie 2 : Construction de l'Infrastructure de Base avec Terraform

2.1. Introduction

Maintenant que notre projet GCP est initialisé et que notre dépôt Git est prêt, nous allons utiliser Terraform pour créer nos premières ressources cloud. Nous allons nous concentrer sur les composants fondamentaux et partagés : le réseau qui isolera nos services, et les espaces de stockage qui contiendront nos artefacts.

Nous allons suivre une structure de dossiers claire pour notre code Terraform au sein de notre monorepo :

skillforge-ai-monorepo/ └── terraform/ ├── environments/ │ ├── _bootstrap/ # Pour créer le backend Terraform │ └── staging/ # Pour l'infrastructure de notre environnement de staging └── modules/ # (vide pour le moment)











2.2. Initialisation du Backend Terraform (Le Paradoxe de la Poule et de l'Œuf)

Nous voulons stocker notre fichier d'état Terraform sur un bucket GCS, mais ce bucket doit d'abord être créé. Nous résolvons ce paradoxe avec une procédure d'amorçage ("bootstrap") en deux temps.

  1. Créer le bucket GCS avec un état local :
# terraform/environments/_bootstrap/bootstrap.tf



# Configure le fournisseur Google Cloud.

provider "google" {

  project = "<ID_DE_VOTRE_PROJET_GCP>"

  region  = "europe-west1"

}



# Crée un bucket GCS unique pour stocker l'état de Terraform.

# Le nom doit être globalement unique.

resource "google_storage_bucket" "tfstate" {

  name          = "<ID_DE_VOTRE_PROJET_GCP>-tfstate"

  location      = "EUROPE-WEST1"

  force_destroy = false # Sécurité pour ne pas le supprimer accidentellement.



  # Active le versioning pour garder un historique des états.

  versioning {

    enabled = true

  }

}





Exécutez les commandes suivantes depuis le dossier terraform/environments/_bootstrap/ :



# Initialise Terraform avec un backend local

terraform init



# Applique la configuration pour créer le bucket

terraform apply



2.3. Code Terraform pour l'Environnement de Staging

Nous allons maintenant travailler dans le dossier terraform/environments/staging/. Tous les fichiers suivants sont à créer dans ce répertoire.

  1. Configurer le Backend distant (backend.tf) :


# terraform/environments/staging/backend.tf



terraform {

  backend "gcs" {

    bucket  = "<ID_DE_VOTRE_PROJET_GCP>-tfstate"

    prefix  = "staging" # Un sous-dossier pour l'état de l'environnement staging

  }

}



2.  Configurer le Fournisseur (provider.tf) :

  - Créez un fichier provider.tf pour définir les paramètres de connexion à GCP.
# terraform/environments/staging/provider.tf



provider "google" {

  project = "<ID_DE_VOTRE_PROJET_GCP>"

  region  = "europe-west1"

}



3. Créer le Réseau VPC (network.tf) :

  - Créez un fichier network.tf pour définir notre réseau privé.
# terraform/environments/staging/network.tf



# Crée le réseau VPC principal

resource "google_compute_network" "vpc_main" {

  name                    = "skillforge-vpc-staging"

  auto_create_subnetworks = false # Nous gérons les sous-réseaux manuellement

}



# Crée un sous-réseau dans la région europe-west1

resource "google_compute_subnetwork" "subnet_main" {

  name          = "skillforge-subnet-staging"

  ip_cidr_range = "10.0.0.0/24"

  region        = "europe-west1"

  network       = google_compute_network.vpc_main.id

}



# Règle de pare-feu pour autoriser tout le trafic interne au VPC

resource "google_compute_firewall" "allow_internal" {

  name    = "allow-internal-traffic"

  network = google_compute_network.vpc_main.name



  allow {

    protocol = "tcp"

    ports    = ["0-65535"]

  }

  allow {

    protocol = "udp"

    ports    = ["0-65535"]

  }

  allow {

    protocol = "icmp"

  }

  source_ranges = ["10.0.0.0/24"] # Autorise le trafic depuis notre propre sous-réseau

}





4.  Créer les Registres et Buckets de Stockage (storage.tf) :

  - Créez un fichier storage.tf.
# terraform/environments/staging/storage.tf



# Crée le dépôt Artifact Registry pour nos images Docker

resource "google_artifact_registry_repository" "docker_repo" {

  location      = "europe-west1"

  repository_id = "skillforge-docker-repo-staging"

  format        = "DOCKER"

  description   = "Docker repository for SkillForge staging environment"

}



# Crée le bucket pour les uploads des utilisateurs

resource "google_storage_bucket" "user_uploads" {

  name          = "<ID_DE_VOTRE_PROJET_GCP>-user-uploads-staging"

  location      = "EUROPE-WEST1"

  uniform_bucket_level_access = true

}



# Crée le bucket pour les fichiers statiques du Front-End

resource "google_storage_bucket" "frontend_assets" {

  name          = "<ID_DE_VOTRE_PROJET_GCP>-frontend-assets-staging"

  location      = "EUROPE-WEST1"

  uniform_bucket_level_access = true



  # Configure le bucket pour l'hébergement de site web statique

  website {

    main_page_suffix = "index.html"

    not_found_page   = "index.html" # Pour les SPAs qui gèrent le routage

  }

}





2.4. Appliquer la Configuration de Base

Maintenant que nos fichiers de configuration pour l'environnement staging sont prêts :

  1. Initialiser Terraform :


cd terraform/environments/staging

terraform init



2.  Planifier et Appliquer :

  - Générez un plan d'exécution pour voir ce que Terraform va créer.
terraform plan



Si le plan vous semble correct, appliquez-le pour créer les ressources.

terraform apply

Confirmez par yes.



### Partie 3 : Déploiement du "Socle de Services" avec Terraform

3.1. Introduction

Cette section décrit comment créer nos services de données managés à l'aide de Terraform. Nous allons ajouter de nouveaux fichiers de configuration dans notre répertoire terraform/environments/staging/.

La gestion des mots de passe est un point de sécurité critique. Nous utiliserons Google Secret Manager pour stocker le mot de passe de la base de données de manière sécurisée, et Terraform y fera référence sans jamais l'exposer en clair dans notre code.

3.2. Code Terraform pour Cloud SQL (PostgreSQL)

  1. Étape Préalable : Créer le Secret Manuellement
  1. Créer le fichier database.tf :


	# terraform/environments/staging/database.tf



# Référence au secret que nous avons créé manuellement.

data "google_secret_manager_secret_version" "postgres_password" {

  secret = "postgres-password-staging"

}



# Crée l'instance principale de PostgreSQL

resource "google_sql_database_instance" "main_postgres" {

  name             = "skillforge-pg-instance-staging"

  database_version = "POSTGRES_16"

  region           = "europe-west1"



  settings {

    tier = "db-n1-standard-1" # Taille de machine adaptée pour du staging



    ip_configuration {

      ipv4_enabled    = false # Désactive l'IP publique pour des raisons de sécurité

      private_network = google_compute_network.vpc_main.id

    }



    backup_configuration {

      enabled = true

    }

  }

}



# Crée la base de données "skillforge_db" à l'intérieur de l'instance

resource "google_sql_database" "main_db" {

  name     = "skillforge_db"

  instance = google_sql_database_instance.main_postgres.name

}



# Crée l'utilisateur applicatif pour la base de données

resource "google_sql_user" "app_user" {

  name     = "skillforge_user"

  instance = google_sql_database_instance.main_postgres.name

  # Le mot de passe est récupéré de manière sécurisée depuis Secret Manager.

  password = data.google_secret_manager_secret_version.postgres_password.secret_data

}





3.3. Code Terraform pour Memorystore (Redis)

Redis sera utilisé comme broker de messages pour nos agents IA. Nous le déployons également sur notre réseau privé.

  1. Activer l'API "Service Networking"
gcloud services enable servicenetworking.googleapis.com



     2. Créer le fichier cache.tf :



	Créez un nouveau fichier terraform/environments/staging/cache.tf.

Ajoutez le contenu suivant :



# terraform/environments/staging/cache.tf



# Réserve une plage d'adresses IP pour les services managés Google

resource "google_compute_global_address" "private_service_access" {

  name          = "private-service-access-staging"

  purpose       = "VPC_PEERING"

  address_type  = "INTERNAL"

  ip_version    = "IPV4"

  prefix_length = 16

  network       = google_compute_network.vpc_main.id

}



# Crée la connexion de peering entre notre VPC et les services Google

resource "google_service_networking_connection" "main_peering" {

  network                 = google_compute_network.vpc_main.id

  service                 = "servicenetworking.googleapis.com"

  reserved_peering_ranges = [google_compute_global_address.private_service_access.name]

}



# Crée l'instance Redis

resource "google_redis_instance" "main_redis" {

  name               = "skillforge-redis-instance-staging"

  tier               = "BASIC" # Tier de base pour le staging

  memory_size_gb     = 1

  location_id        = "europe-west1-b"

  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  authorized_network = google_compute_network.vpc_main.id



  # S'assure que la connexion de peering est établie avant de créer l'instance Redis

  depends_on = [google_service_networking_connection.main_peering]

}





3.4. Appliquer la Configuration du Socle de Services

Maintenant que nos nouveaux fichiers de configuration sont prêts :

  1. Initialiser Terraform (si nécessaire) :
  1. Planifier et Appliquer :
		terraform plan

Si le plan vous semble correct, appliquez-le pour créer les ressources.

terraform apply

  - Confirmez par yes.
Attention : Le provisionnement d'une instance Cloud SQL peut prendre plusieurs minutes (5 à 10 minutes). Soyez patient.

Notre infrastructure de base est maintenant provisionnée et attend de recevoir nos applications. Dans cette partie, nous allons construire les "usines logicielles" - nos pipelines CI/CD - qui prendront le code source écrit par les développeurs et le transformeront en applications déployées.

Pour éviter de répéter la même logique de déploiement pour chaque microservice, nous allons adopter une approche modulaire et réutilisable.





### Partie 4 : Création des Pipelines CI/CD Réutilisables

4.1. Introduction et Principe des "Reusable Workflows"

Plutôt que de créer un long fichier de pipeline pour chacun de nos 10+ services (ce qui serait un cauchemar à maintenir), nous allons créer des briques de base sous forme de "Reusable Workflows" (flux de travail réutilisables) dans GitHub Actions.

  - Le Principe : Nous définissons une seule fois une tâche complexe (comme "construire une image Docker") dans un workflow générique. Ensuite, les pipelines de chaque service peuvent simplement "appeler" ce workflow en lui passant quelques paramètres (comme le chemin vers son Dockerfile).
  - Les Avantages :
Ces workflows réutilisables doivent être créés dans le répertoire .github/workflows/ de notre monorepo.

4.2. Workflow Réutilisable : build-push-docker.yml

Ce workflow est notre "usine à conteneurs". Sa mission : prendre un Dockerfile, construire une image, la scanner pour les vulnérabilités, et la pousser sur notre registre privé.

  1. Créez le fichier .github/workflows/build-push-docker.yml :
  1. Ajoutez le contenu suivant :
# .github/workflows/build-push-docker.yml



name: "Reusable - Build, Scan, and Push Docker Image"



on:

  # Définit ce workflow comme étant appelable par d'autres workflows.

  workflow_call:

    # Définit les paramètres (entrées) que le workflow appelant doit fournir.

    inputs:

      image_name:

        description: 'The name of the docker image without the tag'

        required: true

        type: string

      dockerfile_path:

        description: 'The path to the Dockerfile'

        required: true

        type: string

      gcp_workload_identity_provider:

        description: 'The WIF provider from GCP'

        required: true

        type: string

      gcp_service_account:

        description: 'The GCP service account to impersonate'

        required: true

        type: string

    # Définit les données que ce workflow peut retourner à l'appelant.

    outputs:

      image_uri:

        description: "The full URI of the pushed image"

        value: ${{ jobs.build-scan-push.outputs.image_uri }}



jobs:

  build-scan-push:

    name: Build, Scan & Push

    runs-on: ubuntu-latest

    outputs:

      image_uri: ${{ steps.push.outputs.image_uri }}



    steps:

      - name: Checkout repository

        uses: actions/checkout@v4



      - name: Authenticate to Google Cloud

        id: auth

        uses: google-github-actions/auth@v2

        with:

          workload_identity_provider: ${{ inputs.gcp_workload_identity_provider }}

          service_account: ${{ inputs.gcp_service_account }}



      - name: Configure Docker to use gcloud

        run: gcloud auth configure-docker europe-west1-docker.pkg.dev --quiet



      - name: Build Docker Image

        id: build

        run: |

          IMAGE_URI="europe-west1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/${{ inputs.image_name }}:${{ github.sha }}"

          docker build -t ${IMAGE_URI} -f ${{ inputs.dockerfile_path }} .

          echo "image_uri=${IMAGE_URI}" >> $GITHUB_OUTPUT



      - name: Scan Docker Image for Vulnerabilities

        uses: aquasecurity/trivy-action@0.20.0

        with:

          image-ref: ${{ steps.build.outputs.image_uri }}

          format: 'table'

          # Fait échouer le pipeline si des vulnérabilités de sévérité HAUTE ou CRITIQUE sont trouvées.

          exit-code: '1'

          ignore-unfixed: true

          vuln-type: 'os,library'

          severity: 'HIGH,CRITICAL'



      - name: Push Docker Image to Artifact Registry

        id: push

        run: |

          docker push ${{ steps.build.outputs.image_uri }}

          echo "image_uri=${{ steps.build.outputs.image_uri }}" >> $GITHUB_OUTPUT





4.3. Workflow Réutilisable : deploy-to-cloud-run.yml

Ce workflow est notre "déployeur". Sa mission : prendre une image Docker existante et la déployer comme nouvelle révision d'un service Cloud Run.

  1. Créez le fichier .github/workflows/deploy-to-cloud-run.yml :
  1. Ajoutez le contenu suivant :
# .github/workflows/deploy-to-cloud-run.yml



name: "Reusable - Deploy to Cloud Run"



on:

  workflow_call:

    inputs:

      image_uri:

        description: 'The full URI of the docker image to deploy'

        required: true

        type: string

      service_name:

        description: 'The name of the Cloud Run service to deploy to'

        required: true

        type: string

      gcp_region:

        description: 'The GCP region where the service is located'

        required: true

        type: string

      gcp_workload_identity_provider:

        description: 'The WIF provider from GCP'

        required: true

        type: string

      gcp_service_account:

        description: 'The GCP service account to impersonate'

        required: true

        type: string



jobs:

  deploy:

    name: Deploy to Cloud Run

    runs-on: ubuntu-latest



    steps:

      - name: Authenticate to Google Cloud

        id: auth

        uses: google-github-actions/auth@v2

        with:

          workload_identity_provider: ${{ inputs.gcp_workload_identity_provider }}

          service_account: ${{ inputs.gcp_service_account }}



      - name: Deploy new revision to Cloud Run

        id: deploy

        uses: google-github-actions/deploy-cloudrun@v2

        with:

          service: ${{ inputs.service_name }}

          image: ${{ inputs.image_uri }}

          region: ${{ inputs.gcp_region }}

          # Déploie 100% du trafic sur la nouvelle révision immédiatement

          no-traffic: false





Avec ces deux briques de construction puissantes, nous avons standardisé nos opérations les plus critiques. Les pipelines pour chaque service seront maintenant incroyablement simples : ils n'auront qu'à appeler ces workflows avec les bons paramètres.

C'est ici que tous les éléments que nous avons mis en place (infrastructure de base, pipelines réutilisables) s'assemblent pour accomplir notre objectif final : déployer une application.

Cette section est un guide complet, de bout en bout, pour prendre un de nos microservices, le user-service, et le déployer sur notre environnement de Staging. Ce processus servira de modèle pour tous les autres services.



### Partie 5 : Déploiement End-to-End d'un Premier Service (Exemple : user-service)

5.1. Introduction

Nous allons maintenant créer et configurer tous les artefacts nécessaires au déploiement d'un service spécifique :

  1. L'infrastructure du service avec Terraform (son service Cloud Run, son compte de service dédié).
  1. Son conteneur de production avec un Dockerfile optimisé.
  1. Son pipeline de déploiement avec un fichier de workflow GitHub Actions qui utilise nos briques réutilisables.
5.2. Code Terraform pour le user-service

Nous allons créer la définition de notre service dans un nouveau sous-dossier pour garder notre code organisé.

  1. Créez le fichier terraform/environments/staging/services/user_service.tf :
  1. Ajoutez le contenu suivant :
	# terraform/environments/staging/services/user_service.tf



# 1. Créer un compte de service dédié pour ce microservice

resource "google_service_account" "user_service_sa" {

  account_id   = "sa-user-service-staging"

  display_name = "Service Account for User Service (Staging)"

}



# 2. Lui donner les permissions nécessaires

# a) Accès à la base de données

resource "google_project_iam_member" "user_service_db_access" {

  project = var.project_id # Assurez-vous d'avoir défini une variable project_id

  role    = "roles/cloudsql.client"

  member  = "serviceAccount:${google_service_account.user_service_sa.email}"

}



# b) Accès aux secrets dont il a besoin

resource "google_secret_manager_secret_iam_member" "user_service_db_password_access" {

  secret_id = "postgres-password-staging"

  role      = "roles/secretmanager.secretAccessor"

  member    = "serviceAccount:${google_service_account.user_service_sa.email}"

}

# Répétez pour d'autres secrets comme la clé JWT...



# 3. Créer le service Cloud Run

resource "google_cloud_run_v2_service" "user_service" {

  name     = "user-service-staging"

  location = "europe-west1"



  template {

    # Exécute le conteneur avec son compte de service dédié

    service_account = google_service_account.user_service_sa.email



    containers {

      # L'image sera mise à jour par le pipeline CI/CD

      image = "europe-west1-docker.pkg.dev/${var.project_id}/skillforge-docker-repo-staging/user-service:latest"

      

      # Monte les secrets en tant que variables d'environnement

      env {

        name  = "JWT_SECRET_KEY"

        value_source {

          secret_key_ref {

            secret  = "jwt-secret-key-staging"

            version = "latest"

          }

        }

      }

    }



    # Connecte le service à notre réseau privé pour qu'il puisse parler à la BDD

    vpc_access {

      connector = google_vpc_access_connector.main_connector.id # Assurez-vous de créer ce connecteur

      egress    = "ALL_TRAFFIC"

    }

  }

}



5.3. Fichier Dockerfile pour le user-service

Ce Dockerfile utilise une construction multi-étapes pour créer une image de production légère et sécurisée.

  1. Créez le fichier apps/backend/user-service/Dockerfile :
  1. Ajoutez le contenu suivant :
		# apps/backend/user-service/Dockerfile



# --- Étape 1: Le "Builder" ---

# Installe les dépendances dans une première étape pour optimiser le cache de layers

FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install pip-tools

COPY requirements.txt .

# Installe uniquement les dépendances de production

RUN pip-sync requirements.txt



# --- Étape 2: Le "Runtime" ---

# L'image finale est basée sur la même image slim

FROM python:3.11-slim

WORKDIR /app



# Crée un utilisateur non-root pour des raisons de sécurité

RUN useradd --no-create-home appuser

USER appuser



# Copie les dépendances installées depuis l'étape "builder"

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY --from=builder /usr/local/bin /usr/local/bin



# Copie le code source de l'application

COPY ./app ./app



# Commande pour lancer le serveur de production Uvicorn sur le port 8080 (standard pour Cloud Run)

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]



5.4. Fichier de Pipeline CI/CD pour le user-service

Ce pipeline est simple car il ne fait qu'appeler nos workflows réutilisables.

  1. Créez le fichier .github/workflows/deploy-user-service.yml :
  1. Ajoutez le contenu suivant :
	# .github/workflows/deploy-user-service.yml



name: "Deploy - User Service"



on:

  push:

    branches:

      - 'develop' # Déclenche sur push vers la branche de staging

    paths:

      - 'apps/backend/user-service/**' # Ne se déclenche que si le code de ce service change



jobs:

  deploy-staging:

    name: Deploy to Staging

    runs-on: ubuntu-latest

    # Permissions nécessaires pour l'authentification OIDC avec GCP

    permissions:

      contents: read

      id-token: write



    steps:

      - name: Checkout repository

        uses: actions/checkout@v4



      - name: Build, Scan & Push Docker Image

        id: build

        # Appelle notre workflow réutilisable

        uses: ./.github/workflows/build-push-docker.yml

        with:

          image_name: 'skillforge-docker-repo-staging/user-service'

          dockerfile_path: 'apps/backend/user-service/Dockerfile'

          # Ces secrets doivent être configurés dans les "Actions secrets" du dépôt GitHub

          gcp_workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}

          gcp_service_account: ${{ secrets.GCP_CICD_SERVICE_ACCOUNT }}



      - name: Deploy to Cloud Run

        # Appelle notre second workflow réutilisable

        uses: ./.github/workflows/deploy-to-cloud-run.yml

        # S'assure que l'étape de build est terminée

        needs: build

        with:

          # Utilise l'URI de l'image retournée par l'étape de build

          image_uri: ${{ needs.build.outputs.image_uri }}

          service_name: 'user-service-staging'

          gcp_region: 'europe-west1'

          gcp_workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}

          gcp_service_account: ${{ secrets.GCP_CICD_SERVICE_ACCOUNT }}



5.5. Exécution et Vérification

  1. Appliquer l'infrastructure : Exécutez terraform apply depuis terraform/environments/staging/ pour créer les ressources Cloud Run et IAM.
  1. Déclencher le pipeline : Commitez et poussez ces trois nouveaux fichiers sur votre branche develop.
  1. Observer : Allez dans l'onglet "Actions" de votre dépôt GitHub. Vous verrez le pipeline "Deploy - User Service" s'exécuter.
  1. Vérifier : Une fois le pipeline terminé avec succès, rendez-vous sur la console Google Cloud, dans la section Cloud Run. Vous devriez voir votre service user-service-staging avec une nouvelle révision active, utilisant la dernière image que vous venez de construire.


Ce processus, une fois en place, peut être dupliqué en quelques minutes pour chaque nouveau microservice, garantissant un déploiement standardisé, sécurisé et entièrement automatisé pour l'ensemble de notre plateforme.





Partie 5 (Version Étendue) : Déploiement End-to-End des Services

A. Code Terraform pour le project-service

Le fichier est très similaire, seules les permissions IAM changent.

  - Fichier : terraform/environments/staging/services/project_service.tf
  - Contenu :
# terraform/environments/staging/services/project_service.tf



resource "google_service_account" "project_service_sa" {

  account_id   = "sa-project-service-staging"

  display_name = "Service Account for Project Service (Staging)"

}



# --- PERMISSIONS SPÉCIFIQUES ---

# Ce service a besoin d'accéder à plus de tables.

resource "google_project_iam_member" "project_service_db_access" {

  project = var.project_id

  role    = "roles/cloudsql.client"

  member  = "serviceAccount:${google_service_account.project_service_sa.email}"

}

# Note: Dans une configuration idéale, les GRANTs au niveau SQL seraient gérés par Terraform

# pour donner des droits SELECT/INSERT/UPDATE uniquement sur les tables :

# projects, milestones, skills, project_skills, project_assignments, deliverables.



# ... autres accès aux secrets ...



resource "google_cloud_run_v2_service" "project_service" {

  name     = "project-service-staging" # <- Nom du service différent

  location = "europe-west1"

  # Le reste de la configuration est identique à celle du user-service

  # (template, service_account, vpc_access, etc.)

  # ...

}





B. Dockerfile pour le project-service

Le Dockerfile est identique à celui du user-service, il est simplement situé dans son propre répertoire : apps/backend/project-service/Dockerfile.

. Pipeline CI/CD pour le project-service

Le fichier de workflow est un quasi-clone, seules les variables changent.

  - Fichier : .github/workflows/deploy-project-service.yml
  - Contenu (différences mises en évidence) :
# .github/workflows/deploy-project-service.yml



name: "Deploy - Project Service" # <- Titre différent



on:

  push:

    branches: ['develop']

    paths:

      - 'apps/backend/project-service/**' # <- Chemin de déclenchement différent



jobs:

  deploy-staging:

    # ... permissions, etc. ...

    steps:

      - name: Build, Scan & Push Docker Image

        id: build

        uses: ./.github/workflows/build-push-docker.yml

        with:

          image_name: 'skillforge-docker-repo-staging/project-service' # <- Nom de l'image différent

          dockerfile_path: 'apps/backend/project-service/Dockerfile'     # <- Chemin du Dockerfile différent

          # ... reste des `with` identique ...

      

      - name: Deploy to Cloud Run

        uses: ./.github/workflows/deploy-to-cloud-run.yml

        needs: build

        with:

          image_uri: ${{ needs.build.outputs.image_uri }}

          service_name: 'project-service-staging' # <- Nom du service différent

          # ... reste des `with` identique …





### 5.3. Déploiement de l'Application Front-End

Le déploiement du Front-End est différent : il s'agit de déployer des fichiers statiques sur GCS, et non un service sur Cloud Run.

A. Code Terraform pour le Front-End

Le code Terraform ne crée pas de service, mais s'assure que le pipeline a les droits pour écrire dans le bucket de stockage. Le bucket lui-même (frontend-assets) a déjà été créé dans la Partie 2.

  - Fichier : terraform/environments/staging/services/frontend.tf
  - Contenu :
# terraform/environments/staging/services/frontend.tf



# Donne au compte de service de la CI/CD les droits d'écrire dans le bucket du front-end

resource "google_storage_bucket_iam_member" "cicd_frontend_assets_writer" {

  bucket = google_storage_bucket.frontend_assets.name

  role   = "roles/storage.objectAdmin"

  member = "serviceAccount:sa-github-actions-cicd@${var.project_id}.iam.gserviceaccount.com"

}



B. Dockerfile pour le Front-End

Ce Dockerfile sert uniquement pour l'environnement de développement local (docker-compose). Le pipeline CI/CD, lui, n'utilise que la partie build.

  - Fichier : apps/frontend/Dockerfile
  - Contenu :
# apps/frontend/Dockerfile



# --- Étape 1: Build ---

# Construit les fichiers statiques de production

FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

# La commande de build de Vite génère les fichiers dans /app/dist

RUN npm run build



# --- Étape 2: Serveur de Production ---

# Utilise un serveur Nginx léger pour servir les fichiers statiques

FROM nginx:1.25-alpine

# Copie les fichiers buildés de l'étape précédente vers le répertoire par défaut de Nginx

COPY --from=builder /app/dist /usr/share/nginx/html

# Copie une configuration Nginx si nécessaire (pour gérer le routage SPA)

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]



C. Pipeline CI/CD pour le Front-End

Ce pipeline n'appelle pas nos workflows réutilisables car les étapes sont différentes.

  - Fichier : .github/workflows/deploy-frontend.yml
  - Contenu :
# .github/workflows/deploy-frontend.yml



name: "Deploy - Frontend Application"



on:

  push:

    branches: ['develop']

    paths:

      - 'apps/frontend/**'



jobs:

  build-and-deploy-staging:

    name: Build and Deploy to Staging GCS

    runs-on: ubuntu-latest

    permissions:

      contents: read

      id-token: write



    steps:

      - name: Checkout repository

        uses: actions/checkout@v4



      - name: Setup Node.js

        uses: actions/setup-node@v4

        with:

          node-version-file: 'apps/frontend/.nvmrc'

          cache: 'npm'

          cache-dependency-path: 'apps/frontend/package-lock.json'

      

      - name: Install Dependencies

        run: npm ci --prefix apps/frontend

      

      - name: Build Static Files

        run: npm run build --prefix apps/frontend



      - name: Authenticate to Google Cloud

        uses: google-github-actions/auth@v2

        with:

          workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}

          service_account: ${{ secrets.GCP_CICD_SERVICE_ACCOUNT }}



      - name: Deploy to GCS

        uses: google-github-actions/upload-cloud-storage@v2

        with:

          path: 'apps/frontend/dist'

          destination: '${{ secrets.GCP_PROJECT_ID }}-frontend-assets-staging'

          parent: false



### 5.4. Déploiement des Agents IA

Les agents IA sont similaires aux services Back-End, mais leur déclenchement est événementiel (Pub/Sub) et non HTTP.

A. Code Terraform pour l'evaluation-agent

La différence majeure est la configuration du trigger Pub/Sub.

  - Fichier : terraform/environments/staging/services/evaluation_agent.tf
  - Contenu :
# terraform/environments/staging/services/evaluation_agent.tf



# ... création du service account 'sa-evaluation-agent-staging' ...



# L'agent n'est pas accessible publiquement

resource "google_cloud_run_v2_service" "evaluation_agent" {

  name     = "evaluation-agent-staging"

  location = "europe-west1"

  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY" # <- Différence Clé

  # ... template, etc. ...

}



# Crée le topic Pub/Sub

resource "google_pubsub_topic" "deliverable_submitted" {

  name = "project.deliverable.submitted"

}



# Crée une souscription Pub/Sub qui PUSH vers l'agent Cloud Run

resource "google_pubsub_subscription" "evaluation_agent_subscription" {

  name  = "evaluation-agent-sub-staging"

  topic = google_pubsub_topic.deliverable_submitted.name



  push_config {

    push_endpoint = google_cloud_run_v2_service.evaluation_agent.uri



    oidc_token {

      # Utilise le compte de service de l'agent pour s'authentifier

      service_account_email = google_service_account.evaluation_agent_sa.email

    }

  }

}



B. Dockerfile et Pipeline CI/CD pour l'evaluation-agent

Le Dockerfile et le pipeline CI/CD de l'agent sont structurellement identiques à ceux d'un microservice Back-End. Il suffit de changer les chemins, les noms d'images et les noms de services dans les fichiers respectifs.

### Points de Complétude et d'Excellence Opérationnelle

1. Terraform : Dépendances Manquantes et Variables

Dans ma hâte de fournir les configurations des services, j'ai omis de déclarer deux ressources dont ils dépendent, et je n'ai pas formalisé la gestion des variables.

  - 1.1. Le Connecteur d'Accès VPC (Critique) : Pour qu'un service Cloud Run puisse communiquer avec une base de données sur un réseau privé, il a besoin d'un "Serverless VPC Access Connector". Le code suivant doit être ajouté, par exemple dans votre fichier network.tf.
# terraform/environments/staging/network.tf (à ajouter)



# Crée le connecteur qui fait le pont entre Cloud Run et notre VPC.

resource "google_vpc_access_connector" "main_connector" {

  name          = "skillforge-vpc-connector-staging"

  region        = "europe-west1"

  ip_cidr_range = "10.8.0.0/28" # Doit être une plage non utilisée dans votre VPC.

}



La ligne connector = google_vpc_access_connector.main_connector.id dans la configuration des services Cloud Run fonctionnera maintenant correctement.

1.2. Formalisation des Variables Terraform : J'ai utilisé var.project_id sans le déclarer. Pour une configuration propre, chaque environnement doit avoir un fichier variables.tf (pour déclarer les variables) et un fichier terraform.tfvars (pour leur assigner une valeur), qui lui n'est pas versionné.

  - Fichier terraform/environments/staging/variables.tf :
variable "project_id" {

  type        = string

  description = "The GCP project ID to deploy to."

}

variable "region" {

  type        = string

  description = "The primary GCP region for resources."

  default     = "europe-west1"

}



Fichier terraform/environments/staging/terraform.tfvars :

project_id = "skillforge-ai-mvp"

2. Dockerfile : La Vérification de Santé (Healthcheck)

Un conteneur peut être en cours d'exécution mais l'application à l'intérieur peut être bloquée ou ne pas répondre. Le HEALTHCHECK permet à Docker et à Cloud Run de savoir si l'application est réellement en bonne santé.

  - Ajout au Dockerfile de chaque service Back-End et Agent : Ajoutez ces lignes vers la fin du Dockerfile, juste avant le CMD.
# ... à la fin des Dockerfiles backend/agents



# Ajoute un endpoint /healthz dans ton application FastAPI qui retourne un statut 200 OK.

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \

  CMD curl -f http://localhost:8080/healthz || exit 1



CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]



  - Cela indique à Cloud Run de vérifier toutes les 30 secondes si l'application répond correctement. Si ce n'est pas le cas, la révision sera considérée comme défaillante et Cloud Run ne lui enverra pas de trafic.
3. CI/CD : L'Étape Manquante la plus Critique

J'ai défini le workflow de déploiement mais j'ai omis d'y inclure explicitement l'étape la plus importante avant le déploiement d'un service Back-End : l'application des migrations de base de données. Sans cette étape, un déploiement qui dépend d'un nouveau champ en base de données échouera systématiquement.

  - Correction du Pipeline deploy-*.yml pour les services Back-End et Agents : Le pipeline doit être modifié pour inclure une étape alembic upgrade head.
# .github/workflows/deploy-user-service.yml (corrigé)



# ...

jobs:

  deploy-staging:

    # ...

    steps:

      # ... (Checkout, Auth, Build, Scan, Push) ...



      - name: Build, Scan & Push Docker Image

        id: build

        # ...



      # --- ETAPE CRITIQUE AJOUTEE ---

      - name: Apply Database Migrations

        run: |

          # Installe les dépendances nécessaires pour Alembic

          pip install alembic psycopg2-binary

          # Exécute la migration sur la BDD de staging

          # La DATABASE_URL est injectée ici en tant que secret

          alembic -x database_url=${{ secrets.STAGING_DATABASE_URL }} upgrade head



      - name: Deploy to Cloud Run

        uses: ./.github/workflows/deploy-to-cloud-run.yml

        needs: build # Dépend toujours du build

        with:

          # …



4. Configuration des Secrets dans GitHub

J'ai utilisé des variables comme ${{ secrets.GCP_WIF_PROVIDER }}. Pour une clarté totale, voici la liste des secrets qui doivent être configurés dans l'interface de votre dépôt GitHub (Settings > Secrets and variables > Actions) pour que les pipelines fonctionnent.

  - GCP_PROJECT_ID : L'ID de votre projet GCP (ex: skillforge-ai-mvp).
  - GCP_WIF_PROVIDER : L'ID complet du fournisseur Workload Identity que nous avons récupéré à la Partie 1 (ex: projects/12345/.../providers/github-provider).
  - GCP_CICD_SERVICE_ACCOUNT : L'email du compte de service pour la CI/CD (ex: sa-github-actions-cicd@...).
  - STAGING_DATABASE_URL : L'URL de connexion complète à votre base de données de staging, incluant le mot de passe. C'est le seul endroit où cette URL complète sera stockée.
### Partie 6 : Configuration de l'Observabilité

6.1. Introduction

L'objectif de cette section est de mettre en place les outils qui nous permettront de surveiller la santé de notre plateforme, de diagnostiquer les problèmes et d'être alertés en cas d'incident. Nous allons, comme pour le reste de notre infrastructure, définir notre configuration d'observabilité en tant que code.

Tous les fichiers suivants sont à créer dans le répertoire terraform/environments/staging/.

6.2. Code Terraform pour le Dashboard de Monitoring

Nous allons créer un tableau de bord centralisé dans Google Cloud Monitoring qui affichera les métriques vitales de nos services.

  1. Créer le fichier monitoring.tf :
  1. Ajoutez le contenu suivant. Il définit la structure du tableau de bord en JSON, puis crée la ressource dans GCP.
# terraform/environments/staging/monitoring.tf



# Utilisation d'une variable locale pour stocker la définition JSON du dashboard,

# ce qui rend le code plus lisible.

locals {

  # Définition du Dashboard au format JSON.

  # Ce JSON peut être généré initialement via l'interface graphique de GCP puis exporté.

  main_dashboard_json = jsonencode({

    "displayName": "Dashboard Principal - Staging - SkillForge AI",

    "gridLayout": {

      "columns": "2",

      "widgets": [

        {

          "title": "Taux d'Erreur 5xx (Tous les Services)",

          "xyChart": {

            "dataSets": [

              {

                "timeSeriesQuery": {

                  "timeSeriesQueryLanguage": "fetch cloud_run_revision | metric 'run.googleapis.com/request_count' | filter metric.response_code_class = '5xx' | align rate(1m) | every 1m | group_by [], [value_request_count_aggregate: sum(value.request_count)]"

                },

                "plotType": "LINE"

              }

            ],

            "timeshiftDuration": "0s"

          }

        },

        {

          "title": "Utilisation CPU - Cloud SQL",

          "xyChart": {

            "dataSets": [

              {

                "timeSeriesQuery": {

                  "timeSeriesQueryLanguage": "fetch cloudsql_database | metric 'cloudsql.googleapis.com/database/cpu/utilization' | group_by 1m, [value_utilization_mean: mean(value.utilization)] | every 1m"

                },

                "plotType": "LINE"

              }

            ],

            "timeshiftDuration": "0s"

          }

        }

      ]

    }

  })

}



# Crée le dashboard dans Google Cloud Monitoring.

resource "google_monitoring_dashboard" "main_dashboard" {

  project        = var.project_id

  dashboard_json = local.main_dashboard_json

}



6.3. Code Terraform pour les Politiques d'Alerte

Nous définissons maintenant les règles qui nous notifieront automatiquement en cas de problème.

  1. Ajoutez le code suivant au fichier monitoring.tf :
# terraform/environments/staging/monitoring.tf (à la suite)



# Crée un canal de notification par e-mail (remplacez par un e-mail de votre groupe de distribution).

resource "google_monitoring_notification_channel" "email_alerts" {

  display_name = "Alertes DevOps par Email"

  type         = "email"

  labels = {

    email_address = "devops-alerts@yourcompany.com"

  }

}



# --- Alerte 1: Taux d'erreur 5xx élevé ---

resource "google_monitoring_alert_policy" "high_5xx_rate" {

  display_name = "[Staging] Taux d'Erreur 5xx élevé sur les services Cloud Run"

  combiner     = "OR" # Déclenche si une des conditions est remplie.

  

  conditions {

    display_name = "Le taux d'erreur 5xx dépasse 2% pendant 5 minutes"

    condition_threshold {

      filter     = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" metric.label.response_code_class=\"5xx\""

      comparison = "COMPARISON_GT"

      threshold_value = 0.02 # 2%

      duration   = "300s"    # 5 minutes

      

      # Calcule le ratio entre les erreurs 5xx et toutes les requêtes.

      trigger {

        percent = 100

      }

      denominator_filter = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\""

    }

  }

  

  # Lie l'alerte au canal de notification par e-mail.

  notification_channels = [google_monitoring_notification_channel.email_alerts.name]

}



# --- Alerte 2: Utilisation CPU élevée sur la base de données ---

resource "google_monitoring_alert_policy" "high_sql_cpu" {

  display_name = "[Staging] Utilisation CPU de l'instance Cloud SQL élevée"

  combiner     = "OR"



  conditions {

    display_name = "Le CPU dépasse 90% pendant plus de 15 minutes"

    condition_threshold {

      filter          = "metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\" resource.type=\"cloudsql_database\""

      comparison      = "COMPARISON_GT"

      threshold_value = 0.9 # 90%

      duration        = "900s" # 15 minutes

      trigger {

        count = 1

      }

    }

  }



  notification_channels = [google_monitoring_notification_channel.email_alerts.name]

}





6.4. Déploiement Final

  1. Naviguez dans le dossier terraform/environments/staging/.
  1. Exécutez terraform plan pour visualiser la création du dashboard et des politiques d'alerte.
  1. Exécutez terraform apply et confirmez par yes.


### Conclusion Finale du Guide d'Implémentation

Ce guide vous a accompagné à travers toutes les étapes de la construction et du déploiement de la plateforme SkillForge AI. En partant de zéro, nous avons :

  1. Initialisé un projet GCP et un dépôt GitHub sécurisés.
  1. Construit une infrastructure réseau, de stockage et de données robuste avec Terraform.
  1. Créé des usines logicielles (pipelines CI/CD) modulaires et réutilisables.
  1. Déployé l'ensemble de nos services et agents de manière entièrement automatisée.
  1. Mis en place les outils d'observabilité pour surveiller la santé de notre plateforme.




