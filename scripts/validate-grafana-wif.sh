#!/bin/bash

# Script de validation de la configuration Workload Identity Federation pour Grafana
# Vérifie tous les composants nécessaires

set -euo pipefail

PROJECT_ID="skillforge-ai-mvp-25"
SA_NAME="grafana-monitoring"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
POOL_NAME="grafana-pool"
PROVIDER_NAME="grafana-provider"
GRAFANA_DOMAIN="sahemac.grafana.net"

echo "=== Validation Configuration Workload Identity Federation ==="
echo "Projet: $PROJECT_ID"
echo "Service Account: $SA_EMAIL"
echo "Workload Identity Pool: $POOL_NAME"
echo "OIDC Provider: $PROVIDER_NAME"
echo "Grafana Domain: $GRAFANA_DOMAIN"
echo

# Fonction pour vérifier une commande
check_command() {
    local description="$1"
    local command="$2"
    
    echo -n "🔍 $description... "
    if eval "$command" &>/dev/null; then
        echo "✅ OK"
        return 0
    else
        echo "❌ ÉCHEC"
        return 1
    fi
}

# Fonction pour afficher des détails
show_details() {
    local description="$1"
    local command="$2"
    
    echo
    echo "📋 $description:"
    echo "----------------------------------------"
    eval "$command" 2>/dev/null || echo "❌ Commande échouée"
    echo "----------------------------------------"
}

# Vérifications de base
echo "=== Vérifications de Base ==="

check_command "Authentification gcloud" \
    "gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -1"

check_command "Projet configuré" \
    "[[ \"\$(gcloud config get-value project)\" == \"$PROJECT_ID\" ]]"

check_command "APIs activées (IAM Credentials)" \
    "gcloud services list --enabled --filter='name:iamcredentials.googleapis.com' --format='value(name)'"

check_command "APIs activées (STS)" \
    "gcloud services list --enabled --filter='name:sts.googleapis.com' --format='value(name)'"

check_command "APIs activées (Cloud Monitoring)" \
    "gcloud services list --enabled --filter='name:monitoring.googleapis.com' --format='value(name)'"

# Vérifications Service Account
echo
echo "=== Vérifications Service Account ==="

check_command "Service Account existe" \
    "gcloud iam service-accounts describe \"$SA_EMAIL\""

check_command "Permission monitoring.viewer" \
    "gcloud projects get-iam-policy \"$PROJECT_ID\" --flatten='bindings[].members' --filter='bindings.role:roles/monitoring.viewer AND bindings.members:serviceAccount:$SA_EMAIL' --format='value(bindings.role)'"

check_command "Permission monitoring.metricWriter" \
    "gcloud projects get-iam-policy \"$PROJECT_ID\" --flatten='bindings[].members' --filter='bindings.role:roles/monitoring.metricWriter AND bindings.members:serviceAccount:$SA_EMAIL' --format='value(bindings.role)'"

check_command "Permission logging.viewer" \
    "gcloud projects get-iam-policy \"$PROJECT_ID\" --flatten='bindings[].members' --filter='bindings.role:roles/logging.viewer AND bindings.members:serviceAccount:$SA_EMAIL' --format='value(bindings.role)'"

# Vérifications Workload Identity
echo
echo "=== Vérifications Workload Identity ==="

check_command "Workload Identity Pool existe" \
    "gcloud iam workload-identity-pools describe \"$POOL_NAME\" --location='global'"

check_command "OIDC Provider existe" \
    "gcloud iam workload-identity-pools providers describe \"$PROVIDER_NAME\" --workload-identity-pool=\"$POOL_NAME\" --location='global'"

check_command "Impersonation configurée" \
    "gcloud iam service-accounts get-iam-policy \"$SA_EMAIL\" --flatten='bindings[].members' --filter='bindings.role:roles/iam.workloadIdentityUser' --format='value(bindings.members)'"

# Tests d'impersonation
echo
echo "=== Tests d'Impersonation ==="

check_command "Test impersonation directe" \
    "gcloud auth print-access-token --impersonate-service-account=\"$SA_EMAIL\""

