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
- [ ] Written report (1-2 pages) including your overall approach and design

---

## 📦 Setup
### 1. Install dependencies
```sh
pip install -r requirements.txt
```

### 2. Run the scraper directly
```sh
python -m scraper.selenium_scraper # Run the scraper directly
```


## 🧪 Testing
Run tests with:
```sh
python -m pip install -r requirements-dev.txt
python -m pytest
```

## ⏱️ Cron Job Management
### Automate scraper execution:
```sh
chmod +x scripts/*
./scripts/install_cron.sh    # Add cron job
./scripts/uninstall_cron.sh  # Remove cron job
```

## 📁 Output

Scraped data and charts are saved to:
```
-	data/techinasia_jobs_*.csv
- data/charts/*.png
```
