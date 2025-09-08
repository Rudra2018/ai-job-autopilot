#!/usr/bin/env python3
"""
Industry-Standard Auto Form Filler
Automatically fills job application forms using parsed resume data and industry standards
"""

import asyncio
import json
import os
import re
import random
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import yaml
from playwright.async_api import Page, Locator
import openai
from advanced_resume_parser import ParsedResume

@dataclass
class FormField:
    field_type: str  # text, email, phone, select, textarea, file, checkbox, radio
    selectors: List[str]  # CSS selectors to find the field
    required: bool
    data_source: str  # where to get the data from
    validation_pattern: Optional[str] = None
    options: Optional[List[str]] = None  # for select/radio fields

@dataclass
class ApplicationData:
    # Personal Information
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    linkedin_url: str
    portfolio_url: str
    github_url: str
    
    # Professional Information
    current_title: str
    current_company: str
    years_experience: int
    desired_salary: str
    availability: str
    notice_period: str
    
    # Education
    education_level: str
    university: str
    degree: str
    graduation_year: str
    gpa: str
    
    # Work Authorization
    authorized_to_work: str
    visa_status: str
    sponsorship_required: str
    
    # Other
    cover_letter: str
    why_interested: str
    references_available: str
    
    # Files
    resume_path: str
    cover_letter_path: Optional[str] = None

