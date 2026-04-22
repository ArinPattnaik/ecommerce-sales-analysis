"""
Smart Column Mapper — auto-detects e-commerce columns from ANY CSV.

Uses fuzzy name matching + data pattern analysis to map uploaded columns
to standard e-commerce concepts:
  - order_id, order_date, customer_id
  - revenue/sales, profit/margin, cost, discount, quantity
  - product, category, subcategory
  - region/geography, segment/channel

If enough columns are mapped, the platform unlocks the full e-commerce
deep-dive mode automatically — no manual configuration needed.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
#  COLUMN ROLE DEFINITIONS
# ═══════════════════════════════════════════════
# Each role has: name aliases (fuzzy match), data validators
ECOMMERCE_ROLES = {
    "Order ID": {
        "aliases": [
            "order_id", "order id", "orderid", "order_number", "order number",
            "order_no", "order no", "transaction_id", "transaction id",
            "invoice_id", "invoice id", "invoice_number", "invoice",
            "receipt_id", "receipt", "sale_id", "txn_id", "ref_id",
        ],
        "validate": "_is_id_column",
    },
    "Order Date": {
        "aliases": [
            "order_date", "order date", "orderdate", "date", "order_time",
            "transaction_date", "purchase_date", "sale_date", "created_at",
            "created_date", "invoice_date", "ship_date", "purchase date",
            "transaction date", "sale date", "invoice date",
        ],
        "validate": "_is_date_column",
    },
    "Customer ID": {
        "aliases": [
            "customer_id", "customer id", "customerid", "customer_name",
            "customer name", "customer", "buyer", "buyer_id", "client",
            "client_id", "user_id", "user", "email", "customer_email",
            "account_id", "member_id", "shopper",
        ],
        "validate": None,
    },
    "Sales": {
        "aliases": [
            "sales", "revenue", "total", "amount", "total_amount",
            "total amount", "order_total", "order total", "gross_sales",
            "gross sales", "net_sales", "net sales", "price", "total_price",
            "total price", "subtotal", "sub_total", "order_amount",
            "order amount", "line_total", "value", "turnover", "gmv",
        ],
        "validate": "_is_monetary_column",
    },
    "Profit": {
        "aliases": [
            "profit", "net_profit", "net profit", "margin", "gross_profit",
            "gross profit", "earnings", "net_income", "income", "gain",
            "contribution", "operating_profit",
        ],
        "validate": "_is_monetary_column",
    },
    "Cost": {
        "aliases": [
            "cost", "cogs", "cost_of_goods", "cost of goods", "unit_cost",
            "total_cost", "total cost", "product_cost", "item_cost",
            "purchase_price", "wholesale_price", "expense",
        ],
        "validate": "_is_monetary_column",
    },
    "Discount": {
        "aliases": [
            "discount", "discount_rate", "discount rate", "discount_pct",
            "discount_amount", "discount amount", "promo", "coupon",
            "discount_percent", "disc", "rebate",
        ],
        "validate": "_is_numeric_column",
    },
    "Quantity": {
        "aliases": [
            "quantity", "qty", "units", "items", "count", "units_sold",
            "quantity_ordered", "order_qty", "num_items", "pieces",
            "quantity ordered", "units sold",
        ],
        "validate": "_is_numeric_column",
    },
    "Category": {
        "aliases": [
            "category", "product_category", "product category", "dept",
            "department", "product_type", "product type", "item_category",
            "main_category", "primary_category", "group",
        ],
        "validate": "_is_categorical_column",
    },
    "Sub-Category": {
        "aliases": [
            "sub-category", "sub_category", "subcategory", "sub category",
            "product_name", "product name", "product", "item", "item_name",
            "sku_name", "product_title", "item_description", "description",
            "product_description",
        ],
        "validate": "_is_categorical_column",
    },
    "Region": {
        "aliases": [
            "region", "geography", "geo", "area", "territory", "zone",
            "country", "state", "city", "location", "market", "store",
            "store_name", "branch", "outlet", "ship_state", "ship_country",
            "billing_country", "shipping_region",
        ],
        "validate": "_is_categorical_column",
    },
    "Segment": {
        "aliases": [
            "segment", "customer_segment", "customer segment", "channel",
            "sales_channel", "sales channel", "source", "platform",
            "customer_type", "customer type", "tier", "membership",
            "order_source", "acquisition_channel",
        ],
        "validate": "_is_categorical_column",
    },
}

# Minimum roles needed to unlock e-commerce mode
REQUIRED_ROLES = {"Sales", "Order Date"}
ECOMMERCE_THRESHOLD = 4  # need at least 4 mapped roles for deep-dive


# ═══════════════════════════════════════════════
#  DATA VALIDATORS
# ═══════════════════════════════════════════════
def _is_date_column(series: pd.Series) -> bool:
    """Check if a column looks like dates."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    sample = series.dropna().head(100)
    if len(sample) == 0:
        return False
    try:
        parsed = pd.to_datetime(sample, format="mixed", errors="coerce")
        return parsed.notna().sum() / len(sample) > 0.7
    except Exception:
        return False


