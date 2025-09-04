param()

Write-Host ""
Write-Host "VALIDATION USER-SERVICE SKILLFORGE AI" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$ErrorActionPreference = "Continue"
$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Fonction pour tester Python
function Test-PythonAvailable {
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $version -match "Python \d+\.\d+") {
                return @{
                    Command = $cmd
                    Version = $version
                    Available = $true
                }
            }
        }
        catch {
            continue
        }
    }
    
    return @{
        Available = $false
    }
}

try {
    # Verifier que nous sommes dans le bon repertoire
    if (-not (Test-Path "$serviceDir\main.py")) {
        throw "Fichier main.py non trouve. Assurez-vous d'etre dans le repertoire user-service."
    }
    
    # Verifier Python
    Write-Host ""
    Write-Host "Verification Python..." -ForegroundColor Yellow
    
    $pythonInfo = Test-PythonAvailable
    
    if (-not $pythonInfo.Available) {
        Write-Host "   ERREUR Python non trouve" -ForegroundColor Red
        Write-Host "   SOLUTION Installez Python 3.8+ et ajoutez-le au PATH" -ForegroundColor Yellow
        Write-Host "   INFO Testez : python --version ou python3 --version" -ForegroundColor Cyan
        exit 1
    } else {
        Write-Host "   OK $($pythonInfo.Version) (commande: $($pythonInfo.Command))" -ForegroundColor Green
        $pythonCmd = $pythonInfo.Command
    }
    
    # Tester la disponibilite du script de validation
    if (-not (Test-Path "$serviceDir\validate_service.py")) {
        Write-Host "   ERREUR Script validate_service.py non trouve" -ForegroundColor Red
        exit 1
    }
    
    # Installer les dependances si necessaire
    Write-Host ""
    Write-Host "Installation des dependances..." -ForegroundColor Yellow
    
    # Liste des modules requis
    $requiredModules = @("asyncpg", "httpx", "psutil")
    
    foreach ($module in $requiredModules) {
        try {
            & $pythonCmd -c "import $module" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   OK $module deja installe" -ForegroundColor Green
            } else {
                Write-Host "   Installation $module..." -ForegroundColor Cyan
                & $pythonCmd -m pip install $module
            }
        }
        catch {
            Write-Host "   Installation $module..." -ForegroundColor Cyan
            & $pythonCmd -m pip install $module
        }
    }
    
    # Installer requirements.txt si disponible
    if (Test-Path "$serviceDir\requirements.txt") {
        Write-Host "   Installation requirements.txt..." -ForegroundColor Cyan
        & $pythonCmd -m pip install -r requirements.txt
    }
    
    # Verifier cloud-sql-proxy
    Write-Host ""
    Write-Host "Verification cloud-sql-proxy..." -ForegroundColor Yellow
    
    $proxyRunning = $false
    
    # Methode 1: Chercher le processus
    try {
        $proxyProcess = Get-Process | Where-Object { $_.ProcessName -like "*cloud*sql*proxy*" -or $_.ProcessName -eq "cloud_sql_proxy" }
        if ($proxyProcess) {
            Write-Host "   OK cloud-sql-proxy detecte (PID: $($proxyProcess[0].Id))" -ForegroundColor Green
            $proxyRunning = $true
        }
    }
    catch {
        # Continue
    }
    
    # Methode 2: Tester la connexion au port 5432
    if (-not $proxyRunning) {
        try {
            $tcpClient = New-Object System.Net.Sockets.TcpClient
            $tcpClient.Connect("127.0.0.1", 5432)
            $tcpClient.Close()
            Write-Host "   OK Port 5432 accessible" -ForegroundColor Green
            $proxyRunning = $true
        }
        catch {
            Write-Host "   WARN Port 5432 non accessible" -ForegroundColor Yellow
        }
    }
    
    if (-not $proxyRunning) {
        Write-Host "   WARN cloud-sql-proxy non detecte" -ForegroundColor Yellow
        Write-Host "   INFO Commande pour demarrer cloud-sql-proxy :" -ForegroundColor Cyan
        Write-Host "      cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432" -ForegroundColor Gray
        Write-Host "   INFO Le script continuera mais les tests DB echoueront" -ForegroundColor Yellow
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
    Write-Host "   Commande Python: $pythonCmd" -ForegroundColor Gray
    Write-Host ""
    
    Set-Location $serviceDir
    & $pythonCmd validate_service.py
    
    $exitCode = $LASTEXITCODE
    
    # Resultats
    Write-Host ""
    Write-Host "Validation terminee!" -ForegroundColor Magenta
    
    if ($exitCode -eq 0) {
        Write-Host "SUCCES - Service valide et pret pour la production!" -ForegroundColor Green
        Write-Host "Vous pouvez proceder au commit GitHub" -ForegroundColor Green
    }
    elseif ($exitCode -eq 130) {
        Write-Host "INTERROMPU - Validation arretee par l'utilisateur" -ForegroundColor Yellow
    }
    else {
        Write-Host "ECHEC - Des erreurs ont ete detectees (code: $exitCode)" -ForegroundColor Red
        Write-Host "Consultez les logs ci-dessus pour les details" -ForegroundColor Yellow
    }
    
    # Afficher le rapport si disponible
    if (Test-Path "$serviceDir\test-validation-report.md") {
        Write-Host ""
        Write-Host "Rapport detaille genere :" -ForegroundColor Cyan
        Write-Host "   $serviceDir\test-validation-report.md" -ForegroundColor Gray
        
        # Ouvrir le rapport dans l'editeur par defaut
        $openReport = Read-Host "Voulez-vous ouvrir le rapport maintenant ? (O/N)"
        if ($openReport -eq "O" -or $openReport -eq "o") {
            try {
                Start-Process "$serviceDir\test-validation-report.md"
                Write-Host "Rapport ouvert dans l'editeur par defaut" -ForegroundColor Green
            }
            catch {
                Write-Host "Impossible d'ouvrir le rapport automatiquement" -ForegroundColor Yellow
                Write-Host "Ouvrez manuellement: $serviceDir\test-validation-report.md" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host ""
    Write-Host "Validation user-service terminee!" -ForegroundColor Green
    exit $exitCode
}
catch {
    Write-Host ""
    Write-Host "ERREUR CRITIQUE: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "VERIFICATIONS REQUISES:" -ForegroundColor Yellow
    Write-Host "   1. Python 3.8+ installe et dans le PATH" -ForegroundColor Gray
    Write-Host "      Testez: python --version" -ForegroundColor Gray
    Write-Host "   2. cloud-sql-proxy en cours d'execution" -ForegroundColor Gray  
    Write-Host "      Testez: netstat -an | findstr :5432" -ForegroundColor Gray
    Write-Host "   3. Connexion reseau vers la base de donnees" -ForegroundColor Gray
    Write-Host "   4. Permissions d'execution PowerShell" -ForegroundColor Gray
    Write-Host "      Commande: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Gray
    Write-Host ""
    Write-Host "ALTERNATIVE:" -ForegroundColor Cyan
    Write-Host "   Lancez directement: python validate_service.py" -ForegroundColor Gray
    exit 1
}