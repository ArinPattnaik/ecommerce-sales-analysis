"""Comprehensive tests for the analytics engine."""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_data, preprocess_data
from src.analysis import (
    key_metrics, sales_by_dimension, profit_by_dimension,
    full_dimension_summary, monthly_trends, top_products,
    bottom_products, customer_segmentation, rfm_analysis,
    abc_analysis, detect_anomalies, discount_impact,
    correlation_analysis, yoy_growth, period_comparison,
    sales_forecast,
)
from src.insights import generate_executive_summary


# ─── Fixtures ────────────────────────────────
@pytest.fixture
def sample_df():
    """Create a realistic sample dataset."""
    np.random.seed(42)
    n = 200
    dates = pd.date_range("2022-01-01", periods=n, freq="2D")
    regions = np.random.choice(["East", "West", "Central", "South"], n)
    categories = np.random.choice(["Office Supplies", "Furniture", "Technology"], n)
    subcats = np.random.choice(["Phones", "Chairs", "Binders", "Storage", "Tables"], n)
    segments = np.random.choice(["Consumer", "Corporate", "Home Office"], n)
    sales = np.random.exponential(250, n).round(2)
    discounts = np.random.choice([0, 0.1, 0.15, 0.2, 0.3], n)
    profits = sales * (0.3 - discounts) + np.random.normal(0, 20, n)
    quantities = np.random.randint(1, 8, n)

    df = pd.DataFrame({
        "Row ID": range(1, n + 1),
        "Order ID": [f"ORD-{i:04d}" for i in range(1, n + 1)],
        "Order Date": dates,
        "Region": regions,
        "Category": categories,
        "Sub-Category": subcats,
        "Segment": segments,
        "Sales": sales.round(2),
        "Profit": profits.round(2),
        "Discount": discounts,
        "Quantity": quantities,
    })
    return preprocess_data(df)


# ─── Data Loader Tests ───────────────────────
class TestDataLoader:
    def test_load_data_exists(self):
        assert callable(load_data)

    def test_preprocess_adds_columns(self, sample_df):
        assert "Year" in sample_df.columns
        assert "Month" in sample_df.columns
        assert "Quarter" in sample_df.columns
        assert "Profit Margin %" in sample_df.columns
        assert "Revenue per Unit" in sample_df.columns
        assert "Order Size" in sample_df.columns
        assert "Discount Tier" in sample_df.columns
        assert "Is Profitable" in sample_df.columns

    def test_date_is_datetime(self, sample_df):
        assert pd.api.types.is_datetime64_any_dtype(sample_df["Order Date"])


# ─── Key Metrics Tests ───────────────────────
class TestKeyMetrics:
    def test_returns_all_keys(self, sample_df):
        m = key_metrics(sample_df)
        expected = {"Total Sales", "Total Profit", "Total Orders",
                    "Total Quantity", "Average Order Value", "Profit Margin %",
                    "Avg Discount", "Avg Items/Order"}
        assert expected.issubset(m.keys())

    def test_total_sales_positive(self, sample_df):
        assert key_metrics(sample_df)["Total Sales"] > 0

    def test_margin_reasonable(self, sample_df):
        m = key_metrics(sample_df)["Profit Margin %"]
        assert -100 < m < 100


# ─── Dimensional Analysis ────────────────────
class TestDimensional:
    def test_sales_by_region(self, sample_df):
        result = sales_by_dimension(sample_df, "Region")
        assert len(result) > 0
        assert result.sum() == pytest.approx(sample_df["Sales"].sum(), rel=1e-3)

    def test_profit_by_category(self, sample_df):
        result = profit_by_dimension(sample_df, "Category")
        assert len(result) > 0

    def test_full_summary_columns(self, sample_df):
        result = full_dimension_summary(sample_df, "Region")
        assert "Margin %" in result.columns
        assert "AOV" in result.columns
        assert "Sales Share %" in result.columns


# ─── Advanced Analytics ──────────────────────
class TestAdvancedAnalytics:
    def test_monthly_trends(self, sample_df):
        result = monthly_trends(sample_df)
        assert "Date" in result.columns
        assert "Sales MoM %" in result.columns

    def test_top_products(self, sample_df):
        result = top_products(sample_df, 5)
        assert len(result) <= 5

    def test_bottom_products(self, sample_df):
        result = bottom_products(sample_df, 3)
        assert len(result) <= 3

    def test_abc_analysis(self, sample_df):
        result = abc_analysis(sample_df)
        assert "Class" in result.columns
        assert set(result["Class"].unique()).issubset({"A", "B", "C"})
        # Cumulative should reach 100%
        assert result["Cumulative Share %"].iloc[-1] == pytest.approx(100, abs=0.1)

    def test_rfm_analysis(self, sample_df):
        result = rfm_analysis(sample_df)
        assert "Segment Label" in result.columns
        assert "RFM_Score" in result.columns

    def test_anomaly_detection(self, sample_df):
        result = detect_anomalies(sample_df, "Sales")
        assert "Is Anomaly" in result.columns
        assert "Z-Score" in result.columns

    def test_discount_impact(self, sample_df):
        result = discount_impact(sample_df)
        assert "Margin %" in result.columns

    def test_correlation(self, sample_df):
        result = correlation_analysis(sample_df)
        assert result.shape[0] == result.shape[1]

    def test_yoy_growth(self, sample_df):
        result = yoy_growth(sample_df)
        assert "Sales YoY %" in result.columns

    def test_sales_forecast(self, sample_df):
        result = sales_forecast(sample_df, periods=3)
        forecasted = result[result["Type"] == "Forecast"]
        assert len(forecasted) == 3

    def test_period_comparison(self, sample_df):
        result = period_comparison(sample_df)
        assert "sales_delta" in result


# ─── Insights Tests ──────────────────────────
class TestInsights:
    def test_executive_summary(self, sample_df):
        insights = generate_executive_summary(sample_df)
        assert len(insights) > 0
        assert all(isinstance(i, str) for i in insights)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])