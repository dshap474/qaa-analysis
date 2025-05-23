"""
Unit tests for REV query generation module.

Tests the SQL query generation functions for correctness, edge cases,
and proper handling of different parameter combinations.
"""

import pytest
from datetime import datetime

from src.qaa_analysis.queries.rev_queries import (
    get_blockworks_rev_query,
    validate_date_format,
    get_rev_query_metadata,
)


class TestGetBlockworksRevQuery:
    """Test cases for the get_blockworks_rev_query function."""

    def test_basic_query_generation(self):
        """Test basic query generation with valid parameters."""
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        sample_rate = 1.0

        query = get_blockworks_rev_query(start_date, end_date, sample_rate)

        # Check that query is a string and not empty
        assert isinstance(query, str)
        assert len(query) > 0

        # Check for required SQL components
        assert "WITH filtered_transactions AS" in query
        assert "rev_components AS" in query
        assert "bigquery-public-data.crypto_ethereum.transactions" in query
        assert f"DATE(block_timestamp) BETWEEN '{start_date}' AND '{end_date}'" in query

        # Check for required output columns
        required_columns = [
            "address",
            "tx_date",
            "tx_count",
            "sum_gas_used",
            "total_rev_eth",
            "tips_rev_eth",
            "burned_rev_eth",
            "avg_tx_fee_eth",
        ]
        for column in required_columns:
            assert column in query

    def test_query_with_sampling(self):
        """Test query generation with sampling enabled."""
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        sample_rate = 0.1

        query = get_blockworks_rev_query(start_date, end_date, sample_rate)

        # Check that sampling clause is included
        assert f"RAND() < {sample_rate}" in query
        assert "AND RAND() <" in query

    def test_query_without_sampling(self):
        """Test query generation without sampling (sample_rate = 1.0)."""
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        sample_rate = 1.0

        query = get_blockworks_rev_query(start_date, end_date, sample_rate)

        # Check that sampling clause is NOT included
        assert "RAND()" not in query

    def test_edge_case_zero_sampling(self):
        """Test query generation with zero sampling rate."""
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        sample_rate = 0.0

        query = get_blockworks_rev_query(start_date, end_date, sample_rate)

        # Should not include RAND() clause for 0.0 sample rate
        assert "RAND()" not in query

    def test_invalid_sample_rate_high(self):
        """Test that invalid high sample rate raises ValueError."""
        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.5)

    def test_invalid_sample_rate_negative(self):
        """Test that negative sample rate raises ValueError."""
        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            get_blockworks_rev_query("2024-01-01", "2024-01-07", -0.1)

    def test_single_day_query(self):
        """Test query generation for a single day."""
        start_date = "2024-01-01"
        end_date = "2024-01-01"

        query = get_blockworks_rev_query(start_date, end_date, 1.0)

        assert f"DATE(block_timestamp) BETWEEN '{start_date}' AND '{end_date}'" in query

    def test_eip1559_handling(self):
        """Test that query properly handles EIP-1559 base fee calculations."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Check for proper COALESCE handling of base_fee_per_gas
        assert "COALESCE(base_fee_per_gas, 0)" in query

        # Check for priority fee calculation
        assert "gas_price - COALESCE(base_fee_per_gas, 0)" in query

    def test_query_structure_and_ordering(self):
        """Test that query has proper structure and ordering."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Check for proper GROUP BY
        assert "GROUP BY address, tx_date" in query

        # Check for proper ORDER BY
        assert "ORDER BY tx_date DESC, total_rev_eth DESC" in query

    def test_different_date_formats(self):
        """Test query generation with different valid date formats."""
        # Test with different valid ISO dates
        test_cases = [
            ("2024-01-01", "2024-01-31"),
            ("2023-12-25", "2023-12-31"),
            ("2024-02-29", "2024-03-01"),  # Leap year
        ]

        for start_date, end_date in test_cases:
            query = get_blockworks_rev_query(start_date, end_date, 1.0)
            assert isinstance(query, str)
            assert len(query) > 0
            assert start_date in query
            assert end_date in query


