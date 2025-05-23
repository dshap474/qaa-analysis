import os
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_project_root() -> str:
    """
    Determine the project root directory based on current file location.

    Returns:
        str: Absolute path to the project root directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir) in ["notebook", "scripts"]:
        project_root = os.path.dirname(current_dir)
    else:
        project_root = current_dir
    return project_root


def load_and_display_data_robust(data_path: str) -> Optional[pd.DataFrame]:
    """
    Load Parquet data with robust error handling and multiple conversion strategies.

    This function implements multiple fallback strategies to handle PyArrow to Pandas
    conversion issues, particularly with date types and metadata conflicts.

    Args:
        data_path (str): Path to the Parquet file

    Returns:
        Optional[pd.DataFrame]: Loaded DataFrame or None if loading fails
    """
    logger.info(f"Attempting to load Parquet file: {data_path}")

    try:
        # Strategy 1: Try direct pandas read_parquet (most robust for type conversion)
        logger.info("Strategy 1: Attempting direct pandas.read_parquet()")
        try:
            df = pd.read_parquet(data_path)
            logger.info("Successfully loaded data using pandas.read_parquet()")
            _log_dataframe_info(df)
            return df
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {e}")

        # Strategy 2: PyArrow with ignore_metadata
        logger.info("Strategy 2: Attempting PyArrow with ignore_metadata=True")
        try:
            arrow_table = pq.read_table(data_path)
            logger.info(f"PyArrow Table Schema:\n{arrow_table.schema}")

            # Convert with ignore_metadata to bypass problematic metadata
            df = arrow_table.to_pandas(ignore_metadata=True)
            logger.info("Successfully converted using ignore_metadata=True")
            _log_dataframe_info(df)
            return df
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {e}")

        # Strategy 3: Manual schema conversion
        logger.info("Strategy 3: Attempting manual schema conversion")
        try:
            arrow_table = pq.read_table(data_path)

            # Create a new schema without problematic metadata
            new_fields = []
            for field in arrow_table.schema:
                if field.type == pa.date32():
                    # Convert date32 to timestamp for better pandas compatibility
                    new_field = pa.field(field.name, pa.timestamp("ns"))
                else:
                    new_field = field
                new_fields.append(new_field)

            new_schema = pa.schema(new_fields)

            # Cast the table to the new schema
            casted_table = arrow_table.cast(new_schema)
            df = casted_table.to_pandas()

            logger.info("Successfully converted using manual schema conversion")
            _log_dataframe_info(df)
            return df
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {e}")

        # Strategy 4: Column-by-column conversion
        logger.info("Strategy 4: Attempting column-by-column conversion")
        try:
            arrow_table = pq.read_table(data_path)

            # Convert each column individually
            data_dict = {}
            for i, column_name in enumerate(arrow_table.column_names):
                column = arrow_table.column(i)
                try:
                    if column.type == pa.date32():
                        # Convert date32 to datetime manually
                        pandas_series = column.to_pandas()
                        data_dict[column_name] = pd.to_datetime(pandas_series)
                    else:
                        data_dict[column_name] = column.to_pandas()
                except Exception as col_e:
                    logger.warning(f"Failed to convert column {column_name}: {col_e}")
                    # Fallback to string conversion
                    data_dict[column_name] = column.to_pylist()

            df = pd.DataFrame(data_dict)
            logger.info("Successfully converted using column-by-column approach")
            _log_dataframe_info(df)
            return df
        except Exception as e:
            logger.warning(f"Strategy 4 failed: {e}")

        # If all strategies fail
        logger.error("All conversion strategies failed")
        return None

    except FileNotFoundError:
        logger.error(f"Data file not found at {data_path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
        return None


def _log_dataframe_info(df: pd.DataFrame) -> None:
    """
    Log comprehensive information about the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame to analyze
    """
    logger.info(f"DataFrame shape: {df.shape}")

    print("\n" + "=" * 50)
    print("DATAFRAME ANALYSIS")
    print("=" * 50)

    print("\n--- DataFrame Head ---")
    print(df.head().to_string())

    print("\n--- DataFrame Info ---")
    df.info()

    print("\n--- Data Types ---")
    for col, dtype in df.dtypes.items():
        print(f"{col}: {dtype}")

    print("\n--- DataFrame Description (Numeric Columns) ---")
    numeric_cols = df.select_dtypes(
        include=["int64", "float64", "int32", "float32", "bool"]
    ).columns
    if not numeric_cols.empty:
        print(df[numeric_cols].describe().to_string())
    else:
        print("No standard numeric columns found. Describing all columns:")
        print(df.describe(include="all").to_string())

    # Special handling for date columns
    date_cols = df.select_dtypes(include=["datetime64", "datetime"]).columns
    if not date_cols.empty:
        print(f"\n--- Date Columns Analysis ---")
        for col in date_cols:
            print(f"{col}:")
            print(f"  Data type: {df[col].dtype}")
            print(f"  Sample values: {df[col].head().to_list()}")
            print(f"  Date range: {df[col].min()} to {df[col].max()}")

    if "tx_date" in df.columns:
        logger.info(f"tx_date column type: {df['tx_date'].dtype}")
        logger.info(f"Sample tx_date values: {df['tx_date'].head().to_list()}")


def validate_data_sample(df: pd.DataFrame) -> None:
    """
    Validate data by selecting a sample for manual verification.

    Args:
        df (pd.DataFrame): DataFrame to validate
    """
    logger.info("\n" + "=" * 50)
    logger.info("MANUAL VALIDATION SECTION")
    logger.info("=" * 50)

    if df.empty:
        logger.info("DataFrame is empty, cannot pick a sample for validation.")
        return

    # Try to find a good sample based on tx_count if available
    if "tx_count" in df.columns:
        high_activity_rows = df[df["tx_count"] > 0]
        if not high_activity_rows.empty:
            sample_row = high_activity_rows.sample(1)
            logger.info(
                "Sample row with transaction activity for Etherscan validation:"
            )
            logger.info(f"\n{sample_row.to_string()}")

            address = sample_row["address"].iloc[0]
            tx_date = sample_row["tx_date"].iloc[0]
            logger.info(f"\nValidation details:")
            logger.info(f"Address: {address}")
            logger.info(f"Date: {tx_date}")
            logger.info(f"Transaction count: {sample_row['tx_count'].iloc[0]}")
        else:
            logger.info("No rows with tx_count > 0 found. Showing first available row:")
            logger.info(f"\n{df.head(1).to_string()}")
    else:
        logger.warning("'tx_count' column not found. Showing first available row:")
        logger.info(f"\n{df.head(1).to_string()}")

    logger.info("=" * 50)


if __name__ == "__main__":
    project_root = get_project_root()
    logger.info(f"Project root determined as: {project_root}")

    # Determine filename to load
    try:
        from qaa_analysis.config import PipelineConfig

        config = PipelineConfig()
        _start_date_iso, end_date_iso = config.get_date_filter()
        date_str_for_file = end_date_iso.replace("-", "")
        sample_rate_int = int(config.SAMPLE_RATE * 100)
        data_name = f"basic_rev_daily_data_{date_str_for_file}_to_{date_str_for_file}_sample{sample_rate_int}.parquet"
        logger.info(f"Dynamically determined filename: {data_name}")
    except ImportError:
        logger.warning("Could not import PipelineConfig. Using fallback filename.")
        data_name = "basic_rev_daily_data_20250521_to_20250521_sample100.parquet"

    data_dir = os.path.join(project_root, "data", "processed")
    data_path = os.path.join(data_dir, data_name)

    # Load and analyze data
    df_loaded = load_and_display_data_robust(data_path)

    # Load and analyze data
    df_loaded = load_and_display_data_robust(data_path)

    if df_loaded is None:
        logger.error("Failed to load data. Exiting analysis script.")
    else:
        logger.info("Data loading completed successfully!")

        # --- ADD CSV EXPORT HERE ---
        csv_filename = data_name.replace(".parquet", ".csv")
        csv_path = os.path.join(data_dir, csv_filename)
        try:
            df_loaded.to_csv(csv_path, index=False)
            logger.info(f"Successfully exported data to CSV: {csv_path}")
        except Exception as e:
            logger.error(f"Failed to export data to CSV: {e}", exc_info=True)
        # --- END OF CSV EXPORT ---

        # Validate sample data
        validate_data_sample(df_loaded)

    if df_loaded is None:
        logger.error("Failed to load data. Exiting analysis script.")
    else:
        logger.info("Data loading completed successfully!")

        # Validate sample data
        validate_data_sample(df_loaded)

        logger.info("\n" + "=" * 50)
        logger.info("CACHE VALIDATION INSTRUCTIONS")
        logger.info("=" * 50)
        logger.info("To validate caching functionality:")
        logger.info(
            "1. Re-run the ETL script: poetry run python -m qaa_analysis.etl.basic_rev_etl"
        )
        logger.info("2. Observe logs for cache hit confirmation and faster execution")
        logger.info("3. Compare execution times between first run and subsequent runs")
        logger.info("=" * 50)
