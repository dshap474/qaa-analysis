"""
Basic REV ETL orchestration for QAA Analysis.

This module provides the initial ETL workflow that fetches Blockworks-style
revenue metrics from BigQuery, caches the results locally, and stores
processed data to Parquet files for further analysis.
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from ..cache.query_cache import QueryCache
from ..config import PipelineConfig
from ..etl.cost_aware_client import CostAwareBigQueryClient
from ..queries.rev_queries import get_blockworks_rev_query, get_rev_query_metadata


def setup_logging() -> logging.Logger:
    """
    Configure logging for the ETL process.

    Returns:
        Configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def validate_dataframe(df: pd.DataFrame, operation: str) -> bool:
    """
    Validate that a DataFrame meets basic quality requirements.

    Args:
        df: DataFrame to validate.
        operation: Description of the operation for logging.

    Returns:
        True if DataFrame is valid, False otherwise.
    """
    logger = logging.getLogger(__name__)

    if df is None:
        logger.error(f"{operation}: DataFrame is None")
        return False

    if not isinstance(df, pd.DataFrame):
        logger.error(f"{operation}: Expected DataFrame, got {type(df)}")
        return False

    if df.empty:
        logger.warning(f"{operation}: DataFrame is empty")
        return True  # Empty is valid, just not useful

    # Check for required columns
    required_columns = [
        "address",
        "tx_date",
        "tx_count",
        "sum_gas_used",
        "total_rev_eth",
        "tips_rev_eth",
        "burned_rev_eth",
        "avg_tx_fee_eth",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"{operation}: Missing required columns: {missing_columns}")
        return False

    logger.info(
        f"{operation}: DataFrame validation passed - {len(df):,} rows, {len(df.columns)} columns"
    )
    return True


def save_dataframe_safely(df: pd.DataFrame, output_path: Path, operation: str) -> bool:
    """
    Safely save a DataFrame to Parquet with error handling.

    Args:
        df: DataFrame to save.
        output_path: Path where to save the file.
        operation: Description of the operation for logging.

    Returns:
        True if save was successful, False otherwise.
    """
    logger = logging.getLogger(__name__)

    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to Parquet with compression
        df.to_parquet(output_path, index=False, compression="snappy")

        # Verify file was created and get size
        if output_path.exists():
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(
                f"{operation}: Successfully saved to {output_path} "
                f"({file_size_mb:.2f} MB, {len(df):,} rows)"
            )
            return True
        else:
            logger.error(f"{operation}: File was not created at {output_path}")
            return False

    except Exception as e:
        logger.error(f"{operation}: Failed to save DataFrame - {e}", exc_info=True)
        return False


