"""
Plotly-only Visualization Factory.

Every chart uses a consistent dark theme and the project colour palette.
Charts are returned as go.Figure objects for direct use in Streamlit.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.config import COLORS, CHART_COLORS, PLOTLY_LAYOUT, fmt_currency


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Apply project dark theme to any figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def _empty_figure(message: str = "No data available") -> go.Figure:
    """Return a themed empty figure with a message annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=COLORS["text_muted"]),
    )
    fig.update_layout(
        height=300,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  KPI SPARKLINE
# ═══════════════════════════════════════════════
def kpi_sparkline(values: list, color: str = COLORS["primary"]) -> go.Figure:
    """Tiny sparkline for embedding in KPI cards."""
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)",
    ))
    fig.update_layout(
        height=60, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════
#  SALES & PROFIT CHARTS
# ═══════════════════════════════════════════════
def bar_chart(data: pd.Series, title: str, color: str = COLORS["primary"],
              horizontal: bool = False) -> go.Figure:
    """Generic bar chart from a Series."""
    if data is None or len(data) == 0:
        return _empty_figure(f"{title} — no data")
    orientation = "h" if horizontal else "v"
    x, y = (data.values, data.index) if horizontal else (data.index, data.values)

    fig = go.Figure(go.Bar(
        x=x, y=y, orientation=orientation,
        marker_color=color,
        text=[fmt_currency(v) for v in data.values],
        textposition="auto",
        textfont=dict(size=11),
    ))
    fig.update_layout(title=title, height=400)
    return _apply_theme(fig)


def grouped_bar(df: pd.DataFrame, x: str, y_cols: list,
                title: str, colors: list = None) -> go.Figure:
    """Grouped bar chart for comparing multiple metrics."""
    colors = colors or CHART_COLORS
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=df[x], y=df[col], name=col,
            marker_color=colors[i % len(colors)],
        ))
    fig.update_layout(title=title, barmode="group", height=420)
    return _apply_theme(fig)


def sales_profit_bars(df: pd.DataFrame, dim: str, title: str) -> go.Figure:
    """Side-by-side Sales & Profit bars."""
    agg = df.groupby(dim).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    agg = agg.sort_values("Sales", ascending=False)
    return grouped_bar(agg, dim, ["Sales", "Profit"], title,
                       [COLORS["primary"], COLORS["secondary"]])


# ═══════════════════════════════════════════════
#  TREEMAP
# ═══════════════════════════════════════════════
def sales_treemap(df: pd.DataFrame) -> go.Figure:
    """Hierarchical treemap: Region → Category → Sub-Category."""
    if df is None or len(df) == 0:
        return _empty_figure("Sales Treemap — no data")
    fig = px.treemap(
        df, path=["Region", "Category", "Sub-Category"],
        values="Sales", color="Profit",
        color_continuous_scale=["#EF4444", "#334155", "#22C55E"],
        color_continuous_midpoint=0,
        title="Sales Breakdown  (size = Sales, color = Profit)",
    )
    fig.update_layout(height=550)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  TREND LINES
# ═══════════════════════════════════════════════
def trend_line(monthly: pd.DataFrame, title: str = "Monthly Trend") -> go.Figure:
    """Dual-axis Sales & Profit trend line."""
    if monthly is None or len(monthly) == 0:
        return _empty_figure(f"{title} — no data")
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=monthly["Date"], y=monthly["Sales"],
        mode="lines+markers", name="Sales",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=5),
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=monthly["Date"], y=monthly["Profit"],
        mode="lines+markers", name="Profit",
        line=dict(color=COLORS["secondary"], width=2.5),
        marker=dict(size=5),
    ), secondary_y=True)

    fig.update_layout(title=title, height=420, hovermode="x unified")
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False, gridcolor="rgba(71,85,105,0.2)")
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True, gridcolor="rgba(71,85,105,0.2)")
    return _apply_theme(fig)


def forecast_chart(forecast_df: pd.DataFrame) -> go.Figure:
    """Actual + Forecast overlay."""
    actual   = forecast_df[forecast_df["Type"] == "Actual"]
    forecast = forecast_df[forecast_df["Type"] == "Forecast"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual["Date"], y=actual["Sales"],
        mode="lines+markers", name="Actual",
        line=dict(color=COLORS["primary"], width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=forecast["Date"], y=forecast["Sales"],
        mode="lines+markers", name="Forecast",
        line=dict(color=COLORS["accent"], width=2.5, dash="dash"),
        marker=dict(symbol="diamond", size=7),
    ))
    fig.update_layout(title="Sales Forecast (EMA-Based)", height=420, hovermode="x unified")
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  PIE / DONUT
# ═══════════════════════════════════════════════
def donut_chart(labels: list, values: list, title: str) -> go.Figure:
    """Donut chart."""
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=CHART_COLORS[:len(labels)]),
        textinfo="label+percent",
        textfont=dict(size=12),
    ))
    fig.update_layout(title=title, height=380, showlegend=True)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  SCATTER / BUBBLE
