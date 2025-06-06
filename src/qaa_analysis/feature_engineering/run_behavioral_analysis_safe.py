"""
Safe Behavioral Analysis Runner
---
src/qaa_analysis/feature_engineering/run_behavioral_analysis_safe.py
---
Safe version of behavioral analysis that avoids Unicode encoding issues.
"""

import argparse
from pathlib import Path
from behavioral_analysis import BehavioralAnalyzer

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Safe Analysis Runner Functions                                                     │
# └────────────────────────────────────────────────────────────────────────────────────┘

def run_safe_complete_analysis(data_path: Path, output_dir: Path) -> None:
    """Run complete analysis with safe Unicode handling."""
    print("Running safe complete behavioral analysis...")
    
    analyzer = BehavioralAnalyzer(data_path, output_dir)
    
    print("=" * 60)
    print("Starting behavioral analysis pipeline...")
    
    # Statistical analysis
    print("\n📊 Running statistical analysis...")
    stats = analyzer.generate_summary_statistics()
    print(f"   ✅ Summary statistics: {stats['dataset_info']['total_users']:,} users, {stats['dataset_info']['total_features']} features")
    
    correlations = analyzer.analyze_feature_correlations()
    print(f"   ✅ Correlation analysis: {correlations['total_high_correlations']} high correlations found")
    
    segments = analyzer.identify_user_segments()
    print(f"   ✅ User segmentation: {len(segments['segments'])} segments created")
    
    # Visualizations
    print("\n🎨 Creating visualizations...")
    try:
        analyzer.create_feature_distribution_plots()
        print("   ✅ Feature distribution plots created")
    except Exception as e:
        print(f"   ⚠️  Feature distribution plots failed: {e}")
    
    try:
        analyzer.create_correlation_heatmap()
        print("   ✅ Correlation heatmap created")
    except Exception as e:
        print(f"   ⚠️  Correlation heatmap failed: {e}")
    
    try:
        analyzer.create_segment_analysis_plots()
        print("   ✅ Segment analysis plots created")
    except Exception as e:
        print(f"   ⚠️  Segment analysis plots failed: {e}")
    
    # Safe data export
    print("\n💾 Saving results...")
    try:
        analyzer.save_analysis_results()
        print("   ✅ Analysis results saved to JSON")
    except Exception as e:
        print(f"   ⚠️  JSON export failed: {e}")
    
    # Create a simple text summary instead of markdown report
    try:
        summary_path = output_dir / 'analysis_summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("BEHAVIORAL ANALYSIS SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Dataset: {stats['dataset_info']['total_users']:,} users, {stats['dataset_info']['total_features']} features\n")
            f.write(f"High correlations found: {correlations['total_high_correlations']}\n")
            f.write(f"User segments created: {len(segments['segments'])}\n\n")
            
            f.write("SEGMENT BREAKDOWN:\n")
            for segment_name, segment_data in segments['segments'].items():
                f.write(f"  {segment_name}: {segment_data['user_count']:,} users ({segment_data['percentage']:.1f}%)\n")
            
            if correlations['high_correlations']:
                f.write(f"\nTOP CORRELATIONS:\n")
                for i, corr in enumerate(correlations['high_correlations'][:10]):
                    f.write(f"  {i+1}. {corr['feature1']} <-> {corr['feature2']}: {corr['correlation']:.3f}\n")
        
        print(f"   ✅ Text summary saved to: {summary_path}")
    except Exception as e:
        print(f"   ⚠️  Text summary failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Safe analysis complete!")
    print(f"📁 Results saved to: {output_dir}")
    print("📊 Files created:")
    print("   - analysis_results.json (complete data)")
    print("   - analysis_summary.txt (readable summary)")
    print("   - feature_distributions.png")
    print("   - correlation_heatmap.png") 
    print("   - segment_analysis.png")


def run_quick_safe_analysis(data_path: Path, output_dir: Path) -> None:
    """Run quick analysis with safe handling."""
    print("Running quick safe behavioral analysis...")
    
    analyzer = BehavioralAnalyzer(data_path, output_dir)
    
    # Basic statistics
    stats = analyzer.generate_summary_statistics()
    print(f"\n📊 Dataset: {stats['dataset_info']['total_users']:,} users, {stats['dataset_info']['total_features']} features")
    
    # Quick visualizations
    try:
        analyzer.create_feature_distribution_plots(top_n=12)
        print("✅ Feature distribution plots created")
    except Exception as e:
        print(f"⚠️  Distribution plots failed: {e}")
    
    try:
        analyzer.create_correlation_heatmap(top_n=20)
        print("✅ Correlation heatmap created")
    except Exception as e:
        print(f"⚠️  Correlation heatmap failed: {e}")
    
    print(f"✅ Quick analysis complete! Results in: {output_dir}")


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Main CLI Interface                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

def main():
    """Main CLI interface for safe behavioral analysis."""
    parser = argparse.ArgumentParser(description="Run safe behavioral analysis on user features")
    
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/features/user_behavioral_features_2025-06-04.parquet",
        help="Path to behavioral features parquet file"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/analysis/behavioral_features_safe",
        help="Output directory for analysis results"
    )
    
    parser.add_argument(
        "--analysis-type",
        choices=["quick", "complete"],
        default="complete",
        help="Type of analysis to run"
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
            run_quick_safe_analysis(data_path, output_dir)
        elif args.analysis_type == "complete":
            run_safe_complete_analysis(data_path, output_dir)
        
        print(f"\n🎉 Safe analysis complete! Check results in: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main() 