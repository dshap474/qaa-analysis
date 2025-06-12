# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Ethereum Client Module for Contract Universe Discovery System                     │
# └────────────────────────────────────────────────────────────────────────────────────┘

"""
Ethereum Client Module
---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/eth_client.py
---
Enhanced Ethereum client with retry logic, error handling, and connection management
for blockchain data retrieval operations.
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import List, Dict, Any, Optional, Union
import time
import logging
from .config import EthereumConfig


class EthereumClientError(Exception):
    """Custom exception for Ethereum client errors"""
    pass


class EthereumClient:
    """Enhanced Ethereum client with retry logic and error handling"""
    
    def __init__(self, config: EthereumConfig):
        """
        Initialize the Ethereum client
        
        Args:
            config: EthereumConfig object with connection parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(
            config.rpc_url,
            request_kwargs={'timeout': config.request_timeout}
        ))
        
        # Add PoA middleware if needed (for some networks)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Verify connection
        if not self.w3.is_connected():
            raise EthereumClientError(f"Failed to connect to Ethereum node at {config.rpc_url}")
        
        self.logger.info(f"Successfully connected to Ethereum node at {config.rpc_url}")
    
    def get_logs_with_retry(self, filter_params: Dict[str, Any]) -> List[Dict]:
        """
        Get logs with exponential backoff retry logic
        
        Args:
            filter_params: Dictionary with filter parameters for eth_getLogs
            
        Returns:
            List of log dictionaries
            
        Raises:
            EthereumClientError: If all retry attempts fail
        """
        for attempt in range(self.config.max_retries):
            try:
                logs = self.w3.eth.get_logs(filter_params)
                
                if attempt > 0:
                    self.logger.info(f"Successfully retrieved logs on attempt {attempt + 1}")
                
                return logs
                
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    error_msg = f"Failed to get logs after {self.config.max_retries} attempts: {e}"
                    self.logger.error(error_msg)
                    raise EthereumClientError(error_msg)
                
                wait_time = 2 ** attempt
                self.logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                )
                time.sleep(wait_time)
        
        return []
    
    def get_current_block(self) -> int:
        """
        Get current block number
        
        Returns:
            Current block number
            
        Raises:
            EthereumClientError: If unable to retrieve block number
        """
        try:
            return self.w3.eth.block_number
        except Exception as e:
            raise EthereumClientError(f"Failed to get current block number: {e}")
    
    def get_block_timestamp(self, block_number: int) -> int:
        """
        Get timestamp for a specific block
        
        Args:
            block_number: Block number to get timestamp for
            
        Returns:
            Unix timestamp of the block
            
        Raises:
            EthereumClientError: If unable to retrieve block
        """
        try:
            block = self.w3.eth.get_block(block_number)
            return block['timestamp']
        except Exception as e:
            raise EthereumClientError(f"Failed to get block {block_number}: {e}")
    
    def get_block(self, block_number: Union[int, str], full_transactions: bool = False) -> Dict:
        """
        Get block information
        
        Args:
            block_number: Block number or 'latest'
            full_transactions: Whether to include full transaction objects
            
        Returns:
            Block dictionary
            
        Raises:
            EthereumClientError: If unable to retrieve block
        """
        try:
            return self.w3.eth.get_block(block_number, full_transactions=full_transactions)
        except Exception as e:
            raise EthereumClientError(f"Failed to get block {block_number}: {e}")
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """
        Get transaction by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction dictionary
            
        Raises:
            EthereumClientError: If unable to retrieve transaction
        """
        try:
            return self.w3.eth.get_transaction(tx_hash)
        except Exception as e:
            raise EthereumClientError(f"Failed to get transaction {tx_hash}: {e}")
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """
        Get transaction receipt by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction receipt dictionary
            
        Raises:
            EthereumClientError: If unable to retrieve receipt
        """
        try:
            return self.w3.eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            raise EthereumClientError(f"Failed to get transaction receipt {tx_hash}: {e}")
    
    def is_connected(self) -> bool:
        """
        Check if client is connected to Ethereum node
        
        Returns:
            True if connected, False otherwise
        """
        try:
            return self.w3.is_connected()
        except Exception:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current connection
        
        Returns:
            Dictionary with connection information
        """
        try:
            current_block = self.get_current_block()
            chain_id = self.w3.eth.chain_id
            
            return {
                "rpc_url": self.config.rpc_url,
                "connected": self.is_connected(),
                "current_block": current_block,
                "chain_id": chain_id,
                "client_version": self.w3.client_version if hasattr(self.w3, 'client_version') else "Unknown"
            }
        except Exception as e:
            return {
                "rpc_url": self.config.rpc_url,
                "connected": False,
                "error": str(e)
            }
    
    def estimate_blocks_in_range(self, start_block: int, end_block: int) -> Dict[str, Any]:
        """
        Estimate processing metrics for a block range
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            Dictionary with processing estimates
        """
        total_blocks = end_block - start_block + 1
        chunks = (total_blocks + self.config.chunk_size - 1) // self.config.chunk_size
        
        return {
            "total_blocks": total_blocks,
            "chunk_size": self.config.chunk_size,
            "estimated_chunks": chunks,
            "estimated_requests": chunks
        }
    
    def validate_address(self, address: str) -> bool:
        """
        Validate Ethereum address format
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.w3.to_checksum_address(address)
            return True
        except Exception:
            return False
    
    def to_checksum_address(self, address: str) -> str:
        """
        Convert address to checksum format
        
        Args:
            address: Address to convert
            
        Returns:
            Checksummed address
            
        Raises:
            EthereumClientError: If address is invalid
        """
        try:
            return self.w3.to_checksum_address(address)
        except Exception as e:
            raise EthereumClientError(f"Invalid address {address}: {e}")


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Factory Functions                                                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘

def create_ethereum_client(config: EthereumConfig) -> EthereumClient:
    """
    Factory function to create an Ethereum client
    
    Args:
        config: EthereumConfig object
        
    Returns:
        Initialized EthereumClient instance
    """
    return EthereumClient(config)


def create_default_client(rpc_url: str) -> EthereumClient:
    """
    Factory function to create an Ethereum client with default settings
    
    Args:
        rpc_url: Ethereum RPC URL
        
    Returns:
        EthereumClient instance with default configuration
    """
    from .config import create_ethereum_config
    
    config = create_ethereum_config(rpc_url=rpc_url)
    return EthereumClient(config)


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Utility Functions                                                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘

def test_connection(rpc_url: str) -> Dict[str, Any]:
    """
    Test connection to an Ethereum RPC endpoint
    
    Args:
        rpc_url: RPC URL to test
        
    Returns:
        Dictionary with connection test results
    """
    try:
        client = create_default_client(rpc_url)
        return client.get_connection_info()
    except Exception as e:
        return {
            "rpc_url": rpc_url,
            "connected": False,
            "error": str(e)
        } 