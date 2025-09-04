# Script PowerShell pour valider les environnements Terraform
# Usage: .\validate-environments.ps1

Write-Host "🔧 Validation des environnements Terraform SkillForge AI" -ForegroundColor Green
Write-Host "=" * 60

$environments = @("staging", "production")
$success = $true

foreach ($env in $environments) {
    Write-Host ""
    Write-Host "📁 Validation de l'environnement: $env" -ForegroundColor Yellow
    Write-Host "-" * 30
    
    $envPath = "environments\$env"
    
    if (-not (Test-Path $envPath)) {
        Write-Host "❌ Dossier $envPath n'existe pas" -ForegroundColor Red
        $success = $false
        continue
    }
    
    Set-Location $envPath
    
    # Vérifier les fichiers requis
    $requiredFiles = @("variables.tf", "terraform.tfvars", "backend.tf", "provider.tf", "main.tf")
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "✅ $file" -ForegroundColor Green
        } else {
            Write-Host "❌ $file manquant" -ForegroundColor Red
            $success = $false
        }
    }
    
    # Valider la syntaxe Terraform
    Write-Host ""
    Write-Host "🔍 Validation Terraform..." -ForegroundColor Cyan
    
    # Terraform fmt (formatting check)
    $fmtResult = terraform fmt -check -diff
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Format Terraform OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Format Terraform à corriger" -ForegroundColor Yellow
    }
    
    # Terraform validate (syntax check)
    terraform init -backend=false -input=false > $null 2>&1
    $validateResult = terraform validate
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Syntaxe Terraform valide" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreurs de syntaxe détectées:" -ForegroundColor Red
        Write-Host $validateResult -ForegroundColor Red
        $success = $false
    }
    
    Set-Location ..\..
}

Write-Host ""
Write-Host "=" * 60
if ($success) {
    Write-Host "🎉 Tous les environnements sont valides!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
    Write-Host "1. cd environments/staging"
    Write-Host "2. terraform init"
    Write-Host "3. terraform plan"
    Write-Host "4. terraform apply"
} else {
    Write-Host "❌ Des erreurs ont été détectées. Corrigez-les avant de continuer." -ForegroundColor Red
}
Write-Host ""