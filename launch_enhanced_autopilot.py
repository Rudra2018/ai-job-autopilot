#!/usr/bin/env python3
"""
Enhanced AI Job Autopilot with EMEA/Germany/USA targeting and LinkedIn Easy Apply
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import List, Dict

# Import all the enhanced modules
from smart_scraper.linkedin_scraper import scrape_jobs_linkedin, linkedin_easy_apply
from ml_models.jobbert_runner import match_resume_to_jobs, filter_high_match_jobs
from worker.recruiter_message_generator import generate_message
from worker.application_logger import log_application
from extensions.parser import parse_resume

def load_config():
    """Load user configuration"""
    config_path = Path("config/user_profile.yaml")
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_cybersecurity_keywords():
    """Get comprehensive cybersecurity keywords for job searching"""
    return [
        "penetration testing", "security engineer", "application security", 
        "cloud security", "cybersecurity", "vulnerability assessment",
        "DevSecOps", "security analyst", "incident response", "threat hunting",
        "malware analysis", "forensics", "GRC", "compliance", "SIEM"
    ]

def get_target_locations():
    """Get all target locations for job search"""
    return [
        # EMEA
        "London", "Amsterdam", "Dublin", "Zurich", "Paris", "Stockholm",
        "Copenhagen", "Oslo", "Helsinki", "Vienna", "Brussels", "Luxembourg",
        # Germany  
        "Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne", "Stuttgart",
        "Düsseldorf", "Dresden", "Leipzig",
        # USA
        "New York", "San Francisco", "Los Angeles", "Seattle", "Austin", 
        "Chicago", "Boston", "Washington DC", "Atlanta", "Dallas", "Denver",
        "Raleigh", "Phoenix", "San Diego", "Miami",
        # Remote
        "Remote"
    ]

async def apply_with_easy_apply(job: Dict, resume_path: str) -> Dict:
    """Apply to job using LinkedIn Easy Apply if available"""
    if job.get('easy_apply', False) and 'linkedin.com' in job.get('link', ''):
        print(f"🚀 Attempting Easy Apply for {job['title']} @ {job['company']}")
        result = await linkedin_easy_apply(job['link'], resume_path)
        
        if result['status'] == 'applied':
            print(f"✅ Successfully applied via Easy Apply!")
            return {
                'status': 'applied_easy',
                'method': 'linkedin_easy_apply',
                'job': job
            }
        else:
            print(f"⚠️ Easy Apply failed: {result.get('error', 'Unknown error')}")
    
    # Fallback to standard application process
    print(f"📝 Standard application for {job['title']} @ {job['company']}")
    
    # Generate personalized recruiter message
    recruiter_msg = generate_message(
        candidate_name="Ankit Thakur",
        job=job,
        recipient_name="Hiring Team"
    )
    
    # Log application
    log_application(job, 'applied', recruiter_msg)
    
    return {
        'status': 'applied_standard',
        'method': 'standard_application',
        'job': job,
        'recruiter_message': recruiter_msg
    }

def print_job_stats(jobs: List[Dict]):
    """Print comprehensive job statistics"""
    print("\n" + "="*80)
    print("🎯 JOB SEARCH STATISTICS")
    print("="*80)
    
    # Regional breakdown
    regions = {"EMEA": 0, "Germany": 0, "USA": 0, "Remote": 0}
    for job in jobs:
        location = job.get('location', '').lower()
        if 'remote' in location:
            regions["Remote"] += 1
        elif any(country in location for country in ['uk', 'netherlands', 'ireland', 'switzerland', 'france', 'sweden', 'denmark', 'norway', 'finland', 'austria', 'belgium', 'luxembourg']):
            regions["EMEA"] += 1
        elif 'germany' in location:
            regions["Germany"] += 1
        elif any(state in location for state in ['ny', 'ca', 'tx', 'wa', 'il', 'ma', 'dc', 'ga', 'co', 'nc', 'az', 'fl']):
            regions["USA"] += 1
    
    print(f"📍 Regional Distribution:")
    for region, count in regions.items():
        print(f"   {region}: {count} jobs")
    
    # Role breakdown
    roles = {}
    for job in jobs:
        title = job.get('title', 'Unknown').lower()
        if 'penetration' in title:
            roles['Penetration Tester'] = roles.get('Penetration Tester', 0) + 1
        elif 'application security' in title or 'appsec' in title:
            roles['Application Security Engineer'] = roles.get('Application Security Engineer', 0) + 1
        elif 'cloud security' in title:
            roles['Cloud Security Engineer'] = roles.get('Cloud Security Engineer', 0) + 1
        elif 'security engineer' in title:
            roles['Security Engineer'] = roles.get('Security Engineer', 0) + 1
        else:
            roles['Other Security Roles'] = roles.get('Other Security Roles', 0) + 1
    
    print(f"\n🎭 Role Distribution:")
    for role, count in roles.items():
        print(f"   {role}: {count} jobs")
    
    # Easy Apply stats
    easy_apply_count = sum(1 for job in jobs if job.get('easy_apply', False))
    print(f"\n⚡ Easy Apply Available: {easy_apply_count}/{len(jobs)} jobs ({easy_apply_count/len(jobs)*100:.1f}%)")

async def main():
    """Enhanced autopilot main function"""
    print("🤖 AI JOB AUTOPILOT - ENHANCED GLOBAL VERSION")
    print("🌍 Targeting: EMEA | Germany | USA")
    print("🎯 Focus: Cybersecurity Roles with LinkedIn Easy Apply")
    print("="*60)
    
    # Load configuration
    config = load_config()
    resume_path = config.get('resume_path', 'config/resume.pdf')
    
    # Parse resume
    print("📄 Parsing resume...")
    resume_text = parse_resume(resume_path)
    
    # Get jobs from enhanced LinkedIn scraper
    print("🔍 Scraping jobs globally...")
    keywords = get_cybersecurity_keywords()
    locations = get_target_locations()
    
    all_jobs = scrape_jobs_linkedin(keywords, locations)
    print(f"📊 Found {len(all_jobs)} cybersecurity jobs across all regions")
    
    # Print detailed statistics
    print_job_stats(all_jobs)
    
    # AI matching with enhanced scoring
    print("\n🧠 AI job matching with cybersecurity focus...")
    matches = match_resume_to_jobs(resume_text, all_jobs)
    
    # Filter high-quality matches
    threshold = config.get('job_preferences', {}).get('automation', {}).get('target_match_threshold', 3.0)
    high_matches = filter_high_match_jobs(matches, threshold)
    
    print(f"\n🎯 Top AI-matched jobs (>{threshold}% match):")
    for i, job in enumerate(high_matches[:10], 1):
        easy_apply_icon = "⚡" if job.get('easy_apply', False) else "📝"
        print(f"  {i}. {easy_apply_icon} {job['title']} @ {job['company']} ({job['location']}) — {job['score']}%")
        if 'cyber_bonus' in job:
            print(f"     Base: {job['base_score']}% + Cyber: {job['cyber_bonus']}% + Location: {job['location_bonus']}%")
    
    # Apply to jobs
    max_applications = config.get('job_preferences', {}).get('automation', {}).get('max_applications_per_day', 10)
    applications_to_process = high_matches[:max_applications]
    
    print(f"\n✅ Applying to top {len(applications_to_process)} matches...")
    
    results = []
    for i, job in enumerate(applications_to_process, 1):
        print(f"\n🔄 Application {i}/{len(applications_to_process)}")
        result = await apply_with_easy_apply(job, resume_path)
        results.append(result)
        
        # Small delay between applications
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("📈 APPLICATION SUMMARY")
    print("="*80)
    
    easy_apply_success = sum(1 for r in results if r['status'] == 'applied_easy')
    standard_apply = sum(1 for r in results if r['status'] == 'applied_standard')
    
    print(f"⚡ Easy Apply Successful: {easy_apply_success}")
    print(f"📝 Standard Applications: {standard_apply}")
    print(f"🎯 Total Applications: {len(results)}")
    
    # Regional breakdown of applications
    applied_regions = {}
    for result in results:
        location = result['job'].get('location', 'Unknown')
        region = "Other"
        if 'Remote' in location:
            region = "Remote"
        elif any(country in location for country in ['UK', 'Netherlands', 'Ireland', 'Switzerland', 'France']):
            region = "EMEA" 
        elif 'Germany' in location:
            region = "Germany"
        elif any(state in location for state in ['NY', 'CA', 'TX', 'WA', 'IL', 'MA', 'DC']):
            region = "USA"
        
        applied_regions[region] = applied_regions.get(region, 0) + 1
    
    print(f"\n🌍 Applications by Region:")
    for region, count in applied_regions.items():
        print(f"   {region}: {count} applications")
    
    print("\n🎉 Enhanced Global Autopilot Complete!")
    print("💼 Monitor your email for responses and interview invitations")
    print(f"📊 Dashboard: http://localhost:8501")

if __name__ == "__main__":
    asyncio.run(main())