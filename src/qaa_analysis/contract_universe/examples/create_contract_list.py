#!/usr/bin/env python3

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Create High-Impact DeFi Contract List                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Create Contract List Example
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/examples/create_contract_list.py
---
Simple example showing how to create a high-impact DeFi contract list that defines 90% 
of volume for the largest DeFi apps and saves it to the output folder.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Create high-impact contract list"""
    
    print("# ┌────────────────────────────────────────────────────────────────────────────────────┐")
    print("# │ Create High-Impact DeFi Contract List                                             │")
    print("# └────────────────────────────────────────────────────────────────────────────────────┘")
    print()
    
    # Check for RPC URL
    rpc_url = os.getenv("ETH_RPC_URL")
    if not rpc_url or "YOUR_KEY" in rpc_url:
        print("⚠️  **RPC URL Required**")
        print()
        print("Please set your Ethereum RPC URL as an environment variable:")
        print("```bash")
        print("export ETH_RPC_URL='https://mainnet.infura.io/v3/your_actual_key'")
        print("```")
        print()
        print("**RPC Providers:**")
        print("- Infura: https://infura.io/")
        print("- Alchemy: https://alchemy.com/")
        print("- QuickNode: https://quicknode.com/")
        print()
        print("**For testing with mock data, you can run:**")
        demo_with_mock_data()
        return
    
    print(f"🔗 **Using RPC:** {rpc_url[:50]}...")
    print()
    
    try:
        # Import after path setup
        from qaa_analysis.contract_universe import create_high_impact_contract_list
        
        print("🚀 **Creating high-impact contract list...**")
        print("This will discover contracts representing 90% of DeFi trading volume.")
        print()
        
        # Create the contract list
        contract_list_path = create_high_impact_contract_list(
            eth_rpc_url=rpc_url,
            target_coverage=0.90  # 90% volume coverage
        )
        
        print()
        print("✅ **Contract list creation completed!**")
        print(f"📁 **Contract list saved to:** {contract_list_path}")
        print()
        
        # Show what was created
        output_dir = Path(contract_list_path).parent
        files = list(output_dir.glob("*"))
        print("📂 **Files created:**")
        for file_path in sorted(files):
            size_kb = file_path.stat().st_size // 1024
            print(f"   - {file_path.name} ({size_kb:,} KB)")
        print()
        
        # Show sample of the contract list
        show_sample_contracts(contract_list_path)
        
    except Exception as e:
        print(f"❌ **Error:** {e}")
        print()
        print("**Common issues:**")
        print("- Invalid or expired RPC URL")
        print("- Network connectivity problems")
        print("- Missing dependencies")
        print()
        print("**For testing purposes, you can run with mock data:**")
        demo_with_mock_data()


def demo_with_mock_data():
    """Demo the contract list structure using mock data"""
    print("🧪 **Mock Data Demo**")
    print()
    
    try:
        from qaa_analysis.contract_universe import (
            PoolVolumeData,
            get_all_tracked_protocols,
            ActionMappingPresets
        )
        
        # Show available protocols
        protocols = get_all_tracked_protocols()
        print(f"**Available Protocols:** {len(protocols)} protocols")
        for i, protocol in enumerate(protocols[:8]):
            print(f"   {i+1}. {protocol}")
        if len(protocols) > 8:
            print(f"   ... and {len(protocols) - 8} more")
        print()
        
        # Show core base contracts
        dex_contracts = ActionMappingPresets.get_major_dex_contracts()
        print(f"**Core DEX Contracts:** {len(dex_contracts)} contracts")
        for contract in dex_contracts[:3]:
            print(f"   - {contract.name} ({contract.protocol})")
            print(f"     {contract.address}")
        print()
        
        # Show sample pool data structure
        print("**Sample Contract Entry:**")
        sample_pool = PoolVolumeData(
            address="0xA0b86a33E6441e8e421d60e8d7E0A79ece1b7cF2",
            protocol="Uniswap V2",
            category="DEX Pool",
            volume_180d=2500000000.0,  # $2.5B
            tvl_current=45000000.0,    # $45M
            token0_address="0xA0b86a33E6441e8e421d60e8d7E0A79ece1b7cF2",
            token1_address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            token0_symbol="USDC",
            token1_symbol="WETH",
            creation_block=12345678,
            volume_24h=15000000.0,     # $15M
            volume_7d=95000000.0       # $95M
        )
        
        entry = sample_pool.to_contract_entry()
        print("```json")
        print("{")
        print(f'  "address": "{entry["address"]}",')
        print(f'  "protocol": "{entry["protocol"]}",')
        print(f'  "token_pair": "{entry["token_pair"]}",')
        print(f'  "volume_180d_usd": {entry["volume_180d_usd"]:,.0f},')
        print(f'  "tvl_current_usd": {entry["tvl_current_usd"]:,.0f},')
        print(f'  "volume_24h_usd": {entry["volume_24h_usd"]:,.0f}')
        print("}")
        print("```")
        print()
        
    except Exception as e:
        print(f"⚠️  Demo error: {e}")


def show_sample_contracts(contract_list_path: str):
    """Show a sample of the created contracts"""
    try:
        import json
        
        with open(contract_list_path, 'r') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        contracts = data.get('contracts', [])
        
        print("📊 **Discovery Summary:**")
        print(f"   - Target Coverage: {metadata.get('target_coverage', 0)*100:.0f}%")
        print(f"   - Actual Coverage: {metadata.get('actual_coverage', 0)*100:.1f}%")
        print(f"   - Total Contracts: {metadata.get('total_contracts_discovered', 0):,}")
        print(f"   - Protocols: {', '.join(metadata.get('protocols_included', [])[:4])}...")
        print()
        
        print("🏆 **Top 5 Highest Volume Contracts:**")
        top_contracts = sorted(contracts, key=lambda x: x.get('volume_180d_usd', 0), reverse=True)[:5]
        
        for i, contract in enumerate(top_contracts, 1):
            volume = contract.get('volume_180d_usd', 0)
            pair = contract.get('token_pair', 'Unknown')
            protocol = contract.get('protocol', 'Unknown')
            print(f"   {i}. {pair} ({protocol}) - ${volume:,.0f}")
        print()
        
    except Exception as e:
        print(f"⚠️  Could not read contract list: {e}")


if __name__ == "__main__":
    main() 