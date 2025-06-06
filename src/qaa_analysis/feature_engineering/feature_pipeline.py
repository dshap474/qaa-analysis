"""
Feature Pipeline for QAA Analysis.

This module provides the main orchestration for the feature extraction process,
coordinating multiple feature extractors and managing the end-to-end pipeline.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import time

import pandas as pd
import numpy as np

from .interaction_aggregator import InteractionAggregator
from .protocol_features import ProtocolFeatures
from .temporal_features import TemporalFeatures
from .value_features import ValueFeatures


class FeaturePipeline:
    """
    Orchestrates the complete feature extraction pipeline.
    
    This class manages the process of loading interaction data, extracting features
    from multiple extractors, and producing a final user feature matrix.
    """
    
    def __init__(self, 
                 output_dir: Path,
                 chunk_size: int = 1000,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the feature pipeline.
        
        Args:
            output_dir: Directory to save output files
            chunk_size: Number of users to process in each chunk
            logger: Optional logger instance
        """
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.logger = logger or logging.getLogger(__name__)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.aggregator = InteractionAggregator(logger=self.logger)
        self.extractors = self._initialize_extractors()
        
        # Pipeline state
        self._feature_metadata: Dict[str, Dict[str, Any]] = {}
        self._pipeline_stats: Dict[str, Any] = {}
    
    def _initialize_extractors(self) -> Dict[str, Any]:
        """
        Initialize all feature extractors.
        
        Returns:
            Dictionary mapping extractor names to extractor instances
        """
        extractors = {
            'protocol': ProtocolFeatures(logger=self.logger),
            'temporal': TemporalFeatures(logger=self.logger),
            'value': ValueFeatures(logger=self.logger)
        }
        
        self.logger.info(f"Initialized {len(extractors)} feature extractors")
        return extractors
    
    def run_pipeline(self, 
                    interaction_data_path: Path,
                    output_filename: str = "user_features.parquet") -> Path:
        """
        Run the complete feature extraction pipeline.
        
        Args:
            interaction_data_path: Path to the interaction data Parquet file
            output_filename: Name of the output feature matrix file
            
        Returns:
            Path to the generated feature matrix file
        """
        start_time = time.time()
        
        self.logger.info("=" * 60)
        self.logger.info("STARTING FEATURE EXTRACTION PIPELINE")
        self.logger.info("=" * 60)
        
        # Step 1: Load and prepare interaction data
        self.logger.info("Step 1: Loading interaction data...")
        self.aggregator.load_interactions(interaction_data_path)
        self.aggregator.log_summary()
        
        # Step 2: Extract features for all users
        self.logger.info("Step 2: Extracting features...")
        feature_matrix = self._extract_all_features()
        
        # Step 3: Validate and clean feature matrix
        self.logger.info("Step 3: Validating feature matrix...")
        feature_matrix = self._validate_feature_matrix(feature_matrix)
        
        # Step 4: Save feature matrix
        output_path = self.output_dir / output_filename
        self.logger.info(f"Step 4: Saving feature matrix to {output_path}...")
        self._save_feature_matrix(feature_matrix, output_path)
        
        # Step 5: Generate metadata and summary
        self.logger.info("Step 5: Generating metadata...")
        self._generate_metadata()
        self._log_pipeline_summary(start_time)
        
        self.logger.info("=" * 60)
        self.logger.info("FEATURE EXTRACTION PIPELINE COMPLETED")
        self.logger.info("=" * 60)
        
        return output_path
    
    def _extract_all_features(self) -> pd.DataFrame:
        """
        Extract features for all users using all extractors.
        
        Returns:
            DataFrame with user features
        """
        all_features = []
        processed_users = 0
        total_users = self.aggregator.get_user_count()
        
        self.logger.info(f"Processing {total_users:,} users in chunks of {self.chunk_size}")
        
        # Process users in chunks for memory efficiency
        for user_address, user_interactions in self.aggregator.iter_user_interactions(self.chunk_size):
            try:
                # Extract features from all extractors
                user_features = {'user_address': user_address}
                
                for extractor_name, extractor in self.extractors.items():
                    try:
                        features = extractor.extract_features(user_interactions)
                        user_features.update(features)
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to extract {extractor_name} features for user {user_address}: {e}"
                        )
                        # Add default values for failed extraction
                        for feature_name in extractor.get_feature_names():
                            user_features[feature_name] = 0
                
                all_features.append(user_features)
                processed_users += 1
                
                # Log progress
                if processed_users % 100 == 0:
                    progress = (processed_users / total_users) * 100
                    self.logger.info(f"Processed {processed_users:,}/{total_users:,} users ({progress:.1f}%)")
                    
            except Exception as e:
                self.logger.error(f"Failed to process user {user_address}: {e}")
                continue
        
        # Convert to DataFrame
        feature_df = pd.DataFrame(all_features)
        
        self.logger.info(f"Successfully extracted features for {len(feature_df):,} users")
        self.logger.info(f"Feature matrix shape: {feature_df.shape}")
        
        return feature_df
    
    def _validate_feature_matrix(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean the feature matrix.
        
        Args:
            feature_df: Raw feature matrix DataFrame
            
        Returns:
            Cleaned feature matrix DataFrame
        """
        original_shape = feature_df.shape
        
        # Check for missing values
        missing_counts = feature_df.isnull().sum()
        if missing_counts.sum() > 0:
            self.logger.warning(f"Found missing values in {(missing_counts > 0).sum()} columns")
            
            # Fill missing values with appropriate defaults
            for col in feature_df.columns:
                if col == 'user_address':
                    continue
                    
                if feature_df[col].dtype in ['int64', 'float64']:
                    feature_df[col] = feature_df[col].fillna(0)
                else:
                    feature_df[col] = feature_df[col].fillna('')
        
        # Check for infinite values
        numeric_cols = feature_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col == 'user_address':
                continue
                
            inf_count = np.isinf(feature_df[col]).sum()
            if inf_count > 0:
                self.logger.warning(f"Found {inf_count} infinite values in column '{col}'")
                feature_df[col] = feature_df[col].replace([np.inf, -np.inf], 0)
        
        # Remove duplicate users (shouldn't happen, but safety check)
        duplicates = feature_df.duplicated(subset=['user_address']).sum()
        if duplicates > 0:
            self.logger.warning(f"Found {duplicates} duplicate users, removing...")
            feature_df = feature_df.drop_duplicates(subset=['user_address'])
        
        # Validate data types
        feature_df = self._validate_data_types(feature_df)
        
        final_shape = feature_df.shape
        self.logger.info(f"Feature matrix validation: {original_shape} -> {final_shape}")
        
        return feature_df
    
    def _validate_data_types(self, feature_df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure proper data types for all features.
        
        Args:
            feature_df: Feature matrix DataFrame
            
        Returns:
            DataFrame with corrected data types
        """
        # Get expected data types from extractors
        expected_types = {}
        for extractor in self.extractors.values():
            metadata = extractor.get_feature_metadata()
            for feature_name, meta in metadata.items():
                expected_types[feature_name] = meta['data_type']
        
        # Convert data types
        for col in feature_df.columns:
            if col == 'user_address':
                continue
                
            if col in expected_types:
                expected_type = expected_types[col]
                
                try:
                    if expected_type == 'int64':
                        feature_df[col] = feature_df[col].astype('int64')
                    elif expected_type == 'float64':
                        feature_df[col] = feature_df[col].astype('float64')
                    elif expected_type == 'bool':
                        feature_df[col] = feature_df[col].astype('bool')
                except Exception as e:
                    self.logger.warning(f"Failed to convert column '{col}' to {expected_type}: {e}")
        
        return feature_df
    
    def _save_feature_matrix(self, feature_df: pd.DataFrame, output_path: Path) -> None:
        """
        Save the feature matrix to a Parquet file.
        
        Args:
            feature_df: Feature matrix DataFrame
            output_path: Path to save the file
        """
        try:
            feature_df.to_parquet(output_path, index=False, compression='snappy')
            
            # Verify file was created and get size
            if output_path.exists():
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                self.logger.info(
                    f"Successfully saved feature matrix: {output_path} "
                    f"({file_size_mb:.2f} MB, {len(feature_df):,} users, {len(feature_df.columns)} features)"
                )
            else:
                raise FileNotFoundError("Output file was not created")
                
        except Exception as e:
            self.logger.error(f"Failed to save feature matrix: {e}")
            raise
    
    def _generate_metadata(self) -> None:
        """
        Generate and save feature metadata and documentation.
        """
        # Collect metadata from all extractors
        all_metadata = {}
        for extractor_name, extractor in self.extractors.items():
            extractor_metadata = extractor.get_feature_metadata()
            all_metadata.update(extractor_metadata)
        
        self._feature_metadata = all_metadata
        
        # Save metadata to JSON
        metadata_path = self.output_dir / "feature_metadata.json"
        try:
            import json
            with open(metadata_path, 'w') as f:
                json.dump(all_metadata, f, indent=2, default=str)
            
            self.logger.info(f"Saved feature metadata to {metadata_path}")
        except Exception as e:
            self.logger.warning(f"Failed to save metadata: {e}")
        
        # Generate feature documentation
        self._generate_feature_documentation()
    
    def _generate_feature_documentation(self) -> None:
        """
        Generate human-readable feature documentation.
        """
        doc_path = self.output_dir / "feature_documentation.md"
        
        try:
            with open(doc_path, 'w') as f:
                f.write("# Feature Documentation\n\n")
                f.write("This document describes all features extracted by the QAA Analysis pipeline.\n\n")
                
                # Group features by extractor
                for extractor_name, extractor in self.extractors.items():
                    f.write(f"## {extractor_name.title()} Features\n\n")
                    
                    metadata = extractor.get_feature_metadata()
                    for feature_name, meta in metadata.items():
                        f.write(f"### `{feature_name}`\n")
                        f.write(f"- **Description**: {meta['description']}\n")
                        f.write(f"- **Data Type**: {meta['data_type']}\n")
                        f.write(f"- **Expected Range**: {meta.get('expected_range', 'N/A')}\n")
                        f.write(f"- **Interpretation**: {meta.get('interpretation', 'N/A')}\n\n")
                
                f.write(f"\n---\n\n")
                f.write(f"Generated on: {pd.Timestamp.now()}\n")
                f.write(f"Total features: {len(self._feature_metadata)}\n")
            
            self.logger.info(f"Generated feature documentation: {doc_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to generate documentation: {e}")
    
    def _log_pipeline_summary(self, start_time: float) -> None:
        """
        Log a summary of the pipeline execution.
        
        Args:
            start_time: Pipeline start time
        """
        execution_time = time.time() - start_time
        
        # Collect statistics
        stats = {
            'execution_time_seconds': execution_time,
            'total_users_processed': self.aggregator.get_user_count(),
            'total_interactions': self.aggregator.get_interaction_count(),
            'total_features_extracted': len(self._feature_metadata),
            'extractors_used': list(self.extractors.keys()),
            'output_directory': str(self.output_dir)
        }
        
        self._pipeline_stats = stats
        
        # Log summary
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info("-" * 40)
        self.logger.info(f"Execution time: {execution_time:.2f} seconds ({execution_time/60:.1f} minutes)")
        self.logger.info(f"Users processed: {stats['total_users_processed']:,}")
        self.logger.info(f"Interactions processed: {stats['total_interactions']:,}")
        self.logger.info(f"Features extracted: {stats['total_features_extracted']}")
        self.logger.info(f"Processing rate: {stats['total_users_processed']/execution_time:.1f} users/second")
        self.logger.info(f"Output directory: {self.output_dir}")
    
    def get_feature_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all extracted features.
        
        Returns:
            Dictionary with feature summary information
        """
        summary = {
            'total_features': len(self._feature_metadata),
            'features_by_extractor': {},
            'feature_types': {},
            'pipeline_stats': self._pipeline_stats
        }
        
        # Count features by extractor
        for feature_name, metadata in self._feature_metadata.items():
            extractor = metadata.get('extractor', 'unknown')
            if extractor not in summary['features_by_extractor']:
                summary['features_by_extractor'][extractor] = 0
            summary['features_by_extractor'][extractor] += 1
        
        # Count features by data type
        for feature_name, metadata in self._feature_metadata.items():
            data_type = metadata.get('data_type', 'unknown')
            if data_type not in summary['feature_types']:
                summary['feature_types'][data_type] = 0
            summary['feature_types'][data_type] += 1
        
        return summary
    
    def load_feature_matrix(self, feature_matrix_path: Path) -> pd.DataFrame:
        """
        Load a previously generated feature matrix.
        
        Args:
            feature_matrix_path: Path to the feature matrix Parquet file
            
        Returns:
            Feature matrix DataFrame
        """
        try:
            feature_df = pd.read_parquet(feature_matrix_path)
            self.logger.info(f"Loaded feature matrix: {feature_df.shape}")
            return feature_df
        except Exception as e:
            self.logger.error(f"Failed to load feature matrix: {e}")
            raise 