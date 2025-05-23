"""
Local query cache for QAA Analysis.

This module provides caching functionality to store the results of expensive
computations (especially BigQuery queries) to local Parquet files, reducing
redundant calls and costs during development.
"""

import hashlib
import logging
import time
from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from ..config import PipelineConfig


class QueryCache:
    """
    Local file-based cache for query results using Parquet format.

    This cache stores Pandas DataFrames to local Parquet files with TTL
    (time-to-live) support to avoid re-computation of expensive operations
    like BigQuery queries during development and testing.
    """

    def __init__(self, config: PipelineConfig) -> None:
        """
        Initialize the query cache.

        Args:
            config: Pipeline configuration instance containing cache settings.
        """
        self.config = config
        self.cache_dir = config.LOCAL_CACHE_DIR
        self.ttl_hours = config.CACHE_TTL_HOURS
        self.logger = logging.getLogger(__name__)

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            f"Query cache initialized: {self.cache_dir} "
            f"(TTL: {self.ttl_hours} hours)"
        )

    def _generate_cache_key(self, query: str, params: Optional[dict] = None) -> str:
        """
        Generate a unique and deterministic cache key for a query and parameters.

        Args:
            query: SQL query string.
            params: Optional dictionary of parameters used in the query.

        Returns:
            Hexadecimal hash string to use as cache key.
        """
        # Combine query and params into a single string
        cache_input = query.strip()

        if params:
            # Sort params for deterministic hashing
            sorted_params = sorted(params.items())
            params_str = str(sorted_params)
            cache_input += f"__PARAMS__{params_str}"

        # Generate SHA256 hash and take first 16 characters for shorter filenames
        hash_object = hashlib.sha256(cache_input.encode("utf-8"))
        cache_key = hash_object.hexdigest()[:16]

        self.logger.debug(f"Generated cache key: {cache_key}")
        return cache_key

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Check if a cache file exists and is within the TTL period.

        Args:
            cache_path: Path to the cache file.

        Returns:
            True if cache is valid and fresh, False otherwise.
        """
        if not cache_path.exists():
            return False

        # Check file modification time
        mod_time = cache_path.stat().st_mtime
        current_time = time.time()
        age_hours = (current_time - mod_time) / 3600

        is_valid = age_hours < self.ttl_hours

        if is_valid:
            self.logger.debug(
                f"Cache hit: {cache_path.name} "
                f"(age: {age_hours:.1f}h, TTL: {self.ttl_hours}h)"
            )
        else:
            self.logger.debug(
                f"Cache expired: {cache_path.name} "
                f"(age: {age_hours:.1f}h, TTL: {self.ttl_hours}h)"
            )

        return is_valid

    def get_or_compute(
        self,
        query: str,
        compute_fn: Callable[[], pd.DataFrame],
        params: Optional[dict] = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Get cached result or compute and cache a new result.

        This method checks for a valid cached result first. If found and fresh,
        it returns the cached data. Otherwise, it calls the compute function,
        caches the result, and returns it.

        Args:
            query: SQL query string (used for cache key generation).
            compute_fn: Callable that returns a Pandas DataFrame to be cached.
                       This function should take no arguments.
            params: Optional dictionary of parameters used in the query.
            force_refresh: If True, ignore existing cache and re-compute.

        Returns:
            Pandas DataFrame with the query results.

        Example:
            >>> cache = QueryCache(config)
            >>> def fetch_data():
            ...     return client.safe_query("SELECT * FROM my_table")
            >>> df = cache.get_or_compute(
            ...     query="SELECT * FROM my_table",
            ...     compute_fn=fetch_data
            ... )
        """
        # Generate cache key and file path
        cache_key = self._generate_cache_key(query, params)
        cache_filename = f"query_{cache_key}.parquet"
        cache_path = self.cache_dir / cache_filename

        # Check for valid cache (unless force refresh is requested)
        if not force_refresh and self._is_cache_valid(cache_path):
            try:
                self.logger.info(f"Loading cached result: {cache_filename}")
                cached_df = pd.read_parquet(cache_path)
                self.logger.info(f"Cache hit: {len(cached_df):,} rows loaded")
                return cached_df

            except Exception as e:
                self.logger.warning(
                    f"Failed to load cache file {cache_filename}: {e}. "
                    "Will re-compute."
                )

        # Cache miss or force refresh - compute new result
        if force_refresh:
            self.logger.info(f"Force refresh requested for: {cache_filename}")
        else:
            self.logger.info(f"Cache miss for: {cache_filename}")

        self.logger.info("Computing new result...")

        try:
            # Call the compute function
            result_df = compute_fn()

            # Validate result
            if result_df is None:
                self.logger.warning("Compute function returned None")
                return pd.DataFrame()  # Return empty DataFrame

            if not isinstance(result_df, pd.DataFrame):
                raise TypeError(
                    f"Compute function must return a pandas DataFrame, "
                    f"got {type(result_df)}"
                )

            if result_df.empty:
                self.logger.warning("Compute function returned empty DataFrame")
            else:
                # Cache the result
                try:
                    result_df.to_parquet(cache_path, compression="snappy", index=False)

                    self.logger.info(
                        f"Result cached: {cache_filename} "
                        f"({len(result_df):,} rows, "
                        f"{cache_path.stat().st_size / 1024 / 1024:.1f} MB)"
                    )

                except Exception as e:
                    self.logger.error(f"Failed to cache result: {e}")
                    # Continue without caching - don't fail the operation

            return result_df

        except Exception as e:
            self.logger.error(f"Compute function failed: {e}")
            raise

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache files matching an optional pattern.

        Args:
            pattern: Optional glob pattern to match files. If None, clears all
                    cache files.

        Returns:
            Number of files deleted.
        """
        if pattern:
            files_to_delete = list(self.cache_dir.glob(pattern))
        else:
            files_to_delete = list(self.cache_dir.glob("query_*.parquet"))

        deleted_count = 0
        for file_path in files_to_delete:
            try:
                file_path.unlink()
                deleted_count += 1
                self.logger.debug(f"Deleted cache file: {file_path.name}")
            except Exception as e:
                self.logger.warning(f"Failed to delete {file_path.name}: {e}")

        self.logger.info(f"Cleared {deleted_count} cache files")
        return deleted_count

    def get_cache_stats(self) -> dict:
        """
        Get statistics about the current cache.

        Returns:
            Dictionary with cache statistics including file count, total size,
            and age distribution.
        """
        cache_files = list(self.cache_dir.glob("query_*.parquet"))

        if not cache_files:
            return {
                "file_count": 0,
                "total_size_mb": 0.0,
                "oldest_file_hours": 0.0,
                "newest_file_hours": 0.0,
            }

        current_time = time.time()
        total_size = 0
        ages = []

        for file_path in cache_files:
            try:
                stat = file_path.stat()
                total_size += stat.st_size
                age_hours = (current_time - stat.st_mtime) / 3600
                ages.append(age_hours)
            except Exception as e:
                self.logger.warning(f"Failed to stat {file_path.name}: {e}")

        stats = {
            "file_count": len(cache_files),
            "total_size_mb": total_size / 1024 / 1024,
            "oldest_file_hours": max(ages) if ages else 0.0,
            "newest_file_hours": min(ages) if ages else 0.0,
            "expired_files": sum(1 for age in ages if age > self.ttl_hours),
        }

        return stats

    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_cache_stats()
        return (
            f"QueryCache("
            f"dir='{self.cache_dir}', "
            f"ttl={self.ttl_hours}h, "
            f"files={stats['file_count']}, "
            f"size={stats['total_size_mb']:.1f}MB"
            f")"
        )
