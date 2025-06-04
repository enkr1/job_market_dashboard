# Job Market Dashboard - Take-Home Assessment for Coupang

## Test Overview and Objective for Crawling/Web Scraping Engineer
Extract structured data from a given website, handle potential challenges such
as pagination, or dynamic content, and present findings clearly. This test
evaluates your ability to design and implement a web scraping solution, use
appropriate tools, and communicate your approach and results effectively.
Estimated Time: 2-4 hours

## Task Description

1. Data Extraction
    1. Select a publicly accessible website that contains tabular or list-
based data (e.g., product listings, event schedules, or contact directories). Your goal is to scrape the following:
        - Key data fields
        - Handle pagination or load more buttons if applicable
        - Extract at least 100 records or all available if fewer

2. Data Output
   1. Save the extracted data in a structured format such as JSON or
CSV

3. Challenges Handling
    1. If the site uses JavaScript to load content dynamically, implement a solution to handle this (e.g., using Selenium or Scrapy with Splash). If the site has basic anti-scraping measures (like rate limiting), describe your approach to handle it.

4. Analysis & Summery
    1. Provide a brief analysis of the data you extracted. This could include insights like data distributions, notable patterns, or data quality issues.

## Deliverables
- [X] Code/Scripts used for scraping and data extraction, with clear instructions on how to run them
- [X] Extracted data file in JSON or CSV format
- [X] Written report (1-2 pages) including your overall approach and design - [report](/report.md)

---
Your README setup is already clean and direct, but it can be made even more concise, professional, and welcoming to contributors. Here’s an improved, slightly more polished version that maintains clarity and structure while adding brief context at each step, minimal redundancy, and a bit of friendliness—*without sacrificing any detail*.

---

## 📦 Set up

> **Platform:** macOS (Bash).
> **Prerequisite:** Python 3.x installed.

### Install dependencies

```sh
pip install -r requirements.txt
```

### Run the scraper

```sh
python -m scraper.selenium_scraper
```

### Start the server

```sh
python app.py
```

### 🧪 Run Tests

Install dev dependencies and run tests:

```sh
pip install -r requirements-dev.txt
pytest
```

### ⏰ Schedule Scraper with Cron

Automate scraper execution via cron jobs:

```sh
chmod +x scripts/*
./scripts/install_cron.sh    # Add scheduled run
./scripts/uninstall_cron.sh  # Remove scheduled run
```

Check your cron jobs:

```sh
crontab -l
```

### 📂 Outputs

Scraped data and generated charts will be saved to:

```
data/techinasia_jobs_*.csv
data/charts/*.png
```

> If you encounter issues, ensure all dependencies are installed and your Python version is correct.



---



## 📁 Key Files & Structure

```text
.
├── README.md                 # Setup & usage instructions
├── report.md                 # Project writeup/report
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # Dev/test dependencies
├── app.py                    # API/web server entrypoint
├── logs/                     # Runtime logs
├── _additional/              # Project docs, Dockerfiles, legacy scripts
├── _learnings/               # Personal notes, not needed for review
|
├── data/
│   ├── techinasia_jobs_*.csv # Output: scraped jobs data
│   ├── charts/               # Output: analysis plots
│   │   └── *.png
│   └── quality_report.csv    # Data quality info
|
├── scraper/
│   ├── selenium_scraper.py   # Main Selenium scraping logic (**entry point**)
│   ├── __init__.py
│   ├── settings.py           # Scrapy/Selenium settings (if used)
│   ├── items.py, pipelines.py, middlewares.py  # (Scrapy modules, if used)
│   └── spiders/
│       └── sg_jobs_spider.py # Spider logic (initial idea, for reference)
|
├── data_processing.py        # Cleans & analyses scraped data
├── utils/
│   ├── functions.py          # Shared helper functions
│   ├── reporting.py          # Reporting utilities
│   ├── constants.py          # Constants
|   ├── enums.py              # Enums
│   └── test_reporting.py     # Test for reporting utils
|
├── scripts/
│   ├── install_cron.sh       # Add cron job
│   └── uninstall_cron.sh     # Remove cron job
|
├── test_data_processing.py   # Tests for data processing
|
├── templates/
    └── index.html            # (If web frontend is used)

```

---

***Explanation for reviewers:***

* **scraper/selenium\_scraper.py** – *Main scraping entry point*.
* **data\_processing.py** – *Cleans and analyses data*.
* **data/** – *All output data and generated plots are saved here*.
* **scripts/** – *Cron job management*.
* **utils/** – *Reusable functions and reporting helpers*.
* **README.md / report.md** – *Instructions and technical writeup*.

---

**Unsure/Extra (review if needed):**

* `app.py` (if not running as a web server, can ignore)
* `spiders/`, `items.py`, `pipelines.py`, `middlewares.py` (if not using Scrapy)
* `_additional/`, `_learnings/` (project notes/docs, not needed for build/run)
* `logs/` (helpful for debug, not core logic)



---



## References
- https://www.techinasia.com/jobs/search?country_name[]=Singapore&country_name[]=Remote&job_type[]=Full-time&job_type[]=Freelance&currency=SGD
- https://www.techinasia.com/robots.txt
- https://www.techinasia.com/sitemap.xml
