"""Basic keyword + semantic matcher used in the auto-apply pipeline.

The original project only performed a naive keyword lookup which returned
placeholder job entries.  For the end-to-end demo we instead scrape a small
set of example jobs and score them against the candidate's resume using the
lightweight :func:`jobbert_score` utility.  This keeps the pipeline fully
offline while providing deterministic behaviour for the unit tests.

The function loads job preferences from ``config/user_profile.yaml`` when no
explicit titles/locations are supplied.  It then pulls demo jobs from
``smart_scraper.job_scraper`` and returns the top matches sorted by score.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List

import yaml

from ml_models.jobbert_ranker import jobbert_score
from smart_scraper.job_scraper import scrape_jobs_live


def _load_preferences(titles: Iterable[str] | None,
                       preferences: Dict | None) -> tuple[List[str], List[str]]:
    """Helper for loading job titles and preferred locations."""
    if titles is None or preferences is None:
        with open("config/user_profile.yaml", "r", encoding="utf-8") as f:
            profile = yaml.safe_load(f)
        titles = profile.get("job_preferences", {}).get("titles", [])
        locations = profile.get("job_preferences", {}).get("locations", [])
    else:
        titles = list(titles)
        locations = preferences.get("locations", [])
    return titles, list(locations)


def _location_match(job_loc: str, locations: Iterable[str]) -> bool:
    job_loc = job_loc.lower()
    return any(loc.lower() in job_loc or job_loc in loc.lower() for loc in locations)


def match_jobs_to_resume(resume_text: str,
                         titles: Iterable[str] | None = None,
                         preferences: Dict | None = None,
                         top_n: int = 5) -> List[Dict]:
    titles, locations = _load_preferences(titles, preferences)

    resume_lower = resume_text.lower()

    # Pull demo jobs and filter them by preferences (allow fuzzy location match)
    jobs = [
        job
        for job in scrape_jobs_live()
        if (not titles or any(t.lower() in job["title"].lower() for t in titles))
        and (not locations or _location_match(job["location"], locations))
    ]

    matches: List[Dict] = []
    for job in jobs:
        score = jobbert_score(resume_lower, job.get("description", ""))
        matches.append({**job, "score": score})

    matches.sort(key=lambda j: j["score"], reverse=True)
    return matches[:top_n]

