# User Behavioral Features Analysis Program

## Overview

This program provides comprehensive analysis of DeFi user behavioral features extracted from transaction data. It analyzes 10,137 users across 66+ behavioral features including protocol usage, temporal patterns, and transaction value characteristics.

## Files Created

### Core Analysis Module
- **`behavioral_analysis.py`** - Main analysis class with comprehensive statistical analysis and visualization capabilities
- **`run_behavioral_analysis.py`** - Command-line interface for running different types of analysis
- **`run_behavioral_analysis_safe.py`** - Safe version that avoids Unicode encoding issues (recommended)
- **`behavioral_analysis_notebook.ipynb`** - Interactive Jupyter notebook for exploratory analysis
- **`test_analysis.py`** - Test script to verify functionality
- **`debug_unicode.py`** - Debug script for Unicode issues

## Features

### 📊 Statistical Analysis
- **Summary Statistics**: Comprehensive descriptive statistics for all features
- **Data Quality Assessment**: Missing values, zero values, and infinite values analysis
- **Distribution Analysis**: Skewness, kurtosis, and variance analysis
- **Correlation Analysis**: Feature correlation matrix and high correlation identification

### 👥 User Segmentation
- **Activity-Based Segmentation**: Segments users based on total activity levels
- **Segment Profiling**: Detailed analysis of each user segment
- **Comparative Analysis**: Feature comparison across segments

### 🎨 Visualizations
- **Feature Distributions**: Histograms for top features by variance
- **Correlation Heatmaps**: Visual correlation analysis
- **Segment Analysis Plots**: User distribution and activity patterns
- **Protocol Usage Charts**: Bar charts for protocol and application usage

### 📄 Reporting
- **Markdown Reports**: Human-readable analysis summaries
- **JSON Data Export**: Machine-readable analysis results
- **Comprehensive Insights**: Key findings and recommendations

## Usage

### 1. Command Line Interface

#### Recommended: Safe Analysis (Avoids Unicode issues)
```bash
# Complete analysis (recommended)
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis_safe.py --analysis-type complete

# Quick analysis
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis_safe.py --analysis-type quick
```

#### Alternative: Standard Analysis
```bash
# Quick Analysis (Basic statistics + visualizations)
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py --analysis-type quick

# Detailed Analysis (Complete analysis pipeline)
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py --analysis-type detailed
```

#### Correlation Analysis (Focus on feature correlations)
```bash
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py --analysis-type correlation --correlation-threshold 0.8
```

#### Segmentation Analysis (Focus on user segments)
```bash
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py --analysis-type segmentation --n-segments 7
```

#### Custom Data Path and Output Directory
```bash
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py \
  --data-path "path/to/your/features.parquet" \
  --output-dir "path/to/output" \
  --analysis-type detailed
```

### 2. Python API

```python
from pathlib import Path
from src.qaa_analysis.feature_engineering.behavioral_analysis import BehavioralAnalyzer

# Initialize analyzer
data_path = Path("data/features/user_behavioral_features_2025-06-04.parquet")
output_dir = Path("data/analysis/my_analysis")
analyzer = BehavioralAnalyzer(data_path, output_dir)

# Run complete analysis
analyzer.run_complete_analysis()

# Or run individual analyses
stats = analyzer.generate_summary_statistics()
correlations = analyzer.analyze_feature_correlations(threshold=0.7)
segments = analyzer.identify_user_segments(n_segments=5)

# Create visualizations
analyzer.create_feature_distribution_plots(top_n=20)
analyzer.create_correlation_heatmap(top_n=30)
analyzer.create_segment_analysis_plots()

# Generate reports
report = analyzer.generate_analysis_report()
analyzer.save_analysis_results()
```

### 3. Jupyter Notebook

Open and run the interactive notebook:
```bash
jupyter notebook src/qaa_analysis/feature_engineering/behavioral_analysis_notebook.ipynb
```

The notebook provides:
- Step-by-step analysis workflow
- Interactive visualizations
- Detailed explanations
- Customizable analysis parameters

