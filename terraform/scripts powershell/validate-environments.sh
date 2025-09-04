#!/bin/bash
# Script bash pour valider les environnements Terraform
# Usage: ./validate-environments.sh

set -e

echo "🔧 Validation des environnements Terraform SkillForge AI"
echo "============================================================"

environments=("staging" "production")
success=true

for env in "${environments[@]}"; do
    echo ""
    echo "📁 Validation de l'environnement: $env"
    echo "------------------------------"
    
    env_path="environments/$env"
    
    if [ ! -d "$env_path" ]; then
        echo "❌ Dossier $env_path n'existe pas"
        success=false
        continue
    fi
    
    cd "$env_path"
    
    # Vérifier les fichiers requis
    required_files=("variables.tf" "terraform.tfvars" "backend.tf" "provider.tf" "main.tf")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file"
        else
            echo "❌ $file manquant"
            success=false
        fi
    done
    
    # Valider la syntaxe Terraform
    echo ""
    echo "🔍 Validation Terraform..."
    
    # Terraform fmt (formatting check)
    if terraform fmt -check -diff > /dev/null 2>&1; then
        echo "✅ Format Terraform OK"
    else
        echo "⚠️  Format Terraform à corriger"
    fi
    
    # Terraform validate (syntax check)
    terraform init -backend=false -input=false > /dev/null 2>&1
    if terraform validate > /dev/null 2>&1; then
        echo "✅ Syntaxe Terraform valide"
    else
        echo "❌ Erreurs de syntaxe détectées:"
        terraform validate
        success=false
    fi
    
    cd ../..
done

echo ""
echo "============================================================"
if [ "$success" = true ]; then
    echo "🎉 Tous les environnements sont valides!"
    echo ""
    echo "📋 Prochaines étapes:"
    echo "1. cd environments/staging"
    echo "2. terraform init"
    echo "3. terraform plan"
    echo "4. terraform apply"
else
    echo "❌ Des erreurs ont été détectées. Corrigez-les avant de continuer."
fi
echo ""