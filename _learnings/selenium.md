# Reflection on Web Scraping Approach for Tech in Asia Job Listings

## Introduction
In this technical assessment, my original plan was to extract Software Engineer, Full-time job postings for Singapore from Tech in Asia by reverse-engineering their underlying API (Algolia). After encountering repeated obstacles—expired API keys, 403/400 HTTP errors, and inconsistent payload parameters—I pivoted to a Selenium-based approach. This document reflects on my journey, mistakes, and learning points, and highlights why Selenium ultimately proved stronger for this particular use case.

---

## 1. Initial Approach: API (XHR) Scraping

### 1.1 Motivation
- **Speed**: Hitting the same JSON endpoints that the browser uses usually retrieves structured data quickly.
- **No JavaScript rendering**: Directly retrieving JSON meant there was no need to spin up a browser, reducing overhead.
- **Familiar pattern**: I have previously scraped other sites by capturing network requests via DevTools → Network → XHR, extracting the request payload, and replaying it in Python with `requests`.

### 1.2 Steps Taken
1. **Navigated to DevTools Network tab** on the Tech in Asia Jobs page:
   - Filtered by `country_name[]=Singapore`, `job_category_name[]=Software Engineer`, and `job_type[]=Full-time`.
   - Observed a `POST` to an Algolia endpoint:
     ```
     https://219wx3mpv4-dsn.algolia.net/1/indexes/*/queries?
       x-algolia-agent=Algolia%20for%20vanilla%20JavaScript 3.30.0;JS Helper 2.26.1
       &x-algolia-application-id=219WX3MPV4
       &x-algolia-api-key=<some_key>
     ```
2. **Copied Headers & Payload**:
   - Request Method: `POST`
   - Headers like `X-Algolia-Application-Id: 219WX3MPV4`, `X-Algolia-API-Key: b52800…`, `Content-Type: application/json`, etc.
   - Payload (URL-encoded `params` field with facets, filters, `page=0`, `hitsPerPage=20`, etc.).

3. **Built a Python `fetch_jobs.py`**:
   - Used `requests.post(...)` with those exact headers and JSON body.
   - Printed `response.status_code` and `response.text`.

### 1.3 Challenges & Mistakes
- **Incorrect/Expired API Key**:
  - Initially, I copied the API key `b528003a875dc1cd402bfe0d8db8b3f8e` from DevTools. But I received `403 Forbidden`.
  - Later, DevTools showed a slightly different key (`b528008a75dc1c4402bfe0d8db8b3f8e`), which succeeded once but then timed out or returned `400 Bad Request` in subsequent runs. This meant the key was rotating or tied to a session, which I hadn’t anticipated.

- **Dynamic Payload Parameters**:
  - The `params` field in the Algolia payload is a URL-encoded string containing JSON-like parameters:
    ```text
    query=&hitsPerPage=20&maxValuesPerFacet=1000&page=0&facets=[…]&tagFilters=[[…],[…],[…]]
    ```
  - I hard-coded the `tagFilters` for “Full-time”, “Software Engineer”, “Singapore”. However, I missed subtle updates in the site’s JavaScript: sometimes the site changed the way it combined filters (e.g., changed facet names or their encoding). As a result, “nbHits = 0” became common.

- **Lack of Robust Debugging Prints**:
  - My initial `fetch_jobs.py` printed only “0 hits” and silently wrote an empty CSV. Only in later iterations did I add `[DEBUG]` statements to print full request, headers, and the first 1,000 characters of the response. By then, I had lost confidence that the API method would remain stable.

- **Underestimating Session & Cookies**:
  - I didn’t send the same cookies or referer that the browser did. The Algolia endpoint likely checks for a valid session token or origin; omitting or mis-matching these resulted in `403` or empty responses.

- **Time Spent vs. Return**:
  - Over ~4–5 hours, I chased the API key rotation and tinkered with headers until realizing that even if I got a working request once, it would break later as soon as the site updated their client scripts.

