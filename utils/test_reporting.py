import pandas as pd

from utils.reporting import log_quality_report


def test_log_quality_report_runs(tmp_path):
    sample = pd.DataFrame(
        {
            "id": ["a", "b"],
            "salary_min": [3000, None],
            "published_date_parsed": pd.to_datetime(["2025-05-01", None]),
        }
    )
    output_file = tmp_path / "quality_report.csv"
    log_quality_report(sample, output_path=str(output_file))
    assert output_file.exists()
    df = pd.read_csv(output_file)
    assert "missing_values_id" in df.columns
    assert "salary_min_stats_count" in df.columns
    assert "date_range_oldest" in df.columns


def test_log_quality_report_creates_csv(tmp_path):
    # Create a sample DataFrame
    df = pd.DataFrame(
        {
            "salary_min": [3000, 4000, None],
            "published_date_parsed": pd.to_datetime(["2025-05-01", "2025-05-02", None]),
        }
    )

    # Define the path for the temporary CSV
    output_path = tmp_path / "quality_report.csv"

    # Call the function
    log_quality_report(df, output_path=output_path)

    # Assert the file was created
    assert output_path.exists()

    # Optionally, read and check contents
    report_df = pd.read_csv(output_path)
    assert "salary_min_stats_count" in report_df.columns
