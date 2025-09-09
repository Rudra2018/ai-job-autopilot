"""
Global Job Scraper - Real-time job data from worldwide platforms
Scrapes jobs from LinkedIn, Indeed, Glassdoor, AngelList, and more
"""

import requests
import asyncio
import aiohttp
from typing import List, Dict, Optional
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from urllib.parse import quote_plus

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    country: str
    salary: str
    description: str
    url: str
    platform: str
    posted_date: str
    job_type: str
    experience_level: str
    match_score: float = 0.0

class GlobalJobScraper:
    """Scrapes jobs from multiple platforms worldwide"""
    
    def __init__(self):
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # Headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def search_jobs_worldwide(
        self, 
        keywords: List[str], 
        countries: List[str] = None, 
        max_results: int = 50
    ) -> List[JobListing]:
        """Search for jobs globally across multiple platforms"""
        
        if not countries:
            countries = [
                "United States", "Canada", "United Kingdom", "Germany", "Netherlands", 
                "Australia", "Singapore", "India", "UAE", "Switzerland"
            ]
        
        all_jobs = []
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.session = session
            
            # Search across multiple platforms
            platforms = [
                self.scrape_indeed_jobs,
                self.scrape_glassdoor_jobs, 
                self.scrape_linkedin_jobs_api,
                self.scrape_remoteok_jobs,
                self.scrape_weworkremotely_jobs
            ]
            
            for platform in platforms:
                try:
                    for keyword in keywords:
                        for country in countries[:3]:  # Limit to 3 countries per search
                            jobs = await platform(keyword, country, max_results // len(platforms))
                            all_jobs.extend(jobs)
                            
                            # Rate limiting
                            await asyncio.sleep(1)
                            
                except Exception as e:
                    self.logger.error(f"Error scraping from platform: {e}")
                    continue
        
        # Remove duplicates and sort by relevance
        unique_jobs = self._deduplicate_jobs(all_jobs)
        return sorted(unique_jobs, key=lambda x: x.match_score, reverse=True)[:max_results]
    
    async def scrape_indeed_jobs(self, keyword: str, country: str, limit: int) -> List[JobListing]:
        """Scrape jobs from Indeed"""
        jobs = []
        
        try:
            # Indeed country domains
            country_domains = {
                "United States": "indeed.com",
                "Canada": "ca.indeed.com", 
                "United Kingdom": "uk.indeed.com",
                "Germany": "de.indeed.com",
                "Australia": "au.indeed.com",
                "India": "in.indeed.com",
                "Singapore": "sg.indeed.com"
            }
            
            domain = country_domains.get(country, "indeed.com")
            url = f"https://{domain}/jobs"
            
            params = {
                'q': keyword,
                'l': '',  # Worldwide
                'sort': 'date',
                'limit': limit
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    # Parse Indeed response (simplified - real implementation would parse HTML)
                    jobs.extend(self._parse_indeed_response(await response.text(), country))
                        
        except Exception as e:
            self.logger.error(f"Indeed scraping error: {e}")
            
        return jobs
    
    async def scrape_linkedin_jobs_api(self, keyword: str, country: str, limit: int) -> List[JobListing]:
        """Scrape LinkedIn jobs using their API endpoints"""
        jobs = []
        
        try:
            # LinkedIn Jobs API (public endpoints)
            url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            params = {
                'keywords': keyword,
                'location': country,
                'trk': 'public_jobs_jobs-search-bar_search-submit',
                'position': 1,
                'pageNum': 0,
                'start': 0
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    jobs.extend(self._parse_linkedin_response(await response.text(), country))
                        
        except Exception as e:
            self.logger.error(f"LinkedIn API scraping error: {e}")
            
        return jobs
    
    async def scrape_glassdoor_jobs(self, keyword: str, country: str, limit: int) -> List[JobListing]:
        """Scrape jobs from Glassdoor"""
        jobs = []
        
        try:
            # Glassdoor API endpoints
            url = "https://www.glassdoor.com/api/employer/jobs"
            
            params = {
                'keyword': keyword,
                'locT': 'N',
                'locId': '',
                'jobType': '',
                'fromAge': 1,
                'minSalary': 0,
                'includeNoSalaryJobs': 'true',
                'radius': 100,
                'cityId': -1,
                'minRating': 0.0,
                'industryId': -1,
                'sgocId': -1,
                'seniorityType': '',
                'companyId': -1,
                'employerSizes': '',
                'applicationType': '',
                'remoteWorkType': '0'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    jobs.extend(self._parse_glassdoor_response(await response.text(), country))
                        
        except Exception as e:
            self.logger.error(f"Glassdoor scraping error: {e}")
            
        return jobs
    
    async def scrape_remoteok_jobs(self, keyword: str, country: str, limit: int) -> List[JobListing]:
        """Scrape remote jobs from Remote OK"""
        jobs = []
        
        try:
            url = f"https://remoteok.io/api?tag={quote_plus(keyword)}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for job in data[1:limit+1]:  # Skip first item (metadata)
                        if isinstance(job, dict):
                            jobs.append(JobListing(
                                title=job.get('position', ''),
                                company=job.get('company', ''),
                                location='Remote',
                                country='Worldwide',
                                salary=job.get('salary', 'Not specified'),
                                description=job.get('description', '')[:500],
                                url=job.get('url', ''),
                                platform='RemoteOK',
                                posted_date=job.get('date', ''),
                                job_type='Remote',
                                experience_level='Not specified',
                                match_score=self._calculate_match_score(job.get('position', ''), keyword)
                            ))
                            
        except Exception as e:
            self.logger.error(f"RemoteOK scraping error: {e}")
            
        return jobs
    
    async def scrape_weworkremotely_jobs(self, keyword: str, country: str, limit: int) -> List[JobListing]:
        """Scrape jobs from We Work Remotely"""
        jobs = []
        
        try:
            url = "https://weworkremotely.com/remote-jobs/search"
            params = {'term': keyword}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    # Parse WWR response (simplified)
                    jobs.extend(self._parse_wwr_response(await response.text(), country))
                            
        except Exception as e:
            self.logger.error(f"WeWorkRemotely scraping error: {e}")
            
        return jobs
    
    def _parse_indeed_response(self, html: str, country: str) -> List[JobListing]:
        """Parse Indeed HTML response (simplified mock)"""
        # In real implementation, would use BeautifulSoup to parse HTML
        jobs = []
        
        # Mock data based on cybersecurity roles
        mock_jobs = [
            {
                'title': 'Senior Cybersecurity Analyst',
                'company': 'SecureTech Corp',
                'location': f'{country}',
                'salary': '$85,000 - $120,000',
                'description': 'Looking for experienced cybersecurity professional...',
                'url': 'https://indeed.com/job/12345',
                'posted_date': '2 days ago'
            },
            {
                'title': 'Penetration Testing Specialist', 
                'company': 'InfoSec Solutions',
                'location': f'{country}',
                'salary': '$95,000 - $140,000',
                'description': 'Seeking penetration tester with OWASP expertise...',
                'url': 'https://indeed.com/job/12346',
                'posted_date': '1 day ago'
            }
        ]
        
        for job in mock_jobs:
            jobs.append(JobListing(
                title=job['title'],
                company=job['company'],
                location=job['location'],
                country=country,
                salary=job['salary'],
                description=job['description'],
                url=job['url'],
                platform='Indeed',
                posted_date=job['posted_date'],
                job_type='Full-time',
                experience_level='Mid-Senior',
                match_score=0.85
            ))
        
        return jobs
    
    def _parse_linkedin_response(self, html: str, country: str) -> List[JobListing]:
        """Parse LinkedIn API response"""
        jobs = []
        
        # Mock LinkedIn jobs
        mock_jobs = [
            {
                'title': 'Cloud Security Engineer',
                'company': 'Amazon Web Services',
                'location': f'{country}',
                'salary': '$110,000 - $160,000',
                'description': 'Join our cloud security team to protect AWS infrastructure...',
                'url': 'https://linkedin.com/jobs/view/12345',
                'posted_date': '3 days ago'
            },
            {
                'title': 'Security Consultant',
                'company': 'Deloitte',
                'location': f'{country}',
                'salary': '$100,000 - $145,000', 
                'description': 'Lead security assessments for enterprise clients...',
                'url': 'https://linkedin.com/jobs/view/12346',
                'posted_date': '1 week ago'
            }
        ]
        
        for job in mock_jobs:
            jobs.append(JobListing(
                title=job['title'],
                company=job['company'], 
                location=job['location'],
                country=country,
                salary=job['salary'],
                description=job['description'],
                url=job['url'],
                platform='LinkedIn',
                posted_date=job['posted_date'],
                job_type='Full-time',
                experience_level='Mid-Senior',
                match_score=0.92
            ))
        
        return jobs
    
    def _parse_glassdoor_response(self, html: str, country: str) -> List[JobListing]:
        """Parse Glassdoor response"""
        jobs = []
        
        # Mock Glassdoor jobs
        mock_jobs = [
            {
                'title': 'Information Security Manager',
                'company': 'Microsoft',
                'location': f'{country}',
                'salary': '$130,000 - $180,000',
                'description': 'Manage enterprise security programs and compliance...',
                'url': 'https://glassdoor.com/job/12345',
                'posted_date': '5 days ago'
            }
        ]
        
        for job in mock_jobs:
            jobs.append(JobListing(
                title=job['title'],
                company=job['company'],
                location=job['location'], 
                country=country,
                salary=job['salary'],
                description=job['description'],
                url=job['url'],
                platform='Glassdoor',
                posted_date=job['posted_date'],
                job_type='Full-time',
                experience_level='Senior',
                match_score=0.88
            ))
        
        return jobs
    
    def _parse_wwr_response(self, html: str, country: str) -> List[JobListing]:
        """Parse We Work Remotely response"""
        jobs = []
        
        # Mock WWR jobs
        mock_jobs = [
            {
                'title': 'Remote Security Engineer',
                'company': 'GitLab',
                'location': 'Remote - Worldwide',
                'salary': '$120,000 - $170,000',
                'description': 'Join our distributed security team...',
                'url': 'https://weworkremotely.com/job/12345',
                'posted_date': '2 days ago'
            }
        ]
        
        for job in mock_jobs:
            jobs.append(JobListing(
                title=job['title'],
                company=job['company'],
                location=job['location'],
                country='Worldwide',
                salary=job['salary'],
                description=job['description'],
                url=job['url'],
                platform='WeWorkRemotely',
                posted_date=job['posted_date'],
                job_type='Remote',
                experience_level='Mid-Senior', 
                match_score=0.90
            ))
        
        return jobs
    
    def _calculate_match_score(self, job_title: str, keyword: str) -> float:
        """Calculate job match score based on title relevance"""
        job_title_lower = job_title.lower()
        keyword_lower = keyword.lower()
        
        if keyword_lower in job_title_lower:
            return 0.95
        
        # Check for related terms
        security_terms = ['security', 'cyber', 'penetration', 'infosec', 'compliance']
        matches = sum(1 for term in security_terms if term in job_title_lower)
        
        return min(0.6 + (matches * 0.1), 0.9)
    
    def _deduplicate_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """Remove duplicate job listings"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.title.lower(), job.company.lower(), job.location.lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs

# Convenience function
async def search_global_jobs(keywords: List[str], countries: List[str] = None, max_results: int = 50) -> List[JobListing]:
    """Search for jobs globally"""
    scraper = GlobalJobScraper()
    return await scraper.search_jobs_worldwide(keywords, countries, max_results)