def main() -> None:
    """
    Main ETL orchestration function for basic REV data processing.

    This function coordinates the entire ETL workflow:
    1. Initialize all core modules and configuration
    2. Generate SQL query for REV metrics
    3. Fetch data via cache (with BigQuery fallback)
    4. Validate and save processed data
    """
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Starting Basic REV ETL Process")
    logger.info("=" * 60)

    try:
        # Step 1: Initialize core modules
        logger.info("Initializing core modules...")

        config = PipelineConfig()
        bq_client = CostAwareBigQueryClient(config=config)
        query_cache = QueryCache(config=config)

        logger.info(
            f"Configuration loaded - DEV_MODE: {config.DEV_MODE}, "
            f"Lookback: {config.MAX_DAYS_LOOKBACK} days, "
            f"Sample Rate: {config.SAMPLE_RATE*100:.1f}%"
        )

        # Step 2: Determine query parameters
        logger.info("Determining query parameters...")

        start_date_iso, end_date_iso = config.get_date_filter()
        current_sample_rate = config.SAMPLE_RATE

        logger.info(
            f"Query window: {start_date_iso} to {end_date_iso} "
            f"(sample rate: {current_sample_rate*100:.1f}%)"
        )

        # Step 3: Generate SQL query
        logger.info("Generating SQL query...")

        sql_query_string = get_blockworks_rev_query(
            start_date_iso, end_date_iso, current_sample_rate
        )

        # Get query metadata for logging
        query_metadata = get_rev_query_metadata(
            start_date_iso, end_date_iso, current_sample_rate
        )

        logger.info(
            f"Query generated - Type: {query_metadata['query_type']}, "
            f"Days: {query_metadata['days_span']}, "
            f"Complexity: {query_metadata['estimated_complexity']}"
        )
        logger.debug(f"SQL Query (first 200 chars): {sql_query_string[:200]}...")

        # Step 4: Define data fetching function
        def _fetch_data_from_bq() -> Optional[pd.DataFrame]:
            """
            Inner function to fetch data from BigQuery.

            Returns:
                DataFrame with query results or None if failed.
            """
            logger.info("Attempting to fetch data from BigQuery...")

            try:
                df = bq_client.safe_query(sql_query_string)

                if df is not None and not df.empty:
                    logger.info(f"Successfully fetched {len(df):,} rows from BigQuery")

                    # Log some basic statistics
                    if "total_rev_eth" in df.columns:
                        total_rev = df["total_rev_eth"].sum()
                        logger.info(f"Total revenue in dataset: {total_rev:.6f} ETH")

                    return df
                else:
                    logger.warning(
                        "No data returned from BigQuery or query was aborted"
                    )
                    return None

            except Exception as e:
                logger.error(f"BigQuery fetch failed: {e}", exc_info=True)
                return None

        # Step 5: Fetch data via cache
        logger.info("Fetching data via cache system...")

        cache_request_params = {
            "start": start_date_iso,
            "end": end_date_iso,
            "sample": current_sample_rate,
            "query_version": "1.0",  # For easy cache invalidation
        }

        processed_df = query_cache.get_or_compute(
            query=sql_query_string,
            compute_fn=_fetch_data_from_bq,
            params=cache_request_params,
        )

        # Step 6: Validate retrieved data
        if not validate_dataframe(processed_df, "Data validation"):
            logger.error("Data validation failed, aborting ETL process")
            return

        # Step 7: Store processed data
        if processed_df is not None and not processed_df.empty:
            logger.info("Storing processed data...")

            # Generate output filename with timestamp and date range
            output_filename = (
                f"basic_rev_daily_data_"
                f"{start_date_iso.replace('-', '')}_to_{end_date_iso.replace('-', '')}"
                f"_sample{int(current_sample_rate*100)}.parquet"
            )

            output_path = config.PROCESSED_DATA_DIR / output_filename

            # Save the data
            save_success = save_dataframe_safely(
                processed_df, output_path, "Data storage"
            )

            if save_success:
                logger.info(f"Data successfully stored at: {output_path}")

                # Log summary statistics
                logger.info("=" * 40)
                logger.info("ETL SUMMARY STATISTICS")
                logger.info("=" * 40)
                logger.info(f"Total rows processed: {len(processed_df):,}")
                logger.info(f"Date range: {start_date_iso} to {end_date_iso}")
                logger.info(f"Unique addresses: {processed_df['address'].nunique():,}")
                logger.info(f"Total transactions: {processed_df['tx_count'].sum():,}")

                if "total_rev_eth" in processed_df.columns:
                    total_rev = processed_df["total_rev_eth"].sum()
                    avg_rev = processed_df["total_rev_eth"].mean()
                    logger.info(f"Total revenue: {total_rev:.6f} ETH")
                    logger.info(f"Average daily revenue per address: {avg_rev:.6f} ETH")

                logger.info("=" * 40)
            else:
                logger.error("Failed to save processed data")
        else:
            logger.info("No data to process or save")

        # Step 8: Completion
        logger.info("=" * 60)
        logger.info("Basic REV ETL process completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"ETL process failed with error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
