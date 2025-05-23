"""
Pipeline configuration management for QAA Analysis.

This module provides centralized configuration management with environment variable
loading, type safety, and sensible defaults for development and production modes.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv


class PipelineConfig:
    """
    Centralized configuration management for the QAA pipeline.

    Loads configuration from environment variables with sensible defaults
    and provides typed access to all pipeline settings including BigQuery
    cost controls, caching parameters, and data processing settings.
    """

    def __init__(self) -> None:
        """
        Initialize pipeline configuration by loading environment variables
        and setting up default values based on development mode.
        """
        # Load environment variables from .env file
        load_dotenv()

        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Load and validate required settings
        self._load_project_settings()
        self._load_mode_settings()
        self._load_bigquery_settings()
        self._load_cache_settings()
        self._setup_directories()

        self.logger.info(
            f"Pipeline configuration initialized - DEV_MODE: {self.DEV_MODE}"
        )

    def _load_project_settings(self) -> None:
        """Load and validate Google Cloud project settings."""
        self.PROJECT_ID = os.getenv("GCP_PROJECT_ID")
        if not self.PROJECT_ID:
            raise ValueError(
                "GCP_PROJECT_ID environment variable is required. "
                "Please set it in your .env file or environment."
            )

    def _load_mode_settings(self) -> None:
        """Load development mode and related settings."""
        dev_mode_str = os.getenv("DEV_MODE", "True").lower()
        self.DEV_MODE = dev_mode_str in ("true", "1", "yes", "on")

        if not dev_mode_str:
            self.logger.warning("DEV_MODE not set, defaulting to True")

        # Set mode-dependent defaults
        self.MAX_DAYS_LOOKBACK = 1 if self.DEV_MODE else 30
        self.SAMPLE_RATE = 1.0 if self.DEV_MODE else 0.1

    def _load_bigquery_settings(self) -> None:
        """Load BigQuery cost control and query settings."""
        # Default to 10GB if not set or invalid
        default_max_bytes = 10 * 1024**3  # 10GB

        try:
            max_bytes_str = os.getenv("BIGQUERY_MAX_BYTES_BILLED")
            if max_bytes_str:
                self.MAX_BYTES_BILLED = int(max_bytes_str)
            else:
                self.MAX_BYTES_BILLED = default_max_bytes
                self.logger.warning(
                    f"BIGQUERY_MAX_BYTES_BILLED not set, defaulting to {default_max_bytes:,} bytes"
                )
        except (ValueError, TypeError):
            self.MAX_BYTES_BILLED = default_max_bytes
            self.logger.warning(
                f"Invalid BIGQUERY_MAX_BYTES_BILLED value, defaulting to {default_max_bytes:,} bytes"
            )

        self.REQUIRE_PARTITION_FILTER = True

    def _load_cache_settings(self) -> None:
        """Load caching configuration settings."""
        try:
            cache_ttl_str = os.getenv("CACHE_TTL_HOURS", "24")
            self.CACHE_TTL_HOURS = int(cache_ttl_str)
        except (ValueError, TypeError):
            self.CACHE_TTL_HOURS = 24
            self.logger.warning("Invalid CACHE_TTL_HOURS value, defaulting to 24 hours")

    def _setup_directories(self) -> None:
        """Setup and create necessary directories for data storage and caching."""
        # Determine project root (assuming we're in src/qaa_analysis/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

        # Setup cache directory
        self.LOCAL_CACHE_DIR = project_root / "data" / "cache"
        self.LOCAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Setup processed data directory
        self.PROCESSED_DATA_DIR = project_root / "data" / "processed"
        self.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Cache directory: {self.LOCAL_CACHE_DIR}")
        self.logger.info(f"Processed data directory: {self.PROCESSED_DATA_DIR}")

    def get_date_filter(self, days_back: Optional[int] = None) -> Tuple[str, str]:
        """
        Calculate start and end dates for BigQuery queries.

        Args:
            days_back: Number of days to look back. If None, uses MAX_DAYS_LOOKBACK.

        Returns:
            Tuple of (start_date_iso, end_date_iso) strings in YYYY-MM-DD format.

        Example:
            >>> config = PipelineConfig()
            >>> start, end = config.get_date_filter(7)
            >>> print(f"Query range: {start} to {end}")
        """
        if days_back is None:
            days_back = self.MAX_DAYS_LOOKBACK

        # End date is yesterday (UTC) to ensure data completeness
        end_date = datetime.now(timezone.utc).date() - timedelta(days=1)

        # Start date is days_back - 1 days before end_date
        start_date = end_date - timedelta(days=days_back - 1)

        start_date_iso = start_date.isoformat()
        end_date_iso = end_date.isoformat()

        self.logger.debug(
            f"Date filter: {start_date_iso} to {end_date_iso} ({days_back} days)"
        )

        return start_date_iso, end_date_iso

    def __repr__(self) -> str:
        """String representation of configuration for debugging."""
        return (
            f"PipelineConfig("
            f"PROJECT_ID='{self.PROJECT_ID}', "
            f"DEV_MODE={self.DEV_MODE}, "
            f"MAX_DAYS_LOOKBACK={self.MAX_DAYS_LOOKBACK}, "
            f"SAMPLE_RATE={self.SAMPLE_RATE}, "
            f"MAX_BYTES_BILLED={self.MAX_BYTES_BILLED:,}"
            f")"
        )


# Global configuration instance for easy access
# Users can import this directly: from qaa_analysis.config import config
config = PipelineConfig()