class IndustryStandardFormFiller:
    """Industry-standard form filling with intelligent field detection"""
    
    def __init__(self):
        self.form_patterns = self._load_form_patterns()
        self.industry_standards = self._load_industry_standards()
        self.ai_client = None
        
        # Initialize OpenAI if available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            openai.api_key = openai_key
            self.ai_client = openai
    
    def _load_form_patterns(self) -> Dict[str, FormField]:
        """Load common form field patterns"""
        return {
            'first_name': FormField(
                field_type='text',
                selectors=[
                    'input[name*="first"][name*="name"]',
                    'input[name*="firstName"]',
                    'input[name*="fname"]',
                    'input[id*="first"][id*="name"]',
                    'input[placeholder*="First name"]',
                    'input[aria-label*="First name"]'
                ],
                required=True,
                data_source='personal.first_name'
            ),
            'last_name': FormField(
                field_type='text',
                selectors=[
                    'input[name*="last"][name*="name"]',
                    'input[name*="lastName"]',
                    'input[name*="lname"]',
                    'input[id*="last"][id*="name"]',
                    'input[placeholder*="Last name"]',
                    'input[aria-label*="Last name"]'
                ],
                required=True,
                data_source='personal.last_name'
            ),
            'email': FormField(
                field_type='email',
                selectors=[
                    'input[type="email"]',
                    'input[name*="email"]',
                    'input[id*="email"]',
                    'input[placeholder*="email"]'
                ],
                required=True,
                data_source='personal.email',
                validation_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            ),
            'phone': FormField(
                field_type='tel',
                selectors=[
                    'input[type="tel"]',
                    'input[name*="phone"]',
                    'input[name*="mobile"]',
                    'input[id*="phone"]',
                    'input[placeholder*="phone"]'
                ],
                required=True,
                data_source='personal.phone'
            ),
            'address': FormField(
                field_type='text',
                selectors=[
                    'input[name*="address"]',
                    'input[name*="street"]',
                    'input[id*="address"]',
                    'textarea[name*="address"]'
                ],
                required=False,
                data_source='personal.address'
            ),
            'city': FormField(
                field_type='text',
                selectors=[
                    'input[name*="city"]',
                    'input[id*="city"]',
                    'input[placeholder*="city"]'
                ],
                required=False,
                data_source='personal.city'
            ),
            'state': FormField(
                field_type='select',
                selectors=[
                    'select[name*="state"]',
                    'select[name*="region"]',
                    'input[name*="state"]',
                    'select[id*="state"]'
                ],
                required=False,
                data_source='personal.state'
            ),
            'country': FormField(
                field_type='select',
                selectors=[
                    'select[name*="country"]',
                    'input[name*="country"]',
                    'select[id*="country"]'
                ],
                required=False,
                data_source='personal.country'
            ),
            'linkedin': FormField(
                field_type='url',
                selectors=[
                    'input[name*="linkedin"]',
                    'input[id*="linkedin"]',
                    'input[placeholder*="linkedin"]',
                    'input[name*="profile"]'
                ],
                required=False,
                data_source='personal.linkedin_url'
            ),
            'github': FormField(
                field_type='url',
                selectors=[
                    'input[name*="github"]',
                    'input[id*="github"]',
                    'input[placeholder*="github"]'
                ],
                required=False,
                data_source='personal.github_url'
            ),
            'portfolio': FormField(
                field_type='url',
                selectors=[
                    'input[name*="portfolio"]',
                    'input[name*="website"]',
                    'input[id*="portfolio"]',
                    'input[placeholder*="portfolio"]'
                ],
                required=False,
                data_source='personal.portfolio_url'
            ),
            'current_title': FormField(
                field_type='text',
                selectors=[
                    'input[name*="current"][name*="title"]',
                    'input[name*="job"][name*="title"]',
                    'input[name*="position"]',
                    'input[id*="current"][id*="title"]'
                ],
                required=False,
                data_source='professional.current_title'
            ),
            'current_company': FormField(
                field_type='text',
                selectors=[
                    'input[name*="current"][name*="company"]',
                    'input[name*="employer"]',
                    'input[id*="current"][id*="company"]'
                ],
                required=False,
                data_source='professional.current_company'
            ),
            'experience_years': FormField(
                field_type='select',
                selectors=[
                    'select[name*="experience"]',
                    'select[name*="years"]',
                    'input[name*="experience"]'
                ],
                required=False,
                data_source='professional.years_experience',
                options=['0-1', '1-2', '2-5', '5-10', '10+']
            ),
            'salary_expectation': FormField(
                field_type='text',
                selectors=[
                    'input[name*="salary"]',
                    'input[name*="compensation"]',
                    'input[id*="salary"]'
                ],
                required=False,
                data_source='professional.desired_salary'
            ),
            'education_level': FormField(
                field_type='select',
                selectors=[
                    'select[name*="education"]',
                    'select[name*="degree"]',
                    'select[id*="education"]'
                ],
                required=False,
                data_source='education.education_level',
                options=['High School', 'Bachelor', 'Master', 'PhD', 'Other']
            ),
            'university': FormField(
                field_type='text',
                selectors=[
                    'input[name*="university"]',
                    'input[name*="school"]',
                    'input[name*="college"]',
                    'input[id*="university"]'
                ],
                required=False,
                data_source='education.university'
            ),
            'graduation_year': FormField(
                field_type='select',
                selectors=[
                    'select[name*="graduation"]',
                    'select[name*="grad"][name*="year"]',
                    'input[name*="graduation"]'
                ],
                required=False,
                data_source='education.graduation_year'
            ),
            'work_authorization': FormField(
                field_type='radio',
                selectors=[
                    'input[name*="authorized"]',
                    'input[name*="eligible"]',
                    'input[name*="work"][name*="us"]'
                ],
                required=False,
                data_source='authorization.authorized_to_work',
                options=['Yes', 'No']
            ),
            'sponsorship': FormField(
                field_type='radio',
                selectors=[
                    'input[name*="sponsor"]',
                    'input[name*="visa"]',
                    'input[name*="h1b"]'
                ],
                required=False,
                data_source='authorization.sponsorship_required',
                options=['Yes', 'No']
            ),
            'cover_letter': FormField(
                field_type='textarea',
                selectors=[
                    'textarea[name*="cover"]',
                    'textarea[name*="letter"]',
                    'textarea[name*="why"]',
                    'textarea[id*="cover"]'
                ],
                required=False,
                data_source='content.cover_letter'
            ),
            'resume_upload': FormField(
                field_type='file',
                selectors=[
                    'input[type="file"][name*="resume"]',
                    'input[type="file"][name*="cv"]',
                    'input[type="file"][id*="resume"]',
                    'input[type="file"]'
                ],
                required=True,
                data_source='files.resume_path'
            )
        }
    
    def _load_industry_standards(self) -> Dict[str, Any]:
        """Load industry standard responses and formats"""
        return {
            'work_authorization_responses': {
                'us_citizen': 'Yes, I am authorized to work in the United States',
                'visa_holder': 'Yes, I am authorized to work with current visa status',
                'need_sponsorship': 'I will require sponsorship for work authorization'
            },
            'availability': {
                'immediate': 'Immediately',
                'two_weeks': '2 weeks notice',
                'one_month': '1 month notice',
                'flexible': 'Flexible based on role requirements'
            },
            'salary_formats': {
                'hourly': '$XX/hour',
                'annual': '$XX,000 annually',
                'negotiable': 'Negotiable based on role and benefits package'
            },
            'common_locations': [
                'Remote', 'New York, NY', 'San Francisco, CA', 'Seattle, WA',
                'Austin, TX', 'Boston, MA', 'Chicago, IL', 'Los Angeles, CA',
                'Berlin, Germany', 'London, UK', 'Amsterdam, Netherlands'
            ]
        }
    
    def create_application_data(self, resume: ParsedResume, job_specific_data: Dict = None) -> ApplicationData:
        """Create application data from parsed resume"""
        
        # Extract name parts
        name_parts = resume.contact_info.name.split() if resume.contact_info.name else ["", ""]
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Extract location parts
        location = resume.contact_info.location or ""
        location_parts = self._parse_location(location)
        
        # Get current job info
        current_job = resume.work_experience[0] if resume.work_experience else None
        
        # Get education info
        latest_education = resume.education[0] if resume.education else None
        
        # Generate job-specific content
        cover_letter = self._generate_cover_letter(resume, job_specific_data)
        why_interested = self._generate_why_interested(resume, job_specific_data)
        
        # Default values from job-specific data
        job_data = job_specific_data or {}
        
        return ApplicationData(
            # Personal Information
            first_name=first_name,
            last_name=last_name,
            email=resume.contact_info.email or "",
            phone=resume.contact_info.phone or "",
            address=location_parts.get('address', ''),
            city=location_parts.get('city', ''),
            state=location_parts.get('state', ''),
            country=location_parts.get('country', 'United States'),
            postal_code=location_parts.get('postal_code', ''),
            linkedin_url=resume.contact_info.linkedin or "",
            portfolio_url=resume.contact_info.portfolio or "",
            github_url=resume.contact_info.github or "",
            
            # Professional Information
            current_title=current_job.title if current_job else "",
            current_company=current_job.company if current_job else "",
            years_experience=int(resume.total_experience_years),
            desired_salary=job_data.get('salary_expectation', 'Competitive'),
            availability=job_data.get('availability', 'Two weeks notice'),
            notice_period=job_data.get('notice_period', '2 weeks'),
            
            # Education
            education_level=self._map_education_level(latest_education.degree if latest_education else ""),
            university=latest_education.institution if latest_education else "",
            degree=latest_education.degree if latest_education else "",
            graduation_year=latest_education.graduation_year if latest_education else "",
            gpa=latest_education.gpa if latest_education else "",
            
            # Work Authorization
            authorized_to_work=job_data.get('work_authorization', 'Yes'),
            visa_status=job_data.get('visa_status', 'Citizen'),
            sponsorship_required=job_data.get('sponsorship_required', 'No'),
            
            # Content
            cover_letter=cover_letter,
            why_interested=why_interested,
            references_available="Available upon request",
            
            # Files
            resume_path=resume.file_path,
            cover_letter_path=job_data.get('cover_letter_path')
        )
    
    def _parse_location(self, location: str) -> Dict[str, str]:
        """Parse location string into components"""
        if not location:
            return {}
        
        # Common patterns: "City, State", "City, Country", "City, State, Country"
        parts = [part.strip() for part in location.split(',')]
        
        result = {}
        
        if len(parts) >= 1:
            result['city'] = parts[0]
        
        if len(parts) >= 2:
            # Check if it's a US state (2 letters) or country
            second_part = parts[1]
            if len(second_part) == 2 and second_part.isupper():
                result['state'] = second_part
                result['country'] = 'United States'
            else:
                result['country'] = second_part
        
        if len(parts) >= 3:
            result['country'] = parts[2]
        
        return result
    
    def _map_education_level(self, degree: str) -> str:
        """Map degree to standard education levels"""
        if not degree:
            return ""
        
        degree_lower = degree.lower()
        
        if any(term in degree_lower for term in ['phd', 'doctorate', 'doctoral']):
            return "PhD"
        elif any(term in degree_lower for term in ['master', 'mba', 'ms', 'ma']):
            return "Master"
        elif any(term in degree_lower for term in ['bachelor', 'bs', 'ba', 'btech']):
            return "Bachelor"
        elif any(term in degree_lower for term in ['associate', 'aa', 'as']):
            return "Associate"
        else:
            return "Other"
    
    def _generate_cover_letter(self, resume: ParsedResume, job_data: Dict = None) -> str:
        """Generate tailored cover letter"""
        if not job_data:
            job_data = {}
        
        company = job_data.get('company', 'your company')
        position = job_data.get('position', 'this position')
        
        # Get top skills
        all_skills = []
        for skills_list in resume.skills.values():
            all_skills.extend(skills_list)
        top_skills = all_skills[:5]
        
        # Get recent experience
        recent_experience = ""
        if resume.work_experience:
            recent_job = resume.work_experience[0]
            recent_experience = f"In my recent role as {recent_job.title} at {recent_job.company}, I have gained valuable experience in {', '.join(recent_job.skills_used[:3])}."
        
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {position} role at {company}. With {resume.total_experience_years:.1f} years of experience in {resume.primary_domain}, I am excited about the opportunity to contribute to your team.

