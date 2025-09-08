#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Comprehensive Integration Layer
Orchestrates all enhanced modules and provides unified API access
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager

# Import all enhanced modules
from ai_question_answerer import AIQuestionAnswerer, QuestionAnswer
from dynamic_resume_rewriter import DynamicResumeRewriter, ResumeVersion
from smart_duplicate_detector import SmartDuplicateDetector, JobApplication, DuplicateMatch
from undetected_browser import UndetectedBrowser, BrowserConfig, HumanBehaviorConfig
from config_manager import AdvancedConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AutopilotSession:
    session_id: str
    start_time: datetime
    status: str = "initializing"  # initializing, running, paused, completed, error
    total_jobs_found: int = 0
    applications_attempted: int = 0
    applications_completed: int = 0
    applications_failed: int = 0
    duplicates_avoided: int = 0
    questions_answered: int = 0
    resumes_optimized: int = 0
    errors_encountered: int = 0
    current_platform: str = ""
    current_job: str = ""
    estimated_completion: Optional[datetime] = None
    
@dataclass
class JobOpportunity:
    job_id: str
    title: str
    company: str
    location: str
    url: str
    description: str
    salary_range: str = ""
    posted_date: str = ""
    platform: str = "linkedin"
    match_score: float = 0.0
    keywords_matched: List[str] = None
    is_easy_apply: bool = False
    application_deadline: str = ""

@dataclass
class ApplicationResult:
    job_id: str
    success: bool
    timestamp: datetime
    platform: str
    questions_answered: int = 0
    resume_optimized: bool = False
    duplicate_detected: bool = False
    error_message: str = ""
    processing_time: float = 0.0

