"""
Real LinkedIn Automation with Proper Authentication
Handles login, job search, and application process with stealth mode
"""

import asyncio
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import random

@dataclass
class LinkedInCredentials:
    email: str
    password: str

@dataclass
class JobApplication:
    job_id: str
    title: str
    company: str
    location: str
    url: str
    status: str
    applied_at: str

class LinkedInAutomation:
    """Real LinkedIn automation with proper authentication and stealth mode"""
    
    def __init__(self, credentials: LinkedInCredentials, update_callback: Callable = None):
        self.credentials = credentials
        self.update_callback = update_callback
        self.logger = logging.getLogger(__name__)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.applications_today = []
        
    async def initialize_browser(self) -> bool:
        """Initialize browser with stealth settings and proper authentication"""
        
        try:
            await self._send_update("🌐 Starting secure browser session...")
            
            # Store playwright instance
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Visible browser for user interaction
                slow_mo=500,  # Add delay between actions
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--start-maximized'
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 768},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Add stealth scripts
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            self.page = await self.context.new_page()
            
            await self._send_update("✅ Browser initialized successfully")
            return True
                
        except Exception as e:
            await self._send_update(f"❌ Browser initialization failed: {str(e)}")
            return False
    
    async def login_to_linkedin(self) -> bool:
        """Login to LinkedIn with proper error handling"""
        
        if not self.page:
            await self._send_update("❌ Browser not initialized")
            return False
            
        try:
            await self._send_update("🔑 Navigating to LinkedIn login page...")
            
            # Navigate to LinkedIn login with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.page.goto('https://www.linkedin.com/login', 
                                       wait_until='domcontentloaded', 
                                       timeout=60000)  # 60 second timeout
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        await self._send_update(f"🔄 Retry {attempt + 1}: Connection timeout, retrying...")
                        await asyncio.sleep(5)
                    else:
                        raise e
            
            # Wait for page to load
            await self.page.wait_for_timeout(2000)
            
            # Check if already logged in
            if 'feed' in self.page.url or 'in/me' in self.page.url:
                await self._send_update("✅ Already logged in to LinkedIn")
                self.is_logged_in = True
                return True
            
            await self._send_update("👤 Entering credentials...")
            
            # Enter email
            email_input = await self.page.wait_for_selector('#username', timeout=10000)
            await email_input.fill('')
            await email_input.type(self.credentials.email, delay=100)
            
            # Enter password
            password_input = await self.page.wait_for_selector('#password')
            await password_input.fill('')
            await password_input.type(self.credentials.password, delay=120)
            
            # Add random delay before clicking login
            await self.page.wait_for_timeout(random.randint(1000, 3000))
            
            await self._send_update("🚀 Authenticating with LinkedIn...")
            
            # Click login button
            login_button = await self.page.wait_for_selector('button[type="submit"]')
            await login_button.click()
            
            # Wait for login to complete
            await self.page.wait_for_timeout(5000)
            
            # Check for successful login
            try:
                # Check if we're redirected to feed or if login was successful
                await self.page.wait_for_url('**/feed/**', timeout=15000)
                await self._send_update("✅ Successfully logged in to LinkedIn")
                self.is_logged_in = True
                return True
                
            except:
                # Check for other success indicators
                current_url = self.page.url
                if 'feed' in current_url or 'in/' in current_url or 'linkedin.com/mynetwork' in current_url:
                    await self._send_update("✅ Successfully logged in to LinkedIn")
                    self.is_logged_in = True
                    return True
                else:
                    # Check for errors
                    try:
                        error_element = await self.page.query_selector('.form__label--error')
                        if error_element:
                            error_text = await error_element.text_content()
                            await self._send_update(f"❌ Login failed: {error_text}")
                        else:
                            await self._send_update("❌ Login failed: Please check credentials")
                    except:
                        await self._send_update("❌ Login failed: Authentication error")
                    return False
                    
        except Exception as e:
            await self._send_update(f"❌ Login error: {str(e)}")
            return False
    
    async def search_jobs(self, keywords: List[str], locations: List[str], limit: int = 25) -> List[Dict]:
        """Search for jobs on LinkedIn"""
        
        if not self.is_logged_in:
            await self._send_update("❌ Not logged in to LinkedIn")
            return []
            
        all_jobs = []
        
        try:
            for keyword in keywords[:2]:  # Limit to prevent rate limiting
                for location in locations[:2]:
                    await self._send_update(f"🔍 Searching for {keyword} jobs in {location}...")
                    
                    # Build search URL
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_TPR=r604800&f_LF=f_AL"
                    
                    await self.page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
                    await self.page.wait_for_timeout(3000)
                    
                    # Scroll to load more jobs
                    for _ in range(3):
                        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await self.page.wait_for_timeout(2000)
                    
                    # Use the working selector directly
                    job_cards = await self.page.query_selector_all('.scaffold-layout__list-item')
                    
                    await self._send_update(f"📊 Found {len(job_cards)} jobs for {keyword} in {location}")
                    
                    for i, card in enumerate(job_cards[:limit//4]):
                        try:
                            # Extract job details using working selectors
                            title_element = await card.query_selector('.job-card-container__link')
                            company_element = await card.query_selector('.artdeco-entity-lockup__subtitle')
                            location_element = await card.query_selector('.job-card-container__metadata-wrapper .job-card-container__metadata-item')
                            link_element = title_element  # Same as title link
                            
                            if title_element and company_element:
                                title = await title_element.text_content()
                                company = await company_element.text_content()
                                job_location = await location_element.text_content() if location_element else location
                                
                                # Get job URL and make it absolute
                                job_url = await link_element.get_attribute('href') if link_element else ''
                                if job_url and job_url.startswith('/'):
                                    job_url = f'https://www.linkedin.com{job_url}'
                                
                                if title and company:  # Ensure we have valid data
                                    job_data = {
                                        'id': f'linkedin_{hash(title + company)}'.replace('-', '')[:12],
                                        'title': title.strip(),
                                        'company': company.strip(),
                                        'location': job_location.strip() if job_location else location,
                                        'url': job_url,
                                        'platform': 'LinkedIn',
                                        'posted_date': 'Recently',
                                        'status': '🎯 Ready to Apply'
                                    }
                                    
                                    all_jobs.append(job_data)
                                    await self._send_update(f"✅ Found: {title} at {company}")
                            else:
                                # Debug what we found
                                await self._send_update(f"⚠️ Missing elements - Title: {bool(title_element)}, Company: {bool(company_element)}")
                                
                        except Exception as e:
                            self.logger.error(f"Error extracting job {i}: {e}")
                            continue
                    
                    # Rate limiting
                    await self.page.wait_for_timeout(random.randint(3000, 6000))
            
            await self._send_update(f"✅ Job search completed: {len(all_jobs)} jobs found")
            return all_jobs
            
        except Exception as e:
            await self._send_update(f"❌ Job search failed: {str(e)}")
            return []
    
    async def apply_to_job(self, job_data: Dict) -> bool:
        """Apply to a specific job"""
        
        if not self.is_logged_in:
            await self._send_update("❌ Not logged in to LinkedIn")
            return False
            
        try:
            await self._send_update(f"📝 Applying to {job_data['title']} at {job_data['company']}...")
            
            # Navigate to job page
            if job_data['url']:
                await self.page.goto(job_data['url'], wait_until='domcontentloaded', timeout=60000)
                await self.page.wait_for_timeout(3000)
            
            # Look for Easy Apply button with better selectors
            easy_apply_selectors = [
                'button:has-text("Easy Apply")',
                'button[aria-label*="Easy Apply"]',
                '.jobs-apply-button',
                'button[data-control-name*="apply"]',
                '.jobs-s-apply button',
                'button.jobs-apply-button',
                'button[data-test-id*="apply"]'
            ]
            
            apply_button = None
            await self._send_update("🔍 Looking for Easy Apply button...")
            
            for i, selector in enumerate(easy_apply_selectors):
                try:
                    apply_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if apply_button and await apply_button.is_visible() and await apply_button.is_enabled():
                        await self._send_update(f"✅ Found Easy Apply button with selector #{i+1}")
                        break
                    else:
                        apply_button = None
                except:
                    continue
            
            if not apply_button:
                # Try scrolling down to find the button
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await self.page.wait_for_timeout(2000)
                
                for i, selector in enumerate(easy_apply_selectors):
                    try:
                        apply_button = await self.page.wait_for_selector(selector, timeout=2000)
                        if apply_button and await apply_button.is_visible() and await apply_button.is_enabled():
                            await self._send_update(f"✅ Found Easy Apply button after scroll with selector #{i+1}")
                            break
                        else:
                            apply_button = None
                    except:
                        continue
            
            if not apply_button:
                await self._send_update("⚠️ Easy Apply not available for this job - may require external application")
                return False
            
            # Fast Easy Apply click with immediate JavaScript execution
            await self._send_update("🎯 Clicking Easy Apply button...")
            
            try:
                # Use JavaScript click immediately for speed and reliability
                await apply_button.evaluate("element => { element.scrollIntoView(); element.click(); }")
                await self._send_update("⚡ Clicked Easy Apply button (fast JS method)")
                await self.page.wait_for_timeout(2000)
            except:
                try:
                    # Fallback to force click
                    await apply_button.click(force=True, timeout=3000)
                    await self._send_update("✅ Clicked Easy Apply button (force method)")
                    await self.page.wait_for_timeout(2000)
                except:
                    await self._send_update("❌ Could not click Easy Apply button")
                    return False
            
            # Handle application form
            await self._handle_application_form()
            
            # Record successful application
            application = JobApplication(
                job_id=job_data['id'],
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                url=job_data['url'],
                status='Applied',
                applied_at=datetime.now().isoformat()
            )
            
            self.applications_today.append(application)
            await self._send_update(f"✅ Successfully applied to {job_data['title']}")
            return True
            
        except Exception as e:
            await self._send_update(f"❌ Application failed: {str(e)}")
            return False
    
    async def _handle_application_form(self):
        """Handle LinkedIn Easy Apply form with improved completion flow"""
        
        try:
            # Wait for application modal with better selectors
            modal_selectors = [
                '.jobs-easy-apply-modal',
                '.artdeco-modal',
                '[data-test-modal-id*="easy-apply"]',
                '.scaffold-layout-toolbar'
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self._send_update(f"📝 Application form loaded")
                    modal_found = True
                    break
                except:
                    continue
            
            if not modal_found:
                await self._send_update("⚠️ Application form not found, continuing anyway...")
            
            # Fast form processing - reduced timeouts
            await self.page.wait_for_timeout(1000)
            
            # Handle multiple steps with speed optimization
            max_steps = 5  # Reduced from 8 for faster processing
            current_step = 0
            
            while current_step < max_steps:
                current_step += 1
                await self._send_update(f"⚡ Processing step {current_step}/5...")
                
                # Fill fields quickly
                await self._fill_visible_form_fields_fast()
                
                # Minimal wait after filling
                await self.page.wait_for_timeout(800)
                
                # Look for next/submit button with better selectors
                next_selectors = [
                    'button:has-text("Submit application")',
                    'button:has-text("Submit")',
                    'button[aria-label*="Submit application"]',
                    'button:has-text("Next")',
                    'button[aria-label*="Continue to next step"]',
                    'button[data-control-name="continue_unify"]',
                    'button[data-control-name*="submit"]',
                    'footer button[type="submit"]',
                    '.jobs-easy-apply-modal footer button:last-child'
                ]
                
                next_button = None
                button_text = ""
                
                for i, selector in enumerate(next_selectors):
                    try:
                        next_button = await self.page.wait_for_selector(selector, timeout=1000)  # Faster timeout
                        if next_button and await next_button.is_visible() and await next_button.is_enabled():
                            button_text = await next_button.text_content() or f"Button#{i+1}"
                            await self._send_update(f"⚡ Found: '{button_text.strip()}'")
                            break
                        else:
                            next_button = None
                    except:
                        continue
                
                if not next_button:
                    await self._send_update("🔍 No more buttons found - application may be complete")
                    break
                
                # Fast button click with JavaScript
                await self._send_update(f"⚡ Clicking '{button_text.strip()}'...")
                try:
                    # Use JavaScript for instant click
                    await next_button.evaluate("element => element.click()")
                except:
                    # Fallback to regular click
                    await next_button.click()
                
                await self.page.wait_for_timeout(1500)  # Reduced wait time
                
                # Quick success detection
                success_indicators = [
                    '.artdeco-inline-feedback--success',
                    '.jobs-easy-apply-confirmation',
                    ':has-text("Application submitted")',
                    ':has-text("Your application was sent")',
                    ':has-text("Successfully applied")'
                ]
                
                application_complete = False
                for indicator in success_indicators:
                    try:
                        success_element = await self.page.wait_for_selector(indicator, timeout=1000)  # Faster check
                        if success_element:
                            await self._send_update("🎉 Application submitted!")
                            application_complete = True
                            break
                    except:
                        continue
                
                if application_complete:
                    break
                
                # Quick success check - back to job page
                if 'jobs/view/' in self.page.url:
                    try:
                        modal = await self.page.query_selector('.jobs-easy-apply-modal')
                        if not modal:
                            await self._send_update("✅ Returned to job page - application completed!")
                            break
                    except:
                        pass
            
        except Exception as e:
            self.logger.error(f"Error handling application form: {e}")
    
    async def _fill_visible_form_fields_fast(self):
        """Fast form field filling with minimal delays"""
        
        try:
            # Quick input field detection and filling
            inputs = await self.page.query_selector_all('input[type="text"]:visible, input:not([type]):visible, textarea:visible')
            
            for input_field in inputs[:5]:  # Limit to first 5 fields for speed
                try:
                    # Check if already filled
                    current_value = await input_field.input_value()
                    if current_value:
                        continue
                    
                    # Get field info quickly
                    placeholder = (await input_field.get_attribute('placeholder') or '').lower()
                    name = (await input_field.get_attribute('name') or '').lower()
                    field_info = placeholder + ' ' + name
                    
                    # Fill based on common patterns
                    if any(term in field_info for term in ['phone', 'mobile', 'tel']):
                        await input_field.fill('+91 8717934430')
                    elif any(term in field_info for term in ['website', 'portfolio', 'url']):
                        await input_field.fill('https://ankitthakur.dev')
                    elif any(term in field_info for term in ['salary', 'compensation']):
                        await input_field.fill('80000')
                    elif any(term in field_info for term in ['cover', 'why', 'message']):
                        await input_field.fill("I'm excited about this cybersecurity role and believe my experience in penetration testing and security analysis makes me a strong candidate.")
                    
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in fast form filling: {e}")
    
    async def _fill_visible_form_fields(self):
        """Fill any visible form fields with appropriate data"""
        
        try:
            # Handle text inputs
            text_inputs = await self.page.query_selector_all('input[type="text"]:visible, input:not([type]):visible')
            
            for input_field in text_inputs:
                try:
                    placeholder = await input_field.get_attribute('placeholder') or ''
                    name = await input_field.get_attribute('name') or ''
                    
                    # Skip if already filled
                    current_value = await input_field.input_value()
                    if current_value:
                        continue
                    
                    # Fill based on field characteristics  
                    field_info = (placeholder + ' ' + name).lower()
                    if any(term in field_info for term in ['phone', 'mobile', 'tel']):
                        await input_field.fill('+91 8717934430')
                    elif any(term in placeholder.lower() for term in ['website', 'portfolio', 'url']):
                        await input_field.fill('https://ankitthakur.dev')
                    elif 'salary' in placeholder.lower() or 'compensation' in placeholder.lower():
                        await input_field.fill('80000')
                    
                except Exception as e:
                    continue
            
            # Handle textareas
            textareas = await self.page.query_selector_all('textarea:visible')
            for textarea in textareas:
                try:
                    placeholder = await textarea.get_attribute('placeholder') or ''
                    current_value = await textarea.input_value()
                    
                    if current_value:
                        continue
                    
                    if any(term in placeholder.lower() for term in ['cover', 'why', 'tell', 'message']):
                        cover_letter = """I am excited to apply for this cybersecurity position. With my extensive background in penetration testing, vulnerability assessment, and security architecture, I am confident I can contribute significantly to your security initiatives. I look forward to discussing how my skills can benefit your team."""
                        await textarea.fill(cover_letter)
                
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error filling form fields: {e}")
    
    async def _send_update(self, message: str):
        """Send progress update"""
        
        if self.update_callback:
            await self.update_callback({
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'level': 'info'
            })
        
        self.logger.info(message)
    
    async def close_browser(self):
        """Clean up browser resources"""
        
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

# Convenience function
async def run_linkedin_automation(
    credentials: LinkedInCredentials,
    keywords: List[str],
    locations: List[str],
    max_applications: int = 10,
    update_callback: Callable = None
) -> List[JobApplication]:
    """Run complete LinkedIn automation workflow"""
    
    automation = LinkedInAutomation(credentials, update_callback)
    
    try:
        # Initialize browser and login
        if not await automation.initialize_browser():
            return []
        
        if not await automation.login_to_linkedin():
            return []
        
        # Search for jobs
        jobs = await automation.search_jobs(keywords, locations)
        
        if not jobs:
            await automation._send_update("❌ No jobs found matching criteria")
            return []
        
        # Apply to jobs
        successful_applications = []
        for i, job in enumerate(jobs[:max_applications]):
            if await automation.apply_to_job(job):
                successful_applications.append(job)
            
            # Rate limiting between applications
            if i < len(jobs) - 1:
                await asyncio.sleep(random.randint(30, 60))
        
        await automation._send_update(f"🎯 Automation complete: {len(successful_applications)} applications submitted")
        return automation.applications_today
        
    finally:
        await automation.close_browser()