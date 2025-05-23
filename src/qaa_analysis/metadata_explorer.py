"""
BigQuery Ethereum Dataset Metadata Explorer

Explores table schemas and metadata with minimal cost.
Creates a comprehensive markdown report with robust error handling
and enhanced metadata collection.

This script fixes the schema fetching error by properly handling
the absence of description fields in INFORMATION_SCHEMA.COLUMNS
and adds table-level metadata for better documentation.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from qaa_analysis.config import PipelineConfig

# Initialize configuration and client
config = PipelineConfig()
client = bigquery.Client(project=config.PROJECT_ID)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output container
output: List[str] = []


def log(message: str) -> None:
    """
    Log message to console and output buffer.

    Args:
        message: The message to log
    """
    print(message)
    output.append(message)


def fetch_table_metadata(table_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch table-level metadata from INFORMATION_SCHEMA.TABLES.

    Args:
        table_name: Name of the table to fetch metadata for

    Returns:
        Dictionary containing table metadata or None if fetch fails
    """
    table_meta_query = f"""
    SELECT 
        table_name,
        creation_time,
        last_modified_time,
        row_count,
        size_bytes,
        table_type
    FROM `bigquery-public-data.crypto_ethereum.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = '{table_name}'
    """

    try:
        logger.info(f"Fetching table metadata for {table_name}...")
        table_meta_results = list(client.query(table_meta_query).result())

        if table_meta_results:
            meta = table_meta_results[0]
            return {
                "table_name": meta.table_name,
                "creation_time": meta.creation_time,
                "last_modified_time": meta.last_modified_time,
                "row_count": meta.row_count,
                "size_bytes": meta.size_bytes,
                "table_type": meta.table_type,
            }
        else:
            logger.warning(f"No metadata found for table {table_name}")
            return None

    except Exception as e:
        logger.error(f"Failed to fetch table metadata for {table_name}: {e}")
        return None


def fetch_table_schema(table_name: str) -> Optional[List[Any]]:
    """
    Fetch table schema with fallback for comment fields.

    Attempts to fetch column comments first, falls back to basic schema
    if comment fields are not available.

    Args:
        table_name: Name of the table to fetch schema for

    Returns:
        List of column information or None if fetch fails
    """
    base_schema_fields = """
        ordinal_position,
        column_name,
        data_type,
        is_nullable,
        is_partitioning_column,
        clustering_ordinal_position
    """

    # Try different possible comment field names
    comment_field_attempts = ["description", "column_comment", "comment"]

    for comment_field in comment_field_attempts:
        schema_query_with_comment = f"""
        SELECT 
            {base_schema_fields},
            {comment_field} AS retrieved_comment
        FROM `bigquery-public-data.crypto_ethereum.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """

        try:
            logger.info(
                f"Attempting to fetch schema with '{comment_field}' field for {table_name}..."
            )
            columns = list(client.query(schema_query_with_comment).result())
            logger.info(f"Successfully fetched schema with '{comment_field}' field")
            return columns

        except Exception as e:
            logger.debug(f"Failed to fetch schema with '{comment_field}' field: {e}")
            continue

    # Fallback: fetch schema without comment field
    schema_query_no_comment = f"""
    SELECT 
        {base_schema_fields},
        NULL AS retrieved_comment
    FROM `bigquery-public-data.crypto_ethereum.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """

    try:
        logger.info(f"Fetching basic schema without comments for {table_name}...")
        columns = list(client.query(schema_query_no_comment).result())
        logger.info(f"Successfully fetched basic schema")
        return columns

    except Exception as e:
        logger.error(f"Failed to fetch basic schema for {table_name}: {e}")
        return None


def format_table_metadata(metadata: Dict[str, Any]) -> None:
    """
    Format and log table metadata information.

    Args:
        metadata: Dictionary containing table metadata
    """
    if metadata["last_modified_time"]:
        last_modified = metadata["last_modified_time"].strftime("%Y-%m-%d %H:%M:%S UTC")
        log(f"  - **Last Modified:** {last_modified}")

    if metadata["row_count"] is not None:
        log(f"  - **Row Count:** {metadata['row_count']:,}")

    if metadata["size_bytes"] is not None:
        size_gb = metadata["size_bytes"] / (1024**3)
        log(f"  - **Size:** {size_gb:.2f} GB")

    if metadata["table_type"]:
        log(f"  - **Type:** {metadata['table_type']}")


def format_column_schema(columns: List[Any]) -> None:
    """
    Format and log column schema information.

    Args:
        columns: List of column information from BigQuery
    """
    log(f"\n**Columns ({len(columns)} total):**\n")
    log("| Column | Type | Nullable | Description / Comment |")
    log("|--------|------|----------|-----------------------|")

    for col in columns:
        nullable = "Yes" if col.is_nullable == "YES" else "No"

        # Safely get the comment field
        comment_str = getattr(col, "retrieved_comment", None) or "N/A"

        # Truncate long comments
        if len(comment_str) > 80:
            comment_str = comment_str[:77] + "..."

        # Add partitioning/clustering info
        special = []
        if col.is_partitioning_column == "YES":
            special.append("PARTITION")
        if col.clustering_ordinal_position:
            special.append(f"CLUSTER-{col.clustering_ordinal_position}")

        special_str = f" *[{', '.join(special)}]*" if special else ""

        log(
            f"| `{col.column_name}`{special_str} | {col.data_type} | {nullable} | {comment_str} |"
        )


