# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Phase 3: Action Mapping System Tests                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Test Suite for Action Mapping System
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/test_phase3.py
---
Comprehensive test suite for the Action Mapping System, covering function/event
signature databases, transaction decoding, event log decoding, and action mapping.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from web3 import Web3
from web3.types import TxReceipt, LogReceipt

from action_mapping import (
    ActionType, FunctionSignature, EventSignature, UserAction,
    SignatureDatabase, TransactionDecoder, EventLogDecoder, ActionMapper,
    ActionAnalyzer, PROTOCOL_CONTRACTS, FUNCTION_SIGNATURES, EVENT_SIGNATURES,
    create_action_mapper, calculate_function_selector, calculate_event_topic0,
    quick_action_mapping
)

# ═══════════════════════════════════════════════════════════════════════════════════════
# Test Data and Fixtures
# ═══════════════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_web3():
    """Create a mock Web3 instance for testing"""
    web3 = Mock(spec=Web3)
    web3.eth = Mock()
    return web3

@pytest.fixture
def signature_db():
    """Create a SignatureDatabase instance for testing"""
    return SignatureDatabase()

@pytest.fixture
def sample_function_signature():
    """Sample function signature for testing"""
    return FunctionSignature(
        name="testFunction",
        signature="testFunction(uint256,address)",
        selector="0x12345678",
        action_type=ActionType.SWAP,
        protocol="Test Protocol",
        description="Test function for unit tests"
    )

@pytest.fixture
def sample_event_signature():
    """Sample event signature for testing"""
    return EventSignature(
        name="TestEvent",
        signature="TestEvent(address indexed user, uint256 amount)",
        topic0="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        action_type=ActionType.SUPPLY,
        protocol="Test Protocol",
        indexed_params=["user"],
        data_params=["amount"],
        description="Test event for unit tests"
    )