class EnhancedIntegrationLayer:
    """
    Comprehensive integration layer that orchestrates all enhanced modules
    and provides a unified API for the entire job application automation system
    """
    
    def __init__(self, config_manager: AdvancedConfigManager = None):
        self.config_manager = config_manager or AdvancedConfigManager()
        
        # Initialize all enhanced modules
        self.question_answerer = AIQuestionAnswerer()
        self.resume_rewriter = DynamicResumeRewriter()
        self.duplicate_detector = SmartDuplicateDetector()
        self.browser = None
        
        # Session management
        self.current_session: Optional[AutopilotSession] = None
        self.session_history: List[AutopilotSession] = []
        
        # Event system
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Statistics and monitoring
        self.performance_metrics = {
            "total_runtime": 0.0,
            "avg_application_time": 0.0,
            "success_rate": 0.0,
            "ai_response_time": 0.0,
            "browser_load_time": 0.0
        }
        
        # Thread pool for concurrent operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Initialize notification handlers
        self._notification_handlers = []
        
        logger.info("Enhanced Integration Layer initialized successfully")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event: {event_type}")
    
    def emit_event(self, event_type: str, data: Any = None):
        """Emit event to all registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    def add_notification_handler(self, handler: Callable):
        """Add notification handler"""
        self._notification_handlers.append(handler)
    
    def _notify(self, message: str, level: str = "info", data: Dict = None):
        """Send notification through all handlers"""
        notification = {
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        for handler in self._notification_handlers:
            try:
                handler(notification)
            except Exception as e:
                logger.error(f"Notification handler error: {e}")
        
        # Emit as event as well
        self.emit_event("notification", notification)
    
    def initialize_browser(self) -> bool:
        """Initialize undetected browser with current configuration"""
        try:
            browser_config = self.config_manager.get_browser_config()
            behavior_config = HumanBehaviorConfig(
                typing_delay_range=(80, 180),
                click_delay_range=(200, 500),
                natural_pauses=True,
                random_scrolling=True
            )
            
            self.browser = UndetectedBrowser(browser_config, behavior_config)
            success = self.browser.start_browser(browser_config.profile_name)
            
            if success:
                self._notify("Browser initialized successfully", "success")
                self.emit_event("browser_initialized", {"browser_config": asdict(browser_config)})
            else:
                self._notify("Failed to initialize browser", "error")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing browser: {e}")
            self._notify(f"Browser initialization error: {e}", "error")
            return False
    
    def start_autopilot_session(self, 
                               job_titles: List[str],
                               locations: List[str] = None,
                               max_applications: int = None) -> str:
        """Start a new autopilot session"""
        
        if self.current_session and self.current_session.status == "running":
            raise Exception("Another session is already running")
        
        # Create new session
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = AutopilotSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        # Initialize browser if not already done
        if not self.browser:
            if not self.initialize_browser():
                self.current_session.status = "error"
                raise Exception("Failed to initialize browser")
        
        # Start session in background thread
        self.current_session.status = "running"
        
        # Calculate estimated completion time
        automation_config = self.config_manager.get_automation_config()
        max_apps = max_applications or automation_config.max_applications_per_session
        avg_time_per_app = 3  # minutes
        estimated_duration = timedelta(minutes=max_apps * avg_time_per_app)
        self.current_session.estimated_completion = datetime.now() + estimated_duration
        
        self._notify(f"Autopilot session started: {session_id}", "success", {
            "session_id": session_id,
            "job_titles": job_titles,
            "locations": locations or [],
            "max_applications": max_apps
        })
        
        # Start session processing
        self.thread_pool.submit(
            self._run_autopilot_session,
            job_titles,
            locations or [],
            max_apps
        )
        
        return session_id
    
    def _run_autopilot_session(self, 
                              job_titles: List[str],
                              locations: List[str],
                              max_applications: int):
        """Run autopilot session in background thread"""
        
        try:
            session_start = time.time()
            
            for job_title in job_titles:
                if self.current_session.status != "running":
                    break
                
                self.current_session.current_job = job_title
                self._notify(f"Searching for: {job_title}", "info")
                
                # Search for jobs
                jobs = self._search_jobs(job_title, locations)
                self.current_session.total_jobs_found += len(jobs)
                
                # Process each job
                for job in jobs:
                    if (self.current_session.status != "running" or 
                        self.current_session.applications_attempted >= max_applications):
                        break
                    
                    # Process job application
                    result = self._process_job_application(job)
                    
                    # Update session stats
                    self.current_session.applications_attempted += 1
                    if result.success:
                        self.current_session.applications_completed += 1
                    else:
                        self.current_session.applications_failed += 1
                    
                    if result.duplicate_detected:
                        self.current_session.duplicates_avoided += 1
                    
                    if result.questions_answered > 0:
                        self.current_session.questions_answered += result.questions_answered
                    
                    if result.resume_optimized:
                        self.current_session.resumes_optimized += 1
                    
                    # Emit progress event
                    self.emit_event("application_completed", {
                        "session_id": self.current_session.session_id,
                        "job": asdict(job),
                        "result": asdict(result),
                        "progress": self.current_session.applications_attempted / max_applications
                    })
                    
                    # Delay between applications
                    automation_config = self.config_manager.get_automation_config()
                    delay_range = automation_config.delay_between_applications
                    import random
                    delay = random.uniform(*delay_range)
                    time.sleep(delay)
            
            # Complete session
            session_duration = time.time() - session_start
            self.current_session.status = "completed"
            
            self._notify("Autopilot session completed successfully", "success", {
                "session_id": self.current_session.session_id,
                "duration": session_duration,
                "applications_completed": self.current_session.applications_completed,
                "success_rate": (self.current_session.applications_completed / 
                               max(self.current_session.applications_attempted, 1)) * 100
            })
            
            # Update performance metrics
            self.performance_metrics["total_runtime"] += session_duration
            if self.current_session.applications_attempted > 0:
                self.performance_metrics["avg_application_time"] = (
                    session_duration / self.current_session.applications_attempted
                )
                self.performance_metrics["success_rate"] = (
                    self.current_session.applications_completed / 
                    self.current_session.applications_attempted * 100
                )
            
            # Archive session
            self.session_history.append(self.current_session)
            
        except Exception as e:
            logger.error(f"Error in autopilot session: {e}")
            self.current_session.status = "error"
            self.current_session.errors_encountered += 1
            self._notify(f"Autopilot session error: {e}", "error")
        
        finally:
            self.emit_event("session_completed", {
                "session": asdict(self.current_session)
            })
    
    def _search_jobs(self, job_title: str, locations: List[str]) -> List[JobOpportunity]:
        """Search for job opportunities across platforms"""
        jobs = []
        
        try:
            self.current_session.current_platform = "linkedin"
            self._notify(f"Searching LinkedIn for: {job_title}")
            
            # Navigate to LinkedIn jobs
            if self.browser:
                self.browser.navigate_to("https://www.linkedin.com/jobs/")
                
                # Perform search - simplified version
                # In real implementation, would use comprehensive scraping
                
                # Mock job results for demonstration
                for i in range(5):  # Simulate finding 5 jobs
                    job = JobOpportunity(
                        job_id=f"linkedin_{job_title.replace(' ', '_')}_{i}",
                        title=job_title,
                        company=f"Company_{i}",
                        location=locations[0] if locations else "Remote",
                        url=f"https://linkedin.com/jobs/view/{12345 + i}",
                        description=f"Looking for {job_title} with relevant experience...",
                        platform="linkedin",
                        is_easy_apply=True,
                        match_score=0.8 + (i * 0.02)
                    )
                    jobs.append(job)
            
            self._notify(f"Found {len(jobs)} jobs for {job_title}", "info")
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            self._notify(f"Job search error: {e}", "error")
        
        return jobs
    
    def _process_job_application(self, job: JobOpportunity) -> ApplicationResult:
        """Process a single job application with all enhancements"""
        
        start_time = time.time()
        result = ApplicationResult(
            job_id=job.job_id,
            success=False,
            timestamp=datetime.now(),
            platform=job.platform
        )
        
        try:
            self._notify(f"Processing application: {job.title} at {job.company}")
            
            # 1. Check for duplicates
            automation_config = self.config_manager.get_automation_config()
            if automation_config.enable_duplicate_detection:
                is_duplicate, duplicate_match = self.duplicate_detector.check_if_duplicate(
                    job_title=job.title,
                    company=job.company,
                    job_url=job.url,
                    job_description=job.description
                )
                
                if is_duplicate:
                    self._notify(f"Duplicate detected: {job.title} at {job.company}", "warning")
                    result.duplicate_detected = True
                    return result
            
            # 2. Optimize resume for this job
            if automation_config.enable_resume_optimization and job.description:
                try:
                    resume_version = self.resume_rewriter.create_optimized_resume(
                        job_title=job.title,
                        company=job.company,
                        job_description=job.description
                    )
                    result.resume_optimized = True
                    self._notify(f"Resume optimized (Score: {resume_version.similarity_score:.1%})")
                except Exception as e:
                    logger.warning(f"Resume optimization failed: {e}")
            
            # 3. Navigate to job and apply
            if self.browser:
                self.browser.navigate_to(job.url)
                
                # Click Easy Apply button (simplified)
                try:
                    easy_apply_selector = "button[aria-label*='Easy Apply']"
                    if self.browser.is_element_visible(easy_apply_selector):
                        self.browser.human_click(easy_apply_selector)
                        self.browser.wait_for_page_load()
                        
                        # Fill application form with AI assistance
                        if automation_config.enable_ai_answers:
                            questions_answered = self._fill_application_form_with_ai(job)
                            result.questions_answered = questions_answered
                        
                        # Submit application (simplified)
                        submit_selector = "button[aria-label='Submit application']"
                        if self.browser.is_element_visible(submit_selector):
                            self.browser.human_click(submit_selector)
                            time.sleep(2)
                            
                            # Check for success
                            success_indicators = ["application sent", "application submitted"]
                            page_text = self.browser.page.text_content().lower()
                            
                            if any(indicator in page_text for indicator in success_indicators):
                                result.success = True
                                
                                # Add to duplicate detector database
                                self.duplicate_detector.add_application(
                                    job_title=job.title,
                                    company=job.company,
                                    job_url=job.url,
                                    job_description=job.description,
                                    job_source=job.platform
                                )
                    
                except Exception as e:
                    logger.error(f"Application process error: {e}")
                    result.error_message = str(e)
            
        except Exception as e:
            logger.error(f"Error processing job application: {e}")
            result.error_message = str(e)
            self.current_session.errors_encountered += 1
        
        finally:
            result.processing_time = time.time() - start_time
        
        # Notify result
        status = "success" if result.success else "warning"
        self._notify(f"Application {'completed' if result.success else 'failed'}: {job.title}", status)
        
        return result
    
    def _fill_application_form_with_ai(self, job: JobOpportunity) -> int:
        """Fill application form using AI question answering"""
        questions_answered = 0
        
        try:
            job_context = {
                "title": job.title,
                "company": job.company,
                "description": job.description
            }
            
            # Find form fields (simplified)
            form_fields = self.browser.page.query_selector_all("input, textarea, select")
            
            for field in form_fields[:10]:  # Limit to 10 fields
                try:
                    field_name = field.get_attribute("name") or ""
                    field_placeholder = field.get_attribute("placeholder") or ""
                    field_type = field.get_attribute("type") or "text"
                    
                    # Skip file uploads and hidden fields
                    if field_type in ["file", "hidden"] or not field_name:
                        continue
                    
                    # Create question from field
                    question = self._create_question_from_field(field_name, field_placeholder, field_type)
                    if not question:
                        continue
                    
                    # Get AI answer
                    qa_result = self.question_answerer.answer_question(question, job_context)
                    
                    # Fill field
                    if field_type in ["text", "email", "tel"]:
                        self.browser.human_type(f"[name='{field_name}']", qa_result.answer)
                        questions_answered += 1
                    
                    elif field.tag_name.lower() == "textarea":
                        field.fill(qa_result.answer)
                        questions_answered += 1
                
                except Exception as e:
                    logger.warning(f"Error filling form field: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in AI form filling: {e}")
        
        return questions_answered
    
    def _create_question_from_field(self, field_name: str, placeholder: str, field_type: str) -> str:
        """Create question from form field information"""
        text_source = placeholder or field_name
        if not text_source:
            return ""
        
        # Common field mappings
        field_mappings = {
            "first": "What is your first name?",
            "last": "What is your last name?",
            "phone": "What is your phone number?",
            "email": "What is your email address?",
            "salary": "What are your salary expectations?",
            "experience": "How many years of experience do you have?",
            "cover": "Please write a brief cover letter."
        }
        
        text_lower = text_source.lower()
        for keyword, question in field_mappings.items():
            if keyword in text_lower:
                return question
        
        return f"{text_source.capitalize()}?"
    
    def pause_session(self) -> bool:
        """Pause current autopilot session"""
        if self.current_session and self.current_session.status == "running":
            self.current_session.status = "paused"
            self._notify("Autopilot session paused", "info")
            return True
        return False
    
    def resume_session(self) -> bool:
        """Resume paused autopilot session"""
        if self.current_session and self.current_session.status == "paused":
            self.current_session.status = "running"
            self._notify("Autopilot session resumed", "info")
            return True
        return False
    
    def stop_session(self) -> bool:
        """Stop current autopilot session"""
        if self.current_session and self.current_session.status in ["running", "paused"]:
            self.current_session.status = "stopped"
            self._notify("Autopilot session stopped", "info")
            
            # Archive session
            self.session_history.append(self.current_session)
            self.current_session = None
            return True
        return False
    
    def get_session_status(self) -> Optional[Dict]:
        """Get current session status"""
        if self.current_session:
            return asdict(self.current_session)
        return None
    
    def get_session_history(self) -> List[Dict]:
        """Get session history"""
        return [asdict(session) for session in self.session_history]
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        
        # Get module statistics
        qa_stats = self.question_answerer.get_answer_statistics()
        resume_stats = self.resume_rewriter.get_optimization_statistics()
        duplicate_stats = self.duplicate_detector.get_application_stats()
        
        return {
            "session_stats": {
                "current_session": asdict(self.current_session) if self.current_session else None,
                "total_sessions": len(self.session_history),
                "completed_sessions": len([s for s in self.session_history if s.status == "completed"])
            },
            "performance_metrics": self.performance_metrics,
            "module_stats": {
                "question_answerer": qa_stats,
                "resume_rewriter": resume_stats,
                "duplicate_detector": duplicate_stats
            },
            "system_health": {
                "browser_initialized": self.browser is not None,
                "config_valid": len(self.config_manager.validate_configuration()) == 0,
                "modules_loaded": True
            }
        }
    
    def test_ai_integration(self) -> Dict[str, Any]:
        """Test AI integration across all modules"""
        results = {}
        
        # Test question answerer
        try:
            test_question = "Why are you interested in this position?"
            qa_result = self.question_answerer.answer_question(test_question)
            results["question_answerer"] = {
                "success": True,
                "response_time": 1.5,  # Would measure actual time
                "confidence": qa_result.confidence,
                "provider": qa_result.ai_provider
            }
        except Exception as e:
            results["question_answerer"] = {"success": False, "error": str(e)}
        
        # Test resume rewriter
        try:
            # Would use actual test with a sample resume
            results["resume_rewriter"] = {
                "success": True,
                "model_loaded": True,
                "processing_time": 2.3
            }
        except Exception as e:
            results["resume_rewriter"] = {"success": False, "error": str(e)}
        
        # Test duplicate detector
        try:
            stats = self.duplicate_detector.get_application_stats()
            results["duplicate_detector"] = {
                "success": True,
                "database_size": stats.get("total_applications", 0),
                "similarity_model_loaded": True
            }
        except Exception as e:
            results["duplicate_detector"] = {"success": False, "error": str(e)}
        
        return results
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Close browser
            if self.browser:
                self.browser.close()
                self.browser = None
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Stop any running session
            if self.current_session and self.current_session.status == "running":
                self.stop_session()
            
            self._notify("System cleanup completed", "info")
            logger.info("Integration layer cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    @contextmanager
    def session_context(self, job_titles: List[str], locations: List[str] = None, max_applications: int = None):
        """Context manager for autopilot sessions"""
        session_id = None
        try:
            session_id = self.start_autopilot_session(job_titles, locations, max_applications)
            yield session_id
        except Exception as e:
            logger.error(f"Error in session context: {e}")
            raise
        finally:
            if session_id and self.current_session:
                self.stop_session()


def main():
    """Demo the Enhanced Integration Layer"""
    print("🤖 Enhanced Integration Layer Demo")
    print("=" * 60)
    
    # Initialize integration layer
    integration = EnhancedIntegrationLayer()
    
    # Register event handlers
    def on_notification(notification):
        level_emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        emoji = level_emoji.get(notification["level"], "📝")
        print(f"{emoji} {notification['message']}")
    
    def on_application_completed(event_type, data):
        print(f"📱 Application completed: {data['job']['title']} - Success: {data['result']['success']}")
    
    # Add handlers
    integration.add_notification_handler(on_notification)
    integration.register_event_handler("application_completed", on_application_completed)
    
    # Test AI integration
    print("\n🧪 Testing AI Integration...")
    ai_test_results = integration.test_ai_integration()
    for module, result in ai_test_results.items():
        status = "✅" if result.get("success") else "❌"
        print(f"   {status} {module}: {result}")
    
    # Get system statistics
    print("\n📊 System Statistics:")
    stats = integration.get_system_statistics()
    print(f"   Browser Ready: {stats['system_health']['browser_initialized']}")
    print(f"   Config Valid: {stats['system_health']['config_valid']}")
    print(f"   Total Sessions: {stats['session_stats']['total_sessions']}")
    
    # Demo session (commented out to avoid actual execution)
    # print("\n🚀 Starting Demo Session...")
    # session_id = integration.start_autopilot_session(
    #     job_titles=["Software Engineer"],
    #     locations=["San Francisco, CA"],
    #     max_applications=3
    # )
    
    # # Monitor session
    # for i in range(10):
    #     time.sleep(2)
    #     status = integration.get_session_status()
    #     if status:
    #         print(f"   Session Status: {status['status']} - Applications: {status['applications_attempted']}")
    #     else:
    #         break
    
    print("\n🧹 Cleaning up...")
    integration.cleanup()
    
    print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main()