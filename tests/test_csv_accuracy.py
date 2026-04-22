"""
Integration tests: Verify CSV loading produces accurate results.

Tests both the e-commerce pipeline and the universal analytics pipeline
against the actual superstore_sales.csv to ensure numerical accuracy.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_data, preprocess_data
from src.analysis import (
    key_metrics, sales_by_dimension, abc_analysis,
    discount_impact, correlation_analysis, sales_forecast,
)
from src.generic_analysis import (
    detect_column_types, auto_preprocess,
    compute_kpis, compute_correlations,
    compute_time_aggregates, compute_group_summary,
    generate_generic_insights, data_profile,
)

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "superstore_sales.csv"
)


@pytest.fixture(scope="module")
def ecom_df():
    """Load and preprocess the actual superstore CSV via e-commerce pipeline."""
    df = load_data(DATA_PATH)
    return preprocess_data(df)


@pytest.fixture(scope="module")
def universal_df():
    """Load the actual superstore CSV via universal pipeline."""
    df = pd.read_csv(DATA_PATH)
    col_types = detect_column_types(df)
    return auto_preprocess(df, col_types), col_types


class TestEcommerceAccuracy:
    """Verify the e-commerce pipeline produces accurate numbers."""

    def test_no_rows_lost(self, ecom_df):
        raw = pd.read_csv(DATA_PATH)
        assert len(ecom_df) == len(raw)

    def test_sales_sum_matches_raw(self, ecom_df):
        raw = pd.read_csv(DATA_PATH)
        metrics = key_metrics(ecom_df)
        assert metrics["Total Sales"] == pytest.approx(raw["Sales"].sum(), rel=1e-6)

    def test_profit_sum_matches_raw(self, ecom_df):
        raw = pd.read_csv(DATA_PATH)
        metrics = key_metrics(ecom_df)
        assert metrics["Total Profit"] == pytest.approx(raw["Profit"].sum(), rel=1e-6)

    def test_regional_sales_sum_to_total(self, ecom_df):
        total = ecom_df["Sales"].sum()
        regional = sales_by_dimension(ecom_df, "Region")
        assert regional.sum() == pytest.approx(total, rel=1e-6)

    def test_category_sales_sum_to_total(self, ecom_df):
        total = ecom_df["Sales"].sum()
        by_cat = sales_by_dimension(ecom_df, "Category")
        assert by_cat.sum() == pytest.approx(total, rel=1e-6)

    def test_abc_sales_sum_to_total(self, ecom_df):
        total = ecom_df["Sales"].sum()
        abc = abc_analysis(ecom_df)
        assert abc["Sales"].sum() == pytest.approx(total, rel=1e-6)

    def test_abc_cumulative_reaches_100(self, ecom_df):
        abc = abc_analysis(ecom_df)
        assert abc["Cumulative Share %"].iloc[-1] == pytest.approx(100, abs=0.1)

    def test_correlation_diagonal_is_one(self, ecom_df):
        corr = correlation_analysis(ecom_df)
        for col in corr.columns:
            assert corr.loc[col, col] == pytest.approx(1.0, abs=0.001)

    def test_forecast_produces_correct_periods(self, ecom_df):
        fc = sales_forecast(ecom_df, periods=6)
        assert len(fc[fc["Type"] == "Forecast"]) == 6


class TestUniversalAccuracy:
    """Verify the universal pipeline detects and processes correctly."""

    def test_detects_numeric_columns(self, universal_df):
        _, col_types = universal_df
        for col in ["Sales", "Profit", "Quantity"]:
            assert col in col_types["numeric"]

    def test_detects_categorical_columns(self, universal_df):
        _, col_types = universal_df
        for col in ["Region", "Category"]:
            assert col in col_types["categorical"]

    def test_detects_datetime(self, universal_df):
        _, col_types = universal_df
        assert "Order Date" in col_types["datetime"]

    def test_no_rows_lost(self, universal_df):
        df, _ = universal_df
        raw = pd.read_csv(DATA_PATH)
        assert len(df) == len(raw)

    def test_kpi_sales_matches_raw(self, universal_df):
        df, col_types = universal_df
        kpis = compute_kpis(df, col_types["numeric"])
        sales_kpi = next(k for k in kpis if k["label"] == "Sales")
        assert sales_kpi["sum"] == pytest.approx(df["Sales"].sum(), rel=1e-6)

    def test_insights_generated(self, universal_df):
        df, col_types = universal_df
        insights = generate_generic_insights(df, col_types)
        assert len(insights) > 0


class TestCrossValidation:
    """Verify both pipelines agree on the same data."""

    def test_same_row_count(self, ecom_df, universal_df):
        df, _ = universal_df
        assert len(ecom_df) == len(df)

    def test_same_sales_total(self, ecom_df, universal_df):
        df, col_types = universal_df
        ecom_total = key_metrics(ecom_df)["Total Sales"]
        kpis = compute_kpis(df, col_types["numeric"])
        uni_total = next(k for k in kpis if k["label"] == "Sales")["sum"]
        assert ecom_total == pytest.approx(uni_total, rel=1e-4)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
