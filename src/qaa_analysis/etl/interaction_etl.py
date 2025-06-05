"""
User-Contract Interaction ETL for QAA Analysis.

This module provides ETL functionality to extract user interactions with DeFi contracts
based on the contract mapping in defi_contract_map.json. It identifies transactions
where users interact directly with mapped contracts and enriches the data with
protocol metadata for behavioral analysis.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from ..cache.query_cache import QueryCache
from ..config import PipelineConfig
from ..etl.cost_aware_client import CostAwareBigQueryClient


def setup_logging() -> logging.Logger:
    """
    Configure logging for the interaction ETL process.

    Returns:
        Configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def load_contract_map() -> Tuple[List[str], Dict[str, Dict[str, str]]]:
    """
    Load and parse the DeFi contract map JSON file.
    
    Returns:
        Tuple containing:
        - List of all unique contract addresses (lowercase)
        - Dictionary mapping contract addresses to their metadata
    """
    logger = logging.getLogger(__name__)
    
    # Path to the contract map file
    contract_map_path = Path(__file__).parent.parent / "address-mapping" / "defi_contract_map.json"
    
    if not contract_map_path.exists():
        raise FileNotFoundError(f"Contract map not found at: {contract_map_path}")
    
    logger.info(f"Loading contract map from: {contract_map_path}")
    
    with open(contract_map_path, 'r') as f:
        contract_map = json.load(f)
    
    # Extract all contract addresses and their metadata
    contract_addresses = []
    address_metadata = {}
    
    # Iterate through the nested structure
    for participant_type, user_archetypes in contract_map.items():
        for user_archetype, contracts in user_archetypes.items():
            for contract in contracts:
                address = contract["contract_address"].lower()
                contract_addresses.append(address)
                
                # Store metadata for this address
                address_metadata[address] = {
                    "participant_type": participant_type,
                    "user_archetype": user_archetype,
                    "protocol_category": contract["protocol_category"],
                    "contract_role": contract["contract_role"],
                    "label_type": contract["label_type"],
                    "etherscan_verified": contract["etherscan_verified"],
                    "first_block": contract["first_block"],
                    "notes": contract.get("notes", "")
                }
    
    # Remove duplicates while preserving order
    unique_addresses = list(dict.fromkeys(contract_addresses))
    
    logger.info(f"Loaded {len(unique_addresses)} unique contract addresses from {len(contract_addresses)} total entries")
    
    return unique_addresses, address_metadata


def get_interaction_query(contract_addresses: List[str], start_date: str, end_date: str, sample_rate: float) -> str:
    """
    Generate a BigQuery SQL query to find all transactions to the specified contract addresses.
    
    Args:
        contract_addresses: List of contract addresses to filter for
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        sample_rate: Sampling rate between 0.0 and 1.0
        
    Returns:
        SQL query string
    """
    # Validate sample_rate
    if not 0.0 <= sample_rate <= 1.0:
        raise ValueError(f"sample_rate must be between 0.0 and 1.0, got {sample_rate}")
    
    # Ensure addresses are lowercase and properly quoted for SQL
    formatted_addresses = ", ".join([f"'{addr.lower()}'" for addr in contract_addresses])
    
    # Build WHERE conditions
    where_conditions = [
        f"DATE(block_timestamp) BETWEEN '{start_date}' AND '{end_date}'",
        f"LOWER(to_address) IN ({formatted_addresses})"
    ]
    
    # Add sampling condition if sample_rate < 1.0
    if 0.0 < sample_rate < 1.0:
        where_conditions.append(f"RAND() < {sample_rate}")
    
    where_clause = " AND ".join(where_conditions)
    
    query = f"""
    SELECT
        `hash` as transaction_hash,
        block_timestamp,
        from_address,
        to_address,
        value,
        receipt_gas_used,
        gas_price
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE {where_clause}
    ORDER BY block_timestamp DESC
    """
    
    return query.strip()