# ------------------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------------------
log("# BigQuery Ethereum Dataset Documentation")
log(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log(f"Dataset: `bigquery-public-data.crypto_ethereum`")
log(f"Project: {config.PROJECT_ID}")
log(f"Development Mode: {config.DEV_MODE}")

# ------------------------------------------------------------------------------
# TABLE OVERVIEW
# ------------------------------------------------------------------------------
log("\n## Dataset Overview")
log(
    "\nThe Ethereum public dataset contains blockchain data from genesis to near real-time."
)

# Get all tables
tables_query = """
SELECT 
    table_name,
    table_type,
    IFNULL(ddl, 'No DDL available') as ddl
FROM `bigquery-public-data.crypto_ethereum.INFORMATION_SCHEMA.TABLES`
ORDER BY 
    CASE 
        WHEN table_name = 'blocks' THEN 1
        WHEN table_name = 'transactions' THEN 2
        WHEN table_name = 'logs' THEN 3
        WHEN table_name = 'traces' THEN 4
        ELSE 5
    END,
    table_name
"""

try:
    logger.info("Fetching table list...")
    tables = list(client.query(tables_query).result())

    log("\n### Available Tables\n")
    log("| Table Name | Type | Description |")
    log("|------------|------|-------------|")

    table_descriptions = {
        "blocks": "Block headers and metadata",
        "transactions": "All Ethereum transactions",
        "logs": "Smart contract event logs",
        "traces": "Internal transactions and calls",
        "contracts": "Contract creation information",
        "tokens": "ERC-20 token metadata",
        "token_transfers": "ERC-20 transfer events",
        "balances": "Historical address balances",
        "sessions": "User session analytics",
        "amended_tokens": "Corrected token information",
    }

    for table in tables:
        desc = table_descriptions.get(table.table_name, "Specialized data table")
        log(f"| `{table.table_name}` | {table.table_type} | {desc} |")

    logger.info(f"Successfully fetched {len(tables)} tables")

except Exception as e:
    logger.error(f"Error fetching tables: {e}")
    log(f"\nError fetching tables: {e}")

# ------------------------------------------------------------------------------
# DETAILED SCHEMAS
# ------------------------------------------------------------------------------
log("\n## Table Schemas")

# Define key tables to document
key_tables = ["blocks", "transactions", "logs", "traces", "token_transfers"]

for table_name in key_tables:
    log(f"\n### {table_name}")

    # Fetch table-level metadata
    metadata = fetch_table_metadata(table_name)
    if metadata:
        format_table_metadata(metadata)
    else:
        log(f"  - Warning: Could not fetch extended metadata for table {table_name}")

    # Fetch column schema
    columns = fetch_table_schema(table_name)

    if columns:
        # Table description
        table_descriptions = {
            "blocks": "\nContains one row for each block in the blockchain.",
            "transactions": "\nContains one row for each transaction. Partitioned by block_timestamp.",
            "logs": "\nContains event logs emitted by smart contracts.",
            "traces": "\nContains internal transactions (message calls between addresses).",
            "token_transfers": "\nContains ERC-20 token transfer events.",
        }

        if table_name in table_descriptions:
            log(table_descriptions[table_name])

        format_column_schema(columns)

    else:
        log(f"\n  - Error: Could not fetch schema for table {table_name}")

# ------------------------------------------------------------------------------
# KEY RELATIONSHIPS
# ------------------------------------------------------------------------------
log("\n## Key Relationships")

log(
    """
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
"""
)

# ------------------------------------------------------------------------------
# IMPORTANT FIELDS
# ------------------------------------------------------------------------------
log("\n## Important Fields for Analysis")

log(
    """
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
"""
)

# ------------------------------------------------------------------------------
# QUERY PATTERNS
# ------------------------------------------------------------------------------
log("\n## Efficient Query Patterns")

log(
    """
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
"""
)

# ------------------------------------------------------------------------------
# COST ESTIMATES
# ------------------------------------------------------------------------------
log("\n## Cost Estimates")

log(
    """
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
"""
)

# ------------------------------------------------------------------------------
# LIMITATIONS
# ------------------------------------------------------------------------------
log("\n## Dataset Limitations")

log(
    """
- **Update Frequency**: Near real-time (few minutes lag)
- **History**: Complete from genesis block (July 30, 2015)
- **Decimals**: Values in wei (1 ETH = 1e18 wei)
- **Missing Data**: Some early blocks may have incomplete traces
- **Token Coverage**: Only includes decoded ERC-20 transfers
"""
)

# ------------------------------------------------------------------------------
# CONFIGURATION INFO
# ------------------------------------------------------------------------------
log("\n## Pipeline Configuration")

log(
    f"""
### Current Settings
- **Project ID**: {config.PROJECT_ID}
- **Development Mode**: {config.DEV_MODE}
- **Max Days Lookback**: {config.MAX_DAYS_LOOKBACK}
- **Sample Rate**: {config.SAMPLE_RATE}
- **Max Bytes Billed**: {config.MAX_BYTES_BILLED:,} bytes ({config.MAX_BYTES_BILLED / (1024**3):.1f} GB)
- **Cache TTL**: {config.CACHE_TTL_HOURS} hours
"""
)

# Save to file
output_file = "ethereum_dataset_documentation.md"
try:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    logger.info(f"Documentation saved to {output_file}")
    log(f"\n✓ Documentation saved to {output_file}")
    log("\nTotal cost: < $0.001 (metadata queries only)")

except Exception as e:
    logger.error(f"Failed to save documentation: {e}")
    log(f"\n✗ Failed to save documentation: {e}")
