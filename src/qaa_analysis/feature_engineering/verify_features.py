"""
Feature Engineering Verification Script

This script performs automated checks to verify that feature engineering worked correctly.
It implements the recommended verification approach with data integrity checks,
statistical analysis, and logical consistency validation.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
console = Console()


class FeatureVerifier:
    """Verifies feature engineering outputs through comprehensive checks."""
    
    def __init__(self, features_path: str, interactions_path: str = None):
        self.features_path = features_path
        self.interactions_path = interactions_path
        self.features_df = None
        self.interactions_df = None
        self.verification_results = {}
        
    def load_data(self) -> bool:
        """Load feature and interaction data."""
        try:
            # Load features
            console.print(f"[blue]Loading features from: {self.features_path}[/blue]")
            self.features_df = pd.read_parquet(self.features_path)
            console.print(f"[green]✓ Loaded {len(self.features_df):,} users with features[/green]")
            
            # Load interactions if path provided
            if self.interactions_path and os.path.exists(self.interactions_path):
                console.print(f"[blue]Loading interactions from: {self.interactions_path}[/blue]")
                self.interactions_df = pd.read_parquet(self.interactions_path)
                console.print(f"[green]✓ Loaded {len(self.interactions_df):,} interactions[/green]")
            
            return True
        except Exception as e:
            console.print(f"[red]Error loading data: {e}[/red]")
            return False
    
    def verify_data_integrity(self) -> Dict[str, Any]:
        """Check basic data integrity."""
        console.print("\n[bold yellow]1. DATA INTEGRITY CHECKS[/bold yellow]")
        results = {}
        
        # Check dataframe shape
        n_users, n_features = self.features_df.shape
        results['n_users'] = n_users
        results['n_features'] = n_features - 1  # Subtract user_address column
        
        console.print(f"  • Number of users: {n_users:,}")
        console.print(f"  • Number of features: {results['n_features']}")
        
        # Expected feature categories
        protocol_features = [col for col in self.features_df.columns if col.startswith(('total_', 'dex_', 'lending_', 'staking_', 'other_', 'protocol_'))]
        temporal_features = [col for col in self.features_df.columns if any(x in col for x in ['days_', 'active_', 'first_', 'last_', 'recency', 'frequency', 'consistency'])]
        value_features = [col for col in self.features_df.columns if any(x in col for x in ['eth_value', 'gas_', 'avg_', 'median_', 'max_', 'min_', 'std_'])]
        
        results['protocol_features'] = len(protocol_features)
        results['temporal_features'] = len(temporal_features)
        results['value_features'] = len(value_features)
        
        console.print(f"  • Protocol features: {results['protocol_features']}")
        console.print(f"  • Temporal features: {results['temporal_features']}")
        console.print(f"  • Value features: {results['value_features']}")
        
        # Check for user_address column
        if 'user_address' in self.features_df.columns:
            results['has_user_address'] = True
            results['unique_users'] = self.features_df['user_address'].nunique()
            results['duplicate_users'] = n_users - results['unique_users']
            console.print(f"  • Unique users: {results['unique_users']:,}")
            if results['duplicate_users'] > 0:
                console.print(f"  [red]• Duplicate users found: {results['duplicate_users']}[/red]")
        else:
            results['has_user_address'] = False
            console.print("  [red]• Missing user_address column![/red]")
        
        # Check data types
        numeric_cols = self.features_df.select_dtypes(include=[np.number]).columns.tolist()
        results['numeric_features'] = len(numeric_cols)
        console.print(f"  • Numeric features: {results['numeric_features']}")
        
        self.verification_results['data_integrity'] = results
        return results
    
    def verify_feature_ranges(self) -> Dict[str, Any]:
        """Check that feature values are within expected ranges."""
        console.print("\n[bold yellow]2. FEATURE VALUE RANGE CHECKS[/bold yellow]")
        results = {'issues': []}
        
        # Get numeric columns
        numeric_cols = self.features_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Check for negative values in count/interaction features
        count_features = [col for col in numeric_cols if any(x in col for x in ['total_', 'count', 'interactions', 'active_days'])]
        for col in count_features:
            min_val = self.features_df[col].min()
            if min_val < 0:
                issue = f"Negative values in {col}: min={min_val}"
                results['issues'].append(issue)
                console.print(f"  [red]✗ {issue}[/red]")
        
        # Check percentage/ratio features are between 0 and 1
        ratio_features = [col for col in numeric_cols if any(x in col for x in ['ratio', 'diversity', 'percentage', 'share'])]
        for col in ratio_features:
            min_val = self.features_df[col].min()
            max_val = self.features_df[col].max()
            if min_val < 0 or max_val > 1:
                issue = f"Invalid range in {col}: [{min_val:.4f}, {max_val:.4f}]"
                results['issues'].append(issue)
                console.print(f"  [red]✗ {issue}[/red]")
        
        # Check monetary values are non-negative
        value_features = [col for col in numeric_cols if 'value' in col or 'gas' in col]
        for col in value_features:
            min_val = self.features_df[col].min()
            if min_val < 0:
                issue = f"Negative monetary values in {col}: min={min_val}"
                results['issues'].append(issue)
                console.print(f"  [red]✗ {issue}[/red]")
        
        if len(results['issues']) == 0:
            console.print("  [green]✓ All feature ranges are valid[/green]")
        
        self.verification_results['feature_ranges'] = results
        return results
    
    def analyze_feature_distributions(self) -> Dict[str, Any]:
        """Analyze statistical properties of features."""
        console.print("\n[bold yellow]3. FEATURE DISTRIBUTION ANALYSIS[/bold yellow]")
        results = {}
        
        # Get numeric columns
        numeric_cols = self.features_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Calculate basic statistics
        stats_df = self.features_df[numeric_cols].describe()
        
        # Find features with zero or near-zero variance
        zero_variance_features = []
        low_variance_features = []
        
        for col in numeric_cols:
            variance = self.features_df[col].var()
            if variance == 0:
                zero_variance_features.append(col)
            elif variance < 0.01:
                low_variance_features.append(col)
        
        results['zero_variance_features'] = zero_variance_features
        results['low_variance_features'] = low_variance_features
        
        if zero_variance_features:
            console.print(f"  [yellow]• Features with zero variance: {len(zero_variance_features)}[/yellow]")
            for feat in zero_variance_features[:5]:  # Show first 5
                console.print(f"    - {feat}")
        
        # Check for highly skewed features
        skewed_features = []
        for col in numeric_cols:
            skewness = self.features_df[col].skew()
            if abs(skewness) > 2:
                skewed_features.append((col, skewness))
        
        results['highly_skewed_features'] = len(skewed_features)
        console.print(f"  • Highly skewed features (|skew| > 2): {len(skewed_features)}")
        
        # Missing value analysis
        missing_counts = self.features_df.isnull().sum()
        features_with_missing = missing_counts[missing_counts > 0]
        results['features_with_missing'] = len(features_with_missing)
        results['missing_value_details'] = features_with_missing.to_dict()
        
        if features_with_missing.empty:
            console.print("  [green]✓ No missing values found[/green]")
        else:
            console.print(f"  [yellow]• Features with missing values: {len(features_with_missing)}[/yellow]")
            for feat, count in features_with_missing.items()[:5]:  # Show first 5
                percentage = (count / len(self.features_df)) * 100
                console.print(f"    - {feat}: {count} ({percentage:.1f}%)")
        
        self.verification_results['distributions'] = results
        return results
    
    def verify_logical_consistency(self) -> Dict[str, Any]:
        """Check logical relationships between features."""
        console.print("\n[bold yellow]4. LOGICAL CONSISTENCY CHECKS[/bold yellow]")
        results = {'issues': []}
        
        # Check protocol totals
        if 'total_protocols' in self.features_df.columns:
            protocol_cols = [col for col in self.features_df.columns if col.endswith('_protocols') and col != 'total_protocols']
            if protocol_cols:
                calculated_total = self.features_df[protocol_cols].sum(axis=1)
                discrepancies = (self.features_df['total_protocols'] != calculated_total).sum()
                if discrepancies > 0:
                    issue = f"Protocol total mismatch for {discrepancies} users"
                    results['issues'].append(issue)
                    console.print(f"  [red]✗ {issue}[/red]")
                else:
                    console.print("  [green]✓ Protocol totals are consistent[/green]")
        
        # Check temporal consistency
        if 'first_interaction_days_ago' in self.features_df.columns and 'last_interaction_days_ago' in self.features_df.columns:
            temporal_issues = (self.features_df['first_interaction_days_ago'] < self.features_df['last_interaction_days_ago']).sum()
            if temporal_issues > 0:
                issue = f"Temporal inconsistency: first interaction more recent than last for {temporal_issues} users"
                results['issues'].append(issue)
                console.print(f"  [red]✗ {issue}[/red]")
            else:
                console.print("  [green]✓ Temporal features are consistent[/green]")
        
        # Check value consistency
        if 'total_eth_value' in self.features_df.columns:
            protocol_value_cols = [col for col in self.features_df.columns if col.endswith('_eth_value') and col != 'total_eth_value']
            if protocol_value_cols:
                calculated_total_value = self.features_df[protocol_value_cols].sum(axis=1)
                # Allow small floating point differences
                value_discrepancies = (abs(self.features_df['total_eth_value'] - calculated_total_value) > 0.0001).sum()
                if value_discrepancies > 0:
                    issue = f"ETH value total mismatch for {value_discrepancies} users"
                    results['issues'].append(issue)
                    console.print(f"  [red]✗ {issue}[/red]")
                else:
                    console.print("  [green]✓ ETH value totals are consistent[/green]")
        
        # Check gas efficiency
        if 'gas_efficiency' in self.features_df.columns and 'avg_gas_per_tx' in self.features_df.columns:
            # Gas efficiency should be inversely related to avg gas per tx
            invalid_efficiency = (self.features_df['gas_efficiency'] > 1).sum()
            if invalid_efficiency > 0:
                issue = f"Invalid gas efficiency (>1) for {invalid_efficiency} users"
                results['issues'].append(issue)
                console.print(f"  [red]✗ {issue}[/red]")
        
        if len(results['issues']) == 0:
            console.print("  [green]✓ All logical consistency checks passed[/green]")
        
        self.verification_results['logical_consistency'] = results
        return results
    
    def generate_summary_report(self) -> None:
        """Generate a summary report of all verification checks."""
        console.print("\n[bold cyan]VERIFICATION SUMMARY REPORT[/bold cyan]")
        console.print("=" * 60)
        
        # Create summary table
        table = Table(title="Feature Engineering Verification Results")
        table.add_column("Check Category", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Data integrity row
        integrity = self.verification_results.get('data_integrity', {})
        integrity_status = "✓ PASS" if integrity.get('duplicate_users', 0) == 0 else "⚠ WARNING"
        integrity_details = f"{integrity.get('n_users', 0):,} users, {integrity.get('n_features', 0)} features"
        table.add_row("Data Integrity", integrity_status, integrity_details)
        
        # Feature ranges row
        ranges = self.verification_results.get('feature_ranges', {})
        range_status = "✓ PASS" if len(ranges.get('issues', [])) == 0 else f"✗ {len(ranges.get('issues', []))} ISSUES"
        table.add_row("Feature Ranges", range_status, f"{len(ranges.get('issues', []))} issues found")
        
        # Distributions row
        dist = self.verification_results.get('distributions', {})
        dist_status = "⚠ WARNING" if dist.get('zero_variance_features', []) else "✓ PASS"
        dist_details = f"{dist.get('highly_skewed_features', 0)} skewed, {dist.get('features_with_missing', 0)} with missing"
        table.add_row("Distributions", dist_status, dist_details)
        
        # Logical consistency row
        logic = self.verification_results.get('logical_consistency', {})
        logic_status = "✓ PASS" if len(logic.get('issues', [])) == 0 else f"✗ {len(logic.get('issues', []))} ISSUES"
        table.add_row("Logical Consistency", logic_status, f"{len(logic.get('issues', []))} issues found")
        
        console.print(table)
        
        # Save detailed results to JSON
        output_path = Path(self.features_path).parent / "feature_verification_report.json"
        with open(output_path, 'w') as f:
            json.dump(self.verification_results, f, indent=2, default=str)
        console.print(f"\n[green]Detailed report saved to: {output_path}[/green]")
        
        # Print recommendations
        console.print("\n[bold yellow]RECOMMENDATIONS:[/bold yellow]")
        
        total_issues = (
            len(ranges.get('issues', [])) + 
            len(logic.get('issues', [])) + 
            len(dist.get('zero_variance_features', []))
        )
        
        if total_issues == 0:
            console.print("  [green]✓ Feature engineering appears to be working correctly![/green]")
            console.print("  [green]✓ Ready to proceed with clustering analysis.[/green]")
        else:
            console.print("  [yellow]⚠ Some issues were found that may need attention:[/yellow]")
            if ranges.get('issues'):
                console.print("    • Review features with invalid value ranges")
            if dist.get('zero_variance_features'):
                console.print("    • Consider removing zero-variance features before clustering")
            if logic.get('issues'):
                console.print("    • Investigate logical inconsistencies in feature calculations")
    
    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        if not self.load_data():
            return False
        
        self.verify_data_integrity()
        self.verify_feature_ranges()
        self.analyze_feature_distributions()
        self.verify_logical_consistency()
        self.generate_summary_report()
        
        return True


def main():
    """Main execution function."""
    # Define paths
    base_path = Path("data")
    features_path = base_path / "features" / "user_behavioral_features_2025-06-04.parquet"
    interactions_path = base_path / "processed" / "defi_interactions_2025-06-04_to_2025-06-04.parquet"
    
    # Check if features file exists
    if not features_path.exists():
        console.print(f"[red]Feature file not found at: {features_path}[/red]")
        console.print("[yellow]Please run the feature engineering pipeline first:[/yellow]")
        console.print("  python src/qaa_analysis/feature_engineering/run_pipeline.py")
        return
    
    # Create verifier and run checks
    verifier = FeatureVerifier(str(features_path), str(interactions_path))
    verifier.run_all_checks()


if __name__ == "__main__":
    main()