"""
Unit tests for the enhanced metadata_explorer.py script.

Tests cover schema fetching with fallback mechanisms, table metadata retrieval,
error handling, and output formatting functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

# Import the functions we want to test
from qaa_analysis.metadata_explorer import (
    fetch_table_metadata,
    fetch_table_schema,
    format_table_metadata,
    format_column_schema,
    log,
    output,
)


class TestMetadataExplorer:
    """Test suite for metadata explorer functionality."""

    def setup_method(self):
        """Reset output buffer before each test."""
        global output
        output.clear()

    def test_log_function(self):
        """Test that log function adds messages to output buffer."""
        test_message = "Test log message"
        log(test_message)

        assert test_message in output
        assert len(output) == 1

    @patch("qaa_analysis.metadata_explorer.client")
    def test_fetch_table_metadata_success(self, mock_client):
        """Test successful table metadata fetching."""
        # Mock the query result
        mock_result = Mock()
        mock_result.table_name = "test_table"
        mock_result.creation_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_result.last_modified_time = datetime(2023, 12, 31, 23, 59, 59)
        mock_result.row_count = 1000000
        mock_result.size_bytes = 1073741824  # 1GB
        mock_result.table_type = "BASE TABLE"

        mock_client.query.return_value.result.return_value = [mock_result]

        result = fetch_table_metadata("test_table")

        assert result is not None
        assert result["table_name"] == "test_table"
        assert result["row_count"] == 1000000
        assert result["size_bytes"] == 1073741824
        assert result["table_type"] == "BASE TABLE"

        # Verify the query was called
        mock_client.query.assert_called_once()

    @patch("qaa_analysis.metadata_explorer.client")
    def test_fetch_table_metadata_no_results(self, mock_client):
        """Test table metadata fetching when no results are returned."""
        mock_client.query.return_value.result.return_value = []

        result = fetch_table_metadata("nonexistent_table")

        assert result is None

    @patch("qaa_analysis.metadata_explorer.client")
    def test_fetch_table_metadata_exception(self, mock_client):
        """Test table metadata fetching when an exception occurs."""
        mock_client.query.side_effect = Exception("BigQuery error")

        result = fetch_table_metadata("test_table")

        assert result is None

    @patch("qaa_analysis.metadata_explorer.client")
    def test_fetch_table_schema_with_comments_success(self, mock_client):
        """Test successful schema fetching with comment field."""
        # Mock column result
        mock_column = Mock()
        mock_column.ordinal_position = 1
        mock_column.column_name = "test_column"
        mock_column.data_type = "STRING"
        mock_column.is_nullable = "YES"
        mock_column.is_partitioning_column = "NO"
        mock_column.clustering_ordinal_position = None
        mock_column.retrieved_comment = "Test comment"

        mock_client.query.return_value.result.return_value = [mock_column]

        result = fetch_table_schema("test_table")

        assert result is not None
        assert len(result) == 1
        assert result[0].column_name == "test_column"
        assert result[0].retrieved_comment == "Test comment"

    @patch("qaa_analysis.metadata_explorer.client")
    def test_fetch_table_schema_fallback_to_no_comments(self, mock_client):
        """Test schema fetching fallback when comment fields fail."""
        # First call (with comments) fails, second call (without comments) succeeds
        mock_column = Mock()
        mock_column.ordinal_position = 1
        mock_column.column_name = "test_column"
        mock_column.data_type = "STRING"
        mock_column.is_nullable = "YES"
        mock_column.is_partitioning_column = "NO"
        mock_column.clustering_ordinal_position = None
        mock_column.retrieved_comment = None

        # Configure side effects: first 3 calls fail (trying comment fields), 4th succeeds
        mock_client.query.side_effect = [
            Exception("description field not found"),
            Exception("column_comment field not found"),
            Exception("comment field not found"),
            Mock(result=Mock(return_value=[mock_column])),
        ]

        result = fetch_table_schema("test_table")

        assert result is not None
        assert len(result) == 1
        assert result[0].column_name == "test_column"
        assert result[0].retrieved_comment is None

        # Should have tried 4 times (3 comment attempts + 1 fallback)
        assert mock_client.query.call_count == 4

    @patch("qaa_analysis.metadata_explorer.client")
    def test_fetch_table_schema_complete_failure(self, mock_client):
        """Test schema fetching when all attempts fail."""
        mock_client.query.side_effect = Exception("Complete failure")

        result = fetch_table_schema("test_table")

        assert result is None

    def test_format_table_metadata_complete(self):
        """Test formatting complete table metadata."""
        metadata = {
            "last_modified_time": datetime(2023, 12, 31, 23, 59, 59),
            "row_count": 1000000,
            "size_bytes": 1073741824,  # 1GB
            "table_type": "BASE TABLE",
        }

        format_table_metadata(metadata)

        # Check that all metadata was logged (with markdown formatting)
        assert any(
            "**Last Modified:** 2023-12-31 23:59:59 UTC" in msg for msg in output
        )
        assert any("**Row Count:** 1,000,000" in msg for msg in output)
        assert any("**Size:** 1.00 GB" in msg for msg in output)
        assert any("**Type:** BASE TABLE" in msg for msg in output)

    def test_format_table_metadata_partial(self):
        """Test formatting partial table metadata with None values."""
        metadata = {
            "last_modified_time": None,
            "row_count": None,
            "size_bytes": 2147483648,  # 2GB
            "table_type": "VIEW",
        }

        format_table_metadata(metadata)

        # Should only log non-None values (with markdown formatting)
        assert any("**Size:** 2.00 GB" in msg for msg in output)
        assert any("**Type:** VIEW" in msg for msg in output)
        assert not any("**Last Modified**" in msg for msg in output)
        assert not any("**Row Count**" in msg for msg in output)

    def test_format_column_schema_basic(self):
        """Test formatting basic column schema."""
        mock_column = Mock()
        mock_column.column_name = "test_column"
        mock_column.data_type = "STRING"
        mock_column.is_nullable = "YES"
        mock_column.is_partitioning_column = "NO"
        mock_column.clustering_ordinal_position = None
        mock_column.retrieved_comment = "Test comment"

        columns = [mock_column]
        format_column_schema(columns)

        # Check header
        assert any("Columns (1 total)" in msg for msg in output)
        assert any(
            "| Column | Type | Nullable | Description / Comment |" in msg
            for msg in output
        )

        # Check column row
        assert any(
            "| `test_column` | STRING | Yes | Test comment |" in msg for msg in output
        )

    def test_format_column_schema_with_special_attributes(self):
        """Test formatting column schema with partitioning and clustering."""
        mock_column = Mock()
        mock_column.column_name = "partition_column"
        mock_column.data_type = "TIMESTAMP"
        mock_column.is_nullable = "NO"
        mock_column.is_partitioning_column = "YES"
        mock_column.clustering_ordinal_position = 1
        mock_column.retrieved_comment = "Partition and cluster column"

        columns = [mock_column]
        format_column_schema(columns)

        # Check that special attributes are included
        assert any("*[PARTITION, CLUSTER-1]*" in msg for msg in output)

    def test_format_column_schema_long_comment_truncation(self):
        """Test that long comments are properly truncated."""
        mock_column = Mock()
        mock_column.column_name = "test_column"
        mock_column.data_type = "STRING"
        mock_column.is_nullable = "YES"
        mock_column.is_partitioning_column = "NO"
        mock_column.clustering_ordinal_position = None
        mock_column.retrieved_comment = "A" * 100  # Very long comment

        columns = [mock_column]
        format_column_schema(columns)

        # Check that comment was truncated
        assert any("A" * 77 + "..." in msg for msg in output)

    def test_format_column_schema_no_comment(self):
        """Test formatting column schema when comment is None."""
        mock_column = Mock()
        mock_column.column_name = "test_column"
        mock_column.data_type = "STRING"
        mock_column.is_nullable = "YES"
        mock_column.is_partitioning_column = "NO"
        mock_column.clustering_ordinal_position = None
        mock_column.retrieved_comment = None

        columns = [mock_column]
        format_column_schema(columns)

        # Check that N/A is used for missing comment
        assert any("| `test_column` | STRING | Yes | N/A |" in msg for msg in output)

    def test_format_column_schema_multiple_columns(self):
        """Test formatting multiple columns."""
        mock_column1 = Mock()
        mock_column1.column_name = "column1"
        mock_column1.data_type = "STRING"
        mock_column1.is_nullable = "YES"
        mock_column1.is_partitioning_column = "NO"
        mock_column1.clustering_ordinal_position = None
        mock_column1.retrieved_comment = "First column"

        mock_column2 = Mock()
        mock_column2.column_name = "column2"
        mock_column2.data_type = "INTEGER"
        mock_column2.is_nullable = "NO"
        mock_column2.is_partitioning_column = "YES"
        mock_column2.clustering_ordinal_position = None
        mock_column2.retrieved_comment = "Second column"

        columns = [mock_column1, mock_column2]
        format_column_schema(columns)

        # Check header shows correct count
        assert any("Columns (2 total)" in msg for msg in output)

        # Check both columns are present
        assert any(
            "| `column1` | STRING | Yes | First column |" in msg for msg in output
        )
        assert any(
            "| `column2` *[PARTITION]* | INTEGER | No | Second column |" in msg
            for msg in output
        )


class TestIntegration:
    """Integration tests for the metadata explorer."""

    def setup_method(self):
        """Reset output buffer before each test."""
        global output
        output.clear()

    @patch("qaa_analysis.metadata_explorer.client")
    @patch("qaa_analysis.metadata_explorer.config")
    def test_full_table_processing_success(self, mock_config, mock_client):
        """Test complete table processing workflow."""
        # Setup config mock
        mock_config.PROJECT_ID = "test-project"
        mock_config.DEV_MODE = True

        # Setup table metadata mock
        mock_table_meta = Mock()
        mock_table_meta.table_name = "test_table"
        mock_table_meta.creation_time = datetime(2023, 1, 1)
        mock_table_meta.last_modified_time = datetime(2023, 12, 31)
        mock_table_meta.row_count = 1000
        mock_table_meta.size_bytes = 1024**3  # 1GB
        mock_table_meta.table_type = "BASE TABLE"

        # Setup column schema mock
        mock_column = Mock()
        mock_column.ordinal_position = 1
        mock_column.column_name = "test_column"
        mock_column.data_type = "STRING"
        mock_column.is_nullable = "YES"
        mock_column.is_partitioning_column = "NO"
        mock_column.clustering_ordinal_position = None
        mock_column.retrieved_comment = "Test comment"

        # Configure client to return both metadata and schema
        mock_client.query.return_value.result.side_effect = [
            [mock_table_meta],  # Table metadata query
            [mock_column],  # Schema query
        ]

        # Test the functions
        metadata = fetch_table_metadata("test_table")
        assert metadata is not None

        format_table_metadata(metadata)

        schema = fetch_table_schema("test_table")
        assert schema is not None

        format_column_schema(schema)

        # Verify output contains expected information (with markdown formatting)
        assert any("**Last Modified:**" in msg for msg in output)
        assert any("**Row Count:** 1,000" in msg for msg in output)
        assert any("**Size:** 1.00 GB" in msg for msg in output)
        assert any("Columns (1 total)" in msg for msg in output)
        assert any("test_column" in msg for msg in output)


if __name__ == "__main__":
    pytest.main([__file__])
