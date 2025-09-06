
import json
from datetime import datetime
from pathlib import Path

RETRAIN_LOG = Path("data/resume_feedback_log.jsonl")
RETRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)

def record_outcome(job, outcome: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "title": job.get("title"),
        "company": job.get("company"),
        "score": job.get("score"),
        "outcome": outcome
    }
    with open(RETRAIN_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[📥] Outcome recorded for {job['title']} → {outcome}")
