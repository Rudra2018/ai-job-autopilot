"""
AI Job Autopilot Launcher — wires everything together:
- Parses resume
- Scrapes jobs
- Embeds resume + jobs (JobBERT)
- Applies to top matches
- Sends recruiter messages
- Real job site automation via Playwright
"""

from sentence_transformers import SentenceTransformer, util
from extensions.parser import parse_resume
from smart_scraper.linkedin_scraper import scrape_jobs_linkedin
from worker.playwright_apply import auto_detect_and_apply
from worker.recruiter_message_generator import generate_message
from worker.linkedin_xing_auto_connect import send_connection_requests
from pathlib import Path
import json
import os
import time

RESUME_PATH = "resumes/resume.pdf"
MODEL_PATH = "ml_models/jobbert_v3"
SCRAPED_JOBS_PATH = "smart_scraper/scraped_jobs.jsonl"


def load_jobs():
    if Path(SCRAPED_JOBS_PATH).exists():
        return [json.loads(line) for line in open(SCRAPED_JOBS_PATH)]
    else:
        print("🔎 Scraping jobs from LinkedIn...")
        jobs = scrape_jobs_linkedin(
            ["Security Engineer", "Cloud Security Engineer"], ["Berlin", "Remote"]
        )
        os.makedirs("smart_scraper", exist_ok=True)
        with open(SCRAPED_JOBS_PATH, "w") as f:
            for job in jobs:
                f.write(json.dumps(job) + "\n")
        return jobs


def apply_with_retry(job, max_retries=3):
    """Try applying to a job. If CAPTCHA or site issues, retry."""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔁 Attempt {attempt}: Applying to {job['title']} @ {job['company']}")
            auto_detect_and_apply(job)
            return True
        except Exception as e:
            print(f"[❌] Attempt {attempt} failed: {e}")
            time.sleep(2)
    print(f"[🚫] Failed to apply after {max_retries} attempts.")
    return False


def main():
    print("📄 Parsing resume...")
    resume_text = parse_resume(RESUME_PATH)

    print("📦 Loading JobBERT model...")
    model = SentenceTransformer(MODEL_PATH)
    resume_vec = model.encode(resume_text, convert_to_tensor=True)

    print("🧠 Matching to scraped jobs...")
    jobs = load_jobs()
    matches = []
    for job in jobs:
        job_vec = model.encode(job["description"], convert_to_tensor=True)
        score = float(util.cos_sim(resume_vec, job_vec).item()) * 100
        matches.append({**job, "score": round(score, 2)})
    matches.sort(key=lambda x: -x["score"])

    print("\n🚀 Top AI-matched jobs:")
    top_matches = matches[:5]
    for job in top_matches:
        print(f"  → {job['title']} @ {job['company']} — {job['score']}%")

    print("\n✅ Applying to top matches...")
    for job in top_matches:
        msg = generate_message(job['title'], job['location'], recipient_name="Hiring Team")
        applied = apply_with_retry(job)

        print(f"""💌 Recruiter Message:{msg}""")

    send_connection_requests()


if __name__ == "__main__":
    main()

