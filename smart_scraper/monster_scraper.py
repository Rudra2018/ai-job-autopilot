"""Simplified Monster scraper returning static results."""

from typing import List, Dict


def scrape_jobs_monster(keywords: List[str], locations: List[str]) -> List[Dict]:
    jobs = []
    for kw in keywords:
        for loc in locations:
            jobs.append(
                {
                    "title": f"Senior {kw.title()}",
                    "company": "Monster Worldwide",
                    "location": loc,
                    "description": f"Mock {kw} posting in {loc}",
                    "link": "https://monster.example/job",
                    "platform": "monster",
                }
            )
    return jobs
