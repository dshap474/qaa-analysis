#Requires -Version 5.1

<#
.SYNOPSIS
    Runs the QAA Analysis ETL pipeline for basic REV calculation.

.DESCRIPTION
    This script executes the main ETL pipeline using Poetry to ensure it runs
    within the project's managed virtual environment. Provides clear console
    feedback and proper error handling.

.PARAMETER ProductionMode
    Switch to override DEV_MODE=False for this specific run, regardless of
    .env file or default configuration.

.EXAMPLE
    .\scripts\run_etl.ps1
    Runs the ETL pipeline with default configuration.

.EXAMPLE
    .\scripts\run_etl.ps1 -ProductionMode
    Runs the ETL pipeline with DEV_MODE=False override.
#>

[CmdletBinding()]
param (
    [switch]$ProductionMode
)

# Set error action preference for better error handling
$ErrorActionPreference = "Stop"

Write-Host "[ETL] Starting QAA ETL Process..." -ForegroundColor Green

# Store original DEV_MODE value for restoration
$OriginalDevMode = $env:DEV_MODE

if ($ProductionMode) {
    Write-Host "[ETL] Running in Production Mode override (DEV_MODE=False)." -ForegroundColor Yellow
    $env:DEV_MODE = "False"
}

try {
    Write-Host "[ETL] Executing ETL pipeline via Poetry..." -ForegroundColor Cyan
    
    # Execute the ETL pipeline using Poetry
    poetry run python -m qaa_analysis.etl.basic_rev_etl
    
    # Check the exit code
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[ETL] ETL process failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    } else {
        Write-Host "[ETL] ETL Process completed successfully." -ForegroundColor Green
        Write-Host "[ETL] Check the data/processed/ directory for output files." -ForegroundColor Cyan
    }
}
catch {
    Write-Error "[ETL] An unexpected error occurred while running the ETL process: $($_.Exception.Message)"
    exit 1
}
finally {
    # Restore original DEV_MODE environment variable
    if ($ProductionMode) {
        if ($null -ne $OriginalDevMode) {
            $env:DEV_MODE = $OriginalDevMode
            Write-Host "[ETL] Restored DEV_MODE environment variable to: $OriginalDevMode" -ForegroundColor Yellow
        } else {
            Remove-Item Env:\DEV_MODE -ErrorAction SilentlyContinue
            Write-Host "[ETL] Removed DEV_MODE environment variable override." -ForegroundColor Yellow
        }
    }
}

Write-Host "[ETL] ETL script execution completed." -ForegroundColor Green 