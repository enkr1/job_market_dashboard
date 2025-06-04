## Product Requirements Document (PRD)

Below is a comprehensive PRD for the **job\_market\_dashboard** project, divided into two distinct sections:

1. **Take-Home Assessment Requirements**
2. **Extended Portfolio Plan Requirements**

Each section lists the functional and non-functional requirements, acceptance criteria, and other relevant details.

---

### 1.1. Overview

**Project Name**: `job_market_dashboard`
**Purpose**: Build a robust web-scraping pipeline that extracts structured data on Singapore-based tech job listings, satisfies Coupang’s take-home test requirements, and—beyond that—evolves into a shareable portfolio tool with extended features (e.g. scheduling, visualisation, CI/CD).

---

## 1. TAKE-HOME ASSESSMENT REQUIREMENTS

> **Goal**: Demonstrate your ability to design and implement a web-scraping solution that handles pagination, dynamic content (if any), exports at least 100 structured records in JSON or CSV, and provides a brief analysis of the data.
> **Estimated Effort**: \~2–4 hours.

### 1.1. Functional Requirements

1. **Select a Publicly Accessible Site**

   * Choose a website containing a list or table of ≥ 100 tech-related job listings for Singapore.
   * Confirm via its `robots.txt` that scraping the job listings endpoint is **permitted**.

2. **Scrape Key Data Fields**
   Extract, for each job posting:

   * **Job Title**
   * **Company Name**
   * **Location** (e.g. “Singapore”)
   * **Posted Date** (e.g. “2 days ago”)
   * **Salary Range** (e.g. “\$4,500–\$7,000 SGD” or “Negotiable”)
   * **Employment Type** (e.g. “Full-Time”, “Contract”)
   * **Description Snippet** (first \~200 characters)
   * **Application URL** (absolute link to the job details page)

3. **Handle Pagination (or “Load More”)**

   * Automatically follow the “Next Page” link (or replicate the JSON XHR) until **at least 100 total records** have been collected, or no further pages exist.
   * If content is loaded via JavaScript (e.g. infinite scroll or “Load More” button), implement one of the following:

     * **Scrapy-Splash** (headless rendering)
     * **Selenium** fallback (click button, wait for new items)

4. **Anti-Scraping & Politeness Measures**

   * Respect `robots.txt`: do not crawl any URL patterns explicitly disallowed.
   * Set a realistic `User-Agent` string (e.g. Chrome-like header).
   * Configure a minimal **DOWNLOAD\_DELAY** (e.g. 1 second) and limit concurrent requests (e.g. 2 requests per domain).
   * If the server returns `HTTP 429` (Too Many Requests), implement exponential backoff or retry logic.

5. **Export Data in Structured Format**

   * Save the scraped data as either **CSV** or **JSON**.
   * Ensure proper encoding (UTF-8) and consistent column-order.
   * If using Scrapy, configure `FEED_FORMAT`/`FEED_URI` so that running `scrapy crawl` produces the file automatically.

6. **Brief Data Analysis & Summary**

   * Load the final CSV/JSON into **pandas** (or an equivalent).
   * Compute basic descriptive statistics:

     * **Salary**: min, max, mean, median (after stripping currency symbols).
     * **Posted Date**: distribution (e.g. percentage posted in last 7 days).
     * **Top Hiring Companies**: list the top 5 by frequency.
   * Identify any data-quality issues (e.g. missing salary, inconsistent date formats).
   * Present findings in **200–300 words**, accompanied by 1–2 simple plots (e.g. salary histogram, bar chart of top companies).

7. **Deliverables**

   * **Code / Scripts**

     * A complete Scrapy project (or standalone Python scripts) that can be run with minimal setup.
     * Clear instructions in `README.md` on how to install dependencies and run the scraper.
   * **Extracted Data File**

     * `sg_jobs.csv` (or `sg_jobs.json`) containing ≥ 100 records.
   * **Written Report (1–2 pages)**

     * Title page (project name, author, date)
     * Introduction (objectives)
     * Site selection rationale & robots.txt verification
     * Technology stack & architecture (Python, Scrapy, pandas, optionally Scrapy-Splash/Selenium)
     * Key code snippets and workflow explanation (e.g. pagination logic)
     * Anti-scraping measures summary
     * Data analysis & summary of insights
     * Challenges encountered and how you overcame them
     * Conclusion (confirmation that requirements are met)

