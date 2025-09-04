<#
.SYNOPSIS
    Script de test local du pipeline Terraform avant push
.DESCRIPTION
    Simule les vérifications du pipeline GitHub Actions localement
.EXAMPLE
    .\test-pipeline-local.ps1 -Environment staging
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("staging", "production", "both")]
    [string]$Environment = "staging",
    
    [switch]$SkipSecurityScans,
    [switch]$DetailedOutput
)

$ErrorActionPreference = "Continue"
$startTime = Get-Date

Write-Host "`nTEST LOCAL DU PIPELINE TERRAFORM" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host "Environment(s): $Environment" -ForegroundColor Yellow
$scanMode = if($SkipSecurityScans) { "SKIP" } else { "ENABLED" }
Write-Host "Security Scans: $scanMode" -ForegroundColor Yellow

function Test-Environment {
    param([string]$env)
    
    Write-Host "`nTESTING ENVIRONMENT: $env" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    
    $envPath = "environments\$env"
    if (-not (Test-Path $envPath)) {
        Write-Host "   Environment path not found: $envPath" -ForegroundColor Red
        return $false
    }
    
    Set-Location $envPath
    $success = $true
    
    # Test 1: Terraform Format
    Write-Host "`n1. Terraform Format Check..." -ForegroundColor Yellow
    try {
        $fmtResult = terraform fmt -check -recursive -diff 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Format check passed" -ForegroundColor Green
        } else {
            Write-Host "   Format issues found:" -ForegroundColor Red
            Write-Host $fmtResult -ForegroundColor Yellow
            $success = $false
        }
    }
    catch {
        Write-Host "   Format check failed: $_" -ForegroundColor Red
        $success = $false
    }
    
    # Test 2: Terraform Init
    Write-Host "`n2. Terraform Init..." -ForegroundColor Yellow
    try {
        terraform init -backend=false -no-color 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Init successful" -ForegroundColor Green
        } else {
            Write-Host "   Init failed" -ForegroundColor Red
            $success = $false
        }
    }
    catch {
        Write-Host "   Init error: $_" -ForegroundColor Red
        $success = $false
    }
    
    # Test 3: Terraform Validate
    Write-Host "`n3. Terraform Validate..." -ForegroundColor Yellow
    try {
        $validateOutput = terraform validate -no-color 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   Validation passed" -ForegroundColor Green
        } else {
            Write-Host "   Validation failed:" -ForegroundColor Red
            Write-Host $validateOutput -ForegroundColor Yellow
            $success = $false
        }
    }
    catch {
        Write-Host "   Validation error: $_" -ForegroundColor Red
        $success = $false
    }
    
    # Test 4: Security Scans (if not skipped)
    if (-not $SkipSecurityScans) {
        Write-Host "`n4. Security Scans..." -ForegroundColor Yellow
        
        # Checkov scan
        Write-Host "   Running Checkov..." -ForegroundColor Cyan
        try {
            $checkovInstalled = Get-Command checkov -ErrorAction SilentlyContinue
            if ($checkovInstalled) {
                $checkovResult = checkov -d . --framework terraform --quiet --compact 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "   Checkov scan passed" -ForegroundColor Green
                } else {
                    Write-Host "   Checkov found security issues" -ForegroundColor Yellow
                    if ($DetailedOutput) {
                        Write-Host $checkovResult -ForegroundColor Gray
                    }
                }
            } else {
                Write-Host "   Checkov not installed, skipping" -ForegroundColor Yellow
                Write-Host "      Install with: pip install checkov" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "   Checkov scan error: $_" -ForegroundColor Yellow
        }
        
        # TFSec scan
        Write-Host "   Running TFSec..." -ForegroundColor Cyan
        try {
            $tfsecInstalled = Get-Command tfsec -ErrorAction SilentlyContinue
            if ($tfsecInstalled) {
                $tfsecResult = tfsec . --soft-fail 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "   TFSec scan passed" -ForegroundColor Green
                } else {
                    Write-Host "   TFSec found security issues" -ForegroundColor Yellow
                    if ($DetailedOutput) {
                        Write-Host $tfsecResult -ForegroundColor Gray
                    }
                }
            } else {
                Write-Host "   TFSec not installed, skipping" -ForegroundColor Yellow
                Write-Host "      Download from: https://github.com/aquasecurity/tfsec/releases" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "   TFSec scan error: $_" -ForegroundColor Yellow
        }
    }
    
    # Test 5: Plan (simulation only)
    Write-Host "`n5. Terraform Plan (dry-run)..." -ForegroundColor Yellow
    try {
        if (Test-Path "terraform.tfvars") {
            # Create a temporary backend for local testing
            $tempBackend = @"
terraform {
  backend "local" {
    path = "terraform-test.tfstate"
  }
}
"@
            $tempBackend | Out-File -FilePath "backend-temp.tf" -Encoding UTF8
            
            # Re-init with local backend
            terraform init -force-copy -no-color 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                # Try plan
                $planOutput = terraform plan -var-file="terraform.tfvars" -no-color -detailed-exitcode 2>&1
                $planExitCode = $LASTEXITCODE
                
                if ($planExitCode -eq 0) {
                    Write-Host "   Plan successful - No changes needed" -ForegroundColor Green
                } elseif ($planExitCode -eq 2) {
                    Write-Host "   Plan successful - Changes detected" -ForegroundColor Green
                    if ($DetailedOutput) {
                        Write-Host "   Changes preview:" -ForegroundColor Gray
                        $planOutput | Select-Object -First 20 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
                    }
                } else {
                    Write-Host "   Plan completed with warnings" -ForegroundColor Yellow
                    if ($DetailedOutput) {
                        Write-Host $planOutput -ForegroundColor Gray
                    }
                }
            } else {
                Write-Host "   Plan failed - backend init error" -ForegroundColor Red
                $success = $false
            }
            
            # Cleanup
            Remove-Item "backend-temp.tf" -ErrorAction SilentlyContinue
            Remove-Item "terraform-test.tfstate*" -ErrorAction SilentlyContinue
            Remove-Item -Recurse ".terraform" -ErrorAction SilentlyContinue
        } else {
            Write-Host "   terraform.tfvars not found, skipping plan" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   Plan error: $_" -ForegroundColor Red
        $success = $false
    }
    
    Set-Location ..\..\
    return $success
}

