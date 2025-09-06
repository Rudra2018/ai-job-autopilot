import json
from pathlib import Path

def scrape_jobs_live():
    jobs = [
        {
            "title": "Cloud Security Engineer",
            "company": "Google",
            "description": "Work with GCP IAM, network security, and vulnerability management.",
            "location": "Munich",
            "link": "https://careers.google.com/jobs/cloud-sec"
        },
        {
            "title": "SOC Analyst",
            "company": "NVISO Germany",
            "description": "Monitor alerts, triage incidents, and respond to threats using SIEM/SOAR.",
            "location": "Remote (EU)",
            "link": "https://nviso.eu/careers/soc-analyst"
        }
    ]
    Path("smart_scraper").mkdir(exist_ok=True)
    with open("smart_scraper/scraped_jobs.jsonl", "w") as f:
        for job in jobs:
            f.write(json.dumps(job) + "\n")
    return jobs