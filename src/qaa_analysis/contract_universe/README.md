# Contract Universe Discovery System

**Ethereum Contract Universe Discovery & Behavioral Analysis System**

A comprehensive Python module for automated discovery of Ethereum DeFi and NFT contracts, behavioral analysis, and user action mapping.

## 🏗️ Current Status: Phase 1 Complete

✅ **Phase 1: Infrastructure Setup** - *Complete*
- Configuration management for Ethereum connections and factory contracts
- Enhanced Ethereum client with retry logic and error handling
- Validation and factory functions for easy setup

✅ **PHASE 2 COMPLETE: Volume-Filtered Discovery + Action Mapping Foundation**

---

**Output Location:** `data/contract_universe/`  
**Contract List Generation:** Ready for production  
**Base Contract Tracking:** ✅ 18 protocols across DEX, Lending, Liquid Staking, NFT markets  
**Coverage Strategy:** 90% of DeFi trading volume with ~400-800 contracts (vs 250k+ total)

---

🚧 **Upcoming Phases:**
- Phase 3: Action Mapping System
- Phase 4: Behavioral Analysis Engine
- Phase 5: Data Storage & Indexing

## 🚀 Quick Start

### Installation

The module is part of the `qaa-analysis` project. Ensure you have the required dependencies:

```bash
# Using poetry (recommended)
poetry install

# Or using pip
pip install web3 eth-abi requests
```

### Basic Usage

```python
from qaa_analysis.contract_universe import quick_setup, get_module_info

# Get module information
info = get_module_info()
print(f"Module: {info['name']} v{info['version']}")

# Quick setup with your Ethereum RPC URL
client = quick_setup("https://mainnet.infura.io/v3/YOUR_KEY")

# Test the connection
current_block = client.get_current_block()
print(f"Current block: {current_block:,}")
```

### Environment Setup

Set your Ethereum RPC URL as an environment variable:

```bash
export ETH_RPC_URL="https://mainnet.infura.io/v3/your_actual_key"
```

## 📚 Documentation

### Module Structure

```
contract_universe/
├── __init__.py           # Main module interface
├── config.py            # Configuration classes and defaults
├── eth_client.py        # Enhanced Ethereum client
├── docs/                # Implementation guide and documentation
├── tests/               # Comprehensive test suite
└── examples/            # Usage examples and demos
```

### Core Components

#### EthereumConfig
Configuration class for Ethereum node connections:
- `rpc_url`: Ethereum RPC endpoint
- `archive_node_url`: Optional archive node (for historical data)
- `chunk_size`: Block processing batch size (default: 5000)
- `max_retries`: Connection retry attempts (default: 3)
- `request_timeout`: Request timeout in seconds (default: 30)

#### FactoryConfig
Configuration class for factory contract discovery:
- `protocol`: Protocol name (e.g., "Uniswap V2")
- `factory_address`: Factory contract address
- `event_topic`: Event topic hash for pool/market creation
- `child_slot_index`: Position of child address in event topics
- `creation_block`: Block when factory was deployed
- `category`: Contract category (e.g., "DEX Pool")

#### EthereumClient
Enhanced Web3 client with:
- Automatic retry logic with exponential backoff
- Connection validation and error handling
- Block processing utilities
- Address validation and conversion
- Processing estimation tools

## 🔧 Advanced Usage

### Custom Configuration

```python
from qaa_analysis.contract_universe import (
    create_ethereum_config,
    create_factory_config,
    create_ethereum_client
)

# Create custom Ethereum configuration
eth_config = create_ethereum_config(
    rpc_url="https://your.rpc.endpoint/",
    chunk_size=2000,        # Smaller chunks
    max_retries=5,          # More retries
    request_timeout=45      # Longer timeout
)

# Create custom factory configuration
factory_config = create_factory_config(
    protocol="Custom DEX",
    factory_address="0x...",
    event_topic="0x...",
    child_slot_index=1,
    creation_block=15000000,
    category="DEX Pool"
)

# Create client with custom config
client = create_ethereum_client(eth_config)
```

### Working with Default Configurations

```python
from qaa_analysis.contract_universe import (
    DEFAULT_ETH_CONFIG,
    DEFAULT_FACTORY_CONFIGS
)

# View default configurations
print(f"Default chunk size: {DEFAULT_ETH_CONFIG.chunk_size}")

# See all supported protocols
for config in DEFAULT_FACTORY_CONFIGS:
    print(f"{config.protocol}: {config.factory_address}")
```

### Connection Testing

```python
from qaa_analysis.contract_universe import test_connection

# Test connection to an RPC endpoint
result = test_connection("https://mainnet.infura.io/v3/YOUR_KEY")

if result["connected"]:
    print(f"✅ Connected! Current block: {result['current_block']}")
else:
    print(f"❌ Failed: {result['error']}")
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# From the project root
poetry run pytest src/qaa_analysis/contract_universe/tests/

# Run specific test file
poetry run pytest src/qaa_analysis/contract_universe/tests/test_phase1.py

# Run with coverage
poetry run pytest src/qaa_analysis/contract_universe/tests/ --cov=src/qaa_analysis/contract_universe
```

