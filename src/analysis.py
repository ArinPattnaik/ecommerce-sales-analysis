"""
Advanced Analytics Engine for E-Commerce Sales Analysis.

Provides industrial-grade analytics:
  - Key metrics with period-over-period comparison
  - RFM customer segmentation
  - ABC product classification
  - Cohort retention analysis
  - Anomaly detection (Z-score)
  - Sales forecasting (EMA)
  - Discount ROI analysis
  - Growth rate calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from src.config import ABC_THRESHOLDS, ANOMALY_Z_THRESHOLD

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
#  1. KEY METRICS
# ═══════════════════════════════════════════════
def key_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate top-level KPIs."""
    total_sales  = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    total_qty    = df["Quantity"].sum()

    return {
        "Total Sales":        total_sales,
        "Total Profit":       total_profit,
        "Total Orders":       total_orders,
        "Total Quantity":     total_qty,
        "Average Order Value": total_sales / max(total_orders, 1),
        "Profit Margin %":    (total_profit / max(total_sales, 1)) * 100,
        "Avg Discount":       df["Discount"].mean() * 100,
        "Avg Items/Order":    total_qty / max(total_orders, 1),
    }


def period_comparison(df: pd.DataFrame, date_col: str = "Order Date") -> Dict[str, float]:
    """Compare the most recent full month vs the prior month.

    Returns deltas so the dashboard can show ▲/▼ indicators.
    """
    df = df.copy()
    df["_ym"] = df[date_col].dt.to_period("M")
    periods = sorted(df["_ym"].unique())
    if len(periods) < 2:
        return {"sales_delta": 0, "profit_delta": 0, "orders_delta": 0, "margin_delta": 0}

    curr = df[df["_ym"] == periods[-1]]
    prev = df[df["_ym"] == periods[-2]]

    def _safe_pct(curr_val, prev_val):
        return ((curr_val - prev_val) / max(abs(prev_val), 1)) * 100

    cs, ps = curr["Sales"].sum(), prev["Sales"].sum()
    cp, pp = curr["Profit"].sum(), prev["Profit"].sum()
    co, po = curr["Order ID"].nunique(), prev["Order ID"].nunique()

    cm = (cp / max(cs, 1)) * 100
    pm = (pp / max(ps, 1)) * 100

    return {
        "sales_delta":  _safe_pct(cs, ps),
        "profit_delta": _safe_pct(cp, pp),
        "orders_delta": _safe_pct(co, po),
        "margin_delta": cm - pm,
        "curr_period":  str(periods[-1]),
        "prev_period":  str(periods[-2]),
    }


# ═══════════════════════════════════════════════
#  2. DIMENSIONAL ANALYSIS
# ═══════════════════════════════════════════════
def sales_by_dimension(df: pd.DataFrame, dimension: str) -> pd.Series:
    """Total sales grouped by a dimension, descending."""
    return df.groupby(dimension)["Sales"].sum().sort_values(ascending=False)


def profit_by_dimension(df: pd.DataFrame, dimension: str) -> pd.Series:
    """Total profit grouped by a dimension, descending."""
    return df.groupby(dimension)["Profit"].sum().sort_values(ascending=False)


