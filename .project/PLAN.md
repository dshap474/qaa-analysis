# Quant Address Analytics - Phased Development Plan

**Version:** 1.4
**Date:** (Today's Date)
**Status:** Phase 1 Complete, Phase 2 Starting

## 1. Project Goal

To develop a Quant Address Analytics platform that identifies and characterizes Ethereum address behaviors, attributes revenue (REV) accurately, and delivers actionable insights for protocol teams, REV maximization strategies, and user acquisition. This plan prioritizes cost-effective development, iterative feature enhancement, and continuous validation.

## 2. Guiding Principles

*   **Cost-First Development:** All initial development and experimentation will be performed on minimal, recent datasets (1-7 days) to keep BigQuery costs extremely low (<$1/day initially).
*   **Iterate & Validate:** Start with the simplest viable REV calculation (Blockworks basic) and incrementally add complexity. Each new feature or model component will be validated for correctness and value before wider application.
*   **Fail Fast, Learn Cheaply:** Small-scale experiments allow for rapid identification of what works and what doesn't without significant resource expenditure.
*   **Modularity & Reusability:** Design components (queries, feature transformers, clients) to be modular and reusable as the system scales.
*   **Progressive Data Scaling:** Only expand data windows (e.g., to 30, 90, 365 days) and sampling rates once algorithms are stable and proven valuable on smaller datasets.
*   **Actionable Insights Focus:** Continuously align technical development with the goal of producing interpretable and actionable insights for end-users.

## 3. Core Architectural Pillars (Initial Focus)

*   **Configuration Management (`PipelineConfig`):** Centralized control for development/production modes, data lookback periods, sampling rates, and cost limits. - ✅ **Implemented**
*   **Cost-Aware BigQuery Client (`CostAwareBigQueryClient`):** Wrapper around the BigQuery client to enforce dry-runs, estimate query costs, and apply billing limits before execution. - ✅ **Implemented**
*   **Optimized SQL Queries (`queries/`):** Parameterized, partition-aware SQL queries, starting with basic REV and evolving. - ✅ **Implemented & Corrected**
*   **Local Development Cache (`QueryCache`):** Parquet-based local caching of query results to avoid repeated BigQuery costs during iterative development and debugging of downstream tasks (feature engineering, clustering). - ✅ **Implemented**
*   **Basic Feature Engineering Pipeline:** Initial Python scripts to transform raw query results into basic features. - ⏳ **Upcoming (Phase 2)**
*   **Simple Clustering:** Initial experiments with K-Means on basic features to establish a baseline. - ⏳ **Upcoming (Phase 2)**
*   **Metadata Exploration Tool (`metadata_explorer.py`):** Utility to accurately determine BigQuery table schemas. - ✅ **Enhanced & Operational**
*   **Automation Scripts (`scripts/`):** PowerShell scripts for ETL and test execution. - ✅ **Implemented**
*   **Data Analysis/Validation Script (`notebook/analyze_data.py`):** Helper script to load, inspect, and facilitate validation of processed data, including CSV export. - ✅ **Enhanced & Operational**

## 4. Development & Staging Strategy (Iterative Data Scaling)

| Phase        | Data Window | Sampling | Est. Daily BQ Cost | Purpose                                         |
| :----------- | :---------- | :------- | :----------------- | :---------------------------------------------- |
| **Dev Alpha**| **1 day**   | **100%** | **<$0.10**         | Core algorithm dev, cost control validation     |
| **Dev Beta** | **7 days**  | **100%** | **<$0.70**         | Short-term pattern validation, stability testing|
| **Staging**  | 30 days     | 10-50%   | <$5.00             | Statistical significance, broader patterns      |
| **Pre-Prod** | 90 days     | 50-100%  | <$15.00            | Performance testing, near-production scale      |
| **Prod**     | 90-365+ days| 100%     | Variable           | Full-scale analysis, ongoing operations         |

*Initial development (Phases 1-2 below) will strictly adhere to **Dev Alpha** and **Dev Beta** data windows.*

## 5. Detailed Phased Implementation Plan

### Phase 1: Foundational REV Calculation & Cost Control (Weeks 1-2) - ✅ COMPLETE

**Objective:** Implement the basic Blockworks REV calculation with robust cost controls and local caching for efficient development.

*   **Week 1: Setup & Core Cost Control**
    *   **Task 1.1: Project Setup & Environment - ✅ COMPLETE**
        *   Initialized Python project (Poetry).
        *   Virtual environment and core dependencies installed (including `db-dtypes`).
        *   Git repository and initial project structure established.
    *   **Task 1.2: Configuration Management (`PipelineConfig`) - ✅ COMPLETE**
        *   Implemented `src/qaa_analysis/config.py` with `PipelineConfig` class.
        *   Handles `DEV_MODE`, lookback, sampling, cost limits, paths. Loads from `.env`.
        *   Includes `get_date_filter()` and directory creation.
    *   **Task 1.3: Cost-Aware BigQuery Client (`CostAwareBigQueryClient`) - ✅ COMPLETE**
        *   Implemented `src/qaa_analysis/etl/cost_aware_client.py`.
        *   Integrates `PipelineConfig`, performs dry runs, estimates costs, enforces limits.
    *   **Task 1.4: Local Query Cache (`QueryCache`) - ✅ COMPLETE**
        *   Implemented `src/qaa_analysis/cache/query_cache.py`.
        *   Integrates `PipelineConfig`, uses hashed keys, Parquet storage, TTL.

*   **Week 2: Basic REV Query & Initial Data Pipeline**
    *   **Task 1.5: Basic Blockworks REV Query (`rev_queries.py`) - ✅ COMPLETE & CORRECTED**
        *   Created `src/qaa_analysis/queries/rev_queries.py` with `get_blockworks_rev_query`.
        *   Query now correctly `JOINs transactions t WITH blocks b ON t.block_number = b.number` to fetch `b.base_fee_per_gas` for accurate EIP-1559 fee calculations.
    *   **Task 1.6: Initial ETL Script (`basic_rev_etl.py`) - ✅ COMPLETE & OPERATIONAL**
        *   Created `src/qaa_analysis/etl/basic_rev_etl.py` orchestrating core modules.
        *   Successfully fetches, caches, and saves data using the corrected query.
    *   **Task 1.7: Validation & Cost Monitoring - ✅ COMPLETE**
        *   ETL script successfully executed and validated.
        *   BigQuery costs confirmed low and acceptable.
        *   Data correctness cross-referenced with Etherscan.
        *   Local caching functionality confirmed.
    *   **Task 1.8: PowerShell/Bash Automation Scripts - ✅ COMPLETE**
        *   Created `scripts/run_etl.ps1` and `scripts/run_tests.ps1`.

**Deliverables for Phase 1 (All Complete):**
*   ✅ Functional `PipelineConfig`, `CostAwareBigQueryClient`, `QueryCache` modules.
*   ✅ Enhanced `metadata_explorer.py` for accurate schema discovery.
*   ✅ Basic Blockworks REV query (`get_blockworks_rev_query`) corrected and operational.
*   ✅ ETL script/workflow (`basic_rev_etl.py`) implemented and operational.
*   ✅ PowerShell automation scripts (`run_etl.ps1`, `run_tests.ps1`).
*   ✅ Helper script `notebook/analyze_data.py` for loading/inspecting processed data (including CSV export).
*   ✅ Example `.env` file and usage examples.
*   ✅ Comprehensive test suites for core modules.
*   ✅ Cost control mechanisms confirmed effective.
*   ✅ Data correctness and caching validated.

### Phase 2: Basic Feature Engineering & Initial Clustering (Weeks 3-4) - ⏭️ UP NEXT

**Objective:** Expand on basic REV data to create initial features and perform a first-pass clustering to establish a baseline and test the pipeline.

*   **Week 3: Basic Feature Engineering & Data Expansion**
    *   **Task 2.1: Define Initial Core Features**
        *   Based on the output of the corrected REV query (which is per address, per day), features will be aggregated per address over the entire loaded period.
        *   **Core Features per Address:**
            *   `total_rev_eth_period`: Sum of `total_rev_eth` over all days for the address.
            *   `total_tx_count_period`: Sum of `tx_count` over all days for the address.
            *   `avg_daily_tx_count_period`: Average `tx_count` per day the address was active.
            *   `avg_tx_fee_eth_period`: `total_rev_eth_period / total_tx_count_period`.
            *   `total_tips_rev_eth_period`: Sum of `tips_rev_eth` over all days.
            *   `total_burned_rev_eth_period`: Sum of `burned_rev_eth` over all days.
            *   `tip_to_total_fee_ratio_period`: `total_tips_rev_eth_period / total_rev_eth_period`.
            *   `active_days_count`: Number of unique days the address had transactions.
    *   **Task 2.2: Feature Engineering Script**
        *   Create `src/qaa_analysis/features/basic_features.py`.
        *   This script will:
            1.  Accept a DataFrame (output from Phase 1 ETL, potentially multiple days of data).
            2.  Group data by `address`.
            3.  Calculate the aggregated features listed in Task 2.1.
            4.  Handle potential division by zero (e.g., for ratios if `total_rev_eth_period` is zero) or NaN values gracefully (e.g., fill with 0 or a specific indicator).
            5.  Output a new DataFrame: `address | feature1 | feature2 | ...` (one row per unique address).
    *   **Task 2.3: Data Expansion to 7 Days (`Dev Beta`)**
        *   Modify `PipelineConfig` (`DEV_MODE=True`, `MAX_DAYS_LOOKBACK = 7`).
        *   Run the ETL script (`scripts/run_etl.ps1`) to fetch 7 days of daily REV data. This will result in multiple Parquet files in `data/processed/` (one per day if the ETL saves daily) or one combined file if the ETL is adapted. *For simplicity, assume the ETL saves one file per run covering the entire lookback period.*
        *   Monitor BigQuery costs (expected to be <$0.02 for 7 days with JOIN).
        *   Run the new feature engineering script (`src/qaa_analysis/features/basic_features.py`) on this 7-day dataset (which will be loaded from the single Parquet file covering the 7 days).

*   **Week 4: Initial Clustering & Validation**
    *   **Task 2.4: Simple Clustering Implementation**
        *   In a Jupyter Notebook (`notebooks/prototyping/01_initial_clustering.ipynb`) or a new script:
            1.  Load the 7-day aggregated feature set (output from Task 2.2).
            2.  Perform basic preprocessing:
                *   Scaling (e.g., `StandardScaler` or `MinMaxScaler` from `sklearn.preprocessing`).
                *   Handle outliers if necessary (e.g., clipping, log transformation for highly skewed features like `total_rev_eth_period`).
            3.  Implement K-Means clustering (`sklearn.cluster.KMeans`).
                *   Start with a fixed `k` (e.g., k=5 to 8).
                *   Experiment with the Elbow method or Silhouette scores to find a reasonable `k`.
    *   **Task 2.5: Basic Cluster Interpretation**
        *   Analyze cluster centroids: What are the average feature values for each cluster?
        *   Profile clusters: e.g., "High REV, High Tx Count", "Low REV, Low Tx Count", "High Tip Ratio".
        *   Visualize feature distributions per cluster (box plots, histograms).
    *   **Task 2.6: Cluster Stability (Simple Test)**
        *   If time permits and data allows: Run clustering on different subsets of the 7-day data (e.g., first 3 days vs. last 3 days, or different random samples) to qualitatively assess if similar clusters emerge. (Formal stability metrics later).
    *   **Task 2.7: Document Initial Findings**
        *   Summarize the characteristics of the identified clusters.
        *   Note limitations of the current features and K-Means.

**Deliverables for Phase 2:**
*   Feature engineering script (`basic_features.py`) that produces per-address aggregated features.
*   Initial K-Means clustering model applied to a 7-day dataset.
*   Preliminary cluster profiles and interpretations.
*   Early assessment of cluster stability (if performed).
*   Documentation of findings and limitations.

### Phase 3: Advanced Feature Engineering & Enhanced Clustering (Weeks 5-8)

**Objective:** Introduce more sophisticated behavioral features and explore more robust clustering algorithms, still within cost-controlled data windows.

*   **Week 5-6: Temporal & Contract Interaction Features**
    *   **Task 3.1: Design Temporal Features**
        *   Examples: Inter-transaction time (mean, median, stddev), hour-of-day activity patterns (e.g., % txns in peak hours vs. off-peak).
        *   Requires modifying the base query to pull `block_timestamp` for each transaction before aggregation if not already available at the right granularity.
        *   Update `rev_queries.py` or create new query functions.
    *   **Task 3.2: Design Basic Contract Interaction Features**
        *   Examples: Number of unique contract addresses interacted with (`to_address` where `to_address` is a contract).
        *   Requires joining with `bigquery-public-data.crypto_ethereum.contracts` table or inferring contracts (e.g., `code != '0x'`).
        *   Update queries accordingly. Be mindful of JOIN costs; perform on the filtered transaction set.
    *   **Task 3.3: Implement Feature Engineering for New Features**
        *   Extend `src/qaa_analysis/features/` module.
        *   Ensure new queries are wrapped with `CostAwareBigQueryClient` and `QueryCache`.
    *   **Task 3.4: Correlation Analysis & Feature Selection**
        *   Build a correlation matrix of all features developed so far.
        *   Identify highly correlated features to avoid multicollinearity in models.
        *   Select an initial set of ~15-20 interpretable features.

*   **Week 7-8: Enhanced Clustering & REV Attribution Refinements**
    *   **Task 3.5: Experiment with HDBSCAN**
        *   Apply HDBSCAN (`hdbscan` library) to the enhanced feature set.
        *   Analyze its ability to find natural groupings and handle outliers.
        *   Compare results with K-Means.
    *   **Task 3.6: Experiment with Isolation Forest for Anomaly Detection**
        *   Use `sklearn.ensemble.IsolationForest` to identify anomalous addresses (potential whales, attackers, or unique entities).
        *   Analyze characteristics of detected anomalies.
    *   **Task 3.7: Initial Priority Fee Gaming Analysis (Simplified)**
        *   Query: Identify transactions where `gas_price` is significantly higher (e.g., > 2x) than `block_base_fee_per_gas` or block median/P90 gas price.
        *   Feature: `priority_gaming_tx_ratio` or `avg_priority_premium_paid`.
        *   Incorporate into REV attribution as a component of "Indirect REV" or "Behavioral REV".
    *   **Task 3.8: Refine Cluster Interpretation & Validation**
        *   Use Silhouette scores, Davies-Bouldin Index for cluster quality.
        *   Develop more robust cluster stability metrics (e.g., Jaccard Index for member overlap across time periods).
        *   Focus on interpretability of clusters with new features.

**Deliverables for Phase 3:**
*   Implementation of temporal and basic contract interaction features.
*   Working prototypes of HDBSCAN and Isolation Forest on small datasets.
*   Initial analysis of priority fee gaming patterns.
*   More robust cluster validation and interpretation.
*   A refined set of ~15-20 features.

### Phase 4: MEV & Complex Value Flows (Weeks 9-12+)

**Objective:** Carefully begin exploring MEV-related metrics and more complex value flows, always starting with highly sampled or specific subsets of data due to query complexity and cost.

*   **Task 4.1: MEV - Sandwich Attack Detection (Simplified, Sampled)**
    *   Query: Focus on `traces` and `logs` for known DEX router interactions.
    *   Implement pattern matching for (attacker_tx1 -> victim_tx -> attacker_tx2) within the same block, targeting the same token pair.
    *   **Crucial:** Start with a very small sample of blocks or known MEV bot addresses to develop and test the query logic due to high cost of `traces`.
*   **Task 4.2: Cross-Contract Value Flows (Highly Sampled/Targeted)**
    *   Query: Analyze `traces` table for `call_type` and `value` transfers between contracts.
    *   Focus on identifying common DeFi composability patterns (e.g., flash loan origination -> usage -> repayment).
    *   Again, **extreme caution with `traces` table queries**. Start with specific transaction hashes or addresses.
*   **Task 4.3: Integrate with Multi-Dimensional REV Model (Conceptual)**
    *   Begin mapping features and findings to the proposed multi-dimensional REV model:
        *   Direct REV (already covered)
        *   Indirect REV (e.g., MEV extracted, value provided in LPs - requires token transfer analysis)
        *   Protocol REV (fees generated for specific protocols - requires identifying protocol contract interactions)
*   **Task 4.4: Business Alignment & Use Case Validation**
    *   Schedule interviews with 3-5 potential protocol team users.
    *   Present initial cluster findings and REV metrics.
    *   Gather feedback on what insights are most valuable and actionable for them.
    *   Refine feature priorities and insight presentation based on feedback.

**Deliverables for Phase 4:**
*   Proof-of-concept queries for simplified MEV detection and cross-contract flows on limited data.
*   Initial mapping of findings to the multi-dimensional REV model.
*   Documented feedback from protocol teams.

## 6. Scaling to Production (Beyond Initial 12 Weeks)

*   **Gradual Data Scaling:** Incrementally increase `MAX_DAYS_LOOKBACK` and `SAMPLE_RATE` in `PipelineConfig`, monitoring costs and performance at each step.
*   **Workflow Orchestration:** Implement Prefect/Dagster for managing the complex DAG of data ingestion, feature engineering, clustering, and insight generation.
*   **Feature Store:** Consider Feast/Tecton for versioning features, preventing drift, and serving features for real-time use cases (if applicable).
*   **Optimized Queries for Scale:** Refactor BigQuery queries for performance over larger datasets (e.g., using `APPROX_QUANTILES` instead of exact, further join optimization).
*   **Dedicated Service Accounts & Permissions:** Secure GCP resources.
*   **Monitoring & Alerting:** Set up comprehensive monitoring for pipeline health, data quality (e.g., Great Expectations), and costs.
*   **Serving Layer (if needed):** FastAPI + Redis for real-time cluster assignment or insight delivery.
*   **Multi-Chain Architecture Design:** Formalize the chain-agnostic feature schema if expanding to other chains.

## 7. Key Technologies (Reiteration)

*   **Data Backend:** Google BigQuery (Public Ethereum Dataset)
*   **Processing:** Python, Pandas, PyArrow
*   **Clustering:** Scikit-learn, HDBSCAN
*   **Workflow (Future):** Prefect/Dagster
*   **Feature Store (Future):** Feast/Tecton
*   **Serving (Future):** FastAPI, Redis
*   **Data Quality (Future):** Great Expectations
*   **Version Control:** Git
*   **Dependency Management:** Poetry
*   **Automation:** PowerShell

## 8. Critical Design Decisions (Summary)

*   **Batch vs. Streaming:** Start batch, design for future streaming potential.
*   **Feature Complexity:** Start with basic aggregated features, expand cautiously based on value and interpretability.
*   **Multi-chain:** Design chain-agnostic schemas early if expansion is planned.
*   **Partition Strategy:** Daily partitions with explicit date filters in all BigQuery queries.
*   **Development Cache Layer:** Local Parquet cache with TTL for dev iterations.
*   **Cost Control:** Mandatory dry runs and billing limits via `CostAwareBigQueryClient`.

## 9. Testing and Validation Strategy

*   **Unit Tests:** For individual functions (e.g., feature calculations, config loaders, query generators).
*   **Integration Tests:** For pipeline components (e.g., ETL script with mocked BigQuery).
*   **Data Validation:**
    *   Sanity checks on raw and processed data (e.g., value ranges, non-nulls, expected distributions).
    *   Cross-referencing with Etherscan/Dune Analytics for key metrics.
    *   Great Expectations (future) for automated data quality gates.
*   **Model Validation:**
    *   Cluster evaluation metrics (Silhouette, Davies-Bouldin, etc.).
    *   Cluster stability tests (Jaccard index, Adjusted Rand Index over time).
    *   Qualitative assessment by domain experts/users.
*   **Cost Validation:** Continuous monitoring of BigQuery dry-run estimates and actual costs.

## 10. Risk Management & Mitigation

*   **Risk: BigQuery Cost Overruns**
    *   **Mitigation:** Strict adherence to `CostAwareBigQueryClient`, `PipelineConfig` limits, small data windows in dev, dry-runs, daily cost monitoring.
*   **Risk: Slow Progress on Complex Features (MEV, Value Flows)**
    *   **Mitigation:** Time-box research, start with simplified versions, heavily sample data, defer if initial ROI is low.
*   **Risk: Uninterpretable or Unactionable Clusters**
    *   **Mitigation:** Iterative feature engineering, regular feedback loops with potential users, focus on feature interpretability, start with fewer, simpler features.
*   **Risk: Data Quality Issues in Source Data**
    *   **Mitigation:** Implement data quality checks early, be aware of known limitations of the public dataset, document assumptions.
*   **Risk: Scalability of Pandas Operations**
    *   **Mitigation:** For very large datasets beyond initial phases, consider alternatives like Polars, Dask, or pushing more computation to BigQuery. Start with Pandas for simplicity.

## 11. Documentation and Knowledge Sharing

*   **Code Comments:** Comprehensive comments in all scripts and modules.
*   **READMEs:** In key directories (`scripts/`, `src/qaa_analysis/`) explaining module purpose and usage.
*   **Jupyter Notebooks:** For exploration, prototyping, and documenting analytical steps (`notebooks/`).
*   **This `PLAN.md`:** To be updated regularly as the project evolves.
*   **ADRs (Architecture Decision Records):** For significant architectural choices (to be introduced as needed).
*   **Wiki/Confluence (if applicable):** For design decisions, architectural diagrams, and meeting notes.

## 12. Next Immediate Steps (Post Phase 1 Completion)

1.  **Action:** Begin Phase 2, Task 2.1 (Define Initial Core Features - already done) and Task 2.2 (Implement Feature Engineering Script `src/qaa_analysis/features/basic_features.py`).
2.  **Goal:** Produce a script that takes the daily REV data (output of Phase 1) and aggregates it to create a per-address feature set over the loaded period.

This plan provides a detailed roadmap. Remember that it's a living document and should be revisited and adjusted as you learn more and as project priorities evolve.