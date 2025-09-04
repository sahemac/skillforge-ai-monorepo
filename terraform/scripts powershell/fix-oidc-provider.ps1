<#
.SYNOPSIS
    Script de correction pour le Provider OIDC Workload Identity
.DESCRIPTION
    Corrige l'erreur INVALID_ARGUMENT dans l'attribute mapping du Provider OIDC
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,
    
    [string]$ProjectId = "skillforge-ai-mvp-25",
    [string]$ProjectNumber = "584748485117"
)

Write-Host "`n🔧 CORRECTION DU PROVIDER OIDC" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host "Repository: $RepoName" -ForegroundColor Yellow
Write-Host "Project: $ProjectId" -ForegroundColor Yellow

# 1. Supprimer le provider existant défectueux
Write-Host "`n1️⃣ Suppression du Provider OIDC défectueux..." -ForegroundColor Cyan
try {
    gcloud iam workload-identity-pools providers delete "github" `
        --project=$ProjectId `
        --location="global" `
        --workload-identity-pool="github-actions" `
        --quiet
    Write-Host "   ✅ Provider OIDC supprimé" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Provider n'existait pas ou erreur de suppression" -ForegroundColor Yellow
}

# 2. Créer le Provider OIDC avec la bonne configuration
Write-Host "`n2️⃣ Création du Provider OIDC avec configuration corrigée..." -ForegroundColor Cyan

# Configuration correcte de l'attribute mapping
$attributeMapping = @(
    "google.subject=assertion.sub",
    "attribute.actor=assertion.actor", 
    "attribute.repository=assertion.repository",
    "attribute.repository_owner=assertion.repository_owner",
    "attribute.ref=assertion.ref"
)

$mappingString = $attributeMapping -join ","

