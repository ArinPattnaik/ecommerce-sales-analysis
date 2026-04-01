"""Data loading and preprocessing utilities."""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(data_path: str) -> pd.DataFrame:
    """Load the superstore sales data from CSV file.

    Args:
        data_path: Path to the CSV file.

    Returns:
        DataFrame containing the sales data.
    """
    try:
        df = pd.read_csv(data_path)
        logger.info(f"Loaded data with shape: {df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {data_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess the sales data.

    Args:
        df: Raw DataFrame.

    Returns:
        Preprocessed DataFrame.
    """
    df = df.copy()

    # Convert Order Date to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

    # Extract date features
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Quarter'] = df['Order Date'].dt.quarter
    df['Day of Week'] = df['Order Date'].dt.day_name()

    # Handle missing values
    df = df.dropna(subset=['Order Date'])

    # Ensure numeric columns are float
    numeric_cols = ['Sales', 'Profit', 'Discount', 'Quantity']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    logger.info(f"Preprocessed data shape: {df.shape}")
    return df

def save_processed_data(df: pd.DataFrame, output_path: str):
    """Save processed data to CSV.

    Args:
        df: DataFrame to save.
        output_path: Path to save the file.
    """
    df.to_csv(output_path, index=False)
    logger.info(f"Saved processed data to {output_path}")