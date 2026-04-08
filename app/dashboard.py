"""
Universal Analytics Platform — Premium Dashboard.

Two-mode architecture:
  Mode 1: Universal Analytics — auto-detects columns from ANY uploaded file
  Mode 2: E-Commerce Deep Dive — specialized analytics for the sample dataset

Features: file upload, auto-detection, back button, mobile responsive, CSV export.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# ── Path setup ────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generic_analysis import (
    detect_column_types, auto_preprocess, data_profile,
    compute_kpis, compute_numeric_distribution, compute_categorical_distribution,
    compute_correlations, find_top_correlations,
    compute_time_aggregates, compute_group_summary,
    detect_outliers, generate_generic_insights,
)
from src.config import COLORS
from app.theme import (
    inject_theme, render_insight_card, render_footer,
    section_header, render_file_badge,
)

# ── E-Commerce imports (lazy, only used for sample data) ──
def _load_ecommerce_modules():
    from src.data_loader import load_data, preprocess_data
    from src.analysis import (
        key_metrics, period_comparison, sales_by_dimension,
        profit_by_dimension, full_dimension_summary, monthly_trends,
        quarterly_trends, top_products, bottom_products,
        customer_segmentation, rfm_analysis, abc_analysis,
        cohort_analysis, detect_anomalies, sales_forecast,
        discount_impact, correlation_analysis, yoy_growth,
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
    from src.config import fmt_currency, fmt_pct, fmt_number
    return locals()


# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Universal Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

# ══════════════════════════════════════════════
#  PLOTLY DEFAULTS
# ══════════════════════════════════════════════
CHART_COLORS = [
    "#6366F1", "#22C55E", "#F59E0B", "#EF4444", "#3B82F6",
    "#EC4899", "#14B8A6", "#F97316", "#8B5CF6", "#06B6D4",
]

_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC", family="Inter"),
    hovermode="x unified",
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=CHART_COLORS,
    xaxis=dict(gridcolor="rgba(71,85,105,0.3)"),
    yaxis=dict(gridcolor="rgba(71,85,105,0.3)"),
)


def _apply_layout(fig, **overrides):
    """Apply base dark layout to any Plotly figure with optional overrides."""
    layout = {**_BASE_LAYOUT, "height": 420}
    layout.update(overrides)
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════
if "is_data_loaded" not in st.session_state:
    st.session_state.is_data_loaded = False
    st.session_state.df = None
    st.session_state.col_types = None
    st.session_state.filename = None
    st.session_state.mode = None  # "universal" or "ecommerce"


def reset_state():
    st.session_state.is_data_loaded = False
    st.session_state.df = None
    st.session_state.col_types = None
    st.session_state.filename = None
    st.session_state.mode = None


# ══════════════════════════════════════════════
#  UPLOAD SCREEN
# ══════════════════════════════════════════════
if not st.session_state.is_data_loaded:
    st.markdown(
        "<h1 style='text-align: center; margin-top: 40px;'>"
        "📊 Universal Analytics Platform</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #94a3b8; margin-bottom: 40px;'>"
        "Upload <strong>any</strong> CSV or Excel file — we'll auto-detect your data "
        "and build a complete analytical dashboard instantly.</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        uploaded_file = st.file_uploader(
            "Drag and drop or browse",
            type=["csv", "xlsx", "xls"],
            help="Accepts CSV, XLSX, and XLS files up to 200MB.",
        )

        if uploaded_file is not None:
            try:
                with st.spinner("Reading file..."):
                    if uploaded_file.name.endswith(".csv"):
                        try:
                            temp_df = pd.read_csv(uploaded_file)
                        except UnicodeDecodeError:
                            uploaded_file.seek(0)
                            temp_df = pd.read_csv(uploaded_file, encoding="latin-1")
                    else:
                        temp_df = pd.read_excel(uploaded_file)

                st.success(
                    f"✅ **{uploaded_file.name}** loaded — "
                    f"{temp_df.shape[0]:,} rows × {temp_df.shape[1]} columns"
                )

                with st.expander("👀 Preview Data (first 5 rows)", expanded=True):
                    st.dataframe(temp_df.head(), use_container_width=True)

                col_types = detect_column_types(temp_df)

                st.markdown("### 🔍 Auto-Detected Column Types")
                dc = st.columns(4)
                with dc[0]:
                    st.metric("Numeric", len(col_types["numeric"]))
                    if col_types["numeric"]:
                        st.caption(", ".join(col_types["numeric"][:5]))
                with dc[1]:
                    st.metric("Categorical", len(col_types["categorical"]))
                    if col_types["categorical"]:
                        st.caption(", ".join(col_types["categorical"][:5]))
                with dc[2]:
                    st.metric("Date/Time", len(col_types["datetime"]))
                    if col_types["datetime"]:
                        st.caption(", ".join(col_types["datetime"][:5]))
                with dc[3]:
                    st.metric("ID / Other", len(col_types["id"]) + len(col_types["boolean"]))

                if st.button(
                    "🚀 Generate Analytics Dashboard",
                    use_container_width=True,
                    type="primary",
                ):
                    with st.spinner("Auto-detecting types & preprocessing..."):
                        processed = auto_preprocess(temp_df, col_types)
                        st.session_state.df = processed
                        st.session_state.col_types = col_types
                        st.session_state.filename = uploaded_file.name
                        st.session_state.mode = "universal"
                        st.session_state.is_data_loaded = True
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Could not process file: {str(e)}")

        st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #94a3b8;'>"
            "Or try the built-in e-commerce dataset:</p>",
            unsafe_allow_html=True,
        )

        if st.button("📦 Use Sample E-Commerce Data", use_container_width=True):
            with st.spinner("Loading sample data..."):
                from src.data_loader import load_data, preprocess_data
                data_path = os.path.join(
                    os.path.dirname(__file__), "..", "data", "superstore_sales.csv"
                )
                df = load_data(data_path)
                df = preprocess_data(df)
                st.session_state.df = df
                st.session_state.filename = "superstore_sales.csv"
                st.session_state.mode = "ecommerce"
                st.session_state.is_data_loaded = True
                st.rerun()

    st.stop()


# ══════════════════════════════════════════════
#  DATA IS LOADED — ROUTE TO CORRECT MODE
# ══════════════════════════════════════════════
raw_df = st.session_state.df


def download_csv(dataframe, filename, label="📥 Download CSV"):
    csv = dataframe.to_csv(index=False).encode("utf-8")
    st.download_button(label, csv, filename, "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
#  UNIVERSAL ANALYTICS MODE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == "universal":
    col_types = st.session_state.col_types
    numeric_cols = col_types["numeric"]
    cat_cols = col_types["categorical"]
    date_cols = col_types["datetime"]

    # Build pages dynamically
    pages = ["🏠 Overview", "📊 Distributions", "🔗 Relationships"]
    if date_cols:
        pages.append("📈 Time Analysis")
    if cat_cols and numeric_cols:
        pages.append("🏷️ Group Analysis")
    pages.append("🔎 Data Explorer")

    with st.sidebar:
        st.markdown("# 📊 Analytics")
        if st.button("⬅️ Upload New File", use_container_width=True):
            reset_state()
            st.rerun()
        st.markdown("---")
        render_file_badge(st.session_state.filename, len(raw_df), len(raw_df.columns))
        st.markdown("---")
        page = st.radio("Navigate", pages, label_visibility="collapsed")

    # ── PAGE: OVERVIEW ──────────────────────────
    if page == "🏠 Overview":
        st.markdown(f"# 🏠 Overview — {st.session_state.filename}")
        profile = data_profile(raw_df)
        st.caption(
            f"{profile['rows']:,} rows × {profile['columns']} columns · "
            f"{profile['memory_mb']:.1f} MB · "
            f"{profile['missing_pct']:.1f}% missing values"
        )

        if numeric_cols:
            st.markdown("### 📐 Numeric Summary")
            kpis = compute_kpis(raw_df, numeric_cols)
            cols_per_row = min(4, len(kpis))
            for i in range(0, len(kpis), cols_per_row):
                row_kpis = kpis[i:i + cols_per_row]
                cols = st.columns(cols_per_row)
                for j, kpi in enumerate(row_kpis):
                    with cols[j]:
                        st.metric(kpi["label"], f"{kpi['sum']:,.2f}")
                        st.caption(f"Mean: {kpi['mean']:,.2f} · Median: {kpi['median']:,.2f}")

        st.markdown("---")

        col_left, col_right = st.columns(2)
        with col_left:
            if cat_cols:
                cat = cat_cols[0]
                cdata = compute_categorical_distribution(raw_df, cat, 10)
                fig = px.bar(cdata, x=cat, y="Count", title=f"Top Values — {cat}",
                             color="Count", color_continuous_scale="Viridis")
                _apply_layout(fig, height=380, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with col_right:
            if len(numeric_cols) >= 2:
                fig = px.scatter(raw_df, x=numeric_cols[0], y=numeric_cols[1],
                                 title=f"{numeric_cols[0]} vs {numeric_cols[1]}", opacity=0.6)
                _apply_layout(fig, height=380)
                fig.update_traces(marker=dict(color=CHART_COLORS[0], size=5))
                st.plotly_chart(fig, use_container_width=True)
            elif numeric_cols:
                fig = px.histogram(raw_df, x=numeric_cols[0],
                                   title=f"Distribution — {numeric_cols[0]}", nbins=30)
                _apply_layout(fig, height=380, showlegend=False)
                fig.update_traces(marker_color=CHART_COLORS[0])
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🧠 Auto-Generated Insights")
        insights = generate_generic_insights(raw_df, col_types)
        for insight in insights:
            render_insight_card(insight)

    # ── PAGE: DISTRIBUTIONS ─────────────────────
    elif page == "📊 Distributions":
        section_header("📊", "Distributions", "Understand the spread and shape of every column")
        tab1, tab2 = st.tabs(["Numeric Columns", "Categorical Columns"])

        with tab1:
            if not numeric_cols:
                st.info("No numeric columns detected.")
            else:
                selected = st.multiselect("Select columns", numeric_cols,
                                          default=numeric_cols[:min(4, len(numeric_cols))])
                for i in range(0, len(selected), 2):
                    cols = st.columns(2)
                    for j, col_name in enumerate(selected[i:i+2]):
                        with cols[j]:
                            fig = px.histogram(raw_df, x=col_name,
                                               title=f"Distribution — {col_name}",
                                               nbins=30, marginal="box")
                            _apply_layout(fig, height=380, showlegend=False)
                            fig.update_traces(marker_color=CHART_COLORS[(i + j) % len(CHART_COLORS)])
                            st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📋 Descriptive Statistics")
                desc = raw_df[numeric_cols].describe().round(2)
                st.dataframe(desc, use_container_width=True)
                download_csv(desc.reset_index(), "descriptive_stats.csv")

        with tab2:
            if not cat_cols:
                st.info("No categorical columns detected.")
            else:
                sel_cat = st.selectbox("Select column", cat_cols)
                cat_data = compute_categorical_distribution(raw_df, sel_cat, 20)
                ca, cb = st.columns(2)
                with ca:
                    fig = px.bar(cat_data, x=sel_cat, y="Count",
                                 title=f"Value Counts — {sel_cat}",
                                 color=sel_cat, color_discrete_sequence=CHART_COLORS)
                    _apply_layout(fig, height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                with cb:
                    fig = px.pie(cat_data, names=sel_cat, values="Count",
                                 title=f"Share — {sel_cat}",
                                 hole=0.4, color_discrete_sequence=CHART_COLORS)
                    _apply_layout(fig, height=400)
                    st.plotly_chart(fig, use_container_width=True)
                st.dataframe(cat_data, use_container_width=True)

    # ── PAGE: RELATIONSHIPS ─────────────────────
    elif page == "🔗 Relationships":
        section_header("🔗", "Relationships", "Correlations and scatter analysis")

        if len(numeric_cols) < 2:
            st.info("Need at least 2 numeric columns for correlation analysis.")
        else:
            st.markdown("### 🔥 Correlation Matrix")
            corr = compute_correlations(raw_df, numeric_cols)
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1, title="Correlation Matrix")
            _apply_layout(fig, height=max(400, len(numeric_cols) * 45))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 🏆 Strongest Correlations")
            top_c = find_top_correlations(corr, min(8, len(numeric_cols)))
            if top_c:
                cdf = pd.DataFrame(top_c)
                cdf.columns = ["Column A", "Column B", "Correlation"]
                cdf["Strength"] = cdf["Correlation"].abs().apply(
                    lambda x: "🟢 Strong" if x > 0.7 else ("🟡 Moderate" if x > 0.4 else "⚪ Weak")
                )
                st.dataframe(cdf, use_container_width=True)

            st.markdown("### 🎯 Scatter Explorer")
            s1, s2 = st.columns(2)
            with s1:
                x_col = st.selectbox("X axis", numeric_cols, index=0)
            with s2:
                y_col = st.selectbox("Y axis", numeric_cols, index=min(1, len(numeric_cols) - 1))

            color_opt = None
            if cat_cols:
                color_opt = st.selectbox("Color by (optional)", ["None"] + cat_cols)
                if color_opt == "None":
                    color_opt = None

            fig = px.scatter(raw_df, x=x_col, y=y_col, color=color_opt,
                             title=f"{x_col} vs {y_col}", opacity=0.6,
                             color_discrete_sequence=CHART_COLORS)
            _apply_layout(fig, height=500)
            st.plotly_chart(fig, use_container_width=True)

    # ── PAGE: TIME ANALYSIS ─────────────────────
    elif page == "📈 Time Analysis":
        section_header("📈", "Time Analysis", "Trends and patterns over time")

        if not date_cols:
            st.info("No date/time columns detected.")
        else:
            date_col = st.selectbox("Date column", date_cols)
            metric_cols = st.multiselect("Metrics to plot", numeric_cols,
                                         default=numeric_cols[:min(3, len(numeric_cols))])
            if metric_cols:
                tdata = compute_time_aggregates(raw_df, date_col, metric_cols)
                if not tdata.empty:
                    pcol = tdata.columns[0]
                    for metric in metric_cols:
                        if metric in tdata.columns:
                            fig = px.line(tdata, x=pcol, y=metric,
                                          title=f"{metric} over {pcol}", markers=True)
                            _apply_layout(fig)
                            fig.update_traces(line=dict(width=2))
                            st.plotly_chart(fig, use_container_width=True)

                    if "Records" in tdata.columns:
                        fig = px.bar(tdata, x=pcol, y="Records",
                                     title=f"Record Count per {pcol}")
                        _apply_layout(fig, height=350, showlegend=False)
                        fig.update_traces(marker_color=CHART_COLORS[2])
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("### 📋 Time Aggregation Table")
                    st.dataframe(tdata.round(2), use_container_width=True)
                    download_csv(tdata, "time_analysis.csv")
                else:
                    st.warning("Could not aggregate data over time.")

    # ── PAGE: GROUP ANALYSIS ────────────────────
    elif page == "🏷️ Group Analysis":
        section_header("🏷️", "Group Analysis", "Compare metrics across categories")

        gcol = st.selectbox("Group by", cat_cols)
        gmetrics = st.multiselect("Metrics", numeric_cols,
                                   default=numeric_cols[:min(3, len(numeric_cols))])
        if gmetrics:
            gdata = compute_group_summary(raw_df, gcol, gmetrics)
            if not gdata.empty:
                first_sum = f"{gmetrics[0]}_sum"
                if first_sum in gdata.columns:
                    fig = px.bar(gdata, x=gcol, y=first_sum,
                                 title=f"Total {gmetrics[0]} by {gcol}",
                                 color=gcol, color_discrete_sequence=CHART_COLORS)
                    _apply_layout(fig, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                if len(gmetrics) > 1:
                    mcols = [f"{c}_mean" for c in gmetrics if f"{c}_mean" in gdata.columns]
                    if mcols:
                        melted = gdata.melt(id_vars=[gcol], value_vars=mcols,
                                            var_name="Metric", value_name="Average")
                        melted["Metric"] = melted["Metric"].str.replace("_mean", "")
                        fig = px.bar(melted, x=gcol, y="Average", color="Metric",
                                     barmode="group",
                                     title=f"Average Metrics by {gcol}",
                                     color_discrete_sequence=CHART_COLORS)
                        _apply_layout(fig)
                        st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📋 Full Summary Table")
                st.dataframe(gdata, use_container_width=True, height=400)
                download_csv(gdata, f"group_by_{gcol}.csv")

    # ── PAGE: DATA EXPLORER ─────────────────────
    elif page == "🔎 Data Explorer":
        section_header("🔎", "Data Explorer", "Search, filter, and export your data")

        show_cols = st.multiselect("Columns to display", raw_df.columns.tolist(),
                                   default=raw_df.columns.tolist()[:min(10, len(raw_df.columns))])
        search = st.text_input("🔍 Search across all text columns", "")

        display_df = raw_df[show_cols].copy() if show_cols else raw_df.copy()
        if search:
            mask = pd.Series([False] * len(display_df), index=display_df.index)
            for c in display_df.select_dtypes(include=["object"]).columns:
                mask |= display_df[c].astype(str).str.contains(search, case=False, na=False)
            display_df = display_df[mask]
            st.caption(f"Showing {len(display_df):,} matching rows")

        st.dataframe(display_df, use_container_width=True, height=500)
        download_csv(display_df, f"{st.session_state.filename}_filtered.csv")

        if numeric_cols:
            st.markdown("### 🚨 Outlier Detection")
            out_col = st.selectbox("Check outliers in", numeric_cols)
            outliers = detect_outliers(raw_df, out_col)
            if len(outliers) > 0:
                st.warning(f"Found {len(outliers)} outliers in **{out_col}**")
                st.dataframe(outliers.head(20), use_container_width=True)
            else:
                st.success(f"No significant outliers in **{out_col}**")

    render_footer()


# ══════════════════════════════════════════════════════════════════════════════
#  E-COMMERCE DEEP DIVE MODE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "ecommerce":
    ecom = _load_ecommerce_modules()

    with st.sidebar:
        st.markdown("# 📊 Analytics Platform")
        if st.button("⬅️ Upload New File", use_container_width=True):
            reset_state()
            st.rerun()
        st.markdown("---")
        render_file_badge("superstore_sales.csv", len(raw_df), len(raw_df.columns))
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

        min_date = raw_df["Order Date"].min().date()
        max_date = raw_df["Order Date"].max().date()
        if min_date == max_date:
            date_range = (min_date, max_date)
        else:
            date_range = st.date_input("Date Range", value=(min_date, max_date),
                                       min_value=min_date, max_value=max_date)

        regions = st.multiselect("Region", options=sorted(raw_df["Region"].unique()),
                                 default=sorted(raw_df["Region"].unique()))
        categories = st.multiselect("Category", options=sorted(raw_df["Category"].unique()),
                                    default=sorted(raw_df["Category"].unique()))
        segments = st.multiselect("Segment", options=sorted(raw_df["Segment"].unique()),
                                  default=sorted(raw_df["Segment"].unique()))

    # ── Apply filters ──
    df = raw_df.copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        df = df[(df["Order Date"].dt.date >= date_range[0]) & (df["Order Date"].dt.date <= date_range[1])]
    df = df[df["Region"].isin(regions)]
    df = df[df["Category"].isin(categories)]
    df = df[df["Segment"].isin(segments)]

    if len(df) == 0:
        st.warning("⚠️ No data matches filters.")
        st.stop()

    # Extract functions
    key_metrics = ecom["key_metrics"]
    period_comparison = ecom["period_comparison"]
    monthly_trends = ecom["monthly_trends"]
    customer_segmentation = ecom["customer_segmentation"]
    full_dimension_summary = ecom["full_dimension_summary"]
    rfm_analysis = ecom["rfm_analysis"]
    abc_analysis = ecom["abc_analysis"]
    cohort_analysis = ecom["cohort_analysis"]
    detect_anomalies_fn = ecom["detect_anomalies"]
    sales_forecast = ecom["sales_forecast"]
    discount_impact = ecom["discount_impact"]
    correlation_analysis = ecom["correlation_analysis"]
    yoy_growth = ecom["yoy_growth"]
    top_products = ecom["top_products"]
    bottom_products = ecom["bottom_products"]
    generate_executive_summary = ecom["generate_executive_summary"]
    generate_product_recommendations = ecom["generate_product_recommendations"]
    generate_anomaly_narrative = ecom["generate_anomaly_narrative"]
    trend_line = ecom["trend_line"]
    donut_chart = ecom["donut_chart"]
    sales_treemap = ecom["sales_treemap"]
    sales_heatmap = ecom["sales_heatmap"]
    sales_profit_bars = ecom["sales_profit_bars"]
    profit_waterfall = ecom["profit_waterfall"]
    scatter_sales_profit = ecom["scatter_sales_profit"]
    discount_impact_chart = ecom["discount_impact_chart"]
    correlation_heatmap = ecom["correlation_heatmap"]
    rfm_scatter = ecom["rfm_scatter"]
    cohort_heatmap = ecom["cohort_heatmap"]
    pareto_chart = ecom["pareto_chart"]
    anomaly_chart = ecom["anomaly_chart"]
    forecast_chart = ecom["forecast_chart"]
    yoy_chart = ecom["yoy_chart"]
    fmt_currency = ecom["fmt_currency"]
    fmt_pct = ecom["fmt_pct"]
    fmt_number = ecom["fmt_number"]

    # ── E-COMMERCE PAGES ──
    if page == "🏠 Executive Overview":
        st.markdown("# 🏠 Executive Overview")
        st.caption(f"Showing data from {date_range[0]} to {date_range[1]} · {len(df):,} transactions")
        metrics = key_metrics(df)
        deltas = period_comparison(df)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Revenue", fmt_currency(metrics["Total Sales"]), delta=fmt_pct(deltas["sales_delta"]))
        c2.metric("Total Profit", fmt_currency(metrics["Total Profit"]), delta=fmt_pct(deltas["profit_delta"]))
        c3.metric("Total Orders", fmt_number(metrics["Total Orders"]), delta=fmt_pct(deltas["orders_delta"]))
        c4.metric("Profit Margin", f"{metrics['Profit Margin %']:.1f}%", delta=fmt_pct(deltas["margin_delta"]))
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Avg Order Value", fmt_currency(metrics["Average Order Value"]))
        c6.metric("Total Items Sold", fmt_number(metrics["Total Quantity"]))
        c7.metric("Avg Discount", f"{metrics['Avg Discount']:.1f}%")
        c8.metric("Items / Order", f"{metrics['Avg Items/Order']:.1f}")
        st.markdown("---")
        cl, cr = st.columns([3, 2])
        with cl:
            monthly = monthly_trends(df)
            st.plotly_chart(trend_line(monthly, "Revenue & Profit Trend"), use_container_width=True)
        with cr:
            seg = customer_segmentation(df)
            st.plotly_chart(donut_chart(seg.index.tolist(), seg["Sales"].tolist(), "Revenue by Segment"), use_container_width=True)
        st.markdown("### 🧠 AI-Powered Insights")
        for ins in generate_executive_summary(df):
            render_insight_card(ins)

    elif page == "💰 Sales Deep Dive":
        section_header("💰", "Sales Deep Dive", "Drill into revenue performance")
        st.plotly_chart(sales_treemap(df), use_container_width=True)
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(sales_heatmap(df), use_container_width=True)
        with c2:
            st.plotly_chart(sales_profit_bars(df, "Region", "Sales & Profit by Region"), use_container_width=True)
        st.markdown("---")
        st.markdown("### 📋 Detailed Breakdown")
        dim = st.selectbox("Analyze by", ["Region", "Category", "Sub-Category", "Segment"])
        summary = full_dimension_summary(df, dim)
        st.dataframe(summary, use_container_width=True, height=350)
        download_csv(summary.reset_index(), f"sales_by_{dim.lower()}.csv")

    elif page == "📈 Profitability":
        section_header("📈", "Profitability Analysis", "Understand profit drivers")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(profit_waterfall(df, "Category"), use_container_width=True)
        with c2:
            st.plotly_chart(scatter_sales_profit(df, "Sub-Category"), use_container_width=True)
        st.markdown("---")
        st.markdown("### 💸 Discount Impact")
        disc = discount_impact(df)
        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(discount_impact_chart(disc), use_container_width=True)
        with c2:
            st.dataframe(disc, use_container_width=True, height=300)
        st.markdown("---")
        st.markdown("### 🔗 Correlation Matrix")
        corr = correlation_analysis(df)
        st.plotly_chart(correlation_heatmap(corr), use_container_width=True)
        st.markdown("### 🚨 Loss-Making Products")
        st.dataframe(bottom_products(df, 5), use_container_width=True)
        st.markdown("### 🧠 Recommendations")
        for rec in generate_product_recommendations(df):
            render_insight_card(rec)

    elif page == "👥 Customer Intelligence":
        section_header("👥", "Customer Intelligence", "Segment and retain customers")
        t1, t2, t3 = st.tabs(["Segment Overview", "RFM Analysis", "Cohort Retention"])
        with t1:
            seg = customer_segmentation(df)
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(donut_chart(seg.index.tolist(), seg["Sales"].tolist(), "Revenue by Segment"), use_container_width=True)
            with c2:
                st.plotly_chart(donut_chart(seg.index.tolist(), seg["Profit"].tolist(), "Profit by Segment"), use_container_width=True)
            st.dataframe(seg, use_container_width=True)
        with t2:
            st.markdown("### 🎯 RFM Segmentation")
            rfm = rfm_analysis(df)
            st.plotly_chart(rfm_scatter(rfm), use_container_width=True)
            st.dataframe(rfm, use_container_width=True, height=400)
            download_csv(rfm, "rfm_segmentation.csv")
        with t3:
            st.markdown("### 📊 Cohort Retention")
            retention = cohort_analysis(df)
            st.plotly_chart(cohort_heatmap(retention), use_container_width=True)

    elif page == "📦 Product Analytics":
        section_header("📦", "Product Analytics", "ABC classification and performance")
        st.markdown("### 🏷️ ABC Classification")
        abc = abc_analysis(df)
        st.plotly_chart(pareto_chart(abc), use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Class A (Top 80%)", f"{len(abc[abc['Class']=='A'])} products")
        c2.metric("Class B (Next 15%)", f"{len(abc[abc['Class']=='B'])} products")
        c3.metric("Class C (Bottom 5%)", f"{len(abc[abc['Class']=='C'])} products")
        st.dataframe(abc, use_container_width=True, height=350)
        download_csv(abc, "abc_classification.csv")
        st.markdown("---")
        st.plotly_chart(scatter_sales_profit(df, "Sub-Category"), use_container_width=True)
        st.markdown("### 🏆 Top Products")
        n = st.slider("Show top N", 5, 20, 10)
        st.dataframe(top_products(df, n), use_container_width=True)

    elif page == "📉 Trends & Forecast":
        section_header("📉", "Trends & Forecasting", "Time-series with EMA projections")
        t1, t2, t3 = st.tabs(["Monthly Trends", "Forecasting", "Year-over-Year"])
        with t1:
            monthly = monthly_trends(df)
            st.plotly_chart(trend_line(monthly, "Monthly Sales & Profit"), use_container_width=True)
            gcols = [c for c in ["Date", "Sales", "Profit", "Sales MoM %", "Profit MoM %", "Margin %"] if c in monthly.columns]
            st.dataframe(monthly[gcols], use_container_width=True, height=350)
            download_csv(monthly, "monthly_trends.csv")
        with t2:
            st.markdown("### 🔮 Sales Forecast (6 Months)")
            fd = sales_forecast(df, periods=6)
            st.plotly_chart(forecast_chart(fd), use_container_width=True)
        with t3:
            st.markdown("### 📅 Year-over-Year")
            yearly = yoy_growth(df)
            st.plotly_chart(yoy_chart(yearly), use_container_width=True)
            st.dataframe(yearly, use_container_width=True)

    elif page == "🗺️ Geographic Intelligence":
        section_header("🗺️", "Geographic Intelligence", "Regional performance")
        rsummary = full_dimension_summary(df, "Region")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(sales_profit_bars(df, "Region", "Sales & Profit by Region"), use_container_width=True)
        with c2:
            st.plotly_chart(donut_chart(rsummary.index.tolist(), rsummary["Sales"].tolist(), "Market Share"), use_container_width=True)
        st.markdown("---")
        st.markdown("### 📊 Region × Category")
        pivot = df.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="sum").fillna(0).round(0)
        st.dataframe(pivot.style.format("${:,.0f}").background_gradient(cmap="Blues"), use_container_width=True)
        st.markdown("---")
        st.dataframe(rsummary, use_container_width=True)
        download_csv(rsummary.reset_index(), "regional_performance.csv")

    elif page == "🚨 Anomalies & Alerts":
        section_header("🚨", "Anomalies & Alerts", "Statistical anomaly detection")
        t1, t2 = st.tabs(["Sales Anomalies", "Profit Anomalies"])
        with t1:
            anom = detect_anomalies_fn(df, metric="Sales")
            st.plotly_chart(anomaly_chart(anom), use_container_width=True)
            ac = anom["Is Anomaly"].sum()
            st.metric("Anomalies Detected", f"{ac} months flagged")
            st.markdown("### 📝 Narrative")
            for n in generate_anomaly_narrative(anom):
                render_insight_card(n)
            if ac > 0:
                st.dataframe(anom[anom["Is Anomaly"]][["Date", "Sales", "Profit", "Z-Score", "Anomaly Type"]], use_container_width=True)
        with t2:
            anom_p = detect_anomalies_fn(df, metric="Profit")
            normal = anom_p[~anom_p["Is Anomaly"]]
            anomaly = anom_p[anom_p["Is Anomaly"]]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=normal["Date"], y=normal["Profit"], mode="lines+markers", name="Normal", line=dict(color=COLORS["secondary"], width=2)))
            if len(anomaly) > 0:
                fig.add_trace(go.Scatter(x=anomaly["Date"], y=anomaly["Profit"], mode="markers", name="Anomaly", marker=dict(color=COLORS["danger"], size=14, symbol="x")))
            fig.add_hline(y=anom_p["Profit"].mean(), line_dash="dash", line_color=COLORS["text_muted"], opacity=0.5)
            _apply_layout(fig, title="Anomaly Detection — Monthly Profit", height=440)
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Profit Anomalies", f"{anom_p['Is Anomaly'].sum()} months flagged")

    render_footer()