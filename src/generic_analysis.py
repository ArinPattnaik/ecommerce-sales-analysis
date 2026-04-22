"""
Universal Analytics Engine — works with ANY tabular dataset.

Auto-detects column types and generates:
  - KPIs for every numeric column
  - Distribution summaries
  - Correlation matrices
  - Time-series trends (if dates detected)
  - Auto-generated text insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
#  COLUMN TYPE DETECTION
# ═══════════════════════════════════════════════
def detect_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Classify every column into numeric, categorical, datetime, or id.

    Returns dict with keys: 'numeric', 'categorical', 'datetime', 'id', 'boolean'.
    """
    result = {"numeric": [], "categorical": [], "datetime": [], "id": [], "boolean": []}

    for col in df.columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            result["datetime"].append(col)
            continue

        # Try parsing as dates
        if series.dtype == object:
            try:
                parsed = pd.to_datetime(series, format="mixed", errors="coerce")
                valid_ratio = parsed.notna().sum() / len(series)
                if valid_ratio > 0.7:
                    result["datetime"].append(col)
                    continue
            except Exception:
                pass

        # Boolean
        if series.dtype == bool or (set(series.unique()) <= {0, 1, True, False, "True", "False", "Yes", "No"}):
            result["boolean"].append(col)
            continue

        # Numeric
        if pd.api.types.is_numeric_dtype(series):
            nunique = series.nunique()
            # If every value is unique AND integer-like, probably an ID
            if nunique == len(series) and nunique > 20 and pd.api.types.is_integer_dtype(series):
                result["id"].append(col)
            else:
                result["numeric"].append(col)
            continue

        # Try coercing to numeric
        coerced = pd.to_numeric(series, errors="coerce")
        valid_ratio = coerced.notna().sum() / len(series)
        if valid_ratio > 0.7:
            result["numeric"].append(col)
            continue

        # Categorical (string-like)
        nunique = series.nunique()
        if nunique == len(df) and nunique > 50:
            result["id"].append(col)
        else:
            result["categorical"].append(col)

    return result


