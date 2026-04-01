#!/usr/bin/env python3
"""Command-line script to run the sales analysis."""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_data, preprocess_data, save_processed_data
from analysis import key_metrics, sales_by_dimension, monthly_trends
from visualization import create_interactive_dashboard

def main():
    parser = argparse.ArgumentParser(description='E-Commerce Sales Analysis')
    parser.add_argument('--data', default='data/superstore_sales.csv',
                       help='Path to the data file')
    parser.add_argument('--output', default='data/processed/cleaned_superstore.csv',
                       help='Path to save processed data')
    parser.add_argument('--dashboard', action='store_true',
                       help='Generate interactive dashboard')

    args = parser.parse_args()

    # Load and preprocess data
    print("Loading data...")
    df = load_data(args.data)
    df = preprocess_data(df)

    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # Calculate key metrics
    print("\nKey Metrics:")
    metrics = key_metrics(df)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:,.2f}")
        else:
            print(f"{key}: {value:,}")

    # Sales analysis
    print("\nTop Regions by Sales:")
    sales_region = sales_by_dimension(df, 'Region')
    print(sales_region.head())

    print("\nTop Categories by Sales:")
    sales_cat = sales_by_dimension(df, 'Category')
    print(sales_cat.head())

    # Save processed data
    save_processed_data(df, args.output)
    print(f"\nProcessed data saved to {args.output}")

    # Generate dashboard if requested
    if args.dashboard:
        print("\nGenerating interactive dashboard...")
        fig = create_interactive_dashboard(df)
        fig.write_html("dashboard.html")
        print("Dashboard saved as dashboard.html")

if __name__ == "__main__":
    main()