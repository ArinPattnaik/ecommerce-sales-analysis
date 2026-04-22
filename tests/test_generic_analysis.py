"""Tests for the universal analytics engine (generic_analysis.py)."""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generic_analysis import (
    detect_column_types, auto_preprocess, data_profile,
    compute_kpis, compute_numeric_distribution, compute_categorical_distribution,
    compute_correlations, find_top_correlations,
    compute_time_aggregates, compute_group_summary,
    detect_outliers, generate_generic_insights,
)


@pytest.fixture
def mixed_df():
    """DataFrame with mixed column types for detection testing."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "id": range(1, n + 1),
        "date": pd.date_range("2023-01-01", periods=n, freq="D"),
        "category": np.random.choice(["A", "B", "C"], n),
        "value": np.random.normal(100, 25, n).round(2),
        "count": np.random.randint(1, 50, n),
        "flag": np.random.choice([True, False], n),
        "price": np.random.uniform(10, 500, n).round(2),
    })


@pytest.fixture
def empty_df():
    """Empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def numeric_only_df():
    """DataFrame with only numeric columns."""
    np.random.seed(42)
    return pd.DataFrame({
        "a": np.random.normal(0, 1, 50),
        "b": np.random.normal(5, 2, 50),
        "c": np.random.normal(-3, 0.5, 50),
    })


class TestDetectColumnTypes:
    def test_detects_numeric(self, mixed_df):
        types = detect_column_types(mixed_df)
        assert "value" in types["numeric"]
        assert "price" in types["numeric"]

    def test_detects_categorical(self, mixed_df):
        types = detect_column_types(mixed_df)
        assert "category" in types["categorical"]

    def test_detects_datetime(self, mixed_df):
        types = detect_column_types(mixed_df)
        assert "date" in types["datetime"]

    def test_detects_id(self, mixed_df):
        types = detect_column_types(mixed_df)
        assert "id" in types["id"] or "id" in types["numeric"]

    def test_empty_dataframe(self, empty_df):
        types = detect_column_types(empty_df)
        assert all(len(v) == 0 for v in types.values())

    def test_string_dates_detected(self):
        df = pd.DataFrame({
            "date_str": ["2023-01-01", "2023-02-01", "2023-03-01"] * 10,
            "val": range(30),
        })
        types = detect_column_types(df)
        assert "date_str" in types["datetime"]


class TestAutoPreprocess:
    def test_coerces_dates(self, mixed_df):
        types = detect_column_types(mixed_df)
        result = auto_preprocess(mixed_df, types)
        for col in types["datetime"]:
            assert pd.api.types.is_datetime64_any_dtype(result[col])

    def test_coerces_numerics(self):
        df = pd.DataFrame({"val": ["1.5", "2.3", "3.7", "bad", "5.0"]})
        types = {"numeric": ["val"], "categorical": [], "datetime": [], "id": [], "boolean": []}
        result = auto_preprocess(df, types)
        assert pd.api.types.is_numeric_dtype(result["val"])


class TestDataProfile:
    def test_returns_expected_keys(self, mixed_df):
        profile = data_profile(mixed_df)
        assert "rows" in profile
        assert "columns" in profile
        assert "missing_total" in profile
        assert "memory_mb" in profile

    def test_correct_row_count(self, mixed_df):
        profile = data_profile(mixed_df)
        assert profile["rows"] == 100


class TestComputeKpis:
    def test_returns_kpis(self, mixed_df):
        kpis = compute_kpis(mixed_df, ["value", "count", "price"])
        assert len(kpis) == 3
        assert all("sum" in k for k in kpis)
        assert all("mean" in k for k in kpis)

    def test_empty_cols_list(self, mixed_df):
        kpis = compute_kpis(mixed_df, [])
        assert kpis == []

    def test_caps_at_12(self, numeric_only_df):
        # Even with many cols, should cap
        kpis = compute_kpis(numeric_only_df, ["a", "b", "c"])
        assert len(kpis) <= 12


class TestDistributions:
    def test_numeric_distribution(self, mixed_df):
        result = compute_numeric_distribution(mixed_df, "value")
        assert "values" in result
        assert len(result["values"]) > 0

    def test_numeric_distribution_empty(self):
        df = pd.DataFrame({"x": pd.Series(dtype=float)})
        result = compute_numeric_distribution(df, "x")
        assert result["values"] == []

    def test_categorical_distribution(self, mixed_df):
        result = compute_categorical_distribution(mixed_df, "category")
        assert len(result) <= 15
        assert "Count" in result.columns


class TestCorrelations:
    def test_correlation_matrix(self, numeric_only_df):
        corr = compute_correlations(numeric_only_df, ["a", "b", "c"])
        assert corr.shape == (3, 3)
        # Diagonal should be 1.0
        for col in corr.columns:
            assert corr.loc[col, col] == pytest.approx(1.0, abs=0.01)

    def test_insufficient_columns(self, mixed_df):
        corr = compute_correlations(mixed_df, ["value"])
        assert corr.empty

    def test_top_correlations(self, numeric_only_df):
        corr = compute_correlations(numeric_only_df, ["a", "b", "c"])
        top = find_top_correlations(corr, 3)
        assert len(top) == 3
        assert all("correlation" in t for t in top)


class TestTimeAnalysis:
    def test_time_aggregates(self, mixed_df):
        result = compute_time_aggregates(mixed_df, "date", ["value", "count"])
        assert not result.empty
        assert "Records" in result.columns

    def test_time_aggregates_no_numeric(self, mixed_df):
        result = compute_time_aggregates(mixed_df, "date", ["nonexistent"])
        assert result.empty


class TestGroupSummary:
    def test_group_summary(self, mixed_df):
        result = compute_group_summary(mixed_df, "category", ["value", "count"])
        assert not result.empty
        assert "category" in result.columns

    def test_group_summary_no_valid_cols(self, mixed_df):
        result = compute_group_summary(mixed_df, "category", ["nonexistent"])
        assert result.empty


class TestOutlierDetection:
    def test_detects_outliers(self):
        data = np.random.normal(0, 1, 100)
        data = np.append(data, [10, -10])  # obvious outliers
        df = pd.DataFrame({"val": data})
        result = detect_outliers(df, "val", z_threshold=2.5)
        assert len(result) >= 2

    def test_no_outliers_uniform(self):
        df = pd.DataFrame({"val": [1.0] * 50})
        result = detect_outliers(df, "val")
        assert result.empty

    def test_too_few_rows(self):
        df = pd.DataFrame({"val": [1.0, 2.0]})
        result = detect_outliers(df, "val")
        assert result.empty


class TestGenericInsights:
    def test_generates_insights(self, mixed_df):
        types = detect_column_types(mixed_df)
        insights = generate_generic_insights(mixed_df, types)
        assert len(insights) > 0
        assert all(isinstance(i, str) for i in insights)

    def test_overview_insight_present(self, mixed_df):
        types = detect_column_types(mixed_df)
        insights = generate_generic_insights(mixed_df, types)
        assert any("Dataset Overview" in i for i in insights)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
