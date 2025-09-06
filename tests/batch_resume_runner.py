import os
import json
from pathlib import Path
from extensions.parser import parse_resume
from ml_models.jobbert_ranker import jobbert_score

resumes = list(Path("resumes").glob("*.pdf")) + list(Path("resumes").glob("*.docx"))
jobs = []
with open("smart_scraper/scraped_jobs.jsonl") as f:
    for line in f:
        jobs.append(json.loads(line))

all_results = {}
for resume_file in resumes:
    res_text = parse_resume(resume_file)
    results = []
    for job in jobs:
        score = jobbert_score(res_text, job["description"])
        results.append({"title": job["title"], "company": job["company"], "score": score})
    all_results[resume_file.name] = sorted(results, key=lambda x: -x["score"])[:5]

Path("data").mkdir(exist_ok=True)
with open("data/resume_match_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

print("\n[✅] Resume batch scoring complete. Top matches saved.")