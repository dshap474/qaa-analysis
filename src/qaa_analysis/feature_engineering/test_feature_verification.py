"""
Test script for feature verification - can be used to check if features exist
or to understand what needs to be run first.
"""

import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint

console = Console()


def check_data_structure():
    """Check the current data directory structure and what files exist."""
    console.print(Panel.fit("Feature Engineering Data Structure Check", style="bold blue"))
    
    # Define expected paths
    base_path = Path("data")
    expected_structure = {
        "processed": {
            "description": "Processed interaction data (input for features)",
            "expected_files": ["defi_interactions_*.parquet"]
        },
        "features": {
            "description": "Extracted behavioral features (output)",
            "expected_files": ["user_behavioral_features_*.parquet"]
        },
        "analysis": {
            "description": "Analysis results and visualizations",
            "subdirs": {
                "behavioral_features": {
                    "description": "Behavioral analysis outputs",
                    "expected_files": ["*.png", "*.html", "*.json"]
                }
            }
        },
        "cache": {
            "description": "Query cache files",
            "expected_files": ["*.parquet"]
        }
    }
    
    # Create tree view
    tree = Tree("📁 data/")
    
    for dir_name, dir_info in expected_structure.items():
        dir_path = base_path / dir_name
        exists = dir_path.exists()
        status = "✅" if exists else "❌"
        
        # Add main directory to tree
        branch = tree.add(f"{status} {dir_name}/ - {dir_info['description']}")
        
        if exists:
            # List actual files
            files = list(dir_path.glob("*.parquet")) + list(dir_path.glob("*.json"))
            if files:
                for file in files[:5]:  # Show first 5 files
                    branch.add(f"📄 {file.name}")
                if len(files) > 5:
                    branch.add(f"... and {len(files) - 5} more files")
            else:
                branch.add("[dim]No files found[/dim]")
        
        # Check subdirectories
        if "subdirs" in dir_info:
            for subdir_name, subdir_info in dir_info["subdirs"].items():
                subdir_path = dir_path / subdir_name
                sub_exists = subdir_path.exists()
                sub_status = "✅" if sub_exists else "❌"
                sub_branch = branch.add(f"{sub_status} {subdir_name}/ - {subdir_info['description']}")
    
    console.print(tree)
    
    # Check for specific feature files
    console.print("\n[bold]Checking for feature engineering outputs:[/bold]")
    
    # Look for feature files
    feature_files = list((base_path / "features").glob("*.parquet")) if (base_path / "features").exists() else []
    if feature_files:
        console.print(f"[green]✓ Found {len(feature_files)} feature file(s):[/green]")
        for file in feature_files:
            console.print(f"  • {file.name}")
    else:
        console.print("[yellow]⚠ No feature files found[/yellow]")
    
    # Look for interaction data
    interaction_files = list((base_path / "processed").glob("defi_interactions_*.parquet")) if (base_path / "processed").exists() else []
    if interaction_files:
        console.print(f"\n[green]✓ Found {len(interaction_files)} interaction file(s):[/green]")
        for file in interaction_files:
            console.print(f"  • {file.name}")
    else:
        console.print("\n[yellow]⚠ No interaction data found[/yellow]")
    
    return feature_files, interaction_files


def suggest_next_steps(feature_files, interaction_files):
    """Suggest what to do next based on current state."""
    console.print("\n" + "="*60)
    console.print(Panel.fit("Next Steps", style="bold cyan"))
    
    if not interaction_files:
        console.print("[red]1. First, you need to generate interaction data:[/red]")
        console.print("   poetry run python -m qaa_analysis.etl.interaction_etl")
        console.print("\n   This will create the base interaction data needed for feature engineering.")
    
    elif not feature_files:
        console.print("[yellow]2. Run the feature engineering pipeline:[/yellow]")
        console.print("   poetry run python src/qaa_analysis/feature_engineering/run_pipeline.py")
        console.print("\n   This will extract behavioral features from the interaction data.")
    
    else:
        console.print("[green]3. Run the feature verification:[/green]")
        console.print("   poetry run python src/qaa_analysis/feature_engineering/verify_features.py")
        console.print("\n   This will verify that the feature engineering worked correctly.")
        
        console.print("\n[green]4. (Optional) Run behavioral analysis:[/green]")
        console.print("   poetry run python src/qaa_analysis/feature_engineering/run_behavioral_analysis.py")
        console.print("\n   This will generate visualizations and deeper analysis.")


def check_dependencies():
    """Check if required Python packages are installed."""
    console.print("\n[bold]Checking dependencies:[/bold]")
    
    required_packages = [
        "pandas",
        "numpy",
        "scikit-learn",
        "rich",
        "pyarrow"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            console.print(f"  ✅ {package}")
        except ImportError:
            console.print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        console.print(f"\n[red]Missing packages: {', '.join(missing)}[/red]")
        console.print("[yellow]Install with: poetry install[/yellow]")
    else:
        console.print("\n[green]All required packages are installed![/green]")


def main():
    """Main execution."""
    console.print(Panel.fit(
        "Feature Engineering Verification Setup Check",
        subtitle=f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        style="bold magenta"
    ))
    
    # Check data structure
    feature_files, interaction_files = check_data_structure()
    
    # Check dependencies
    check_dependencies()
    
    # Suggest next steps
    suggest_next_steps(feature_files, interaction_files)
    
    # Summary
    console.print("\n" + "="*60)
    if feature_files:
        console.print("[bold green]✅ Ready to run feature verification![/bold green]")
        console.print("\nRun: poetry run python src/qaa_analysis/feature_engineering/verify_features.py")
    else:
        console.print("[bold yellow]⚠ Need to generate data first before verification[/bold yellow]")


if __name__ == "__main__":
    main()