#!/usr/bin/env python3
"""
Company Career Page Scraper with Dynamic Discovery
Automatically discovers and scrapes job postings from company career pages
"""

import asyncio
import json
import os
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin, urlunparse
import aiohttp
from playwright.async_api import async_playwright, Browser, Page
from dataclasses import dataclass
import hashlib
from pathlib import Path
import yaml
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

@dataclass
class CompanyInfo:
    name: str
    website: str
    career_url: str
    industry: str
    size: str
    locations: List[str]

class CompanyCareerDiscoverer:
    """Discovers company career pages from various sources"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.discovered_companies = []
        
        # Major tech companies to start with
        self.seed_companies = [
            {"name": "Google", "website": "https://google.com", "career_path": "/careers"},
            {"name": "Microsoft", "website": "https://microsoft.com", "career_path": "/careers"},
            {"name": "Amazon", "website": "https://amazon.com", "career_path": "/jobs"},
            {"name": "Apple", "website": "https://apple.com", "career_path": "/careers"},
            {"name": "Meta", "website": "https://meta.com", "career_path": "/careers"},
            {"name": "Netflix", "website": "https://netflix.com", "career_path": "/jobs"},
            {"name": "Tesla", "website": "https://tesla.com", "career_path": "/careers"},
            {"name": "Uber", "website": "https://uber.com", "career_path": "/careers"},
            {"name": "Airbnb", "website": "https://airbnb.com", "career_path": "/careers"},
            {"name": "Spotify", "website": "https://spotify.com", "career_path": "/jobs"},
            {"name": "Salesforce", "website": "https://salesforce.com", "career_path": "/careers"},
            {"name": "Oracle", "website": "https://oracle.com", "career_path": "/careers"},
            {"name": "IBM", "website": "https://ibm.com", "career_path": "/careers"},
            {"name": "Intel", "website": "https://intel.com", "career_path": "/jobs"},
            {"name": "Cisco", "website": "https://cisco.com", "career_path": "/careers"},
            # Financial companies
            {"name": "JPMorgan", "website": "https://jpmorgan.com", "career_path": "/careers"},
            {"name": "Goldman Sachs", "website": "https://goldmansachs.com", "career_path": "/careers"},
            {"name": "Morgan Stanley", "website": "https://morganstanley.com", "career_path": "/careers"},
            {"name": "Deutsche Bank", "website": "https://db.com", "career_path": "/careers"},
            {"name": "Barclays", "website": "https://barclays.com", "career_path": "/careers"},
            # Consulting
            {"name": "McKinsey", "website": "https://mckinsey.com", "career_path": "/careers"},
            {"name": "BCG", "website": "https://bcg.com", "career_path": "/careers"},
            {"name": "Bain", "website": "https://bain.com", "career_path": "/careers"},
            # European tech
            {"name": "SAP", "website": "https://sap.com", "career_path": "/careers"},
            {"name": "Siemens", "website": "https://siemens.com", "career_path": "/careers"},
            {"name": "ASML", "website": "https://asml.com", "career_path": "/careers"},
            {"name": "Adidas", "website": "https://adidas.com", "career_path": "/careers"},
            {"name": "BMW", "website": "https://bmw.com", "career_path": "/careers"},
            {"name": "Mercedes", "website": "https://mercedes-benz.com", "career_path": "/careers"},
            {"name": "Volkswagen", "website": "https://volkswagen.com", "career_path": "/careers"},
            # Startups and scale-ups
            {"name": "Stripe", "website": "https://stripe.com", "career_path": "/jobs"},
            {"name": "Shopify", "website": "https://shopify.com", "career_path": "/careers"},
            {"name": "Square", "website": "https://squareup.com", "career_path": "/careers"},
            {"name": "Coinbase", "website": "https://coinbase.com", "career_path": "/careers"},
            {"name": "Robinhood", "website": "https://robinhood.com", "career_path": "/careers"},
            {"name": "Palantir", "website": "https://palantir.com", "career_path": "/careers"},
            {"name": "Databricks", "website": "https://databricks.com", "career_path": "/careers"},
            {"name": "Snowflake", "website": "https://snowflake.com", "career_path": "/careers"}
        ]
    
    async def discover_from_crunchbase(self, keywords: List[str] = None) -> List[CompanyInfo]:
        """Discover companies from Crunchbase API"""
        if not keywords:
            keywords = ["cybersecurity", "fintech", "ai", "cloud computing", "enterprise software"]
        
        companies = []
        
        # Note: This would require Crunchbase API key in production
        # For demo, we'll use seed companies
        print("🔍 Using seed company database for discovery...")
        
        for company_data in self.seed_companies[:20]:  # Limit for demo
            try:
                company = CompanyInfo(
                    name=company_data["name"],
                    website=company_data["website"],
                    career_url=company_data["website"] + company_data["career_path"],
                    industry="Technology",  # Default for demo
                    size="Large",
                    locations=["Multiple"]
                )
                companies.append(company)
            except Exception as e:
                print(f"Error processing {company_data['name']}: {str(e)}")
                continue
        
        return companies
    
    async def discover_from_glassdoor(self, search_terms: List[str] = None) -> List[CompanyInfo]:
        """Discover companies from Glassdoor top employers lists"""
        if not search_terms:
            search_terms = ["best tech companies", "top cybersecurity companies"]
        
        companies = []
        
        # In a real implementation, this would scrape Glassdoor
        # For demo, returning additional companies
        additional_companies = [
            {"name": "CrowdStrike", "website": "https://crowdstrike.com", "career_path": "/careers"},
            {"name": "Palo Alto Networks", "website": "https://paloaltonetworks.com", "career_path": "/careers"},
            {"name": "Okta", "website": "https://okta.com", "career_path": "/careers"},
            {"name": "Zscaler", "website": "https://zscaler.com", "career_path": "/careers"},
            {"name": "SentinelOne", "website": "https://sentinelone.com", "career_path": "/careers"},
        ]
        
        for company_data in additional_companies:
            company = CompanyInfo(
                name=company_data["name"],
                website=company_data["website"],
                career_url=company_data["website"] + company_data["career_path"],
                industry="Cybersecurity",
                size="Medium",
                locations=["Multiple"]
            )
            companies.append(company)
        
        return companies
    
    def discover_career_page_patterns(self, base_url: str) -> List[str]:
        """Discover potential career page URLs from a company website"""
        parsed = urlparse(base_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common career page patterns
        career_patterns = [
            "/careers", "/careers/", "/jobs", "/jobs/", "/opportunities",
            "/career", "/career/", "/job", "/job/", "/work-with-us",
            "/join-us", "/hiring", "/employment", "/openings", "/positions",
            "/talent", "/open-positions", "/job-openings", "/job-opportunities",
            "/careers/jobs", "/careers/opportunities", "/about/careers",
            "/company/careers", "/work", "/work/", "/team/careers"
        ]
        
        potential_urls = []
        for pattern in career_patterns:
            potential_urls.append(base_domain + pattern)
        
        return potential_urls

class CompanyCareerScraper:
    """Scrapes job postings from company career pages"""
    
    def __init__(self):
        self.scraped_jobs = []
        self.failed_companies = []
        
        # Common selectors for different career page types
        self.job_selectors = {
            'greenhouse': {
                'job_list': '[data-board] .opening, .job-post',
                'title': 'h3, .opening-title, .job-title',
                'location': '.location, .opening-location',
                'department': '.department, .opening-department',
                'apply_link': 'a[href*="apply"], .apply-link'
            },
            'lever': {
                'job_list': '.posting, .lever-job',
                'title': '.posting-name, .lever-job-title h5',
                'location': '.posting-location, .lever-job-location',
                'department': '.posting-department, .lever-job-department',
                'apply_link': 'a[href*="apply"], .posting-apply'
            },
            'workday': {
                'job_list': '[data-automation-id="jobPosting"], .job-item',
                'title': '[data-automation-id="jobPostingTitle"], .job-title',
                'location': '[data-automation-id="locations"], .job-location',
                'department': '.job-department',
                'apply_link': 'a[href*="apply"], .apply-button'
            },
            'bamboohr': {
                'job_list': '.BambooHR-ATS-Jobs-Item, .job-listing',
                'title': '.BambooHR-ATS-Jobs-Item-Name, .job-title',
                'location': '.BambooHR-ATS-Jobs-Item-Location, .job-location',
                'department': '.job-department',
                'apply_link': 'a[href*="apply"], .apply-link'
            },
            'generic': {
                'job_list': '.job, .position, .opening, .career-item, [class*="job"], [class*="career"], [class*="position"]',
                'title': 'h1, h2, h3, .title, .job-title, .position-title, [class*="title"]',
                'location': '.location, .job-location, .position-location, [class*="location"]',
                'department': '.department, .team, [class*="department"]',
                'apply_link': 'a[href*="apply"], .apply, .btn-apply, [class*="apply"]'
            }
        }
    
    def detect_career_page_type(self, page_content: str) -> str:
        """Detect the type of career page system being used"""
        content_lower = page_content.lower()
        
        if 'greenhouse' in content_lower or 'boards.greenhouse.io' in content_lower:
            return 'greenhouse'
        elif 'lever' in content_lower or 'jobs.lever.co' in content_lower:
            return 'lever'
        elif 'workday' in content_lower or 'myworkdayjobs.com' in content_lower:
            return 'workday'
        elif 'bamboohr' in content_lower:
            return 'bamboohr'
        else:
            return 'generic'
    
    async def scrape_company_jobs(self, company: CompanyInfo, page: Page, keywords: List[str] = None) -> List[Dict]:
        """Scrape jobs from a specific company's career page"""
        if not keywords:
            keywords = [
                'security', 'cyber', 'engineer', 'developer', 'analyst',
                'penetration', 'vulnerability', 'compliance', 'risk'
            ]
        
        jobs = []
        
        try:
            print(f"🏢 Scraping {company.name}...")
            
            # Try the main career URL first
            career_urls = [company.career_url]
            
            # If main URL fails, try discovered patterns
            discoverer = CompanyCareerDiscoverer()
            potential_urls = discoverer.discover_career_page_patterns(company.website)
            career_urls.extend(potential_urls[:5])  # Try top 5 alternatives
            
            for url in career_urls:
                try:
                    await page.goto(url, timeout=15000)
                    await page.wait_for_timeout(random.randint(2000, 4000))
                    
                    # Handle cookie consent and popups
                    await self._handle_popups(page)
                    
                    # Get page content to detect career page type
                    content = await page.content()
                    page_type = self.detect_career_page_type(content)
                    
                    print(f"   📋 Detected career page type: {page_type}")
                    
                    # Get appropriate selectors
                    selectors = self.job_selectors.get(page_type, self.job_selectors['generic'])
                    
                    # Find job listings
                    job_elements = await page.locator(selectors['job_list']).all()
                    
                    if not job_elements:
                        print(f"   ⚠️  No job listings found with {page_type} selectors")
                        continue
                    
                    print(f"   📊 Found {len(job_elements)} job listings")
                    
                    for i, job_elem in enumerate(job_elements[:15]):  # Process first 15 jobs
                        try:
                            # Extract job details
                            title = await self._safe_text(job_elem.locator(selectors['title']))
                            location = await self._safe_text(job_elem.locator(selectors['location']))
                            department = await self._safe_text(job_elem.locator(selectors['department']))
                            
                            # Check if job matches our keywords
                            if not title or not any(keyword.lower() in title.lower() for keyword in keywords):
                                continue
                            
                            # Get apply link
                            apply_elem = job_elem.locator(selectors['apply_link'])
                            apply_url = ""
                            
                            if await apply_elem.count() > 0:
                                apply_url = await apply_elem.first.get_attribute('href') or ""
                                if apply_url and not apply_url.startswith('http'):
                                    apply_url = urljoin(url, apply_url)
                            
                            # Click to get job description
                            description = ""
                            try:
                                await job_elem.click()
                                await page.wait_for_timeout(2000)
                                
                                # Try various description selectors
                                desc_selectors = [
                                    '.job-description', '.posting-description', '.description',
                                    '.job-content', '.posting-content', '[class*="description"]'
                                ]
                                
                                for desc_sel in desc_selectors:
                                    desc_elem = page.locator(desc_sel)
                                    if await desc_elem.count() > 0:
                                        description = await self._safe_text(desc_elem)
                                        break
                            except:
                                pass
                            
                            if title:
                                job_id = hashlib.md5(f"{company.name}{title}{location}".encode()).hexdigest()[:12]
                                
                                job = {
                                    'id': f"{company.name.lower().replace(' ', '_')}_{job_id}",
                                    'title': title,
                                    'company': company.name,
                                    'location': location or 'Not specified',
                                    'department': department,
                                    'description': description[:1000],
                                    'apply_url': apply_url,
                                    'career_page_url': url,
                                    'company_website': company.website,
                                    'industry': company.industry,
                                    'company_size': company.size,
                                    'source': 'company_career_page',
                                    'scraped_at': datetime.now().isoformat(),
                                    'skills_required': self._extract_skills_from_description(description),
                                    'remote_friendly': self._is_remote_friendly(title, location, description)
                                }
                                
                                jobs.append(job)
                                print(f"   ✅ {title} ({location})")
                        
                        except Exception as e:
                            print(f"   ❌ Error processing job {i+1}: {str(e)}")
                            continue
                    
                    # If we found jobs, break from URL trying loop
                    if jobs:
                        break
                        
                except Exception as e:
                    print(f"   ❌ Error accessing {url}: {str(e)}")
                    continue
            
            if not jobs:
                self.failed_companies.append(company.name)
                print(f"   ❌ No matching jobs found for {company.name}")
            
        except Exception as e:
            print(f"   ❌ Error scraping {company.name}: {str(e)}")
            self.failed_companies.append(company.name)
        
        return jobs
    
    async def _handle_popups(self, page: Page):
        """Handle common popups and overlays"""
        popup_selectors = [
            'button:has-text("Accept")', 'button:has-text("Accept all")',
            'button:has-text("Agree")', 'button:has-text("OK")',
            'button:has-text("Close")', 'button[aria-label="Close"]',
            '.modal-close', '.popup-close', '.overlay-close',
            '[data-dismiss="modal"]', '.cookie-accept', '.gdpr-accept'
        ]
        
        for selector in popup_selectors:
            try:
                elem = page.locator(selector)
                if await elem.count() > 0:
                    await elem.first.click()
                    await page.wait_for_timeout(1000)
                    break
            except:
                continue
    
    async def _safe_text(self, locator) -> str:
        """Safely extract text from locator"""
        try:
            if await locator.count() > 0:
                text = await locator.first.text_content()
                return text.strip() if text else ""
        except:
            pass
        return ""
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract technical skills from job description"""
        if not description:
            return []
        
        skills_database = [
            # Programming languages
            'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
            # Security skills
            'cybersecurity', 'penetration testing', 'vulnerability assessment',
            'incident response', 'threat modeling', 'risk assessment',
            'security architecture', 'compliance', 'gdpr', 'iso 27001',
            'network security', 'cloud security', 'application security',
            # Cloud platforms
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            # Tools and frameworks
            'terraform', 'ansible', 'jenkins', 'git', 'linux', 'windows'
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in skills_database:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _is_remote_friendly(self, title: str, location: str, description: str) -> bool:
        """Determine if job is remote-friendly"""
        remote_indicators = ['remote', 'work from home', 'distributed', 'anywhere', 'hybrid']
        
        combined_text = f"{title} {location} {description}".lower()
        
        return any(indicator in combined_text for indicator in remote_indicators)

class CompanyJobPipeline:
    """Complete pipeline for company job discovery and scraping"""
    
    def __init__(self):
        self.discoverer = CompanyCareerDiscoverer()
        self.scraper = CompanyCareerScraper()
        self.all_jobs = []
        
        # Load user preferences
        self.load_user_preferences()
    
    def load_user_preferences(self):
        """Load user job preferences"""
        try:
            with open('config/user_profile.yaml', 'r') as f:
                self.user_profile = yaml.safe_load(f)
        except:
            self.user_profile = {
                'preferred_keywords': [
                    'security engineer', 'cybersecurity', 'penetration tester',
                    'cloud security', 'application security', 'security analyst'
                ],
                'preferred_locations': ['Remote', 'Berlin', 'Munich', 'London'],
                'experience_level': 'senior',
                'industries': ['Technology', 'Financial Services', 'Cybersecurity']
            }
    
    async def run_full_pipeline(self, max_companies: int = 50) -> List[Dict]:
        """Run the complete company job discovery and scraping pipeline"""
        print("🚀 COMPANY CAREER PAGE PIPELINE")
        print("🔍 Step 1: Discovering companies...")
        print("="*50)
        
        # Discover companies
        discovered_companies = []
        
        # From Crunchbase-style discovery
        cb_companies = await self.discoverer.discover_from_crunchbase()
        discovered_companies.extend(cb_companies)
        
        # From Glassdoor-style discovery  
        gd_companies = await self.discoverer.discover_from_glassdoor()
        discovered_companies.extend(gd_companies)
        
        # Limit companies to process
        companies_to_process = discovered_companies[:max_companies]
        
        print(f"✅ Discovered {len(companies_to_process)} companies to scrape")
        
        # Scraping phase
        print(f"\n🏢 Step 2: Scraping company career pages...")
        print("="*50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Process companies in batches
            batch_size = 5
            for i in range(0, len(companies_to_process), batch_size):
                batch = companies_to_process[i:i + batch_size]
                
                print(f"\n📦 Processing batch {i//batch_size + 1} ({len(batch)} companies)...")
                
                for company in batch:
                    jobs = await self.scraper.scrape_company_jobs(
                        company, 
                        page, 
                        self.user_profile.get('preferred_keywords')
                    )
                    
                    self.all_jobs.extend(jobs)
                    
                    # Random delay between companies
                    await asyncio.sleep(random.randint(3, 7))
                
                # Longer delay between batches
                if i + batch_size < len(companies_to_process):
                    print(f"   ⏸️  Resting between batches...")
                    await asyncio.sleep(random.randint(10, 20))
            
            await browser.close()
        
        # Save results
        self.save_results()
        
        return self.all_jobs
    
    def save_results(self):
        """Save scraping results to files"""
        output_dir = Path("data/company_jobs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save all jobs
        jobs_file = output_dir / f"company_jobs_{timestamp}.json"
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_jobs, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary = {
            'total_jobs_found': len(self.all_jobs),
            'companies_with_jobs': len(set(job['company'] for job in self.all_jobs)),
            'failed_companies': self.scraper.failed_companies,
            'top_companies': self._get_top_companies(),
            'skill_distribution': self._analyze_skills(),
            'location_distribution': self._analyze_locations(),
            'scraped_at': datetime.now().isoformat()
        }
        
        summary_file = output_dir / f"scraping_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to:")
        print(f"   📄 Jobs: {jobs_file}")
        print(f"   📊 Summary: {summary_file}")
    
    def _get_top_companies(self) -> List[Dict]:
        """Get companies with most job postings"""
        company_counts = {}
        for job in self.all_jobs:
            company = job['company']
            company_counts[company] = company_counts.get(company, 0) + 1
        
        return [
            {'company': company, 'job_count': count}
            for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _analyze_skills(self) -> Dict[str, int]:
        """Analyze skill distribution across all jobs"""
        skill_counts = {}
        for job in self.all_jobs:
            for skill in job.get('skills_required', []):
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def _analyze_locations(self) -> Dict[str, int]:
        """Analyze location distribution"""
        location_counts = {}
        for job in self.all_jobs:
            location = job['location']
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10])

async def main():
    """Main function to run company career scraping pipeline"""
    print("🏢 COMPANY CAREER PAGE SCRAPER")
    print("🎯 Discovering and scraping jobs from company websites")
    print("🧠 AI-powered job matching and skill extraction")
    print("="*70)
    
    pipeline = CompanyJobPipeline()
    
    # Run the full pipeline
    jobs = await pipeline.run_full_pipeline(max_companies=30)
    
    print(f"\n📊 FINAL RESULTS")
    print("="*30)
    print(f"✅ Total Jobs Found: {len(jobs)}")
    print(f"🏢 Companies Processed: {len(set(job['company'] for job in jobs))}")
    print(f"❌ Failed Companies: {len(pipeline.scraper.failed_companies)}")
    
    if jobs:
        print(f"\n🎯 TOP MATCHES:")
        for i, job in enumerate(jobs[:10]):
            print(f"   {i+1}. {job['title']} @ {job['company']}")
            print(f"      📍 {job['location']} | 🏭 {job.get('department', 'N/A')}")
        
        print(f"\n💡 Next steps:")
        print(f"   • Review jobs in data/company_jobs/")
        print(f"   • Run auto-application on selected jobs")
        print(f"   • Check failed companies for manual review")
    
    return jobs

if __name__ == "__main__":
    asyncio.run(main())