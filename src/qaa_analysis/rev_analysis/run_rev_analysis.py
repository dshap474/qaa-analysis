"""
Run complete REV analysis for clustered users.

This script orchestrates the full REV analysis pipeline:
1. Load cluster data
2. Load/calculate REV data from interactions
3. Analyze REV patterns by cluster
4. Generate visualizations and reports
"""

import sys
from pathlib import Path
import logging
import pandas as pd
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from rev_cluster_analyzer import RevClusterAnalyzer
from rev_visualizations import RevVisualizer


def setup_logging(output_dir: Path) -> logging.Logger:
    """Setup logging configuration."""
    log_file = output_dir / 'rev_analysis.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """Run the complete REV analysis pipeline."""
    
    # Configuration
    CLUSTER_DATA_PATH = Path('/Users/daniel/Documents/qaa-analysis/data/clustering_results/20250606_083121/clustered_users_with_addresses.parquet')
    INTERACTION_DATA_PATH = Path('/Users/daniel/Documents/qaa-analysis/data/cache/query_57d486c1405131be.parquet')
    OUTPUT_DIR = Path('/Users/daniel/Documents/qaa-analysis/data/rev_analysis_results') / datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Setup logging
    logger = setup_logging(OUTPUT_DIR)
    logger.info("=" * 60)
    logger.info("Starting REV Cluster Analysis")
    logger.info("=" * 60)
    
    try:
        # Step 1: Initialize analyzer
        logger.info("Initializing REV analyzer...")
        analyzer = RevClusterAnalyzer(
            cluster_data_path=CLUSTER_DATA_PATH,
            interaction_data_path=INTERACTION_DATA_PATH
        )
        
        # Step 2: Merge and calculate metrics
        logger.info("Merging REV data with clusters...")
        merged_data = analyzer.merge_with_clusters()
        
        logger.info("Calculating cluster-level metrics...")
        cluster_metrics = analyzer.calculate_cluster_metrics()
        
        # Save cluster metrics
        metrics_path = OUTPUT_DIR / 'cluster_rev_metrics.csv'
        cluster_metrics.to_csv(metrics_path, index=False)
        logger.info(f"Saved cluster metrics to {metrics_path}")
        
        # Step 3: Identify top users
        logger.info("Identifying top REV users per cluster...")
        top_users = analyzer.identify_top_rev_users(n=10)
        
        # Save top users for each cluster
        for cluster, users_df in top_users.items():
            top_users_path = OUTPUT_DIR / f'top_rev_users_cluster_{cluster}.csv'
            users_df.to_csv(top_users_path, index=False)
            logger.info(f"Saved top users for cluster {cluster}")
        
        # Step 4: Analyze efficiency
        logger.info("Analyzing REV efficiency patterns...")
        efficiency_metrics = analyzer.analyze_rev_efficiency()
        efficiency_path = OUTPUT_DIR / 'efficiency_metrics.csv'
        efficiency_metrics.to_csv(efficiency_path)
        logger.info(f"Saved efficiency metrics to {efficiency_path}")
        
        # Step 5: Generate summary report
        logger.info("Generating summary report...")
        summary_report = analyzer.generate_summary_report()
        
        report_path = OUTPUT_DIR / 'rev_analysis_summary.txt'
        with open(report_path, 'w') as f:
            f.write(summary_report)
        logger.info(f"Saved summary report to {report_path}")
        
        # Print summary to console
        print("\n" + summary_report)
        
        # Step 6: Create visualizations
        logger.info("Creating visualizations...")
        visualizer = RevVisualizer(analyzer)
        
        plots_dir = OUTPUT_DIR / 'plots'
        plots_dir.mkdir(exist_ok=True)
        
        visualizer.create_summary_dashboard(plots_dir)
        
        # Step 7: Save enriched data
        logger.info("Saving enriched cluster data with REV...")
        enriched_path = OUTPUT_DIR / 'clustered_users_with_rev.parquet'
        merged_data.to_parquet(enriched_path, index=False)
        logger.info(f"Saved enriched data to {enriched_path}")
        
        # Step 8: Create metadata file
        metadata = {
            'analysis_timestamp': datetime.now().isoformat(),
            'cluster_data_source': str(CLUSTER_DATA_PATH),
            'interaction_data_source': str(INTERACTION_DATA_PATH),
            'total_users': len(merged_data),
            'users_with_rev': int((merged_data['rev_eth'] > 0).sum()),
            'total_rev_eth': float(merged_data['rev_eth'].sum()),
            'cluster_count': int(merged_data['cluster'].nunique()),
            'output_files': {
                'cluster_metrics': 'cluster_rev_metrics.csv',
                'summary_report': 'rev_analysis_summary.txt',
                'enriched_data': 'clustered_users_with_rev.parquet',
                'plots': 'plots/'
            }
        }
        
        metadata_path = OUTPUT_DIR / 'analysis_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_path}")
        
        # Final summary
        logger.info("=" * 60)
        logger.info("REV Analysis Complete!")
        logger.info(f"Results saved to: {OUTPUT_DIR}")
        logger.info("=" * 60)
        
        print(f"\n✅ Analysis complete! Results saved to:\n{OUTPUT_DIR}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()