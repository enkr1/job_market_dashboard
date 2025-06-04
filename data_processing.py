#!/usr/bin/env python3

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from utils.constants import (
    OUTPUT_PATH_CHART_JOBS_PER_DAY,
    OUTPUT_PATH_CHART_SALARY,
    OUTPUT_PATH_CHART_TOP_COMPANIES,
    OUTPUT_PATH_SANITISED,
)
from utils.functions import get_csv_path, get_logger
from utils.reporting import log_quality_report

logger = get_logger(__name__)


def extract_salaries(compensation):
    """
    Extract min and max salary from compensation string, e.g. 'SGD 4,000 – 8,000 with equity'
    Returns (min_salary, max_salary) as ints or (None, None) if not found.
    """
    if not isinstance(compensation, str):
        return None, None
    match = re.search(r"SGD\s*([\d,]+)\s*[–-]\s*([\d,]+)", compensation)
    if match:
        min_salary = int(match.group(1).replace(",", ""))
        max_salary = int(match.group(2).replace(",", ""))
        return min_salary, max_salary
    return None, None


def cleanup_and_analyse(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw Tech-in-Asia job listings and write artefacts.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw dataset as produced by `selenium_scraper.py`.

    Returns
    -------
    pandas.DataFrame
        Sanitised subset (columns listed in `sanitised_cols`).
    """

    logger.info("Starting data cleanup and analysis.")

    # 1. Extract salary_min and salary_max from 'compensation'
    if "compensation" in df.columns:
        df[["salary_min", "salary_max"]] = df["compensation"].apply(
            lambda x: pd.Series(extract_salaries(x))
        )

    # 2. Create company_name for consistency
    if "company" in df.columns:
        df["company_name"] = df["company"]

    # 3. Drop duplicates by 'id' (the job's unique identifier)
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"])

    # 3b. Parse the published_date into an actual datetime for downstream analysis
    if "published_date" in df.columns:
        df["published_date_parsed"] = pd.to_datetime(
            df["published_date"], errors="coerce"
        )

    # 4. Clean company_name column
    df["company_name"] = df["company_name"].astype(str).str.strip().str.lower()

    # 5. Convert salary_min to numeric
    df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")

    logger.info("Data cleaning completed.")

    # -----------------------------------------------------------------
    # Persist the broad sanitised CSV (keep rows even when salary/company are NaN)
    # -----------------------------------------------------------------
    Path(OUTPUT_PATH_SANITISED).parent.mkdir(parents=True, exist_ok=True)

    sanitised_cols = [
        "id",
        "title",
        "company_name",
        "location",
        "link",
        "image_url",
        "salary_min",
        "salary_max",
        "published_date_parsed",
        "metadata",
    ]
    df[sanitised_cols].to_csv(OUTPUT_PATH_SANITISED, index=False)
    logger.info(f"Saved sanitised dataset → {OUTPUT_PATH_SANITISED}")

    # NEW: quick quality snapshot
    log_quality_report(df[sanitised_cols])

    # -----------------------------------------------------------------
    # 1) Salary histogram – only rows with salary_min
    # -----------------------------------------------------------------
    salary_df = df.dropna(subset=["salary_min"])
    if not salary_df.empty:
        plt.figure(figsize=(10, 6))
        sns.histplot(salary_df["salary_min"], bins=20, kde=True)
        plt.title("Salary Distribution (posts w/ salary only)")
        plt.xlabel("Minimum Salary (SGD)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(OUTPUT_PATH_CHART_SALARY)
        plt.close()
        logger.info("Saved salary histogram.")
    else:
        logger.warning("No rows with salary_min; salary histogram skipped.")

    # -----------------------------------------------------------------
    # 2) Top‑companies bar chart – need company_name
    # -----------------------------------------------------------------
    company_df = df.dropna(subset=["company_name"])
    if not company_df.empty:
        top_companies = company_df["company_name"].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_companies.values, y=top_companies.index)
        plt.title("Top 10 Companies by Job Postings")
        plt.xlabel("# Postings")
        plt.ylabel("Company")
        plt.tight_layout()
        plt.savefig(OUTPUT_PATH_CHART_TOP_COMPANIES)
        plt.close()
        logger.info("Saved top companies bar chart.")
    else:
        logger.warning("No company_name values; top‑companies chart skipped.")

    # -----------------------------------------------------------------
    # 3) Jobs‑per‑day line chart – need published_date_parsed
    # -----------------------------------------------------------------
    date_df = df.dropna(subset=["published_date_parsed"])
    daily_counts = (
        date_df.set_index("published_date_parsed")
        .resample("D")
        .size()
        .rename("num_jobs")
        .reset_index()
    )

    if not daily_counts.empty:
        end_date = daily_counts["published_date_parsed"].max()
        start_date = end_date - pd.Timedelta(days=30)
        plot_series = daily_counts[daily_counts["published_date_parsed"] >= start_date]
        plt.figure(figsize=(12, 4))
        plt.plot(
            plot_series["published_date_parsed"],
            plot_series["num_jobs"],
            marker="o",
            linestyle="-",
        )
        plt.title("Job postings per day (last 30 days)")
        plt.xlabel("Date")
        plt.ylabel("# jobs scraped")
        plt.tight_layout()
        plt.savefig(OUTPUT_PATH_CHART_JOBS_PER_DAY)
        plt.close()
        logger.info("Saved jobs‑per‑day line chart.")
    else:
        logger.warning("No valid dates; jobs‑per‑day chart skipped.")

    return df


if __name__ == "__main__":
    csv_path = get_csv_path()
    logger.info(f"Reading data from '{csv_path}'.")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        logger.error(
            "CSV file not found. Please ensure 'data/techinasia_jobs_master.csv' exists."
        )
    else:
        cleaned_df = cleanup_and_analyse(df)
        logger.info("Script execution completed.")
