param()

Write-Host ""
Write-Host "VALIDATION USER-SERVICE SKILLFORGE AI" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"
$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    # Verifier que nous sommes dans le bon repertoire
    if (-not (Test-Path "$serviceDir\main.py")) {
        throw "Fichier main.py non trouve. Assurez-vous d'etre dans le repertoire user-service."
    }
    
    # Verifier Python
    Write-Host ""
    Write-Host "Verification Python..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "   OK $pythonVersion" -ForegroundColor Green
    }
    catch {
        throw "Python non trouve. Installez Python 3.8+ et ajoutez-le au PATH."
    }
    
    # Installer les dependances si necessaire
    Write-Host ""
    Write-Host "Installation des dependances..." -ForegroundColor Yellow
    
    # Verifier si asyncpg est installe
    try {
        python -c "import asyncpg" 2>$null
        Write-Host "   OK asyncpg deja installe" -ForegroundColor Green
    }
    catch {
        Write-Host "   Installation asyncpg..." -ForegroundColor Cyan
        pip install asyncpg
    }
    
    # Verifier httpx
    try {
        python -c "import httpx" 2>$null
        Write-Host "   OK httpx deja installe" -ForegroundColor Green
    }
    catch {
        Write-Host "   Installation httpx..." -ForegroundColor Cyan
        pip install httpx
    }
    
    # Verifier psutil
    try {
        python -c "import psutil" 2>$null
        Write-Host "   OK psutil deja installe" -ForegroundColor Green
    }
    catch {
        Write-Host "   Installation psutil..." -ForegroundColor Cyan
        pip install psutil
    }
    
    # Installer requirements.txt si disponible
    if (Test-Path "$serviceDir\requirements.txt") {
        Write-Host "   Installation requirements.txt..." -ForegroundColor Cyan
        pip install -r requirements.txt
    }
    
    # Verifier cloud-sql-proxy
    Write-Host ""
    Write-Host "Verification cloud-sql-proxy..." -ForegroundColor Yellow
    
    $proxyRunning = $false
    try {
        $proxyProcess = Get-Process -Name "*cloud*sql*proxy*" -ErrorAction SilentlyContinue
        if ($proxyProcess) {
            Write-Host "   OK cloud-sql-proxy detecte (PID: $($proxyProcess.Id))" -ForegroundColor Green
            $proxyRunning = $true
        }
    }
    catch {
        # Ignore
    }
    
    # Tester la connexion au port 5432
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("127.0.0.1", 5432)
        $tcpClient.Close()
        Write-Host "   OK Port 5432 accessible" -ForegroundColor Green
        $proxyRunning = $true
    }
    catch {
        if (-not $proxyRunning) {
            Write-Host "   WARN cloud-sql-proxy non detecte sur 127.0.0.1:5432" -ForegroundColor Yellow
            Write-Host "   INFO Assurez-vous que cloud-sql-proxy est en cours d'execution :" -ForegroundColor Cyan
            Write-Host "      cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432" -ForegroundColor Gray
        }
    }
    
    # Variables d'environnement
    Write-Host ""
    Write-Host "Configuration variables d'environnement..." -ForegroundColor Yellow
    
    $env:DATABASE_URL = "postgresql+asyncpg://skillforge_user:Psaumes@27@127.0.0.1:5432/skillforge_db"
    $env:PYTHONPATH = $serviceDir
    
    Write-Host "   OK DATABASE_URL configure" -ForegroundColor Green
    Write-Host "   OK PYTHONPATH configure" -ForegroundColor Green
    
    # Lancer la validation
    Write-Host ""
    Write-Host "Lancement de la validation..." -ForegroundColor Yellow
    Write-Host "   Repertoire: $serviceDir" -ForegroundColor Gray
    Write-Host "   Script: validate_service.py" -ForegroundColor Gray
    Write-Host ""
    
    Set-Location $serviceDir
    python validate_service.py
    
    $exitCode = $LASTEXITCODE
    
    # Resultats
    Write-Host ""
    Write-Host "Validation terminee!" -ForegroundColor Magenta
    
    if ($exitCode -eq 0) {
        Write-Host "SUCCES - Service valide et pret pour la production!" -ForegroundColor Green
        Write-Host "Vous pouvez proceder au commit GitHub" -ForegroundColor Green
    }
    else {
        Write-Host "ECHEC - Des erreurs ont ete detectees" -ForegroundColor Red
        Write-Host "Corrigez les erreurs avant de committer" -ForegroundColor Yellow
    }
    
    # Afficher le rapport si disponible
    if (Test-Path "$serviceDir\test-validation-report.md") {
        Write-Host ""
        Write-Host "Rapport detaille genere :" -ForegroundColor Cyan
        Write-Host "   $serviceDir\test-validation-report.md" -ForegroundColor Gray
        
        # Ouvrir le rapport dans l'editeur par defaut
        $openReport = Read-Host "Voulez-vous ouvrir le rapport maintenant ? (O/N)"
        if ($openReport -eq "O" -or $openReport -eq "o") {
            Start-Process "$serviceDir\test-validation-report.md"
        }
    }
    
    Write-Host ""
    Write-Host "Validation user-service terminee!" -ForegroundColor Green
    exit $exitCode
}
catch {
    Write-Host ""
    Write-Host "ERREUR: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifiez :" -ForegroundColor Yellow
    Write-Host "   - Python 3.8+ installe et dans le PATH" -ForegroundColor Gray
    Write-Host "   - cloud-sql-proxy en cours d'execution" -ForegroundColor Gray
    Write-Host "   - Connexion reseau vers la base de donnees" -ForegroundColor Gray
    Write-Host "   - Variables d'environnement correctes" -ForegroundColor Gray
    exit 1
}