"""Simplified RemoteOK scraper returning static remote jobs."""

from typing import List, Dict


def scrape_jobs_remoteok(keywords: List[str], locations: List[str]) -> List[Dict]:
    jobs = []
    for kw in keywords:
        jobs.append(
            {
                "title": f"{kw.title()} (Remote)",
                "company": "RemoteOK",
                "location": "Remote",
                "description": f"Remote {kw} position",
                "link": "https://remoteok.example/job",
                "platform": "remoteok",
            }
        )
    return jobs
