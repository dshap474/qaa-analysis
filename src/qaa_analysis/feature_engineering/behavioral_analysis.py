"""
Behavioral Features Analysis
---
src/qaa_analysis/feature_engineering/behavioral_analysis.py
---
Comprehensive analysis program for user behavioral features parquet file.
Provides statistical analysis, visualization, and insights into user behavior patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import warnings
from datetime import datetime
import json

# Configuration constants
FIGURE_SIZE = (12, 8)
CORRELATION_THRESHOLD = 0.7
TOP_N_FEATURES = 20

warnings.filterwarnings('ignore')

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ BehavioralAnalyzer Class                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘

class BehavioralAnalyzer:
    """
    Comprehensive analyzer for user behavioral features.
    
    Provides statistical analysis, visualization, and insights into DeFi user behavior
    patterns extracted from transaction data.
    """
    
    def __init__(self, data_path: Path, output_dir: Optional[Path] = None):
        """
        Initialize the behavioral analyzer.
        
        Args:
            data_path: Path to the behavioral features parquet file
            output_dir: Directory to save analysis outputs (default: data/analysis)
        """
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir) if output_dir else Path("data/analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.df = self._load_data()
        self.feature_columns = self._get_feature_columns()
        self.analysis_results = {}
        
        print(f"Loaded behavioral data: {self.df.shape[0]} users, {len(self.feature_columns)} features")
    
    def _load_data(self) -> pd.DataFrame:
        """Load and validate the behavioral features data."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        df = pd.read_parquet(self.data_path)
        
        # Basic validation
        if 'user_address' not in df.columns:
            raise ValueError("Data must contain 'user_address' column")
        
        return df
    
    def _get_feature_columns(self) -> List[str]:
        """Get list of feature columns (excluding user_address)."""
        return [col for col in self.df.columns if col != 'user_address']
    
    # ┌────────────────────────────────────────────────────────────────────────────────────┐
    # │ Statistical Analysis Methods                                                       │
    # └────────────────────────────────────────────────────────────────────────────────────┘
    
    def generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        print("Generating summary statistics...")
        
        stats = {
            'dataset_info': {
                'total_users': len(self.df),
                'total_features': len(self.feature_columns),
                'data_shape': self.df.shape,
                'analysis_date': datetime.now().isoformat()
            },
            'feature_statistics': {},
            'data_quality': {}
        }
        
        # Feature statistics
        feature_stats = self.df[self.feature_columns].describe()
        stats['feature_statistics'] = feature_stats.to_dict()
        
        # Data quality metrics
        stats['data_quality'] = {
            'missing_values': self.df[self.feature_columns].isnull().sum().to_dict(),
            'zero_values': (self.df[self.feature_columns] == 0).sum().to_dict(),
            'infinite_values': np.isinf(self.df[self.feature_columns]).sum().to_dict()
        }
        
        # Feature distributions
        stats['distributions'] = {
            'skewness': self.df[self.feature_columns].skew().to_dict(),
            'kurtosis': self.df[self.feature_columns].kurtosis().to_dict()
        }
        
        self.analysis_results['summary_statistics'] = stats
        return stats
    
    def analyze_feature_correlations(self, threshold: float = CORRELATION_THRESHOLD) -> Dict[str, Any]:
        """Analyze correlations between features."""
        print("Analyzing feature correlations...")
        
        # Calculate correlation matrix
        corr_matrix = self.df[self.feature_columns].corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= threshold:
                    high_corr_pairs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        # Sort by absolute correlation
        high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        correlation_analysis = {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlations': high_corr_pairs,
            'correlation_threshold': threshold,
            'total_high_correlations': len(high_corr_pairs)
        }
        
        self.analysis_results['correlations'] = correlation_analysis
        return correlation_analysis
    
    def identify_user_segments(self, n_segments: int = 5) -> Dict[str, Any]:
        """Identify user segments based on activity levels."""
        print("Identifying user segments...")
        
        # Calculate total activity score
        activity_features = [col for col in self.feature_columns if 'interactions' in col]
        self.df['total_activity'] = self.df[activity_features].sum(axis=1)
        
        # Create activity-based segments with duplicate handling
        try:
            self.df['activity_segment'] = pd.qcut(
                self.df['total_activity'], 
                q=n_segments, 
                labels=[f'Segment_{i+1}' for i in range(n_segments)],
                duplicates='drop'
            )
        except ValueError:
            # Fallback to cut if qcut fails due to too many duplicates
            print("  Warning: Using cut instead of qcut due to many duplicate values")
            max_activity = self.df['total_activity'].max()
            bins = np.linspace(0, max_activity, n_segments + 1)
            self.df['activity_segment'] = pd.cut(
                self.df['total_activity'], 
                bins=bins, 
                labels=[f'Segment_{i+1}' for i in range(n_segments)],
                include_lowest=True
            )
        
        # Analyze segments
        segment_analysis = {}
        valid_segments = self.df['activity_segment'].dropna().unique()
        
        for segment in valid_segments:
            segment_data = self.df[self.df['activity_segment'] == segment]
            if len(segment_data) > 0:  # Only analyze non-empty segments
                segment_analysis[segment] = {
                    'user_count': len(segment_data),
                    'percentage': len(segment_data) / len(self.df) * 100,
                    'avg_total_activity': segment_data['total_activity'].mean(),
                    'top_features': segment_data[self.feature_columns].mean().nlargest(10).to_dict()
                }
        
        segmentation_results = {
            'segments': segment_analysis,
            'segment_distribution': self.df['activity_segment'].value_counts(dropna=True).to_dict()
        }
        
        self.analysis_results['segmentation'] = segmentation_results
        return segmentation_results
    
    # ┌────────────────────────────────────────────────────────────────────────────────────┐
    # │ Visualization Methods                                                              │
    # └────────────────────────────────────────────────────────────────────────────────────┘
    
    def create_feature_distribution_plots(self, top_n: int = TOP_N_FEATURES) -> None:
        """Create distribution plots for top features."""
        print(f"Creating distribution plots for top {top_n} features...")
        
        # Select top features by variance
        feature_variances = self.df[self.feature_columns].var().sort_values(ascending=False)
        top_features = feature_variances.head(top_n).index.tolist()
        
        # Create subplots
        n_cols = 4
        n_rows = (len(top_features) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5*n_rows))
        axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else axes
        
        for i, feature in enumerate(top_features):
            if i < len(axes):
                ax = axes[i]
                self.df[feature].hist(bins=50, ax=ax, alpha=0.7)
                ax.set_title(f'{feature}\n(Variance: {feature_variances[feature]:.2f})')
                ax.set_xlabel('Value')
                ax.set_ylabel('Frequency')
        
        # Hide unused subplots
        for i in range(len(top_features), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'feature_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_correlation_heatmap(self, top_n: int = 30) -> None:
        """Create correlation heatmap for top features."""
        print(f"Creating correlation heatmap for top {top_n} features...")
        
        # Select top features by variance
        feature_variances = self.df[self.feature_columns].var().sort_values(ascending=False)
        top_features = feature_variances.head(top_n).index.tolist()
        
        # Create correlation matrix
        corr_matrix = self.df[top_features].corr()
        
        # Create heatmap
        plt.figure(figsize=(16, 14))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(
            corr_matrix, 
            mask=mask,
            annot=False,
            cmap='coolwarm',
            center=0,
            square=True,
            fmt='.2f',
            cbar_kws={'shrink': 0.8}
        )
        
        plt.title(f'Feature Correlation Heatmap (Top {top_n} Features)')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_segment_analysis_plots(self) -> None:
        """Create plots for user segment analysis."""
        if 'activity_segment' not in self.df.columns:
            print("Running segmentation analysis first...")
            self.identify_user_segments()
        
        print("Creating segment analysis plots...")
        
        # Check if we have valid segments
        segment_counts = self.df['activity_segment'].value_counts(dropna=True)
        if len(segment_counts) == 0:
            print("  Warning: No valid segments found, skipping segment plots")
            return
        
        # Segment distribution pie chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        ax1.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%')
        ax1.set_title('User Distribution by Activity Segment')
        
        # Activity distribution by segment - only for users with valid segments
        df_with_segments = self.df.dropna(subset=['activity_segment'])
        if len(df_with_segments) > 0:
            df_with_segments.boxplot(column='total_activity', by='activity_segment', ax=ax2)
            ax2.set_title('Activity Distribution by Segment')
            ax2.set_xlabel('Activity Segment')
            ax2.set_ylabel('Total Activity')
        else:
            ax2.text(0.5, 0.5, 'No valid segments for boxplot', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Activity Distribution by Segment (No Data)')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'segment_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # ┌────────────────────────────────────────────────────────────────────────────────────┐
    # │ Report Generation Methods                                                          │
    # └────────────────────────────────────────────────────────────────────────────────────┘
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report."""
        print("Generating comprehensive analysis report...")
        
        # Run all analyses if not already done
        if 'summary_statistics' not in self.analysis_results:
            self.generate_summary_statistics()
        if 'correlations' not in self.analysis_results:
            self.analyze_feature_correlations()
        if 'segmentation' not in self.analysis_results:
            self.identify_user_segments()
        
        # Generate report
        report_lines = [
            "# User Behavioral Features Analysis Report",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Dataset Overview",
            f"- **Total Users**: {self.analysis_results['summary_statistics']['dataset_info']['total_users']:,}",
            f"- **Total Features**: {self.analysis_results['summary_statistics']['dataset_info']['total_features']}",
            f"- **Data Shape**: {self.analysis_results['summary_statistics']['dataset_info']['data_shape']}",
            "",
            "## Key Findings",
            "",
            "### Data Quality",
        ]
        
        # Data quality summary
        missing_values = self.analysis_results['summary_statistics']['data_quality']['missing_values']
        total_missing = sum(missing_values.values())
        report_lines.extend([
            f"- **Total Missing Values**: {total_missing:,}",
            f"- **Features with Missing Values**: {sum(1 for v in missing_values.values() if v > 0)}",
            ""
        ])
        
        # Correlation insights
        high_corr_count = self.analysis_results['correlations']['total_high_correlations']
        report_lines.extend([
            "### Feature Correlations",
            f"- **High Correlations Found**: {high_corr_count} pairs (threshold: {CORRELATION_THRESHOLD})",
            ""
        ])
        
        if high_corr_count > 0:
            top_correlations = self.analysis_results['correlations']['high_correlations'][:5]
            report_lines.append("**Top Correlated Feature Pairs**:")
            for corr in top_correlations:
                report_lines.append(f"- {corr['feature1']} <-> {corr['feature2']}: {corr['correlation']:.3f}")
            report_lines.append("")
        
        # Segmentation insights
        segments = self.analysis_results['segmentation']['segments']
        report_lines.extend([
            "### User Segmentation",
            f"- **Number of Segments**: {len(segments)}",
            ""
        ])
        
        for segment_name, segment_data in segments.items():
            report_lines.extend([
                f"**{segment_name}**:",
                f"- Users: {segment_data['user_count']:,} ({segment_data['percentage']:.1f}%)",
                f"- Avg Activity: {segment_data['avg_total_activity']:.1f}",
                ""
            ])
        
        # Save report
        report_content = "\n".join(report_lines)
        report_path = self.output_dir / 'behavioral_analysis_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Analysis report saved to: {report_path}")
        return report_content
    
    def save_analysis_results(self) -> None:
        """Save all analysis results to JSON file."""
        results_path = self.output_dir / 'analysis_results.json'
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        serializable_results = convert_numpy_types(self.analysis_results)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis results saved to: {results_path}")
    
    # ┌────────────────────────────────────────────────────────────────────────────────────┐
    # │ Main Analysis Pipeline                                                             │
    # └────────────────────────────────────────────────────────────────────────────────────┘
    
    def run_complete_analysis(self) -> None:
        """Run complete behavioral analysis pipeline."""
        print("Starting complete behavioral analysis...")
        print("=" * 60)
        
        # Statistical analysis
        self.generate_summary_statistics()
        self.analyze_feature_correlations()
        self.identify_user_segments()
        
        # Visualizations
        self.create_feature_distribution_plots()
        self.create_correlation_heatmap()
        self.create_segment_analysis_plots()
        
        # Reports
        self.generate_analysis_report()
        self.save_analysis_results()
        
        print("=" * 60)
        print("Analysis complete! Check the output directory for results:")
        print(f"  📁 {self.output_dir}")
        print(f"  📊 Plots: feature_distributions.png, correlation_heatmap.png, segment_analysis.png")
        print(f"  📄 Report: behavioral_analysis_report.md")
        print(f"  💾 Data: analysis_results.json")


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Main Execution                                                                     │
# └────────────────────────────────────────────────────────────────────────────────────┘

def main():
    """Main function to run behavioral analysis."""
    # Default data path
    data_path = Path("data/features/user_behavioral_features_2025-06-04.parquet")
    output_dir = Path("data/analysis/behavioral_features")
    
    try:
        # Initialize analyzer
        analyzer = BehavioralAnalyzer(data_path, output_dir)
        
        # Run complete analysis
        analyzer.run_complete_analysis()
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main() 