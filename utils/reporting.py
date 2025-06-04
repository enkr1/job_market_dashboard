from __future__ import annotations

import pandas as pd

from utils.constants import OUTPUT_PATH_REPORT
from utils.functions import get_logger

logger = get_logger(__name__)


def log_quality_report(df: pd.DataFrame, output_path: str = OUTPUT_PATH_REPORT) -> None:
    """
    Generate and save a data-quality report to a CSV file.

    Parameters
    ----------
    df : pandas.DataFrame
        The **sanitised** DataFrame (after calling cleanup_and_analyse).
    output_path : str
        The file path to save the quality report CSV.
    """
    report = {}

    # Missing Value Report
    missing = df.isna().sum()
    report["missing_values"] = missing.to_dict()
    logger.info("--- Missing-Value Report ---")
    logger.info("\n%s", missing.to_frame("nulls").T)

    # Descriptive Stats for salary_min
    if "salary_min" in df.columns:
        salary_stats = df["salary_min"].describe()
        report["salary_min_stats"] = salary_stats.to_dict()
        logger.info("--- Descriptive Stats (salary_min) ---")
        logger.info("\n%s", salary_stats)

    # Date Range
    if "published_date_parsed" in df.columns:
        oldest = df["published_date_parsed"].min()
        newest = df["published_date_parsed"].max()
        report["date_range"] = {"oldest": str(oldest), "newest": str(newest)}
        logger.info("--- Date Range ---")
        logger.info("oldest=%s   newest=%s", oldest, newest)

    # Convert report dictionary to DataFrame for saving
    report_df = pd.json_normalize(report, sep="_")
    report_df.to_csv(output_path, index=False)
    logger.info("Quality report saved to %s", output_path)
