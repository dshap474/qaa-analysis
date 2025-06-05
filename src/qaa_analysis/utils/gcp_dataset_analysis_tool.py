"""
GCP Dataset Analysis Tool

A comprehensive tool for analyzing BigQuery datasets including:
- Schema analysis
- Table structure and relationships
- Data type analysis
- Sample data inspection
- Statistics and metadata
- Data quality checks
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound, Forbidden
except ImportError:
    print("Warning: google-cloud-bigquery not installed. Install with: pip install google-cloud-bigquery")
    bigquery = None

logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    """Information about a table column"""
    name: str
    data_type: str
    mode: str  # NULLABLE, REQUIRED, REPEATED
    description: Optional[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    fields: Optional[List['ColumnInfo']] = None  # For nested/record types


@dataclass
class TableInfo:
    """Information about a BigQuery table"""
    table_id: str
    dataset_id: str
    project_id: str
    table_type: str  # TABLE, VIEW, EXTERNAL, etc.
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    num_rows: Optional[int] = None
    num_bytes: Optional[int] = None
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    columns: Optional[List[ColumnInfo]] = None
    clustering_fields: Optional[List[str]] = None
    partitioning: Optional[Dict[str, Any]] = None


@dataclass
class DatasetInfo:
    """Information about a BigQuery dataset"""
    dataset_id: str
    project_id: str
    location: str
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    tables: Optional[List[TableInfo]] = None


class GCPDatasetAnalysisTool:
    """
    Comprehensive tool for analyzing GCP BigQuery datasets
    """
    
    def __init__(self, project_id: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize the analysis tool
        
        Args:
            project_id: GCP project ID (if None, uses default from environment)
            credentials_path: Path to service account credentials JSON file
        """
        if bigquery is None:
            raise ImportError("google-cloud-bigquery is required. Install with: pip install google-cloud-bigquery")
        
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id) if project_id else bigquery.Client()
        if not self.project_id:
            self.project_id = self.client.project
        
        logger.info(f"Initialized GCP Dataset Analysis Tool for project: {self.project_id}")
    
    def analyze_dataset(self, dataset_id: str, include_sample_data: bool = False, 
                       sample_size: int = 100) -> DatasetInfo:
        """
        Perform comprehensive analysis of a BigQuery dataset
        
        Args:
            dataset_id: ID of the dataset to analyze
            include_sample_data: Whether to include sample data in analysis
            sample_size: Number of sample rows to fetch per table
            
        Returns:
            DatasetInfo object with complete analysis
        """
        logger.info(f"Starting analysis of dataset: {dataset_id}")
        
        try:
            # Get dataset metadata
            dataset_ref = self.client.dataset(dataset_id)
            dataset = self.client.get_dataset(dataset_ref)
            
            dataset_info = DatasetInfo(
                dataset_id=dataset.dataset_id,
                project_id=dataset.project,
                location=dataset.location,
                created=dataset.created,
                modified=dataset.modified,
                description=dataset.description,
                labels=dict(dataset.labels) if dataset.labels else None
            )
            
            # Analyze all tables in the dataset
            tables = []
            for table_ref in self.client.list_tables(dataset):
                table_info = self.analyze_table(
                    dataset_id, 
                    table_ref.table_id, 
                    include_sample_data=include_sample_data,
                    sample_size=sample_size
                )
                tables.append(table_info)
            
            dataset_info.tables = tables
            
            logger.info(f"Completed analysis of dataset: {dataset_id} ({len(tables)} tables)")
            return dataset_info
            
        except NotFound:
            logger.error(f"Dataset {dataset_id} not found")
            raise
        except Forbidden:
            logger.error(f"Access denied to dataset {dataset_id}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing dataset {dataset_id}: {str(e)}")
            raise
    
    def analyze_table(self, dataset_id: str, table_id: str, 
                     include_sample_data: bool = False, sample_size: int = 100) -> TableInfo:
        """
        Analyze a specific table in detail
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
            include_sample_data: Whether to include sample data
            sample_size: Number of sample rows to fetch
            
        Returns:
            TableInfo object with detailed analysis
        """
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            # Extract partitioning info
            partitioning_info = None
            if table.time_partitioning:
                partitioning_info = {
                    'type': 'time',
                    'field': table.time_partitioning.field,
                    'expiration_ms': table.time_partitioning.expiration_ms
                }
            elif table.range_partitioning:
                partitioning_info = {
                    'type': 'range',
                    'field': table.range_partitioning.field,
                    'range': {
                        'start': table.range_partitioning.range_.start,
                        'end': table.range_partitioning.range_.end,
                        'interval': table.range_partitioning.range_.interval
                    }
                }
            
            # Analyze schema
            columns = self._analyze_schema(table.schema)
            
            table_info = TableInfo(
                table_id=table.table_id,
                dataset_id=table.dataset_id,
                project_id=table.project,
                table_type=table.table_type,
                created=table.created,
                modified=table.modified,
                num_rows=table.num_rows,
                num_bytes=table.num_bytes,
                description=table.description,
                labels=dict(table.labels) if table.labels else None,
                columns=columns,
                clustering_fields=list(table.clustering_fields) if table.clustering_fields else None,
                partitioning=partitioning_info
            )
            
            return table_info
            
        except Exception as e:
            logger.error(f"Error analyzing table {dataset_id}.{table_id}: {str(e)}")
            raise
    
    def _analyze_schema(self, schema_fields) -> List[ColumnInfo]:
        """
        Analyze table schema fields recursively
        
        Args:
            schema_fields: BigQuery schema fields
            
        Returns:
            List of ColumnInfo objects
        """
        columns = []
        
        for field in schema_fields:
            column = ColumnInfo(
                name=field.name,
                data_type=field.field_type,
                mode=field.mode,
                description=field.description,
                max_length=getattr(field, 'max_length', None),
                precision=getattr(field, 'precision', None),
                scale=getattr(field, 'scale', None)
            )
            
            # Handle nested/record fields
            if field.fields:
                column.fields = self._analyze_schema(field.fields)
            
            columns.append(column)
        
        return columns
    
    def get_sample_data(self, dataset_id: str, table_id: str, 
                       limit: int = 100, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get sample data from a table
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
            limit: Number of rows to sample
            columns: Specific columns to select (if None, selects all)
            
        Returns:
            DataFrame with sample data
        """
        try:
            column_clause = "*" if not columns else ", ".join(f"`{col}`" for col in columns)
            query = f"""
            SELECT {column_clause}
            FROM `{self.project_id}.{dataset_id}.{table_id}`
            LIMIT {limit}
            """
            
            return self.client.query(query).to_dataframe()
            
        except Exception as e:
            logger.error(f"Error getting sample data from {dataset_id}.{table_id}: {str(e)}")
            raise
    
    def get_data_quality_stats(self, dataset_id: str, table_id: str, 
                              columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get data quality statistics for a table
        
        Args:
            dataset_id: Dataset ID
            table_id: Table ID
            columns: Specific columns to analyze (if None, analyzes all)
            
        Returns:
            Dictionary with data quality statistics
        """
        try:
            # Get table schema first
            table_info = self.analyze_table(dataset_id, table_id)
            
            if not columns:
                columns = [col.name for col in table_info.columns if col.data_type in 
                          ['STRING', 'INTEGER', 'FLOAT', 'NUMERIC', 'TIMESTAMP', 'DATE']]
            
            stats = {}
            
            for column in columns:
                query = f"""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT(`{column}`) as non_null_count,
                    COUNT(*) - COUNT(`{column}`) as null_count,
                    COUNT(DISTINCT `{column}`) as distinct_count
                FROM `{self.project_id}.{dataset_id}.{table_id}`
                """
                
                result = list(self.client.query(query))[0]
                
                stats[column] = {
                    'total_count': result.total_count,
                    'non_null_count': result.non_null_count,
                    'null_count': result.null_count,
                    'distinct_count': result.distinct_count,
                    'null_percentage': (result.null_count / result.total_count * 100) if result.total_count > 0 else 0,
                    'uniqueness_ratio': (result.distinct_count / result.non_null_count) if result.non_null_count > 0 else 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting data quality stats for {dataset_id}.{table_id}: {str(e)}")
            raise
    
    def find_relationships(self, dataset_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Attempt to identify potential relationships between tables
        
        Args:
            dataset_id: Dataset ID to analyze
            
        Returns:
            Dictionary mapping table names to potential relationships
        """
        try:
            dataset_info = self.analyze_dataset(dataset_id)
            relationships = {}
            
            # Simple heuristic: look for columns with similar names across tables
            for table in dataset_info.tables:
                table_relationships = []
                
                for other_table in dataset_info.tables:
                    if table.table_id == other_table.table_id:
                        continue
                    
                    # Find matching column names
                    table_columns = {col.name.lower() for col in table.columns}
                    other_columns = {col.name.lower() for col in other_table.columns}
                    
                    common_columns = table_columns.intersection(other_columns)
                    
                    if common_columns:
                        table_relationships.append({
                            'related_table': other_table.table_id,
                            'common_columns': list(common_columns),
                            'relationship_strength': len(common_columns) / len(table_columns.union(other_columns))
                        })
                
                if table_relationships:
                    relationships[table.table_id] = table_relationships
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error finding relationships in dataset {dataset_id}: {str(e)}")
            raise
    
    def export_analysis(self, dataset_info: DatasetInfo, output_path: str, 
                       format: str = 'json') -> None:
        """
        Export analysis results to file
        
        Args:
            dataset_info: DatasetInfo object to export
            output_path: Path to save the analysis
            format: Export format ('json' or 'yaml')
        """
        try:
            # Convert dataclass to dict, handling datetime objects
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            data = asdict(dataset_info)
            
            # Convert datetime objects recursively
            def process_dict(d):
                if isinstance(d, dict):
                    return {k: process_dict(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [process_dict(item) for item in d]
                elif isinstance(d, datetime):
                    return d.isoformat()
                return d
            
            data = process_dict(data)
            
            if format.lower() == 'json':
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2, default=convert_datetime)
            elif format.lower() == 'yaml':
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Analysis exported to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting analysis: {str(e)}")
            raise
    
    def print_summary(self, dataset_info: DatasetInfo) -> None:
        """
        Print a human-readable summary of the dataset analysis
        
        Args:
            dataset_info: DatasetInfo object to summarize
        """
        print(f"\n{'='*60}")
        print(f"DATASET ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"Dataset: {dataset_info.project_id}.{dataset_info.dataset_id}")
        print(f"Location: {dataset_info.location}")
        print(f"Created: {dataset_info.created}")
        print(f"Modified: {dataset_info.modified}")
        if dataset_info.description:
            print(f"Description: {dataset_info.description}")
        
        if dataset_info.tables:
            print(f"\nTables ({len(dataset_info.tables)}):")
            print("-" * 40)
            
            for table in dataset_info.tables:
                print(f"\n📊 {table.table_id}")
                print(f"   Type: {table.table_type}")
                print(f"   Rows: {table.num_rows:,}" if table.num_rows else "   Rows: Unknown")
                print(f"   Size: {table.num_bytes:,} bytes" if table.num_bytes else "   Size: Unknown")
                print(f"   Columns: {len(table.columns)}" if table.columns else "   Columns: Unknown")
                
                if table.columns:
                    print("   Schema:")
                    for col in table.columns[:5]:  # Show first 5 columns
                        mode_str = f" ({col.mode})" if col.mode != "NULLABLE" else ""
                        print(f"     • {col.name}: {col.data_type}{mode_str}")
                    
                    if len(table.columns) > 5:
                        print(f"     ... and {len(table.columns) - 5} more columns")
                
                if table.partitioning:
                    print(f"   Partitioning: {table.partitioning['type']} on {table.partitioning.get('field', 'N/A')}")
                
                if table.clustering_fields:
                    print(f"   Clustering: {', '.join(table.clustering_fields)}")
        
        print(f"\n{'='*60}")


# Convenience function for quick analysis
def analyze_gcp_dataset(dataset_id: str, project_id: Optional[str] = None, 
                       include_sample_data: bool = False, sample_size: int = 100) -> DatasetInfo:
    """
    Quick function to analyze a GCP dataset
    
    Args:
        dataset_id: ID of the dataset to analyze
        project_id: GCP project ID (optional)
        include_sample_data: Whether to include sample data
        sample_size: Number of sample rows per table
        
    Returns:
        DatasetInfo object with complete analysis
    """
    tool = GCPDatasetAnalysisTool(project_id=project_id)
    return tool.analyze_dataset(dataset_id, include_sample_data, sample_size)


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze GCP BigQuery Dataset")
    parser.add_argument("dataset_id", help="Dataset ID to analyze")
    parser.add_argument("--project", help="GCP Project ID")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=['json', 'yaml'], default='json', help="Output format")
    parser.add_argument("--sample", action='store_true', help="Include sample data")
    parser.add_argument("--sample-size", type=int, default=100, help="Sample size per table")
    
    args = parser.parse_args()
    
    # Perform analysis
    tool = GCPDatasetAnalysisTool(project_id=args.project)
    dataset_info = tool.analyze_dataset(
        args.dataset_id, 
        include_sample_data=args.sample,
        sample_size=args.sample_size
    )
    
    # Print summary
    tool.print_summary(dataset_info)
    
    # Export if requested
    if args.output:
        tool.export_analysis(dataset_info, args.output, args.format)
