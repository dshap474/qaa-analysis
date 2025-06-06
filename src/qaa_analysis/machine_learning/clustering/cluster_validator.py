"""
Cluster Validator for QAA Analysis.

Validates clustering quality and stability.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.metrics import pairwise_distances
import logging

from .kmeans_clusterer import KMeansClusterer


class ClusterValidator:
    """
    Validate clustering results using multiple metrics and stability analysis.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize cluster validator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics_ = {}
        self.stability_results_ = None
    
    def validate_clustering(self, X: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """
        Calculate comprehensive validation metrics.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            labels: Cluster labels
            
        Returns:
            Dictionary of validation metrics
        """
        self.logger.info("Calculating clustering validation metrics")
        
        n_clusters = len(np.unique(labels))
        n_samples = len(labels)
        
        metrics = {}
        
        # Basic checks
        if n_clusters == 1:
            self.logger.warning("Only one cluster found - metrics may not be meaningful")
            return {
                'n_clusters': 1,
                'n_samples': n_samples,
                'silhouette_score': -1,
                'davies_bouldin_score': np.inf,
                'calinski_harabasz_score': 0,
                'mean_cluster_size': n_samples,
                'min_cluster_size': n_samples,
                'max_cluster_size': n_samples
            }
        
        # Internal validation metrics
        metrics['silhouette_score'] = silhouette_score(X, labels)
        metrics['davies_bouldin_score'] = davies_bouldin_score(X, labels)
        metrics['calinski_harabasz_score'] = calinski_harabasz_score(X, labels)
        
        # Cluster size statistics
        unique_labels, counts = np.unique(labels, return_counts=True)
        metrics['n_clusters'] = n_clusters
        metrics['n_samples'] = n_samples
        metrics['mean_cluster_size'] = np.mean(counts)
        metrics['std_cluster_size'] = np.std(counts)
        metrics['min_cluster_size'] = np.min(counts)
        metrics['max_cluster_size'] = np.max(counts)
        metrics['cluster_size_ratio'] = metrics['max_cluster_size'] / metrics['min_cluster_size']
        
        # Calculate cluster cohesion and separation
        cohesion, separation = self._calculate_cohesion_separation(X, labels)
        metrics['mean_cohesion'] = np.mean(cohesion)
        metrics['mean_separation'] = np.mean(separation)
        metrics['cohesion_separation_ratio'] = metrics['mean_cohesion'] / metrics['mean_separation']
        
        self.metrics_ = metrics
        return metrics
    
    def _calculate_cohesion_separation(self, X: np.ndarray, labels: np.ndarray) -> Tuple[List[float], List[float]]:
        """
        Calculate within-cluster cohesion and between-cluster separation.
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            
        Returns:
            Tuple of (cohesion_scores, separation_scores)
        """
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels)
        
        cohesion_scores = []
        separation_scores = []
        
        # Calculate cluster centers
        centers = []
        for label in unique_labels:
            mask = labels == label
            center = X[mask].mean(axis=0)
            centers.append(center)
        centers = np.array(centers)
        
        # Calculate cohesion (within-cluster distances)
        for label in unique_labels:
            mask = labels == label
            cluster_points = X[mask]
            if len(cluster_points) > 1:
                # Average distance to cluster center
                center = centers[label]
                distances = np.linalg.norm(cluster_points - center, axis=1)
                cohesion_scores.append(np.mean(distances))
            else:
                cohesion_scores.append(0)
        
        # Calculate separation (between-cluster distances)
        if n_clusters > 1:
            for i in range(n_clusters):
                min_dist = np.inf
                for j in range(n_clusters):
                    if i != j:
                        dist = np.linalg.norm(centers[i] - centers[j])
                        min_dist = min(min_dist, dist)
                separation_scores.append(min_dist)
        else:
            separation_scores = [0]
        
        return cohesion_scores, separation_scores
    
    def stability_analysis(self, X: np.ndarray, n_clusters: int, 
                          n_iterations: int = 10, subsample_ratio: float = 0.8) -> Dict[str, Any]:
        """
        Analyze clustering stability through multiple runs and subsampling.
        
        Args:
            X: Feature matrix
            n_clusters: Number of clusters
            n_iterations: Number of stability iterations
            subsample_ratio: Fraction of data to use in each iteration
            
        Returns:
            Dictionary with stability metrics
        """
        self.logger.info(f"Running stability analysis with {n_iterations} iterations")
        
        n_samples = X.shape[0]
        subsample_size = int(n_samples * subsample_ratio)
        
        all_metrics = []
        label_agreement_scores = []
        
        # Reference clustering on full data
        ref_clusterer = KMeansClusterer(n_clusters=n_clusters, random_state=42)
        ref_clusterer.fit(X)
        ref_labels = ref_clusterer.labels_
        
        for i in range(n_iterations):
            # Random subsample
            indices = np.random.choice(n_samples, subsample_size, replace=False)
            X_sub = X[indices]
            
            # Cluster subsample
            clusterer = KMeansClusterer(n_clusters=n_clusters, random_state=i)
            clusterer.fit(X_sub)
            
            # Get metrics
            metrics = clusterer.get_metrics()
            all_metrics.append(metrics)
            
            # Predict labels for full dataset
            pred_labels = clusterer.predict(X)
            
            # Calculate agreement with reference
            agreement = self._calculate_label_agreement(ref_labels, pred_labels)
            label_agreement_scores.append(agreement)
        
        # Aggregate results
        metrics_df = pd.DataFrame(all_metrics)
        
        stability_results = {
            'mean_silhouette': metrics_df['silhouette_score'].mean(),
            'std_silhouette': metrics_df['silhouette_score'].std(),
            'mean_davies_bouldin': metrics_df['davies_bouldin_score'].mean(),
            'std_davies_bouldin': metrics_df['davies_bouldin_score'].std(),
            'mean_label_agreement': np.mean(label_agreement_scores),
            'std_label_agreement': np.std(label_agreement_scores),
            'stability_score': np.mean(label_agreement_scores) / (1 + np.std(label_agreement_scores))
        }
        
        self.stability_results_ = stability_results
        return stability_results
    
    def _calculate_label_agreement(self, labels1: np.ndarray, labels2: np.ndarray) -> float:
        """
        Calculate agreement between two sets of cluster labels.
        
        Uses the Adjusted Rand Index which accounts for label permutations.
        
        Args:
            labels1: First set of labels
            labels2: Second set of labels
            
        Returns:
            Agreement score (0 to 1)
        """
        from sklearn.metrics import adjusted_rand_score
        return adjusted_rand_score(labels1, labels2)
    
    def generate_validation_report(self) -> str:
        """
        Generate a text report of validation results.
        
        Returns:
            Formatted validation report
        """
        report = "=" * 60 + "\n"
        report += "CLUSTERING VALIDATION REPORT\n"
        report += "=" * 60 + "\n\n"
        
        # Basic metrics
        if self.metrics_:
            report += "VALIDATION METRICS:\n"
            report += "-" * 30 + "\n"
            for metric, value in self.metrics_.items():
                if isinstance(value, float):
                    report += f"{metric:.<30} {value:.4f}\n"
                else:
                    report += f"{metric:.<30} {value}\n"
            report += "\n"
        
        # Stability results
        if self.stability_results_:
            report += "STABILITY ANALYSIS:\n"
            report += "-" * 30 + "\n"
            for metric, value in self.stability_results_.items():
                report += f"{metric:.<30} {value:.4f}\n"
            report += "\n"
        
        # Interpretation
        report += "INTERPRETATION:\n"
        report += "-" * 30 + "\n"
        
        if self.metrics_:
            silhouette = self.metrics_.get('silhouette_score', -1)
            if silhouette > 0.7:
                report += "• Strong cluster structure (silhouette > 0.7)\n"
            elif silhouette > 0.5:
                report += "• Reasonable cluster structure (silhouette > 0.5)\n"
            elif silhouette > 0.25:
                report += "• Weak cluster structure (silhouette > 0.25)\n"
            else:
                report += "• Poor cluster structure (silhouette < 0.25)\n"
            
            size_ratio = self.metrics_.get('cluster_size_ratio', 1)
            if size_ratio > 10:
                report += "• Warning: Highly imbalanced cluster sizes\n"
            elif size_ratio > 5:
                report += "• Moderately imbalanced cluster sizes\n"
            else:
                report += "• Well-balanced cluster sizes\n"
        
        if self.stability_results_:
            stability = self.stability_results_.get('mean_label_agreement', 0)
            if stability > 0.8:
                report += "• Highly stable clustering (agreement > 0.8)\n"
            elif stability > 0.6:
                report += "• Moderately stable clustering (agreement > 0.6)\n"
            else:
                report += "• Unstable clustering (agreement < 0.6)\n"
        
        return report