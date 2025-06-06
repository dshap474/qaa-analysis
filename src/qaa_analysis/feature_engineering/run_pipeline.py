"""
Run Feature Engineering Pipeline with Actual Data.

This script runs the feature engineering pipeline using the actual
DeFi interaction data available in the project.
"""

import logging
from pathlib import Path
import sys

# Add the parent directory to the path to import qaa_analysis modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from qaa_analysis.feature_engineering import FeaturePipeline


def setup_logging() -> logging.Logger:
    """Set up logging for the pipeline run."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("feature_extraction_run.log")
        ]
    )
    return logging.getLogger(__name__)


def main():
    """
    Main function to run the feature extraction pipeline.
    """
    logger = setup_logging()
    
    logger.info("=" * 80)
    logger.info("QAA FEATURE ENGINEERING PIPELINE - PRODUCTION RUN")
    logger.info("=" * 80)
    
    # Configuration - using actual data file
    interaction_data_path = Path("data/processed/defi_interactions_2025-06-04_to_2025-06-04.parquet")
    output_dir = Path("data/features")
    
    # Check if input data exists
    if not interaction_data_path.exists():
        logger.error(f"Input data file not found: {interaction_data_path}")
        logger.info("Available files in data/processed:")
        processed_dir = Path("data/processed")
        if processed_dir.exists():
            for file in processed_dir.iterdir():
                logger.info(f"  - {file.name}")
        return
    
    # Log file info
    file_size_mb = interaction_data_path.stat().st_size / (1024 * 1024)
    logger.info(f"Input file: {interaction_data_path}")
    logger.info(f"File size: {file_size_mb:.2f} MB")
    
    try:
        # Initialize the feature pipeline
        logger.info("Initializing feature extraction pipeline...")
        pipeline = FeaturePipeline(
            output_dir=output_dir,
            chunk_size=100,  # Start with smaller chunks for testing
            logger=logger
        )
        
        # Run the complete pipeline
        logger.info("Starting feature extraction...")
        feature_matrix_path = pipeline.run_pipeline(
            interaction_data_path=interaction_data_path,
            output_filename="user_behavioral_features_2025-06-04.parquet"
        )
        
        # Get pipeline summary
        summary = pipeline.get_feature_summary()
        
        logger.info("=" * 80)
        logger.info("FEATURE EXTRACTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total features extracted: {summary['total_features']}")
        logger.info("Features by extractor:")
        for extractor, count in summary['features_by_extractor'].items():
            logger.info(f"  - {extractor}: {count} features")
        
        logger.info("Feature data types:")
        for data_type, count in summary['feature_types'].items():
            logger.info(f"  - {data_type}: {count} features")
        
        logger.info(f"Feature matrix saved to: {feature_matrix_path}")
        logger.info(f"Output directory: {output_dir}")
        
        # Load and inspect the feature matrix
        logger.info("Loading feature matrix for inspection...")
        feature_df = pipeline.load_feature_matrix(feature_matrix_path)
        
        logger.info(f"Feature matrix shape: {feature_df.shape}")
        logger.info(f"Number of users: {len(feature_df):,}")
        logger.info(f"Number of features: {len(feature_df.columns) - 1}")  # -1 for user_address
        
        # Show sample feature names
        feature_cols = [col for col in feature_df.columns if col != 'user_address']
        logger.info(f"Sample feature names: {feature_cols[:10]}")
        
        # Show basic statistics
        logger.info("Basic feature statistics:")
        numeric_features = feature_df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_features) > 0:
            non_zero_per_user = (feature_df[numeric_features] != 0).sum(axis=1).mean()
            logger.info(f"Average non-zero features per user: {non_zero_per_user:.1f}")
            
            # Show some sample users
            logger.info("Sample users and their feature counts:")
            for i, (idx, row) in enumerate(feature_df.head(3).iterrows()):
                user_addr = row['user_address']
                non_zero_count = (row[numeric_features] != 0).sum()
                logger.info(f"  User {user_addr[:10]}...: {non_zero_count} non-zero features")
        
        logger.info("=" * 80)
        logger.info("FEATURE EXTRACTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Results saved to: {output_dir}")
        logger.info("Files generated:")
        if output_dir.exists():
            for file in output_dir.iterdir():
                file_size = file.stat().st_size / (1024 * 1024)
                logger.info(f"  - {file.name} ({file_size:.2f} MB)")
        
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main() 