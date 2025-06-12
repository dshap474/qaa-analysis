# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Ethereum Contract Universe Discovery & Behavioral Analysis Implementation Guide    │
# └────────────────────────────────────────────────────────────────────────────────────┘

**Practical Implementation Guide for Automated Discovery of High-Volume Ethereum DeFi Contracts and User Action Mapping for Behavioral Analysis**

---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/docs/Implementation-Guide.md
---
Step-by-step implementation guide with code examples for building an automated system 
to discover the most active DEX pools, lending markets, and NFT marketplace contracts 
using 180-day volume coverage, then map user actions for behavioral analysis.

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Phase 1: Infrastructure Setup](#phase-1-infrastructure-setup)
3. [Phase 2: Volume-Filtered Contract Discovery](#phase-2-volume-filtered-contract-discovery)
4. [Phase 3: Action Mapping System](#phase-3-action-mapping-system)
5. [Phase 4: Behavioral Analysis Engine](#phase-4-behavioral-analysis-engine)
6. [Phase 5: Data Storage & Indexing](#phase-5-data-storage-indexing)

## System Architecture Overview

```mermaid
graph TD
    A[Factory Discovery] --> B[Volume Data Enrichment]
    B --> C[180-Day Coverage Filter]
    C --> D[High-Volume Contract Universe]
    D --> E[Action Mapping]
    E --> F[Behavioral Analysis]
    F --> G[User Profiles & Insights]
```

**Key Design Principle**: Focus on the ~400-800 pools that account for 90% of 180-day trailing volume, rather than all 300k+ contracts. This provides maximum analytical value with minimal computational overhead.

```
  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
  │   Factory       │───▶│   Volume        │───▶│   Transaction   │
  │   Discovery     │    │   Filtering     │    │   Decoder       │
  └─────────────────┘    └─────────────────┘    └─────────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
  │ All Pool        │    │ High-Volume     │    │ User Action     │
  │ Addresses       │    │ Pool Universe   │    │ Mapping         │
  │ (300k+)         │    │ (~400-800)      │    │                 │
  └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Phase 1: Infrastructure Setup

### 1.1 Environment Configuration

```python
# config.py
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class EthereumConfig:
    """Configuration for Ethereum node connection and analysis parameters"""
    rpc_url: str
    archive_node_url: Optional[str] = None
    chunk_size: int = 5000  # Blocks to process in each batch
    max_retries: int = 3
    request_timeout: int = 30

@dataclass
class FactoryConfig:
    """Configuration for factory contract discovery"""
    protocol: str
    factory_address: str
    event_topic: str
    child_slot_index: int
    creation_block: int
    category: str

# Load configuration from environment
ETH_CONFIG = EthereumConfig(
    rpc_url=os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY"),
    archive_node_url=os.getenv("ETH_ARCHIVE_URL"),
    chunk_size=int(os.getenv("CHUNK_SIZE", "5000"))
)

# Core factory configurations
FACTORY_CONFIGS = [
    FactoryConfig(
        protocol="Uniswap V2",
        factory_address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        event_topic="0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9",
        child_slot_index=2,
        creation_block=10000835,
        category="DEX Pool"
    ),
    FactoryConfig(
        protocol="Uniswap V3",
        factory_address="0x1F98431c8aD98523631AE4a59f267346ea31F984",
        event_topic="0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118",
        child_slot_index=4,
        creation_block=12369621,
        category="DEX Pool"
    ),
    FactoryConfig(
        protocol="Curve CryptoSwap",
        factory_address="0xf18056bbd320e96a48e3fbf8bc061322531aac99",
        event_topic="0x062384933E4AA575767D87DAd5f6F3529C070D3A4579C8D9AA80916852577E09",
        child_slot_index=0,
        creation_block=14725543,
        category="DEX Pool"
    )
]
```

### 1.2 Core Dependencies Setup

```python
# requirements.txt content for your project
"""
web3>=6.0.0
eth-abi>=4.0.0
requests>=2.28.0
pandas>=1.5.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
click>=8.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
"""

# eth_client.py
from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import List, Dict, Any, Optional
import time
import logging

class EthereumClient:
    """Enhanced Ethereum client with retry logic and error handling"""
    
    def __init__(self, config: EthereumConfig):
        self.config = config
        self.w3 = Web3(Web3.HTTPProvider(
            config.rpc_url,
            request_kwargs={'timeout': config.request_timeout}
        ))
        
        # Add PoA middleware if needed (for some networks)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum node")
        
        self.logger = logging.getLogger(__name__)
    
    def get_logs_with_retry(self, filter_params: Dict[str, Any]) -> List[Dict]:
        """Get logs with exponential backoff retry logic"""
        for attempt in range(self.config.max_retries):
            try:
                logs = self.w3.eth.get_logs(filter_params)
                return logs
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"Failed to get logs after {self.config.max_retries} attempts: {e}")
                    raise
                
                wait_time = 2 ** attempt
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return []
    
    def get_current_block(self) -> int:
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_block_timestamp(self, block_number: int) -> int:
        """Get timestamp for a specific block"""
        block = self.w3.eth.get_block(block_number)
        return block['timestamp']
```

## Phase 2: Volume-Filtered Contract Discovery

### 2.1 Volume-Filtered Discovery Architecture

```python
# volume_filtered_discovery.py
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests
import time
from datetime import datetime, timedelta

@dataclass
class PoolVolumeData:
    """Pool with volume metrics for filtering"""
    address: str
    protocol: str
    category: str
    volume_180d: float
    tvl_current: float
    token0_address: str
    token1_address: str
    token0_symbol: str
    token1_symbol: str
    creation_block: int

class VolumeFilteredDiscovery:
    """Discover contracts filtered by 180-day volume coverage"""
    
    def __init__(self, eth_client, volume_coverage: float = 0.90):
        self.client = eth_client
        self.target_coverage = volume_coverage
        self.volume_period_days = 180
        self.logger = logging.getLogger(__name__)
    
    def discover_with_volume_filter(self) -> List[PoolVolumeData]:
        """Main discovery pipeline with volume filtering"""
        
        self.logger.info(f"Starting volume-filtered discovery (target: {self.target_coverage*100}% coverage)")
        
        # Step 1: Quick address discovery from factories
        self.logger.info("Step 1: Discovering pool addresses from factories...")
        all_pools = self.discover_pool_addresses()
        self.logger.info(f"Found {len(all_pools)} total pools across all protocols")
        
        # Step 2: Enrich with 180-day volume data
        self.logger.info("Step 2: Enriching with 180-day volume data...")
        pools_with_volume = self.enrich_with_volume_data(all_pools)
        self.logger.info(f"Successfully enriched {len(pools_with_volume)} pools with volume data")
        
        # Step 3: Calculate volume coverage threshold
        self.logger.info("Step 3: Calculating volume coverage threshold...")
        coverage_result = self.calculate_coverage_threshold(pools_with_volume)
        
        self.logger.info(f"Volume threshold for {self.target_coverage*100}% coverage: ${coverage_result['volume_threshold']:,.2f}")
        self.logger.info(f"Pools needed: {coverage_result['pools_needed']}")
        self.logger.info(f"Actual coverage: {coverage_result['actual_coverage']*100:.2f}%")
        
        # Step 4: Filter pools by volume coverage
        filtered_pools = pools_with_volume[:coverage_result['pools_needed']]
        
        self.logger.info(f"Final filtered universe: {len(filtered_pools)} pools")
        return filtered_pools
```

### 2.2 Factory Address Discovery (Lightweight)

```python
def discover_pool_addresses(self) -> List[Dict]:
    """Efficiently discover pool addresses from factory contracts"""
    
    all_pools = []
    
    for factory_config in self.factory_configs:
        self.logger.info(f"Discovering pools from {factory_config.protocol}...")
        
        try:
            # Method 1: Factory read functions (fastest for historical)
            if factory_config.protocol in ["Uniswap V2", "SushiSwap"]:
                pools = self._discover_via_read_functions(factory_config)
            
            # Method 2: Recent event logs (for newer pools)
            else:
                pools = self._discover_via_recent_events(factory_config)
            
            all_pools.extend(pools)
            self.logger.info(f"Found {len(pools)} pools from {factory_config.protocol}")
            
        except Exception as e:
            self.logger.error(f"Failed to discover pools from {factory_config.protocol}: {e}")
            continue
    
    return all_pools

def _discover_via_read_functions(self, factory_config) -> List[Dict]:
    """Use factory enumeration functions for bulk discovery"""
    
    factory_address = self.client.to_checksum_address(factory_config.factory_address)
    
    # Get factory contract (simplified ABI)
    factory_abi = [
        {"name": "allPairsLength", "type": "function", "stateMutability": "view", 
         "inputs": [], "outputs": [{"type": "uint256"}]},
        {"name": "allPairs", "type": "function", "stateMutability": "view",
         "inputs": [{"type": "uint256"}], "outputs": [{"type": "address"}]}
    ]
    
    factory_contract = self.client.w3.eth.contract(
        address=factory_address, 
        abi=factory_abi
    )
    
    # Get total number of pairs
    total_pairs = factory_contract.functions.allPairsLength().call()
    self.logger.info(f"Total pairs in {factory_config.protocol}: {total_pairs:,}")
    
    # Get all pair addresses (batched)
    pools = []
    batch_size = 100
    
    for start_idx in range(0, total_pairs, batch_size):
        end_idx = min(start_idx + batch_size, total_pairs)
        
        # Batch contract calls for efficiency
        for i in range(start_idx, end_idx):
            try:
                pair_address = factory_contract.functions.allPairs(i).call()
                pools.append({
                    "address": pair_address,
                    "protocol": factory_config.protocol,
                    "category": factory_config.category,
                    "creation_block": factory_config.creation_block + i  # Approximate
                })
            except Exception as e:
                self.logger.warning(f"Failed to get pair {i}: {e}")
                continue
        
        # Rate limiting
        time.sleep(0.1)
    
    return pools
```

### 2.3 Volume Data Enrichment

```python
def enrich_with_volume_data(self, pools: List[Dict]) -> List[PoolVolumeData]:
    """Enrich pools with 180-day volume data from multiple sources"""
    
    enriched_pools = []
    
    # Process in batches to respect API rate limits
    batch_size = 50
    for i in range(0, len(pools), batch_size):
        batch = pools[i:i + batch_size]
        
        self.logger.info(f"Processing volume data batch {i//batch_size + 1}/{len(pools)//batch_size + 1}")
        
        for pool in batch:
            try:
                volume_data = self._get_pool_volume_data(pool)
                if volume_data:
                    enriched_pools.append(volume_data)
            except Exception as e:
                self.logger.warning(f"Failed to get volume data for {pool['address']}: {e}")
                continue
        
        # Rate limiting between batches
        time.sleep(1)
    
    # Sort by 180-day volume (descending)
    enriched_pools.sort(key=lambda x: x.volume_180d, reverse=True)
    
    return enriched_pools

def _get_pool_volume_data(self, pool: Dict) -> Optional[PoolVolumeData]:
    """Get 180-day volume data for a specific pool"""
    
    # Try multiple data sources in order of preference
    volume_data = None
    
    # Source 1: The Graph Protocol (most reliable)
    try:
        volume_data = self._get_volume_from_graph(pool)
    except Exception as e:
        self.logger.debug(f"Graph query failed for {pool['address']}: {e}")
    
    # Source 2: DeFiLlama API (backup)
    if not volume_data:
        try:
            volume_data = self._get_volume_from_defillama(pool)
        except Exception as e:
            self.logger.debug(f"DeFiLlama query failed for {pool['address']}: {e}")
    
    # Source 3: DEX Screener (validation)
    if not volume_data:
        try:
            volume_data = self._get_volume_from_dexscreener(pool)
        except Exception as e:
            self.logger.debug(f"DEX Screener query failed for {pool['address']}: {e}")
    
    return volume_data

def _get_volume_from_graph(self, pool: Dict) -> Optional[PoolVolumeData]:
    """Get volume data from The Graph Protocol"""
    
    # Protocol-specific subgraph endpoints
    subgraph_urls = {
        "Uniswap V2": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
        "Uniswap V3": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
        "SushiSwap": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"
    }
    
    subgraph_url = subgraph_urls.get(pool['protocol'])
    if not subgraph_url:
        return None
    
    # Query for 180-day volume data
    query = f"""
    {{
      pair(id: "{pool['address'].lower()}") {{
        id
        volumeUSD
        reserveUSD
        token0 {{
          id
          symbol
          decimals
        }}
        token1 {{
          id
          symbol
          decimals
        }}
        dayData(
          first: 180
          orderBy: date
          orderDirection: desc
        ) {{
          date
          dailyVolumeUSD
        }}
      }}
    }}
    """
    
    response = requests.post(subgraph_url, json={"query": query}, timeout=10)
    data = response.json()
    
    if "errors" in data or not data.get("data", {}).get("pair"):
        return None
    
    pair_data = data["data"]["pair"]
    
    # Calculate 180-day volume
    volume_180d = sum(float(day["dailyVolumeUSD"]) for day in pair_data["dayData"])
    
    return PoolVolumeData(
        address=pool['address'],
        protocol=pool['protocol'],
        category=pool['category'],
        volume_180d=volume_180d,
        tvl_current=float(pair_data.get("reserveUSD", 0)),
        token0_address=pair_data["token0"]["id"],
        token1_address=pair_data["token1"]["id"],
        token0_symbol=pair_data["token0"]["symbol"],
        token1_symbol=pair_data["token1"]["symbol"],
        creation_block=pool.get('creation_block', 0)
    )
```

### 2.4 Volume Coverage Calculation

```python
def calculate_coverage_threshold(self, pools_with_volume: List[PoolVolumeData]) -> Dict:
    """Calculate volume threshold for target coverage"""
    
    # Sort pools by 180-day volume (descending)
    sorted_pools = sorted(pools_with_volume, key=lambda x: x.volume_180d, reverse=True)
    
    total_volume = sum(p.volume_180d for p in sorted_pools)
    target_volume = total_volume * self.target_coverage
    
    cumulative_volume = 0
    for i, pool in enumerate(sorted_pools):
        cumulative_volume += pool.volume_180d
        
        if cumulative_volume >= target_volume:
            return {
                'volume_threshold': pool.volume_180d,
                'pools_needed': i + 1,
                'actual_coverage': cumulative_volume / total_volume,
                'total_volume': total_volume,
                'coverage_volume': cumulative_volume
            }
    
    # If we need all pools to reach target coverage
    return {
        'volume_threshold': sorted_pools[-1].volume_180d if sorted_pools else 0,
        'pools_needed': len(sorted_pools),
        'actual_coverage': 1.0,
        'total_volume': total_volume,
        'coverage_volume': total_volume
    }
```

### 2.5 Expected Results

**Volume Distribution Analysis**
```python
EXPECTED_RESULTS = {
    "Total Pools Discovered": "~250,000",
    "90% Volume Coverage": "~400-800 pools",
    "Processing Time": "~30 minutes",
    "API Calls": "~500",
    "Final Dataset Size": "~200KB",
    "Update Frequency": "Weekly"
}

EXAMPLE_COVERAGE_BREAKDOWN = {
    "Uniswap V2": {
        "total_pools": 150_000,
        "90%_volume_pools": 200,
        "example_pairs": ["USDC/WETH", "WBTC/WETH", "DAI/USDC"]
    },
    "Uniswap V3": {
        "total_pools": 70_000,
        "90%_volume_pools": 100,
        "example_pairs": ["USDC/WETH 0.05%", "WBTC/WETH 0.3%"]
    },
    "Curve": {
        "total_pools": 5_000,
        "90%_volume_pools": 25,
        "example_pairs": ["3pool", "stETH/ETH", "FRAX/USDC"]
    }
}
```

## Phase 3: Action Mapping System

### 3.1 Function and Event Selector Registry

```python
# action_selectors.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from web3 import Web3

@dataclass
class ActionSignature:
    """Represents a function or event signature with its selector"""
    name: str
    signature: str
    selector: str
    protocol: str
    contract_type: str
    description: str

class SelectorRegistry:
    """Registry for function and event selectors across DeFi protocols"""
    
    def __init__(self):
        self.function_selectors: Dict[str, ActionSignature] = {}
        self.event_selectors: Dict[str, ActionSignature] = {}
        self._populate_selectors()
    
    def _populate_selectors(self):
        """Populate registry with known selectors"""
        
        # Uniswap V2 Router Functions
        self._add_function_selector(
            "swapExactTokensForTokens",
            "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
            "Uniswap V2",
            "Router",
            "Swap exact input tokens for output tokens"
        )
        
        self._add_function_selector(
            "addLiquidity",
            "addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)",
            "Uniswap V2",
            "Router",
            "Add liquidity to a V2 pair"
        )
        
        self._add_function_selector(
            "removeLiquidity",
            "removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)",
            "Uniswap V2",
            "Router",
            "Remove liquidity from a V2 pair"
        )
        
        # Uniswap V3 SwapRouter Functions
        self._add_function_selector(
            "exactInputSingle",
            "exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))",
            "Uniswap V3",
            "SwapRouter",
            "Single-hop exact input swap"
        )
        
        self._add_function_selector(
            "exactOutputSingle",
            "exactOutputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))",
            "Uniswap V3",
            "SwapRouter",
            "Single-hop exact output swap"
        )
        
        # Aave V3 Pool Functions
        self._add_function_selector(
            "supply",
            "supply(address,uint256,address,uint16)",
            "Aave V3",
            "Pool",
            "Supply assets to earn interest"
        )
        
        self._add_function_selector(
            "borrow",
            "borrow(address,uint256,uint256,uint16,address)",
            "Aave V3",
            "Pool",
            "Borrow assets against collateral"
        )
        
        self._add_function_selector(
            "repay",
            "repay(address,uint256,uint256,address)",
            "Aave V3",
            "Pool",
            "Repay borrowed assets"
        )
        
        self._add_function_selector(
            "withdraw",
            "withdraw(address,uint256,address)",
            "Aave V3",
            "Pool",
            "Withdraw supplied assets"
        )
        
        # Lido Staking Functions
        self._add_function_selector(
            "submit",
            "submit(address)",
            "Lido",
            "StakingToken",
            "Stake ETH to receive stETH"
        )
        
        # OpenSea Seaport Functions
        self._add_function_selector(
            "fulfillBasicOrder",
            "fulfillBasicOrder((address,address,address,(uint8,address,uint256,uint256,uint256),(uint8,address,uint256,uint256,uint256,address),uint8,uint256,uint256,bytes32,uint256,bytes32,uint256))",
            "OpenSea",
            "Seaport",
            "Fulfill a basic order for NFT purchase"
        )
        
        # Event Selectors
        
        # Uniswap V2 Pair Events
        self._add_event_selector(
            "Swap",
            "Swap(address,uint256,uint256,uint256,uint256,address)",
            "Uniswap V2",
            "Pair",
            "Token swap executed"
        )
        
        self._add_event_selector(
            "Mint",
            "Mint(address,uint256,uint256)",
            "Uniswap V2",
            "Pair",
            "Liquidity tokens minted"
        )
        
        self._add_event_selector(
            "Burn",
            "Burn(address,uint256,uint256,address)",
            "Uniswap V2",
            "Pair",
            "Liquidity tokens burned"
        )
        
        # Uniswap V3 Pool Events
        self._add_event_selector(
            "Swap",
            "Swap(address,address,int256,int256,uint160,uint128,int24)",
            "Uniswap V3",
            "Pool",
            "V3 swap executed"
        )
        
        # Aave V3 Pool Events
        self._add_event_selector(
            "Supply",
            "Supply(address,address,address,uint256,uint16)",
            "Aave V3",
            "Pool",
            "Assets supplied to pool"
        )
        
        self._add_event_selector(
            "Borrow",
            "Borrow(address,address,address,uint256,uint8,uint256,uint16)",
            "Aave V3",
            "Pool",
            "Assets borrowed from pool"
        )
        
        self._add_event_selector(
            "Repay",
            "Repay(address,address,address,uint256,bool)",
            "Aave V3",
            "Pool",
            "Borrowed assets repaid"
        )
        
        self._add_event_selector(
            "Withdraw",
            "Withdraw(address,address,address,uint256)",
            "Aave V3",
            "Pool",
            "Assets withdrawn from pool"
        )
        
        # ERC20 Transfer (used by many protocols)
        self._add_event_selector(
            "Transfer",
            "Transfer(address,address,uint256)",
            "ERC20",
            "Token",
            "Token transfer"
        )
        
        # OpenSea Seaport Events
        self._add_event_selector(
            "OrderFulfilled",
            "OrderFulfilled(bytes32,address,address,address,(uint8,address,uint256,uint256),(uint8,address,uint256,uint256,address))",
            "OpenSea",
            "Seaport",
            "NFT order fulfilled"
        )
    
    def _add_function_selector(self, name: str, signature: str, protocol: str, 
                             contract_type: str, description: str):
        """Add a function selector to the registry"""
        selector = Web3.keccak(text=signature)[:4].hex()
        action_sig = ActionSignature(
            name=name,
            signature=signature,
            selector=selector,
            protocol=protocol,
            contract_type=contract_type,
            description=description
        )
        self.function_selectors[selector] = action_sig
    
    def _add_event_selector(self, name: str, signature: str, protocol: str,
                           contract_type: str, description: str):
        """Add an event selector to the registry"""
        selector = Web3.keccak(text=signature).hex()
        action_sig = ActionSignature(
            name=name,
            signature=signature,
            selector=selector,
            protocol=protocol,
            contract_type=contract_type,
            description=description
        )
        self.event_selectors[selector] = action_sig
    
    def get_function_action(self, selector: str) -> Optional[ActionSignature]:
        """Get function action by selector"""
        return self.function_selectors.get(selector)
    
    def get_event_action(self, selector: str) -> Optional[ActionSignature]:
        """Get event action by selector"""
        return self.event_selectors.get(selector)
```

### 3.2 Transaction Decoder

```python
# transaction_decoder.py
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from web3.types import TxReceipt, LogReceipt

@dataclass
class DecodedAction:
    """Represents a decoded user action"""
    tx_hash: str
    block_number: int
    timestamp: int
    user_address: str
    contract_address: str
    protocol: str
    action_type: str
    function_signature: Optional[str]
    event_signature: Optional[str]
    gas_used: int
    gas_price: int
    success: bool
    metadata: Dict

class TransactionDecoder:
    """Decodes transactions to identify user actions"""
    
    def __init__(self, eth_client: EthereumClient, universe: ContractUniverse, 
                 selector_registry: SelectorRegistry):
        self.eth_client = eth_client
        self.universe = universe
        self.selector_registry = selector_registry
        self.logger = logging.getLogger(__name__)
    
    def decode_transaction(self, tx_hash: str) -> Optional[List[DecodedAction]]:
        """
        Decode a transaction to identify user actions
        
        Args:
            tx_hash: Transaction hash to decode
            
        Returns:
            List of decoded actions (can be multiple actions per transaction)
        """
        try:
            # Get transaction and receipt
            tx = self.eth_client.w3.eth.get_transaction(tx_hash)
            receipt = self.eth_client.w3.eth.get_transaction_receipt(tx_hash)
            
            # Skip if transaction failed
            if receipt.status == 0:
                return []
            
            # Check if transaction interacts with tracked contracts
            if not self.universe.is_tracked_contract(tx['to']):
                return []
            
            return self._decode_transaction_internal(tx, receipt)
            
        except Exception as e:
            self.logger.error(f"Error decoding transaction {tx_hash}: {e}")
            return []
    
    def _decode_transaction_internal(self, tx, receipt: TxReceipt) -> List[DecodedAction]:
        """Internal transaction decoding logic"""
        actions = []
        
        # Get contract info
        contract_info = self.universe.get_contract_info(tx['to'])
        
        # Decode function call (intent)
        function_selector = tx['input'][:10] if len(tx['input']) >= 10 else None
        function_action = None
        if function_selector:
            function_action = self.selector_registry.get_function_action(function_selector)
        
        # Decode events (outcome)
        event_actions = self._decode_events(receipt.logs)
        
        # Create decoded action
        if function_action or event_actions:
            # Get block timestamp
            block = self.eth_client.w3.eth.get_block(receipt.blockNumber)
            
            action = DecodedAction(
                tx_hash=tx['hash'].hex(),
                block_number=receipt.blockNumber,
                timestamp=block['timestamp'],
                user_address=tx['from'],
                contract_address=tx['to'],
                protocol=contract_info.get('protocol', 'Unknown'),
                action_type=self._determine_action_type(function_action, event_actions),
                function_signature=function_action.signature if function_action else None,
                event_signature=self._get_primary_event_signature(event_actions),
                gas_used=receipt.gasUsed,
                gas_price=tx.get('gasPrice', 0),
                success=receipt.status == 1,
                metadata=self._extract_metadata(tx, receipt, function_action, event_actions)
            )
            
            actions.append(action)
        
        return actions
    
    def _decode_events(self, logs: List[LogReceipt]) -> List[ActionSignature]:
        """Decode event logs to identify actions"""
        event_actions = []
        
        for log in logs:
            if not log['topics']:
                continue
            
            event_selector = log['topics'][0].hex()
            event_action = self.selector_registry.get_event_action(event_selector)
            
            if event_action:
                event_actions.append(event_action)
        
        return event_actions
    
    def _determine_action_type(self, function_action: Optional[ActionSignature],
                              event_actions: List[ActionSignature]) -> str:
        """Determine the primary action type"""
        # Prioritize function action if available
        if function_action:
            return function_action.name
        
        # Otherwise use the most relevant event
        if event_actions:
            # Filter out generic events like Transfer
            specific_events = [e for e in event_actions if e.name != "Transfer"]
            if specific_events:
                return specific_events[0].name
            return event_actions[0].name
        
        return "Unknown"
    
    def _get_primary_event_signature(self, event_actions: List[ActionSignature]) -> Optional[str]:
        """Get the primary event signature"""
        if not event_actions:
            return None
        
        # Filter out generic events
        specific_events = [e for e in event_actions if e.name != "Transfer"]
        if specific_events:
            return specific_events[0].signature
        
        return event_actions[0].signature
    
    def _extract_metadata(self, tx, receipt: TxReceipt, 
                         function_action: Optional[ActionSignature],
                         event_actions: List[ActionSignature]) -> Dict:
        """Extract additional metadata from transaction and events"""
        metadata = {
            "tx_value": tx.get('value', 0),
            "gas_limit": tx.get('gas', 0),
            "event_count": len(event_actions),
            "log_count": len(receipt.logs)
        }
        
        # Add protocol-specific metadata extraction here
        # This can be expanded based on specific analysis needs
        
        return metadata
```

## Phase 4: Behavioral Analysis Engine

### 4.1 User Profile Management

```python
# user_profiles.py
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

@dataclass
class UserProfile:
    """Comprehensive user profile with behavioral metrics"""
    address: str
    categories: Set[str] = field(default_factory=set)
    action_counts: Dict[str, int] = field(default_factory=dict)
    protocol_usage: Dict[str, int] = field(default_factory=dict)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    total_transactions: int = 0
    total_gas_spent: int = 0
    total_value_transacted: int = 0
    unique_contracts: Set[str] = field(default_factory=set)
    risk_score: float = 0.0
    sophistication_score: float = 0.0

class BehavioralAnalysisEngine:
    """Engine for analyzing user behavior and assigning categories"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.logger = logging.getLogger(__name__)
        
        # Behavioral thresholds (configurable)
        self.TRADER_SWAP_THRESHOLD = 10
        self.LP_THRESHOLD = 3
        self.BORROWER_THRESHOLD = 1
        self.STAKER_THRESHOLD = 1
        self.ARBITRAGEUR_PROFIT_THRESHOLD = 0.01  # 1% profit margin
        self.HIGH_VALUE_THRESHOLD = 100_000  # $100k equivalent
    
    def update_profile(self, action: DecodedAction) -> None:
        """Update user profile based on a decoded action"""
        address = action.user_address
        
        # Initialize profile if new user
        if address not in self.user_profiles:
            self.user_profiles[address] = UserProfile(address=address)
        
        profile = self.user_profiles[address]
        
        # Update basic metrics
        profile.total_transactions += 1
        profile.total_gas_spent += action.gas_used * action.gas_price
        profile.total_value_transacted += action.metadata.get('tx_value', 0)
        profile.unique_contracts.add(action.contract_address)
        
        # Update timestamps
        action_time = datetime.fromtimestamp(action.timestamp)
        if not profile.first_seen:
            profile.first_seen = action_time
        profile.last_seen = action_time
        
        # Update action counts
        profile.action_counts[action.action_type] = \
            profile.action_counts.get(action.action_type, 0) + 1
        
        # Update protocol usage
        profile.protocol_usage[action.protocol] = \
            profile.protocol_usage.get(action.protocol, 0) + 1
        
        # Apply behavioral rules
        self._apply_behavioral_rules(profile, action)
        
        # Update sophistication and risk scores
        self._update_scores(profile, action)
    
    def _apply_behavioral_rules(self, profile: UserProfile, action: DecodedAction) -> None:
        """Apply heuristic rules to assign behavioral categories"""
        
        # Trading behavior
        swap_count = profile.action_counts.get('Swap', 0)
        if swap_count >= self.TRADER_SWAP_THRESHOLD:
            profile.categories.add('Trader')
        
        # Liquidity provision
        if (profile.action_counts.get('Mint', 0) >= self.LP_THRESHOLD or
            profile.action_counts.get('addLiquidity', 0) >= self.LP_THRESHOLD):
            profile.categories.add('Liquidity_Provider')
        
        # Lending behavior
        if profile.action_counts.get('Supply', 0) >= 1:
            profile.categories.add('Lender')
        
        # Borrowing behavior
        if profile.action_counts.get('Borrow', 0) >= self.BORROWER_THRESHOLD:
            profile.categories.add('Borrower')
        
        # Staking behavior
        if profile.action_counts.get('submit', 0) >= self.STAKER_THRESHOLD:
            profile.categories.add('Staker')
        
        # NFT trading
        if profile.action_counts.get('fulfillBasicOrder', 0) >= 1:
            profile.categories.add('NFT_Trader')
        
        # High-value user
        if profile.total_value_transacted >= self.HIGH_VALUE_THRESHOLD:
            profile.categories.add('High_Value_User')
        
        # Multi-protocol user
        if len(profile.protocol_usage) >= 3:
            profile.categories.add('Multi_Protocol_User')
        
        # Active user (high transaction frequency)
        if profile.first_seen and profile.last_seen:
            days_active = (profile.last_seen - profile.first_seen).days + 1
            tx_per_day = profile.total_transactions / days_active
            if tx_per_day >= 5:
                profile.categories.add('Active_User')
        
        # Detect potential arbitrageur patterns
        self._detect_arbitrageur(profile, action)
    
    def _detect_arbitrageur(self, profile: UserProfile, action: DecodedAction) -> None:
        """Detect potential arbitrage patterns"""
        # This is a simplified heuristic - in practice, you'd want more sophisticated analysis
        
        # Check for rapid-fire transactions
        if (profile.total_transactions >= 100 and
            len(profile.unique_contracts) >= 10 and
            profile.action_counts.get('Swap', 0) >= 50):
            profile.categories.add('Potential_Arbitrageur')
        
        # Check for flash loan usage (if you track this)
        if profile.action_counts.get('FlashLoan', 0) >= 1:
            profile.categories.add('Flash_Loan_User')
            profile.categories.add('Potential_Arbitrageur')
    
    def _update_scores(self, profile: UserProfile, action: DecodedAction) -> None:
        """Update user sophistication and risk scores"""
        
        # Sophistication score (0-100)
        sophistication_factors = [
            len(profile.categories) * 5,  # Diverse behavior
            min(len(profile.protocol_usage) * 10, 30),  # Multi-protocol usage
            min(len(profile.unique_contracts) / 10 * 20, 20),  # Contract diversity
            10 if 'Flash_Loan_User' in profile.categories else 0,  # Advanced features
            15 if profile.total_transactions >= 1000 else 0  # High activity
        ]
        profile.sophistication_score = min(sum(sophistication_factors), 100)
        
        # Risk score (0-100) - higher = more risky
        risk_factors = [
            20 if 'Borrower' in profile.categories else 0,  # Leverage usage
            15 if 'Flash_Loan_User' in profile.categories else 0,  # Complex transactions
            10 if profile.total_transactions >= 1000 else 0,  # High activity
            25 if profile.total_value_transacted >= 1_000_000 else 0,  # High value
            5 * len([c for c in profile.categories if 'Potential' in c])  # Potential risks
        ]
        profile.risk_score = min(sum(risk_factors), 100)
    
    def get_profile(self, address: str) -> Optional[UserProfile]:
        """Get user profile by address"""
        return self.user_profiles.get(address)
    
    def get_users_by_category(self, category: str) -> List[UserProfile]:
        """Get all users with a specific category"""
        return [profile for profile in self.user_profiles.values() 
                if category in profile.categories]
    
    def export_profiles(self, filename: str = "user_profiles.json") -> None:
        """Export user profiles to JSON file"""
        serializable_profiles = {}
        
        for address, profile in self.user_profiles.items():
            serializable_profiles[address] = {
                "address": profile.address,
                "categories": list(profile.categories),
                "action_counts": profile.action_counts,
                "protocol_usage": profile.protocol_usage,
                "first_seen": profile.first_seen.isoformat() if profile.first_seen else None,
                "last_seen": profile.last_seen.isoformat() if profile.last_seen else None,
                "total_transactions": profile.total_transactions,
                "total_gas_spent": profile.total_gas_spent,
                "total_value_transacted": profile.total_value_transacted,
                "unique_contracts": list(profile.unique_contracts),
                "risk_score": profile.risk_score,
                "sophistication_score": profile.sophistication_score
            }
        
        with open(filename, 'w') as f:
            json.dump({
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "total_profiles": len(self.user_profiles)
                },
                "profiles": serializable_profiles
            }, f, indent=2)
        
        self.logger.info(f"Exported {len(self.user_profiles)} profiles to {filename}")
```

### 4.2 Real-time Analysis Pipeline

```python
# analysis_pipeline.py
from typing import List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class AnalysisPipeline:
    """Real-time pipeline for processing blockchain data and analyzing behavior"""
    
    def __init__(self, eth_client: EthereumClient, universe: ContractUniverse,
                 selector_registry: SelectorRegistry, behavioral_engine: BehavioralAnalysisEngine):
        self.eth_client = eth_client
        self.universe = universe
        self.selector_registry = selector_registry
        self.behavioral_engine = behavioral_engine
        self.decoder = TransactionDecoder(eth_client, universe, selector_registry)
        self.logger = logging.getLogger(__name__)
    
    def process_block(self, block_number: int) -> Dict[str, int]:
        """
        Process a single block and analyze all relevant transactions
        
        Returns:
            Dictionary with processing statistics
        """
        self.logger.info(f"Processing block {block_number}")
        
        try:
            block = self.eth_client.w3.eth.get_block(block_number, full_transactions=True)
            
            stats = {
                "total_transactions": len(block.transactions),
                "relevant_transactions": 0,
                "decoded_actions": 0,
                "new_users": 0,
                "updated_profiles": 0
            }
            
            # Filter relevant transactions
            relevant_txs = []
            for tx in block.transactions:
                if tx['to'] and self.universe.is_tracked_contract(tx['to']):
                    relevant_txs.append(tx['hash'].hex())
                    stats["relevant_transactions"] += 1
            
            # Process relevant transactions
            for tx_hash in relevant_txs:
                actions = self.decoder.decode_transaction(tx_hash)
                stats["decoded_actions"] += len(actions)
                
                for action in actions:
                    # Check if this is a new user
                    if action.user_address not in self.behavioral_engine.user_profiles:
                        stats["new_users"] += 1
                    
                    # Update user profile
                    self.behavioral_engine.update_profile(action)
                    stats["updated_profiles"] += 1
            
            self.logger.info(f"Block {block_number} processed: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error processing block {block_number}: {e}")
            return {"error": str(e)}
    
    def process_block_range(self, start_block: int, end_block: int, 
                           max_workers: int = 4) -> List[Dict]:
        """
        Process a range of blocks with parallel execution
        
        Args:
            start_block: Starting block number
            end_block: Ending block number (inclusive)
            max_workers: Maximum number of worker threads
            
        Returns:
            List of processing statistics for each block
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all block processing tasks
            future_to_block = {
                executor.submit(self.process_block, block_num): block_num
                for block_num in range(start_block, end_block + 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_block):
                block_num = future_to_block[future]
                try:
                    result = future.result()
                    result["block_number"] = block_num
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing block {block_num}: {e}")
                    results.append({"block_number": block_num, "error": str(e)})
        
        # Sort results by block number
        results.sort(key=lambda x: x["block_number"])
        return results
    
    def start_real_time_monitoring(self, poll_interval: int = 12) -> None:
        """
        Start real-time monitoring of new blocks
        
        Args:
            poll_interval: Seconds to wait between block checks
        """
        import time
        
        self.logger.info("Starting real-time monitoring...")
        last_processed_block = self.eth_client.get_current_block()
        
        while True:
            try:
                current_block = self.eth_client.get_current_block()
                
                # Process any new blocks
                if current_block > last_processed_block:
                    for block_num in range(last_processed_block + 1, current_block + 1):
                        self.process_block(block_num)
                    
                    last_processed_block = current_block
                    
                    # Periodically save profiles
                    if last_processed_block % 100 == 0:
                        self.behavioral_engine.export_profiles()
                
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Stopping real-time monitoring...")
                break
            except Exception as e:
                self.logger.error(f"Error in real-time monitoring: {e}")
                time.sleep(poll_interval)
```

## Phase 5: Data Storage & Indexing

### 5.1 Database Schema

```python
# database_schema.py
from sqlalchemy import create_engine, Column, String, Integer, BigInteger, Boolean, DateTime, Text, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Contract(Base):
    """Contract universe table"""
    __tablename__ = 'contracts'
    
    address = Column(String(42), primary_key=True)
    protocol = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    factory_address = Column(String(42), index=True)
    creation_block = Column(BigInteger, index=True)
    creation_timestamp = Column(DateTime, index=True)
    metadata = Column(JSON)
    source = Column(String(20))  # 'factory_discovery' or 'manual_registry'
    created_at = Column(DateTime, default=datetime.utcnow)

class DecodedTransaction(Base):
    """Decoded transaction actions table"""
    __tablename__ = 'decoded_transactions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tx_hash = Column(String(66), nullable=False, index=True)
    block_number = Column(BigInteger, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    user_address = Column(String(42), nullable=False, index=True)
    contract_address = Column(String(42), nullable=False, index=True)
    protocol = Column(String(50), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    function_signature = Column(Text)
    event_signature = Column(Text)
    gas_used = Column(BigInteger)
    gas_price = Column(BigInteger)
    success = Column(Boolean, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_protocol', 'user_address', 'protocol'),
        Index('idx_user_action', 'user_address', 'action_type'),
        Index('idx_block_timestamp', 'block_number', 'timestamp'),
    )

class UserProfile(Base):
    """User behavioral profiles table"""
    __tablename__ = 'user_profiles'
    
    address = Column(String(42), primary_key=True)
    categories = Column(JSON)  # Store as JSON array
    action_counts = Column(JSON)
    protocol_usage = Column(JSON)
    first_seen = Column(DateTime, index=True)
    last_seen = Column(DateTime, index=True)
    total_transactions = Column(Integer, default=0)
    total_gas_spent = Column(BigInteger, default=0)
    total_value_transacted = Column(BigInteger, default=0)
    unique_contracts_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0, index=True)
    sophistication_score = Column(Float, default=0.0, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProcessingStatus(Base):
    """Track processing status for blocks"""
    __tablename__ = 'processing_status'
    
    block_number = Column(BigInteger, primary_key=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    total_transactions = Column(Integer)
    relevant_transactions = Column(Integer)
    decoded_actions = Column(Integer)
    processing_time_seconds = Column(Float)
```

### 5.2 Database Manager

```python
# database_manager.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Optional
import json

class DatabaseManager:
    """Manages database operations for the analysis system"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        self.logger.info("Database tables created")
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def save_contracts(self, contracts: List[DiscoveredContract]):
        """Save discovered contracts to database"""
        with self.get_session() as session:
            try:
                for contract in contracts:
                    db_contract = Contract(
                        address=contract.address,
                        protocol=contract.protocol,
                        category=contract.category,
                        factory_address=contract.factory_address,
                        creation_block=contract.creation_block,
                        creation_timestamp=datetime.fromtimestamp(contract.creation_timestamp),
                        metadata=contract.metadata,
                        source="factory_discovery"
                    )
                    session.merge(db_contract)  # Use merge to handle duplicates
                
                session.commit()
                self.logger.info(f"Saved {len(contracts)} contracts to database")
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error saving contracts: {e}")
                raise
    
    def save_decoded_actions(self, actions: List[DecodedAction]):
        """Save decoded actions to database"""
        with self.get_session() as session:
            try:
                for action in actions:
                    db_action = DecodedTransaction(
                        tx_hash=action.tx_hash,
                        block_number=action.block_number,
                        timestamp=datetime.fromtimestamp(action.timestamp),
                        user_address=action.user_address,
                        contract_address=action.contract_address,
                        protocol=action.protocol,
                        action_type=action.action_type,
                        function_signature=action.function_signature,
                        event_signature=action.event_signature,
                        gas_used=action.gas_used,
                        gas_price=action.gas_price,
                        success=action.success,
                        metadata=action.metadata
                    )
                    session.add(db_action)
                
                session.commit()
                self.logger.info(f"Saved {len(actions)} decoded actions to database")
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error saving decoded actions: {e}")
                raise
    
    def update_user_profile(self, profile: UserProfile):
        """Update user profile in database"""
        with self.get_session() as session:
            try:
                db_profile = UserProfile(
                    address=profile.address,
                    categories=list(profile.categories),
                    action_counts=profile.action_counts,
                    protocol_usage=profile.protocol_usage,
                    first_seen=profile.first_seen,
                    last_seen=profile.last_seen,
                    total_transactions=profile.total_transactions,
                    total_gas_spent=profile.total_gas_spent,
                    total_value_transacted=profile.total_value_transacted,
                    unique_contracts_count=len(profile.unique_contracts),
                    risk_score=profile.risk_score,
                    sophistication_score=profile.sophistication_score
                )
                session.merge(db_profile)
                session.commit()
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error updating user profile {profile.address}: {e}")
                raise
    
    def get_user_profiles_by_category(self, category: str) -> List[Dict]:
        """Get user profiles by behavioral category"""
        with self.get_session() as session:
            result = session.execute(
                text("SELECT * FROM user_profiles WHERE JSON_CONTAINS(categories, :category)"),
                {"category": json.dumps([category])}
            )
            return [dict(row) for row in result]
    
    def get_protocol_stats(self) -> Dict[str, Dict]:
        """Get statistics by protocol"""
        with self.get_session() as session:
            result = session.execute(text("""
                SELECT 
                    protocol,
                    COUNT(*) as total_transactions,
                    COUNT(DISTINCT user_address) as unique_users,
                    AVG(gas_used) as avg_gas_used
                FROM decoded_transactions 
                GROUP BY protocol
                ORDER BY total_transactions DESC
            """))
            
            return {row.protocol: {
                "total_transactions": row.total_transactions,
                "unique_users": row.unique_users,
                "avg_gas_used": float(row.avg_gas_used)
            } for row in result}

# Usage example in main application
def main():
    """Main application entry point"""
    
    # Initialize components
    eth_client = EthereumClient(ETH_CONFIG)
    universe = ContractUniverse(eth_client)
    selector_registry = SelectorRegistry()
    behavioral_engine = BehavioralAnalysisEngine()
    db_manager = DatabaseManager("postgresql://user:pass@localhost/blockchain_analysis")
    
    # Create database tables
    db_manager.create_tables()
    
    # Build contract universe
    contracts = universe.build_universe()
    
    # Save to database
    discovered_contracts = []
    for address, info in contracts.items():
        if info.get("source") == "factory_discovery":
            discovered_contracts.append(DiscoveredContract(
                address=address,
                protocol=info["protocol"],
                category=info["category"],
                factory_address=info["factory_address"],
                creation_block=info["creation_block"],
                creation_timestamp=info["creation_timestamp"],
                metadata=info["metadata"]
            ))
    
    db_manager.save_contracts(discovered_contracts)
    
    # Create analysis pipeline
    pipeline = AnalysisPipeline(eth_client, universe, selector_registry, behavioral_engine)
    
    # Process recent blocks
    current_block = eth_client.get_current_block()
    results = pipeline.process_block_range(current_block - 100, current_block)
    
    # Export results
    behavioral_engine.export_profiles()
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
```

## Summary

This implementation guide provides a complete, production-ready system for:

1. **Automated Contract Discovery**: Using factory events to discover all DEX pools and markets
2. **Behavioral Action Mapping**: Decoding transactions to identify specific user actions
3. **Real-time Analysis**: Processing new blocks and updating user profiles
4. **Scalable Storage**: Database schema optimized for behavioral analysis queries
5. **User Categorization**: Sophisticated heuristics to classify user behavior patterns

The system is designed to be modular, scalable, and extensible for various blockchain analysis use cases. 