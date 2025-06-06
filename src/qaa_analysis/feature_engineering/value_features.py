"""
Value Features Extractor for QAA Analysis.

This module extracts features related to transaction values, gas usage,
and financial behavior patterns from user interactions.
"""

import logging
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np

from .feature_extractor import FeatureExtractor


class ValueFeatures(FeatureExtractor):
    """
    Extracts value and gas-related behavioral features from user interactions.
    
    This includes ETH transaction values, gas usage patterns, and financial
    behavior indicators.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the value features extractor.
        
        Args:
            logger: Optional logger instance
        """
        super().__init__("ValueFeatures", logger)
        
        # Define value thresholds for categorization
        self.high_value_threshold = 1.0  # ETH
        self.very_high_value_threshold = 10.0  # ETH
        self.micro_value_threshold = 0.01  # ETH
        
        # Initialize feature metadata
        self._initialize_metadata()
    
    def _initialize_metadata(self) -> None:
        """Initialize metadata for all features produced by this extractor."""
        
        value_features = {
            # ETH Value Features
            'total_eth_value': ('Total ETH value transacted', 'float64', '[0, inf)', 'Higher values indicate larger financial activity'),
            'avg_tx_value': ('Average ETH value per transaction', 'float64', '[0, inf)', 'Higher values indicate preference for larger transactions'),
            'median_tx_value': ('Median ETH value per transaction', 'float64', '[0, inf)', 'Robust measure of typical transaction size'),
            'max_tx_value': ('Maximum ETH value in a single transaction', 'float64', '[0, inf)', 'Indicates capacity for large transactions'),
            'value_volatility': ('Standard deviation of transaction values', 'float64', '[0, inf)', 'Higher values indicate more variable transaction sizes'),
            'value_concentration_gini': ('Gini coefficient of transaction value distribution', 'float64', '[0, 1]', 'Higher values indicate more concentrated value in few transactions'),
            
            # Value Category Ratios
            'high_value_tx_ratio': ('Proportion of transactions >1 ETH', 'float64', '[0, 1]', 'Higher values indicate preference for large transactions'),
            'very_high_value_tx_ratio': ('Proportion of transactions >10 ETH', 'float64', '[0, 1]', 'Higher values indicate very large transaction capability'),
            'micro_tx_ratio': ('Proportion of transactions <0.01 ETH', 'float64', '[0, 1]', 'Higher values indicate micro-transaction behavior'),
            'zero_value_tx_ratio': ('Proportion of zero-value transactions', 'float64', '[0, 1]', 'Higher values indicate contract interaction focus'),
            
            # Gas Features
            'total_gas_used': ('Total gas consumed across all transactions', 'int64', '[0, inf)', 'Higher values indicate more complex or frequent interactions'),
            'avg_gas_per_tx': ('Average gas used per transaction', 'float64', '[0, inf)', 'Higher values indicate more complex transactions'),
            'median_gas_per_tx': ('Median gas used per transaction', 'float64', '[0, inf)', 'Robust measure of typical gas usage'),
            'total_gas_cost_eth': ('Total gas cost in ETH', 'float64', '[0, inf)', 'Higher values indicate more expensive transaction patterns'),
            'avg_gas_price': ('Average gas price paid (gwei)', 'float64', '[0, inf)', 'Higher values indicate willingness to pay for speed'),
            'gas_price_volatility': ('Standard deviation of gas prices paid', 'float64', '[0, inf)', 'Higher values indicate variable gas price strategy'),
            
            # Efficiency Features
            'gas_efficiency': ('ETH value per gas unit (value/gas ratio)', 'float64', '[0, inf)', 'Higher values indicate more value-efficient transactions'),
            'value_to_gas_cost_ratio': ('Ratio of transaction value to gas cost', 'float64', '[0, inf)', 'Higher values indicate more cost-effective transactions'),
            'avg_tx_cost_ratio': ('Average gas cost as proportion of transaction value', 'float64', '[0, inf)', 'Lower values indicate more cost-effective usage'),
            
            # Sophistication Indicators
            'complex_tx_ratio': ('Proportion of high-gas transactions (>200k gas)', 'float64', '[0, 1]', 'Higher values indicate more complex transaction patterns'),
            'premium_gas_ratio': ('Proportion of transactions with above-median gas price', 'float64', '[0, 1]', 'Higher values indicate willingness to pay premium for speed'),
            'value_consistency_score': ('Consistency score for transaction values', 'float64', '[0, 1]', 'Higher values indicate more consistent transaction sizing')
        }
        
        for feature_name, (description, data_type, range_val, interpretation) in value_features.items():
            self.add_feature_metadata(feature_name, description, data_type, range_val, interpretation)
    
    def extract_features(self, user_interactions: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract value and gas-related features for a single user.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary mapping feature names to their values
        """
        # Validate input data
        required_columns = ['value', 'receipt_gas_used', 'gas_price']
        self.validate_input_data(user_interactions, required_columns)
        
        # Prepare data with derived columns
        df = self._prepare_value_data(user_interactions)
        
        features = {}
        
        # Extract ETH value features
        eth_features = self._extract_eth_value_features(df)
        features.update(eth_features)
        
        # Extract gas features
        gas_features = self._extract_gas_features(df)
        features.update(gas_features)
        
        # Extract efficiency features
        efficiency_features = self._extract_efficiency_features(df)
        features.update(efficiency_features)
        
        # Extract sophistication features
        sophistication_features = self._extract_sophistication_features(df)
        features.update(sophistication_features)
        
        return features
    
    def _prepare_value_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare value data with derived columns.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            DataFrame with additional value-related columns
        """
        df_prepared = df.copy()
        
        # Convert to numeric and handle missing values
        numeric_columns = ['value', 'receipt_gas_used', 'gas_price']
        for col in numeric_columns:
            df_prepared[col] = pd.to_numeric(df_prepared[col], errors='coerce').fillna(0)
        
        # Convert wei to ETH
        df_prepared['value_eth'] = df_prepared['value'] / 1e18
        df_prepared['gas_cost_eth'] = (df_prepared['receipt_gas_used'] * df_prepared['gas_price']) / 1e18
        df_prepared['gas_price_gwei'] = df_prepared['gas_price'] / 1e9
        
        # Create value category flags
        df_prepared['is_high_value'] = df_prepared['value_eth'] > self.high_value_threshold
        df_prepared['is_very_high_value'] = df_prepared['value_eth'] > self.very_high_value_threshold
        df_prepared['is_micro_value'] = (df_prepared['value_eth'] > 0) & (df_prepared['value_eth'] < self.micro_value_threshold)
        df_prepared['is_zero_value'] = df_prepared['value_eth'] == 0
        
        # Create gas category flags
        df_prepared['is_complex_tx'] = df_prepared['receipt_gas_used'] > 200000  # High gas usage
        
        return df_prepared
    
    def _extract_eth_value_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract ETH value-related features.
        
        Args:
            df: Prepared user interactions DataFrame
            
        Returns:
            Dictionary of ETH value features
        """
        features = {}
        
        value_series = df['value_eth']
        
        # Basic value statistics
        features['total_eth_value'] = float(value_series.sum())
        features['avg_tx_value'] = float(value_series.mean())
        features['median_tx_value'] = float(value_series.median())
        features['max_tx_value'] = float(value_series.max())
        features['value_volatility'] = float(value_series.std())
        
        # Value concentration
        features['value_concentration_gini'] = self.calculate_gini_coefficient(value_series)
        
        # Value category ratios
        total_tx = len(df)
        features['high_value_tx_ratio'] = self.safe_divide(df['is_high_value'].sum(), total_tx)
        features['very_high_value_tx_ratio'] = self.safe_divide(df['is_very_high_value'].sum(), total_tx)
        features['micro_tx_ratio'] = self.safe_divide(df['is_micro_value'].sum(), total_tx)
        features['zero_value_tx_ratio'] = self.safe_divide(df['is_zero_value'].sum(), total_tx)
        
        return features
    
    def _extract_gas_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract gas usage and pricing features.
        
        Args:
            df: Prepared user interactions DataFrame
            
        Returns:
            Dictionary of gas features
        """
        features = {}
        
        gas_used_series = df['receipt_gas_used']
        gas_price_series = df['gas_price_gwei']
        gas_cost_series = df['gas_cost_eth']
        
        # Gas usage statistics
        features['total_gas_used'] = int(gas_used_series.sum())
        features['avg_gas_per_tx'] = float(gas_used_series.mean())
        features['median_gas_per_tx'] = float(gas_used_series.median())
        
        # Gas cost statistics
        features['total_gas_cost_eth'] = float(gas_cost_series.sum())
        
        # Gas price statistics
        features['avg_gas_price'] = float(gas_price_series.mean())
        features['gas_price_volatility'] = float(gas_price_series.std())
        
        return features
    
    def _extract_efficiency_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract efficiency and cost-effectiveness features.
        
        Args:
            df: Prepared user interactions DataFrame
            
        Returns:
            Dictionary of efficiency features
        """
        features = {}
        
        # Gas efficiency (value per gas unit)
        total_value = df['value_eth'].sum()
        total_gas = df['receipt_gas_used'].sum()
        features['gas_efficiency'] = self.safe_divide(total_value, total_gas)
        
        # Value to gas cost ratio
        total_gas_cost = df['gas_cost_eth'].sum()
        features['value_to_gas_cost_ratio'] = self.safe_divide(total_value, total_gas_cost)
        
        # Average transaction cost ratio (gas cost / transaction value)
        # Only for non-zero value transactions
        non_zero_value_df = df[df['value_eth'] > 0]
        if len(non_zero_value_df) > 0:
            cost_ratios = non_zero_value_df['gas_cost_eth'] / non_zero_value_df['value_eth']
            features['avg_tx_cost_ratio'] = float(cost_ratios.mean())
        else:
            features['avg_tx_cost_ratio'] = 0.0
        
        return features
    
    def _extract_sophistication_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract features indicating user sophistication and behavior patterns.
        
        Args:
            df: Prepared user interactions DataFrame
            
        Returns:
            Dictionary of sophistication features
        """
        features = {}
        
        total_tx = len(df)
        
        # Complex transaction ratio
        features['complex_tx_ratio'] = self.safe_divide(df['is_complex_tx'].sum(), total_tx)
        
        # Premium gas ratio (above median gas price)
        if len(df) > 0:
            median_gas_price = df['gas_price_gwei'].median()
            premium_gas_tx = (df['gas_price_gwei'] > median_gas_price).sum()
            features['premium_gas_ratio'] = self.safe_divide(premium_gas_tx, total_tx)
        else:
            features['premium_gas_ratio'] = 0.0
        
        # Value consistency score (inverse of coefficient of variation)
        value_series = df['value_eth']
        if len(value_series) > 1 and value_series.mean() > 0:
            cv = value_series.std() / value_series.mean()  # Coefficient of variation
            features['value_consistency_score'] = 1 / (1 + cv)  # Higher score = more consistent
        else:
            features['value_consistency_score'] = 1.0
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """
        Get the list of feature names that this extractor produces.
        
        Returns:
            List of feature names
        """
        return [
            # ETH Value Features
            'total_eth_value',
            'avg_tx_value',
            'median_tx_value',
            'max_tx_value',
            'value_volatility',
            'value_concentration_gini',
            
            # Value Category Ratios
            'high_value_tx_ratio',
            'very_high_value_tx_ratio',
            'micro_tx_ratio',
            'zero_value_tx_ratio',
            
            # Gas Features
            'total_gas_used',
            'avg_gas_per_tx',
            'median_gas_per_tx',
            'total_gas_cost_eth',
            'avg_gas_price',
            'gas_price_volatility',
            
            # Efficiency Features
            'gas_efficiency',
            'value_to_gas_cost_ratio',
            'avg_tx_cost_ratio',
            
            # Sophistication Indicators
            'complex_tx_ratio',
            'premium_gas_ratio',
            'value_consistency_score'
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
    
    def analyze_value_patterns(self, user_interactions: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform detailed analysis of user value and gas patterns.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary with detailed value pattern analysis
        """
        df = self._prepare_value_data(user_interactions)
        
        analysis = {
            'value_percentiles': {
                '25th': df['value_eth'].quantile(0.25),
                '50th': df['value_eth'].quantile(0.50),
                '75th': df['value_eth'].quantile(0.75),
                '90th': df['value_eth'].quantile(0.90),
                '95th': df['value_eth'].quantile(0.95)
            },
            'gas_percentiles': {
                '25th': df['receipt_gas_used'].quantile(0.25),
                '50th': df['receipt_gas_used'].quantile(0.50),
                '75th': df['receipt_gas_used'].quantile(0.75),
                '90th': df['receipt_gas_used'].quantile(0.90),
                '95th': df['receipt_gas_used'].quantile(0.95)
            },
            'value_categories': {
                'zero_value': (df['value_eth'] == 0).sum(),
                'micro_value': df['is_micro_value'].sum(),
                'normal_value': ((df['value_eth'] >= self.micro_value_threshold) & 
                               (df['value_eth'] < self.high_value_threshold)).sum(),
                'high_value': df['is_high_value'].sum(),
                'very_high_value': df['is_very_high_value'].sum()
            },
            'gas_efficiency_by_value': {
                'zero_value': self._calculate_avg_gas_for_category(df, df['is_zero_value']),
                'micro_value': self._calculate_avg_gas_for_category(df, df['is_micro_value']),
                'high_value': self._calculate_avg_gas_for_category(df, df['is_high_value'])
            }
        }
        
        return analysis
    
    def _calculate_avg_gas_for_category(self, df: pd.DataFrame, category_mask: pd.Series) -> float:
        """
        Calculate average gas usage for a specific value category.
        
        Args:
            df: Prepared user interactions DataFrame
            category_mask: Boolean mask for the category
            
        Returns:
            Average gas usage for the category
        """
        category_df = df[category_mask]
        if len(category_df) > 0:
            return float(category_df['receipt_gas_used'].mean())
        return 0.0
    
    def identify_value_archetype(self, user_interactions: pd.DataFrame) -> str:
        """
        Identify the user's value behavior archetype.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            String describing the value behavior archetype
        """
        features = self.extract_features(user_interactions)
        
        # Rule-based archetype identification
        if features['very_high_value_tx_ratio'] > 0.1:
            return "Whale"
        elif features['high_value_tx_ratio'] > 0.3:
            return "High Value User"
        elif features['zero_value_tx_ratio'] > 0.8:
            return "Contract Interactor"
        elif features['micro_tx_ratio'] > 0.5:
            return "Micro Transactor"
        elif features['complex_tx_ratio'] > 0.5:
            return "Complex User"
        elif features['premium_gas_ratio'] > 0.7:
            return "Speed Prioritizer"
        elif features['value_consistency_score'] > 0.8:
            return "Consistent User"
        else:
            return "Regular User" 