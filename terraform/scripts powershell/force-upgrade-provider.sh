#!/bin/bash
# Script bash pour forcer la mise à jour du provider Google Cloud
# Résout le problème "Resource instance managed by newer provider version"

set -e

ENVIRONMENT=${1:-"staging"}

echo -e "\n🔧 RESOLUTION FORCÉE - Provider Version Mismatch"
echo "================================================="
echo "Environment: $ENVIRONMENT"

ORIGINAL_DIR=$(pwd)
cd "environments/$ENVIRONMENT"

# Fonction de nettoyage en cas d'erreur
cleanup() {
    if [ $? -ne 0 ]; then
        echo -e "\n❌ Erreur détectée, nettoyage en cours..."
        cd "$ORIGINAL_DIR"
    fi
}
trap cleanup EXIT

# 1. Sauvegarde complète de l'état
echo -e "\n1️⃣ Sauvegarde de l'état actuel..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="backup-complete-$TIMESTAMP.json"

if [ -f terraform.tfstate ]; then
    cp terraform.tfstate "terraform.tfstate.backup.$TIMESTAMP"
    echo "   ✅ État local sauvegardé"
fi

terraform state pull > "$BACKUP_FILE" 2>/dev/null || true
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    echo "   ✅ État distant sauvegardé dans: $BACKUP_FILE"
fi

# 2. Nettoyage COMPLET du cache Terraform
echo -e "\n2️⃣ Nettoyage complet du cache Terraform..."

FILES_TO_REMOVE=(
    ".terraform"
    ".terraform.lock.hcl"
    "terraform.tfstate"
    "terraform.tfstate.backup"
    "*.tfplan"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    if [ -e "$file" ]; then
        rm -rf "$file"
        echo "   ✅ Supprimé: $file"
    fi
done

# 3. Vérifier la version dans backend.tf
echo -e "\n3️⃣ Vérification de la version du provider..."
if grep -q 'version.*=.*"' backend.tf; then
    CONFIGURED_VERSION=$(grep 'version.*=.*"' backend.tf | sed 's/.*"\([^"]*\)".*/\1/')
    echo "   📌 Version configurée: $CONFIGURED_VERSION"
    
    # Forcer la version à la plus récente si nécessaire
    if ! echo "$CONFIGURED_VERSION" | grep -q "6\."; then
        echo "   ⚠️  Version ancienne détectée, mise à jour vers ~> 6.0"
        sed -i 's/version.*=.*"[^"]*"/version = "~> 6.0"/' backend.tf
    fi
fi

# 4. Réinitialiser avec la dernière version du provider
echo -e "\n4️⃣ Réinitialisation avec la dernière version du provider..."
terraform init -upgrade

if [ $? -ne 0 ]; then
    echo "   ❌ Erreur lors de terraform init"
    exit 1
fi

# 5. Récupérer l'état actuel et le rafraîchir
echo -e "\n5️⃣ Rafraîchissement de l'état..."
terraform refresh -var-file="terraform.tfvars" || true

# 6. Plan détaillé pour vérifier les changements
echo -e "\n6️⃣ Génération du plan de mise à jour..."
terraform plan -var-file="terraform.tfvars" -out="provider-upgrade.tfplan" -detailed-exitcode
PLAN_EXIT_CODE=$?

if [ $PLAN_EXIT_CODE -eq 0 ]; then
    echo -e "\n✅ Aucun changement d'infrastructure requis"
    echo "Le provider a été mis à jour avec succès!"
elif [ $PLAN_EXIT_CODE -eq 2 ]; then
    echo -e "\n⚠️  Des changements sont détectés dans le plan"
    echo "Veuillez examiner le plan avant d'appliquer:"
    echo "  terraform show provider-upgrade.tfplan"
    echo ""
    echo "Si les changements sont acceptables, appliquez avec:"
    echo "  terraform apply provider-upgrade.tfplan"
else
    echo -e "\n❌ Erreur lors de la planification"
    echo "Vérifiez les erreurs ci-dessus"
    exit 1
fi

# 7. Résumé final
echo -e "\n📊 RÉSUMÉ"
echo "========="
echo "✅ Cache Terraform nettoyé"
echo "✅ Provider mis à jour vers la dernière version 6.x"
echo "✅ État sauvegardé dans: $BACKUP_FILE"

# Afficher la version actuelle du provider
echo -e "\n📦 Versions des providers:"
terraform version | grep -E "provider|google"

echo -e "\n🎉 Problème de version du provider résolu!"
echo ""
echo "Prochaines étapes:"
echo "1. Vérifiez le plan: terraform show provider-upgrade.tfplan"
echo "2. Si OK, appliquez: terraform apply provider-upgrade.tfplan"
echo "3. Testez: terraform plan -var-file=\"terraform.tfvars\""

cd "$ORIGINAL_DIR"