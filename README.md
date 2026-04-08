# 📊 Universal Analytics Platform

> **Upload any CSV or Excel file** — the platform auto-detects your columns, builds interactive dashboards, and generates AI-powered insights instantly. No configuration needed.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecommerce-sales-analysis-arin.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🔥 What This Platform Does

### Universal Mode — Works With ANY Data
Upload **any CSV or Excel file** (sales, sports, HR, finance, IoT — anything) and the platform will:

| Capability | How It Works |
|-----------|-------------|
| **Auto-Detection** | Classifies every column as numeric, categorical, datetime, or ID — zero configuration |
| **Smart KPIs** | Generates sum, mean, median, min/max stats for every numeric column |
| **Distribution Analysis** | Histograms with box plots for numerics, value counts + pie charts for categoricals |
| **Correlation Matrix** | Heatmap + top-N strongest correlations with strength indicators |
| **Time Analysis** | Auto-detects date columns and aggregates metrics by day/month/year |
| **Group Analysis** | Cross-tabulate any categorical dimension against any numeric metric |
| **Outlier Detection** | Z-score based outlier flagging on any numeric field |
| **Data Explorer** | Full-text search, column filter, CSV export |

### E-Commerce Deep Dive — Built-In Sample Data
Includes a specialized 8-page dashboard with advanced e-commerce analytics:

| Problem | Solution | Business Impact |
|---------|----------|-----------------|
| "Which products to discontinue?" | ABC Classification + Pareto | Focus on 20% of products driving 80% revenue |
| "Are discounts profitable?" | Discount ROI Analysis | Quantify margin destruction by tier |
| "Which customers are we losing?" | RFM Segmentation | Identify at-risk customers before churn |
| "What happened last month?" | Anomaly Detection (Z-score) | Auto-flag unusual patterns |
| "What will next quarter look like?" | EMA Forecasting | 6-month sales projections |

---

## 📸 Dashboard Preview

### Executive Overview
KPI cards with period-over-period trends, revenue & profit timelines, and AI-generated insights.

### Product Analytics
ABC classification with Pareto chart — instantly see which products drive your business.

### Anomaly Detection  
Statistical Z-score anomaly detection with auto-generated narrative explanations.

---

## 🚀 Live Demo

**[Launch Dashboard →](https://ecommerce-sales-analysis-arin.streamlit.app/)**

---

## 🏗️ Architecture

```
ecommerce-sales-analysis/
├── app/
│   ├── dashboard.py          # Two-mode dashboard (Universal + E-Commerce)
│   ├── theme.py              # Premium dark theme + mobile responsive CSS
│   └── __init__.py
├── src/
│   ├── generic_analysis.py   # 🆕 Universal analytics engine (any data)
│   ├── config.py             # Colors, palettes, business rules
│   ├── data_loader.py        # ETL pipeline with validation
│   ├── analysis.py           # E-Commerce analytics (RFM, ABC, anomaly, forecast)
│   ├── insights.py           # AI-powered insight generator
│   └── visualization.py      # Plotly chart factory (20+ chart types)
├── data/
│   └── superstore_sales.csv  # 1,200 transactions (sample e-commerce data)
├── tests/
│   └── test_analysis.py      # 21 automated tests
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── Dockerfile                # Production Docker image
├── requirements.txt          # Pinned dependencies
└── README.md
```

---

## 📊 Dashboard Pages

### Universal Analytics (any uploaded file, up to 6 pages)

| Page | Key Features |
|------|-------------|
| **🏠 Overview** | Auto-generated KPIs for all numeric columns, quick charts, AI insights |
| **📊 Distributions** | Histograms with box plots, categorical value counts, descriptive stats |
| **🔗 Relationships** | Correlation heatmap, top-N correlations, interactive scatter explorer |
| **📈 Time Analysis** | Auto-detected date aggregation, multi-metric trend lines |
| **🏷️ Group Analysis** | Cross-tabulate categories vs metrics, grouped bar comparisons |
| **🔎 Data Explorer** | Full-text search, column selector, outlier detection, CSV export |

### E-Commerce Deep Dive (sample data, 8 pages)

| Page | Key Features |
|------|-------------|
| **🏠 Executive Overview** | 8 KPI cards with ▲/▼ deltas, trend chart, segment donut, AI insights |
| **💰 Sales Deep Dive** | Interactive treemap, sales heatmap, dimensional P&L tables |
| **📈 Profitability** | Waterfall chart, scatter matrix, discount ROI, correlation heatmap |
| **👥 Customer Intelligence** | RFM segmentation, cohort retention heatmap, segment comparison |
| **📦 Product Analytics** | ABC Pareto chart, product performance matrix, top/bottom rankings |
| **📉 Trends & Forecast** | Monthly trends with MoM growth, EMA forecast, YoY comparison |
| **🗺️ Geographic Intelligence** | Regional P&L, market share donuts, cross-region benchmarking |
| **🚨 Anomalies & Alerts** | Z-score anomaly detection, auto-generated narratives, flagged data |

**Global Features**: Back button, mobile responsive, CSV download on every page.

---

## 🛠️ Tech Stack

- **Dashboard**: Streamlit 1.28+ with custom dark theme
- **Visualization**: Plotly (treemaps, waterfalls, heatmaps, scatter, gauges)
- **Analytics**: Pandas, NumPy, scikit-learn
- **AI Insights**: Custom NLP-style insight engine
- **Deployment**: Streamlit Community Cloud / Docker

---

## 🚀 Quick Start

### Local Development

```bash
# Clone
git clone https://github.com/ArinPattnaik/ecommerce-sales-analysis.git
cd ecommerce-sales-analysis

# Install
pip install -r requirements.txt

# Run
streamlit run app/dashboard.py
```

Open `http://localhost:8501` in your browser.

### Docker

```bash
docker build -t ecommerce-analytics .
docker run -p 8501:8501 ecommerce-analytics
```

### Run Tests

```bash
python -m pytest tests/ -v
```

---

## 📈 Analytics Capabilities

### RFM Customer Segmentation
Classifies customers into actionable segments: Champions, Loyal, At Risk, Lost — enabling targeted marketing strategies.

### ABC Product Classification
Pareto analysis categorizing products into A (top 80% revenue), B (next 15%), C (bottom 5%) for inventory optimization.

### Anomaly Detection
Z-score based statistical detection flags unusual monthly patterns, with auto-generated narrative explanations.

### Discount ROI Analysis
Quantifies the true cost of discounting by tier, showing how margin erodes as discount depth increases.

### Forecasting
Exponential Moving Average (EMA) projections with trend extrapolation for 6-month forward planning.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Arin Pattnaik** — [GitHub](https://github.com/ArinPattnaik) · [Website](https://www.arinpattnaik.me)

---

> ⚡ Transforming raw data into business intelligence, one insight at a time.