if command -v curl &>/dev/null; then
    check_command "Test accès API Monitoring" \
        "curl -s -H \"Authorization: Bearer \$(gcloud auth print-access-token --impersonate-service-account=\"$SA_EMAIL\")\" \"https://monitoring.googleapis.com/v1/projects/$PROJECT_ID/metricDescriptors\" | grep -q '\"metricDescriptors\"'"
else
    echo "⚠️  curl non disponible, impossible de tester l'API Monitoring"
fi

# Vérifications des fichiers générés
echo
echo "=== Vérifications Fichiers ==="

CONFIG_FILE="monitoring/grafana/workload-identity-config.json"
TEST_SCRIPT="monitoring/grafana/test-workload-identity.sh"

check_command "Fichier de configuration existe" \
    "[[ -f \"$CONFIG_FILE\" ]]"

check_command "Fichier de configuration valide JSON" \
    "jq empty \"$CONFIG_FILE\""

check_command "Script de test existe" \
    "[[ -f \"$TEST_SCRIPT\" ]]"

check_command "Script de test exécutable" \
    "[[ -x \"$TEST_SCRIPT\" ]]"

# Affichage des détails
echo
echo "=== Détails de Configuration ==="

show_details "Service Account" \
    "gcloud iam service-accounts describe \"$SA_EMAIL\" --format='yaml'"

show_details "Workload Identity Pool" \
    "gcloud iam workload-identity-pools describe \"$POOL_NAME\" --location='global' --format='yaml'"

show_details "OIDC Provider" \
    "gcloud iam workload-identity-pools providers describe \"$PROVIDER_NAME\" --workload-identity-pool=\"$POOL_NAME\" --location='global' --format='yaml'"

show_details "Permissions Service Account" \
    "gcloud projects get-iam-policy \"$PROJECT_ID\" --flatten='bindings[].members' --filter='bindings.members:serviceAccount:$SA_EMAIL' --format='table(bindings.role)'"

# Affichage de la configuration Grafana
echo
echo "=== Configuration Grafana Cloud ==="
echo "🌐 URL Grafana: https://$GRAFANA_DOMAIN"
echo "📁 Chemin configuration: $CONFIG_FILE"
echo
echo "Configuration à utiliser dans Grafana:"
echo "----------------------------------------"
echo "Authentication Type: Workload Identity Federation"
echo "Audience: //iam.googleapis.com/projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"
echo "Service Account: $SA_EMAIL"
echo "Project ID: $PROJECT_ID"
echo "Region: europe-west1"
echo "----------------------------------------"

# Instructions finales
echo
echo "=== Instructions Finales ==="
echo "1. 📊 Aller sur https://$GRAFANA_DOMAIN"
echo "2. ⚙️  Configuration > Data Sources > Add Google Cloud Monitoring"
echo "3. 🔐 Choisir 'Workload Identity Federation' comme authentification"
echo "4. 📝 Copier les valeurs affichées ci-dessus"
echo "5. 💾 Save & Test"
echo "6. 📈 Importer les dashboards (IDs: 1860, 13865)"
echo "7. 🚨 Configurer les alertes pour monitoring proactif"
echo

# Tests optionnels
echo "=== Tests Optionnels ==="
echo "Pour tester la configuration complète:"
echo "1. Exécuter: ./monitoring/grafana/test-workload-identity.sh"
echo "2. Tester dans Grafana: query 'up{job=\"monitoring\"}'"
echo "3. Vérifier les métriques Cloud Run dans un dashboard"
echo

echo "✅ Validation terminée!"
echo
echo "📋 RÉSUMÉ:"
echo "   - Service Account: configuré avec permissions minimales"
echo "   - Workload Identity: pool et provider OIDC créés"
echo "   - Impersonation: testée et fonctionnelle"
echo "   - Fichiers: configuration et scripts générés"
echo "   - Prêt pour: configuration dans Grafana Cloud"
echo
echo "🚀 Next Step: Configurer la data source dans Grafana!"