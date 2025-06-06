"""
Interaction Aggregator for QAA Analysis.

This module provides functionality to aggregate raw interaction data by user,
preparing it for feature extraction while maintaining data quality and performance.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator

import pandas as pd
import numpy as np


class InteractionAggregator:
    """
    Aggregates raw interaction data by user for feature extraction.
    
    This class handles loading interaction data, grouping by user, and providing
    efficient iteration over user groups for feature extraction.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the interaction aggregator.
        
        Args:
            logger: Optional logger instance. If None, creates a new logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self._interactions_df: Optional[pd.DataFrame] = None
        self._user_groups: Optional[pd.core.groupby.DataFrameGroupBy] = None
        self._analysis_date: Optional[pd.Timestamp] = None
        
    def load_interactions(self, data_path: Path) -> None:
        """
        Load interaction data from a Parquet file.
        
        Args:
            data_path: Path to the Parquet file containing interaction data
            
        Raises:
            FileNotFoundError: If the data file doesn't exist
            ValueError: If the data format is invalid
        """
        if not data_path.exists():
            raise FileNotFoundError(f"Interaction data file not found: {data_path}")
        
        self.logger.info(f"Loading interaction data from {data_path}")
        
        try:
            self._interactions_df = pd.read_parquet(data_path)
            self.logger.info(f"Loaded {len(self._interactions_df):,} interactions")
            
            # Validate required columns
            self._validate_interaction_data()
            
            # Prepare data for aggregation
            self._prepare_data()
            
            # Create user groups
            self._create_user_groups()
            
        except Exception as e:
            self.logger.error(f"Failed to load interaction data: {e}")
            raise
    
    def _validate_interaction_data(self) -> None:
        """
        Validate that the interaction data has the required structure.
        
        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        required_columns = [
            'transaction_hash', 'block_timestamp', 'from_address', 'to_address',
            'value', 'receipt_gas_used', 'gas_price', 'protocol_category',
            'application', 'user_type', 'contract_role'
        ]
        
        missing_columns = [col for col in required_columns if col not in self._interactions_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for empty data
        if self._interactions_df.empty:
            raise ValueError("Interaction data is empty")
        
        # Check for null values in critical columns
        critical_columns = ['from_address', 'to_address', 'protocol_category']
        for col in critical_columns:
            null_count = self._interactions_df[col].isna().sum()
            if null_count > 0:
                self.logger.warning(f"Found {null_count} null values in column '{col}'")
        
        self.logger.info("Interaction data validation passed")
    
    def _prepare_data(self) -> None:
        """
        Prepare the interaction data for efficient aggregation.
        
        This includes data type conversions, derived columns, and sorting.
        """
        df = self._interactions_df
        
        # Convert timestamps
        if not pd.api.types.is_datetime64_any_dtype(df['block_timestamp']):
            df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])
        
        # Convert numeric columns
        numeric_columns = ['value', 'receipt_gas_used', 'gas_price']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Create derived columns
        df['date'] = df['block_timestamp'].dt.date
        df['hour'] = df['block_timestamp'].dt.hour
        df['day_of_week'] = df['block_timestamp'].dt.dayofweek
        
        # Convert ETH values from wei to ETH
        df['value_eth'] = df['value'] / 1e18
        df['gas_cost_eth'] = (df['receipt_gas_used'] * df['gas_price']) / 1e18
        
        # Create high-value transaction flag (>1 ETH)
        df['is_high_value'] = df['value_eth'] > 1.0
        
        # Sort by user and timestamp for efficient processing
        df.sort_values(['from_address', 'block_timestamp'], inplace=True)
        
        # Set analysis date (latest timestamp in data)
        self._analysis_date = df['block_timestamp'].max()
        
        self.logger.info("Data preparation completed")
    
    def _create_user_groups(self) -> None:
        """
        Create user groups for efficient iteration.
        """
        self._user_groups = self._interactions_df.groupby('from_address')
        unique_users = len(self._user_groups)
        
        self.logger.info(f"Created groups for {unique_users:,} unique users")
    
    def get_user_count(self) -> int:
        """
        Get the total number of unique users in the dataset.
        
        Returns:
            Number of unique users
        """
        if self._user_groups is None:
            return 0
        return len(self._user_groups)
    
    def get_interaction_count(self) -> int:
        """
        Get the total number of interactions in the dataset.
        
        Returns:
            Number of interactions
        """
        if self._interactions_df is None:
            return 0
        return len(self._interactions_df)
    
    def get_analysis_date(self) -> Optional[pd.Timestamp]:
        """
        Get the analysis date (latest timestamp in the data).
        
        Returns:
            Analysis date or None if no data loaded
        """
        return self._analysis_date
    
    def get_user_interactions(self, user_address: str) -> pd.DataFrame:
        """
        Get all interactions for a specific user.
        
        Args:
            user_address: The user's address
            
        Returns:
            DataFrame containing all interactions for the user
            
        Raises:
            ValueError: If user not found in data
        """
        if self._user_groups is None:
            raise ValueError("No interaction data loaded")
        
        try:
            return self._user_groups.get_group(user_address).copy()
        except KeyError:
            raise ValueError(f"User {user_address} not found in interaction data")
    
    def iter_user_interactions(self, chunk_size: Optional[int] = None) -> Iterator[Tuple[str, pd.DataFrame]]:
        """
        Iterate over user interactions in chunks for memory efficiency.
        
        Args:
            chunk_size: Number of users to process at once. If None, processes all users.
            
        Yields:
            Tuple of (user_address, user_interactions_dataframe)
        """
        if self._user_groups is None:
            raise ValueError("No interaction data loaded")
        
        if chunk_size is None:
            # Process all users
            for user_address, user_data in self._user_groups:
                yield user_address, user_data.copy()
        else:
            # Process in chunks
            user_addresses = list(self._user_groups.groups.keys())
            
            for i in range(0, len(user_addresses), chunk_size):
                chunk_addresses = user_addresses[i:i + chunk_size]
                
                for user_address in chunk_addresses:
                    user_data = self._user_groups.get_group(user_address)
                    yield user_address, user_data.copy()
    
    def get_protocol_summary(self) -> pd.DataFrame:
        """
        Get a summary of protocol categories in the data.
        
        Returns:
            DataFrame with protocol category statistics
        """
        if self._interactions_df is None:
            return pd.DataFrame()
        
        summary = self._interactions_df.groupby('protocol_category').agg({
            'transaction_hash': 'count',
            'from_address': 'nunique',
            'value_eth': ['sum', 'mean'],
            'gas_cost_eth': ['sum', 'mean']
        }).round(4)
        
        # Flatten column names
        summary.columns = [
            'total_interactions', 'unique_users', 'total_eth_value', 'avg_eth_value',
            'total_gas_cost', 'avg_gas_cost'
        ]
        
        return summary.sort_values('total_interactions', ascending=False)
    
    def get_user_summary(self) -> pd.DataFrame:
        """
        Get a summary of user activity levels.
        
        Returns:
            DataFrame with user activity statistics
        """
        if self._interactions_df is None:
            return pd.DataFrame()
        
        user_summary = self._interactions_df.groupby('from_address').agg({
            'transaction_hash': 'count',
            'protocol_category': 'nunique',
            'application': 'nunique',
            'value_eth': 'sum',
            'gas_cost_eth': 'sum',
            'block_timestamp': ['min', 'max']
        })
        
        # Flatten column names
        user_summary.columns = [
            'total_interactions', 'unique_protocols', 'unique_applications',
            'total_eth_value', 'total_gas_cost', 'first_interaction', 'last_interaction'
        ]
        
        # Calculate activity duration
        user_summary['activity_duration_days'] = (
            user_summary['last_interaction'] - user_summary['first_interaction']
        ).dt.days
        
        return user_summary
    
    def get_data_quality_report(self) -> Dict[str, any]:
        """
        Generate a data quality report for the loaded interactions.
        
        Returns:
            Dictionary containing data quality metrics
        """
        if self._interactions_df is None:
            return {}
        
        df = self._interactions_df
        
        report = {
            'total_interactions': len(df),
            'unique_users': df['from_address'].nunique(),
            'unique_contracts': df['to_address'].nunique(),
            'date_range': {
                'start': df['block_timestamp'].min(),
                'end': df['block_timestamp'].max(),
                'days': (df['block_timestamp'].max() - df['block_timestamp'].min()).days
            },
            'protocol_categories': df['protocol_category'].nunique(),
            'applications': df['application'].nunique(),
            'null_values': {
                col: df[col].isna().sum() for col in df.columns if df[col].isna().sum() > 0
            },
            'value_statistics': {
                'total_eth_transacted': df['value_eth'].sum(),
                'total_gas_cost_eth': df['gas_cost_eth'].sum(),
                'high_value_transactions': df['is_high_value'].sum(),
                'zero_value_transactions': (df['value_eth'] == 0).sum()
            }
        }
        
        return report
    
    def log_summary(self) -> None:
        """
        Log a summary of the loaded interaction data.
        """
        if self._interactions_df is None:
            self.logger.warning("No interaction data loaded")
            return
        
        report = self.get_data_quality_report()
        
        self.logger.info("=" * 60)
        self.logger.info("INTERACTION DATA SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total interactions: {report['total_interactions']:,}")
        self.logger.info(f"Unique users: {report['unique_users']:,}")
        self.logger.info(f"Unique contracts: {report['unique_contracts']:,}")
        self.logger.info(f"Date range: {report['date_range']['start']} to {report['date_range']['end']}")
        self.logger.info(f"Analysis period: {report['date_range']['days']} days")
        self.logger.info(f"Protocol categories: {report['protocol_categories']}")
        self.logger.info(f"Applications: {report['applications']}")
        self.logger.info(f"Total ETH transacted: {report['value_statistics']['total_eth_transacted']:.2f}")
        self.logger.info(f"Total gas cost: {report['value_statistics']['total_gas_cost_eth']:.2f} ETH")
        self.logger.info(f"High-value transactions (>1 ETH): {report['value_statistics']['high_value_transactions']:,}")
        
        if report['null_values']:
            self.logger.warning(f"Null values found: {report['null_values']}")
        
        self.logger.info("=" * 60) 