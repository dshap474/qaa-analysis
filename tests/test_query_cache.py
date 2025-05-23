"""
Tests for the QueryCache class.

This module tests local Parquet file caching functionality including
cache hits/misses, TTL behavior, and cache management operations.
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from qaa_analysis.cache.query_cache import QueryCache
from qaa_analysis.config import PipelineConfig


class TestQueryCache:
    """Test suite for QueryCache class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary directory for cache testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_config(self, temp_cache_dir):
        """Create a mock configuration with temporary cache directory."""
        with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}, clear=True):
            config = PipelineConfig()
            config.LOCAL_CACHE_DIR = temp_cache_dir
            config.CACHE_TTL_HOURS = 1  # 1 hour for testing
            return config

    @pytest.fixture
    def query_cache(self, mock_config):
        """Create a QueryCache instance for testing."""
        return QueryCache(mock_config)

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "value": [10.5, 20.3, 30.1, 40.7, 50.9],
            }
        )

    def test_cache_initialization(self, query_cache, temp_cache_dir):
        """Test cache initialization and directory setup."""
        assert query_cache.cache_dir == temp_cache_dir
        assert query_cache.ttl_hours == 1
        assert temp_cache_dir.exists()

    def test_generate_cache_key_consistency(self, query_cache):
        """Test that cache key generation is consistent and deterministic."""
        query = "SELECT * FROM test_table WHERE date = '2024-01-01'"
        params = {"limit": 100, "offset": 0}

        # Generate key multiple times
        key1 = query_cache._generate_cache_key(query, params)
        key2 = query_cache._generate_cache_key(query, params)
        key3 = query_cache._generate_cache_key(query, params)

        assert key1 == key2 == key3
        assert len(key1) == 16  # Should be truncated to 16 chars

    def test_generate_cache_key_different_queries(self, query_cache):
        """Test that different queries generate different cache keys."""
        query1 = "SELECT * FROM table1"
        query2 = "SELECT * FROM table2"

        key1 = query_cache._generate_cache_key(query1)
        key2 = query_cache._generate_cache_key(query2)

        assert key1 != key2

    def test_generate_cache_key_different_params(self, query_cache):
        """Test that different parameters generate different cache keys."""
        query = "SELECT * FROM test_table"
        params1 = {"limit": 100}
        params2 = {"limit": 200}

        key1 = query_cache._generate_cache_key(query, params1)
        key2 = query_cache._generate_cache_key(query, params2)

        assert key1 != key2

    def test_cache_miss_and_compute(self, query_cache, sample_dataframe):
        """Test cache miss scenario where data is computed and cached."""
        query = "SELECT * FROM test_table"
        compute_called = False

        def compute_fn():
            nonlocal compute_called
            compute_called = True
            return sample_dataframe.copy()

        # First call should be a cache miss
        result_df = query_cache.get_or_compute(query, compute_fn)

        assert compute_called
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 5
        assert list(result_df.columns) == ["id", "name", "value"]

        # Verify cache file was created
        cache_files = list(query_cache.cache_dir.glob("query_*.parquet"))
        assert len(cache_files) == 1

    def test_cache_hit(self, query_cache, sample_dataframe):
        """Test cache hit scenario where cached data is returned."""
        query = "SELECT * FROM test_table"
        compute_call_count = 0

        def compute_fn():
            nonlocal compute_call_count
            compute_call_count += 1
            return sample_dataframe.copy()

        # First call - cache miss
        result1 = query_cache.get_or_compute(query, compute_fn)
        assert compute_call_count == 1

        # Second call - should be cache hit
        result2 = query_cache.get_or_compute(query, compute_fn)
        assert compute_call_count == 1  # Should not increment

        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)

        def test_cache_expiry(self, query_cache, sample_dataframe):
            """Test cache expiry based on TTL."""  # Set very short TTL for testing        query_cache.ttl_hours = 0.0001  # ~0.36 seconds                query = "SELECT * FROM test_table"        compute_call_count = 0                def compute_fn():            nonlocal compute_call_count            compute_call_count += 1            return sample_dataframe.copy()                # First call - cache miss        query_cache.get_or_compute(query, compute_fn)        assert compute_call_count == 1                # Wait for cache to expire        time.sleep(0.5)  # 500ms should be enough for 0.36s TTL                # Second call - should be cache miss due to expiry        query_cache.get_or_compute(query, compute_fn)        assert compute_call_count == 2

    def test_force_refresh(self, query_cache, sample_dataframe):
        """Test force refresh functionality."""
        query = "SELECT * FROM test_table"
        compute_call_count = 0

        def compute_fn():
            nonlocal compute_call_count
            compute_call_count += 1
            df = sample_dataframe.copy()
            df["call_count"] = compute_call_count  # Add call count to distinguish calls
            return df

        # First call - cache miss
        result1 = query_cache.get_or_compute(query, compute_fn)
        assert compute_call_count == 1
        assert result1["call_count"].iloc[0] == 1

        # Second call with force_refresh=True
        result2 = query_cache.get_or_compute(query, compute_fn, force_refresh=True)
        assert compute_call_count == 2
        assert result2["call_count"].iloc[0] == 2

    def test_compute_function_returns_none(self, query_cache):
        """Test handling when compute function returns None."""
        query = "SELECT * FROM empty_table"

        def compute_fn():
            return None

        result = query_cache.get_or_compute(query, compute_fn)

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_compute_function_returns_wrong_type(self, query_cache):
        """Test handling when compute function returns wrong type."""
        query = "SELECT * FROM test_table"

        def compute_fn():
            return "not a dataframe"

        with pytest.raises(TypeError, match="must return a pandas DataFrame"):
            query_cache.get_or_compute(query, compute_fn)

    def test_compute_function_raises_exception(self, query_cache):
        """Test handling when compute function raises an exception."""
        query = "SELECT * FROM test_table"

        def compute_fn():
            raise ValueError("Computation failed")

        with pytest.raises(ValueError, match="Computation failed"):
            query_cache.get_or_compute(query, compute_fn)

    def test_cache_with_parameters(self, query_cache, sample_dataframe):
        """Test caching with query parameters."""
        query = "SELECT * FROM test_table WHERE id > ?"
        params1 = {"threshold": 2}
        params2 = {"threshold": 3}

        compute_call_count = 0

        def compute_fn():
            nonlocal compute_call_count
            compute_call_count += 1
            return sample_dataframe.copy()

        # Call with first set of parameters
        query_cache.get_or_compute(query, compute_fn, params=params1)
        assert compute_call_count == 1

        # Call with same parameters - should be cache hit
        query_cache.get_or_compute(query, compute_fn, params=params1)
        assert compute_call_count == 1

        # Call with different parameters - should be cache miss
        query_cache.get_or_compute(query, compute_fn, params=params2)
        assert compute_call_count == 2

    def test_clear_cache_all(self, query_cache, sample_dataframe):
        """Test clearing all cache files."""
        # Create multiple cache entries
        queries = [
            "SELECT * FROM table1",
            "SELECT * FROM table2",
            "SELECT * FROM table3",
        ]

        def compute_fn():
            return sample_dataframe.copy()

        for query in queries:
            query_cache.get_or_compute(query, compute_fn)

        # Verify cache files exist
        cache_files = list(query_cache.cache_dir.glob("query_*.parquet"))
        assert len(cache_files) == 3

        # Clear all cache
        deleted_count = query_cache.clear_cache()
        assert deleted_count == 3

        # Verify cache files are gone
        cache_files = list(query_cache.cache_dir.glob("query_*.parquet"))
        assert len(cache_files) == 0

    def test_clear_cache_with_pattern(self, query_cache, sample_dataframe):
        """Test clearing cache files with a specific pattern."""

        # Create cache files with different names
        def compute_fn():
            return sample_dataframe.copy()

        query_cache.get_or_compute("SELECT * FROM table1", compute_fn)
        query_cache.get_or_compute("SELECT * FROM table2", compute_fn)

        # Manually create a non-query cache file
        other_file = query_cache.cache_dir / "other_cache.parquet"
        sample_dataframe.to_parquet(other_file)

        # Clear only query cache files
        deleted_count = query_cache.clear_cache("query_*.parquet")
        assert deleted_count == 2

        # Verify other file still exists
        assert other_file.exists()

    def test_get_cache_stats_empty(self, query_cache):
        """Test cache statistics when cache is empty."""
        stats = query_cache.get_cache_stats()

        assert stats["file_count"] == 0
        assert stats["total_size_mb"] == 0.0
        assert stats["oldest_file_hours"] == 0.0
        assert stats["newest_file_hours"] == 0.0

    def test_get_cache_stats_with_files(self, query_cache, sample_dataframe):
        """Test cache statistics with cached files."""

        def compute_fn():
            return sample_dataframe.copy()

        # Create a few cache entries
        query_cache.get_or_compute("SELECT * FROM table1", compute_fn)
        query_cache.get_or_compute("SELECT * FROM table2", compute_fn)

        stats = query_cache.get_cache_stats()

        assert stats["file_count"] == 2
        assert stats["total_size_mb"] > 0
        assert stats["oldest_file_hours"] >= 0
        assert stats["newest_file_hours"] >= 0
        assert stats["oldest_file_hours"] >= stats["newest_file_hours"]

    def test_cache_repr(self, query_cache):
        """Test string representation of cache."""
        repr_str = repr(query_cache)

        assert "QueryCache" in repr_str
        assert str(query_cache.cache_dir) in repr_str
        assert "ttl=1h" in repr_str
        assert "files=" in repr_str
        assert "size=" in repr_str

    def test_corrupted_cache_file_handling(self, query_cache, sample_dataframe):
        """Test handling of corrupted cache files."""
        query = "SELECT * FROM test_table"

        def compute_fn():
            return sample_dataframe.copy()

        # Create a cache entry
        query_cache.get_or_compute(query, compute_fn)

        # Corrupt the cache file
        cache_files = list(query_cache.cache_dir.glob("query_*.parquet"))
        assert len(cache_files) == 1

        with open(cache_files[0], "w") as f:
            f.write("corrupted data")

        # Should handle corruption gracefully and re-compute
        compute_call_count = 0

        def compute_fn_with_counter():
            nonlocal compute_call_count
            compute_call_count += 1
            return sample_dataframe.copy()

        result = query_cache.get_or_compute(query, compute_fn_with_counter)

        assert compute_call_count == 1  # Should have re-computed
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5


if __name__ == "__main__":
    pytest.main([__file__])
