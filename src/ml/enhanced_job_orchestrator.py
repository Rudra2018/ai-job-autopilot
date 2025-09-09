#!/usr/bin/env python3
"""
Enhanced Job Application Orchestrator
Advanced orchestrator using the new resume processing pipeline for maximum accuracy
"""

import asyncio
import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
import yaml
import random

# Import our enhanced pipeline components
from src.core.resume_processing_pipeline import (
    ResumeProcessingPipeline, PipelineConfig, PipelineResult,
    process_resume_complete, process_resume_for_job
)
from src.core.enhanced_resume_parser import ParsedResume
from src.ml.ai_resume_enhancer import EnhancedResumeData, JobMatchScore

@dataclass
class EnhancedApplicationSession:
    """Enhanced application session with pipeline results"""
    session_id: str
    start_time: str
    resume_file: str
    
    # Pipeline results
    pipeline_result: Optional[PipelineResult] = None
    parsed_resume: Optional[ParsedResume] = None
    enhanced_data: Optional[EnhancedResumeData] = None
    
    # Job processing
    target_jobs: List[Dict] = field(default_factory=list)
    job_matches: List[Tuple[Dict, JobMatchScore]] = field(default_factory=list)
    applied_jobs: List[Dict] = field(default_factory=list)
    failed_applications: List[Dict] = field(default_factory=list)
    
    # Session configuration
    user_preferences: Dict = field(default_factory=dict)
    pipeline_config: Optional[PipelineConfig] = None
    
    # Performance metrics
    session_stats: Dict = field(default_factory=dict)
    processing_times: Dict = field(default_factory=dict)
    quality_metrics: Dict = field(default_factory=dict)
    
    end_time: Optional[str] = None

@dataclass
class ApplicationResult:
    """Result of a job application attempt"""
    job_id: str
    job_title: str
    company: str
    application_url: str
    status: str  # success, failed, skipped, review_required, match_too_low
    applied_at: str
    
    # Enhanced matching data
    match_score: Optional[JobMatchScore] = None
    confidence_score: float = 0.0
    
    # Application details
    form_data_used: Dict = field(default_factory=dict)
    application_method: str = ""  # auto_form, linkedin_easy_apply, manual_review
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

