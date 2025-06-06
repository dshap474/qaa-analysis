# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QAA-Analysis (Quantitative Ethereum Address Analytics) is a Python-based analytics platform for calculating transaction fee revenue for Ethereum addresses using Google BigQuery. The project features cost-aware data processing, intelligent caching, and behavioral feature engineering for blockchain analytics.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with: GCP_PROJECT_ID="your-gcp-project-id"
```

### Running the Application
```bash
# Main ETL pipeline
poetry run python -m qaa_analysis.etl.basic_rev_etl

# Windows/PowerShell alternative
.\scripts\run_etl.ps1

# Production mode
.\scripts\run_etl.ps1 -ProductionMode
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/qaa_analysis --cov-report=html

# Run specific test
poetry run pytest tests/test_config.py -v

# PowerShell with options
.\scripts\run_tests.ps1 -VerboseOutput -Coverage -FailFast
```

### Code Quality
```bash
# Format code
poetry run black .

# Lint and auto-fix
poetry run ruff check --fix .
```

### Building
```bash
poetry build
```

## Architecture & Key Patterns

### Cost-Aware BigQuery Access
The codebase enforces cost controls on all BigQuery operations:
- `CostAwareBigQueryClient` in `src/qaa_analysis/etl/cost_aware_client.py` wraps all queries with dry-run cost estimation
- Default limit: 10GB per query (configurable via `BIGQUERY_MAX_BYTES_BILLED`)
- All queries must pass cost validation before execution

### Caching Strategy
- `QueryCache` in `src/qaa_analysis/cache/query_cache.py` provides local Parquet caching
- Cache keys are SHA256 hashes of query + parameters
- Default TTL: 24 hours (configurable via `CACHE_TTL_HOURS`)
- Cache location: `data/cache/`

### ETL Pipeline Flow
1. **Configuration** (`config.py`): Environment-based settings with DEV_MODE toggle
2. **Queries** (`queries/rev_queries.py`): SQL generation with proper JOINs and filters
3. **ETL** (`etl/basic_rev_etl.py`): Orchestrates data extraction, transformation, and storage
4. **Output**: Parquet files in `data/` directory

### Feature Engineering
- Abstract `FeatureExtractor` base class for extensibility
- Parallel processing with chunk-based memory management
- 67+ behavioral features across temporal, value, and protocol dimensions
- Located in `src/qaa_analysis/feature_engineering/`

### Testing Approach
- Tests use `pytest` with environment mocking for configuration
- Test files mirror source structure
- Key test patterns:
  - Mock `os.environ` for configuration tests
  - Parameterized tests for multiple scenarios
  - Integration tests for complete workflows

## Important Configuration

### Environment Variables
- **Required**: `GCP_PROJECT_ID` - Your Google Cloud Project ID
- **Optional**:
  - `DEV_MODE` - "True" (default) for 1-day window, "False" for 30-day window
  - `SAMPLE_RATE` - 1.0 in dev, 0.1 in production
  - `BIGQUERY_MAX_BYTES_BILLED` - Cost limit in bytes (default: 10GB)
  - `CACHE_TTL_HOURS` - Cache expiration (default: 24)

### Development vs Production
The codebase automatically adjusts behavior based on `DEV_MODE`:
- **Development**: 1-day data window, 100% sampling, verbose logging
- **Production**: 30-day data window, 10% sampling, optimized performance

## Key Files to Understand

1. **`src/qaa_analysis/config.py`**: Central configuration management
2. **`src/qaa_analysis/etl/cost_aware_client.py`**: BigQuery cost controls
3. **`src/qaa_analysis/queries/rev_queries.py`**: Core SQL query generation
4. **`src/qaa_analysis/etl/basic_rev_etl.py`**: Main ETL orchestration
5. **`src/qaa_analysis/cache/query_cache.py`**: Caching implementation

## Common Tasks

### Adding New Queries
1. Add query function to `queries/rev_queries.py`
2. Implement cost estimation in the query function
3. Add corresponding ETL logic in `etl/basic_rev_etl.py`
4. Write tests in `tests/test_rev_queries.py`

### Extending Feature Engineering
1. Create new feature extractor inheriting from `FeatureExtractor`
2. Implement `extract()` method
3. Add to pipeline in `feature_engineering/feature_pipeline.py`
4. Document features in module docstring

### Debugging BigQuery Costs
1. Check dry-run estimates in logs
2. Use `CostAwareBigQueryClient.estimate_query_cost()` directly
3. Monitor `MAX_BYTES_BILLED` parameter
4. Review query efficiency with `EXPLAIN` in BigQuery console