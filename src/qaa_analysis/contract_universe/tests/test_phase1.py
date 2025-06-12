# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Phase 1 Tests - Infrastructure Setup                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Phase 1 Tests
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/tests/test_phase1.py
---
Comprehensive tests for Phase 1 infrastructure components including configuration
management and Ethereum client functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch

from ..config import (
    EthereumConfig,
    FactoryConfig,
    DEFAULT_ETH_CONFIG,
    DEFAULT_FACTORY_CONFIGS,
    validate_ethereum_config,
    validate_factory_config,
    create_ethereum_config,
    create_factory_config
)

from ..eth_client import (
    EthereumClient,
    EthereumClientError,
    create_ethereum_client,
    create_default_client,
    test_connection
)


class TestEthereumConfig:
    """Test EthereumConfig class and validation"""
    
    def test_default_config_creation(self):
        """Test creating config with default values"""
        config = EthereumConfig(rpc_url="https://mainnet.infura.io/v3/test")
        
        assert config.rpc_url == "https://mainnet.infura.io/v3/test"
        assert config.archive_node_url is None
        assert config.chunk_size == 5000
        assert config.max_retries == 3
        assert config.request_timeout == 30
    
    def test_custom_config_creation(self):
        """Test creating config with custom values"""
        config = EthereumConfig(
            rpc_url="https://custom.rpc/",
            archive_node_url="https://archive.rpc/",
            chunk_size=1000,
            max_retries=5,
            request_timeout=60
        )
        
        assert config.rpc_url == "https://custom.rpc/"
        assert config.archive_node_url == "https://archive.rpc/"
        assert config.chunk_size == 1000
        assert config.max_retries == 5
        assert config.request_timeout == 60
    
    def test_validate_ethereum_config_valid(self):
        """Test validation with valid config"""
        config = EthereumConfig(rpc_url="https://test.rpc/")
        assert validate_ethereum_config(config) is True
    
    def test_validate_ethereum_config_empty_url(self):
        """Test validation fails with empty RPC URL"""
        config = EthereumConfig(rpc_url="")
        
        with pytest.raises(ValueError, match="RPC URL is required"):
            validate_ethereum_config(config)
    
    def test_validate_ethereum_config_invalid_chunk_size(self):
        """Test validation fails with invalid chunk size"""
        config = EthereumConfig(rpc_url="https://test.rpc/", chunk_size=0)
        
        with pytest.raises(ValueError, match="Chunk size must be positive"):
            validate_ethereum_config(config)
    
    def test_validate_ethereum_config_negative_retries(self):
        """Test validation fails with negative retries"""
        config = EthereumConfig(rpc_url="https://test.rpc/", max_retries=-1)
        
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            validate_ethereum_config(config)
    
    def test_validate_ethereum_config_invalid_timeout(self):
        """Test validation fails with invalid timeout"""
        config = EthereumConfig(rpc_url="https://test.rpc/", request_timeout=0)
        
        with pytest.raises(ValueError, match="Request timeout must be positive"):
            validate_ethereum_config(config)


class TestFactoryConfig:
    """Test FactoryConfig class and validation"""
    
    def test_factory_config_creation(self):
        """Test creating factory config"""
        config = FactoryConfig(
            protocol="Test Protocol",
            factory_address="0x1234567890123456789012345678901234567890",
            event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
            child_slot_index=1,
            creation_block=1000,
            category="Test Category"
        )
        
        assert config.protocol == "Test Protocol"
        assert config.factory_address == "0x1234567890123456789012345678901234567890"
        assert config.event_topic == "0x1234567890123456789012345678901234567890123456789012345678901234"
        assert config.child_slot_index == 1
        assert config.creation_block == 1000
        assert config.category == "Test Category"
    
    def test_validate_factory_config_valid(self):
        """Test validation with valid factory config"""
        config = FactoryConfig(
            protocol="Test",
            factory_address="0x1234567890123456789012345678901234567890",
            event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
            child_slot_index=0,
            creation_block=1000,
            category="Test"
        )
        
        assert validate_factory_config(config) is True
    
    def test_validate_factory_config_empty_protocol(self):
        """Test validation fails with empty protocol"""
        config = FactoryConfig(
            protocol="",
            factory_address="0x1234567890123456789012345678901234567890",
            event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
            child_slot_index=0,
            creation_block=1000,
            category="Test"
        )
        
        with pytest.raises(ValueError, match="Protocol name is required"):
            validate_factory_config(config)
    
    def test_validate_factory_config_invalid_address(self):
        """Test validation fails with invalid address"""
        config = FactoryConfig(
            protocol="Test",
            factory_address="0x123",  # Too short
            event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
            child_slot_index=0,
            creation_block=1000,
            category="Test"
        )
        
        with pytest.raises(ValueError, match="Valid factory address is required"):
            validate_factory_config(config)
    
    def test_validate_factory_config_invalid_topic(self):
        """Test validation fails with invalid event topic"""
        config = FactoryConfig(
            protocol="Test",
            factory_address="0x1234567890123456789012345678901234567890",
            event_topic="0x123",  # Too short
            child_slot_index=0,
            creation_block=1000,
            category="Test"
        )
        
        with pytest.raises(ValueError, match="Valid event topic is required"):
            validate_factory_config(config)


