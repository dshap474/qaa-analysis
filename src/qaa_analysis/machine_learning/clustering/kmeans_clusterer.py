"""
K-Means Clusterer for QAA Analysis.

Implementation of K-Means clustering for behavioral segmentation.
"""

import time
from typing import Optional, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

from .base_clusterer import BaseClusterer


class KMeansClusterer(BaseClusterer):
    """
    K-Means clustering implementation for behavioral segmentation.
    
    Wrapper around scikit-learn's KMeans with additional functionality
    for the QAA analysis use case.
    """
    
    def __init__(self,
                 n_clusters: int = 8,
                 init: str = 'k-means++',
                 n_init: int = 10,
                 max_iter: int = 300,
                 random_state: int = 42,
                 logger: Optional[Any] = None):
        """
        Initialize K-Means clusterer.
        
        Args:
            n_clusters: Number of clusters to form
            init: Method for initialization ('k-means++', 'random')
            n_init: Number of times to run k-means with different seeds
            max_iter: Maximum iterations for a single run
            random_state: Random seed for reproducibility
            logger: Optional logger instance
        """
        super().__init__(random_state=random_state, logger=logger)
        
        self.n_clusters = n_clusters
        self.init = init
        self.n_init = n_init
        self.max_iter = max_iter
        
        # Additional K-Means specific attributes
        self.inertia_ = None
        self.cluster_centers_ = None
        self.n_iter_ = None
        
        # Validation metrics
        self.silhouette_score_ = None
        self.davies_bouldin_score_ = None
        self.calinski_harabasz_score_ = None
        
        # Update metadata
        self.metadata_.update({
            'n_clusters': n_clusters,
            'init': init,
            'n_init': n_init,
            'max_iter': max_iter
        })
    
    def fit(self, X: np.ndarray, feature_names: Optional[list] = None) -> 'KMeansClusterer':
        """
        Fit K-Means clustering model.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
            feature_names: Optional list of feature names
            
        Returns:
            Self for method chaining
        """
        self.logger.info(f"Fitting K-Means with {self.n_clusters} clusters")
        
        # Validate input
        X = self._validate_input(X)
        self.n_samples_, self.n_features_ = X.shape
        
        if feature_names is not None:
            self.feature_names_ = feature_names
        
        # Record start time
        start_time = time.time()
        
        # Initialize and fit K-Means
        self.model = KMeans(
            n_clusters=self.n_clusters,
            init=self.init,
            n_init=self.n_init,
            max_iter=self.max_iter,
            random_state=self.random_state
        )
        
        self.labels_ = self.model.fit_predict(X)
        self.n_clusters_ = self.n_clusters
        
        # Store additional attributes
        self.inertia_ = self.model.inertia_
        self.cluster_centers_ = self.model.cluster_centers_
        self.n_iter_ = self.model.n_iter_
        
        # Calculate validation metrics
        self._calculate_metrics(X)
        
        # Record fit time
        self.fit_time_ = time.time() - start_time
        self.is_fitted = True
        
        # Update metadata
        self.metadata_.update({
            'fit_time': self.fit_time_,
            'n_samples': self.n_samples_,
            'n_features': self.n_features_,
            'inertia': self.inertia_,
            'n_iterations': self.n_iter_
        })
        
        self.logger.info(
            f"K-Means fitting completed in {self.fit_time_:.2f}s. "
            f"Inertia: {self.inertia_:.2f}, Silhouette: {self.silhouette_score_:.3f}"
        )
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels for new data.
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
            
        Returns:
            Predicted cluster labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = self._validate_input(X)
        
        # Check feature dimensions
        if X.shape[1] != self.n_features_:
            raise ValueError(
                f"Expected {self.n_features_} features, got {X.shape[1]}"
            )
        
        return self.model.predict(X)
    
    def _calculate_metrics(self, X: np.ndarray) -> None:
        """
        Calculate clustering quality metrics.
        
        Args:
            X: Feature matrix used for clustering
        """
        if self.n_clusters_ > 1 and self.n_clusters_ < self.n_samples_:
            # Silhouette score: higher is better (-1 to 1)
            self.silhouette_score_ = silhouette_score(X, self.labels_)
            
            # Davies-Bouldin score: lower is better (0 to inf)
            self.davies_bouldin_score_ = davies_bouldin_score(X, self.labels_)
            
            # Calinski-Harabasz score: higher is better
            self.calinski_harabasz_score_ = calinski_harabasz_score(X, self.labels_)
        else:
            self.silhouette_score_ = -1
            self.davies_bouldin_score_ = np.inf
            self.calinski_harabasz_score_ = 0
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get clustering quality metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        return {
            'inertia': self.inertia_,
            'silhouette_score': self.silhouette_score_,
            'davies_bouldin_score': self.davies_bouldin_score_,
            'calinski_harabasz_score': self.calinski_harabasz_score_
        }
    
    def get_cluster_centers(self) -> np.ndarray:
        """
        Get cluster centroids.
        
        Returns:
            Array of cluster centers (n_clusters, n_features)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        return self.cluster_centers_
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform X to cluster-distance space.
        
        Args:
            X: Feature matrix
            
        Returns:
            Distance to each cluster center
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        X = self._validate_input(X)
        return self.model.transform(X)
    
    def get_feature_importance(self) -> Dict[str, np.ndarray]:
        """
        Calculate feature importance based on cluster centers.
        
        Returns:
            Dictionary with feature importance metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        # Calculate variance of each feature across cluster centers
        center_variance = np.var(self.cluster_centers_, axis=0)
        
        # Calculate mean absolute deviation from global mean
        global_mean = np.mean(self.cluster_centers_, axis=0)
        mean_abs_deviation = np.mean(
            np.abs(self.cluster_centers_ - global_mean), 
            axis=0
        )
        
        # Normalize to 0-1 range
        if np.max(center_variance) > 0:
            center_variance_norm = center_variance / np.max(center_variance)
        else:
            center_variance_norm = center_variance
            
        if np.max(mean_abs_deviation) > 0:
            mad_norm = mean_abs_deviation / np.max(mean_abs_deviation)
        else:
            mad_norm = mean_abs_deviation
        
        return {
            'center_variance': center_variance,
            'center_variance_normalized': center_variance_norm,
            'mean_absolute_deviation': mean_abs_deviation,
            'mean_absolute_deviation_normalized': mad_norm
        }