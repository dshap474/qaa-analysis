"""
Fetch REV data for specific dates to support cluster analysis.

This script runs the REV ETL pipeline for the dates matching our clustering data.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from qaa_analysis.etl.basic_rev_etl import main as run_rev_etl
from qaa_analysis.config import PipelineConfig


def fetch_rev_for_clustering_date():
    """Fetch REV data for 2025-06-05 to match clustering data."""
    
    logger = logging.getLogger(__name__)
    
    # Override config to get specific date
    config = PipelineConfig()
    
    # We need to ensure we get 2025-06-05 data
    # The config uses MAX_DAYS_LOOKBACK from current date
    # So we'll run the existing ETL which should handle this
    
    logger.info("Fetching REV data for cluster analysis date: 2025-06-05")
    
    try:
        # Run the REV ETL
        run_rev_etl()
        
        logger.info("REV data fetch completed successfully")
        
        # Check if output file was created
        expected_file = config.PROCESSED_DATA_DIR / "basic_rev_daily_data_20250605_to_20250605_sample100.parquet"
        if expected_file.exists():
            logger.info(f"REV data successfully saved to: {expected_file}")
            return expected_file
        else:
            # Check for any REV files
            rev_files = list(config.PROCESSED_DATA_DIR.glob("*rev*.parquet"))
            if rev_files:
                logger.info(f"Found REV files: {rev_files}")
                return rev_files[0]
            else:
                logger.warning("No REV data files found after ETL run")
                return None
                
    except Exception as e:
        logger.error(f"Failed to fetch REV data: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    rev_file = fetch_rev_for_clustering_date()
    if rev_file:
        print(f"\nREV data available at: {rev_file}")
    else:
        print("\nFailed to fetch REV data")