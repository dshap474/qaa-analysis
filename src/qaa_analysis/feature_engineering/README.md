# Feature Engineering Module

## Overview

The Feature Engineering module transforms raw DeFi interaction data into a comprehensive set of behavioral features suitable for machine learning clustering. This module implements Phase 2.4 of the QAA Analysis project.

## Architecture

### Core Components

1. **`FeatureExtractor`** - Abstract base class defining the interface for all feature extractors
2. **`InteractionAggregator`** - Loads and groups interaction data by user
3. **`ProtocolFeatures`** - Extracts protocol usage patterns and diversity metrics
4. **`TemporalFeatures`** - Extracts time-based behavioral patterns
5. **`ValueFeatures`** - Extracts transaction value and gas usage patterns
6. **`FeaturePipeline`** - Orchestrates the complete feature extraction process

### Data Flow

```
Raw Interactions (Parquet)
    ↓
InteractionAggregator
    ↓
Feature Extractors (Parallel)
    ├── ProtocolFeatures
    ├── TemporalFeatures
    └── ValueFeatures
    ↓
FeaturePipeline
    ↓
User Feature Matrix (Parquet)
```

## Features Extracted

### Protocol Features (27 features)
- **Protocol Interaction Counts**: DEX, Lending, Staking, Yield Farming, Bridge, etc.
- **Application Counts**: Uniswap, Aave, Compound, Curve, etc.
- **Diversity Metrics**: Shannon entropy, Herfindahl index
- **Usage Ratios**: DEX ratio, lending ratio, DeFi-native ratio

### Temporal Features (18 features)
- **Recency**: Days since last/first transaction
- **Activity Frequency**: Total interactions, active days, activity duration
- **Activity Patterns**: Weekend/night activity ratios, business hours usage
- **Lifecycle Metrics**: Early adopter score, activity trend, recent activity ratio

### Value Features (22 features)
- **ETH Value Metrics**: Total, average, median, max transaction values
- **Value Categories**: High-value, micro-transaction, zero-value ratios
- **Gas Usage**: Total gas, average gas per transaction, gas costs
- **Efficiency Metrics**: Gas efficiency, value-to-cost ratios
- **Sophistication Indicators**: Complex transaction ratio, premium gas usage

## Usage

### Basic Usage

```python
from pathlib import Path
from qaa_analysis.feature_engineering import FeaturePipeline

# Initialize pipeline
pipeline = FeaturePipeline(
    output_dir=Path("data/features"),
    chunk_size=1000
)

# Run feature extraction
feature_matrix_path = pipeline.run_pipeline(
    interaction_data_path=Path("data/defi_interactions_enriched.parquet"),
    output_filename="user_behavioral_features.parquet"
)

# Load results
feature_df = pipeline.load_feature_matrix(feature_matrix_path)
print(f"Extracted {feature_df.shape[1]-1} features for {len(feature_df)} users")
```

### Individual Extractor Usage

```python
from qaa_analysis.feature_engineering import ProtocolFeatures
import pandas as pd

# Load user interaction data
user_interactions = pd.read_parquet("user_data.parquet")

# Extract protocol features
extractor = ProtocolFeatures()
features = extractor.extract_features(user_interactions)

print(f"DEX interactions: {features['dex_interactions']}")
print(f"Protocol diversity: {features['protocol_diversity_shannon']}")
```

## Input Data Requirements

The feature extraction pipeline expects interaction data with the following columns:

### Required Columns
- `transaction_hash`: Unique transaction identifier
- `block_timestamp`: Transaction timestamp
- `from_address`: User address (sender)
- `to_address`: Contract address (recipient)
- `value`: Transaction value in wei
- `receipt_gas_used`: Gas consumed by transaction
- `gas_price`: Gas price in wei
- `protocol_category`: Protocol category (DEX, Lending, etc.)
- `application`: Specific application name (Uniswap, Aave, etc.)
- `user_type`: User type classification
- `contract_role`: Contract role in the protocol