class EnhancedJobOrchestrator:
    """Enhanced job application orchestrator with improved resume processing"""
    
    def __init__(self, config_path: str = "config/orchestrator_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize pipeline with configuration
        self.pipeline_config = self._create_pipeline_config()
        self.resume_pipeline = ResumeProcessingPipeline(self.pipeline_config)
        
        # Session state
        self.current_session: Optional[EnhancedApplicationSession] = None
        
        # Performance tracking
        self.session_history: List[EnhancedApplicationSession] = []
        
    def _load_config(self) -> Dict:
        """Load orchestrator configuration"""
        try:
            config_path = Path(self.config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            self.logger.warning(f"Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "resume_processing": {
                "enable_ai_enhancement": True,
                "enable_job_matching": True,
                "min_confidence_threshold": 0.6,
                "use_ocr_fallback": True,
                "clean_extracted_text": True
            },
            "job_matching": {
                "min_match_score": 0.3,
                "prefer_high_confidence": True,
                "max_applications_per_session": 50
            },
            "application": {
                "auto_apply_threshold": 0.7,
                "review_required_threshold": 0.5,
                "skip_below_threshold": 0.3,
                "delay_between_applications": (30, 120)  # seconds
            },
            "quality_assurance": {
                "validate_contact_info": True,
                "check_duplicate_applications": True,
                "verify_form_completion": True
            }
        }
    
    def _create_pipeline_config(self) -> PipelineConfig:
        """Create pipeline configuration from orchestrator config"""
        resume_config = self.config.get("resume_processing", {})
        
        return PipelineConfig(
            enable_ai_enhancement=resume_config.get("enable_ai_enhancement", True),
            enable_job_matching=resume_config.get("enable_job_matching", True),
            min_confidence_threshold=resume_config.get("min_confidence_threshold", 0.6),
            use_ocr_fallback=resume_config.get("use_ocr_fallback", True),
            clean_extracted_text=resume_config.get("clean_extracted_text", True),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            save_intermediate_results=True,
            enable_validation=True
        )
    
    async def start_application_session(
        self, 
        resume_file: str, 
        target_jobs: List[Dict],
        user_preferences: Optional[Dict] = None
    ) -> EnhancedApplicationSession:
        """Start a new enhanced application session"""
        
        session_id = f"session_{int(datetime.now().timestamp())}"
        session = EnhancedApplicationSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            resume_file=resume_file,
            target_jobs=target_jobs,
            user_preferences=user_preferences or {},
            pipeline_config=self.pipeline_config
        )
        
        self.current_session = session
        self.logger.info(f"Starting enhanced application session: {session_id}")
        
        try:
            # Phase 1: Process Resume with Enhanced Pipeline
            await self._process_resume_phase(session)
            
            # Phase 2: Analyze and Match Jobs
            await self._job_matching_phase(session)
            
            # Phase 3: Execute Applications
            await self._application_execution_phase(session)
            
            # Phase 4: Generate Session Report
            self._generate_session_report(session)
            
        except Exception as e:
            self.logger.error(f"Session {session_id} failed: {e}")
            session.session_stats["session_error"] = str(e)
        finally:
            session.end_time = datetime.now().isoformat()
            self.session_history.append(session)
        
        return session
    
    async def _process_resume_phase(self, session: EnhancedApplicationSession):
        """Phase 1: Process resume using enhanced pipeline"""
        self.logger.info("Phase 1: Processing resume with enhanced pipeline")
        phase_start = datetime.now()
        
        try:
            # Process resume through pipeline
            session.pipeline_result = self.resume_pipeline.process_resume(session.resume_file)
            
            if not session.pipeline_result.overall_success:
                raise ValueError(f"Resume processing failed: {', '.join(session.pipeline_result.errors)}")
            
            # Extract key data
            session.parsed_resume = session.pipeline_result.parsed_resume
            session.enhanced_data = session.pipeline_result.enhanced_data
            
            # Validate critical information
            if not self._validate_resume_data(session.parsed_resume):
                raise ValueError("Resume lacks critical information for job applications")
            
            # Log processing metrics
            processing_time = (datetime.now() - phase_start).total_seconds()
            session.processing_times["resume_processing"] = processing_time
            session.quality_metrics["resume_confidence"] = session.pipeline_result.confidence_score
            session.quality_metrics["resume_quality"] = session.pipeline_result.quality_score
            
            self.logger.info(f"Resume processed successfully. Confidence: {session.pipeline_result.confidence_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Resume processing phase failed: {e}")
            raise
    
    async def _job_matching_phase(self, session: EnhancedApplicationSession):
        """Phase 2: Match jobs against processed resume"""
        self.logger.info("Phase 2: Matching jobs against resume")
        phase_start = datetime.now()
        
        try:
            job_matches = []
            matching_config = self.config.get("job_matching", {})
            min_match_score = matching_config.get("min_match_score", 0.3)
            
            for job in session.target_jobs:
                try:
                    # Extract job description
                    job_description = self._extract_job_description(job)
                    
                    # Calculate match using AI enhancer
                    if session.enhanced_data and hasattr(self.resume_pipeline, 'ai_enhancer'):
                        match_score = self.resume_pipeline.ai_enhancer.calculate_job_match(
                            session.parsed_resume, 
                            job_description
                        )
                    else:
                        # Fallback to basic matching
                        match_score = self._calculate_basic_match(session.parsed_resume, job_description)
                    
                    # Filter by minimum match score
                    if match_score.overall_match >= min_match_score:
                        job_matches.append((job, match_score))
                        self.logger.debug(f"Job {job.get('title', 'Unknown')} matched with score: {match_score.overall_match:.2f}")
                    else:
                        self.logger.debug(f"Job {job.get('title', 'Unknown')} below threshold: {match_score.overall_match:.2f}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to match job {job.get('id', 'unknown')}: {e}")
                    continue
            
            # Sort by match score (best matches first)
            job_matches.sort(key=lambda x: x[1].overall_match, reverse=True)
            session.job_matches = job_matches
            
            # Apply session limits
            max_applications = matching_config.get("max_applications_per_session", 50)
            session.job_matches = session.job_matches[:max_applications]
            
            processing_time = (datetime.now() - phase_start).total_seconds()
            session.processing_times["job_matching"] = processing_time
            
            self.logger.info(f"Found {len(session.job_matches)} suitable job matches")
            
        except Exception as e:
            self.logger.error(f"Job matching phase failed: {e}")
            raise
    
    async def _application_execution_phase(self, session: EnhancedApplicationSession):
        """Phase 3: Execute job applications"""
        self.logger.info("Phase 3: Executing job applications")
        phase_start = datetime.now()
        
        application_config = self.config.get("application", {})
        auto_apply_threshold = application_config.get("auto_apply_threshold", 0.7)
        review_threshold = application_config.get("review_required_threshold", 0.5)
        skip_threshold = application_config.get("skip_below_threshold", 0.3)
        
        delay_range = application_config.get("delay_between_applications", (30, 120))
        
        try:
            for i, (job, match_score) in enumerate(session.job_matches):
                try:
                    # Determine application strategy
                    if match_score.overall_match >= auto_apply_threshold:
                        strategy = "auto_apply"
                    elif match_score.overall_match >= review_threshold:
                        strategy = "review_required"
                    elif match_score.overall_match >= skip_threshold:
                        strategy = "manual_review"
                    else:
                        strategy = "skip"
                    
                    # Execute application based on strategy
                    result = await self._execute_single_application(
                        session, job, match_score, strategy
                    )
                    
                    if result.status == "success":
                        session.applied_jobs.append(result)
                    else:
                        session.failed_applications.append(result)
                    
                    # Add delay between applications (human-like behavior)
                    if i < len(session.job_matches) - 1:
                        delay = random.randint(*delay_range)
                        self.logger.debug(f"Waiting {delay}s before next application...")
                        await asyncio.sleep(delay)
                        
                except Exception as e:
                    self.logger.error(f"Failed to apply to job {job.get('id', 'unknown')}: {e}")
                    
                    error_result = ApplicationResult(
                        job_id=job.get("id", "unknown"),
                        job_title=job.get("title", "Unknown"),
                        company=job.get("company", "Unknown"),
                        application_url=job.get("url", ""),
                        status="failed",
                        applied_at=datetime.now().isoformat(),
                        match_score=match_score,
                        error_message=str(e)
                    )
                    session.failed_applications.append(error_result)
            
            processing_time = (datetime.now() - phase_start).total_seconds()
            session.processing_times["application_execution"] = processing_time
            
        except Exception as e:
            self.logger.error(f"Application execution phase failed: {e}")
            raise
    
    async def _execute_single_application(
        self, 
        session: EnhancedApplicationSession, 
        job: Dict, 
        match_score: JobMatchScore, 
        strategy: str
    ) -> ApplicationResult:
        """Execute a single job application"""
        
        job_id = job.get("id", f"job_{int(datetime.now().timestamp())}")
        self.logger.info(f"Applying to {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} (Strategy: {strategy})")
        
        result = ApplicationResult(
            job_id=job_id,
            job_title=job.get("title", "Unknown"),
            company=job.get("company", "Unknown"),
            application_url=job.get("url", ""),
            status="pending",
            applied_at=datetime.now().isoformat(),
            match_score=match_score,
            confidence_score=session.pipeline_result.confidence_score if session.pipeline_result else 0.0
        )
        
        try:
            if strategy == "auto_apply":
                # Attempt automated application
                success = await self._auto_apply_to_job(session, job, result)
                result.status = "success" if success else "failed"
                result.application_method = "automated"
                
            elif strategy == "review_required":
                # Mark for manual review
                result.status = "review_required"
                result.application_method = "manual_review"
                self.logger.info(f"Job {job_id} marked for manual review")
                
            elif strategy == "manual_review":
                # Save for later manual processing
                result.status = "manual_review"
                result.application_method = "manual"
                
            else:  # skip
                result.status = "skipped"
                result.application_method = "none"
                self.logger.info(f"Skipping job {job_id} - match score too low")
        
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)
            self.logger.error(f"Application to job {job_id} failed: {e}")
        
        return result
    
    async def _auto_apply_to_job(
        self, 
        session: EnhancedApplicationSession, 
        job: Dict, 
        result: ApplicationResult
    ) -> bool:
        """Attempt automated application to a job"""
        
        try:
            # Prepare application data from processed resume
            application_data = self._prepare_application_data(session.parsed_resume, job)
            
            # Check if this is a supported platform
            job_url = job.get("url", "")
            
            if "linkedin.com" in job_url:
                return await self._apply_via_linkedin(session, job, application_data, result)
            elif "indeed.com" in job_url:
                return await self._apply_via_indeed(session, job, application_data, result)
            else:
                # Generic form-based application
                return await self._apply_via_generic_form(session, job, application_data, result)
        
        except Exception as e:
            self.logger.error(f"Auto-apply failed: {e}")
            return False
    
    async def _apply_via_linkedin(
        self, 
        session: EnhancedApplicationSession, 
        job: Dict, 
        application_data: Dict, 
        result: ApplicationResult
    ) -> bool:
        """Apply via LinkedIn Easy Apply"""
        # Placeholder for LinkedIn application logic
        # This would integrate with LinkedIn automation
        self.logger.info("LinkedIn Easy Apply not yet implemented")
        result.warnings.append("LinkedIn Easy Apply feature pending implementation")
        return False
    
    async def _apply_via_indeed(
        self, 
        session: EnhancedApplicationSession, 
        job: Dict, 
        application_data: Dict, 
        result: ApplicationResult
    ) -> bool:
        """Apply via Indeed"""
        # Placeholder for Indeed application logic
        self.logger.info("Indeed application not yet implemented")
        result.warnings.append("Indeed application feature pending implementation")
        return False
    
    async def _apply_via_generic_form(
        self, 
        session: EnhancedApplicationSession, 
        job: Dict, 
        application_data: Dict, 
        result: ApplicationResult
    ) -> bool:
        """Apply via generic form filling"""
        # Placeholder for generic form application
        self.logger.info("Generic form application not yet implemented")
        result.warnings.append("Generic form application feature pending implementation")
        return False
    
    def _validate_resume_data(self, resume: ParsedResume) -> bool:
        """Validate that resume has critical information for applications"""
        if not resume.contact_info.email:
            return False
        if not resume.contact_info.name:
            return False
        if not resume.work_experience:
            return False
        return True
    
    def _extract_job_description(self, job: Dict) -> str:
        """Extract job description text from job data"""
        description_fields = ["description", "job_description", "details", "requirements"]
        
        for field in description_fields:
            if field in job and job[field]:
                return str(job[field])
        
        # Fallback: combine available text fields
        text_parts = []
        for key, value in job.items():
            if isinstance(value, str) and len(value) > 20:
                text_parts.append(value)
        
        return " ".join(text_parts)
    
    def _calculate_basic_match(self, resume: ParsedResume, job_description: str) -> JobMatchScore:
        """Calculate basic job match score without AI"""
        match_score = JobMatchScore()
        
        # Simple keyword matching
        job_text = job_description.lower()
        resume_skills = [skill.lower() for skill in resume.skills]
        
        # Count skill matches
        matched_skills = []
        for skill in resume_skills:
            if skill in job_text:
                matched_skills.append(skill)
        
        match_score.matched_skills = matched_skills
        match_score.skill_match = len(matched_skills) / max(len(resume_skills), 1)
        match_score.overall_match = match_score.skill_match * 0.8 + 0.2  # Base score
        
        return match_score
    
    def _prepare_application_data(self, resume: ParsedResume, job: Dict) -> Dict:
        """Prepare application data from processed resume"""
        return {
            "personal_info": {
                "first_name": resume.contact_info.name.split()[0] if resume.contact_info.name else "",
                "last_name": " ".join(resume.contact_info.name.split()[1:]) if resume.contact_info.name else "",
                "email": resume.contact_info.email,
                "phone": resume.contact_info.phone,
                "address": resume.contact_info.address,
                "linkedin": resume.contact_info.linkedin
            },
            "professional": {
                "summary": resume.summary,
                "experience": [asdict(exp) for exp in resume.work_experience],
                "education": [asdict(edu) for edu in resume.education],
                "skills": resume.skills
            },
            "job_specific": {
                "job_title": job.get("title", ""),
                "company": job.get("company", ""),
                "cover_letter": self._generate_cover_letter(resume, job)
            }
        }
    
    def _generate_cover_letter(self, resume: ParsedResume, job: Dict) -> str:
        """Generate a basic cover letter"""
        # Placeholder - could be enhanced with AI
        return f"""Dear Hiring Manager,

I am writing to express my interest in the {job.get('title', 'position')} role at {job.get('company', 'your company')}. 

With {len(resume.work_experience)} years of experience and expertise in {', '.join(resume.skills[:5])}, I believe I would be a valuable addition to your team.

{resume.summary}

I look forward to hearing from you.

Best regards,
{resume.contact_info.name}"""
    
    def _generate_session_report(self, session: EnhancedApplicationSession):
        """Generate comprehensive session report"""
        
        total_jobs = len(session.target_jobs)
        matched_jobs = len(session.job_matches)
        applied_jobs = len(session.applied_jobs)
        failed_jobs = len(session.failed_applications)
        
        session.session_stats = {
            "session_summary": {
                "total_jobs_analyzed": total_jobs,
                "jobs_matched": matched_jobs,
                "applications_submitted": applied_jobs,
                "applications_failed": failed_jobs,
                "success_rate": applied_jobs / max(matched_jobs, 1),
                "match_rate": matched_jobs / max(total_jobs, 1)
            },
            "resume_processing": {
                "extraction_method": session.pipeline_result.extraction_result.method if session.pipeline_result else "unknown",
                "extraction_confidence": session.pipeline_result.extraction_result.confidence if session.pipeline_result else 0.0,
                "parsing_confidence": session.pipeline_result.confidence_score if session.pipeline_result else 0.0,
                "quality_score": session.pipeline_result.quality_score if session.pipeline_result else 0.0
            },
            "performance_metrics": session.processing_times,
            "quality_metrics": session.quality_metrics
        }
        
        self.logger.info(f"Session {session.session_id} completed:")
        self.logger.info(f"  • Jobs analyzed: {total_jobs}")
        self.logger.info(f"  • Matches found: {matched_jobs}")
        self.logger.info(f"  • Applications submitted: {applied_jobs}")
        self.logger.info(f"  • Success rate: {session.session_stats['session_summary']['success_rate']:.1%}")
    
    def export_session_report(self, session: EnhancedApplicationSession, output_path: Optional[str] = None) -> str:
        """Export detailed session report"""
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"job_application_report_{session.session_id}_{timestamp}.json"
        
        report_data = {
            "session_info": {
                "session_id": session.session_id,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "resume_file": session.resume_file
            },
            "pipeline_results": asdict(session.pipeline_result) if session.pipeline_result else {},
            "job_matches": [(asdict(job), asdict(match)) for job, match in session.job_matches],
            "applications": {
                "successful": [asdict(app) for app in session.applied_jobs],
                "failed": [asdict(app) for app in session.failed_applications]
            },
            "session_statistics": session.session_stats,
            "configuration": asdict(session.pipeline_config) if session.pipeline_config else {}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"Session report exported to: {output_path}")
        return output_path
    
    def get_session_history(self) -> List[EnhancedApplicationSession]:
        """Get history of all application sessions"""
        return self.session_history
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all sessions"""
        if not self.session_history:
            return {}
        
        total_sessions = len(self.session_history)
        total_applications = sum(len(s.applied_jobs) for s in self.session_history)
        total_matches = sum(len(s.job_matches) for s in self.session_history)
        
        avg_confidence = sum(
            s.pipeline_result.confidence_score for s in self.session_history 
            if s.pipeline_result
        ) / max(total_sessions, 1)
        
        return {
            "total_sessions": total_sessions,
            "total_applications": total_applications, 
            "total_matches": total_matches,
            "average_confidence": avg_confidence,
            "average_applications_per_session": total_applications / max(total_sessions, 1),
            "overall_success_rate": sum(
                len(s.applied_jobs) / max(len(s.job_matches), 1) 
                for s in self.session_history
            ) / max(total_sessions, 1)
        }

# Convenience functions
async def run_job_application_session(
    resume_file: str,
    target_jobs: List[Dict],
    config_path: Optional[str] = None,
    openai_api_key: Optional[str] = None
) -> EnhancedApplicationSession:
    """Run a complete job application session"""
    
    orchestrator = EnhancedJobOrchestrator(config_path)
    
    # Set OpenAI key if provided
    if openai_api_key:
        orchestrator.pipeline_config.openai_api_key = openai_api_key
    
    session = await orchestrator.start_application_session(
        resume_file=resume_file,
        target_jobs=target_jobs
    )
    
    return session

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_job_orchestrator.py <resume_file.pdf>")
        sys.exit(1)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example job data (normally would come from scrapers)
    sample_jobs = [
        {
            "id": "job1",
            "title": "Python Developer",
            "company": "TechCorp",
            "url": "https://example.com/job1",
            "description": "We are looking for a Python developer with experience in Django, FastAPI, and cloud technologies."
        },
        {
            "id": "job2", 
            "title": "Data Scientist",
            "company": "DataInc",
            "url": "https://example.com/job2",
            "description": "Data scientist role requiring Python, machine learning, pandas, and statistical analysis skills."
        }
    ]
    
    async def main():
        session = await run_job_application_session(
            resume_file=sys.argv[1],
            target_jobs=sample_jobs
        )
        
        # Print results
        print(f"\n{'='*60}")
        print(f"JOB APPLICATION SESSION RESULTS")
        print(f"{'='*60}")
        print(f"Session ID: {session.session_id}")
        print(f"Resume Confidence: {session.pipeline_result.confidence_score:.2f}")
        print(f"Jobs Analyzed: {len(session.target_jobs)}")
        print(f"Matches Found: {len(session.job_matches)}")
        print(f"Applications Submitted: {len(session.applied_jobs)}")
        print(f"Failed Applications: {len(session.failed_applications)}")
        
        if session.job_matches:
            print(f"\nTop Job Matches:")
            for i, (job, match) in enumerate(session.job_matches[:5]):
                print(f"{i+1}. {job['title']} at {job['company']} - Match: {match.overall_match:.2f}")
    
    # Run the async main function
    asyncio.run(main())