8. **Timeline & Acceptance Criteria**

   * **Within 4 hours**: Must be able to produce ≥ 100 records, the CSV/JSON file, and a 1–2 page PDF/Markdown report.
   * **Validation**:

     1. Download/run instructions work “out of the box.” A reviewer can clone the repo, install, and run `scrapy crawl sg_jobs` (or an equivalent script) to reproduce the data file.
     2. The data file contains at least 100 non-duplicate, valid job entries.
     3. The written report clearly explains your approach, shows a snippet of critical code, and summarises data insights.

---

## 2. PORTFOLIO PLAN REQUIREMENTS

> **Goal**: Extend beyond the take-home assessment to evolve **job\_market\_dashboard** into a reusable, automated tool that can be scheduled, visualised, and shared publicly. This section defines additional features, enhancements, and “niceties” that will strengthen your portfolio and highlight your end-to-end engineering & DevOps capabilities.

### 2.1. Functional Requirements

1. **Project Initialization & Licensing**

   * Rename the repository to `job_market_dashboard` (already done).
   * Add an **MIT LICENSE** file at the repo root to explicitly grant open-source rights.
   * Ensure that all code files begin with a short license header or a reference to the repository’s root LICENSE.

2. **Modular, Configurable Scraper**

   * Allow the scraper to accept **command-line arguments** or a **YAML/JSON config** specifying:

     * **Target site URL** (e.g. Tech in Asia, JobsDB).
     * **Max records to fetch** (default: 200).
     * **Output format** (`csv` or `json`).
     * **Throttling settings** (download delay, concurrent requests).
   * Move hard-coded CSS/XPath selectors into a configuration file so that supporting a second site (e.g. JobsDB) is as simple as adding another entry.

3. **Docker & Container Orchestration**

   * Provide a **Dockerfile** that:

     * Uses a lightweight Python base (e.g. `python:3.11-slim`).
     * Installs dependencies from `requirements.txt`.
     * Defines an entrypoint such as `CMD ["scrapy", "crawl", "sg_jobs"]`.
   * Provide a **docker-compose.yml** that can spin up Scrapy + (optionally) Splash for JS rendering:

     ```yaml
     version: '3.8'
     services:
       splash:
         image: scrapinghub/splash:3.7.4
         ports:
           - "8050:8050"
       scraper:
         build: .
         depends_on:
           - splash
         environment:
           - SPLASH_URL=http://splash:8050
         command: ["scrapy", "crawl", "sg_jobs"]
     ```
   * Document in `README.md` how to build and run with Docker:

     ```bash
     docker-compose build
     docker-compose up -d
     docker logs -f job_market_dashboard_scraper_1
     ```

4. **Scheduled Automation & CI/CD**

   * Create a **GitHub Actions** workflow (`.github/workflows/schedule_scrape.yml`) that:

     1. Runs **nightly** at 02:00 AM Singapore time.
     2. Checks out the repo, builds the Docker container (or installs dependencies in a runner), and executes the scraper.
     3. Commits the newly scraped data file (`sg_jobs_YYYYMMDD.csv`) into a separate branch or S3 bucket.
     4. Optionally, triggers a rebuild of a static front-end if present.
   * Alternatively, demonstrate how to schedule on **AWS** using Terraform:

     * An **AWS Lambda** function (packaged via a Lambda layer containing Scrapy dependencies) triggered by **EventBridge** daily.
     * Store results in an **S3 bucket** (`s3://job-market-dashboard-data/`) with a sensible key prefix (`jobs/YYYY/MM/DD/`).

5. **Data Cleaning & Post-Processing Pipeline**

   * Implement a **Scrapy pipeline** (`pipelines.py`) that:

     1. Normalises salary strings → numeric fields (`salary_min`, `salary_max`).
     2. Parses “Posted Date” strings → ISO-formatted dates.
     3. Filters out any duplicate job IDs or URLs.
   * After scraping, invoke a **Python script** (or Jupyter Notebook) that:

     * Loads the pipeline’s output into **pandas**.
     * Runs basic analytics:

       * Salary distribution (mean, median, quantiles).
       * Top 10 hiring companies.
       * Trend of “new postings per day” over the last 7 days (if historical data available).
     * Saves a cleaned CSV (`sg_jobs_cleaned.csv`) for consumption by the front-end or visualisation layer.

