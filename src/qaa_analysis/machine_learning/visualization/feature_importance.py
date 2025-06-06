"""
Feature Importance Visualizer for QAA Analysis.

Creates visualizations for understanding feature importance in clustering.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict
from pathlib import Path
import logging


class FeatureImportanceVisualizer:
    """
    Visualize feature importance for clustering results.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize feature importance visualizer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def plot_feature_importance_bars(self,
                                   importance_df: pd.DataFrame,
                                   top_n: int = 20,
                                   save_path: Optional[Path] = None) -> None:
        """
        Create bar plot of feature importance scores.
        
        Args:
            importance_df: DataFrame with 'feature' and 'importance_score' columns
            top_n: Number of top features to show
            save_path: Optional path to save plot
        """
        # Get top features
        top_features = importance_df.nlargest(top_n, 'importance_score')
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create horizontal bar plot
        y_pos = np.arange(len(top_features))
        ax.barh(y_pos, top_features['importance_score'], 
                color='steelblue', alpha=0.8)
        
        # Customize plot
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_features['feature'])
        ax.set_xlabel('Importance Score')
        ax.set_title(f'Top {top_n} Most Important Features for Clustering')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (idx, row) in enumerate(top_features.iterrows()):
            ax.text(row['importance_score'] + 0.01, i, 
                   f"{row['importance_score']:.3f}",
                   va='center')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def plot_cluster_feature_comparison(self,
                                      cluster_profiles: pd.DataFrame,
                                      features: List[str],
                                      save_path: Optional[Path] = None) -> None:
        """
        Create comparison plot of feature values across clusters.
        
        Args:
            cluster_profiles: DataFrame with cluster profiles
            features: List of features to compare
            save_path: Optional path to save plot
        """
        # Extract z-scores for selected features
        data = []
        for _, profile in cluster_profiles.iterrows():
            cluster_data = {'cluster': int(profile['cluster'])}
            for feature in features:
                z_score_col = f"{feature}_z_score"
                if z_score_col in profile.index:
                    cluster_data[feature] = profile[z_score_col]
            data.append(cluster_data)
        
        comparison_df = pd.DataFrame(data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set up bar positions
        n_clusters = len(comparison_df)
        n_features = len(features)
        bar_width = 0.8 / n_clusters
        x = np.arange(n_features)
        
        # Plot bars for each cluster
        colors = plt.cm.Set3(np.linspace(0, 1, n_clusters))
        
        for i, (_, row) in enumerate(comparison_df.iterrows()):
            positions = x + i * bar_width - (n_clusters - 1) * bar_width / 2
            values = [row.get(feat, 0) for feat in features]
            ax.bar(positions, values, bar_width, 
                  label=f"Cluster {int(row['cluster'])}", 
                  color=colors[i], alpha=0.8)
        
        # Customize plot
        ax.set_xlabel('Features')
        ax.set_ylabel('Z-Score (Standard Deviations from Mean)')
        ax.set_title('Feature Comparison Across Clusters')
        ax.set_xticks(x)
        ax.set_xticklabels(features, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def plot_feature_correlation_matrix(self,
                                      feature_df: pd.DataFrame,
                                      cluster_labels: Optional[np.ndarray] = None,
                                      save_path: Optional[Path] = None) -> None:
        """
        Create correlation matrix heatmap of features.
        
        Args:
            feature_df: DataFrame with features
            cluster_labels: Optional cluster labels for ordering
            save_path: Optional path to save plot
        """
        # Calculate correlation matrix
        corr_matrix = feature_df.corr()
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap
        sns.heatmap(corr_matrix, 
                   mask=mask,
                   cmap='RdBu_r',
                   center=0,
                   square=True,
                   linewidths=0.5,
                   cbar_kws={"shrink": 0.8, "label": "Correlation"},
                   vmin=-1, vmax=1)
        
        ax.set_title('Feature Correlation Matrix')
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def plot_cumulative_importance(self,
                                 importance_df: pd.DataFrame,
                                 save_path: Optional[Path] = None) -> None:
        """
        Create cumulative importance plot.
        
        Args:
            importance_df: DataFrame with importance scores
            save_path: Optional path to save plot
        """
        # Sort by importance
        sorted_df = importance_df.sort_values('importance_score', ascending=False)
        
        # Calculate cumulative importance
        cumulative_importance = np.cumsum(sorted_df['importance_score'])
        cumulative_importance = cumulative_importance / cumulative_importance.iloc[-1]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(1, len(cumulative_importance) + 1)
        ax.plot(x, cumulative_importance, 'b-', linewidth=2)
        ax.fill_between(x, 0, cumulative_importance, alpha=0.3)
        
        # Add reference lines
        ax.axhline(y=0.8, color='r', linestyle='--', alpha=0.5, 
                  label='80% variance explained')
        ax.axhline(y=0.9, color='orange', linestyle='--', alpha=0.5,
                  label='90% variance explained')
        
        # Find number of features for 80% and 90%
        n_80 = np.argmax(cumulative_importance >= 0.8) + 1
        n_90 = np.argmax(cumulative_importance >= 0.9) + 1
        
        ax.axvline(x=n_80, color='r', linestyle=':', alpha=0.5)
        ax.axvline(x=n_90, color='orange', linestyle=':', alpha=0.5)
        
        # Annotations
        ax.text(n_80, 0.1, f'{n_80} features\nfor 80%', 
               ha='center', va='bottom', fontsize=10)
        ax.text(n_90, 0.2, f'{n_90} features\nfor 90%', 
               ha='center', va='bottom', fontsize=10)
        
        ax.set_xlabel('Number of Features')
        ax.set_ylabel('Cumulative Importance')
        ax.set_title('Cumulative Feature Importance')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()