## 📋 Examples

### Run the Phase 1 Demo

```bash
# Set your RPC URL
export ETH_RPC_URL="https://mainnet.infura.io/v3/YOUR_KEY"

# Run the demo
poetry run python -C src/qaa_analysis/contract_universe/examples/phase1_demo.py
```

The demo showcases:
- Quick setup and module information
- Custom configuration creation
- Default configuration usage
- Client features and utilities
- Connection testing
- Validation error handling

## 🔗 Supported Protocols (Default)

The module comes with pre-configured support for major DeFi protocols:

| Protocol | Factory Address | Category | Creation Block |
|----------|----------------|----------|----------------|
| Uniswap V2 | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | DEX Pool | 10,000,835 |
| Uniswap V3 | `0x1F98431c8aD98523631AE4a59f267346ea31F984` | DEX Pool | 12,369,621 |
| Curve CryptoSwap | `0xf18056bbd320e96a48e3fbf8bc061322531aac99` | DEX Pool | 14,725,543 |

## 🛡️ Error Handling

The module includes comprehensive error handling:

- **Connection Errors**: Automatic retry with exponential backoff
- **Validation Errors**: Clear error messages for invalid configurations
- **Network Errors**: Graceful handling of RPC timeouts and failures
- **Custom Exceptions**: `EthereumClientError` for blockchain-specific issues

## 🔮 Roadmap

### Phase 2: Volume-Filtered Contract Discovery (Next)
- 180-day volume coverage strategy for high-impact pools
- Multi-source volume data integration and validation
- Smart filtering: 90% volume coverage with ~400-800 pools vs 300k+ total
- Efficient processing: ~30 minutes vs 8+ hours for full discovery

### Phase 3: Action Mapping System
- Function and event selector registry
- Transaction decoder for user actions
- Real-time action identification

### Phase 4: Behavioral Analysis Engine
- User profile management and scoring
- Behavioral categorization heuristics
- Pattern detection and analytics

### Phase 5: Data Storage & Indexing
- Database schema and management
- Efficient data storage and querying
- Analytics and reporting tools

## 🤝 Contributing

The module follows the project's established patterns:

1. **Comment Banners**: Use the consistent banner format for sections
2. **File Headers**: Include name, path, and description
3. **Documentation**: Comprehensive docstrings and type hints
4. **Testing**: Write tests for all functionality
5. **Examples**: Provide clear usage examples

## 📄 License

Part of the QAA Analysis project. See the main project license for details.

## 🆘 Support

For issues and questions:
1. Check the examples and tests for usage patterns
2. Review the comprehensive documentation in `docs/`
3. Refer to the Implementation Guide for technical details

---

**Phase 1 Complete** ✅ | **Ready for Phase 2** 🚀 

### 1. **Create High-Impact Contract List**
```python
from qaa_analysis.contract_universe import create_high_impact_contract_list

# Set your RPC URL
eth_rpc_url = "https://mainnet.infura.io/v3/YOUR_KEY"

# Generate comprehensive contract list (saves to data/contract_universe/)
contract_list_path = create_high_impact_contract_list(eth_rpc_url)
print(f"📁 Contract list saved to: {contract_list_path}")
```

### 2. **Configure Specific DeFi Apps to Track**
```python
# Option 1: Select specific protocols
major_defi_protocols = [
    "Uniswap V2", "Uniswap V3", "SushiSwap",
    "Aave V2", "Aave V3", "Compound V3",
    "Lido", "Rocket Pool"
]

contract_list_path = create_high_impact_contract_list(
    eth_rpc_url=eth_rpc_url,
    protocols=major_defi_protocols,
    target_coverage=0.95  # 95% coverage
)
```

### 3. **Configure User Action Tracking**
```python
from qaa_analysis.contract_universe import create_action_mapper

# Track DEX interactions only
dex_mapper = create_action_mapper(categories=['DEX'])

# Check if address is a tracked contract
uniswap_router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
is_tracked = dex_mapper.is_tracked_contract(uniswap_router)
functions = dex_mapper.get_contract_functions(uniswap_router)
```

---

## Features

### 📊 **Volume-Filtered Discovery**
- **90% Coverage Strategy**: Discovers contracts representing 90% of DeFi trading volume
- **Efficiency**: ~400-800 contracts vs 250k+ total (99%+ reduction)
- **Real-time Processing**: ~30 minutes vs 8+ hours for comprehensive discovery
- **Multi-source Data**: The Graph Protocol, DeFiLlama API, DEX Screener API + mock fallback

