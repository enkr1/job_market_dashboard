#!/usr/bin/env python3
"""
selenium_scrapper.py

A production‐ready Selenium script to scrape all Software Engineer, Full-time jobs in Singapore
from Tech in Asia, saving results to '<project_root>/data/techinasia_jobs_selenium.csv'.

- Uses Python logging to record debug/info/warning messages.
- Scrolls until no new job listings appear.
- Wraps each “job‐card → dict” conversion in a try/except.
- Ensures output is always written to <project_root>/data/, no matter where the script is invoked.
- Includes docstrings and inline comments for clarity.
- Captures `image_url` for each job (company logo) and writes/merges into a *master* CSV, deduplicated by the job’s canonical link.
"""


import sys
import time
import traceback

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from data_processing import cleanup_and_analyse
from utils.constants import INITIAL_WAIT_TIMEOUT, SCROLL_PAUSE_TIME
from utils.enums import URL, CSSSelector
from utils.functions import get_csv_path, get_logger

logger = get_logger(__name__)

# ────────────────────────────────────────────────────────────────────────────────
# CONSTANTS / CONFIGURATION  (delegated to utils.enums)
# ────────────────────────────────────────────────────────────────────────────────
TECH_IN_ASIA_URL = URL.TECH_IN_ASIA.value

# CSS selectors
JOB_CARD_SELECTOR = CSSSelector.JOB_CARD.value
CSS_TITLE_LINK = CSSSelector.TITLE_LINK.value
CSS_COMPANY_LINK = CSSSelector.COMPANY_LINK.value
CSS_LOCATION_DIV = CSSSelector.LOCATION_DIV.value
CSS_AVATAR_IMG = CSSSelector.AVATAR_IMG.value
CSS_COMPENSATION = CSSSelector.COMPENSATION.value
CSS_PUBLISHED_DATE = CSSSelector.PUBLISHED_DATE.value
CSS_METADATA = CSSSelector.METADATA.value


