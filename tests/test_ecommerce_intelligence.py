"""Tests for the e-commerce intelligence module."""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import preprocess_data
from src.ecommerce_intelligence import (
    customer_lifetime_metrics, compute_clv_summary, estimate_churn,
    basket_size_trends, order_frequency_distribution,
    day_of_week_analysis, monthly_seasonality, detect_peak_periods,
    weekday_vs_weekend, generate_smart_insights,
)


@pytest.fixture
def ecom_df():
    """E-commerce dataset with Customer IDs."""
    np.random.seed(42)
    n = 200
    customers = np.random.choice([f"CUST-{i:03d}" for i in range(30)], n)
    return preprocess_data(pd.DataFrame({
        "Order ID": [f"ORD-{i:04d}" for i in range(n)],
        "Order Date": pd.date_range("2022-01-01", periods=n, freq="2D"),
        "Customer ID": customers,
        "Region": np.random.choice(["East", "West", "Central"], n),
        "Category": np.random.choice(["Tech", "Office"], n),
        "Sub-Category": np.random.choice(["Phones", "Paper", "Chairs"], n),
        "Segment": np.random.choice(["Consumer", "Corporate"], n),
        "Sales": np.random.exponential(200, n).round(2),
        "Profit": np.random.normal(30, 40, n).round(2),
        "Discount": np.random.choice([0, 0.1, 0.2], n),
        "Quantity": np.random.randint(1, 6, n),
    }))


class TestCustomerLifetimeMetrics:
    def test_returns_dataframe(self, ecom_df):
        result = customer_lifetime_metrics(ecom_df)
        assert not result.empty
        assert "total_revenue" in result.columns
        assert "avg_order_value" in result.columns
        assert "lifetime_days" in result.columns

    def test_one_row_per_customer(self, ecom_df):
        result = customer_lifetime_metrics(ecom_df)
        assert result["Customer ID"].nunique() == len(result)

    def test_missing_columns(self):
        df = pd.DataFrame({"A": [1, 2, 3]})
        result = customer_lifetime_metrics(df)
        assert result.empty


class TestCLVSummary:
    def test_returns_metrics(self, ecom_df):
        cust = customer_lifetime_metrics(ecom_df)
        summary = compute_clv_summary(cust)
        assert "total_customers" in summary
        assert "repeat_rate_pct" in summary
        assert "avg_clv" in summary
        assert "avg_order_value" in summary

    def test_repeat_rate_range(self, ecom_df):
        cust = customer_lifetime_metrics(ecom_df)
        summary = compute_clv_summary(cust)
        assert 0 <= summary["repeat_rate_pct"] <= 100

    def test_empty_input(self):
        summary = compute_clv_summary(pd.DataFrame())
        assert summary == {}


class TestChurn:
    def test_returns_metrics(self, ecom_df):
        result = estimate_churn(ecom_df)
        assert "active" in result
        assert "at_risk" in result
        assert "churned" in result

    def test_totals_add_up(self, ecom_df):
        result = estimate_churn(ecom_df)
        assert result["active"] + result["at_risk"] + result["churned"] == result["total_customers"]

    def test_missing_columns(self):
        result = estimate_churn(pd.DataFrame({"A": [1]}))
        assert result == {}


class TestBasketTrends:
    def test_returns_data(self, ecom_df):
        result = basket_size_trends(ecom_df)
        assert not result.empty
        assert "avg_basket_items" in result.columns
        assert "avg_basket_value" in result.columns

    def test_missing_columns(self):
        result = basket_size_trends(pd.DataFrame({"A": [1]}))
        assert result.empty


class TestOrderFrequency:
    def test_returns_distribution(self, ecom_df):
        cust = customer_lifetime_metrics(ecom_df)
        freq = order_frequency_distribution(cust)
        assert not freq.empty
        assert "Orders" in freq.columns
        assert "Customers" in freq.columns

    def test_empty_input(self):
        result = order_frequency_distribution(pd.DataFrame())
        assert result.empty


class TestDayOfWeek:
    def test_returns_7_days(self, ecom_df):
        result = day_of_week_analysis(ecom_df)
        assert len(result) == 7
        assert "Day" in result.columns
        assert "total_sales" in result.columns

    def test_missing_columns(self):
        result = day_of_week_analysis(pd.DataFrame({"A": [1]}))
        assert result.empty


class TestMonthlySeasonality:
    def test_returns_data(self, ecom_df):
        result = monthly_seasonality(ecom_df)
        assert not result.empty
        assert "seasonality_index" in result.columns

    def test_index_around_100(self, ecom_df):
        result = monthly_seasonality(ecom_df)
        # Average of seasonality index should be around 100
        avg = result["seasonality_index"].mean()
        assert 50 < avg < 200


class TestPeakPeriods:
    def test_returns_peaks(self, ecom_df):
        peaks = detect_peak_periods(ecom_df, top_n=3)
        assert len(peaks) == 3
        assert all("period" in p for p in peaks)
        assert all("pct_above_avg" in p for p in peaks)

    def test_sorted_descending(self, ecom_df):
        peaks = detect_peak_periods(ecom_df, top_n=5)
        sales = [p["sales"] for p in peaks]
        assert sales == sorted(sales, reverse=True)


class TestWeekdayVsWeekend:
    def test_returns_metrics(self, ecom_df):
        result = weekday_vs_weekend(ecom_df)
        assert "weekday_sales" in result
        assert "weekend_sales" in result
        assert "weekend_share_pct" in result

    def test_shares_add_up(self, ecom_df):
        result = weekday_vs_weekend(ecom_df)
        total = result["weekday_sales"] + result["weekend_sales"]
        assert total == pytest.approx(ecom_df["Sales"].sum(), rel=1e-3)


class TestSmartInsights:
    def test_generates_insights(self, ecom_df):
        cust = customer_lifetime_metrics(ecom_df)
        clv = compute_clv_summary(cust)
        churn = estimate_churn(ecom_df)
        peaks = detect_peak_periods(ecom_df)
        wdwe = weekday_vs_weekend(ecom_df)
        insights = generate_smart_insights(ecom_df, clv, churn, peaks, wdwe)
        assert len(insights) > 0
        assert all(isinstance(i, str) for i in insights)

    def test_empty_inputs(self, ecom_df):
        insights = generate_smart_insights(ecom_df, {}, {}, [], {})
        assert isinstance(insights, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
