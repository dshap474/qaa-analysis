"""
Safe value conversion utilities for feature extraction.

This module provides utilities to safely convert pandas values to Python types,
handling NA/NaN values appropriately.
"""

import pandas as pd
import numpy as np
from typing import Union, Any


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float, handling NA/NaN values.
    
    Args:
        value: Value to convert (can be pandas scalar, numpy scalar, or Python type)
        default: Default value to return for NA/NaN values
        
    Returns:
        Float value or default if conversion fails
    """
    try:
        # Handle pandas NA
        if pd.isna(value):
            return default
        
        # Handle numpy nan
        if isinstance(value, (np.floating, float)) and np.isnan(value):
            return default
            
        # Convert to float
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int, handling NA/NaN values.
    
    Args:
        value: Value to convert (can be pandas scalar, numpy scalar, or Python type)
        default: Default value to return for NA/NaN values
        
    Returns:
        Integer value or default if conversion fails
    """
    try:
        # Handle pandas NA
        if pd.isna(value):
            return default
        
        # Handle numpy nan
        if isinstance(value, (np.floating, float)) and np.isnan(value):
            return default
            
        # Convert to int
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_series_sum(series: pd.Series, default: float = 0.0) -> float:
    """
    Safely compute sum of a pandas Series, handling all-NA series.
    
    Args:
        series: Pandas Series to sum
        default: Default value if series is empty or all NA
        
    Returns:
        Sum as float or default
    """
    if series.empty or series.isna().all():
        return default
    return safe_float(series.sum(), default)


def safe_series_mean(series: pd.Series, default: float = 0.0) -> float:
    """
    Safely compute mean of a pandas Series, handling all-NA series.
    
    Args:
        series: Pandas Series to average
        default: Default value if series is empty or all NA
        
    Returns:
        Mean as float or default
    """
    if series.empty or series.isna().all():
        return default
    return safe_float(series.mean(), default)


def safe_series_median(series: pd.Series, default: float = 0.0) -> float:
    """
    Safely compute median of a pandas Series, handling all-NA series.
    
    Args:
        series: Pandas Series
        default: Default value if series is empty or all NA
        
    Returns:
        Median as float or default
    """
    if series.empty or series.isna().all():
        return default
    return safe_float(series.median(), default)


def safe_series_std(series: pd.Series, default: float = 0.0) -> float:
    """
    Safely compute standard deviation of a pandas Series, handling all-NA series.
    
    Args:
        series: Pandas Series
        default: Default value if series is empty or all NA
        
    Returns:
        Standard deviation as float or default
    """
    if series.empty or series.isna().all() or len(series) < 2:
        return default
    return safe_float(series.std(), default)


def safe_series_max(series: pd.Series, default: float = 0.0) -> float:
    """
    Safely compute max of a pandas Series, handling all-NA series.
    
    Args:
        series: Pandas Series
        default: Default value if series is empty or all NA
        
    Returns:
        Max as float or default
    """
    if series.empty or series.isna().all():
        return default
    return safe_float(series.max(), default)


def safe_series_min(series: pd.Series, default: float = 0.0) -> float:
    """
    Safely compute min of a pandas Series, handling all-NA series.
    
    Args:
        series: Pandas Series
        default: Default value if series is empty or all NA
        
    Returns:
        Min as float or default
    """
    if series.empty or series.isna().all():
        return default
    return safe_float(series.min(), default)