class TestFactoryFunctions:
    """Test configuration factory functions"""
    
    def test_create_ethereum_config(self):
        """Test creating Ethereum config with factory function"""
        config = create_ethereum_config(
            rpc_url="https://test.rpc/",
            chunk_size=2000
        )
        
        assert isinstance(config, EthereumConfig)
        assert config.rpc_url == "https://test.rpc/"
        assert config.chunk_size == 2000
    
    def test_create_ethereum_config_validation_error(self):
        """Test factory function validates config"""
        with pytest.raises(ValueError):
            create_ethereum_config(rpc_url="")
    
    def test_create_factory_config(self):
        """Test creating factory config with factory function"""
        config = create_factory_config(
            protocol="Test",
            factory_address="0x1234567890123456789012345678901234567890",
            event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
            child_slot_index=0,
            creation_block=1000,
            category="Test"
        )
        
        assert isinstance(config, FactoryConfig)
        assert config.protocol == "Test"
    
    def test_create_factory_config_validation_error(self):
        """Test factory function validates config"""
        with pytest.raises(ValueError):
            create_factory_config(
                protocol="",  # Invalid
                factory_address="0x1234567890123456789012345678901234567890",
                event_topic="0x1234567890123456789012345678901234567890123456789012345678901234",
                child_slot_index=0,
                creation_block=1000,
                category="Test"
            )


class TestDefaultConfigs:
    """Test default configuration values"""
    
    def test_default_eth_config_exists(self):
        """Test that default Ethereum config exists and is valid"""
        assert isinstance(DEFAULT_ETH_CONFIG, EthereumConfig)
        assert DEFAULT_ETH_CONFIG.rpc_url
        assert DEFAULT_ETH_CONFIG.chunk_size > 0
    
    def test_default_factory_configs_exist(self):
        """Test that default factory configs exist and are valid"""
        assert isinstance(DEFAULT_FACTORY_CONFIGS, list)
        assert len(DEFAULT_FACTORY_CONFIGS) > 0
        
        for config in DEFAULT_FACTORY_CONFIGS:
            assert isinstance(config, FactoryConfig)
            assert config.protocol
            assert config.factory_address
            assert config.event_topic
    
    def test_default_factory_configs_protocols(self):
        """Test that expected protocols are in default configs"""
        protocols = [config.protocol for config in DEFAULT_FACTORY_CONFIGS]
        
        assert "Uniswap V2" in protocols
        assert "Uniswap V3" in protocols
        assert "Curve CryptoSwap" in protocols


class TestEthereumClient:
    """Test EthereumClient class (mocked)"""
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_client_initialization_success(self, mock_web3):
        """Test successful client initialization"""
        # Mock Web3 instance
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://test.rpc/")
        client = EthereumClient(config)
        
        assert client.config == config
        assert client.w3 == mock_w3_instance
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_client_initialization_failure(self, mock_web3):
        """Test client initialization failure"""
        # Mock Web3 instance that fails to connect
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = False
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://invalid.rpc/")
        
        with pytest.raises(EthereumClientError, match="Failed to connect"):
            EthereumClient(config)
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_get_current_block(self, mock_web3):
        """Test getting current block number"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.block_number = 18500000
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://test.rpc/")
        client = EthereumClient(config)
        
        assert client.get_current_block() == 18500000
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_get_current_block_error(self, mock_web3):
        """Test error handling when getting current block"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.block_number = Mock(side_effect=Exception("Network error"))
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://test.rpc/")
        client = EthereumClient(config)
        
        with pytest.raises(EthereumClientError, match="Failed to get current block number"):
            client.get_current_block()
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_validate_address(self, mock_web3):
        """Test address validation"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.to_checksum_address = Mock(return_value="0x1234567890123456789012345678901234567890")
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://test.rpc/")
        client = EthereumClient(config)
        
        assert client.validate_address("0x1234567890123456789012345678901234567890") is True
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_validate_address_invalid(self, mock_web3):
        """Test invalid address validation"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.to_checksum_address = Mock(side_effect=Exception("Invalid address"))
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://test.rpc/")
        client = EthereumClient(config)
        
        assert client.validate_address("invalid_address") is False


class TestFactoryFunctionsEthClient:
    """Test Ethereum client factory functions"""
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_create_ethereum_client(self, mock_web3):
        """Test creating client with factory function"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_web3.return_value = mock_w3_instance
        
        config = EthereumConfig(rpc_url="https://test.rpc/")
        client = create_ethereum_client(config)
        
        assert isinstance(client, EthereumClient)
        assert client.config == config
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_create_default_client(self, mock_web3):
        """Test creating client with defaults"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_web3.return_value = mock_w3_instance
        
        client = create_default_client("https://test.rpc/")
        
        assert isinstance(client, EthereumClient)
        assert client.config.rpc_url == "https://test.rpc/"
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_test_connection_success(self, mock_web3):
        """Test connection test function success"""
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.block_number = 18500000
        mock_w3_instance.eth.chain_id = 1
        mock_web3.return_value = mock_w3_instance
        
        result = test_connection("https://test.rpc/")
        
        assert result["connected"] is True
        assert result["current_block"] == 18500000
        assert result["chain_id"] == 1
    
    def test_test_connection_failure(self):
        """Test connection test function failure"""
        result = test_connection("https://invalid.rpc/")
        
        assert result["connected"] is False
        assert "error" in result


class TestModuleIntegration:
    """Test module-level integration"""
    
    @patch('qaa_analysis.contract_universe.eth_client.Web3')
    def test_full_workflow(self, mock_web3):
        """Test a complete workflow using the module"""
        # Mock Web3
        mock_w3_instance = Mock()
        mock_w3_instance.is_connected.return_value = True
        mock_w3_instance.eth.block_number = 18500000
        mock_web3.return_value = mock_w3_instance
        
        # Import the module
        from qaa_analysis.contract_universe import quick_setup, get_module_info
        
        # Test quick setup
        client = quick_setup("https://test.rpc/")
        assert isinstance(client, EthereumClient)
        
        # Test module info
        info = get_module_info()
        assert info["name"] == "contract_universe"
        assert "phase" in info
        assert "components" in info


if __name__ == "__main__":
    pytest.main([__file__]) 