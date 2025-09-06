from sentence_transformers import SentenceTransformer, util
import torch

# Load the JobBERT-v3 model locally (after downloading from Hugging Face)
MODEL_PATH = "ml_models/jobbert_v3"
model = SentenceTransformer(MODEL_PATH)

def embed(text):
    return model.encode(text, convert_to_tensor=True)

def match_resume_to_jobs(resume_text, jobs):
    resume_vec = embed(resume_text)
    matches = []

    for job in jobs:
        job_vec = embed(job["description"])
        score = float(util.cos_sim(resume_vec, job_vec).item()) * 100
        matches.append({**job, "score": round(score, 2)})

    return sorted(matches, key=lambda x: -x["score"])

# Example usage (with preloaded resume_text and job list)
if __name__ == "__main__":
    import json
    from extensions.parser import parse_resume

    resume_text = parse_resume("resumes/Ankit_Thakur_Resume.pdf")

    with open("smart_scraper/scraped_jobs.jsonl") as f:
        jobs = [json.loads(line) for line in f]

    top_matches = match_resume_to_jobs(resume_text, jobs)
    print("\nTop AI-matched jobs:")
    for job in top_matches[:5]:
        print(f"{job['title']} @ {job['company']} — Score: {job['score']}%")