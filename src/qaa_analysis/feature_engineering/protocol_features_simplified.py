"""
Protocol Features Extractor for QAA Analysis (Simplified Version).

This module extracts features related to protocol usage patterns for the 4 main DeFi categories:
DEX (AMM), Lending, Stablecoin, and Liquid Staking (LSD).
"""

import logging
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np

from .feature_extractor import FeatureExtractor


class ProtocolFeatures(FeatureExtractor):
    """
    Extracts simplified protocol-related behavioral features from user interactions.
    
    Focuses only on the 4 main protocol categories in the data.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the protocol features extractor.
        
        Args:
            logger: Optional logger instance
        """
        super().__init__("ProtocolFeatures", logger)
        
        # Define the 4 protocol categories we have in the data
        self.protocol_categories = {
            'dex': 'DEX (AMM)',
            'lending': 'Lending',
            'stablecoin': 'Stablecoin',
            'lsd': 'Liquid Staking (LSD)'
        }
        
        # Initialize feature metadata
        self._initialize_metadata()
    
    def _initialize_metadata(self) -> None:
        """Initialize metadata for all features produced by this extractor."""
        
        # Total protocols feature
        self.add_feature_metadata(
            'total_protocols',
            'Number of unique protocol categories used',
            'int64',
            '[0, 4]',
            'Higher values indicate more diverse protocol usage'
        )
        
        # Protocol interaction counts
        protocol_metadata = {
            'dex_interactions': ('Number of interactions with DEX protocols', 'Higher values indicate more DEX activity'),
            'lending_interactions': ('Number of interactions with lending protocols', 'Higher values indicate more lending activity'),
            'stablecoin_interactions': ('Number of interactions with stablecoin protocols', 'Higher values indicate more stablecoin activity'),
            'lsd_interactions': ('Number of interactions with liquid staking protocols', 'Higher values indicate more staking activity')
        }
        
        for feature_name, (description, interpretation) in protocol_metadata.items():
            self.add_feature_metadata(
                feature_name,
                description,
                'int64',
                '[0, inf)',
                interpretation
            )
        
        # Diversity features
        diversity_features = {
            'protocol_diversity_shannon': ('Shannon entropy of protocol category usage', 'float64', '[0, log(4)]', 'Higher values indicate more balanced protocol usage'),
            'protocol_concentration_hhi': ('Herfindahl index of protocol usage concentration', 'float64', '[0, 1]', 'Higher values indicate more concentrated usage')
        }
        
        for feature_name, (description, data_type, range_val, interpretation) in diversity_features.items():
            self.add_feature_metadata(feature_name, description, data_type, range_val, interpretation)
    
    def extract_features(self, user_interactions: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract protocol-related features for a single user.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary mapping feature names to their values
        """
        # Validate input data
        required_columns = ['protocol_category']
        self.validate_input_data(user_interactions, required_columns)
        
        features = {}
        
        # Extract protocol interaction counts
        protocol_counts = self._extract_protocol_counts(user_interactions)
        features.update(protocol_counts)
        
        # Extract diversity features
        diversity_features = self._extract_diversity_features(user_interactions)
        features.update(diversity_features)
        
        return features
    
    def _extract_protocol_counts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract interaction counts by protocol category.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of protocol counts
        """
        # Get value counts for protocol categories
        protocol_counts = df['protocol_category'].value_counts()
        
        features = {}
        
        # Count interactions for each protocol category
        for feature_key, protocol_name in self.protocol_categories.items():
            feature_name = f"{feature_key}_interactions"
            features[feature_name] = int(protocol_counts.get(protocol_name, 0))
        
        # Count total unique protocols used
        unique_protocols_used = df['protocol_category'].nunique()
        features['total_protocols'] = int(unique_protocols_used)
        
        return features
    
    def _extract_diversity_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract diversity and concentration features.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of diversity features
        """
        features = {}
        
        # Get protocol counts
        protocol_counts = df['protocol_category'].value_counts()
        
        # Only calculate diversity metrics if there are interactions
        if len(protocol_counts) > 0:
            # Shannon entropy for protocol diversity
            features['protocol_diversity_shannon'] = self.calculate_shannon_entropy(protocol_counts)
            
            # Herfindahl index for concentration
            features['protocol_concentration_hhi'] = self.calculate_herfindahl_index(protocol_counts)
        else:
            features['protocol_diversity_shannon'] = 0.0
            features['protocol_concentration_hhi'] = 0.0
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """
        Get the list of feature names that this extractor produces.
        
        Returns:
            List of feature names
        """
        return [
            'total_protocols',
            'dex_interactions',
            'lending_interactions', 
            'stablecoin_interactions',
            'lsd_interactions',
            'protocol_diversity_shannon',
            'protocol_concentration_hhi'
        ]
    
    def get_feature_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions for each feature produced by this extractor.
        
        Returns:
            Dictionary mapping feature names to their descriptions
        """
        descriptions = {}
        
        # Extract descriptions from metadata
        for feature_name, metadata in self._feature_metadata.items():
            descriptions[feature_name] = metadata['description']
        
        return descriptions