### 📁 **Output Generation**
- **Location**: `data/contract_universe/`
- **Formats**: JSON (with metadata) and CSV  
- **Timestamped Files**: `high_impact_contracts_20241201_143022.json`
- **Latest Versions**: `high_impact_contracts_latest.json`
- **Discovery Summaries**: Statistics and protocol breakdown

### 🎯 **Core Base Contracts for User Action Tracking**
- **18 Protocols**: Uniswap, Aave, Compound, Lido, OpenSea, Blur, etc.
- **Function Tracking**: Primary functions and events for behavioral analysis
- **Configurable**: Filter by protocol or category
- **Phase 3 Ready**: Foundation for transaction decoding and user profiling

### 🔧 **Flexible Configuration**
```python
# By protocol
get_factory_configs_by_protocol(["Uniswap V2", "Aave V3"])

# By category  
get_factory_configs_by_category(["DEX Pool", "Lending Market"])

# Core base contracts
ActionMappingPresets.get_major_dex_contracts()
ActionMappingPresets.get_major_lending_contracts()
```

---

## Protocol Coverage

### **DEX Protocols**
- Uniswap V2, V3 (Universal Router)
- SushiSwap
- Curve Finance (CryptoSwap + StableSwap)
- Balancer V2

### **Lending & Borrowing**
- Aave V2, V3
- Compound V2, V3 (Comet)
- MakerDAO

### **Liquid Staking**
- Lido (stETH)
- Rocket Pool (rETH)

### **Yield & Vaults**
- Yearn Finance
- Convex Finance

### **NFT Marketplaces**
- OpenSea (Seaport 1.6)
- Blur

---

## Output Structure

```
data/contract_universe/
├── high_impact_contracts_20241201_143022.json    # Timestamped contract list
├── high_impact_contracts_20241201_143022.csv     # CSV format
├── high_impact_contracts_latest.json             # Latest JSON
├── high_impact_contracts_latest.csv              # Latest CSV
├── discovery_summary_20241201_143022.json        # Discovery statistics  
└── discovery_summary_latest.json                 # Latest summary
```

### **JSON Format**
```json
{
  "metadata": {
    "discovery_timestamp": "2024-12-01T14:30:22Z",
    "target_coverage": 0.90,
    "actual_coverage": 0.912,
    "total_contracts_discovered": 423,
    "protocols_included": ["Uniswap V2", "Uniswap V3", "Curve", "Aave"],
    "description": "High-impact DeFi contracts representing 91.2% of 180-day trading volume"
  },
  "contracts": [
    {
      "address": "0x...",
      "protocol": "Uniswap V2",
      "token_pair": "USDC/WETH", 
      "volume_180d_usd": 2500000000,
      "tvl_current_usd": 45000000
    }
  ]
}
```

---

## Examples

### **Run Contract Discovery**
```bash
# Set your RPC URL
export ETH_RPC_URL="https://mainnet.infura.io/v3/YOUR_KEY"

# Run the example script
poetry run python src/qaa_analysis/contract_universe/examples/create_contract_list.py
```

### **Custom Configuration Examples**
```python
# Focus on major DEXs only
dex_protocols = ["Uniswap V2", "Uniswap V3", "SushiSwap", "Curve CryptoSwap"]
create_high_impact_contract_list(eth_rpc_url, protocols=dex_protocols)

# High coverage for comprehensive analysis
create_high_impact_contract_list(eth_rpc_url, target_coverage=0.95)

# Custom output location
create_high_impact_contract_list(eth_rpc_url, output_dir="./my_contract_lists")
```

---

## Testing

```bash
# Run all Phase 2 tests (24 tests)
poetry run python -m pytest src/qaa_analysis/contract_universe/tests/test_phase2.py -v

# Test action mapping
poetry run python -c "from src.qaa_analysis.contract_universe import create_action_mapper; print(len(create_action_mapper().get_all_tracked_addresses()))"
```

---

## What's Next: Phase 3

### **Complete Action Mapping System**
- ✅ **Foundation Ready**: Core base contracts and configuration system
- 🔄 **Next**: Transaction decoding and event parsing
- 🔄 **Next**: User action identification and behavioral mapping
- 🔄 **Next**: Real-time monitoring and analysis pipeline

### **User Behavioral Analysis**
- Transaction pattern analysis
- DeFi protocol usage profiling  
- Risk assessment and categorization
- Portfolio analysis and insights

---

## Architecture

```
Phase 2: Volume-Filtered Discovery + Action Mapping Foundation
├── volume_discovery.py     # Volume-filtered contract discovery
├── action_mapping.py       # Core base contracts for user tracking
├── config.py              # Protocol configurations & base contracts
├── eth_client.py          # Enhanced Ethereum client
└── examples/              # Usage examples and demos
    ├── create_contract_list.py
    └── phase2_demo.py
```

**Current Status**: ✅ **Phase 2 Complete**  
**Next Phase**: Phase 3 (Complete Action Mapping System)  
**Module Version**: v0.2.0 