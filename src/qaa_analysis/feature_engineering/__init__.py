"""
Feature Engineering Module for QAA Analysis.

This module provides comprehensive feature extraction capabilities for transforming
raw DeFi interaction data into behavioral features suitable for machine learning clustering.
"""

from .feature_extractor import FeatureExtractor
from .interaction_aggregator import InteractionAggregator
from .feature_pipeline import FeaturePipeline

__all__ = [
    "FeatureExtractor",
    "InteractionAggregator", 
    "FeaturePipeline"
] 