def _is_id_column(series: pd.Series) -> bool:
    """Check if a column looks like IDs (high cardinality, mostly unique)."""
    nunique = series.nunique()
    return nunique > len(series) * 0.5 and nunique > 10


def _is_monetary_column(series: pd.Series) -> bool:
    """Check if a column contains monetary values."""
    if pd.api.types.is_numeric_dtype(series):
        return True
    sample = series.dropna().head(100).astype(str)
    # Strip currency symbols and try to parse
    cleaned = sample.str.replace(r'[$€£¥,]', '', regex=True)
    coerced = pd.to_numeric(cleaned, errors="coerce")
    return coerced.notna().sum() / max(len(sample), 1) > 0.7


def _is_numeric_column(series: pd.Series) -> bool:
    """Check if a column is numeric."""
    if pd.api.types.is_numeric_dtype(series):
        return True
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.notna().sum() / max(len(series.dropna()), 1) > 0.7


def _is_categorical_column(series: pd.Series) -> bool:
    """Check if a column is categorical (not too many unique values)."""
    nunique = series.nunique()
    return 2 <= nunique <= max(len(series) * 0.5, 50)


VALIDATORS = {
    "_is_date_column": _is_date_column,
    "_is_id_column": _is_id_column,
    "_is_monetary_column": _is_monetary_column,
    "_is_numeric_column": _is_numeric_column,
    "_is_categorical_column": _is_categorical_column,
}


# ═══════════════════════════════════════════════
#  FUZZY MATCHING ENGINE
# ═══════════════════════════════════════════════
def _normalize(name: str) -> str:
    """Normalize a column name for matching."""
    return re.sub(r'[^a-z0-9]', '', name.lower().strip())


def _match_score(col_name: str, aliases: List[str]) -> float:
    """Score how well a column name matches a set of aliases. 0-1."""
    norm = _normalize(col_name)
    if not norm:
        return 0.0

    best = 0.0
    for alias in aliases:
        norm_alias = _normalize(alias)
        # Exact match
        if norm == norm_alias:
            return 1.0
        # Contains match
        if norm_alias in norm or norm in norm_alias:
            score = len(norm_alias) / max(len(norm), len(norm_alias))
            best = max(best, score * 0.9)
        # Starts-with match
        if norm.startswith(norm_alias) or norm_alias.startswith(norm):
            overlap = min(len(norm), len(norm_alias))
            score = overlap / max(len(norm), len(norm_alias))
            best = max(best, score * 0.85)

    return best


