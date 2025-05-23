"""
Example usage of the core QAA Analysis modules.

This script demonstrates how to use PipelineConfig, CostAwareBigQueryClient,
and QueryCache together for cost-controlled BigQuery operations with caching.
"""

import logging
from typing import Optional

import pandas as pd

from qaa_analysis.cache.query_cache import QueryCache
from qaa_analysis.config import PipelineConfig
from qaa_analysis.etl.cost_aware_client import CostAwareBigQueryClient, QueryCostError


def setup_logging() -> None:
    """Configure logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def example_basic_usage() -> None:
    """Demonstrate basic usage of all three modules."""
    print("=== Basic Usage Example ===")

    # Initialize configuration
    config = PipelineConfig()
    print(f"Configuration: {config}")

    # Initialize BigQuery client with cost controls
    bq_client = CostAwareBigQueryClient(config)
    print(f"BigQuery client: {bq_client}")

    # Initialize query cache
    cache = QueryCache(config)
    print(f"Query cache: {cache}")

    # Get date filter for queries
    start_date, end_date = config.get_date_filter()
    print(f"Date range: {start_date} to {end_date}")


def example_cached_query() -> Optional[pd.DataFrame]:
    """Demonstrate cached BigQuery execution."""
    print("\n=== Cached Query Example ===")

    # Initialize components
    config = PipelineConfig()
    bq_client = CostAwareBigQueryClient(config)
    cache = QueryCache(config)

    # Example query (replace with your actual query)
    query = """
    SELECT 
        DATE(block_timestamp) as date,
        COUNT(*) as transaction_count,
        COUNT(DISTINCT from_address) as unique_senders
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE DATE(block_timestamp) BETWEEN @start_date AND @end_date
    GROUP BY date
    ORDER BY date
    """

    # Get date parameters
    start_date, end_date = config.get_date_filter(days_back=7)
    query_params = {"start_date": start_date, "end_date": end_date}

    try:
        # Define compute function for cache
        def fetch_ethereum_data() -> pd.DataFrame:
            # Replace parameters in query (in real usage, use parameterized queries)
            formatted_query = query.replace("@start_date", f"'{start_date}'")
            formatted_query = formatted_query.replace("@end_date", f"'{end_date}'")

            return bq_client.safe_query(formatted_query)

        # Get data with caching
        print("Fetching Ethereum transaction data...")
        df = cache.get_or_compute(
            query=query, compute_fn=fetch_ethereum_data, params=query_params
        )

        if df is not None and not df.empty:
            print(f"Retrieved {len(df)} rows of data")
            print("\nSample data:")
            print(df.head())
            return df
        else:
            print("No data returned")
            return None

    except QueryCostError as e:
        print(f"Query blocked due to cost limits: {e}")
        return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None


def example_cost_estimation() -> None:
    """Demonstrate query cost estimation."""
    print("\n=== Cost Estimation Example ===")

    config = PipelineConfig()
    bq_client = CostAwareBigQueryClient(config)

    # Example queries with different costs
    queries = [
        "SELECT COUNT(*) FROM `bigquery-public-data.crypto_ethereum.transactions` LIMIT 1000",
        "SELECT * FROM `bigquery-public-data.crypto_ethereum.transactions` WHERE DATE(block_timestamp) = '2024-01-01'",
        "SELECT * FROM `bigquery-public-data.crypto_ethereum.transactions`",  # This would be expensive
    ]

    for i, query in enumerate(queries, 1):
        try:
            print(f"\nQuery {i} cost estimation:")
            bytes_estimate, cost_estimate = bq_client.estimate_query_cost(query)

            print(f"  Estimated bytes: {bytes_estimate:,}")
            print(f"  Estimated cost: ${cost_estimate:.4f}")
            print(f"  Within limits: {bytes_estimate <= config.MAX_BYTES_BILLED}")

        except Exception as e:
            print(f"  Error estimating cost: {e}")


def example_cache_management() -> None:
    """Demonstrate cache management operations."""
    print("\n=== Cache Management Example ===")

    config = PipelineConfig()
    cache = QueryCache(config)

    # Get cache statistics
    stats = cache.get_cache_stats()
    print(f"Cache statistics: {stats}")

    if stats["file_count"] > 0:
        print(f"Cache contains {stats['file_count']} files")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        print(f"Oldest file: {stats['oldest_file_hours']:.1f} hours old")
        print(f"Expired files: {stats['expired_files']}")

        # Optionally clear expired cache
        if stats["expired_files"] > 0:
            print("\nClearing expired cache files...")
            # Note: This would require implementing expired file cleanup
            # For now, we'll just clear all cache as an example
            cleared = cache.clear_cache()
            print(f"Cleared {cleared} cache files")
    else:
        print("Cache is empty")


def example_configuration_modes() -> None:
    """Demonstrate different configuration modes."""
    print("\n=== Configuration Modes Example ===")

    config = PipelineConfig()

    print(f"Current mode: {'Development' if config.DEV_MODE else 'Production'}")
    print(f"Max days lookback: {config.MAX_DAYS_LOOKBACK}")
    print(f"Sample rate: {config.SAMPLE_RATE}")
    print(
        f"Max bytes billed: {config.MAX_BYTES_BILLED:,} ({config.MAX_BYTES_BILLED / 1024**3:.1f} GB)"
    )
    print(f"Cache TTL: {config.CACHE_TTL_HOURS} hours")
    print(f"Cache directory: {config.LOCAL_CACHE_DIR}")
    print(f"Processed data directory: {config.PROCESSED_DATA_DIR}")


def main() -> None:
    """Run all examples."""
    setup_logging()

    try:
        example_basic_usage()
        example_configuration_modes()
        example_cost_estimation()

        # Only run actual query if in development mode with proper credentials
        config = PipelineConfig()
        if config.DEV_MODE:
            print("\n⚠️  Skipping actual BigQuery execution in example")
            print("   To run with real queries, ensure you have:")
            print("   1. Valid GCP credentials")
            print("   2. Access to the specified BigQuery datasets")
            print("   3. Appropriate billing setup")
            # example_cached_query()

        example_cache_management()

        print("\n✅ All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    main()