{recent_experience}

My key qualifications include:
• Expertise in {', '.join(top_skills[:3])}
• Strong background in {resume.primary_domain}
• {resume.seniority_level.title()}-level experience with a track record of success

I am particularly drawn to {company} because of your reputation for innovation and excellence in the industry. I would welcome the opportunity to discuss how my skills and experience can contribute to your team's continued success.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{resume.contact_info.name}"""

        return cover_letter
    
    def _generate_why_interested(self, resume: ParsedResume, job_data: Dict = None) -> str:
        """Generate why interested response"""
        if not job_data:
            job_data = {}
        
        company = job_data.get('company', 'your company')
        
        return f"I am interested in this role at {company} because it aligns perfectly with my background in {resume.primary_domain} and offers the opportunity to apply my {resume.total_experience_years:.0f} years of experience in a challenging and innovative environment."
    
    async def fill_form(self, page: Page, application_data: ApplicationData, form_url: str = None) -> Dict[str, Any]:
        """Fill out a job application form automatically"""
        
        if form_url:
            await page.goto(form_url)
            await page.wait_for_timeout(3000)
        
        print(f"🔧 Starting form filling process...")
        
        results = {
            'filled_fields': [],
            'failed_fields': [],
            'uploaded_files': [],
            'form_submitted': False,
            'errors': []
        }
        
        try:
            # Handle any popups or overlays first
            await self._handle_popups(page)
            
            # Fill each field type
            for field_name, field_config in self.form_patterns.items():
                try:
                    success = await self._fill_field(page, field_name, field_config, application_data)
                    if success:
                        results['filled_fields'].append(field_name)
                        print(f"   ✅ Filled: {field_name}")
                    else:
                        results['failed_fields'].append(field_name)
                        print(f"   ⚠️  Skipped: {field_name} (field not found)")
                        
                except Exception as e:
                    results['failed_fields'].append(field_name)
                    results['errors'].append(f"{field_name}: {str(e)}")
                    print(f"   ❌ Error filling {field_name}: {str(e)}")
            
            # Handle file uploads separately
            await self._handle_file_uploads(page, application_data, results)
            
            # Look for and handle special fields
            await self._handle_special_fields(page, application_data, results)
            
            print(f"📊 Form filling completed:")
            print(f"   ✅ Successfully filled: {len(results['filled_fields'])} fields")
            print(f"   ⚠️  Failed/Skipped: {len(results['failed_fields'])} fields")
            print(f"   📎 Files uploaded: {len(results['uploaded_files'])}")
            
        except Exception as e:
            print(f"❌ Error during form filling: {str(e)}")
            results['errors'].append(f"General error: {str(e)}")
        
        return results
    
    async def _fill_field(self, page: Page, field_name: str, field_config: FormField, data: ApplicationData) -> bool:
        """Fill a specific field"""
        # Get data value
        value = self._get_field_value(field_name, field_config.data_source, data)
        
        if not value and field_config.required:
            print(f"   ⚠️  Required field {field_name} has no data")
            return False
        
        if not value:
            return False  # Skip optional fields with no data
        
        # Try each selector until we find the field
        for selector in field_config.selectors:
            try:
                elements = await page.locator(selector).all()
                if not elements:
                    continue
                
                element = elements[0]
                
                # Fill based on field type
                if field_config.field_type == 'text' or field_config.field_type == 'email' or field_config.field_type == 'tel' or field_config.field_type == 'url':
                    await element.clear()
                    await element.type(str(value), delay=random.randint(50, 150))
                    
                elif field_config.field_type == 'textarea':
                    await element.clear()
                    # Type with more realistic delays for longer text
                    await self._type_naturally(element, str(value))
                    
                elif field_config.field_type == 'select':
                    await self._fill_select_field(element, str(value), field_config.options)
                    
                elif field_config.field_type == 'radio':
                    await self._fill_radio_field(page, selector, str(value))
                    
                elif field_config.field_type == 'checkbox':
                    if str(value).lower() in ['yes', 'true', '1']:
                        await element.check()
                
                return True
                
            except Exception as e:
                print(f"     Error with selector {selector}: {str(e)}")
                continue
        
        return False
    
    async def _type_naturally(self, element: Locator, text: str):
        """Type text with natural human-like timing"""
        words = text.split()
        for i, word in enumerate(words):
            await element.type(word, delay=random.randint(50, 120))
            if i < len(words) - 1:
                await element.type(" ")
                # Occasional pause between sentences
                if word.endswith('.') or word.endswith('!') or word.endswith('?'):
                    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def _fill_select_field(self, element: Locator, value: str, options: List[str] = None):
        """Fill select dropdown field"""
        try:
            # First, try direct value selection
            await element.select_option(value=value)
        except:
            try:
                # Try by text content
                await element.select_option(label=value)
            except:
                # Fuzzy match against available options
                option_elements = await element.locator('option').all()
                for option in option_elements:
                    option_text = await option.text_content()
                    if option_text and (value.lower() in option_text.lower() or option_text.lower() in value.lower()):
                        option_value = await option.get_attribute('value')
                        await element.select_option(value=option_value)
                        break
    
    async def _fill_radio_field(self, page: Page, base_selector: str, value: str):
        """Fill radio button field"""
        # Look for radio buttons with the base selector
        radio_elements = await page.locator(f'{base_selector}').all()
        
        for radio in radio_elements:
            # Check the label or value
            label_text = ""
            try:
                # Try to find associated label
                radio_id = await radio.get_attribute('id')
                if radio_id:
                    label = page.locator(f'label[for="{radio_id}"]')
                    if await label.count() > 0:
                        label_text = await label.text_content() or ""
                
                # Also check the radio value
                radio_value = await radio.get_attribute('value') or ""
                
                # Match value
                if (value.lower() in label_text.lower()) or (value.lower() in radio_value.lower()):
                    await radio.check()
                    break
                    
            except Exception as e:
                print(f"     Error checking radio option: {e}")
                continue
    
    def _get_field_value(self, field_name: str, data_source: str, data: ApplicationData) -> Any:
        """Get value for a field from application data"""
        try:
            # Navigate nested data source like "personal.first_name"
            parts = data_source.split('.')
            value = data
            
            for part in parts:
                value = getattr(value, part, None)
                if value is None:
                    break
            
            return value
            
        except Exception as e:
            print(f"Error getting field value for {field_name}: {e}")
            return None
    
    async def _handle_popups(self, page: Page):
        """Handle common popups and overlays"""
        popup_selectors = [
            'button:has-text("Accept")', 
            'button:has-text("Accept all")',
            'button:has-text("Agree")', 
            'button:has-text("OK")',
            'button:has-text("Close")', 
            'button[aria-label="Close"]',
            '.modal-close', 
            '.popup-close', 
            '.overlay-close',
            '[data-dismiss="modal"]', 
            '.cookie-accept', 
            '.gdpr-accept'
        ]
        
        for selector in popup_selectors:
            try:
                element = page.locator(selector)
                if await element.count() > 0:
                    await element.first.click()
                    await page.wait_for_timeout(1000)
                    break
            except:
                continue
    
    async def _handle_file_uploads(self, page: Page, data: ApplicationData, results: Dict):
        """Handle file upload fields"""
        file_selectors = [
            'input[type="file"][name*="resume"]',
            'input[type="file"][name*="cv"]',
            'input[type="file"][id*="resume"]',
            'input[type="file"]'
        ]
        
        # Upload resume
        if data.resume_path and Path(data.resume_path).exists():
            for selector in file_selectors:
                try:
                    file_input = page.locator(selector)
                    if await file_input.count() > 0:
                        await file_input.first.set_input_files(data.resume_path)
                        results['uploaded_files'].append('resume')
                        print(f"   📎 Uploaded resume: {Path(data.resume_path).name}")
                        break
                except Exception as e:
                    print(f"   ❌ Error uploading resume: {e}")
        
        # Upload cover letter if available
        if data.cover_letter_path and Path(data.cover_letter_path).exists():
            cover_letter_selectors = [
                'input[type="file"][name*="cover"]',
                'input[type="file"][name*="letter"]'
            ]
            
            for selector in cover_letter_selectors:
                try:
                    file_input = page.locator(selector)
                    if await file_input.count() > 0:
                        await file_input.first.set_input_files(data.cover_letter_path)
                        results['uploaded_files'].append('cover_letter')
                        print(f"   📎 Uploaded cover letter")
                        break
                except Exception as e:
                    print(f"   ❌ Error uploading cover letter: {e}")
    
    async def _handle_special_fields(self, page: Page, data: ApplicationData, results: Dict):
        """Handle special fields that need custom logic"""
        
        # Handle "How did you hear about us?" fields
        referral_selectors = [
            'select[name*="referral"]',
            'select[name*="source"]',
            'select[name*="hear"]'
        ]
        
        for selector in referral_selectors:
            try:
                element = page.locator(selector)
                if await element.count() > 0:
                    # Try common options
                    options = ['Company website', 'LinkedIn', 'Job board', 'Referral']
                    for option in options:
                        try:
                            await element.select_option(label=option)
                            results['filled_fields'].append('referral_source')
                            print(f"   ✅ Selected referral source: {option}")
                            break
                        except:
                            continue
                    break
            except:
                continue
        
        # Handle custom questions using AI if available
        await self._handle_custom_questions(page, data, results)
    
    async def _handle_custom_questions(self, page: Page, data: ApplicationData, results: Dict):
        """Handle custom application questions using AI"""
        if not self.ai_client:
            return
        
        # Look for textarea fields that might be custom questions
        custom_textareas = await page.locator('textarea').all()
        
        for textarea in custom_textareas:
            try:
                # Skip if already filled
                current_value = await textarea.input_value()
                if current_value and len(current_value) > 10:
                    continue
                
                # Try to find the question text
                question_text = await self._extract_question_text(textarea)
                
                if question_text and len(question_text) > 10:
                    # Generate answer using AI
                    answer = await self._generate_ai_answer(question_text, data)
                    
                    if answer:
                        await textarea.clear()
                        await self._type_naturally(textarea, answer)
                        results['filled_fields'].append(f'custom_question: {question_text[:50]}...')
                        print(f"   🧠 AI answered custom question")
                
            except Exception as e:
                print(f"   ❌ Error handling custom question: {e}")
    
    async def _extract_question_text(self, textarea: Locator) -> str:
        """Extract the question text associated with a textarea"""
        try:
            # Try to find label
            textarea_id = await textarea.get_attribute('id')
            if textarea_id:
                label = textarea.page.locator(f'label[for="{textarea_id}"]')
                if await label.count() > 0:
                    return await label.text_content() or ""
            
            # Try to find preceding text
            parent = textarea.locator('..')
            parent_text = await parent.text_content() or ""
            
            # Extract question-like text (text ending with ?)
            sentences = parent_text.split('.')
            for sentence in sentences:
                if '?' in sentence:
                    return sentence.strip()
            
            return parent_text[:200] if len(parent_text) > 10 else ""
            
        except:
            return ""
    
    async def _generate_ai_answer(self, question: str, data: ApplicationData) -> str:
        """Generate AI answer for custom questions"""
        try:
            prompt = f"""
            You are helping fill out a job application form. Answer this question professionally and concisely:
            
            Question: {question}
            
            Candidate background:
            - Name: {data.first_name} {data.last_name}
            - Current role: {data.current_title} at {data.current_company}
            - Experience: {data.years_experience} years
            - Education: {data.degree} from {data.university}
            
            Provide a brief, professional answer (100-200 words):
            """
            
            response = await self.ai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"   ❌ AI answer generation failed: {e}")
            return ""
    
    async def review_before_submit(self, page: Page) -> Dict[str, Any]:
        """Review form before submission"""
        print("🔍 Reviewing form before submission...")
        
        review_results = {
            'required_fields_filled': [],
            'missing_required_fields': [],
            'form_ready': False,
            'submit_button_found': False
        }
        
        # Check for required fields
        required_selectors = [
            'input[required]',
            'select[required]',
            'textarea[required]',
            'input[aria-required="true"]'
        ]
        
        for selector in required_selectors:
            try:
                elements = await page.locator(selector).all()
                for element in elements:
                    value = await element.input_value()
                    field_name = await element.get_attribute('name') or await element.get_attribute('id') or 'unknown'
                    
                    if value and value.strip():
                        review_results['required_fields_filled'].append(field_name)
                    else:
                        review_results['missing_required_fields'].append(field_name)
                        
            except Exception as e:
                print(f"   Error checking required fields: {e}")
        
        # Look for submit button
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Apply")',
            'button:has-text("Send")',
            '.submit-btn',
            '.apply-btn'
        ]
        
        for selector in submit_selectors:
            if await page.locator(selector).count() > 0:
                review_results['submit_button_found'] = True
                break
        
        # Determine if form is ready
        review_results['form_ready'] = (
            len(review_results['missing_required_fields']) == 0 and 
            review_results['submit_button_found']
        )
        
        print(f"📋 Form review completed:")
        print(f"   ✅ Required fields filled: {len(review_results['required_fields_filled'])}")
        print(f"   ❌ Missing required fields: {len(review_results['missing_required_fields'])}")
        print(f"   🎯 Form ready to submit: {review_results['form_ready']}")
        
        if review_results['missing_required_fields']:
            print(f"   ⚠️  Missing: {', '.join(review_results['missing_required_fields'])}")
        
        return review_results

async def main():
    """Demo function"""
    print("🤖 AUTO FORM FILLER DEMO")
    print("="*40)
    
    # This would normally be integrated with the full application system
    print("💡 This system integrates with:")
    print("   • Resume parser for candidate data")
    print("   • Job scraper for application URLs") 
    print("   • Browser automation for form filling")
    print("   • AI services for custom question answering")
    
    print("\n✅ Auto Form Filler system created successfully!")
    print("🔧 Ready to integrate with job application pipeline")

if __name__ == "__main__":
    asyncio.run(main())