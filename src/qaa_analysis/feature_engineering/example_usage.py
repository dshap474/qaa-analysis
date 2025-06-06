"""
Example Usage of QAA Feature Engineering Pipeline.

This script demonstrates how to use the feature engineering pipeline
to extract behavioral features from DeFi interaction data.
"""

import logging
from pathlib import Path
import sys

# Add the parent directory to the path to import qaa_analysis modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from qaa_analysis.feature_engineering import FeaturePipeline


def setup_logging() -> logging.Logger:
    """Set up logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("feature_extraction.log")
        ]
    )
    return logging.getLogger(__name__)


def main():
    """
    Main function demonstrating feature extraction pipeline usage.
    """
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("QAA FEATURE ENGINEERING EXAMPLE")
    logger.info("=" * 60)
    
    # Configuration
    # NOTE: Update these paths to match your actual data locations
    interaction_data_path = Path("data/defi_interactions_enriched.parquet")
    output_dir = Path("data/features")
    
    # Check if input data exists
    if not interaction_data_path.exists():
        logger.error(f"Input data file not found: {interaction_data_path}")
        logger.info("Please ensure you have run the interaction ETL pipeline first.")
        logger.info("Expected file: data/defi_interactions_enriched.parquet")
        return
    
    try:
        # Initialize the feature pipeline
        logger.info("Initializing feature extraction pipeline...")
        pipeline = FeaturePipeline(
            output_dir=output_dir,
            chunk_size=500,  # Process 500 users at a time
            logger=logger
        )
        
        # Run the complete pipeline
        logger.info("Starting feature extraction...")
        feature_matrix_path = pipeline.run_pipeline(
            interaction_data_path=interaction_data_path,
            output_filename="user_behavioral_features.parquet"
        )
        
        # Get pipeline summary
        summary = pipeline.get_feature_summary()
        
        logger.info("=" * 60)
        logger.info("FEATURE EXTRACTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total features extracted: {summary['total_features']}")
        logger.info("Features by extractor:")
        for extractor, count in summary['features_by_extractor'].items():
            logger.info(f"  - {extractor}: {count} features")
        
        logger.info("Feature data types:")
        for data_type, count in summary['feature_types'].items():
            logger.info(f"  - {data_type}: {count} features")
        
        logger.info(f"Feature matrix saved to: {feature_matrix_path}")
        logger.info(f"Output directory: {output_dir}")
        
        # Example: Load and inspect the feature matrix
        logger.info("Loading feature matrix for inspection...")
        feature_df = pipeline.load_feature_matrix(feature_matrix_path)
        
        logger.info(f"Feature matrix shape: {feature_df.shape}")
        logger.info(f"Sample of feature names: {list(feature_df.columns[:10])}")
        
        # Show basic statistics
        logger.info("Basic feature statistics:")
        numeric_features = feature_df.select_dtypes(include=['int64', 'float64']).columns
        stats = feature_df[numeric_features].describe()
        logger.info(f"Non-zero features per user (avg): {(feature_df[numeric_features] != 0).sum(axis=1).mean():.1f}")
        
        logger.info("=" * 60)
        logger.info("FEATURE EXTRACTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main() 