"""
E-Commerce Sales Analytics Platform — Premium Dashboard.

8-page Streamlit application with global filters, interactive Plotly charts,
AI-powered insights, and data export functionality.
"""

import streamlit as st
import pandas as pd
import sys
import os

# ── Path setup ────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_data, preprocess_data
from src.analysis import (
    key_metrics, period_comparison, sales_by_dimension, profit_by_dimension,
    full_dimension_summary, monthly_trends, quarterly_trends,
    top_products, bottom_products, customer_segmentation,
    rfm_analysis, abc_analysis, cohort_analysis,
    detect_anomalies, sales_forecast, discount_impact,
    correlation_analysis, yoy_growth,
)
from src.insights import (
    generate_executive_summary, generate_product_recommendations,
    generate_anomaly_narrative,
)
from src.visualization import (
    kpi_sparkline, bar_chart, grouped_bar, sales_profit_bars,
    sales_treemap, trend_line, forecast_chart, donut_chart,
    scatter_sales_profit, sales_heatmap, correlation_heatmap,
    profit_waterfall, pareto_chart, anomaly_chart,
    rfm_scatter, cohort_heatmap, discount_impact_chart, yoy_chart,
)
from src.config import COLORS, fmt_currency, fmt_pct, fmt_number
from app.theme import inject_theme, render_insight_card, render_footer, section_header

# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="E-Commerce Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

# ══════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_all_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "superstore_sales.csv")
    df = load_data(data_path)
    df = preprocess_data(df)
    return df

raw_df = load_all_data()

