"""
Run Complete Clustering Pipeline for QAA Analysis.

This script orchestrates the entire clustering workflow:
1. Load verified feature data
2. Preprocess features
3. Find optimal number of clusters
4. Train final K-means model
5. Generate cluster profiles and visualizations
6. Export results
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import json
import argparse

# Import ML components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from preprocessing.feature_preprocessor import FeaturePreprocessor
from preprocessing.feature_selector import FeatureSelector
from clustering.kmeans_clusterer import KMeansClusterer
from clustering.optimal_k_finder import OptimalKFinder
from evaluation.cluster_profiler import ClusterProfiler
from evaluation.cluster_metrics import ClusterMetrics
from visualization.cluster_visualizer import ClusterVisualizer


def setup_logging(output_dir: Path) -> logging.Logger:
    """Setup logging configuration."""
    log_file = output_dir / 'clustering_pipeline.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def load_feature_data(feature_path: Path, logger: logging.Logger) -> pd.DataFrame:
    """Load and validate feature data."""
    logger.info(f"Loading feature data from {feature_path}")
    
    df = pd.read_parquet(feature_path)
    logger.info(f"Loaded {len(df)} users with {len(df.columns)} features")
    
    # Basic validation
    if 'user' in df.columns:
        df = df.set_index('user')
    
    # Remove any remaining non-numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < len(df.columns):
        logger.warning(f"Removing {len(df.columns) - len(numeric_cols)} non-numeric columns")
        df = df[numeric_cols]
    
    return df


def preprocess_features(df: pd.DataFrame, logger: logging.Logger) -> tuple:
    """Preprocess features for clustering."""
    logger.info("Preprocessing features")
    
    # Initialize preprocessor
    preprocessor = FeaturePreprocessor(
        scaling_method='robust',  # Robust to outliers
        handle_outliers=True,
        outlier_threshold=3.0,
        log_transform_threshold=2.0,
        logger=logger
    )
    
    # Fit and transform
    X_preprocessed_array = preprocessor.fit_transform(df)
    
    # Convert back to DataFrame for feature selection
    X_preprocessed_df = pd.DataFrame(
        X_preprocessed_array, 
        columns=preprocessor.feature_names_
    )
    
    # Feature selection
    logger.info("Selecting features")
    selector = FeatureSelector(
        correlation_threshold=0.95,  # Remove highly correlated features
        variance_threshold=0.01,     # Remove low variance features
        logger=logger
    )
    
    X_selected_df = selector.fit_transform(X_preprocessed_df)
    X_selected = X_selected_df.values
    selected_features = X_selected_df.columns.tolist()
    
    logger.info(f"Selected {len(selected_features)} features from {len(df.columns)}")
    
    return X_selected, selected_features, preprocessor, selector


def find_optimal_clusters(X: np.ndarray, logger: logging.Logger, output_dir: Path) -> int:
    """Find optimal number of clusters."""
    logger.info("Finding optimal number of clusters")
    
    finder = OptimalKFinder(
        min_k=2,
        max_k=15,  # Test 2-15 clusters
        logger=logger
    )
    
    optimal_k = finder.find_optimal_k(X)
    
    # Save plots
    plots_dir = output_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    finder.plot_scores(save_path=plots_dir / 'optimal_k_analysis.png')
    
    # Log results
    logger.info(f"Optimal K analysis complete:")
    logger.info(f"Consensus optimal K: {optimal_k}")
    
    return optimal_k


def train_final_model(X: np.ndarray, n_clusters: int, logger: logging.Logger) -> KMeansClusterer:
    """Train final K-means model."""
    logger.info(f"Training final K-means model with {n_clusters} clusters")
    
    model = KMeansClusterer(
        n_clusters=n_clusters,
        n_init=50,  # Multiple initializations for stability
        max_iter=500,
        random_state=42,
        logger=logger
    )
    
    model.fit(X)
    
    # Log metrics
    metrics = model.get_metrics()
    logger.info("Clustering metrics:")
    for metric, value in metrics.items():
        logger.info(f"  {metric}: {value:.3f}")
    
    return model


def generate_profiles(X: pd.DataFrame, labels: np.ndarray, 
                     feature_names: list, logger: logging.Logger, 
                     output_dir: Path) -> ClusterProfiler:
    """Generate cluster profiles."""
    logger.info("Generating cluster profiles")
    
    profiler = ClusterProfiler(logger=logger)
    
    # Create DataFrame for profiling
    profile_df = pd.DataFrame(X, columns=feature_names)
    
    # Generate profiles
    profiles = profiler.create_profiles(profile_df, labels)
    
    # Save profiles
    profiler.export_profiles(output_dir / 'cluster_profiles.csv')
    
    # Generate and save report
    report = profiler.generate_profile_report(
        save_path=output_dir / 'cluster_profile_report.txt'
    )
    
    return profiler


def create_visualizations(X: np.ndarray, labels: np.ndarray, 
                         feature_names: list, profiler: ClusterProfiler,
                         logger: logging.Logger, output_dir: Path) -> None:
    """Create all visualizations."""
    logger.info("Creating visualizations")
    
    visualizer = ClusterVisualizer(logger=logger)
    plots_dir = output_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    # 2D visualizations
    visualizer.plot_clusters_2d(
        X, labels, 
        method='pca',
        feature_names=feature_names,
        save_path=plots_dir / 'clusters_pca.png'
    )
    
    visualizer.plot_clusters_2d(
        X, labels,
        method='tsne', 
        feature_names=feature_names,
        save_path=plots_dir / 'clusters_tsne.png'
    )
    
    # Cluster sizes
    visualizer.plot_cluster_sizes(
        labels,
        save_path=plots_dir / 'cluster_sizes.png'
    )
    
    # Feature heatmap
    profile_df = pd.DataFrame(X, columns=feature_names)
    visualizer.plot_feature_heatmap(
        profile_df, labels,
        top_n_features=20,
        save_path=plots_dir / 'feature_heatmap.png'
    )
    
    # Interactive 3D plot
    visualizer.create_interactive_3d_plot(
        X, labels,
        feature_names=feature_names,
        save_path=plots_dir / 'clusters_3d_interactive.html'
    )
    
    # Radar charts for each cluster
    for cluster in np.unique(labels):
        # Select top features for radar chart
        importance_df = profiler.feature_importance_
        top_features = importance_df.head(8)['feature'].tolist()
        
        visualizer.plot_cluster_radar_chart(
            profiler.cluster_profiles_,
            cluster,
            top_features,
            save_path=plots_dir / f'cluster_{cluster}_radar.png'
        )


def evaluate_clustering(X: np.ndarray, labels: np.ndarray, 
                       logger: logging.Logger, output_dir: Path) -> None:
    """Evaluate clustering quality."""
    logger.info("Evaluating clustering quality")
    
    evaluator = ClusterMetrics(logger=logger)
    metrics = evaluator.calculate_metrics(X, labels)
    
    # Save metrics
    metrics_df, cluster_metrics_df = evaluator.create_metrics_dataframe()
    metrics_df.to_csv(output_dir / 'clustering_metrics.csv')
    
    if cluster_metrics_df is not None:
        cluster_metrics_df.to_csv(output_dir / 'cluster_specific_metrics.csv')
    
    # Log quality assessment
    assessment = evaluator.get_quality_assessment()
    logger.info("\n" + assessment)
    
    # Save assessment
    with open(output_dir / 'quality_assessment.txt', 'w') as f:
        f.write(assessment)


def save_results(df: pd.DataFrame, labels: np.ndarray, 
                model: KMeansClusterer, output_dir: Path,
                metadata: dict) -> None:
    """Save all clustering results."""
    # Add cluster labels to original data
    results_df = df.copy()
    results_df['cluster'] = labels
    
    # Save results
    results_df.to_parquet(output_dir / 'clustered_users.parquet')
    results_df.to_csv(output_dir / 'clustered_users.csv')
    
    # Save model
    import joblib
    joblib.dump(model, output_dir / 'kmeans_model.pkl')
    
    # Save metadata
    metadata['timestamp'] = datetime.now().isoformat()
    with open(output_dir / 'clustering_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)


def main():
    """Run the complete clustering pipeline."""
    parser = argparse.ArgumentParser(description='Run clustering pipeline for QAA Analysis')
    parser.add_argument(
        '--features-path',
        type=Path,
        default='data/features/user_behavioral_features_2025-06-05.parquet',
        help='Path to feature data'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default='data/clustering_results',
        help='Output directory for results'
    )
    parser.add_argument(
        '--n-clusters',
        type=int,
        default=None,
        help='Force specific number of clusters (skip optimization)'
    )
    
    args = parser.parse_args()
    
    # Setup
    output_dir = Path(args.output_dir) / datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger = setup_logging(output_dir)
    logger.info("Starting clustering pipeline")
    
    try:
        # Load data
        df = load_feature_data(args.features_path, logger)
        
        # Preprocess
        X_processed, selected_features, preprocessor, selector = preprocess_features(df, logger)
        
        # Find optimal K or use provided
        if args.n_clusters is None:
            n_clusters = find_optimal_clusters(X_processed, logger, output_dir)
        else:
            n_clusters = args.n_clusters
            logger.info(f"Using provided number of clusters: {n_clusters}")
        
        # Train model
        model = train_final_model(X_processed, n_clusters, logger)
        labels = model.labels_
        
        # Generate profiles
        profiler = generate_profiles(
            X_processed, labels, selected_features, logger, output_dir
        )
        
        # Create visualizations
        create_visualizations(
            X_processed, labels, selected_features, profiler, logger, output_dir
        )
        
        # Evaluate clustering
        evaluate_clustering(X_processed, labels, logger, output_dir)
        
        # Save results
        metadata = {
            'n_users': len(df),
            'n_features_original': len(df.columns),
            'n_features_selected': len(selected_features),
            'n_clusters': n_clusters,
            'selected_features': selected_features,
            'preprocessing_params': {
                'scaling_method': preprocessor.scaling_method,
                'handle_outliers': preprocessor.handle_outliers,
                'log_transform_threshold': preprocessor.log_transform_threshold
            }
        }
        
        save_results(df, labels, model, output_dir, metadata)
        
        logger.info(f"Pipeline complete! Results saved to {output_dir}")
        
        # Print summary
        print("\n" + "="*60)
        print("CLUSTERING PIPELINE COMPLETE")
        print("="*60)
        print(f"Users clustered: {len(df)}")
        print(f"Number of clusters: {n_clusters}")
        print(f"Results directory: {output_dir}")
        print("\nKey outputs:")
        print("- clustered_users.parquet: Original data with cluster labels")
        print("- cluster_profiles.csv: Detailed cluster characteristics")
        print("- plots/: All visualizations")
        print("- clustering_metrics.csv: Quality metrics")
        print("- kmeans_model.pkl: Trained model for future predictions")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()