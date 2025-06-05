# BigQuery Ethereum Dataset Documentation

Generated: 2025-05-22 16:39:06
Dataset: `bigquery-public-data.crypto_ethereum`
Project: qaa-analysis
Development Mode: True

## Dataset Overview

The Ethereum public dataset contains blockchain data from genesis to near real-time.

### Available Tables

| Table Name | Type | Description |
|------------|------|-------------|
| `blocks` | BASE TABLE | Block headers and metadata |
| `transactions` | BASE TABLE | All Ethereum transactions |
| `logs` | BASE TABLE | Smart contract event logs |
| `traces` | BASE TABLE | Internal transactions and calls |
| `amended_tokens` | VIEW | Corrected token information |
| `balances` | BASE TABLE | Historical address balances |
| `contracts` | BASE TABLE | Contract creation information |
| `load_metadata` | BASE TABLE | Specialized data table |
| `sessions` | BASE TABLE | User session analytics |
| `token_transfers` | BASE TABLE | ERC-20 transfer events |
| `tokens` | BASE TABLE | ERC-20 token metadata |

## Table Schemas

### blocks
  - Warning: Could not fetch extended metadata for table blocks

Contains one row for each block in the blockchain.

**Columns (23 total):**

| Column | Type | Nullable | Description / Comment |
|--------|------|----------|-----------------------|
| `timestamp` *[PARTITION]* | TIMESTAMP | No | N/A |
| `number` | INT64 | No | N/A |
| `hash` | STRING | No | N/A |
| `parent_hash` | STRING | Yes | N/A |
| `nonce` | STRING | No | N/A |
| `sha3_uncles` | STRING | Yes | N/A |
| `logs_bloom` | STRING | Yes | N/A |
| `transactions_root` | STRING | Yes | N/A |
| `state_root` | STRING | Yes | N/A |
| `receipts_root` | STRING | Yes | N/A |
| `miner` | STRING | Yes | N/A |
| `difficulty` | NUMERIC | Yes | N/A |
| `total_difficulty` | NUMERIC | Yes | N/A |
| `size` | INT64 | Yes | N/A |
| `extra_data` | STRING | Yes | N/A |
| `gas_limit` | INT64 | Yes | N/A |
| `gas_used` | INT64 | Yes | N/A |
| `transaction_count` | INT64 | Yes | N/A |
| `base_fee_per_gas` | INT64 | Yes | N/A |
| `withdrawals_root` | STRING | Yes | N/A |
| `withdrawals` | ARRAY<STRUCT<index INT64, validator_index INT64, address STRING, amount STRING>> | No | N/A |
| `blob_gas_used` | INT64 | Yes | N/A |
| `excess_blob_gas` | INT64 | Yes | N/A |

### transactions
  - Warning: Could not fetch extended metadata for table transactions

Contains one row for each transaction. Partitioned by block_timestamp.

**Columns (25 total):**

| Column | Type | Nullable | Description / Comment |
|--------|------|----------|-----------------------|
| `hash` | STRING | No | N/A |
| `nonce` | INT64 | No | N/A |
| `transaction_index` | INT64 | No | N/A |
| `from_address` | STRING | No | N/A |
| `to_address` | STRING | Yes | N/A |
| `value` | NUMERIC | Yes | N/A |
| `gas` | INT64 | Yes | N/A |
| `gas_price` | INT64 | Yes | N/A |
| `input` | STRING | Yes | N/A |
| `receipt_cumulative_gas_used` | INT64 | Yes | N/A |
| `receipt_gas_used` | INT64 | Yes | N/A |
| `receipt_contract_address` | STRING | Yes | N/A |
| `receipt_root` | STRING | Yes | N/A |
| `receipt_status` | INT64 | Yes | N/A |
| `block_timestamp` *[PARTITION]* | TIMESTAMP | No | N/A |
| `block_number` | INT64 | No | N/A |
| `block_hash` | STRING | No | N/A |
| `max_fee_per_gas` | INT64 | Yes | N/A |
| `max_priority_fee_per_gas` | INT64 | Yes | N/A |
| `transaction_type` | INT64 | Yes | N/A |
| `receipt_effective_gas_price` | INT64 | Yes | N/A |
| `max_fee_per_blob_gas` | INT64 | Yes | N/A |
| `blob_versioned_hashes` | ARRAY<STRING> | No | N/A |
| `receipt_blob_gas_price` | INT64 | Yes | N/A |
| `receipt_blob_gas_used` | INT64 | Yes | N/A |

