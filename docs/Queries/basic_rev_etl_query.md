BIGQUERY_MAX_BYTES_BILLED not set, defaulting to 10,737,418,240 bytes
2025-05-30 12:23:52 - INFO - basic_rev_etl - ============================================================
2025-05-30 12:23:52 - INFO - basic_rev_etl - Starting Basic REV ETL Process
2025-05-30 12:23:52 - INFO - basic_rev_etl - ============================================================
2025-05-30 12:23:52 - INFO - basic_rev_etl - Initializing core modules...
2025-05-30 12:23:52 - WARNING - config - BIGQUERY_MAX_BYTES_BILLED not set, defaulting to 10,737,418,240 bytes
2025-05-30 12:23:52 - INFO - config - Cache directory: C:\Users\dansh\Documents\Job\Blockworks\projects\qaa-analysis\data\cache
2025-05-30 12:23:52 - INFO - config - Processed data directory: C:\Users\dansh\Documents\Job\Blockworks\projects\qaa-analysis\data\processed
2025-05-30 12:23:52 - INFO - config - Pipeline configuration initialized - DEV_MODE: True      
2025-05-30 12:23:54 - INFO - cost_aware_client - BigQuery client initialized for project: qaa-analysis
2025-05-30 12:23:54 - INFO - query_cache - Query cache initialized: C:\Users\dansh\Documents\Job\Blockworks\projects\qaa-analysis\data\cache (TTL: 24 hours)
2025-05-30 12:23:54 - INFO - basic_rev_etl - Configuration loaded - DEV_MODE: True, Lookback: 1 days, Sample Rate: 100.0%
2025-05-30 12:23:54 - INFO - basic_rev_etl - Determining query parameters...
2025-05-30 12:23:54 - INFO - basic_rev_etl - Query window: 2025-05-29 to 2025-05-29 (sample rate: 100.0%)
2025-05-30 12:23:54 - INFO - basic_rev_etl - Generating SQL query...
2025-05-30 12:23:54 - INFO - basic_rev_etl - Query generated - Type: blockworks_rev, Days: 1, Complexity: medium
2025-05-30 12:23:54 - INFO - basic_rev_etl - Fetching data via cache system...
2025-05-30 12:23:54 - INFO - query_cache - Cache miss for: query_ed8b8680c81619c9.parquet      
2025-05-30 12:23:54 - INFO - query_cache - Computing new result...
2025-05-30 12:23:54 - INFO - basic_rev_etl - Attempting to fetch data from BigQuery...
2025-05-30 12:23:57 - INFO - cost_aware_client - Query cost estimate: 364,281,592 bytes ($0.0021 USD)
2025-05-30 12:23:57 - INFO - cost_aware_client - Proceeding with query execution ($0.0021 USD estimated cost)
2025-05-30 12:24:17 - INFO - cost_aware_client - Query completed successfully. Actual usage: 364,904,448 bytes ($0.0021 USD), Rows returned: 427,738
2025-05-30 12:24:17 - INFO - basic_rev_etl - Successfully fetched 427,738 rows from BigQuery   
2025-05-30 12:24:17 - INFO - basic_rev_etl - Total revenue in dataset: 743.006399 ETH
2025-05-30 12:24:18 - INFO - query_cache - Result cached: query_ed8b8680c81619c9.parquet (427,738 rows, 29.1 MB)
2025-05-30 12:24:18 - INFO - basic_rev_etl - Data validation: DataFrame validation passed - 427,738 rows, 8 columns
2025-05-30 12:24:18 - INFO - basic_rev_etl - Storing processed data...
2025-05-30 12:24:18 - INFO - basic_rev_etl - Data storage: Successfully saved to C:\Users\dansh\Documents\Job\Blockworks\projects\qaa-analysis\data\processed\basic_rev_daily_data_20250529_to_20250529_sample100.parquet (29.10 MB, 427,738 rows)
2025-05-30 12:24:18 - INFO - basic_rev_etl - Data successfully stored at: C:\Users\dansh\Documents\Job\Blockworks\projects\qaa-analysis\data\processed\basic_rev_daily_data_20250529_to_20250529_sample100.parquet
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total rows processed: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Date range: 2025-05-29 to 2025-05-29
2025-05-30 12:24:18 - INFO - basic_rev_etl - Unique addresses: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total transactions: 1,400,670
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total revenue: 743.006399 ETH
2025-05-30 12:24:18 - INFO - basic_rev_etl - Average daily revenue per address: 0.001737 ETH   
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ============================================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Basic REV ETL process completed successfully      
2025-05-30 12:24:18 - INFO - basic_rev_etl - ============================================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total rows processed: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Date range: 2025-05-29 to 2025-05-29
2025-05-30 12:24:18 - INFO - basic_rev_etl - Unique addresses: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total transactions: 1,400,670
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total revenue: 743.006399 ETH
2025-05-30 12:24:18 - INFO - basic_rev_etl - Average daily revenue per address: 0.001737 ETH   
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ============================================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total rows processed: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Date range: 2025-05-29 to 2025-05-29
2025-05-30 12:24:18 - INFO - basic_rev_etl - Unique addresses: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total transactions: 1,400,670
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total revenue: 743.006399 ETH
2025-05-30 12:24:18 - INFO - basic_rev_etl - Average daily revenue per address: 0.001737 ETH   
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total rows processed: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Date range: 2025-05-29 to 2025-05-29
2025-05-30 12:24:18 - INFO - basic_rev_etl - Unique addresses: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total rows processed: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ETL SUMMARY STATISTICS
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total rows processed: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Date range: 2025-05-29 to 2025-05-29
2025-05-30 12:24:18 - INFO - basic_rev_etl - Unique addresses: 427,738
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total transactions: 1,400,670
2025-05-30 12:24:18 - INFO - basic_rev_etl - Total revenue: 743.006399 ETH
2025-05-30 12:24:18 - INFO - basic_rev_etl - Average daily revenue per address: 0.001737 ETH   
2025-05-30 12:24:18 - INFO - basic_rev_etl - ========================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - ============================================================
2025-05-30 12:24:18 - INFO - basic_rev_etl - Basic REV ETL process completed successfully      
2025-05-30 12:24:18 - INFO - basic_rev_etl - ============================================================