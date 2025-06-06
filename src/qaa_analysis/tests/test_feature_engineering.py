"""
Unit Tests for Feature Engineering Components.

This module contains tests for the feature extraction pipeline and individual extractors.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import logging

# Import the feature engineering components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from qaa_analysis.feature_engineering.feature_extractor import FeatureExtractor
from qaa_analysis.feature_engineering.protocol_features import ProtocolFeatures
from qaa_analysis.feature_engineering.temporal_features import TemporalFeatures
from qaa_analysis.feature_engineering.value_features import ValueFeatures
from qaa_analysis.feature_engineering.interaction_aggregator import InteractionAggregator


class TestFeatureExtractor(unittest.TestCase):
    """Test the base FeatureExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestExtractor(FeatureExtractor):
            def extract_features(self, user_interactions):
                return {'test_feature': 42}
            
            def get_feature_names(self):
                return ['test_feature']
            
            def get_feature_descriptions(self):
                return {'test_feature': 'A test feature'}
        
        self.extractor = TestExtractor("TestExtractor")
    
    def test_safe_divide(self):
        """Test safe division utility method."""
        self.assertEqual(self.extractor.safe_divide(10, 2), 5.0)
        self.assertEqual(self.extractor.safe_divide(10, 0), 0.0)
        self.assertEqual(self.extractor.safe_divide(10, 0, default=1.0), 1.0)
    
    def test_gini_coefficient(self):
        """Test Gini coefficient calculation."""
        # Perfect equality
        equal_values = pd.Series([1, 1, 1, 1])
        self.assertAlmostEqual(self.extractor.calculate_gini_coefficient(equal_values), 0.0, places=2)
        
        # Maximum inequality
        unequal_values = pd.Series([0, 0, 0, 10])
        gini = self.extractor.calculate_gini_coefficient(unequal_values)
        self.assertGreater(gini, 0.5)
    
    def test_shannon_entropy(self):
        """Test Shannon entropy calculation."""
        # Equal distribution
        equal_counts = pd.Series([1, 1, 1, 1])
        entropy = self.extractor.calculate_shannon_entropy(equal_counts)
        self.assertAlmostEqual(entropy, 2.0, places=1)  # log2(4) = 2
        
        # Single category
        single_count = pd.Series([4])
        self.assertEqual(self.extractor.calculate_shannon_entropy(single_count), 0.0)


class TestProtocolFeatures(unittest.TestCase):
    """Test the ProtocolFeatures extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = ProtocolFeatures()
        
        # Create sample interaction data
        self.sample_data = pd.DataFrame({
            'protocol_category': ['DEX', 'DEX', 'Lending', 'Staking', 'DEX'],
            'application': ['Uniswap', 'Uniswap', 'Aave', 'Lido', 'SushiSwap'],
            'user_type': ['Trader', 'Trader', 'Lender', 'Staker', 'Trader'],
            'transaction_hash': ['0x1', '0x2', '0x3', '0x4', '0x5']
        })
    
    def test_extract_features(self):
        """Test feature extraction."""
        features = self.extractor.extract_features(self.sample_data)
        
        # Check that all expected features are present
        expected_features = self.extractor.get_feature_names()
        for feature_name in expected_features:
            self.assertIn(feature_name, features)
        
        # Check specific values
        self.assertEqual(features['dex_interactions'], 3)
        self.assertEqual(features['lending_interactions'], 1)
        self.assertEqual(features['staking_interactions'], 1)
        self.assertEqual(features['unique_protocols'], 3)
        self.assertEqual(features['unique_applications'], 4)
        
        # Check ratios
        self.assertAlmostEqual(features['dex_ratio'], 0.6, places=2)
        self.assertAlmostEqual(features['lending_ratio'], 0.2, places=2)
    
    def test_user_archetype_identification(self):
        """Test user archetype identification."""
        # DEX-heavy user
        dex_data = pd.DataFrame({
            'protocol_category': ['DEX'] * 8 + ['Lending'] * 2,
            'application': ['Uniswap'] * 10,
            'user_type': ['Trader'] * 10
        })
        archetype = self.extractor.identify_user_archetype(dex_data)
        self.assertEqual(archetype, "DEX Trader")


class TestTemporalFeatures(unittest.TestCase):
    """Test the TemporalFeatures extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analysis_date = pd.Timestamp('2024-01-15')
        self.extractor = TemporalFeatures(analysis_date=self.analysis_date)
        
        # Create sample temporal data
        base_time = pd.Timestamp('2024-01-01')
        self.sample_data = pd.DataFrame({
            'block_timestamp': [
                base_time,
                base_time + timedelta(hours=1),
                base_time + timedelta(days=1),
                base_time + timedelta(days=2),
                base_time + timedelta(days=7)
            ],
            'transaction_hash': ['0x1', '0x2', '0x3', '0x4', '0x5']
        })
    
    def test_extract_features(self):
        """Test temporal feature extraction."""
        features = self.extractor.extract_features(self.sample_data)
        
        # Check that all expected features are present
        expected_features = self.extractor.get_feature_names()
        for feature_name in expected_features:
            self.assertIn(feature_name, features)
        
        # Check specific values
        self.assertEqual(features['total_interactions'], 5)
        self.assertEqual(features['days_since_last_tx'], 8)  # 15 - 7 = 8
        self.assertEqual(features['activity_duration_days'], 7)
        self.assertGreater(features['avg_time_between_tx_hours'], 0)
    
    def test_activity_streak_calculation(self):
        """Test activity streak calculation."""
        # Create consecutive daily activity
        consecutive_data = pd.DataFrame({
            'block_timestamp': [
                pd.Timestamp('2024-01-01'),
                pd.Timestamp('2024-01-02'),
                pd.Timestamp('2024-01-03'),
                pd.Timestamp('2024-01-05')  # Gap here
            ]
        })
        
        daily_counts = consecutive_data['block_timestamp'].dt.date.value_counts()
        streak = self.extractor._calculate_activity_streak(daily_counts)
        self.assertEqual(streak, 3)  # 3 consecutive days


