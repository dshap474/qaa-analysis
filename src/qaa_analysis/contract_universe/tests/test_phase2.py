"""
Phase 2 Tests: Volume-Filtered Contract Discovery
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/tests/test_phase2.py
---
Comprehensive tests for the volume-filtered discovery system including
API integrations, factory discovery, and coverage calculations.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from ..config import FactoryConfig, EthereumConfig
from ..eth_client import EthereumClient
from ..volume_discovery import (
    PoolVolumeData,
    VolumeThreshold,
    VolumeDataProvider,
    FactoryDiscovery,
    VolumeCoverageCalculator,
    VolumeFilteredDiscovery,
    quick_volume_discovery
)


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Fixtures                                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘

@pytest.fixture
def mock_eth_client():
    """Mock Ethereum client for testing"""
    client = Mock(spec=EthereumClient)
    client.to_checksum_address.side_effect = lambda x: x.lower()
    client.get_current_block.return_value = 19000000
    client.get_logs_with_retry.return_value = []
    client.w3 = Mock()
    return client

@pytest.fixture
def sample_factory_config():
    """Sample factory configuration for testing"""
    return FactoryConfig(
        protocol="Test Protocol",
        factory_address="0x1234567890123456789012345678901234567890",
        event_topic="0xabcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
        child_slot_index=2,
        creation_block=12345678,
        category="DEX Pool"
    )

@pytest.fixture
def sample_pools_data():
    """Sample pools data for testing"""
    return [
        {
            "address": "0x1111111111111111111111111111111111111111",
            "protocol": "Test Protocol",
            "category": "DEX Pool",
            "creation_block": 12345680,
            "factory_index": 0
        },
        {
            "address": "0x2222222222222222222222222222222222222222",
            "protocol": "Test Protocol",
            "category": "DEX Pool",
            "creation_block": 12345681,
            "factory_index": 1
        }
    ]

@pytest.fixture
def sample_volume_data():
    """Sample volume data for testing"""
    return [
        PoolVolumeData(
            address="0x1111111111111111111111111111111111111111",
            protocol="Test Protocol",
            category="DEX Pool",
            volume_180d=1000000.0,
            tvl_current=500000.0,
            token0_address="0xtoken0",
            token1_address="0xtoken1",
            token0_symbol="TOKEN0",
            token1_symbol="TOKEN1",
            creation_block=12345680,
            volume_24h=5555.0,
            volume_7d=38888.0
        ),
        PoolVolumeData(
            address="0x2222222222222222222222222222222222222222",
            protocol="Test Protocol",
            category="DEX Pool",
            volume_180d=500000.0,
            tvl_current=250000.0,
            token0_address="0xtoken2",
            token1_address="0xtoken3",
            token0_symbol="TOKEN2",
            token1_symbol="TOKEN3",
            creation_block=12345681,
            volume_24h=2777.0,
            volume_7d=19444.0
        )
    ]


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Data Model Tests                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestPoolVolumeData:
    """Test PoolVolumeData data class"""
    
    def test_pool_volume_data_creation(self):
        """Test creating PoolVolumeData instance"""
        pool = PoolVolumeData(
            address="0x1234567890123456789012345678901234567890",
            protocol="Uniswap V2",
            category="DEX Pool",
            volume_180d=1000000.0,
            tvl_current=500000.0,
            token0_address="0xtoken0",
            token1_address="0xtoken1",
            token0_symbol="USDC",
            token1_symbol="WETH",
            creation_block=12345678
        )
        
        assert pool.address == "0x1234567890123456789012345678901234567890"
        assert pool.protocol == "Uniswap V2"
        assert pool.volume_180d == 1000000.0
        assert pool.token0_symbol == "USDC"
        assert pool.token1_symbol == "WETH"
    
    def test_to_dict_conversion(self):
        """Test converting PoolVolumeData to dictionary"""
        pool = PoolVolumeData(
            address="0x1234567890123456789012345678901234567890",
            protocol="Uniswap V2",
            category="DEX Pool",
            volume_180d=1000000.0,
            tvl_current=500000.0,
            token0_address="0xtoken0",
            token1_address="0xtoken1",
            token0_symbol="USDC",
            token1_symbol="WETH",
            creation_block=12345678
        )
        
        data_dict = pool.to_dict()
        assert isinstance(data_dict, dict)
        assert data_dict["address"] == pool.address
        assert data_dict["volume_180d"] == pool.volume_180d

class TestVolumeThreshold:
    """Test VolumeThreshold data class"""
    
    def test_volume_threshold_creation(self):
        """Test creating VolumeThreshold instance"""
        threshold = VolumeThreshold(
            pools_needed=100,
            volume_threshold=10000.0,
            actual_coverage=0.905,
            total_volume_180d=1000000.0,
            coverage_volume=905000.0,
            target_coverage=0.90
        )
        
        assert threshold.pools_needed == 100
        assert threshold.actual_coverage == 0.905
        assert threshold.target_coverage == 0.90


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Volume Data Provider Tests                                                         │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestVolumeDataProvider:
    """Test VolumeDataProvider class"""
    
    def test_volume_data_provider_init(self):
        """Test VolumeDataProvider initialization"""
        provider = VolumeDataProvider(request_timeout=15)
        
        assert provider.timeout == 15
        assert "Uniswap V2" in provider.thegraph_endpoints
        assert "https://api.llama.fi" in provider.defillama_url
    
    @patch('requests.Session.post')
    def test_get_volume_from_graph_success(self, mock_post):
        """Test successful Graph API query"""
        # Mock successful Graph response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "pair": {
                    "id": "0x1234567890123456789012345678901234567890",
                    "volumeUSD": "1000000",
                    "reserveUSD": "500000",
                    "token0": {"id": "0xtoken0", "symbol": "USDC", "decimals": "6"},
                    "token1": {"id": "0xtoken1", "symbol": "WETH", "decimals": "18"},
                    "dayData": [
                        {"date": "1609459200", "dailyVolumeUSD": "5555.0"},
                        {"date": "1609372800", "dailyVolumeUSD": "4444.0"}
                    ]
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        provider = VolumeDataProvider()
        result = provider._get_volume_from_graph(
            "0x1234567890123456789012345678901234567890", 
            "Uniswap V2"
        )
        
        assert result is not None
        assert result["token0_symbol"] == "USDC"
        assert result["token1_symbol"] == "WETH"
        assert result["volume_180d"] == 9999.0  # Sum of dayData
    
    @patch('requests.Session.get')
    def test_get_volume_from_defillama_success(self, mock_get):
        """Test successful DeFiLlama API query"""
        # Mock successful DeFiLlama response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "volume180d": 1000000.0,
                "tvl": 500000.0,
                "token0": {"address": "0xtoken0", "symbol": "USDC"},
                "token1": {"address": "0xtoken1", "symbol": "WETH"},
                "volume24h": 5555.0,
                "volume7d": 38888.0
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        provider = VolumeDataProvider()
        result = provider._get_volume_from_defillama(
            "0x1234567890123456789012345678901234567890",
            "Uniswap V2"
        )
        
        assert result is not None
        assert result["volume_180d"] == 1000000.0
        assert result["volume_24h"] == 5555.0
    
    def test_get_mock_volume_data(self):
        """Test mock volume data generation"""
        provider = VolumeDataProvider()
        result = provider._get_mock_volume_data(
            "0x1234567890123456789012345678901234567890",
            "Test Protocol"
        )
        
        assert isinstance(result, dict)
        assert "volume_180d" in result
        assert "tvl_current" in result
        assert "token0_symbol" in result
        assert "token1_symbol" in result
        assert result["token1_symbol"] == "WETH"


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Factory Discovery Tests                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestFactoryDiscovery:
    """Test FactoryDiscovery class"""
    
    def test_factory_discovery_init(self, mock_eth_client, sample_factory_config):
        """Test FactoryDiscovery initialization"""
        discovery = FactoryDiscovery(mock_eth_client, [sample_factory_config])
        
        assert discovery.client == mock_eth_client
        assert len(discovery.factory_configs) == 1
        assert "Uniswap V2" in discovery.factory_abis
    
    def test_discover_pool_addresses(self, mock_eth_client, sample_factory_config):
        """Test pool address discovery"""
        discovery = FactoryDiscovery(mock_eth_client, [sample_factory_config])
        
        # Mock the discovery methods to return test data
        with patch.object(discovery, '_discover_via_events') as mock_events:
            mock_events.return_value = [
                {
                    "address": "0x1111111111111111111111111111111111111111",
                    "protocol": "Test Protocol",
                    "category": "DEX Pool",
                    "creation_block": 12345680
                }
            ]
            
            pools = discovery.discover_pool_addresses()
            
            assert len(pools) == 1
            assert pools[0]["address"] == "0x1111111111111111111111111111111111111111"
    
    def test_extract_pool_address_from_log(self, mock_eth_client, sample_factory_config):
        """Test extracting pool address from event log"""
        discovery = FactoryDiscovery(mock_eth_client, [sample_factory_config])
        
        # Mock event log with pool address in topics[2]
        mock_log = {
            "topics": [
                "0xeventtopic",
                "0xtoken0topic",
                "0x0000000000000000000000001234567890123456789012345678901234567890",  # pool address
                "0xothertopic"
            ],
            "data": "0x1234567890abcdef"
        }
        
        pool_address = discovery._extract_pool_address_from_log(mock_log, sample_factory_config)
        
        assert pool_address == "0x1234567890123456789012345678901234567890"
    
    def test_mock_discover_pools(self, mock_eth_client, sample_factory_config):
        """Test mock pool discovery fallback"""
        discovery = FactoryDiscovery(mock_eth_client, [sample_factory_config])
        
        pools = discovery._mock_discover_pools(sample_factory_config)
        
        assert len(pools) == 20  # Should generate 20 mock pools
        assert all(pool["protocol"] == "Test Protocol" for pool in pools)
        assert all(pool["is_mock"] for pool in pools)


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Volume Coverage Calculator Tests                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestVolumeCoverageCalculator:
    """Test VolumeCoverageCalculator class"""
    
    def test_coverage_calculator_init(self):
        """Test VolumeCoverageCalculator initialization"""
        calculator = VolumeCoverageCalculator(target_coverage=0.95)
        
        assert calculator.target_coverage == 0.95
    
    def test_calculate_coverage_threshold(self, sample_volume_data):
        """Test volume coverage threshold calculation"""
        calculator = VolumeCoverageCalculator(target_coverage=0.90)
        
        result = calculator.calculate_coverage_threshold(sample_volume_data)
        
        assert isinstance(result, VolumeThreshold)
        assert result.target_coverage == 0.90
        assert result.pools_needed >= 1
        assert result.actual_coverage >= 0.90
        assert result.total_volume_180d == 1500000.0  # Sum of sample volumes
    
    def test_calculate_coverage_threshold_empty_list(self):
        """Test coverage calculation with empty pool list"""
        calculator = VolumeCoverageCalculator(target_coverage=0.90)
        
        result = calculator.calculate_coverage_threshold([])
        
        assert result.pools_needed == 0
        assert result.total_volume_180d == 0
        assert result.actual_coverage == 1.0
    
    def test_calculate_coverage_single_pool_exceeds_target(self):
        """Test coverage calculation when single pool exceeds target"""
        calculator = VolumeCoverageCalculator(target_coverage=0.50)
        
        pools = [
            PoolVolumeData(
                address="0x1111111111111111111111111111111111111111",
                protocol="Test",
                category="DEX Pool",
                volume_180d=1000000.0,
                tvl_current=500000.0,
                token0_address="0xtoken0",
                token1_address="0xtoken1",
                token0_symbol="TOKEN0",
                token1_symbol="TOKEN1",
                creation_block=12345680
            )
        ]
        
        result = calculator.calculate_coverage_threshold(pools)
        
        assert result.pools_needed == 1
        assert result.actual_coverage == 1.0


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Volume Filtered Discovery Tests                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestVolumeFilteredDiscovery:
    """Test VolumeFilteredDiscovery main class"""
    
    def test_volume_filtered_discovery_init(self, mock_eth_client, sample_factory_config):
        """Test VolumeFilteredDiscovery initialization"""
        discovery = VolumeFilteredDiscovery(
            eth_client=mock_eth_client,
            factory_configs=[sample_factory_config],
            target_coverage=0.85,
            max_workers=2
        )
        
        assert discovery.client == mock_eth_client
        assert discovery.target_coverage == 0.85
        assert discovery.max_workers == 2
        assert len(discovery.factory_configs) == 1
    
    def test_enrich_with_volume_data(self, mock_eth_client, sample_pools_data):
        """Test volume data enrichment"""
        discovery = VolumeFilteredDiscovery(eth_client=mock_eth_client)
        
        # Mock the volume provider
        with patch.object(discovery.volume_provider, 'get_180d_volume') as mock_volume:
            mock_volume.return_value = {
                "volume_180d": 1000000.0,
                "tvl_current": 500000.0,
                "token0_address": "0xtoken0",
                "token1_address": "0xtoken1",
                "token0_symbol": "TOKEN0",
                "token1_symbol": "TOKEN1",
                "volume_24h": 5555.0,
                "volume_7d": 38888.0
            }
            
            enriched_pools = discovery.enrich_with_volume_data(sample_pools_data)
            
            assert len(enriched_pools) == 2
            assert all(isinstance(pool, PoolVolumeData) for pool in enriched_pools)
            assert enriched_pools[0].volume_180d == 1000000.0
    
    def test_discover_with_volume_filter_integration(self, mock_eth_client, sample_factory_config):
        """Test full discovery pipeline integration"""
        discovery = VolumeFilteredDiscovery(
            eth_client=mock_eth_client,
            factory_configs=[sample_factory_config],
            target_coverage=0.90
        )
        
        # Mock all the components
        with patch.object(discovery.factory_discovery, 'discover_pool_addresses') as mock_factory:
            with patch.object(discovery, 'enrich_with_volume_data') as mock_enrich:
                with patch.object(discovery.coverage_calculator, 'calculate_coverage_threshold') as mock_coverage:
                    
                    # Setup mocks
                    mock_factory.return_value = [{"address": "0x1111", "protocol": "Test"}]
                    mock_enrich.return_value = [
                        PoolVolumeData(
                            address="0x1111",
                            protocol="Test",
                            category="DEX Pool",
                            volume_180d=1000000.0,
                            tvl_current=500000.0,
                            token0_address="0xtoken0",
                            token1_address="0xtoken1",
                            token0_symbol="TOKEN0",
                            token1_symbol="TOKEN1",
                            creation_block=12345680
                        )
                    ]
                    mock_coverage.return_value = VolumeThreshold(
                        pools_needed=1,
                        volume_threshold=1000000.0,
                        actual_coverage=1.0,
                        total_volume_180d=1000000.0,
                        coverage_volume=1000000.0,
                        target_coverage=0.90
                    )
                    
                    # Run discovery
                    result = discovery.discover_with_volume_filter()
                    
                    assert len(result) == 1
                    assert result[0].address == "0x1111"


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Integration and Utility Function Tests                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestUtilityFunctions:
    """Test utility functions and integration"""
    
    @patch('qaa_analysis.contract_universe.volume_discovery.EthereumClient')
    def test_quick_volume_discovery(self, mock_client_class):
        """Test quick_volume_discovery function"""
        # Mock the EthereumClient and VolumeFilteredDiscovery
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        with patch('qaa_analysis.contract_universe.volume_discovery.VolumeFilteredDiscovery') as mock_discovery_class:
            mock_discovery = Mock()
            mock_discovery.discover_with_volume_filter.return_value = []
            mock_discovery_class.return_value = mock_discovery
            
            result = quick_volume_discovery(
                eth_rpc_url="https://test.rpc.url",
                target_coverage=0.95,
                protocols=["Uniswap V2"]
            )
            
            assert isinstance(result, list)
            mock_discovery.discover_with_volume_filter.assert_called_once()


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Error Handling and Edge Cases                                                      │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_volume_provider_network_error(self):
        """Test handling of network errors in volume provider"""
        provider = VolumeDataProvider()
        
        with patch('requests.Session.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            # Should fall back to mock data
            result = provider.get_180d_volume(
                "0x1234567890123456789012345678901234567890",
                "Uniswap V2"
            )
            
            assert result is not None  # Should get mock data
            assert "volume_180d" in result
    
    def test_factory_discovery_contract_error(self, mock_eth_client, sample_factory_config):
        """Test handling of contract interaction errors"""
        discovery = FactoryDiscovery(mock_eth_client, [sample_factory_config])
        
        # Mock client methods to raise errors (for events discovery path)
        mock_eth_client.get_current_block.side_effect = Exception("RPC error")
        mock_eth_client.get_logs_with_retry.side_effect = Exception("Logs error")
        
        # Should fall back to mock data
        pools = discovery.discover_pool_addresses()
        
        assert len(pools) > 0  # Should get mock data
        assert all(pool.get("is_mock") for pool in pools)
    
    def test_invalid_log_format(self, mock_eth_client, sample_factory_config):
        """Test handling of invalid event log formats"""
        discovery = FactoryDiscovery(mock_eth_client, [sample_factory_config])
        
        # Test with malformed log
        malformed_log = {
            "topics": ["0xshort"],  # Too short
            "data": "0xinvalid"
        }
        
        result = discovery._extract_pool_address_from_log(malformed_log, sample_factory_config)
        
        assert result is None


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Performance and Load Tests                                                         │
# └────────────────────────────────────────────────────────────────────────────────────┘

class TestPerformance:
    """Test performance characteristics"""
    
    def test_large_pool_set_processing(self):
        """Test processing large numbers of pools"""
        calculator = VolumeCoverageCalculator()
        
        # Generate large dataset
        large_pool_set = []
        for i in range(1000):
            large_pool_set.append(
                PoolVolumeData(
                    address=f"0x{i:040x}",
                    protocol="Test",
                    category="DEX Pool",
                    volume_180d=1000000.0 / (i + 1),  # Decreasing volume
                    tvl_current=500000.0,
                    token0_address="0xtoken0",
                    token1_address="0xtoken1",
                    token0_symbol="TOKEN0",
                    token1_symbol="TOKEN1",
                    creation_block=12345680 + i
                )
            )
        
        result = calculator.calculate_coverage_threshold(large_pool_set)
        
        assert result.pools_needed > 0
        assert result.pools_needed <= len(large_pool_set)
        assert 0 <= result.actual_coverage <= 1.0


def test_phase2_integration():
    """High-level integration test for Phase 2"""
    
    # Test that all components can be imported and instantiated
    from ..volume_discovery import (
        VolumeFilteredDiscovery,
        VolumeDataProvider,
        FactoryDiscovery,
        VolumeCoverageCalculator
    )
    
    # Mock components should work together
    mock_client = Mock()
    mock_client.to_checksum_address.side_effect = lambda x: x
    
    factory_config = FactoryConfig(
        protocol="Test",
        factory_address="0x1234567890123456789012345678901234567890",
        event_topic="0xabcdef",
        child_slot_index=2,
        creation_block=12345678,
        category="DEX Pool"
    )
    
    # Should be able to create all components without errors
    provider = VolumeDataProvider()
    factory_discovery = FactoryDiscovery(mock_client, [factory_config])
    calculator = VolumeCoverageCalculator()
    discovery = VolumeFilteredDiscovery(
        eth_client=mock_client,
        factory_configs=[factory_config]
    )
    
    assert provider is not None
    assert factory_discovery is not None
    assert calculator is not None
    assert discovery is not None
