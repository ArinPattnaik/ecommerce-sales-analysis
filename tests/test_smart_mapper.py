"""Tests for the smart column mapper."""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.smart_mapper import (
    auto_map_columns, get_mapping_confidence, apply_mapping,
    _match_score, _is_date_column, _is_monetary_column,
    _is_id_column, _is_categorical_column,
)


@pytest.fixture
def superstore_df():
    """Simulate the standard superstore column names."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        "Order ID": [f"ORD-{i}" for i in range(n)],
        "Order Date": pd.date_range("2023-01-01", periods=n),
        "Region": np.random.choice(["East", "West"], n),
        "Category": np.random.choice(["Tech", "Office"], n),
        "Sub-Category": np.random.choice(["Phones", "Paper"], n),
        "Segment": np.random.choice(["Consumer", "Corp"], n),
        "Sales": np.random.uniform(10, 500, n).round(2),
        "Profit": np.random.uniform(-50, 100, n).round(2),
        "Discount": np.random.choice([0, 0.1, 0.2], n),
        "Quantity": np.random.randint(1, 10, n),
    })


@pytest.fixture
def shopify_df():
    """Simulate a Shopify-style export with different column names."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        "Name": [f"#SH{i:04d}" for i in range(n)],
        "Created at": pd.date_range("2023-01-01", periods=n),
        "Total": np.random.uniform(20, 300, n).round(2),
        "Subtotal": np.random.uniform(15, 280, n).round(2),
        "Discount Amount": np.random.uniform(0, 20, n).round(2),
        "Lineitem quantity": np.random.randint(1, 5, n),
        "Lineitem name": np.random.choice(["T-Shirt", "Hoodie", "Cap"], n),
        "Shipping Country": np.random.choice(["US", "UK", "CA"], n),
        "Customer Email": [f"user{i}@test.com" for i in range(n)],
        "Financial Status": np.random.choice(["paid", "refunded"], n),
    })


@pytest.fixture
def woocommerce_df():
    """Simulate a WooCommerce-style export."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame({
        "order_number": range(1000, 1000 + n),
        "date": pd.date_range("2023-06-01", periods=n),
        "order_total": np.random.uniform(25, 400, n).round(2),
        "item_cost": np.random.uniform(10, 200, n).round(2),
        "qty": np.random.randint(1, 8, n),
        "product_name": np.random.choice(["Widget A", "Widget B", "Gadget"], n),
        "product_category": np.random.choice(["Electronics", "Home"], n),
        "customer_name": [f"Customer {i}" for i in range(n)],
        "city": np.random.choice(["NYC", "LA", "Chicago"], n),
        "discount_percent": np.random.choice([0, 5, 10, 15], n),
    })


@pytest.fixture
def minimal_df():
    """Minimal CSV with just revenue and dates."""
    return pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=20),
        "amount": np.random.uniform(50, 500, 20).round(2),
    })


class TestMatchScore:
    def test_exact_match(self):
        assert _match_score("Sales", ["sales"]) == 1.0

    def test_partial_match(self):
        score = _match_score("total_amount", ["amount", "total"])
        assert score > 0.4

    def test_no_match(self):
        score = _match_score("xyz_column", ["sales", "revenue"])
        assert score < 0.3


class TestValidators:
    def test_date_column(self):
        s = pd.Series(pd.date_range("2023-01-01", periods=10))
        assert _is_date_column(s) is True

    def test_string_dates(self):
        s = pd.Series(["2023-01-01", "2023-02-01", "2023-03-01"])
        assert _is_date_column(s) == True

    def test_not_date(self):
        s = pd.Series(["hello", "world", "foo"])
        assert _is_date_column(s) == False

    def test_monetary(self):
        s = pd.Series([10.5, 20.3, 100.0])
        assert _is_monetary_column(s) is True

    def test_id_column(self):
        s = pd.Series(range(100))
        assert _is_id_column(s) is True

    def test_categorical(self):
        s = pd.Series(["A", "B", "C"] * 20)
        assert _is_categorical_column(s) is True


class TestAutoMapSuperstore:
    def test_maps_all_standard_columns(self, superstore_df):
        mapping = auto_map_columns(superstore_df)
        assert mapping["Sales"] == "Sales"
        assert mapping["Order Date"] == "Order Date"
        assert mapping["Order ID"] == "Order ID"
        assert mapping["Region"] == "Region"

    def test_confidence_is_ecommerce(self, superstore_df):
        mapping = auto_map_columns(superstore_df)
        conf = get_mapping_confidence(mapping)
        assert conf["is_ecommerce"] is True
        assert conf["has_required"] is True


class TestAutoMapShopify:
    def test_maps_shopify_columns(self, shopify_df):
        mapping = auto_map_columns(shopify_df)
        conf = get_mapping_confidence(mapping)
        # Should detect at least Sales and Date
        assert conf["has_required"] is True
        assert mapping["Sales"] is not None
        assert mapping["Order Date"] is not None

    def test_shopify_is_ecommerce(self, shopify_df):
        mapping = auto_map_columns(shopify_df)
        conf = get_mapping_confidence(mapping)
        assert conf["mapped_count"] >= 4


class TestAutoMapWooCommerce:
    def test_maps_woo_columns(self, woocommerce_df):
        mapping = auto_map_columns(woocommerce_df)
        assert mapping["Sales"] is not None
        assert mapping["Order Date"] is not None

    def test_woo_confidence(self, woocommerce_df):
        mapping = auto_map_columns(woocommerce_df)
        conf = get_mapping_confidence(mapping)
        assert conf["has_required"] is True
        assert conf["mapped_count"] >= 4


class TestAutoMapMinimal:
    def test_minimal_maps_basics(self, minimal_df):
        mapping = auto_map_columns(minimal_df)
        conf = get_mapping_confidence(mapping)
        assert conf["has_required"] is True
        assert mapping["Sales"] is not None
        assert mapping["Order Date"] is not None

    def test_minimal_not_full_ecommerce(self, minimal_df):
        mapping = auto_map_columns(minimal_df)
        conf = get_mapping_confidence(mapping)
        # Only 2 columns, shouldn't qualify for full e-commerce
        assert conf["is_ecommerce"] is False


class TestApplyMapping:
    def test_renames_columns(self, shopify_df):
        mapping = auto_map_columns(shopify_df)
        result = apply_mapping(shopify_df, mapping)
        assert "Sales" in result.columns
        assert "Order Date" in result.columns

    def test_generates_order_id(self, minimal_df):
        mapping = auto_map_columns(minimal_df)
        result = apply_mapping(minimal_df, mapping)
        assert "Order ID" in result.columns
        assert result["Order ID"].nunique() == len(minimal_df)

    def test_estimates_profit(self, minimal_df):
        mapping = auto_map_columns(minimal_df)
        result = apply_mapping(minimal_df, mapping)
        assert "Profit" in result.columns
        assert result["Profit"].sum() > 0

    def test_profit_from_cost(self, woocommerce_df):
        mapping = auto_map_columns(woocommerce_df)
        result = apply_mapping(woocommerce_df, mapping)
        assert "Profit" in result.columns

    def test_normalizes_discount_percentages(self, woocommerce_df):
        mapping = auto_map_columns(woocommerce_df)
        result = apply_mapping(woocommerce_df, mapping)
        if "Discount" in result.columns:
            assert result["Discount"].max() <= 1.0

    def test_fills_missing_columns(self, minimal_df):
        mapping = auto_map_columns(minimal_df)
        result = apply_mapping(minimal_df, mapping)
        for col in ["Region", "Category", "Sub-Category", "Segment", "Quantity"]:
            assert col in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
