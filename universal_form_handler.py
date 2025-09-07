#!/usr/bin/env python3
"""
Universal Form Handler - Handles ANY job application form
"""

import asyncio
from playwright.async_api import async_playwright

class UniversalFormHandler:
    def __init__(self, candidate_data):
        self.data = candidate_data
    
    async def handle_any_form(self, page, form_context=""):
        """Universal form handler that works on any job application form"""
        try:
            print(f"🔧 Universal Form Handler: {form_context}")
            
            # Step 1: Dismiss ALL possible popups/overlays
            await self.nuclear_popup_dismissal(page)
            
            # Step 2: Smart field detection and filling
            await self.universal_field_filler(page)
            
            # Step 3: Handle file uploads
            await self.universal_file_upload(page)
            
            # Step 4: Handle rich text/WYSIWYG editors
            await self.universal_text_editor_handler(page)
            
            # Step 5: Handle dropdowns/selects
            await self.universal_dropdown_handler(page)
            
            # Step 6: Handle checkboxes/radio buttons
            await self.universal_selection_handler(page)
            
            # Step 7: Handle dynamic form elements
            await self.dynamic_form_handler(page)
            
            # Step 8: Submit form intelligently
            return await self.universal_form_submitter(page)
            
        except Exception as e:
            print(f"❌ Universal form handler error: {str(e)}")
            return False
    
    async def nuclear_popup_dismissal(self, page):
        """Nuclear option - dismiss EVERYTHING that could be a popup"""
        dismissal_strategies = [
            # Cookie/GDPR banners
            {'selectors': ['button:has-text("Accept all")', 'button:has-text("Accept")', 'button:has-text("I agree")', 'button:has-text("Allow all")', '#onetrust-accept-btn-handler'], 'action': 'click'},
            
            # Modal/dialog dismissals  
            {'selectors': ['button[aria-label*="close" i]', 'button[aria-label*="dismiss" i]', 'button:has-text("×")', '.modal-close', '[data-dismiss="modal"]'], 'action': 'click'},
            
            # Notification bars
            {'selectors': ['button:has-text("Not now")', 'button:has-text("Later")', 'button:has-text("Skip")', '.notification-close'], 'action': 'click'},
            
            # Overlay removals
            {'selectors': ['.overlay', '.modal-backdrop', '.popup-overlay'], 'action': 'remove'},
            
            # LinkedIn specific
            {'selectors': ['.artdeco-modal__dismiss', 'button[aria-label="Dismiss"]'], 'action': 'click'},
            
            # Generic aggressive dismissal
            {'selectors': ['[role="dialog"] button', '.close-button', '.popup-close'], 'action': 'click'}
        ]
        
        for strategy in dismissal_strategies:
            for selector in strategy['selectors']:
                try:
                    elements = await page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            if strategy['action'] == 'click':
                                await element.click()
                                await page.wait_for_timeout(500)
                            elif strategy['action'] == 'remove':
                                await page.evaluate('(element) => element.remove()', await element.element_handle())
                except:
                    continue
    
    async def universal_field_filler(self, page):
        """Fill ALL possible form fields intelligently"""
        
        # Comprehensive field mapping
        field_mappings = {
            # Personal Information
            'first.*name|given.*name|fname': self.data['first_name'],
            'last.*name|family.*name|surname|lname': self.data['last_name'], 
            'full.*name|name': f"{self.data['first_name']} {self.data['last_name']}",
            'email': self.data['email'],
            'phone|mobile|tel': self.data['phone'],
            'address|street': self.data.get('address', ''),
            'city': self.data.get('city', ''),
            'zip|postal': self.data.get('zip', ''),
            'country': self.data.get('country', ''),
            
            # Professional Information  
            'title|position': self.data.get('current_title', 'Security Engineer'),
            'company': self.data.get('current_company', 'Halodoc Technologies'),
            'experience|years': self.data.get('years_experience', '5'),
            'salary|compensation': self.data.get('salary_expectation', 'Competitive'),
            'start.*date|available': self.data.get('availability', 'Immediately available'),
            'notice': self.data.get('notice_period', '2 weeks'),
            
            # Authorization/Legal
            'authorized|eligible|legal': 'Yes',
            'sponsorship|visa': 'No',
            'background.*check|security.*clearance': 'Yes',
            'relocate|move': 'Yes',
            
            # Additional Questions
            'why.*interested|motivation': 'Passionate about cybersecurity and interested in contributing to your team',
            'strength|skill': 'Penetration testing, cloud security, GDPR compliance',
            'reference': 'Available upon request'
        }
        
        # Get ALL input elements
        all_inputs = await page.locator('input, textarea').all()
        
        for input_elem in all_inputs:
            try:
                if not await input_elem.is_visible() or not await input_elem.is_enabled():
                    continue
                
                # Get element context
                element_id = await input_elem.get_attribute('id') or ''
                element_name = await input_elem.get_attribute('name') or ''
                element_placeholder = await input_elem.get_attribute('placeholder') or ''
                element_aria_label = await input_elem.get_attribute('aria-label') or ''
                element_type = await input_elem.get_attribute('type') or 'text'
                
                context = f"{element_id} {element_name} {element_placeholder} {element_aria_label}".lower()
                
                # Skip if already filled
                current_value = await input_elem.input_value()
                if current_value and len(current_value.strip()) > 0:
                    continue
                
                # Match against field mappings
                for pattern, value in field_mappings.items():
                    import re
                    if re.search(pattern, context, re.IGNORECASE):
                        if element_type in ['text', 'email', 'tel', 'search', 'url']:
                            await input_elem.fill(str(value))
                            print(f"         ✅ Filled {pattern}: {value}")
                        elif element_type == 'number':
                            number_value = re.search(r'\d+', str(value))
                            if number_value:
                                await input_elem.fill(number_value.group())
                                print(f"         ✅ Filled number {pattern}: {number_value.group()}")
                        break
                        
            except:
                continue
    
    async def universal_file_upload(self, page):
        """Universal file upload handler"""
        resume_path = "config/resume.pdf"
        
        # Comprehensive file upload strategies
        upload_strategies = [
            # Direct file inputs
            'input[type="file"]',
            'input[accept*="pdf"]',
            'input[accept*="doc"]',
            
            # Semantic file inputs
            'input[name*="resume" i]',
            'input[name*="cv" i]', 
            'input[aria-label*="resume" i]',
            'input[aria-label*="upload" i]',
            'input[placeholder*="resume" i]',
            
            # Data attribute file inputs
            'input[data-test*="resume"]',
            'input[data-test*="file"]',
            'input[data-testid*="file"]'
        ]
        
        for selector in upload_strategies:
            try:
                file_inputs = await page.locator(selector).all()
                for file_input in file_inputs:
                    if await file_input.is_visible():
                        await file_input.set_input_files(resume_path)
                        print(f"         📄 Resume uploaded via {selector}")
                        await page.wait_for_timeout(2000)
                        return True
            except:
                continue
        
        # Try drag-drop zones
        drop_zone_selectors = [
            '.file-drop-zone',
            '.upload-area', 
            '.drag-drop-area',
            '[data-test*="drop"]',
            '.dropzone'
        ]
        
        for selector in drop_zone_selectors:
            try:
                zones = await page.locator(selector).all()
                for zone in zones:
                    if await zone.is_visible():
                        await zone.hover()
                        print(f"         📄 Found drop zone: {selector}")
                        # Would need additional drag-drop implementation
                        return True
            except:
                continue
                
        return False
    
    async def universal_text_editor_handler(self, page):
        """Handle rich text editors, WYSIWYG, etc."""
        
        cover_letter_content = f"""Dear Hiring Team,

I am {self.data['first_name']} {self.data['last_name']}, writing to express my strong interest in this position.

With {self.data.get('years_experience', '5')} years of experience in cybersecurity, including roles at {self.data.get('current_company', 'leading technology companies')}, I bring comprehensive expertise in:

• Penetration Testing & Vulnerability Assessment
• Cloud Security & API Security  
• GDPR Compliance & ISO 27001
• DevSecOps & Security Architecture

Key achievements include reducing security risks by 25% and achieving Hall of Fame recognition from major technology companies.

I am excited about this opportunity and would welcome the chance to discuss how my skills align with your needs.

Best regards,
{self.data['first_name']} {self.data['last_name']}
{self.data['email']} | {self.data['phone']}"""

        # Rich text editor selectors
        editor_selectors = [
            # Standard textareas
            'textarea',
            'textarea[name*="cover" i]',
            'textarea[name*="message" i]',
            'textarea[placeholder*="cover" i]',
            
            # Rich text editors
            '[contenteditable="true"]',
            '.rich-text-editor',
            '.wysiwyg-editor',
            '.ql-editor',
            '.note-editable',
            '.mce-content-body',
            
            # Framework specific
            '.trix-content',
            '.fr-element',
            '.jodit-wysiwyg'
        ]
        
        for selector in editor_selectors:
            try:
                editors = await page.locator(selector).all()
                for editor in editors:
                    if await editor.is_visible():
                        # Different strategies for different editor types
                        if selector == 'textarea':
                            await editor.fill(cover_letter_content)
                        else:
                            # For rich text editors
                            await editor.click()
                            await page.wait_for_timeout(500)
                            await editor.fill(cover_letter_content)
                            
                        print(f"         💌 Cover letter added to {selector}")
                        return True
            except:
                continue
                
        return False
    
    async def universal_dropdown_handler(self, page):
        """Handle all types of dropdowns intelligently"""
        
        # Selection preferences
        selection_preferences = {
            'experience': ['5', 'senior', 'experienced', '3-5', '5-7', '4-6'],
            'education': ['bachelor', 'master', 'degree', 'university'],
            'authorization': ['yes', 'authorized', 'eligible', 'permitted'],
            'clearance': ['no', 'none', 'not required'],
            'sponsorship': ['no', 'not required', 'not needed'],
            'salary': ['competitive', 'negotiable', 'market rate'],
            'start_date': ['immediately', 'asap', '2 weeks', 'flexible']
        }
        
        # Handle standard selects
        selects = await page.locator('select').all()
        for select in selects:
            try:
                if not await select.is_visible():
                    continue
                
                # Get context
                select_name = (await select.get_attribute('name') or '').lower()
                select_aria = (await select.get_attribute('aria-label') or '').lower() 
                context = f"{select_name} {select_aria}"
                
                options = await select.locator('option').all()
                
                # Smart selection based on context
                selected = False
                for category, preferences in selection_preferences.items():
                    if category in context:
                        for pref in preferences:
                            for option in options:
                                option_text = (await option.text_content() or '').lower()
                                if pref in option_text:
                                    await select.select_option(value=await option.get_attribute('value'))
                                    print(f"         ✅ Selected {category}: {option_text}")
                                    selected = True
                                    break
                            if selected:
                                break
                    if selected:
                        break
                        
            except:
                continue
        
        # Handle custom dropdowns (div-based)
        custom_dropdown_selectors = [
            '.dropdown',
            '.select',
            '[role="combobox"]',
            '[aria-haspopup="listbox"]'
        ]
        
        for selector in custom_dropdown_selectors:
            try:
                dropdowns = await page.locator(selector).all()
                for dropdown in dropdowns:
                    if await dropdown.is_visible():
                        await dropdown.click()
                        await page.wait_for_timeout(1000)
                        
                        # Look for options
                        option_selectors = [
                            '[role="option"]',
                            '.dropdown-item',
                            '.select-option',
                            'li'
                        ]
                        
                        for opt_selector in option_selectors:
                            options = await page.locator(opt_selector).all()
                            if options:
                                # Select first reasonable option
                                for option in options[:3]:
                                    option_text = (await option.text_content() or '').lower()
                                    if any(word in option_text for word in ['yes', 'senior', 'experienced']):
                                        await option.click()
                                        print(f"         ✅ Selected custom dropdown option: {option_text}")
                                        break
                                break
            except:
                continue
    
    async def universal_selection_handler(self, page):
        """Handle checkboxes and radio buttons"""
        
        # Checkbox handling
        checkboxes = await page.locator('input[type="checkbox"]').all()
        for checkbox in checkboxes:
            try:
                if not await checkbox.is_visible():
                    continue
                
                # Get associated label
                checkbox_id = await checkbox.get_attribute('id')
                label_text = ""
                
                if checkbox_id:
                    label = page.locator(f'label[for="{checkbox_id}"]')
                    if await label.count() > 0:
                        label_text = (await label.text_content() or '').lower()
                
                # Smart checkbox selection
                if any(word in label_text for word in [
                    'agree', 'terms', 'privacy', 'consent', 'authorize', 
                    'understand', 'acknowledge', 'accept', 'confirm'
                ]):
                    await checkbox.check()
                    print(f"         ✅ Checked: {label_text[:50]}...")
                    
            except:
                continue
        
        # Radio button handling
        radio_groups = {}
        radios = await page.locator('input[type="radio"]').all()
        
        for radio in radios:
            try:
                radio_name = await radio.get_attribute('name')
                if radio_name:
                    if radio_name not in radio_groups:
                        radio_groups[radio_name] = []
                    radio_groups[radio_name].append(radio)
            except:
                continue
        
        # Select one option per radio group
        for group_name, group_radios in radio_groups.items():
            try:
                for radio in group_radios:
                    radio_value = (await radio.get_attribute('value') or '').lower()
                    if any(word in radio_value for word in ['yes', 'true', 'agree', 'authorized']):
                        await radio.check()
                        print(f"         ✅ Selected radio {group_name}: {radio_value}")
                        break
            except:
                continue
    
    async def dynamic_form_handler(self, page):
        """Handle dynamically loaded form elements"""
        
        # Wait for dynamic content
        await page.wait_for_timeout(2000)
        
        # Re-run field detection for newly loaded elements
        await self.universal_field_filler(page)
        
        # Handle progressive forms (forms that reveal more fields)
        progress_indicators = await page.locator('.progress, .step-indicator, .form-step').all()
        if progress_indicators:
            print("         🔄 Detected multi-step form")
            
            # Look for "Next" buttons that might reveal more fields
            next_buttons = await page.locator('button:has-text("Next"), button:has-text("Continue")').all()
            for next_btn in next_buttons:
                try:
                    if await next_btn.is_visible() and await next_btn.is_enabled():
                        await next_btn.click()
                        await page.wait_for_timeout(3000)
                        
                        # Fill newly revealed fields
                        await self.universal_field_filler(page)
                        break
                except:
                    continue
    
    async def universal_form_submitter(self, page):
        """Intelligently submit any form"""
        
        submit_selectors = [
            # Standard submits
            'button[type="submit"]',
            'input[type="submit"]',
            
            # Text-based submits
            'button:has-text("Submit")',
            'button:has-text("Apply")', 
            'button:has-text("Send")',
            'button:has-text("Continue")',
            'button:has-text("Next")',
            'button:has-text("Finish")',
            'button:has-text("Complete")',
            
            # Aria labels
            'button[aria-label*="submit" i]',
            'button[aria-label*="apply" i]',
            'button[aria-label*="send" i]',
            
            # Classes
            '.submit-button',
            '.apply-button', 
            '.send-button',
            
            # Data attributes
            'button[data-test*="submit"]',
            'button[data-testid*="submit"]'
        ]
        
        for selector in submit_selectors:
            try:
                buttons = await page.locator(selector).all()
                for button in buttons:
                    if await button.is_visible() and await button.is_enabled():
                        button_text = (await button.text_content() or '').strip()
                        print(f"         🎯 Found submit button: {button_text}")
                        
                        # Click submit (or pause for manual review)
                        # Uncomment to actually submit:
                        # await button.click()
                        # await page.wait_for_timeout(5000)
                        
                        print(f"         ⏸️  Ready to submit - review form and click manually")
                        return True
                        
            except:
                continue
                
        return False

# Usage example
candidate_info = {
    'first_name': 'Ankit',
    'last_name': 'Thakur', 
    'email': 'at87.at17@gmail.com',
    'phone': '+91 8717934430',
    'current_title': 'SDET II (Cyber Security)',
    'current_company': 'Halodoc Technologies LLP',
    'years_experience': '5',
    'salary_expectation': 'Competitive based on role and location',
    'availability': 'Immediately available',
    'notice_period': '2 weeks'
}

async def demo_universal_handler():
    """Demo the universal form handler"""
    handler = UniversalFormHandler(candidate_info)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Example: Handle any job application form
        await page.goto('https://example-job-site.com/apply')
        success = await handler.handle_any_form(page, "Example Job Application")
        
        print(f"Form handling result: {'Success' if success else 'Failed'}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(demo_universal_handler())