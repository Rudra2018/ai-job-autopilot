#!/usr/bin/env python3
"""
🌐 Internet Job Scraper
Advanced web scraping engine to find exact and relevant job matches across the internet
"""

import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlencode, quote_plus
import random
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InternetJobScraper:
    """Advanced internet-wide job scraper for comprehensive job discovery"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Job search engines and career portals
        self.job_sources = {
            'indeed': {
                'base_url': 'https://www.indeed.com/jobs',
                'search_params': {'q': '{title}', 'l': '{location}', 'radius': '25'},
                'selectors': {
                    'jobs': '[data-jk]',
                    'title': 'h2.jobTitle a span',
                    'company': '.companyName',
                    'location': '.companyLocation',
                    'summary': '.job-snippet',
                    'salary': '.salary-snippet',
                    'link': 'h2.jobTitle a'
                }
            },
            'linkedin': {
                'base_url': 'https://www.linkedin.com/jobs/search',
                'search_params': {'keywords': '{title}', 'location': '{location}', 'f_TPR': 'r86400'},
                'selectors': {
                    'jobs': '.job-search-card',
                    'title': '.base-search-card__title',
                    'company': '.base-search-card__subtitle a',
                    'location': '.job-search-card__location',
                    'summary': '.job-search-card__summary',
                    'link': '.base-card__full-link'
                }
            },
            'glassdoor': {
                'base_url': 'https://www.glassdoor.com/Job/jobs.htm',
                'search_params': {'sc.keyword': '{title}', 'locT': 'C', 'locId': '1147401'},
                'selectors': {
                    'jobs': '[data-test="job-listing"]',
                    'title': '[data-test="job-title"]',
                    'company': '[data-test="employer-name"]',
                    'location': '[data-test="job-location"]',
                    'summary': '[data-test="job-description-snippet"]',
                    'salary': '[data-test="detailSalary"]'
                }
            },
            'monster': {
                'base_url': 'https://www.monster.com/jobs/search',
                'search_params': {'q': '{title}', 'where': '{location}'},
                'selectors': {
                    'jobs': '.job-cardstyle__JobCardComponent',
                    'title': '.job-title',
                    'company': '.company-name',
                    'location': '.job-location',
                    'summary': '.job-summary'
                }
            },
            'dice': {
                'base_url': 'https://www.dice.com/jobs',
                'search_params': {'q': '{title}', 'location': '{location}'},
                'selectors': {
                    'jobs': '[data-cy="search-result-card"]',
                    'title': '[data-cy="search-result-position-title"]',
                    'company': '[data-cy="search-result-company-name"]',
                    'location': '[data-cy="search-result-location"]',
                    'summary': '[data-cy="search-result-description"]'
                }
            }
        }
        
        # Company career pages
        self.company_career_pages = {
            'google': 'https://careers.google.com/jobs/results/',
            'microsoft': 'https://careers.microsoft.com/professionals/us/en/search-results',
            'apple': 'https://jobs.apple.com/en-us/search',
            'meta': 'https://www.metacareers.com/jobs/',
            'amazon': 'https://www.amazon.jobs/en/search',
            'netflix': 'https://jobs.netflix.com/search',
            'salesforce': 'https://salesforce.wd1.myworkdayjobs.com/External_Career_Site',
            'uber': 'https://www.uber.com/careers/list/',
            'airbnb': 'https://careers.airbnb.com/positions/',
            'stripe': 'https://stripe.com/jobs/search'
        }
        
        # Initialize Chrome driver options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
    
    async def search_jobs_across_internet(self, 
                                        job_titles: List[str], 
                                        locations: List[str] = None,
                                        company_preferences: List[str] = None,
                                        max_jobs_per_source: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs across all internet sources"""
        
        if locations is None:
            locations = ['Remote', 'San Francisco', 'New York', 'Seattle']
        
        logger.info(f"🌐 Starting comprehensive internet job search for {len(job_titles)} titles across {len(self.job_sources)} sources")
        
        all_jobs = []
        
        # Search major job boards
        for source_name, source_config in self.job_sources.items():
            try:
                logger.info(f"🔍 Searching {source_name}...")
                source_jobs = await self._search_job_source(
                    source_name, source_config, job_titles, locations, max_jobs_per_source
                )
                
                # Add source metadata
                for job in source_jobs:
                    job['source'] = source_name
                    job['source_type'] = 'job_board'
                
                all_jobs.extend(source_jobs)
                logger.info(f"✅ Found {len(source_jobs)} jobs from {source_name}")
                
                # Rate limiting
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"❌ Error searching {source_name}: {e}")
        
        # Search company career pages
        if company_preferences:
            for company in company_preferences:
                company_lower = company.lower()
                if company_lower in self.company_career_pages:
                    try:
                        logger.info(f"🏢 Searching {company} career page...")
                        company_jobs = await self._search_company_careers(
                            company_lower, job_titles, max_jobs_per_source // 2
                        )
                        
                        for job in company_jobs:
                            job['source'] = f"{company}_careers"
                            job['source_type'] = 'company_direct'
                            job['company'] = company
                        
                        all_jobs.extend(company_jobs)
                        logger.info(f"✅ Found {len(company_jobs)} jobs from {company}")
                        
                        await asyncio.sleep(random.uniform(2, 4))
                        
                    except Exception as e:
                        logger.error(f"❌ Error searching {company} careers: {e}")
        
        # Remove duplicates and enhance jobs
        unique_jobs = self._deduplicate_jobs(all_jobs)
        enhanced_jobs = self._enhance_job_data(unique_jobs, job_titles)
        
        # Sort by relevance score
        enhanced_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"🎯 Total unique jobs found: {len(enhanced_jobs)}")
        return enhanced_jobs
    
    async def _search_job_source(self, 
                                source_name: str, 
                                source_config: Dict[str, Any], 
                                job_titles: List[str], 
                                locations: List[str],
                                max_jobs: int) -> List[Dict[str, Any]]:
        """Search a specific job source"""
        
        jobs = []
        
        for title in job_titles[:3]:  # Limit to top 3 titles
            for location in locations[:2]:  # Limit to top 2 locations
                try:
                    # Build search URL
                    params = source_config['search_params'].copy()
                    for key, value in params.items():
                        params[key] = value.format(title=title, location=location)
                    
                    search_url = f"{source_config['base_url']}?{urlencode(params)}"
                    
                    # Fetch and parse jobs
                    source_jobs = await self._fetch_jobs_from_url(
                        search_url, source_config['selectors'], max_jobs // 4
                    )
                    
                    jobs.extend(source_jobs)
                    
                    if len(jobs) >= max_jobs:
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error searching {source_name} for {title} in {location}: {e}")
            
            if len(jobs) >= max_jobs:
                break
        
        return jobs[:max_jobs]
    
    async def _fetch_jobs_from_url(self, 
                                  url: str, 
                                  selectors: Dict[str, str], 
                                  max_jobs: int) -> List[Dict[str, Any]]:
        """Fetch and parse jobs from a URL"""
        
        try:
            # Use both requests and Selenium for different sites
            jobs = []
            
            # Try requests first (faster)
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    jobs = self._parse_jobs_from_html(response.text, selectors, max_jobs)
            except Exception as e:
                logger.warning(f"⚠️ Requests failed for {url}: {e}")
            
            # If no jobs found, try Selenium (handles JavaScript)
            if not jobs:
                jobs = await self._fetch_with_selenium(url, selectors, max_jobs)
            
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Error fetching {url}: {e}")
            return []
    
    def _parse_jobs_from_html(self, 
                             html: str, 
                             selectors: Dict[str, str], 
                             max_jobs: int) -> List[Dict[str, Any]]:
        """Parse jobs from HTML using BeautifulSoup"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            job_elements = soup.select(selectors.get('jobs', ''))
            
            jobs = []
            
            for job_elem in job_elements[:max_jobs]:
                try:
                    job = {
                        'title': self._extract_text(job_elem, selectors.get('title', '')),
                        'company': self._extract_text(job_elem, selectors.get('company', '')),
                        'location': self._extract_text(job_elem, selectors.get('location', '')),
                        'summary': self._extract_text(job_elem, selectors.get('summary', '')),
                        'salary': self._extract_text(job_elem, selectors.get('salary', '')),
                        'link': self._extract_link(job_elem, selectors.get('link', '')),
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Only add job if it has minimum required fields
                    if job['title'] and job['company']:
                        jobs.append(job)
                
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing job element: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Error parsing HTML: {e}")
            return []
    
    async def _fetch_with_selenium(self, 
                                  url: str, 
                                  selectors: Dict[str, str], 
                                  max_jobs: int) -> List[Dict[str, Any]]:
        """Fetch jobs using Selenium for JavaScript-heavy sites"""
        
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Wait for jobs to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors.get('jobs', '')))
            )
            
            # Scroll to load more jobs
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)
            
            # Get page source and parse
            html = driver.page_source
            jobs = self._parse_jobs_from_html(html, selectors, max_jobs)
            
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Selenium fetch error for {url}: {e}")
            return []
        
        finally:
            if driver:
                driver.quit()
    
    async def _search_company_careers(self, 
                                    company: str, 
                                    job_titles: List[str], 
                                    max_jobs: int) -> List[Dict[str, Any]]:
        """Search specific company career pages"""
        
        # This is a simplified implementation
        # In practice, each company would need custom scraping logic
        
        jobs = []
        base_url = self.company_career_pages.get(company)
        
        if not base_url:
            return jobs
        
        try:
            # Generic approach - would need customization per company
            for title in job_titles[:2]:
                search_url = f"{base_url}?q={quote_plus(title)}"
                
                # Simulate finding jobs (replace with actual scraping)
                company_jobs = [
                    {
                        'title': f"{title} - {company.title()}",
                        'company': company.title(),
                        'location': 'Multiple Locations',
                        'summary': f"Exciting {title} opportunity at {company.title()}",
                        'link': search_url,
                        'salary': 'Competitive',
                        'posted_date': datetime.now().strftime('%Y-%m-%d'),
                        'scraped_at': datetime.now().isoformat()
                    }
                ]
                
                jobs.extend(company_jobs)
                
                if len(jobs) >= max_jobs:
                    break
        
        except Exception as e:
            logger.error(f"❌ Error searching {company} careers: {e}")
        
        return jobs[:max_jobs]
    
    def _extract_text(self, element, selector: str) -> str:
        """Extract text from element using selector"""
        try:
            if selector:
                found = element.select_one(selector)
                return found.get_text(strip=True) if found else ''
            return ''
        except Exception:
            return ''
    
    def _extract_link(self, element, selector: str) -> str:
        """Extract link from element using selector"""
        try:
            if selector:
                found = element.select_one(selector)
                return found.get('href', '') if found else ''
            return ''
        except Exception:
            return ''
    
    def _deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on title and company"""
        
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            job_key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _enhance_job_data(self, jobs: List[Dict[str, Any]], search_titles: List[str]) -> List[Dict[str, Any]]:
        """Enhance job data with relevance scoring and additional metadata"""
        
        for job in jobs:
            try:
                # Calculate relevance score
                relevance_score = self._calculate_job_relevance(job, search_titles)
                job['relevance_score'] = relevance_score
                
                # Extract additional data
                job['requirements'] = self._extract_requirements(job.get('summary', ''))
                job['benefits'] = self._extract_benefits(job.get('summary', ''))
                job['job_type'] = self._detect_job_type(job.get('title', '') + ' ' + job.get('summary', ''))
                job['experience_level'] = self._detect_experience_level(job.get('title', '') + ' ' + job.get('summary', ''))
                
                # Standardize salary
                job['salary_display'] = self._standardize_salary(job.get('salary', ''))
                
            except Exception as e:
                logger.warning(f"⚠️ Error enhancing job data: {e}")
                job['relevance_score'] = 50  # Default score
        
        return jobs
    
    def _calculate_job_relevance(self, job: Dict[str, Any], search_titles: List[str]) -> int:
        """Calculate how relevant a job is to the search criteria"""
        
        score = 0
        job_text = f"{job.get('title', '')} {job.get('summary', '')}".lower()
        
        # Title matching (40% weight)
        title_score = 0
        job_title = job.get('title', '').lower()
        
        for search_title in search_titles:
            search_words = set(search_title.lower().split())
            title_words = set(job_title.split())
            
            # Exact match bonus
            if search_title.lower() in job_title:
                title_score = max(title_score, 100)
            else:
                # Word overlap scoring
                overlap = len(search_words.intersection(title_words))
                if search_words:
                    overlap_score = (overlap / len(search_words)) * 80
                    title_score = max(title_score, overlap_score)
        
        score += title_score * 0.4
        
        # Content relevance (30% weight)
        content_keywords = [
            'python', 'javascript', 'react', 'node', 'aws', 'docker', 'kubernetes',
            'senior', 'lead', 'architect', 'full-stack', 'backend', 'frontend'
        ]
        
        content_matches = sum(1 for keyword in content_keywords if keyword in job_text)
        content_score = min(100, (content_matches / len(content_keywords)) * 100)
        score += content_score * 0.3
        
        # Company reputation (15% weight)
        company = job.get('company', '').lower()
        premium_companies = [
            'google', 'microsoft', 'apple', 'meta', 'amazon', 'netflix',
            'salesforce', 'uber', 'airbnb', 'stripe', 'spotify', 'twitter'
        ]
        
        company_score = 80 if any(comp in company for comp in premium_companies) else 60
        score += company_score * 0.15
        
        # Recency (10% weight)
        recency_score = 90  # Assume recent since we're scraping
        score += recency_score * 0.1
        
        # Location bonus (5% weight)
        location = job.get('location', '').lower()
        location_score = 100 if 'remote' in location else 70
        score += location_score * 0.05
        
        return min(100, max(1, int(score)))
    
    def _extract_requirements(self, summary: str) -> List[str]:
        """Extract job requirements from summary"""
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(?:proficient|experience|skilled)\s*(?:in|with)\s*([^,.]+)',
            r'(?:must\s*have|required|need)\s*([^,.]+)',
            r'(?:bachelor|master|phd)\s*(?:degree|\'s)?(?:\s*in\s*([^,.]+))?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, summary, re.IGNORECASE)
            requirements.extend([match if isinstance(match, str) else match[0] for match in matches])
        
        return requirements[:5]  # Limit to top 5
    
    def _extract_benefits(self, summary: str) -> List[str]:
        """Extract job benefits from summary"""
        benefit_keywords = [
            'health insurance', 'dental', 'vision', '401k', 'retirement',
            'vacation', 'pto', 'remote work', 'flexible hours', 'stock options',
            'bonus', 'competitive salary', 'professional development'
        ]
        
        benefits = []
        summary_lower = summary.lower()
        
        for benefit in benefit_keywords:
            if benefit in summary_lower:
                benefits.append(benefit.title())
        
        return benefits
    
    def _detect_job_type(self, job_text: str) -> str:
        """Detect job type from job text"""
        job_text_lower = job_text.lower()
        
        if any(term in job_text_lower for term in ['contract', 'contractor', 'consulting']):
            return 'Contract'
        elif any(term in job_text_lower for term in ['part-time', 'part time']):
            return 'Part-time'
        elif any(term in job_text_lower for term in ['intern', 'internship']):
            return 'Internship'
        else:
            return 'Full-time'
    
    def _detect_experience_level(self, job_text: str) -> str:
        """Detect experience level from job text"""
        job_text_lower = job_text.lower()
        
        if any(term in job_text_lower for term in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(term in job_text_lower for term in ['junior', 'jr.', 'entry', 'graduate', 'associate']):
            return 'Entry'
        elif any(term in job_text_lower for term in ['mid', 'intermediate', '3-5 years', '2-4 years']):
            return 'Mid'
        else:
            return 'Mid'  # Default
    
    def _standardize_salary(self, salary: str) -> str:
        """Standardize salary display format"""
        if not salary:
            return 'Not specified'
        
        # Extract numbers and format consistently
        numbers = re.findall(r'\$?(\d+(?:,\d+)*(?:k|K)?)', salary)
        if numbers:
            return f"${numbers[0]}" if len(numbers) == 1 else f"${numbers[0]} - ${numbers[1]}"
        
        return salary

# Global instance
internet_scraper = InternetJobScraper()

async def search_jobs_across_internet(job_titles: List[str], 
                                     locations: List[str] = None,
                                     company_preferences: List[str] = None,
                                     max_jobs: int = 100) -> List[Dict[str, Any]]:
    """Main function to search jobs across the internet"""
    return await internet_scraper.search_jobs_across_internet(
        job_titles, locations, company_preferences, max_jobs
    )