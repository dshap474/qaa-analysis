"""
Quick fix to add user addresses back to cluster data.
"""

import pandas as pd
from pathlib import Path

# Load original feature data with user addresses
features_df = pd.read_parquet('/Users/daniel/Documents/qaa-analysis/data/features/user_behavioral_features_2025-06-05.parquet')

# Load cluster data
cluster_df = pd.read_parquet('/Users/daniel/Documents/qaa-analysis/data/clustering_results/20250606_083121/clustered_users.parquet')

# Add user addresses to cluster data
# Assuming the order is preserved (which it should be)
cluster_df['user'] = features_df['user_address'].values

# Reorder columns to put user first
cols = ['user'] + [col for col in cluster_df.columns if col != 'user']
cluster_df = cluster_df[cols]

# Save fixed data
output_path = Path('/Users/daniel/Documents/qaa-analysis/data/clustering_results/20250606_083121/clustered_users_with_addresses.parquet')
cluster_df.to_parquet(output_path, index=False)

print(f"Fixed cluster data saved to: {output_path}")
print(f"Shape: {cluster_df.shape}")
print(f"Columns: {cluster_df.columns.tolist()[:5]}")
print(f"Sample user addresses: {cluster_df['user'].head(3).tolist()}")