"""
Analyze Feature Engineering Results.

This script analyzes the generated feature matrix and provides insights
about the extracted behavioral features.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json


def analyze_feature_matrix():
    """Analyze the generated feature matrix."""
    
    # Load the feature matrix
    feature_path = Path("data/features/user_behavioral_features_2025-06-04.parquet")
    metadata_path = Path("data/features/feature_metadata.json")
    
    print("=" * 80)
    print("FEATURE MATRIX ANALYSIS")
    print("=" * 80)
    
    # Load data
    df = pd.read_parquet(feature_path)
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Number of users: {len(df):,}")
    print(f"Number of features: {len(df.columns) - 1}")  # -1 for user_address
    
    # Separate feature columns
    feature_cols = [col for col in df.columns if col != 'user_address']
    
    # Basic statistics
    print("\n" + "=" * 50)
    print("FEATURE STATISTICS")
    print("=" * 50)
    
    # Count features by extractor
    extractor_counts = {}
    for feature, meta in metadata.items():
        extractor = meta.get('extractor', 'Unknown')
        extractor_counts[extractor] = extractor_counts.get(extractor, 0) + 1
    
    print("Features by extractor:")
    for extractor, count in extractor_counts.items():
        print(f"  - {extractor}: {count} features")
    
    # Data type distribution
    print("\nData types:")
    dtype_counts = df[feature_cols].dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  - {dtype}: {count} features")
    
    # Non-zero feature analysis
    print("\n" + "=" * 50)
    print("FEATURE COMPLETENESS")
    print("=" * 50)
    
    non_zero_counts = (df[feature_cols] != 0).sum()
    zero_features = non_zero_counts[non_zero_counts == 0].index.tolist()
    
    print(f"Features with all zeros: {len(zero_features)}")
    if zero_features:
        print("Zero features:", zero_features[:10])  # Show first 10
    
    # User activity analysis
    print("\n" + "=" * 50)
    print("USER ACTIVITY PATTERNS")
    print("=" * 50)
    
    # Non-zero features per user
    non_zero_per_user = (df[feature_cols] != 0).sum(axis=1)
    print(f"Average non-zero features per user: {non_zero_per_user.mean():.1f}")
    print(f"Median non-zero features per user: {non_zero_per_user.median():.1f}")
    print(f"Min non-zero features per user: {non_zero_per_user.min()}")
    print(f"Max non-zero features per user: {non_zero_per_user.max()}")
    
    # Most active users
    print("\nMost active users (by non-zero features):")
    top_users = non_zero_per_user.nlargest(5)
    for user_idx, count in top_users.items():
        user_addr = df.iloc[user_idx]['user_address']
        print(f"  {user_addr[:10]}...: {count} features")
    
    # Feature popularity
    print("\n" + "=" * 50)
    print("FEATURE POPULARITY")
    print("=" * 50)
    
    feature_popularity = (df[feature_cols] != 0).sum().sort_values(ascending=False)
    print("Most common features (users with non-zero values):")
    for feature, count in feature_popularity.head(10).items():
        pct = (count / len(df)) * 100
        print(f"  {feature}: {count:,} users ({pct:.1f}%)")
    
    print("\nLeast common features:")
    for feature, count in feature_popularity.tail(10).items():
        pct = (count / len(df)) * 100
        print(f"  {feature}: {count:,} users ({pct:.1f}%)")
    
    # Value distribution analysis for key features
    print("\n" + "=" * 50)
    print("KEY FEATURE DISTRIBUTIONS")
    print("=" * 50)
    
    key_features = ['total_interactions', 'unique_protocols', 'total_eth_value', 'total_gas_used']
    
    for feature in key_features:
        if feature in df.columns:
            values = df[feature]
            non_zero_values = values[values > 0]
            
            print(f"\n{feature}:")
            print(f"  Non-zero users: {len(non_zero_values):,} ({len(non_zero_values)/len(df)*100:.1f}%)")
            if len(non_zero_values) > 0:
                print(f"  Mean: {non_zero_values.mean():.2f}")
                print(f"  Median: {non_zero_values.median():.2f}")
                print(f"  Min: {non_zero_values.min():.2f}")
                print(f"  Max: {non_zero_values.max():.2f}")
    
    # Protocol usage analysis
    print("\n" + "=" * 50)
    print("PROTOCOL USAGE ANALYSIS")
    print("=" * 50)
    
    protocol_features = [col for col in feature_cols if '_interactions' in col and 'total' not in col]
    protocol_usage = df[protocol_features].sum().sort_values(ascending=False)
    
    print("Total interactions by protocol:")
    for protocol, total in protocol_usage.head(10).items():
        print(f"  {protocol}: {total:,} interactions")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    analyze_feature_matrix() 