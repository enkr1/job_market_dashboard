# TODO: ACING the Take-Home Assessment (Singapore Tech-Jobs Scraper)

- [X] Confirm Docker is *not* required and local Python env is sufficient.

---

## 1. Project Setup

- [X] Repo is named `job_market_dashboard`.
- [X] `.gitignore` set up to exclude Python/data files.
- [X] Python `.venv` created and activated.
- [X] All dependencies installed via `requirements.txt`.
- [X] Confirmed Scrapy and pandas are importable in Python.

---

## 2. Site Selection & Research

- [X] Verified `/jobs` endpoint is allowed in `robots.txt`.
- [X] Inspected Tech in Asia Jobs for allowed scraping.
- [X] Located and documented job card CSS selectors.
- [X] Identified pagination/“Load More” mechanism (requires Selenium).
- [X] Documented expected data fields for each job post.

---

## 3. Data Extraction (Selenium Scraper)

- [X] Wrote and debugged a Selenium-based scraper for Tech in Asia Jobs.
- [X] Implemented scraping logic to handle dynamic loading and scroll/pagination.
- [X] Successfully exported job data as a CSV file with all required fields.
- [X] Ensured CSV is saved at root `data/` folder for easy access.
- [X] Add polite throttling note in code comments (how we avoid overloading TIA).

---

## 4. Data Cleaning & Analysis
- [X] Create or update a script (`analysis/clean_and_analyse.py`) to:
  - [X] Load the raw job CSV.
  - [X] Parse salary ranges and posted dates.
  - [X] Print missing-value counts and basic descriptive statistics.
  - [X] Save a cleaned CSV for further analysis.
  - [X] Generate at least two simple plots
         • salary distribution (salary_histogram.png)
         • top companies (bar_top_companies.png)
         • jobs-per-day (jobs_per_day.png)
- [X] Log a compact data-quality report via `utils.reporting.log_quality_report`.
- [X] Write a tiny docstring on *why* rows without salary are kept/dropped.

---

## 5. Dashboard (Flask + Chart.js)
- [X] Build `/api/v1/jobs` endpoint (NaN-free JSON).
- [X] Serve interactive Chart.js graphs (salary, companies, jobs/day).
- [X] Display “Last updated” timestamp in footer.
- [ ] Add auto-refresh badge or spinner while charts reload.
- [ ] Note in README how to change port / host for deployment.

---

## 6. Automated Tests

- [X] Unit tests for util helpers (`utils`, salary parser, date parser).
- [X] Smoke test for scraper functions using `pytest` & monkeypatch.
- [ ] Add one integration test that loads a tiny CSV and hits `/api/v1/jobs`.
- [ ] CI workflow stub (GitHub Actions) that runs `pytest` on push.

---

## 7. Reporting

- [ ] Draft a concise, well-structured **report (Markdown or PDF)** covering:
  - Project goal & scraping challenges.
  - Tech stack used and reasons for using Selenium.
  - Code workflow and logic highlights.
  - Data analysis: insights, statistics, and key plots.
  - Problems encountered and solutions taken.
  - Final results and location of output files.
- [ ] Update **README.md** to clearly document:
  - Project purpose and features.
  - How to set up and run everything locally.
  - Where to find the main outputs (CSV, cleaned data, plots, report).
  - Short “Troubleshooting” section (e.g., ChromeDriver path).

---

## 8. Validation & Submission

- [ ] Test end-to-end: scraping → cleaning → analysis → dashboard.
- [ ] Ensure outputs meet requirements (≥100 jobs, data quality, clear outputs).
- [ ] Proofread all deliverables for clarity, grammar, and professionalism.
- [ ] Prepare submission package (repo link or ZIP) with all required files included.
