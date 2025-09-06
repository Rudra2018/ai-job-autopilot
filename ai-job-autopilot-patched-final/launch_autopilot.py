
from sentence_transformers import SentenceTransformer, util
from extensions.parser import parse_resume
from extensions.resume_retrain import record_outcome
from extensions.ocr_job_parser import extract_text_from_job_image, parse_job_details
from extensions.llm_fallback_ollama import gemini_fallback_respond
from worker.playwright_apply import simulate_job_apply
from worker.recruiter_message_generator import generate_message
from worker.linkedin_xing_auto_connect import send_connection_requests
from pathlib import Path
import json, os, asyncio

RESUME_PATH = "resumes/resume.pdf"
MODEL_PATH = "ml_models/jobbert_v3"
SCRAPED_JOBS_PATH = "smart_scraper/scraped_jobs.jsonl"
SCREENSHOT_PATH = "screenshots/job.png"

def load_jobs():
    if Path(SCRAPED_JOBS_PATH).exists():
        return [json.loads(line) for line in open(SCRAPED_JOBS_PATH)]
    elif Path(SCREENSHOT_PATH).exists():
        print("🖼️ Using OCR to parse job screenshot...")
        ocr_text = extract_text_from_job_image(SCREENSHOT_PATH)
        job = parse_job_details(ocr_text)
        return [job]
    else:
        print("[⚠️] No jobs or screenshots found.")
        return []

async def main():
    print("📄 Parsing resume...")
    resume_text = parse_resume(RESUME_PATH)

    print("📦 Loading JobBERT model...")
    model = SentenceTransformer(MODEL_PATH)
    resume_vec = model.encode(resume_text, convert_to_tensor=True)

    print("🧠 Matching to scraped or OCR'd jobs...")
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
        print(f"  → {job['title']} @ {job.get('company', 'Unknown')} — {job['score']}%")

    print("\n✅ Applying to top matches...")
    for job in top_matches:
        try:
            prompt = f"Write a short outreach message for the job title '{job['title']}' in location '{job['location']}'."
            msg = gemini_fallback_respond(prompt).strip()
        except Exception:
            msg = generate_message(job['title'], job['location'], recipient_name="Hiring Team")

        print(f"💌 Recruiter Message:\n{msg}\n")
        await simulate_job_apply(job)
        record_outcome(job, "applied")

    send_connection_requests()

if __name__ == "__main__":
    asyncio.run(main())
