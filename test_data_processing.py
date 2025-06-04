import pandas as pd


def cleanup_and_analyse(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans up raw job data and analyses salary columns.

    Args:
        df (pd.DataFrame): Raw job data with columns including id, title, company, compensation, etc.

    Returns:
        pd.DataFrame: Cleaned data with salary_min, salary_max, company_name, and duplicates removed.
    """

    # Data Cleaning

    # Normalise the primary‑key column name so we can de‑duplicate robustly
    if "job_id" in df.columns:
        id_col = "job_id"
    elif "id" in df.columns:
        id_col = "id"
        # Rename to a canonical name for downstream consistency
        df = df.rename(columns={"id": "job_id"})
        id_col = "job_id"
    else:
        id_col = None  # Fallback if neither column exists

    if id_col:
        df = df.drop_duplicates(subset=[id_col])

    # Parse salary_min and salary_max from compensation string
    def parse_salary(salary_str):
        if not isinstance(salary_str, str):
            return None, None
        # Remove currency and spaces
        s = salary_str.replace("SGD", "").replace(",", "").strip()
        if "–" in s:
            parts = s.split("–")
            try:
                min_salary = float(parts[0].strip())
                max_salary = float(parts[1].strip())
                return min_salary, max_salary
            except ValueError:
                return None, None
        return None, None

    salaries = df["compensation"].apply(parse_salary)
    df["salary_min"] = [s[0] for s in salaries]
    df["salary_max"] = [s[1] for s in salaries]

    # Drop rows without parsable salary
    df = df.dropna(subset=["salary_min", "salary_max"])

    # Normalize company_name to lowercase
    df["company_name"] = df["company"].str.lower()

    return df
