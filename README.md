# E-Commerce Sales Analysis Dashboard

A comprehensive, production-ready analytics project for e-commerce sales data analysis. This project transforms raw sales data into actionable business insights through advanced analytics, interactive visualizations, and a professional dashboard.

## 🚀 Features

- **Comprehensive Data Analysis**: Sales trends, profitability analysis, customer segmentation
- **Interactive Dashboard**: Streamlit-based web application for real-time insights
- **Advanced Visualizations**: Matplotlib, Seaborn, and Plotly charts
- **Modular Codebase**: Well-structured Python package with reusable components
- **Statistical Analysis**: Correlation analysis, discount impact assessment
- **Time Series Analysis**: Monthly trends and forecasting capabilities
- **Production Ready**: Logging, error handling, and scalable architecture

## 📊 Key Insights

- Regional performance analysis with profit/loss identification
- Product category profitability rankings
- Monthly sales and profit trends
- Customer segment analysis
- Discount strategy optimization
- Correlation between sales drivers

## 🛠️ Tech Stack

- **Python 3.8+**
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Web Dashboard**: Streamlit
- **Analysis**: Scikit-learn, Statsmodels
- **Development**: Jupyter Notebook

## 📁 Project Structure

```
ecommerce-sales-analysis/
├── data/
│   ├── superstore_sales.csv          # Raw dataset
│   └── processed/                     # Processed data
├── src/                               # Source code
│   ├── __init__.py
│   ├── data_loader.py                 # Data loading utilities
│   ├── analysis.py                    # Analysis functions
│   └── visualization.py               # Visualization functions
├── notebooks/                         # Jupyter notebooks
│   └── sales_analysis.ipynb           # Main analysis notebook
├── app/                               # Streamlit application
│   └── dashboard.py                   # Dashboard app
├── tests/                             # Unit tests
├── docs/                              # Documentation
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ecommerce-sales-analysis.git
   cd ecommerce-sales-analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Run the Interactive Dashboard

```bash
streamlit run app/dashboard.py
```

Navigate to `http://localhost:8501` in your browser to access the dashboard.

#### Run the Analysis Notebook

```bash
jupyter notebook notebooks/sales_analysis.ipynb
```

#### Use as a Python Package

```python
from src.data_loader import load_data, preprocess_data
from src.analysis import key_metrics, sales_by_dimension
from src.visualization import create_interactive_dashboard

# Load and analyze data
df = load_data('data/superstore_sales.csv')
df = preprocess_data(df)
metrics = key_metrics(df)
print(metrics)
```

## 📈 Analysis Capabilities

### Sales Analysis
- Sales by region, category, and customer segment
- Top-performing products and categories
- Monthly and quarterly sales trends

### Profit Analysis
- Profit margins by product and region
- Impact of discounts on profitability
- Cost-benefit analysis of sales strategies

### Customer Insights
- Customer segmentation analysis
- Purchase behavior patterns
- Segment profitability

### Statistical Analysis
- Correlation analysis between variables
- Discount impact modeling
- Trend analysis and forecasting

## 🎯 Business Value

This project provides actionable insights for:

- **Sales Teams**: Identify high-performing regions and products
- **Marketing Teams**: Optimize discount strategies and customer targeting
- **Management**: Monitor KPIs and make data-driven decisions
- **Finance Teams**: Understand profitability patterns and margins

## 🔧 Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Quality

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Use type hints for better code documentation
- Write unit tests for new features

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📊 Sample Visualizations

The dashboard includes:

- Interactive sales and profit charts
- Regional performance maps
- Time series trend analysis
- Correlation heatmaps
- Customer segment analysis
- Product performance rankings

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Dataset: Superstore Sales Sample Data
- Built with modern Python data science stack
- Inspired by real-world e-commerce analytics needs

## 📞 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Transforming raw data into business intelligence, one insight at a time.**
