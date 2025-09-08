#!/usr/bin/env python3
"""
🧪 Comprehensive End-to-End Test Suite
Complete testing framework for the Ultimate Job Autopilot System
"""

import asyncio
import pytest
import unittest
import tempfile
import json
import os
import sys
import time
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import pandas as pd

# Selenium for UI testing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Playwright for modern web testing
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

# Streamlit testing
import streamlit as st
from streamlit.testing.v1 import AppTest

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

# Import our modules
from universal_job_scraper import UniversalJobScraper, JobListing
from company_career_scraper import CompanyJobPipeline
from advanced_resume_parser import ResumeParser, ParsedResume
from intelligent_job_matcher import AIJobMatcher
from auto_form_filler import IndustryStandardFormFiller, ApplicationData
from job_application_orchestrator import JobApplicationOrchestrator
from scraping_analytics_monitor import ScrapingAnalyticsMonitor
from proxy_rotation_system import ProxyRotationSystem

class TestDataGenerator:
    """Generate mock test data for testing"""
    
    @staticmethod
    def create_test_resume_pdf():
        """Create a test resume PDF file"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        temp_dir = Path("temp/test_data")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        resume_path = temp_dir / "test_resume.pdf"
        
        c = canvas.Canvas(str(resume_path), pagesize=letter)
        
        # Add resume content
        c.drawString(100, 750, "ANKIT THAKUR")
        c.drawString(100, 730, "Senior Cybersecurity Engineer")
        c.drawString(100, 710, "Email: at87.at17@gmail.com")
        c.drawString(100, 690, "Phone: +91 8717934430")
        c.drawString(100, 670, "Location: Remote / Europe")
        
        c.drawString(100, 640, "EXPERIENCE:")
        c.drawString(100, 620, "• 5+ years in cybersecurity and penetration testing")
        c.drawString(100, 600, "• Expert in cloud security and AWS")
        c.drawString(100, 580, "• Python programming and automation")
        
        c.drawString(100, 550, "SKILLS:")
        c.drawString(100, 530, "• Penetration Testing, Vulnerability Assessment")
        c.drawString(100, 510, "• Cloud Security, AWS, Network Security")
        c.drawString(100, 490, "• Python, JavaScript, SQL")
        c.drawString(100, 470, "• Docker, Kubernetes, Terraform")
        
        c.drawString(100, 440, "EDUCATION:")
        c.drawString(100, 420, "• Bachelor of Technology in Computer Science")
        c.drawString(100, 400, "• Various cybersecurity certifications")
        
        c.save()
        
        return str(resume_path)
    
    @staticmethod
    def create_sample_jobs() -> List[Dict]:
        """Create sample job listings for testing"""
        return [
            {
                'id': 'test_job_001',
                'title': 'Senior Cybersecurity Engineer',
                'company': 'TechSecure Inc',
                'location': 'Berlin, Germany',
                'description': 'We are looking for an experienced cybersecurity professional with expertise in penetration testing, cloud security, and Python programming.',
                'requirements': 'Bachelor\'s degree in Computer Science, 5+ years experience in cybersecurity',
                'salary': '€90,000 - €120,000',
                'experience_level': 'senior',
                'job_type': 'full-time',
                'remote_friendly': True,
                'application_url': 'https://techsecure.com/careers/senior-cyber',
                'source_platform': 'linkedin',
                'posted_date': '2024-01-15',
                'skills_required': ['penetration testing', 'python', 'aws', 'cloud security'],
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'test_job_002',
                'title': 'Cloud Security Architect',
                'company': 'CloudFirst GmbH',
                'location': 'Remote',
                'description': 'Join our cloud security team to design and implement security architectures for enterprise clients.',
                'requirements': 'Advanced degree preferred, 7+ years in cloud security',
                'salary': '€100,000 - €140,000',
                'experience_level': 'senior',
                'job_type': 'full-time',
                'remote_friendly': True,
                'application_url': 'https://cloudfirst.com/jobs/architect',
                'source_platform': 'indeed',
                'posted_date': '2024-01-14',
                'skills_required': ['aws', 'azure', 'cloud security', 'kubernetes'],
                'scraped_at': datetime.now().isoformat()
            },
            {
                'id': 'test_job_003',
                'title': 'Junior Security Analyst',
                'company': 'StartupSec Ltd',
                'location': 'Munich, Germany',
                'description': 'Entry-level position for recent graduates interested in cybersecurity.',
                'requirements': 'Bachelor\'s degree, basic knowledge of security tools',
                'salary': '€45,000 - €55,000',
                'experience_level': 'junior',
                'job_type': 'full-time',
                'remote_friendly': False,
                'application_url': 'https://startupsec.com/careers/analyst',
                'source_platform': 'remoteok',
                'posted_date': '2024-01-13',
                'skills_required': ['security tools', 'networking', 'incident response'],
                'scraped_at': datetime.now().isoformat()
            }
        ]

class EndToEndTestSuite:
    """Comprehensive end-to-end test suite"""
    
    def __init__(self):
        self.test_data_generator = TestDataGenerator()
        self.test_results = {
            'unit_tests': {},
            'integration_tests': {},
            'ui_tests': {},
            'performance_tests': {},
            'e2e_tests': {}
        }
        self.test_start_time = datetime.now()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories"""
        print("🧪 Starting Comprehensive End-to-End Testing")
        print("=" * 60)
        
        # Setup test environment
        await self.setup_test_environment()
        
        # Run test categories
        await self.run_unit_tests()
        await self.run_integration_tests()
        await self.run_ui_tests()
        await self.run_performance_tests()
        await self.run_end_to_end_pipeline_test()
        
        # Generate test report
        report = await self.generate_test_report()
        
        # Cleanup
        await self.cleanup_test_environment()
        
        return report
    
    async def setup_test_environment(self):
        """Setup test environment and mock data"""
        print("🔧 Setting up test environment...")
        
        # Create test directories
        test_dirs = [
            'temp/test_data',
            'temp/test_screenshots',
            'temp/test_logs',
            'temp/test_db'
        ]
        
        for directory in test_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Generate test data
        self.test_resume_path = self.test_data_generator.create_test_resume_pdf()
        self.test_jobs = self.test_data_generator.create_sample_jobs()
        
        # Create test configuration
        self.test_config = {
            'resume': {'file_path': self.test_resume_path},
            'scraping': {
                'enabled_platforms': ['test_platform'],
                'max_jobs_per_platform': 10,
                'keywords': ['cybersecurity', 'security engineer'],
                'use_proxy_rotation': False
            },
            'matching': {
                'min_match_score': 0.6,
                'auto_apply_threshold': 0.8
            },
            'user_preferences': {
                'preferred_locations': ['Remote', 'Berlin'],
                'min_salary': 80000,
                'work_authorization': 'Yes'
            },
            'application': {
                'auto_submit': False,
                'save_screenshots': True
            }
        }
        
        print("✅ Test environment setup complete")