class TestValidateDateFormat:
    """Test cases for the validate_date_format function."""

    def test_valid_date_formats(self):
        """Test validation of valid ISO date formats."""
        valid_dates = [
            "2024-01-01",
            "2023-12-31",
            "2024-02-29",  # Leap year
            "2000-01-01",
        ]

        for date_str in valid_dates:
            assert validate_date_format(date_str) is True

    def test_invalid_date_formats(self):
        """Test validation of invalid date formats."""
        invalid_dates = [
            "2024/01/01",  # Wrong separator
            "01-01-2024",  # Wrong order
            "2024-1-1",  # Missing leading zeros
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "not-a-date",  # Not a date
            "",  # Empty string
            "2024-02-30",  # Invalid date for February
        ]

        for date_str in invalid_dates:
            assert validate_date_format(date_str) is False


class TestGetRevQueryMetadata:
    """Test cases for the get_rev_query_metadata function."""

    def test_basic_metadata_generation(self):
        """Test basic metadata generation."""
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        sample_rate = 0.5

        metadata = get_rev_query_metadata(start_date, end_date, sample_rate)

        # Check required fields
        assert metadata["query_type"] == "blockworks_rev"
        assert metadata["start_date"] == start_date
        assert metadata["end_date"] == end_date
        assert metadata["days_span"] == 7
        assert metadata["sample_rate"] == sample_rate
        assert metadata["is_sampled"] is True
        assert (
            metadata["target_table"]
            == "bigquery-public-data.crypto_ethereum.transactions"
        )

    def test_metadata_complexity_assessment(self):
        """Test complexity assessment in metadata."""
        # Test medium complexity (7 days or less)
        metadata_medium = get_rev_query_metadata("2024-01-01", "2024-01-07", 1.0)
        assert metadata_medium["estimated_complexity"] == "medium"

        # Test high complexity (more than 7 days)
        metadata_high = get_rev_query_metadata("2024-01-01", "2024-01-15", 1.0)
        assert metadata_high["estimated_complexity"] == "high"

    def test_metadata_sampling_detection(self):
        """Test sampling detection in metadata."""
        # Test with sampling
        metadata_sampled = get_rev_query_metadata("2024-01-01", "2024-01-07", 0.1)
        assert metadata_sampled["is_sampled"] is True

        # Test without sampling
        metadata_full = get_rev_query_metadata("2024-01-01", "2024-01-07", 1.0)
        assert metadata_full["is_sampled"] is False

    def test_metadata_single_day(self):
        """Test metadata for single day query."""
        metadata = get_rev_query_metadata("2024-01-01", "2024-01-01", 1.0)
        assert metadata["days_span"] == 1
        assert metadata["estimated_complexity"] == "medium"

    def test_metadata_invalid_dates(self):
        """Test metadata generation with invalid dates."""
        with pytest.raises(ValueError, match="Invalid start_date_iso format"):
            get_rev_query_metadata("invalid-date", "2024-01-07", 1.0)

        with pytest.raises(ValueError, match="Invalid end_date_iso format"):
            get_rev_query_metadata("2024-01-01", "invalid-date", 1.0)

    def test_metadata_date_range_calculation(self):
        """Test correct date range calculation."""
        test_cases = [
            ("2024-01-01", "2024-01-01", 1),  # Same day
            ("2024-01-01", "2024-01-02", 2),  # Two days
            ("2024-01-01", "2024-01-31", 31),  # Full month
            ("2024-02-01", "2024-02-29", 29),  # Leap year February
        ]

        for start_date, end_date, expected_days in test_cases:
            metadata = get_rev_query_metadata(start_date, end_date, 1.0)
            assert metadata["days_span"] == expected_days


# Integration test
class TestQueryIntegration:
    """Integration tests for query generation workflow."""

    def test_full_workflow_integration(self):
        """Test the complete workflow from metadata to query generation."""
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        sample_rate = 0.1

        # Get metadata first
        metadata = get_rev_query_metadata(start_date, end_date, sample_rate)

        # Generate query
        query = get_blockworks_rev_query(start_date, end_date, sample_rate)

        # Verify consistency
        assert metadata["start_date"] == start_date
        assert metadata["end_date"] == end_date
        assert metadata["sample_rate"] == sample_rate
        assert start_date in query
        assert end_date in query

        if metadata["is_sampled"]:
            assert "RAND()" in query
        else:
            assert "RAND()" not in query
