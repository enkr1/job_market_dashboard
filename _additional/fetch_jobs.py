import requests
import pandas as pd

# ——————————————————————————————————————————————
# 1. The exact POST URL (copy from DevTools → Network → XHR → Headers → “Request URL”)
POST_URL = (
    "https://219wx3mpv4-dsn.algolia.net/1/indexes/*/queries?"
    "x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.30.0%3BJS%20Helper%202.26.1&"
    "x-algolia-application-id=219WX3MPV4&"
    "x-algolia-api-key=b528008a75dc1c4402bfe0d8db8b3f8e"
)

# ——————————————————————————————————————————————
# 2. The request headers that the browser sent (copy from DevTools → Network → XHR → Headers → “Request Headers”).
#    At minimum, Algolia requires:
#       • Content-Type: application/json; charset=UTF-8
#       • X-Algolia-Application-Id
#       • X-Algolia-API-Key
headers = {
    "Content-Type": "application/json",
    "X-Algolia-Application-Id": "219WX3MPV4",
    "X-Algolia-API-Key": "b528008a75dc1c4402bfe0d8db8b3f8e",
    "X-Algolia-Agent": "Algolia for vanilla JavaScript 3.30.0; JS Helper 2.26.1",
    "Origin": "https://www.techinasia.com",
    "Referer": "https://www.techinasia.com/jobs/search?country_name[]=Singapore&job_category_name[]=Software%20Engineer&job_type[]=Full-time",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "accept": "application/json",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

# ——————————————————————————————————————————————
# 3. The JSON payload (copy exactly from DevTools → Network → XHR → Payload).
#    We’ll use “page=0” as the starting page. To fetch page N, we’ll replace “page=0” with “page=N”.
payload_template = {
    "requests": [
        {
            "indexName": "job_postings",
            "params": (
                "query=&hitsPerPage=20&maxValuesPerFacet=1000&page=0&"
                "facets=%5B%22*%22%2C%22city.work_country_name%22%2C%22"
                "position.name%22%2C%22industries.vertical_name%22%2C"
                "%22experience%22%2C%22job_type.name%22%2C%22is_salary_visible%22%2C"
                "%22has_equity%22%2C%22currency.currency_code%22%2C"
                "%22salary_min%22%2C%22taxonomies.slug%22%5D&"
                "tagFilters=%5B%5B%22job_type.name%3AFull-time%22%5D%2C"
                "%5B%22position.name%3ASoftware%20Engineer%22%5D%2C"
                "%5B%22city.work_country_name%3ASingapore%22%5D%5D"
            ),
        }
    ]
}

# ——————————————————————————————————————————————
def fetch_page(page_number: int) -> dict:
    import json
    payload = {
        "requests": [
            {
                "indexName": payload_template["requests"][0]["indexName"],
                "params": payload_template["requests"][0]["params"].replace(
                    "page=0", f"page={page_number}"
                ),
            }
        ]
    }

    print(f"\n==== DEBUG: FETCHING PAGE {page_number} ====")
    print("Request Headers:")
    print(json.dumps(headers, indent=2))
    print("Request Payload:")
    print(json.dumps(payload, indent=2))

    response = requests.post(POST_URL, headers=headers, json=payload)
    print(f"HTTP Status: {response.status_code}")
    print(f"Response Text (first 1000 chars):\n{response.text[:1000]}")

    try:
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

    data = response.json()
    if "results" not in data or len(data["results"]) == 0:
        print("[WARNING] No 'results' found in response!")
    else:
        print(f"[DEBUG] Number of hits: {len(data['results'][0]['hits'])}")

    return data

if __name__ == "__main__":
    # —————————————————————————
    # (A) Fetch page 0 to see how many “nbPages” exist
    result_page0 = fetch_page(0)
    hits0 = result_page0["results"][0]["hits"]
    nb_pages = result_page0["results"][0]["nbPages"]
    print(f"Page 0 returned {len(hits0)} hits. Total pages: {nb_pages}.\n")

    # Print out the first 20 hits from page 0:
    print("=== Page 0 “hits” ===")
    for job in hits0:
        title = job.get("title", "(no title)")
        company = job.get("company", {}).get("name", "(no company)")
        exp = job.get("experience", "(no experience)")
        link = job.get("external_link", "")
        print(f" • {title!r} @ {company!r} (exp={exp}) → {link}")
    print("\n")

    # —————————————————————————
    # (B) Loop through all pages (0 .. nb_pages−1), collect every job
    all_jobs = []
    for pg in range(nb_pages):
        page_json = fetch_page(pg)
        hits = page_json["results"][0]["hits"]
        for h in hits:
            all_jobs.append(
                {
                    "id": h.get("id"),
                    "title": h.get("title"),
                    "company": h.get("company", {}).get("name"),
                    "experience": h.get("experience"),
                    "salary_min": h.get("salary_min"),
                    "salary_max": h.get("salary_max"),
                    "external_link": h.get("external_link"),
                }
            )
        print(f" Fetched page {pg} ({len(hits)} hits).")

    print(f"\n✅ Collected {len(all_jobs)} job postings across all {nb_pages} pages.\n")

    # —————————————————————————
    # (C) Save to CSV (or JSON if you prefer)
    df = pd.DataFrame(all_jobs)
    df.to_csv("techinasia_sg_sw_engineer_fulltime.csv", index=False)
    print("CSV written to techinasia_sg_sw_engineer_fulltime.csv")
