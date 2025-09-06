# extensions/resume_retrain.py

import json
from datetime import datetime
from pathlib import Path

FEEDBACK_LOG = Path("resumes/feedback_log.jsonl")

def record_outcome(company, status, note=""):
    entry = {
        "company": company,
        "status": status,
        "note": note,
        "timestamp": datetime.utcnow().isoformat()
    }
    with open(FEEDBACK_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