def enrich_interactions_with_metadata(df: pd.DataFrame, address_metadata: Dict[str, Dict[str, str]]) -> pd.DataFrame:
    """
    Enrich the interactions DataFrame with contract metadata.
    
    Args:
        df: DataFrame with interaction data
        address_metadata: Dictionary mapping addresses to metadata
        
    Returns:
        Enriched DataFrame with additional metadata columns
    """
    logger = logging.getLogger(__name__)
    
    if df.empty:
        logger.warning("DataFrame is empty, returning as-is")
        return df
    
    # Create a metadata DataFrame for merging
    metadata_df = pd.DataFrame.from_dict(address_metadata, orient='index')
    metadata_df.index.name = 'to_address'
    metadata_df = metadata_df.reset_index()
    
    # Ensure to_address is lowercase for consistent matching
    df['to_address_lower'] = df['to_address'].str.lower()
    metadata_df['to_address'] = metadata_df['to_address'].str.lower()
    
    # Merge the DataFrames
    enriched_df = df.merge(
        metadata_df,
        left_on='to_address_lower',
        right_on='to_address',
        how='left',
        suffixes=('', '_meta')
    )
    
    # Drop the temporary columns
    enriched_df = enriched_df.drop(columns=['to_address_lower', 'to_address_meta'])
    
    # Check for any unmatched addresses (should be none if our logic is correct)
    unmatched = enriched_df['protocol_category'].isna().sum()
    if unmatched > 0:
        logger.warning(f"Found {unmatched} interactions with unmatched contract addresses")
    
    logger.info(f"Successfully enriched {len(enriched_df)} interactions with metadata")
    
    return enriched_df


