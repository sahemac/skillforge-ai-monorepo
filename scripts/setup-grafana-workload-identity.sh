#!/bin/bash

# Script pour configurer Grafana avec Workload Identity Federation
# Contourne la contrainte constraints/iam.disableServiceAccountKeyCreation

set -euo pipefail

PROJECT_ID="skillforge-ai-mvp-25"
SA_NAME="grafana-monitoring"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
POOL_NAME="grafana-pool"
PROVIDER_NAME="grafana-provider"
GRAFANA_DOMAIN="sahemac.grafana.net"

echo "=== Configuration Grafana avec Workload Identity Federation ==="
echo "Projet: $PROJECT_ID"
echo "Service Account: $SA_EMAIL"
echo "Workload Identity Pool: $POOL_NAME"
echo "OIDC Provider: $PROVIDER_NAME"
echo "Grafana Domain: $GRAFANA_DOMAIN"
echo

# Vérifier que gcloud est configuré
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo "❌ Erreur: Veuillez vous authentifier avec gcloud auth login"
    exit 1
fi

echo "✅ Authentification gcloud vérifiée"

# Vérifier le projet
CURRENT_PROJECT=$(gcloud config get-value project)
if [[ "$CURRENT_PROJECT" != "$PROJECT_ID" ]]; then
    echo "⚠️  Changement de projet: $CURRENT_PROJECT -> $PROJECT_ID"
    gcloud config set project "$PROJECT_ID"
fi

echo "✅ Projet configuré: $PROJECT_ID"

# Activer les APIs nécessaires
echo "🔧 Activation des APIs nécessaires..."
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable monitoring.googleapis.com

echo "✅ APIs activées"

# Créer le service account s'il n'existe pas
if ! gcloud iam service-accounts describe "$SA_EMAIL" &>/dev/null; then
    echo "📝 Création du service account..."
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="Grafana Monitoring Service Account" \
        --description="Service account for Grafana to access Cloud Monitoring APIs via Workload Identity"
else
    echo "✅ Service account existant trouvé"
fi

# Assigner les permissions minimales nécessaires
echo "🔐 Configuration des permissions..."

ROLES=(
    "roles/monitoring.viewer"
    "roles/monitoring.metricWriter"
    "roles/logging.viewer"
)

for role in "${ROLES[@]}"; do
    echo "  Assignation: $role"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
done

# Créer le Workload Identity Pool
echo "🌐 Configuration du Workload Identity Pool..."

if ! gcloud iam workload-identity-pools describe "$POOL_NAME" --location="global" &>/dev/null; then
    echo "  Création du Workload Identity Pool..."
    gcloud iam workload-identity-pools create "$POOL_NAME" \
        --location="global" \
        --description="Pool for Grafana Cloud access" \
        --display-name="Grafana Pool"
else
    echo "✅ Workload Identity Pool existant trouvé"
fi

# Créer le provider OIDC
echo "🔑 Configuration du provider OIDC..."

PROVIDER_FULL_NAME="projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"

if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --workload-identity-pool="$POOL_NAME" \
    --location="global" &>/dev/null; then
    
    echo "  Création du provider OIDC..."
    gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
        --workload-identity-pool="$POOL_NAME" \
        --location="global" \
        --issuer-uri="https://$GRAFANA_DOMAIN" \
        --allowed-audiences="$PROJECT_ID" \
        --attribute-mapping="google.subject=assertion.sub,attribute.grafana_org=assertion.org_id" \
        --attribute-condition="assertion.aud=='$PROJECT_ID'"
else
    echo "✅ Provider OIDC existant trouvé"
fi

# Permettre au pool d'impersonner le service account
echo "👤 Configuration de l'impersonation..."

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_NAME/*"

echo "✅ Impersonation configurée"

# Générer la configuration pour Grafana
echo "📄 Génération de la configuration Grafana..."

CONFIG_FILE="monitoring/grafana/workload-identity-config.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

cat > "$CONFIG_FILE" << EOF
{
  "type": "external_account",
  "audience": "//iam.googleapis.com/projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME",
  "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
  "token_url": "https://sts.googleapis.com/v1/token",
  "credential_source": {
    "url": "https://$GRAFANA_DOMAIN/api/auth/workload-identity/token",
    "headers": {
      "Authorization": "Bearer \${GRAFANA_TOKEN}"
    }
  },
  "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/$SA_EMAIL:generateAccessToken"
}
EOF

echo "✅ Configuration générée: $CONFIG_FILE"

# Créer un script de test
TEST_SCRIPT="monitoring/grafana/test-workload-identity.sh"
cat > "$TEST_SCRIPT" << EOF
#!/bin/bash

# Script de test pour vérifier la configuration Workload Identity

echo "=== Test Workload Identity Federation pour Grafana ==="

# Test 1: Vérifier le pool
echo "1. Vérification du Workload Identity Pool..."
gcloud iam workload-identity-pools describe "$POOL_NAME" --location="global"

# Test 2: Vérifier le provider
echo "2. Vérification du provider OIDC..."
gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \\
    --workload-identity-pool="$POOL_NAME" \\
    --location="global"

# Test 3: Vérifier les permissions du service account
echo "3. Vérification des permissions..."
gcloud projects get-iam-policy "$PROJECT_ID" \\
    --flatten="bindings[].members" \\
    --format="table(bindings.role)" \\
    --filter="bindings.members:serviceAccount:$SA_EMAIL"

# Test 4: Tester l'impersonation (nécessite un token externe)
echo "4. Pour tester l'impersonation, utilisez:"
echo "gcloud auth print-access-token --impersonate-service-account=$SA_EMAIL"

echo "✅ Tests terminés"
EOF

chmod +x "$TEST_SCRIPT"

echo "✅ Script de test créé: $TEST_SCRIPT"

# Afficher les informations finales
echo
echo "=== Configuration Workload Identity Complète ==="
echo "🔗 Workload Identity Pool:"
echo "   Name: $POOL_NAME"
echo "   Full Name: projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_NAME"
echo
echo "🔑 OIDC Provider:"
echo "   Name: $PROVIDER_NAME"
echo "   Issuer: https://$GRAFANA_DOMAIN"
echo "   Audience: $PROJECT_ID"
echo
echo "👤 Service Account:"
echo "   Email: $SA_EMAIL"
echo "   Roles: ${ROLES[*]}"
echo
echo "📁 Fichiers générés:"
echo "   Configuration: $CONFIG_FILE"
echo "   Test script: $TEST_SCRIPT"
echo

echo "=== Instructions pour Grafana Cloud ==="
echo "1. Dans Grafana, allez dans Configuration > Data Sources"
echo "2. Ajoutez 'Google Cloud Monitoring'"
echo "3. Authentification: 'Workload Identity Federation'"
echo "4. Audience: //iam.googleapis.com/projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"
echo "5. Service Account: $SA_EMAIL"
echo "6. Project ID: $PROJECT_ID"
echo

echo "=== Alternative avec metadata server ==="
echo "Si Grafana tourne sur GCE:"
echo "1. Attachez le service account $SA_EMAIL à l'instance"
echo "2. Utilisez 'Google Cloud Metadata Server' comme authentification"
echo "3. Laissez les champs vides (auto-détection)"
echo

echo "✅ Configuration Workload Identity terminée avec succès!"
echo
echo "⚠️  IMPORTANT:"
echo "   - Aucune clé JSON n'a été créée (conforme à l'organisation policy)"
echo "   - L'authentification se fait via OIDC/JWT tokens"
echo "   - Plus sécurisé que les clés statiques"
echo "   - Tokens expirés automatiquement"