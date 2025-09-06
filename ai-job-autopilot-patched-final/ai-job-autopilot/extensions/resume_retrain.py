from dotenv import load_dotenvnload_dotenv()nimport osn
import json, os
from extensions.llm_fallback_ollama import fallback_to_ollama

DB_PATH = "data/interview_outcomes.json"

def record_outcome(company, status, notes):
    os.makedirs("data", exist_ok=True)
    data = []
    if os.path.exists(DB_PATH):
        data = json.load(open(DB_PATH))
    data.append({"company": company, "status": status, "notes": notes})
    json.dump(data, open(DB_PATH, "w"), indent=2)

def retrain_resume(resume_text):
    if not os.path.exists(DB_PATH): return resume_text
    data = json.load(open(DB_PATH))
    feedback = "\n".join([f"- {d['company']}: {d['status']} — {d['notes']}" for d in data if d['status'] != "Accepted"])
    prompt = f"""
Improve this resume to overcome previous interview failures:

Resume:
"""{resume_text}"""

Feedback:
{feedback}
"""
    return fallback_to_ollama(prompt)
