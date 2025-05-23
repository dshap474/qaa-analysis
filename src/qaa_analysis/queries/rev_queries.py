"""
Revenue (REV) query generation for QAA Analysis.

This module provides SQL query generators for calculating Blockworks-style
revenue metrics from Ethereum transaction data, including total fees,
priority fees (tips), and burned base fees per address per day.
"""

from typing import Tuple


def get_blockworks_rev_query(
    start_date_iso: str, end_date_iso: str, sample_rate: float = 1.0
) -> str:
    """
    Generates a BigQuery SQL query to calculate basic Blockworks-style REV metrics.

    The query calculates total fees, priority fees (tips), and burned base fees
    per address per day, based on transaction data joined with block data to access
    base_fee_per_gas. It incorporates date-based partition pruning and optional
    sampling for cost control.

    Args:
        start_date_iso: The start date for the query window (ISO format "YYYY-MM-DD").
        end_date_iso: The end date for the query window (ISO format "YYYY-MM-DD").
        sample_rate: A float between 0.0 and 1.0 for table sampling.
                     If 1.0, no sampling clause is added.

    Returns:
        A string containing the formatted SQL query that JOINs transactions
        and blocks tables.

    Raises:
        ValueError: If sample_rate is not between 0.0 and 1.0.

    Example:
        >>> query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 0.1)
        >>> print(query[:100])  # First 100 characters
    """
    # Validate sample_rate
    if not 0.0 <= sample_rate <= 1.0:
        raise ValueError(f"sample_rate must be between 0.0 and 1.0, got {sample_rate}")

    # Build the WHERE clause with date filter
    where_conditions = [
        f"DATE(t.block_timestamp) BETWEEN '{start_date_iso}' AND '{end_date_iso}'"
    ]

    # Add sampling condition if sample_rate < 1.0
    if sample_rate < 1.0 and sample_rate > 0.0:
        where_conditions.append(f"RAND() < {sample_rate}")

    where_clause = " AND ".join(where_conditions)

    # Construct the complete SQL query
    query = f"""
WITH source_transactions_with_block_fees AS (
  SELECT
    t.from_address,
    t.receipt_gas_used,
    t.gas_price,
    b.base_fee_per_gas AS block_base_fee_per_gas,
    t.block_timestamp
  FROM `bigquery-public-data.crypto_ethereum.transactions` AS t
  INNER JOIN `bigquery-public-data.crypto_ethereum.blocks` AS b
    ON t.block_number = b.number
  WHERE {where_clause}
),

rev_components AS (
  SELECT
    from_address AS address,
    DATE(block_timestamp) AS tx_date,
    receipt_gas_used,
    -- Total transaction fee in ETH
    (receipt_gas_used * gas_price) / 1e18 AS total_transaction_fee_eth,
    -- Priority fee (tip) in ETH - handles pre-EIP-1559 transactions
    ((gas_price - COALESCE(block_base_fee_per_gas, 0)) * receipt_gas_used) / 1e18 AS priority_fee_eth,
    -- Base fee burned in ETH - zero for pre-EIP-1559 transactions
    (COALESCE(block_base_fee_per_gas, 0) * receipt_gas_used) / 1e18 AS base_fee_burned_eth
  FROM source_transactions_with_block_fees
)

SELECT
  address,
  tx_date,
  COUNT(*) AS tx_count,
  SUM(receipt_gas_used) AS sum_gas_used,
  SUM(total_transaction_fee_eth) AS total_rev_eth,
  SUM(priority_fee_eth) AS tips_rev_eth,
  SUM(base_fee_burned_eth) AS burned_rev_eth,
  AVG(total_transaction_fee_eth) AS avg_tx_fee_eth
FROM rev_components
GROUP BY address, tx_date
ORDER BY tx_date DESC, total_rev_eth DESC
"""

    return query.strip()


def validate_date_format(date_iso: str) -> bool:
    """
    Validate that a date string is in ISO format (YYYY-MM-DD).

    Args:
        date_iso: Date string to validate.

    Returns:
        True if valid ISO format, False otherwise.
    """
    try:
        from datetime import datetime
        import re

        # First check if it matches the exact pattern YYYY-MM-DD
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_iso):
            return False

        # Then validate it's a real date
        datetime.strptime(date_iso, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def get_rev_query_metadata(
    start_date_iso: str, end_date_iso: str, sample_rate: float = 1.0
) -> dict:
    """
    Get metadata about a REV query without generating the full SQL.

    Args:
        start_date_iso: The start date for the query window.
        end_date_iso: The end date for the query window.
        sample_rate: Sampling rate for the query.

    Returns:
        Dictionary containing query metadata.
    """
    from datetime import datetime

    # Validate dates
    if not validate_date_format(start_date_iso):
        raise ValueError(f"Invalid start_date_iso format: {start_date_iso}")
    if not validate_date_format(end_date_iso):
        raise ValueError(f"Invalid end_date_iso format: {end_date_iso}")

    # Calculate date range
    start_date = datetime.strptime(start_date_iso, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_iso, "%Y-%m-%d").date()
    days_span = (end_date - start_date).days + 1

    return {
        "query_type": "blockworks_rev",
        "start_date": start_date_iso,
        "end_date": end_date_iso,
        "days_span": days_span,
        "sample_rate": sample_rate,
        "is_sampled": sample_rate < 1.0,
        "target_tables": [
            "bigquery-public-data.crypto_ethereum.transactions",
            "bigquery-public-data.crypto_ethereum.blocks",
        ],
        "estimated_complexity": "medium" if days_span <= 7 else "high",
    }