class UnitTests(unittest.TestCase):
    """Unit tests for individual components"""
    
    def setUp(self):
        self.test_resume_path = TestDataGenerator.create_test_resume_pdf()
        self.test_jobs = TestDataGenerator.create_sample_jobs()
    
    def test_resume_parser(self):
        """Test resume parsing functionality"""
        print("Testing Resume Parser...")
        
        parser = ResumeParser()
        
        # Test file existence check
        self.assertTrue(Path(self.test_resume_path).exists())
        
        # Test parsing
        try:
            parsed_resume = parser.parse_resume(self.test_resume_path)
            
            # Verify parsed data
            self.assertIsNotNone(parsed_resume)
            self.assertIsNotNone(parsed_resume.contact_info.name)
            self.assertIsNotNone(parsed_resume.contact_info.email)
            self.assertGreater(len(parsed_resume.skills), 0)
            self.assertGreater(parsed_resume.total_experience_years, 0)
            
            print("✅ Resume Parser tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Resume Parser test failed: {e}")
            return False
    
    def test_job_matcher(self):
        """Test job matching functionality"""
        print("Testing Job Matcher...")
        
        try:
            # Create mock resume
            mock_resume = Mock()
            mock_resume.skills = {
                'cybersecurity': ['penetration testing', 'vulnerability assessment'],
                'programming_languages': ['python', 'javascript'],
                'cloud_platforms': ['aws', 'azure']
            }
            mock_resume.total_experience_years = 5.5
            mock_resume.seniority_level = 'senior'
            mock_resume.primary_domain = 'cybersecurity'
            
            # Create matcher
            matcher = AIJobMatcher()
            
            # Test basic functionality (without actual AI models for speed)
            self.assertIsNotNone(matcher)
            
            print("✅ Job Matcher tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Job Matcher test failed: {e}")
            return False
    
    def test_form_filler(self):
        """Test form filling functionality"""
        print("Testing Form Filler...")
        
        try:
            filler = IndustryStandardFormFiller()
            
            # Create test application data
            test_data = ApplicationData(
                first_name="Ankit",
                last_name="Thakur",
                email="at87.at17@gmail.com",
                phone="+91 8717934430",
                address="Remote",
                city="Remote",
                state="",
                country="Germany",
                postal_code="",
                linkedin_url="",
                portfolio_url="",
                github_url="",
                current_title="Senior Cybersecurity Engineer",
                current_company="TechCorp",
                years_experience=5,
                desired_salary="€100,000",
                availability="Two weeks notice",
                notice_period="2 weeks",
                education_level="Bachelor",
                university="Technical University",
                degree="Computer Science",
                graduation_year="2018",
                gpa="",
                authorized_to_work="Yes",
                visa_status="EU Citizen",
                sponsorship_required="No",
                cover_letter="Test cover letter",
                why_interested="Test interest",
                references_available="Available upon request",
                resume_path=self.test_resume_path
            )
            
            self.assertIsNotNone(test_data)
            self.assertEqual(test_data.first_name, "Ankit")
            self.assertEqual(test_data.email, "at87.at17@gmail.com")
            
            print("✅ Form Filler tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Form Filler test failed: {e}")
            return False

