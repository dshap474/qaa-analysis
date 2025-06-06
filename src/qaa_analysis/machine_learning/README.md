# Machine Learning Module for QAA Analysis

This module provides comprehensive machine learning tools for behavioral segmentation of blockchain users based on their DeFi interactions.

## Overview

The module implements a complete clustering pipeline with the following components:

### 1. Preprocessing (`preprocessing/`)
- **FeaturePreprocessor**: Handles scaling, outlier detection, and transformations
- **FeatureSelector**: Removes correlated and low-variance features

### 2. Clustering (`clustering/`)
- **KMeansClusterer**: K-means implementation with comprehensive metrics
- **OptimalKFinder**: Finds optimal number of clusters using multiple methods
- **ClusterValidator**: Validates clustering quality

### 3. Evaluation (`evaluation/`)
- **ClusterProfiler**: Generates interpretable cluster profiles
- **ClusterMetrics**: Calculates quality metrics (silhouette, Davies-Bouldin, etc.)

### 4. Visualization (`visualization/`)
- **ClusterVisualizer**: Creates 2D/3D plots, heatmaps, and radar charts
- **FeatureImportanceVisualizer**: Visualizes feature importance

## Quick Start

### Simple Example
```python
from qaa_analysis.machine_learning import KMeansClusterer, ClusterProfiler

# Load your feature data
df = pd.read_parquet('data/features/user_behavioral_features.parquet')

# Simple clustering
kmeans = KMeansClusterer(n_clusters=4)
kmeans.fit(df.values)

# Generate profiles
profiler = ClusterProfiler()
profiles = profiler.create_profiles(df, kmeans.labels_)
```

### Run the Complete Pipeline
```bash
# Run with automatic optimization
python -m qaa_analysis.machine_learning.run_clustering_pipeline

# Run with specific number of clusters
python -m qaa_analysis.machine_learning.run_clustering_pipeline --n-clusters 5

# Specify custom paths
python -m qaa_analysis.machine_learning.run_clustering_pipeline \
    --features-path data/custom_features.parquet \
    --output-dir results/clustering
```

### Run the Demo
```bash
python -m qaa_analysis.machine_learning.example_clustering
```

## Pipeline Workflow

1. **Load Data**: Reads verified feature data from parquet file
2. **Preprocess**: 
   - Scales features using RobustScaler
   - Handles outliers using IQR method
   - Log-transforms highly skewed features
   - Removes correlated features (>0.95 correlation)
3. **Find Optimal K**:
   - Tests 2-15 clusters
   - Uses elbow method, silhouette analysis, and gap statistic
   - Selects consensus optimal K
4. **Train Model**:
   - K-means with 50 initializations for stability
   - Calculates comprehensive metrics
5. **Generate Profiles**:
   - Creates statistical profiles for each cluster
   - Identifies distinguishing features
   - Generates descriptive cluster names
6. **Create Visualizations**:
   - 2D plots using PCA and t-SNE
   - 3D interactive plot
   - Feature heatmaps
   - Radar charts for each cluster
7. **Evaluate Quality**:
   - Silhouette scores
   - Davies-Bouldin index
   - Cluster size balance
   - Quality assessment report

## Output Structure

Running the pipeline creates a timestamped directory with:

```
data/clustering_results/YYYYMMDD_HHMMSS/
├── clustered_users.parquet       # Original data with cluster labels
├── clustered_users.csv           # CSV version
├── cluster_profiles.csv          # Detailed cluster characteristics
├── clustering_metrics.csv        # Quality metrics
├── cluster_profile_report.txt    # Human-readable report
├── quality_assessment.txt        # Clustering quality assessment
├── clustering_metadata.json      # Pipeline metadata
├── kmeans_model.pkl             # Trained model
├── clustering_pipeline.log      # Execution log
└── plots/
    ├── optimal_k_analysis.png   # K selection plots
    ├── clusters_pca.png         # 2D PCA visualization
    ├── clusters_tsne.png        # 2D t-SNE visualization
    ├── clusters_3d_interactive.html  # Interactive 3D plot
    ├── cluster_sizes.png        # Size distribution
    ├── feature_heatmap.png      # Feature comparison
    └── cluster_N_radar.png      # Radar charts for each cluster
```

## Key Features

- **Modular Design**: Each component can be used independently
- **Comprehensive Metrics**: Multiple validation metrics for robust evaluation
- **Interpretable Results**: Automatic cluster profiling and naming
- **Rich Visualizations**: Multiple plot types for different insights
- **Production Ready**: Logging, error handling, and model persistence

## Dependencies

- scikit-learn
- pandas
- numpy
- matplotlib
- seaborn
- plotly
- joblib

## Future Enhancements

- Support for additional clustering algorithms (DBSCAN, hierarchical)
- Time-series clustering for temporal patterns
- Ensemble clustering methods
- Real-time cluster assignment for new users
- Integration with feature engineering pipeline