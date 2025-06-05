#!/usr/bin/env python3
"""
Verify the output of the interaction ETL.
"""

import pandas as pd
from pathlib import Path

def main():
    # Load the output file
    output_file = Path("data/processed/defi_interactions_2025-06-04_to_2025-06-04.parquet")
    
    if not output_file.exists():
        print(f"❌ Output file not found: {output_file}")
        return
    
    print(f"✅ Loading output file: {output_file}")
    df = pd.read_parquet(output_file)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    
    print(f"\n📋 Columns:")
    for col in df.columns:
        print(f"   • {col}")
    
    print(f"\n🏷️ Protocol Category Distribution:")
    protocol_counts = df['protocol_category'].value_counts()
    for protocol, count in protocol_counts.items():
        print(f"   • {protocol}: {count:,} interactions")
    
    print(f"\n🔗 Contract Role Distribution (Top 10):")
    role_counts = df['contract_role'].value_counts()
    for role, count in role_counts.head(10).items():
        print(f"   • {role}: {count:,} interactions")
    
    print(f"\n👥 User Archetype Distribution:")
    archetype_counts = df['user_archetype'].value_counts()
    for archetype, count in archetype_counts.items():
        print(f"   • {archetype}: {count:,} interactions")
    
    print(f"\n📅 Date Range:")
    print(f"   From: {df['block_timestamp'].min()}")
    print(f"   To: {df['block_timestamp'].max()}")
    
    print(f"\n🔍 Sample Data (first 3 rows):")
    sample_cols = ['transaction_hash', 'from_address', 'to_address', 'protocol_category', 'contract_role']
    for idx, row in df[sample_cols].head(3).iterrows():
        print(f"   Row {idx + 1}:")
        for col in sample_cols:
            value = str(row[col])
            if col in ['transaction_hash', 'from_address', 'to_address']:
                value = value[:10] + "..." if len(value) > 10 else value
            print(f"     {col}: {value}")
        print()
    
    print("✅ Verification completed successfully!")

if __name__ == "__main__":
    main() 