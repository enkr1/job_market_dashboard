# tests/test_data_processing.py

import pandas as pd
from data_processing import cleanup_and_analyse

def test_cleanup_and_analyse():
    test_data = {
        'job_id': [1, 2, 2, 3],
        'salary_min': ['5000', '6000', '6000', None],
        'company_name': ['Company A', 'Company B', 'Company B', 'Company C']
    }
    df = pd.DataFrame(test_data)
    cleaned_df = cleanup_and_analyse(df)
    assert cleaned_df.shape[0] == 2  # After removing duplicates and rows with missing salary
