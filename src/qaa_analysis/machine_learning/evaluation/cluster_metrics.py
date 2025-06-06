"""
Cluster Metrics for QAA Analysis.

Comprehensive metrics for evaluating clustering quality.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score, calinski_harabasz_score,
    silhouette_samples
)
import logging


class ClusterMetrics:
    """
    Calculate and analyze clustering quality metrics.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize cluster metrics calculator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics_ = None
        self.sample_silhouettes_ = None
    
    def calculate_metrics(self, X: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """
        Calculate comprehensive clustering metrics.
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            
        Returns:
            Dictionary of metrics
        """
        self.logger.info("Calculating clustering metrics")
        
        n_clusters = len(np.unique(labels))
        n_samples = len(labels)
        
        if n_clusters < 2:
            self.logger.warning("Less than 2 clusters found - metrics may not be meaningful")
            return {
                'n_clusters': n_clusters,
                'n_samples': n_samples,
                'silhouette_score': -1,
                'davies_bouldin_score': np.inf,
                'calinski_harabasz_score': 0
            }
        
        # Calculate metrics
        metrics = {
            'n_clusters': n_clusters,
            'n_samples': n_samples,
            'silhouette_score': silhouette_score(X, labels),
            'davies_bouldin_score': davies_bouldin_score(X, labels),
            'calinski_harabasz_score': calinski_harabasz_score(X, labels)
        }
        
        # Calculate per-sample silhouette scores
        self.sample_silhouettes_ = silhouette_samples(X, labels)
        
        # Add silhouette statistics
        metrics.update(self._calculate_silhouette_statistics(labels))
        
        # Add cluster size statistics
        metrics.update(self._calculate_size_statistics(labels))
        
        self.metrics_ = metrics
        return metrics
    
    def _calculate_silhouette_statistics(self, labels: np.ndarray) -> Dict[str, float]:
        """
        Calculate detailed silhouette statistics.
        
        Args:
            labels: Cluster labels
            
        Returns:
            Dictionary of silhouette statistics
        """
        if self.sample_silhouettes_ is None:
            return {}
        
        stats = {
            'silhouette_min': float(np.min(self.sample_silhouettes_)),
            'silhouette_max': float(np.max(self.sample_silhouettes_)),
            'silhouette_std': float(np.std(self.sample_silhouettes_))
        }
        
        # Per-cluster silhouette scores
        unique_labels = np.unique(labels)
        cluster_silhouettes = {}
        
        for label in unique_labels:
            mask = labels == label
            cluster_sil = self.sample_silhouettes_[mask]
            cluster_silhouettes[f'silhouette_cluster_{label}'] = float(np.mean(cluster_sil))
        
        stats.update(cluster_silhouettes)
        
        return stats
    
    def _calculate_size_statistics(self, labels: np.ndarray) -> Dict[str, float]:
        """
        Calculate cluster size statistics.
        
        Args:
            labels: Cluster labels
            
        Returns:
            Dictionary of size statistics
        """
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        stats = {
            'size_mean': float(np.mean(counts)),
            'size_std': float(np.std(counts)),
            'size_min': int(np.min(counts)),
            'size_max': int(np.max(counts)),
            'size_ratio': float(np.max(counts) / np.min(counts))
        }
        
        # Individual cluster sizes
        for label, count in zip(unique_labels, counts):
            stats[f'size_cluster_{label}'] = int(count)
        
        return stats
    
    def get_quality_assessment(self) -> str:
        """
        Get text assessment of clustering quality.
        
        Returns:
            Quality assessment string
        """
        if self.metrics_ is None:
            return "No metrics calculated yet"
        
        silhouette = self.metrics_['silhouette_score']
        db_score = self.metrics_['davies_bouldin_score']
        size_ratio = self.metrics_['size_ratio']
        
        # Silhouette assessment
        if silhouette > 0.7:
            sil_quality = "Excellent"
        elif silhouette > 0.5:
            sil_quality = "Good"
        elif silhouette > 0.25:
            sil_quality = "Fair"
        else:
            sil_quality = "Poor"
        
        # Davies-Bouldin assessment
        if db_score < 0.5:
            db_quality = "Excellent"
        elif db_score < 1.0:
            db_quality = "Good"
        elif db_score < 2.0:
            db_quality = "Fair"
        else:
            db_quality = "Poor"
        
        # Size balance assessment
        if size_ratio < 3:
            balance_quality = "Well-balanced"
        elif size_ratio < 10:
            balance_quality = "Moderately balanced"
        else:
            balance_quality = "Highly imbalanced"
        
        assessment = f"""
Clustering Quality Assessment:
- Silhouette Score: {silhouette:.3f} ({sil_quality})
- Davies-Bouldin Score: {db_score:.3f} ({db_quality})
- Cluster Size Balance: {balance_quality} (ratio: {size_ratio:.1f})

Overall: The clustering shows {sil_quality.lower()} separation with {balance_quality.lower()} cluster sizes.
"""
        
        return assessment.strip()
    
    def create_metrics_dataframe(self) -> pd.DataFrame:
        """
        Create a DataFrame with all metrics for easy viewing.
        
        Returns:
            DataFrame with metrics
        """
        if self.metrics_ is None:
            raise ValueError("Must calculate metrics first")
        
        # Separate different types of metrics
        main_metrics = {
            k: v for k, v in self.metrics_.items() 
            if not k.startswith(('silhouette_cluster_', 'size_cluster_'))
        }
        
        cluster_metrics = {}
        for k, v in self.metrics_.items():
            if k.startswith('silhouette_cluster_'):
                cluster_id = k.replace('silhouette_cluster_', '')
                if cluster_id not in cluster_metrics:
                    cluster_metrics[cluster_id] = {}
                cluster_metrics[cluster_id]['silhouette'] = v
            elif k.startswith('size_cluster_'):
                cluster_id = k.replace('size_cluster_', '')
                if cluster_id not in cluster_metrics:
                    cluster_metrics[cluster_id] = {}
                cluster_metrics[cluster_id]['size'] = v
        
        # Create main metrics DataFrame
        main_df = pd.DataFrame([main_metrics]).T
        main_df.columns = ['value']
        main_df.index.name = 'metric'
        
        # Create cluster metrics DataFrame
        if cluster_metrics:
            cluster_df = pd.DataFrame(cluster_metrics).T
            cluster_df.index.name = 'cluster'
        else:
            cluster_df = None
        
        return main_df, cluster_df