# Main execution
$originalLocation = Get-Location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

try {
    $allSuccess = $true
    
    # Test Prerequisites
    Write-Host "`nChecking Prerequisites..." -ForegroundColor Yellow
    
    # Check Terraform
    try {
        $tfVersion = terraform version
        Write-Host "   Terraform: $($tfVersion[0])" -ForegroundColor Green
    }
    catch {
        Write-Host "   Terraform not found" -ForegroundColor Red
        Write-Host "      Install from: https://terraform.io/downloads" -ForegroundColor Gray
        exit 1
    }
    
    # Check Git status
    try {
        $gitStatus = git status --porcelain 2>&1
        if ($gitStatus) {
            Write-Host "   Git working directory has changes:" -ForegroundColor Yellow
            $gitStatus | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        } else {
            Write-Host "   Git working directory clean" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "   Not in a git repository" -ForegroundColor Yellow
    }
    
    # Run tests based on environment parameter
    if ($Environment -eq "both") {
        $stagingSuccess = Test-Environment "staging"
        $productionSuccess = Test-Environment "production" 
        $allSuccess = $stagingSuccess -and $productionSuccess
    } else {
        $allSuccess = Test-Environment $Environment
    }
    
    # Final results
    Write-Host "`nTEST RESULTS" -ForegroundColor Magenta
    Write-Host "===============" -ForegroundColor Magenta
    
    if ($allSuccess) {
        Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
        Write-Host "Ready for pipeline execution" -ForegroundColor Green
        Write-Host "`nNext steps:" -ForegroundColor Cyan
        Write-Host "1. Commit your changes: git add ." -ForegroundColor Cyan
        Write-Host "2. Push to trigger pipeline: git push origin your-branch" -ForegroundColor Cyan
        Write-Host "3. Create PR for validation" -ForegroundColor Cyan
    } else {
        Write-Host "`nSOME TESTS FAILED" -ForegroundColor Red
        Write-Host "Fix issues before pushing to trigger pipeline" -ForegroundColor Yellow
        Write-Host "`nCommon fixes:" -ForegroundColor Cyan
        Write-Host "- Run: terraform fmt -recursive" -ForegroundColor Cyan
        Write-Host "- Check: terraform validate output" -ForegroundColor Cyan
        Write-Host "- Review: security scan results" -ForegroundColor Cyan
        exit 1
    }
    
    # Performance summary
    Write-Host "`nPerformance Info:" -ForegroundColor Gray
    $duration = ((Get-Date) - $startTime).TotalSeconds
    Write-Host "- Test duration: $duration seconds" -ForegroundColor Gray
    Write-Host "- Environment(s) tested: $Environment" -ForegroundColor Gray
    $scanStatus = if($SkipSecurityScans) { "Skipped" } else { "Included" }
    Write-Host "- Security scans: $scanStatus" -ForegroundColor Gray
}
catch {
    Write-Host "`nERROR: $_" -ForegroundColor Red
}
finally {
    Set-Location $originalLocation
}

Write-Host "`nLocal pipeline test completed!" -ForegroundColor Green