class TestValueFeatures(unittest.TestCase):
    """Test the ValueFeatures extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = ValueFeatures()
        
        # Create sample value data (in wei)
        self.sample_data = pd.DataFrame({
            'value': [
                int(1e18),      # 1 ETH
                int(0.5e18),    # 0.5 ETH
                int(10e18),     # 10 ETH (high value)
                0,              # 0 ETH
                int(0.005e18)   # 0.005 ETH (micro)
            ],
            'receipt_gas_used': [21000, 50000, 100000, 200000, 300000],
            'gas_price': [int(20e9), int(30e9), int(50e9), int(25e9), int(40e9)],  # gwei
            'transaction_hash': ['0x1', '0x2', '0x3', '0x4', '0x5']
        })
    
    def test_extract_features(self):
        """Test value feature extraction."""
        features = self.extractor.extract_features(self.sample_data)
        
        # Check that all expected features are present
        expected_features = self.extractor.get_feature_names()
        for feature_name in expected_features:
            self.assertIn(feature_name, features)
        
        # Check specific values
        self.assertAlmostEqual(features['total_eth_value'], 11.505, places=3)
        self.assertEqual(features['high_value_tx_ratio'], 0.4)  # 2/5 transactions > 1 ETH
        self.assertEqual(features['very_high_value_tx_ratio'], 0.2)  # 1/5 transactions > 10 ETH
        self.assertEqual(features['zero_value_tx_ratio'], 0.2)  # 1/5 transactions = 0 ETH
        self.assertGreater(features['total_gas_used'], 0)
    
    def test_value_archetype_identification(self):
        """Test value archetype identification."""
        # High value user
        high_value_data = pd.DataFrame({
            'value': [int(5e18)] * 10,  # All 5 ETH transactions
            'receipt_gas_used': [21000] * 10,
            'gas_price': [int(20e9)] * 10
        })
        archetype = self.extractor.identify_value_archetype(high_value_data)
        self.assertEqual(archetype, "High Value User")


class TestInteractionAggregator(unittest.TestCase):
    """Test the InteractionAggregator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = InteractionAggregator()
        
        # Create sample interaction data
        self.sample_data = pd.DataFrame({
            'transaction_hash': ['0x1', '0x2', '0x3', '0x4'],
            'block_timestamp': [
                pd.Timestamp('2024-01-01'),
                pd.Timestamp('2024-01-01'),
                pd.Timestamp('2024-01-02'),
                pd.Timestamp('2024-01-02')
            ],
            'from_address': ['0xuser1', '0xuser2', '0xuser1', '0xuser2'],
            'to_address': ['0xcontract1', '0xcontract2', '0xcontract1', '0xcontract2'],
            'value': [int(1e18), int(2e18), int(0.5e18), int(3e18)],
            'receipt_gas_used': [21000, 50000, 30000, 40000],
            'gas_price': [int(20e9), int(25e9), int(30e9), int(35e9)],
            'protocol_category': ['DEX', 'Lending', 'DEX', 'Lending'],
            'application': ['Uniswap', 'Aave', 'Uniswap', 'Aave'],
            'user_type': ['Trader', 'Lender', 'Trader', 'Lender'],
            'contract_role': ['Router', 'Pool', 'Router', 'Pool']
        })
    
    def test_data_preparation(self):
        """Test data preparation functionality."""
        # Save sample data to temporary file
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            self.sample_data.to_parquet(tmp_path, index=False)
        
        try:
            # Load data through aggregator
            self.aggregator.load_interactions(tmp_path)
            
            # Check basic statistics
            self.assertEqual(self.aggregator.get_user_count(), 2)
            self.assertEqual(self.aggregator.get_interaction_count(), 4)
            
            # Test user iteration
            users_processed = 0
            for user_address, user_data in self.aggregator.iter_user_interactions():
                users_processed += 1
                self.assertIn(user_address, ['0xuser1', '0xuser2'])
                self.assertGreater(len(user_data), 0)
            
            self.assertEqual(users_processed, 2)
            
        finally:
            # Clean up
            tmp_path.unlink()
    
    def test_data_quality_report(self):
        """Test data quality reporting."""
        # Save sample data to temporary file
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            self.sample_data.to_parquet(tmp_path, index=False)
        
        try:
            self.aggregator.load_interactions(tmp_path)
            report = self.aggregator.get_data_quality_report()
            
            # Check report structure
            self.assertIn('total_interactions', report)
            self.assertIn('unique_users', report)
            self.assertIn('date_range', report)
            self.assertIn('value_statistics', report)
            
            # Check values
            self.assertEqual(report['total_interactions'], 4)
            self.assertEqual(report['unique_users'], 2)
            
        finally:
            tmp_path.unlink()


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2) 