# ══════════════════════════════════════════════
#  SIDEBAR — GLOBAL FILTERS
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📊 Analytics Platform")
    st.markdown("---")

    page = st.radio("Navigate", [
        "🏠 Executive Overview",
        "💰 Sales Deep Dive",
        "📈 Profitability",
        "👥 Customer Intelligence",
        "📦 Product Analytics",
        "📉 Trends & Forecast",
        "🗺️ Geographic Intelligence",
        "🚨 Anomalies & Alerts",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("##### 🔍 Global Filters")

    # Date range
    min_date = raw_df["Order Date"].min().date()
    max_date = raw_df["Order Date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Region
    regions = st.multiselect(
        "Region",
        options=sorted(raw_df["Region"].unique()),
        default=sorted(raw_df["Region"].unique()),
    )

    # Category
    categories = st.multiselect(
        "Category",
        options=sorted(raw_df["Category"].unique()),
        default=sorted(raw_df["Category"].unique()),
    )

    # Segment
    segments = st.multiselect(
        "Segment",
        options=sorted(raw_df["Segment"].unique()),
        default=sorted(raw_df["Segment"].unique()),
    )

    st.markdown("---")
    st.caption("⚡ E-Commerce Analytics Platform v2.0")

# ── Apply Filters ─────────────────────────────
df = raw_df.copy()
if len(date_range) == 2:
    df = df[(df["Order Date"].dt.date >= date_range[0]) & (df["Order Date"].dt.date <= date_range[1])]
df = df[df["Region"].isin(regions)]
df = df[df["Category"].isin(categories)]
df = df[df["Segment"].isin(segments)]

# Guard
if len(df) == 0:
    st.warning("⚠️ No data matches the current filters. Adjust the sidebar filters.")
    st.stop()


# ══════════════════════════════════════════════
#  HELPER: Download button
# ══════════════════════════════════════════════
def download_csv(dataframe: pd.DataFrame, filename: str, label: str = "📥 Download CSV"):
    csv = dataframe.to_csv(index=False).encode("utf-8")
    st.download_button(label, csv, filename, "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Executive Overview":
    st.markdown("# 🏠 Executive Overview")
    st.caption(f"Showing data from {date_range[0]} to {date_range[1]}  ·  {len(df):,} transactions")

    # KPIs with deltas
    metrics = key_metrics(df)
    deltas  = period_comparison(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", fmt_currency(metrics["Total Sales"]),
              delta=fmt_pct(deltas["sales_delta"]))
    c2.metric("Total Profit", fmt_currency(metrics["Total Profit"]),
              delta=fmt_pct(deltas["profit_delta"]))
    c3.metric("Total Orders", fmt_number(metrics["Total Orders"]),
              delta=fmt_pct(deltas["orders_delta"]))
    c4.metric("Profit Margin", f"{metrics['Profit Margin %']:.1f}%",
              delta=fmt_pct(deltas["margin_delta"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Order Value", fmt_currency(metrics["Average Order Value"]))
    c6.metric("Total Items Sold", fmt_number(metrics["Total Quantity"]))
    c7.metric("Avg Discount", f"{metrics['Avg Discount']:.1f}%")
    c8.metric("Items / Order", f"{metrics['Avg Items/Order']:.1f}")

    st.markdown("---")

    # Charts row
    col_left, col_right = st.columns([3, 2])

    with col_left:
        monthly = monthly_trends(df)
        st.plotly_chart(trend_line(monthly, "Revenue & Profit Trend"), use_container_width=True)

    with col_right:
        seg_data = customer_segmentation(df)
        st.plotly_chart(
            donut_chart(seg_data.index.tolist(), seg_data["Sales"].tolist(), "Revenue by Segment"),
            use_container_width=True,
        )

    # AI Insights
    st.markdown("### 🧠 AI-Powered Insights")
    insights = generate_executive_summary(df)
    for insight in insights:
        render_insight_card(insight)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — SALES DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Sales Deep Dive":
    section_header("💰", "Sales Deep Dive", "Drill into revenue performance across every dimension")

    # Treemap
    st.plotly_chart(sales_treemap(df), use_container_width=True)

    st.markdown("---")

    # Heatmap + Bars
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(sales_heatmap(df), use_container_width=True)

    with col2:
        st.plotly_chart(sales_profit_bars(df, "Region", "Sales & Profit by Region"),
                        use_container_width=True)

    st.markdown("---")

    # Dimension summary table
    st.markdown("### 📋 Detailed Breakdown")
    dim = st.selectbox("Analyze by", ["Region", "Category", "Sub-Category", "Segment"], key="sales_dim")
    summary = full_dimension_summary(df, dim)
    st.dataframe(summary, use_container_width=True, height=350)
    download_csv(summary.reset_index(), f"sales_by_{dim.lower()}.csv")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — PROFITABILITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Profitability":
    section_header("📈", "Profitability Analysis", "Understand what drives profit and what's destroying it")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(profit_waterfall(df, "Category"), use_container_width=True)

    with col2:
        st.plotly_chart(scatter_sales_profit(df, "Sub-Category"), use_container_width=True)

    st.markdown("---")

    # Discount impact
    st.markdown("### 💸 Discount Impact on Profitability")
    disc_data = discount_impact(df)
    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(discount_impact_chart(disc_data), use_container_width=True)
    with col2:
        st.dataframe(disc_data, use_container_width=True, height=300)

    st.markdown("---")

    # Correlation
    st.markdown("### 🔗 Correlation Matrix")
    corr = correlation_analysis(df)
    st.plotly_chart(correlation_heatmap(corr), use_container_width=True)

    # Loss-making products
    st.markdown("### 🚨 Loss-Making Products")
    losers = bottom_products(df, 5)
    st.dataframe(losers, use_container_width=True)

    # Recommendations
    st.markdown("### 🧠 Product Recommendations")
    recs = generate_product_recommendations(df)
    for rec in recs:
        render_insight_card(rec)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — CUSTOMER INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥 Customer Intelligence":
    section_header("👥", "Customer Intelligence", "Segment, target, and retain your best customers")

    tab1, tab2, tab3 = st.tabs(["Segment Overview", "RFM Analysis", "Cohort Retention"])

    with tab1:
        seg = customer_segmentation(df)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                donut_chart(seg.index.tolist(), seg["Sales"].tolist(), "Revenue by Segment"),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                donut_chart(seg.index.tolist(), seg["Profit"].tolist(), "Profit by Segment"),
                use_container_width=True,
            )

        st.markdown("### 📋 Segment P&L")
        st.dataframe(seg, use_container_width=True)

    with tab2:
        st.markdown("### 🎯 RFM Customer Segmentation")
        st.caption("Using Segment + Region as customer proxy (dataset lacks Customer ID)")
        rfm = rfm_analysis(df)
        st.plotly_chart(rfm_scatter(rfm), use_container_width=True)

        st.markdown("### 📋 RFM Detail Table")
        st.dataframe(rfm, use_container_width=True, height=400)
        download_csv(rfm, "rfm_segmentation.csv")

    with tab3:
        st.markdown("### 📊 Cohort Retention Matrix")
        retention = cohort_analysis(df)
        st.plotly_chart(cohort_heatmap(retention), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 5 — PRODUCT ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Product Analytics":
    section_header("📦", "Product Analytics", "ABC classification and product performance matrix")

    # ABC Analysis
    st.markdown("### 🏷️ ABC Product Classification")
    abc = abc_analysis(df)
    st.plotly_chart(pareto_chart(abc), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    a_count = len(abc[abc["Class"] == "A"])
    b_count = len(abc[abc["Class"] == "B"])
    c_count = len(abc[abc["Class"] == "C"])
    col1.metric("Class A (Top 80%)", f"{a_count} products",
                delta=f"{abc[abc['Class']=='A']['Sales Share %'].sum():.0f}% of revenue")
    col2.metric("Class B (Next 15%)", f"{b_count} products",
                delta=f"{abc[abc['Class']=='B']['Sales Share %'].sum():.0f}% of revenue")
    col3.metric("Class C (Bottom 5%)", f"{c_count} products",
                delta=f"{abc[abc['Class']=='C']['Sales Share %'].sum():.0f}% of revenue")

    st.dataframe(abc, use_container_width=True, height=350)
    download_csv(abc, "abc_classification.csv")

    st.markdown("---")

    # Product performance scatter
    st.markdown("### 🎯 Product Performance Matrix")
    st.plotly_chart(scatter_sales_profit(df, "Sub-Category"), use_container_width=True)

    # Top products table
    st.markdown("### 🏆 Top Products")
    n = st.slider("Show top N products", 5, 20, 10)
    top = top_products(df, n)
    st.dataframe(top, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 6 — TRENDS & FORECAST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📉 Trends & Forecast":
    section_header("📉", "Trends & Forecasting", "Time-series analysis with EMA-based projections")

    tab1, tab2, tab3 = st.tabs(["Monthly Trends", "Forecasting", "Year-over-Year"])

    with tab1:
        monthly = monthly_trends(df)
        st.plotly_chart(trend_line(monthly, "Monthly Sales & Profit"), use_container_width=True)

        st.markdown("### 📊 Growth Rates (Month-over-Month)")
        growth_cols = ["Date", "Sales", "Profit", "Sales MoM %", "Profit MoM %", "Margin %"]
        available = [c for c in growth_cols if c in monthly.columns]
        st.dataframe(monthly[available], use_container_width=True, height=350)
        download_csv(monthly, "monthly_trends.csv")

    with tab2:
        st.markdown("### 🔮 Sales Forecast (6-Month Projection)")
        forecast_data = sales_forecast(df, periods=6)
        st.plotly_chart(forecast_chart(forecast_data), use_container_width=True)
        st.caption("Forecast based on Exponential Moving Average (EMA) with trend extrapolation. For demonstration purposes.")

    with tab3:
        st.markdown("### 📅 Year-over-Year Comparison")
        yearly = yoy_growth(df)
        st.plotly_chart(yoy_chart(yearly), use_container_width=True)
        st.dataframe(yearly, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 7 — GEOGRAPHIC INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Geographic Intelligence":
    section_header("🗺️", "Geographic Intelligence", "Regional performance benchmarking and market share")

    # Regional P&L
    region_summary = full_dimension_summary(df, "Region")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(sales_profit_bars(df, "Region", "Sales & Profit by Region"),
                        use_container_width=True)
    with col2:
        st.plotly_chart(
            donut_chart(region_summary.index.tolist(),
                        region_summary["Sales"].tolist(), "Regional Market Share"),
            use_container_width=True,
        )

    st.markdown("---")

    # Regional category breakdown
    st.markdown("### 📊 Region × Category Performance")
    pivot = df.pivot_table(index="Region", columns="Category",
                           values="Sales", aggfunc="sum").fillna(0).round(0)
    st.dataframe(pivot.style.format("${:,.0f}").background_gradient(cmap="Blues"),
                 use_container_width=True)

    st.markdown("---")

    # Full P&L table
    st.markdown("### 📋 Regional P&L Summary")
    st.dataframe(region_summary, use_container_width=True)
    download_csv(region_summary.reset_index(), "regional_performance.csv")

    # Insights
    st.markdown("### 🧠 Geographic Insights")
    best = region_summary["Sales"].idxmax()
    worst_margin = region_summary["Margin %"].idxmin()
    render_insight_card(
        f"🏆 **{best}** leads in total revenue with {fmt_currency(region_summary.loc[best, 'Sales'])}."
    )
    render_insight_card(
        f"⚠️ **{worst_margin}** has the lowest margin at {region_summary.loc[worst_margin, 'Margin %']:.1f}% "
        f"— investigate pricing and discount practices in this region."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 8 — ANOMALIES & ALERTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚨 Anomalies & Alerts":
    section_header("🚨", "Anomalies & Alerts", "Statistical anomaly detection in sales and profit patterns")

    tab1, tab2 = st.tabs(["Sales Anomalies", "Profit Anomalies"])

    with tab1:
        anomaly_data = detect_anomalies(df, metric="Sales")
        st.plotly_chart(anomaly_chart(anomaly_data), use_container_width=True)

        anomaly_count = anomaly_data["Is Anomaly"].sum()
        st.metric("Anomalies Detected", f"{anomaly_count} months flagged")

        narratives = generate_anomaly_narrative(anomaly_data)
        st.markdown("### 📝 Anomaly Narrative")
        for n in narratives:
            render_insight_card(n)

        if anomaly_count > 0:
            st.markdown("### 📋 Flagged Data Points")
            flagged = anomaly_data[anomaly_data["Is Anomaly"]]
            st.dataframe(flagged[["Date", "Sales", "Profit", "Z-Score", "Anomaly Type"]],
                         use_container_width=True)

    with tab2:
        anomaly_profit = detect_anomalies(df, metric="Profit")
        # Reuse the same chart structure for profit
        normal  = anomaly_profit[~anomaly_profit["Is Anomaly"]]
        anomaly = anomaly_profit[anomaly_profit["Is Anomaly"]]

        import plotly.graph_objects as go
        from src.config import ANOMALY_Z_THRESHOLD as Z

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=normal["Date"], y=normal["Profit"],
            mode="lines+markers", name="Normal",
            line=dict(color=COLORS["secondary"], width=2),
        ))
        if len(anomaly) > 0:
            fig.add_trace(go.Scatter(
                x=anomaly["Date"], y=anomaly["Profit"],
                mode="markers", name="Anomaly",
                marker=dict(color=COLORS["danger"], size=14, symbol="x"),
            ))
        mean_p = anomaly_profit["Profit"].mean()
        std_p  = anomaly_profit["Profit"].std()
        fig.add_hline(y=mean_p, line_dash="dash", line_color=COLORS["text_muted"], opacity=0.5)
        fig.update_layout(
            title="Anomaly Detection — Monthly Profit", height=440,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_primary"]),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        profit_anomalies = anomaly_profit["Is Anomaly"].sum()
        st.metric("Profit Anomalies Detected", f"{profit_anomalies} months flagged")


# ══════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════
render_footer()