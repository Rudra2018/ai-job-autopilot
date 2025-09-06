import yaml
from pyresparser import ResumeParser

def generate_job_titles(resume_path):
    data = ResumeParser(resume_path).get_extracted_data()
    skills = data.get("skills", [])
    print("\nSuggested Job Titles Based on Resume:")
    if "aws" in [s.lower() for s in skills]:
        print("- Cloud Security Engineer")
    if "python" in [s.lower() for s in skills]:
        print("- Security Automation Engineer")
    if "siem" in [s.lower() for s in skills]:
        print("- SOC Analyst")
    if not skills:
        print("No skills found in resume.")
    return skills

if __name__ == "__main__":
    generate_job_titles("config/resume.pdf")