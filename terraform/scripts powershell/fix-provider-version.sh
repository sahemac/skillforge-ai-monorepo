#!/bin/bash
# Script pour résoudre les problèmes de version du provider Google
# Usage: ./fix-provider-version.sh [staging|production]

set -e

ENVIRONMENT=${1:-"staging"}

echo "🔧 Correction des problèmes de version du provider Google"
echo "Environment: $ENVIRONMENT"
echo "=========================================================="

cd "environments/$ENVIRONMENT"

echo "1. Sauvegarde de l'état actuel..."
terraform state pull > "backup-state-$(date +%Y%m%d-%H%M%S).json"

echo "2. Suppression du cache Terraform..."
rm -rf .terraform/
rm -f .terraform.lock.hcl

echo "3. Réinitialisation avec la nouvelle version du provider..."
terraform init

echo "4. Mise à jour du lock file..."
terraform providers lock \
  -platform=windows_amd64 \
  -platform=darwin_amd64 \
  -platform=linux_amd64

echo "5. Validation de la configuration..."
if terraform validate; then
    echo "✅ Configuration valide"
else
    echo "❌ Erreur de validation détectée"
    exit 1
fi

echo "6. Test du plan..."
if terraform plan -var-file="terraform.tfvars" -out="upgrade-plan.tfplan" -detailed-exitcode; then
    plan_exit_code=$?
    if [ $plan_exit_code -eq 0 ]; then
        echo "✅ Aucun changement requis"
    elif [ $plan_exit_code -eq 2 ]; then
        echo "⚠️  Des changements sont planifiés - Review requis avant apply"
        echo "Pour appliquer: terraform apply upgrade-plan.tfplan"
    fi
else
    echo "❌ Erreur lors de la planification"
    exit 1
fi

echo ""
echo "🎉 Problème de version du provider résolu!"
echo ""
echo "Prochaines étapes:"
echo "1. Reviewez le plan: terraform show upgrade-plan.tfplan"
echo "2. Si OK, appliquez: terraform apply upgrade-plan.tfplan"
echo ""
echo "En cas de problème:"
echo "- État sauvegardé dans: backup-state-*.json"
echo "- Restaurer avec: terraform state push backup-state-*.json"