### Data Preparation
The interaction data should be pre-processed and enriched using the `interaction_etl.py` module before feature extraction.

## Output

### Feature Matrix
- **Format**: Parquet file with Snappy compression
- **Structure**: One row per user, one column per feature
- **Index**: `user_address` column identifies each user
- **Features**: 67+ behavioral features across protocol, temporal, and value dimensions

### Metadata Files
- `feature_metadata.json`: Machine-readable feature definitions
- `feature_documentation.md`: Human-readable feature descriptions
- `feature_extraction.log`: Detailed processing logs

## Performance

### Benchmarks
- **Processing Rate**: ~1,000-5,000 users per second (depending on hardware)
- **Memory Usage**: Processes data in configurable chunks to manage memory
- **Scalability**: Designed to handle 100K+ users efficiently

### Optimization Tips
1. **Chunk Size**: Adjust `chunk_size` parameter based on available memory
2. **Parallel Processing**: Feature extractors run independently and can be parallelized
3. **Data Types**: Automatic data type optimization reduces memory usage

## Configuration

### Pipeline Parameters
```python
pipeline = FeaturePipeline(
    output_dir=Path("output"),      # Output directory
    chunk_size=1000,                # Users per processing chunk
    logger=custom_logger            # Optional custom logger
)
```

### Feature Extractor Parameters
```python
# Temporal features with custom analysis date
temporal_extractor = TemporalFeatures(
    analysis_date=pd.Timestamp('2024-01-01')
)

# Value features with custom thresholds
value_extractor = ValueFeatures()
value_extractor.high_value_threshold = 5.0  # ETH
```

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python -m pytest src/qaa_analysis/tests/test_feature_engineering.py -v

# Run specific test class
python -m pytest src/qaa_analysis/tests/test_feature_engineering.py::TestProtocolFeatures -v
```

## Error Handling

The pipeline includes comprehensive error handling:

1. **Data Validation**: Checks for required columns and data types
2. **Missing Values**: Automatic handling with appropriate defaults
3. **Infinite Values**: Detection and replacement of infinite/NaN values
4. **User-Level Errors**: Graceful degradation for individual user processing failures
5. **Logging**: Detailed logging for debugging and monitoring

## Extension Points

### Adding New Features
1. Create a new extractor class inheriting from `FeatureExtractor`
2. Implement required abstract methods
3. Add the extractor to `FeaturePipeline._initialize_extractors()`

### Custom Extractors
```python
from qaa_analysis.feature_engineering import FeatureExtractor

class CustomFeatures(FeatureExtractor):
    def __init__(self):
        super().__init__("CustomFeatures")
    
    def extract_features(self, user_interactions):
        return {'custom_feature': calculate_custom_metric(user_interactions)}
    
    def get_feature_names(self):
        return ['custom_feature']
    
    def get_feature_descriptions(self):
        return {'custom_feature': 'Description of custom feature'}
```

## Dependencies

- `pandas >= 1.5.0`: Data manipulation and analysis
- `numpy >= 1.20.0`: Numerical computations
- `pyarrow >= 10.0.0`: Parquet file support

## Integration

This module integrates with:
- **Phase 1**: Interaction ETL pipeline (data input)
- **Phase 2.5**: Data preprocessing (feature scaling, outlier handling)
- **Phase 2.6**: Initial clustering experiments (feature consumption)

## Troubleshooting

### Common Issues

1. **Memory Errors**: Reduce `chunk_size` parameter
2. **Missing Columns**: Ensure input data includes all required columns
3. **Data Type Errors**: Check that numeric columns contain valid numbers
4. **Performance Issues**: Monitor chunk processing and adjust parameters

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Planned improvements for future phases:
1. **Graph Features**: Network-based behavioral features
2. **Sequential Features**: Time-series pattern recognition
3. **Cross-Protocol Features**: Multi-protocol interaction patterns
4. **Risk Features**: MEV, sandwich attack, and risk indicators 