### 1.4 Learning Points from API Scraping
- **Network requests can be ephemeral**: API keys embedded in public JavaScript can rotate or expire frequently.
- **DevTools ≠ stable reference**: Copying exactly from Network tab is a good starting point, but the site’s JS might rebuild/obfuscate keys on every page load or even per session.
- **Add early debug prints**: Always log full request URL + payload + headers to verify what you’re sending versus what the browser sends.
- **Check site terms**: Many modern sites explicitly discourage or rate-limit direct API hits. Sometimes a headless browser is “the intended” way to expose data.

---

## 2. Transition to Selenium-Based Scraping

### 2.1 Why Selenium?
- **Full Browser Context**:
  - Selenium launches a real (headless) Chrome instance that executes all JavaScript. This ensures that any obfuscated key or client-side token generation happens automatically. I no longer needed to reverse-engineer Algolia calls.

- **Resilience to Minor Site Changes**:
  - If Tech in Asia changes how they encode filters in the URL or in JavaScript, as long as the job cards still have a stable `data-cy="job-result"` attribute, I can reliably locate elements on the rendered page.

- **Ease of Debugging**:
  - With Selenium’s `driver.page_source`, I can instantly dump the HTML after rendering. If something goes wrong, I see whether the jobs are truly not in the DOM, or if my CSS selector is wrong.

### 2.2 Key Steps in the Selenium Implementation
1. **Configure Headless Chrome**
   - Used `--headless`, `--no-sandbox`, `--disable-dev-shm-usage`.
   - Verified that my local ChromeDriver version matches my installed Chrome version (common pitfall).

2. **Waiting for Initial Elements**
   - Wrapped `WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-cy='job-result']")))`.
   - This replaced the fragile “sleep 15 seconds” approach. The script now proceeds as soon as at least one job card appears, but errors out after 15s if none ever show.

3. **Extracting Job Fields**
   - For each job card (`<article data-cy="job-result">`), I extracted:
     - **Title**: `job_card.find_element(By.CSS_SELECTOR, "a[data-cy='job-title']").text`
     - **Link**: `.get_attribute("href")`
     - **Company**: `.find_element(By.CSS_SELECTOR, ".details a[href^='/companies']").text`
     - **Location**: `.find_element(By.CSS_SELECTOR, ".details > div:nth-child(3)").text`
   - Wrapped each extraction in a `try/except`, so that if one card lost a field, the script simply logs a warning and moves on rather than crashing.

4. **Infinite Scroll Loop**
   - After scraping the initially visible cards, I repeatedly ran:
     ```python
     driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
     time.sleep(2)
     new_height = driver.execute_script("return document.body.scrollHeight")
     if new_height == last_height:
         break
     last_height = new_height
     # Then re-fetch job cards and add any new ones.
     ```
   - This pattern ensures that I load every “lazy-loaded” card. Each round, I re-queried `driver.find_elements(By.CSS_SELECTOR, JOB_CARD_SELECTOR)` and compared their links against a `set()` of already-seen URLs. Only truly new jobs got appended to my list.

5. **Logging & Debug Prints**
   - Migrated from bare `print` statements to Python’s `logging` module with `DEBUG`, `INFO`, `WARNING`, `ERROR` levels.
   - Example logs:
     ```
     [INFO ] Navigating to URL…
     [DEBUG] Waiting up to 15s for initial job cards…
     [INFO ] Initial load: found 20 job cards
     [DEBUG] Extracted job: “Senior Frontend Engineer” @ Cyberbot Pte Ltd
     [DEBUG] Scroll round #1: old_height=1234, new_height=2345
     [INFO ] Round #1 → scraped 20 NEW job cards
     [INFO ] No height change detected; all jobs loaded
     [INFO ] Total jobs collected: 40
     [INFO ] CSV written to /path/to/project_root/data/techinasia_jobs_selenium.csv
     ```
   - Having granular logs allowed me to trace exactly which step might have stalling or failures.

