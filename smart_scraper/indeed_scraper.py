"""Simplified Indeed scraper for demo and testing purposes.

The real implementation would use Playwright or an API to fetch jobs.
Here we simply return a static list so unit tests remain deterministic."""

from typing import List, Dict


def scrape_jobs_indeed(keywords: List[str], locations: List[str]) -> List[Dict]:
    jobs = []
    for kw in keywords:
        for loc in locations:
            jobs.append(
                {
                    "title": f"{kw.title()} Engineer",
                    "company": "Indeed Corp",
                    "location": loc,
                    "description": f"Sample {kw} role for {loc}",
                    "link": "https://indeed.example/job",
                    "platform": "indeed",
                }
            )
    return jobs
