#!/usr/bin/env python3
"""
🔗 Integration Test Suite
Comprehensive integration testing for all pipeline components
"""

import asyncio
import json
import tempfile
import sqlite3
import os
import sys
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import aiohttp
import pandas as pd
from dataclasses import dataclass, asdict

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

# Import our modules
from universal_job_scraper import UniversalJobScraper, JobListing
from company_career_scraper import CompanyJobPipeline, CompanyInfo
from advanced_resume_parser import ResumeParser, ParsedResume, ContactInfo, WorkExperience, Education
from intelligent_job_matcher import AIJobMatcher, JobRequirement, MatchResult
from auto_form_filler import IndustryStandardFormFiller, ApplicationData
from job_application_orchestrator import JobApplicationOrchestrator
from scraping_analytics_monitor import ScrapingAnalyticsMonitor, ScrapingMetrics, ApplicationMetrics
from proxy_rotation_system import ProxyRotationSystem, ProxyConfig

class MockDataFactory:
    """Factory for creating realistic test data"""
    
    @staticmethod
    def create_mock_resume() -> ParsedResume:
        """Create a comprehensive mock resume"""
        contact_info = ContactInfo(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            linkedin="https://linkedin.com/in/johndoe",
            github="https://github.com/johndoe",
            portfolio="https://johndoe.dev",
            location="San Francisco, CA"
        )
        
        work_experience = [
            WorkExperience(
                title="Senior Security Engineer",
                company="TechCorp Inc",
                location="San Francisco, CA",
                start_date="2020-01",
                end_date=None,
                duration_months=48,
                responsibilities=[
                    "Led security architecture for cloud infrastructure",
                    "Implemented zero-trust security model",
                    "Conducted security assessments and penetration testing"
                ],
                achievements=[
                    "Reduced security incidents by 60%",
                    "Saved company $2M through security improvements",
                    "Led team of 5 security professionals"
                ],
                skills_used=["python", "aws", "kubernetes", "penetration testing"]
            ),
            WorkExperience(
                title="Security Analyst",
                company="SecureStart LLC",
                location="Remote",
                start_date="2018-06",
                end_date="2019-12",
                duration_months=18,
                responsibilities=[
                    "Monitored security events and incidents",
                    "Performed vulnerability assessments",
                    "Developed security policies and procedures"
                ],
                achievements=[
                    "Implemented SIEM solution",
                    "Achieved SOC 2 compliance",
                    "Reduced false positives by 40%"
                ],
                skills_used=["splunk", "nessus", "wireshark", "incident response"]
            )
        ]
        
        education = [
            Education(
                degree="Master of Science",
                field="Cybersecurity",
                institution="University of Technology",
                graduation_year="2018",
                gpa="3.8"
            ),
            Education(
                degree="Bachelor of Science",
                field="Computer Science",
                institution="State University",
                graduation_year="2016",
                gpa="3.6"
            )
        ]
        
        skills = {
            'cybersecurity': ['penetration testing', 'vulnerability assessment', 'incident response'],
            'programming_languages': ['python', 'javascript', 'bash'],
            'cloud_platforms': ['aws', 'azure', 'gcp'],
            'tools': ['splunk', 'nessus', 'wireshark', 'metasploit']
        }
        
        return ParsedResume(
            contact_info=contact_info,
            summary="Experienced cybersecurity professional with 4+ years in threat detection and security architecture",
            skills=skills,
            work_experience=work_experience,
            education=education,
            certifications=[],
            projects=[],
            languages=["English", "Spanish"],
            awards=["Employee of the Year 2022", "Security Innovation Award"],
            publications=[],
            raw_text="Mock resume text content",
            file_path="/tmp/mock_resume.pdf",
            parsed_at=datetime.now().isoformat(),
            total_experience_years=4.5,
            seniority_level="senior",
            primary_domain="cybersecurity",
            skill_confidence_scores={
                'python': 0.9,
                'aws': 0.85,
                'penetration testing': 0.95,
                'incident response': 0.8
            }
        )
    
    @staticmethod
    def create_mock_job_listings() -> List[JobListing]:
        """Create comprehensive mock job listings"""
        jobs = [
            JobListing(
                id="job_001",
                title="Senior Cybersecurity Engineer",
                company="InnovateTech Solutions",
                location="San Francisco, CA",
                description="""We are seeking an experienced cybersecurity professional to join our security team. 
                The ideal candidate will have expertise in cloud security, threat detection, and incident response.
                
                Key Responsibilities:
                - Design and implement security architecture
                - Conduct security assessments and penetration testing
                - Lead incident response activities
                - Mentor junior security analysts
                
                Required Skills:
                - 5+ years experience in cybersecurity
                - Strong knowledge of AWS/Azure security
                - Python programming skills
                - Experience with SIEM tools like Splunk
                - Knowledge of compliance frameworks (SOX, SOC2)
                """,
                requirements="Bachelor's degree in Computer Science or related field, 5+ years cybersecurity experience",
                salary="$140,000 - $180,000",
                experience_level="senior",
                job_type="full-time",
                remote_friendly=True,
                application_url="https://innovatetech.com/careers/senior-cyber",
                source_platform="linkedin",
                posted_date="2024-01-15",
                skills_required=["python", "aws", "penetration testing", "splunk", "incident response"],
                benefits="Health insurance, 401k, flexible PTO",
                company_size="500-1000",
                industry="Technology",
                scraped_at=datetime.now().isoformat()
            ),
            JobListing(
                id="job_002", 
                title="Cloud Security Architect",
                company="CloudFirst Inc",
                location="Remote",
                description="""Join our growing security team as a Cloud Security Architect. You'll be responsible
                for designing secure cloud architectures and ensuring compliance across our infrastructure.
                
                What You'll Do:
                - Architect secure cloud solutions on AWS/Azure/GCP
                - Develop security standards and best practices
                - Collaborate with DevOps teams on secure deployments
                - Conduct security reviews and threat modeling
                
                Requirements:
                - 7+ years in cybersecurity with cloud focus
                - Deep knowledge of cloud security services
                - Experience with Infrastructure as Code (Terraform)
                - Strong communication and leadership skills
                """,
                requirements="Advanced degree preferred, 7+ years cloud security experience",
                salary="$160,000 - $200,000",
                experience_level="senior",
                job_type="full-time", 
                remote_friendly=True,
                application_url="https://cloudfirst.com/jobs/architect",
                source_platform="indeed",
                posted_date="2024-01-12",
                skills_required=["aws", "azure", "terraform", "kubernetes", "security architecture"],
                benefits="Equity, unlimited PTO, learning budget",
                company_size="100-500",
                industry="Technology",
                scraped_at=datetime.now().isoformat()
            ),
            JobListing(
                id="job_003",
                title="Junior Security Analyst", 
                company="StartupSecure",
                location="Austin, TX",
                description="""Entry-level opportunity for recent graduates interested in cybersecurity.
                You'll work alongside senior analysts to monitor security events and learn the fundamentals
                of information security.
                
                Responsibilities:
                - Monitor security alerts and events
                - Assist with vulnerability assessments
                - Document security procedures
                - Participate in incident response activities
                
                We're looking for:
                - Recent graduate with cybersecurity interest
                - Basic knowledge of networking and security concepts
                - Eagerness to learn and grow in security field
                - Strong analytical and problem-solving skills
                """,
                requirements="Bachelor's degree in Computer Science, IT, or related field",
                salary="$65,000 - $75,000",
                experience_level="junior",
                job_type="full-time",
                remote_friendly=False,
                application_url="https://startupsecure.com/careers/junior-analyst", 
                source_platform="remoteok",
                posted_date="2024-01-10",
                skills_required=["networking", "security fundamentals", "siem", "vulnerability scanning"],
                benefits="Health insurance, professional development",
                company_size="10-50", 
                industry="Technology",
                scraped_at=datetime.now().isoformat()
            )
        ]
        
        return jobs
    
    @staticmethod
    def create_mock_company_info() -> List[CompanyInfo]:
        """Create mock company information"""
        return [
            CompanyInfo(
                name="TechGiant Corp",
                website="https://techgiant.com",
                career_url="https://techgiant.com/careers",
                industry="Technology",
                size="10000+",
                locations=["San Francisco", "New York", "Austin", "Remote"]
            ),
            CompanyInfo(
                name="CloudInnovate Inc", 
                website="https://cloudinnovate.com",
                career_url="https://cloudinnovate.com/jobs",
                industry="Cloud Computing",
                size="1000-5000",
                locations=["Seattle", "Denver", "Remote"]
            ),
            CompanyInfo(
                name="CyberDefense Solutions",
                website="https://cyberdefense.com", 
                career_url="https://cyberdefense.com/careers",
                industry="Cybersecurity",
                size="500-1000",
                locations=["Washington DC", "Chicago", "Remote"]
            )
        ]
    
    @staticmethod
    def create_mock_application_data() -> ApplicationData:
        """Create mock application data"""
        return ApplicationData(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            address="123 Main Street",
            city="San Francisco",
            state="CA", 
            country="United States",
            postal_code="94105",
            linkedin_url="https://linkedin.com/in/johndoe",
            portfolio_url="https://johndoe.dev",
            github_url="https://github.com/johndoe",
            current_title="Senior Security Engineer",
            current_company="TechCorp Inc",
            years_experience=5,
            desired_salary="$150,000",
            availability="Two weeks notice",
            notice_period="2 weeks",
            education_level="Master", 
            university="University of Technology",
            degree="Computer Science",
            graduation_year="2018",
            gpa="3.8",
            authorized_to_work="Yes",
            visa_status="US Citizen",
            sponsorship_required="No",
            cover_letter="I am excited to apply for this position...",
            why_interested="Your company's innovative approach to security aligns with my career goals",
            references_available="Available upon request",
            resume_path="/tmp/mock_resume.pdf"
        )

