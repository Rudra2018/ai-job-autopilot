"""Stubbed LinkedIn scraper.

The real project uses Playwright to interact with LinkedIn's UI. For test
purposes we expose a deterministic function that mimics filtering by
*Easy Apply* jobs posted in the last ``max_posted_hours`` hours.
"""

from typing import Iterable, List


def scrape_jobs_linkedin(
    keywords: Iterable[str],
    locations: Iterable[str],
    easy_apply_only: bool = True,
    max_posted_hours: int = 24,
) -> List[dict]:
    """Return sample LinkedIn jobs filtered by Easy Apply and freshness."""

    sample_jobs = [
        {
            "title": "Cloud Security Engineer",
            "company": "Siemens AG",
            "location": "Berlin",
            "description": (
                "We are seeking a skilled Cloud Security Engineer to join our team. "
                "Experience with AWS, GCP, or Azure required. ISO 27001 knowledge is a plus."
            ),
            "link": "https://jobs.siemens.com/security-engineer-berlin",
            "platform": "linkedin",
            "easy_apply": True,
            "posted_hours": 12,
        },
        {
            "title": "Security Engineer",
            "company": "NVISO",
            "location": "Remote",
            "description": (
                "Work on cutting-edge security research and implementation across APIs, "
                "containers, and cloud environments."
            ),
            "link": "https://nviso.eu/careers/security-engineer",
            "platform": "linkedin",
            "easy_apply": False,
            "posted_hours": 30,
        },
    ]

    def _eligible(job: dict) -> bool:
        return (
            (not easy_apply_only or job.get("easy_apply"))
            and job.get("posted_hours", 999) <= max_posted_hours
        )

    return [job for job in sample_jobs if _eligible(job)]