def validate_interactions_dataframe(df: pd.DataFrame, operation: str) -> bool:
    """
    Validate that an interactions DataFrame meets basic quality requirements.
    
    Args:
        df: DataFrame to validate
        operation: Description of the operation for logging
        
    Returns:
        True if DataFrame is valid, False otherwise
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
    
    # Check for required columns from BigQuery
    required_bq_columns = [
        "transaction_hash",
        "block_timestamp", 
        "from_address",
        "to_address",
        "value",
        "receipt_gas_used",
        "gas_price"
    ]
    
    # Check for required enrichment columns
    required_enrichment_columns = [
        "participant_type",
        "user_archetype", 
        "protocol_category",
        "contract_role"
    ]
    
    all_required = required_bq_columns + required_enrichment_columns
    missing_columns = [col for col in all_required if col not in df.columns]
    
    if missing_columns:
        logger.error(f"{operation}: Missing required columns: {missing_columns}")
        return False
    
    # Check for null values in critical columns
    critical_columns = ["transaction_hash", "from_address", "to_address", "protocol_category"]
    for col in critical_columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            logger.warning(f"{operation}: Found {null_count} null values in critical column '{col}'")
    
    logger.info(
        f"{operation}: DataFrame validation passed - {len(df):,} rows, {len(df.columns)} columns"
    )
    
    return True


def save_dataframe_safely(df: pd.DataFrame, output_path: Path, operation: str) -> bool:
    """
    Safely save a DataFrame to Parquet with error handling.
    
    Args:
        df: DataFrame to save
        output_path: Path where to save the file
        operation: Description of the operation for logging
        
    Returns:
        True if save was successful, False otherwise
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
    Main ETL orchestration function for user-contract interaction data processing.
    
    This function coordinates the entire ETL workflow:
    1. Initialize all core modules and configuration
    2. Load and parse the DeFi contract map
    3. Generate SQL query for contract interactions
    4. Fetch data via cache (with BigQuery fallback)
    5. Enrich data with contract metadata
    6. Validate and save processed data
    """
    # Setup logging
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Starting User-Contract Interaction ETL Process")
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
        
        # Step 2: Load contract map
        logger.info("Loading DeFi contract map...")
        
        contract_addresses, address_metadata = load_contract_map()
        
        logger.info(f"Loaded {len(contract_addresses)} contract addresses covering {len(set(meta['protocol_category'] for meta in address_metadata.values()))} protocol categories")
        
        # Step 3: Determine query parameters
        logger.info("Determining query parameters...")
        
        start_date_iso, end_date_iso = config.get_date_filter()
        current_sample_rate = config.SAMPLE_RATE
        
        logger.info(
            f"Query window: {start_date_iso} to {end_date_iso} "
            f"(sample rate: {current_sample_rate*100:.1f}%)"
        )
        
        # Step 4: Generate SQL query
        logger.info("Generating SQL query...")
        
        sql_query_string = get_interaction_query(
            contract_addresses, start_date_iso, end_date_iso, current_sample_rate
        )
        
        logger.info(f"Query generated for {len(contract_addresses)} contract addresses")
        logger.debug(f"SQL Query (first 200 chars): {sql_query_string[:200]}...")
        
        # Step 5: Define data fetching function
        def _fetch_data_from_bq() -> Optional[pd.DataFrame]:
            """
            Inner function to fetch data from BigQuery.
            
            Returns:
                DataFrame with query results or None if failed.
            """
            logger.info("Attempting to fetch interaction data from BigQuery...")
            
            try:
                df = bq_client.safe_query(sql_query_string)
                
                if df is not None and not df.empty:
                    logger.info(f"Successfully fetched {len(df):,} interactions from BigQuery")
                    
                    # Log some basic statistics
                    unique_users = df["from_address"].nunique()
                    unique_contracts = df["to_address"].nunique()
                    date_range = f"{df['block_timestamp'].min()} to {df['block_timestamp'].max()}"
                    
                    logger.info(f"Interaction summary: {unique_users:,} unique users, {unique_contracts} unique contracts")
                    logger.info(f"Date range: {date_range}")
                    
                    return df
                else:
                    logger.warning("Query returned empty results")
                    return None
                    
            except Exception as e:
                logger.error(f"Failed to fetch data from BigQuery: {e}", exc_info=True)
                return None
        
        # Step 6: Fetch data (with caching)
        logger.info("Fetching interaction data...")
        
        # Create cache parameters for consistent caching
        cache_params = {
            "start_date": start_date_iso,
            "end_date": end_date_iso,
            "sample_rate": current_sample_rate,
            "num_contracts": len(contract_addresses)
        }
        
        df = query_cache.get_or_compute(
            query=sql_query_string,
            compute_fn=_fetch_data_from_bq,
            params=cache_params
        )
        
        if df is None or df.empty:
            logger.error("No interaction data available. Exiting.")
            return
        
        # Step 7: Enrich data with contract metadata
        logger.info("Enriching interaction data with contract metadata...")
        
        enriched_df = enrich_interactions_with_metadata(df, address_metadata)
        
        # Step 8: Validate enriched data
        logger.info("Validating enriched interaction data...")
        
        if not validate_interactions_dataframe(enriched_df, "Enriched Interactions"):
            logger.error("Data validation failed. Exiting.")
            return
        
        # Step 9: Save processed data
        logger.info("Saving processed interaction data...")
        
        # Define output filename
        sample_suffix = f"_sample{current_sample_rate}" if current_sample_rate < 1.0 else ""
        output_filename = f"defi_interactions_{start_date_iso}_to_{end_date_iso}{sample_suffix}.parquet"
        output_path = config.PROCESSED_DATA_DIR / output_filename
        
        success = save_dataframe_safely(enriched_df, output_path, "Interaction Data")
        
        if success:
            logger.info("=" * 60)
            logger.info("User-Contract Interaction ETL Process Completed Successfully")
            logger.info("=" * 60)
            
            # Log final summary
            protocol_summary = enriched_df['protocol_category'].value_counts()
            logger.info("Protocol category distribution:")
            for protocol, count in protocol_summary.head(10).items():
                logger.info(f"  {protocol}: {count:,} interactions")
            
        else:
            logger.error("Failed to save processed data")
            
    except Exception as e:
        logger.error(f"ETL process failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main() 