### logs
  - Warning: Could not fetch extended metadata for table logs

Contains event logs emitted by smart contracts.

**Columns (9 total):**

| Column | Type | Nullable | Description / Comment |
|--------|------|----------|-----------------------|
| `log_index` | INT64 | No | N/A |
| `transaction_hash` | STRING | No | N/A |
| `transaction_index` | INT64 | No | N/A |
| `address` | STRING | Yes | N/A |
| `data` | STRING | Yes | N/A |
| `topics` | ARRAY<STRING> | No | N/A |
| `block_timestamp` *[PARTITION]* | TIMESTAMP | No | N/A |
| `block_number` | INT64 | No | N/A |
| `block_hash` | STRING | No | N/A |

### traces
  - Warning: Could not fetch extended metadata for table traces

Contains internal transactions (message calls between addresses).

**Columns (20 total):**

| Column | Type | Nullable | Description / Comment |
|--------|------|----------|-----------------------|
| `transaction_hash` | STRING | Yes | N/A |
| `transaction_index` | INT64 | Yes | N/A |
| `from_address` | STRING | Yes | N/A |
| `to_address` | STRING | Yes | N/A |
| `value` | NUMERIC | Yes | N/A |
| `input` | STRING | Yes | N/A |
| `output` | STRING | Yes | N/A |
| `trace_type` | STRING | No | N/A |
| `call_type` | STRING | Yes | N/A |
| `reward_type` | STRING | Yes | N/A |
| `gas` | INT64 | Yes | N/A |
| `gas_used` | INT64 | Yes | N/A |
| `subtraces` | INT64 | Yes | N/A |
| `trace_address` | STRING | Yes | N/A |
| `error` | STRING | Yes | N/A |
| `status` | INT64 | Yes | N/A |
| `block_timestamp` *[PARTITION]* | TIMESTAMP | No | N/A |
| `block_number` | INT64 | No | N/A |
| `block_hash` | STRING | No | N/A |
| `trace_id` | STRING | Yes | N/A |

### token_transfers
  - Warning: Could not fetch extended metadata for table token_transfers

Contains ERC-20 token transfer events.

**Columns (9 total):**

| Column | Type | Nullable | Description / Comment |
|--------|------|----------|-----------------------|
| `token_address` | STRING | No | N/A |
| `from_address` | STRING | Yes | N/A |
| `to_address` | STRING | Yes | N/A |
| `value` | STRING | Yes | N/A |
| `transaction_hash` | STRING | No | N/A |
| `log_index` | INT64 | No | N/A |
| `block_timestamp` *[PARTITION]* | TIMESTAMP | No | N/A |
| `block_number` | INT64 | No | N/A |
| `block_hash` | STRING | No | N/A |

## Key Relationships

### Primary Keys and Joins

1. **blocks** ↔ **transactions**
   - Join on: `blocks.number = transactions.block_number`
   - Relationship: 1 block → many transactions

2. **transactions** ↔ **logs**
   - Join on: `transactions.hash = logs.transaction_hash`
   - Relationship: 1 transaction → many logs

3. **transactions** ↔ **traces**
   - Join on: `transactions.hash = traces.transaction_hash`
   - Relationship: 1 transaction → many traces

4. **logs** ↔ **token_transfers**
   - Token transfers are decoded from specific log entries
   - Join on: `logs.transaction_hash = token_transfers.transaction_hash`


## Important Fields for Analysis

