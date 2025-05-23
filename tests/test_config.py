"""
Tests for the PipelineConfig class.

This module tests configuration loading, environment variable handling,
default values, and date filtering functionality.
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from qaa_analysis.config import PipelineConfig


class TestPipelineConfig:
    """Test suite for PipelineConfig class."""

    def test_config_with_minimal_env(self):
        """Test configuration with minimal required environment variables."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}, clear=True):
            config = PipelineConfig()

            assert config.PROJECT_ID == "test-project"
            assert config.DEV_MODE is True  # Default
            assert config.MAX_DAYS_LOOKBACK == 1  # Dev mode default
            assert config.SAMPLE_RATE == 1.0  # Dev mode default
            assert config.MAX_BYTES_BILLED == 10 * 1024**3  # 10GB default
            assert config.REQUIRE_PARTITION_FILTER is True
            assert config.CACHE_TTL_HOURS == 24

    def test_config_with_full_env(self):
        """Test configuration with all environment variables set."""
        env_vars = {
            "GCP_PROJECT_ID": "prod-project",
            "DEV_MODE": "False",
            "BIGQUERY_MAX_BYTES_BILLED": "21474836480",  # 20GB
            "CACHE_TTL_HOURS": "48",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = PipelineConfig()

            assert config.PROJECT_ID == "prod-project"
            assert config.DEV_MODE is False
            assert config.MAX_DAYS_LOOKBACK == 30  # Prod mode default
            assert config.SAMPLE_RATE == 0.1  # Prod mode default
            assert config.MAX_BYTES_BILLED == 21474836480
            assert config.CACHE_TTL_HOURS == 48

    def test_dev_mode_parsing(self):
        """Test various DEV_MODE value parsing."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("invalid", False),
        ]

        for dev_mode_value, expected in test_cases:
            env_vars = {"GCP_PROJECT_ID": "test-project", "DEV_MODE": dev_mode_value}

            with patch.dict(os.environ, env_vars, clear=True):
                config = PipelineConfig()
                assert (
                    config.DEV_MODE == expected
                ), f"Failed for DEV_MODE='{dev_mode_value}'"

    def test_invalid_numeric_values(self):
        """Test handling of invalid numeric environment variables."""
        env_vars = {
            "GCP_PROJECT_ID": "test-project",
            "BIGQUERY_MAX_BYTES_BILLED": "not-a-number",
            "CACHE_TTL_HOURS": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = PipelineConfig()

            # Should fall back to defaults
            assert config.MAX_BYTES_BILLED == 10 * 1024**3  # 10GB default
            assert config.CACHE_TTL_HOURS == 24  # Default

    def test_get_date_filter_default(self):
        """Test date filter with default lookback period."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}, clear=True):
            config = PipelineConfig()

            start_date, end_date = config.get_date_filter()

            # Parse the returned ISO dates
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()

            # End date should be yesterday
            expected_end = datetime.now(timezone.utc).date() - timedelta(days=1)
            assert end == expected_end

            # Start date should be MAX_DAYS_LOOKBACK - 1 days before end
            expected_start = expected_end - timedelta(days=config.MAX_DAYS_LOOKBACK - 1)
            assert start == expected_start

    def test_get_date_filter_custom_days(self):
        """Test date filter with custom lookback period."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}, clear=True):
            config = PipelineConfig()

            custom_days = 7
            start_date, end_date = config.get_date_filter(days_back=custom_days)

            # Parse the returned ISO dates
            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()

            # End date should be yesterday
            expected_end = datetime.now(timezone.utc).date() - timedelta(days=1)
            assert end == expected_end

            # Start date should be custom_days - 1 days before end
            expected_start = expected_end - timedelta(days=custom_days - 1)
            assert start == expected_start

    def test_config_repr(self):
        """Test string representation of configuration."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}, clear=True):
            config = PipelineConfig()

            repr_str = repr(config)

            assert "PipelineConfig" in repr_str
            assert "test-project" in repr_str
            assert "DEV_MODE=True" in repr_str
            assert "MAX_DAYS_LOOKBACK=1" in repr_str
            assert "SAMPLE_RATE=1.0" in repr_str


if __name__ == "__main__":
    pytest.main([__file__])
