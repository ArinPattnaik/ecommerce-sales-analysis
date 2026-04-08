#!/usr/bin/env python3
"""Command-line script to run the sales analysis."""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import load_data, preprocess_data, save_processed_data
from src.analysis import key_metrics, sales_by_dimension, monthly_trends
from src.config import fmt_currency


def main():
    parser = argparse.ArgumentParser(description='E-Commerce Sales Analysis')
    parser.add_argument('--data', default='data/superstore_sales.csv',
                       help='Path to the data file')
    parser.add_argument('--output', default='data/processed/cleaned_superstore.csv',
                       help='Path to save processed data')

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
            print(f"  {key}: {value:,.2f}")
        else:
            print(f"  {key}: {value:,}")

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

    print("\nTo launch the dashboard, run:")
    print("  streamlit run app/dashboard.py")


if __name__ == "__main__":
    main()