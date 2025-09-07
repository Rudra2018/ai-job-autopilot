import json
from pathlib import Path

def scrape_jobs_live():
    jobs = [
        {
            "title": "Cloud Security Engineer",
            "company": "Google",
            "description": "Work with GCP IAM, network security, and vulnerability management.",
            "location": "Munich",
            "url": "https://careers.google.com/jobs/cloud-sec",
        },
        {
            "title": "SOC Analyst",
            "company": "NVISO Germany",
            "description": "Monitor alerts, triage incidents, and respond to threats using SIEM/SOAR.",
            "location": "Remote (EU)",
            "url": "https://nviso.eu/careers/soc-analyst",
        },
    ]
    Path("smart_scraper").mkdir(exist_ok=True)
    with open("smart_scraper/scraped_jobs.jsonl", "w", encoding="utf-8") as f:
        for job in jobs:
            f.write(json.dumps(job) + "\n")
    return jobs