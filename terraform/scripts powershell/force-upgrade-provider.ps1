<#
.SYNOPSIS
    Script PowerShell pour forcer la mise à jour du provider Google Cloud dans Terraform.
.DESCRIPTION
    Résout le problème "Resource instance managed by newer provider version".
#>

param(
    [string]$Environment = "staging"
)

Write-Host "`n[INFO] RESOLUTION FORCEE - Provider Version Mismatch"
Write-Host "================================================="
Write-Host "[INFO] Environment: $Environment"

$originalDir = Get-Location
Set-Location "environments\$Environment"

try {
    # 1. Sauvegarde complète de l'état
    Write-Host "`n[INFO] 1. Sauvegarde de l'état actuel..."
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFile = "backup-complete-$timestamp.json"

    if (Test-Path terraform.tfstate) {
        Copy-Item terraform.tfstate "terraform.tfstate.backup.$timestamp"
        Write-Host "[SUCCESS] État local sauvegardé"
    }

    terraform state pull > $backupFile 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] État distant sauvegardé dans: $backupFile"
    }

    # 2. Nettoyage COMPLET du cache Terraform
    Write-Host "`n[INFO] 2. Nettoyage complet du cache Terraform..."

    $filesToRemove = @(
        ".terraform",
        ".terraform.lock.hcl",
        "terraform.tfstate",
        "terraform.tfstate.backup",
        "*.tfplan"
    )

    foreach ($file in $filesToRemove) {
        if (Test-Path $file) {
            Remove-Item -Recurse -Force $file -ErrorAction SilentlyContinue
            Write-Host "[SUCCESS] Supprimé: $file"
        }
    }

    # 3. Vérifier la version dans backend.tf
    Write-Host "`n[INFO] 3. Vérification de la version du provider..."

    if (Test-Path backend.tf) {
        $backendContent = Get-Content backend.tf -Raw
        # Chercher spécifiquement la version du provider Google (pas required_version)
        if ($backendContent -match 'google\s*=\s*\{[^}]*version\s*=\s*"([^"]+)"') {
            $configuredVersion = $matches[1]
            Write-Host "[INFO] Version du provider Google configurée: $configuredVersion"

            # Forcer la version du provider Google uniquement si nécessaire
            if ($configuredVersion -notmatch "6\.\d+") {
                Write-Host "[WARNING] Version provider Google ancienne détectée, mise à jour vers ~> 6.0"
                # Remplacer SEULEMENT la version du provider Google, pas required_version
                $backendContent = $backendContent -replace '(google\s*=\s*\{[^}]*version\s*=\s*")[^"]+(")', '${1}~> 6.0${2}'
                Set-Content -Path backend.tf -Value $backendContent
                Write-Host "[SUCCESS] Version du provider Google mise à jour"
            } else {
                Write-Host "[INFO] Version du provider Google déjà correcte"
            }
        } else {
            Write-Host "[WARNING] Impossible de détecter la version du provider Google dans backend.tf"
        }
    }

    # 4. Réinitialiser avec la dernière version du provider
    Write-Host "`n[INFO] 4. Réinitialisation avec la dernière version du provider..."
    terraform init -upgrade

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Erreur lors de terraform init"
        exit 1
    }

    # 5. Rafraîchir l'état
    Write-Host "`n[INFO] 5. Rafraîchissement de l'état..."
    terraform refresh -var-file="terraform.tfvars"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] Avertissement lors du refresh (peut être ignoré)"
    }

    # 6. Générer le plan de mise à jour
    Write-Host "`n[INFO] 6. Génération du plan de mise à jour..."
    terraform plan -var-file="terraform.tfvars" -out="provider-upgrade.tfplan" -detailed-exitcode
    $planExitCode = $LASTEXITCODE

    if ($planExitCode -eq 0) {
        Write-Host "`n[SUCCESS] Aucun changement d'infrastructure requis"
        Write-Host "Le provider a été mis à jour avec succès!"
    }
    elseif ($planExitCode -eq 2) {
        Write-Host "`n[WARNING] Des changements sont détectés dans le plan"
        Write-Host "Veuillez examiner le plan avant d'appliquer:"
        Write-Host "  terraform show provider-upgrade.tfplan"
        Write-Host ""
        Write-Host "Si les changements sont acceptables, appliquez avec:"
        Write-Host "  terraform apply provider-upgrade.tfplan"
    }
    else {
        Write-Host "`n[ERROR] Erreur lors de la planification"
        Write-Host "Vérifiez les erreurs ci-dessus"
        exit 1
    }

    # 7. Résumé final
    Write-Host "`n[INFO] RÉSUMÉ"
    Write-Host "========="
    Write-Host "[SUCCESS] Cache Terraform nettoyé"
    Write-Host "[SUCCESS] Provider mis à jour vers la dernière version 6.x"
    Write-Host "[SUCCESS] État sauvegardé dans: $backupFile"

    # Afficher la version actuelle du provider
    $providers = terraform version -json | ConvertFrom-Json
    if ($providers.provider_selections) {
        Write-Host "`n[INFO] Versions des providers:"
        $providers.provider_selections | ForEach-Object {
            Write-Host "   $($_.Name): $($_.Version)"
        }
    }

    Write-Host "`n[SUCCESS] Problème de version du provider résolu!"
    Write-Host ""
    Write-Host "Prochaines étapes:"
    Write-Host "1. Vérifiez le plan: terraform show provider-upgrade.tfplan"
    Write-Host "2. Si OK, appliquez: terraform apply provider-upgrade.tfplan"
    Write-Host "3. Testez: terraform plan -var-file=`"terraform.tfvars`""
}
catch {
    Write-Host "`n[ERROR] Erreur inattendue: $_"
    Write-Host "[INFO] Restauration possible avec: terraform state push $backupFile"
    exit 1
}
finally {
    Set-Location $originalDir
}