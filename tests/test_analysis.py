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
    sales_forecast, cohort_analysis,
)
from src.insights import (
    generate_executive_summary,
    generate_product_recommendations,
    generate_anomaly_narrative,
)


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


@pytest.fixture
def small_df():
    """Minimal dataset for edge-case testing."""
    return preprocess_data(pd.DataFrame({
        "Order ID": ["ORD-001", "ORD-002"],
        "Order Date": pd.to_datetime(["2023-01-01", "2023-01-15"]),
        "Region": ["East", "West"],
        "Category": ["Tech", "Tech"],
        "Sub-Category": ["Phones", "Phones"],
        "Segment": ["Consumer", "Consumer"],
        "Sales": [100.0, 200.0],
        "Profit": [20.0, 50.0],
        "Discount": [0.0, 0.1],
        "Quantity": [1, 2],
    }))


@pytest.fixture
def single_row_df():
    """Single-row dataset for boundary testing."""
    return preprocess_data(pd.DataFrame({
        "Order ID": ["ORD-001"],
        "Order Date": pd.to_datetime(["2023-06-15"]),
        "Region": ["East"],
        "Category": ["Tech"],
        "Sub-Category": ["Phones"],
        "Segment": ["Consumer"],
        "Sales": [500.0],
        "Profit": [100.0],
        "Discount": [0.0],
        "Quantity": [3],
    }))


# ─── Data Loader Tests ───────────────────────
class TestDataLoader:
    def test_load_data_exists(self):
        assert callable(load_data)

    def test_preprocess_adds_columns(self, sample_df):
        expected_cols = [
            "Year", "Month", "Quarter", "Profit Margin %",
            "Revenue per Unit", "Order Size", "Discount Tier", "Is Profitable",
        ]
        for col in expected_cols:
            assert col in sample_df.columns, f"Missing column: {col}"

    def test_date_is_datetime(self, sample_df):
        assert pd.api.types.is_datetime64_any_dtype(sample_df["Order Date"])

    def test_preprocess_no_null_dates(self, sample_df):
        assert sample_df["Order Date"].isnull().sum() == 0

    def test_preprocess_numeric_coercion(self, sample_df):
        for col in ["Sales", "Profit", "Discount", "Quantity"]:
            assert pd.api.types.is_numeric_dtype(sample_df[col])

    def test_load_data_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent_file.csv")


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

    def test_single_row(self, single_row_df):
        m = key_metrics(single_row_df)
        assert m["Total Sales"] == 500.0
        assert m["Total Orders"] == 1

    def test_small_dataset(self, small_df):
        m = key_metrics(small_df)
        assert m["Total Sales"] == pytest.approx(300.0, rel=1e-3)


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

    def test_full_summary_shares_sum_to_100(self, sample_df):
        result = full_dimension_summary(sample_df, "Region")
        assert result["Sales Share %"].sum() == pytest.approx(100.0, abs=0.5)


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
        assert result["Cumulative Share %"].iloc[-1] == pytest.approx(100, abs=0.1)

    def test_rfm_analysis(self, sample_df):
        result = rfm_analysis(sample_df)
        assert "Segment Label" in result.columns
        assert "RFM_Score" in result.columns

    def test_rfm_handles_null_segment(self, sample_df):
        """RFM should not crash when Segment/Region has nulls."""
        df = sample_df.copy()
        df.loc[0, "Segment"] = None
        df.loc[1, "Region"] = None
        result = rfm_analysis(df)
        assert len(result) > 0

    def test_anomaly_detection(self, sample_df):
        result = detect_anomalies(sample_df, "Sales")
        assert "Is Anomaly" in result.columns
        assert "Z-Score" in result.columns

    def test_discount_impact(self, sample_df):
        result = discount_impact(sample_df)
        assert "Margin %" in result.columns

    def test_discount_impact_missing_columns(self):
        """Should return empty DataFrame when required columns are missing."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        result = discount_impact(df)
        assert result.empty

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

    def test_period_comparison_single_month(self, single_row_df):
        """Should return zeros when only one period exists."""
        result = period_comparison(single_row_df)
        assert result["sales_delta"] == 0

    def test_cohort_analysis(self, sample_df):
        result = cohort_analysis(sample_df)
        assert not result.empty

    def test_customer_segmentation(self, sample_df):
        result = customer_segmentation(sample_df)
        assert "Sales" in result.columns
        assert len(result) > 0


# ─── Insights Tests ──────────────────────────
class TestInsights:
    def test_executive_summary(self, sample_df):
        insights = generate_executive_summary(sample_df)
        assert len(insights) > 0
        assert all(isinstance(i, str) for i in insights)

    def test_product_recommendations(self, sample_df):
        recs = generate_product_recommendations(sample_df)
        assert isinstance(recs, list)
        assert all(isinstance(r, str) for r in recs)

    def test_anomaly_narrative_no_anomalies(self, small_df):
        """With only 2 data points, anomaly detection should handle gracefully."""
        anom = detect_anomalies(small_df, "Sales")
        narratives = generate_anomaly_narrative(anom)
        assert isinstance(narratives, list)
        assert len(narratives) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
