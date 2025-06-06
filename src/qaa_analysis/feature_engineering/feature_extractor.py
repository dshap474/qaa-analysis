"""
Base Feature Extractor for QAA Analysis.

This module provides the abstract base class for all feature extractors,
defining the common interface and shared functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np


class FeatureExtractor(ABC):
    """
    Abstract base class for all feature extractors.
    
    This class defines the common interface that all feature extractors must implement,
    along with shared utility methods for data validation and logging.
    """
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the feature extractor.
        
        Args:
            name: Human-readable name for this feature extractor
            logger: Optional logger instance. If None, creates a new logger.
        """
        self.name = name
        self.logger = logger or logging.getLogger(f"{__name__}.{name}")
        self._feature_metadata: Dict[str, Dict[str, Any]] = {}
        
    @abstractmethod
    def extract_features(self, user_interactions: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract features for a single user from their interaction data.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary mapping feature names to their values
            
        Raises:
            ValueError: If the input data is invalid or missing required columns
        """
        pass
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """
        Get the list of feature names that this extractor produces.
        
        Returns:
            List of feature names
        """
        pass
    
    @abstractmethod
    def get_feature_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions for each feature produced by this extractor.
        
        Returns:
            Dictionary mapping feature names to their descriptions
        """
        pass
    
    def validate_input_data(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validate that the input DataFrame has the required structure.
        
        Args:
            df: DataFrame to validate
            required_columns: List of column names that must be present
            
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if df is None or df.empty:
            raise ValueError(f"{self.name}: Input DataFrame is None or empty")
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"{self.name}: Missing required columns: {missing_columns}. "
                f"Available columns: {list(df.columns)}"
            )
        
        self.logger.debug(f"{self.name}: Input validation passed for {len(df)} rows")
        return True
    
    def safe_divide(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Safely divide two numbers, handling division by zero.
        
        Args:
            numerator: The numerator
            denominator: The denominator
            default: Value to return if denominator is zero
            
        Returns:
            The division result or default value
        """
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    
    def calculate_gini_coefficient(self, values: pd.Series) -> float:
        """
        Calculate the Gini coefficient for a series of values.
        
        The Gini coefficient measures inequality in a distribution.
        0 = perfect equality, 1 = maximum inequality.
        
        Args:
            values: Series of numeric values
            
        Returns:
            Gini coefficient between 0 and 1
        """
        if len(values) == 0 or values.sum() == 0:
            return 0.0
        
        # Remove zeros and sort
        values = values[values > 0].sort_values()
        n = len(values)
        
        if n == 0:
            return 0.0
        
        # Calculate Gini coefficient
        cumsum = values.cumsum()
        return (n + 1 - 2 * cumsum.sum() / cumsum.iloc[-1]) / n
    
    def calculate_shannon_entropy(self, counts: pd.Series) -> float:
        """
        Calculate Shannon entropy for a series of counts.
        
        Shannon entropy measures the diversity/uncertainty in a distribution.
        Higher values indicate more diversity.
        
        Args:
            counts: Series of count values
            
        Returns:
            Shannon entropy value
        """
        if len(counts) == 0 or counts.sum() == 0:
            return 0.0
        
        # Calculate probabilities
        probabilities = counts / counts.sum()
        probabilities = probabilities[probabilities > 0]  # Remove zeros
        
        # Calculate entropy
        return -np.sum(probabilities * np.log2(probabilities))
    
    def calculate_herfindahl_index(self, counts: pd.Series) -> float:
        """
        Calculate the Herfindahl-Hirschman Index (HHI) for concentration.
        
        HHI measures market concentration. Higher values indicate more concentration.
        Range: 1/n (perfect equality) to 1 (complete concentration).
        
        Args:
            counts: Series of count values
            
        Returns:
            HHI value between 0 and 1
        """
        if len(counts) == 0 or counts.sum() == 0:
            return 0.0
        
        # Calculate market shares
        shares = counts / counts.sum()
        
        # Calculate HHI
        return np.sum(shares ** 2)
    
    def get_percentile_rank(self, value: float, reference_series: pd.Series) -> float:
        """
        Get the percentile rank of a value within a reference series.
        
        Args:
            value: The value to rank
            reference_series: Series of reference values
            
        Returns:
            Percentile rank between 0 and 100
        """
        if len(reference_series) == 0:
            return 50.0  # Default to median
        
        return (reference_series <= value).mean() * 100
    
    def add_feature_metadata(self, feature_name: str, description: str, 
                           data_type: str, expected_range: Optional[str] = None,
                           interpretation: Optional[str] = None) -> None:
        """
        Add metadata for a feature.
        
        Args:
            feature_name: Name of the feature
            description: Brief description of what the feature measures
            data_type: Data type (e.g., 'int64', 'float64', 'bool')
            expected_range: Expected range of values (e.g., '[0, inf)', '[0, 1]')
            interpretation: How to interpret the feature values
        """
        self._feature_metadata[feature_name] = {
            'description': description,
            'data_type': data_type,
            'expected_range': expected_range,
            'interpretation': interpretation,
            'extractor': self.name
        }
    
    def get_feature_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all features produced by this extractor.
        
        Returns:
            Dictionary mapping feature names to their metadata
        """
        return self._feature_metadata.copy()
    
    def log_extraction_summary(self, user_address: str, features: Dict[str, Any]) -> None:
        """
        Log a summary of the extracted features for debugging.
        
        Args:
            user_address: The user address being processed
            features: The extracted features
        """
        non_zero_features = {k: v for k, v in features.items() if v != 0 and not pd.isna(v)}
        self.logger.debug(
            f"{self.name}: Extracted {len(features)} features for {user_address}, "
            f"{len(non_zero_features)} non-zero"
        ) 