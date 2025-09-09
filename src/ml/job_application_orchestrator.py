#!/usr/bin/env python3
"""
Job Application Orchestrator
Main system that orchestrates the entire automated job application pipeline
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import yaml
import random
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Import our custom modules
from advanced_resume_parser import ResumeParser, ParsedResume
from universal_job_scraper import UniversalJobScraper, JobListing
from company_career_scraper import CompanyJobPipeline, CompanyInfo
from intelligent_job_matcher import AIJobMatcher, JobRequirement, MatchResult
from auto_form_filler import IndustryStandardFormFiller, ApplicationData
from undetected_browser import UndetectedBrowser
from smart_duplicate_detector import SmartDuplicateDetector

@dataclass
class ApplicationSession:
    session_id: str
    start_time: str
    resume_file: str
    user_preferences: Dict
    scraped_jobs: List[Dict]
    matched_jobs: List[Dict]
    applied_jobs: List[Dict]
    failed_applications: List[Dict]
    session_stats: Dict
    end_time: Optional[str] = None

@dataclass
class ApplicationResult:
    job_id: str
    job_title: str
    company: str
    application_url: str
    status: str  # success, failed, skipped, review_required
    applied_at: str
    match_score: float
    form_fields_filled: int
    files_uploaded: List[str]
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None

class JobApplicationOrchestrator:
    """Main orchestrator for the entire job application pipeline"""
    
    def __init__(self, config_path: str = "config/application_config.yaml"):
        self.config = self._load_config(config_path)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        self.resume_parser = ResumeParser()
        self.job_scraper = UniversalJobScraper()
        self.company_scraper = CompanyJobPipeline()
        self.job_matcher = AIJobMatcher()
        self.form_filler = IndustryStandardFormFiller()
        self.duplicate_detector = SmartDuplicateDetector()
        
        # Session tracking
        self.parsed_resume = None
        self.application_session = None
        self.browser_context = None
        
        # Setup logging
        self._setup_logging()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'resume': {
                'file_path': 'config/resume.pdf',
                'auto_parse': True
            },
            'scraping': {
                'enabled_platforms': ['linkedin', 'indeed', 'remoteok'],
                'enable_company_scraping': True,
                'max_jobs_per_platform': 50,
                'max_companies': 20,
                'keywords': [
                    'cybersecurity engineer', 'security engineer', 'penetration tester',
                    'cloud security', 'application security', 'security analyst'
                ],
                'use_proxy_rotation': False
            },
            'matching': {
                'min_match_score': 0.6,
                'max_applications_per_session': 20,
                'prioritize_remote': True,
                'auto_apply_threshold': 0.8
            },
            'application': {
                'auto_submit': False,  # For safety, require manual review
                'save_screenshots': True,
                'delay_between_applications': {'min': 30, 'max': 120},  # seconds
                'max_retries': 2,
                'skip_duplicate_companies': True
            },
            'user_preferences': {
                'preferred_locations': ['Remote', 'Berlin', 'Munich', 'Hamburg'],
                'min_salary': 80000,
                'job_types': ['full-time'],
                'industries': ['Technology', 'Financial Services', 'Cybersecurity'],
                'work_authorization': 'Yes',
                'sponsorship_required': 'No',
                'availability': 'Two weeks notice'
            },
            'notifications': {
                'email_updates': True,
                'slack_webhook': None,
                'desktop_notifications': True
            }
        }
    
    def _setup_logging(self):
        """Setup logging for the session"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"job_application_{self.session_id}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Job Application Orchestrator initialized - Session: {self.session_id}")
    
    async def run_complete_pipeline(self) -> ApplicationSession:
        """Run the complete job application pipeline"""
        self.logger.info("🚀 Starting complete job application pipeline")
        
        start_time = datetime.now()
        
        # Initialize session
        self.application_session = ApplicationSession(
            session_id=self.session_id,
            start_time=start_time.isoformat(),
            resume_file=self.config['resume']['file_path'],
            user_preferences=self.config['user_preferences'],
            scraped_jobs=[],
            matched_jobs=[],
            applied_jobs=[],
            failed_applications=[],
            session_stats={}
        )
        
        try:
            # Step 1: Parse resume
            await self._step_parse_resume()
            
            # Step 2: Scrape jobs
            await self._step_scrape_jobs()
            
            # Step 3: Match jobs
            await self._step_match_jobs()
            
            # Step 4: Apply to jobs
            await self._step_apply_to_jobs()
            
            # Step 5: Generate session summary
            await self._step_generate_summary()
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise
        finally:
            # Cleanup
            if self.browser_context:
                await self.browser_context.close()
            
            self.application_session.end_time = datetime.now().isoformat()
            await self._save_session_data()
        
        return self.application_session
    
    async def _step_parse_resume(self):
        """Step 1: Parse the resume"""
        self.logger.info("📄 Step 1: Parsing resume...")
        
        resume_path = self.config['resume']['file_path']
        if not Path(resume_path).exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        
        self.parsed_resume = self.resume_parser.parse_resume(resume_path)
        
        self.logger.info(f"✅ Resume parsed successfully:")
        self.logger.info(f"   👤 Name: {self.parsed_resume.contact_info.name}")
        self.logger.info(f"   🎯 Domain: {self.parsed_resume.primary_domain}")
        self.logger.info(f"   📊 Experience: {self.parsed_resume.total_experience_years:.1f} years")
        self.logger.info(f"   🔧 Skills: {len(self._flatten_skills(self.parsed_resume.skills))}")
    
    async def _step_scrape_jobs(self):
        """Step 2: Scrape jobs from various sources"""
        self.logger.info("🔍 Step 2: Scraping jobs from multiple sources...")
        
        all_jobs = []
        
        # Scrape from job portals
        if self.config['scraping']['enabled_platforms']:
            self.logger.info("   🌐 Scraping job portals...")
            portal_jobs = await self.job_scraper.scrape_all_platforms(
                keywords=self.config['scraping']['keywords'],
                locations=self.config['user_preferences']['preferred_locations'],
                min_match_score=0.4  # Lower threshold for scraping, we'll filter later
            )
            
            # Convert JobListing objects to dictionaries
            for job in portal_jobs:
                job_dict = self._job_listing_to_dict(job)
                all_jobs.append(job_dict)
            
            self.logger.info(f"   ✅ Found {len(portal_jobs)} jobs from job portals")
        
        # Scrape from company career pages
        if self.config['scraping']['enable_company_scraping']:
            self.logger.info("   🏢 Scraping company career pages...")
            company_jobs = await self.company_scraper.run_full_pipeline(
                max_companies=self.config['scraping']['max_companies']
            )
            
            all_jobs.extend(company_jobs)
            self.logger.info(f"   ✅ Found {len(company_jobs)} jobs from company pages")
        
        # Remove duplicates
        self.logger.info("   🔍 Removing duplicate jobs...")
        unique_jobs = await self._remove_duplicate_jobs(all_jobs)
        
        self.application_session.scraped_jobs = unique_jobs
        self.logger.info(f"✅ Total unique jobs scraped: {len(unique_jobs)}")
    
    async def _step_match_jobs(self):
        """Step 3: Match jobs with resume using AI"""
        self.logger.info("🎯 Step 3: Matching jobs with resume...")
        
        # Convert scraped jobs to JobRequirement objects
        job_requirements = []
        for job_data in self.application_session.scraped_jobs:
            job_req = self._dict_to_job_requirement(job_data)
            if job_req:
                job_requirements.append(job_req)
        
        # Perform matching
        matches = self.job_matcher.batch_match_jobs(
            resume=self.parsed_resume,
            jobs=job_requirements,
            user_preferences=self.config['user_preferences'],
            top_n=self.config['matching']['max_applications_per_session'] * 2  # Get more matches than we'll apply to
        )
        
        # Filter by minimum match score
        min_score = self.config['matching']['min_match_score']
        filtered_matches = [match for match in matches if match.overall_score >= min_score]
        
        # Convert to dictionaries for storage
        matched_jobs = []
        for match in filtered_matches:
            match_dict = asdict(match)
            matched_jobs.append(match_dict)
        
        self.application_session.matched_jobs = matched_jobs
        self.logger.info(f"✅ Found {len(filtered_matches)} high-quality matches (≥{min_score:.0%})")
    
    async def _step_apply_to_jobs(self):
        """Step 4: Apply to matched jobs"""
        self.logger.info("📝 Step 4: Applying to matched jobs...")
        
        if not self.application_session.matched_jobs:
            self.logger.warning("No matched jobs found to apply to")
            return
        
        # Setup browser
        await self._setup_browser()
        
        # Apply to jobs
        applied_count = 0
        max_applications = self.config['matching']['max_applications_per_session']
        
        for i, match_data in enumerate(self.application_session.matched_jobs[:max_applications]):
            try:
                self.logger.info(f"🎯 Applying to job {i+1}/{min(max_applications, len(self.application_session.matched_jobs))}")
                
                # Apply to job
                result = await self._apply_to_single_job(match_data)
                
                if result.status == 'success':
                    self.application_session.applied_jobs.append(asdict(result))
                    applied_count += 1
                    self.logger.info(f"   ✅ Successfully applied to {result.job_title} @ {result.company}")
                else:
                    self.application_session.failed_applications.append(asdict(result))
                    self.logger.warning(f"   ⚠️  Failed to apply to {result.job_title} @ {result.company}: {result.error_message}")
                
                # Random delay between applications
                if i < len(self.application_session.matched_jobs) - 1:
                    delay = random.randint(
                        self.config['application']['delay_between_applications']['min'],
                        self.config['application']['delay_between_applications']['max']
                    )
                    self.logger.info(f"   ⏸️  Waiting {delay}s before next application...")
                    await asyncio.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"   ❌ Error applying to job {i+1}: {str(e)}")
                error_result = ApplicationResult(
                    job_id=match_data.get('job_id', 'unknown'),
                    job_title=match_data.get('job_title', 'unknown'),
                    company=match_data.get('company', 'unknown'),
                    application_url='',
                    status='failed',
                    applied_at=datetime.now().isoformat(),
                    match_score=match_data.get('overall_score', 0),
                    form_fields_filled=0,
                    files_uploaded=[],
                    error_message=str(e)
                )
                self.application_session.failed_applications.append(asdict(error_result))
        
        self.logger.info(f"✅ Application phase completed:")
        self.logger.info(f"   📝 Successfully applied: {len(self.application_session.applied_jobs)}")
        self.logger.info(f"   ❌ Failed applications: {len(self.application_session.failed_applications)}")
    
    async def _setup_browser(self):
        """Setup browser for job applications"""
        self.logger.info("🌐 Setting up browser...")
        
        playwright = await async_playwright().__aenter__()
        
        browser = await playwright.chromium.launch(
            headless=False,  # Keep visible for debugging
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-dev-shm-usage',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        self.browser_context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9'
            }
        )
        
        self.logger.info("✅ Browser setup completed")
    
    async def _apply_to_single_job(self, match_data: Dict) -> ApplicationResult:
        """Apply to a single job"""
        job_id = match_data.get('job_id', 'unknown')
        job_title = match_data.get('job_title', 'unknown')  
        company = match_data.get('company', 'unknown')
        application_url = match_data.get('application_url', '')
        
        self.logger.info(f"   📝 Applying to: {job_title} @ {company}")
        
        # Check for duplicates
        if self.config['application']['skip_duplicate_companies']:
            applied_companies = [job['company'] for job in self.application_session.applied_jobs]
            if company in applied_companies:
                return ApplicationResult(
                    job_id=job_id,
                    job_title=job_title,
                    company=company,
                    application_url=application_url,
                    status='skipped',
                    applied_at=datetime.now().isoformat(),
                    match_score=match_data.get('overall_score', 0),
                    form_fields_filled=0,
                    files_uploaded=[],
                    error_message='Duplicate company - already applied'
                )
        
        # Create application data
        application_data = self.form_filler.create_application_data(
            resume=self.parsed_resume,
            job_specific_data={
                'company': company,
                'position': job_title,
                **self.config['user_preferences']
            }
        )
        
        # Create new page for this application
        page = await self.browser_context.new_page()
        
        try:
            # Navigate to application URL
            if application_url:
                await page.goto(application_url, timeout=30000)
                await page.wait_for_timeout(3000)
            
            # Fill the form
            fill_results = await self.form_filler.fill_form(page, application_data, application_url)
            
            # Take screenshot if enabled
            screenshot_path = None
            if self.config['application']['save_screenshots']:
                screenshot_dir = Path(f"screenshots/{self.session_id}")
                screenshot_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = screenshot_dir / f"{job_id}_{company.replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_path)
            
            # Review form before submission
            review_results = await self.form_filler.review_before_submit(page)
            
            # Determine application status
            if review_results['form_ready'] and not self.config['application']['auto_submit']:
                status = 'review_required'
                self.logger.info(f"   ⏸️  Form filled successfully - manual review required")
            elif review_results['form_ready'] and self.config['application']['auto_submit']:
                # Submit the form (implement submission logic here if needed)
                status = 'success'
                self.logger.info(f"   ✅ Form submitted successfully")
            else:
                status = 'failed'
                self.logger.warning(f"   ❌ Form not ready for submission")
            
            return ApplicationResult(
                job_id=job_id,
                job_title=job_title,
                company=company,
                application_url=application_url,
                status=status,
                applied_at=datetime.now().isoformat(),
                match_score=match_data.get('overall_score', 0),
                form_fields_filled=len(fill_results.get('filled_fields', [])),
                files_uploaded=fill_results.get('uploaded_files', []),
                screenshot_path=str(screenshot_path) if screenshot_path else None,
                error_message='; '.join(fill_results.get('errors', []))
            )
            
        except Exception as e:
            return ApplicationResult(
                job_id=job_id,
                job_title=job_title,
                company=company,
                application_url=application_url,
                status='failed',
                applied_at=datetime.now().isoformat(),
                match_score=match_data.get('overall_score', 0),
                form_fields_filled=0,
                files_uploaded=[],
                error_message=str(e)
            )
        finally:
            await page.close()
    
    async def _step_generate_summary(self):
        """Step 5: Generate session summary and statistics"""
        self.logger.info("📊 Step 5: Generating session summary...")
        
        # Calculate statistics
        total_scraped = len(self.application_session.scraped_jobs)
        total_matched = len(self.application_session.matched_jobs)
        total_applied = len(self.application_session.applied_jobs)
        total_failed = len(self.application_session.failed_applications)
        
        # Success rate
        success_rate = (total_applied / (total_applied + total_failed) * 100) if (total_applied + total_failed) > 0 else 0
        
        # Average match score
        if self.application_session.applied_jobs:
            avg_match_score = sum(job['match_score'] for job in self.application_session.applied_jobs) / len(self.application_session.applied_jobs)
        else:
            avg_match_score = 0
        
        # Company distribution
        applied_companies = [job['company'] for job in self.application_session.applied_jobs]
        company_distribution = {}
        for company in applied_companies:
            company_distribution[company] = company_distribution.get(company, 0) + 1
        
        # Session duration
        start_time = datetime.fromisoformat(self.application_session.start_time)
        end_time = datetime.now()
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        self.application_session.session_stats = {
            'total_scraped_jobs': total_scraped,
            'total_matched_jobs': total_matched,
            'total_applied_jobs': total_applied,
            'total_failed_jobs': total_failed,
            'success_rate_percent': round(success_rate, 1),
            'average_match_score': round(avg_match_score, 3),
            'session_duration_minutes': round(duration_minutes, 1),
            'company_distribution': company_distribution,
            'top_skills_matched': self._get_top_matched_skills(),
            'platforms_used': list(set(job.get('source_platform', 'unknown') for job in self.application_session.scraped_jobs))
        }
        
        # Log summary
        self.logger.info(f"📊 SESSION SUMMARY:")
        self.logger.info(f"   🔍 Jobs scraped: {total_scraped}")
        self.logger.info(f"   🎯 Jobs matched: {total_matched}")
        self.logger.info(f"   ✅ Successfully applied: {total_applied}")
        self.logger.info(f"   ❌ Failed applications: {total_failed}")
        self.logger.info(f"   📈 Success rate: {success_rate:.1f}%")
        self.logger.info(f"   🎯 Average match score: {avg_match_score:.1%}")
        self.logger.info(f"   ⏱️  Session duration: {duration_minutes:.1f} minutes")
    
    def _get_top_matched_skills(self) -> List[str]:
        """Get the most commonly matched skills"""
        if not self.application_session.applied_jobs:
            return []
        
        skill_counts = {}
        for job in self.application_session.applied_jobs:
            matching_skills = job.get('matching_skills', [])
            for skill in matching_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return [skill for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    async def _save_session_data(self):
        """Save session data to files"""
        output_dir = Path(f"data/sessions/{self.session_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save complete session data
        session_file = output_dir / "session_data.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.application_session), f, indent=2, ensure_ascii=False)
        
        # Save applied jobs summary
        if self.application_session.applied_jobs:
            applied_summary = []
            for job in self.application_session.applied_jobs:
                summary = {
                    'job_title': job['job_title'],
                    'company': job['company'],
                    'match_score': job['match_score'],
                    'status': job['status'],
                    'applied_at': job['applied_at']
                }
                applied_summary.append(summary)
            
            summary_file = output_dir / "applied_jobs_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(applied_summary, f, indent=2)
        
        self.logger.info(f"💾 Session data saved to: {output_dir}")
    
    async def _remove_duplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs using the smart duplicate detector"""
        unique_jobs = []
        
        for job in jobs:
            is_duplicate = False
            for unique_job in unique_jobs:
                if self.duplicate_detector.check_if_duplicate(job, unique_job):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_jobs.append(job)
        
        removed_count = len(jobs) - len(unique_jobs)
        if removed_count > 0:
            self.logger.info(f"   🗑️  Removed {removed_count} duplicate jobs")
        
        return unique_jobs
    
    def _job_listing_to_dict(self, job: 'JobListing') -> Dict:
        """Convert JobListing object to dictionary"""
        return {
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
            'scraped_at': job.scraped_at
        }
    
    def _dict_to_job_requirement(self, job_dict: Dict) -> Optional['JobRequirement']:
        """Convert dictionary to JobRequirement object"""
        try:
            from intelligent_job_matcher import JobRequirement
            
            return JobRequirement(
                id=job_dict.get('id', ''),
                title=job_dict.get('title', ''),
                company=job_dict.get('company', ''),
                location=job_dict.get('location', ''),
                description=job_dict.get('description', ''),
                required_skills=job_dict.get('skills_required', []),
                preferred_skills=[],  # Could be extracted from description
                experience_level=job_dict.get('experience_level', 'mid'),
                education_required='bachelor',  # Default
                salary_range=None,
                job_type=job_dict.get('job_type', 'full-time'),
                remote_friendly=job_dict.get('remote_friendly', False),
                industry='Technology',  # Default
                company_size='Medium',  # Default
                benefits=[],
                application_url=job_dict.get('application_url', ''),
                source_platform=job_dict.get('source_platform', ''),
                posted_date=job_dict.get('posted_date', '')
            )
        except Exception as e:
            self.logger.error(f"Error converting job dict to JobRequirement: {e}")
            return None
    
    def _flatten_skills(self, skills: Dict[str, List[str]]) -> List[str]:
        """Flatten categorized skills into a single list"""
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list)
        return all_skills

async def main():
    """Main function to run the complete job application pipeline"""
    print("🚀 JOB APPLICATION ORCHESTRATOR")
    print("🤖 Complete automated job application pipeline")
    print("="*60)
    
    # Create orchestrator
    orchestrator = JobApplicationOrchestrator()
    
    try:
        # Run the complete pipeline
        session = await orchestrator.run_complete_pipeline()
        
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"Session ID: {session.session_id}")
        print(f"📊 Results:")
        print(f"   🔍 Jobs scraped: {session.session_stats['total_scraped_jobs']}")
        print(f"   🎯 Jobs matched: {session.session_stats['total_matched_jobs']}")
        print(f"   ✅ Successfully applied: {session.session_stats['total_applied_jobs']}")
        print(f"   📈 Success rate: {session.session_stats['success_rate_percent']}%")
        print(f"   ⏱️  Duration: {session.session_stats['session_duration_minutes']} minutes")
        
        if session.applied_jobs:
            print(f"\n📝 APPLICATIONS SUBMITTED:")
            for job in session.applied_jobs[:5]:  # Show top 5
                print(f"   • {job['job_title']} @ {job['company']} ({job['match_score']:.1%} match)")
        
        print(f"\n💾 Session data saved to: data/sessions/{session.session_id}/")
        print(f"🔍 Check logs for detailed information")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        print(f"🔍 Check logs for error details")

if __name__ == "__main__":
    asyncio.run(main())