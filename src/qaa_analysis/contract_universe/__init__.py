# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Contract Universe Discovery System - Main Module                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Contract Universe Discovery System
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/__init__.py
---
A comprehensive system for automated discovery of Ethereum DeFi and NFT contracts,
behavioral analysis, and user action mapping.

This module provides infrastructure for:
- Automated contract discovery via factory events
- Transaction decoding and action mapping  
- User behavioral analysis and categorization
- Real-time monitoring and data storage

Phase 1: Infrastructure Setup
- Configuration management for Ethereum connections and factory contracts
- Enhanced Ethereum client with retry logic and error handling
- Validation and factory functions for easy setup
"""

from .config import (
    EthereumConfig,
    FactoryConfig,
    BaseContractConfig,
    DEFAULT_ETH_CONFIG,
    DEFAULT_FACTORY_CONFIGS,
    CORE_BASE_CONTRACTS,
    validate_ethereum_config,
    validate_factory_config,
    create_ethereum_config,
    create_factory_config,
    get_factory_configs_by_protocol,
    get_factory_configs_by_category,
    get_base_contracts_by_protocol,
    get_base_contracts_by_category,
    get_all_tracked_protocols,
    get_all_tracked_categories
)

from .eth_client import (
    EthereumClient,
    EthereumClientError,
    create_ethereum_client,
    create_default_client,
    test_connection
)

from .volume_discovery import (
    VolumeFilteredDiscovery,
    PoolVolumeData,
    VolumeThreshold,
    VolumeDataProvider,
    FactoryDiscovery,
    VolumeCoverageCalculator,
    quick_volume_discovery,
    create_high_impact_contract_list
)

from .action_mapping import (
    ActionMappingManager,
    ActionMappingPresets,
    create_action_mapper,
    get_tracked_contract_summary,
    print_available_protocols
)

# Version information
__version__ = "0.2.0"
__author__ = "QAA Analysis Team"

# Module metadata
__all__ = [
    # Configuration classes and constants
    "EthereumConfig",
    "FactoryConfig",
    "BaseContractConfig",
    "DEFAULT_ETH_CONFIG",
    "DEFAULT_FACTORY_CONFIGS",
    "CORE_BASE_CONTRACTS",
    
    # Configuration functions
    "validate_ethereum_config",
    "validate_factory_config", 
    "create_ethereum_config",
    "create_factory_config",
    "get_factory_configs_by_protocol",
    "get_factory_configs_by_category",
    "get_base_contracts_by_protocol",
    "get_base_contracts_by_category",
    "get_all_tracked_protocols",
    "get_all_tracked_categories",
    
    # Ethereum client classes and functions
    "EthereumClient",
    "EthereumClientError",
    "create_ethereum_client",
    "create_default_client",
    "test_connection",
    
    # Volume-filtered discovery (Phase 2)
    "VolumeFilteredDiscovery",
    "PoolVolumeData",
    "VolumeThreshold",
    "VolumeDataProvider",
    "FactoryDiscovery",
    "VolumeCoverageCalculator",
    "quick_volume_discovery",
    "create_high_impact_contract_list",
    
    # Action mapping system (Phase 3 foundation)
    "ActionMappingManager",
    "ActionMappingPresets",
    "create_action_mapper",
    "get_tracked_contract_summary",
    "print_available_protocols",
    
    # Utility functions
    "quick_setup",
    "get_module_info"
]


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Convenience Functions                                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

def quick_setup(rpc_url: str) -> EthereumClient:
    """
    Quick setup function to get started with default configuration
    
    Args:
        rpc_url: Ethereum RPC URL (e.g., Infura, Alchemy endpoint)
        
    Returns:
        Configured EthereumClient ready for use
        
    Example:
        >>> from qaa_analysis.contract_universe import quick_setup
        >>> client = quick_setup("https://mainnet.infura.io/v3/YOUR_KEY")
        >>> print(client.get_current_block())
    """
    return create_default_client(rpc_url)


def get_module_info() -> dict:
    """
    Get information about the contract_universe module
    
    Returns:
        Dictionary with module information
    """
    return {
        "name": "contract_universe",
        "version": __version__,
        "author": __author__,
        "description": "Ethereum Contract Universe Discovery & Behavioral Analysis System",
        "phase": "Phase 2: Volume-Filtered Discovery & Action Mapping Foundation",
        "components": {
            "config": "Configuration management for Ethereum and factory contracts",
            "eth_client": "Enhanced Ethereum client with retry logic and error handling",
            "volume_discovery": "Volume-filtered contract discovery with 180-day coverage strategy and output generation",
            "action_mapping": "Core base contracts and user action tracking configuration for behavioral analysis"
        },
        "features": [
            "✅ Automated discovery of high-impact DeFi pools (90% volume coverage)",
            "✅ Multi-format output generation (JSON, CSV) to data/contract_universe",
            "✅ Comprehensive protocol tracking (DEX, Lending, Liquid Staking, NFT)",
            "✅ Core base contract registry for user action mapping",
            "✅ Configurable protocol and category filtering",
            "✅ Real-time processing with fallback data sources"
        ],
        "next_phases": [
            "Phase 3: Complete Action Mapping System (transaction decoding)", 
            "Phase 4: Behavioral Analysis Engine (user profiling)",
            "Phase 5: Data Storage & Indexing (database integration)"
        ],
        "output_location": "data/contract_universe/",
        "supported_protocols": [
            "Uniswap V2/V3", "SushiSwap", "Curve Finance", "Balancer V2",
            "Aave V2/V3", "Compound V2/V3", "MakerDAO",
            "Lido", "Rocket Pool", "Yearn Finance", "Convex Finance",
            "OpenSea", "Blur"
        ]
    }


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Module Initialization                                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

# Set up basic logging configuration if not already configured
import logging

logger = logging.getLogger(__name__)

# Only configure if no handlers exist
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger.info(f"Contract Universe module v{__version__} initialized")
logger.info("Phase 1: Infrastructure Setup - Ready")
