# ai_job_autopilot/extensions/resume_auto_apply.py

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import yaml
from pathlib import Path

# Ensure project root is on the import path when executed as a script
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extensions.parser import parse_resume
from worker.linkedin_xing_auto_connect import send_connection_requests
from worker.keyword_matcher import match_jobs_to_resume
from worker.recruiter_message_generator import generate_message
from worker.playwright_apply import simulate_job_apply

CONFIG_PATH = Path("config/user_profile.yaml")

if not CONFIG_PATH.exists():
    raise FileNotFoundError("user_profile.yaml not found. Please create it in config/")

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

resume_path = config.get("resume_path")
resume_text = parse_resume(resume_path)

# Find best matching jobs using the helper in ``worker.keyword_matcher``.  The
# function automatically loads title/location preferences from the same
# ``user_profile.yaml`` when not provided explicitly.
matched_jobs = match_jobs_to_resume(resume_text)

if not matched_jobs:
    print("\n[🚫] No strong job matches found for the resume.")
    exit()

print(f"\n[🚀] Auto-applying to {len(matched_jobs)} matched jobs...")
for job in matched_jobs:
    print(
        f"  → {job['title']} @ {job['company']} ({job['location']}) — {job['score']}%"
    )
    recruiter_msg = generate_message(config["name"], job, recipient_name="Hiring Manager")
    simulate_job_apply(job, config, recruiter_msg)

send_connection_requests()
print("\n[✅] Auto-apply pipeline finished.")