def configure_webdriver() -> webdriver.Chrome:
    """
    Instantiate and return a headless Chrome WebDriver.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # no browser window
    chrome_options.add_argument("--no-sandbox")  # best practice in many Linux envs
    chrome_options.add_argument(
        "--disable-dev-shm-usage"
    )  # avoid /dev/shm issues in containers

    # You can also set a custom user‐agent here if you want to mimic a real browser more closely:
    # chrome_options.add_argument("user-agent=MyCustomAgent/1.0")

    logger.debug("Initializing headless Chrome WebDriver")
    driver = webdriver.Chrome(options=chrome_options)
    # Give the headless browser a realistic viewport; some lazy‑load
    # triggers depend on a non‑zero window height.
    driver.set_window_size(1920, 1080)
    # If Chromedriver isn’t on your PATH, pass executable_path=...
    return driver


def extract_job_data_from_card(job_card) -> dict:
    """
    Given a Selenium WebElement for a single job card, extract title, company, location, link.
    Wraps everything in try/except so one malformed card won’t crash the entire run.
    """
    job_info = {}
    try:
        title_element = job_card.find_element(By.CSS_SELECTOR, CSS_TITLE_LINK)
        JOB_LINK = title_element.get_attribute("href").strip()
        HASED_ID = JOB_LINK.rstrip("/").rsplit("/", 1)[
            -1
        ]  # Deterministic UUID‑based primary key

        job_info["id"] = HASED_ID
        job_info["title"] = title_element.text.strip()
        job_info["company"] = job_card.find_element(
            By.CSS_SELECTOR, CSS_COMPANY_LINK
        ).text.strip()
        job_info["location"] = job_card.find_element(
            By.CSS_SELECTOR, CSS_LOCATION_DIV
        ).text.strip()
        job_info["link"] = JOB_LINK

        # Grab the company logo or job thumbnail (if present)
        try:
            img_element = job_card.find_element(By.CSS_SELECTOR, CSS_AVATAR_IMG)
            img_src = img_element.get_attribute("src") or img_element.get_attribute(
                "data-src"
            )
            job_info["image_url"] = (img_src or "").strip()
        except Exception:
            job_info["image_url"] = ""

        # Compensation / salary text
        try:
            comp_element = job_card.find_element(By.CSS_SELECTOR, CSS_COMPENSATION)
            job_info["compensation"] = comp_element.text.strip()
        except Exception:
            job_info["compensation"] = ""

        # Published date text
        try:
            date_element = job_card.find_element(By.CSS_SELECTOR, CSS_PUBLISHED_DATE)
            job_info["published_date"] = date_element.text.strip()
        except Exception:
            job_info["published_date"] = ""

        # Additional metadata tags (join <li> texts with ",")
        try:
            meta_ul = job_card.find_element(By.CSS_SELECTOR, CSS_METADATA)
            meta_texts = [
                li.text.strip() for li in meta_ul.find_elements(By.TAG_NAME, "li")
            ]
            job_info["metadata"] = ",".join(meta_texts)
        except Exception:
            job_info["metadata"] = ""

        logger.debug(f"Extracted job: {job_info['title']} @ {job_info['company']}")
    except Exception as e:
        # We catch any piece that fails, log a warning, and return an empty dict
        logger.warning(f"Failed to parse a job card: {e}")
        return {}

    return job_info


# ────────────────────────────────────────────────────────────────────────────────
# MAIN SCRAPING LOGIC
# ────────────────────────────────────────────────────────────────────────────────
def scrape_all_jobs() -> pd.DataFrame:
    """
    Launches a headless browser, navigates to the Tech in Asia page, waits for
    initial jobs to load, then scrolls until no new jobs appear. Returns a DataFrame.
    """
    driver = configure_webdriver()
    all_jobs = []  # Accumulate job‐dicts here
    seen_ids = set()  # Keep track of which job IDs we've already scraped

    try:
        logger.info(f"Navigating to {TECH_IN_ASIA_URL}")
        driver.get(TECH_IN_ASIA_URL)

        # 1) Wait for the first batch of job cards to appear
        logger.debug(
            f"Waiting up to {INITIAL_WAIT_TIMEOUT}s for initial job listings..."
        )
        wait = WebDriverWait(driver, INITIAL_WAIT_TIMEOUT)
        initial_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, JOB_CARD_SELECTOR))
        )
        logger.info(f"Initial load: found {len(initial_cards)} job cards")

        # 2) Scrape whatever's already on screen
        for card in initial_cards:
            data = extract_job_data_from_card(card)
            if data and data.get("id") not in seen_ids:
                all_jobs.append(data)
                seen_ids.add(data["id"])

        # 3) Scroll to the bottom repeatedly until no new cards are added.
        #
        # Strategy:
        #   • Grab the current document.body.scrollHeight.
        #   • Scroll to the very bottom.
        #   • Wait a few seconds for network requests / DOM mutations.
        #   • Count job cards; if the count grows, scrape the new ones and repeat.
        #   • If the DOM height AND the job‑card count both stay constant for
        #     `MAX_NO_GROWTH_ROUNDS` consecutive rounds, assume we’re done.
        previous_height = driver.execute_script("return document.body.scrollHeight")
        previous_count = len(seen_ids)
        no_growth_rounds = 0
        MAX_NO_GROWTH_ROUNDS = 2

        while no_growth_rounds < MAX_NO_GROWTH_ROUNDS:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.debug("Scrolled to bottom; waiting for potential new content…")
            time.sleep(SCROLL_PAUSE_TIME)

            # Recompute height and card count
            new_height = driver.execute_script("return document.body.scrollHeight")
            current_cards = driver.find_elements(By.CSS_SELECTOR, JOB_CARD_SELECTOR)
            current_count = len(current_cards)

            # Extract any *new* cards this round
            new_jobs_this_round = 0
            for card in current_cards:
                data = extract_job_data_from_card(card)

                if data and data.get("id") not in seen_ids:
                    all_jobs.append(data)
                    seen_ids.add(data["id"])
                    new_jobs_this_round += 1

            if new_height == previous_height and current_count == previous_count:
                no_growth_rounds += 1
                logger.debug(
                    f"No page growth detected "
                    f"({no_growth_rounds}/{MAX_NO_GROWTH_ROUNDS})"
                )
            else:
                logger.info(
                    f"Page grew → height: {previous_height}->{new_height}, "
                    f"cards: {previous_count}->{current_count}, "
                    f"new jobs added: {new_jobs_this_round}"
                )
                previous_height = new_height
                previous_count = current_count
                no_growth_rounds = 0

        # 4) Once scrolling is done, convert to DataFrame
        if not all_jobs:
            logger.warning("No jobs were scraped; returning an empty DataFrame.")
            return pd.DataFrame()

        if len(all_jobs) <= 100:
            logger.warning("Collected fewer than 100 jobs – consider widening filters")

        logger.info(f"Total jobs collected: {len(all_jobs)}")
        df = pd.DataFrame(all_jobs)
        return df

    except Exception as run_e:
        # If anything major goes wrong, log the full traceback and rethrow
        logger.error(f"Exception during scraping: {run_e}")
        traceback.print_exc()
        # Optionally, we could save a “partial result” here, or re‐raise to abort entirely
        raise

    finally:
        # Always quit the browser
        logger.debug("Quitting WebDriver")
        driver.quit()


def main():
    """
    The main entry point. Calls scrape_all_jobs(), then writes to CSV under <project_root>/data/.
    """
    # 1) Figure out project root, ensure <project_root>/data/ exists
    output_path = get_csv_path()

    try:
        # 2) Run the scraper
        df_jobs = scrape_all_jobs()

        # ── UPSERT into master CSV ───────────────────────────────────────────
        if output_path.exists() and not output_path.is_dir():
            try:
                existing_df = pd.read_csv(output_path)
                combined_df = pd.concat([existing_df, df_jobs], ignore_index=True)
                # Use the UUID‑based 'id' column as primary key for deduplication
                combined_df.drop_duplicates(subset="id", inplace=True)
                df_jobs = combined_df
                logger.info(
                    f"Upsert complete → {len(existing_df)} existing rows + "
                    f"{len(df_jobs) - len(existing_df)} new or updated rows "
                    f"= {len(df_jobs)} total"
                )
            except Exception as merge_e:
                logger.warning(f"Could not merge with existing CSV: {merge_e}")

        # 3) Save to CSV
        if not df_jobs.empty:
            df_jobs.to_csv(output_path, index=False)
            logger.info(f"CSV written successfully to: {output_path}")
        else:
            # Even if it’s empty, write an empty CSV (or decide not to write at all)
            df_jobs.to_csv(output_path, index=False)
            logger.warning(f"Wrote an empty CSV to {output_path} (no jobs found)")

        cleanup_and_analyse(df_jobs)  # produces charts + clean CSV

    except Exception as e:
        logger.error(f"Aborting: could not complete scraping → {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
