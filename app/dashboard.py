"""Streamlit dashboard for E-Commerce Sales Analysis."""

import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_loader import load_data, preprocess_data
from src.analysis import (
    sales_by_dimension, profit_by_dimension, monthly_trends,
    top_products, customer_segmentation, correlation_analysis,
    discount_impact, key_metrics
)
from src.visualization import (
    plot_sales_by_region, plot_profit_by_category, plot_monthly_trends,
    create_interactive_dashboard, plot_correlation_heatmap, plot_discount_impact
)

# Page config
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_processed_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'superstore_sales.csv')
    df = load_data(data_path)
    df = preprocess_data(df)
    return df

df = load_processed_data()

# Sidebar
st.sidebar.title("📊 E-Commerce Sales Analysis")
page = st.sidebar.radio("Navigate", [
    "Overview",
    "Sales Analysis",
    "Profit Analysis",
    "Trends & Forecasting",
    "Product Insights",
    "Customer Segments"
])

# Main content
st.title("🛒 E-Commerce Sales Dashboard")

if page == "Overview":
    st.header("📈 Key Metrics")

    metrics = key_metrics(df)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sales", f"${metrics['Total Sales']:,.0f}")

    with col2:
        st.metric("Total Profit", f"${metrics['Total Profit']:,.0f}")

    with col3:
        st.metric("Total Orders", f"{metrics['Total Orders']:,.0f}")

    with col4:
        st.metric("Profit Margin", f"{metrics['Profit Margin']:.1f}%")

    st.header("📊 Interactive Dashboard")
    fig = create_interactive_dashboard(df)
    st.plotly_chart(fig, width='stretch')

elif page == "Sales Analysis":
    st.header("💰 Sales Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sales by Region")
        sales_region = sales_by_dimension(df, 'Region')
        st.bar_chart(sales_region)

    with col2:
        st.subheader("Sales by Category")
        sales_cat = sales_by_dimension(df, 'Category')
        st.bar_chart(sales_cat)

    st.subheader("Sales by Sub-Category")
    sales_subcat = sales_by_dimension(df, 'Sub-Category')
    st.bar_chart(sales_subcat)

elif page == "Profit Analysis":
    st.header("💵 Profit Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Profit by Region")
        profit_region = profit_by_dimension(df, 'Region')
        st.bar_chart(profit_region)

    with col2:
        st.subheader("Profit by Category")
        profit_cat = profit_by_dimension(df, 'Category')
        st.bar_chart(profit_cat)

    st.subheader("Correlation Analysis")
    corr = correlation_analysis(df)
    st.dataframe(corr.style.background_gradient(cmap='coolwarm'))

    st.subheader("Discount Impact")
    discount_df = discount_impact(df)
    st.dataframe(discount_df)

elif page == "Trends & Forecasting":
    st.header("📈 Trends & Forecasting")

    monthly = monthly_trends(df)

    st.subheader("Monthly Sales & Profit Trends")
    fig = plot_monthly_trends(df)
    st.pyplot(fig)

    st.subheader("Monthly Data Table")
    st.dataframe(monthly)

elif page == "Product Insights":
    st.header("📦 Product Insights")

    top_n = st.slider("Number of top products", 5, 20, 10)
    top_prods = top_products(df, top_n)
    st.dataframe(top_prods)

    st.subheader("Sales Distribution by Category")
    category_sales = df.groupby('Category')['Sales'].sum()
    st.bar_chart(category_sales)

elif page == "Customer Segments":
    st.header("👥 Customer Segments")

    segments = customer_segmentation(df)
    st.dataframe(segments)

    st.subheader("Sales by Customer Segment")
    st.bar_chart(segments['Sales'])

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit & Python")
st.sidebar.markdown("Data: Superstore Sales Dataset")