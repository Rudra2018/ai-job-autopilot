import os
import pdfplumber
import docx
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel
from difflib import SequenceMatcher

load_dotenv()

class ResumeProfile(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = []
    experience: list[str] = []
    education: list[str] = []
    certifications: list[str] = []

def extract_text_from_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def parse_resume(path):
    if path.endswith(".pdf"):
        content = extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        content = extract_text_from_docx(path)
    else:
        return None

    lines = content.splitlines()
    profile = ResumeProfile()
    for line in lines:
        lower = line.lower()
        if "@" in line and "." in line:
            profile.email = line.strip()
        elif any(word in lower for word in ["skills", "technologies"]):
            profile.skills.extend(line.split(","))
        elif any(word in lower for word in ["experience", "worked at"]):
            profile.experience.append(line.strip())
        elif "certification" in lower:
            profile.certifications.append(line.strip())
        elif any(word in lower for word in ["bachelor", "master", "phd", "university"]):
            profile.education.append(line.strip())
    return profile

def score_match(profile, job):
    text = " ".join(profile.skills + profile.experience + profile.education)
    return round(SequenceMatcher(None, text.lower(), job["title"].lower()).ratio() * 100, 2)

def main():
    with open("config/user_profile.yaml") as f:
        user_profile = yaml.safe_load(f)

    resumes = [f for f in os.listdir("resumes") if f.endswith((".pdf", ".docx"))]
    for res_file in resumes:
        profile = parse_resume(os.path.join("resumes", res_file))
        if not profile:
            print(f"❌ Failed to parse: {res_file}")
            continue
        print(f"📄 Resume: {res_file}")
        for job in user_profile.get("job_targets", []):
            score = score_match(profile, job)
            print(f"  ✅ Match with '{job['title']}' ({job['location']}): {score}%")

        # Optional: inject top keywords to .env (if > 70%)
        top_jobs = sorted(user_profile.get("job_targets", []), key=lambda j: score_match(profile, j), reverse=True)
        if top_jobs and score_match(profile, top_jobs[0]) > 70:
            with open(".env", "a") as envfile:
                envfile.write(f"TOP_JOB_TITLE={top_jobs[0]['title']}\n")
                envfile.write(f"TOP_JOB_LOCATION={top_jobs[0]['location']}\n")

if __name__ == "__main__":
    main()
