"""
Optimal K Finder for K-Means Clustering.

Implements multiple methods to determine the optimal number of clusters.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
import logging
from pathlib import Path

from .kmeans_clusterer import KMeansClusterer


class OptimalKFinder:
    """
    Find optimal number of clusters using multiple methods.
    
    Methods implemented:
    - Elbow method (inertia)
    - Silhouette analysis
    - Davies-Bouldin index
    - Calinski-Harabasz index
    """
    
    def __init__(self, 
                 min_k: int = 2,
                 max_k: int = 15,
                 random_state: int = 42,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize optimal K finder.
        
        Args:
            min_k: Minimum number of clusters to test
            max_k: Maximum number of clusters to test
            random_state: Random seed for reproducibility
            logger: Optional logger instance
        """
        self.min_k = min_k
        self.max_k = max_k
        self.random_state = random_state
        self.logger = logger or logging.getLogger(__name__)
        
        # Results storage
        self.results_ = None
        self.optimal_k_ = None
        self.X_ = None
    
    def find_optimal_k(self, X: np.ndarray, n_init: int = 10) -> int:
        """
        Find optimal number of clusters using multiple metrics.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            n_init: Number of initializations for each K
            
        Returns:
            Recommended optimal K
        """
        self.logger.info(f"Finding optimal K from {self.min_k} to {self.max_k}")
        
        self.X_ = X
        results = []
        
        # Test each value of K
        for k in range(self.min_k, self.max_k + 1):
            self.logger.info(f"Testing K={k}")
            
            # Fit K-Means
            kmeans = KMeansClusterer(
                n_clusters=k,
                n_init=n_init,
                random_state=self.random_state,
                logger=self.logger
            )
            kmeans.fit(X)
            
            # Get metrics
            metrics = kmeans.get_metrics()
            metrics['k'] = k
            metrics['labels'] = kmeans.labels_
            
            results.append(metrics)
        
        # Convert to DataFrame for easier analysis
        self.results_ = pd.DataFrame(results)
        
        # Calculate optimal K using different methods
        self.optimal_k_ = self._calculate_optimal_k()
        
        self.logger.info(f"Optimal K determined: {self.optimal_k_}")
        
        return self.optimal_k_
    
    def _calculate_optimal_k(self) -> int:
        """
        Calculate optimal K using multiple methods and combine results.
        
        Returns:
            Recommended optimal K
        """
        recommendations = {}
        
        # Method 1: Elbow method on inertia
        elbow_k = self._find_elbow_point(
            self.results_['k'].values,
            self.results_['inertia'].values
        )
        recommendations['elbow'] = elbow_k
        
        # Method 2: Maximum silhouette score
        silhouette_k = self.results_.loc[
            self.results_['silhouette_score'].idxmax(), 'k'
        ]
        recommendations['silhouette'] = int(silhouette_k)
        
        # Method 3: Minimum Davies-Bouldin score
        davies_bouldin_k = self.results_.loc[
            self.results_['davies_bouldin_score'].idxmin(), 'k'
        ]
        recommendations['davies_bouldin'] = int(davies_bouldin_k)
        
        # Method 4: Maximum Calinski-Harabasz score
        calinski_k = self.results_.loc[
            self.results_['calinski_harabasz_score'].idxmax(), 'k'
        ]
        recommendations['calinski_harabasz'] = int(calinski_k)
        
        self.logger.info(f"Method recommendations: {recommendations}")
        
        # Use majority vote or median
        recommended_k = int(np.median(list(recommendations.values())))
        
        return recommended_k
    
    def _find_elbow_point(self, k_values: np.ndarray, inertias: np.ndarray) -> int:
        """
        Find elbow point using the kneedle algorithm.
        
        Args:
            k_values: Array of K values
            inertias: Array of inertia values
            
        Returns:
            K value at elbow point
        """
        # Normalize the data
        k_norm = (k_values - k_values.min()) / (k_values.max() - k_values.min())
        inertia_norm = (inertias - inertias.min()) / (inertias.max() - inertias.min())
        
        # Calculate differences
        diffs = np.diff(inertia_norm)
        diffs2 = np.diff(diffs)
        
        # Find elbow as point of maximum curvature
        if len(diffs2) > 0:
            elbow_idx = np.argmax(diffs2) + 2  # +2 because of double diff
            elbow_k = k_values[min(elbow_idx, len(k_values) - 1)]
        else:
            elbow_k = k_values[len(k_values) // 2]  # Default to middle
        
        return int(elbow_k)
    
    def plot_metrics(self, save_path: Optional[Path] = None) -> None:
        """
        Plot all metrics for visual inspection.
        
        Args:
            save_path: Optional path to save the plot
        """
        if self.results_ is None:
            raise ValueError("Must run find_optimal_k first")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Optimal K Analysis', fontsize=16)
        
        # Plot 1: Elbow curve (Inertia)
        ax1 = axes[0, 0]
        ax1.plot(self.results_['k'], self.results_['inertia'], 'bo-')
        ax1.axvline(x=self.optimal_k_, color='r', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Number of Clusters (K)')
        ax1.set_ylabel('Inertia')
        ax1.set_title('Elbow Method')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Silhouette score
        ax2 = axes[0, 1]
        ax2.plot(self.results_['k'], self.results_['silhouette_score'], 'go-')
        ax2.axvline(x=self.optimal_k_, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Number of Clusters (K)')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Silhouette Analysis (Higher is Better)')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Davies-Bouldin score
        ax3 = axes[1, 0]
        ax3.plot(self.results_['k'], self.results_['davies_bouldin_score'], 'ro-')
        ax3.axvline(x=self.optimal_k_, color='r', linestyle='--', alpha=0.5)
        ax3.set_xlabel('Number of Clusters (K)')
        ax3.set_ylabel('Davies-Bouldin Score')
        ax3.set_title('Davies-Bouldin Index (Lower is Better)')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Calinski-Harabasz score
        ax4 = axes[1, 1]
        ax4.plot(self.results_['k'], self.results_['calinski_harabasz_score'], 'mo-')
        ax4.axvline(x=self.optimal_k_, color='r', linestyle='--', alpha=0.5)
        ax4.set_xlabel('Number of Clusters (K)')
        ax4.set_ylabel('Calinski-Harabasz Score')
        ax4.set_title('Calinski-Harabasz Index (Higher is Better)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def get_results_summary(self) -> pd.DataFrame:
        """
        Get summary of results for all K values.
        
        Returns:
            DataFrame with metrics for each K
        """
        if self.results_ is None:
            raise ValueError("Must run find_optimal_k first")
        
        summary = self.results_[
            ['k', 'inertia', 'silhouette_score', 
             'davies_bouldin_score', 'calinski_harabasz_score']
        ].copy()
        
        # Add recommendation indicator
        summary['is_optimal'] = summary['k'] == self.optimal_k_
        
        return summary
    
    def plot_silhouette_analysis(self, k: Optional[int] = None, 
                                save_path: Optional[Path] = None) -> None:
        """
        Create detailed silhouette plot for a specific K.
        
        Args:
            k: Number of clusters (uses optimal_k if None)
            save_path: Optional path to save the plot
        """
        if self.X_ is None:
            raise ValueError("Must run find_optimal_k first")
        
        if k is None:
            k = self.optimal_k_
        
        # Get labels for specified k
        labels = self.results_[self.results_['k'] == k]['labels'].iloc[0]
        
        # Calculate silhouette scores for each sample
        from sklearn.metrics import silhouette_samples
        silhouette_vals = silhouette_samples(self.X_, labels)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        y_lower = 10
        for i in range(k):
            # Get silhouette scores for cluster i
            cluster_silhouette_vals = silhouette_vals[labels == i]
            cluster_silhouette_vals.sort()
            
            size_cluster_i = cluster_silhouette_vals.shape[0]
            y_upper = y_lower + size_cluster_i
            
            color = plt.cm.nipy_spectral(float(i) / k)
            ax.fill_betweenx(
                np.arange(y_lower, y_upper),
                0,
                cluster_silhouette_vals,
                facecolor=color,
                edgecolor=color,
                alpha=0.7
            )
            
            # Label clusters
            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
            
            y_lower = y_upper + 10
        
        ax.set_title(f"Silhouette Plot for K={k}")
        ax.set_xlabel("Silhouette Coefficient")
        ax.set_ylabel("Cluster Label")
        
        # Add average silhouette score line
        avg_score = self.results_[self.results_['k'] == k]['silhouette_score'].iloc[0]
        ax.axvline(x=avg_score, color="red", linestyle="--", label=f"Average: {avg_score:.3f}")
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Silhouette plot saved to {save_path}")
        
        plt.show()