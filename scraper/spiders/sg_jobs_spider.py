# job_market_dashboard/scraper/scraper/spiders/sg_jobs_spider.py

import scrapy
from scraper.items import JobItem

class SGJobsAPIJsonSpider(scrapy.Spider):
    name = "sg_jobs_api"
    allowed_domains = ["techinasia.com"]

    def start_requests(self):
        # Start at page 1 of the JSON API
        url = (
            "https://www.techinasia.com/jobs/api/search?"
            "country_name[]=Singapore&"
            "job_category_name[]=Software%20Engineer&"
            "job_type[]=Full-time&page=1"
        )
        yield scrapy.Request(url=url, callback=self.parse_json)

    def parse_json(self, response):
        data = response.json()  # parse the JSON response
        for job_data in data.get("data", []):
            item = JobItem()
            item['title'] = job_data.get("title", "").strip()
            item['company'] = job_data.get("company", "").strip()
            item['location'] = job_data.get("location", "").strip()
            item['salary'] = job_data.get("compensation", "").strip()

            # Combine category, sector, and type into a list:
            metas = []
            if job_data.get("category"):
                metas.append(job_data["category"].strip())
            if job_data.get("sector"):
                metas.append(job_data["sector"].strip())
            if job_data.get("type"):
                metas.append(job_data["type"].strip())
            item['additional_meta'] = metas

            item['posted_date'] = job_data.get("posted_at", "").strip()

            # JSON gives a relative URL; join it:
            item['application_url'] = response.urljoin(job_data.get("url", ""))

            yield item

        # Pagination logic
        pagination = data.get("pagination", {})
        current_page = pagination.get("page")
        has_next = pagination.get("has_next", False)
        if has_next:
            next_page = current_page + 1
            next_url = (
                "https://www.techinasia.com/jobs/api/search?"
                f"country_name[]=Singapore&"
                f"job_category_name[]=Software%20Engineer&"
                f"job_type[]=Full-time&page={next_page}"
            )
            yield scrapy.Request(url=next_url, callback=self.parse_json)
