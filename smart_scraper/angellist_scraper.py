"""Simplified AngelList/Wellfound scraper returning static startup jobs."""

from typing import List, Dict


def scrape_jobs_angellist(keywords: List[str], locations: List[str]) -> List[Dict]:
    jobs = []
    for kw in keywords:
        for loc in locations:
            jobs.append(
                {
                    "title": f"{kw.title()} at Stealth Startup",
                    "company": "AngelList",
                    "location": loc,
                    "description": f"Startup {kw} role in {loc}",
                    "link": "https://angellist.example/job",
                    "platform": "angellist",
                }
            )
    return jobs