def auto_map_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Auto-detect which DataFrame columns map to e-commerce roles.

    Returns a dict: {role_name: column_name_or_None}.
    Uses a two-pass approach:
      1. Fuzzy name matching (weighted 0.7)
      2. Data pattern validation (weighted 0.3)

    Each column can only be assigned to one role (best match wins).
    """
    mapping: Dict[str, Optional[str]] = {role: None for role in ECOMMERCE_ROLES}
    used_columns: set = set()

    # Build score matrix: (role, column) -> score
    scores: List[Tuple[float, str, str]] = []

    for role, config in ECOMMERCE_ROLES.items():
        for col in df.columns:
            # Name score (0-1)
            name_score = _match_score(col, config["aliases"])

            # Validation score (0 or 1)
            val_score = 0.0
            if config["validate"] and name_score > 0.2:
                validator = VALIDATORS.get(config["validate"])
                if validator:
                    try:
                        val_score = 1.0 if validator(df[col]) else 0.0
                    except Exception:
                        val_score = 0.0

            # Combined score
            combined = name_score * 0.7 + val_score * 0.3
            if combined > 0.3:
                scores.append((combined, role, col))

    # Greedy assignment: highest scores first, no column reuse
    scores.sort(reverse=True)
    for score, role, col in scores:
        if mapping[role] is None and col not in used_columns:
            mapping[role] = col
            used_columns.add(col)

    return mapping


def get_mapping_confidence(mapping: Dict[str, Optional[str]]) -> Dict:
    """Evaluate the quality of a column mapping.

    Returns:
        dict with keys:
          - mapped_count: how many roles were mapped
          - total_roles: total possible roles
          - has_required: whether minimum required roles are present
          - is_ecommerce: whether enough roles for deep-dive mode
          - missing_required: list of missing required roles
          - mapped_roles: list of successfully mapped roles
          - unmapped_roles: list of roles that couldn't be mapped
    """
    mapped = {k: v for k, v in mapping.items() if v is not None}
    unmapped = {k for k, v in mapping.items() if v is None}
    missing_req = REQUIRED_ROLES - set(mapped.keys())

    return {
        "mapped_count": len(mapped),
        "total_roles": len(ECOMMERCE_ROLES),
        "has_required": len(missing_req) == 0,
        "is_ecommerce": len(mapped) >= ECOMMERCE_THRESHOLD and len(missing_req) == 0,
        "missing_required": list(missing_req),
        "mapped_roles": list(mapped.keys()),
        "unmapped_roles": list(unmapped),
        "mapping": mapped,
    }


def apply_mapping(df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> pd.DataFrame:
    """Apply a column mapping to standardize a DataFrame for e-commerce analysis.

    - Renames mapped columns to standard names
    - Fills missing optional columns with sensible defaults
    - Infers Profit from Cost if Profit is missing but Cost is present
    - Generates Order IDs if missing
    - Normalizes Discount to 0-1 range if it looks like percentages
    """
    df = df.copy()
    active = {role: col for role, col in mapping.items() if col is not None}

    # Rename mapped columns (avoid overwriting if source == target)
    rename_dict = {}
    for role, col in active.items():
        if col != role and col in df.columns:
            rename_dict[col] = role
    if rename_dict:
        df = df.rename(columns=rename_dict)

    # ── Profit estimation from Cost ───────────
    if "Profit" not in df.columns and "Cost" in df.columns and "Sales" in df.columns:
        df["Profit"] = df["Sales"] - df["Cost"]
        logger.info("Estimated Profit = Sales - Cost")
    elif "Profit" not in df.columns and "Sales" in df.columns:
        # No profit or cost data — estimate with configurable margin
        df["Profit"] = df["Sales"] * 0.15  # assume 15% margin
        df["_profit_estimated"] = True
        logger.info("Estimated Profit at 15% default margin (no cost data)")

    # ── Generate Order IDs if missing ─────────
    if "Order ID" not in df.columns:
        df["Order ID"] = [f"ORD-{i:06d}" for i in range(1, len(df) + 1)]

    # ── Customer ID fallback ──────────────────
    if "Customer ID" not in df.columns:
        # Try to create a proxy from available columns
        if "Segment" in df.columns and "Region" in df.columns:
            df["Customer ID"] = df["Segment"].fillna("Unknown") + " | " + df["Region"].fillna("Unknown")
        else:
            df["Customer ID"] = df["Order ID"]  # each order = unique customer

    # ── Fill missing optional columns ─────────
    defaults = {
        "Region": "All Regions",
        "Category": "General",
        "Sub-Category": "General",
        "Segment": "All Customers",
        "Discount": 0.0,
        "Quantity": 1,
    }
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val

    # ── Normalize Discount ────────────────────
    if "Discount" in df.columns and pd.api.types.is_numeric_dtype(df["Discount"]):
        disc_max = df["Discount"].max()
        if disc_max > 1.0:
            # Looks like percentages (e.g., 10, 20, 30) — convert to 0-1
            df["Discount"] = df["Discount"] / 100.0
            logger.info(f"Normalized Discount from percentage (max was {disc_max})")

    # ── Coerce types ──────────────────────────
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    for col in ["Sales", "Profit", "Discount", "Quantity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
