<#
.SYNOPSIS
    Script PowerShell pour automatiser la configuration des secrets GitHub pour SkillForge AI
.DESCRIPTION
    Ce script automatise la création des secrets et la configuration GCP pour le pipeline Terraform
.EXAMPLE
    .\setup-github-secrets.ps1 -RepoName "VOTRE-USERNAME/skillforge-ai-monorepo"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoName,
    
    [string]$ProjectId = "skillforge-ai-mvp-25",
    [string]$ProjectNumber = "584748485117",
    [string]$ServiceAccountName = "terraform-ci-cd"
)

Write-Host "`n🚀 CONFIGURATION DES SECRETS GITHUB - SKILLFORGE AI" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "Project ID: $ProjectId" -ForegroundColor Yellow
Write-Host "Repository: $RepoName" -ForegroundColor Yellow
Write-Host "Service Account: $ServiceAccountName" -ForegroundColor Yellow

# Vérifier que gcloud est installé
try {
    gcloud --version | Out-Null
    Write-Host "`n✅ Google Cloud CLI détecté" -ForegroundColor Green
}
catch {
    Write-Host "`n❌ Google Cloud CLI non trouvé. Installez-le depuis https://cloud.google.com/sdk" -ForegroundColor Red
    exit 1
}

# Vérifier l'authentification
Write-Host "`n1️⃣ Vérification de l'authentification Google Cloud..." -ForegroundColor Cyan
$currentAccount = gcloud config get-value account
if (-not $currentAccount) {
    Write-Host "❌ Non authentifié. Exécutez 'gcloud auth login' d'abord" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Authentifié en tant que: $currentAccount" -ForegroundColor Green

# Créer le service account
Write-Host "`n2️⃣ Création du service account..." -ForegroundColor Cyan
$serviceAccountEmail = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"

try {
    gcloud iam service-accounts create $ServiceAccountName `
        --project=$ProjectId `
        --description="Service account for Terraform CI/CD pipeline" `
        --display-name="Terraform CI/CD" `
        --quiet
    Write-Host "   ✅ Service account créé: $serviceAccountEmail" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Service account existe déjà ou erreur de création" -ForegroundColor Yellow
}

# Assigner les rôles
Write-Host "`n3️⃣ Attribution des rôles IAM..." -ForegroundColor Cyan
$roles = @(
    "roles/editor",
    "roles/storage.admin", 
    "roles/iam.serviceAccountAdmin",
    "roles/compute.admin",
    "roles/cloudsql.admin",
    "roles/run.admin"
)

foreach ($role in $roles) {
    try {
        gcloud projects add-iam-policy-binding $ProjectId `
            --member="serviceAccount:$serviceAccountEmail" `
            --role="$role" `
            --quiet
        Write-Host "   ✅ Rôle assigné: $role" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  Erreur lors de l'assignation du rôle: $role" -ForegroundColor Yellow
    }
}

# Créer Workload Identity Pool
Write-Host "`n4️⃣ Création du Workload Identity Pool..." -ForegroundColor Cyan
try {
    gcloud iam workload-identity-pools create "github-actions" `
        --project=$ProjectId `
        --location="global" `
        --display-name="GitHub Actions Pool" `
        --quiet
    Write-Host "   ✅ Workload Identity Pool créé" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Pool existe déjà ou erreur de création" -ForegroundColor Yellow
}

# Créer le Provider OIDC
Write-Host "`n5️⃣ Création du Provider OIDC..." -ForegroundColor Cyan
try {
    # Configuration correcte de l'attribute mapping sans condition
    gcloud iam workload-identity-pools providers create-oidc "github" `
        --project=$ProjectId `
        --location="global" `
        --workload-identity-pool="github-actions" `
        --display-name="GitHub Actions Provider" `
        --description="OIDC provider for GitHub Actions workflows" `
        --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor,attribute.ref=assertion.ref" `
        --issuer-uri="https://token.actions.githubusercontent.com" `
        --quiet
    Write-Host "   ✅ Provider OIDC créé" -ForegroundColor Green
}
catch {
    Write-Host "   ⚠️  Provider existe déjà ou erreur de création" -ForegroundColor Yellow
    Write-Host "   Si erreur INVALID_ARGUMENT, utilisez: .\fix-oidc-provider.ps1 -RepoName '$RepoName'" -ForegroundColor Cyan
}

# Autoriser le repository GitHub
Write-Host "`n6️⃣ Autorisation du repository GitHub..." -ForegroundColor Cyan
$principalSet = "principalSet://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions/attribute.repository/$RepoName"

try {
    gcloud iam service-accounts add-iam-policy-binding `
        --project=$ProjectId `
        --role="roles/iam.workloadIdentityUser" `
        --member="$principalSet" `
        $serviceAccountEmail `
        --quiet
    Write-Host "   ✅ Repository autorisé: $RepoName" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Erreur lors de l'autorisation du repository" -ForegroundColor Red
}

# Générer les secrets
Write-Host "`n7️⃣ Génération des secrets..." -ForegroundColor Cyan

function Generate-SecurePassword {
    param([int]$Length = 32)
    $bytes = New-Object byte[] $Length
    $random = [System.Security.Cryptography.RNGCryptoServiceProvider]::Create()
    $random.GetBytes($bytes)
    return [Convert]::ToBase64String($bytes)
}

$jwtSecretStaging = Generate-SecurePassword -Length 48
$jwtSecretProduction = Generate-SecurePassword -Length 48
$postgresPasswordStaging = Generate-SecurePassword -Length 32
$postgresPasswordProduction = Generate-SecurePassword -Length 32

# Sauvegarder les secrets dans un fichier sécurisé
$secretsFile = "secrets-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$secrets = @{
    "generated_date" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "project_id" = $ProjectId
    "repository" = $RepoName
    "staging" = @{
        "jwt_secret" = $jwtSecretStaging
        "postgres_password" = $postgresPasswordStaging
    }
    "production" = @{
        "jwt_secret" = $jwtSecretProduction
        "postgres_password" = $postgresPasswordProduction
    }
}

$secrets | ConvertTo-Json -Depth 3 | Out-File -FilePath $secretsFile -Encoding UTF8
Write-Host "   ✅ Secrets sauvegardés dans: $secretsFile" -ForegroundColor Green

# Afficher les résultats
Write-Host "`n🎉 CONFIGURATION TERMINÉE!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

Write-Host "`n📋 SECRETS À CONFIGURER DANS GITHUB:" -ForegroundColor Yellow
Write-Host "Repository Secrets (Settings → Secrets and variables → Actions):" -ForegroundColor Cyan

$workloadIdentityProvider = "projects/$ProjectNumber/locations/global/workloadIdentityPools/github-actions/providers/github"

Write-Host ""
Write-Host "GCP_WORKLOAD_IDENTITY_PROVIDER:" -ForegroundColor White
Write-Host $workloadIdentityProvider -ForegroundColor Green

Write-Host ""
Write-Host "GCP_SERVICE_ACCOUNT:" -ForegroundColor White  
Write-Host $serviceAccountEmail -ForegroundColor Green

Write-Host "`n🔐 ENVIRONMENT SECRETS:" -ForegroundColor Yellow

Write-Host "`nStaging Environment Secrets:" -ForegroundColor Cyan
Write-Host "TF_VAR_jwt_secret: $jwtSecretStaging" -ForegroundColor White
Write-Host "TF_VAR_postgres_password: $postgresPasswordStaging" -ForegroundColor White

Write-Host "`nProduction Environment Secrets:" -ForegroundColor Cyan  
Write-Host "TF_VAR_jwt_secret: $jwtSecretProduction" -ForegroundColor White
Write-Host "TF_VAR_postgres_password: $postgresPasswordProduction" -ForegroundColor White

Write-Host "`n📋 ÉTAPES SUIVANTES:" -ForegroundColor Yellow
Write-Host "1. Copiez les valeurs ci-dessus dans GitHub Secrets" -ForegroundColor Cyan
Write-Host "2. Créez les environments 'staging' et 'production'" -ForegroundColor Cyan
Write-Host "3. Configurez les protection rules pour production" -ForegroundColor Cyan
Write-Host "4. Testez le workflow avec un changement dans /terraform/" -ForegroundColor Cyan

Write-Host "`n🔒 SÉCURITÉ:" -ForegroundColor Red
Write-Host "- Sauvegardez le fichier $secretsFile dans un lieu sûr" -ForegroundColor Yellow
Write-Host "- Ne committez jamais ce fichier dans Git" -ForegroundColor Yellow
Write-Host "- Supprimez ce fichier après configuration" -ForegroundColor Yellow

Write-Host "`n✅ Script terminé avec succès!" -ForegroundColor Green

# Test de connectivité (optionnel)
Write-Host "`n🧪 TEST DE VALIDATION:" -ForegroundColor Magenta
Write-Host "Voulez-vous tester la configuration? (O/N): " -ForegroundColor Yellow -NoNewline
$test = Read-Host

if ($test -eq "O" -or $test -eq "o") {
    Write-Host "`nTest de la configuration..." -ForegroundColor Cyan
    
    # Test 1: Vérifier le service account
    Write-Host "Test 1: Service Account..." -ForegroundColor Cyan
    try {
        $saInfo = gcloud iam service-accounts describe $serviceAccountEmail --format=json | ConvertFrom-Json
        Write-Host "   ✅ Service Account OK: $($saInfo.email)" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Erreur Service Account" -ForegroundColor Red
    }
    
    # Test 2: Vérifier Workload Identity
    Write-Host "Test 2: Workload Identity Pool..." -ForegroundColor Cyan
    try {
        gcloud iam workload-identity-pools describe github-actions --project=$ProjectId --location=global --quiet
        Write-Host "   ✅ Workload Identity Pool OK" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Erreur Workload Identity Pool" -ForegroundColor Red
    }
    
    Write-Host "`n✅ Tests terminés!" -ForegroundColor Green
}

Write-Host "`n🚀 Configuration prête pour GitHub Actions!" -ForegroundColor Green