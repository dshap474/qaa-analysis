"""
Temporal Features Extractor for QAA Analysis.

This module extracts time-based behavioral features from user interactions,
including activity patterns, cadence, and lifecycle metrics.
"""

import logging
from typing import Dict, List, Optional, Any

import pandas as pd
import numpy as np

from .feature_extractor import FeatureExtractor


class TemporalFeatures(FeatureExtractor):
    """
    Extracts temporal behavioral features from user interactions.
    
    This includes activity frequency, timing patterns, lifecycle metrics,
    and transaction cadence analysis.
    """
    
    def __init__(self, analysis_date: Optional[pd.Timestamp] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the temporal features extractor.
        
        Args:
            analysis_date: Reference date for calculating recency metrics. 
                          If None, uses the latest timestamp in the data.
            logger: Optional logger instance
        """
        super().__init__("TemporalFeatures", logger)
        self.analysis_date = analysis_date
        
        # Initialize feature metadata
        self._initialize_metadata()
    
    def _initialize_metadata(self) -> None:
        """Initialize metadata for all features produced by this extractor."""
        
        temporal_features = {
            # Recency features
            'days_since_last_tx': ('Days since the last transaction', 'int64', '[0, inf)', 'Lower values indicate more recent activity'),
            'days_since_first_tx': ('Days since the first transaction', 'int64', '[0, inf)', 'Higher values indicate longer presence in DeFi'),
            
            # Activity frequency features
            'total_interactions': ('Total number of interactions', 'int64', '[1, inf)', 'Higher values indicate more active users'),
            'active_days': ('Number of unique days with transactions', 'int64', '[1, inf)', 'Higher values indicate more consistent activity'),
            'activity_duration_days': ('Days between first and last transaction', 'int64', '[0, inf)', 'Higher values indicate longer engagement period'),
            
            # Activity intensity features
            'tx_per_active_day': ('Average transactions per active day', 'float64', '[1, inf)', 'Higher values indicate more intensive usage'),
            'avg_time_between_tx_hours': ('Average time between consecutive transactions (hours)', 'float64', '[0, inf)', 'Lower values indicate more frequent activity'),
            'median_time_between_tx_hours': ('Median time between consecutive transactions (hours)', 'float64', '[0, inf)', 'Lower values indicate more consistent frequent activity'),
            
            # Activity patterns
            'weekend_activity_ratio': ('Proportion of transactions on weekends', 'float64', '[0, 1]', 'Higher values indicate weekend preference'),
            'night_activity_ratio': ('Proportion of transactions during night hours (22-06)', 'float64', '[0, 1]', 'Higher values indicate night owl behavior'),
            'business_hours_ratio': ('Proportion of transactions during business hours (09-17)', 'float64', '[0, 1]', 'Higher values indicate business hours preference'),
            
            # Activity distribution
            'activity_concentration_gini': ('Gini coefficient of daily activity distribution', 'float64', '[0, 1]', 'Higher values indicate more concentrated activity'),
            'max_daily_transactions': ('Maximum transactions in a single day', 'int64', '[1, inf)', 'Higher values indicate burst activity capability'),
            'activity_streak_days': ('Longest streak of consecutive active days', 'int64', '[1, inf)', 'Higher values indicate sustained engagement'),
            
            # Lifecycle features
            'early_adopter_score': ('Score indicating early adoption behavior', 'float64', '[0, 1]', 'Higher values indicate early DeFi adoption'),
            'activity_trend': ('Trend in activity over time (slope)', 'float64', '(-inf, inf)', 'Positive values indicate increasing activity'),
            'recent_activity_ratio': ('Proportion of activity in recent period (last 30 days)', 'float64', '[0, 1]', 'Higher values indicate recent engagement')
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
        
        # Ensure timestamp column is datetime
        if not pd.api.types.is_datetime64_any_dtype(user_interactions['block_timestamp']):
            user_interactions = user_interactions.copy()
            user_interactions['block_timestamp'] = pd.to_datetime(user_interactions['block_timestamp'])
        
        # Set analysis date if not provided
        if self.analysis_date is None:
            self.analysis_date = user_interactions['block_timestamp'].max()
        
        features = {}
        
        # Extract basic temporal features
        basic_features = self._extract_basic_temporal_features(user_interactions)
        features.update(basic_features)
        
        # Extract activity pattern features
        pattern_features = self._extract_activity_patterns(user_interactions)
        features.update(pattern_features)
        
        # Extract lifecycle features
        lifecycle_features = self._extract_lifecycle_features(user_interactions)
        features.update(lifecycle_features)
        
        return features
    
    def _extract_basic_temporal_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract basic temporal features like recency, frequency, and duration.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of basic temporal features
        """
        features = {}
        
        # Sort by timestamp
        df_sorted = df.sort_values('block_timestamp')
        timestamps = df_sorted['block_timestamp']
        
        # Recency features
        last_tx = timestamps.max()
        first_tx = timestamps.min()
        
        features['days_since_last_tx'] = (self.analysis_date - last_tx).days
        features['days_since_first_tx'] = (self.analysis_date - first_tx).days
        
        # Activity frequency features
        features['total_interactions'] = len(df)
        
        # Calculate active days
        active_dates = df['block_timestamp'].dt.date.nunique()
        features['active_days'] = active_dates
        
        # Activity duration
        activity_duration = (last_tx - first_tx).days
        features['activity_duration_days'] = max(activity_duration, 0)
        
        # Activity intensity
        features['tx_per_active_day'] = self.safe_divide(len(df), active_dates, 1.0)
        
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
        Extract activity pattern features like weekend/night activity.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of activity pattern features
        """
        features = {}
        
        # Add time-based columns if not present
        df_with_time = df.copy()
        df_with_time['hour'] = df_with_time['block_timestamp'].dt.hour
        df_with_time['day_of_week'] = df_with_time['block_timestamp'].dt.dayofweek
        df_with_time['date'] = df_with_time['block_timestamp'].dt.date
        
        total_tx = len(df_with_time)
        
        # Weekend activity (Saturday=5, Sunday=6)
        weekend_tx = len(df_with_time[df_with_time['day_of_week'].isin([5, 6])])
        features['weekend_activity_ratio'] = self.safe_divide(weekend_tx, total_tx)
        
        # Night activity (22:00 - 06:00)
        night_tx = len(df_with_time[
            (df_with_time['hour'] >= 22) | (df_with_time['hour'] <= 6)
        ])
        features['night_activity_ratio'] = self.safe_divide(night_tx, total_tx)
        
        # Business hours activity (09:00 - 17:00)
        business_tx = len(df_with_time[
            (df_with_time['hour'] >= 9) & (df_with_time['hour'] <= 17)
        ])
        features['business_hours_ratio'] = self.safe_divide(business_tx, total_tx)
        
        # Daily activity distribution
        daily_counts = df_with_time.groupby('date').size()
        
        # Activity concentration (Gini coefficient)
        features['activity_concentration_gini'] = self.calculate_gini_coefficient(daily_counts)
        
        # Maximum daily transactions
        features['max_daily_transactions'] = int(daily_counts.max()) if len(daily_counts) > 0 else 0
        
        # Activity streak (consecutive active days)
        features['activity_streak_days'] = self._calculate_activity_streak(daily_counts)
        
        return features
    
    def _extract_lifecycle_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract lifecycle and trend features.
        
        Args:
            df: User interactions DataFrame
            
        Returns:
            Dictionary of lifecycle features
        """
        features = {}
        
        # Sort by timestamp
        df_sorted = df.sort_values('block_timestamp')
        
        # Early adopter score (based on first transaction date)
        # This would need a reference "DeFi start date" - using a reasonable estimate
        defi_start_date = pd.Timestamp('2020-01-01')  # Approximate DeFi boom start
        first_tx = df_sorted['block_timestamp'].min()
        
        days_since_defi_start = (first_tx - defi_start_date).days
        max_days = (self.analysis_date - defi_start_date).days
        
        # Early adopter score: higher for earlier adoption
        early_adopter_raw = 1 - (days_since_defi_start / max_days)
        features['early_adopter_score'] = max(0, min(1, early_adopter_raw))
        
        # Activity trend (simple linear trend)
        if len(df_sorted) > 2:
            # Create time series of daily activity
            df_sorted['date'] = df_sorted['block_timestamp'].dt.date
            daily_activity = df_sorted.groupby('date').size().reset_index()
            daily_activity.columns = ['date', 'count']
            daily_activity['days_from_start'] = (
                pd.to_datetime(daily_activity['date']) - pd.to_datetime(daily_activity['date'].min())
            ).dt.days
            
            # Calculate trend (slope of linear regression)
            if len(daily_activity) > 1:
                x = daily_activity['days_from_start'].values
                y = daily_activity['count'].values
                
                # Simple linear regression slope
                n = len(x)
                slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2)
                features['activity_trend'] = slope
            else:
                features['activity_trend'] = 0.0
        else:
            features['activity_trend'] = 0.0
        
        # Recent activity ratio (last 30 days)
        recent_cutoff = self.analysis_date - pd.Timedelta(days=30)
        recent_tx = len(df_sorted[df_sorted['block_timestamp'] >= recent_cutoff])
        features['recent_activity_ratio'] = self.safe_divide(recent_tx, len(df_sorted))
        
        return features
    
    def _calculate_activity_streak(self, daily_counts: pd.Series) -> int:
        """
        Calculate the longest streak of consecutive active days.
        
        Args:
            daily_counts: Series with dates as index and transaction counts as values
            
        Returns:
            Length of longest activity streak in days
        """
        if len(daily_counts) == 0:
            return 0
        
        # Convert index to datetime if it's not already
        dates = pd.to_datetime(daily_counts.index)
        dates_sorted = sorted(dates)
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(dates_sorted)):
            # Check if consecutive days
            if (dates_sorted[i] - dates_sorted[i-1]).days == 1:
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
            # Recency features
            'days_since_last_tx',
            'days_since_first_tx',
            
            # Activity frequency features
            'total_interactions',
            'active_days',
            'activity_duration_days',
            
            # Activity intensity features
            'tx_per_active_day',
            'avg_time_between_tx_hours',
            'median_time_between_tx_hours',
            
            # Activity patterns
            'weekend_activity_ratio',
            'night_activity_ratio',
            'business_hours_ratio',
            
            # Activity distribution
            'activity_concentration_gini',
            'max_daily_transactions',
            'activity_streak_days',
            
            # Lifecycle features
            'early_adopter_score',
            'activity_trend',
            'recent_activity_ratio'
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
    
    def analyze_activity_patterns(self, user_interactions: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform detailed analysis of user activity patterns.
        
        Args:
            user_interactions: DataFrame containing all interactions for one user
            
        Returns:
            Dictionary with detailed activity pattern analysis
        """
        df = user_interactions.copy()
        df['hour'] = df['block_timestamp'].dt.hour
        df['day_of_week'] = df['block_timestamp'].dt.dayofweek
        df['date'] = df['block_timestamp'].dt.date
        
        analysis = {
            'hourly_distribution': df['hour'].value_counts().sort_index().to_dict(),
            'daily_distribution': df['day_of_week'].value_counts().sort_index().to_dict(),
            'most_active_hour': df['hour'].mode().iloc[0] if len(df) > 0 else None,
            'most_active_day': df['day_of_week'].mode().iloc[0] if len(df) > 0 else None,
            'activity_variance': df.groupby('date').size().var() if len(df) > 1 else 0
        }
        
        return analysis 