import re
import yaml

def match_jobs_to_resume(resume_text, titles=None, preferences=None):
    """
    Matches job titles and locations against the given resume text.

    Args:
        resume_text (str): Extracted resume text.
        titles (list[str], optional): List of job titles to match.
        preferences (dict, optional): Dictionary with location preferences under key 'locations'.

    Returns:
        list[dict]: Matched job entries with 'title', 'company', and 'location'.
    """
    if titles is None or preferences is None:
        with open("config/user_profile.yaml", "r") as f:
            profile = yaml.safe_load(f)
        titles = profile.get("job_preferences", {}).get("titles", [])
        locations = profile.get("job_preferences", {}).get("locations", [])
    else:
        locations = preferences.get("locations", [])

    matched_jobs = []
    resume_lower = resume_text.lower()

    for title in titles:
        title_keywords = re.findall(r'\w+', title.lower())
        if all(keyword in resume_lower for keyword in title_keywords):
            for location in locations:
                matched_jobs.append({
                    "title": title,
                    "company": "Scraped Job",
                    "location": location
                })

    return matched_jobs

