"""Central configuration for the E-Commerce Analytics Platform."""

# ──────────────────────────────────────────────
# Color Palette  (dark-theme first)
# ──────────────────────────────────────────────
COLORS = {
    "primary":      "#6366F1",   # Indigo-500
    "primary_light": "#818CF8",  # Indigo-400
    "secondary":    "#14B8A6",   # Teal-500
    "accent":       "#F59E0B",   # Amber-500
    "danger":       "#EF4444",   # Red-500
    "success":      "#22C55E",   # Green-500
    "warning":      "#F97316",   # Orange-500
    "info":         "#3B82F6",   # Blue-500
    "bg_dark":      "#0F172A",   # Slate-900
    "bg_card":      "#1E293B",   # Slate-800
    "bg_surface":   "#334155",   # Slate-700
    "text_primary": "#F8FAFC",   # Slate-50
    "text_muted":   "#94A3B8",   # Slate-400
    "border":       "#475569",   # Slate-600
}

# Plotly sequential / categorical palettes
CHART_COLORS = [
    "#6366F1", "#14B8A6", "#F59E0B", "#EF4444",
    "#3B82F6", "#EC4899", "#8B5CF6", "#22C55E",
    "#F97316", "#06B6D4",
]

GRADIENT_SALES   = ["#1E293B", "#6366F1"]
GRADIENT_PROFIT  = ["#1E293B", "#14B8A6"]
GRADIENT_DANGER  = ["#1E293B", "#EF4444"]

# ──────────────────────────────────────────────
# Business Rules
# ──────────────────────────────────────────────
ABC_THRESHOLDS = {"A": 0.80, "B": 0.95, "C": 1.00}

RFM_SEGMENTS = {
    "Champions":        {"r": (4, 5), "f": (4, 5), "m": (4, 5)},
    "Loyal":            {"r": (3, 5), "f": (3, 5), "m": (3, 5)},
    "Potential Loyal":  {"r": (3, 5), "f": (1, 3), "m": (1, 3)},
    "Recent":           {"r": (4, 5), "f": (1, 1), "m": (1, 1)},
    "Promising":        {"r": (3, 4), "f": (1, 1), "m": (1, 1)},
    "Needs Attention":  {"r": (2, 3), "f": (2, 3), "m": (2, 3)},
    "About to Sleep":   {"r": (2, 3), "f": (1, 2), "m": (1, 2)},
    "At Risk":          {"r": (1, 2), "f": (3, 5), "m": (3, 5)},
    "Hibernating":      {"r": (1, 2), "f": (1, 2), "m": (1, 2)},
    "Lost":             {"r": (1, 1), "f": (1, 1), "m": (1, 1)},
}

ANOMALY_Z_THRESHOLD = 2.5  # flag data points > 2.5 std from mean

# Discount tiers for ROI analysis
DISCOUNT_TIERS = [0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0]
DISCOUNT_LABELS = [
    "0-5%", "5-10%", "10-15%", "15-20%", "20-30%", "30-50%", "50%+"
]

# ──────────────────────────────────────────────
# Chart Layout Defaults (Plotly)
# ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text_primary"], size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_muted"], size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(71,85,105,0.3)",
        zerolinecolor="rgba(71,85,105,0.3)",
    ),
    yaxis=dict(
        gridcolor="rgba(71,85,105,0.3)",
        zerolinecolor="rgba(71,85,105,0.3)",
    ),
    hoverlabel=dict(
        bgcolor=COLORS["bg_card"],
        font_size=12,
        font_color=COLORS["text_primary"],
        bordercolor=COLORS["border"],
    ),
)

# ──────────────────────────────────────────────
# KPI Formatting
# ──────────────────────────────────────────────
def fmt_currency(v):
    """Format a number as currency with K/M suffixes."""
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:,.1f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:,.1f}K"
    return f"${v:,.0f}"


def fmt_pct(v):
    """Format a number as percentage."""
    return f"{v:+.1f}%" if v != 0 else "0.0%"


def fmt_number(v):
    """Format a number with commas."""
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:,.1f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:,.1f}K"
    return f"{v:,.0f}"
