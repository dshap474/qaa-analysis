# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Configuration Module for Contract Universe Discovery System                        │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Configuration Module
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/config.py
---
Configuration classes and settings for Ethereum node connection and factory contract
discovery parameters.
"""

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


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Default Configuration                                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

# Load configuration from environment
DEFAULT_ETH_CONFIG = EthereumConfig(
    rpc_url=os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY"),
    archive_node_url=os.getenv("ETH_ARCHIVE_URL"),
    chunk_size=int(os.getenv("CHUNK_SIZE", "5000"))
)

# Core factory configurations for major DeFi protocols
DEFAULT_FACTORY_CONFIGS = [
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ Decentralized Exchanges (DEXs)                                             │
    # └─────────────────────────────────────────────────────────────────────────────┘
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
        protocol="SushiSwap",
        factory_address="0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
        event_topic="0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9",
        child_slot_index=2,
        creation_block=10794229,
        category="DEX Pool"
    ),
    FactoryConfig(
        protocol="Curve CryptoSwap",
        factory_address="0xf18056bbd320e96a48e3fbf8bc061322531aac99",
        event_topic="0x062384933E4AA575767D87DAd5f6F3529C070D3A4579C8D9AA80916852577E09",
        child_slot_index=0,
        creation_block=14725543,
        category="DEX Pool"
    ),
    FactoryConfig(
        protocol="Curve StableSwap",
        factory_address="0x0959158b6040D32d04c301A72CBFD6b39E21c9AE",
        event_topic="0x964a81b15fb64a1e6aabff8d1f82c4f85fac0c53ba6bb1a90d55f41b2b58e49e",
        child_slot_index=0,
        creation_block=12893599,
        category="DEX Pool"
    ),
    FactoryConfig(
        protocol="Balancer V2",
        factory_address="0xA5bf2ddF098bb0Ef6d120C98217dD6B141c74EE0",
        event_topic="0x83a48fbcfc991335314e74d0496aab6a1987e992ddc85dddbcc4d6dd6ef2e9fc",
        child_slot_index=0,
        creation_block=12272146,
        category="DEX Pool"
    ),
    
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ Lending & Borrowing Protocols                                               │
    # └─────────────────────────────────────────────────────────────────────────────┘
    FactoryConfig(
        protocol="Aave V3",
        factory_address="0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=16291127,
        category="Lending Market"
    ),
    FactoryConfig(
        protocol="Aave V2",
        factory_address="0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=11362579,
        category="Lending Market"
    ),
    FactoryConfig(
        protocol="Compound V3",
        factory_address="0xA17581A9E3356d9A858b789D68B4d866e593aE94",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=15331586,
        category="Lending Market"
    ),
    FactoryConfig(
        protocol="Compound V2",
        factory_address="0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=7710760,
        category="Lending Market"
    ),
    FactoryConfig(
        protocol="MakerDAO",
        factory_address="0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=8928152,
        category="Lending Market"
    ),
    
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ Liquid Staking Protocols                                                    │
    # └─────────────────────────────────────────────────────────────────────────────┘
    FactoryConfig(
        protocol="Lido",
        factory_address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=11473216,
        category="Liquid Staking"
    ),
    FactoryConfig(
        protocol="Rocket Pool",
        factory_address="0xDD3f50F8A6CafbE9b31a427582963f465E745AF8",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=13325304,
        category="Liquid Staking"
    ),
    
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ Yield Farming & Vaults                                                      │
    # └─────────────────────────────────────────────────────────────────────────────┘
    FactoryConfig(
        protocol="Yearn Finance",
        factory_address="0x50c1a2eA0a861A967D9d0FFE2AE4012c2E053804",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=12045555,
        category="Yield Vault"
    ),
    FactoryConfig(
        protocol="Convex Finance",
        factory_address="0xF403C135812408BFbE8713b5A23a04b3D48AAE31",
        event_topic="0x33c7d7adf0ad6b56e178d4e5b78d516b5dd6bf9b6d4b1a8b5b8b8b8b8b8b8b8b",
        child_slot_index=0,
        creation_block=12353322,
        category="Yield Vault"
    )
]


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Core Base Contracts for User Action Tracking                                      │
# └────────────────────────────────────────────────────────────────────────────────────┘

@dataclass
class BaseContractConfig:
    """Configuration for core base contracts used for user action mapping"""
    protocol: str
    contract_type: str  # "Router", "Pool", "Vault", "Marketplace", etc.
    address: str
    name: str
    description: str
    category: str
    primary_functions: List[str]  # Key function signatures to track
    primary_events: List[str]     # Key event signatures to track
    
# Core base contracts that users interact with directly
# These are the main entry points for user actions across DeFi
CORE_BASE_CONTRACTS = [
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ DEX Routers & Core Contracts                                                │
    # └─────────────────────────────────────────────────────────────────────────────┘
    BaseContractConfig(
        protocol="Uniswap V2",
        contract_type="Router",
        address="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        name="UniswapV2Router02",
        description="Main router for Uniswap V2 swaps and liquidity operations",
        category="DEX",
        primary_functions=[
            "swapExactTokensForTokens",
            "swapTokensForExactTokens", 
            "addLiquidity",
            "removeLiquidity",
            "swapExactETHForTokens",
            "swapExactTokensForETH"
        ],
        primary_events=["Swap", "Mint", "Burn"]
    ),
    BaseContractConfig(
        protocol="Uniswap V3",
        contract_type="Router",
        address="0xE592427A0AEce92De3Edee1F18E0157C05861564",
        name="SwapRouter",
        description="Main router for Uniswap V3 swaps",
        category="DEX",
        primary_functions=[
            "exactInputSingle",
            "exactOutputSingle",
            "exactInput",
            "exactOutput"
        ],
        primary_events=["Swap"]
    ),
    BaseContractConfig(
        protocol="Uniswap",
        contract_type="Universal Router",
        address="0xEf1c6E67703c7BD7107eed8303Fbe6EC2554BF6B",
        name="UniversalRouter",
        description="Universal router for V2/V3 and NFT operations",
        category="DEX",
        primary_functions=["execute"],
        primary_events=["Swap", "Transfer"]
    ),
    BaseContractConfig(
        protocol="SushiSwap",
        contract_type="Router",
        address="0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        name="SushiSwapRouter",
        description="Main router for SushiSwap operations",
        category="DEX",
        primary_functions=[
            "swapExactTokensForTokens",
            "addLiquidity",
            "removeLiquidity"
        ],
        primary_events=["Swap", "Mint", "Burn"]
    ),
    
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ Lending & Borrowing                                                         │
    # └─────────────────────────────────────────────────────────────────────────────┘
    BaseContractConfig(
        protocol="Aave V3",
        contract_type="Pool",
        address="0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        name="Aave V3 Pool",
        description="Main lending pool for Aave V3",
        category="Lending",
        primary_functions=[
            "supply",
            "borrow", 
            "repay",
            "withdraw",
            "flashLoan"
        ],
        primary_events=["Supply", "Borrow", "Repay", "Withdraw", "FlashLoan"]
    ),
    BaseContractConfig(
        protocol="Aave V2",
        contract_type="Pool",
        address="0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
        name="Aave V2 LendingPool",
        description="Main lending pool for Aave V2",
        category="Lending",
        primary_functions=[
            "deposit",
            "borrow",
            "repay", 
            "withdraw",
            "flashLoan"
        ],
        primary_events=["Deposit", "Borrow", "Repay", "Withdraw", "FlashLoan"]
    ),
    BaseContractConfig(
        protocol="Compound V3",
        contract_type="Comet",
        address="0xc3d688B66703497DAA19211EEdff47f25384cdc3",
        name="Compound V3 USDC Comet",
        description="Compound V3 USDC market",
        category="Lending",
        primary_functions=[
            "supply",
            "withdraw",
            "borrow",
            "repay"
        ],
        primary_events=["Supply", "Withdraw", "SupplyCollateral", "WithdrawCollateral"]
    ),
    
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ Liquid Staking                                                              │
    # └─────────────────────────────────────────────────────────────────────────────┘
    BaseContractConfig(
        protocol="Lido",
        contract_type="Token",
        address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
        name="Lido stETH",
        description="Lido liquid staking token",
        category="Liquid Staking",
        primary_functions=["submit"],
        primary_events=["Transfer", "Submitted"]
    ),
    BaseContractConfig(
        protocol="Rocket Pool", 
        contract_type="Deposit Pool",
        address="0xDD3f50F8A6CafbE9b31a427582963f465E745AF8",
        name="Rocket Pool Deposit Pool",
        description="Main contract for ETH deposits",
        category="Liquid Staking",
        primary_functions=["deposit"],
        primary_events=["DepositReceived", "Transfer"]
    ),
    
    # ┌─────────────────────────────────────────────────────────────────────────────┐
    # │ NFT Marketplaces                                                            │
    # └─────────────────────────────────────────────────────────────────────────────┘
    BaseContractConfig(
        protocol="OpenSea",
        contract_type="Marketplace",
        address="0x00000000000000068F116a894984e2DB1123eB395",
        name="Seaport 1.6",
        description="OpenSea marketplace protocol",
        category="NFT Marketplace",
        primary_functions=[
            "fulfillBasicOrder",
            "fulfillOrder",
            "fulfillAdvancedOrder"
        ],
        primary_events=["OrderFulfilled"]
    ),
    BaseContractConfig(
        protocol="Blur",
        contract_type="Marketplace", 
        address="0x000000000000Ad05Ccc4F10045630fb830B95127",
        name="Blur Marketplace",
        description="Blur NFT marketplace",
        category="NFT Marketplace",
        primary_functions=["execute"],
        primary_events=["OrdersMatched"]
    )
]


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Configuration Selection Functions                                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘

def get_factory_configs_by_protocol(protocols: List[str]) -> List[FactoryConfig]:
    """Get factory configurations for specific protocols"""
    return [fc for fc in DEFAULT_FACTORY_CONFIGS if fc.protocol in protocols]

def get_factory_configs_by_category(categories: List[str]) -> List[FactoryConfig]:
    """Get factory configurations for specific categories"""
    return [fc for fc in DEFAULT_FACTORY_CONFIGS if fc.category in categories]

def get_base_contracts_by_protocol(protocols: List[str]) -> List[BaseContractConfig]:
    """Get base contract configurations for specific protocols"""
    return [bc for bc in CORE_BASE_CONTRACTS if bc.protocol in protocols]

def get_base_contracts_by_category(categories: List[str]) -> List[BaseContractConfig]:
    """Get base contract configurations for specific categories"""
    return [bc for bc in CORE_BASE_CONTRACTS if bc.category in categories]

def get_all_tracked_protocols() -> List[str]:
    """Get list of all protocols we can track"""
    factory_protocols = {fc.protocol for fc in DEFAULT_FACTORY_CONFIGS}
    base_protocols = {bc.protocol for bc in CORE_BASE_CONTRACTS}
    return sorted(factory_protocols.union(base_protocols))

def get_all_tracked_categories() -> List[str]:
    """Get list of all categories we can track"""
    factory_categories = {fc.category for fc in DEFAULT_FACTORY_CONFIGS}
    base_categories = {bc.category for bc in CORE_BASE_CONTRACTS}
    return sorted(factory_categories.union(base_categories))


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Configuration Validation                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘

def validate_ethereum_config(config: EthereumConfig) -> bool:
    """Validate Ethereum configuration parameters"""
    if not config.rpc_url:
        raise ValueError("RPC URL is required")
    
    if config.chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    if config.max_retries < 0:
        raise ValueError("Max retries cannot be negative")
    
    if config.request_timeout <= 0:
        raise ValueError("Request timeout must be positive")
    
    return True


def validate_factory_config(config: FactoryConfig) -> bool:
    """Validate factory configuration parameters"""
    if not config.protocol:
        raise ValueError("Protocol name is required")
    
    if not config.factory_address or len(config.factory_address) != 42:
        raise ValueError("Valid factory address is required")
    
    if not config.event_topic or len(config.event_topic) != 66:
        raise ValueError("Valid event topic is required")
    
    if config.child_slot_index < 0:
        raise ValueError("Child slot index cannot be negative")
    
    if config.creation_block < 0:
        raise ValueError("Creation block cannot be negative")
    
    if not config.category:
        raise ValueError("Category is required")
    
    return True


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Configuration Factory Functions                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

def create_ethereum_config(
    rpc_url: str,
    archive_node_url: Optional[str] = None,
    chunk_size: int = 5000,
    max_retries: int = 3,
    request_timeout: int = 30
) -> EthereumConfig:
    """Create and validate an Ethereum configuration"""
    config = EthereumConfig(
        rpc_url=rpc_url,
        archive_node_url=archive_node_url,
        chunk_size=chunk_size,
        max_retries=max_retries,
        request_timeout=request_timeout
    )
    validate_ethereum_config(config)
    return config


def create_factory_config(
    protocol: str,
    factory_address: str,
    event_topic: str,
    child_slot_index: int,
    creation_block: int,
    category: str
) -> FactoryConfig:
    """Create and validate a factory configuration"""
    config = FactoryConfig(
        protocol=protocol,
        factory_address=factory_address,
        event_topic=event_topic,
        child_slot_index=child_slot_index,
        creation_block=creation_block,
        category=category
    )
    validate_factory_config(config)
    return config 