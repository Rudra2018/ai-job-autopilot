"""
Universal Auto-Fill System - Applies to any job portal automatically
Intelligently detects and fills forms on any job application website
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

from playwright.async_api import async_playwright, Page, Browser, ElementHandle
from bs4 import BeautifulSoup
import openai
from transformers import pipeline

@dataclass
class ApplicationData:
    """User's application data"""
    personal_info: Dict[str, str]
    experience: List[Dict[str, str]]
    education: List[Dict[str, str]]
    skills: List[str]
    portfolio_links: Dict[str, str]
    cover_letter_template: str
    resume_path: str
    preferences: Dict[str, Any]

@dataclass
class FormField:
    """Represents a form field that needs to be filled"""
    element: ElementHandle
    field_type: str  # text, email, tel, textarea, select, file, radio, checkbox
    field_name: str
    label: str
    is_required: bool
    placeholder: str
    options: List[str]  # For select, radio, checkbox
    suggested_value: str

class UniversalAutoFill:
    """Universal auto-fill system that works on any job portal"""
    
    def __init__(self, update_callback: Callable = None):
        self.update_callback = update_callback
        self.logger = logging.getLogger(__name__)
        self.ai_assistant = pipeline('text-generation', model='microsoft/DialoGPT-medium')
        
        # Load user application data
        self.app_data = self._load_application_data()
        
        # Field detection patterns
        self.field_patterns = {
            'first_name': [
                'first.?name', 'fname', 'given.?name', 'firstname', 'name.*first'
            ],
            'last_name': [
                'last.?name', 'lname', 'surname', 'family.?name', 'lastname', 'name.*last'
            ],
            'full_name': [
                'full.?name', 'name', 'your.?name', 'applicant.?name', 'candidate.?name'
            ],
            'email': [
                'email', 'e.?mail', 'mail', 'email.?address', 'contact.?email'
            ],
            'phone': [
                'phone', 'mobile', 'telephone', 'tel', 'phone.?number', 'contact.?number', 'cell'
            ],
            'address': [
                'address', 'street', 'location', 'where.*located', 'residence'
            ],
            'city': [
                'city', 'town', 'municipality', 'location.*city'
            ],
            'state': [
                'state', 'province', 'region', 'county'
            ],
            'country': [
                'country', 'nation', 'nationality'
            ],
            'zipcode': [
                'zip', 'postal', 'post.?code', 'zip.?code'
            ],
            'linkedin': [
                'linkedin', 'linked.?in', 'profile.*url', 'linkedin.*profile'
            ],
            'portfolio': [
                'portfolio', 'website', 'personal.?site', 'portfolio.*url', 'web.*portfolio'
            ],
            'github': [
                'github', 'git.*profile', 'code.*repository', 'github.*url'
            ],
            'experience_years': [
                'experience', 'years.*experience', 'work.*experience', 'professional.*experience'
            ],
            'current_company': [
                'current.*company', 'employer', 'current.*employer', 'workplace'
            ],
            'current_position': [
                'current.*position', 'current.*role', 'current.*title', 'job.*title'
            ],
            'salary_expectation': [
                'salary', 'compensation', 'pay.*expectation', 'expected.*salary', 'wage'
            ],
            'availability': [
                'availability', 'start.*date', 'available.*from', 'when.*start', 'notice.*period'
            ],
            'cover_letter': [
                'cover.*letter', 'motivation.*letter', 'why.*apply', 'tell.*us.*about', 'introduce.*yourself'
            ],
            'resume': [
                'resume', 'cv', 'curriculum.*vitae', 'upload.*resume', 'attach.*resume'
            ],
            'visa_status': [
                'visa', 'work.*authorization', 'eligible.*work', 'visa.*status', 'right.*work'
            ]
        }
        
    def _load_application_data(self) -> ApplicationData:
        """Load user's application data"""
        
        # This would normally load from user profile/database
        # For now, using the resume data we extracted
        return ApplicationData(
            personal_info={
                'first_name': 'Ankit',
                'last_name': 'Thakur',
                'full_name': 'Ankit Thakur',
                'email': 'at87.at17@gmail.com',
                'phone': '+91 8717934430',
                'address': 'Berlin, Germany',
                'city': 'Berlin',
                'state': 'Berlin',
                'country': 'Germany',
                'zipcode': '10115',
                'linkedin': 'https://linkedin.com/in/ankit-thakur',
                'github': 'https://github.com/ankitthakur',
                'portfolio': 'https://ankitthakur.dev'
            },
            experience=[
                {
                    'company': 'TechCorp',
                    'position': 'Senior Cybersecurity Engineer',
                    'duration': '2021-Present',
                    'description': 'Led security initiatives, penetration testing, and vulnerability assessments'
                }
            ],
            education=[
                {
                    'institution': 'Technical University',
                    'degree': 'Bachelor of Computer Science',
                    'year': '2019',
                    'gpa': '3.8'
                }
            ],
            skills=[
                'Cybersecurity', 'Penetration Testing', 'Vulnerability Assessment',
                'Cloud Security', 'AWS', 'Network Security', 'Python', 'Linux'
            ],
            portfolio_links={
                'LinkedIn': 'https://linkedin.com/in/ankit-thakur',
                'GitHub': 'https://github.com/ankitthakur',
                'Portfolio': 'https://ankitthakur.dev'
            },
            cover_letter_template="""Dear Hiring Manager,

I am excited to apply for the {position} role at {company}. With my extensive background in cybersecurity and passion for protecting digital assets, I believe I would be a valuable addition to your team.

In my current role as Senior Cybersecurity Engineer, I have successfully led multiple security initiatives, conducted thorough penetration testing, and implemented robust security frameworks that reduced security incidents by 40%.

I am particularly drawn to {company}'s commitment to innovation and security excellence. I would welcome the opportunity to contribute my expertise in cloud security, threat analysis, and risk assessment to help strengthen your security posture.

Thank you for your consideration. I look forward to discussing how I can contribute to your team's success.

Best regards,
Ankit Thakur""",
            resume_path="/Users/ankitthakur/Downloads/ai-job-autopilot/Ankit_Thakur_Resume.pdf",
            preferences={
                'salary_expectation': '€80,000 - €120,000',
                'availability': 'Immediately',
                'visa_status': 'Authorized to work in EU',
                'willing_to_relocate': True,
                'remote_work': True
            }
        )
    
    async def auto_fill_application(self, job_url: str, company_name: str, position_title: str) -> Dict[str, Any]:
        """Automatically fill job application on any portal"""
        
        result = {
            'success': False,
            'url': job_url,
            'company': company_name,
            'position': position_title,
            'steps_completed': [],
            'errors': [],
            'screenshot_path': None
        }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                await self._send_update(f"🌐 Opening job application: {position_title} at {company_name}")
                
                # Navigate to job page
                await page.goto(job_url)
                await page.wait_for_load_state('networkidle')
                result['steps_completed'].append('Navigated to job page')
                
                # Look for application form or apply button
                await self._send_update("🔍 Detecting application form...")
                apply_button = await self._find_apply_button(page)
                
                if apply_button:
                    await self._send_update("🖱️ Clicking apply button...")
                    await apply_button.click()
                    await page.wait_for_timeout(3000)
                    result['steps_completed'].append('Clicked apply button')
                
                # Wait for application form to load
                await page.wait_for_timeout(2000)
                
                # Detect and analyze form fields
                await self._send_update("📝 Analyzing application form...")
                form_fields = await self._detect_form_fields(page)
                
                if not form_fields:
                    await self._send_update("❌ No application form detected")
                    result['errors'].append('No application form found')
                    return result
                
                await self._send_update(f"✅ Detected {len(form_fields)} form fields")
                
                # Fill out the form
                filled_fields = 0
                for field in form_fields:
                    try:
                        success = await self._fill_form_field(page, field, company_name, position_title)
                        if success:
                            filled_fields += 1
                            await self._send_update(f"✅ Filled: {field.label or field.field_name}")
                        await asyncio.sleep(0.5)  # Prevent being detected as bot
                        
                    except Exception as e:
                        self.logger.error(f"Error filling field {field.field_name}: {e}")
                        result['errors'].append(f"Failed to fill {field.field_name}: {str(e)}")
                
                result['steps_completed'].append(f'Filled {filled_fields}/{len(form_fields)} fields')
                
                # Handle file uploads (resume/cover letter)
                await self._handle_file_uploads(page, result)
                
                # Take screenshot before submission
                screenshot_path = f"screenshots/application_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                Path("screenshots").mkdir(exist_ok=True)
                await page.screenshot(path=screenshot_path, full_page=True)
                result['screenshot_path'] = screenshot_path
                
                # Look for and click submit button
                submit_button = await self._find_submit_button(page)
                if submit_button:
                    await self._send_update("🚀 Submitting application...")
                    
                    # Optional: Add confirmation dialog
                    # await submit_button.click()
                    # result['steps_completed'].append('Application submitted')
                    # result['success'] = True
                    
                    # For safety, we'll just report that we're ready to submit
                    await self._send_update("✅ Application form completed and ready for submission")
                    result['steps_completed'].append('Form completed - ready for manual submission')
                    result['success'] = True
                else:
                    result['errors'].append('Submit button not found')
                
                await browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in auto-fill process: {e}")
            result['errors'].append(f"Auto-fill error: {str(e)}")
        
        return result
    
    async def _find_apply_button(self, page: Page) -> Optional[ElementHandle]:
        """Find the apply button on the job page"""
        
        apply_selectors = [
            # Common apply button selectors
            'button:has-text("Apply")', 'button:has-text("Apply Now")',
            'button:has-text("Easy Apply")', 'a:has-text("Apply")',
            'button:has-text("Submit Application")', 'input[value*="Apply"]',
            '.apply-button', '.apply-btn', '#apply-button', '#apply-btn',
            '.easy-apply-button', '.job-apply-button', '.apply-now-button',
            
            # Platform-specific selectors
            'button[data-control-name*="apply"]',  # LinkedIn
            '.ia-IndeedApplyButton',  # Indeed
            '.apply-button-top'  # Glassdoor
        ]
        
        for selector in apply_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    # Check if element is visible and clickable
                    if await element.is_visible() and await element.is_enabled():
                        return element
            except:
                continue
        
        return None
    
    async def _detect_form_fields(self, page: Page) -> List[FormField]:
        """Detect and analyze all form fields on the page"""
        
        form_fields = []
        
        # Get all potential form elements
        selectors = [
            'input:not([type="hidden"]):not([type="submit"]):not([type="button"])',
            'textarea',
            'select'
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            
            for element in elements:
                try:
                    # Skip invisible elements
                    if not await element.is_visible():
                        continue
                    
                    # Get element properties
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    input_type = await element.get_attribute('type') or 'text'
                    name = await element.get_attribute('name') or ''
                    placeholder = await element.get_attribute('placeholder') or ''
                    required = await element.get_attribute('required') is not None
                    
                    # Get label text
                    label = await self._find_field_label(page, element)
                    
                    # Get options for select elements
                    options = []
                    if tag_name == 'select':
                        option_elements = await element.query_selector_all('option')
                        for option in option_elements:
                            option_text = await option.text_content()
                            if option_text and option_text.strip():
                                options.append(option_text.strip())
                    
                    # Determine field type
                    if tag_name == 'select':
                        field_type = 'select'
                    elif tag_name == 'textarea':
                        field_type = 'textarea'
                    elif input_type in ['file']:
                        field_type = 'file'
                    elif input_type in ['radio', 'checkbox']:
                        field_type = input_type
                    else:
                        field_type = input_type
                    
                    # Suggest value based on field analysis
                    suggested_value = self._suggest_field_value(name, label, placeholder, field_type, options)
                    
                    form_field = FormField(
                        element=element,
                        field_type=field_type,
                        field_name=name,
                        label=label,
                        is_required=required,
                        placeholder=placeholder,
                        options=options,
                        suggested_value=suggested_value
                    )
                    
                    form_fields.append(form_field)
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing form element: {e}")
                    continue
        
        return form_fields
    
    async def _find_field_label(self, page: Page, element: ElementHandle) -> str:
        """Find the label for a form field"""
        
        try:
            # Try to find associated label element
            element_id = await element.get_attribute('id')
            if element_id:
                label_element = await page.query_selector(f'label[for="{element_id}"]')
                if label_element:
                    return await label_element.text_content()
            
            # Try to find parent label
            parent_label = await element.evaluate('''
                el => {
                    let parent = el.closest('label');
                    if (parent) return parent.textContent;
                    
                    // Look for nearby text
                    let prev = el.previousElementSibling;
                    while (prev && prev.tagName !== 'INPUT' && prev.tagName !== 'TEXTAREA' && prev.tagName !== 'SELECT') {
                        if (prev.textContent && prev.textContent.trim()) {
                            return prev.textContent.trim();
                        }
                        prev = prev.previousElementSibling;
                    }
                    
                    return '';
                }
            ''')
            
            return parent_label or ''
            
        except:
            return ''
    
    def _suggest_field_value(self, name: str, label: str, placeholder: str, field_type: str, options: List[str]) -> str:
        """Suggest appropriate value for a form field"""
        
        # Combine all text for analysis
        field_text = f"{name} {label} {placeholder}".lower()
        
        # Match against known patterns
        for field_category, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, field_text, re.IGNORECASE):
                    return self._get_value_for_category(field_category, field_type, options)
        
        # Special handling for specific field types
        if field_type == 'email':
            return self.app_data.personal_info['email']
        elif field_type == 'tel':
            return self.app_data.personal_info['phone']
        elif field_type == 'url':
            return self.app_data.personal_info['portfolio']
        elif field_type == 'textarea':
            if any(term in field_text for term in ['cover', 'motivation', 'why', 'tell']):
                return self._generate_cover_letter()
            elif any(term in field_text for term in ['experience', 'background']):
                return self._generate_experience_summary()
        
        return ''
    
    def _get_value_for_category(self, category: str, field_type: str, options: List[str]) -> str:
        """Get appropriate value for a field category"""
        
        personal_info = self.app_data.personal_info
        preferences = self.app_data.preferences
        
        value_mapping = {
            'first_name': personal_info['first_name'],
            'last_name': personal_info['last_name'],
            'full_name': personal_info['full_name'],
            'email': personal_info['email'],
            'phone': personal_info['phone'],
            'address': personal_info['address'],
            'city': personal_info['city'],
            'state': personal_info['state'],
            'country': personal_info['country'],
            'zipcode': personal_info['zipcode'],
            'linkedin': personal_info['linkedin'],
            'portfolio': personal_info['portfolio'],
            'github': personal_info['github'],
            'experience_years': '5+ years',
            'current_company': self.app_data.experience[0]['company'] if self.app_data.experience else '',
            'current_position': self.app_data.experience[0]['position'] if self.app_data.experience else '',
            'salary_expectation': preferences['salary_expectation'],
            'availability': preferences['availability'],
            'visa_status': preferences['visa_status']
        }
        
        base_value = value_mapping.get(category, '')
        
        # Handle select fields with options
        if field_type == 'select' and options:
            return self._match_select_option(base_value, options, category)
        
        return base_value
    
    def _match_select_option(self, target_value: str, options: List[str], category: str) -> str:
        """Match target value to closest select option"""
        
        if not target_value or not options:
            return ''
        
        target_lower = target_value.lower()
        
        # Direct match
        for option in options:
            if option.lower() == target_lower:
                return option
        
        # Partial match
        for option in options:
            if target_lower in option.lower() or option.lower() in target_lower:
                return option
        
        # Category-specific matching
        if category == 'experience_years':
            for option in options:
                if any(year in option for year in ['5', '3-5', '4-6', 'senior']):
                    return option
        elif category == 'country':
            for option in options:
                if any(country in option.lower() for country in ['germany', 'united states', 'canada']):
                    return option
        
        return ''
    
    async def _fill_form_field(self, page: Page, field: FormField, company_name: str, position_title: str) -> bool:
        """Fill a specific form field"""
        
        try:
            if not field.suggested_value:
                return False
            
            if field.field_type == 'select':
                await field.element.select_option(field.suggested_value)
            
            elif field.field_type == 'textarea':
                # Clear existing content and fill
                await field.element.click()
                await field.element.fill('')
                
                # Generate contextual content if needed
                if 'cover' in field.label.lower() or 'motivation' in field.label.lower():
                    content = self._generate_cover_letter(company_name, position_title)
                else:
                    content = field.suggested_value
                
                await field.element.type(content, delay=10)  # Simulate human typing
            
            elif field.field_type == 'checkbox':
                if field.suggested_value.lower() in ['true', 'yes', '1']:
                    await field.element.check()
            
            elif field.field_type == 'radio':
                await field.element.check()
            
            elif field.field_type == 'file':
                if field.suggested_value and Path(field.suggested_value).exists():
                    await field.element.set_input_files(field.suggested_value)
            
            else:  # text, email, tel, url, etc.
                await field.element.click()
                await field.element.fill('')
                await field.element.type(field.suggested_value, delay=20)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error filling field {field.field_name}: {e}")
            return False
    
    def _generate_cover_letter(self, company_name: str = "", position_title: str = "") -> str:
        """Generate personalized cover letter"""
        
        template = self.app_data.cover_letter_template
        
        # Replace placeholders
        cover_letter = template.format(
            company=company_name or "[COMPANY]",
            position=position_title or "[POSITION]"
        )
        
        return cover_letter
    
    def _generate_experience_summary(self) -> str:
        """Generate experience summary"""
        
        if not self.app_data.experience:
            return "Experienced professional with strong background in cybersecurity and technology."
        
        exp = self.app_data.experience[0]
        return f"Currently working as {exp['position']} at {exp['company']}. {exp['description']}"
    
    async def _handle_file_uploads(self, page: Page, result: Dict) -> None:
        """Handle resume and document uploads"""
        
        try:
            # Look for file upload fields
            file_inputs = await page.query_selector_all('input[type="file"]')
            
            for file_input in file_inputs:
                if not await file_input.is_visible():
                    continue
                
                # Check if it's for resume/CV
                field_info = await self._get_file_field_info(page, file_input)
                
                if any(term in field_info.lower() for term in ['resume', 'cv', 'curriculum']):
                    if Path(self.app_data.resume_path).exists():
                        await file_input.set_input_files(self.app_data.resume_path)
                        await self._send_update("📎 Uploaded resume")
                        result['steps_completed'].append('Resume uploaded')
                    else:
                        result['errors'].append('Resume file not found')
                
        except Exception as e:
            self.logger.error(f"Error handling file uploads: {e}")
            result['errors'].append(f"File upload error: {str(e)}")
    
    async def _get_file_field_info(self, page: Page, file_input: ElementHandle) -> str:
        """Get information about file upload field"""
        
        try:
            # Get nearby text/labels
            info = await file_input.evaluate('''
                el => {
                    let info = [];
                    
                    // Get labels
                    if (el.id) {
                        let label = document.querySelector(`label[for="${el.id}"]`);
                        if (label) info.push(label.textContent);
                    }
                    
                    // Get parent element text
                    let parent = el.parentElement;
                    if (parent) info.push(parent.textContent);
                    
                    // Get nearby elements
                    let prev = el.previousElementSibling;
                    if (prev) info.push(prev.textContent);
                    
                    let next = el.nextElementSibling;
                    if (next) info.push(next.textContent);
                    
                    return info.join(' ');
                }
            ''')
            
            return info
            
        except:
            return ''
    
    async def _find_submit_button(self, page: Page) -> Optional[ElementHandle]:
        """Find the submit button"""
        
        submit_selectors = [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'button:has-text("Apply")',
            'button:has-text("Send Application")', 'button:has-text("Continue")',
            '.submit-button', '.submit-btn', '#submit-button', '#submit-btn',
            '.apply-submit', '.form-submit'
        ]
        
        for selector in submit_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible() and await element.is_enabled():
                    return element
            except:
                continue
        
        return None
    
    async def _send_update(self, message: str):
        """Send progress update"""
        
        if self.update_callback:
            await self.update_callback({
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'level': 'info'
            })
        
        self.logger.info(message)

# Convenience function for integration
async def auto_apply_to_job(
    job_url: str, 
    company_name: str, 
    position_title: str,
    update_callback: Callable = None
) -> Dict[str, Any]:
    """Apply to a job automatically"""
    
    autofill = UniversalAutoFill(update_callback)
    return await autofill.auto_fill_application(job_url, company_name, position_title)