"""
Premium Dark Theme for Streamlit Dashboard.

Injects custom CSS to create a sleek, industry-grade look.
Includes mobile-responsive breakpoints and a persistent back/reset button.
"""

import streamlit as st

CUSTOM_CSS = """
<style>
/* ─── Google Font ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ─── Root ─── */
:root {
    --bg-primary:   #0F172A;
    --bg-card:      #1E293B;
    --bg-surface:   #334155;
    --text-primary: #F8FAFC;
    --text-muted:   #94A3B8;
    --border:       #475569;
    --accent:       #6366F1;
    --accent-glow:  rgba(99,102,241,0.25);
    --success:      #22C55E;
    --danger:       #EF4444;
    --warning:      #F59E0B;
    --info:         #3B82F6;
}

/* ─── Global ─── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

[data-testid="stSidebar"] {
    background-color: #0B1120 !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .stRadio > label {
    color: var(--text-muted) !important;
    font-weight: 500;
}

/* ─── Headers ─── */
h1, h2, h3, h4 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}
h1 { font-size: 2rem !important; }

/* ─── KPI Cards ─── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, var(--bg-card) 0%, rgba(99,102,241,0.08) 100%) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px var(--accent-glow);
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] > div {
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}

/* ─── Data Frames ─── */
[data-testid="stDataFrame"], .stDataFrame {
    border-radius: 10px !important;
    overflow: hidden;
}
.stDataFrame table {
    background-color: var(--bg-card) !important;
}
.stDataFrame th {
    background-color: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em;
}
.stDataFrame td {
    color: var(--text-primary) !important;
    border-color: rgba(71,85,105,0.3) !important;
}

/* ─── Expander ─── */
[data-testid="stExpander"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: var(--bg-card);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--text-muted);
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background-color: var(--accent) !important;
    color: white !important;
    font-weight: 600;
}

/* ─── Buttons ─── */
.stDownloadButton button, .stButton button {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
    transition: all 0.2s;
}
.stDownloadButton button:hover, .stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px var(--accent-glow);
}

/* ─── Sidebar Radio ─── */
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 10px 14px !important;
    border-radius: 8px !important;
    margin-bottom: 4px !important;
    transition: background 0.2s;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background-color: rgba(99,102,241,0.1) !important;
}
[data-testid="stSidebar"] [role="radiogroup"] [data-checked="true"] {
    background-color: rgba(99,102,241,0.15) !important;
}

/* ─── Multiselect / Select ─── */
[data-testid="stMultiSelect"], .stSelectbox {
    border-radius: 8px;
}

/* ─── Dividers ─── */
hr {
    border-color: var(--border) !important;
    opacity: 0.4;
}

/* ─── Plotly Charts Container ─── */
.js-plotly-plot .plotly .modebar {
    right: 8px !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ─── Insight Cards ─── */
.insight-card {
    background: var(--bg-card);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ─── Footer ─── */
.footer-text {
    color: var(--text-muted);
    font-size: 0.75rem;
    text-align: center;
    padding: 20px 0 10px 0;
    border-top: 1px solid rgba(71,85,105,0.3);
    margin-top: 40px;
}

/* ─── Mobile Header Bar ─── */
.mobile-header {
    display: none;
}

/* ─── File Info Badge ─── */
.file-badge {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    margin-bottom: 12px;
    font-size: 0.8rem;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 8px;
}
.file-badge strong {
    color: var(--text-primary);
}

/* ─── Upload Area ─── */
[data-testid="stFileUploader"] {
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg-card) !important;
}

/* ─── Hide Streamlit branding ─── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ═══════════════════════════════════════════
   MOBILE RESPONSIVE (< 768px)
   ═══════════════════════════════════════════ */
@media (max-width: 768px) {
    /* Show mobile header */
    .mobile-header {
        display: flex !important;
        position: sticky;
        top: 0;
        z-index: 999;
        background: #0B1120;
        padding: 10px 16px;
        border-bottom: 1px solid var(--border);
        align-items: center;
        justify-content: space-between;
        gap: 8px;
    }
    .mobile-header h3 {
        margin: 0 !important;
        font-size: 1rem !important;
    }

    /* Smaller headings */
    h1 { font-size: 1.4rem !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1rem !important; }

    /* KPIs — make 2 per row */
    [data-testid="stMetric"] {
        padding: 12px 14px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.65rem !important;
    }

    /* Charts height */
    .js-plotly-plot {
        max-height: 300px;
    }

    /* Better column stacking */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Tabs on mobile */
    .stTabs [data-baseweb="tab"] {
        padding: 6px 10px;
        font-size: 0.8rem;
    }
}

/* ═══════════════════════════════════════════
   SMALL MOBILE (< 480px)
   ═══════════════════════════════════════════ */
@media (max-width: 480px) {
    h1 { font-size: 1.2rem !important; }
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }
}
</style>
"""


def inject_theme():
    """Inject the custom CSS theme into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_insight_card(text: str):
    """Render a styled insight card."""
    st.markdown(f'<div class="insight-card">{text}</div>', unsafe_allow_html=True)


def render_footer():
    """Render a styled footer."""
    st.markdown(
        '<div class="footer-text">'
        '⚡ Universal Analytics Platform &nbsp;·&nbsp; '
        'Built with Streamlit & Plotly &nbsp;·&nbsp; '
        'Upload any CSV or Excel file'
        '</div>',
        unsafe_allow_html=True,
    )


def render_file_badge(filename: str, rows: int, cols: int):
    """Render a file info badge showing the loaded dataset."""
    st.markdown(
        f'<div class="file-badge">'
        f'📄 <strong>{filename}</strong> &nbsp;·&nbsp; {rows:,} rows × {cols} columns'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, subtitle: str = ""):
    """Render a section header with optional subtitle."""
    st.markdown(f"## {icon} {title}")
    if subtitle:
        st.caption(subtitle)
