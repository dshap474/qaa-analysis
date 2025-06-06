"""
Pyvis Network Visualization for DeFi Address Interactions

This module creates an interactive network visualization using pyvis to show
how addresses interact with different DeFi protocol groups.
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from pyvis.network import Network


def setup_logging() -> logging.Logger:
    """Configure logging for the visualization process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def load_interaction_data(data_path: Path, percentage: float = 10.0) -> pd.DataFrame:
    """
    Load the processed interaction data and get a percentage of unique addresses.
    
    Args:
        data_path: Path to the processed parquet file
        percentage: Percentage of unique addresses to include (1-100)
        
    Returns:
        DataFrame with interactions for the selected percentage of addresses
    """
    logger = logging.getLogger(__name__)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found at: {data_path}")
    
    if not 1 <= percentage <= 100:
        raise ValueError("Percentage must be between 1 and 100")
    
    logger.info(f"Loading interaction data from: {data_path}")
    
    # Load the full dataset
    df = pd.read_parquet(data_path)
    logger.info(f"Loaded {len(df):,} total interactions")
    
    # Get all unique addresses ordered by their first appearance
    unique_addresses = df['from_address'].drop_duplicates()
    total_addresses = len(unique_addresses)
    
    # Calculate how many addresses to include based on percentage
    num_addresses = max(1, int(total_addresses * (percentage / 100)))
    selected_addresses = unique_addresses.head(num_addresses)
    
    logger.info(f"Total unique addresses: {total_addresses:,}")
    logger.info(f"Selected {percentage}% = {len(selected_addresses):,} addresses")
    
    # Filter data to only include these addresses
    filtered_df = df[df['from_address'].isin(selected_addresses)].copy()
    logger.info(f"Filtered to {len(filtered_df):,} interactions for selected addresses")
    
    return filtered_df