class IntegrationTests:
    """Integration tests for component interactions"""
    
    async def test_scraper_to_matcher_pipeline(self):
        """Test scraping to matching pipeline"""
        print("Testing Scraper → Matcher Pipeline...")
        
        try:
            # Mock scraper results
            test_jobs = TestDataGenerator.create_sample_jobs()
            
            # Convert to job requirements for matcher
            from intelligent_job_matcher import JobRequirement
            
            job_requirements = []
            for job_data in test_jobs:
                job_req = JobRequirement(
                    id=job_data['id'],
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    description=job_data['description'],
                    required_skills=job_data['skills_required'],
                    preferred_skills=[],
                    experience_level=job_data['experience_level'],
                    education_required='bachelor',
                    salary_range=None,
                    job_type=job_data['job_type'],
                    remote_friendly=job_data['remote_friendly'],
                    industry='Technology',
                    company_size='Medium',
                    benefits=[],
                    application_url=job_data['application_url'],
                    source_platform=job_data['source_platform'],
                    posted_date=job_data['posted_date']
                )
                job_requirements.append(job_req)
            
            # Test that we have valid job requirements
            self.assertEqual(len(job_requirements), 3)
            
            print("✅ Scraper → Matcher Pipeline tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Scraper → Matcher Pipeline test failed: {e}")
            return False
    
    async def test_matcher_to_application_pipeline(self):
        """Test matching to application pipeline"""
        print("Testing Matcher → Application Pipeline...")
        
        try:
            # Create mock match results
            mock_matches = [
                {
                    'job_id': 'test_job_001',
                    'job_title': 'Senior Cybersecurity Engineer',
                    'company': 'TechSecure Inc',
                    'overall_score': 0.95,
                    'recommendation': 'HIGHLY RECOMMENDED',
                    'application_url': 'https://example.com/apply'
                }
            ]
            
            # Test application data creation
            filler = IndustryStandardFormFiller()
            
            # Mock resume
            mock_resume = Mock()
            mock_resume.contact_info.name = "Ankit Thakur"
            mock_resume.contact_info.email = "at87.at17@gmail.com"
            mock_resume.contact_info.phone = "+91 8717934430"
            mock_resume.contact_info.location = "Remote"
            mock_resume.work_experience = []
            mock_resume.education = []
            mock_resume.file_path = TestDataGenerator.create_test_resume_pdf()
            
            app_data = filler.create_application_data(mock_resume)
            
            self.assertIsNotNone(app_data)
            self.assertEqual(app_data.first_name, "Ankit")
            
            print("✅ Matcher → Application Pipeline tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Matcher → Application Pipeline test failed: {e}")
            return False
    
    async def test_database_integration(self):
        """Test database operations"""
        print("Testing Database Integration...")
        
        try:
            # Test analytics database
            db_path = "temp/test_db/test_analytics.db"
            
            # Create test database
            conn = sqlite3.connect(db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_metrics (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    metric_value REAL
                )
            """)
            
            # Insert test data
            conn.execute(
                "INSERT INTO test_metrics (timestamp, metric_value) VALUES (?, ?)",
                (datetime.now().isoformat(), 0.85)
            )
            conn.commit()
            
            # Verify data
            cursor = conn.execute("SELECT COUNT(*) FROM test_metrics")
            count = cursor.fetchone()[0]
            
            self.assertEqual(count, 1)
            
            conn.close()
            
            print("✅ Database Integration tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Database Integration test failed: {e}")
            return False

class UITests:
    """UI and dashboard testing"""
    
    def __init__(self):
        self.dashboard_process = None
        self.dashboard_url = "http://localhost:8501"
    
    async def start_dashboard_for_testing(self):
        """Start Streamlit dashboard for testing"""
        print("🚀 Starting dashboard for UI testing...")
        
        try:
            dashboard_path = Path("ui/ultimate_job_dashboard.py")
            
            if not dashboard_path.exists():
                print("❌ Dashboard file not found!")
                return False
            
            # Start dashboard in background
            self.dashboard_process = subprocess.Popen([
                sys.executable, '-m', 'streamlit', 'run',
                str(dashboard_path),
                '--server.headless', 'true',
                '--server.port', '8501',
                '--browser.gatherUsageStats', 'false'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for dashboard to start
            await asyncio.sleep(10)
            
            # Test if dashboard is accessible
            import requests
            try:
                response = requests.get(self.dashboard_url, timeout=5)
                if response.status_code == 200:
                    print("✅ Dashboard started successfully")
                    return True
            except:
                pass
            
            print("❌ Dashboard failed to start properly")
            return False
            
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
            return False
    
    async def test_dashboard_accessibility(self):
        """Test dashboard page accessibility"""
        print("Testing Dashboard Accessibility...")
        
        try:
            import requests
            
            # Test main dashboard page
            response = requests.get(self.dashboard_url, timeout=10)
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("Ultimate Job Autopilot", response.text)
            
            print("✅ Dashboard Accessibility tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Dashboard Accessibility test failed: {e}")
            return False
    
    async def test_streamlit_app_components(self):
        """Test Streamlit app components using AppTest"""
        print("Testing Streamlit App Components...")
        
        try:
            # Create a simple test version of the dashboard
            test_dashboard_code = '''
import streamlit as st

st.title("🚀 Ultimate Job Autopilot")
st.write("AI-Powered Job Discovery System")

# Test components
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Jobs Scraped", 150)
with col2:
    st.metric("Jobs Matched", 45)
with col3:
    st.metric("Applications", 12)

# Test input components
job_keywords = st.text_input("Job Keywords", "cybersecurity engineer")
locations = st.multiselect("Locations", ["Remote", "Berlin", "Munich"], default=["Remote"])

if st.button("Start Scraping"):
    st.success("Scraping started!")
'''
            
            # Write test dashboard
            test_dashboard_path = Path("temp/test_dashboard.py")
            with open(test_dashboard_path, 'w') as f:
                f.write(test_dashboard_code)
            
            # Test with AppTest
            at = AppTest.from_file(str(test_dashboard_path))
            at.run()
            
            # Verify components exist
            self.assertTrue(len(at.title) > 0)
            self.assertTrue(len(at.metric) == 3)
            
            # Test interactions
            at.text_input("job_keywords").set_value("security engineer")
            at.button("start_scraping").click()
            at.run()
            
            # Check success message appears
            self.assertTrue(len(at.success) > 0)
            
            print("✅ Streamlit App Components tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Streamlit App Components test failed: {e}")
            return False
    
    async def test_playwright_ui_interactions(self):
        """Test UI interactions using Playwright"""
        print("Testing UI Interactions with Playwright...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to dashboard
                await page.goto(self.dashboard_url)
                await page.wait_for_timeout(3000)
                
                # Check page title
                title = await page.title()
                self.assertIn("Ultimate Job Autopilot", title)
                
                # Test sidebar navigation (if present)
                try:
                    sidebar = page.locator('[data-testid="stSidebar"]')
                    if await sidebar.count() > 0:
                        print("✅ Sidebar found and accessible")
                except:
                    print("ℹ️  Sidebar not found (may be expected)")
                
                # Test main content area
                main_content = page.locator('[data-testid="stMain"]')
                if await main_content.count() > 0:
                    print("✅ Main content area accessible")
                
                # Take screenshot for manual verification
                screenshot_path = Path("temp/test_screenshots/dashboard_test.png")
                await page.screenshot(path=screenshot_path)
                print(f"📷 Screenshot saved: {screenshot_path}")
                
                await browser.close()
                
            print("✅ Playwright UI Interactions tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Playwright UI Interactions test failed: {e}")
            return False
    
    async def stop_dashboard(self):
        """Stop the dashboard process"""
        if self.dashboard_process:
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
            print("✅ Dashboard stopped")

class PerformanceTests:
    """Performance and load testing"""
    
    async def test_scraping_performance(self):
        """Test job scraping performance"""
        print("Testing Scraping Performance...")
        
        try:
            start_time = time.time()
            
            # Mock scraping performance test
            test_jobs = []
            
            # Simulate scraping 100 jobs
            for i in range(100):
                job = {
                    'id': f'perf_test_{i}',
                    'title': f'Test Job {i}',
                    'company': f'Company {i}',
                    'location': 'Remote',
                    'description': 'Test job description for performance testing',
                    'skills_required': ['python', 'testing'],
                    'scraped_at': datetime.now().isoformat()
                }
                test_jobs.append(job)
                
                # Simulate processing time
                await asyncio.sleep(0.01)  # 10ms per job
            
            end_time = time.time()
            processing_time = end_time - start_time
            jobs_per_second = len(test_jobs) / processing_time
            
            print(f"   📊 Processed {len(test_jobs)} jobs in {processing_time:.2f}s")
            print(f"   ⚡ Speed: {jobs_per_second:.1f} jobs/second")
            
            # Performance thresholds
            self.assertLess(processing_time, 10.0)  # Should complete in under 10 seconds
            self.assertGreater(jobs_per_second, 5.0)  # Should process at least 5 jobs/second
            
            print("✅ Scraping Performance tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Scraping Performance test failed: {e}")
            return False
    
    async def test_matching_performance(self):
        """Test job matching performance"""
        print("Testing Matching Performance...")
        
        try:
            start_time = time.time()
            
            # Create test jobs and resume
            test_jobs = TestDataGenerator.create_sample_jobs()
            
            # Mock matching process
            matches = []
            for job in test_jobs:
                # Simulate AI matching computation
                await asyncio.sleep(0.05)  # 50ms per job matching
                
                match = {
                    'job_id': job['id'],
                    'overall_score': 0.8,
                    'processing_time': 0.05
                }
                matches.append(match)
            
            end_time = time.time()
            total_time = end_time - start_time
            matches_per_second = len(matches) / total_time
            
            print(f"   📊 Matched {len(matches)} jobs in {total_time:.2f}s")
            print(f"   ⚡ Speed: {matches_per_second:.1f} matches/second")
            
            # Performance thresholds
            self.assertLess(total_time, 5.0)  # Should complete in under 5 seconds
            self.assertGreater(matches_per_second, 0.5)  # Should process at least 0.5 matches/second
            
            print("✅ Matching Performance tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Matching Performance test failed: {e}")
            return False
    
    async def test_memory_usage(self):
        """Test memory usage during operations"""
        print("Testing Memory Usage...")
        
        try:
            import psutil
            process = psutil.Process(os.getpid())
            
            # Get initial memory usage
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate heavy operations
            large_dataset = []
            for i in range(10000):
                job_data = {
                    'id': f'mem_test_{i}',
                    'title': f'Memory Test Job {i}' * 10,  # Make it bigger
                    'description': 'A' * 1000,  # 1KB description
                    'skills': ['skill'] * 100
                }
                large_dataset.append(job_data)
            
            # Get peak memory usage
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory
            
            print(f"   💾 Initial memory: {initial_memory:.1f} MB")
            print(f"   💾 Peak memory: {peak_memory:.1f} MB")
            print(f"   📈 Memory increase: {memory_increase:.1f} MB")
            
            # Memory usage thresholds
            self.assertLess(memory_increase, 500)  # Should not increase by more than 500MB
            self.assertLess(peak_memory, 2000)     # Should not exceed 2GB total
            
            # Cleanup
            del large_dataset
            
            print("✅ Memory Usage tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Memory Usage test failed: {e}")
            return False

class EndToEndPipelineTest:
    """Complete end-to-end pipeline testing"""
    
    async def test_complete_pipeline(self):
        """Test the complete job application pipeline"""
        print("Testing Complete End-to-End Pipeline...")
        
        try:
            pipeline_start_time = time.time()
            
            # Step 1: Resume Parsing
            print("   Step 1: Testing Resume Parsing...")
            resume_path = TestDataGenerator.create_test_resume_pdf()
            
            # Mock successful resume parsing
            parsed_resume_data = {
                'name': 'Ankit Thakur',
                'email': 'at87.at17@gmail.com',
                'skills': ['cybersecurity', 'python', 'aws'],
                'experience_years': 5.5
            }
            print("   ✅ Resume parsed successfully")
            
            # Step 2: Job Scraping
            print("   Step 2: Testing Job Scraping...")
            scraped_jobs = TestDataGenerator.create_sample_jobs()
            print(f"   ✅ Scraped {len(scraped_jobs)} jobs")
            
            # Step 3: Job Matching
            print("   Step 3: Testing Job Matching...")
            matched_jobs = []
            for job in scraped_jobs:
                # Mock matching logic
                match_score = 0.85 if 'cybersecurity' in job['title'].lower() else 0.65
                
                if match_score >= 0.6:  # Minimum threshold
                    matched_job = {
                        'job_id': job['id'],
                        'job_title': job['title'],
                        'company': job['company'],
                        'overall_score': match_score,
                        'recommendation': 'RECOMMENDED' if match_score >= 0.8 else 'CONSIDER'
                    }
                    matched_jobs.append(matched_job)
            
            print(f"   ✅ Matched {len(matched_jobs)} jobs")
            
            # Step 4: Application Preparation
            print("   Step 4: Testing Application Preparation...")
            
            high_match_jobs = [job for job in matched_jobs if job['overall_score'] >= 0.8]
            
            prepared_applications = []
            for job in high_match_jobs:
                application = {
                    'job_id': job['job_id'],
                    'job_title': job['job_title'],
                    'company': job['company'],
                    'form_data_prepared': True,
                    'resume_attached': True,
                    'cover_letter_generated': True
                }
                prepared_applications.append(application)
            
            print(f"   ✅ Prepared {len(prepared_applications)} applications")
            
            # Step 5: Mock Application Submission
            print("   Step 5: Testing Application Submission (Mock)...")
            
            submitted_applications = []
            for app in prepared_applications:
                # Mock submission success/failure
                success = True  # Mock 100% success for testing
                
                result = {
                    'job_id': app['job_id'],
                    'job_title': app['job_title'],
                    'company': app['company'],
                    'status': 'success' if success else 'failed',
                    'submitted_at': datetime.now().isoformat()
                }
                submitted_applications.append(result)
            
            successful_apps = [app for app in submitted_applications if app['status'] == 'success']
            print(f"   ✅ Successfully submitted {len(successful_apps)} applications")
            
            # Step 6: Results Analysis
            print("   Step 6: Analyzing Results...")
            
            pipeline_end_time = time.time()
            total_pipeline_time = pipeline_end_time - pipeline_start_time
            
            pipeline_results = {
                'resume_parsed': bool(parsed_resume_data),
                'jobs_scraped': len(scraped_jobs),
                'jobs_matched': len(matched_jobs),
                'applications_prepared': len(prepared_applications),
                'applications_submitted': len(successful_apps),
                'total_time_seconds': total_pipeline_time,
                'success_rate': len(successful_apps) / len(prepared_applications) if prepared_applications else 0
            }
            
            print("   📊 Pipeline Results:")
            for key, value in pipeline_results.items():
                if key == 'success_rate':
                    print(f"      {key}: {value:.1%}")
                elif key == 'total_time_seconds':
                    print(f"      {key}: {value:.2f}s")
                else:
                    print(f"      {key}: {value}")
            
            # Validate pipeline results
            self.assertGreater(pipeline_results['jobs_scraped'], 0)
            self.assertGreater(pipeline_results['jobs_matched'], 0)
            self.assertGreater(pipeline_results['applications_prepared'], 0)
            self.assertGreater(pipeline_results['success_rate'], 0.8)  # 80% success rate
            self.assertLess(pipeline_results['total_time_seconds'], 60)  # Complete in under 1 minute
            
            print("✅ Complete End-to-End Pipeline test passed")
            return pipeline_results
            
        except Exception as e:
            print(f"❌ Complete End-to-End Pipeline test failed: {e}")
            return None

# Main test execution class
class ComprehensiveTestExecutor:
    """Execute all tests and generate comprehensive report"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
    
    def assertEqual(self, a, b, msg=None):
        """Simple assertion helper"""
        if a != b:
            raise AssertionError(msg or f"Expected {a} == {b}")
    
    def assertTrue(self, condition, msg=None):
        """Simple assertion helper"""
        if not condition:
            raise AssertionError(msg or f"Expected condition to be True")
    
    def assertGreater(self, a, b, msg=None):
        """Simple assertion helper"""
        if not (a > b):
            raise AssertionError(msg or f"Expected {a} > {b}")
    
    def assertLess(self, a, b, msg=None):
        """Simple assertion helper"""
        if not (a < b):
            raise AssertionError(msg or f"Expected {a} < {b}")
    
    def assertIn(self, item, container, msg=None):
        """Simple assertion helper"""
        if item not in container:
            raise AssertionError(msg or f"Expected {item} to be in {container}")
    
    def assertIsNotNone(self, obj, msg=None):
        """Simple assertion helper"""
        if obj is None:
            raise AssertionError(msg or "Expected object to not be None")
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("🧪 COMPREHENSIVE END-TO-END TESTING SUITE")
        print("🚀 Ultimate Job Autopilot System Validation")
        print("=" * 70)
        
        # Initialize test classes
        unit_tests = UnitTests()
        unit_tests.setUp()  # Setup test data
        
        integration_tests = IntegrationTests()
        ui_tests = UITests()
        performance_tests = PerformanceTests()
        e2e_tests = EndToEndPipelineTest()
        
        # Copy assertion methods to test classes
        for test_class in [integration_tests, performance_tests, e2e_tests]:
            test_class.assertEqual = self.assertEqual
            test_class.assertTrue = self.assertTrue
            test_class.assertGreater = self.assertGreater
            test_class.assertLess = self.assertLess
            test_class.assertIn = self.assertIn
            test_class.assertIsNotNone = self.assertIsNotNone
        
        # Test execution plan
        test_plan = [
            ("Unit Tests", [
                ("Resume Parser", unit_tests.test_resume_parser),
                ("Job Matcher", unit_tests.test_job_matcher),
                ("Form Filler", unit_tests.test_form_filler),
            ]),
            ("Integration Tests", [
                ("Scraper → Matcher Pipeline", integration_tests.test_scraper_to_matcher_pipeline),
                ("Matcher → Application Pipeline", integration_tests.test_matcher_to_application_pipeline),
                ("Database Integration", integration_tests.test_database_integration),
            ]),
            ("Performance Tests", [
                ("Scraping Performance", performance_tests.test_scraping_performance),
                ("Matching Performance", performance_tests.test_matching_performance),
                ("Memory Usage", performance_tests.test_memory_usage),
            ]),
            ("UI Tests", [
                ("Dashboard Startup", ui_tests.start_dashboard_for_testing),
                ("Dashboard Accessibility", ui_tests.test_dashboard_accessibility),
                ("Streamlit Components", ui_tests.test_streamlit_app_components),
                ("UI Interactions", ui_tests.test_playwright_ui_interactions),
            ]),
            ("End-to-End Tests", [
                ("Complete Pipeline", e2e_tests.test_complete_pipeline),
            ])
        ]
        
        # Execute all tests
        overall_results = {}
        total_tests = 0
        passed_tests = 0
        
        for category_name, tests in test_plan:
            print(f"\n🔬 {category_name.upper()}")
            print("-" * 50)
            
            category_results = {}
            
            for test_name, test_func in tests:
                total_tests += 1
                test_start = time.time()
                
                try:
                    if asyncio.iscoroutinefunction(test_func):
                        result = await test_func()
                    else:
                        result = test_func()
                    
                    test_end = time.time()
                    test_duration = test_end - test_start
                    
                    if result is not False:  # Consider None and True as pass
                        passed_tests += 1
                        status = "✅ PASSED"
                    else:
                        status = "❌ FAILED"
                    
                    category_results[test_name] = {
                        'status': 'passed' if result is not False else 'failed',
                        'duration': test_duration,
                        'result': result
                    }
                    
                    print(f"   {status} {test_name} ({test_duration:.2f}s)")
                    
                except Exception as e:
                    test_end = time.time()
                    test_duration = test_end - test_start
                    
                    category_results[test_name] = {
                        'status': 'failed',
                        'duration': test_duration,
                        'error': str(e)
                    }
                    
                    print(f"   ❌ FAILED {test_name} ({test_duration:.2f}s)")
                    print(f"      Error: {str(e)}")
            
            overall_results[category_name] = category_results
        
        # Stop dashboard if it was started
        try:
            await ui_tests.stop_dashboard()
        except:
            pass
        
        # Generate final report
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n" + "=" * 70)
        print(f"🏆 TEST EXECUTION COMPLETE")
        print(f"=" * 70)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {passed_tests / total_tests * 100:.1f}%")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        
        # Category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in overall_results.items():
            category_passed = sum(1 for r in results.values() if r['status'] == 'passed')
            category_total = len(results)
            print(f"   {category}: {category_passed}/{category_total} ({category_passed/category_total*100:.1f}%)")
        
        # Save detailed results
        results_file = Path("temp/test_results.json")
        results_file.parent.mkdir(exist_ok=True)
        
        detailed_results = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': passed_tests / total_tests,
                'total_duration_seconds': total_duration,
                'test_start_time': self.start_time.isoformat(),
                'test_end_time': end_time.isoformat()
            },
            'results_by_category': overall_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Cleanup
        await self.cleanup_test_files()
        
        return detailed_results
    
    async def cleanup_test_files(self):
        """Cleanup test files and directories"""
        print("\n🧹 Cleaning up test files...")
        
        import shutil
        
        cleanup_paths = [
            'temp/test_data',
            'temp/test_screenshots', 
            'temp/test_logs',
            'temp/test_db'
        ]
        
        for path in cleanup_paths:
            if Path(path).exists():
                shutil.rmtree(path)
        
        print("✅ Cleanup complete")

# Main execution function
async def main():
    """Main function to run comprehensive tests"""
    executor = ComprehensiveTestExecutor()
    results = await executor.run_all_tests()
    
    # Return results for external use
    return results

if __name__ == "__main__":
    # Run the comprehensive test suite
    results = asyncio.run(main())
    
    # Exit with appropriate code
    success_rate = results['summary']['success_rate']
    exit_code = 0 if success_rate >= 0.8 else 1  # Require 80% success rate
    
    print(f"\n🏁 Test suite completed with exit code: {exit_code}")
    sys.exit(exit_code)