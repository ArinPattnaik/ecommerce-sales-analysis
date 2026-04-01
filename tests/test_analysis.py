"""Unit tests for the sales analysis package."""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import load_data, preprocess_data
from analysis import key_metrics, sales_by_dimension

class TestDataLoader:
    """Test data loading and preprocessing functions."""

    def test_load_data(self):
        """Test loading data from CSV."""
        # This would need actual test data
        # For now, just test that function exists
        assert callable(load_data)

    def test_preprocess_data(self):
        """Test data preprocessing."""
        # Create sample data
        sample_data = {
            'Order ID': ['ORD-001', 'ORD-002'],
            'Order Date': ['2023-01-01', '2023-01-02'],
            'Region': ['East', 'West'],
            'Category': ['Office Supplies', 'Furniture'],
            'Sales': [100.0, 200.0],
            'Profit': [10.0, 20.0],
            'Discount': [0.0, 0.1],
            'Quantity': [1, 2]
        }
        df = pd.DataFrame(sample_data)
        processed = preprocess_data(df)

        assert 'Year' in processed.columns
        assert 'Month' in processed.columns
        assert pd.api.types.is_datetime64_any_dtype(processed['Order Date'])

class TestAnalysis:
    """Test analysis functions."""

    def setup_method(self):
        """Set up test data."""
        self.sample_df = pd.DataFrame({
            'Order ID': ['ORD-001', 'ORD-002', 'ORD-003'],
            'Order Date': pd.date_range('2023-01-01', periods=3),
            'Region': ['East', 'West', 'East'],
            'Category': ['Office', 'Furniture', 'Office'],
            'Sales': [100, 200, 150],
            'Profit': [10, 20, 15],
            'Discount': [0.0, 0.1, 0.0],
            'Quantity': [1, 2, 1]
        })

    def test_key_metrics(self):
        """Test key metrics calculation."""
        metrics = key_metrics(self.sample_df)
        assert 'Total Sales' in metrics
        assert 'Total Profit' in metrics
        assert metrics['Total Sales'] == 450
        assert metrics['Total Profit'] == 45

    def test_sales_by_dimension(self):
        """Test sales aggregation by dimension."""
        sales_by_region = sales_by_dimension(self.sample_df, 'Region')
        assert sales_by_region['East'] == 250
        assert sales_by_region['West'] == 200

if __name__ == "__main__":
    pytest.main([__file__])