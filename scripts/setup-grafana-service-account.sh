#!/bin/bash

# Script pour créer un service account Grafana avec permissions minimales
# ⚠️  DÉPRÉCIÉ: Utiliser setup-grafana-workload-identity.sh à la place
# Raison: Organisation policy constraints/iam.disableServiceAccountKeyCreation bloque la création de clés JSON

set -euo pipefail

PROJECT_ID="skillforge-ai-mvp-25"
SA_NAME="grafana-monitoring"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="monitoring/grafana/grafana-sa-key.json"

echo "⚠️  AVERTISSEMENT: Ce script est DÉPRÉCIÉ"
echo "   Raison: constraints/iam.disableServiceAccountKeyCreation bloque les clés JSON"
echo "   Solution: Utiliser Workload Identity Federation à la place"
echo "   Script recommandé: ./scripts/setup-grafana-workload-identity.sh"
echo
echo "Voulez-vous continuer avec ce script (déprécié) ? [y/N]"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "❌ Arrêt du script. Utilisez: ./scripts/setup-grafana-workload-identity.sh"
    exit 1
fi

echo "=== Configuration du Service Account Grafana (DÉPRÉCIÉ) ==="
echo "Projet: $PROJECT_ID"
echo "Service Account: $SA_EMAIL"
echo "Fichier de clés: $KEY_FILE"
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

# Créer le service account s'il n'existe pas
if ! gcloud iam service-accounts describe "$SA_EMAIL" &>/dev/null; then
    echo "📝 Création du service account..."
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="Grafana Monitoring Service Account" \
        --description="Service account for Grafana to access Cloud Monitoring APIs"
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

# Créer une nouvelle clé de service account
echo "🔑 Génération d'une nouvelle clé de service account..."

# Sauvegarder l'ancienne clé si elle existe
if [[ -f "$KEY_FILE" ]]; then
    backup_file="${KEY_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$KEY_FILE" "$backup_file"
    echo "  Sauvegarde de l'ancienne clé: $backup_file"
fi

# Créer le dossier si nécessaire
mkdir -p "$(dirname "$KEY_FILE")"

# Générer la nouvelle clé (PROBABLEMENT ÉCHOUERA)
echo "⚠️  TENTATIVE de création de clé JSON (probablement bloquée)..."
if gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SA_EMAIL" \
    --key-file-type=json 2>/dev/null; then
    
    echo "✅ Nouvelle clé générée: $KEY_FILE"

    # Vérifier que le fichier a été créé et est valide
    if [[ -f "$KEY_FILE" ]] && jq empty "$KEY_FILE" 2>/dev/null; then
        echo "✅ Fichier de clés valide généré"
        
        # Afficher les informations de la clé
        echo
        echo "=== Informations du Service Account ==="
        echo "Email: $(jq -r '.client_email' "$KEY_FILE")"
        echo "Project ID: $(jq -r '.project_id' "$KEY_FILE")"
        echo "Private Key ID: $(jq -r '.private_key_id' "$KEY_FILE")"
        echo
        
        # Instructions pour Grafana
        echo "=== Instructions pour Grafana ==="
        echo "1. Dans Grafana, allez dans Configuration > Data Sources"
        echo "2. Ajoutez/Modifiez la source 'Google Cloud Monitoring'"
        echo "3. Authentification: 'Google JWT File'"
        echo "4. Uploadez le fichier: $KEY_FILE"
        echo "5. Projet par défaut: $PROJECT_ID"
        echo "6. Testez la connexion"
        echo
        
        echo "✅ Configuration terminée avec succès!"
        echo
        echo "⚠️  IMPORTANT: Le fichier $KEY_FILE contient des credentials sensibles"
        echo "   Il est automatiquement ignoré par Git grâce au .gitignore"
        echo "   Ne partagez jamais ce fichier publiquement"
    else
        echo "❌ Erreur: Impossible de créer ou valider le fichier de clés"
        exit 1
    fi
else
    echo "❌ ERREUR ATTENDUE: Création de clé bloquée par organisation policy"
    echo "   constraints/iam.disableServiceAccountKeyCreation est active"
    echo
    echo "🔄 SOLUTION RECOMMANDÉE:"
    echo "   Utilisez Workload Identity Federation à la place:"
    echo "   ./scripts/setup-grafana-workload-identity.sh"
    echo
    echo "📖 Documentation complète:"
    echo "   Documentations/Rapports_Infrastructure/GRAFANA_WORKLOAD_IDENTITY_SETUP.md"
    echo
    exit 1
fi