import yaml
import re

def match_jobs_to_resume(resume_text, user_profile_path="config/user_profile.yaml"):
    with open(user_profile_path, "r") as f:
        profile = yaml.safe_load(f)

    titles = profile.get("job_preferences", {}).get("titles", [])
    locations = profile.get("job_preferences", {}).get("locations", [])

    matched_jobs = []
    resume_lower = resume_text.lower()

    for title in titles:
        title_keywords = re.findall(r'\w+', title.lower())
        if all(keyword in resume_lower for keyword in title_keywords):
            for location in locations:
                matched_jobs.append({
                    "title": title,
                    "location": location
                })

    return matched_jobs