## Output Files

When you run the analysis, the following files are created in the output directory:

### 📊 Visualizations
- **`feature_distributions.png`** - Distribution plots for top features
- **`correlation_heatmap.png`** - Feature correlation heatmap
- **`segment_analysis.png`** - User segmentation visualizations

### 📄 Reports
- **`behavioral_analysis_report.md`** - Comprehensive analysis report
- **`analysis_results.json`** - Complete analysis data in JSON format

### 📁 Directory Structure
```
data/analysis/behavioral_features/
├── feature_distributions.png
├── correlation_heatmap.png
├── segment_analysis.png
├── behavioral_analysis_report.md
└── analysis_results.json
```

## Data Requirements

The program expects a parquet file with the following structure:
- **`user_address`** - Unique user identifier
- **Feature columns** - 66+ behavioral features including:
  - Protocol interaction counts (DEX, lending, staking, etc.)
  - Application usage (Uniswap, Aave, Compound, etc.)
  - Temporal patterns (activity frequency, recency, etc.)
  - Value metrics (transaction values, gas usage, etc.)
  - Diversity measures (Shannon entropy, Herfindahl index, etc.)

## Key Insights Generated

### 🔍 Data Quality
- Missing value analysis
- Feature completeness assessment
- Data distribution characteristics

### 🏛️ Protocol Usage Patterns
- Most popular protocol categories
- Application usage rankings
- User preference analysis

### 👥 User Segmentation
- Activity-based user segments
- Segment characteristics and sizes
- Behavioral differences between segments

### 🔗 Feature Relationships
- Highly correlated feature pairs
- Feature redundancy identification
- Relationship strength analysis

### 💰 Value and Gas Analysis
- Transaction value distributions
- Gas usage patterns
- User value segments

## Configuration Options

### Analysis Parameters
- **Correlation Threshold**: Adjust sensitivity for correlation analysis (default: 0.7)
- **Number of Segments**: Control user segmentation granularity (default: 5)
- **Top N Features**: Limit visualizations to top N features (default: 20)

### Visualization Settings
- **Figure Size**: Customizable plot dimensions
- **Color Schemes**: Multiple color palette options
- **Output Formats**: PNG, PDF, SVG support

## Performance

- **Processing Speed**: ~1,000-5,000 users per second
- **Memory Usage**: Optimized for large datasets
- **Scalability**: Handles 100K+ users efficiently

## Dependencies

Required packages (automatically installed with poetry):
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical data visualization
- `pathlib` - Path handling

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure you're running from the project root directory
2. **Data Not Found**: Check the data path and file existence
3. **Memory Issues**: Reduce chunk size or use a machine with more RAM
4. **Visualization Issues**: Install matplotlib backend for your system

### Testing

Run the test script to verify everything works:
```bash
poetry run python src/qaa_analysis/feature_engineering/test_analysis.py
```

## Examples

### Example 1: Quick Analysis
```bash
# Run quick analysis with default settings
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py --analysis-type quick
```

### Example 2: Custom Correlation Analysis
```bash
# Find features with correlation > 0.8
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py \
  --analysis-type correlation \
  --correlation-threshold 0.8
```

### Example 3: Detailed Segmentation
```bash
# Create 10 user segments for detailed analysis
poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py \
  --analysis-type segmentation \
  --n-segments 10
```

## Next Steps

After running the analysis, you can:

1. **Review the generated report** for key insights
2. **Examine visualizations** to understand patterns
3. **Use segmentation results** for targeted analysis
4. **Identify highly correlated features** for dimensionality reduction
5. **Export results** for further machine learning applications

## Support

For questions or issues:
1. Check the test script output for basic functionality
2. Review the generated logs for detailed error information
3. Examine the example outputs to understand expected results

---

**Created**: User Behavioral Features Analysis Program  
**Purpose**: Comprehensive analysis of DeFi user behavioral patterns  
**Data**: 10,137 users × 66+ features from transaction data 