6. **Basic Front-End Dashboard (Optional but Recommended)**

   * Build a minimal **React** (or plain HTML + Chart.js) “dashboard” that:

     * Fetches `sg_jobs_cleaned.csv` (or JSON) from a **public S3 bucket** or GitHub raw URL.
     * Displays:

       * A **histogram** of salary ranges.
       * A **bar chart** of the top 5 companies by listing count.
       * A **line chart** showing the number of new postings per day (if timestamps available).
     * Allows the user to filter by:

       * **Date range** (e.g. last 7 days, last 30 days).
       * **Minimum salary** threshold.
       * **Employment type** (“Full-Time”, “Contract”).
   * Host the front-end on **GitHub Pages** (via a `gh-pages` branch) or on **S3 + CloudFront** with a custom domain (e.g. `jobs.enkr1.com`).

7. **Documentation & Usage Guide**

   * Expand `README.md` to include:

     * **Project overview** and motivations (both for take-home and portfolio).
     * Detailed **installation instructions** (local Python, virtual environment, Docker).
     * **Configuration guide** (example `config.yaml`).
     * **Usage examples**:

       * Running locally: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && scrapy crawl sg_jobs`
       * Running in Docker: `docker-compose up`
       * Running via GitHub Actions (how to review logs & downloaded data).
     * **License**: reference to `LICENSE` (MIT).
     * **Roadmap/Future Enhancements**: e.g. add sentiment analysis on job descriptions, support multiple countries.

8. **Testing & Validation**

   * Add a **smoke-test script** (`tests/test_selectors.py`) that verifies:

     1. The CSS selector for `.job-listing__item` yields at least one element on page 1.
     2. The “Next Page” link selector exists.
   * In GitHub Actions, run `pytest` or a script that checks for selector validity (to catch layout changes).

### 2.2. Non-Functional Requirements

1. **Code Quality & Maintainability**

   * Follow **PEP 8** style guidelines for Python.
   * Use **docstrings** and comments to explain non-trivial logic (e.g. date parsing).
   * Keep configuration (CSS selectors, URLs) outside of code in a separate file if possible.

2. **Performance & Scalability**

   * The scraper should complete 100 records in ≤ 2 minutes on a standard GitHub Actions runner or local machine.
   * Use **Scrapy’s asynchronous engine** and respect throttling to avoid overloading the target site.

3. **Reliability & Error Handling**

   * If a request fails (e.g. network timeout), retry up to 3 times with exponential backoff.
   * If a specific job listing is missing a required field, skip it gracefully and log a warning.

4. **Security & Ethics**

   * Do not hard-code any secrets or API keys.
   * Respect the target site’s `robots.txt` policies.
   * Do not store scraped data publicly if it contains personal data. In this case, job listings are public, so it is acceptable to share aggregated results.

5. **Documentation & Traceability**

   * All configuration and “magic numbers” (e.g. “scrape at 02:00 AM”).
   * Version the data files (e.g. `sg_jobs_20250604.csv`) so it’s clear which date the data corresponds to.

6. **Licensing & Open Source**

   * The project must be released under the **MIT License**.
   * All code files should reference the root `LICENSE` in their headers, e.g.:

     ```python
     # SPDX-License-Identifier: MIT
     # © 2025 Jing Hui PANG
     ```

---









## 2. How to Add an MIT License After Publishing

> **Question**: “I forgot to choose MIT licence before I published. Does it matter? How should I add that now?”

1. **Why It Matters**

   * By default, a GitHub repository is “All Rights Reserved.” Others cannot legally reuse, modify, or redistribute your code without explicit permission.
   * Adding an MIT licence removes ambiguity: it grants everyone permission to use, copy, modify, and distribute your code, provided they include the same licence.

2. **How to Add the MIT License**

   1. **Create a `LICENSE` file** in the root of your repository with the standard MIT text. You can generate it via GitHub’s web interface or manually paste this template, then replace `[year]` and `[fullname]`:

      ```text
      MIT License

      © 2025 Jing Hui PANG

      Permission is hereby granted, free of charge, to any person obtaining a copy
      of this software and associated documentation files (the “Software”), to deal
      in the Software without restriction, including without limitation the rights
      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
      copies of the Software, and to permit persons to whom the Software is
      furnished to do so, subject to the following conditions:

      The above copyright notice and this permission notice shall be included in all
      copies or substantial portions of the Software.

      THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
      AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
      LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
      SOFTWARE.
      ```

   2. **Commit & Push**

      ```bash
      git checkout main
      touch LICENSE
      # Paste the MIT text into LICENSE, save
      git add LICENSE
      git commit -m "Add MIT License"
      git push origin main
      ```

   3. **Update `README.md`**

      * At the top or bottom, add a badge or note:

        ```markdown
        ## License

        This project is licensed under the [MIT License](LICENSE).
        ```
      * Optionally add a SPDX identifier in your code files’ headers:

        ```python
        # SPDX-License-Identifier: MIT
        # © 2025 Jing Hui PANG
        ```

3. **Result**

   * Once pushed, GitHub will automatically detect the `LICENSE` file and display “MIT License” on the repo homepage. This ensures anyone cloning or forking knows they can legally reuse your code.

---

## 3. “bash: docker: command not found” — What Happened & How to Fix

> **Question**: “What happened to my Docker!? I got this error → `bash: docker: command not found`”

1. **Cause**

   * That error indicates that the `docker` binary (client) is not installed or not in your shell’s `PATH`.
   * On a **macOS** or **Linux** system, if Docker Desktop (mac) or Docker Engine (Linux) is not installed, the `docker` command will be unavailable.
   * It may also mean you are operating in an environment (e.g. a remote VM or Linux user account) where Docker has not yet been set up.

2. **How to Install Docker**

   ### 3.1. On macOS

   * **Docker Desktop for Mac** is the easiest approach:

     1. Download from [https://docs.docker.com/desktop/mac/install/](https://docs.docker.com/desktop/mac/install/)
     2. Open the `.dmg` and drag Docker Desktop to your `Applications` folder.
     3. Launch Docker Desktop; wait for the “Docker is running” whale icon to appear in the menu bar.
     4. Open a new Terminal window and run:

        ```bash
        docker --version
        ```

        You should see something like `Docker version 24.0.2, build abcdef`.

   * **Homebrew (alternative)**:

     ```bash
     brew install --cask docker
     open /Applications/Docker.app
     ```

     Then confirm with `docker --version`.

   ### 3.2. On Linux (Ubuntu/Debian)

   1. **Uninstall old versions** (if any):

      ```bash
      sudo apt-get remove docker docker-engine docker.io containerd runc
      ```
   2. **Set up repository**:

      ```bash
      sudo apt-get update
      sudo apt-get install \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
      echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      ```
   3. **Install Docker Engine**:

      ```bash
      sudo apt-get update
      sudo apt-get install docker-ce docker-ce-cli containerd.io
      ```
   4. **Verify installation**:

      ```bash
      docker --version
      ```
   5. **Manage Docker as a non-root user** (optional, but recommended):

      ```bash
      sudo groupadd docker
      sudo usermod -aG docker $USER
      # Then log out and back in for changes to take effect
      ```
   6. **Start Docker service**:

      ```bash
      sudo systemctl enable docker
      sudo systemctl start docker
      ```

   ### 3.3. On Windows

   * Download **Docker Desktop for Windows** from [https://docs.docker.com/desktop/windows/install/](https://docs.docker.com/desktop/windows/install/)
   * Follow the installer. Ensure **WSL 2** is enabled if you’re on Windows 10/11.
   * After installation, open PowerShell or Command Prompt and run:

     ```powershell
     docker --version
     ```

3. **Alternative Without Docker**

   * If you cannot install Docker (e.g. corporate laptop with restricted privileges), you can still run the project locally in a Python virtual environment:

     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     scrapy crawl sg_jobs
     ```
   * The Docker “convenience” (consistent environment) is nice for CI/CD, but not strictly required if the local Python setup works.