6. **Robust Directory Handling**
   - To ensure the CSV always lands in `<project_root>/data/`, regardless of where the script is run:
     ```python
     project_root = Path(__file__).resolve().parent.parent
     data_dir = project_root / "data"
     data_dir.mkdir(parents=True, exist_ok=True)
     output_path = data_dir / "techinasia_jobs_selenium.csv"
     ```
   - This avoids confusion if someone `cd scraper` then `python selenium_scrapper.py`—the CSV still appears at the project root.

### 2.3 Mistakes & Iterations During Selenium Phase
- **Circular Import “selenium.py”**:
  - I initially named my script `selenium.py`. When I did `from selenium import webdriver`, Python resolved my file instead of the real `selenium` package → `ImportError: cannot import name 'webdriver' from partially initialized module 'selenium'`.
  - **Lesson**: Avoid naming your scripts after libraries you import.

- **Waiting Too Short / Too Long**:
  - My first code used `WebDriverWait(driver, 5)` and timed out on slower network. I bumped to 15s. Then I noticed that if the page partially loaded in 5s, but images or some script-loaded elements took 7s, I was still missing data.
  - **Lesson**: Find the right compromise between “wait long enough to see content” and “don’t force the user to wait 60 seconds.” Often, 10–15 seconds is sufficient for a modern site if your internet connection is stable.

- **Scroll Loop Did Not Re-fetch Cards**:
  - In my first iteration, I simply scrolled until the page height stabilized, but **forgot** to re-collect new job cards on each loop iteration. The result: only the initial batch got scraped, and `all_jobs` never grew after the first pass. Seeing “Total jobs collected: 20” when I knew there were 40+ on the site flagged that problem.
  - **Fix**: After each scroll, call `driver.find_elements(...)` again and compare against a `seen_links` set.

- **Saving Data Before Quitting Driver**:
  - Originally, I did `driver.quit()` immediately after finishing scraping, then tried `df.to_csv(...)`. In a couple of runs, if `driver.quit()` raised an unexpected error or invoked some cleanup that deleted my `jobs` list, the script aborted before writing CSV.
  - **Lesson**: Only quit the driver after I’ve safely written the CSV (or I ensure that `driver.quit()` is in a `finally:` block that still preserves the `jobs` list).

- **Hard-coding the Data Folder**
  - My early Selenium attempt tried `df.to_csv("data/techinasia_jobs_selenium.csv")` without creating `data/` first. This crashed with `OSError: Cannot save file into a non-existent directory: 'data'`.
  - **Lesson**: Always verify target directories exist before writing. Wrapping it with `os.makedirs("data", exist_ok=True)` or using `Path(...).mkdir(parents=True, exist_ok=True)` fixes it.

---

## 3. Why Selenium Was Ultimately Stronger for This Use Case

1. **Complete Browser Context & Automatic Token Handling**
   - The Algolia API keys embedded in Tech in Asia’sscripts were clearly ephemeral—possibly regenerating per page load or per session. By using Selenium, I no longer needed to reverse-engineer or manually supply those keys; Chrome’s JavaScript did it for me.
   - Any client-side encryption, or dynamic header generation, is automatically handled.

2. **Rendering & Lazy-Loading**
   - Modern job boards often load new items “on scroll.” A simple `requests.get()` + JSON-parsing approach fails if the site doesn’t expose a stable, documented endpoint for “all jobs.”
   - Selenium automatically executes the same scroll events a real user does. That ensures all items are visible in the DOM, and I can scrape them directly.

3. **Resilience to Minor Markup Changes**
   - If Tech in Asia renamed the Algolia endpoint or added a geolocation check, my direct API approach would break again.
   - However, as long as they preserve the top-level CSS structure (e.g., `article[data-cy="job-result"]`), my scraper keeps working. Even if they changed internal XHR calls, Selenium sees the final rendered page.