def create_legend_html(df: pd.DataFrame, user_type_colors: Dict[str, str]) -> str:
    """
    Create HTML legend for the network visualization.
    
    Args:
        df: DataFrame with interaction data
        user_type_colors: Dictionary mapping user types to colors
        
    Returns:
        HTML string for the legend
    """
    # Get unique values from the data
    user_types = sorted(df['user_type'].unique())
    protocol_categories = sorted(df['protocol_category'].unique())
    
    # Calculate statistics for each user type for tooltips
    user_type_stats = df.groupby('user_type').agg({
        'from_address': 'nunique',
        'transaction_hash': 'count',
        'value': 'sum',
        'protocol_category': lambda x: len(x.unique()),
        'application': lambda x: len(x.unique())
    }).round(4)
    
    legend_html = """
    <style>
        .tooltip {
            position: absolute;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 11px;
            max-width: 250px;
            z-index: 10000;
            pointer-events: none;
            border: 1px solid #555;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .user-type-item {
            cursor: pointer;
            padding: 2px;
            border-radius: 3px;
            transition: background-color 0.2s;
        }
        .user-type-item:hover {
            background-color: rgba(255,255,255,0.1);
        }
    </style>
    
    <div style="position: fixed; top: 10px; left: 10px; background: rgba(0,0,0,0.8); 
                color: white; padding: 15px; border-radius: 10px; font-family: Arial; 
                font-size: 12px; max-width: 300px; z-index: 1000;">
        <h3 style="margin-top: 0; color: #FFD700;">Network Legend</h3>
        
        <div style="margin-bottom: 15px;">
            <h4 style="margin: 5px 0; color: #87CEEB;">User Types:</h4>
    """
    
    # Add user type legend items with hover functionality
    for user_type in user_types:
        color = user_type_colors.get(user_type, '#4ECDC4')
        
        # Get stats for this user type
        if user_type in user_type_stats.index:
            stats = user_type_stats.loc[user_type]
            unique_addresses = stats['from_address']
            total_transactions = stats['transaction_hash']
            total_value_eth = float(stats['value']) / 1e18
            unique_protocols = stats['protocol_category']
            unique_apps = stats['application']
            
            tooltip_content = f"""
            <strong>{user_type}</strong><br/>
            Unique Addresses: {unique_addresses:,}<br/>
            Total Transactions: {total_transactions:,}<br/>
            Total Value: {total_value_eth:.4f} ETH<br/>
            Protocols Used: {unique_protocols}<br/>
            Applications Used: {unique_apps}
            """
        else:
            tooltip_content = f"<strong>{user_type}</strong><br/>No data available"
        
        legend_html += f"""
            <div class="user-type-item" style="margin: 3px 0;" 
                 onmouseover="showTooltip(event, `{tooltip_content.replace('`', '\\`')}`)" 
                 onmouseout="hideTooltip()">
                <span style="display: inline-block; width: 12px; height: 12px; 
                           background-color: {color}; border-radius: 50%; margin-right: 8px;"></span>
                {user_type}
            </div>
        """
    
    legend_html += """
        </div>
        
        <div style="margin-bottom: 15px;">
            <h4 style="margin: 5px 0; color: #87CEEB;">Protocol Categories:</h4>
    """
    
    # Add protocol category legend items
    for protocol_cat in protocol_categories:
        legend_html += f"""
            <div style="margin: 3px 0;">
                <span style="display: inline-block; width: 12px; height: 12px; 
                           background-color: #45B7D1; border-radius: 50%; margin-right: 8px;"></span>
                {protocol_cat}
            </div>
        """
    
    legend_html += """
        </div>
        
        <div>
            <h4 style="margin: 5px 0; color: #87CEEB;">Other Elements:</h4>
            <div style="margin: 3px 0;">
                <span style="display: inline-block; width: 12px; height: 12px; 
                           background-color: #FF6B6B; border-radius: 50%; margin-right: 8px;"></span>
                User Addresses
            </div>
            <div style="margin: 3px 0;">
                <span style="display: inline-block; width: 12px; height: 12px; 
                           background-color: #96CEB4; border-radius: 50%; margin-right: 8px;"></span>
                Applications
            </div>
            <div style="margin: 3px 0; color: #FFD700;">
                ⭐ Yellow labels = Major DeFi protocols
            </div>
            <div style="margin: 3px 0; color: #CCCCCC;">
                📏 Node size = Interaction volume
            </div>
        </div>
    </div>
    
    <!-- Tooltip container -->
    <div id="tooltip" class="tooltip" style="display: none;"></div>
    
    <script>
        function showTooltip(event, content) {
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = content;
            tooltip.style.display = 'block';
            
            // Position tooltip near mouse cursor
            const x = event.clientX + 10;
            const y = event.clientY + 10;
            
            // Ensure tooltip doesn't go off screen
            const tooltipRect = tooltip.getBoundingClientRect();
            const windowWidth = window.innerWidth;
            const windowHeight = window.innerHeight;
            
            let finalX = x;
            let finalY = y;
            
            if (x + tooltipRect.width > windowWidth) {
                finalX = event.clientX - tooltipRect.width - 10;
            }
            
            if (y + tooltipRect.height > windowHeight) {
                finalY = event.clientY - tooltipRect.height - 10;
            }
            
            tooltip.style.left = finalX + 'px';
            tooltip.style.top = finalY + 'px';
        }
        
        function hideTooltip() {
            const tooltip = document.getElementById('tooltip');
            tooltip.style.display = 'none';
        }
    </script>
    """
    
    return legend_html