@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing"""
    return {
        'hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12',
        'from': '0x742d35Cc6620C0532895041e1c6Ec83a0CD5a86A',
        'to': '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',
        'input': '0x38ed1739000000000000000000000000000000000000000000000000000000000000007b',
        'value': 0,
        'gasPrice': 20000000000,
        'blockNumber': 18500000
    }

@pytest.fixture
def sample_receipt():
    """Sample transaction receipt for testing"""
    return {
        'transactionHash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12',
        'blockNumber': 18500000,
        'gasUsed': 150000,
        'status': 1,
        'logs': [
            {
                'address': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                'topics': [
                    '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822',
                    '0x0000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d',
                    '0x000000000000000000000000742d35Cc6620C0532895041e1c6Ec83a0CD5a86A'
                ],
                'data': '0x0000000000000000000000000000000000000000000000000000000000000000',
                'blockNumber': 18500000,
                'transactionHash': '0x1234567890abcdef',
                'logIndex': 0
            }
        ]
    }

@pytest.fixture
def sample_block():
    """Sample block data for testing"""
    return {
        'number': 18500000,
        'timestamp': 1700000000,
        'hash': '0xblockhash1234567890abcdef1234567890abcdef1234567890abcdef1234567890'
    }

# ═══════════════════════════════════════════════════════════════════════════════════════
# SignatureDatabase Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestSignatureDatabase:
    """Test cases for SignatureDatabase"""
    
    def test_database_initialization(self, signature_db):
        """Test that database loads default signatures correctly"""
        # Should have loaded default function and event signatures
        assert len(signature_db.function_signatures) > 0
        assert len(signature_db.event_signatures) > 0
        
        # Check that known signatures are loaded
        uniswap_swap_selector = "0x38ed1739"
        assert uniswap_swap_selector in signature_db.function_signatures
        
        uniswap_swap_topic = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
        assert uniswap_swap_topic in signature_db.event_signatures
    
    def test_add_custom_function_signature(self, signature_db, sample_function_signature):
        """Test adding custom function signatures"""
        initial_count = len(signature_db.function_signatures)
        
        signature_db.add_function_signature(sample_function_signature)
        
        assert len(signature_db.function_signatures) == initial_count + 1
        assert signature_db.function_signatures[sample_function_signature.selector] == sample_function_signature
    
    def test_add_custom_event_signature(self, signature_db, sample_event_signature):
        """Test adding custom event signatures"""
        initial_count = len(signature_db.event_signatures)
        
        signature_db.add_event_signature(sample_event_signature)
        
        assert len(signature_db.event_signatures) == initial_count + 1
        assert signature_db.event_signatures[sample_event_signature.topic0] == sample_event_signature
    
    def test_get_function_signature(self, signature_db):
        """Test retrieving function signatures"""
        # Test with known signature
        uniswap_swap_selector = "0x38ed1739"
        sig = signature_db.get_function_signature(uniswap_swap_selector)
        
        assert sig is not None
        assert sig.selector == uniswap_swap_selector
        assert sig.action_type == ActionType.SWAP
        assert sig.protocol == "Uniswap V2"
        
        # Test with unknown signature
        unknown_sig = signature_db.get_function_signature("0x99999999")
        assert unknown_sig is None
    
    def test_get_event_signature(self, signature_db):
        """Test retrieving event signatures"""
        # Test with known signature
        uniswap_swap_topic = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
        sig = signature_db.get_event_signature(uniswap_swap_topic)
        
        assert sig is not None
        assert sig.topic0 == uniswap_swap_topic
        assert sig.action_type == ActionType.SWAP
        assert sig.protocol == "Uniswap V2"
        
        # Test with unknown signature
        unknown_sig = signature_db.get_event_signature("0x9999999999999999999999999999999999999999999999999999999999999999")
        assert unknown_sig is None
    
    def test_list_protocols(self, signature_db):
        """Test listing supported protocols"""
        protocols = signature_db.list_protocols()
        
        assert isinstance(protocols, list)
        assert len(protocols) > 0
        assert "Uniswap V2" in protocols
        assert "Aave V3" in protocols
        assert "Lido" in protocols

# ═══════════════════════════════════════════════════════════════════════════════════════
# Data Model Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestDataModels:
    """Test cases for data models"""
    
    def test_function_signature_creation(self):
        """Test FunctionSignature creation and validation"""
        sig = FunctionSignature(
            name="swap",
            signature="swap(uint256,address)",
            selector="12345678",  # Without 0x prefix
            action_type=ActionType.SWAP,
            protocol="Test"
        )
        
        # Should auto-add 0x prefix
        assert sig.selector == "0x12345678"
        assert sig.name == "swap"
        assert sig.action_type == ActionType.SWAP
    
    def test_event_signature_creation(self):
        """Test EventSignature creation and validation"""
        sig = EventSignature(
            name="Transfer",
            signature="Transfer(address indexed from, address indexed to, uint256 value)",
            topic0="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",  # Without 0x prefix
            action_type=ActionType.STAKE_ETH,
            protocol="ERC20",
            indexed_params=["from", "to"],
            data_params=["value"]
        )
        
        # Should auto-add 0x prefix
        assert sig.topic0 == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert sig.indexed_params == ["from", "to"]
        assert sig.data_params == ["value"]
    
    def test_user_action_creation(self):
        """Test UserAction creation and serialization"""
        action = UserAction(
            transaction_hash="0x1234",
            block_number=18500000,
            timestamp=1700000000,
            user_address="0x742d35Cc6620C0532895041e1c6Ec83a0CD5a86A",
            contract_address="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
            action_type=ActionType.SWAP,
            protocol="Uniswap V2",
            token_in_address="0xA0b86a33E6417c391c62aD4c9F1B2a83D7D70a10",
            token_in_amount="1000000000000000000",
            gas_used=150000
        )
        
        assert action.action_type == ActionType.SWAP
        assert action.protocol == "Uniswap V2"
        assert action.gas_used == 150000
        
        # Test serialization
        action_dict = action.to_dict()
        assert isinstance(action_dict, dict)
        assert action_dict['action_type'] == "SWAP"
        assert action_dict['protocol'] == "Uniswap V2"
        assert action_dict['token_in_amount'] == "1000000000000000000"

# ═══════════════════════════════════════════════════════════════════════════════════════
# TransactionDecoder Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestTransactionDecoder:
    """Test cases for TransactionDecoder"""
    
    def test_decode_known_transaction(self, signature_db):
        """Test decoding transaction with known function signature"""
        decoder = TransactionDecoder(signature_db)
        
        # Uniswap V2 swapExactTokensForTokens transaction
        tx_data = {
            'input': '0x38ed1739000000000000000000000000000000000000000000000000000000000000007b'
        }
        
        result = decoder.decode_transaction_input(tx_data)
        
        assert result is not None
        assert result['selector'] == '0x38ed1739'
        assert result['function_signature'].name == 'swapExactTokensForTokens'
        assert result['function_signature'].action_type == ActionType.SWAP
        assert result['function_signature'].protocol == 'Uniswap V2'
        assert 'params_data' in result
    
    def test_decode_unknown_transaction(self, signature_db):
        """Test decoding transaction with unknown function signature"""
        decoder = TransactionDecoder(signature_db)
        
        tx_data = {
            'input': '0x99999999000000000000000000000000000000000000000000000000000000000000007b'
        }
        
        result = decoder.decode_transaction_input(tx_data)
        assert result is None
    
    def test_decode_empty_input(self, signature_db):
        """Test decoding transaction with empty input"""
        decoder = TransactionDecoder(signature_db)
        
        # Empty input
        result = decoder.decode_transaction_input({'input': '0x'})
        assert result is None
        
        # No input field
        result = decoder.decode_transaction_input({})
        assert result is None
        
        # Too short input
        result = decoder.decode_transaction_input({'input': '0x1234'})
        assert result is None

# ═══════════════════════════════════════════════════════════════════════════════════════
# EventLogDecoder Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestEventLogDecoder:
    """Test cases for EventLogDecoder"""
    
    def test_decode_known_event(self, signature_db):
        """Test decoding event log with known event signature"""
        decoder = EventLogDecoder(signature_db)
        
        # Uniswap V2 Swap event log
        log_data = {
            'topics': [
                '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822',  # Swap event topic0
                '0x0000000000000000000000007a250d5630b4cf539739df2c5dacb4c659f2488d',  # sender
                '0x000000000000000000000000742d35Cc6620C0532895041e1c6Ec83a0CD5a86A'   # to
            ],
            'data': '0x000000000000000000000000000000000000000000000000000000000000007b',
            'address': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
            'blockNumber': 18500000,
            'transactionHash': '0x1234567890abcdef',
            'logIndex': 0
        }
        
        result = decoder.decode_event_log(log_data)
        
        assert result is not None
        assert result['topic0'] == '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
        assert result['event_signature'].name == 'Swap'
        assert result['event_signature'].action_type == ActionType.SWAP
        assert result['event_signature'].protocol == 'Uniswap V2'
        assert 'indexed_params' in result
        assert 'data_params' in result
    
    def test_decode_unknown_event(self, signature_db):
        """Test decoding event log with unknown event signature"""
        decoder = EventLogDecoder(signature_db)
        
        log_data = {
            'topics': [
                '0x9999999999999999999999999999999999999999999999999999999999999999',  # Unknown topic0
            ],
            'data': '0x000000000000000000000000000000000000000000000000000000000000007b',
            'address': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
        }
        
        result = decoder.decode_event_log(log_data)
        assert result is None
    
    def test_decode_empty_log(self, signature_db):
        """Test decoding empty or invalid event logs"""
        decoder = EventLogDecoder(signature_db)
        
        # No topics
        result = decoder.decode_event_log({'topics': []})
        assert result is None
        
        # No topics field
        result = decoder.decode_event_log({})
        assert result is None

# ═══════════════════════════════════════════════════════════════════════════════════════
# ActionMapper Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestActionMapper:
    """Test cases for ActionMapper"""
    
    def setup_mock_web3_responses(self, mock_web3, sample_transaction, sample_receipt, sample_block):
        """Setup mock Web3 responses for testing"""
        # Mock transaction
        mock_tx = Mock()
        for key, value in sample_transaction.items():
            setattr(mock_tx, key, value)
        mock_tx.hash = Mock()
        mock_tx.hash.hex = Mock(return_value=sample_transaction['hash'])
        
        # Mock receipt
        mock_receipt = Mock()
        for key, value in sample_receipt.items():
            setattr(mock_receipt, key, value)
        
        # Mock block
        mock_block = Mock()
        for key, value in sample_block.items():
            setattr(mock_block, key, value)
        
        # Setup Web3 mock responses
        mock_web3.eth.get_transaction.return_value = mock_tx
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        mock_web3.eth.get_block.return_value = mock_block
        
        return mock_tx, mock_receipt, mock_block
    
    def test_action_mapper_creation(self, mock_web3):
        """Test ActionMapper creation"""
        mapper = ActionMapper(mock_web3)
        
        assert mapper.w3 == mock_web3
        assert isinstance(mapper.signature_db, SignatureDatabase)
        assert mapper.tx_decoder is not None
        assert mapper.event_decoder is not None
    
    def test_map_transaction_success(self, mock_web3, sample_transaction, sample_receipt, sample_block):
        """Test successful transaction mapping"""
        mapper = ActionMapper(mock_web3)
        
        # Setup mocks
        self.setup_mock_web3_responses(mock_web3, sample_transaction, sample_receipt, sample_block)
        
        # Mock the logs in receipt to have proper format
        mock_logs = []
        for log_data in sample_receipt['logs']:
            mock_log = Mock()
            for key, value in log_data.items():
                setattr(mock_log, key, value)
            mock_logs.append(mock_log)
        
        mock_receipt = mock_web3.eth.get_transaction_receipt.return_value
        mock_receipt.logs = mock_logs
        
        # Test mapping
        tx_hash = sample_transaction['hash']
        actions = mapper.map_transaction_to_action(tx_hash)
        
        # Should return a list (may be empty if no recognized patterns)
        assert isinstance(actions, list)
        
        # Verify Web3 calls were made
        mock_web3.eth.get_transaction.assert_called_once_with(tx_hash)
        mock_web3.eth.get_transaction_receipt.assert_called_once_with(tx_hash)
    
    def test_map_transaction_error_handling(self, mock_web3):
        """Test error handling in transaction mapping"""
        mapper = ActionMapper(mock_web3)
        
        # Mock Web3 to raise an exception
        mock_web3.eth.get_transaction.side_effect = Exception("Network error")
        
        actions = mapper.map_transaction_to_action("0xinvalid")
        
        # Should return empty list on error
        assert actions == []

# ═══════════════════════════════════════════════════════════════════════════════════════
# ActionAnalyzer Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestActionAnalyzer:
    """Test cases for ActionAnalyzer"""
    
    def test_analyzer_creation(self, mock_web3):
        """Test ActionAnalyzer creation"""
        mapper = ActionMapper(mock_web3)
        analyzer = ActionAnalyzer(mapper)
        
        assert analyzer.action_mapper == mapper
    
    def test_analyze_address_activity(self, mock_web3):
        """Test address activity analysis"""
        mapper = ActionMapper(mock_web3)
        analyzer = ActionAnalyzer(mapper)
        
        address = "0x742d35Cc6620C0532895041e1c6Ec83a0CD5a86A"
        block_range = (18500000, 18500100)
        
        result = analyzer.analyze_address_activity(address, block_range)
        
        assert isinstance(result, dict)
        assert result['address'] == address
        assert result['block_range'] == block_range
        # Note: Current implementation returns placeholder data
    
    def test_analyze_contract_activity(self, mock_web3):
        """Test contract activity analysis"""
        mapper = ActionMapper(mock_web3)
        analyzer = ActionAnalyzer(mapper)
        
        contract = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
        block_range = (18500000, 18500100)
        
        result = analyzer.analyze_contract_activity(contract, block_range)
        
        assert isinstance(result, dict)
        assert result['contract_address'] == contract
        assert result['block_range'] == block_range

# ═══════════════════════════════════════════════════════════════════════════════════════
# Utility Function Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_create_action_mapper(self, mock_web3):
        """Test create_action_mapper utility function"""
        mapper = create_action_mapper(mock_web3)
        
        assert isinstance(mapper, ActionMapper)
        assert mapper.w3 == mock_web3
    
    def test_calculate_function_selector(self):
        """Test function selector calculation"""
        signature = "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)"
        selector = calculate_function_selector(signature)
        
        # Should return 4-byte hex string
        assert isinstance(selector, str)
        assert len(selector) == 8  # 4 bytes = 8 hex characters
        
        # Should match known Uniswap V2 selector
        expected = "38ed1739"
        assert selector == expected
    
    def test_calculate_event_topic0(self):
        """Test event topic0 calculation"""
        signature = "Swap(address indexed sender, uint256 amount0In, uint256 amount1In, uint256 amount0Out, uint256 amount1Out, address indexed to)"
        topic0 = calculate_event_topic0(signature)
        
        # Should return 32-byte hex string with 0x prefix
        assert isinstance(topic0, str)
        assert topic0.startswith('0x')
        assert len(topic0) == 66  # 0x + 64 hex characters
        
        # Should match known Uniswap V2 Swap event topic0
        expected = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
        assert topic0 == expected
    
    def test_quick_action_mapping(self, mock_web3, sample_transaction, sample_receipt, sample_block):
        """Test quick_action_mapping utility function"""
        # Setup mocks
        mock_tx = Mock()
        for key, value in sample_transaction.items():
            setattr(mock_tx, key, value)
        mock_tx.hash = Mock()
        mock_tx.hash.hex = Mock(return_value=sample_transaction['hash'])
        
        mock_receipt = Mock()
        for key, value in sample_receipt.items():
            setattr(mock_receipt, key, value)
        mock_receipt.logs = []
        
        mock_block = Mock()
        for key, value in sample_block.items():
            setattr(mock_block, key, value)
        
        mock_web3.eth.get_transaction.return_value = mock_tx
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        mock_web3.eth.get_block.return_value = mock_block
        
        # Test quick mapping
        tx_hash = sample_transaction['hash']
        actions = quick_action_mapping(mock_web3, tx_hash)
        
        assert isinstance(actions, list)

# ═══════════════════════════════════════════════════════════════════════════════════════
# Protocol-Specific Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestProtocolConfigurations:
    """Test cases for protocol configurations"""
    
    def test_protocol_contracts_loaded(self):
        """Test that protocol contracts are properly defined"""
        assert "uniswap_v2" in PROTOCOL_CONTRACTS
        assert "router" in PROTOCOL_CONTRACTS["uniswap_v2"]
        assert "factory" in PROTOCOL_CONTRACTS["uniswap_v2"]
        
        assert "aave_v3" in PROTOCOL_CONTRACTS
        assert "pool" in PROTOCOL_CONTRACTS["aave_v3"]
        
        assert "lido" in PROTOCOL_CONTRACTS
        assert "steth" in PROTOCOL_CONTRACTS["lido"]
    
    def test_function_signatures_loaded(self):
        """Test that function signatures are properly defined"""
        assert len(FUNCTION_SIGNATURES) > 0
        
        # Check for specific known signatures
        uniswap_swap = next((sig for sig in FUNCTION_SIGNATURES if sig.selector == "0x38ed1739"), None)
        assert uniswap_swap is not None
        assert uniswap_swap.action_type == ActionType.SWAP
        assert uniswap_swap.protocol == "Uniswap V2"
        
        aave_supply = next((sig for sig in FUNCTION_SIGNATURES if sig.selector == "0x617ba037"), None)
        assert aave_supply is not None
        assert aave_supply.action_type == ActionType.SUPPLY
        assert aave_supply.protocol == "Aave V3"
    
    def test_event_signatures_loaded(self):
        """Test that event signatures are properly defined"""
        assert len(EVENT_SIGNATURES) > 0
        
        # Check for specific known signatures
        uniswap_swap = next((sig for sig in EVENT_SIGNATURES if sig.topic0 == "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"), None)
        assert uniswap_swap is not None
        assert uniswap_swap.action_type == ActionType.SWAP
        assert uniswap_swap.protocol == "Uniswap V2"
        
        erc20_transfer = next((sig for sig in EVENT_SIGNATURES if sig.topic0 == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"), None)
        assert erc20_transfer is not None
        assert erc20_transfer.name == "Transfer"

# ═══════════════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests for the complete action mapping pipeline"""
    
    def test_end_to_end_mapping_simulation(self, mock_web3):
        """Test end-to-end action mapping simulation"""
        # Create complete pipeline
        mapper = create_action_mapper(mock_web3)
        analyzer = ActionAnalyzer(mapper)
        
        # Mock a complete transaction flow
        tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
        
        # Mock transaction with Uniswap V2 swap
        mock_tx = Mock()
        mock_tx.hash.hex.return_value = tx_hash
        mock_tx.__getitem__ = lambda self, key: {
            'from': '0x742d35Cc6620C0532895041e1c6Ec83a0CD5a86A',
            'to': '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',
            'value': 0,
            'gasPrice': 20000000000
        }[key]
        mock_tx.get = lambda key, default=None: {
            'from': '0x742d35Cc6620C0532895041e1c6Ec83a0CD5a86A',
            'to': '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',
            'value': 0,
            'gasPrice': 20000000000
        }.get(key, default)
        
        # Mock receipt with swap event
        mock_receipt = Mock()
        mock_receipt.blockNumber = 18500000
        mock_receipt.gasUsed = 150000
        mock_receipt.logs = []
        
        # Mock block
        mock_block = Mock()
        mock_block.timestamp = 1700000000
        
        # Setup Web3 mock responses
        mock_web3.eth.get_transaction.return_value = mock_tx
        mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
        mock_web3.eth.get_block.return_value = mock_block
        
        # Test the mapping
        actions = mapper.map_transaction_to_action(tx_hash)
        
        # Should complete without errors
        assert isinstance(actions, list)
        
        # Test analyzer
        address_analysis = analyzer.analyze_address_activity(
            "0x742d35Cc6620C0532895041e1c6Ec83a0CD5a86A",
            (18500000, 18500100)
        )
        assert isinstance(address_analysis, dict)

