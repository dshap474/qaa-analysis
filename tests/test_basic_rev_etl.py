"""
Unit tests for Basic REV ETL module.

Tests the ETL orchestration functions, data validation, file operations,
and integration with core modules.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.qaa_analysis.etl.basic_rev_etl import (
    setup_logging,
    validate_dataframe,
    save_dataframe_safely,
    main,
)


class TestSetupLogging:
    """Test cases for logging setup."""

    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging()
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")


class TestValidateDataframe:
    """Test cases for DataFrame validation."""

    def test_validate_valid_dataframe(self):
        """Test validation of a valid DataFrame."""
        # Create a valid DataFrame with all required columns
        df = pd.DataFrame(
            {
                "address": ["0x123", "0x456"],
                "tx_date": ["2024-01-01", "2024-01-02"],
                "tx_count": [5, 3],
                "sum_gas_used": [100000, 75000],
                "total_rev_eth": [0.01, 0.008],
                "tips_rev_eth": [0.002, 0.001],
                "burned_rev_eth": [0.008, 0.007],
                "avg_tx_fee_eth": [0.002, 0.0027],
            }
        )

        result = validate_dataframe(df, "Test operation")
        assert result is True

    def test_validate_none_dataframe(self):
        """Test validation of None DataFrame."""
        result = validate_dataframe(None, "Test operation")
        assert result is False

    def test_validate_wrong_type(self):
        """Test validation of wrong data type."""
        result = validate_dataframe("not a dataframe", "Test operation")
        assert result is False

    def test_validate_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        df = pd.DataFrame()
        result = validate_dataframe(df, "Test operation")
        assert result is True  # Empty is valid, just not useful

    def test_validate_missing_columns(self):
        """Test validation of DataFrame with missing required columns."""
        df = pd.DataFrame(
            {
                "address": ["0x123"],
                "tx_date": ["2024-01-01"],
                # Missing other required columns
            }
        )

        result = validate_dataframe(df, "Test operation")
        assert result is False

    def test_validate_extra_columns_allowed(self):
        """Test that extra columns don't break validation."""
        df = pd.DataFrame(
            {
                "address": ["0x123"],
                "tx_date": ["2024-01-01"],
                "tx_count": [5],
                "sum_gas_used": [100000],
                "total_rev_eth": [0.01],
                "tips_rev_eth": [0.002],
                "burned_rev_eth": [0.008],
                "avg_tx_fee_eth": [0.002],
                "extra_column": ["extra_data"],  # Extra column
            }
        )

        result = validate_dataframe(df, "Test operation")
        assert result is True