# ═══════════════════════════════════════════════
def scatter_sales_profit(df: pd.DataFrame, dim: str = "Sub-Category") -> go.Figure:
    """Scatter plot of Sales vs Profit per dimension."""
    if df is None or len(df) == 0:
        return _empty_figure(f"Sales vs Profit by {dim} — no data")
    agg = df.groupby(dim).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Avg_Discount=("Discount", "mean"),
    ).reset_index()

    fig = px.scatter(
        agg, x="Sales", y="Profit", size="Quantity",
        color="Avg_Discount", color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
        hover_name=dim, title=f"Sales vs Profit by {dim}  (size=Qty, color=Discount)",
        size_max=40,
    )
    # Add zero-profit line
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["danger"], opacity=0.5,
                  annotation_text="Break-even", annotation_font_color=COLORS["danger"])
    fig.update_layout(height=480)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  HEATMAP
# ═══════════════════════════════════════════════
def sales_heatmap(df: pd.DataFrame) -> go.Figure:
    """Month × Category sales heatmap."""
    pivot = df.pivot_table(index="Category", columns="Month", values="Sales", aggfunc="sum").fillna(0)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cols_in_data = [m for m in range(1, 13) if m in pivot.columns]
    col_labels = [months[m - 1] for m in cols_in_data]

    fig = go.Figure(go.Heatmap(
        z=pivot[cols_in_data].values,
        x=col_labels, y=pivot.index.tolist(),
        colorscale=[[0, "#1E293B"], [0.5, "#6366F1"], [1, "#C084FC"]],
        text=[[fmt_currency(v) for v in row] for row in pivot[cols_in_data].values],
        texttemplate="%{text}",
        textfont=dict(size=10),
        hovertemplate="Category: %{y}<br>Month: %{x}<br>Sales: %{text}<extra></extra>",
    ))
    fig.update_layout(title="Sales Heatmap — Month × Category", height=350)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  CORRELATION HEATMAP