# ═══════════════════════════════════════════════════════════════════════════════════════
# Performance and Edge Case Tests
# ═══════════════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_malformed_transaction_data(self, mock_web3):
        """Test handling of malformed transaction data"""
        mapper = ActionMapper(mock_web3)
        
        # Test with None input
        result = mapper.tx_decoder.decode_transaction_input(None)
        assert result is None
        
        # Test with malformed input
        result = mapper.tx_decoder.decode_transaction_input({'input': 'not_hex'})
        assert result is None
    
    def test_malformed_event_data(self, mock_web3):
        """Test handling of malformed event data"""
        mapper = ActionMapper(mock_web3)
        
        # Test with None log
        result = mapper.event_decoder.decode_event_log(None)
        assert result is None
        
        # Test with malformed topics
        result = mapper.event_decoder.decode_event_log({'topics': ['not_hex']})
        assert result is None
    
    def test_network_errors(self, mock_web3):
        """Test handling of network errors"""
        mapper = ActionMapper(mock_web3)
        
        # Mock network error
        mock_web3.eth.get_transaction.side_effect = Exception("Network timeout")
        
        actions = mapper.map_transaction_to_action("0xtest")
        assert actions == []  # Should return empty list on error

if __name__ == "__main__":
    print("🧪 Running Phase 3 Action Mapping Tests")
    print("=" * 60)
    
    # Run tests with pytest if available, otherwise run basic validation
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("⚠️  pytest not available, running basic validation...")
        
        # Basic validation
        from action_mapping import demo_action_mapping
        demo_action_mapping()
        
        print("\n✅ Basic validation completed")
        print("💡 Install pytest for full test suite: pip install pytest") 