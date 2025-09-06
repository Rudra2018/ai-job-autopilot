import os
from pyresparser import ResumeParser

def parse_resume(resume_path):
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume not found: {resume_path}")
    data = ResumeParser(resume_path).get_extracted_data()
    print("Extracted Resume Data:")
    for k, v in data.items():
        print(f"{k}: {v}")
    return data

if __name__ == "__main__":
    parse_resume("config/resume.pdf")