def create_network_graph(df: pd.DataFrame) -> Network:
    """
    Create a pyvis network graph from the interaction data.
    
    Args:
        df: DataFrame with interaction data
        
    Returns:
        Pyvis Network object
    """
    logger = logging.getLogger(__name__)
    
    # Initialize the network
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        directed=True
    )
    
    # Configure physics for stable network layout
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {
          "iterations": 200,
          "updateInterval": 25
        },
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.1,
          "springLength": 200,
          "springConstant": 0.02,
          "damping": 0.4,
          "avoidOverlap": 0.5
        }
      },
      "edges": {
        "arrows": {
          "to": {"enabled": true, "scaleFactor": 1.0}
        },
        "smooth": {
          "enabled": false
        }
      },
      "interaction": {
        "dragNodes": true,
        "dragView": true,
        "zoomView": true
      }
    }
    """)
    
    # Color scheme for different node types
    colors = {
        'address': '#FF6B6B',           # Red for user addresses
        'protocol_category': '#45B7D1', # Blue for protocol categories
        'application': '#96CEB4',       # Green for applications
        'contract': '#FFA07A'           # Light salmon for contracts
    }
    
    # Unique colors for each user type category
    user_type_colors = {
        'Trader': '#FF6B35',        # Orange-red
        'Lender': '#4ECDC4',        # Teal
        'Borrower': '#45B7D1',      # Blue
        'Liquidity Provider': '#96CEB4',  # Green
        'Arbitrageur': '#FFEAA7',   # Yellow
        'MEV Bot': '#DDA0DD',       # Plum
        'Yield Farmer': '#98D8C8',  # Mint
        'Governance Participant': '#F7DC6F',  # Light yellow
        'Bridge User': '#BB8FCE',   # Light purple
        'NFT Trader': '#F8C471',    # Peach
        'Staker': '#85C1E9',        # Light blue
        'Flashloan User': '#F1948A', # Light red
        'Cross-chain User': '#82E0AA', # Light green
        'DeFi Aggregator User': '#D7BDE2', # Lavender
        'Options Trader': '#FAD7A0', # Light orange
    }
    
    # Track nodes to avoid duplicates
    added_nodes = set()
    
    # Add user type nodes with unique colors
    user_types = df['user_type'].unique()
    for user_type in user_types:
        if user_type not in added_nodes:
            # Get color for this user type, default to teal if not found
            user_color = user_type_colors.get(user_type, '#4ECDC4')
            
            net.add_node(
                user_type,
                label=user_type,
                color=user_color,
                size=30,
                title=f"User Type: {user_type}",
                group="user_type",
                font={'size': 12, 'color': 'white', 'face': 'arial bold'}
            )
            added_nodes.add(user_type)
    
    # Calculate interaction counts for sizing nodes
    protocol_interaction_counts = df.groupby('protocol_category').size()
    app_interaction_counts = df.groupby('application').size()
    
    # Add protocol category nodes with size based on interaction count
    protocol_categories = df['protocol_category'].unique()
    for protocol_cat in protocol_categories:
        if protocol_cat not in added_nodes:
            interaction_count = protocol_interaction_counts.get(protocol_cat, 0)
            # Size based on interaction count (min 25, max 60)
            node_size = min(60, max(25, 25 + (interaction_count / 1000)))
            
            net.add_node(
                protocol_cat,
                label=protocol_cat,
                color=colors['protocol_category'],
                size=node_size,
                title=f"Protocol Category: {protocol_cat}<br>Interactions: {interaction_count:,}",
                group="protocol_category",
                font={'size': 14, 'color': 'white', 'face': 'arial bold'}
            )
            added_nodes.add(protocol_cat)
    
    # Add application nodes with size based on interaction count
    applications = df['application'].unique()
    for app in applications:
        if app not in added_nodes:
            interaction_count = app_interaction_counts.get(app, 0)
            # Size based on interaction count (min 20, max 50)
            node_size = min(50, max(20, 20 + (interaction_count / 1000)))
            
            # Highlight major DeFi protocols with special formatting
            major_protocols = ['Uniswap', 'Aave', 'Compound', 'MakerDAO', 'Curve', 'SushiSwap', 'Balancer']
            is_major = any(major in app for major in major_protocols)
            
            font_config = {'size': 12, 'color': 'white', 'face': 'arial'}
            if is_major:
                font_config = {'size': 16, 'color': 'yellow', 'face': 'arial bold'}
            
            net.add_node(
                app,
                label=app,
                color=colors['application'],
                size=node_size,
                title=f"Application: {app}<br>Interactions: {interaction_count:,}",
                group="application",
                font=font_config
            )
            added_nodes.add(app)
    
    # Add address nodes and their connections
    address_stats = df.groupby('from_address').agg({
        'transaction_hash': 'count',
        'user_type': lambda x: list(x.unique()),
        'protocol_category': lambda x: list(x.unique()),
        'application': lambda x: list(x.unique()),
        'value': 'sum',
        'receipt_gas_used': 'sum'
    }).reset_index()
    
    for _, row in address_stats.iterrows():
        address = row['from_address']
        tx_count = row['transaction_hash']
        total_value = row['value']
        total_gas = row['receipt_gas_used']
        
        # Truncate address for display
        display_address = f"{address[:6]}...{address[-4:]}"
        
        # Calculate node size based on transaction count (min 10, max 40)
        node_size = min(40, max(10, tx_count / 2))
        
        # Create hover info
        hover_info = f"""
        Address: {address}
        Transactions: {tx_count:,}
                 Total Value: {float(total_value)/1e18:.4f} ETH
        Total Gas Used: {total_gas:,}
        User Types: {', '.join(row['user_type'])}
        Protocols: {', '.join(row['protocol_category'])}
        Applications: {', '.join(row['application'])}
        """
        
        # Add address node
        net.add_node(
            address,
            label=display_address,
            color=colors['address'],
            size=node_size,
            title=hover_info.strip(),
            group="address"
        )
        
        # Connect address to user types with lighter edges
        for user_type in row['user_type']:
            net.add_edge(
                address, user_type, 
                width=1, 
                color='rgba(255,107,107,0.4)',
                length=150
            )
        
        # Connect address to protocol categories with lighter edges
        for protocol_cat in row['protocol_category']:
            net.add_edge(
                address, protocol_cat, 
                width=1, 
                color='rgba(69,183,209,0.3)',
                length=120
            )
        
        # Connect address to applications with lighter edges
        for app in row['application']:
            net.add_edge(
                address, app, 
                width=0.5, 
                color='rgba(150,206,180,0.2)',
                length=100
            )
    
    # Add connections between group levels with stable edges
    # Connect user types to protocol categories
    user_protocol_connections = df.groupby(['user_type', 'protocol_category']).size().reset_index(name='count')
    for _, row in user_protocol_connections.iterrows():
        edge_width = max(0.5, min(3, row['count'] / 1000))  # Thinner edges
        net.add_edge(
            row['user_type'], 
            row['protocol_category'], 
            width=edge_width,
            color='rgba(128,128,128,0.3)',
            length=80
        )
    
    # Connect protocol categories to applications
    protocol_app_connections = df.groupby(['protocol_category', 'application']).size().reset_index(name='count')
    for _, row in protocol_app_connections.iterrows():
        edge_width = max(0.5, min(2, row['count'] / 1000))  # Thinner edges
        net.add_edge(
            row['protocol_category'], 
            row['application'], 
            width=edge_width,
            color='rgba(128,128,128,0.2)',
            length=60
        )
    
    logger.info(f"Created network with {len(net.nodes)} nodes and {len(net.edges)} edges")
    
    return net


def create_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Create summary statistics for the network.
    
    Args:
        df: DataFrame with interaction data
        
    Returns:
        Dictionary with summary statistics
    """
    stats = {
        'total_addresses': df['from_address'].nunique(),
        'total_interactions': len(df),
        'unique_user_types': df['user_type'].nunique(),
        'unique_protocols': df['protocol_category'].nunique(),
        'unique_applications': df['application'].nunique(),
        'date_range': f"{df['block_timestamp'].min()} to {df['block_timestamp'].max()}",
        'total_value_eth': float(df['value'].sum()) / 1e18,
        'total_gas_used': df['receipt_gas_used'].sum()
    }
    
    return stats


