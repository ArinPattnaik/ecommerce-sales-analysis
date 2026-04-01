"""Visualization functions for sales analysis."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def plot_sales_by_region(df: pd.DataFrame):
    """Plot sales by region using matplotlib."""
    sales_region = df.groupby('Region')['Sales'].sum()
    plt.figure(figsize=(10, 6))
    sales_region.plot(kind='bar')
    plt.title('Sales by Region')
    plt.xlabel('Region')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.gcf()

def plot_profit_by_category(df: pd.DataFrame):
    """Plot profit by category."""
    profit_cat = df.groupby('Category')['Profit'].sum()
    plt.figure(figsize=(10, 6))
    profit_cat.plot(kind='bar', color='green')
    plt.title('Profit by Category')
    plt.xlabel('Category')
    plt.ylabel('Total Profit')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.gcf()

def plot_monthly_trends(df: pd.DataFrame):
    """Plot monthly sales and profit trends."""
    monthly = df.groupby(['Year', 'Month']).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly['Date'] = pd.to_datetime(monthly[['Year', 'Month']].assign(day=1))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(monthly['Date'], monthly['Sales'], marker='o')
    ax1.set_title('Monthly Sales Trend')
    ax1.set_ylabel('Sales')
    ax1.grid(True)

    ax2.plot(monthly['Date'], monthly['Profit'], marker='o', color='green')
    ax2.set_title('Monthly Profit Trend')
    ax2.set_ylabel('Profit')
    ax2.set_xlabel('Date')
    ax2.grid(True)

    plt.tight_layout()
    return fig

def create_interactive_dashboard(df: pd.DataFrame) -> go.Figure:
    """Create an interactive dashboard with Plotly."""
    # Sales by Region
    sales_region = df.groupby('Region')['Sales'].sum().reset_index()

    # Profit by Category
    profit_cat = df.groupby('Category')['Profit'].sum().reset_index()

    # Monthly trends
    monthly = df.groupby(['Year', 'Month']).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly['Date'] = pd.to_datetime(monthly[['Year', 'Month']].assign(day=1))

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Sales by Region', 'Profit by Category', 'Monthly Sales', 'Monthly Profit'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'scatter'}, {'type': 'scatter'}]]
    )

    # Sales by Region
    fig.add_trace(
        go.Bar(x=sales_region['Region'], y=sales_region['Sales'], name='Sales by Region'),
        row=1, col=1
    )

    # Profit by Category
    fig.add_trace(
        go.Bar(x=profit_cat['Category'], y=profit_cat['Profit'], name='Profit by Category'),
        row=1, col=2
    )

    # Monthly Sales
    fig.add_trace(
        go.Scatter(x=monthly['Date'], y=monthly['Sales'], mode='lines+markers', name='Monthly Sales'),
        row=2, col=1
    )

    # Monthly Profit
    fig.add_trace(
        go.Scatter(x=monthly['Date'], y=monthly['Profit'], mode='lines+markers', name='Monthly Profit'),
        row=2, col=2
    )

    fig.update_layout(height=800, title_text="E-Commerce Sales Dashboard")
    return fig

def plot_correlation_heatmap(df: pd.DataFrame):
    """Plot correlation heatmap."""
    numeric_cols = ['Sales', 'Profit', 'Discount', 'Quantity']
    corr = df[numeric_cols].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    return plt.gcf()

def plot_discount_impact(df: pd.DataFrame):
    """Plot discount impact on profit."""
    discount_analysis = df.groupby(pd.cut(df['Discount'], bins=5)).agg({
        'Sales': 'mean',
        'Profit': 'mean'
    }).reset_index()
    discount_analysis['Discount Bin'] = discount_analysis['Discount'].astype(str)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(discount_analysis['Discount Bin'], discount_analysis['Sales'])
    ax1.set_title('Average Sales by Discount Level')
    ax1.set_xlabel('Discount Range')
    ax1.set_ylabel('Average Sales')
    ax1.tick_params(axis='x', rotation=45)

    ax2.bar(discount_analysis['Discount Bin'], discount_analysis['Profit'], color='orange')
    ax2.set_title('Average Profit by Discount Level')
    ax2.set_xlabel('Discount Range')
    ax2.set_ylabel('Average Profit')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    return fig