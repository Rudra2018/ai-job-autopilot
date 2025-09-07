"""AI Job Autopilot Launcher.

This script glues the individual modules together to provide an end-to-end
demo of the project.  It deliberately avoids heavy ML dependencies by using
the lightweight scoring utilities shipped with the repository.
"""

import time
from pathlib import Path

from extensions.parser import parse_resume
from worker.keyword_matcher import match_jobs_to_resume
from worker.playwright_apply import auto_detect_and_apply
from worker.recruiter_message_generator import generate_message
from worker.linkedin_xing_auto_connect import send_connection_requests
from worker.application_logger import log_application

RESUME_PATH = "config/resume.pdf"


def apply_with_retry(job, max_retries=3):
    """Try applying to a job. If CAPTCHA or site issues, retry."""
    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"🔁 Attempt {attempt}: Applying to {job['title']} @ {job['company']}"
            )
            auto_detect_and_apply(job)
            return True
        except Exception as e:  # pragma: no cover - best effort logging
            print(f"[❌] Attempt {attempt} failed: {e}")
            time.sleep(2)
    print(f"[🚫] Failed to apply after {max_retries} attempts.")
    return False


def main():
    print("📄 Parsing resume...")
    resume_text = parse_resume(RESUME_PATH)

    print("🧠 Matching to scraped jobs...")
    matches = match_jobs_to_resume(resume_text)

    print("\n🚀 Top AI-matched jobs:")
    for job in matches:
        print(
            f"  → {job['title']} @ {job['company']} ({job['location']}) — {job['score']}%"
        )

    print("\n✅ Applying to top matches...")
    for job in matches:
        msg = generate_message("Candidate", job, recipient_name="Hiring Team")
        applied = apply_with_retry(job)
        status = "applied" if applied else "failed"
        log_application(job, status, recruiter_msg=msg)
        print(f"""💌 Recruiter Message:{msg}""")

    send_connection_requests()


if __name__ == "__main__":
    main()

