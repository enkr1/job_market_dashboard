# Take Home Test from Coupang | By PANG JING HUI | Web Scraping Tech in Asia Job Board | Project Report



## Project Goal and Choice of Platform

The goal of this project was to demonstrate end-to-end web scraping and data analysis by building a dataset from scratch. I chose the Tech in Asia job board because it focuses on tech startup jobs in Asia (especially Singapore) and its dynamic content made it a suitably challenging target. Plus, I have a personal interest in regional tech career trends, which kept me motivated throughout the project.



## Design and Tech Stack Decisions

**Stack:** I used Python for its robust scraping and data libraries. I opted for **Selenium** (headless Chrome) over Scrapy/Requests because Tech in Asia’s job list is loaded by JavaScript. Selenium let me render and interact with the site like a real user, which was necessary to retrieve all jobs from the infinite-scroll interface. Scrapy would have been faster, but without JS support it would have missed most data.

**Data format:** I exported the results to **CSV**. The data is tabular (each job with key fields like job title, company title, hash tags (metadatas), etc.), so, CSV made it easy to load into pandas or Excel for analysis. I considered JSON for this project as the data structure was flat, CSV offered simplicity and readability for this use case.



## Implementation Workflow
0. **Verify:** I went through the site's robots.txt (https://www.techinasia.com/robots.txt) to verify and understand whether I am allowed to scrape the site.
1. **Scraping:** Using Selenium, I opened the Singapore jobs page and automated scrolling to load all available listings (239 jobs in total). I inserted short delays between scrolls to allow content to render and to avoid overwhelming the server. For each job card, I extracted the title, company, location, post date, and salary range (when available) directly from the listing without needing to click into each detail page.
2. **Data Sanitising:** I then cleaned and structured the data. For example, I parsed compensation column text into numeric `salary_min`/`salary_max` values, converted relative dates (e.g. “3 days ago”) into actual dates, and split combined tags into separate fields (job function vs. company industry). Location data was uniform (“Singapore”), so minimal cleaning was needed there. Missing values (like salary for most jobs) were left as null, to be handled in analysis.
3. **Analysis:** Finally, I used pandas to explore and analyse the data. I computed frequencies (e.g. job counts by category and company) and summary statistics (like salary ranges). I also created a few quick plots (such as a bar chart of jobs by category) to visualise the trends. Given time constraints, I prioritised extracting key insights over exhaustive visualization, using charts mainly to double-check the patterns I spotted. Graphs that came into my mind that could be interesting to look at such as: Jobs Per Day (Last 30 Days), Salary Distribution (SGD), and Top 10 Companies by Postings on this scraped website.



## Challenges and Solutions

* **Dynamic content loading:**
  * *Situation:* A simple GET request returned no job data because the site’s content is loaded via JavaScript.
  * *Task:* Find a way to scrape a JS-dependent page.
  * *Action:* I used Selenium to load the page in a real browser context and added scrolling with waits to fetch all listings.
  * *Result:* Successfully retrieved all job posts.
  * *Learning:* Assessing a site’s structure early is crucial; identifying the need for a browser-based approach upfront saved time.
* **Missing salary info:** Many postings did not display salary information (only \~10% showed a range).
  * *Situation:* This limited any salary analysis.
  * *Task:* Capture available salary data and handle the missing values.
  * *Action:* I recorded salaries when present and left them blank when absent, noting this limitation. I considered logging in (in case salaries were visible to logged-in users) but skipped it due to time and potential TOS issues.
  * *Result:* The dataset includes the salary data that was public, with missing values clearly indicated.
  * *Learning:* In real-world scraping, not all data will be available; it’s important to handle gaps gracefully and be transparent about them.
* **Performance and politeness:** Running a real browser for scraping is slower and heavier than direct requests.
  * *Situation:* I needed to avoid long runtimes and reduce server load.
  * *Task:* Optimise the scraping process for efficiency and low impact.
  * *Action:* I ran the browser in headless mode and throttled the scraping speed with deliberate pauses.
  * *Result:* The scrape finished without any bans or crashes, just taking a bit more time.
  * *Learning:* Politeness in scraping (rate limiting, etc.) goes a long way to ensure the process completes reliably.

## Data Insights and Findings

Even with some missing fields, the dataset revealed interesting trends in the tech job market:

* **Popular roles:** The most common job function was Software Engineer, which made up about one-third of the postings (79 out of 239). The next largest categories were Sales & Business Development (34 jobs) and Project/Product Management (28), followed by Data & Analytics (20) and Marketing & PR (19). This shows strong demand for both core technical talent and roles that drive product and revenue.
* **Top employers:** Certain companies were hiring aggressively. Notably, **OpenAI had 15 openings**, the most of any company – highlighting the surge in AI-related roles. Other active employers included OKX and Airwallex (\~6 each), as well as startups like Rida.ai and MicroSec with multiple listings. It was insightful to see both major global players and local startups using the platform.
* **Salary ranges:** Only about 25 jobs listed salaries, and those ranges varied widely. At the lower end, a finance associate role was around **SGD 2.5k–3.2k** per month, whereas a senior sales role at Grafana Labs went up to **SGD 400k** (likely annual). The few data points suggest a median around SGD 6k–10k for mid-level roles. Due to the scarcity of salary data, any broad conclusions on pay would be unreliable, so I focused on qualitative observations like the huge range between junior and senior role salaries.
* **Miscellaneous:** All jobs were located in Singapore (as expected from the site filter), and only 2 out of 239 explicitly mentioned a remote option. The postings captured were from May 2025 (about one month’s span), so the dataset is a snapshot in time rather than a full-year survey.

## Conclusion: Reflections & Learnings

I am genuinely thankful for this opportunity to learn by doing – a philosophy that has defined my career so far. Whether it was proving myself as an intern and earning a full-time role within two weeks, or navigating new technical domains, I have always believed that learning happens best through real-world execution. This project was a powerful reminder of that.

Designing and building the end-to-end scraping and analysis pipeline brought me back to the excitement I felt during my MIT IDSS Machine Learning certification. The process of conceiving the idea, architecting the scraping logic, handling messy real-world data, and finally visualising insights was both a challenge and a refreshment. It reinforced many lessons from my academic training, but—perhaps more importantly—highlighted areas that only surface through hands-on practice.

I want to be candid about the areas where, in a full production environment, there is room for improvement. While my solution worked robustly for the given site and use case, I could have implemented some strategies for unexpected failures, such as dynamic site layout changes, URL path updates, or anti-scraping countermeasures. In a real-world project, I would always adopt a more defensive programming mindset—leveraging Test-Driven Development (TDD), writing modular code, and setting up proactive monitoring and alerting. I’m also a strong advocate for clear/better logging for monitoring system, exception handling, and graceful fallbacks, and I recognise these are necessary next steps to elevate this prototype to a true production-grade solution.

Despite these caveats, I believe I have demonstrated not just technical competency but the critical mindset Coupang seeks: the ability to break down ambiguous challenges, iterate quickly, and communicate findings transparently. Each challenge I faced—from choosing the right tool, to wrangling data, to acknowledging where I could have gone further—was an opportunity to reflect and grow.

If there’s one takeaway from this experience, it’s a renewed appreciation for continuous improvement and the humility to know that there is always more to learn. Thank you for this chance to showcase my skills in a hands-on way; it has been genuinely rewarding, and I am eager to bring this spirit of curiosity and resilience to Coupang.