4. **Built-in Debugging Tools**
   - Whenever a job card failed to be found by CSS selectors, I simply printed `driver.page_source[:1000]` to inspect the raw HTML.
   - If a script relied on a CAPTCHA or triggered a login redirect, I could instantly spot that in the page source or screenshot—something that is much harder to diagnose from an opaque 403 JSON response.

5. **Flexibility for Future Enhancements**
   - If I want to click on each job to navigate into the detailed description page and scrape additional fields (e.g., responsibilities, apply link), I can extend the Selenium flow easily.
   - Attempting the same with the API would require capturing deeper API calls or loading additional endpoints that may be even more heavily protected.

---

## 4. Comprehensive Lessons Learned & Best Practices

Below is a distilled list of mistakes I made and how I corrected them—valuable points to remember for any future scraping or automation task:

1. **Filename Conflicts**
   - **Mistake**: Named my script `selenium.py`, causing a circular import.
   - **Fix**: Renamed to `selenium_scrapper.py`.

2. **Relying on a Static API Key**
   - **Mistake**: Hard-coded the Algolia API key copied from DevTools. It expired or changed.
   - **Fix**: Switched to Selenium so the browser handles key generation.

3. **Insufficient Debugging Output**
   - **Mistake**: My first `fetch_jobs.py` printed only the final “0 hits” and wrote an empty CSV, leaving me confused.
   - **Fix**: Added `[DEBUG]` prints for request URL, headers, payload, response body. In Selenium, added logs at every step: navigation, wait, extraction, scroll iteration, new items found, errors, and CSV write.

4. **Incorrect “Infinite Scroll” Logic**
   - **Mistake**: Scrolled to bottom but never re-scraped new cards each round—so only initial jobs were collected.
   - **Fix**: After each scroll+pause, re‐queried `find_elements(...)` and appended only new URLs by tracking `seen_links`.

5. **Directory Creation Errors**
   - **Mistake**: Attempting to write to `data/` without ensuring it existed caused an `OSError`.
   - **Fix**: Used `Path(...).mkdir(parents=True, exist_ok=True)` to guarantee `<project_root>/data/` exists before writing.

6. **Overly-Short Wait Times**
   - **Mistake**: Using `WebDriverWait(driver, 5)` triggered frequent `TimeoutException` on slower networks.
   - **Fix**: Increased to 15 seconds to allow JavaScript and network resources to load page content.

7. **Driver Lifecycle Management**
   - **Mistake**: Quitting the driver before writing CSV risked losing the scraped data if a driver cleanup error occurred.
   - **Fix**: Quitting in a `finally:` block only after data was preserved, and logging a message to indicate the driver shutdown.

8. **Missing Exception Granularity**
   - **Mistake**: In early attempts, one missing field (`company` or `location`) in a card caused the entire loop to crash.
   - **Fix**: Wrapped `find_element(...)` calls in a `try/except` inside `extract_job_data_from_card()` so that one bad card logs a warning and is skipped without halting the run.

9. **Hard-coding “Relative Paths”**
   - **Mistake**: Using `"data/techinasia_jobs_selenium.csv"` assumed the script was always run from project root. Running it from `scraper/` wrote to `scraper/data/...` instead.
   - **Fix**: Computed `project_root = Path(__file__).resolve().parent.parent` and used `project_root / "data" / "filename.csv"` to guarantee consistent output location.

10. **No Modular Structure**
    - **Mistake**: Putting all code at top level made it harder to import or test.
    - **Fix**: Refactored into functions (`configure_webdriver()`, `extract_job_data_from_card()`, `scrape_all_jobs()`, `main()`) and used the `if __name__ == "__main__": main()` pattern.

---

## 5. Final “Production‐Ready” Code Highlights

Below is a short excerpt of the final script, showing how I combined best practices:

