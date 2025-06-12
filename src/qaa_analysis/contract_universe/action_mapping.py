# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Action Mapping Module for User Behavior Analysis                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Action Mapping Module
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/action_mapping.py
---
Provides core base contracts and user action mapping functionality for behavioral analysis.
This module exposes the key contracts that users interact with directly across DeFi protocols.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from .config import (
    BaseContractConfig, 
    CORE_BASE_CONTRACTS,
    get_base_contracts_by_protocol,
    get_base_contracts_by_category,
    get_all_tracked_protocols,
    get_all_tracked_categories
)


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Action Mapping Manager                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘

class ActionMappingManager:
    """Manager for core base contracts and user action tracking configuration"""
    
    def __init__(self, custom_contracts: Optional[List[BaseContractConfig]] = None):
        """
        Initialize action mapping manager
        
        Args:
            custom_contracts: Optional list of additional contracts to track
        """
        self.logger = logging.getLogger(__name__)
        
        # Load default core contracts
        self.base_contracts = CORE_BASE_CONTRACTS.copy()
        
        # Add custom contracts if provided
        if custom_contracts:
            self.base_contracts.extend(custom_contracts)
            self.logger.info(f"Added {len(custom_contracts)} custom contracts")
        
        # Create lookup mappings
        self._create_lookups()
        
        self.logger.info(f"Initialized ActionMappingManager with {len(self.base_contracts)} contracts")
    
    def _create_lookups(self):
        """Create internal lookup mappings for fast access"""
        self.contracts_by_address = {c.address.lower(): c for c in self.base_contracts}
        self.contracts_by_protocol = {}
        self.contracts_by_category = {}
        
        for contract in self.base_contracts:
            # Group by protocol
            if contract.protocol not in self.contracts_by_protocol:
                self.contracts_by_protocol[contract.protocol] = []
            self.contracts_by_protocol[contract.protocol].append(contract)
            
            # Group by category
            if contract.category not in self.contracts_by_category:
                self.contracts_by_category[contract.category] = []
            self.contracts_by_category[contract.category].append(contract)
    
    def get_contract_by_address(self, address: str) -> Optional[BaseContractConfig]:
        """Get contract configuration by address"""
        return self.contracts_by_address.get(address.lower())
    
    def get_contracts_by_protocol(self, protocol: str) -> List[BaseContractConfig]:
        """Get all contracts for a specific protocol"""
        return self.contracts_by_protocol.get(protocol, [])
    
    def get_contracts_by_category(self, category: str) -> List[BaseContractConfig]:
        """Get all contracts for a specific category"""
        return self.contracts_by_category.get(category, [])
    
    def is_tracked_contract(self, address: str) -> bool:
        """Check if an address is a tracked core contract"""
        return address.lower() in self.contracts_by_address
    
    def get_contract_functions(self, address: str) -> List[str]:
        """Get primary functions to track for a contract"""
        contract = self.get_contract_by_address(address)
        return contract.primary_functions if contract else []
    
    def get_contract_events(self, address: str) -> List[str]:
        """Get primary events to track for a contract"""
        contract = self.get_contract_by_address(address)
        return contract.primary_events if contract else []
    
    def get_all_tracked_addresses(self) -> Set[str]:
        """Get all tracked contract addresses"""
        return set(self.contracts_by_address.keys())
    
    def get_protocols(self) -> List[str]:
        """Get list of all tracked protocols"""
        return sorted(self.contracts_by_protocol.keys())
    
    def get_categories(self) -> List[str]:
        """Get list of all tracked categories"""
        return sorted(self.contracts_by_category.keys())
    
    def get_protocol_summary(self) -> Dict[str, Dict]:
        """Get summary of all protocols and their contracts"""
        summary = {}
        for protocol, contracts in self.contracts_by_protocol.items():
            summary[protocol] = {
                "contract_count": len(contracts),
                "contract_types": list(set(c.contract_type for c in contracts)),
                "categories": list(set(c.category for c in contracts)),
                "addresses": [c.address for c in contracts]
            }
        return summary
    
    def export_contract_list(self, output_file: str) -> None:
        """Export all tracked contracts to JSON file"""
        import json
        from datetime import datetime, timezone
        
        export_data = {
            "metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_contracts": len(self.base_contracts),
                "protocols": self.get_protocols(),
                "categories": self.get_categories(),
                "description": "Core base contracts for DeFi user action tracking"
            },
            "contracts": [
                {
                    "protocol": c.protocol,
                    "contract_type": c.contract_type,
                    "address": c.address,
                    "name": c.name,
                    "description": c.description,
                    "category": c.category,
                    "primary_functions": c.primary_functions,
                    "primary_events": c.primary_events
                }
                for c in self.base_contracts
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported {len(self.base_contracts)} contracts to {output_file}")


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Configuration Presets                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘

class ActionMappingPresets:
    """Predefined configurations for common use cases"""
    
    @staticmethod
    def get_dex_only_contracts() -> List[BaseContractConfig]:
        """Get only DEX-related contracts"""
        return get_base_contracts_by_category(["DEX"])
    
    @staticmethod
    def get_lending_only_contracts() -> List[BaseContractConfig]:
        """Get only lending protocol contracts"""
        return get_base_contracts_by_category(["Lending"])
    
    @staticmethod
    def get_defi_core_contracts() -> List[BaseContractConfig]:
        """Get core DeFi contracts (DEX + Lending + Liquid Staking)"""
        return get_base_contracts_by_category(["DEX", "Lending", "Liquid Staking"])
    
    @staticmethod
    def get_uniswap_contracts() -> List[BaseContractConfig]:
        """Get all Uniswap-related contracts"""
        return get_base_contracts_by_protocol(["Uniswap V2", "Uniswap V3", "Uniswap"])
    
    @staticmethod
    def get_major_dex_contracts() -> List[BaseContractConfig]:
        """Get contracts for major DEXs (Uniswap, SushiSwap)"""
        return get_base_contracts_by_protocol(["Uniswap V2", "Uniswap V3", "Uniswap", "SushiSwap"])
    
    @staticmethod
    def get_major_lending_contracts() -> List[BaseContractConfig]:
        """Get contracts for major lending protocols (Aave, Compound)"""
        return get_base_contracts_by_protocol(["Aave V2", "Aave V3", "Compound V3"])
    
    @staticmethod
    def get_nft_marketplace_contracts() -> List[BaseContractConfig]:
        """Get NFT marketplace contracts"""
        return get_base_contracts_by_category(["NFT Marketplace"])


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Convenience Functions                                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

def create_action_mapper(protocols: Optional[List[str]] = None, 
                        categories: Optional[List[str]] = None,
                        custom_contracts: Optional[List[BaseContractConfig]] = None) -> ActionMappingManager:
    """
    Create an action mapping manager with optional filtering
    
    Args:
        protocols: List of protocols to include (default: all)
        categories: List of categories to include (default: all)
        custom_contracts: Additional custom contracts to track
    
    Returns:
        Configured ActionMappingManager
    """
    
    # Start with all contracts or filter by protocols/categories
    contracts = CORE_BASE_CONTRACTS.copy()
    
    if protocols:
        contracts = [c for c in contracts if c.protocol in protocols]
    
    if categories:
        contracts = [c for c in contracts if c.category in categories]
    
    # Add custom contracts
    if custom_contracts:
        contracts.extend(custom_contracts)
    
    return ActionMappingManager(contracts)


def get_tracked_contract_summary() -> Dict[str, Dict]:
    """Get a summary of all available tracked contracts"""
    
    protocols = {}
    for contract in CORE_BASE_CONTRACTS:
        if contract.protocol not in protocols:
            protocols[contract.protocol] = {
                "contracts": [],
                "categories": set(),
                "contract_types": set()
            }
        
        protocols[contract.protocol]["contracts"].append(contract.address)
        protocols[contract.protocol]["categories"].add(contract.category)
        protocols[contract.protocol]["contract_types"].add(contract.contract_type)
    
    # Convert sets to lists for JSON serialization
    for protocol in protocols.values():
        protocol["categories"] = sorted(protocol["categories"])
        protocol["contract_types"] = sorted(protocol["contract_types"])
        protocol["contract_count"] = len(protocol["contracts"])
    
    return protocols


def print_available_protocols():
    """Print all available protocols and their details"""
    
    print("# ┌────────────────────────────────────────────────────────────────────────────────────┐")
    print("# │ Available DeFi Protocols for User Action Tracking                                 │")
    print("# └────────────────────────────────────────────────────────────────────────────────────┘")
    print()
    
    summary = get_tracked_contract_summary()
    
    for protocol, info in sorted(summary.items()):
        print(f"**{protocol}**")
        print(f"  - Contracts: {info['contract_count']}")
        print(f"  - Categories: {', '.join(info['categories'])}")
        print(f"  - Types: {', '.join(info['contract_types'])}")
        print(f"  - Addresses: {', '.join(info['contracts'][:3])}{'...' if len(info['contracts']) > 3 else ''}")
        print()
    
    print(f"**Total**: {len(CORE_BASE_CONTRACTS)} core contracts across {len(summary)} protocols")
    print()
    print("**Usage Examples:**")
    print("```python")
    print("# Track only DEXs")
    print("mapper = create_action_mapper(categories=['DEX'])")
    print()
    print("# Track only Uniswap contracts")
    print("mapper = create_action_mapper(protocols=['Uniswap V2', 'Uniswap V3'])")
    print()
    print("# Check if address is tracked")
    print("is_tracked = mapper.is_tracked_contract('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')")
    print("```")


if __name__ == "__main__":
    # Demo the action mapping functionality
    print_available_protocols()
    
    # Create a manager and show some examples
    print("\n" + "="*80)
    print("DEMO: Action Mapping Manager")
    print("="*80)
    
    # Create manager with all contracts
    manager = ActionMappingManager()
    
    print(f"Total tracked contracts: {len(manager.get_all_tracked_addresses())}")
    print(f"Protocols: {', '.join(manager.get_protocols())}")
    print(f"Categories: {', '.join(manager.get_categories())}")
    
    # Test a specific contract
    uniswap_router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    print(f"\nUniswap V2 Router ({uniswap_router}):")
    print(f"  - Is tracked: {manager.is_tracked_contract(uniswap_router)}")
    print(f"  - Functions: {manager.get_contract_functions(uniswap_router)}")
    print(f"  - Events: {manager.get_contract_events(uniswap_router)}") 