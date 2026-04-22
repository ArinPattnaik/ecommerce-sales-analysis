"""
E-Commerce Intelligence — advanced auto-derived metrics.

Works with any e-commerce dataset that has been mapped through smart_mapper.
Computes:
  - Customer Lifetime Value (CLV)
  - Repeat purchase rate & order frequency
  - Basket size trends
  - Churn estimation
  - Seasonality detection (peak periods, weekday vs weekend, holiday effects)
  - Date intelligence (day-of-week patterns, monthly patterns)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
#  CUSTOMER METRICS
# ═══════════════════════════════════════════════
def customer_lifetime_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-customer lifetime metrics.

    Requires: Customer ID, Order ID, Order Date, Sales, Profit.
    Returns DataFrame with one row per customer.
    """
    required = {"Customer ID", "Order ID", "Order Date", "Sales"}
    if not required.issubset(df.columns):
        logger.warning(f"customer_lifetime_metrics: missing {required - set(df.columns)}")
        return pd.DataFrame()

    cust = df.groupby("Customer ID").agg(
        first_order=("Order Date", "min"),
        last_order=("Order Date", "max"),
        total_orders=("Order ID", "nunique"),
        total_revenue=("Sales", "sum"),
        total_profit=("Profit", "sum") if "Profit" in df.columns else ("Sales", lambda x: x.sum() * 0.15),
        total_quantity=("Quantity", "sum") if "Quantity" in df.columns else ("Order ID", "count"),
        avg_discount=("Discount", "mean") if "Discount" in df.columns else ("Sales", lambda x: 0),
    ).reset_index()

    # Derived metrics
    cust["lifetime_days"] = (cust["last_order"] - cust["first_order"]).dt.days
    cust["avg_order_value"] = cust["total_revenue"] / cust["total_orders"].replace(0, 1)
    cust["avg_days_between_orders"] = cust["lifetime_days"] / (cust["total_orders"] - 1).replace(0, np.nan)
    cust["profit_margin_pct"] = (cust["total_profit"] / cust["total_revenue"].replace(0, np.nan)) * 100
    cust["avg_basket_size"] = cust["total_quantity"] / cust["total_orders"].replace(0, 1)

    return cust.round(2)


def compute_clv_summary(cust_df: pd.DataFrame) -> Dict:
    """Compute aggregate CLV statistics from customer lifetime data.

    Returns dict with CLV metrics for dashboard display.
    """
    if cust_df.empty:
        return {}

    total_customers = len(cust_df)
    repeat_customers = len(cust_df[cust_df["total_orders"] > 1])
    repeat_rate = (repeat_customers / max(total_customers, 1)) * 100

    return {
        "total_customers": total_customers,
        "repeat_customers": repeat_customers,
        "repeat_rate_pct": round(repeat_rate, 1),
        "avg_clv": round(cust_df["total_revenue"].mean(), 2),
        "median_clv": round(cust_df["total_revenue"].median(), 2),
        "top_10pct_clv": round(cust_df["total_revenue"].quantile(0.9), 2),
        "avg_order_value": round(cust_df["avg_order_value"].mean(), 2),
        "avg_orders_per_customer": round(cust_df["total_orders"].mean(), 1),
        "avg_basket_size": round(cust_df["avg_basket_size"].mean(), 1),
        "avg_lifetime_days": round(cust_df["lifetime_days"].mean(), 0),
        "one_time_buyers_pct": round((1 - repeat_rate / 100) * 100, 1),
    }


def estimate_churn(df: pd.DataFrame, lookback_days: int = 90) -> Dict:
    """Estimate customer churn based on recency.

    A customer is considered 'churned' if they haven't ordered in
    the last `lookback_days` days relative to the most recent order date.
    """
    if "Customer ID" not in df.columns or "Order Date" not in df.columns:
        return {}

    reference = df["Order Date"].max()
    last_order = df.groupby("Customer ID")["Order Date"].max().reset_index()
    last_order.columns = ["Customer ID", "Last Order"]
    last_order["days_since"] = (reference - last_order["Last Order"]).dt.days

    total = len(last_order)
    active = len(last_order[last_order["days_since"] <= lookback_days])
    at_risk = len(last_order[(last_order["days_since"] > lookback_days) & (last_order["days_since"] <= lookback_days * 2)])
    churned = len(last_order[last_order["days_since"] > lookback_days * 2])

    return {
        "total_customers": total,
        "active": active,
        "active_pct": round(active / max(total, 1) * 100, 1),
        "at_risk": at_risk,
        "at_risk_pct": round(at_risk / max(total, 1) * 100, 1),
        "churned": churned,
        "churned_pct": round(churned / max(total, 1) * 100, 1),
        "lookback_days": lookback_days,
    }


