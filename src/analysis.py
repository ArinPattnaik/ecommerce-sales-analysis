"""Sales analysis functions."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

def sales_by_dimension(df: pd.DataFrame, dimension: str) -> pd.Series:
    """Calculate total sales by a given dimension.

    Args:
        df: Preprocessed DataFrame.
        dimension: Column name to group by.

    Returns:
        Series with sales totals.
    """
    return df.groupby(dimension)['Sales'].sum().sort_values(ascending=False)

def profit_by_dimension(df: pd.DataFrame, dimension: str) -> pd.Series:
    """Calculate total profit by a given dimension.

    Args:
        df: Preprocessed DataFrame.
        dimension: Column name to group by.

    Returns:
        Series with profit totals.
    """
    return df.groupby(dimension)['Profit'].sum().sort_values(ascending=False)

def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly sales and profit trends.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        DataFrame with monthly aggregates.
    """
    monthly = df.groupby(['Year', 'Month']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum',
        'Order ID': 'count'
    }).reset_index()
    monthly['Date'] = pd.to_datetime(monthly[['Year', 'Month']].assign(day=1))
    return monthly.sort_values('Date')

def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Get top N products by sales.

    Args:
        df: Preprocessed DataFrame.
        n: Number of top products.

    Returns:
        DataFrame with top products.
    """
    return df.groupby(['Category', 'Sub-Category']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).sort_values('Sales', ascending=False).head(n)

def customer_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """Perform basic customer segmentation based on sales.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        DataFrame with customer segments.
    """
    # Assuming Segment column exists, but let's create RFM-like
    customer_sales = df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'count'
    }).rename(columns={'Order ID': 'Order Count'})
    return customer_sales

def correlation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate correlations between numeric variables.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        Correlation matrix.
    """
    numeric_cols = ['Sales', 'Profit', 'Discount', 'Quantity']
    return df[numeric_cols].corr()

def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze the impact of discounts on profit.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        DataFrame with discount analysis.
    """
    discount_analysis = df.groupby(pd.cut(df['Discount'], bins=10)).agg({
        'Sales': 'mean',
        'Profit': 'mean',
        'Quantity': 'mean'
    }).reset_index()
    discount_analysis['Discount Bin'] = discount_analysis['Discount'].astype(str)
    return discount_analysis

def key_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate key business metrics.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        Dictionary of key metrics.
    """
    metrics = {
        'Total Sales': df['Sales'].sum(),
        'Total Profit': df['Profit'].sum(),
        'Total Orders': df['Order ID'].nunique(),
        'Average Order Value': df['Sales'].sum() / df['Order ID'].nunique(),
        'Profit Margin': (df['Profit'].sum() / df['Sales'].sum()) * 100,
        'Total Quantity': df['Quantity'].sum()
    }
    return metrics