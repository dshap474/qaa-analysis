# CHECKLIST.md: On-Chain Behavioral Clustering & Revenue Analysis (Progress Check)

This checklist breaks down the "Advanced Framework for On-Chain Behavioral Clustering and Revenue Analysis in Decentralized Finance" into actionable phases and tasks.

**KEY:**
*   `[x]` - Appears substantially done or well underway based on provided files.
*   `[p]` - Partially done, or a clear foundation/intent is visible.
*   `[ ]` - No clear evidence in the provided files.

## Phase 1: Foundational Setup & Initial Data Extraction (Baseline)

**Objective:** Establish core data pipeline, validate initial contract map, and extract basic interaction data.

### 1.1. Project Initialization & Scope Refinement
- [x] **Define Core Objectives:**
    - [x] Clearly articulate definitions for "Behavior" (interaction patterns, sequential dynamics, financial magnitude, network characteristics). *(Evident in `User-Archetype-Report.md`)*
    - [p] Clearly articulate definitions for "Revenue" (trading profits, MEV, LP fees, lending interest, staking, yield farming, airdrops). Differentiate active vs. passive. *(Initial REV calculation focuses on tx fees. Broader revenue definitions are in the plan but not yet implemented in code.)*
- [x] **Define Scope:**
    - [x] Finalize historical time range for analysis (e.g., last 12-24 months). *(Handled by `PipelineConfig` with `MAX_DAYS_LOOKBACK`)*
    - [x] Confirm initial focus on Ethereum mainnet. *(Implicit throughout, `bigquery-public-data.crypto_ethereum`)*
    - [p] Outline strategy for incorporating `transactions`, `logs`, and `traces` tables. *(Current REV query uses `transactions` and `blocks`. The plan discusses `logs` and `traces` extensively, but code for their broad use in clustering isn't present yet.)*
- [x] **Establish BigQuery Cost Management:**
    - [x] Configure `CostAwareBigQueryClient` with appropriate limits. *(Implemented in `cost_aware_client.py` and `config.py`)*
    - [x] Implement procedures for query cost estimation (dry runs). *(Implemented in `cost_aware_client.py`)*
    - [ ] Set up project/user-level billing alerts in GCP. *(External to codebase, assumed)*
- [x] **Setup Version Control & Project Structure:**
    - [x] Ensure all code, configurations, and maps are in Git. *(Implied by `.gitignore` and project structure)*
    - [x] Organize project directories for data, scripts, notebooks, etc. *(Structure is evident)*

### 1.2. `defi_contract_map.json` - Initial Version & Validation
- [x] **Load Existing `defi_contract_map.json`:** Programmatically parse the current map. *(File exists and is structured for parsing)*
- [p] **Initial Validation:**
    - [p] Cross-reference a sample of existing contract addresses with Etherscan tags. *(`defi_contract_map.json` has "etherscan_verified": "Yes" and "first_block", suggesting some validation)*
    - [p] Cross-reference with external sources (e.g., DeFi Llama, official docs) for a sample. *(`Address-Mapping.md` mentions this methodology)*
- [x] **Define Initial Contract Categories/Sub-categories:** Ensure they are sufficient for Phase 1 analysis. *(`defi_contract_map.json` has a detailed structure)*
- [x] **Document Validation Process & Sources.** *(Present in `Address-Mapping.md`)*

### 1.3. Basic Interaction Data Extraction (BigQuery)
- [x] **Develop Initial SQL Queries:**
    - [x] Query `transactions` table: `from_address` interacting with `to_address` IN (contracts from `defi_contract_map.json`). *(This is the core of the REV query, though not yet generalized for *all* contracts in the map for clustering purposes)*
    - [ ] Query `logs` table: `logs.address` IN (contracts from `defi_contract_map.json`), then join to `transactions` to get `from_address`. *(Planned, but not evident in current core ETL for REV)*
    - [x] Ensure mandatory `block_timestamp` filtering in all queries. *(Implemented in `rev_queries.py`)*
- [x] **Implement Python Script for Query Execution:**
    - [x] Use `CostAwareBigQueryClient`. *(`basic_rev_etl.py` uses it)*
    - [x] Implement caching for query results (`QueryCache`). *(`basic_rev_etl.py` uses it)*
- [p] **Extract Initial Interaction Dataset:**
    - [p] Output: `user_address`, `interacted_contract_address`, `timestamp`, `transaction_hash`, `source_table` (transactions/logs). *(The REV ETL produces `address`, `tx_date`, etc. A more general interaction dataset for clustering is the next step based on the plan.)*
- [x] **Store Extracted Data:** (e.g., Parquet files locally or in cloud storage). *(`basic_rev_etl.py` saves to Parquet)*

### 1.4. Basic Feature Engineering & EDA
- [ ] **Map Interactions to Contract Categories:** Add `contract_group` from `defi_contract_map.json` to the interaction dataset. *(This would be the next step after extracting interactions based on the full map)*
- [p] **Develop Basic Features:**
    - [p] Per `user_address`: Count of interactions with each top-level contract category. *(The REV ETL calculates `tx_count`, `sum_gas_used`, `total_rev_eth` which are features, but not yet counts *per contract category* from the map for clustering.)*
- [p] **Perform Exploratory Data Analysis (EDA):**
    - [p] Analyze distributions of interaction counts. *(`analyze_data.py` notebook script suggests EDA on the REV output)*
    - [ ] Identify initial patterns or anomalies.
- [p] **Document Initial Findings and Feature Definitions.** *(The REV query itself and its metadata function define initial features. `User-Archetype-Report.md` documents findings from a different kind of analysis/research.)*

## Phase 2: Enhanced Core Features & Proxy Contract Handling

**Objective:** Refine contract map, implement robust proxy handling, and develop a richer set of core behavioral features.

### 2.1. `defi_contract_map.json` - Enhancement & Granularity
- [p] **Expand Contract Coverage:**
    - [ ] Research and add more DeFi contract addresses. *(`defi_contract_map.json` is substantial but ongoing)*
    - [ ] Investigate automated discovery methods (APIs, services) to supplement manual curation. *(Mentioned in the plan, not in code)*
- [x] **Increase Granularity:** Refine categories/sub-categories (e.g., "Uniswap V3 Trader"). *(`defi_contract_map.json` shows good granularity)*
- [ ] **Implement Dynamic Update Strategy:** Plan for periodic review and updates to the map. *(Mentioned in `Address-Mapping.md` as future work)*
- [x] **Differentiate Proxy vs. Logic Contracts:** Explicitly mark known proxies and, if possible, their initial/common logic contracts. *(`defi_contract_map.json` has "label_type": "Proxy")*

### 2.2. Proxy Contract Interaction Analysis
- [ ] **Develop Strategy for Proxy Resolution:**
    - [ ] Identify known proxy addresses from the enhanced map.
- [ ] **Implement `traces` Table Queries:**
    - [ ] For transactions to known proxies, query `traces` to find `DELEGATECALL` operations.
    - [ ] Identify the `logic_contract_address` from these traces.
- [ ] **Update Interaction Dataset:**
    - [ ] For interactions via proxies, attribute the interaction to the `logic_contract_address`.
    - [ ] Store both `proxy_address` and `logic_contract_address` if useful.
- [ ] **Handle Logic Contract Upgradability (Initial Consideration):**
    - [ ] Note timestamps of interactions and be aware that logic contracts can change. (Full historical versioning of logic contracts might be Phase 3/4).

### 2.3. Decoding Key Transaction Inputs & Event Logs
- [ ] **Identify Key Function Selectors & Event Signatures:** For common DeFi actions (e.g., `swap`, `deposit`, `borrow`, `Transfer` event). *(`Address-Mapping.md` mentions some common function selectors)*
- [ ] **Implement Basic Decoding:**
    - [ ] For `transactions.input`: Extract function selectors.
    - [ ] For `logs.topics` and `logs.data`: Extract key indexed/non-indexed parameters for pre-identified events.
    - [ ] Decide on initial approach: SQL string manipulation for simple cases, or export for offline Python decoding (e.g., `web3.py`).
- [ ] **Augment Interaction Dataset:** Add columns for decoded information (e.g., `function_called`, `event_emitted`, `token_address_from_event`, `amount_from_event`).

### 2.4. Core Feature Engineering - Augmentation
- [ ] **Develop Sub-Group Interaction Counts:** Based on refined `defi_contract_map.json`.
- [ ] **Develop Gas Usage Features:**
    - [ ] Total gas per user, per contract category.
    - [ ] Average gas per interaction.
- [ ] **Develop Transaction Value-Based Features (Initial):**
    - [ ] Total `msg.value` (ETH sent) to contract categories.
    - [ ] If decoded, sum of token amounts from key events.
- [ ] **Develop Basic Temporal Features:**
    - [ ] Recency of interaction (e.g., days since last activity).
    - [ ] Frequency (e.g., active days in period).
    - [ ] Duration of activity (e.g., time between first and last interaction).
- [ ] **Develop Ratio Features:** (e.g., DEX swap count / lending op count).
- [ ] **Develop Success/Failure Rate Features (Initial):** Based on `transactions.status`.
- [ ] **Develop Risk-Related Features (Initial):** Average gas price paid.

### 2.5. Data Preprocessing (Initial)
- [ ] **Handle Missing Values:** Define strategy (imputation, removal).
- [p] **Address Data Skewness (Initial):** Apply log transformations to highly skewed count/value features. *(The example `etl.py` uses `StandardScaler`, which handles scaling but not directly skewness like log transform)*
- [p] **Feature Scaling (Initial):** Apply Min-Max Scaling or Standardization. *(`StandardScaler` used in `etl.py` example)*

### 2.6. Initial Clustering & Qualitative Validation
- [p] **Select Initial Clustering Algorithm:** (e.g., K-Means as a baseline). *(KMeans used in `etl.py` example)*
- [ ] **Determine Initial `K` (Number of Clusters):** (e.g., using Elbow method, Silhouette scores).
- [p] **Train Initial Clustering Model.** *(Done in `etl.py` example)*
- [ ] **Perform Qualitative Validation:**
    - [ ] Examine cluster centroids/representative points.
    - [ ] Analyze feature distributions per cluster.
    - [ ] Manually inspect sample addresses from each cluster on Etherscan.
    - [ ] Attempt to assign preliminary descriptive names to clusters.

## Phase 3: Advanced Behavioral Feature Engineering & Clustering Refinement

**Objective:** Develop sophisticated features capturing complex behaviors and refine clustering models for better interpretability and robustness.

*(Most items in Phase 3 are future work based on the current codebase state)*
### 3.1. Advanced Temporal Dynamics Features
- [ ] **Interaction Cadence:** (avg time between tx, median inter-tx interval).
- [ ] **Sessionization:** Implement logic to group transactions into sessions; derive session-based features.
- [ ] **Burstiness:** Identify and quantify periods of high activity.
- [ ] **Lifecycle Patterns:** (time since first DeFi tx, adoption speed, dormancy).
- [ ] **Time-Based Attributes:** (hour of day, day of week, proximity to market events).
- [ ] **Seasonality/Trend Decomposition (Optional):** For activity time series.

### 3.2. Graph-Based Features
- [ ] **Construct Interaction Graph (Conceptual or Actual):** Addresses as nodes, interactions as edges.
- [ ] **Basic Graph Metrics:** (degree centrality, weighted degree).
- [ ] **Advanced Graph Metrics (Optional, based on complexity/need):** (Betweenness, Closeness, PageRank).
- [ ] **Ego Network Features:** (neighbor activity, local clustering coefficient).
- [ ] **Node Embeddings (Optional, Advanced):** (Node2Vec, DeepWalk) if simpler graph metrics are insufficient.

### 3.3. Sequential Features
- [ ] **Define "Actions":** (e.g., interaction with contract category, specific function call).
- [ ] **N-grams of Actions:** Identify frequent sequences of N actions.
- [ ] **Sequence Embeddings (Optional, Advanced):** (RNNs, LSTMs) if n-grams are not discriminative enough.

### 3.4. Protocol-Specific Signatures
- [ ] **DEX-Specific Features:** (swap frequency, avg size, token diversity, preferred pairs, stablecoin ratios).
- [ ] **Lending-Specific Features:** (supply/borrow/repay frequency, collateral types, LTV ratios, liquidation history).
- [ ] **Staking-Specific Features:** (amounts, duration, reward claim frequency, LST patterns).
- [ ] **Yield Farming-Specific Features:** (deposit/withdrawal frequency, farm diversity, reward handling).

### 3.5. Advanced Data Preprocessing & Dimensionality Reduction
- [ ] **Refine Skewness Handling:** Experiment with Box-Cox, Yeo-Johnson, Quantile transforms.
- [ ] **Refine Scaling:** Experiment with Robust Scaler if outliers are problematic.
- [ ] **Feature Selection:**
    - [ ] Filter methods (variance threshold, correlation analysis).
    - [ ] Embedded methods (feature importance from tree models if used for supervised sub-tasks or proxy).
- [ ] **Dimensionality Reduction:**
    - [ ] PCA.
    - [ ] t-SNE / UMAP (for visualization and potentially as preprocessing for clustering).
    - [ ] Autoencoders (Optional, Advanced).

### 3.6. Clustering Algorithm Experimentation & Optimization
- [ ] **Experiment with Multiple Algorithms:** (GMM, DBSCAN, Hierarchical, Spectral, Autoencoder-based).
- [ ] **Hyperparameter Tuning:** For each algorithm (grid search, random search using internal validation metrics).
- [ ] **Refined Cluster Validation:**
    - [ ] Rigorous use of Silhouette Score, Calinski-Harabasz, Davies-Bouldin.
    - [ ] If any labeled data available, use Purity, ARI, NMI.
    - [ ] In-depth qualitative profiling and persona development for each stable cluster.
    - [ ] Investigate "dark" or unattributable clusters.

## Phase 4: Revenue Attribution & Integrated Analysis

**Objective:** Quantify DeFi revenue streams for users/clusters and correlate with behavioral patterns.

*(Most items in Phase 4 are future work based on the current codebase state, beyond the initial REV calculation)*
### 4.1. Define and Categorize DeFi Revenue Streams
- [p] **Finalize List of Revenue Categories:** (Trading profits, MEV types, LP fees, Lending interest, Staking rewards, Yield Farming, Airdrops). *(The plan document lists these comprehensively. Current code focuses on tx fee REV.)*
- [ ] **Document On-Chain Markers for Each Revenue Stream.**

### 4.2. Develop Revenue Attribution Models
- [ ] **Trading P/L Model:**
    - [ ] Track buy/sell events (from decoded swaps).
    - [ ] Implement cost basis calculation (e.g., FIFO).
    - [ ] Account for gas fees.
    - [ ] Requires reliable price feeds for tokens at transaction time.
- [ ] **LP Fee Attribution Model:**
    - [ ] Uniswap V2: Track `Mint`/`Burn` events, estimate value changes (consider impermanent loss).
    - [ ] Uniswap V3: Track `Collect` events from `NonfungiblePositionManager`.
- [ ] **Lending Interest & Reward Token Model:**
    - [ ] Interest: Track changes in aToken/cToken balances (from `Transfer` events).
    - [ ] Rewards: Identify and decode `ClaimReward` (or similar) events from incentive controllers.
- [ ] **Staking Rewards Model:**
    - [ ] ETH Staking (Consensus Layer): Query `beacon_*` tables for validator rewards.
    - [ ] ETH Staking (Execution Layer): Attribute priority fees/MEV to proposers.
    - [ ] Liquid Staking: Analyze LST balance changes/rebases or withdrawal values.
- [ ] **Yield Farming Rewards Model:** Identify and decode `ClaimReward`/`Harvest` events from various farm contracts.
- [ ] **MEV Profit Quantification (Ambitious, Iterative):**
    *   **Arbitrage:**
        *   [ ] Develop logic to detect multi-leg swaps by the same EOA across different DEXs in short timeframes.
        *   [ ] Calculate net profit after gas.
    *   **Liquidations:**
        *   [ ] Identify calls to `liquidate` functions.
        *   [ ] Calculate liquidator's profit (collateral bonus - debt repaid - gas).
    *   **Sandwich Attacks (Highly Advanced):**
        *   [ ] Research and attempt to implement pattern detection for front-run -> victim -> back-run sequences.
        *   [ ] Estimate attacker's profit.
    *   **MEV Payments to Builders/Proposers:** Analyze `traces` for direct payments (e.g., `coinbase.transfer()`).

### 4.3. Attribute Revenue to Users and Clusters
- [ ] **Calculate Revenue Metrics per User:** For each identified revenue stream.
- [ ] **Aggregate Revenue Data at Cluster Level:** (total revenue, average revenue per user, distribution of revenue sources within each cluster).

### 4.4. Integrated Analysis: Correlating Behavior with Revenue
- [ ] **Identify Dominant Revenue Streams per Cluster.**
- [ ] **Relate Revenue Streams to Defining Behavioral Features of Clusters.**
- [ ] **Interpret User Archetypes:** Based on both behavior and how they generate/capture value.
- [ ] **Differentiate Extractive vs. Generative Clusters (if possible).**
- [ ] **Document Key Insights and Findings.**

## Phase 5: Operationalization, Monitoring, & Ethics

**Objective:** Ensure long-term viability, relevance, and ethical conduct of the analysis.

### 5.1. System Adaptability & Maintenance
- [ ] **Monitor for Smart Contract Upgrades:** Track changes to logic contracts for key proxies.
- [p] **Update `defi_contract_map.json` Periodically:** Incorporate new protocols and contract changes. *(Intent stated in docs)*
- [ ] **Plan for Model Retraining/Recalibration:** Address concept drift in behaviors and features.
- [ ] **Monitor Cluster Stability Over Time.**
- [ ] **Monitor Feature Distributions for Drift.**
- [ ] **Establish Feedback Loops:** Insights from revenue analysis to refine features/clustering.

### 5.2. Ethical Framework Implementation & Adherence
- [p] **Formalize Ethical Guidelines for the Project:**
    - [p] Data minimization principles. *(Implicit by focusing queries)*
    - [p] Purpose limitation. *(Implicit by project goals)*
    - [ ] Strategies to mitigate deanonymization risks.
- [p] **Responsible Reporting Strategy:**
    - [ ] Focus on aggregate insights.
    - [ ] Avoid highlighting individual pseudonymous addresses unless ethically justified and for aggregate analysis of known public actors.
    - [ ] Clearly state limitations and probabilistic nature of findings.
- [ ] **Review for Algorithmic Bias:** In feature engineering and clustering.
- [p] **Ensure Transparency of Methodology in all outputs.** *(Good documentation so far)*
- [ ] **Conduct Internal Ethical Review (or seek external advice if needed).**

### 5.3. Documentation & Knowledge Sharing
- [x] **Maintain Comprehensive Documentation:** For data sources, feature definitions, model parameters, validation results, and revenue attribution logic. *(Excellent start with `User-Archetype-Report.md`, `Address-Mapping.md`, `GCP_DATABASE_SCHEMA.md`, READMEs)*
- [ ] **Document All Iterations and Key Decisions Made.**
- [ ] **Consider (with extreme prudence) community contributions if ethically sound and aligned with goals.**

### 5.4. Final Reporting & Dissemination
- [ ] **Prepare Final Report/Presentation of Findings.**
- [ ] **Outline Limitations and Areas for Future Research.**

---