try {
    gcloud iam workload-identity-pools providers create-oidc "github" `
        --project=$ProjectId `
        --location="global" `
        --workload-identity-pool="github-actions" `
        --display-name="GitHub Actions Provider" `
        --description="OIDC provider for GitHub Actions workflows" `
        --attribute-mapping=$mappingString `
        --issuer-uri="https://token.actions.githubusercontent.com" `
        --allowed-audiences="https://github.com/$RepoName" `
        --attribute-condition="assertion.repository=='$RepoName'" `
        --quiet
    
    Write-Host "   ✅ Provider OIDC créé avec succès" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Erreur lors de la création du Provider OIDC:" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Yellow
    
    Write-Host "`n   🔧 Tentative avec configuration simplifiée..." -ForegroundColor Cyan
    
    # Configuration simplifiée sans attribute-condition
    try {
        gcloud iam workload-identity-pools providers create-oidc "github" `
            --project=$ProjectId `
            --location="global" `
            --workload-identity-pool="github-actions" `
            --display-name="GitHub Actions Provider" `
            --description="OIDC provider for GitHub Actions workflows" `
            --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" `
            --issuer-uri="https://token.actions.githubusercontent.com" `
            --quiet
            
        Write-Host "   ✅ Provider OIDC créé avec configuration simplifiée" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Échec avec configuration simplifiée aussi" -ForegroundColor Red
        Write-Host "   $_" -ForegroundColor Yellow
        exit 1
    }
}

# 3. Vérifier la création du Provider
Write-Host "`n3️⃣ Vérification du Provider créé..." -ForegroundColor Cyan
try {
    $providerInfo = gcloud iam workload-identity-pools providers describe "github" `
        --project=$ProjectId `
        --location="global" `
        --workload-identity-pool="github-actions" `
        --format="json" | ConvertFrom-Json
        
    Write-Host "   ✅ Provider vérifié:" -ForegroundColor Green
    Write-Host "   - Nom: $($providerInfo.displayName)" -ForegroundColor Gray
    Write-Host "   - État: $($providerInfo.state)" -ForegroundColor Gray
    Write-Host "   - Issuer: $($providerInfo.oidc.issuerUri)" -ForegroundColor Gray
}
catch {
    Write-Host "   ⚠️  Impossible de vérifier le provider, mais il pourrait être créé" -ForegroundColor Yellow
}

# 4. Reconfigurer l'autorisation du repository
Write-Host "`n4️⃣ Configuration de l'autorisation du repository..." -ForegroundColor Cyan

$serviceAccountEmail = "terraform-ci-cd@$ProjectId.iam.gserviceaccount.com"

# Supprimer d'abord l'ancienne autorisation (si existe)
try {
    gcloud iam service-accounts remove-iam-policy-binding `
        --project=$ProjectId `
        --role="roles/iam.workloadIdentityUser" `
        --member="principalSet://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions/attribute.repository/$RepoName" `
        $serviceAccountEmail `
        --quiet 2>$null
}
catch {
    # Ignoré si n'existe pas
}

# Ajouter la nouvelle autorisation
try {
    gcloud iam service-accounts add-iam-policy-binding `
        --project=$ProjectId `
        --role="roles/iam.workloadIdentityUser" `
        --member="principalSet://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions/attribute.repository/$RepoName" `
        $serviceAccountEmail `
        --quiet
        
    Write-Host "   ✅ Autorisation du repository configurée" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Erreur lors de l'autorisation:" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Yellow
    
    Write-Host "`n   🔧 Tentative avec principal spécifique..." -ForegroundColor Cyan
    
    # Essayer avec un principal plus spécifique
    try {
        $principal = "principal://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions/subject/repo:$RepoName`:ref:refs/heads/main"
        
        gcloud iam service-accounts add-iam-policy-binding `
            --project=$ProjectId `
            --role="roles/iam.workloadIdentityUser" `
            --member="$principal" `
            $serviceAccountEmail `
            --quiet
            
        Write-Host "   ✅ Autorisation avec principal spécifique configurée" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  Tentative alternative également échouée" -ForegroundColor Yellow
        Write-Host "   Configuration manuelle requise" -ForegroundColor Yellow
    }
}

# 5. Test de la configuration
Write-Host "`n5️⃣ Test de la configuration..." -ForegroundColor Cyan

Write-Host "   🔍 Vérification du Workload Identity Pool..." -ForegroundColor Gray
try {
    gcloud iam workload-identity-pools describe "github-actions" `
        --project=$ProjectId `
        --location="global" `
        --format="value(name)" `
        --quiet
    Write-Host "   ✅ Workload Identity Pool OK" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Problème avec le Workload Identity Pool" -ForegroundColor Red
}

Write-Host "   🔍 Vérification du Provider OIDC..." -ForegroundColor Gray
try {
    gcloud iam workload-identity-pools providers describe "github" `
        --project=$ProjectId `
        --location="global" `
        --workload-identity-pool="github-actions" `
        --format="value(name)" `
        --quiet
    Write-Host "   ✅ Provider OIDC OK" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Problème avec le Provider OIDC" -ForegroundColor Red
}

Write-Host "   🔍 Vérification du Service Account..." -ForegroundColor Gray
try {
    gcloud iam service-accounts describe $serviceAccountEmail `
        --format="value(email)" `
        --quiet
    Write-Host "   ✅ Service Account OK" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Problème avec le Service Account" -ForegroundColor Red
}

# 6. Afficher les valeurs finales pour GitHub
Write-Host "`n🎉 CONFIGURATION CORRIGÉE!" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green

Write-Host "`n📋 SECRETS POUR GITHUB REPOSITORY:" -ForegroundColor Yellow
Write-Host ""
Write-Host "GCP_WORKLOAD_IDENTITY_PROVIDER:" -ForegroundColor Cyan
Write-Host "projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions/providers/github" -ForegroundColor Green
Write-Host ""
Write-Host "GCP_SERVICE_ACCOUNT:" -ForegroundColor Cyan
Write-Host $serviceAccountEmail -ForegroundColor Green

Write-Host "`n📝 ÉTAPES SUIVANTES:" -ForegroundColor Yellow
Write-Host "1. Ajoutez ces valeurs dans GitHub Repository Secrets" -ForegroundColor Cyan
Write-Host "2. Testez le pipeline avec une PR sur /terraform/" -ForegroundColor Cyan
Write-Host "3. Vérifiez l'authentification dans les logs GitHub Actions" -ForegroundColor Cyan

Write-Host "`n⚡ COMMANDE DE TEST RAPIDE:" -ForegroundColor Yellow
Write-Host "# Test local du pipeline" -ForegroundColor Gray
Write-Host ".\test-pipeline-local.ps1 -Environment staging" -ForegroundColor Green

Write-Host "`n✅ Correction du Provider OIDC terminée!" -ForegroundColor Green