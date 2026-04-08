"""
Enhanced data loading and preprocessing pipeline.

Handles:
  - Schema validation
  - Type coercion & date parsing
  - Feature engineering (profit margin, revenue/unit, fiscal quarter, etc.)
  - Data quality reporting
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Required columns in the raw CSV
REQUIRED_COLUMNS = {
    "Order ID", "Order Date", "Region", "Category",
    "Sub-Category", "Segment", "Sales", "Profit",
    "Discount", "Quantity",
}


# ──────────────────────────────────────────────
# Loading
# ──────────────────────────────────────────────
def load_data(data_path: str) -> pd.DataFrame:
    """Load the superstore sales data from a CSV file.

    Args:
        data_path: Path to the CSV file.

    Returns:
        Raw DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    path = Path(data_path)
    if not path.exists():
        logger.error(f"File not found: {data_path}")
        raise FileNotFoundError(f"File not found: {data_path}")

    df = pd.read_csv(path)
    logger.info(f"Loaded raw data: {df.shape[0]:,} rows × {df.shape[1]} cols")

    # Validate schema
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df


# ──────────────────────────────────────────────
# Preprocessing & Feature Engineering
# ──────────────────────────────────────────────
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data and engineer business-relevant features.

    Steps:
      1. Parse dates and drop unparseable rows
      2. Coerce numeric columns
      3. Add time-based features (Year, Month, Quarter, Week, Day, etc.)
      4. Add business features (Profit Margin, Revenue/Unit, Order Size Bucket)
    """
    df = df.copy()

    # ── Dates ─────────────────────────────────
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["Order Date"])
    if (dropped := before - len(df)) > 0:
        logger.warning(f"Dropped {dropped} rows with invalid dates")

    # ── Numeric coercion ──────────────────────
    for col in ("Sales", "Profit", "Discount", "Quantity"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Time features ─────────────────────────
    dt = df["Order Date"]
    df["Year"]       = dt.dt.year
    df["Month"]      = dt.dt.month
    df["Quarter"]    = dt.dt.quarter
    df["Week"]       = dt.dt.isocalendar().week.astype(int)
    df["Day of Week"] = dt.dt.day_name()
    df["Is Weekend"] = dt.dt.dayofweek >= 5
    df["Year-Month"] = dt.dt.to_period("M").astype(str)
    df["Year-Quarter"] = df["Year"].astype(str) + "-Q" + df["Quarter"].astype(str)

    # ── Business features ─────────────────────
    df["Profit Margin %"] = np.where(
        df["Sales"] != 0,
        (df["Profit"] / df["Sales"]) * 100,
        0,
    )
    df["Revenue per Unit"] = np.where(
        df["Quantity"] != 0,
        df["Sales"] / df["Quantity"],
        0,
    )
    df["Is Profitable"] = df["Profit"] > 0

    # Order size buckets
    bins   = [0, 100, 300, 600, float("inf")]
    labels = ["Small (<$100)", "Medium ($100-300)", "Large ($300-600)", "Enterprise (>$600)"]
    df["Order Size"] = pd.cut(df["Sales"], bins=bins, labels=labels, include_lowest=True)

    # Discount tier
    df["Discount Tier"] = pd.cut(
        df["Discount"],
        bins=[0, 0.01, 0.10, 0.20, 0.30, 1.0],
        labels=["No Discount", "1-10%", "10-20%", "20-30%", "30%+"],
        include_lowest=True,
    )

    logger.info(f"Preprocessed data: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


# ──────────────────────────────────────────────
# Data Quality Report
# ──────────────────────────────────────────────
def data_quality_report(df: pd.DataFrame) -> Dict:
    """Generate a data quality summary."""
    total = len(df)
    return {
        "total_rows": total,
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicated_rows": int(df.duplicated().sum()),
        "date_range": (
            df["Order Date"].min().strftime("%Y-%m-%d"),
            df["Order Date"].max().strftime("%Y-%m-%d"),
        ),
        "numeric_stats": df[["Sales", "Profit", "Discount", "Quantity"]]
        .describe()
        .to_dict(),
    }


# ──────────────────────────────────────────────
# Save
# ──────────────────────────────────────────────
def save_processed_data(df: pd.DataFrame, output_path: str):
    """Save processed DataFrame to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved processed data → {output_path}")