
"""
Dynamic Candidate Configurator for AI Job Autopilot
Generates per-user config YAMLs based on uploaded resume + metadata
To be used across Vertex AI pipelines & smart scraper filters
"""

import yaml
from pathlib import Path

def build_candidate_config(name, email, phone, resume_path, location_preferences, job_titles, languages, linkedin_url, xing_url):
    config = {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin_url": linkedin_url,
        "xing_url": xing_url,
        "resume_path": resume_path,
        "languages": languages,
        "job_targets": [{"title": t, "location": l} for t in job_titles for l in location_preferences],
        "job_preferences": {
            "titles": job_titles,
            "locations": location_preferences
        },
        "vision_ocr": True,
        "geolocation_filtering": True,
        "auto_apply": True,
        "smart_scraper_enabled": True,
        "german_recruiter_messages": True
    }
    path = Path(f"config/generated_{name.replace(' ', '_').lower()}.yaml")
    with open(path, "w") as f:
        yaml.dump(config, f)
    print(f"[✅] Config generated at: {path.resolve()}")
    return config

# Example usage
if __name__ == "__main__":
    build_candidate_config(
        name="Ankit Thakur",
        email="hacking4bucks@gmail.com",
        phone="+91-8717934430",
        resume_path="config/resume.pdf",
        location_preferences=["Berlin", "Munich", "Remote (EU)"],
        job_titles=["Cloud Security Engineer", "DevSecOps Specialist"],
        languages=["English", "German (A2)"],
        linkedin_url="https://www.linkedin.com/in/ankit-t-8258661b2/",
        xing_url="https://www.xing.com/profile/Ankit_Thakur092429/web_profiles"
    )
