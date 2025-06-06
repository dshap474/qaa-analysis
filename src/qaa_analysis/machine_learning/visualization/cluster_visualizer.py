"""
Cluster Visualizer for QAA Analysis.

Creates various visualizations for clustering results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import logging


class ClusterVisualizer:
    """
    Create visualizations for clustering results.
    
    Includes:
    - 2D/3D scatter plots with dimensionality reduction
    - Cluster distribution plots
    - Feature heatmaps
    - Radar charts for cluster profiles
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize cluster visualizer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        # Use matplotlib colors instead of plotly for compatibility
        self.color_palette = plt.cm.Set3(np.linspace(0, 1, 10))
    
    def plot_clusters_2d(self, 
                        X: np.ndarray, 
                        labels: np.ndarray,
                        method: str = 'pca',
                        feature_names: Optional[List[str]] = None,
                        save_path: Optional[Path] = None) -> None:
        """
        Create 2D visualization of clusters using dimensionality reduction.
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            method: Dimensionality reduction method ('pca' or 'tsne')
            feature_names: Optional feature names
            save_path: Optional path to save plot
        """
        self.logger.info(f"Creating 2D cluster plot using {method}")
        
        # Reduce dimensions
        if method == 'pca':
            reducer = PCA(n_components=2, random_state=42)
            X_reduced = reducer.fit_transform(X)
            explained_var = reducer.explained_variance_ratio_
            axis_labels = [
                f"PC1 ({explained_var[0]:.1%} variance)",
                f"PC2 ({explained_var[1]:.1%} variance)"
            ]
        elif method == 'tsne':
            reducer = TSNE(n_components=2, random_state=42, perplexity=30)
            X_reduced = reducer.fit_transform(X)
            axis_labels = ["t-SNE 1", "t-SNE 2"]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot each cluster
        unique_labels = np.unique(labels)
        for i, label in enumerate(unique_labels):
            mask = labels == label
            ax.scatter(
                X_reduced[mask, 0],
                X_reduced[mask, 1],
                c=self.color_palette[i % len(self.color_palette)],
                label=f"Cluster {label}",
                alpha=0.6,
                s=50
            )
        
        ax.set_xlabel(axis_labels[0])
        ax.set_ylabel(axis_labels[1])
        ax.set_title(f"Cluster Visualization ({method.upper()})")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def plot_cluster_sizes(self, 
                          labels: np.ndarray,
                          save_path: Optional[Path] = None) -> None:
        """
        Create bar plot of cluster sizes.
        
        Args:
            labels: Cluster labels
            save_path: Optional path to save plot
        """
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(unique_labels, counts, 
                      color=[self.color_palette[i % len(self.color_palette)] 
                             for i in range(len(unique_labels))])
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}\n({height/len(labels)*100:.1f}%)',
                   ha='center', va='bottom')
        
        ax.set_xlabel("Cluster")
        ax.set_ylabel("Number of Users")
        ax.set_title("Cluster Size Distribution")
        ax.set_xticks(unique_labels)
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def plot_feature_heatmap(self,
                            X: pd.DataFrame,
                            labels: np.ndarray,
                            top_n_features: int = 20,
                            save_path: Optional[Path] = None) -> None:
        """
        Create heatmap of average feature values by cluster.
        
        Args:
            X: Feature DataFrame
            labels: Cluster labels
            top_n_features: Number of top features to show
            save_path: Optional path to save plot
        """
        # Calculate cluster means
        data = X.copy()
        data['cluster'] = labels
        cluster_means = data.groupby('cluster').mean()
        
        # Select top features by variance across clusters
        feature_vars = cluster_means.var()
        top_features = feature_vars.nlargest(top_n_features).index
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        
        # Normalize features for better visualization
        cluster_means_norm = (cluster_means[top_features] - cluster_means[top_features].mean()) / cluster_means[top_features].std()
        
        sns.heatmap(
            cluster_means_norm.T,
            cmap='RdBu_r',
            center=0,
            cbar_kws={'label': 'Normalized Value'},
            yticklabels=top_features,
            xticklabels=[f"Cluster {i}" for i in cluster_means.index]
        )
        
        plt.title(f"Top {top_n_features} Distinguishing Features by Cluster")
        plt.xlabel("Cluster")
        plt.ylabel("Feature")
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()
    
    def create_interactive_3d_plot(self,
                                  X: np.ndarray,
                                  labels: np.ndarray,
                                  feature_names: Optional[List[str]] = None,
                                  save_path: Optional[Path] = None) -> go.Figure:
        """
        Create interactive 3D plot using Plotly.
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            feature_names: Optional feature names
            save_path: Optional path to save HTML
            
        Returns:
            Plotly figure object
        """
        self.logger.info("Creating interactive 3D cluster plot")
        
        # Reduce to 3D using PCA
        pca = PCA(n_components=3, random_state=42)
        X_3d = pca.fit_transform(X)
        
        # Create DataFrame for plotting
        plot_df = pd.DataFrame(
            X_3d,
            columns=['PC1', 'PC2', 'PC3']
        )
        plot_df['Cluster'] = labels.astype(str)
        
        # Create 3D scatter plot
        fig = px.scatter_3d(
            plot_df,
            x='PC1',
            y='PC2',
            z='PC3',
            color='Cluster',
            title='3D Cluster Visualization (PCA)',
            labels={
                'PC1': f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                'PC2': f'PC2 ({pca.explained_variance_ratio_[1]:.1%})',
                'PC3': f'PC3 ({pca.explained_variance_ratio_[2]:.1%})'
            },
            color_discrete_sequence=px.colors.qualitative.Set3,
            hover_data={'Cluster': True}
        )
        
        fig.update_traces(marker=dict(size=5, opacity=0.7))
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(save_path))
            self.logger.info(f"Interactive plot saved to {save_path}")
        
        return fig
    
    def plot_cluster_radar_chart(self,
                                cluster_profiles: pd.DataFrame,
                                cluster_id: int,
                                features: List[str],
                                save_path: Optional[Path] = None) -> None:
        """
        Create radar chart for a specific cluster profile.
        
        Args:
            cluster_profiles: DataFrame with cluster profiles
            cluster_id: Cluster to visualize
            features: List of features to include
            save_path: Optional path to save plot
        """
        profile = cluster_profiles[cluster_profiles['cluster'] == cluster_id].iloc[0]
        
        # Get feature values (z-scores)
        values = []
        for feature in features:
            z_score_col = f"{feature}_z_score"
            if z_score_col in profile.index:
                # Convert z-score to 0-1 range for radar chart
                # Using sigmoid-like transformation
                z = profile[z_score_col]
                normalized = 1 / (1 + np.exp(-z))
                values.append(normalized)
            else:
                values.append(0.5)  # Neutral value
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
        values = values + values[:1]  # Close the polygon
        angles = angles + angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, 
                color=self.color_palette[cluster_id % len(self.color_palette)])
        ax.fill(angles, values, alpha=0.25,
                color=self.color_palette[cluster_id % len(self.color_palette)])
        
        # Customize
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(features, size=10)
        ax.set_ylim(0, 1)
        ax.set_title(f"Cluster {cluster_id} Profile", size=16, pad=20)
        ax.grid(True, alpha=0.3)
        
        # Add reference circle at 0.5 (neutral)
        ax.plot(angles, [0.5] * len(angles), 'k--', alpha=0.3, linewidth=1)
        
        plt.tight_layout()
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        
        plt.show()