"""
Example usage of the clustering pipeline.

This script demonstrates how to use the clustering components
for a quick analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path

from qaa_analysis.machine_learning.preprocessing import FeaturePreprocessor
from qaa_analysis.machine_learning.clustering import KMeansClusterer
from qaa_analysis.machine_learning.evaluation import ClusterProfiler
from qaa_analysis.machine_learning.visualization import ClusterVisualizer


def quick_clustering_demo():
    """Run a quick clustering demo."""
    # Load feature data
    feature_path = Path('data/features/user_behavioral_features_2025-06-05.parquet')
    
    if not feature_path.exists():
        print(f"Feature file not found at {feature_path}")
        print("Please run the feature engineering pipeline first.")
        return
    
    print(f"Loading features from {feature_path}")
    df = pd.read_parquet(feature_path)
    
    if 'user' in df.columns:
        df = df.set_index('user')
    
    print(f"Loaded {len(df)} users with {len(df.columns)} features")
    
    # Select numeric features only
    numeric_df = df.select_dtypes(include=[np.number])
    print(f"Using {len(numeric_df.columns)} numeric features")
    
    # Simple preprocessing (just scaling)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(numeric_df.values)
    
    # Quick K-means with 4 clusters
    print("\nClustering users into 4 groups...")
    kmeans = KMeansClusterer(n_clusters=4, random_state=42)
    kmeans.fit(X_scaled, feature_names=numeric_df.columns.tolist())
    
    # Get cluster labels
    labels = kmeans.labels_
    
    # Print metrics
    print("\nClustering Metrics:")
    metrics = kmeans.get_metrics()
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.3f}")
    
    # Create simple profiles
    print("\nGenerating cluster profiles...")
    profiler = ClusterProfiler()
    profiles = profiler.create_profiles(numeric_df, labels)
    
    # Print cluster summaries
    print("\nCluster Summaries:")
    print("-" * 60)
    for cluster in range(4):
        summary = profiler.get_cluster_summary(cluster)
        print(f"\n{summary['name']} (n={summary['size']}, {summary['size_percentage']:.1f}%)")
        print("Top distinguishing features:")
        for feat in summary['distinguishing_features'][:3]:
            print(f"  - {feat['feature']}: {feat['direction']} average (z={feat['z_score']:.2f})")
    
    # Create a simple visualization
    print("\nCreating visualization...")
    visualizer = ClusterVisualizer()
    
    # Create output directory
    output_dir = Path('data/clustering_demo')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save 2D PCA plot
    visualizer.plot_clusters_2d(
        X_scaled, labels,
        method='pca',
        feature_names=numeric_df.columns.tolist(),
        save_path=output_dir / 'demo_clusters.png'
    )
    
    # Save results
    results = numeric_df.copy()
    results['cluster'] = labels
    results.to_csv(output_dir / 'demo_results.csv')
    
    print(f"\nDemo complete! Results saved to {output_dir}")
    print("\nTo run the full pipeline with optimization, use:")
    print("python -m qaa_analysis.machine_learning.run_clustering_pipeline")


if __name__ == "__main__":
    quick_clustering_demo()