```python
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 1) Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# 2) Find project root and data directory
def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent

def ensure_data_directory(root: Path) -> Path:
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# 3) Initialize headless Chrome
def configure_webdriver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    logger.debug("Launching headless Chrome")
    return webdriver.Chrome(options=opts)

# 4) Extract job fields with try/except
def extract_job_data(job_card) -> dict:
    try:
        title_elem = job_card.find_element(By.CSS_SELECTOR, "a[data-cy='job-title']")
        company_elem = job_card.find_element(By.CSS_SELECTOR, ".details a[href^='/companies']")
        location_elem = job_card.find_element(By.CSS_SELECTOR, ".details > div:nth-child(3)")
        return {
            "title": title_elem.text.strip(),
            "link": title_elem.get_attribute("href").strip(),
            "company": company_elem.text.strip(),
            "location": location_elem.text.strip(),
        }
    except Exception as e:
        logger.warning(f"Skipping malformed card: {e}")
        return {}

# 5) Main scraping loop (initial load + infinite scroll)
def scrape_all_jobs() -> pd.DataFrame:
    driver = configure_webdriver()
    all_jobs, seen_links = [], set()
    try:
        driver.get(TECH_IN_ASIA_URL)
        # Wait + initial scrape omitted for brevity…
        # Scroll loop:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            cards = driver.find_elements(By.CSS_SELECTOR, JOB_CARD_SELECTOR)
            for card in cards:
                data = extract_job_data(card)
                if data and data["link"] not in seen_links:
                    all_jobs.append(data)
                    seen_links.add(data["link"])
        return pd.DataFrame(all_jobs)
    finally:
        driver.quit()

def main():
    project_root = get_project_root()
    data_dir = ensure_data_directory(project_root)
    df = scrape_all_jobs()
    outfile = data_dir / "techinasia_jobs_selenium.csv"
    df.to_csv(outfile, index=False)
    logger.info(f"Result: {len(df)} jobs → {outfile}")

if __name__ == "__main__":
    main()

	•	Notice the function separation, robust logging, and guarded extraction.
	•	The infinite scroll loop ensures every “lazy-loaded” job card is captured.
	•	The output path is computed relative to the project root.

⸻

6. Concluding Thoughts
	•	Mistakes Are Learning Opportunities: My biggest early mistake was trying to “beat” an API by copying an Algolia key—only to discover that keys expire and site scripts can change payload formats at any time. Recognizing that, and swiftly pivoting to Selenium, saved me hours of continued frustration.
	•	Selenium as a Reliable Fallback: Whenever a site relies heavily on JavaScript, embeds rotating tokens, or otherwise obfuscates its data endpoints, Selenium (or a headless-browser approach) often proves more stable than brittle “XHR replay” tactics.
	•	Importance of Structure & Logging: A few well-placed logger.debug() statements, and a clean function‐based structure, transformed my one-off proof-of-concept into a maintainable script I can reuse, refactor, and extend (e.g., to scrape additional fields or to support other countries/job categories).
	•	Future Extensions:
	1.	Detail-page scraping: After collecting the job card links, navigate into each /jobs/<uuid> page to extract salary details, requirements, and company profiles.
	2.	Scheduled Runs: Incorporate cron or a Python scheduler (e.g., schedule library) to refresh data daily, then compare against yesterday’s data to detect new postings automatically.
	3.	Headless Browser Alternatives: Explore Puppeteer (via pyppeteer) or Playwright for even more control over network traffic, if needed.

By documenting each misstep and explaining how Selenium solved the core issues, this reflection not only illustrates my own growth as a scrapers engineer but also showcases the rationale behind tool choice, best practices in exception handling, directory management, and developer‐friendly logging. When I package this code and reflection into the final PDF submission, readers will clearly see why I arrived at the Selenium solution, how I debugged it, and how I structured it for production readiness.

⸻