def full_dimension_summary(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Complete P&L summary by a dimension."""
    agg = df.groupby(dimension).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean"),
    ).sort_values("Sales", ascending=False)

    agg["Margin %"]   = (agg["Profit"] / agg["Sales"].replace(0, np.nan)) * 100
    agg["AOV"]         = agg["Sales"] / agg["Orders"].replace(0, np.nan)
    agg["Sales Share %"] = (agg["Sales"] / agg["Sales"].sum()) * 100
    return agg.round(2)


# ═══════════════════════════════════════════════
#  3. MONTHLY / QUARTERLY TRENDS
# ═══════════════════════════════════════════════
def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly aggregates with growth rates."""
    monthly = df.groupby(["Year", "Month"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
    ).reset_index()

    monthly["Date"] = pd.to_datetime(monthly[["Year", "Month"]].assign(day=1))
    monthly = monthly.sort_values("Date")

    # Growth rates
    monthly["Sales MoM %"]  = monthly["Sales"].pct_change() * 100
    monthly["Profit MoM %"] = monthly["Profit"].pct_change() * 100
    monthly["Margin %"]     = (monthly["Profit"] / monthly["Sales"].replace(0, np.nan)) * 100

    return monthly.round(2)


def quarterly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Quarterly aggregates."""
    q = df.groupby(["Year", "Quarter"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
    ).reset_index()
    q["Period"] = q["Year"].astype(str) + "-Q" + q["Quarter"].astype(str)
    q["Margin %"] = (q["Profit"] / q["Sales"].replace(0, np.nan)) * 100
    return q.round(2)


# ═══════════════════════════════════════════════
#  4. TOP / BOTTOM PRODUCTS
# ═══════════════════════════════════════════════
def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top N sub-categories by sales with P&L metrics."""
    agg = df.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", "mean"),
    ).reset_index()
    agg["Margin %"] = (agg["Profit"] / agg["Sales"].replace(0, np.nan)) * 100
    return agg.sort_values("Sales", ascending=False).head(n).round(2)


def bottom_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Bottom N sub-categories by profit (loss-making)."""
    agg = df.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount", "mean"),
    ).reset_index()
    agg["Margin %"] = (agg["Profit"] / agg["Sales"].replace(0, np.nan)) * 100
    return agg.sort_values("Profit", ascending=True).head(n).round(2)


# ═══════════════════════════════════════════════
#  5. CUSTOMER SEGMENTATION – RFM
# ═══════════════════════════════════════════════
def customer_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """Basic segment-level summary."""
    return df.groupby("Segment").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", "mean"),
    ).round(2)


def rfm_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """RFM segmentation using Order ID as proxy for customers.

    Since the dataset lacks a Customer ID, we use Segment + Region
    as a customer proxy to demonstrate the methodology.
    """
    # Create a customer proxy
    df = df.copy()
    df["Customer Proxy"] = df["Segment"] + " | " + df["Region"]

    reference_date = df["Order Date"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("Customer Proxy").agg(
        Recency=("Order Date", lambda x: (reference_date - x.max()).days),
        Frequency=("Order ID", "nunique"),
        Monetary=("Sales", "sum"),
    ).reset_index()

    # Score each dimension 1-5 (quintiles)
    for col in ["Frequency", "Monetary"]:
        rfm[f"{col}_Score"] = pd.qcut(rfm[col], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop").astype(int)
    # Recency: lower is better, so reverse
    rfm["Recency_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop").astype(int)

    rfm["RFM_Score"] = rfm["Recency_Score"] + rfm["Frequency_Score"] + rfm["Monetary_Score"]

    # Segment label
    def _label(row):
        r, f, m = row["Recency_Score"], row["Frequency_Score"], row["Monetary_Score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal"
        elif r >= 4 and f <= 2:
            return "Recent"
        elif r >= 3 and f <= 2:
            return "Promising"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2 and m <= 2:
            return "Lost / Hibernating"
        else:
            return "Needs Attention"

    rfm["Segment Label"] = rfm.apply(_label, axis=1)
    return rfm.round(2)


# ═══════════════════════════════════════════════
#  6. ABC PRODUCT CLASSIFICATION
# ═══════════════════════════════════════════════
def abc_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Pareto-based ABC classification of sub-categories."""
    agg = df.groupby("Sub-Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
    ).sort_values("Sales", ascending=False).reset_index()

    total = agg["Sales"].sum()
    agg["Cumulative Sales"]   = agg["Sales"].cumsum()
    agg["Cumulative Share %"] = (agg["Cumulative Sales"] / total) * 100
    agg["Sales Share %"]      = (agg["Sales"] / total) * 100
    agg["Margin %"]           = (agg["Profit"] / agg["Sales"].replace(0, np.nan)) * 100

    def _classify(pct):
        if pct <= ABC_THRESHOLDS["A"] * 100:
            return "A"
        elif pct <= ABC_THRESHOLDS["B"] * 100:
            return "B"
        return "C"

    agg["Class"] = agg["Cumulative Share %"].apply(_classify)
    return agg.round(2)


# ═══════════════════════════════════════════════
#  7. COHORT ANALYSIS
# ═══════════════════════════════════════════════
def cohort_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly cohort retention matrix using Segment+Region proxy."""
    df = df.copy()
    df["Customer Proxy"] = df["Segment"] + " | " + df["Region"]
    df["Order Period"]   = df["Order Date"].dt.to_period("M")

    # First purchase month per customer
    first_purchase = df.groupby("Customer Proxy")["Order Period"].min().reset_index()
    first_purchase.columns = ["Customer Proxy", "Cohort"]

    df = df.merge(first_purchase, on="Customer Proxy")
    df["Period Index"] = (df["Order Period"] - df["Cohort"]).apply(lambda x: x.n if hasattr(x, 'n') else 0)

    cohort_data = df.groupby(["Cohort", "Period Index"])["Customer Proxy"].nunique().reset_index()
    cohort_data.columns = ["Cohort", "Period Index", "Customers"]

    cohort_pivot = cohort_data.pivot(index="Cohort", columns="Period Index", values="Customers").fillna(0)

    # Convert to retention %
    cohort_sizes = cohort_pivot[0] if 0 in cohort_pivot.columns else cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.div(cohort_sizes, axis=0) * 100

    return retention.round(1)


# ═══════════════════════════════════════════════
#  8. ANOMALY DETECTION
# ═══════════════════════════════════════════════
def detect_anomalies(df: pd.DataFrame, metric: str = "Sales") -> pd.DataFrame:
    """Flag monthly data points that deviate > Z_THRESHOLD standard deviations."""
    monthly = monthly_trends(df)

    mean = monthly[metric].mean()
    std  = monthly[metric].std()

    monthly["Z-Score"]    = (monthly[metric] - mean) / max(std, 1e-9)
    monthly["Is Anomaly"] = monthly["Z-Score"].abs() > ANOMALY_Z_THRESHOLD
    monthly["Anomaly Type"] = monthly.apply(
        lambda r: "📈 Spike" if r["Z-Score"] > ANOMALY_Z_THRESHOLD
        else ("📉 Drop" if r["Z-Score"] < -ANOMALY_Z_THRESHOLD else "Normal"),
        axis=1,
    )

    return monthly


# ═══════════════════════════════════════════════
#  9. FORECASTING (Exponential Moving Average)
# ═══════════════════════════════════════════════
def sales_forecast(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """Simple EMA-based forecast for demonstration."""
    monthly = monthly_trends(df)

    # Calculate EMA
    monthly["EMA"] = monthly["Sales"].ewm(span=4, adjust=False).mean()

    # Project forward
    last_date = monthly["Date"].max()
    last_ema  = monthly["EMA"].iloc[-1]
    trend     = monthly["Sales"].diff().tail(6).mean()  # avg recent trend

    future_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=periods, freq="MS")
    forecast_vals = [last_ema + trend * (i + 1) for i in range(periods)]

    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Sales": forecast_vals,
        "Type": "Forecast",
    })

    actual_df = monthly[["Date", "Sales"]].copy()
    actual_df["Type"] = "Actual"

    combined = pd.concat([actual_df, forecast_df], ignore_index=True)
    return combined.round(2)


# ═══════════════════════════════════════════════
#  10. DISCOUNT ROI ANALYSIS
# ═══════════════════════════════════════════════
def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze profit / margin by discount tier."""
    if "Discount Tier" not in df.columns:
        df = df.copy()
        df["Discount Tier"] = pd.cut(
            df["Discount"],
            bins=[0, 0.01, 0.10, 0.20, 0.30, 1.0],
            labels=["No Discount", "1-10%", "10-20%", "20-30%", "30%+"],
            include_lowest=True,
        )

    agg = df.groupby("Discount Tier", observed=True).agg(
        Orders=("Order ID", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Avg_Sale=("Sales", "mean"),
        Avg_Profit=("Profit", "mean"),
    ).reset_index()

    agg["Margin %"] = (agg["Total_Profit"] / agg["Total_Sales"].replace(0, np.nan)) * 100
    agg["Profit per Order"] = agg["Total_Profit"] / agg["Orders"].replace(0, np.nan)
    return agg.round(2)


# ═══════════════════════════════════════════════
#  11. CORRELATION ANALYSIS
# ═══════════════════════════════════════════════
def correlation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix for numeric variables."""
    cols = ["Sales", "Profit", "Discount", "Quantity"]
    available = [c for c in cols if c in df.columns]
    return df[available].corr().round(3)


# ═══════════════════════════════════════════════
#  12. GROWTH METRICS
# ═══════════════════════════════════════════════
def yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-Year growth comparison."""
    yearly = df.groupby("Year").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
    ).reset_index()

    yearly["Sales YoY %"]  = yearly["Sales"].pct_change() * 100
    yearly["Profit YoY %"] = yearly["Profit"].pct_change() * 100
    yearly["Margin %"]     = (yearly["Profit"] / yearly["Sales"].replace(0, np.nan)) * 100
    return yearly.round(2)