4. **Next Steps**

   * **Install** Docker following the appropriate platform instructions above.
   * Once `docker` is recognised, you can build/run the container as documented in your `README.md`.

---

## 4. Interpretation of TechInAsia’s robots.txt

> **Question**: “Here is TechInAsia’s `robots.txt`. What does it mean for our scraping plan?”

```text
User-agent: *
Disallow: */comments$
Disallow: */feed$
Disallow: */trackback$
Disallow: /cgi-bin
Disallow: /core$
Disallow: /core/
Disallow: /create
Disallow: /forgot-password
Disallow: /login
Disallow: /logout
Disallow: /register
Disallow: /vendor$
Disallow: /vendor/
Disallow: /version.json
Disallow: /wp-content/cache
Disallow: /wp-content/uploads/*/*/1650344292_1.png
Disallow: /wp-content/uploads/**/*seo-restricted*.*
Disallow: /harassment-bankruptcy-debts-lawsuits-moovaz
Disallow: /laundry-list-issues-moovaz
Sitemap: https://www.techinasia.com/sitemap.xml
Sitemap: https://www.techinasia.com/sitemaps/articles/sitemap.xml
Sitemap: https://www.techinasia.com/sitemaps/people/sitemap.xml
Sitemap: https://www.techinasia.com/sitemaps/jobs/sitemap.xml
Sitemap: https://www.techinasia.com/sitemaps/companies/sitemap.xml
Sitemap: https://www.techinasia.com/sitemaps/asktia/sitemap.xml
```

