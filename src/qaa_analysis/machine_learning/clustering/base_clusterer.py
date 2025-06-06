"""
Base Clusterer for QAA Analysis.

Abstract base class defining the interface for all clustering algorithms.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
import json
import pickle
from pathlib import Path


class BaseClusterer(ABC):
    """
    Abstract base class for clustering algorithms.
    
    Provides common interface and functionality for all clustering implementations.
    """
    
    def __init__(self, 
                 random_state: int = 42,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the base clusterer.
        
        Args:
            random_state: Random seed for reproducibility
            logger: Optional logger instance
        """
        self.random_state = random_state
        self.logger = logger or logging.getLogger(__name__)
        
        # Model state
        self.is_fitted = False
        self.model = None
        self.labels_ = None
        self.n_clusters_ = None
        
        # Metadata
        self.fit_time_ = None
        self.n_samples_ = None
        self.n_features_ = None
        self.feature_names_ = None
        self.metadata_ = {
            'algorithm': self.__class__.__name__,
            'created_at': datetime.now().isoformat(),
            'random_state': random_state
        }
    
    @abstractmethod
    def fit(self, X: np.ndarray, feature_names: Optional[list] = None) -> 'BaseClusterer':
        """
        Fit the clustering model to the data.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
            feature_names: Optional list of feature names
            
        Returns:
            Self for method chaining
        """
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels for new data.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
            
        Returns:
            Cluster labels
        """
        pass
    
    def fit_predict(self, X: np.ndarray, feature_names: Optional[list] = None) -> np.ndarray:
        """
        Fit the model and return cluster labels.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
            feature_names: Optional list of feature names
            
        Returns:
            Cluster labels
        """
        self.fit(X, feature_names)
        return self.labels_
    
    def save_model(self, filepath: Path) -> None:
        """
        Save the fitted model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before saving")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model state
        model_state = {
            'model': self.model,
            'labels': self.labels_,
            'n_clusters': self.n_clusters_,
            'metadata': self.metadata_,
            'feature_names': self.feature_names_,
            'n_samples': self.n_samples_,
            'n_features': self.n_features_
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_state, f)
        
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: Path) -> None:
        """
        Load a fitted model from disk.
        
        Args:
            filepath: Path to the saved model
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_state = pickle.load(f)
        
        # Restore model state
        self.model = model_state['model']
        self.labels_ = model_state['labels']
        self.n_clusters_ = model_state['n_clusters']
        self.metadata_ = model_state['metadata']
        self.feature_names_ = model_state['feature_names']
        self.n_samples_ = model_state['n_samples']
        self.n_features_ = model_state['n_features']
        self.is_fitted = True
        
        self.logger.info(f"Model loaded from {filepath}")
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the clustering results.
        
        Returns:
            Dictionary with cluster statistics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        unique_labels, counts = np.unique(self.labels_, return_counts=True)
        
        summary = {
            'n_clusters': self.n_clusters_,
            'n_samples': self.n_samples_,
            'n_features': self.n_features_,
            'cluster_sizes': dict(zip(unique_labels.tolist(), counts.tolist())),
            'cluster_proportions': dict(zip(
                unique_labels.tolist(), 
                (counts / self.n_samples_).tolist()
            )),
            'metadata': self.metadata_
        }
        
        return summary
    
    def save_labels(self, filepath: Path, user_ids: Optional[pd.Series] = None) -> None:
        """
        Save cluster labels to CSV.
        
        Args:
            filepath: Path to save the labels
            user_ids: Optional series of user identifiers
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Create DataFrame with labels
        if user_ids is not None:
            df = pd.DataFrame({
                'user_id': user_ids,
                'cluster': self.labels_
            })
        else:
            df = pd.DataFrame({
                'sample_index': range(len(self.labels_)),
                'cluster': self.labels_
            })
        
        df.to_csv(filepath, index=False)
        self.logger.info(f"Cluster labels saved to {filepath}")
    
    def _validate_input(self, X: np.ndarray) -> np.ndarray:
        """
        Validate and prepare input data.
        
        Args:
            X: Input data
            
        Returns:
            Validated numpy array
        """
        # Convert to numpy if needed
        if isinstance(X, pd.DataFrame):
            if self.feature_names_ is None:
                self.feature_names_ = X.columns.tolist()
            X = X.values
        
        # Ensure 2D array
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        
        # Check for NaN/inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ValueError("Input contains NaN or infinite values")
        
        return X