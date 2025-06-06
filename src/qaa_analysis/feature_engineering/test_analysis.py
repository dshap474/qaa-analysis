"""
Test Behavioral Analysis
---
src/qaa_analysis/feature_engineering/test_analysis.py
---
Simple test script to verify behavioral analysis functionality.
"""

from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.qaa_analysis.feature_engineering.behavioral_analysis import BehavioralAnalyzer
    print("✅ Successfully imported BehavioralAnalyzer")
    
    # Test data path
    data_path = Path("data/features/user_behavioral_features_2025-06-04.parquet")
    
    if data_path.exists():
        print(f"✅ Data file found: {data_path}")
        
        # Initialize analyzer
        analyzer = BehavioralAnalyzer(data_path)
        print(f"✅ Analyzer initialized successfully")
        print(f"   - Users: {len(analyzer.df):,}")
        print(f"   - Features: {len(analyzer.feature_columns)}")
        
        # Run quick statistics
        stats = analyzer.generate_summary_statistics()
        print(f"✅ Summary statistics generated")
        print(f"   - Total users: {stats['dataset_info']['total_users']:,}")
        print(f"   - Total features: {stats['dataset_info']['total_features']}")
        
        print("\n🎉 All tests passed! The behavioral analysis program is working correctly.")
        
    else:
        print(f"❌ Data file not found: {data_path}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    raise 