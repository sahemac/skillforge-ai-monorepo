<#
.SYNOPSIS
    Script de correction pour la configuration GitHub Secrets
.DESCRIPTION
    Résout les problèmes d'authentification et re-configure correctement
#>

Write-Host "`n🔧 CORRECTION DE LA CONFIGURATION GCP" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# 1. Ré-authentification complète
Write-Host "`n1️⃣ Ré-authentification GCP..." -ForegroundColor Cyan
Write-Host "Exécutez ces commandes dans PowerShell :" -ForegroundColor Yellow
Write-Host ""
Write-Host "gcloud auth login --force" -ForegroundColor White
Write-Host "gcloud auth application-default login" -ForegroundColor White
Write-Host "gcloud config set project skillforge-ai-mvp-25" -ForegroundColor White
Write-Host ""

# 2. Vérification des permissions
Write-Host "2️⃣ Vérification des permissions..." -ForegroundColor Cyan
Write-Host "Vérifiez que votre compte a les droits Owner ou Editor sur le projet :" -ForegroundColor Yellow
Write-Host "gcloud projects get-iam-policy skillforge-ai-mvp-25 --flatten='bindings[].members' --filter='bindings.members:sah@emacsah.com'" -ForegroundColor White
Write-Host ""

# 3. Nettoyage et nouvelle tentative
Write-Host "3️⃣ Commandes de nettoyage si nécessaire..." -ForegroundColor Cyan
Write-Host "Si des ressources partielles ont été créées :" -ForegroundColor Yellow
Write-Host ""
Write-Host "# Supprimer le service account (si créé partiellement)" -ForegroundColor Gray
Write-Host "gcloud iam service-accounts delete terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com --quiet" -ForegroundColor White
Write-Host ""
Write-Host "# Supprimer le workload identity pool (si créé partiellement)" -ForegroundColor Gray
Write-Host "gcloud iam workload-identity-pools delete github-actions --location=global --quiet" -ForegroundColor White
Write-Host ""

# 4. Nouvelle configuration avec le bon nom de repository
Write-Host "4️⃣ Nouvelle exécution avec le bon paramètre..." -ForegroundColor Cyan
Write-Host "Une fois l'authentification réparée, lancez :" -ForegroundColor Yellow
Write-Host ""

# Détecter le nom du repository automatiquement
try {
    $gitRemote = git remote get-url origin 2>$null
    if ($gitRemote -match "github\.com[:/]([^/]+)/([^/]+)\.git") {
        $repoName = "$($matches[1])/$($matches[2])"
        Write-Host ".\setup-github-secrets.ps1 -RepoName '$repoName'" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Repository détecté automatiquement : $repoName" -ForegroundColor Cyan
    } else {
        Write-Host ".\setup-github-secrets.ps1 -RepoName 'VOTRE-USERNAME/skillforge-ai-monorepo'" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  Remplacez VOTRE-USERNAME par votre nom d'utilisateur GitHub" -ForegroundColor Yellow
    }
} catch {
    Write-Host ".\setup-github-secrets.ps1 -RepoName 'VOTRE-USERNAME/skillforge-ai-monorepo'" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Remplacez VOTRE-USERNAME par votre nom d'utilisateur GitHub" -ForegroundColor Yellow
}

Write-Host "5️⃣ Secrets générés à utiliser..." -ForegroundColor Cyan
Write-Host "Les secrets ont été générés et sauvés dans :" -ForegroundColor Yellow
Write-Host "secrets-backup-20250903-235518.json" -ForegroundColor Green
Write-Host ""
Write-Host "🔑 Valeurs à copier dans GitHub (même si la config GCP a échoué) :" -ForegroundColor Yellow
Write-Host ""
Write-Host "Staging Environment Secrets:" -ForegroundColor Cyan
Write-Host "TF_VAR_jwt_secret: elrJxPx8kEhSrZTkSVL5kB+ldq0Khgyi143DTSAsSAdIs/CaFVg2ocoL9Cnzoq0E" -ForegroundColor White
Write-Host "TF_VAR_postgres_password: /OeuzN5Xj+Q3MsT4AVUj3tTn0x5XSkUvkiSLyxfwcN8=" -ForegroundColor White
Write-Host ""
Write-Host "Production Environment Secrets:" -ForegroundColor Cyan  
Write-Host "TF_VAR_jwt_secret: sX7sNX4k/j65iNG5x/Pn3a0eDbL+88s7Tt9jIt9dqSgttNU1umVm9MM5VrpCSI6v" -ForegroundColor White
Write-Host "TF_VAR_postgres_password: qHnYEtQHfBYV3ATG8czX46+JgFA0iLFi+AMY/3f9h+U=" -ForegroundColor White
Write-Host ""

Write-Host "🚀 PLAN D'ACTION RECOMMANDÉ :" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host "1. Exécutez les commandes d'authentification ci-dessus" -ForegroundColor Yellow
Write-Host "2. Configurez d'abord les secrets dans GitHub (étape 6 ci-dessous)" -ForegroundColor Yellow  
Write-Host "3. Puis relancez la config GCP une fois l'auth réparée" -ForegroundColor Yellow
Write-Host "4. Le pipeline pourra fonctionner même sans Workload Identity au début" -ForegroundColor Yellow
Write-Host ""

Write-Host "6️⃣ Configuration GitHub (à faire maintenant) ..." -ForegroundColor Cyan
Write-Host ""
Write-Host "A. Créer les Environments:" -ForegroundColor Yellow
Write-Host "1. Allez sur https://github.com/VOTRE-USERNAME/skillforge-ai-monorepo" -ForegroundColor Gray
Write-Host "2. Settings > Environments > New environment" -ForegroundColor Gray
Write-Host "3. Créez 'staging' et 'production'" -ForegroundColor Gray
Write-Host ""
Write-Host "B. Ajouter les Environment Secrets:" -ForegroundColor Yellow
Write-Host "Dans chaque environment, ajoutez les TF_VAR_* ci-dessus" -ForegroundColor Gray
Write-Host ""
Write-Host "C. Repository Secrets (pour plus tard, quand GCP sera fixé):" -ForegroundColor Yellow
Write-Host "GCP_WORKLOAD_IDENTITY_PROVIDER: projects/584748485117/locations/global/workloadIdentityPools/github-actions/providers/github" -ForegroundColor Gray
Write-Host "GCP_SERVICE_ACCOUNT: terraform-ci-cd@skillforge-ai-mvp-25.iam.gserviceaccount.com" -ForegroundColor Gray

Write-Host "`n✅ Suivez ce plan et tout devrait fonctionner !" -ForegroundColor Green