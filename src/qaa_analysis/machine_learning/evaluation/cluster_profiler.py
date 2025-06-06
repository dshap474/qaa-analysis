"""
Cluster Profiler for QAA Analysis.

Generates detailed profiles and interpretations for each cluster.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path


class ClusterProfiler:
    """
    Generate comprehensive profiles for each cluster.
    
    Creates interpretable descriptions of cluster characteristics
    based on feature distributions and statistical analysis.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize cluster profiler.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Profile results
        self.cluster_profiles_ = None
        self.feature_importance_ = None
        self.cluster_names_ = None
    
    def create_profiles(self, 
                       X: pd.DataFrame, 
                       labels: np.ndarray,
                       feature_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create detailed profiles for each cluster.
        
        Args:
            X: Feature DataFrame or array
            labels: Cluster labels
            feature_names: Optional feature names if X is array
            
        Returns:
            DataFrame with cluster profiles
        """
        self.logger.info("Creating cluster profiles")
        
        # Convert to DataFrame if needed
        if not isinstance(X, pd.DataFrame):
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(X.shape[1])]
            X = pd.DataFrame(X, columns=feature_names)
        
        # Add cluster labels
        data = X.copy()
        data['cluster'] = labels
        
        # Calculate profiles
        profiles = []
        unique_labels = np.unique(labels)
        
        for cluster in unique_labels:
            profile = self._create_single_cluster_profile(data, cluster)
            profiles.append(profile)
        
        self.cluster_profiles_ = pd.DataFrame(profiles)
        
        # Calculate feature importance
        self.feature_importance_ = self._calculate_feature_importance(data)
        
        # Generate cluster names
        self.cluster_names_ = self._generate_cluster_names()
        
        return self.cluster_profiles_
    
    def _create_single_cluster_profile(self, data: pd.DataFrame, cluster: int) -> Dict:
        """
        Create profile for a single cluster.
        
        Args:
            data: DataFrame with features and cluster labels
            cluster: Cluster ID
            
        Returns:
            Dictionary with cluster profile
        """
        cluster_data = data[data['cluster'] == cluster].drop('cluster', axis=1)
        overall_data = data.drop('cluster', axis=1)
        
        profile = {
            'cluster': cluster,
            'size': len(cluster_data),
            'size_pct': len(cluster_data) / len(data) * 100
        }
        
        # Calculate statistics for each feature
        for feature in cluster_data.columns:
            cluster_mean = cluster_data[feature].mean()
            cluster_std = cluster_data[feature].std()
            overall_mean = overall_data[feature].mean()
            overall_std = overall_data[feature].std()
            
            # Z-score: how many standard deviations from overall mean
            if overall_std > 0:
                z_score = (cluster_mean - overall_mean) / overall_std
            else:
                z_score = 0
            
            profile[f"{feature}_mean"] = cluster_mean
            profile[f"{feature}_std"] = cluster_std
            profile[f"{feature}_z_score"] = z_score
        
        return profile
    
    def _calculate_feature_importance(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate feature importance for distinguishing clusters.
        
        Uses ANOVA F-statistic to measure feature importance.
        
        Args:
            data: DataFrame with features and cluster labels
            
        Returns:
            DataFrame with feature importance scores
        """
        from sklearn.feature_selection import f_classif
        
        X = data.drop('cluster', axis=1)
        y = data['cluster']
        
        # Calculate F-statistics
        f_stats, p_values = f_classif(X, y)
        
        # Create importance DataFrame
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'f_statistic': f_stats,
            'p_value': p_values,
            'importance_score': f_stats / f_stats.max()  # Normalize to 0-1
        }).sort_values('f_statistic', ascending=False)
        
        return importance_df
    
    def _generate_cluster_names(self) -> Dict[int, str]:
        """
        Generate descriptive names for each cluster based on their characteristics.
        
        Returns:
            Dictionary mapping cluster ID to descriptive name
        """
        if self.cluster_profiles_ is None:
            return {}
        
        names = {}
        
        for _, profile in self.cluster_profiles_.iterrows():
            cluster = int(profile['cluster'])
            
            # Find most distinguishing features (highest absolute z-scores)
            z_scores = {}
            for col in profile.index:
                if col.endswith('_z_score'):
                    feature = col.replace('_z_score', '')
                    z_scores[feature] = abs(profile[col])
            
            # Get top 3 distinguishing features
            top_features = sorted(z_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Create name based on characteristics
            name_parts = []
            for feature, z_score in top_features:
                if z_score > 0.5:  # Only include if significantly different
                    mean_col = f"{feature}_mean"
                    z_col = f"{feature}_z_score"
                    
                    if profile[z_col] > 0:
                        direction = "High"
                    else:
                        direction = "Low"
                    
                    # Simplify feature name
                    feature_simple = feature.replace('_', ' ').title()
                    name_parts.append(f"{direction} {feature_simple}")
            
            if name_parts:
                names[cluster] = " + ".join(name_parts[:2])  # Use top 2 characteristics
            else:
                names[cluster] = f"Cluster {cluster}"
        
        return names
    
    def get_cluster_summary(self, cluster: int) -> Dict:
        """
        Get detailed summary for a specific cluster.
        
        Args:
            cluster: Cluster ID
            
        Returns:
            Dictionary with cluster summary
        """
        if self.cluster_profiles_ is None:
            raise ValueError("Must create profiles first")
        
        profile = self.cluster_profiles_[self.cluster_profiles_['cluster'] == cluster].iloc[0]
        
        # Get distinguishing features
        distinguishing_features = []
        for col in profile.index:
            if col.endswith('_z_score') and abs(profile[col]) > 1:
                feature = col.replace('_z_score', '')
                distinguishing_features.append({
                    'feature': feature,
                    'mean': profile[f"{feature}_mean"],
                    'z_score': profile[col],
                    'direction': 'above' if profile[col] > 0 else 'below'
                })
        
        # Sort by absolute z-score
        distinguishing_features.sort(key=lambda x: abs(x['z_score']), reverse=True)
        
        summary = {
            'cluster_id': cluster,
            'name': self.cluster_names_.get(cluster, f"Cluster {cluster}"),
            'size': int(profile['size']),
            'size_percentage': profile['size_pct'],
            'distinguishing_features': distinguishing_features[:5]  # Top 5
        }
        
        return summary
    
    def generate_profile_report(self, save_path: Optional[Path] = None) -> str:
        """
        Generate a comprehensive text report of all cluster profiles.
        
        Args:
            save_path: Optional path to save the report
            
        Returns:
            Formatted report string
        """
        if self.cluster_profiles_ is None:
            raise ValueError("Must create profiles first")
        
        report = "=" * 80 + "\n"
        report += "CLUSTER PROFILE REPORT\n"
        report += "=" * 80 + "\n\n"
        
        # Overall statistics
        report += "OVERALL STATISTICS:\n"
        report += "-" * 40 + "\n"
        report += f"Total clusters: {len(self.cluster_profiles_)}\n"
        report += f"Total samples: {self.cluster_profiles_['size'].sum()}\n"
        report += f"Cluster sizes: {self.cluster_profiles_['size'].tolist()}\n\n"
        
        # Feature importance
        report += "TOP 10 DISTINGUISHING FEATURES:\n"
        report += "-" * 40 + "\n"
        for _, row in self.feature_importance_.head(10).iterrows():
            report += f"{row['feature']:.<30} {row['importance_score']:.3f}\n"
        report += "\n"
        
        # Individual cluster profiles
        for cluster in self.cluster_profiles_['cluster']:
            summary = self.get_cluster_summary(cluster)
            
            report += f"CLUSTER {cluster}: {summary['name']}\n"
            report += "-" * 40 + "\n"
            report += f"Size: {summary['size']} ({summary['size_percentage']:.1f}%)\n"
            report += "Distinguishing features:\n"
            
            for feat in summary['distinguishing_features']:
                report += f"  • {feat['feature']}: {feat['mean']:.3f} "
                report += f"({feat['direction']} average, z={feat['z_score']:.2f})\n"
            
            report += "\n"
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(report)
            self.logger.info(f"Profile report saved to {save_path}")
        
        return report
    
    def export_profiles(self, filepath: Path) -> None:
        """
        Export cluster profiles to CSV.
        
        Args:
            filepath: Path to save the profiles
        """
        if self.cluster_profiles_ is None:
            raise ValueError("Must create profiles first")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Add cluster names to profiles
        export_df = self.cluster_profiles_.copy()
        export_df['cluster_name'] = export_df['cluster'].map(self.cluster_names_)
        
        # Reorder columns
        cols = ['cluster', 'cluster_name', 'size', 'size_pct'] + \
               [c for c in export_df.columns if c not in ['cluster', 'cluster_name', 'size', 'size_pct']]
        export_df = export_df[cols]
        
        export_df.to_csv(filepath, index=False)
        self.logger.info(f"Cluster profiles exported to {filepath}")