# ═══════════════════════════════════════════════
#  BASKET & ORDER ANALYSIS
# ═══════════════════════════════════════════════
def basket_size_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Track average basket size (items per order) over time.

    Returns monthly aggregation of basket metrics.
    """
    if not {"Order ID", "Order Date", "Quantity"}.issubset(df.columns):
        return pd.DataFrame()

    df = df.copy()
    df["_ym"] = df["Order Date"].dt.to_period("M")

    # Per-order basket
    order_basket = df.groupby(["_ym", "Order ID"]).agg(
        items=("Quantity", "sum"),
        revenue=("Sales", "sum"),
    ).reset_index()

    monthly = order_basket.groupby("_ym").agg(
        avg_basket_items=("items", "mean"),
        avg_basket_value=("revenue", "mean"),
        total_orders=("Order ID", "nunique"),
    ).reset_index()

    monthly["Period"] = monthly["_ym"].astype(str)
    monthly = monthly.drop(columns=["_ym"])
    return monthly.round(2)


def order_frequency_distribution(cust_df: pd.DataFrame) -> pd.DataFrame:
    """Distribution of order counts per customer.

    Returns a frequency table: how many customers placed 1, 2, 3... orders.
    """
    if cust_df.empty or "total_orders" not in cust_df.columns:
        return pd.DataFrame()

    freq = cust_df["total_orders"].value_counts().sort_index().reset_index()
    freq.columns = ["Orders", "Customers"]

    # Bucket high values
    if len(freq) > 10:
        top = freq[freq["Orders"] <= 10].copy()
        rest = freq[freq["Orders"] > 10]
        if len(rest) > 0:
            top = pd.concat([top, pd.DataFrame({
                "Orders": ["11+"],
                "Customers": [rest["Customers"].sum()],
            })], ignore_index=True)
        freq = top

    return freq


# ═══════════════════════════════════════════════
#  SEASONALITY & DATE INTELLIGENCE
# ═══════════════════════════════════════════════
def day_of_week_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Sales performance by day of week."""
    if "Order Date" not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["_dow"] = df["Order Date"].dt.day_name()
    df["_dow_num"] = df["Order Date"].dt.dayofweek

    agg = df.groupby(["_dow", "_dow_num"]).agg(
        total_sales=("Sales", "sum"),
        avg_sales=("Sales", "mean"),
        order_count=("Order ID", "nunique") if "Order ID" in df.columns else ("Sales", "count"),
    ).reset_index().sort_values("_dow_num")

    agg["Day"] = agg["_dow"]
    agg["is_weekend"] = agg["_dow_num"] >= 5
    return agg[["Day", "is_weekend", "total_sales", "avg_sales", "order_count"]].round(2)


def monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Average sales by calendar month (across all years) to detect seasonality."""
    if "Order Date" not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["_month"] = df["Order Date"].dt.month
    df["_month_name"] = df["Order Date"].dt.strftime("%b")

    agg = df.groupby(["_month", "_month_name"]).agg(
        avg_sales=("Sales", "sum") if df["Order Date"].dt.year.nunique() <= 1
        else ("Sales", "mean"),
        total_sales=("Sales", "sum"),
        order_count=("Order ID", "nunique") if "Order ID" in df.columns else ("Sales", "count"),
    ).reset_index().sort_values("_month")

    # Normalize to show relative strength (100 = average month)
    mean_sales = agg["total_sales"].mean()
    agg["seasonality_index"] = (agg["total_sales"] / max(mean_sales, 1) * 100).round(1)

    return agg[["_month_name", "total_sales", "order_count", "seasonality_index"]].rename(
        columns={"_month_name": "Month"}
    ).round(2)


def detect_peak_periods(df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
    """Identify the top N peak sales periods (months).

    Returns list of dicts with period, sales, and how much above average.
    """
    if "Order Date" not in df.columns or "Sales" not in df.columns:
        return []

    df = df.copy()
    df["_period"] = df["Order Date"].dt.to_period("M")

    monthly = df.groupby("_period")["Sales"].sum().reset_index()
    monthly.columns = ["Period", "Sales"]
    monthly = monthly.sort_values("Sales", ascending=False)

    avg = monthly["Sales"].mean()
    peaks = []
    for _, row in monthly.head(top_n).iterrows():
        pct_above = ((row["Sales"] - avg) / max(avg, 1)) * 100
        peaks.append({
            "period": str(row["Period"]),
            "sales": round(row["Sales"], 2),
            "pct_above_avg": round(pct_above, 1),
        })

    return peaks


def weekday_vs_weekend(df: pd.DataFrame) -> Dict:
    """Compare weekday vs weekend performance."""
    if "Order Date" not in df.columns or "Sales" not in df.columns:
        return {}

    df = df.copy()
    df["_is_weekend"] = df["Order Date"].dt.dayofweek >= 5

    weekday = df[~df["_is_weekend"]]
    weekend = df[df["_is_weekend"]]

    wd_orders = weekday["Order ID"].nunique() if "Order ID" in df.columns else len(weekday)
    we_orders = weekend["Order ID"].nunique() if "Order ID" in df.columns else len(weekend)

    return {
        "weekday_sales": round(weekday["Sales"].sum(), 2),
        "weekend_sales": round(weekend["Sales"].sum(), 2),
        "weekday_avg_order": round(weekday["Sales"].sum() / max(wd_orders, 1), 2),
        "weekend_avg_order": round(weekend["Sales"].sum() / max(we_orders, 1), 2),
        "weekday_orders": wd_orders,
        "weekend_orders": we_orders,
        "weekend_share_pct": round(weekend["Sales"].sum() / max(df["Sales"].sum(), 1) * 100, 1),
    }


# ═══════════════════════════════════════════════
#  SMART INSIGHTS GENERATOR
# ═══════════════════════════════════════════════
def generate_smart_insights(
    df: pd.DataFrame,
    clv_summary: Dict,
    churn: Dict,
    peaks: List[Dict],
    wdwe: Dict,
) -> List[str]:
    """Generate intelligent insights from all computed metrics."""
    insights = []

    # CLV insights
    if clv_summary:
        rr = clv_summary.get("repeat_rate_pct", 0)
        if rr < 20:
            insights.append(
                f"🚨 **Low repeat rate ({rr}%)** — most customers buy only once. "
                f"Consider loyalty programs, post-purchase emails, or subscription options."
            )
        elif rr > 50:
            insights.append(
                f"🌟 **Strong repeat rate ({rr}%)** — customers are coming back. "
                f"Focus on increasing average order value (currently ${clv_summary.get('avg_order_value', 0):,.0f})."
            )
        else:
            insights.append(
                f"📊 **Repeat purchase rate: {rr}%** with avg CLV of ${clv_summary.get('avg_clv', 0):,.0f}. "
                f"Top 10% of customers spend ${clv_summary.get('top_10pct_clv', 0):,.0f}+."
            )

        avg_basket = clv_summary.get("avg_basket_size", 0)
        if avg_basket < 2:
            insights.append(
                f"🛒 **Average basket size is {avg_basket:.1f} items** — consider cross-selling, "
                f"bundles, or 'frequently bought together' recommendations."
            )

    # Churn insights
    if churn:
        churn_pct = churn.get("churned_pct", 0)
        at_risk_pct = churn.get("at_risk_pct", 0)
        if churn_pct > 30:
            insights.append(
                f"⚠️ **{churn_pct}% of customers have churned** ({churn.get('churned', 0):,} customers). "
                f"Win-back campaigns could recover significant revenue."
            )
        if at_risk_pct > 20:
            insights.append(
                f"🔔 **{at_risk_pct}% of customers are at risk** ({churn.get('at_risk', 0):,}). "
                f"Target them with re-engagement offers before they churn."
            )

    # Seasonality insights
    if peaks and len(peaks) >= 2:
        top = peaks[0]
        insights.append(
            f"📅 **Peak sales period: {top['period']}** — {top['pct_above_avg']:.0f}% above average. "
            f"Plan inventory and marketing around these peaks."
        )

    # Weekday vs weekend
    if wdwe:
        we_share = wdwe.get("weekend_share_pct", 0)
        wd_avg = wdwe.get("weekday_avg_order", 0)
        we_avg = wdwe.get("weekend_avg_order", 0)
        if we_avg > wd_avg * 1.2:
            insights.append(
                f"🗓️ **Weekend orders are {((we_avg/max(wd_avg,1))-1)*100:.0f}% higher** "
                f"(${we_avg:,.0f} vs ${wd_avg:,.0f} weekday). Boost weekend promotions."
            )
        elif wd_avg > we_avg * 1.2:
            insights.append(
                f"🗓️ **Weekday orders outperform weekends** "
                f"(${wd_avg:,.0f} vs ${we_avg:,.0f}). Consider weekend-specific deals."
            )

    return insights