# ═══════════════════════════════════════════════
#  AUTO-PREPROCESS
# ═══════════════════════════════════════════════
def auto_preprocess(df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
    """Coerce detected types so analytics work smoothly."""
    df = df.copy()

    for col in col_types["datetime"]:
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in col_types["numeric"]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ═══════════════════════════════════════════════
#  DATA PROFILE
# ═══════════════════════════════════════════════
def data_profile(df: pd.DataFrame) -> Dict:
    """Generate a high-level data profile."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_total": int(df.isnull().sum().sum()),
        "missing_pct": round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 1),
        "duplicated_rows": int(df.duplicated().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
    }


# ═══════════════════════════════════════════════
#  KPIs FOR NUMERIC COLUMNS
# ═══════════════════════════════════════════════
def compute_kpis(df: pd.DataFrame, numeric_cols: List[str]) -> List[Dict]:
    """Generate KPI cards for each numeric column."""
    if not numeric_cols:
        return []
    kpis = []
    for col in numeric_cols[:12]:  # Cap at 12 KPIs
        series = df[col].dropna()
        if len(series) == 0:
            continue
        kpis.append({
            "label": col,
            "sum": round(float(series.sum()), 2),
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "std": round(float(series.std()), 2),
            "count": int(series.count()),
            "zeros": int((series == 0).sum()),
            "nulls": int(df[col].isnull().sum()),
        })
    return kpis


# ═══════════════════════════════════════════════
#  DISTRIBUTIONS
# ═══════════════════════════════════════════════
def compute_numeric_distribution(df: pd.DataFrame, col: str, bins: int = 30) -> Dict:
    """Histogram data for a numeric column."""
    series = df[col].dropna()
    if len(series) == 0:
        return {"col": col, "values": [], "bin_edges": []}

    counts, bin_edges = np.histogram(series, bins=min(bins, len(series.unique())))
    return {
        "col": col,
        "values": counts.tolist(),
        "bin_edges": [round(float(e), 4) for e in bin_edges],
    }


def compute_categorical_distribution(df: pd.DataFrame, col: str, top_n: int = 15) -> pd.DataFrame:
    """Value counts for a categorical column."""
    counts = df[col].value_counts().head(top_n).reset_index()
    counts.columns = [col, "Count"]
    return counts


# ═══════════════════════════════════════════════
#  CORRELATIONS
# ═══════════════════════════════════════════════
def compute_correlations(df: pd.DataFrame, numeric_cols: List[str]) -> pd.DataFrame:
    """Correlation matrix for numeric columns.

    Returns empty DataFrame if fewer than 2 valid numeric columns.
    """
    cols = [c for c in numeric_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if len(cols) < 2:
        return pd.DataFrame()
    return df[cols].corr().round(3)


def find_top_correlations(corr_matrix: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Find the top N strongest correlations (excluding self-correlation)."""
    if corr_matrix.empty:
        return []

    pairs = []
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append({
                "col_a": cols[i],
                "col_b": cols[j],
                "correlation": float(corr_matrix.iloc[i, j]),
            })

    pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return pairs[:n]


# ═══════════════════════════════════════════════
#  TIME-SERIES ANALYSIS
# ═══════════════════════════════════════════════
def compute_time_trends(
    df: pd.DataFrame, date_col: str, numeric_cols: List[str], freq: str = "auto"
) -> pd.DataFrame:
    """Aggregate numeric columns over time."""
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    df = df.dropna(subset=[date_col])
    if len(df) == 0:
        return pd.DataFrame()

    # Auto-detect best frequency
    if freq == "auto":
        date_range = (df[date_col].max() - df[date_col].min()).days
        if date_range <= 2:
            freq = "h"  # hourly
        elif date_range <= 90:
            freq = "D"  # daily
        elif date_range <= 730:
            freq = "MS"  # monthly
        else:
            freq = "YS"  # yearly

    # Only use cols that actually exist and are numeric
    valid_cols = [c for c in numeric_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not valid_cols:
        return pd.DataFrame()

    df = df.set_index(date_col)
    resampled = df[valid_cols].resample(freq).agg(["sum", "mean", "count"])
    resampled.columns = [f"{c[0]}_{c[1]}" for c in resampled.columns]
    resampled = resampled.reset_index()
    resampled = resampled.rename(columns={date_col: "Date"})

    return resampled


def compute_time_aggregates(
    df: pd.DataFrame, date_col: str, numeric_cols: List[str]
) -> pd.DataFrame:
    """Simple time aggregation — just sums by auto-detected period."""
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    if len(df) == 0:
        return pd.DataFrame()

    date_range = (df[date_col].max() - df[date_col].min()).days

    if date_range <= 90:
        df["_period"] = df[date_col].dt.date
        period_label = "Day"
    elif date_range <= 1500:
        df["_period"] = df[date_col].dt.to_period("M").astype(str)
        period_label = "Month"
    else:
        df["_period"] = df[date_col].dt.year
        period_label = "Year"

    valid_cols = [c for c in numeric_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not valid_cols:
        return pd.DataFrame()

    agg_dict = {c: "sum" for c in valid_cols}
    agg_dict["_count"] = (date_col, "count")

    result = df.groupby("_period").agg(**{c: (c, "sum") for c in valid_cols}).reset_index()
    result = result.rename(columns={"_period": period_label})

    # Add row count
    counts = df.groupby("_period").size().reset_index(name="Records")
    result = result.merge(counts, left_on=period_label, right_on="_period", how="left")
    if "_period" in result.columns:
        result = result.drop(columns=["_period"])

    return result


# ═══════════════════════════════════════════════
#  GROUP-BY ANALYSIS
# ═══════════════════════════════════════════════
def compute_group_summary(
    df: pd.DataFrame, group_col: str, numeric_cols: List[str], top_n: int = 20
) -> pd.DataFrame:
    """Aggregate numeric columns by a categorical dimension."""
    valid_cols = [c for c in numeric_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if not valid_cols:
        return pd.DataFrame()

    agg = df.groupby(group_col)[valid_cols].agg(["sum", "mean", "count"]).reset_index()
    agg.columns = [group_col] + [f"{c[0]}_{c[1]}" for c in agg.columns[1:]]

    # Sort by the sum of the first numeric column
    first_sum_col = f"{valid_cols[0]}_sum"
    if first_sum_col in agg.columns:
        agg = agg.sort_values(first_sum_col, ascending=False)

    return agg.head(top_n).round(2)


# ═══════════════════════════════════════════════
#  OUTLIER DETECTION
# ═══════════════════════════════════════════════
def detect_outliers(df: pd.DataFrame, col: str, z_threshold: float = 2.5) -> pd.DataFrame:
    """Flag outliers using Z-score method."""
    series = df[col].dropna()
    if len(series) < 5:
        return pd.DataFrame()

    mean = series.mean()
    std = series.std()
    if std == 0:
        return pd.DataFrame()

    z_scores = (series - mean) / std
    outlier_mask = z_scores.abs() > z_threshold

    result = df.loc[outlier_mask].copy()
    result["_z_score"] = z_scores[outlier_mask].round(2)
    result["_outlier_type"] = result["_z_score"].apply(
        lambda z: "High" if z > 0 else "Low"
    )
    return result


# ═══════════════════════════════════════════════
#  AUTO-GENERATED INSIGHTS
# ═══════════════════════════════════════════════
def generate_generic_insights(
    df: pd.DataFrame, col_types: Dict[str, List[str]]
) -> List[str]:
    """Generate natural-language insights about the dataset."""
    insights = []
    profile = data_profile(df)

    insights.append(
        f"📊 **Dataset Overview**: {profile['rows']:,} rows × {profile['columns']} columns. "
        f"Memory usage: {profile['memory_mb']:.1f} MB."
    )

    if profile["missing_pct"] > 0:
        insights.append(
            f"⚠️ **Data Quality**: {profile['missing_pct']:.1f}% of values are missing "
            f"({profile['missing_total']:,} total null values)."
        )

    if profile["duplicated_rows"] > 0:
        insights.append(
            f"🔁 **Duplicates**: Found {profile['duplicated_rows']:,} duplicate rows "
            f"({profile['duplicated_rows']/profile['rows']*100:.1f}% of data)."
        )

    # Numeric insights
    for col in col_types["numeric"][:5]:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        mean_val = series.mean()
        std_val = series.std()
        if std_val > 0:
            cv = (std_val / abs(mean_val)) * 100 if mean_val != 0 else 0
            if cv > 100:
                insights.append(
                    f"📈 **{col}** is highly variable (CV={cv:.0f}%). "
                    f"Range: {series.min():,.2f} → {series.max():,.2f}."
                )
            elif series.skew() > 1.5:
                insights.append(
                    f"📐 **{col}** is right-skewed (skewness={series.skew():.1f}). "
                    f"Mean ({mean_val:,.2f}) is significantly higher than median ({series.median():,.2f})."
                )

    # Categorical insights
    for col in col_types["categorical"][:3]:
        nunique = df[col].nunique()
        top_val = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "N/A"
        top_pct = (df[col] == top_val).sum() / len(df) * 100
        insights.append(
            f"🏷️ **{col}** has {nunique} unique values. "
            f"Most common: \"{top_val}\" ({top_pct:.1f}% of records)."
        )

    # Correlation insights
    if len(col_types["numeric"]) >= 2:
        corr = compute_correlations(df, col_types["numeric"])
        top_corrs = find_top_correlations(corr, 2)
        for tc in top_corrs:
            strength = "strongly" if abs(tc["correlation"]) > 0.7 else "moderately"
            direction = "positively" if tc["correlation"] > 0 else "negatively"
            insights.append(
                f"🔗 **{tc['col_a']}** and **{tc['col_b']}** are {strength} {direction} "
                f"correlated (r={tc['correlation']:.2f})."
            )

    return insights
