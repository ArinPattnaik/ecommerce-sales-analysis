# 📊 E-Commerce Sales Analytics Platform

> **Industrial-grade analytics dashboard** that transforms raw sales data into actionable business intelligence through advanced analytics, AI-powered insights, and interactive visualizations.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecommerce-sales-analysis-arin.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🔥 What This Platform Does

Unlike basic dashboards that just show charts, this platform **solves real e-commerce problems**:

| Problem | Solution | Business Impact |
|---------|----------|-----------------|
| "Which products should we discontinue?" | ABC Classification + Pareto Analysis | Focus inventory on 20% of products driving 80% revenue |
| "Are our discounts profitable?" | Discount ROI Analysis | Quantify margin destruction from heavy discounts |
| "Which customers are we losing?" | RFM Segmentation | Identify at-risk customers before they churn |
| "What happened last month?" | Anomaly Detection (Z-score) | Auto-flag unusual sales/profit patterns |
| "What will next quarter look like?" | EMA-based Forecasting | 6-month sales projections with trend analysis |
| "Where should we invest?" | AI-Powered Insights | Natural-language recommendations ranked by impact |

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
│   ├── dashboard.py          # 8-page Streamlit dashboard
│   └── theme.py              # Premium dark theme CSS
├── src/
│   ├── config.py             # Colors, palettes, business rules
│   ├── data_loader.py        # ETL pipeline with validation
│   ├── analysis.py           # Analytics engine (RFM, ABC, anomaly, forecast)
│   ├── insights.py           # AI-powered insight generator
│   └── visualization.py      # Plotly chart factory (20+ chart types)
├── data/
│   └── superstore_sales.csv  # 1,200 transactions (2021-2023)
├── tests/
│   └── test_analysis.py      # 21 automated tests
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
├── Dockerfile                # Production Docker image
├── requirements.txt          # Pinned dependencies
└── README.md
```

---

## 📊 Dashboard Pages (8 Total)

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

**Global Features**: Date range filter, multi-select region/category/segment, CSV download on every page.

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
