"""
AI-Powered Insights Generator.

Produces natural-language business recommendations by analysing the data
and surfacing the most impactful findings.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from src.config import fmt_currency, fmt_pct


def generate_executive_summary(df: pd.DataFrame) -> List[str]:
    """Return a list of executive insight strings."""
    insights: List[str] = []

    total_sales  = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    margin       = (total_profit / max(total_sales, 1)) * 100

    # 1 — Overall health
    if margin > 15:
        insights.append(f"✅ **Healthy profit margin at {margin:.1f}%** — the business is operating above the typical 10-15% e-commerce benchmark.")
    elif margin > 5:
        insights.append(f"⚠️ **Profit margin at {margin:.1f}%** — below the healthy 15% threshold.  Focus on reducing discounts and cutting low-margin products.")
    else:
        insights.append(f"🚨 **Critical: Profit margin is only {margin:.1f}%** — immediate action needed on pricing strategy and cost control.")

    # 2 — Best / worst region
    region_profit = df.groupby("Region")["Profit"].sum().sort_values()
    best_region  = region_profit.index[-1]
    worst_region = region_profit.index[0]
    insights.append(
        f"🏆 **{best_region}** is the most profitable region ({fmt_currency(region_profit.iloc[-1])}), "
        f"while **{worst_region}** lags at {fmt_currency(region_profit.iloc[0])}."
    )

    # 3 — Loss-making sub-categories
    subcat_profit = df.groupby("Sub-Category")["Profit"].sum()
    losers = subcat_profit[subcat_profit < 0]
    if len(losers) > 0:
        names = ", ".join(losers.index.tolist())
        total_loss = losers.sum()
        insights.append(
            f"🔴 **Loss-making products: {names}** — collectively losing {fmt_currency(abs(total_loss))}. "
            f"Evaluate whether to discontinue, reprice, or reduce discounts on these items."
        )

    # 4 — Discount danger
    heavy_discount = df[df["Discount"] >= 0.20]
    if len(heavy_discount) > 0:
        hd_margin = (heavy_discount["Profit"].sum() / max(heavy_discount["Sales"].sum(), 1)) * 100
        no_discount = df[df["Discount"] == 0]
        nd_margin = (no_discount["Profit"].sum() / max(no_discount["Sales"].sum(), 1)) * 100
        insights.append(
            f"💸 **Heavy discounts (≥20%) yield {hd_margin:.1f}% margin** vs **{nd_margin:.1f}% at full price**. "
            f"Consider capping maximum discount at 15-20%."
        )

    # 5 — Top product
    top_prod = df.groupby("Sub-Category")["Sales"].sum().idxmax()
    top_sales = df.groupby("Sub-Category")["Sales"].sum().max()
    insights.append(f"⭐ **{top_prod}** is the top-selling sub-category at {fmt_currency(top_sales)}.")

    # 6 — Segment insight
    seg = df.groupby("Segment").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    seg["Margin"] = seg["Profit"] / seg["Sales"] * 100
    best_seg = seg["Margin"].idxmax()
    insights.append(
        f"👥 **{best_seg}** segment has the highest profit margin ({seg['Margin'].max():.1f}%) — "
        f"prioritize marketing spend here."
    )

    # 7 — Growth trend
    yearly = df.groupby("Year")["Sales"].sum()
    if len(yearly) >= 2:
        years = sorted(yearly.index)
        growth = ((yearly[years[-1]] - yearly[years[-2]]) / max(yearly[years[-2]], 1)) * 100
        direction = "📈 grew" if growth > 0 else "📉 declined"
        insights.append(
            f"Sales {direction} by **{abs(growth):.1f}%** from {years[-2]} to {years[-1]}."
        )

    return insights


def generate_product_recommendations(df: pd.DataFrame) -> List[str]:
    """Generate product-specific recommendations."""
    recs: List[str] = []

    # High-sales, low-margin products
    subcat = df.groupby("Sub-Category").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount", "mean"),
    )
    subcat["Margin"] = subcat["Profit"] / subcat["Sales"] * 100

    high_sales_low_margin = subcat[(subcat["Sales"] > subcat["Sales"].median()) & (subcat["Margin"] < 5)]
    for name, row in high_sales_low_margin.iterrows():
        recs.append(
            f"🔧 **{name}**: High volume ({fmt_currency(row['Sales'])}) but only {row['Margin']:.1f}% margin. "
            f"Average discount is {row['Avg_Discount']*100:.0f}%. Reduce discounts to improve profitability."
        )

    # Stars — high sales + high margin
    stars = subcat[(subcat["Sales"] > subcat["Sales"].median()) & (subcat["Margin"] > subcat["Margin"].median())]
    if len(stars) > 0:
        names = ", ".join(stars.index.tolist())
        recs.append(f"🌟 **Star products ({names})** — invest more in marketing and inventory for these high-performers.")

    return recs


def generate_anomaly_narrative(anomaly_df: pd.DataFrame) -> List[str]:
    """Narrate anomalies in human readable form."""
    flagged = anomaly_df[anomaly_df["Is Anomaly"]]
    if len(flagged) == 0:
        return ["✅ No significant anomalies detected in the time series."]

    narratives = []
    for _, row in flagged.iterrows():
        date_str = row["Date"].strftime("%B %Y")
        atype = row["Anomaly Type"]
        narratives.append(
            f"{atype} in **{date_str}** — Sales were {fmt_currency(row['Sales'])} "
            f"(Z-score: {row['Z-Score']:.2f}). Investigate promotional events or supply disruptions."
        )
    return narratives
