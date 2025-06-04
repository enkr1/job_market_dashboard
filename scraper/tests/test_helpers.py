from utils.functions import get_csv_path
from scraper.selenium_scraper import extract_job_data_from_card
from scraper.selenium_scraper import scrape_all_jobs
from selenium.webdriver.remote.webelement import WebElement
from unittest.mock import MagicMock

import pandas as pd



def test_get_csv_path_creates_data_directory(tmp_path):
    # Arrange: Set up a temporary directory as the project root
    fake_project_root = tmp_path
    fake_data_dir = fake_project_root / "data"
    expected_csv_path = fake_data_dir / "techinasia_jobs_master.csv"

    # Act: Call the function under test with the temporary root directory
    csv_path = get_csv_path(root_dir=fake_project_root)

    # Assert: Check that the data directory is created
    assert fake_data_dir.exists() and fake_data_dir.is_dir(), "Data directory was not created."

    # Assert: Check that the returned path is correct
    assert csv_path == expected_csv_path, "CSV path is not as expected."



def test_extract_job_data_from_card():
    # Create a mock WebElement
    mock_card = MagicMock(spec=WebElement)

    # Mock the elements and their return values
    mock_card.find_element.return_value.text = 'Software Engineer'
    mock_card.find_element.return_value.get_attribute.return_value = 'https://example.com/job/123'

    # Call the function
    job_data = extract_job_data_from_card(mock_card)

    # Assertions
    assert job_data['title'] == 'Software Engineer'
    assert job_data['link'] == 'https://example.com/job/123'



def test_extract_job_data_from_card_missing_elements():
    # Create a mock WebElement that raises exceptions
    mock_card = MagicMock(spec=WebElement)
    mock_card.find_element.side_effect = Exception('Element not found')

    # Call the function
    job_data = extract_job_data_from_card(mock_card)

    # Assertions
    assert job_data == {}



def test_scrape_all_jobs_returns_dataframe(monkeypatch):
    # Create a mock WebElement representing a job card
    mock_card = MagicMock(spec=WebElement)
    mock_card.find_element.return_value.text = 'Software Engineer'
    mock_card.find_element.return_value.get_attribute.return_value = 'https://example.com/job/123'

    # Create a mock driver
    mock_driver = MagicMock()
    mock_driver.get.return_value = None
    mock_driver.execute_script.return_value = 1000
    mock_driver.find_elements.return_value = [mock_card]

    # Mock configure_webdriver to return the mock driver
    monkeypatch.setattr('scraper.selenium_scraper.configure_webdriver', lambda: mock_driver)

    # Call the function
    df = scrape_all_jobs()

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert not df.empty



def test_dedup_by_id(monkeypatch):
    dup_card = MagicMock(spec=WebElement)
    # Two cards with same anchor href ⇒ same id
    dup_card.find_element.return_value.get_attribute.return_value = (
        "https://www.techinasia.com/jobs/abc-123"
    )

    mock_driver = MagicMock()
    mock_driver.find_elements.return_value = [dup_card, dup_card]
    monkeypatch.setattr("scraper.selenium_scraper.configure_webdriver", lambda: mock_driver)

    df = scrape_all_jobs()
    assert len(df) == 1      # only one row kept