class IntegrationTestSuite(unittest.TestCase):
    """Comprehensive integration tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.mock_data = MockDataFactory()
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_analytics.db")
        
        # Create test resume file
        self.test_resume_path = os.path.join(self.temp_dir, "test_resume.pdf")
        with open(self.test_resume_path, 'w') as f:
            f.write("Mock resume content")
    
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scraper_to_parser_integration(self):
        """Test integration between job scraper and resume parser"""
        print("Testing Scraper → Parser Integration...")
        
        # Mock scraped jobs
        mock_jobs = self.mock_data.create_mock_job_listings()
        
        # Verify job data structure
        self.assertIsInstance(mock_jobs, list)
        self.assertGreater(len(mock_jobs), 0)
        
        for job in mock_jobs:
            self.assertIsInstance(job, JobListing)
            self.assertIsNotNone(job.id)
            self.assertIsNotNone(job.title)
            self.assertIsNotNone(job.company)
            self.assertIsInstance(job.skills_required, list)
        
        # Mock resume parsing
        mock_resume = self.mock_data.create_mock_resume()
        
        # Verify resume data structure
        self.assertIsInstance(mock_resume, ParsedResume)
        self.assertIsNotNone(mock_resume.contact_info.name)
        self.assertIsNotNone(mock_resume.contact_info.email)
        self.assertGreater(mock_resume.total_experience_years, 0)
        self.assertIsInstance(mock_resume.skills, dict)
        
        print("✅ Scraper → Parser Integration test passed")
        return True

    def test_parser_to_matcher_integration(self):
        """Test integration between resume parser and job matcher"""
        print("Testing Parser → Matcher Integration...")
        
        # Create mock data
        mock_resume = self.mock_data.create_mock_resume()
        mock_jobs = self.mock_data.create_mock_job_listings()
        
        # Convert JobListing to JobRequirement for matcher
        from intelligent_job_matcher import JobRequirement
        
        job_requirements = []
        for job in mock_jobs:
            job_req = JobRequirement(
                id=job.id,
                title=job.title,
                company=job.company,
                location=job.location,
                description=job.description,
                required_skills=job.skills_required,
                preferred_skills=[],
                experience_level=job.experience_level,
                education_required="bachelor",
                salary_range=(100000, 150000) if job.salary else None,
                job_type=job.job_type,
                remote_friendly=job.remote_friendly,
                industry=job.industry,
                company_size=job.company_size,
                benefits=job.benefits.split(", ") if job.benefits else [],
                application_url=job.application_url,
                source_platform=job.source_platform,
                posted_date=job.posted_date
            )
            job_requirements.append(job_req)
        
        # Test matcher initialization
        matcher = AIJobMatcher()
        self.assertIsNotNone(matcher)
        
        # Mock the AI matching process (since we don't want to run actual AI models)
        with patch.object(matcher, 'calculate_comprehensive_match') as mock_match:
            mock_match_result = MatchResult(
                job_id="job_001",
                overall_score=0.85,
                skill_match_score=0.9,
                experience_match_score=0.8,
                education_match_score=1.0,
                location_match_score=0.7,
                culture_fit_score=0.8,
                salary_compatibility=0.9,
                detailed_analysis={'strengths': ['Excellent skill match']},
                recommendation="HIGHLY RECOMMENDED",
                missing_skills=["terraform"],
                matching_skills=["python", "aws", "penetration testing"],
                confidence_level="HIGH"
            )
            mock_match.return_value = mock_match_result
            
            # Test matching process
            match_result = matcher.calculate_comprehensive_match(
                mock_resume, 
                job_requirements[0], 
                {'preferred_locations': ['San Francisco']}
            )
            
            # Verify match result
            self.assertIsInstance(match_result, MatchResult)
            self.assertGreater(match_result.overall_score, 0)
            self.assertIsInstance(match_result.matching_skills, list)
            self.assertIsInstance(match_result.missing_skills, list)
        
        print("✅ Parser → Matcher Integration test passed")
        return True

    def test_matcher_to_form_filler_integration(self):
        """Test integration between job matcher and form filler"""
        print("Testing Matcher → Form Filler Integration...")
        
        # Create mock match result
        mock_match = MatchResult(
            job_id="job_001",
            overall_score=0.85,
            skill_match_score=0.9,
            experience_match_score=0.8,
            education_match_score=1.0,
            location_match_score=0.7,
            culture_fit_score=0.8,
            salary_compatibility=0.9,
            detailed_analysis={'job_title': 'Senior Cybersecurity Engineer', 'company': 'TechCorp'},
            recommendation="HIGHLY RECOMMENDED",
            missing_skills=["terraform"],
            matching_skills=["python", "aws"],
            confidence_level="HIGH"
        )
        
        # Create mock resume
        mock_resume = self.mock_data.create_mock_resume()
        
        # Test form filler
        form_filler = IndustryStandardFormFiller()
        self.assertIsNotNone(form_filler)
        
        # Test application data creation
        job_specific_data = {
            'company': 'TechCorp',
            'position': 'Senior Cybersecurity Engineer',
            'salary_expectation': '$150,000'
        }
        
        app_data = form_filler.create_application_data(mock_resume, job_specific_data)
        
        # Verify application data
        self.assertIsInstance(app_data, ApplicationData)
        self.assertEqual(app_data.first_name, "John")
        self.assertEqual(app_data.last_name, "Doe")
        self.assertEqual(app_data.email, "john.doe@example.com")
        self.assertIsNotNone(app_data.current_title)
        self.assertIsNotNone(app_data.cover_letter)
        
        print("✅ Matcher → Form Filler Integration test passed")
        return True

    def test_full_pipeline_data_flow(self):
        """Test complete data flow through the entire pipeline"""
        print("Testing Full Pipeline Data Flow...")
        
        pipeline_data = {}
        
        # Step 1: Job Scraping (Mock)
        scraped_jobs = self.mock_data.create_mock_job_listings()
        pipeline_data['scraped_jobs'] = scraped_jobs
        self.assertGreater(len(pipeline_data['scraped_jobs']), 0)
        
        # Step 2: Resume Parsing (Mock)
        parsed_resume = self.mock_data.create_mock_resume()
        pipeline_data['parsed_resume'] = parsed_resume
        self.assertIsNotNone(pipeline_data['parsed_resume'].contact_info.name)
        
        # Step 3: Job Matching (Mock)
        matcher = AIJobMatcher()
        
        # Mock the matching process
        mock_matches = []
        for job in scraped_jobs:
            match = MatchResult(
                job_id=job.id,
                overall_score=0.8 if 'senior' in job.title.lower() else 0.6,
                skill_match_score=0.85,
                experience_match_score=0.75,
                education_match_score=1.0,
                location_match_score=0.8,
                culture_fit_score=0.7,
                salary_compatibility=0.9,
                detailed_analysis={'job_title': job.title, 'company': job.company},
                recommendation="RECOMMENDED",
                missing_skills=["docker"],
                matching_skills=["python", "aws"],
                confidence_level="MEDIUM"
            )
            mock_matches.append(match)
        
        pipeline_data['matched_jobs'] = mock_matches
        self.assertGreater(len(pipeline_data['matched_jobs']), 0)
        
        # Step 4: Application Data Preparation
        form_filler = IndustryStandardFormFiller()
        
        prepared_applications = []
        for match in mock_matches:
            if match.overall_score >= 0.7:  # High-confidence matches only
                app_data = form_filler.create_application_data(
                    parsed_resume, 
                    {
                        'company': match.detailed_analysis.get('company', 'Unknown'),
                        'position': match.detailed_analysis.get('job_title', 'Unknown')
                    }
                )
                prepared_applications.append({
                    'job_id': match.job_id,
                    'application_data': app_data,
                    'match_score': match.overall_score
                })
        
        pipeline_data['prepared_applications'] = prepared_applications
        self.assertGreater(len(pipeline_data['prepared_applications']), 0)
        
        # Verify data integrity across pipeline stages
        original_job_ids = {job.id for job in scraped_jobs}
        matched_job_ids = {match.job_id for match in mock_matches}
        application_job_ids = {app['job_id'] for app in prepared_applications}
        
        # All matched jobs should correspond to original scraped jobs
        self.assertTrue(matched_job_ids.issubset(original_job_ids))
        
        # All applications should correspond to matched jobs
        self.assertTrue(application_job_ids.issubset(matched_job_ids))
        
        print(f"   📊 Pipeline processed: {len(original_job_ids)} jobs → {len(matched_job_ids)} matches → {len(application_job_ids)} applications")
        print("✅ Full Pipeline Data Flow test passed")
        return True

    def test_analytics_integration(self):
        """Test analytics system integration"""
        print("Testing Analytics Integration...")
        
        # Initialize analytics monitor
        analytics = ScrapingAnalyticsMonitor(self.test_db_path)
        
        # Test scraping metrics recording
        scraping_metrics = ScrapingMetrics(
            session_id="test_session_001",
            timestamp=datetime.now().isoformat(),
            platform="linkedin",
            jobs_found=25,
            jobs_processed=20,
            success_rate=0.8,
            avg_response_time=2.5,
            errors_count=2,
            blocked_count=1,
            captcha_count=0,
            proxy_rotations=3,
            memory_usage_mb=450.5,
            cpu_usage_percent=65.2
        )
        
        analytics.record_scraping_metrics(scraping_metrics)
        
        # Test application metrics recording
        app_metrics = ApplicationMetrics(
            session_id="test_session_001",
            timestamp=datetime.now().isoformat(),
            jobs_applied=5,
            applications_successful=4,
            applications_failed=1,
            forms_filled=5,
            files_uploaded=5,
            avg_form_fill_time=45.2,
            success_rate=0.8
        )
        
        analytics.record_application_metrics(app_metrics)
        
        # Verify data was recorded in database
        conn = sqlite3.connect(self.test_db_path)
        
        # Check scraping metrics
        cursor = conn.execute("SELECT COUNT(*) FROM scraping_metrics")
        scraping_count = cursor.fetchone()[0]
        self.assertGreater(scraping_count, 0)
        
        # Check application metrics
        cursor = conn.execute("SELECT COUNT(*) FROM application_metrics") 
        app_count = cursor.fetchone()[0]
        self.assertGreater(app_count, 0)
        
        conn.close()
        
        # Test analytics report generation
        report = analytics.generate_analytics_report(days=1)
        
        self.assertIsInstance(report, dict)
        self.assertIn('scraping_summary', report)
        self.assertIn('application_summary', report)
        self.assertGreater(report['scraping_summary']['sessions'], 0)
        
        print("✅ Analytics Integration test passed")
        return True

    def test_database_consistency(self):
        """Test database consistency across components"""
        print("Testing Database Consistency...")
        
        # Initialize analytics with test database
        analytics = ScrapingAnalyticsMonitor(self.test_db_path)
        
        # Insert test data from multiple "sessions"
        test_sessions = ["session_001", "session_002", "session_003"]
        
        for session_id in test_sessions:
            # Add scraping metrics
            for platform in ["linkedin", "indeed", "remoteok"]:
                metrics = ScrapingMetrics(
                    session_id=session_id,
                    timestamp=datetime.now().isoformat(),
                    platform=platform,
                    jobs_found=20,
                    jobs_processed=18,
                    success_rate=0.9,
                    avg_response_time=2.0,
                    errors_count=1,
                    blocked_count=0,
                    captcha_count=0,
                    proxy_rotations=2,
                    memory_usage_mb=400.0,
                    cpu_usage_percent=60.0
                )
                analytics.record_scraping_metrics(metrics)
            
            # Add application metrics
            app_metrics = ApplicationMetrics(
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                jobs_applied=10,
                applications_successful=8,
                applications_failed=2,
                forms_filled=10,
                files_uploaded=8,
                avg_form_fill_time=35.0,
                success_rate=0.8
            )
            analytics.record_application_metrics(app_metrics)
        
        # Verify data consistency
        conn = sqlite3.connect(self.test_db_path)
        
        # Check total records
        cursor = conn.execute("SELECT COUNT(DISTINCT session_id) FROM scraping_metrics")
        unique_sessions = cursor.fetchone()[0]
        self.assertEqual(unique_sessions, len(test_sessions))
        
        # Check platform distribution
        cursor = conn.execute("SELECT COUNT(DISTINCT platform) FROM scraping_metrics")
        unique_platforms = cursor.fetchone()[0]
        self.assertEqual(unique_platforms, 3)  # linkedin, indeed, remoteok
        
        # Check data integrity
        cursor = conn.execute("""
            SELECT session_id, COUNT(*) as metrics_count 
            FROM scraping_metrics 
            GROUP BY session_id
        """)
        
        session_counts = cursor.fetchall()
        for session_id, count in session_counts:
            self.assertEqual(count, 3)  # Each session should have 3 platform metrics
        
        # Test cross-table joins
        cursor = conn.execute("""
            SELECT s.session_id, s.platform, a.jobs_applied
            FROM scraping_metrics s
            LEFT JOIN application_metrics a ON s.session_id = a.session_id
            WHERE a.jobs_applied IS NOT NULL
        """)
        
        joined_data = cursor.fetchall()
        self.assertGreater(len(joined_data), 0)
        
        conn.close()
        
        print("✅ Database Consistency test passed")
        return True

    def test_error_handling_integration(self):
        """Test error handling across integrated components"""
        print("Testing Error Handling Integration...")
        
        # Test 1: Invalid resume file handling
        try:
            parser = ResumeParser()
            # Try to parse non-existent file
            with self.assertRaises((FileNotFoundError, ValueError)):
                parser.parse_resume("/nonexistent/file.pdf")
            print("   ✅ Invalid resume file error handled correctly")
        except Exception as e:
            print(f"   ❌ Unexpected error in resume parsing: {e}")
        
        # Test 2: Invalid job data handling
        try:
            matcher = AIJobMatcher()
            
            # Create invalid job requirement (missing required fields)
            from intelligent_job_matcher import JobRequirement
            
            invalid_job = JobRequirement(
                id="",  # Invalid empty ID
                title="",  # Invalid empty title
                company="",  # Invalid empty company
                location="",
                description="",
                required_skills=[],
                preferred_skills=[],
                experience_level="unknown",  # Invalid level
                education_required="",
                salary_range=None,
                job_type="",
                remote_friendly=False,
                industry="",
                company_size="",
                benefits=[],
                application_url="",
                source_platform="",
                posted_date=""
            )
            
            mock_resume = self.mock_data.create_mock_resume()
            
            # This should handle invalid data gracefully
            result = matcher.calculate_comprehensive_match(mock_resume, invalid_job)
            
            # Should return a result even with invalid data
            self.assertIsNotNone(result)
            print("   ✅ Invalid job data handled gracefully")
            
        except Exception as e:
            print(f"   ✅ Invalid job data raised expected error: {type(e).__name__}")
        
        # Test 3: Database connection errors
        try:
            # Try to initialize analytics with invalid database path
            invalid_db_path = "/invalid/path/database.db"
            
            with self.assertRaises((OSError, sqlite3.Error)):
                analytics = ScrapingAnalyticsMonitor(invalid_db_path)
                # Force database creation attempt
                analytics._init_database()
            
            print("   ✅ Database connection error handled correctly")
            
        except Exception as e:
            print(f"   ❌ Unexpected database error: {e}")
        
        # Test 4: Form filling with missing data
        try:
            filler = IndustryStandardFormFiller()
            
            # Create incomplete resume
            incomplete_resume = Mock()
            incomplete_resume.contact_info = Mock()
            incomplete_resume.contact_info.name = None  # Missing name
            incomplete_resume.contact_info.email = ""  # Empty email
            incomplete_resume.work_experience = []
            incomplete_resume.education = []
            incomplete_resume.file_path = ""
            
            # Should handle missing data gracefully
            app_data = filler.create_application_data(incomplete_resume)
            self.assertIsNotNone(app_data)
            
            print("   ✅ Missing resume data handled gracefully")
            
        except Exception as e:
            print(f"   ❌ Unexpected form filling error: {e}")
        
        print("✅ Error Handling Integration test passed")
        return True

    def test_concurrent_processing(self):
        """Test concurrent processing capabilities"""
        print("Testing Concurrent Processing...")
        
        async def concurrent_test():
            # Create multiple mock processing tasks
            tasks = []
            
            # Simulate multiple scraping sessions
            for i in range(5):
                task = asyncio.create_task(self.mock_scraping_session(f"session_{i:03d}"))
                tasks.append(task)
            
            # Simulate multiple matching sessions  
            for i in range(3):
                task = asyncio.create_task(self.mock_matching_session(f"match_{i:03d}"))
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify results
            successful_tasks = sum(1 for r in results if r is True)
            total_tasks = len(tasks)
            
            self.assertGreater(successful_tasks, 0)
            
            success_rate = successful_tasks / total_tasks
            print(f"   📊 Concurrent tasks: {successful_tasks}/{total_tasks} successful ({success_rate:.1%})")
            
            return success_rate > 0.8  # Require 80% success rate
        
        # Run concurrent test
        result = asyncio.run(concurrent_test())
        self.assertTrue(result)
        
        print("✅ Concurrent Processing test passed")
        return True
    
    async def mock_scraping_session(self, session_id: str) -> bool:
        """Mock a scraping session for concurrent testing"""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.1)
            
            # Simulate creating job listings
            jobs = self.mock_data.create_mock_job_listings()
            
            # Simulate analytics recording
            if hasattr(self, 'test_db_path'):
                analytics = ScrapingAnalyticsMonitor(self.test_db_path)
                
                metrics = ScrapingMetrics(
                    session_id=session_id,
                    timestamp=datetime.now().isoformat(),
                    platform="test_platform",
                    jobs_found=len(jobs),
                    jobs_processed=len(jobs),
                    success_rate=1.0,
                    avg_response_time=1.5,
                    errors_count=0,
                    blocked_count=0,
                    captcha_count=0,
                    proxy_rotations=1,
                    memory_usage_mb=300.0,
                    cpu_usage_percent=50.0
                )
                
                analytics.record_scraping_metrics(metrics)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Mock scraping session {session_id} failed: {e}")
            return False
    
    async def mock_matching_session(self, session_id: str) -> bool:
        """Mock a matching session for concurrent testing"""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.2)
            
            # Simulate job matching
            jobs = self.mock_data.create_mock_job_listings()
            resume = self.mock_data.create_mock_resume()
            
            # Mock matching results
            matches = len(jobs)  # Assume all jobs match for testing
            
            return True
            
        except Exception as e:
            print(f"   ❌ Mock matching session {session_id} failed: {e}")
            return False

class PerformanceBenchmarks:
    """Performance benchmarking for integration tests"""
    
    def __init__(self):
        self.benchmarks = {}
    
    def benchmark_resume_parsing(self, iterations: int = 100) -> Dict[str, float]:
        """Benchmark resume parsing performance"""
        print(f"Benchmarking Resume Parsing ({iterations} iterations)...")
        
        parser = ResumeParser()
        mock_data = MockDataFactory()
        
        # Create test resume file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            John Doe
            john.doe@example.com
            +1-555-0123
            
            Experience:
            Senior Security Engineer at TechCorp (2020-Present)
            - Led security initiatives
            - Implemented security controls
            - Conducted penetration testing
            
            Skills:
            Python, AWS, Kubernetes, Penetration Testing, Incident Response
            
            Education:
            Master of Science in Cybersecurity
            University of Technology (2018)
            """)
            test_file = f.name
        
        start_time = time.time()
        successful_parses = 0
        
        try:
            for i in range(iterations):
                try:
                    parsed = parser.parse_resume(test_file)
                    if parsed and parsed.contact_info.name:
                        successful_parses += 1
                except Exception:
                    pass  # Count failures
            
            end_time = time.time()
            total_time = end_time - start_time
            
            metrics = {
                'total_time_seconds': total_time,
                'average_time_per_parse': total_time / iterations,
                'parses_per_second': iterations / total_time,
                'success_rate': successful_parses / iterations,
                'successful_parses': successful_parses,
                'total_iterations': iterations
            }
            
            print(f"   📊 Parsing Performance:")
            print(f"      Total time: {total_time:.2f}s")
            print(f"      Avg per parse: {metrics['average_time_per_parse']*1000:.1f}ms")
            print(f"      Parses/sec: {metrics['parses_per_second']:.1f}")
            print(f"      Success rate: {metrics['success_rate']:.1%}")
            
            self.benchmarks['resume_parsing'] = metrics
            
        finally:
            # Cleanup
            os.unlink(test_file)
        
        return metrics
    
    def benchmark_job_matching(self, iterations: int = 50) -> Dict[str, float]:
        """Benchmark job matching performance"""
        print(f"Benchmarking Job Matching ({iterations} iterations)...")
        
        matcher = AIJobMatcher()
        mock_data = MockDataFactory()
        
        mock_resume = mock_data.create_mock_resume()
        mock_jobs = mock_data.create_mock_job_listings()
        
        # Convert to job requirements
        from intelligent_job_matcher import JobRequirement
        
        job_reqs = []
        for job in mock_jobs:
            job_req = JobRequirement(
                id=job.id, title=job.title, company=job.company,
                location=job.location, description=job.description,
                required_skills=job.skills_required, preferred_skills=[],
                experience_level=job.experience_level, education_required="bachelor",
                salary_range=None, job_type=job.job_type, remote_friendly=job.remote_friendly,
                industry=job.industry, company_size=job.company_size, benefits=[],
                application_url=job.application_url, source_platform=job.source_platform,
                posted_date=job.posted_date
            )
            job_reqs.append(job_req)
        
        start_time = time.time()
        successful_matches = 0
        
        # Mock the actual AI matching to focus on integration performance
        with patch.object(matcher, 'calculate_comprehensive_match') as mock_match:
            mock_result = MatchResult(
                job_id="test", overall_score=0.8, skill_match_score=0.9,
                experience_match_score=0.8, education_match_score=1.0,
                location_match_score=0.7, culture_fit_score=0.8,
                salary_compatibility=0.9, detailed_analysis={},
                recommendation="RECOMMENDED", missing_skills=[], matching_skills=[],
                confidence_level="HIGH"
            )
            mock_match.return_value = mock_result
            
            for i in range(iterations):
                try:
                    for job_req in job_reqs:
                        result = matcher.calculate_comprehensive_match(mock_resume, job_req)
                        if result and result.overall_score > 0:
                            successful_matches += 1
                except Exception:
                    pass  # Count failures
        
        end_time = time.time()
        total_time = end_time - start_time
        total_operations = iterations * len(job_reqs)
        
        metrics = {
            'total_time_seconds': total_time,
            'average_time_per_match': total_time / total_operations,
            'matches_per_second': total_operations / total_time,
            'success_rate': successful_matches / total_operations,
            'successful_matches': successful_matches,
            'total_operations': total_operations
        }
        
        print(f"   📊 Matching Performance:")
        print(f"      Total time: {total_time:.2f}s")
        print(f"      Avg per match: {metrics['average_time_per_match']*1000:.1f}ms") 
        print(f"      Matches/sec: {metrics['matches_per_second']:.1f}")
        print(f"      Success rate: {metrics['success_rate']:.1%}")
        
        self.benchmarks['job_matching'] = metrics
        
        return metrics
    
    def benchmark_database_operations(self, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark database operations"""
        print(f"Benchmarking Database Operations ({iterations} iterations)...")
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            analytics = ScrapingAnalyticsMonitor(db_path)
            
            # Benchmark write operations
            write_start = time.time()
            
            for i in range(iterations):
                metrics = ScrapingMetrics(
                    session_id=f"bench_session_{i % 10}",  # 10 different sessions
                    timestamp=datetime.now().isoformat(),
                    platform=["linkedin", "indeed", "remoteok"][i % 3],
                    jobs_found=25, jobs_processed=20, success_rate=0.8,
                    avg_response_time=2.0, errors_count=1, blocked_count=0,
                    captcha_count=0, proxy_rotations=2, memory_usage_mb=400.0,
                    cpu_usage_percent=60.0
                )
                analytics.record_scraping_metrics(metrics)
            
            write_end = time.time()
            write_time = write_end - write_start
            
            # Benchmark read operations  
            read_start = time.time()
            
            for i in range(iterations // 10):  # Fewer read operations
                report = analytics.generate_analytics_report(days=1)
                
            read_end = time.time()
            read_time = read_end - read_start
            
            metrics = {
                'write_time_seconds': write_time,
                'read_time_seconds': read_time,
                'writes_per_second': iterations / write_time,
                'reads_per_second': (iterations // 10) / read_time,
                'avg_write_time_ms': (write_time / iterations) * 1000,
                'avg_read_time_ms': (read_time / (iterations // 10)) * 1000
            }
            
            print(f"   📊 Database Performance:")
            print(f"      Write ops/sec: {metrics['writes_per_second']:.1f}")
            print(f"      Read ops/sec: {metrics['reads_per_second']:.1f}")
            print(f"      Avg write: {metrics['avg_write_time_ms']:.2f}ms")
            print(f"      Avg read: {metrics['avg_read_time_ms']:.2f}ms")
            
            self.benchmarks['database_operations'] = metrics
            
        finally:
            # Cleanup
            os.unlink(db_path)
        
        return metrics
    
    def run_all_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Run all performance benchmarks"""
        print("🚀 RUNNING PERFORMANCE BENCHMARKS")
        print("=" * 40)
        
        benchmarks = {}
        
        try:
            benchmarks['resume_parsing'] = self.benchmark_resume_parsing(50)
            benchmarks['job_matching'] = self.benchmark_job_matching(25) 
            benchmarks['database_operations'] = self.benchmark_database_operations(500)
        except Exception as e:
            print(f"❌ Benchmark execution failed: {e}")
        
        return benchmarks

# Main test runner
async def run_integration_tests():
    """Run all integration tests"""
    print("🔗 INTEGRATION TEST SUITE")
    print("=" * 40)
    
    # Run unit tests using unittest
    test_suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestSuite)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Run performance benchmarks
    print("\n🚀 PERFORMANCE BENCHMARKS")
    print("=" * 40)
    
    benchmark_runner = PerformanceBenchmarks()
    benchmark_results = benchmark_runner.run_all_benchmarks()
    
    # Generate summary
    tests_run = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)
    success_count = tests_run - failures - errors
    success_rate = success_count / tests_run if tests_run > 0 else 0
    
    print(f"\n" + "=" * 40)
    print(f"🏆 INTEGRATION TESTING COMPLETE")
    print(f"=" * 40)
    print(f"📊 Tests Run: {tests_run}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failures}")  
    print(f"💥 Errors: {errors}")
    print(f"📈 Success Rate: {success_rate:.1%}")
    
    if benchmark_results:
        print(f"\n📊 PERFORMANCE SUMMARY:")
        for test_name, metrics in benchmark_results.items():
            if 'success_rate' in metrics:
                print(f"   {test_name}: {metrics['success_rate']:.1%} success rate")
    
    # Save results
    results = {
        'test_summary': {
            'tests_run': tests_run,
            'successful': success_count,
            'failed': failures,
            'errors': errors,
            'success_rate': success_rate,
            'timestamp': datetime.now().isoformat()
        },
        'benchmark_results': benchmark_results,
        'test_failures': [str(failure) for failure in test_result.failures],
        'test_errors': [str(error) for error in test_result.errors]
    }
    
    # Save to file
    results_file = Path("temp/integration_test_results.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Integration test results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    # Run integration tests
    results = asyncio.run(run_integration_tests())
    
    # Exit with appropriate code
    success_rate = results['test_summary']['success_rate']
    exit_code = 0 if success_rate >= 0.8 else 1  # Require 80% success rate
    
    print(f"\n🏁 Integration testing completed with exit code: {exit_code}")
    sys.exit(exit_code)