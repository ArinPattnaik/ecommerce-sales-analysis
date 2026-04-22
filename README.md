# 📊 Universal Analytics Platform

> **Upload any CSV or Excel file** — the platform auto-detects your columns, intelligently recognizes e-commerce data, builds interactive dashboards, and generates AI-powered insights instantly. Zero configuration needed.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecommerce-sales-analysis-arin.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-148%20passing-22C55E?logo=pytest&logoColor=white)](#-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🔥 What This Platform Does

This is a **two-mode analytics platform** that adapts to your data:

1. **Upload any CSV** → the Smart Column Mapper scans your columns and decides the best mode
2. **E-commerce data detected?** → unlocks a 9-page deep-dive with RFM, CLV, churn, seasonality, and more
3. **Generic data?** → builds a full 6-page analytical dashboard with distributions, correlations, and time analysis

No setup, no column configuration, no code. Just drag and drop.

---

## 🛒 Smart Column Mapper

The platform recognizes e-commerce data **regardless of column names**. Whether your export comes from Shopify, WooCommerce, Amazon, or a custom system, the mapper:

- **Fuzzy-matches** 100+ column name variations (`total_amount` → Sales, `created_at` → Order Date, `qty` → Quantity)
- **Validates with data patterns** — confirms a column actually contains dates, money, IDs, etc.
- **Estimates missing fields** — no Profit column? It calculates `Sales - Cost`, or estimates at 15% margin
- **Normalizes formats** — discounts as percentages (10, 20, 30) get auto-converted to decimals (0.1, 0.2, 0.3)
- **Generates Order IDs** if your data doesn't have them

When enough columns map (≥4 roles + Sales + Date), you get the full e-commerce deep-dive automatically.

---

## 📊 Dashboard Pages

### Universal Analytics (any file — 6 pages)

| Page | What It Does |
|------|-------------|
| **🏠 Overview** | Auto-generated KPIs, quick charts, AI insights |
| **📊 Distributions** | Histograms + box plots, categorical breakdowns |
| **🔗 Relationships** | Correlation heatmap, scatter explorer |
| **📈 Time Analysis** | Auto-detected date aggregation, trend lines |
| **🏷️ Group Analysis** | Cross-tabulate categories vs metrics |
| **🔎 Data Explorer** | Search, filter, paginated view, outlier detection, CSV export |

### E-Commerce Deep Dive (9 pages)

| Page | Key Features |
|------|-------------|
| **🏠 Executive Overview** | 8 KPI cards with ▲/▼ deltas, trend chart, segment donut, AI insights |
| **💰 Sales Deep Dive** | Interactive treemap, sales heatmap, dimensional P&L tables |
| **📈 Profitability** | Waterfall chart, scatter matrix, discount ROI, correlation heatmap |
| **👥 Customer Intelligence** | RFM segmentation, cohort retention heatmap, segment comparison |
| **� Product Analytics** | ABC Pareto chart, product performance matrix, top/bottom rankings |
| **📉 Trends & Forecast** | Monthly trends with MoM growth, EMA forecast, YoY comparison |
| **🗺️ Geographic Intelligence** | Regional P&L, market share donuts, cross-region benchmarking |
| **🚨 Anomalies & Alerts** | Z-score anomaly detection, auto-generated narratives |
| **🧠 Smart Insights** | CLV analysis, churn estimation, seasonality, basket trends, AI recommendations |

---

## 🧠 Smart Insights — New in v2.0

The **Smart Insights** page computes advanced e-commerce intelligence automatically:

### Customer Lifetime Value (CLV)
- Per-customer metrics: total revenue, order count, lifetime days, avg order value
- Repeat purchase rate and one-time buyer percentage
- Top 10% customer spend threshold

### Churn Estimation
- Classifies customers as **Active**, **At Risk**, or **Churned** based on recency
- Visual donut chart showing customer health distribution
- Actionable recommendations for win-back campaigns

### Seasonality & Date Intelligence
- **Day-of-week analysis** — sales by Monday through Sunday, weekday vs weekend comparison
- **Monthly seasonality index** — which months are above/below average (100 = baseline)
- **Peak period detection** — top revenue months with % above average
- **Weekday vs weekend** — avg order value comparison

### Basket & Order Analysis
- Average basket size (items per order) trends over time
- Average order value trends
- Order frequency distribution — how many customers placed 1, 2, 3+ orders

### AI Recommendations
- Flags low repeat rates with suggestions (loyalty programs, post-purchase emails)
- Identifies churn risk with win-back campaign recommendations
- Highlights basket size opportunities (cross-selling, bundles)
- Surfaces seasonality patterns for inventory and marketing planning

---

## 🏗️ Architecture

```
ecommerce-sales-analysis/
├── app/
│   ├── dashboard.py              # Two-mode dashboard (Universal + E-Commerce)
│   ├── theme.py                  # Premium dark theme + mobile responsive CSS
│   └── __init__.py
├── src/
│   ├── smart_mapper.py           # 🆕 Fuzzy column mapper for any e-commerce CSV
│   ├── ecommerce_intelligence.py # 🆕 CLV, churn, seasonality, basket analysis
│   ├── generic_analysis.py       # Universal analytics engine (any data)
│   ├── config.py                 # Colors, palettes, business rules, formatting
│   ├── data_loader.py            # ETL pipeline with validation & feature engineering
│   ├── analysis.py               # E-Commerce analytics (RFM, ABC, anomaly, forecast)
│   ├── insights.py               # AI-powered insight generator
│   ├── visualization.py          # Plotly chart factory (20+ chart types)
│   └── __init__.py
├── data/
│   └── superstore_sales.csv      # 1,200 transactions (sample e-commerce data)
├── tests/
│   ├── test_analysis.py          # Core analytics tests (34 tests)
│   ├── test_generic_analysis.py  # Universal engine tests (28 tests)
│   ├── test_visualization.py     # Chart rendering tests (23 tests)
│   ├── test_csv_accuracy.py      # Integration accuracy tests (17 tests)
│   ├── test_smart_mapper.py      # Column mapper tests (22 tests)
│   ├── test_ecommerce_intelligence.py  # Intelligence tests (24 tests)
│   └── __init__.py
├── .streamlit/
│   └── config.toml               # Streamlit theme configuration
├── Dockerfile                    # Production Docker image (non-root user)
├── pyproject.toml                # Package config & pytest settings
├── requirements.txt              # Production dependencies (pinned)
├── requirements-dev.txt          # Development dependencies
└── README.md
```

---

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/ArinPattnaik/ecommerce-sales-analysis.git
cd ecommerce-sales-analysis

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app/dashboard.py
```

Open **http://localhost:8501** in your browser. You'll see the upload screen — either drag in your own CSV or click "Use Sample E-Commerce Data" to explore the built-in dataset.

### Docker

```bash
docker build -t analytics-platform .
docker run -p 8501:8501 analytics-platform
```

The container runs as a non-root user with a health check endpoint at `/_stcore/health`.

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all 148 tests
python -m pytest tests/ -v
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Dashboard** | Streamlit 1.28+ with custom dark theme & mobile CSS |
| **Visualization** | Plotly (treemaps, waterfalls, heatmaps, scatter, donuts, sparklines) |
| **Analytics** | Pandas, NumPy |
| **Column Mapping** | Custom fuzzy matcher with data pattern validation |
| **AI Insights** | Rule-based insight engine with business heuristics |
| **Testing** | pytest (148 tests across 6 files) |
| **Deployment** | Streamlit Community Cloud / Docker |

---

## 📈 Analytics Capabilities

### Smart Column Mapper
Recognizes e-commerce data from Shopify, WooCommerce, Amazon, and custom exports. Maps columns like `total_amount`, `created_at`, `qty`, `product_name` to standard roles automatically.

### RFM Customer Segmentation
Classifies customers into actionable segments: Champions, Loyal, At Risk, Lost — enabling targeted marketing strategies. Uses real Customer IDs when available, falls back to intelligent proxies.

### Customer Lifetime Value
Computes per-customer CLV, repeat purchase rate, average order frequency, and basket size. Identifies your top 10% customers and flags one-time buyers.

### Churn Estimation
Recency-based classification into Active / At Risk / Churned with configurable lookback windows. Generates win-back campaign recommendations.

### ABC Product Classification
Pareto analysis categorizing products into A (top 80% revenue), B (next 15%), C (bottom 5%) for inventory optimization.

### Seasonality Detection
Identifies peak sales periods, day-of-week patterns, weekday vs weekend performance, and monthly seasonality indices.

### Anomaly Detection
Z-score based statistical detection flags unusual monthly patterns, with auto-generated narrative explanations.

### Discount ROI Analysis
Quantifies the true cost of discounting by tier, showing how margin erodes as discount depth increases.

### Forecasting
Exponential Moving Average (EMA) projections with trend extrapolation for 6-month forward planning.

### Profit Estimation
When profit data is missing, estimates from cost columns or applies configurable margin assumptions so profitability analytics still work.

---

## 🧪 Testing

The project has **148 automated tests** across 6 test files:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_analysis.py` | 34 | Core analytics, key metrics, RFM, ABC, anomaly, forecast |
| `test_generic_analysis.py` | 28 | Column detection, KPIs, correlations, time analysis, outliers |
| `test_visualization.py` | 23 | All chart functions, empty data handling |
| `test_csv_accuracy.py` | 17 | Integration tests, cross-pipeline validation |
| `test_smart_mapper.py` | 22 | Fuzzy matching, Shopify/WooCommerce/minimal mapping |
| `test_ecommerce_intelligence.py` | 24 | CLV, churn, basket trends, seasonality, insights |

```bash
python -m pytest tests/ -v
# ========================= 148 passed =========================
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Arin Pattnaik**

- GitHub: [@ArinPattnaik](https://github.com/ArinPattnaik)
- Website: [arinpattnaik.me](https://www.arinpattnaik.me)
- Email: arinpattnaikofficial@gmail.com

---

> ⚡ Transforming raw data into business intelligence, one insight at a time.
