from extensions.parser import parse_resume
from ml_models.jobbert_onnx_runner import match_resume_to_jobs
import json

resume_text = parse_resume("resumes/Ankit_Thakur_Resume.pdf")

with open("smart_scraper/scraped_jobs.jsonl") as f:
    jobs = [json.loads(line) for line in f]

top_matches = match_resume_to_jobs(resume_text, jobs)

print("\nTop AI-matched jobs:")
for job in top_matches[:5]:
    print(f"{job['title']} @ {job['company']} — Score: {job['score']}%")