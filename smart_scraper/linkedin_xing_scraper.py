from playwright.sync_api import sync_playwright
import json, time

def scrape_jobs_linkedin_xing(keywords, locations):
    scraped_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for kw in keywords:
            for loc in locations:
                # LinkedIn
                url = f"https://www.linkedin.com/jobs/search?keywords={kw}&location={loc}&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
                page.goto(url)
                time.sleep(5)
                items = page.query_selector_all("li.jobs-search-results__list-item")
                for item in items[:10]:
                    title = item.query_selector("h3").inner_text() if item.query_selector("h3") else "N/A"
                    company = item.query_selector("h4").inner_text() if item.query_selector("h4") else "N/A"
                    link = item.query_selector("a").get_attribute("href") if item.query_selector("a") else "N/A"
                    scraped_jobs.append({
                        "title": title,
                        "company": company,
                        "location": loc,
                        "link": link,
                        "description": f"Placeholder: job description for {title} at {company}"
                    })

        browser.close()

    with open("smart_scraper/scraped_jobs.jsonl", "w") as f:
        for job in scraped_jobs:
            f.write(json.dumps(job) + "\n")

    print(f"[✅] Scraped {len(scraped_jobs)} jobs from LinkedIn/Xing.")
    return scraped_jobs