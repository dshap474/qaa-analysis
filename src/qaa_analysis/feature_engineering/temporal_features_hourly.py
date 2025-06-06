"""
Temporal Features Extractor for QAA Analysis (Hourly Version).

This module extracts time-based behavioral features from user interactions,
focusing on hourly patterns for single-day data analysis.
All timestamps are handled as timezone-aware (UTC).
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

import pandas as pd
import numpy as np

from .feature_extractor import FeatureExtractor


class TemporalFeatures(FeatureExtractor):
    """
    Extracts temporal behavioral features from user interactions.
    
    Focuses on hourly patterns and metrics suitable for single-day data analysis.
    All timestamps are handled as timezone-aware (UTC).
    """
    
    def __init__(self, analysis_date: Optional[pd.Timestamp] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the temporal features extractor.
        
        Args:
            analysis_date: Reference date for calculating metrics. 
                          Will be converted to timezone-aware (UTC) if not already.
            logger: Optional logger instance
        """
        super().__init__("TemporalFeatures", logger)
        
        # Ensure analysis_date is timezone-aware if provided
        if analysis_date is not None:
            if analysis_date.tz is None:
                # If naive, assume UTC
                self.analysis_date = analysis_date.tz_localize('UTC')
            else:
                # If already has timezone, convert to UTC
                self.analysis_date = analysis_date.tz_convert('UTC')
        else:
            self.analysis_date = None
        
        # Initialize feature metadata
        self._initialize_metadata()
    
    def _initialize_metadata(self) -> None:
        """Initialize metadata for all features produced by this extractor."""
        
        temporal_features = {
            # Activity frequency features
            'total_interactions': ('Total number of interactions', 'int64', '[1, inf)', 'Higher values indicate more active users'),
            'active_hours': ('Number of unique hours with transactions', 'int64', '[1, 24]', 'Higher values indicate activity spread across more hours'),
            'activity_duration_hours': ('Hours between first and last transaction', 'float64', '[0, 24)', 'Higher values indicate longer engagement period'),
            
            # Activity intensity features
            'tx_per_active_hour': ('Average transactions per active hour', 'float64', '[1, inf)', 'Higher values indicate more intensive usage'),
            'avg_time_between_tx_hours': ('Average time between consecutive transactions (hours)', 'float64', '[0, inf)', 'Lower values indicate more frequent activity'),
            'median_time_between_tx_hours': ('Median time between consecutive transactions (hours)', 'float64', '[0, inf)', 'Lower values indicate more consistent frequent activity'),
            
            # Activity patterns
            'night_activity_ratio': ('Proportion of transactions during night hours (22-06 UTC)', 'float64', '[0, 1]', 'Higher values indicate night owl behavior'),
            'business_hours_ratio': ('Proportion of transactions during business hours (09-17 UTC)', 'float64', '[0, 1]', 'Higher values indicate business hours preference'),
            
            # Activity distribution
            'hourly_concentration_gini': ('Gini coefficient of hourly activity distribution', 'float64', '[0, 1]', 'Higher values indicate more concentrated activity'),
            'max_hourly_transactions': ('Maximum transactions in a single hour', 'int64', '[1, inf)', 'Higher values indicate burst activity capability'),
            'activity_streak_hours': ('Longest streak of consecutive active hours', 'int64', '[1, 24]', 'Higher values indicate sustained engagement')
        }
        
        for feature_name, (description, data_type, range_val, interpretation) in temporal_features.items():
            self.add_feature_metadata(feature_name, description, data_type, range_val, interpretation)
    
    def extract_features(self, user_interactions: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract temporal features for a single user.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary mapping feature names to their values
        """
        # Validate input data
        required_columns = ['block_timestamp']
        self.validate_input_data(user_interactions, required_columns)
        
        # Ensure timestamp column is datetime and timezone-aware
        if not pd.api.types.is_datetime64_any_dtype(user_interactions['block_timestamp']):
            user_interactions = user_interactions.copy()
            user_interactions['block_timestamp'] = pd.to_datetime(user_interactions['block_timestamp'])
        
        # Make timestamps timezone-aware if they aren't already
        if user_interactions['block_timestamp'].dt.tz is None:
            user_interactions = user_interactions.copy()
            user_interactions['block_timestamp'] = user_interactions['block_timestamp'].dt.tz_localize('UTC')
        else:
            # Convert to UTC if in different timezone
            user_interactions = user_interactions.copy()
            user_interactions['block_timestamp'] = user_interactions['block_timestamp'].dt.tz_convert('UTC')
        
        # Set analysis date if not provided
        if self.analysis_date is None:
            # Use the maximum timestamp from the data, ensuring it's timezone-aware
            max_timestamp = user_interactions['block_timestamp'].max()
            if pd.isna(max_timestamp):
                # If no valid timestamps, use current UTC time
                self.analysis_date = pd.Timestamp.now(tz='UTC')
            else:
                self.analysis_date = max_timestamp
        
        features = {}
        
        # Extract basic temporal features
        basic_features = self._extract_basic_temporal_features(user_interactions)
        features.update(basic_features)
        
        # Extract activity pattern features
        pattern_features = self._extract_activity_patterns(user_interactions)
        features.update(pattern_features)
        
        return features
    
    def _extract_basic_temporal_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract basic temporal features focused on hourly metrics.
        
        Args:
            df: User interactions DataFrame with timezone-aware timestamps
            
        Returns:
            Dictionary of basic temporal features
        """
        features = {}
        
        # Sort by timestamp
        df_sorted = df.sort_values('block_timestamp')
        timestamps = df_sorted['block_timestamp']
        
        # Activity frequency features
        features['total_interactions'] = len(df)
        
        # Calculate active hours (unique hours in the day)
        # Extract hour of day for each transaction
        active_hours = df['block_timestamp'].dt.hour.nunique()
        features['active_hours'] = active_hours
        
        # Activity duration in hours
        first_tx = timestamps.min()
        last_tx = timestamps.max()
        duration_seconds = (last_tx - first_tx).total_seconds()
        duration_hours = duration_seconds / 3600.0
        features['activity_duration_hours'] = max(duration_hours, 0.0)
        
        # Activity intensity
        features['tx_per_active_hour'] = self.safe_divide(len(df), active_hours, 1.0)
        
        # Time between transactions
        if len(timestamps) > 1:
            time_diffs = timestamps.diff().dropna()
            avg_time_between = time_diffs.mean().total_seconds() / 3600  # Convert to hours
            median_time_between = time_diffs.median().total_seconds() / 3600
            
            features['avg_time_between_tx_hours'] = avg_time_between
            features['median_time_between_tx_hours'] = median_time_between
        else:
            features['avg_time_between_tx_hours'] = 0.0
            features['median_time_between_tx_hours'] = 0.0
        
        return features
    
    def _extract_activity_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract activity pattern features like night/business hours activity.
        
        Args:
            df: User interactions DataFrame with timezone-aware timestamps
            
        Returns:
            Dictionary of activity pattern features
        """
        features = {}
        
        # Add time-based columns if not present (using UTC time)
        df_with_time = df.copy()
        df_with_time['hour'] = df_with_time['block_timestamp'].dt.hour
        
        total_tx = len(df_with_time)
        
        # Night activity (22:00 - 06:00 UTC)
        night_tx = len(df_with_time[
            (df_with_time['hour'] >= 22) | (df_with_time['hour'] <= 6)
        ])
        features['night_activity_ratio'] = self.safe_divide(night_tx, total_tx)
        
        # Business hours activity (09:00 - 17:00 UTC)
        business_tx = len(df_with_time[
            (df_with_time['hour'] >= 9) & (df_with_time['hour'] <= 17)
        ])
        features['business_hours_ratio'] = self.safe_divide(business_tx, total_tx)
        
        # Hourly activity distribution
        hourly_counts = df_with_time.groupby('hour').size()
        
        # Activity concentration (Gini coefficient for hourly distribution)
        # Fill in missing hours with zeros for proper Gini calculation
        all_hours = pd.Series(0, index=range(24))
        all_hours.update(hourly_counts)
        features['hourly_concentration_gini'] = self.calculate_gini_coefficient(all_hours)
        
        # Maximum hourly transactions
        features['max_hourly_transactions'] = int(hourly_counts.max()) if len(hourly_counts) > 0 else 0
        
        # Activity streak (consecutive active hours)
        features['activity_streak_hours'] = self._calculate_hourly_streak(hourly_counts)
        
        return features
    
    def _calculate_hourly_streak(self, hourly_counts: pd.Series) -> int:
        """
        Calculate the longest streak of consecutive active hours.
        
        Args:
            hourly_counts: Series with hours as index and transaction counts as values
            
        Returns:
            Length of longest activity streak in hours
        """
        if len(hourly_counts) == 0:
            return 0
        
        # Get active hours (hours with transactions)
        active_hours = sorted(hourly_counts.index.tolist())
        
        if len(active_hours) == 0:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(active_hours)):
            # Check if consecutive hours (considering wrap-around from 23 to 0)
            if active_hours[i] == active_hours[i-1] + 1 or (active_hours[i] == 0 and active_hours[i-1] == 23):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_feature_names(self) -> List[str]:
        """
        Get the list of feature names that this extractor produces.
        
        Returns:
            List of feature names
        """
        return [
            # Activity frequency features
            'total_interactions',
            'active_hours',
            'activity_duration_hours',
            
            # Activity intensity features
            'tx_per_active_hour',
            'avg_time_between_tx_hours',
            'median_time_between_tx_hours',
            
            # Activity patterns
            'night_activity_ratio',
            'business_hours_ratio',
            
            # Activity distribution
            'hourly_concentration_gini',
            'max_hourly_transactions',
            'activity_streak_hours'
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