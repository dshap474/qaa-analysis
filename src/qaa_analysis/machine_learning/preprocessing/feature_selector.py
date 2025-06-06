"""
Feature Selector for QAA Analysis.

Selects most relevant features for clustering.
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Tuple
from sklearn.feature_selection import VarianceThreshold
import logging


class FeatureSelector:
    """
    Select relevant features for clustering.
    
    Methods:
    - Remove low variance features
    - Remove highly correlated features
    - Select top K features based on variance
    """
    
    def __init__(self,
                 variance_threshold: float = 0.01,
                 correlation_threshold: float = 0.95,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize feature selector.
        
        Args:
            variance_threshold: Minimum variance to keep feature
            correlation_threshold: Maximum correlation between features
            logger: Optional logger instance
        """
        self.variance_threshold = variance_threshold
        self.correlation_threshold = correlation_threshold
        self.logger = logger or logging.getLogger(__name__)
        
        # Selection state
        self.selected_features_ = None
        self.removed_features_ = {}
        self.feature_names_ = None
        self.is_fitted_ = False
    
    def fit(self, X: pd.DataFrame) -> 'FeatureSelector':
        """
        Fit the feature selector.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Self for method chaining
        """
        self.logger.info("Fitting feature selector")
        
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        self.feature_names_ = X.columns.tolist()
        selected_features = self.feature_names_.copy()
        self.removed_features_ = {
            'low_variance': [],
            'high_correlation': []
        }
        
        # Step 1: Remove low variance features
        low_var_features = self._identify_low_variance_features(X)
        selected_features = [f for f in selected_features if f not in low_var_features]
        self.removed_features_['low_variance'] = low_var_features
        
        # Step 2: Remove highly correlated features
        if len(selected_features) > 1:
            X_selected = X[selected_features]
            high_corr_features = self._identify_correlated_features(X_selected)
            selected_features = [f for f in selected_features if f not in high_corr_features]
            self.removed_features_['high_correlation'] = high_corr_features
        
        self.selected_features_ = selected_features
        self.is_fitted_ = True
        
        self.logger.info(
            f"Selected {len(self.selected_features_)} features "
            f"(removed {len(self.feature_names_) - len(self.selected_features_)})"
        )
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Select features from DataFrame.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            DataFrame with selected features
        """
        if not self.is_fitted_:
            raise ValueError("Selector must be fitted first")
        
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        return X[self.selected_features_]
    
    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform in one step.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            DataFrame with selected features
        """
        self.fit(X)
        return self.transform(X)
    
    def _identify_low_variance_features(self, X: pd.DataFrame) -> List[str]:
        """
        Identify features with low variance.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            List of low variance feature names
        """
        low_var_features = []
        
        for col in X.columns:
            variance = X[col].var()
            if variance < self.variance_threshold:
                low_var_features.append(col)
                self.logger.info(f"Removing low variance feature: {col} (var={variance:.4f})")
        
        return low_var_features
    
    def _identify_correlated_features(self, X: pd.DataFrame) -> List[str]:
        """
        Identify highly correlated features and select which to remove.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            List of features to remove
        """
        # Calculate correlation matrix
        corr_matrix = X.corr().abs()
        
        # Find highly correlated pairs
        upper_tri = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        
        # Find features to remove
        to_remove = set()
        
        for column in upper_tri.columns:
            if column in to_remove:
                continue
                
            # Find features correlated with this one
            correlated = upper_tri.index[upper_tri[column] > self.correlation_threshold].tolist()
            
            if correlated:
                # Keep the feature with higher variance, remove others
                features = [column] + correlated
                variances = {f: X[f].var() for f in features}
                keep_feature = max(variances, key=variances.get)
                
                for f in features:
                    if f != keep_feature and f not in to_remove:
                        to_remove.add(f)
                        self.logger.info(
                            f"Removing correlated feature: {f} "
                            f"(corr with {keep_feature} = {corr_matrix.loc[f, keep_feature]:.3f})"
                        )
        
        return list(to_remove)
    
    def get_selection_summary(self) -> dict:
        """
        Get summary of feature selection.
        
        Returns:
            Dictionary with selection information
        """
        if not self.is_fitted_:
            raise ValueError("Selector must be fitted first")
        
        summary = {
            'n_original_features': len(self.feature_names_),
            'n_selected_features': len(self.selected_features_),
            'n_removed_features': len(self.feature_names_) - len(self.selected_features_),
            'removed_low_variance': len(self.removed_features_['low_variance']),
            'removed_high_correlation': len(self.removed_features_['high_correlation']),
            'selected_features': self.selected_features_,
            'removed_features': self.removed_features_
        }
        
        return summary