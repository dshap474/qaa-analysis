"""
REV Cluster Analyzer for QAA Analysis.

Analyzes transaction fee (REV) patterns across behavioral clusters.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime


class RevClusterAnalyzer:
    """Analyze REV (transaction fee) patterns by behavioral cluster."""
    
    def __init__(self, cluster_data_path: Path, interaction_data_path: Optional[Path] = None):
        """
        Initialize REV analyzer with cluster and transaction data.
        
        Args:
            cluster_data_path: Path to clustered users parquet file
            interaction_data_path: Path to interaction data with gas info
        """
        self.logger = logging.getLogger(__name__)
        
        # Load cluster data
        self.logger.info(f"Loading cluster data from {cluster_data_path}")
        self.clusters = pd.read_parquet(cluster_data_path)
        
        # If interaction data provided, calculate REV from it
        if interaction_data_path:
            self.logger.info(f"Loading interaction data from {interaction_data_path}")
            self.interactions = pd.read_parquet(interaction_data_path)
            self.rev_data = self._calculate_rev_from_interactions()
        else:
            self.rev_data = None
            
        self.merged_data = None
        self.cluster_metrics = None
        
    def _calculate_rev_from_interactions(self) -> pd.DataFrame:
        """Calculate REV metrics from interaction data."""
        self.logger.info("Calculating REV from interaction data")
        
        # Convert decimal columns to float
        decimal_columns = ['value', 'receipt_gas_used', 'gas_price']
        for col in decimal_columns:
            if col in self.interactions.columns:
                self.interactions[col] = pd.to_numeric(self.interactions[col], errors='coerce')
        
        # Calculate REV per transaction
        self.interactions['rev_eth'] = (
            self.interactions['receipt_gas_used'].astype(float) * 
            self.interactions['gas_price'].astype(float)
        ) / 1e18
        
        # Aggregate by user
        rev_by_user = self.interactions.groupby('from_address').agg({
            'rev_eth': 'sum',
            'transaction_hash': 'count',
            'receipt_gas_used': 'sum',
            'gas_price': 'mean',
            'value': 'sum'
        }).rename(columns={
            'transaction_hash': 'tx_count',
            'receipt_gas_used': 'total_gas_used',
            'gas_price': 'avg_gas_price',
            'value': 'total_eth_value'
        })
        
        # Convert value from Wei to ETH (ensure float type)
        rev_by_user['total_eth_value'] = rev_by_user['total_eth_value'].astype(float) / 1e18
        rev_by_user['avg_gas_price_gwei'] = rev_by_user['avg_gas_price'].astype(float) / 1e9
        
        # Calculate additional metrics
        rev_by_user['avg_rev_per_tx'] = rev_by_user['rev_eth'] / rev_by_user['tx_count']
        rev_by_user['gas_efficiency'] = rev_by_user['total_eth_value'] / rev_by_user['rev_eth']
        rev_by_user['rev_rate'] = rev_by_user['rev_eth'] / rev_by_user['total_eth_value']
        
        # Handle infinities and NaNs
        rev_by_user['gas_efficiency'] = rev_by_user['gas_efficiency'].replace([np.inf, -np.inf], np.nan)
        rev_by_user['rev_rate'] = rev_by_user['rev_rate'].replace([np.inf, -np.inf], np.nan)
        
        # Reset index to make from_address a column
        rev_by_user = rev_by_user.reset_index()
        rev_by_user.rename(columns={'from_address': 'user'}, inplace=True)
        
        self.logger.info(f"Calculated REV for {len(rev_by_user)} users")
        
        return rev_by_user
        
    def merge_with_clusters(self) -> pd.DataFrame:
        """Merge REV data with cluster assignments."""
        if self.rev_data is None:
            raise ValueError("No REV data available. Provide interaction data or REV data.")
            
        self.logger.info("Merging REV data with cluster assignments")
        
        # Prepare cluster data
        cluster_cols = ['cluster']
        if 'user' in self.clusters.columns:
            user_col = 'user'
        else:
            user_col = self.clusters.index.name or 'index'
            self.clusters = self.clusters.reset_index()
            
        # Merge on user/address
        self.merged_data = pd.merge(
            self.clusters[[user_col, 'cluster']],
            self.rev_data,
            left_on=user_col,
            right_on='user',
            how='left'
        )
        
        # Fill NaN values for users with no transactions
        rev_columns = ['rev_eth', 'tx_count', 'total_gas_used', 'total_eth_value']
        self.merged_data[rev_columns] = self.merged_data[rev_columns].fillna(0)
        
        self.logger.info(f"Merged data shape: {self.merged_data.shape}")
        self.logger.info(f"Users with REV > 0: {(self.merged_data['rev_eth'] > 0).sum()}")
        
        return self.merged_data
        
    def calculate_cluster_metrics(self) -> pd.DataFrame:
        """Calculate comprehensive REV metrics by cluster."""
        if self.merged_data is None:
            self.merge_with_clusters()
            
        self.logger.info("Calculating cluster-level REV metrics")
        
        metrics = []
        
        for cluster in sorted(self.merged_data['cluster'].unique()):
            cluster_data = self.merged_data[self.merged_data['cluster'] == cluster]
            active_users = cluster_data[cluster_data['rev_eth'] > 0]
            
            # Basic counts
            total_users = len(cluster_data)
            active_count = len(active_users)
            
            # REV metrics
            total_rev = cluster_data['rev_eth'].sum()
            total_network_rev = self.merged_data['rev_eth'].sum()
            
            # Distribution metrics
            if active_count > 0:
                rev_values = active_users['rev_eth'].values
                rev_gini = self._calculate_gini(rev_values)
                
                # Top user analysis
                rev_sorted = active_users['rev_eth'].sort_values(ascending=False)
                top_10_pct_count = max(1, int(active_count * 0.1))
                top_10_pct_rev = rev_sorted.head(top_10_pct_count).sum()
                top_10_pct_share = top_10_pct_rev / total_rev if total_rev > 0 else 0
            else:
                rev_gini = 0
                top_10_pct_share = 0
                
            # Efficiency metrics
            total_value = cluster_data['total_eth_value'].sum()
            total_tx = cluster_data['tx_count'].sum()
            
            cluster_metrics = {
                'cluster': cluster,
                'total_users': total_users,
                'active_users': active_count,
                'active_ratio': active_count / total_users if total_users > 0 else 0,
                
                # REV totals
                'total_rev_eth': total_rev,
                'rev_share_pct': (total_rev / total_network_rev * 100) if total_network_rev > 0 else 0,
                
                # Per user metrics
                'mean_rev_all': total_rev / total_users if total_users > 0 else 0,
                'mean_rev_active': total_rev / active_count if active_count > 0 else 0,
                'median_rev_all': cluster_data['rev_eth'].median(),
                'median_rev_active': active_users['rev_eth'].median() if active_count > 0 else 0,
                
                # Distribution
                'rev_gini': rev_gini,
                'top_10pct_share': top_10_pct_share,
                'rev_std': cluster_data['rev_eth'].std(),
                'rev_p25': cluster_data['rev_eth'].quantile(0.25),
                'rev_p75': cluster_data['rev_eth'].quantile(0.75),
                'rev_p90': cluster_data['rev_eth'].quantile(0.90),
                'rev_p99': cluster_data['rev_eth'].quantile(0.99),
                
                # Efficiency
                'total_tx_count': total_tx,
                'total_eth_value': total_value,
                'rev_per_tx': total_rev / total_tx if total_tx > 0 else 0,
                'rev_per_eth': total_rev / total_value if total_value > 0 else 0,
                'avg_gas_price_gwei': active_users['avg_gas_price_gwei'].mean() if active_count > 0 else 0,
                
                # User size relative to network
                'user_share_pct': total_users / len(self.merged_data) * 100
            }
            
            metrics.append(cluster_metrics)
            
        self.cluster_metrics = pd.DataFrame(metrics)
        
        # Calculate relative metrics
        self.cluster_metrics['rev_concentration_ratio'] = (
            self.cluster_metrics['rev_share_pct'] / self.cluster_metrics['user_share_pct']
        )
        
        return self.cluster_metrics
        
    def identify_top_rev_users(self, n: int = 10) -> Dict[int, pd.DataFrame]:
        """Identify top REV generators in each cluster."""
        if self.merged_data is None:
            self.merge_with_clusters()
            
        top_users = {}
        
        for cluster in sorted(self.merged_data['cluster'].unique()):
            cluster_data = self.merged_data[self.merged_data['cluster'] == cluster]
            
            # Get top N users by REV
            top_n = cluster_data.nlargest(n, 'rev_eth')[
                ['user', 'rev_eth', 'tx_count', 'total_eth_value', 
                 'avg_rev_per_tx', 'gas_efficiency', 'avg_gas_price_gwei']
            ]
            
            top_users[cluster] = top_n
            
        return top_users
        
    def analyze_rev_efficiency(self) -> pd.DataFrame:
        """Analyze REV efficiency patterns across clusters."""
        if self.merged_data is None:
            self.merge_with_clusters()
            
        # Calculate efficiency metrics for active users only
        active_users = self.merged_data[self.merged_data['rev_eth'] > 0].copy()
        
        # Efficiency metrics
        efficiency_by_cluster = active_users.groupby('cluster').agg({
            'gas_efficiency': ['mean', 'median', 'std'],
            'rev_rate': ['mean', 'median', 'std'],
            'avg_rev_per_tx': ['mean', 'median', 'std'],
            'avg_gas_price_gwei': ['mean', 'median', 'std']
        })
        
        # Flatten column names
        efficiency_by_cluster.columns = ['_'.join(col).strip() for col in efficiency_by_cluster.columns]
        
        return efficiency_by_cluster
        
    def _calculate_gini(self, values: np.ndarray) -> float:
        """Calculate Gini coefficient for distribution analysis."""
        if len(values) == 0:
            return 0
            
        # Remove zeros and sort
        values = values[values > 0]
        if len(values) == 0:
            return 0
            
        sorted_values = np.sort(values)
        n = len(sorted_values)
        
        # Calculate Gini
        index = np.arange(1, n + 1)
        return (2 * index @ sorted_values) / (n * np.sum(sorted_values)) - (n + 1) / n
        
    def generate_summary_report(self) -> str:
        """Generate a text summary of REV analysis."""
        if self.cluster_metrics is None:
            self.calculate_cluster_metrics()
            
        total_rev = self.merged_data['rev_eth'].sum()
        total_users = len(self.merged_data)
        active_users = (self.merged_data['rev_eth'] > 0).sum()
        
        report = f"""
