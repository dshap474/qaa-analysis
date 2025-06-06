"""
Debug Unicode Issues
---
src/qaa_analysis/feature_engineering/debug_unicode.py
---
Debug script to identify Unicode character issues in the behavioral analysis.
"""

from pathlib import Path
import sys
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.qaa_analysis.feature_engineering.behavioral_analysis import BehavioralAnalyzer

def debug_unicode_issues():
    """Debug Unicode character issues in the analysis."""
    print("🔍 Debugging Unicode issues...")
    
    # Initialize analyzer
    data_path = Path("data/features/user_behavioral_features_2025-06-04.parquet")
    analyzer = BehavioralAnalyzer(data_path)
    
    # Check feature names for Unicode characters
    print("\n📋 Checking feature names for Unicode characters...")
    for feature in analyzer.feature_columns:
        try:
            feature.encode('ascii')
        except UnicodeEncodeError as e:
            print(f"  ❌ Unicode in feature name: {feature} - {e}")
    
    # Run individual analyses to isolate the issue
    print("\n📊 Running summary statistics...")
    try:
        stats = analyzer.generate_summary_statistics()
        print("  ✅ Summary statistics completed")
    except Exception as e:
        print(f"  ❌ Error in summary statistics: {e}")
        return
    
    print("\n🔗 Running correlation analysis...")
    try:
        correlations = analyzer.analyze_feature_correlations()
        print("  ✅ Correlation analysis completed")
        print(f"  Found {correlations['total_high_correlations']} high correlations")
        
        # Check correlation results for Unicode
        if correlations['high_correlations']:
            print("  Checking correlation pairs for Unicode...")
            for i, corr in enumerate(correlations['high_correlations'][:5]):
                try:
                    test_string = f"{corr['feature1']} <-> {corr['feature2']}: {corr['correlation']:.3f}"
                    test_string.encode('ascii')
                    print(f"    ✅ Correlation {i+1}: ASCII-safe")
                except UnicodeEncodeError as e:
                    print(f"    ❌ Unicode in correlation {i+1}: {test_string} - {e}")
                    print(f"        Feature1: {repr(corr['feature1'])}")
                    print(f"        Feature2: {repr(corr['feature2'])}")
                    
    except Exception as e:
        print(f"  ❌ Error in correlation analysis: {e}")
        return
    
    print("\n👥 Running segmentation analysis...")
    try:
        segments = analyzer.identify_user_segments()
        print("  ✅ Segmentation analysis completed")
    except Exception as e:
        print(f"  ❌ Error in segmentation analysis: {e}")
        return
    
    print("\n📄 Testing report generation...")
    try:
        # Try to generate report content without writing to file
        report_lines = [
            "# Test Report",
            f"Total Users: {stats['dataset_info']['total_users']:,}",
            f"Total Features: {stats['dataset_info']['total_features']}",
        ]
        
        # Add correlation info
        if correlations['high_correlations']:
            report_lines.append("Top Correlations:")
            for corr in correlations['high_correlations'][:3]:
                line = f"- {corr['feature1']} <-> {corr['feature2']}: {corr['correlation']:.3f}"
                report_lines.append(line)
                # Test encoding
                try:
                    line.encode('ascii')
                except UnicodeEncodeError as e:
                    print(f"  ❌ Unicode in line: {line}")
                    print(f"      Error: {e}")
        
        # Test the full report content
        report_content = "\n".join(report_lines)
        try:
            report_content.encode('ascii')
            print("  ✅ Report content is ASCII-safe")
        except UnicodeEncodeError as e:
            print(f"  ❌ Unicode in report content at position {e.start}: {e}")
            print(f"      Problematic character: {repr(report_content[e.start:e.end])}")
            
        # Try writing with UTF-8
        test_path = Path("data/analysis/test_report.md")
        test_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"  ✅ Successfully wrote test report to: {test_path}")
        
    except Exception as e:
        print(f"  ❌ Error in report generation: {e}")
        return
    
    print("\n🎉 Unicode debugging completed!")

if __name__ == "__main__":
    debug_unicode_issues() 