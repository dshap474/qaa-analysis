# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Phase 2 Demo: Volume-Filtered Contract Discovery                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Phase 2 Demo: Volume-Filtered Contract Discovery
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/examples/phase2_demo.py
---
Demonstrates the Phase 2 volume-filtered discovery system that focuses on 
high-impact pools accounting for 90% of total volume rather than all contracts.
"""

import os
import sys
import logging
import time
import json
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..config import EthereumConfig, DEFAULT_FACTORY_CONFIGS
from ..eth_client import EthereumClient
from ..volume_discovery import (
    VolumeFilteredDiscovery, 
    PoolVolumeData, 
    VolumeDataProvider,
    FactoryDiscovery,
    VolumeCoverageCalculator,
    quick_volume_discovery
)


def setup_logging():
    """Configure logging for demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('phase2_demo.log')
        ]
    )

def print_banner(title: str, char: str = "=", width: int = 80):
    """Print a formatted banner"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")

def print_section(title: str, char: str = "-", width: int = 60):
    """Print a formatted section header"""
    print(f"\n{char * width}")
    print(f" {title}")
    print(f"{char * width}")

def demo_volume_filtered_discovery():
    """Main demonstration of volume-filtered discovery"""
    
    print_banner("Phase 2: Volume-Filtered Contract Discovery Demo")
    
    # Setup
    print_section("1. Setup & Configuration")
    
    rpc_url = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/demo")
    target_coverage = 0.90
    
    print(f"RPC URL: {rpc_url}")
    print(f"Target Volume Coverage: {target_coverage * 100}%")
    print(f"Factory Configs: {len(DEFAULT_FACTORY_CONFIGS)} protocols")
    
    for config in DEFAULT_FACTORY_CONFIGS:
        print(f"  - {config.protocol}: {config.factory_address}")
    
    # Initialize components
    print_section("2. Component Initialization")
    
    try:
        eth_config = EthereumConfig(rpc_url=rpc_url, chunk_size=2000)
        client = EthereumClient(eth_config)
        print("✅ Ethereum client initialized")
        
        discovery = VolumeFilteredDiscovery(
            eth_client=client,
            target_coverage=target_coverage,
            max_workers=4
        )
        print("✅ Volume-filtered discovery initialized")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n💡 Note: Using mock data for demonstration (RPC connection failed)")
        
        # Use mock client for demo
        from unittest.mock import Mock
        client = Mock()
        client.to_checksum_address = lambda x: x
        client.get_current_block = lambda: 19000000
        client.get_logs_with_retry = lambda x: []
        
        discovery = VolumeFilteredDiscovery(
            eth_client=client,
            target_coverage=target_coverage
        )
        print("✅ Mock discovery initialized for demo")
    
    # Step-by-step discovery process
    print_section("3. Discovery Process")
    
    start_time = time.time()
    
    try:
        # Step 1: Pool address discovery
        print("\n🔍 Step 1: Discovering pool addresses from factories...")
        step_start = time.time()
        
        all_pools = discovery.factory_discovery.discover_pool_addresses()
        
        step_time = time.time() - step_start
        print(f"   Found {len(all_pools):,} pools in {step_time:.1f}s")
        
        # Show sample pools by protocol
        protocols = {}
        for pool in all_pools:
            protocol = pool['protocol']
            if protocol not in protocols:
                protocols[protocol] = []
            protocols[protocol].append(pool)
        
        for protocol, pools in protocols.items():
            print(f"   - {protocol}: {len(pools):,} pools")
            if pools:
                print(f"     Example: {pools[0]['address']}")
        
        # Step 2: Volume data enrichment
        print("\n📊 Step 2: Enriching with volume data...")
        step_start = time.time()
        
        # For demo, limit to a subset for faster processing
        sample_pools = all_pools[:50] if len(all_pools) > 50 else all_pools
        pools_with_volume = discovery.enrich_with_volume_data(sample_pools)
        
        step_time = time.time() - step_start
        print(f"   Enriched {len(pools_with_volume):,} pools in {step_time:.1f}s")
        
        # Show volume statistics
        if pools_with_volume:
            volumes = [p.volume_180d for p in pools_with_volume]
            total_volume = sum(volumes)
            max_volume = max(volumes)
            min_volume = min(volumes)
            avg_volume = total_volume / len(volumes)
            
            print(f"   Total 180-day volume: ${total_volume:,.0f}")
            print(f"   Average pool volume: ${avg_volume:,.0f}")
            print(f"   Highest pool volume: ${max_volume:,.0f}")
            print(f"   Lowest pool volume: ${min_volume:,.0f}")
        
        # Step 3: Coverage calculation
        print("\n🎯 Step 3: Calculating volume coverage threshold...")
        step_start = time.time()
        
        coverage_result = discovery.coverage_calculator.calculate_coverage_threshold(pools_with_volume)
        
        step_time = time.time() - step_start
        print(f"   Coverage calculation completed in {step_time:.1f}s")
        
        print(f"   Pools needed for {target_coverage*100}% coverage: {coverage_result.pools_needed:,}")
        print(f"   Volume threshold: ${coverage_result.volume_threshold:,.0f}")
        print(f"   Actual coverage achieved: {coverage_result.actual_coverage*100:.2f}%")
        print(f"   Coverage volume: ${coverage_result.coverage_volume:,.0f}")
        
        # Step 4: Apply filter
        print("\n✂️  Step 4: Applying volume filter...")
        
        filtered_pools = pools_with_volume[:coverage_result.pools_needed]
        excluded_pools = len(pools_with_volume) - coverage_result.pools_needed
        
        print(f"   High-impact pools: {len(filtered_pools):,}")
        print(f"   Excluded low-volume pools: {excluded_pools:,}")
        print(f"   Efficiency gain: {(excluded_pools / len(pools_with_volume) * 100):.1f}% reduction")
        
        total_time = time.time() - start_time
        print(f"\n🏁 Total discovery time: {total_time:.1f}s")
        
        # Results analysis
        print_section("4. Results Analysis")
        
        print("Top 10 pools by 180-day volume:")
        for i, pool in enumerate(filtered_pools[:10]):
            print(f"{i+1:2d}. {pool.token0_symbol}/{pool.token1_symbol} "
                  f"({pool.protocol}) - ${pool.volume_180d:,.0f}")
        
        # Protocol breakdown
        print("\nProtocol breakdown of high-impact pools:")
        protocol_stats = {}
        for pool in filtered_pools:
            protocol = pool.protocol
            if protocol not in protocol_stats:
                protocol_stats[protocol] = {"count": 0, "volume": 0}
            protocol_stats[protocol]["count"] += 1
            protocol_stats[protocol]["volume"] += pool.volume_180d
        
        for protocol, stats in sorted(protocol_stats.items(), key=lambda x: x[1]["volume"], reverse=True):
            print(f"  {protocol}: {stats['count']:,} pools, ${stats['volume']:,.0f} volume")
        
        # TVL analysis
        print("\nTVL analysis:")
        total_tvl = sum(p.tvl_current for p in filtered_pools)
        avg_tvl = total_tvl / len(filtered_pools) if filtered_pools else 0
        print(f"  Total TVL in high-impact pools: ${total_tvl:,.0f}")
        print(f"  Average TVL per pool: ${avg_tvl:,.0f}")
        
        # Save results
        print_section("5. Saving Results")
        
        output_data = {
            "discovery_metadata": {
                "timestamp": time.time(),
                "target_coverage": target_coverage,
                "total_discovery_time": total_time,
                "protocols_scanned": len(DEFAULT_FACTORY_CONFIGS)
            },
            "coverage_results": {
                "pools_needed": coverage_result.pools_needed,
                "volume_threshold": coverage_result.volume_threshold,
                "actual_coverage": coverage_result.actual_coverage,
                "total_volume_180d": coverage_result.total_volume_180d
            },
            "high_impact_pools": [pool.to_dict() for pool in filtered_pools]
        }
        
        with open("phase2_discovery_results.json", "w") as f:
            json.dump(output_data, f, indent=2)
        
        print("✅ Results saved to 'phase2_discovery_results.json'")
        print(f"   File contains {len(filtered_pools)} high-impact pool records")
        
        return filtered_pools
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        logging.exception("Discovery process failed")
        return []

def demo_output_generation():
    """Demo contract list output generation"""
    print_section("Contract List Output Generation")
    
    print("📁 **Output Generation Features:**")
    print("- Saves high-impact contracts to data/contract_universe/")
    print("- Multiple formats: JSON (with metadata) and CSV")
    print("- Timestamped files + latest versions")
    print("- Discovery summaries with statistics")
    print()
    
    print("**Example Output Structure:**")
    print("```")
    print("data/contract_universe/")
    print("├── high_impact_contracts_20241201_143022.json")
    print("├── high_impact_contracts_20241201_143022.csv") 
    print("├── high_impact_contracts_latest.json")
    print("├── high_impact_contracts_latest.csv")
    print("├── discovery_summary_20241201_143022.json")
    print("└── discovery_summary_latest.json")
    print("```")
    print()
    
    print("**JSON Output Format:**")
    print("```json")
    print("{")
    print('  "metadata": {')
    print('    "discovery_timestamp": "2024-12-01T14:30:22Z",')
    print('    "target_coverage": 0.90,')
    print('    "actual_coverage": 0.912,') 
    print('    "total_contracts_discovered": 423,')
    print('    "protocols_included": ["Uniswap V2", "Uniswap V3", "Curve", "Aave"],')
    print('    "description": "High-impact DeFi contracts representing 91.2% of 180-day trading volume"')
    print('  },')
    print('  "contracts": [')
    print('    {')
    print('      "address": "0x...",')
    print('      "protocol": "Uniswap V2",')
    print('      "token_pair": "USDC/WETH",')
    print('      "volume_180d_usd": 2500000000,')
    print('      "tvl_current_usd": 45000000')
    print('    }')
    print('  ]')
    print('}')
    print("```")
    print()


def demo_action_mapping_configuration():
    """Demo the action mapping and base contract configuration"""
    print_section("Core Base Contracts for User Action Tracking")
    
    try:
        from qaa_analysis.contract_universe import (
            create_action_mapper,
            ActionMappingPresets,
            get_all_tracked_protocols,
            print_available_protocols
        )
        
        print("🎯 **Core Base Contracts Overview:**")
        print("These are the main contracts users interact with directly.")
        print("Phase 3 will decode transactions to these contracts for behavioral analysis.")
        print()
        
        # Show available protocols
        protocols = get_all_tracked_protocols()
        print(f"**Tracked Protocols:** {', '.join(protocols[:8])}...")
        print()
        
        print("**Category Examples:**")
        
        # DEX example
        dex_contracts = ActionMappingPresets.get_major_dex_contracts()
        print(f"📊 **DEXs:** {len(dex_contracts)} contracts")
        for contract in dex_contracts[:2]:
            print(f"   - {contract.name} ({contract.protocol})")
            print(f"     Address: {contract.address}")
            print(f"     Functions: {', '.join(contract.primary_functions[:3])}...")
        print()
        
        # Lending example  
        lending_contracts = ActionMappingPresets.get_major_lending_contracts()
        print(f"🏦 **Lending:** {len(lending_contracts)} contracts")
        for contract in lending_contracts[:2]:
            print(f"   - {contract.name} ({contract.protocol})")
            print(f"     Address: {contract.address}")
            print(f"     Functions: {', '.join(contract.primary_functions[:3])}...")
        print()
        
        print("**Usage Example:**")
        print("```python")
        print("# Create action mapper for DEXs only")
        print("mapper = create_action_mapper(categories=['DEX'])")
        print()
        print("# Check if address is tracked")
        print("uniswap_router = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'")
        print("is_tracked = mapper.is_tracked_contract(uniswap_router)")
        print("functions = mapper.get_contract_functions(uniswap_router)")
        print("```")
        print()
        
        # Create a sample mapper
        mapper = create_action_mapper(categories=['DEX'])
        uniswap_router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        
        print("**Live Example:**")
        print(f"✅ Uniswap V2 Router tracked: {mapper.is_tracked_contract(uniswap_router)}")
        functions = mapper.get_contract_functions(uniswap_router)
        print(f"📋 Functions to track: {', '.join(functions[:4])}...")
        print(f"🏷️  Total DEX contracts: {len(mapper.get_all_tracked_addresses())}")
        
    except Exception as e:
        print(f"⚠️  Action mapping demo requires implementation: {e}")
        print("This will be available when action_mapping.py is fully integrated.")


def demo_custom_protocol_selection():
    """Demo how to select specific protocols and apps for tracking"""
    print_section("Custom Protocol Selection")
    
    print("🎛️  **You can easily configure which DeFi apps to track:**")
    print()
    
    print("**Option 1: By Protocol Name**")
    print("```python")
    print("# Track only Uniswap and Aave")
    print("protocols = ['Uniswap V2', 'Uniswap V3', 'Aave V2', 'Aave V3']")
    print("pools = quick_volume_discovery(rpc_url, protocols=protocols)")
    print("```")
    print()
    
    print("**Option 2: By Category**")
    print("```python")
    print("# Track only DEXs")
    print("factory_configs = get_factory_configs_by_category(['DEX Pool'])")
    print()
    print("# Track only lending protocols") 
    print("factory_configs = get_factory_configs_by_category(['Lending Market'])")
    print("```")
    print()
    
    print("**Option 3: Preset Configurations**")
    print("```python")
    print("# Major DeFi protocols (recommended)")
    print("protocols = [")
    print("    'Uniswap V2', 'Uniswap V3', 'SushiSwap',")
    print("    'Curve CryptoSwap', 'Aave V2', 'Aave V3',")
    print("    'Lido', 'Rocket Pool'")
    print("]")
    print()
    print("# Use the convenience function")
    print("contract_list = create_high_impact_contract_list(")
    print("    eth_rpc_url='https://mainnet.infura.io/v3/YOUR_KEY',")
    print("    protocols=protocols")
    print(")")
    print("```")
    print()
    
    print("**Available Categories:**")
    try:
        from qaa_analysis.contract_universe import get_all_tracked_categories
        categories = get_all_tracked_categories()
        for category in categories:
            print(f"   - {category}")
    except:
        print("   - DEX Pool")
        print("   - Lending Market")
        print("   - Liquid Staking")
        print("   - Yield Vault")
        print("   - NFT Marketplace")
    print()


def demo_complete_workflow():
    """Demo the complete workflow for creating contract lists"""
    print_section("Complete Workflow Example")
    
    print("🔄 **End-to-End Contract Discovery Workflow:**")
    print()
    
    print("**Step 1: Simple Contract List Generation**")
    print("```python")
    print("from qaa_analysis.contract_universe import create_high_impact_contract_list")
    print()
    print("# Create comprehensive contract list")
    print("contract_list_path = create_high_impact_contract_list(")
    print("    eth_rpc_url='https://mainnet.infura.io/v3/YOUR_KEY'")
    print(")")
    print()
    print("print(f'Contract list saved to: {contract_list_path}')")
    print("```")
    print()
    
    print("**Step 2: Custom Configuration**")
    print("```python")
    print("# Focus on major DEXs and lending protocols")
    print("major_defi_protocols = [")
    print("    'Uniswap V2', 'Uniswap V3', 'SushiSwap',")
    print("    'Aave V2', 'Aave V3', 'Compound V3'")
    print("]")
    print()
    print("contract_list_path = create_high_impact_contract_list(")
    print("    eth_rpc_url='https://mainnet.infura.io/v3/YOUR_KEY',")
    print("    protocols=major_defi_protocols,")
    print("    target_coverage=0.95,  # 95% coverage")
    print("    output_dir='./custom_output'")
    print(")")
    print("```")
    print()
    
    print("**Expected Results:**")
    print("- 📊 ~400-800 high-impact contracts (vs 250k+ total)")
    print("- 🎯 90-95% of total trading volume coverage")
    print("- ⚡ ~30 minutes processing (vs 8+ hours for full discovery)")
    print("- 📁 Clean JSON/CSV output ready for analysis")
    print("- 📈 Protocol breakdown and statistics")
    print()
    
    print("**Output Files Generated:**")
    print("1. `high_impact_contracts_latest.json` - Main contract list")
    print("2. `high_impact_contracts_latest.csv` - Spreadsheet format")
    print("3. `discovery_summary_latest.json` - Statistics and metrics")
    print("4. Timestamped versions for historical tracking")
    print()


def main():
    """Run the enhanced Phase 2 demo"""
    print_banner("Phase 2: Volume-Filtered Discovery + Action Mapping Foundation")
    
    print("🎉 **Phase 2 Enhanced Features:**")
    print("- ✅ Volume-filtered contract discovery (90% coverage strategy)")
    print("- ✅ Multi-format output generation (JSON + CSV)")
    print("- ✅ Core base contracts for user action tracking")  
    print("- ✅ Configurable protocol and category filtering")
    print("- ✅ Automatic output to data/contract_universe/")
    print("- ✅ Foundation for Phase 3 behavioral analysis")
    print()
    
    demos = [
        demo_volume_filtered_discovery,
        demo_output_generation,
        demo_action_mapping_configuration,
        demo_custom_protocol_selection,
        demo_complete_workflow
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  Demo error: {e}")
        print()
    
    print_banner("Phase 2 Demo Complete", char="=")
    print()
    print("🚀 **Ready for Phase 3: Complete Action Mapping System**")
    print("   - Transaction decoding and event parsing")
    print("   - User action identification and mapping")
    print("   - Real-time behavioral analysis pipeline")
    print()
    print("📂 **Your contract lists will be saved to:** `data/contract_universe/`")
    print("🔧 **To get started:** Set your ETH_RPC_URL and run create_high_impact_contract_list()")
    print()

if __name__ == "__main__":
    main() 