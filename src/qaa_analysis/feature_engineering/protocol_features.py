"""
Protocol Features Extractor for QAA Analysis.

This module extracts features related to protocol usage patterns,
including interaction counts, ratios, and diversity metrics.
"""

import logging
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np

from .feature_extractor import FeatureExtractor


class ProtocolFeatures(FeatureExtractor):
    """
    Extracts protocol-related behavioral features from user interactions.
    
    This includes counts by protocol category, application diversity,
    and protocol usage patterns.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the protocol features extractor.
        
        Args:
            logger: Optional logger instance
        """
        super().__init__("ProtocolFeatures", logger)
        
        # Define protocol categories we expect to see
        self.expected_protocols = [
            'DEX', 'Lending', 'Staking', 'Yield Farming', 'Bridge',
            'Derivatives', 'Insurance', 'Governance', 'NFT', 'Gaming'
        ]
        
        # Define top applications to track individually
        self.top_applications = [
            'Uniswap', 'Aave', 'Compound', 'Curve', 'SushiSwap',
            'Balancer', 'MakerDAO', 'Lido', 'Convex', 'Yearn'
        ]
        
        # Initialize feature metadata
        self._initialize_metadata()
    
    def _initialize_metadata(self) -> None:
        """Initialize metadata for all features produced by this extractor."""
        
        # Protocol interaction counts
        for protocol in self.expected_protocols:
            feature_name = f"{protocol.lower().replace(' ', '_')}_interactions"
            self.add_feature_metadata(
                feature_name,
                f"Number of interactions with {protocol} protocols",
                "int64",
                "[0, inf)",
                f"Higher values indicate more activity in {protocol} protocols"
            )
        
        # Application interaction counts
        for app in self.top_applications:
            feature_name = f"{app.lower()}_interactions"
            self.add_feature_metadata(
                feature_name,
                f"Number of interactions with {app}",
                "int64",
                "[0, inf)",
                f"Higher values indicate preference for {app}"
            )
        
        # Diversity and ratio features
        diversity_features = {
            'unique_protocols': ('Number of unique protocol categories used', 'int64', '[0, inf)', 'Higher values indicate more diverse protocol usage'),
            'unique_applications': ('Number of unique applications used', 'int64', '[0, inf)', 'Higher values indicate more diverse application usage'),
            'protocol_diversity_shannon': ('Shannon entropy of protocol category usage', 'float64', '[0, inf)', 'Higher values indicate more balanced protocol usage'),
            'application_concentration_hhi': ('Herfindahl index of application usage concentration', 'float64', '[0, 1]', 'Higher values indicate more concentrated usage'),
            'dex_ratio': ('Proportion of interactions with DEX protocols', 'float64', '[0, 1]', 'Higher values indicate DEX specialization'),
            'lending_ratio': ('Proportion of interactions with lending protocols', 'float64', '[0, 1]', 'Higher values indicate lending specialization'),
            'defi_native_ratio': ('Proportion of interactions with DeFi-native vs traditional finance protocols', 'float64', '[0, 1]', 'Higher values indicate DeFi-native preference')
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
        required_columns = ['protocol_category', 'application', 'user_type']
        self.validate_input_data(user_interactions, required_columns)
        
        features = {}
        
        # Extract protocol interaction counts
        protocol_counts = self._extract_protocol_counts(user_interactions)
        features.update(protocol_counts)
        
        # Extract application interaction counts
        application_counts = self._extract_application_counts(user_interactions)
        features.update(application_counts)
        
        # Extract diversity features
        diversity_features = self._extract_diversity_features(user_interactions)
        features.update(diversity_features)
        
        # Extract ratio features
        ratio_features = self._extract_ratio_features(user_interactions, protocol_counts)
        features.update(ratio_features)
        
        return features
    
    def _extract_protocol_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Extract interaction counts by protocol category.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of protocol counts
        """
        protocol_counts = df['protocol_category'].value_counts()
        
        features = {}
        for protocol in self.expected_protocols:
            feature_name = f"{protocol.lower().replace(' ', '_')}_interactions"
            features[feature_name] = int(protocol_counts.get(protocol, 0))
        
        return features
    
    def _extract_application_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Extract interaction counts by application.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of application counts
        """
        application_counts = df['application'].value_counts()
        
        features = {}
        for app in self.top_applications:
            feature_name = f"{app.lower()}_interactions"
            features[feature_name] = int(application_counts.get(app, 0))
        
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
        
        # Protocol diversity
        protocol_counts = df['protocol_category'].value_counts()
        features['unique_protocols'] = len(protocol_counts)
        features['protocol_diversity_shannon'] = self.calculate_shannon_entropy(protocol_counts)
        
        # Application diversity
        application_counts = df['application'].value_counts()
        features['unique_applications'] = len(application_counts)
        features['application_concentration_hhi'] = self.calculate_herfindahl_index(application_counts)
        
        return features
    
    def _extract_ratio_features(self, df: pd.DataFrame, protocol_counts: Dict[str, int]) -> Dict[str, float]:
        """
        Extract ratio features based on protocol usage.
        
        Args:
            df: User interactions DataFrame
            protocol_counts: Dictionary of protocol interaction counts
            
        Returns:
            Dictionary of ratio features
        """
        total_interactions = len(df)
        
        features = {}
        
        # Protocol ratios
        features['dex_ratio'] = self.safe_divide(
            protocol_counts.get('dex_interactions', 0), 
            total_interactions
        )
        
        features['lending_ratio'] = self.safe_divide(
            protocol_counts.get('lending_interactions', 0), 
            total_interactions
        )
        
        # DeFi native vs traditional finance ratio
        defi_native_protocols = ['DEX', 'Yield Farming', 'Governance', 'NFT']
        defi_native_count = sum(
            protocol_counts.get(f"{p.lower().replace(' ', '_')}_interactions", 0) 
            for p in defi_native_protocols
        )
        
        features['defi_native_ratio'] = self.safe_divide(defi_native_count, total_interactions)
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """
        Get the list of feature names that this extractor produces.
        
        Returns:
            List of feature names
        """
        feature_names = []
        
        # Protocol counts
        for protocol in self.expected_protocols:
            feature_names.append(f"{protocol.lower().replace(' ', '_')}_interactions")
        
        # Application counts
        for app in self.top_applications:
            feature_names.append(f"{app.lower()}_interactions")
        
        # Diversity and ratio features
        feature_names.extend([
            'unique_protocols',
            'unique_applications', 
            'protocol_diversity_shannon',
            'application_concentration_hhi',
            'dex_ratio',
            'lending_ratio',
            'defi_native_ratio'
        ])
        
        return feature_names
    
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
    
    def get_protocol_specialization_score(self, user_interactions: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate specialization scores for each protocol category.
        
        A specialization score indicates how much a user focuses on a particular
        protocol relative to their overall activity.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary mapping protocol categories to specialization scores
        """
        protocol_counts = user_interactions['protocol_category'].value_counts()
        total_interactions = len(user_interactions)
        
        specialization_scores = {}
        for protocol, count in protocol_counts.items():
            # Specialization score is the proportion of interactions in this protocol
            # weighted by the inverse of the number of protocols used
            proportion = count / total_interactions
            diversity_penalty = 1 / len(protocol_counts)  # Penalty for using many protocols
            
            specialization_scores[protocol] = proportion * (1 + diversity_penalty)
        
        return specialization_scores
    
    def identify_user_archetype(self, user_interactions: pd.DataFrame) -> str:
        """
        Identify the user archetype based on protocol usage patterns.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            String describing the user archetype
        """
        features = self.extract_features(user_interactions)
        
        # Simple rule-based archetype identification
        if features['dex_ratio'] > 0.7:
            return "DEX Trader"
        elif features['lending_ratio'] > 0.5:
            return "Lending User"
        elif features['unique_protocols'] >= 5:
            return "DeFi Explorer"
        elif features['protocol_diversity_shannon'] > 2.0:
            return "Diversified User"
        elif features['defi_native_ratio'] > 0.8:
            return "DeFi Native"
        else:
            return "Casual User" 