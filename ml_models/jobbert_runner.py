from sentence_transformers import SentenceTransformer, util
import torch
import yaml
import re
from pathlib import Path

# Load the JobBERT-v3 model locally (after downloading from Hugging Face)
MODEL_PATH = "ml_models/jobbert_v3"
model = SentenceTransformer(MODEL_PATH)

def load_user_preferences():
    """Load user preferences from config/user_profile.yaml"""
    config_path = Path("config/user_profile.yaml")
    if config_path.exists():
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    return {}

def embed(text):
    return model.encode(text, convert_to_tensor=True)

def calculate_cybersecurity_bonus(job, config):
    """Calculate bonus score for cybersecurity-specific roles and keywords"""
    bonus = 0.0
    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    
    # Get user's preferred keywords
    keywords = config.get('job_preferences', {}).get('keywords', [])
    
    # Core cybersecurity role bonus
    core_roles = ['penetration tester', 'security engineer', 'application security', 'cloud security']
    if any(role in job_text for role in core_roles):
        bonus += 15.0
    
    # Keyword matching bonus
    keyword_matches = sum(1 for keyword in keywords if keyword.lower() in job_text)
    bonus += min(keyword_matches * 2.0, 20.0)  # Max 20% from keywords
    
    # Location preference bonus
    preferred_locations = config.get('job_preferences', {}).get('locations', [])
    job_location = job.get('location', '').lower()
    if any(loc.lower() in job_location for loc in preferred_locations):
        bonus += 10.0
    
    # Experience level matching
    if 'senior' in job_text and 'senior' in job.get('title', '').lower():
        bonus += 8.0
    
    # Easy Apply bonus (faster application process)
    if job.get('easy_apply', False):
        bonus += 5.0
    
    # Company reputation bonus
    top_companies = ['google', 'microsoft', 'amazon', 'apple', 'meta', 'netflix', 
                    'siemens', 'sap', 'deutsche bank', 'ing bank', 'bae systems']
    company_name = job.get('company', '').lower()
    if any(company in company_name for company in top_companies):
        bonus += 12.0
    
    return min(bonus, 50.0)  # Cap total bonus at 50%

def calculate_location_bonus(job, config):
    """Calculate location-specific bonus based on target regions"""
    bonus = 0.0
    job_location = job.get('location', '').lower()
    
    # EMEA region bonus
    emea_locations = ['london', 'amsterdam', 'dublin', 'zurich', 'paris', 'stockholm', 
                     'copenhagen', 'oslo', 'helsinki', 'vienna', 'brussels', 'luxembourg']
    if any(loc in job_location for loc in emea_locations):
        bonus += 8.0
    
    # Germany bonus (specific target)
    if 'germany' in job_location or any(city in job_location for city in 
        ['berlin', 'munich', 'frankfurt', 'hamburg', 'cologne']):
        bonus += 12.0
    
    # USA bonus
    usa_cities = ['new york', 'san francisco', 'seattle', 'austin', 'chicago', 'boston']
    if any(city in job_location for city in usa_cities):
        bonus += 10.0
    
    # Remote work bonus
    if 'remote' in job_location:
        bonus += 15.0
    
    return bonus

def match_resume_to_jobs(resume_text, jobs):
    """Enhanced job matching with cybersecurity focus and regional preferences"""
    config = load_user_preferences()
    resume_vec = embed(resume_text)
    matches = []
    
    # Enhanced resume text with Ankit's specific skills
    enhanced_resume = f"""
    {resume_text}
    
    Ankit Thakur - Cybersecurity Professional
    Expertise: Penetration Testing, API Security, Cloud Security, GDPR Compliance
    Experience: SDET II at Halodoc Technologies, Senior Security Consultant at Prescient Security
    Certifications: AWS Security Specialty, CompTIA Security+, AWS SysOps Administrator
    Achievements: Reduced security risks by 25%, improved data protection by 30%
    Recognition: Hall of Fame from Google, Facebook, Yahoo, U.S. Department of Defense
    Skills: Vulnerability Assessment, DevSecOps, SIEM, Threat Modeling, ISO 27001, NIST
    """
    
    enhanced_resume_vec = embed(enhanced_resume)
    
    for job in jobs:
        # Standard semantic similarity
        job_description = job.get("description", "")
        job_vec = embed(job_description)
        base_score = float(util.cos_sim(enhanced_resume_vec, job_vec).item()) * 100
        
        # Add cybersecurity-specific bonuses
        cyber_bonus = calculate_cybersecurity_bonus(job, config)
        location_bonus = calculate_location_bonus(job, config)
        
        # Calculate final score
        final_score = base_score + cyber_bonus + location_bonus
        
        matches.append({
            **job, 
            "score": round(min(final_score, 100.0), 2),  # Cap at 100%
            "base_score": round(base_score, 2),
            "cyber_bonus": round(cyber_bonus, 2),
            "location_bonus": round(location_bonus, 2)
        })
    
    return sorted(matches, key=lambda x: -x["score"])

def filter_high_match_jobs(matches, threshold=3.0):
    """Filter jobs above the specified threshold"""
    return [job for job in matches if job["score"] >= threshold]

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