# ═══════════════════════════════════════════════
def correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Correlation matrix heatmap."""
    if corr_matrix is None or corr_matrix.empty:
        return _empty_figure("Correlation Matrix — insufficient data")
    fig = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[[0, "#EF4444"], [0.5, "#1E293B"], [1, "#22C55E"]],
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate="%{text}",
        textfont=dict(size=13),
    ))
    fig.update_layout(title="Correlation Matrix", height=400)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  WATERFALL
# ═══════════════════════════════════════════════
def profit_waterfall(df: pd.DataFrame, dim: str = "Category") -> go.Figure:
    """Waterfall chart of profit contributions."""
    if df is None or len(df) == 0:
        return _empty_figure(f"Profit Waterfall by {dim} — no data")
    agg = df.groupby(dim)["Profit"].sum().sort_values(ascending=False).reset_index()

    fig = go.Figure(go.Waterfall(
        x=agg[dim], y=agg["Profit"],
        textposition="outside",
        text=[fmt_currency(v) for v in agg["Profit"]],
        connector=dict(line=dict(color=COLORS["border"])),
        increasing=dict(marker=dict(color=COLORS["success"])),
        decreasing=dict(marker=dict(color=COLORS["danger"])),
    ))
    fig.update_layout(title=f"Profit Waterfall by {dim}", height=420)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  PARETO (ABC)
# ═══════════════════════════════════════════════
def pareto_chart(abc_df: pd.DataFrame) -> go.Figure:
    """Pareto chart for ABC analysis."""
    if abc_df is None or len(abc_df) == 0:
        return _empty_figure("ABC Pareto — no data")
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    colors = [COLORS["success"] if c == "A" else (COLORS["accent"] if c == "B" else COLORS["danger"])
              for c in abc_df["Class"]]

    fig.add_trace(go.Bar(
        x=abc_df["Sub-Category"], y=abc_df["Sales"],
        name="Sales", marker_color=colors,
        text=[fmt_currency(v) for v in abc_df["Sales"]],
        textposition="auto", textfont=dict(size=10),
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=abc_df["Sub-Category"], y=abc_df["Cumulative Share %"],
        name="Cumulative %", mode="lines+markers",
        line=dict(color=COLORS["accent"], width=2.5),
        marker=dict(size=6),
    ), secondary_y=True)

    # Reference lines
    fig.add_hline(y=80, line_dash="dot", line_color=COLORS["success"], opacity=0.5,
                  annotation_text="80%", secondary_y=True)
    fig.add_hline(y=95, line_dash="dot", line_color=COLORS["accent"], opacity=0.5,
                  annotation_text="95%", secondary_y=True)

    fig.update_layout(title="ABC Product Classification (Pareto)", height=480)
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative %", secondary_y=True, range=[0, 105])
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  ANOMALY CHART
# ═══════════════════════════════════════════════
def anomaly_chart(anomaly_df: pd.DataFrame) -> go.Figure:
    """Time series with anomaly flags."""
    normal  = anomaly_df[~anomaly_df["Is Anomaly"]]
    anomaly = anomaly_df[anomaly_df["Is Anomaly"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=normal["Date"], y=normal["Sales"],
        mode="lines+markers", name="Normal",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=5),
    ))
    if len(anomaly) > 0:
        fig.add_trace(go.Scatter(
            x=anomaly["Date"], y=anomaly["Sales"],
            mode="markers", name="Anomaly",
            marker=dict(color=COLORS["danger"], size=14, symbol="x",
                        line=dict(width=2, color=COLORS["danger"])),
        ))

    # Mean ± threshold bands
    mean = anomaly_df["Sales"].mean()
    std  = anomaly_df["Sales"].std()
    from src.config import ANOMALY_Z_THRESHOLD as Z
    fig.add_hline(y=mean, line_dash="dash", line_color=COLORS["text_muted"], opacity=0.5,
                  annotation_text="Mean")
    fig.add_hrect(y0=mean - Z * std, y1=mean + Z * std,
                  fillcolor=COLORS["primary"], opacity=0.05,
                  line_width=0, annotation_text="Normal Band")

    fig.update_layout(title="Anomaly Detection — Monthly Sales", height=440, hovermode="x unified")
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  RFM SCATTER
# ═══════════════════════════════════════════════
def rfm_scatter(rfm_df: pd.DataFrame) -> go.Figure:
    """3D-style scatter of RFM segments."""
    fig = px.scatter(
        rfm_df, x="Recency", y="Monetary", size="Frequency",
        color="Segment Label", title="RFM Customer Segmentation",
        color_discrete_sequence=CHART_COLORS,
        hover_name="Customer Proxy",
        size_max=35,
    )
    fig.update_layout(height=500)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  COHORT HEATMAP
# ═══════════════════════════════════════════════
def cohort_heatmap(retention: pd.DataFrame) -> go.Figure:
    """Retention cohort heatmap."""
    fig = go.Figure(go.Heatmap(
        z=retention.values,
        x=[f"Month {c}" for c in retention.columns],
        y=[str(i) for i in retention.index],
        colorscale=[[0, "#1E293B"], [0.5, "#6366F1"], [1, "#22C55E"]],
        text=retention.round(0).values.astype(str),
        texttemplate="%{text}%",
        textfont=dict(size=10),
    ))
    fig.update_layout(title="Cohort Retention Heatmap (%)", height=400)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  DISCOUNT IMPACT
# ═══════════════════════════════════════════════
def discount_impact_chart(discount_df: pd.DataFrame) -> go.Figure:
    """Grouped bar of margin & avg profit by discount tier."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=discount_df["Discount Tier"].astype(str),
        y=discount_df["Total_Sales"],
        name="Total Sales",
        marker_color=COLORS["primary"],
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=discount_df["Discount Tier"].astype(str),
        y=discount_df["Margin %"],
        mode="lines+markers", name="Margin %",
        line=dict(color=COLORS["danger"], width=2.5),
        marker=dict(size=8),
    ), secondary_y=True)

    fig.update_layout(title="Discount Impact on Sales & Margin", height=420)
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig.update_yaxes(title_text="Margin %", secondary_y=True)
    return _apply_theme(fig)


# ═══════════════════════════════════════════════
#  YOY COMPARISON
# ═══════════════════════════════════════════════
def yoy_chart(yearly: pd.DataFrame) -> go.Figure:
    """Year-over-Year comparison bars."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yearly["Year"].astype(str), y=yearly["Sales"],
        name="Sales", marker_color=COLORS["primary"],
        text=[fmt_currency(v) for v in yearly["Sales"]],
        textposition="auto",
    ))
    fig.add_trace(go.Bar(
        x=yearly["Year"].astype(str), y=yearly["Profit"],
        name="Profit", marker_color=COLORS["secondary"],
        text=[fmt_currency(v) for v in yearly["Profit"]],
        textposition="auto",
    ))
    fig.update_layout(title="Year-over-Year Performance", barmode="group", height=400)
    return _apply_theme(fig)