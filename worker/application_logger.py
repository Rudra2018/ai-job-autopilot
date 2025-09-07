"""Utility for logging job application attempts.

Writes each application attempt to ``dashboard/application_log.jsonl`` so
it can be visualised by the Streamlit dashboard.  Each entry contains the
job metadata, application status and optional recruiter message.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Optional

LOG_PATH = Path("dashboard/application_log.jsonl")


def log_application(
    job: Dict, status: str, recruiter_msg: Optional[str] = None
) -> None:
    """Append an application attempt to the log file.

    Parameters
    ----------
    job: mapping with at least ``title`` and ``company`` keys
    status: short string describing the outcome (e.g. ``"applied"`` or
        ``"failed"``)
    recruiter_msg: optional message sent to the recruiter
    """
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "url": job.get("url"),
        "status": status,
        "recruiter_msg": recruiter_msg,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_application_log(limit: Optional[int] = None) -> Iterable[Dict]:
    """Return entries from the application log.

    Parameters
    ----------
    limit: optionally limit the number of returned entries
    """
    if not LOG_PATH.exists():
        return []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:] if limit else f.readlines()
    return [json.loads(line) for line in lines]
