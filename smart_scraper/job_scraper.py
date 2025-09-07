"""Aggregate job scrapers for multiple platforms.

Each scraper returns a list of job dictionaries with a ``platform`` field.
The live scrapers would use Playwright or official APIs; here we keep things
simple and deterministic for tests."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .linkedin_scraper import scrape_jobs_linkedin
from .indeed_scraper import scrape_jobs_indeed
from .glassdoor_scraper import scrape_jobs_glassdoor
from .monster_scraper import scrape_jobs_monster
from .remoteok_scraper import scrape_jobs_remoteok
from .angellist_scraper import scrape_jobs_angellist

SCRAPERS = [
    scrape_jobs_linkedin,
    scrape_jobs_indeed,
    scrape_jobs_glassdoor,
    scrape_jobs_monster,
    scrape_jobs_remoteok,
    scrape_jobs_angellist,
]


def scrape_jobs_live(
    keywords: Optional[List[str]] = None,
    locations: Optional[List[str]] = None,
) -> List[Dict]:
    """Run all configured scrapers and persist results to JSONL."""
    keywords = keywords or ["engineer"]
    locations = locations or ["Remote"]

    jobs: List[Dict] = []
    for scraper in SCRAPERS:
        try:
            jobs.extend(scraper(keywords, locations))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[⚠️] {scraper.__name__} failed: {exc}")

    Path("smart_scraper").mkdir(exist_ok=True)
    with open("smart_scraper/scraped_jobs.jsonl", "w", encoding="utf-8") as f:
        for job in jobs:
            f.write(json.dumps(job) + "\n")
    return jobs
