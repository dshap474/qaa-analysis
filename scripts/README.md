# QAA Analysis - Automation Scripts

This directory contains PowerShell automation scripts to streamline common development workflows for the QAA Analysis project.

## Prerequisites

- PowerShell 5.1 or later
- Poetry installed and configured for the project
- Project dependencies installed via `poetry install`

## Available Scripts

### 🚀 ETL Pipeline Runner (`run_etl.ps1`)

Executes the main ETL pipeline for basic REV calculation.

**Basic Usage:**
```powershell
.\scripts\run_etl.ps1
```

**Production Mode Override:**
```powershell
.\scripts\run_etl.ps1 -ProductionMode
```

**Features:**
- Runs ETL pipeline via Poetry's managed virtual environment
- Optional production mode override (sets `DEV_MODE=False`)
- Clear console feedback with colored output
- Proper error handling and exit codes
- Environment variable restoration

### 🧪 Test Suite Runner (`run_tests.ps1`)

Executes the project test suite using pytest.

**Basic Usage:**
```powershell
.\scripts\run_tests.ps1
```

**Advanced Usage:**
```powershell
# Run with verbose output and coverage
.\scripts\run_tests.ps1 -VerboseOutput -Coverage

# Run specific test file
.\scripts\run_tests.ps1 -TestPath "tests/test_config.py" -VerboseOutput

# Run tests in a directory with fail-fast
.\scripts\run_tests.ps1 -TestPath "tests/" -FailFast

# All options combined
.\scripts\run_tests.ps1 -TestPath "tests/" -VerboseOutput -Coverage -FailFast
```

**Parameters:**
- `-TestPath`: Run specific test file or directory
- `-VerboseOutput`: Enable verbose pytest output
- `-Coverage`: Generate coverage reports (terminal + HTML)
- `-FailFast`: Stop on first test failure

**Features:**
- Runs tests via Poetry's managed virtual environment
- Flexible parameter combinations
- Coverage reporting with HTML output in `htmlcov/`
- Clear console feedback with colored output
- Proper error handling and exit codes

## Usage Tips

1. **Run from Project Root**: Execute scripts from the project root directory for proper path resolution.

2. **Check Exit Codes**: Scripts properly propagate exit codes, making them suitable for CI/CD pipelines.

3. **Environment Variables**: The ETL script can temporarily override `DEV_MODE` without affecting your global environment.

4. **Coverage Reports**: When using `-Coverage`, HTML reports are generated in the `htmlcov/` directory for detailed analysis.

5. **PowerShell Help**: Use `Get-Help` for detailed parameter information:
   ```powershell
   Get-Help .\scripts\run_etl.ps1 -Full
   Get-Help .\scripts\run_tests.ps1 -Full
   ```

## Troubleshooting

- **Poetry Not Found**: Ensure Poetry is installed and available in your PATH
- **Permission Errors**: You may need to adjust PowerShell execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Module Import Errors**: Ensure all dependencies are installed: `poetry install`

## Integration with Development Workflow

These scripts are designed to integrate seamlessly with your development workflow:

1. **Development Cycle**: Use `run_tests.ps1` frequently during development
2. **Data Pipeline Testing**: Use `run_etl.ps1` to test the complete pipeline
3. **CI/CD Integration**: Both scripts return appropriate exit codes for automation
4. **Code Coverage**: Regular use of `-Coverage` helps maintain code quality

For more information about the project structure and modules, see the main project README. 