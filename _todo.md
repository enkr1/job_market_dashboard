# TODO: ACING the Take-Home Assessment (Singapore Tech-Jobs Scraper)

- [x] Confirm Docker is *not* required and local Python env is sufficient.

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

---

## 4. Data Cleaning & Analysis

- [ ] Create or update a script (`analysis/clean_and_analyse.py`) to:
  - Load the raw job CSV.
  - Parse salary ranges and posted dates.
  - Print missing-value counts and basic descriptive statistics.
  - Save a cleaned CSV for further analysis.
  - Generate at least two simple plots (salary distribution, top companies).

---

## 5. Reporting

- [ ] Draft a concise, well-structured report (Markdown or PDF) covering:
  - Project goal & scraping challenges.
  - Tech stack used and reasons for using Selenium.
  - Code workflow and logic highlights.
  - Data analysis: insights, statistics, and key plots.
  - Problems encountered and solutions taken.
  - Final results and location of output files.

- [ ] Update `README.md` to clearly document:
  - Project purpose and features.
  - How to set up and run everything locally.
  - Where to find the main outputs (CSV, cleaned data, plots, report).

---

## 6. Validation & Submission

- [ ] Test end-to-end: from scraping to cleaning to analysis to reporting.
- [ ] Ensure outputs meet requirements (≥100 jobs, data quality, clear outputs).
- [ ] Proofread all deliverables for clarity, grammar, and professionalism.
- [ ] Prepare submission package (repo or ZIP) with all required files included.
