"""Tests for the visualization module."""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.visualization import (
    kpi_sparkline, bar_chart, grouped_bar, sales_profit_bars,
    sales_treemap, trend_line, forecast_chart, donut_chart,
    scatter_sales_profit, sales_heatmap, correlation_heatmap,
    profit_waterfall, pareto_chart, anomaly_chart,
    rfm_scatter, cohort_heatmap, discount_impact_chart, yoy_chart,
    _empty_figure,
)
from src.data_loader import preprocess_data
from src.analysis import (
    abc_analysis, rfm_analysis, detect_anomalies,
    monthly_trends, discount_impact, yoy_growth,
    correlation_analysis, cohort_analysis, sales_forecast,
)


@pytest.fixture
def sample_df():
    """Create a realistic sample dataset for visualization tests."""
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2022-01-01", periods=n, freq="4D")
    df = pd.DataFrame({
        "Row ID": range(1, n + 1),
        "Order ID": [f"ORD-{i:04d}" for i in range(1, n + 1)],
        "Order Date": dates,
        "Region": np.random.choice(["East", "West", "Central", "South"], n),
        "Category": np.random.choice(["Office Supplies", "Furniture", "Technology"], n),
        "Sub-Category": np.random.choice(["Phones", "Chairs", "Binders", "Storage", "Tables"], n),
        "Segment": np.random.choice(["Consumer", "Corporate", "Home Office"], n),
        "Sales": np.random.exponential(250, n).round(2),
        "Profit": np.random.normal(30, 50, n).round(2),
        "Discount": np.random.choice([0, 0.1, 0.15, 0.2, 0.3], n),
        "Quantity": np.random.randint(1, 8, n),
    })
    return preprocess_data(df)


def _is_figure(obj):
    return isinstance(obj, go.Figure)


class TestEmptyFigure:
    def test_returns_figure(self):
        fig = _empty_figure("test message")
        assert _is_figure(fig)


class TestKpiSparkline:
    def test_returns_figure(self):
        fig = kpi_sparkline([1, 3, 2, 5, 4])
        assert _is_figure(fig)

    def test_empty_values(self):
        fig = kpi_sparkline([])
        assert _is_figure(fig)


class TestBarChart:
    def test_returns_figure(self):
        data = pd.Series([100, 200, 300], index=["A", "B", "C"])
        fig = bar_chart(data, "Test Bar")
        assert _is_figure(fig)

    def test_horizontal(self):
        data = pd.Series([100, 200], index=["X", "Y"])
        fig = bar_chart(data, "Horizontal", horizontal=True)
        assert _is_figure(fig)

    def test_empty_data(self):
        data = pd.Series(dtype=float)
        fig = bar_chart(data, "Empty")
        assert _is_figure(fig)


class TestSalesTreemap:
    def test_returns_figure(self, sample_df):
        fig = sales_treemap(sample_df)
        assert _is_figure(fig)

    def test_empty_df(self):
        fig = sales_treemap(pd.DataFrame())
        assert _is_figure(fig)


class TestTrendLine:
    def test_returns_figure(self, sample_df):
        monthly = monthly_trends(sample_df)
        fig = trend_line(monthly, "Test Trend")
        assert _is_figure(fig)

    def test_empty_data(self):
        fig = trend_line(pd.DataFrame())
        assert _is_figure(fig)


class TestDonutChart:
    def test_returns_figure(self):
        fig = donut_chart(["A", "B", "C"], [10, 20, 30], "Test Donut")
        assert _is_figure(fig)


class TestScatterSalesProfit:
    def test_returns_figure(self, sample_df):
        fig = scatter_sales_profit(sample_df, "Sub-Category")
        assert _is_figure(fig)

    def test_empty_df(self):
        fig = scatter_sales_profit(pd.DataFrame())
        assert _is_figure(fig)


class TestCorrelationHeatmap:
    def test_returns_figure(self, sample_df):
        corr = correlation_analysis(sample_df)
        fig = correlation_heatmap(corr)
        assert _is_figure(fig)

    def test_empty_matrix(self):
        fig = correlation_heatmap(pd.DataFrame())
        assert _is_figure(fig)


class TestProfitWaterfall:
    def test_returns_figure(self, sample_df):
        fig = profit_waterfall(sample_df, "Category")
        assert _is_figure(fig)

    def test_empty_df(self):
        fig = profit_waterfall(pd.DataFrame())
        assert _is_figure(fig)


class TestParetoChart:
    def test_returns_figure(self, sample_df):
        abc = abc_analysis(sample_df)
        fig = pareto_chart(abc)
        assert _is_figure(fig)

    def test_empty_df(self):
        fig = pareto_chart(pd.DataFrame())
        assert _is_figure(fig)


class TestAnomalyChart:
    def test_returns_figure(self, sample_df):
        anom = detect_anomalies(sample_df, "Sales")
        fig = anomaly_chart(anom)
        assert _is_figure(fig)


class TestDiscountImpactChart:
    def test_returns_figure(self, sample_df):
        disc = discount_impact(sample_df)
        fig = discount_impact_chart(disc)
        assert _is_figure(fig)


class TestYoyChart:
    def test_returns_figure(self, sample_df):
        yearly = yoy_growth(sample_df)
        fig = yoy_chart(yearly)
        assert _is_figure(fig)


class TestForecastChart:
    def test_returns_figure(self, sample_df):
        fd = sales_forecast(sample_df, periods=3)
        fig = forecast_chart(fd)
        assert _is_figure(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
