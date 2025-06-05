Okay, here's a detailed README.md for your `qaa-analysis` repository, based on the provided codebase.

```markdown
# QAA-Analysis: Quantitative Ethereum Address Analytics

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing) <!-- TODO: Add actual test coverage badge if CI is set up -->

QAA-Analysis is a Python-based project designed for in-depth analysis of Ethereum blockchain data, with a primary focus on calculating transaction fee revenue ("REV") attributed to user addresses. It leverages Google BigQuery for data extraction, implements cost-aware querying and caching mechanisms, and provides a foundation for further quantitative analysis, potentially including DeFi user behavior and address clustering.

## Key Features

*   **Ethereum REV Calculation:** Accurately calculates daily transaction fee revenue (total, tips, and burned fees post-EIP-1559) per Ethereum address.
*   **Cost-Aware BigQuery Client:** Interacts with Google BigQuery, estimating query costs to prevent budget overruns and ensuring efficient data retrieval.
*   **Query Caching:** Implements a local Parquet-based caching system to store results of expensive BigQuery queries, reducing redundant API calls and costs.
*   **Configurable ETL Pipeline:** A robust ETL (Extract, Transform, Load) process to fetch, process, and store REV data.
*   **Development & Production Modes:** Configuration options to tailor data lookback periods, sampling rates, and other parameters for different environments.
*   **DeFi Data Dictionary:** Includes curated metadata for major DeFi protocols, contracts, event selectors, and tokens to support advanced on-chain analysis.
*   **BigQuery Dataset Documentation:** A utility to generate Markdown documentation for the `bigquery-public-data.crypto_ethereum` dataset schema.
*   **Automated Testing:** Comprehensive unit and integration tests using `pytest`.
*   **Example Analysis Notebooks:** Scripts to demonstrate loading and inspecting the processed data.
*   **PowerShell Automation Scripts:** Helper scripts for common development tasks like running the ETL pipeline and test suite.

## Architecture Overview

The system is structured around a few core components:

1.  **Configuration (`src/qaa_analysis/config.py`):** Manages all pipeline settings, including GCP project ID, BigQuery limits, cache TTL, and operational modes (Dev/Prod). Reads from a `.env` file.
2.  **Cost-Aware BigQuery Client (`src/qaa_analysis/etl/cost_aware_client.py`):** A wrapper around the Google BigQuery client that performs dry runs to estimate query costs and ensures queries stay within defined byte limits.
3.  **Query Cache (`src/qaa_analysis/cache/query_cache.py`):** Stores the results of BigQuery queries as Parquet files locally. If a query with the same parameters is run again within the TTL, the cached result is served, saving time and cost.
4.  **REV Queries (`src/qaa_analysis/queries/rev_queries.py`):** Defines the SQL queries used to extract and calculate REV metrics from the Ethereum `transactions` and `blocks` tables in BigQuery.
5.  **Basic REV ETL (`src/qaa_analysis/etl/basic_rev_etl.py`):** The main ETL script that orchestrates the process:
    *   Initializes configuration, BQ client, and cache.
    *   Generates the REV SQL query based on the configured date range and sample rate.
    *   Fetches data from BigQuery (using the cache if available).
    *   Validates the retrieved DataFrame.
    *   Saves the processed DataFrame to a Parquet file in the `data/processed/` directory.
6.  **Data Dictionary (`data-dictionary/`):** Contains CSV files and Markdown documentation detailing DeFi protocol contracts, event selectors, and token metadata, crucial for contextualizing on-chain activity.
7.  **Metadata Explorer (`src/qaa_analysis/metadata_explorer.py`):** A script to query BigQuery's `INFORMATION_SCHEMA` and generate documentation for the public Ethereum dataset.

## Prerequisites

*   Python 3.11+
*   Poetry (for dependency management and virtual environments)
*   Google Cloud Platform (GCP) Account
*   A GCP Project with the BigQuery API enabled
*   Permissions to query the `bigquery-public-data.crypto_ethereum` dataset
*   Google Cloud SDK configured for authentication (e.g., via `gcloud auth application-default login`) or a service account key.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd qaa-analysis
    ```

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```
    This will create a virtual environment and install all necessary packages.

3.  **Set up environment variables:**
    Create a `.env` file in the project root directory by copying the example:
    ```bash
    cp .env.example .env  # Assuming you create an .env.example
    ```
    Then, edit the `.env` file with your specific configuration:
    ```env
    # .env
    GCP_PROJECT_ID="your-gcp-project-id"

    # Optional: Override defaults from config.py
    DEV_MODE="True"  # True for development (smaller lookback, no sampling), False for production
    BIGQUERY_MAX_BYTES_BILLED="10737418240" # Max bytes for a single query (e.g., 10 GB)
    CACHE_TTL_HOURS="24" # How long cached query results are valid
    ```
    **Note:** `GCP_PROJECT_ID` is mandatory. The other variables will use defaults from `config.py` if not set.

## Configuration

The pipeline's behavior is primarily controlled by environment variables loaded via `src/qaa_analysis/config.py`. Key variables include:

*   `GCP_PROJECT_ID`: (Required) Your Google Cloud Project ID.
*   `DEV_MODE`: (Default: `True`)
    *   `True`: Uses a short lookback period (e.g., 1 day) and full sampling (1.0). Ideal for development and testing.
    *   `False`: Uses a longer lookback period (e.g., 30 days) and a smaller sample rate (e.g., 0.1 or 10%). Suitable for production runs.
*   `BIGQUERY_MAX_BYTES_BILLED`: (Default: 10 GB) The maximum number of bytes a single BigQuery query is allowed to process. The `CostAwareBigQueryClient` will prevent queries exceeding this.
*   `CACHE_TTL_HOURS`: (Default: 24 hours) The time-to-live for cached query results.

These can be set in the `.env` file or as system environment variables.

## Core Modules

*   `src/qaa_analysis/config.py`: Handles pipeline configuration.
*   `src/qaa_analysis/etl/cost_aware_client.py`: Manages cost-effective BigQuery interactions.
*   `src/qaa_analysis/cache/query_cache.py`: Implements the query caching logic.
*   `src/qaa_analysis/queries/rev_queries.py`: Generates SQL for REV calculation.
*   `src/qaa_analysis/etl/basic_rev_etl.py`: Main ETL pipeline script.
*   `src/qaa_analysis/metadata_explorer.py`: Generates documentation for the BigQuery Ethereum dataset.

## Running the Pipeline

### 1. Execute the Basic REV ETL

To run the main ETL process which calculates and saves the daily REV data:

```bash
poetry run python -m qaa_analysis.etl.basic_rev_etl
```

This script will:
*   Load configuration.
*   Determine the date range and sample rate.
*   Generate the SQL query.
*   Attempt to fetch data from the cache or, if a cache miss/expiry, from BigQuery.
*   Save the processed data as a Parquet file in `data/processed/`. The filename will indicate the date range and sample rate (e.g., `basic_rev_daily_data_YYYYMMDD_to_YYYYMMDD_sampleNN.parquet`).

### 2. Analyzing Processed Data

An example script is provided to load and inspect the Parquet files generated by the ETL:

```bash
poetry run python notebook/analyze_data.py
```
This script will attempt to load the most recently generated Parquet file (based on `DEV_MODE` settings in `config.py`), display its schema, head, and basic statistics. It also exports the data to a CSV file in the same directory.

### 3. Generating BigQuery Ethereum Dataset Documentation

To generate a Markdown file documenting the schema of key tables in the `bigquery-public-data.crypto_ethereum` dataset:

```bash
poetry run python src/qaa_analysis/metadata_explorer.py
```
This will create `ethereum_dataset_documentation.md` in the project root.

## Automation Scripts (PowerShell)

The `scripts/` directory contains PowerShell scripts to streamline common tasks:

*   **`run_etl.ps1`**: Executes the main ETL pipeline.
    ```powershell
    .\scripts\run_etl.ps1
    .\scripts\run_etl.ps1 -ProductionMode # Overrides DEV_MODE to False
    ```
*   **`run_tests.ps1`**: Executes the test suite using pytest.
    ```powershell
    .\scripts\run_tests.ps1
    .\scripts\run_tests.ps1 -Coverage -VerboseOutput
    ```
Refer to `scripts/README.md` for more details on these scripts.

## Testing

The project uses `pytest` for testing. To run the test suite:

```bash
poetry run pytest
```

Or, for more options like coverage:

```bash
poetry run pytest --cov=src/qaa_analysis --cov-report=html
```
This will generate a coverage report in the `htmlcov/` directory.

## Data Dictionary

A detailed data dictionary for DeFi protocol contracts, event selectors, and token metadata used for deeper analysis can be found in:
`data-dictionary/DATA_DICTIONARY.md`

The CSV files in this directory (`defi_app_contracts.csv`, `event_selectors.csv`, etc.) provide the raw data.

## Directory Structure

```
qaa-analysis/
├── .env.example                # Example environment file
├── .gitignore
├── data/                       # Stores local data
│   ├── cache/                  # Cached BigQuery query results (Parquet)
│   └── processed/              # Processed data from ETL (Parquet, CSV)
├── data-dictionary/            # Curated DeFi metadata and documentation
├── docs/                       # Generated documentation (e.g., BQ dataset schema)
├── examples/                   # Example scripts demonstrating core module usage
├── notebook/                   # Scripts for data analysis and exploration
├── pyproject.toml              # Poetry project configuration and dependencies
├── repomix.config.json         # Repomix configuration (if used)
├── scripts/                    # Automation scripts (e.g., PowerShell)
│   ├── README.md
│   ├── run_etl.ps1
│   └── run_tests.ps1
├── src/
│   └── qaa_analysis/           # Main source code
│       ├── __init__.py
│       ├── cache/              # Query caching module
│       ├── config.py           # Configuration management
│       ├── etl/                # ETL logic, including BQ client
│       ├── metadata_explorer.py # BigQuery schema documentation generator
│       ├── queries/            # SQL query generation
│       └── tests/              # Pytest tests for src modules (can also be top-level tests/)
├── tests/                      # Alternative/additional location for tests
└── README.md                   # This file
```

## Contributing

Contributions are welcome! Please follow these general guidelines:
1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Write clean, well-documented code.
4.  Ensure all tests pass (`poetry run pytest`).
5.  Format your code using Black (`poetry run black .`).
6.  Lint your code using Ruff (`poetry run ruff check --fix .`).
7.  Submit a pull request with a clear description of your changes.

## License

<!-- TODO: Add License if applicable, e.g., MIT -->
This project is currently unlicensed.
```