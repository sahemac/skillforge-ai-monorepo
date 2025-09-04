<#
.SYNOPSIS
    Script PowerShell pour résoudre les problèmes de version du provider Google.
.DESCRIPTION
    Ce script corrige les problèmes de version du provider Google dans Terraform.
.EXAMPLE
    .\fix-provider-version.ps1 staging
#>
param(
    [string]$Environment = "staging"
)
Write-Host "`n🔧 Correction des problèmes de version du provider Google" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
$originalDir = Get-Location
Set-Location "environments\$Environment"
try {
    Write-Host "`n1. Sauvegarde de l'état actuel..." -ForegroundColor Cyan
    $backupFile = "backup-state-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    terraform state pull > $backupFile 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ État sauvegardé dans: $backupFile" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Impossible de sauvegarder l'état" -ForegroundColor Yellow
    }
    Write-Host "`n2. Suppression du cache Terraform..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force .terraform -ErrorAction SilentlyContinue
    Remove-Item -Force .terraform.lock.hcl -ErrorAction SilentlyContinue
    Write-Host "`n3. Réinitialisation avec la nouvelle version du provider..." -ForegroundColor Cyan
    terraform init -upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Erreur lors de terraform init" -ForegroundColor Red
        exit 1
    }
    Write-Host "`n4. Mise à jour du lock file..." -ForegroundColor Cyan
    terraform providers lock -platform=windows_amd64 -platform=darwin_amd64 -platform=linux_amd64
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ⚠️  Impossible de mettre à jour le lock file" -ForegroundColor Yellow
    }
    Write-Host "`n5. Validation de la configuration..." -ForegroundColor Cyan
    terraform validate
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Configuration valide" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erreur de validation détectée" -ForegroundColor Red
        exit 1
    }
    Write-Host "`n6. Test du plan..." -ForegroundColor Cyan
    terraform plan -var-file="terraform.tfvars" -out="upgrade-plan.tfplan" -detailed-exitcode
    $planExitCode = $LASTEXITCODE
    if ($planExitCode -eq 0) {
        Write-Host "`n✅ Aucun changement requis" -ForegroundColor Green
    } elseif ($planExitCode -eq 2) {
        Write-Host "`n⚠️  Des changements sont planifiés - Review requis avant apply" -ForegroundColor Yellow
        Write-Host "Pour appliquer: terraform apply upgrade-plan.tfplan" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Erreur lors de la planification" -ForegroundColor Red
        exit 1
    }
    Write-Host "`n🎉 Problème de version du provider résolu!" -ForegroundColor Green
    Write-Host "`nProchaines étapes:" -ForegroundColor Cyan
    Write-Host "1. Reviewez le plan: terraform show upgrade-plan.tfplan" -ForegroundColor Cyan
    Write-Host "2. Si OK, appliquez: terraform apply upgrade-plan.tfplan" -ForegroundColor Cyan
    Write-Host "`nEn cas de problème:" -ForegroundColor Yellow
    Write-Host ("- État sauvegardé dans: " + $backupFile) -ForegroundColor Yellow
    $restoreCommand = "terraform state push $backupFile"
    Write-Host ("- Restaurer avec: $restoreCommand") -ForegroundColor Yellow
}
finally {
    Set-Location $originalDir
}