### Address Analytics
- `transactions.from_address` - Transaction sender
- `transactions.to_address` - Transaction recipient  
- `traces.from_address` - Internal transaction sender
- `traces.to_address` - Internal transaction recipient
- `token_transfers.from_address` - Token sender
- `token_transfers.to_address` - Token recipient

### Value Metrics
- `transactions.value` - ETH transferred (in wei, divide by 1e18 for ETH)
- `transactions.gas_price` - Price per gas unit (in wei)
- `transactions.receipt_gas_used` - Actual gas consumed
- `token_transfers.value` - Token amount transferred

### Time Series
- `blocks.timestamp` - Block creation time
- `transactions.block_timestamp` - Transaction timestamp (partitioned)

### Gas/Fee Calculations
```sql
-- Transaction fee in ETH
(receipt_gas_used * gas_price) / 1e18 as fee_eth

-- Transaction cost in ETH  
(receipt_gas_used * gas_price + value) / 1e18 as total_cost_eth
```


## Efficient Query Patterns

### Cost Optimization Rules

1. **ALWAYS use partition filters:**
   ```sql
   WHERE DATE(block_timestamp) = '2025-05-21'
   -- or
   WHERE DATE(block_timestamp) BETWEEN '2025-05-01' AND '2025-05-07'
   ```

2. **Use approximate functions for statistics:**
   ```sql
   SELECT APPROX_COUNT_DISTINCT(from_address) as unique_addresses
   ```

3. **Limit data scanned with sampling:**
   ```sql
   SELECT * FROM `...transactions`
   WHERE DATE(block_timestamp) = '2025-05-21'
     AND RAND() < 0.001  -- 0.1% sample
   ```

### Example Queries

**Daily Transaction Volume:**
```sql
SELECT
  DATE(block_timestamp) as date,
  COUNT(*) as tx_count,
  SUM(value)/1e18 as total_eth_transferred
FROM `bigquery-public-data.crypto_ethereum.transactions`
WHERE DATE(block_timestamp) >= CURRENT_DATE() - 7
GROUP BY date
ORDER BY date DESC
```

**Top Gas Consumers by Address:**
```sql
SELECT
  from_address,
  COUNT(*) as tx_count,
  SUM(receipt_gas_used) as total_gas,
  SUM(receipt_gas_used * gas_price)/1e18 as total_fees_eth
FROM `bigquery-public-data.crypto_ethereum.transactions`  
WHERE DATE(block_timestamp) = '2025-05-21'
GROUP BY from_address
ORDER BY total_fees_eth DESC
LIMIT 100
```


## Cost Estimates

### Full Table Scan Costs (Approximate)

| Table | Estimated Size | Cost per Full Scan |
|-------|----------------|-------------------|
| blocks | ~2 TB | ~$10 |
| transactions | ~15 TB | ~$75 |
| logs | ~20 TB | ~$100 |
| traces | ~25 TB | ~$125 |
| token_transfers | ~5 TB | ~$25 |

### Cost Reduction Strategies

1. **Date Partitioning**: Reduces cost by 99%+ (scan only needed days)
2. **Column Selection**: Only query needed columns
3. **Aggregation Push-down**: GROUP BY before JOIN
4. **Materialized Views**: Pre-aggregate common queries
5. **BI Engine**: For dashboard/repeated queries


## Dataset Limitations

- **Update Frequency**: Near real-time (few minutes lag)
- **History**: Complete from genesis block (July 30, 2015)
- **Decimals**: Values in wei (1 ETH = 1e18 wei)
- **Missing Data**: Some early blocks may have incomplete traces
- **Token Coverage**: Only includes decoded ERC-20 transfers


## Pipeline Configuration

### Current Settings
- **Project ID**: qaa-analysis
- **Development Mode**: True
- **Max Days Lookback**: 1
- **Sample Rate**: 1.0
- **Max Bytes Billed**: 10,737,418,240 bytes (10.0 GB)
- **Cache TTL**: 24 hours
