param()

Write-Host ""
Write-Host "CORRECTION DEPENDANCES USER-SERVICE" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

$ErrorActionPreference = "Continue"

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
    # Verifier Python
    Write-Host ""
    Write-Host "Verification Python..." -ForegroundColor Yellow
    
    $pythonInfo = Test-PythonAvailable
    
    if (-not $pythonInfo.Available) {
        throw "Python non trouve. Installez Python 3.8+ et ajoutez-le au PATH."
    } else {
        Write-Host "   OK $($pythonInfo.Version) (commande: $($pythonInfo.Command))" -ForegroundColor Green
        $pythonCmd = $pythonInfo.Command
    }
    
    # Mettre a jour pip
    Write-Host ""
    Write-Host "Mise a jour de pip..." -ForegroundColor Yellow
    & $pythonCmd -m pip install --upgrade pip
    
    # Installer wheel et setuptools d'abord
    Write-Host ""
    Write-Host "Installation des outils de base..." -ForegroundColor Yellow
    & $pythonCmd -m pip install wheel setuptools
    
    # Installer les dependances problematiques en premier
    Write-Host ""
    Write-Host "Installation des dependances critiques..." -ForegroundColor Yellow
    
    # cryptography avec version compatible
    Write-Host "   Installation cryptography (version compatible)..." -ForegroundColor Cyan
    & $pythonCmd -m pip install "cryptography>=3.0.0,<42.0.0"
    
    # python-jose sans cryptography d'abord
    Write-Host "   Installation python-jose..." -ForegroundColor Cyan  
    & $pythonCmd -m pip install python-jose
    
    # Dependances essentielles une par une
    $criticalModules = @(
        "sqlmodel==0.0.14",
        "fastapi==0.104.1", 
        "uvicorn[standard]==0.24.0",
        "asyncpg==0.29.0",
        "psycopg2-binary",
        "alembic==1.13.1",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6"
    )
    
    foreach ($module in $criticalModules) {
        Write-Host "   Installation $module..." -ForegroundColor Cyan
        try {
            & $pythonCmd -m pip install $module
            if ($LASTEXITCODE -eq 0) {
                Write-Host "      OK $module installe" -ForegroundColor Green
            } else {
                Write-Host "      WARN Probleme avec $module, continuant..." -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "      ERROR Echec $module : $_" -ForegroundColor Red
        }
    }
    
    # Dependances de test
    Write-Host ""
    Write-Host "Installation des dependances de test..." -ForegroundColor Yellow
    
    $testModules = @(
        "pytest==7.4.3",
        "pytest-cov==4.1.0", 
        "pytest-asyncio==0.21.1",
        "httpx==0.25.2",
        "asyncpg==0.29.0",
        "psutil==5.9.6"
    )
    
    foreach ($module in $testModules) {
        Write-Host "   Installation $module..." -ForegroundColor Cyan
        try {
            & $pythonCmd -m pip install $module
        }
        catch {
            Write-Host "      WARN Echec $module, continuant..." -ForegroundColor Yellow
        }
    }
    
    # Verification des installations
    Write-Host ""
    Write-Host "Verification des installations..." -ForegroundColor Yellow
    
    $requiredModules = @(
        "sqlmodel", "fastapi", "uvicorn", "asyncpg", 
        "alembic", "pytest", "httpx", "psutil"
    )
    
    $failedModules = @()
    foreach ($module in $requiredModules) {
        try {
            & $pythonCmd -c "import $module" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   OK $module disponible" -ForegroundColor Green
            } else {
                Write-Host "   FAIL $module non disponible" -ForegroundColor Red
                $failedModules += $module
            }
        }
        catch {
            Write-Host "   ERROR $module erreur: $_" -ForegroundColor Red
            $failedModules += $module
        }
    }
    
    # Resultats
    Write-Host ""
    Write-Host "RESULTATS INSTALLATION" -ForegroundColor Magenta
    Write-Host "======================" -ForegroundColor Magenta
    
    if ($failedModules.Count -eq 0) {
        Write-Host "SUCCES - Toutes les dependances sont installees!" -ForegroundColor Green
        Write-Host "Vous pouvez maintenant lancer: .\run_validation.ps1" -ForegroundColor Green
    } else {
        Write-Host "ATTENTION - Certains modules ont echoue:" -ForegroundColor Yellow
        foreach ($module in $failedModules) {
            Write-Host "   - $module" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "SOLUTIONS ALTERNATIVES:" -ForegroundColor Cyan
        Write-Host "1. Installation manuelle:" -ForegroundColor Gray
        foreach ($module in $failedModules) {
            Write-Host "   pip install $module" -ForegroundColor Gray
        }
        Write-Host ""
        Write-Host "2. Environnement virtuel:" -ForegroundColor Gray
        Write-Host "   python -m venv venv" -ForegroundColor Gray
        Write-Host "   .\venv\Scripts\activate" -ForegroundColor Gray
        Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Installation des dependances terminee!" -ForegroundColor Green
    
}
catch {
    Write-Host ""
    Write-Host "ERREUR CRITIQUE: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUTIONS:" -ForegroundColor Yellow
    Write-Host "1. Utilisez un environnement virtuel:" -ForegroundColor Gray
    Write-Host "   python -m venv venv" -ForegroundColor Gray
    Write-Host "   .\venv\Scripts\activate" -ForegroundColor Gray
    Write-Host "   pip install --upgrade pip wheel setuptools" -ForegroundColor Gray
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Si probleme Rust/cryptography:" -ForegroundColor Gray
    Write-Host "   pip install --upgrade pip" -ForegroundColor Gray  
    Write-Host "   pip install cryptography --only-binary=cryptography" -ForegroundColor Gray
    exit 1
}