REV CLUSTER ANALYSIS SUMMARY
===========================

Overall Network Statistics:
- Total REV: {total_rev:.4f} ETH
- Total Users: {total_users:,}
- Active Users (REV > 0): {active_users:,} ({active_users/total_users*100:.1f}%)
- Average REV per User: {total_rev/total_users:.6f} ETH
- Average REV per Active User: {total_rev/active_users:.6f} ETH

Cluster Breakdown:
"""
        
        for _, cluster in self.cluster_metrics.iterrows():
            report += f"""
Cluster {int(cluster['cluster'])}:
- Users: {int(cluster['total_users']):,} ({cluster['user_share_pct']:.1f}% of network)
- Active: {int(cluster['active_users']):,} ({cluster['active_ratio']*100:.1f}% activity rate)
- Total REV: {cluster['total_rev_eth']:.4f} ETH ({cluster['rev_share_pct']:.1f}% of network)
- REV Concentration Ratio: {cluster['rev_concentration_ratio']:.2f}x
- Mean REV per Active User: {cluster['mean_rev_active']:.6f} ETH
- Median REV (all users): {cluster['median_rev_all']:.6f} ETH
- REV Gini Coefficient: {cluster['rev_gini']:.3f}
- Top 10% Share: {cluster['top_10pct_share']*100:.1f}%
- Efficiency: {cluster['rev_per_eth']*100:.3f}% of value as fees
"""
        
        # Add key insights
        most_rev_cluster = self.cluster_metrics.loc[self.cluster_metrics['total_rev_eth'].idxmax()]
        most_efficient_cluster = self.cluster_metrics.loc[self.cluster_metrics['rev_per_eth'].idxmin()]
        
        report += f"""
Key Insights:
- Cluster {int(most_rev_cluster['cluster'])} generates the most REV ({most_rev_cluster['rev_share_pct']:.1f}% of total)
- Cluster {int(most_efficient_cluster['cluster'])} is most efficient ({most_efficient_cluster['rev_per_eth']*100:.3f}% fee rate)
- REV concentration varies significantly across clusters (Gini: {self.cluster_metrics['rev_gini'].min():.3f} to {self.cluster_metrics['rev_gini'].max():.3f})
"""
        
        return report