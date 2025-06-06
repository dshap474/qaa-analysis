"""
Visualization tools for REV cluster analysis.

Creates various plots to understand REV distribution and patterns across clusters.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Dict
import logging


class RevVisualizer:
    """Create visualizations for REV analysis across clusters."""
    
    def __init__(self, analyzer):
        """
        Initialize visualizer with a RevClusterAnalyzer instance.
        
        Args:
            analyzer: RevClusterAnalyzer instance with processed data
        """
        self.analyzer = analyzer
        self.logger = logging.getLogger(__name__)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = plt.cm.Set3(np.linspace(0, 1, 10))
        
    def plot_rev_distribution(self, save_path: Optional[Path] = None):
        """Create REV distribution plots by cluster."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.ravel()
        
        merged_data = self.analyzer.merged_data
        
        for i, cluster in enumerate(sorted(merged_data['cluster'].unique())):
            if i >= 4:
                break
                
            ax = axes[i]
            cluster_data = merged_data[merged_data['cluster'] == cluster]
            
            # Get REV data for active users
            rev_data = cluster_data[cluster_data['rev_eth'] > 0]['rev_eth']
            
            if len(rev_data) > 0:
                # Log scale histogram
                bins = np.logspace(np.log10(rev_data.min()), 
                                 np.log10(rev_data.max()), 30)
                ax.hist(rev_data, bins=bins, alpha=0.7, 
                       color=self.colors[i], edgecolor='black')
                ax.set_xscale('log')
                
                # Add statistics
                ax.axvline(rev_data.median(), color='red', linestyle='--', 
                          label=f'Median: {rev_data.median():.6f}')
                ax.axvline(rev_data.mean(), color='green', linestyle='--', 
                          label=f'Mean: {rev_data.mean():.6f}')
            
            ax.set_xlabel('REV (ETH)')
            ax.set_ylabel('Number of Users')
            ax.set_title(f'Cluster {cluster} REV Distribution\n'
                        f'({len(cluster_data)} users, '
                        f'{(cluster_data["rev_eth"] > 0).sum()} active)')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('REV Distribution by Cluster (Log Scale)', fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved REV distribution plot to {save_path}")
        plt.show()
        
    def plot_cluster_comparison(self, save_path: Optional[Path] = None):
        """Create comparative visualizations across clusters."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        metrics = self.analyzer.cluster_metrics
        
        # 1. REV Share vs User Share
        ax = axes[0, 0]
        x = np.arange(len(metrics))
        width = 0.35
        
        ax.bar(x - width/2, metrics['user_share_pct'], width, 
               label='User Share %', color=self.colors[0])
        ax.bar(x + width/2, metrics['rev_share_pct'], width, 
               label='REV Share %', color=self.colors[1])
        
        ax.set_xlabel('Cluster')
        ax.set_ylabel('Percentage of Total')
        ax.set_title('User Share vs REV Share by Cluster')
        ax.set_xticks(x)
        ax.set_xticklabels([f'C{int(c)}' for c in metrics['cluster']])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 2. REV Concentration Ratio
        ax = axes[0, 1]
        bars = ax.bar(x, metrics['rev_concentration_ratio'], 
                      color=[self.colors[i] for i in range(len(metrics))])
        ax.axhline(y=1, color='red', linestyle='--', alpha=0.5)
        
        # Add value labels
        for bar, val in zip(bars, metrics['rev_concentration_ratio']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f}x', ha='center', va='bottom')
        
        ax.set_xlabel('Cluster')
        ax.set_ylabel('REV Concentration Ratio')
        ax.set_title('REV Concentration by Cluster\n(>1 = Higher REV than user share)')
        ax.set_xticks(x)
        ax.set_xticklabels([f'C{int(c)}' for c in metrics['cluster']])
        ax.grid(True, alpha=0.3)
        
        # 3. Average REV per Active User
        ax = axes[1, 0]
        bars = ax.bar(x, metrics['mean_rev_active'], 
                      color=[self.colors[i] for i in range(len(metrics))])
        
        # Add value labels
        for bar, val in zip(bars, metrics['mean_rev_active']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.4f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Cluster')
        ax.set_ylabel('Average REV (ETH)')
        ax.set_title('Average REV per Active User')
        ax.set_xticks(x)
        ax.set_xticklabels([f'C{int(c)}' for c in metrics['cluster']])
        ax.grid(True, alpha=0.3)
        
        # 4. REV Efficiency (REV per ETH transferred)
        ax = axes[1, 1]
        bars = ax.bar(x, metrics['rev_per_eth'] * 100, 
                      color=[self.colors[i] for i in range(len(metrics))])
        
        # Add value labels
        for bar, val in zip(bars, metrics['rev_per_eth'] * 100):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}%', ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Cluster')
        ax.set_ylabel('REV as % of Value')
        ax.set_title('REV Efficiency by Cluster\n(Lower = More Efficient)')
        ax.set_xticks(x)
        ax.set_xticklabels([f'C{int(c)}' for c in metrics['cluster']])
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('Cluster REV Comparison Metrics', fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved cluster comparison plot to {save_path}")
        plt.show()
        
    def plot_lorenz_curves(self, save_path: Optional[Path] = None):
        """Plot Lorenz curves showing REV concentration within each cluster."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot 45-degree line (perfect equality)
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect Equality')
        
        merged_data = self.analyzer.merged_data
        
        for i, cluster in enumerate(sorted(merged_data['cluster'].unique())):
            cluster_data = merged_data[merged_data['cluster'] == cluster]
            active_users = cluster_data[cluster_data['rev_eth'] > 0]
            
            if len(active_users) > 0:
                # Calculate Lorenz curve
                sorted_rev = np.sort(active_users['rev_eth'])
                cumsum = np.cumsum(sorted_rev)
                cumsum_norm = cumsum / cumsum[-1]
                x_norm = np.arange(1, len(sorted_rev) + 1) / len(sorted_rev)
                
                # Add (0,0) point
                x_norm = np.concatenate([[0], x_norm])
                cumsum_norm = np.concatenate([[0], cumsum_norm])
                
                # Get Gini from metrics
                gini = self.analyzer.cluster_metrics.loc[
                    self.analyzer.cluster_metrics['cluster'] == cluster, 'rev_gini'
                ].values[0]
                
                ax.plot(x_norm, cumsum_norm, 
                       label=f'Cluster {cluster} (Gini={gini:.3f})',
                       color=self.colors[i], linewidth=2)
        
        ax.set_xlabel('Cumulative Share of Users')
        ax.set_ylabel('Cumulative Share of REV')
        ax.set_title('REV Concentration by Cluster (Lorenz Curves)')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved Lorenz curves to {save_path}")
        plt.show()
        
    def plot_efficiency_scatter(self, save_path: Optional[Path] = None):
        """Create scatter plots showing REV efficiency relationships."""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        merged_data = self.analyzer.merged_data
        active_users = merged_data[merged_data['rev_eth'] > 0]
        
        # 1. REV vs Total ETH Value
        ax = axes[0]
        for i, cluster in enumerate(sorted(active_users['cluster'].unique())):
            cluster_data = active_users[active_users['cluster'] == cluster]
            ax.scatter(cluster_data['total_eth_value'], 
                      cluster_data['rev_eth'],
                      alpha=0.6, s=30,
                      color=self.colors[i],
                      label=f'Cluster {cluster}')
        
        ax.set_xlabel('Total ETH Value Transferred')
        ax.set_ylabel('Total REV Paid (ETH)')
        ax.set_title('REV vs Value Transferred')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add efficiency lines
        for efficiency in [0.001, 0.01, 0.1]:  # 0.1%, 1%, 10%
            x_line = np.logspace(-4, 2, 100)
            y_line = x_line * efficiency
            ax.plot(x_line, y_line, '--', alpha=0.3, 
                   label=f'{efficiency*100}% fee rate')
        
        # 2. REV per TX vs Gas Price
        ax = axes[1]
        for i, cluster in enumerate(sorted(active_users['cluster'].unique())):
            cluster_data = active_users[active_users['cluster'] == cluster]
            ax.scatter(cluster_data['avg_gas_price_gwei'], 
                      cluster_data['avg_rev_per_tx'],
                      alpha=0.6, s=30,
                      color=self.colors[i],
                      label=f'Cluster {cluster}')
        
        ax.set_xlabel('Average Gas Price (Gwei)')
        ax.set_ylabel('Average REV per Transaction (ETH)')
        ax.set_title('Transaction Cost vs Gas Price')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('REV Efficiency Analysis', fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved efficiency scatter to {save_path}")
        plt.show()
        
    def create_summary_dashboard(self, output_dir: Path):
        """Create all visualizations and save to directory."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Creating REV analysis dashboard in {output_dir}")
        
        # Generate all plots
        self.plot_rev_distribution(output_dir / 'rev_distribution.png')
        self.plot_cluster_comparison(output_dir / 'cluster_comparison.png')
        self.plot_lorenz_curves(output_dir / 'lorenz_curves.png')
        self.plot_efficiency_scatter(output_dir / 'efficiency_analysis.png')
        
        self.logger.info("Dashboard creation complete")