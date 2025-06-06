#!/usr/bin/env python3
"""
Simple script to check the status of feature engineering data.
"""

import os
from pathlib import Path
from datetime import datetime

def main():
    print("Feature Engineering Status Check")
    print("=" * 50)
    print(f"Run at: {datetime.now()}")
    print()
    
    # Check for data directory
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Data directory not found")
        print("\nTo get started:")
        print("1. Create .env file with your GCP_PROJECT_ID")
        print("2. Run: poetry run python -m qaa_analysis.etl.interaction_etl")
        print("   This will create interaction data")
        print("3. Run: poetry run python src/qaa_analysis/feature_engineering/run_pipeline.py")
        print("   This will extract features")
        print("4. Run: poetry run python src/qaa_analysis/feature_engineering/verify_features.py")
        print("   This will verify features")
        return
    
    print("✅ Data directory exists")
    
    # Check subdirectories
    subdirs = ["processed", "features", "analysis", "cache"]
    for subdir in subdirs:
        path = data_dir / subdir
        if path.exists():
            files = list(path.glob("*.parquet")) + list(path.glob("*.json"))
            print(f"  ✅ {subdir}/: {len(files)} files")
            for f in files[:3]:
                print(f"     - {f.name}")
        else:
            print(f"  ❌ {subdir}/: not found")
    
    # Check for specific files
    print("\nChecking for key files:")
    
    # Interaction data
    interaction_files = list(data_dir.glob("processed/defi_interactions_*.parquet"))
    if interaction_files:
        print(f"✅ Interaction data: {len(interaction_files)} file(s)")
        for f in interaction_files:
            print(f"   - {f.name}")
    else:
        print("❌ No interaction data found")
        print("   Run: poetry run python -m qaa_analysis.etl.interaction_etl")
    
    # Feature data
    feature_files = list(data_dir.glob("features/user_behavioral_features_*.parquet"))
    if feature_files:
        print(f"\n✅ Feature data: {len(feature_files)} file(s)")
        for f in feature_files:
            print(f"   - {f.name}")
        print("\n✅ Ready to run verification!")
        print("   Run: poetry run python src/qaa_analysis/feature_engineering/verify_features.py")
    else:
        print("\n❌ No feature data found")
        if interaction_files:
            print("   Run: poetry run python src/qaa_analysis/feature_engineering/run_pipeline.py")

if __name__ == "__main__":
    main()