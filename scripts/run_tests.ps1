#Requires -Version 5.1

<#
.SYNOPSIS
    Runs the QAA Analysis test suite using pytest.

.DESCRIPTION
    This script executes pytest using Poetry to ensure tests run within the
    project's managed virtual environment. Supports various pytest options
    including verbose output, coverage reporting, and running specific tests.

.PARAMETER TestPath
    Optional path to a specific test file or directory to run.
    If not specified, runs all tests in the project.

.PARAMETER VerboseOutput
    Switch to enable verbose pytest output (-v flag).

.PARAMETER Coverage
    Switch to enable coverage reporting with term-missing output.

.PARAMETER FailFast
    Switch to stop on first test failure (-x flag).

.EXAMPLE
    .\scripts\run_tests.ps1
    Runs all tests with default settings.

.EXAMPLE
    .\scripts\run_tests.ps1 -VerboseOutput -Coverage
    Runs all tests with verbose output and coverage reporting.

.EXAMPLE
    .\scripts\run_tests.ps1 -TestPath "tests/test_config.py" -VerboseOutput
    Runs specific test file with verbose output.

.EXAMPLE
    .\scripts\run_tests.ps1 -TestPath "tests/" -FailFast
    Runs all tests in directory and stops on first failure.
#>

[CmdletBinding()]
param (
    [string]$TestPath,
    [switch]$VerboseOutput,
    [switch]$Coverage,
    [switch]$FailFast
)

# Set error action preference for better error handling
$ErrorActionPreference = "Stop"

Write-Host "[TEST] Starting QAA Test Suite..." -ForegroundColor Green

# Build pytest arguments
$PytestArgs = New-Object System.Collections.Generic.List[string]

if ($VerboseOutput) { 
    $PytestArgs.Add("-v")
    Write-Host "[TEST] Verbose output enabled." -ForegroundColor Cyan
}

if ($Coverage) { 
    $PytestArgs.Add("--cov=src/qaa_analysis")
    $PytestArgs.Add("--cov-report=term-missing")
    $PytestArgs.Add("--cov-report=html:htmlcov")
    Write-Host "[TEST] Coverage reporting enabled." -ForegroundColor Cyan
}

if ($FailFast) {
    $PytestArgs.Add("-x")
    Write-Host "[TEST] Fail-fast mode enabled." -ForegroundColor Cyan
}

if ($TestPath) { 
    $PytestArgs.Add($TestPath)
    Write-Host "[TEST] Running specific tests: $TestPath" -ForegroundColor Cyan
} else {
    Write-Host "[TEST] Running all tests in the project." -ForegroundColor Cyan
}

# Construct the command
$PytestArgsString = $PytestArgs -join ' '
$Command = "poetry run pytest $PytestArgsString".Trim()

Write-Host "[TEST] Executing: $Command" -ForegroundColor Yellow

try {
    # Execute pytest using Poetry
    Invoke-Expression $Command
    
    # Check the exit code
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[TEST] Test suite failed with exit code $LASTEXITCODE."
        if ($Coverage) {
            Write-Host "[TEST] Coverage report may still be available in htmlcov/ directory." -ForegroundColor Yellow
        }
        exit $LASTEXITCODE
    } else {
        Write-Host "[TEST] All tests passed successfully!" -ForegroundColor Green
        if ($Coverage) {
            Write-Host "[TEST] Coverage report generated in htmlcov/ directory." -ForegroundColor Cyan
        }
    }
}
catch {
    Write-Error "[TEST] An unexpected error occurred while running tests: $($_.Exception.Message)"
    exit 1
}

Write-Host "[TEST] Test execution completed." -ForegroundColor Green 