"""
REV Analysis Module for QAA Analysis.

This module provides tools for analyzing Real Economic Value (REV) - 
the transaction fees paid by users - across behavioral clusters.
"""

from .rev_cluster_analyzer import RevClusterAnalyzer
from .rev_visualizations import RevVisualizer

__all__ = ['RevClusterAnalyzer', 'RevVisualizer']