class TestSaveDataframeSafely:
    """Test cases for safe DataFrame saving."""

    def setUp(self):
        """Set up temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_save_valid_dataframe(self):
        """Test saving a valid DataFrame."""
        self.setUp()
        try:
            df = pd.DataFrame(
                {
                    "address": ["0x123", "0x456"],
                    "tx_date": ["2024-01-01", "2024-01-02"],
                    "tx_count": [5, 3],
                    "sum_gas_used": [100000, 75000],
                    "total_rev_eth": [0.01, 0.008],
                    "tips_rev_eth": [0.002, 0.001],
                    "burned_rev_eth": [0.008, 0.007],
                    "avg_tx_fee_eth": [0.002, 0.0027],
                }
            )

            output_path = self.temp_path / "test_output.parquet"
            result = save_dataframe_safely(df, output_path, "Test save")

            assert result is True
            assert output_path.exists()

            # Verify we can read the file back
            loaded_df = pd.read_parquet(output_path)
            assert len(loaded_df) == len(df)
            assert list(loaded_df.columns) == list(df.columns)
        finally:
            self.tearDown()

    def test_save_creates_directory(self):
        """Test that saving creates necessary directories."""
        self.setUp()
        try:
            df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

            # Use a nested path that doesn't exist
            output_path = self.temp_path / "nested" / "dir" / "test.parquet"
            result = save_dataframe_safely(df, output_path, "Test save")

            assert result is True
            assert output_path.exists()
            assert output_path.parent.exists()
        finally:
            self.tearDown()

    def test_save_empty_dataframe(self):
        """Test saving an empty DataFrame."""
        self.setUp()
        try:
            df = pd.DataFrame()
            output_path = self.temp_path / "empty.parquet"
            result = save_dataframe_safely(df, output_path, "Test save")

            assert result is True
            assert output_path.exists()
        finally:
            self.tearDown()


class TestMainETLFunction:
    """Test cases for the main ETL function."""

    @patch("src.qaa_analysis.etl.basic_rev_etl.PipelineConfig")
    @patch("src.qaa_analysis.etl.basic_rev_etl.CostAwareBigQueryClient")
    @patch("src.qaa_analysis.etl.basic_rev_etl.QueryCache")
    @patch("src.qaa_analysis.etl.basic_rev_etl.get_blockworks_rev_query")
    @patch("src.qaa_analysis.etl.basic_rev_etl.get_rev_query_metadata")
    def test_main_successful_execution(
        self, mock_metadata, mock_query, mock_cache, mock_client, mock_config
    ):
        """Test successful execution of main ETL function."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.DEV_MODE = True
        mock_config_instance.MAX_DAYS_LOOKBACK = 1
        mock_config_instance.SAMPLE_RATE = 1.0
        mock_config_instance.get_date_filter.return_value = ("2024-01-01", "2024-01-01")
        mock_config_instance.PROCESSED_DATA_DIR = Path("/tmp/test")
        mock_config.return_value = mock_config_instance

        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance

        # Create a valid test DataFrame
        test_df = pd.DataFrame(
            {
                "address": ["0x123"],
                "tx_date": ["2024-01-01"],
                "tx_count": [5],
                "sum_gas_used": [100000],
                "total_rev_eth": [0.01],
                "tips_rev_eth": [0.002],
                "burned_rev_eth": [0.008],
                "avg_tx_fee_eth": [0.002],
            }
        )

        mock_cache_instance.get_or_compute.return_value = test_df
        mock_query.return_value = "SELECT * FROM test"
        mock_metadata.return_value = {
            "query_type": "blockworks_rev",
            "days_span": 1,
            "estimated_complexity": "medium",
        }

        # Mock the save operation
        with patch(
            "src.qaa_analysis.etl.basic_rev_etl.save_dataframe_safely"
        ) as mock_save:
            mock_save.return_value = True

            # Execute main function - should not raise any exceptions
            try:
                main()
            except Exception as e:
                pytest.fail(f"main() raised an exception: {e}")

    @patch("src.qaa_analysis.etl.basic_rev_etl.PipelineConfig")
    @patch("src.qaa_analysis.etl.basic_rev_etl.CostAwareBigQueryClient")
    @patch("src.qaa_analysis.etl.basic_rev_etl.QueryCache")
    def test_main_handles_empty_dataframe(self, mock_cache, mock_client, mock_config):
        """Test main function handles empty DataFrame gracefully."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.DEV_MODE = True
        mock_config_instance.MAX_DAYS_LOOKBACK = 1
        mock_config_instance.SAMPLE_RATE = 1.0
        mock_config_instance.get_date_filter.return_value = ("2024-01-01", "2024-01-01")
        mock_config.return_value = mock_config_instance

        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_cache_instance = Mock()
        mock_cache_instance.get_or_compute.return_value = (
            pd.DataFrame()
        )  # Empty DataFrame
        mock_cache.return_value = mock_cache_instance

        with patch(
            "src.qaa_analysis.etl.basic_rev_etl.get_blockworks_rev_query"
        ) as mock_query:
            with patch(
                "src.qaa_analysis.etl.basic_rev_etl.get_rev_query_metadata"
            ) as mock_metadata:
                mock_query.return_value = "SELECT * FROM test"
                mock_metadata.return_value = {
                    "query_type": "blockworks_rev",
                    "days_span": 1,
                    "estimated_complexity": "medium",
                }

                # Should handle empty DataFrame without crashing
                try:
                    main()
                except Exception as e:
                    pytest.fail(
                        f"main() should handle empty DataFrame gracefully, but raised: {e}"
                    )

    @patch("src.qaa_analysis.etl.basic_rev_etl.PipelineConfig")
    def test_main_handles_config_error(self, mock_config):
        """Test main function handles configuration errors."""
        # Make config initialization raise an exception
        mock_config.side_effect = Exception("Config error")

        with pytest.raises(Exception, match="Config error"):
            main()

    @patch("src.qaa_analysis.etl.basic_rev_etl.setup_logging")
    @patch("src.qaa_analysis.etl.basic_rev_etl.PipelineConfig")
    @patch("src.qaa_analysis.etl.basic_rev_etl.CostAwareBigQueryClient")
    @patch("src.qaa_analysis.etl.basic_rev_etl.QueryCache")
    def test_main_logs_appropriately(
        self, mock_cache, mock_client, mock_config, mock_logging
    ):
        """Test that main function logs appropriate messages."""
        # Setup mocks
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        mock_config_instance = Mock()
        mock_config_instance.DEV_MODE = True
        mock_config_instance.MAX_DAYS_LOOKBACK = 1
        mock_config_instance.SAMPLE_RATE = 1.0
        mock_config_instance.get_date_filter.return_value = ("2024-01-01", "2024-01-01")
        mock_config_instance.PROCESSED_DATA_DIR = Path("/tmp/test")
        mock_config.return_value = mock_config_instance

        mock_client.return_value = Mock()

        mock_cache_instance = Mock()
        mock_cache_instance.get_or_compute.return_value = pd.DataFrame()  # Empty result
        mock_cache.return_value = mock_cache_instance

        with patch("src.qaa_analysis.etl.basic_rev_etl.get_blockworks_rev_query"):
            with patch("src.qaa_analysis.etl.basic_rev_etl.get_rev_query_metadata"):
                main()

                # Verify that info logging was called
                assert mock_logger.info.called

                # Check for specific log messages
                log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
                assert any("Starting Basic REV ETL Process" in msg for msg in log_calls)
                assert any("completed successfully" in msg for msg in log_calls)


class TestETLIntegration:
    """Integration tests for ETL components."""

    def test_dataframe_validation_and_save_integration(self):
        """Test integration between validation and save functions."""
        # Create a valid DataFrame
        df = pd.DataFrame(
            {
                "address": ["0x123", "0x456"],
                "tx_date": ["2024-01-01", "2024-01-02"],
                "tx_count": [5, 3],
                "sum_gas_used": [100000, 75000],
                "total_rev_eth": [0.01, 0.008],
                "tips_rev_eth": [0.002, 0.001],
                "burned_rev_eth": [0.008, 0.007],
                "avg_tx_fee_eth": [0.002, 0.0027],
            }
        )

        # Validate first
        is_valid = validate_dataframe(df, "Integration test")
        assert is_valid is True

        # Then save
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "integration_test.parquet"
            save_success = save_dataframe_safely(df, output_path, "Integration test")
            assert save_success is True

            # Verify file exists and can be read
            assert output_path.exists()
            loaded_df = pd.read_parquet(output_path)
            assert len(loaded_df) == len(df)

    def test_invalid_dataframe_workflow(self):
        """Test workflow with invalid DataFrame."""
        # Create invalid DataFrame (missing columns)
        df = pd.DataFrame({"address": ["0x123"], "incomplete": ["data"]})

        # Validation should fail
        is_valid = validate_dataframe(df, "Invalid test")
        assert is_valid is False

        # Save should still work (validation is separate concern)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "invalid_test.parquet"
            save_success = save_dataframe_safely(df, output_path, "Invalid test")
            assert save_success is True  # Save operation itself succeeds
