"""
Run Behavioral Analysis
---
src/qaa_analysis/feature_engineering/run_behavioral_analysis.py
---
Simple script to run behavioral analysis on user features with various options.
"""

import argparse
from pathlib import Path
from behavioral_analysis import BehavioralAnalyzer

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Analysis Runner Functions                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘

def run_quick_analysis(data_path: Path, output_dir: Path) -> None:
    """Run a quick analysis with basic statistics and visualizations."""
    print("Running quick behavioral analysis...")
    
    analyzer = BehavioralAnalyzer(data_path, output_dir)
    
    # Basic statistics
    stats = analyzer.generate_summary_statistics()
    print(f"\n📊 Dataset: {stats['dataset_info']['total_users']:,} users, {stats['dataset_info']['total_features']} features")
    
    # Quick visualizations
    analyzer.create_feature_distribution_plots(top_n=12)
    analyzer.create_correlation_heatmap(top_n=20)
    
    print(f"✅ Quick analysis complete! Results in: {output_dir}")


def run_detailed_analysis(data_path: Path, output_dir: Path) -> None:
    """Run detailed analysis with all features."""
    print("Running detailed behavioral analysis...")
    
    analyzer = BehavioralAnalyzer(data_path, output_dir)
    analyzer.run_complete_analysis()


def run_correlation_analysis(data_path: Path, output_dir: Path, threshold: float = 0.7) -> None:
    """Focus on correlation analysis."""
    print(f"Running correlation analysis (threshold: {threshold})...")
    
    analyzer = BehavioralAnalyzer(data_path, output_dir)
    
    # Correlation analysis
    corr_results = analyzer.analyze_feature_correlations(threshold=threshold)
    
    print(f"\n🔗 Found {corr_results['total_high_correlations']} high correlations")
    
    if corr_results['high_correlations']:
        print("\nTop 10 correlations:")
        for i, corr in enumerate(corr_results['high_correlations'][:10]):
            print(f"  {i+1}. {corr['feature1']} <-> {corr['feature2']}: {corr['correlation']:.3f}")
    
    # Create correlation heatmap
    analyzer.create_correlation_heatmap(top_n=30)
    analyzer.save_analysis_results()


def run_segmentation_analysis(data_path: Path, output_dir: Path, n_segments: int = 5) -> None:
    """Focus on user segmentation analysis."""
    print(f"Running segmentation analysis ({n_segments} segments)...")
    
    analyzer = BehavioralAnalyzer(data_path, output_dir)
    
    # Segmentation analysis
    seg_results = analyzer.identify_user_segments(n_segments=n_segments)
    
    print(f"\n👥 Created {len(seg_results['segments'])} user segments:")
    for segment_name, segment_data in seg_results['segments'].items():
        print(f"  {segment_name}: {segment_data['user_count']:,} users ({segment_data['percentage']:.1f}%)")
    
    # Create segment visualizations
    analyzer.create_segment_analysis_plots()
    analyzer.save_analysis_results()


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Main CLI Interface                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

def main():
    """Main CLI interface for behavioral analysis."""
    parser = argparse.ArgumentParser(description="Run behavioral analysis on user features")
    
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/features/user_behavioral_features_2025-06-04.parquet",
        help="Path to behavioral features parquet file"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/analysis/behavioral_features",
        help="Output directory for analysis results"
    )
    
    parser.add_argument(
        "--analysis-type",
        choices=["quick", "detailed", "correlation", "segmentation"],
        default="detailed",
        help="Type of analysis to run"
    )
    
    parser.add_argument(
        "--correlation-threshold",
        type=float,
        default=0.7,
        help="Correlation threshold for correlation analysis"
    )
    
    parser.add_argument(
        "--n-segments",
        type=int,
        default=5,
        help="Number of segments for segmentation analysis"
    )
    
    args = parser.parse_args()
    
    # Convert paths
    data_path = Path(args.data_path)
    output_dir = Path(args.output_dir)
    
    # Validate data path
    if not data_path.exists():
        print(f"❌ Error: Data file not found: {data_path}")
        return
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run selected analysis
    try:
        if args.analysis_type == "quick":
            run_quick_analysis(data_path, output_dir)
        elif args.analysis_type == "detailed":
            run_detailed_analysis(data_path, output_dir)
        elif args.analysis_type == "correlation":
            run_correlation_analysis(data_path, output_dir, args.correlation_threshold)
        elif args.analysis_type == "segmentation":
            run_segmentation_analysis(data_path, output_dir, args.n_segments)
        
        print(f"\n🎉 Analysis complete! Check results in: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main() 