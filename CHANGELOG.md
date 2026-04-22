# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0](https://github.com/ArinPattnaik/ecommerce-sales-analysis/compare/v0.1.0...v0.2.0) (2026-04-22)


### Features

* v2.0.0 — smart column mapper, CLV, churn, seasonality intelligence ([96a5dc3](https://github.com/ArinPattnaik/ecommerce-sales-analysis/commit/96a5dc31bbac87cde275d3044af59d19d2ae7873))

## [2.0.0](https://github.com/ArinPattnaik/ecommerce-sales-analysis/releases/tag/v2.0.0) (2026-04-23)

### 🛒 Smart Column Mapper — E-Commerce Auto-Detection
- **Fuzzy column name matching** — recognizes 100+ column name variations across Shopify, WooCommerce, Amazon, and custom e-commerce exports
- **Data pattern validation** — confirms matches by checking if data actually contains dates, monetary values, IDs, or categories
- **Two-pass scoring engine** — name similarity (70%) + data validation (30%) with greedy assignment to prevent double-mapping
- **Auto-detection on upload** — when enough e-commerce columns are found (≥4 roles), the platform offers the full deep-dive mode automatically
- **Profit estimation** — calculates `Sales - Cost` when cost data exists, or estimates at 15% default margin when neither profit nor cost is available
- **Discount normalization** — auto-converts percentage-style discounts (10, 20, 30) to decimal format (0.1, 0.2, 0.3)
- **Order ID generation** — creates unique IDs when the uploaded data doesn't have them
- **Customer ID inference** — uses real customer identifiers when available, falls back to intelligent proxies

### 🧠 Smart Insights Page — Advanced E-Commerce Intelligence
- **Customer Lifetime Value (CLV)** — per-customer total revenue, order count, lifetime days, avg order value, basket size, top 10% threshold
- **Repeat purchase rate** — percentage of customers who buy more than once, one-time buyer identification
- **Churn estimation** — classifies customers as Active / At Risk / Churned based on recency with visual donut chart
- **Order frequency distribution** — histogram showing how many customers placed 1, 2, 3+ orders
- **Basket size trends** — monthly average items per order and average order value over time
- **Day-of-week analysis** — sales performance Monday through Sunday with weekday vs weekend comparison
- **Monthly seasonality index** — identifies which months are above/below average (100 = baseline)
- **Peak period detection** — top N highest-revenue months with percentage above average
- **AI-generated recommendations** — actionable insights based on repeat rate, churn risk, basket size, and seasonality patterns

### 🔧 Quality & Reliability Improvements
- **Streamlit caching** — added `@st.cache_data` to KPI computation, data profiling, and insight generation for faster page loads
- **Error boundaries** — `safe_chart()` wrapper catches rendering errors and shows warnings instead of crashing the page
- **Pagination** — Data Explorer now paginates at 500 rows per page for large datasets
- **Empty data guards** — 8 chart functions now return themed placeholder figures instead of crashing on empty data
- **Input validation** — `discount_impact()` validates required columns, `rfm_analysis()` and `cohort_analysis()` handle null Segment/Region values
- **Deprecation fixes** — replaced `infer_datetime_format` with `format="mixed"`, replaced `use_container_width` with `width`
- **Config fix** — resolved CORS/XSRF compatibility warning in Streamlit config

### 📦 Infrastructure
- **Removed unused dependencies** — dropped `scikit-learn` and `statsmodels` from requirements
- **Version ceilings** — all dependencies now use `>=X.Y.Z,<X+1.0.0` to prevent breaking upgrades
- **`pyproject.toml`** — proper Python package configuration with pytest settings
- **`requirements-dev.txt`** — separate dev dependencies (pytest, pytest-cov)
- **Docker security** — Dockerfile now runs as non-root user (`appuser`)
- **`.dockerignore`** — excludes tests, notebooks, and dev files from production image
- **Duplicate constants removed** — dashboard now imports `CHART_COLORS` and `PLOTLY_LAYOUT` from `src/config` instead of redefining them

### 🧪 Testing — 21 → 148 Tests
- **`test_analysis.py`** — expanded to 34 tests: edge cases (single row, null segments, missing columns), cohort analysis, customer segmentation, product recommendations
- **`test_generic_analysis.py`** — 28 new tests: column type detection, auto-preprocessing, KPIs, distributions, correlations, time aggregation, outlier detection, insight generation
- **`test_visualization.py`** — 23 new tests: all chart functions return valid figures, empty data handling
- **`test_csv_accuracy.py`** — 17 new integration tests: verifies both pipelines produce numerically accurate results, cross-validates e-commerce and universal totals match
- **`test_smart_mapper.py`** — 22 new tests: fuzzy matching, validators, Shopify/WooCommerce/minimal CSV mapping, column renaming, profit estimation, discount normalization
- **`test_ecommerce_intelligence.py`** — 24 new tests: CLV, churn, basket trends, order frequency, day-of-week, seasonality, peak periods, smart insights

---

## [0.1.0](https://github.com/ArinPattnaik/ecommerce-sales-analysis/releases/tag/v0.1.0) (2026-04-08)

### Features
- Add dynamic data upload and column mapping ([82d1c3c](https://github.com/ArinPattnaik/ecommerce-sales-analysis/commit/82d1c3c2e92e2b92bb0b77ce7edd510cd741d678))
- Transform to industrial-grade analytics platform v2.0 ([0c932f2](https://github.com/ArinPattnaik/ecommerce-sales-analysis/commit/0c932f2dcab7410321682712782cde19a1199b58))
- Universal analytics — accepts ANY CSV/Excel file ([1a10f1b](https://github.com/ArinPattnaik/ecommerce-sales-analysis/commit/1a10f1bbb7d829b9c10c2dc0d5cb9ee6c3f6d1be))

### Bug Fixes
- Add app/__init__.py for Streamlit Cloud deployment ([5521494](https://github.com/ArinPattnaik/ecommerce-sales-analysis/commit/55214945eb3548f3a3751c05dab6d464e2ba1317))
