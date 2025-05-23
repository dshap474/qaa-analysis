"""
Cost-aware BigQuery client for QAA Analysis.

This module provides a wrapper around the Google BigQuery client that enforces
cost controls by performing mandatory dry runs, estimating query costs, and
checking against billing limits before executing queries.
"""

import logging
from typing import Optional, Tuple

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError

from ..config import PipelineConfig


class QueryCostError(Exception):
    """Raised when a query exceeds the maximum allowed cost."""

    pass


class CostAwareBigQueryClient:
    """
    A wrapper around Google BigQuery client with built-in cost controls.

    This client performs mandatory dry runs to estimate query costs before
    execution and enforces billing limits to prevent accidental expensive
    queries during development and production.
    """

    # BigQuery on-demand pricing (as of 2024)
    COST_PER_TIB_USD = 6.25
    BYTES_PER_TIB = 1024**4

    def __init__(self, config: PipelineConfig) -> None:
        """
        Initialize the cost-aware BigQuery client.

        Args:
            config: Pipeline configuration instance containing project settings
                   and cost control parameters.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        try:
            self.client = bigquery.Client(project=self.config.PROJECT_ID)
            self.logger.info(
                f"BigQuery client initialized for project: {self.config.PROJECT_ID}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize BigQuery client: {e}")
            raise

    def estimate_query_cost(self, query: str) -> Tuple[int, float]:
        """
        Estimate the cost of a BigQuery query using a dry run.

        Args:
            query: SQL query string to estimate.

        Returns:
            Tuple of (bytes_billed_estimate, cost_usd_estimate).

        Raises:
            GoogleCloudError: If the dry run fails.
            QueryCostError: If the estimated cost exceeds limits.
        """
        # Configure dry run job
        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False,  # Get fresh estimate
            maximum_bytes_billed=self.config.MAX_BYTES_BILLED,
        )

        try:
            # Perform dry run
            query_job = self.client.query(query, job_config=job_config)

            # Get estimated bytes processed
            bytes_estimate = query_job.total_bytes_processed or 0

            # Calculate cost estimate
            cost_estimate = (
                bytes_estimate / self.BYTES_PER_TIB
            ) * self.COST_PER_TIB_USD

            self.logger.info(
                f"Query cost estimate: {bytes_estimate:,} bytes "
                f"(${cost_estimate:.4f} USD)"
            )

            return bytes_estimate, cost_estimate

        except GoogleCloudError as e:
            self.logger.error(f"Dry run failed: {e}")
            raise

    def safe_query(
        self, query: str, job_config_customizations: Optional[dict] = None
    ) -> Optional[pd.DataFrame]:
        """
        Execute a BigQuery query with cost controls and safety checks.

        This method performs a dry run first to estimate costs, then executes
        the query only if it's within the configured billing limits.

        Args:
            query: SQL query string to execute.
            job_config_customizations: Optional dictionary of additional
                                     job configuration parameters.

        Returns:
            Pandas DataFrame with query results, or None if query was blocked.

        Raises:
            QueryCostError: If the estimated cost exceeds MAX_BYTES_BILLED.
            GoogleCloudError: If the query execution fails.
        """
        # Step 1: Estimate query cost
        try:
            bytes_estimate, cost_estimate = self.estimate_query_cost(query)
        except Exception as e:
            self.logger.error(f"Cost estimation failed: {e}")
            raise

        # Step 2: Check against billing limits
        if bytes_estimate > self.config.MAX_BYTES_BILLED:
            error_msg = (
                f"Query exceeds maximum bytes billed limit. "
                f"Estimated: {bytes_estimate:,} bytes, "
                f"Limit: {self.config.MAX_BYTES_BILLED:,} bytes "
                f"(${cost_estimate:.4f} USD)"
            )
            self.logger.error(error_msg)
            raise QueryCostError(error_msg)

        # Step 3: Execute the query
        self.logger.info(
            f"Proceeding with query execution "
            f"(${cost_estimate:.4f} USD estimated cost)"
        )

        # Configure actual job
        job_config = bigquery.QueryJobConfig(
            dry_run=False,
            use_query_cache=True,  # Use cache for repeated queries
            maximum_bytes_billed=self.config.MAX_BYTES_BILLED,
        )

        # Apply any custom job configuration
        if job_config_customizations:
            for key, value in job_config_customizations.items():
                if hasattr(job_config, key):
                    setattr(job_config, key, value)
                else:
                    self.logger.warning(f"Unknown job config parameter: {key}")

        try:
            # Execute query
            query_job = self.client.query(query, job_config=job_config)

            # Wait for completion and get results
            results_df = query_job.to_dataframe()

            # Log actual usage
            actual_bytes = query_job.total_bytes_billed or 0
            actual_cost = (actual_bytes / self.BYTES_PER_TIB) * self.COST_PER_TIB_USD

            self.logger.info(
                f"Query completed successfully. "
                f"Actual usage: {actual_bytes:,} bytes "
                f"(${actual_cost:.4f} USD), "
                f"Rows returned: {len(results_df):,}"
            )

            return results_df

        except GoogleCloudError as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during query execution: {e}")
            raise

    def get_table_info(self, table_id: str) -> dict:
        """
        Get metadata information about a BigQuery table.

        Args:
            table_id: Fully qualified table ID (project.dataset.table).

        Returns:
            Dictionary containing table metadata.
        """
        try:
            table = self.client.get_table(table_id)

            info = {
                "table_id": table.table_id,
                "dataset_id": table.dataset_id,
                "project": table.project,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "created": table.created,
                "modified": table.modified,
                "schema": [
                    {
                        "name": field.name,
                        "field_type": field.field_type,
                        "mode": field.mode,
                        "description": field.description,
                    }
                    for field in table.schema
                ],
            }

            self.logger.debug(f"Retrieved metadata for table: {table_id}")
            return info

        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_id}: {e}")
            raise

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"CostAwareBigQueryClient("
            f"project='{self.config.PROJECT_ID}', "
            f"max_bytes_billed={self.config.MAX_BYTES_BILLED:,}"
            f")"
        )