### 4.1. What Is Disallowed?

1. **Comments, Feeds, Trackback Endpoints**

   * Any URL ending in `/comments` or `/feed` or `/trackback` is forbidden.
   * e.g. `https://www.techinasia.com/some-article/comments` should not be scraped.

2. **Authentication & User-Generated Paths**

   * `/create`, `/login`, `/logout`, `/register`: do not attempt to scrape user-authentication pages.
   * `/forgot-password`: obviously not relevant.

3. **Core or Vendor Folders** (internal assets)

   * `/core`, `/core/`, `/vendor`, `/vendor/`: internal and not relevant to job listings.

4. **Static Asset Cache & Specific Files**

   * `/wp-content/cache` and certain `/wp-content/uploads/*` patterns: do not fetch these.
   * Specific SEO-restricted images (irrelevant for jobs).

5. **Two Specific Slugs**

   * `/harassment-bankruptcy-debts-lawsuits-moovaz`
   * `/laundry-list-issues-moovaz`
   * These appear to be URLs for specific articles. They are disallowed, but do not affect `/jobs`.

6. **Allowed**

   * **No rule explicitly disallows** `/jobs` or `/sitemaps/jobs/`.
   * The presence of `Sitemap: https://www.techinasia.com/sitemaps/jobs/sitemap.xml` suggests they publish a sitemap of all job URLs.

### 4.2. Implications for Your Scraper

1. **Scraping `/jobs` is Permitted**

   * Because there is no `Disallow: /jobs` line, crawling `https://www.techinasia.com/jobs/singapore` (and its pagination) is allowed.
   * Best practice: fetch the sitemap first (`/sitemaps/jobs/sitemap.xml`) to confirm the exact URLs you will crawl.

2. **Use the Sitemap to Your Advantage**

   * Instead of crawling page by page, you could download and parse the jobs sitemap (which might list thousands of job‐detail URLs) and then selectively crawl only those you need (e.g. first 100).
   * Example:

     ```python
     import requests
     from bs4 import BeautifulSoup

     sitemap_url = "https://www.techinasia.com/sitemaps/jobs/sitemap.xml"
     r = requests.get(sitemap_url)
     soup = BeautifulSoup(r.text, "xml")
     urls = [loc.text for loc in soup.find_all("loc")]
     # Now `urls` is a list of all job‐detail pages.
     # You could filter for only Singapore jobs or limit to 100.
     ```

3. **Continue Respecting Crawl-Delay & Throttling**

   * Even if `/jobs` is allowed, refrain from making hundreds of rapid requests: use a \~1 second delay, or rely on Scrapy’s AutoThrottle.
   * If you rely on the job sitemap, do not fetch *all* 1,000+ job pages at once; fetch only what you need (e.g. the first 100).

4. **Avoid Disallowed URLs**

   * Do **not** attempt to crawl any of the paths under `Disallow:` (e.g. `/login`, `/register`).
   * If you discover a comment section link in the HTML (unlikely on job listings), skip it.

### 4.3. Conclusion

* **TechInAsia’s `robots.txt` explicitly permits** crawling of `/jobs` pages.
* You may proceed with confidence, provided you obey rate limits, user-agent policies, and avoid any disallowed patterns.

---

## 5. Summary & Next Steps

1. **PRD Complete**

   * You now have a detailed PRD in Markdown covering both the strict take-home assessment requirements and an extended, future-proof portfolio plan.

2. **License Added**

   * Create and commit an `MIT LICENSE` file immediately to formalise open-source usage.

3. **Docker Installation**

   * Follow the platform-specific guidelines above to install Docker so you can build and run the scraper in a container.

4. **robots.txt Verification**

   * Confirmed that scraping `/jobs` on TechInAsia is allowed. You may optionally use the `/sitemaps/jobs/sitemap.xml` to obtain the list of job URLs.

Once the above tasks are complete, you can proceed to implement the scraper, containerise it, schedule it via GitHub Actions (or AWS), and—if you choose—build a minimal front-end dashboard. This will ensure that **job\_market\_dashboard** not only satisfies the immediate take-home assessment but also becomes a polished, shareable project in your GitHub portfolio. Good luck!
