# REV (Real Economic Value) Calculation Specification

## Definition
REV represents the total transaction fees paid by users for on-chain execution, measuring the monetary demand for blockspace.

## Exact Calculation from GCP BigQuery Tables

### Data Sources
- **Primary Table**: `bigquery-public-data.crypto_ethereum.transactions`
- **Secondary Table**: `bigquery-public-data.crypto_ethereum.blocks` (for EIP-1559 base fee)

### Column Mappings

#### From `transactions` table:
- `from_address`: The user (fee payer)
- `receipt_gas_used`: Actual gas consumed (NOT `gas` which is the limit)
- `gas_price`: Total price per gas unit in Wei
- `block_number`: For joining with blocks table
- `block_timestamp`: Transaction timestamp

#### From `blocks` table:
- `base_fee_per_gas`: Base fee per gas (available after block 12,965,000)

### REV Calculation Formula

```sql
-- Per Transaction REV (in Wei)
REV_wei = receipt_gas_used * gas_price

-- Per Transaction REV (in ETH)
REV_eth = (receipt_gas_used * gas_price) / 1e18

-- Components breakdown (post-EIP-1559):
base_fee_wei = receipt_gas_used * base_fee_per_gas
priority_fee_wei = receipt_gas_used * (gas_price - base_fee_per_gas)

-- Where:
-- base_fee_wei gets burned (destroyed)
-- priority_fee_wei goes to validators
```

### SQL Implementation

```sql
-- Core REV calculation per user per day
SELECT
    from_address as user,
    DATE(block_timestamp) as date,
    -- Total REV in ETH
    SUM(CAST(receipt_gas_used AS NUMERIC) * CAST(gas_price AS NUMERIC)) / 1e18 as total_rev_eth,
    -- Transaction count
    COUNT(*) as tx_count,
    -- Average REV per transaction
    AVG(CAST(receipt_gas_used AS NUMERIC) * CAST(gas_price AS NUMERIC)) / 1e18 as avg_rev_per_tx_eth
FROM `bigquery-public-data.crypto_ethereum.transactions`
WHERE 
    DATE(block_timestamp) = '2025-06-05'
    AND receipt_status = 1  -- Only successful transactions
GROUP BY user, date
```

### Important Calculation Details

1. **Use `receipt_gas_used`, NOT `gas`**
   - `gas` = gas limit (maximum willing to pay)
   - `receipt_gas_used` = actual gas consumed
   - REV must use actual consumption

2. **Wei to ETH Conversion**
   - Always divide by 1e18 (10^18)
   - 1 ETH = 1,000,000,000,000,000,000 Wei

3. **Transaction Status**
   - Include only `receipt_status = 1` (successful transactions)
   - Failed transactions (`receipt_status = 0`) still consume gas but we exclude them for user analysis
   - Decision: We focus on successful transaction patterns

4. **EIP-1559 Considerations**
   - Before block 12,965,000: All fees went to miners
   - After block 12,965,000: Base fee burned, priority fee to validators
   - For total REV: Use `gas_price` (includes both components)

5. **Data Type Casting**
   - Cast to NUMERIC to handle large numbers
   - Prevents integer overflow in calculations

### Aggregation Levels

1. **Per Transaction**: `receipt_gas_used * gas_price / 1e18`
2. **Per User Per Day**: `SUM(receipt_gas_used * gas_price) / 1e18`
3. **Per User Total**: Sum across all days
4. **Per Cluster**: Aggregate user-level REV by cluster assignment

### Validation Checks

- REV should always be positive (gas_price and gas_used are always > 0)
- Daily REV typically ranges from 0.0001 to 10+ ETH per active user
- If REV = 0, user had no transactions that day
- Total REV should match network-wide fee statistics