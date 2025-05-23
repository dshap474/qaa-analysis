"""
Tests for the CostAwareBigQueryClient class.

This module tests BigQuery client cost controls, dry run functionality,
and query execution with billing limits.
"""

import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from qaa_analysis.config import PipelineConfig
from qaa_analysis.etl.cost_aware_client import CostAwareBigQueryClient, QueryCostError


class TestCostAwareBigQueryClient:
    """Test suite for CostAwareBigQueryClient class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}, clear=True):
            config = PipelineConfig()
            config.MAX_BYTES_BILLED = 1024**3  # 1GB for testing
            return config

    @pytest.fixture
    def mock_bigquery_client(self):
        """Create a mock BigQuery client."""
        return Mock(spec=bigquery.Client)

    @pytest.fixture
    def cost_aware_client(self, mock_config, mock_bigquery_client):
        """Create a CostAwareBigQueryClient with mocked dependencies."""
        with patch(
            "qaa_analysis.etl.cost_aware_client.bigquery.Client",
            return_value=mock_bigquery_client,
        ):
            return CostAwareBigQueryClient(mock_config)

    def test_client_initialization(self, mock_config):
        """Test successful client initialization."""
        with patch(
            "qaa_analysis.etl.cost_aware_client.bigquery.Client"
        ) as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = CostAwareBigQueryClient(mock_config)

            assert client.config == mock_config
            assert client.client == mock_client
            mock_client_class.assert_called_once_with(project="test-project")

    def test_client_initialization_failure(self, mock_config):
        """Test client initialization failure handling."""
        with patch(
            "qaa_analysis.etl.cost_aware_client.bigquery.Client",
            side_effect=Exception("Auth failed"),
        ):
            with pytest.raises(Exception, match="Auth failed"):
                CostAwareBigQueryClient(mock_config)

    def test_estimate_query_cost_success(self, cost_aware_client):
        """Test successful query cost estimation."""
        # Mock query job for dry run
        mock_job = Mock()
        mock_job.total_bytes_processed = 500 * 1024**2  # 500MB

        cost_aware_client.client.query.return_value = mock_job

        query = "SELECT * FROM test_table"
        bytes_estimate, cost_estimate = cost_aware_client.estimate_query_cost(query)

        assert bytes_estimate == 500 * 1024**2
        assert cost_estimate > 0  # Should be positive

        # Verify dry run configuration
        cost_aware_client.client.query.assert_called_once()
        call_args = cost_aware_client.client.query.call_args
        job_config = call_args[1]["job_config"]

        assert job_config.dry_run is True
        assert job_config.use_query_cache is False
        assert (
            job_config.maximum_bytes_billed == cost_aware_client.config.MAX_BYTES_BILLED
        )

    def test_estimate_query_cost_failure(self, cost_aware_client):
        """Test query cost estimation failure handling."""
        cost_aware_client.client.query.side_effect = GoogleCloudError("Dry run failed")

        query = "SELECT * FROM invalid_table"

        with pytest.raises(GoogleCloudError, match="Dry run failed"):
            cost_aware_client.estimate_query_cost(query)

    def test_safe_query_within_limits(self, cost_aware_client):
        """Test successful query execution within cost limits."""
        # Mock dry run (cost estimation)
        mock_dry_run_job = Mock()
        mock_dry_run_job.total_bytes_processed = (
            100 * 1024**2
        )  # 100MB (within 1GB limit)

        # Mock actual query execution
        mock_actual_job = Mock()
        mock_actual_job.total_bytes_billed = 95 * 1024**2  # 95MB actual

        # Mock DataFrame result
        mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        mock_actual_job.to_dataframe.return_value = mock_df

        # Configure client to return different jobs for dry run vs actual
        cost_aware_client.client.query.side_effect = [mock_dry_run_job, mock_actual_job]

        query = "SELECT * FROM test_table"
        result_df = cost_aware_client.safe_query(query)

        # Verify result
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        assert list(result_df.columns) == ["col1", "col2"]

        # Verify two calls were made (dry run + actual)
        assert cost_aware_client.client.query.call_count == 2

    def test_safe_query_exceeds_limits(self, cost_aware_client):
        """Test query blocked when exceeding cost limits."""
        # Mock dry run with high cost
        mock_dry_run_job = Mock()
        mock_dry_run_job.total_bytes_processed = 2 * 1024**3  # 2GB (exceeds 1GB limit)

        cost_aware_client.client.query.return_value = mock_dry_run_job

        query = "SELECT * FROM huge_table"

        with pytest.raises(
            QueryCostError, match="Query exceeds maximum bytes billed limit"
        ):
            cost_aware_client.safe_query(query)

        # Verify only dry run was called, not actual execution
        assert cost_aware_client.client.query.call_count == 1

    def test_safe_query_with_custom_job_config(self, cost_aware_client):
        """Test query execution with custom job configuration."""
        # Mock dry run
        mock_dry_run_job = Mock()
        mock_dry_run_job.total_bytes_processed = 100 * 1024**2  # 100MB

        # Mock actual query
        mock_actual_job = Mock()
        mock_actual_job.total_bytes_billed = 95 * 1024**2
        mock_actual_job.to_dataframe.return_value = pd.DataFrame()

        cost_aware_client.client.query.side_effect = [mock_dry_run_job, mock_actual_job]

        query = "SELECT * FROM test_table"
        custom_config = {"use_legacy_sql": True, "priority": "INTERACTIVE"}

        result_df = cost_aware_client.safe_query(
            query, job_config_customizations=custom_config
        )

        assert isinstance(result_df, pd.DataFrame)

        # Verify custom config was applied to actual job (second call)
        actual_call_args = cost_aware_client.client.query.call_args_list[1]
        actual_job_config = actual_call_args[1]["job_config"]

        assert actual_job_config.use_legacy_sql is True
        assert actual_job_config.priority == "INTERACTIVE"

    def test_safe_query_execution_failure(self, cost_aware_client):
        """Test handling of query execution failures."""
        # Mock successful dry run
        mock_dry_run_job = Mock()
        mock_dry_run_job.total_bytes_processed = 100 * 1024**2

        # Mock failed actual execution
        cost_aware_client.client.query.side_effect = [
            mock_dry_run_job,
            GoogleCloudError("Query execution failed"),
        ]

        query = "SELECT * FROM test_table"

        with pytest.raises(GoogleCloudError, match="Query execution failed"):
            cost_aware_client.safe_query(query)

    def test_get_table_info_success(self, cost_aware_client):
        """Test successful table metadata retrieval."""
        # Mock table object
        mock_table = Mock()
        mock_table.table_id = "test_table"
        mock_table.dataset_id = "test_dataset"
        mock_table.project = "test-project"
        mock_table.num_rows = 1000
        mock_table.num_bytes = 1024**2  # 1MB
        mock_table.created = "2024-01-01T00:00:00Z"
        mock_table.modified = "2024-01-02T00:00:00Z"

        # Mock schema fields
        mock_field1 = Mock()
        mock_field1.name = "id"
        mock_field1.field_type = "INTEGER"
        mock_field1.mode = "REQUIRED"
        mock_field1.description = "Primary key"

        mock_field2 = Mock()
        mock_field2.name = "name"
        mock_field2.field_type = "STRING"
        mock_field2.mode = "NULLABLE"
        mock_field2.description = "Name field"

        mock_table.schema = [mock_field1, mock_field2]

        cost_aware_client.client.get_table.return_value = mock_table

        table_id = "test-project.test_dataset.test_table"
        info = cost_aware_client.get_table_info(table_id)

        assert info["table_id"] == "test_table"
        assert info["dataset_id"] == "test_dataset"
        assert info["project"] == "test-project"
        assert info["num_rows"] == 1000
        assert info["num_bytes"] == 1024**2
        assert len(info["schema"]) == 2
        assert info["schema"][0]["name"] == "id"
        assert info["schema"][1]["name"] == "name"

    def test_get_table_info_failure(self, cost_aware_client):
        """Test table metadata retrieval failure handling."""
        cost_aware_client.client.get_table.side_effect = Exception("Table not found")

        table_id = "test-project.test_dataset.nonexistent_table"

        with pytest.raises(Exception, match="Table not found"):
            cost_aware_client.get_table_info(table_id)

    def test_client_repr(self, cost_aware_client):
        """Test string representation of the client."""
        repr_str = repr(cost_aware_client)

        assert "CostAwareBigQueryClient" in repr_str
        assert "test-project" in repr_str
        # The repr formats numbers with commas, so check for the formatted version
        assert f"{cost_aware_client.config.MAX_BYTES_BILLED:,}" in repr_str

    def test_cost_calculation_accuracy(self, cost_aware_client):
        """Test accuracy of cost calculation."""
        # Test with known values
        bytes_processed = 1024**4  # 1 TiB
        expected_cost = 6.25  # $6.25 per TiB

        mock_job = Mock()
        mock_job.total_bytes_processed = bytes_processed
        cost_aware_client.client.query.return_value = mock_job

        _, cost_estimate = cost_aware_client.estimate_query_cost("SELECT 1")

        assert abs(cost_estimate - expected_cost) < 0.01  # Within 1 cent


if __name__ == "__main__":
    pytest.main([__file__])
