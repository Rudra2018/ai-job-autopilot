"""Simplified Glassdoor scraper returning static results."""

from typing import List, Dict


def scrape_jobs_glassdoor(keywords: List[str], locations: List[str]) -> List[Dict]:
    jobs = []
    for kw in keywords:
        for loc in locations:
            jobs.append(
                {
                    "title": f"{kw.title()} Specialist",
                    "company": "Glassdoor Inc",
                    "location": loc,
                    "description": f"Example {kw} job in {loc}",
                    "link": "https://glassdoor.example/job",
                    "platform": "glassdoor",
                }
            )
    return jobs
