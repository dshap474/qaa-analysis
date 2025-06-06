"""
Feature Preprocessor for QAA Analysis.

Handles feature scaling, outlier detection, and transformation.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.compose import ColumnTransformer
import pickle
from pathlib import Path
import logging


class FeaturePreprocessor:
    """
    Preprocess features for clustering analysis.
    
    Handles:
    - Feature scaling (StandardScaler, MinMaxScaler, RobustScaler)
    - Outlier handling
    - Log transformation for skewed features
    - Missing value imputation
    """
    
    def __init__(self,
                 scaling_method: str = 'robust',
                 handle_outliers: bool = True,
                 outlier_threshold: float = 3.0,
                 log_transform_threshold: float = 2.0,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize feature preprocessor.
        
        Args:
            scaling_method: Method for scaling ('standard', 'minmax', 'robust')
            handle_outliers: Whether to cap outliers
            outlier_threshold: Z-score threshold for outlier detection
            log_transform_threshold: Skewness threshold for log transformation
            logger: Optional logger instance
        """
        self.scaling_method = scaling_method
        self.handle_outliers = handle_outliers
        self.outlier_threshold = outlier_threshold
        self.log_transform_threshold = log_transform_threshold
        self.logger = logger or logging.getLogger(__name__)
        
        # Preprocessing state
        self.scaler_ = None
        self.feature_names_ = None
        self.log_transformed_features_ = []
        self.outlier_bounds_ = {}
        self.is_fitted_ = False
        
        # Statistics
        self.preprocessing_stats_ = {}
    
    def fit(self, X: pd.DataFrame) -> 'FeaturePreprocessor':
        """
        Fit the preprocessor on the data.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Self for method chaining
        """
        self.logger.info("Fitting feature preprocessor")
        
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        self.feature_names_ = X.columns.tolist()
        X_processed = X.copy()
        
        # Step 1: Handle missing values
        X_processed = self._handle_missing_values(X_processed)
        
        # Step 2: Identify and transform skewed features
        if self.log_transform_threshold > 0:
            X_processed = self._identify_log_transform_features(X_processed)
        
        # Step 3: Handle outliers
        if self.handle_outliers:
            X_processed = self._fit_outlier_bounds(X_processed)
        
        # Step 4: Fit scaler
        self._fit_scaler(X_processed)
        
        self.is_fitted_ = True
        
        # Calculate preprocessing statistics
        self._calculate_statistics(X, X_processed)
        
        return self
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform features using fitted preprocessing.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Transformed feature array
        """
        if not self.is_fitted_:
            raise ValueError("Preprocessor must be fitted first")
        
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        
        # Check feature names match
        if X.columns.tolist() != self.feature_names_:
            raise ValueError("Feature names don't match fitted data")
        
        X_processed = X.copy()
        
        # Apply transformations in same order as fit
        X_processed = self._handle_missing_values(X_processed)
        X_processed = self._apply_log_transform(X_processed)
        
        if self.handle_outliers:
            X_processed = self._apply_outlier_bounds(X_processed)
        
        # Apply scaling
        X_scaled = self.scaler_.transform(X_processed)
        
        return X_scaled
    
    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit and transform in one step.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Transformed feature array
        """
        self.fit(X)
        return self.transform(X)
    
    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values with median imputation.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            DataFrame with imputed values
        """
        missing_counts = X.isnull().sum()
        if missing_counts.any():
            self.logger.warning(f"Found {missing_counts.sum()} missing values")
            X = X.fillna(X.median())
        
        return X
    
    def _identify_log_transform_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Identify and log-transform highly skewed features.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            DataFrame with log-transformed features
        """
        self.log_transformed_features_ = []
        
        for col in X.columns:
            skewness = X[col].skew()
            
            if abs(skewness) > self.log_transform_threshold:
                # Check if all values are positive
                if X[col].min() > 0:
                    self.logger.info(f"Log-transforming {col} (skewness: {skewness:.2f})")
                    X[col] = np.log1p(X[col])
                    self.log_transformed_features_.append(col)
                elif X[col].min() >= 0:
                    # Add small constant to handle zeros
                    self.logger.info(f"Log-transforming {col} with offset (skewness: {skewness:.2f})")
                    X[col] = np.log1p(X[col] + 1e-8)
                    self.log_transformed_features_.append(col)
        
        return X
    
    def _apply_log_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Apply log transformation to identified features.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Transformed DataFrame
        """
        X_transformed = X.copy()
        
        for col in self.log_transformed_features_:
            if X_transformed[col].min() > 0:
                X_transformed[col] = np.log1p(X_transformed[col])
            else:
                X_transformed[col] = np.log1p(X_transformed[col] + 1e-8)
        
        return X_transformed
    
    def _fit_outlier_bounds(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate outlier bounds using z-score method.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            DataFrame with outliers capped
        """
        self.outlier_bounds_ = {}
        X_capped = X.copy()
        
        for col in X.columns:
            mean = X[col].mean()
            std = X[col].std()
            
            if std > 0:
                z_scores = np.abs((X[col] - mean) / std)
                outliers = z_scores > self.outlier_threshold
                
                if outliers.any():
                    # Calculate bounds
                    lower_bound = mean - self.outlier_threshold * std
                    upper_bound = mean + self.outlier_threshold * std
                    
                    self.outlier_bounds_[col] = {
                        'lower': lower_bound,
                        'upper': upper_bound
                    }
                    
                    # Cap outliers
                    X_capped[col] = X_capped[col].clip(lower=lower_bound, upper=upper_bound)
                    
                    n_outliers = outliers.sum()
                    self.logger.info(f"Capped {n_outliers} outliers in {col}")
        
        return X_capped
    
    def _apply_outlier_bounds(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Apply fitted outlier bounds to new data.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            DataFrame with outliers capped
        """
        X_capped = X.copy()
        
        for col, bounds in self.outlier_bounds_.items():
            X_capped[col] = X_capped[col].clip(
                lower=bounds['lower'], 
                upper=bounds['upper']
            )
        
        return X_capped
    
    def _fit_scaler(self, X: pd.DataFrame) -> None:
        """
        Fit the selected scaler.
        
        Args:
            X: Feature DataFrame
        """
        if self.scaling_method == 'standard':
            self.scaler_ = StandardScaler()
        elif self.scaling_method == 'minmax':
            self.scaler_ = MinMaxScaler()
        elif self.scaling_method == 'robust':
            self.scaler_ = RobustScaler()
        else:
            raise ValueError(f"Unknown scaling method: {self.scaling_method}")
        
        self.scaler_.fit(X)
        self.logger.info(f"Fitted {self.scaling_method} scaler")
    
    def _calculate_statistics(self, X_original: pd.DataFrame, X_processed: pd.DataFrame) -> None:
        """
        Calculate preprocessing statistics.
        
        Args:
            X_original: Original feature DataFrame
            X_processed: Processed feature DataFrame
        """
        self.preprocessing_stats_ = {
            'n_features': len(self.feature_names_),
            'n_log_transformed': len(self.log_transformed_features_),
            'n_features_with_outliers': len(self.outlier_bounds_),
            'scaling_method': self.scaling_method
        }
    
    def save(self, filepath: Path) -> None:
        """
        Save preprocessor to disk.
        
        Args:
            filepath: Path to save the preprocessor
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        
        self.logger.info(f"Preprocessor saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: Path) -> 'FeaturePreprocessor':
        """
        Load preprocessor from disk.
        
        Args:
            filepath: Path to the saved preprocessor
            
        Returns:
            Loaded preprocessor instance
        """
        with open(filepath, 'rb') as f:
            preprocessor = pickle.load(f)
        
        return preprocessor
    
    def get_preprocessing_summary(self) -> Dict[str, Any]:
        """
        Get summary of preprocessing steps applied.
        
        Returns:
            Dictionary with preprocessing information
        """
        if not self.is_fitted_:
            raise ValueError("Preprocessor must be fitted first")
        
        summary = {
            'scaling_method': self.scaling_method,
            'handle_outliers': self.handle_outliers,
            'outlier_threshold': self.outlier_threshold,
            'log_transform_threshold': self.log_transform_threshold,
            'statistics': self.preprocessing_stats_,
            'log_transformed_features': self.log_transformed_features_,
            'features_with_outliers': list(self.outlier_bounds_.keys())
        }
        
        return summary