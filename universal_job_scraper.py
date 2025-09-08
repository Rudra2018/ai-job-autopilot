#!/usr/bin/env python3
"""
Universal Job Scraper - Multi-Platform Job Discovery & Auto-Application
Scrapes jobs from all major job portals and company websites automatically
"""

import asyncio
import json
import os
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin
import aiohttp
from playwright.async_api import async_playwright, Browser, Page
from dataclasses import dataclass
import hashlib
from pathlib import Path
import yaml

# AI imports for skill matching
import openai
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class JobListing:
    """Standardized job listing structure"""
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: str
    salary: Optional[str]
    experience_level: str
    job_type: str  # full-time, part-time, contract
    remote_friendly: bool
    application_url: str
    source_platform: str
    posted_date: Optional[str]
    skills_required: List[str]
    benefits: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    scraped_at: str

class JobPlatformScraper:
    """Base scraper class for job platforms"""
    
    def __init__(self, platform_name: str, base_url: str):
        self.platform_name = platform_name
        self.base_url = base_url
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
    
    async def scrape(self, keywords: List[str], locations: List[str], page: Page) -> List[JobListing]:
        """Override this method in platform-specific scrapers"""
        raise NotImplementedError

class LinkedInScraper(JobPlatformScraper):
    """LinkedIn job scraper with Easy Apply detection"""
    
    def __init__(self):
        super().__init__("LinkedIn", "https://www.linkedin.com/jobs/search/")
    
    async def scrape(self, keywords: List[str], locations: List[str], page: Page) -> List[JobListing]:
        jobs = []
        
        for keyword in keywords[:3]:  # Limit to prevent rate limiting
            for location in locations[:2]:
                try:
                    # Build LinkedIn search URL
                    search_url = f"{self.base_url}?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_LF=f_AL"  # f_AL = Easy Apply
                    
                    await page.goto(search_url)
                    await page.wait_for_timeout(random.randint(3000, 5000))
                    
                    # Handle LinkedIn login if needed
                    if "login" in page.url or "challenge" in page.url:
                        print(f"   ⚠️  LinkedIn login required for {keyword}")
                        continue
                    
                    # Scroll to load more jobs
                    for _ in range(3):
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(2000)
                    
                    # Extract job cards
                    job_cards = await page.locator('[data-entity-urn*="urn:li:fsd_jobPosting"], .job-search-card').all()
                    
                    print(f"   📊 Found {len(job_cards)} LinkedIn jobs for '{keyword}' in {location}")
                    
                    for i, card in enumerate(job_cards[:20]):  # Process first 20
                        try:
                            await card.click()
                            await page.wait_for_timeout(2000)
                            
                            # Extract job details
                            title_elem = page.locator('.job-details-jobs-unified-top-card__job-title h1, .jobs-unified-top-card__job-title')
                            company_elem = page.locator('.job-details-jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name')
                            location_elem = page.locator('.job-details-jobs-unified-top-card__bullet, .jobs-unified-top-card__bullet')
                            description_elem = page.locator('.jobs-description__content, .jobs-box__html-content')
                            
                            title = await self._safe_text(title_elem)
                            company = await self._safe_text(company_elem)
                            job_location = await self._safe_text(location_elem)
                            description = await self._safe_text(description_elem)
                            
                            # Check for Easy Apply button
                            easy_apply_btn = page.locator('button:has-text("Easy Apply"), .jobs-apply-button--top-card')
                            has_easy_apply = await easy_apply_btn.count() > 0
                            
                            if title and company and has_easy_apply:
                                job_id = hashlib.md5(f"{title}{company}{job_location}".encode()).hexdigest()[:12]
                                
                                job = JobListing(
                                    id=f"linkedin_{job_id}",
                                    title=title,
                                    company=company,
                                    location=job_location or location,
                                    description=description[:1000],
                                    requirements=self._extract_requirements(description),
                                    salary=None,  # LinkedIn often doesn't show salary
                                    experience_level=self._extract_experience_level(description),
                                    job_type="full-time",
                                    remote_friendly="remote" in description.lower() or "remote" in title.lower(),
                                    application_url=page.url,
                                    source_platform="LinkedIn",
                                    posted_date=None,
                                    skills_required=self._extract_skills(description),
                                    benefits=None,
                                    company_size=None,
                                    industry=None,
                                    scraped_at=datetime.now().isoformat()
                                )
                                
                                jobs.append(job)
                                print(f"   ✅ {title} @ {company}")
                                
                        except Exception as e:
                            print(f"   ❌ Error processing LinkedIn job {i+1}: {str(e)}")
                            continue
                    
                    await page.wait_for_timeout(3000)
                    
                except Exception as e:
                    print(f"   ❌ Error scraping LinkedIn for '{keyword}': {str(e)}")
                    continue
        
        return jobs
    
    async def _safe_text(self, locator) -> str:
        try:
            if await locator.count() > 0:
                return (await locator.first.text_content()).strip()
        except:
            pass
        return ""
    
    def _extract_requirements(self, description: str) -> str:
        """Extract requirements from job description"""
        requirements_patterns = [
            r"Requirements?:?\s*(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Qualifications?:?\s*(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Must have:?\s*(.*?)(?:\n\n|\n[A-Z]|$)"
        ]
        
        for pattern in requirements_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:500]
        
        return ""
    
    def _extract_experience_level(self, description: str) -> str:
        """Extract experience level from description"""
        description_lower = description.lower()
        
        if any(term in description_lower for term in ['senior', '5+', 'lead', 'principal']):
            return "senior"
        elif any(term in description_lower for term in ['junior', 'entry', 'graduate', '0-2']):
            return "junior"
        else:
            return "mid"
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract technical skills from description"""
        common_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'terraform', 'git', 'linux', 'mongodb', 'postgresql',
            'cybersecurity', 'penetration testing', 'vulnerability assessment',
            'incident response', 'security architecture', 'cloud security',
            'network security', 'compliance', 'risk assessment', 'threat modeling'
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills

class IndeedScraper(JobPlatformScraper):
    """Indeed job scraper with apply tracking"""
    
    def __init__(self):
        super().__init__("Indeed", "https://www.indeed.com/jobs")
    
    async def scrape(self, keywords: List[str], locations: List[str], page: Page) -> List[JobListing]:
        jobs = []
        
        for keyword in keywords[:3]:
            for location in locations[:2]:
                try:
                    search_url = f"{self.base_url}?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}"
                    
                    await page.goto(search_url)
                    await page.wait_for_timeout(random.randint(2000, 4000))
                    
                    # Handle Indeed's popup if present
                    try:
                        popup_close = page.locator('button[aria-label="close"], .icl-CloseIcon')
                        if await popup_close.count() > 0:
                            await popup_close.first.click()
                    except:
                        pass
                    
                    # Extract job cards
                    job_cards = await page.locator('[data-jk], .job_seen_beacon').all()
                    
                    print(f"   📊 Found {len(job_cards)} Indeed jobs for '{keyword}' in {location}")
                    
                    for i, card in enumerate(job_cards[:15]):
                        try:
                            await card.click()
                            await page.wait_for_timeout(2000)
                            
                            # Extract job details
                            title = await self._safe_text(page.locator('h1[data-testid="jobsearch-JobInfoHeader-title"], .jobsearch-JobInfoHeader-title'))
                            company = await self._safe_text(page.locator('[data-testid="inlineHeader-companyName"], .jobsearch-CompanyReview--link'))
                            job_location = await self._safe_text(page.locator('[data-testid="job-location"], .jobsearch-JobMetadataHeader-iconLabel'))
                            description = await self._safe_text(page.locator('[data-testid="jobsearch-jobDescriptionText"], .jobsearch-jobDescriptionText'))
                            salary = await self._safe_text(page.locator('[data-testid="jobsearch-JobMetadataHeader-item"], .jobsearch-JobMetadataHeader-item'))
                            
                            # Check if we can apply directly
                            apply_btn = page.locator('button:has-text("Apply now"), .ia-IndeedApplyButton')
                            can_apply_directly = await apply_btn.count() > 0
                            
                            if title and company:
                                job_id = hashlib.md5(f"{title}{company}{job_location}".encode()).hexdigest()[:12]
                                
                                job = JobListing(
                                    id=f"indeed_{job_id}",
                                    title=title,
                                    company=company,
                                    location=job_location or location,
                                    description=description[:1000],
                                    requirements=self._extract_requirements(description),
                                    salary=salary if '$' in salary else None,
                                    experience_level=self._extract_experience_level(description),
                                    job_type=self._extract_job_type(description),
                                    remote_friendly="remote" in description.lower() or "remote" in title.lower(),
                                    application_url=page.url,
                                    source_platform="Indeed",
                                    posted_date=None,
                                    skills_required=self._extract_skills(description),
                                    benefits=None,
                                    company_size=None,
                                    industry=None,
                                    scraped_at=datetime.now().isoformat()
                                )
                                
                                jobs.append(job)
                                print(f"   ✅ {title} @ {company}")
                                
                        except Exception as e:
                            print(f"   ❌ Error processing Indeed job {i+1}: {str(e)}")
                            continue
                    
                except Exception as e:
                    print(f"   ❌ Error scraping Indeed for '{keyword}': {str(e)}")
                    continue
        
        return jobs
    
    async def _safe_text(self, locator) -> str:
        try:
            if await locator.count() > 0:
                return (await locator.first.text_content()).strip()
        except:
            pass
        return ""
    
    def _extract_requirements(self, description: str) -> str:
        requirements_patterns = [
            r"Requirements?:?\s*(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Qualifications?:?\s*(.*?)(?:\n\n|\n[A-Z]|$)"
        ]
        
        for pattern in requirements_patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:500]
        return ""
    
    def _extract_experience_level(self, description: str) -> str:
        description_lower = description.lower()
        
        if any(term in description_lower for term in ['senior', '5+', 'lead']):
            return "senior"
        elif any(term in description_lower for term in ['junior', 'entry', '0-2']):
            return "junior"
        return "mid"
    
    def _extract_job_type(self, description: str) -> str:
        description_lower = description.lower()
        
        if "contract" in description_lower:
            return "contract"
        elif "part-time" in description_lower:
            return "part-time"
        return "full-time"
    
    def _extract_skills(self, description: str) -> List[str]:
        skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws',
            'cybersecurity', 'penetration testing', 'security architecture'
        ]
        
        description_lower = description.lower()
        return [skill for skill in skills if skill.lower() in description_lower]

class RemoteOKScraper(JobPlatformScraper):
    """Remote OK scraper for remote jobs"""
    
    def __init__(self):
        super().__init__("RemoteOK", "https://remoteok.io/remote-dev-jobs")
    
    async def scrape(self, keywords: List[str], locations: List[str], page: Page) -> List[JobListing]:
        jobs = []
        
        try:
            await page.goto(self.base_url)
            await page.wait_for_timeout(3000)
            
            # Extract job listings
            job_elements = await page.locator('.job, [data-jobid]').all()
            
            print(f"   📊 Found {len(job_elements)} RemoteOK jobs")
            
            for i, job_elem in enumerate(job_elements[:20]):
                try:
                    title = await self._safe_text(job_elem.locator('.company h2, .title'))
                    company = await self._safe_text(job_elem.locator('.company h3, .company_name'))
                    location = "Remote"
                    tags = await self._get_tags(job_elem)
                    
                    # Click to get more details
                    await job_elem.click()
                    await page.wait_for_timeout(2000)
                    
                    description = await self._safe_text(page.locator('.jobpage, .job-description'))
                    
                    if title and company:
                        job_id = hashlib.md5(f"{title}{company}remoteok".encode()).hexdigest()[:12]
                        
                        job = JobListing(
                            id=f"remoteok_{job_id}",
                            title=title,
                            company=company,
                            location=location,
                            description=description[:1000],
                            requirements="",
                            salary=None,
                            experience_level="mid",
                            job_type="full-time",
                            remote_friendly=True,
                            application_url=page.url,
                            source_platform="RemoteOK",
                            posted_date=None,
                            skills_required=tags,
                            benefits=None,
                            company_size=None,
                            industry=None,
                            scraped_at=datetime.now().isoformat()
                        )
                        
                        jobs.append(job)
                        print(f"   ✅ {title} @ {company}")
                        
                except Exception as e:
                    print(f"   ❌ Error processing RemoteOK job {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error scraping RemoteOK: {str(e)}")
        
        return jobs
    
    async def _safe_text(self, locator) -> str:
        try:
            if await locator.count() > 0:
                return (await locator.first.text_content()).strip()
        except:
            pass
        return ""
    
    async def _get_tags(self, job_elem) -> List[str]:
        try:
            tag_elements = await job_elem.locator('.tag, .tags span').all()
            tags = []
            for tag_elem in tag_elements:
                tag_text = await self._safe_text(tag_elem)
                if tag_text:
                    tags.append(tag_text.lower())
            return tags
        except:
            return []

class UniversalJobScraper:
    """Universal job scraper orchestrating all platforms"""
    
    def __init__(self):
        self.scrapers = {
            'linkedin': LinkedInScraper(),
            'indeed': IndeedScraper(),
            'remoteok': RemoteOKScraper()
        }
        
        # Initialize AI models for skill matching
        self.skill_matcher = pipeline('feature-extraction', model='sentence-transformers/all-MiniLM-L6-v2')
        
        # Load user profile
        self.user_profile = self._load_user_profile()
        
    def _load_user_profile(self) -> Dict:
        """Load user profile and skills from config"""
        profile_path = Path("config/user_profile.yaml")
        
        if profile_path.exists():
            with open(profile_path) as f:
                return yaml.safe_load(f)
        
        # Default profile if not found
        return {
            'name': 'Ankit Thakur',
            'email': 'at87.at17@gmail.com',
            'phone': '+91 8717934430',
            'skills': [
                'cybersecurity', 'penetration testing', 'vulnerability assessment',
                'cloud security', 'aws', 'network security', 'incident response',
                'compliance', 'risk assessment', 'security architecture',
                'python', 'javascript', 'sql', 'linux', 'docker'
            ],
            'experience_level': 'senior',
            'preferred_locations': ['Remote', 'Berlin', 'Munich', 'Hamburg', 'London', 'Amsterdam'],
            'job_types': ['full-time', 'contract'],
            'salary_expectations': {
                'min': 80000,
                'currency': 'EUR'
            }
        }
    
    def calculate_job_match_score(self, job: JobListing) -> float:
        """Calculate match score between job and user profile using AI"""
        try:
            # Combine job skills and description for matching
            job_text = f"{job.title} {job.description} {' '.join(job.skills_required)}"
            user_skills_text = ' '.join(self.user_profile['skills'])
            
            # Get embeddings
            job_embedding = self.skill_matcher(job_text)[0]
            user_embedding = self.skill_matcher(user_skills_text)[0]
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                np.array(job_embedding).reshape(1, -1),
                np.array(user_embedding).reshape(1, -1)
            )[0][0]
            
            # Boost score based on various factors
            boost_factors = 0.0
            
            # Experience level match
            if job.experience_level == self.user_profile.get('experience_level', 'mid'):
                boost_factors += 0.1
            
            # Location preference
            if job.location in self.user_profile.get('preferred_locations', []) or job.remote_friendly:
                boost_factors += 0.1
            
            # Job type match
            if job.job_type in self.user_profile.get('job_types', ['full-time']):
                boost_factors += 0.05
            
            # Platform reliability (LinkedIn and Indeed are more reliable)
            if job.source_platform in ['LinkedIn', 'Indeed']:
                boost_factors += 0.05
            
            final_score = min(1.0, similarity + boost_factors)
            return final_score
            
        except Exception as e:
            print(f"Error calculating match score: {str(e)}")
            return 0.5  # Default score
    
    async def scrape_all_platforms(
        self, 
        keywords: List[str] = None, 
        locations: List[str] = None,
        min_match_score: float = 0.6
    ) -> List[JobListing]:
        """Scrape jobs from all platforms and filter by match score"""
        
        if not keywords:
            keywords = [
                "cybersecurity engineer", "security engineer", "penetration tester",
                "information security", "cloud security", "application security"
            ]
        
        if not locations:
            locations = self.user_profile.get('preferred_locations', ['Remote'])
        
        all_jobs = []
        
        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions-except=/path/to/extension',
                    '--disable-extensions',
                    '--disable-plugins-discovery',
                    '--disable-dev-shm-usage'
                ]
            )
            
            context = await browser.new_context(
                user_agent=random.choice(self.scrapers['linkedin'].user_agents),
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Scrape each platform
            for platform_name, scraper in self.scrapers.items():
                try:
                    print(f"\n🔍 Scraping {platform_name.upper()}...")
                    
                    jobs = await scraper.scrape(keywords, locations, page)
                    
                    # Filter jobs by match score
                    scored_jobs = []
                    for job in jobs:
                        match_score = self.calculate_job_match_score(job)
                        if match_score >= min_match_score:
                            job.match_score = match_score  # Add match score to job
                            scored_jobs.append(job)
                    
                    print(f"   ✅ {len(scored_jobs)} high-match jobs from {platform_name}")
                    all_jobs.extend(scored_jobs)
                    
                    # Random delay between platforms
                    await asyncio.sleep(random.randint(5, 10))
                    
                except Exception as e:
                    print(f"   ❌ Error scraping {platform_name}: {str(e)}")
                    continue
            
            await browser.close()
        
        # Sort by match score (highest first)
        all_jobs.sort(key=lambda x: getattr(x, 'match_score', 0), reverse=True)
        
        # Remove duplicates based on title and company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            job_signature = f"{job.title.lower()}_{job.company.lower()}"
            if job_signature not in seen:
                seen.add(job_signature)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def save_jobs(self, jobs: List[JobListing], filename: str = "scraped_jobs.json"):
        """Save scraped jobs to file"""
        output_dir = Path("data/scraped_jobs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        
        # Convert JobListing objects to dictionaries
        jobs_data = []
        for job in jobs:
            job_dict = {
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'requirements': job.requirements,
                'salary': job.salary,
                'experience_level': job.experience_level,
                'job_type': job.job_type,
                'remote_friendly': job.remote_friendly,
                'application_url': job.application_url,
                'source_platform': job.source_platform,
                'posted_date': job.posted_date,
                'skills_required': job.skills_required,
                'benefits': job.benefits,
                'company_size': job.company_size,
                'industry': job.industry,
                'scraped_at': job.scraped_at,
                'match_score': getattr(job, 'match_score', 0)
            }
            jobs_data.append(job_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(jobs)} jobs to {output_file}")
        
        # Also save a summary
        summary = {
            'total_jobs': len(jobs),
            'platforms': list(set(job.source_platform for job in jobs)),
            'top_companies': list(set(job.company for job in jobs[:20])),
            'skill_distribution': self._analyze_skill_distribution(jobs),
            'location_distribution': self._analyze_location_distribution(jobs),
            'scraped_at': datetime.now().isoformat()
        }
        
        with open(output_dir / 'scraping_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _analyze_skill_distribution(self, jobs: List[JobListing]) -> Dict[str, int]:
        """Analyze skill distribution across jobs"""
        skill_count = {}
        for job in jobs:
            for skill in job.skills_required:
                skill_count[skill] = skill_count.get(skill, 0) + 1
        
        # Return top 20 skills
        return dict(sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def _analyze_location_distribution(self, jobs: List[JobListing]) -> Dict[str, int]:
        """Analyze location distribution across jobs"""
        location_count = {}
        for job in jobs:
            location = job.location
            location_count[location] = location_count.get(location, 0) + 1
        
        return dict(sorted(location_count.items(), key=lambda x: x[1], reverse=True)[:10])

async def main():
    """Main function to run universal job scraper"""
    print("🚀 UNIVERSAL JOB SCRAPER - AI-POWERED JOB DISCOVERY")
    print("🎯 Scraping jobs from LinkedIn, Indeed, RemoteOK and more...")
    print("🧠 Using AI for skill matching and job scoring")
    print("="*70)
    
    scraper = UniversalJobScraper()
    
    # Run scraping
    jobs = await scraper.scrape_all_platforms(
        min_match_score=0.6  # Only jobs with 60%+ match
    )
    
    print(f"\n📊 SCRAPING RESULTS")
    print("="*30)
    print(f"✅ Total High-Match Jobs Found: {len(jobs)}")
    
    if jobs:
        # Save results
        scraper.save_jobs(jobs, f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Show top matches
        print(f"\n🎯 TOP MATCHES:")
        for i, job in enumerate(jobs[:10]):
            match_score = getattr(job, 'match_score', 0)
            print(f"   {i+1}. {job.title} @ {job.company}")
            print(f"      📍 {job.location} | 🎯 {match_score:.2%} match | 🔗 {job.source_platform}")
        
        print(f"\n💡 Next steps:")
        print(f"   • Run auto-application script to apply to top matches")
        print(f"   • Check data/scraped_jobs/ for detailed results")
        print(f"   • Review job matches in the dashboard")
    
    return jobs

if __name__ == "__main__":
    asyncio.run(main())