<#
.SYNOPSIS
    Test rapide de syntaxe PowerShell pour run_validation.ps1
#>

Write-Host "🧪 Test de syntaxe PowerShell" -ForegroundColor Green

# Test 1: Vérifier que le script peut être parsé
try {
    $scriptPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "run_validation.ps1"
    $scriptContent = Get-Content $scriptPath -Raw
    $scriptBlock = [scriptblock]::Create($scriptContent)
    Write-Host "✅ Syntaxe PowerShell valide" -ForegroundColor Green
}
catch {
    Write-Host "❌ Erreur de syntaxe PowerShell: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Vérifier les encodages de caractères
$problematicChars = @("'", "'", """, """, "…")
$foundProblems = @()

foreach ($char in $problematicChars) {
    if ($scriptContent -match [regex]::Escape($char)) {
        $foundProblems += $char
    }
}

if ($foundProblems.Count -gt 0) {
    Write-Host "⚠️  Caractères problématiques trouvés: $($foundProblems -join ', ')" -ForegroundColor Yellow
} else {
    Write-Host "✅ Pas de caractères problématiques" -ForegroundColor Green
}

# Test 3: Vérifier les blocs try/catch
$tryCount = ($scriptContent | Select-String "try \{").Count
$catchCount = ($scriptContent | Select-String "catch \{").Count

if ($tryCount -eq $catchCount) {
    Write-Host "✅ Blocs try/catch équilibrés ($tryCount/$catchCount)" -ForegroundColor Green
} else {
    Write-Host "❌ Blocs try/catch déséquilibrés ($tryCount try, $catchCount catch)" -ForegroundColor Red
}

Write-Host "`n🎉 Test de syntaxe terminé" -ForegroundColor Green