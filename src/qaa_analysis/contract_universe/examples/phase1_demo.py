# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Phase 1 Demo - Infrastructure Setup Usage Examples                                │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Phase 1 Demo
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/examples/phase1_demo.py
---
Demonstration script showing how to use Phase 1 infrastructure components
for Ethereum connection setup and configuration management.
"""

import os
import logging
import time
from typing import Dict, Any

# Configure logging for the demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_quick_setup():
    """Demonstrate the quickest way to get started"""
    logger.info("=" * 60)
    logger.info("DEMO: Quick Setup")
    logger.info("=" * 60)
    
    # Replace with your actual RPC URL
    rpc_url = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY")
    
    if "YOUR_KEY" in rpc_url:
        logger.warning("⚠️  Using placeholder RPC URL. Set ETH_RPC_URL environment variable for real testing.")
        logger.info("📝 Example: export ETH_RPC_URL='https://mainnet.infura.io/v3/your_actual_key'")
        return
    
    try:
        # Import the contract_universe module
        from qaa_analysis.contract_universe import quick_setup, get_module_info
        
        # Get module information
        info = get_module_info()
        logger.info(f"✅ Module: {info['name']} v{info['version']}")
        logger.info(f"📋 Phase: {info['phase']}")
        
        # Quick setup with default configuration
        logger.info(f"🔗 Connecting to: {rpc_url}")
        client = quick_setup(rpc_url)
        
        # Test the connection
        current_block = client.get_current_block()
        logger.info(f"🏗️  Current block: {current_block:,}")
        
        # Get connection info
        conn_info = client.get_connection_info()
        logger.info(f"⛓️  Chain ID: {conn_info['chain_id']}")
        logger.info(f"📡 Connected: {conn_info['connected']}")
        
        logger.info("✅ Quick setup successful!")
        
    except Exception as e:
        logger.error(f"❌ Quick setup failed: {e}")


def demo_custom_configuration():
    """Demonstrate creating custom configurations"""
    logger.info("=" * 60)
    logger.info("DEMO: Custom Configuration")
    logger.info("=" * 60)
    
    try:
        from qaa_analysis.contract_universe import (
            create_ethereum_config,
            create_factory_config,
            create_ethereum_client,
            EthereumConfig,
            FactoryConfig
        )
        
        # Create custom Ethereum configuration
        eth_config = create_ethereum_config(
            rpc_url="https://mainnet.infura.io/v3/demo",
            chunk_size=2000,  # Smaller chunks for demo
            max_retries=5,    # More retries
            request_timeout=45  # Longer timeout
        )
        
        logger.info(f"📝 Created Ethereum config:")
        logger.info(f"   🔗 RPC URL: {eth_config.rpc_url}")
        logger.info(f"   📦 Chunk size: {eth_config.chunk_size}")
        logger.info(f"   🔄 Max retries: {eth_config.max_retries}")
        logger.info(f"   ⏱️  Timeout: {eth_config.request_timeout}s")
        
        # Create custom factory configuration
        custom_factory = create_factory_config(
            protocol="Custom DEX",
            factory_address="0x1234567890123456789012345678901234567890",
            event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
            child_slot_index=1,
            creation_block=15000000,
            category="Custom Pool"
        )
        
        logger.info(f"🏭 Created factory config:")
        logger.info(f"   📛 Protocol: {custom_factory.protocol}")
        logger.info(f"   📍 Address: {custom_factory.factory_address}")
        logger.info(f"   🏷️  Category: {custom_factory.category}")
        logger.info(f"   🧱 Creation block: {custom_factory.creation_block:,}")
        
        logger.info("✅ Custom configuration successful!")
        
    except Exception as e:
        logger.error(f"❌ Custom configuration failed: {e}")


def demo_default_configurations():
    """Demonstrate working with default configurations"""
    logger.info("=" * 60)
    logger.info("DEMO: Default Configurations")
    logger.info("=" * 60)
    
    try:
        from qaa_analysis.contract_universe import (
            DEFAULT_ETH_CONFIG,
            DEFAULT_FACTORY_CONFIGS
        )
        
        # Show default Ethereum configuration
        logger.info(f"🔧 Default Ethereum Config:")
        logger.info(f"   🔗 RPC URL: {DEFAULT_ETH_CONFIG.rpc_url}")
        logger.info(f"   📦 Chunk size: {DEFAULT_ETH_CONFIG.chunk_size}")
        logger.info(f"   🔄 Max retries: {DEFAULT_ETH_CONFIG.max_retries}")
        
        # Show default factory configurations
        logger.info(f"🏭 Default Factory Configs ({len(DEFAULT_FACTORY_CONFIGS)} total):")
        for i, config in enumerate(DEFAULT_FACTORY_CONFIGS, 1):
            logger.info(f"   {i}. {config.protocol}")
            logger.info(f"      📍 {config.factory_address}")
            logger.info(f"      🏷️  {config.category}")
            logger.info(f"      🧱 Block: {config.creation_block:,}")
        
        logger.info("✅ Default configurations loaded!")
        
    except Exception as e:
        logger.error(f"❌ Default configurations failed: {e}")


def demo_client_features():
    """Demonstrate advanced client features"""
    logger.info("=" * 60)
    logger.info("DEMO: Client Features")
    logger.info("=" * 60)
    
    rpc_url = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY")
    
    if "YOUR_KEY" in rpc_url:
        logger.warning("⚠️  Using placeholder RPC URL. Set ETH_RPC_URL for real testing.")
        return
    
    try:
        from qaa_analysis.contract_universe import create_default_client
        
        # Create client
        client = create_default_client(rpc_url)
        
        # Test address validation
        valid_address = "0xA0b86a33E6441949b34Af3C9F6dB3e3B2A0CB0F6"
        invalid_address = "invalid_address"
        
        logger.info(f"📍 Address validation:")
        logger.info(f"   ✅ {valid_address}: {client.validate_address(valid_address)}")
        logger.info(f"   ❌ {invalid_address}: {client.validate_address(invalid_address)}")
        
        # Test checksum conversion
        checksum_addr = client.to_checksum_address(valid_address.lower())
        logger.info(f"   🔤 Checksum: {checksum_addr}")
        
        # Get connection information
        conn_info = client.get_connection_info()
        logger.info(f"📡 Connection Info:")
        for key, value in conn_info.items():
            logger.info(f"   {key}: {value}")
        
        # Estimate processing for a block range
        current_block = client.get_current_block()
        start_block = current_block - 1000
        estimate = client.estimate_blocks_in_range(start_block, current_block)
        
        logger.info(f"📊 Processing Estimate (last 1000 blocks):")
        logger.info(f"   🧱 Total blocks: {estimate['total_blocks']:,}")
        logger.info(f"   📦 Chunks: {estimate['estimated_chunks']}")
        logger.info(f"   📡 Requests: {estimate['estimated_requests']}")
        
        logger.info("✅ Client features demo successful!")
        
    except Exception as e:
        logger.error(f"❌ Client features demo failed: {e}")


def demo_connection_testing():
    """Demonstrate connection testing functionality"""
    logger.info("=" * 60)
    logger.info("DEMO: Connection Testing")
    logger.info("=" * 60)
    
    try:
        from qaa_analysis.contract_universe import test_connection
        
        # Test a few different connection scenarios
        test_urls = [
            "https://mainnet.infura.io/v3/invalid_key",  # Should fail
            "https://invalid.rpc.url/",                  # Should fail
            os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY")  # Might work
        ]
        
        for i, url in enumerate(test_urls, 1):
            logger.info(f"🧪 Test {i}: {url[:50]}{'...' if len(url) > 50 else ''}")
            
            start_time = time.time()
            result = test_connection(url)
            elapsed = time.time() - start_time
            
            if result["connected"]:
                logger.info(f"   ✅ Connected in {elapsed:.2f}s")
                logger.info(f"   🏗️  Block: {result.get('current_block', 'N/A')}")
                logger.info(f"   ⛓️  Chain: {result.get('chain_id', 'N/A')}")
            else:
                logger.info(f"   ❌ Failed in {elapsed:.2f}s")
                logger.info(f"   🚫 Error: {result.get('error', 'Unknown')}")
            
            logger.info("")  # Empty line for readability
        
        logger.info("✅ Connection testing complete!")
        
    except Exception as e:
        logger.error(f"❌ Connection testing failed: {e}")


def demo_validation_errors():
    """Demonstrate configuration validation"""
    logger.info("=" * 60)
    logger.info("DEMO: Validation Errors")
    logger.info("=" * 60)
    
    try:
        from qaa_analysis.contract_universe import (
            create_ethereum_config,
            create_factory_config
        )
        
        # Test Ethereum config validation errors
        logger.info("🧪 Testing Ethereum config validation:")
        
        test_cases = [
            ("Empty RPC URL", {"rpc_url": ""}),
            ("Zero chunk size", {"rpc_url": "https://test.rpc/", "chunk_size": 0}),
            ("Negative retries", {"rpc_url": "https://test.rpc/", "max_retries": -1}),
            ("Zero timeout", {"rpc_url": "https://test.rpc/", "request_timeout": 0})
        ]
        
        for test_name, kwargs in test_cases:
            try:
                create_ethereum_config(**kwargs)
                logger.info(f"   ❌ {test_name}: Should have failed!")
            except ValueError as e:
                logger.info(f"   ✅ {test_name}: {e}")
        
        # Test Factory config validation errors
        logger.info("🧪 Testing Factory config validation:")
        
        factory_test_cases = [
            ("Empty protocol", {"protocol": "", "factory_address": "0x1234567890123456789012345678901234567890", 
                              "event_topic": "0x1234567890123456789012345678901234567890123456789012345678901234",
                              "child_slot_index": 0, "creation_block": 1000, "category": "Test"}),
            ("Invalid address", {"protocol": "Test", "factory_address": "0x123", 
                               "event_topic": "0x1234567890123456789012345678901234567890123456789012345678901234",
                               "child_slot_index": 0, "creation_block": 1000, "category": "Test"}),
            ("Invalid topic", {"protocol": "Test", "factory_address": "0x1234567890123456789012345678901234567890", 
                             "event_topic": "0x123", "child_slot_index": 0, "creation_block": 1000, "category": "Test"})
        ]
        
        for test_name, kwargs in factory_test_cases:
            try:
                create_factory_config(**kwargs)
                logger.info(f"   ❌ {test_name}: Should have failed!")
            except ValueError as e:
                logger.info(f"   ✅ {test_name}: {e}")
        
        logger.info("✅ Validation testing complete!")
        
    except Exception as e:
        logger.error(f"❌ Validation testing failed: {e}")


def main():
    """Run all Phase 1 demonstrations"""
    logger.info("🚀 Starting Phase 1 Contract Universe Demo")
    logger.info("📋 This demo showcases infrastructure setup and configuration management")
    logger.info("")
    
    # Run all demonstrations
    demo_quick_setup()
    logger.info("")
    
    demo_custom_configuration()
    logger.info("")
    
    demo_default_configurations()
    logger.info("")
    
    demo_client_features()
    logger.info("")
    
    demo_connection_testing()
    logger.info("")
    
    demo_validation_errors()
    logger.info("")
    
    logger.info("🎉 Phase 1 demo complete!")
    logger.info("📋 Next: Implement Phase 2 (Contract Discovery Engine)")


if __name__ == "__main__":
    main() 