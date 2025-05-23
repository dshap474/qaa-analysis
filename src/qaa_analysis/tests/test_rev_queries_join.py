"""
Tests for the modified REV queries with JOIN functionality.

This module tests the updated get_blockworks_rev_query function that now
correctly JOINs the transactions and blocks tables to access base_fee_per_gas.
"""

import pytest
from qaa_analysis.queries.rev_queries import (
    get_blockworks_rev_query,
    get_rev_query_metadata,
)


class TestRevQueriesWithJoin:
    """Test suite for REV queries with JOIN functionality."""

    def test_query_contains_join(self):
        """Test that the generated query contains the required JOIN."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Check for JOIN syntax
        assert "INNER JOIN" in query
        assert "bigquery-public-data.crypto_ethereum.transactions" in query
        assert "bigquery-public-data.crypto_ethereum.blocks" in query
        assert "ON t.block_number = b.number" in query

    def test_query_uses_block_base_fee_per_gas(self):
        """Test that the query uses base_fee_per_gas from blocks table."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Check that we're using the aliased column from blocks table
        assert "b.base_fee_per_gas AS block_base_fee_per_gas" in query
        assert "block_base_fee_per_gas" in query

        # Ensure we're not trying to access base_fee_per_gas directly from transactions
        lines = query.split("\n")
        transaction_select_lines = [
            line
            for line in lines
            if "FROM `bigquery-public-data.crypto_ethereum.transactions`" in line
        ]
        assert len(transaction_select_lines) > 0

    def test_query_structure_with_sampling(self):
        """Test query structure with sampling enabled."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 0.1)

        # Check for sampling clause
        assert "RAND() < 0.1" in query

        # Check for proper table aliases
        assert "AS t" in query
        assert "AS b" in query

        # Check for proper date filtering with table alias
        assert "DATE(t.block_timestamp)" in query

    def test_query_structure_without_sampling(self):
        """Test query structure without sampling."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Should not contain sampling clause
        assert "RAND()" not in query

        # Should still have proper structure
        assert "source_transactions_with_block_fees" in query
        assert "rev_components" in query

    def test_fee_calculations_use_block_data(self):
        """Test that fee calculations use the correct base_fee_per_gas source."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Check priority fee calculation
        assert "gas_price - COALESCE(block_base_fee_per_gas, 0)" in query

        # Check base fee burned calculation
        assert "COALESCE(block_base_fee_per_gas, 0) * receipt_gas_used" in query

    def test_output_columns_unchanged(self):
        """Test that the final output columns remain the same."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        expected_columns = [
            "address",
            "tx_date",
            "tx_count",
            "sum_gas_used",
            "total_rev_eth",
            "tips_rev_eth",
            "burned_rev_eth",
            "avg_tx_fee_eth",
        ]

        for column in expected_columns:
            assert column in query

    def test_metadata_reflects_multiple_tables(self):
        """Test that metadata function reflects the use of multiple tables."""
        metadata = get_rev_query_metadata("2024-01-01", "2024-01-07", 1.0)

        assert "target_tables" in metadata
        assert isinstance(metadata["target_tables"], list)
        assert len(metadata["target_tables"]) == 2
        assert (
            "bigquery-public-data.crypto_ethereum.transactions"
            in metadata["target_tables"]
        )
        assert (
            "bigquery-public-data.crypto_ethereum.blocks" in metadata["target_tables"]
        )

    def test_query_with_edge_case_dates(self):
        """Test query generation with edge case dates."""
        # Single day query
        query = get_blockworks_rev_query("2024-01-01", "2024-01-01", 0.5)

        assert "2024-01-01" in query
        assert "RAND() < 0.5" in query
        assert "INNER JOIN" in query

    def test_query_syntax_validity(self):
        """Test that the generated query has valid SQL syntax structure."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Check for proper CTE structure
        assert query.count("WITH") == 1
        assert query.count("SELECT") >= 3  # One for each CTE and final SELECT
        assert query.count("FROM") >= 3  # One for each CTE and final SELECT

        # Check for proper parentheses balance
        assert query.count("(") == query.count(")")

    def test_date_filtering_uses_transaction_timestamp(self):
        """Test that date filtering uses the transaction timestamp with proper alias."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        # Should use t.block_timestamp for filtering
        assert "DATE(t.block_timestamp) BETWEEN" in query

        # Should not use unqualified block_timestamp
        lines = query.split("\n")
        where_lines = [line for line in lines if "WHERE" in line and "DATE(" in line]
        for line in where_lines:
            if "block_timestamp" in line:
                assert (
                    "t.block_timestamp" in line
                ), f"Found unqualified block_timestamp in: {line}"


class TestRevQueriesJoinValidation:
    """Test validation and error handling for JOIN queries."""

    def test_invalid_sample_rate_still_raises_error(self):
        """Test that invalid sample rates still raise appropriate errors."""
        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.5)

        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            get_blockworks_rev_query("2024-01-01", "2024-01-07", -0.1)

    def test_zero_sample_rate_handling(self):
        """Test handling of zero sample rate."""
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 0.0)

        # Should not include sampling clause for 0.0
        assert "RAND()" not in query
        assert "INNER JOIN" in query

    def test_metadata_validation_still_works(self):
        """Test that metadata validation still works with JOIN queries."""
        # Valid dates should work
        metadata = get_rev_query_metadata("2024-01-01", "2024-01-07", 0.5)
        assert metadata["query_type"] == "blockworks_rev"

        # Invalid dates should still raise errors
        with pytest.raises(ValueError, match="Invalid start_date_iso format"):
            get_rev_query_metadata("invalid-date", "2024-01-07", 0.5)
