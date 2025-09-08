#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Enhanced LinkedIn Automation System
Integrates all advanced features: AI question answering, dynamic resume rewriting,
smart duplicate detection, and undetected browser automation
"""

import os
import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
from datetime import datetime
import yaml

# Import our enhanced modules
from ai_question_answerer import AIQuestionAnswerer
from dynamic_resume_rewriter import DynamicResumeRewriter
from smart_duplicate_detector import SmartDuplicateDetector
from undetected_browser import UndetectedBrowser, BrowserConfig, HumanBehaviorConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedLinkedInAutopilot:
    def __init__(self, config_path: str = "config/enhanced_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize all enhanced modules
        self.question_answerer = AIQuestionAnswerer()
        self.resume_rewriter = DynamicResumeRewriter()
        self.duplicate_detector = SmartDuplicateDetector()
        
        # Initialize undetected browser
        browser_config = BrowserConfig(
            headless=self.config.get('browser', {}).get('headless', False),
            stealth_mode=True
        )
        behavior_config = HumanBehaviorConfig(
            typing_delay_range=(80, 180),
            click_delay_range=(200, 500),
            natural_pauses=True,
            random_scrolling=True
        )
        self.browser = UndetectedBrowser(browser_config, behavior_config)
        
        # Session statistics
        self.session_stats = {
            "applications_attempted": 0,
            "applications_completed": 0,
            "duplicates_avoided": 0,
            "questions_answered": 0,
            "resumes_optimized": 0,
            "errors_encountered": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # LinkedIn selectors (updated for current LinkedIn)
        self.selectors = {
            "login_email": "input[name='session_key']",
            "login_password": "input[name='session_password']",
            "login_button": "button[type='submit']",
            "jobs_link": "a[href*='jobs']",
            "search_box": "input[placeholder*='Search jobs']",
            "easy_apply_button": "button[aria-label*='Easy Apply']",
            "apply_button": "button[aria-label='Submit application']",
            "next_button": "button[aria-label='Continue to next step']",
            "job_title": "h1.t-24",
            "company_name": ".jobs-unified-top-card__company-name",
            "job_description": ".jobs-description-content__text",
            "form_fields": "input, select, textarea",
            "radio_buttons": "input[type='radio']",
            "checkboxes": "input[type='checkbox']",
            "file_upload": "input[type='file']",
            "submit_button": "button[type='submit']",
            "close_button": "button[aria-label='Dismiss']",
            "job_cards": ".job-card-container",
            "pagination_next": "button[aria-label='Next']"
        }
    
    def _load_config(self) -> Dict:
        """Load enhanced configuration"""
        default_config = {
            "linkedin": {
                "email": os.getenv("LINKEDIN_EMAIL", ""),
                "password": os.getenv("LINKEDIN_PASSWORD", "")
            },
            "browser": {
                "headless": os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true",
                "profile_name": "linkedin_autopilot"
            },
            "automation": {
                "max_applications_per_session": 20,
                "delay_between_applications": (30, 90),  # seconds
                "max_questions_per_form": 10,
                "enable_resume_optimization": True,
                "enable_duplicate_detection": True,
                "enable_ai_answers": True
            },
            "job_preferences": {
                "keywords": ["software engineer", "python developer", "full stack"],
                "locations": ["San Francisco", "New York", "Remote"],
                "experience_level": "mid-senior",
                "exclude_companies": [],
                "salary_minimum": 80000
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            else:
                # Save default config
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                logger.info(f"Created default config at: {self.config_path}")
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        
        return default_config
    
    def start_session(self) -> bool:
        """Start the enhanced LinkedIn automation session"""
        logger.info("🚀 Starting Enhanced LinkedIn Autopilot Session")
        logger.info("=" * 60)
        
        try:
            # Start undetected browser
            profile_name = self.config['browser']['profile_name']
            success = self.browser.start_browser(profile_name)
            if not success:
                logger.error("Failed to start browser")
                return False
            
            # Login to LinkedIn
            login_success = self._login_to_linkedin()
            if not login_success:
                logger.error("Failed to login to LinkedIn")
                return False
            
            logger.info("✅ Session started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            self.session_stats["errors_encountered"] += 1
            return False
    
    def _login_to_linkedin(self) -> bool:
        """Enhanced LinkedIn login with stealth"""
        try:
            logger.info("🔐 Logging into LinkedIn...")
            
            # Navigate to LinkedIn login
            self.browser.navigate_to("https://www.linkedin.com/login")
            
            # Check if already logged in
            if "feed" in self.browser.get_current_url():
                logger.info("✅ Already logged in to LinkedIn")
                return True
            
            # Enter credentials with human-like typing
            email = self.config['linkedin']['email']
            password = self.config['linkedin']['password']
            
            if not email or not password:
                logger.error("LinkedIn credentials not provided")
                return False
            
            # Type email
            self.browser.human_type(self.selectors['login_email'], email)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Type password
            self.browser.human_type(self.selectors['login_password'], password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login button
            self.browser.human_click(self.selectors['login_button'])
            
            # Wait for login and handle potential 2FA/security checks
            self.browser.wait_for_page_load(timeout=30000)
            
            # Check if login was successful
            current_url = self.browser.get_current_url()
            if "feed" in current_url or "mynetwork" in current_url:
                logger.info("✅ Successfully logged into LinkedIn")
                return True
            elif "challenge" in current_url:
                logger.warning("⚠️ LinkedIn security challenge detected")
                logger.info("Please complete the challenge manually and restart")
                time.sleep(30)  # Give user time to complete challenge
                return "feed" in self.browser.get_current_url()
            else:
                logger.error("❌ Login failed - unexpected redirect")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def search_and_apply_jobs(self, keywords: List[str], max_applications: int = None) -> Dict:
        """Enhanced job search and application process"""
        
        if max_applications is None:
            max_applications = self.config['automation']['max_applications_per_session']
        
        logger.info(f"🔍 Searching and applying for jobs: {', '.join(keywords)}")
        
        results = {
            "jobs_found": 0,
            "applications_completed": 0,
            "duplicates_skipped": 0,
            "errors": 0
        }
        
        try:
            # Navigate to LinkedIn Jobs
            self.browser.navigate_to("https://www.linkedin.com/jobs/")
            
            # Perform job search
            for keyword in keywords:
                if results["applications_completed"] >= max_applications:
                    break
                
                logger.info(f"🔎 Searching for: {keyword}")
                
                # Search for jobs
                job_results = self._search_jobs(keyword)
                results["jobs_found"] += len(job_results)
                
                # Process each job
                for job in job_results:
                    if results["applications_completed"] >= max_applications:
                        break
                    
                    try:
                        # Check for duplicates
                        if self.config['automation']['enable_duplicate_detection']:
                            is_duplicate, duplicate_match = self.duplicate_detector.check_if_duplicate(
                                job_title=job['title'],
                                company=job['company'],
                                job_url=job['url']
                            )
                            
                            if is_duplicate:
                                logger.info(f"⏭️ Skipping duplicate: {job['title']} at {job['company']}")
                                results["duplicates_skipped"] += 1
                                self.session_stats["duplicates_avoided"] += 1
                                continue
                        
                        # Apply to job
                        application_result = self._apply_to_job(job)
                        
                        if application_result["success"]:
                            results["applications_completed"] += 1
                            self.session_stats["applications_completed"] += 1
                            
                            # Add to duplicate detector database
                            self.duplicate_detector.add_application(
                                job_title=job['title'],
                                company=job['company'],
                                job_url=job['url'],
                                job_description=job.get('description', ''),
                                job_source="linkedin"
                            )
                        
                        # Random delay between applications
                        delay_range = self.config['automation']['delay_between_applications']
                        delay = random.uniform(*delay_range)
                        logger.info(f"⏳ Waiting {delay:.1f}s before next application...")
                        time.sleep(delay)
                        
                    except Exception as e:
                        logger.error(f"Error processing job {job['title']}: {e}")
                        results["errors"] += 1
                        self.session_stats["errors_encountered"] += 1
        
        except Exception as e:
            logger.error(f"Error in job search and apply: {e}")
            results["errors"] += 1
            self.session_stats["errors_encountered"] += 1
        
        return results
    
    def _search_jobs(self, keyword: str) -> List[Dict]:
        """Search for jobs on LinkedIn"""
        jobs = []
        
        try:
            # Enter search keyword
            search_box_selector = self.selectors['search_box']
            self.browser.human_type(search_box_selector, keyword, clear_first=True)
            self.browser.page.keyboard.press("Enter")
            
            self.browser.wait_for_page_load()
            
            # Filter for Easy Apply jobs
            easy_apply_filter = "button[aria-label*='Easy Apply filter']"
            if self.browser.is_element_visible(easy_apply_filter):
                self.browser.human_click(easy_apply_filter)
                self.browser.wait_for_page_load()
            
            # Collect job listings
            job_cards = self.browser.page.query_selector_all(self.selectors['job_cards'])
            
            for i, card in enumerate(job_cards[:20]):  # Limit to first 20 jobs
                try:
                    # Extract job information
                    job_title_elem = card.query_selector("h3 a")
                    company_elem = card.query_selector(".job-card-container__company-name")
                    link_elem = card.query_selector("h3 a")
                    
                    if job_title_elem and company_elem and link_elem:
                        job = {
                            "title": job_title_elem.text_content().strip(),
                            "company": company_elem.text_content().strip(),
                            "url": link_elem.get_attribute("href"),
                            "card_element": card
                        }
                        jobs.append(job)
                
                except Exception as e:
                    logger.warning(f"Error extracting job info from card {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
        
        logger.info(f"Found {len(jobs)} jobs for keyword: {keyword}")
        return jobs
    
    def _apply_to_job(self, job: Dict) -> Dict:
        """Apply to a specific job with all enhancements"""
        
        result = {
            "success": False,
            "job_title": job['title'],
            "company": job['company'],
            "questions_answered": 0,
            "resume_optimized": False,
            "error": None
        }
        
        try:
            logger.info(f"📝 Applying to: {job['title']} at {job['company']}")
            self.session_stats["applications_attempted"] += 1
            
            # Click on job card to open details
            job['card_element'].click()
            self.browser.wait_for_page_load()
            
            # Get job description for resume optimization
            job_description = ""
            try:
                job_desc_elem = self.browser.page.query_selector(self.selectors['job_description'])
                if job_desc_elem:
                    job_description = job_desc_elem.text_content().strip()
                    job['description'] = job_description
            except:
                pass
            
            # Optimize resume if enabled
            if (self.config['automation']['enable_resume_optimization'] and job_description):
                try:
                    logger.info("📄 Optimizing resume for this job...")
                    resume_version = self.resume_rewriter.create_optimized_resume(
                        job_title=job['title'],
                        company=job['company'],
                        job_description=job_description
                    )
                    result["resume_optimized"] = True
                    self.session_stats["resumes_optimized"] += 1
                    logger.info(f"✅ Resume optimized (Score: {resume_version.similarity_score:.3f})")
                except Exception as e:
                    logger.warning(f"Resume optimization failed: {e}")
            
            # Click Easy Apply button
            easy_apply_btn = self.browser.page.query_selector(self.selectors['easy_apply_button'])
            if not easy_apply_btn:
                result["error"] = "Easy Apply button not found"
                return result
            
            self.browser.human_click(self.selectors['easy_apply_button'])
            self.browser.wait_for_page_load()
            
            # Handle multi-step application form
            max_steps = 5
            current_step = 0
            
            while current_step < max_steps:
                current_step += 1
                logger.info(f"📋 Processing application step {current_step}")
                
                # Fill form fields
                questions_answered = self._fill_application_form(job)
                result["questions_answered"] += questions_answered
                self.session_stats["questions_answered"] += questions_answered
                
                # Look for Next button or Submit button
                next_btn = self.browser.page.query_selector(self.selectors['next_button'])
                submit_btn = self.browser.page.query_selector(self.selectors['apply_button'])
                
                if submit_btn:
                    # Final submission
                    logger.info("📤 Submitting application...")
                    self.browser.human_click(self.selectors['apply_button'])
                    time.sleep(3)  # Wait for submission
                    
                    # Check for success indicators
                    if self._check_application_success():
                        result["success"] = True
                        logger.info(f"✅ Application submitted successfully!")
                    else:
                        result["error"] = "Application submission unclear"
                    
                    break
                
                elif next_btn:
                    # Continue to next step
                    self.browser.human_click(self.selectors['next_button'])
                    self.browser.wait_for_page_load()
                
                else:
                    # No next step found
                    result["error"] = "Cannot proceed - no next/submit button"
                    break
            
            # Close any remaining modals
            self._close_application_modal()
            
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            result["error"] = str(e)
            self.session_stats["errors_encountered"] += 1
        
        return result
    
    def _fill_application_form(self, job: Dict) -> int:
        """Fill application form using AI question answering"""
        questions_answered = 0
        
        try:
            # Find all form fields
            form_fields = self.browser.page.query_selector_all(self.selectors['form_fields'])
            
            job_context = {
                "title": job['title'],
                "company": job['company'],
                "description": job.get('description', '')
            }
            
            for field in form_fields:
                try:
                    field_type = field.get_attribute("type")
                    field_name = field.get_attribute("name") or ""
                    field_id = field.get_attribute("id") or ""
                    field_placeholder = field.get_attribute("placeholder") or ""
                    field_label = ""
                    
                    # Try to find associated label
                    try:
                        if field_id:
                            label_elem = self.browser.page.query_selector(f"label[for='{field_id}']")
                            if label_elem:
                                field_label = label_elem.text_content().strip()
                    except:
                        pass
                    
                    # Create question from field information
                    question = self._create_question_from_field(
                        field_name, field_id, field_placeholder, field_label, field_type
                    )
                    
                    if not question:
                        continue
                    
                    # Skip if field is already filled
                    current_value = field.input_value() if hasattr(field, 'input_value') else ""
                    if current_value and current_value.strip():
                        continue
                    
                    # Get AI answer if enabled
                    if self.config['automation']['enable_ai_answers']:
                        try:
                            qa_result = self.question_answerer.answer_question(question, job_context)
                            answer = qa_result.answer
                        except Exception as e:
                            logger.warning(f"AI answering failed for '{question}': {e}")
                            answer = self._get_fallback_answer(field_name, field_type)
                    else:
                        answer = self._get_fallback_answer(field_name, field_type)
                    
                    # Fill the field based on type
                    if field_type == "file":
                        # Handle file upload (resume)
                        resume_path = "config/resume.pdf"
                        if os.path.exists(resume_path):
                            field.set_input_files(resume_path)
                            logger.info("📄 Resume uploaded")
                    
                    elif field_type in ["text", "email", "tel"]:
                        # Text input
                        self.browser.human_type(f"#{field_id}" if field_id else f"[name='{field_name}']", answer)
                        questions_answered += 1
                    
                    elif field_type == "textarea":
                        # Textarea
                        field.fill(answer)
                        questions_answered += 1
                    
                    elif field_type == "select":
                        # Select dropdown
                        options = field.query_selector_all("option")
                        for option in options:
                            if answer.lower() in option.text_content().lower():
                                field.select_option(option.get_attribute("value"))
                                questions_answered += 1
                                break
                    
                    # Random delay between fields
                    time.sleep(random.uniform(0.3, 1.0))
                
                except Exception as e:
                    logger.warning(f"Error filling form field: {e}")
                    continue
            
            # Handle radio buttons and checkboxes separately
            questions_answered += self._handle_radio_and_checkbox_fields(job_context)
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
        
        return questions_answered
    
    def _create_question_from_field(self, name: str, field_id: str, placeholder: str, label: str, field_type: str) -> str:
        """Create a natural question from form field information"""
        
        # Priority: label > placeholder > name > id
        text_source = label or placeholder or name or field_id
        
        if not text_source:
            return ""
        
        # Clean up the text
        text_source = text_source.lower().replace("*", "").replace(":", "").strip()
        
        # Common field mappings
        field_mappings = {
            "first name": "What is your first name?",
            "last name": "What is your last name?",
            "phone": "What is your phone number?",
            "email": "What is your email address?",
            "linkedin": "What is your LinkedIn profile URL?",
            "website": "What is your personal website URL?",
            "cover letter": "Please write a brief cover letter for this position.",
            "why interested": "Why are you interested in this position?",
            "salary": "What are your salary expectations?",
            "availability": "When are you available to start?",
            "experience": "How many years of relevant experience do you have?",
            "notice period": "What is your notice period?",
            "relocate": "Are you willing to relocate?",
            "remote": "Are you interested in remote work?",
            "travel": "Are you willing to travel for work?",
            "visa": "Do you require visa sponsorship?"
        }
        
        # Find matching question
        for keyword, question in field_mappings.items():
            if keyword in text_source:
                return question
        
        # Fallback: create question from field text
        if "?" not in text_source:
            return f"{text_source.capitalize()}?"
        
        return text_source.capitalize()
    
    def _get_fallback_answer(self, field_name: str, field_type: str) -> str:
        """Get fallback answer when AI fails"""
        
        field_name = field_name.lower() if field_name else ""
        
        fallback_answers = {
            "first": "John",
            "last": "Doe",
            "phone": "+1-555-0123",
            "email": "johndoe@email.com",
            "linkedin": "https://linkedin.com/in/johndoe",
            "salary": "Competitive",
            "experience": "5",
            "notice": "2 weeks",
            "available": "Immediately"
        }
        
        for keyword, answer in fallback_answers.items():
            if keyword in field_name:
                return answer
        
        # Default responses by type
        if field_type in ["text", "email"]:
            return "N/A"
        elif field_type == "tel":
            return "+1-555-0123"
        elif field_type == "number":
            return "5"
        
        return "Yes"
    
    def _handle_radio_and_checkbox_fields(self, job_context: Dict) -> int:
        """Handle radio buttons and checkboxes with AI"""
        questions_answered = 0
        
        try:
            # Handle radio buttons
            radio_groups = {}
            radio_buttons = self.browser.page.query_selector_all(self.selectors['radio_buttons'])
            
            for radio in radio_buttons:
                name = radio.get_attribute("name")
                if name:
                    if name not in radio_groups:
                        radio_groups[name] = []
                    radio_groups[name].append(radio)
            
            # Answer each radio group
            for group_name, radios in radio_groups.items():
                if len(radios) > 1:  # Only if it's actually a group
                    try:
                        # Find question text for this group
                        question = self._find_question_for_radio_group(radios[0])
                        
                        if question and self.config['automation']['enable_ai_answers']:
                            qa_result = self.question_answerer.answer_question(question, job_context)
                            answer = qa_result.answer.lower()
                            
                            # Select best matching radio button
                            best_match = None
                            best_score = 0
                            
                            for radio in radios:
                                radio_label = self._get_radio_label(radio)
                                if radio_label:
                                    # Simple matching
                                    if any(word in answer for word in radio_label.lower().split()):
                                        score = len([w for w in radio_label.lower().split() if w in answer])
                                        if score > best_score:
                                            best_score = score
                                            best_match = radio
                            
                            if best_match:
                                best_match.click()
                                questions_answered += 1
                            else:
                                # Default to first option
                                radios[0].click()
                                questions_answered += 1
                    
                    except Exception as e:
                        logger.warning(f"Error handling radio group {group_name}: {e}")
            
            # Handle checkboxes (usually select all relevant ones)
            checkboxes = self.browser.page.query_selector_all(self.selectors['checkboxes'])
            for checkbox in checkboxes:
                try:
                    # Skip if already checked
                    if checkbox.is_checked():
                        continue
                    
                    # Get checkbox question/label
                    question = self._find_question_for_checkbox(checkbox)
                    if question and self.config['automation']['enable_ai_answers']:
                        qa_result = self.question_answerer.answer_question(question, job_context)
                        if "yes" in qa_result.answer.lower() or "agree" in qa_result.answer.lower():
                            checkbox.click()
                            questions_answered += 1
                
                except Exception as e:
                    logger.warning(f"Error handling checkbox: {e}")
        
        except Exception as e:
            logger.error(f"Error handling radio/checkbox fields: {e}")
        
        return questions_answered
    
    def _find_question_for_radio_group(self, radio_element) -> str:
        """Find question text for radio button group"""
        try:
            # Look for fieldset legend
            fieldset = radio_element.locator("xpath=ancestor::fieldset[1]")
            if fieldset.count() > 0:
                legend = fieldset.locator("legend")
                if legend.count() > 0:
                    return legend.text_content().strip()
            
            # Look for label
            name = radio_element.get_attribute("name")
            if name:
                label = self.browser.page.query_selector(f"label[for*='{name}']")
                if label:
                    return label.text_content().strip()
            
            return "Please select an option"
        
        except:
            return "Please select an option"
    
    def _get_radio_label(self, radio_element) -> str:
        """Get label text for radio button"""
        try:
            radio_id = radio_element.get_attribute("id")
            if radio_id:
                label = self.browser.page.query_selector(f"label[for='{radio_id}']")
                if label:
                    return label.text_content().strip()
            
            # Look for adjacent text
            parent = radio_element.locator("xpath=..")
            if parent.count() > 0:
                return parent.text_content().strip()
            
            return ""
        
        except:
            return ""
    
    def _find_question_for_checkbox(self, checkbox_element) -> str:
        """Find question text for checkbox"""
        try:
            checkbox_id = checkbox_element.get_attribute("id")
            if checkbox_id:
                label = self.browser.page.query_selector(f"label[for='{checkbox_id}']")
                if label:
                    return f"Do you agree with: {label.text_content().strip()}?"
            
            return "Do you agree with this statement?"
        
        except:
            return "Do you agree with this statement?"
    
    def _check_application_success(self) -> bool:
        """Check if application was submitted successfully"""
        try:
            # Look for success indicators
            success_indicators = [
                "application sent",
                "application submitted",
                "thank you",
                "we'll be in touch",
                "successfully applied"
            ]
            
            page_text = self.browser.page.text_content().lower()
            
            for indicator in success_indicators:
                if indicator in page_text:
                    return True
            
            # Check URL for success patterns
            current_url = self.browser.get_current_url().lower()
            if "success" in current_url or "confirmation" in current_url:
                return True
            
            return False
        
        except:
            return False
    
    def _close_application_modal(self):
        """Close application modal/popup"""
        try:
            close_selectors = [
                self.selectors['close_button'],
                "button[aria-label*='close']",
                ".artdeco-modal__dismiss",
                "[data-test-modal-close-btn]"
            ]
            
            for selector in close_selectors:
                if self.browser.is_element_visible(selector):
                    self.browser.human_click(selector)
                    time.sleep(1)
                    break
        
        except Exception as e:
            logger.warning(f"Error closing modal: {e}")
    
    def get_session_summary(self) -> Dict:
        """Get comprehensive session summary"""
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.session_stats["start_time"])
        duration = (end_time - start_time).total_seconds() / 60  # minutes
        
        summary = {
            **self.session_stats,
            "end_time": end_time.isoformat(),
            "duration_minutes": round(duration, 2),
            "success_rate": 0,
            "duplicate_detection_stats": self.duplicate_detector.get_application_stats(),
            "question_answerer_stats": self.question_answerer.get_answer_statistics(),
            "resume_rewriter_stats": self.resume_rewriter.get_optimization_statistics()
        }
        
        if self.session_stats["applications_attempted"] > 0:
            summary["success_rate"] = round(
                (self.session_stats["applications_completed"] / self.session_stats["applications_attempted"]) * 100, 2
            )
        
        return summary
    
    def end_session(self):
        """End the LinkedIn automation session"""
        try:
            # Save browser profile
            self.browser.close(save_profile_name=self.config['browser']['profile_name'])
            
            # Print session summary
            summary = self.get_session_summary()
            
            logger.info("\\n🎯 Enhanced LinkedIn Autopilot Session Summary")
            logger.info("=" * 60)
            logger.info(f"📊 Duration: {summary['duration_minutes']} minutes")
            logger.info(f"📝 Applications Attempted: {summary['applications_attempted']}")
            logger.info(f"✅ Applications Completed: {summary['applications_completed']}")
            logger.info(f"🚫 Duplicates Avoided: {summary['duplicates_avoided']}")
            logger.info(f"❓ Questions Answered: {summary['questions_answered']}")
            logger.info(f"📄 Resumes Optimized: {summary['resumes_optimized']}")
            logger.info(f"⚠️ Errors Encountered: {summary['errors_encountered']}")
            logger.info(f"📈 Success Rate: {summary['success_rate']}%")
            
            # Save session summary
            summary_path = Path("data/session_summaries")
            summary_path.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with open(summary_path / f"session_{timestamp}.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"\\n💾 Session summary saved")
            logger.info("🎉 Enhanced LinkedIn Autopilot session completed!")
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")


def main():
    """Main function to run Enhanced LinkedIn Autopilot"""
    print("🤖 Enhanced LinkedIn Autopilot")
    print("=" * 50)
    print("Features: AI Answers • Dynamic Resumes • Duplicate Detection • Stealth Browser")
    print()
    
    # Initialize autopilot
    autopilot = EnhancedLinkedInAutopilot()
    
    try:
        # Start session
        success = autopilot.start_session()
        if not success:
            print("❌ Failed to start session")
            return
        
        # Configure job search
        keywords = autopilot.config['job_preferences']['keywords']
        max_applications = autopilot.config['automation']['max_applications_per_session']
        
        print(f"🎯 Searching for: {', '.join(keywords)}")
        print(f"📊 Max applications: {max_applications}")
        print()
        
        # Start job search and application process
        results = autopilot.search_and_apply_jobs(keywords, max_applications)
        
        print("\\n📋 Search Results:")
        print(f"   Jobs Found: {results['jobs_found']}")
        print(f"   Applications Completed: {results['applications_completed']}")
        print(f"   Duplicates Skipped: {results['duplicates_skipped']}")
        print(f"   Errors: {results['errors']}")
        
    except KeyboardInterrupt:
        print("\\n🛑 Session interrupted by user")
    except Exception as e:
        print(f"\\n❌ Error during session: {e}")
        logger.error(f"Main error: {e}")
    
    finally:
        # Always end session properly
        autopilot.end_session()


if __name__ == "__main__":
    main()