def main() -> None:
    """
    Main function to create the pyvis network visualization.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Create interactive network visualization of DeFi address interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pyvis_address_network.py --percentage 10    # Analyze 10% of addresses
  python pyvis_address_network.py --percentage 1     # Analyze 1% of addresses
  python pyvis_address_network.py --percentage 50    # Analyze 50% of addresses
        """
    )
    
    parser.add_argument(
        "--percentage",
        type=float,
        default=10.0,
        help="Percentage of addresses to analyze (1-100, default: 10)"
    )
    
    parser.add_argument(
        "--data-path",
        type=Path,
        help="Path to the processed parquet file (optional, uses default if not specified)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for visualizations (optional, uses default if not specified)"
    )
    
    args = parser.parse_args()
    
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Starting Pyvis Address Network Visualization")
    logger.info(f"Analyzing {args.percentage}% of addresses")
    logger.info("=" * 60)
    
    try:
        # Set up paths
        if args.data_path:
            data_path = args.data_path
        else:
            data_path = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "defi_interactions_2025-06-04_to_2025-06-04.parquet"
        
        if args.output_dir:
            output_dir = args.output_dir
        else:
            output_dir = Path(__file__).parent.parent.parent.parent / "data" / "visualizations"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data for specified percentage of addresses
        logger.info(f"Loading interaction data for {args.percentage}% of addresses...")
        df = load_interaction_data(data_path, percentage=args.percentage)
        
        # Create summary statistics
        stats = create_summary_stats(df)
        logger.info("Network Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        # Create network graph
        logger.info("Creating pyvis network graph...")
        net = create_network_graph(df)
        
        # Add title and description
        net.heading = f"DeFi Address Interaction Network - {args.percentage}% of Addresses"
        
        # Save the network
        output_filename = f"address_interaction_network_{args.percentage}pct.html"
        output_path = output_dir / output_filename
        net.save_graph(str(output_path))
        
        # Add legend to the HTML file
        logger.info("Adding legend to visualization...")
        user_type_colors = {
            'Trader': '#FF6B35',        # Orange-red
            'Lender': '#4ECDC4',        # Teal
            'Borrower': '#45B7D1',      # Blue
            'Liquidity Provider': '#96CEB4',  # Green
            'Arbitrageur': '#FFEAA7',   # Yellow
            'MEV Bot': '#DDA0DD',       # Plum
            'Yield Farmer': '#98D8C8',  # Mint
            'Governance Participant': '#F7DC6F',  # Light yellow
            'Bridge User': '#BB8FCE',   # Light purple
            'NFT Trader': '#F8C471',    # Peach
            'Staker': '#85C1E9',        # Light blue
            'Flashloan User': '#F1948A', # Light red
            'Cross-chain User': '#82E0AA', # Light green
            'DeFi Aggregator User': '#D7BDE2', # Lavender
            'Options Trader': '#FAD7A0', # Light orange
        }
        
        legend_html = create_legend_html(df, user_type_colors)
        
        # Read the generated HTML file and add the legend
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Insert legend after the body tag
        html_content = html_content.replace('<body>', f'<body>{legend_html}')
        
        # Write the updated HTML back
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("=" * 60)
        logger.info(f"Interactive network saved to: {output_path}")
        logger.info("=" * 60)
        logger.info("Network Legend:")
        logger.info("  🔴 Red nodes: User addresses")
        logger.info("  🎨 Colored nodes: User types (each type has unique color)")
        logger.info("  🔵 Blue nodes: Protocol categories (DEX, Lending, etc.)")
        logger.info("  🟢 Green nodes: Applications (Uniswap, Aave, etc.)")
        logger.info("  ⭐ Yellow labels: Major DeFi protocols")
        logger.info("  📏 Node size: Proportional to interaction count")
        logger.info("  🔗 Edge thickness: Proportional to interaction frequency")
        logger.info("  📋 Interactive legend: Available in top-left of visualization")
        logger.info("=" * 60)
        logger.info("Pyvis Network Visualization Complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Visualization process failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main() 