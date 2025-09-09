#!/usr/bin/env python3
"""
Company Career Portal Scraper with Auto-Application
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json
from datetime import datetime
import re

load_dotenv()

# Major tech and finance companies with security roles
COMPANY_PORTALS = {
    'google': {
        'url': 'https://careers.google.com/jobs/results/',
        'search_params': 'q=security%20engineer',
        'job_selector': '[data-job-id]',
        'title_selector': '[data-test="job-title"]',
        'location_selector': '[data-test="job-location"]',
        'apply_selector': 'button:has-text("Apply")'
    },
    'microsoft': {
        'url': 'https://careers.microsoft.com/professionals/us/en/search-results',
        'search_params': 'keywords=security%20engineer',
        'job_selector': '.jobs-list-item',
        'title_selector': '.job-title',
        'location_selector': '.job-location',
        'apply_selector': '.apply-button'
    },
    'amazon': {
        'url': 'https://www.amazon.jobs/en/search',
        'search_params': 'base_query=security%20engineer',
        'job_selector': '.job-tile',
        'title_selector': '.job-title',
        'location_selector': '.location-and-id',
        'apply_selector': '.apply-button'
    },
    'apple': {
        'url': 'https://jobs.apple.com/en-us/search',
        'search_params': 'search=security%20engineer',
        'job_selector': '[data-job-id]',
        'title_selector': '.job-title',
        'location_selector': '.job-location',
        'apply_selector': '.apply-link'
    },
    'siemens': {
        'url': 'https://jobs.siemens.com/careers/JobSearch',
        'search_params': 'searchText=security%20engineer',
        'job_selector': '.job-item',
        'title_selector': '.job-title',
        'location_selector': '.job-location',
        'apply_selector': '.apply-button'
    },
    'sap': {
        'url': 'https://jobs.sap.com/search/',
        'search_params': 'q=security%20engineer',
        'job_selector': '.job-result-item',
        'title_selector': '.job-title',
        'location_selector': '.job-location',
        'apply_selector': '.apply-btn'
    },
    'deutsche_bank': {
        'url': 'https://careers.db.com/explore-the-bank/careers-search/',
        'search_params': 'q=security%20engineer',
        'job_selector': '.job-item',
        'title_selector': '.job-title',
        'location_selector': '.job-location', 
        'apply_selector': '.apply-button'
    }
}

async def scrape_company_portal(company_name, portal_config):
    """Scrape jobs from a specific company portal"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        jobs = []
        
        try:
            print(f"🏢 Scraping {company_name.upper()} careers...")
            
            # Build search URL
            search_url = f"{portal_config['url']}?{portal_config['search_params']}"
            await page.goto(search_url)
            await page.wait_for_timeout(8000)
            
            # Handle cookie consent
            try:
                cookie_btns = page.locator('button:has-text("Accept"), button:has-text("Agree"), button:has-text("OK")')
                if await cookie_btns.count() > 0:
                    await cookie_btns.first.click()
                    await page.wait_for_timeout(2000)
            except:
                pass
            
            # Find job listings
            job_elements = await page.locator(portal_config['job_selector']).all()
            print(f"   📊 Found {len(job_elements)} jobs")
            
            for i, job_elem in enumerate(job_elements[:8]):  # Process first 8 jobs
                try:
                    # Extract job details
                    title_elem = job_elem.locator(portal_config['title_selector'])
                    location_elem = job_elem.locator(portal_config['location_selector'])
                    
                    title = await get_safe_text(title_elem)
                    location = await get_safe_text(location_elem)
                    
                    if title and any(keyword in title.lower() for keyword in 
                        ['security', 'cyber', 'penetration', 'vulnerability']):
                        
                        # Click to view job details
                        await job_elem.click()
                        await page.wait_for_timeout(4000)
                        
                        # Look for apply button
                        apply_btn = page.locator(portal_config['apply_selector'])
                        
                        job = {
                            'title': title,
                            'company': company_name,
                            'location': location or 'Multiple Locations',
                            'portal_url': page.url,
                            'has_apply_button': await apply_btn.count() > 0,
                            'scraped_at': datetime.now().isoformat(),
                            'source': f'{company_name}_portal'
                        }
                        
                        jobs.append(job)
                        print(f"   ✅ {title} ({location})")
                        
                        # Go back to job list
                        await page.go_back()
                        await page.wait_for_timeout(3000)
                
                except Exception as e:
                    print(f"   ❌ Error processing job {i+1}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Error scraping {company_name}: {str(e)}")
        finally:
            await browser.close()
    
    return jobs

async def get_safe_text(locator):
    """Safely extract text from locator"""
    try:
        if await locator.count() > 0:
            return (await locator.first.text_content()).strip()
    except:
        pass
    return ""

async def auto_fill_application(page, job_title, company):
    """Auto-fill job application forms"""
    try:
        print(f"     📝 Auto-filling application for {job_title} @ {company}")
        
        # Common form fields
        form_fields = {
            'firstName': 'Ankit',
            'first_name': 'Ankit',
            'lastname': 'Thakur',
            'last_name': 'Thakur',
            'email': 'at87.at17@gmail.com',
            'phone': '+91 8717934430',
            'phoneNumber': '+91 8717934430'
        }
        
        # Fill text inputs
        for field_name, value in form_fields.items():
            inputs = page.locator(f'input[name="{field_name}"], input[id="{field_name}"]')
            if await inputs.count() > 0:
                await inputs.first.fill(value)
                print(f"       ✅ Filled {field_name}")
        
        # Resume upload
        file_inputs = page.locator('input[type="file"]')
        if await file_inputs.count() > 0:
            resume_path = os.path.abspath("config/resume.pdf")
            if os.path.exists(resume_path):
                await file_inputs.first.set_input_files(resume_path)
                print("       📄 Resume uploaded")
        
        # Cover letter
        text_areas = page.locator('textarea')
        if await text_areas.count() > 0:
            cover_letter = f"""Dear {company} Team,

I am Ankit Thakur, writing to express my interest in the {job_title} position. 

With over 5 years of experience in cybersecurity at companies like Halodoc Technologies and Prescient Security LLC, I bring expertise in:

• Penetration Testing & Vulnerability Assessment
• API Security & Cloud Security (AWS certified)  
• GDPR Compliance & ISO 27001 implementation
• DevSecOps & Security Architecture

Key achievements include reducing security risks by 25% for enterprise clients and achieving Hall of Fame recognition from Google, Facebook, and Yahoo for responsible disclosure.

I am excited about the opportunity to contribute to {company}'s security initiatives and would welcome the chance to discuss how my skills align with your team's needs.

Best regards,
Ankit Thakur
at87.at17@gmail.com | +91 8717934430"""

            await text_areas.first.fill(cover_letter)
            print("       💌 Cover letter added")
        
        # Handle dropdowns
        selects = page.locator('select')
        if await selects.count() > 0:
            for select in await selects.all():
                try:
                    options = await select.locator('option').all()
                    # Select experienced/senior level options
                    for option in options:
                        text = await option.text_content() 
                        if text and any(word in text.lower() for word in ['5', 'senior', 'experienced']):
                            await select.select_option(value=await option.get_attribute('value'))
                            print(f"       ✅ Selected: {text}")
                            break
                except:
                    continue
        
        return True
        
    except Exception as e:
        print(f"     ❌ Auto-fill error: {str(e)}")
        return False

async def apply_to_company_jobs():
    """Apply to jobs across all company portals"""
    
    all_jobs = []
    applications = []
    
    for company_name, portal_config in COMPANY_PORTALS.items():
        print(f"\n🎯 Processing {company_name.upper()}...")
        
        jobs = await scrape_company_portal(company_name, portal_config)
        all_jobs.extend(jobs)
        
        # Apply to jobs with apply buttons
        applicable_jobs = [job for job in jobs if job.get('has_apply_button', False)]
        
        if applicable_jobs:
            print(f"   ⚡ Found {len(applicable_jobs)} jobs with apply buttons")
            
            # Apply to first 3 jobs per company
            for job in applicable_jobs[:3]:
                try:
                    print(f"   🚀 Applying to: {job['title']}")
                    
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=False)
                        page = await browser.new_page()
                        
                        await page.goto(job['portal_url'])
                        await page.wait_for_timeout(5000)
                        
                        # Click apply button
                        apply_btn = page.locator('button:has-text("Apply"), .apply-button, .apply-link')
                        if await apply_btn.count() > 0:
                            await apply_btn.first.click()
                            await page.wait_for_timeout(5000)
                            
                            # Auto-fill application
                            success = await auto_fill_application(page, job['title'], company_name)
                            
                            if success:
                                # Look for submit button (but don't click for safety)
                                submit_btn = page.locator('button:has-text("Submit"), input[type="submit"]')
                                if await submit_btn.count() > 0:
                                    print(f"   ✅ Application form ready for {job['title']}")
                                    print(f"   ⏸️  Pausing for manual review/submission...")
                                    
                                    applications.append({
                                        'title': job['title'],
                                        'company': company_name,
                                        'location': job['location'],
                                        'status': 'form_filled',
                                        'url': job['portal_url'],
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    
                                    # Wait for manual review
                                    await page.wait_for_timeout(15000)
                        
                        await browser.close()
                
                except Exception as e:
                    print(f"   ❌ Error applying to {job['title']}: {str(e)}")
                    continue
        
        await asyncio.sleep(5)  # Delay between companies
    
    return all_jobs, applications

async def main():
    """Main company portal automation"""
    print("🏢 COMPANY CAREER PORTAL SCRAPER & AUTO-APPLY")
    print("🎯 Target: Major tech and finance companies")
    print("⚡ Method: Automated form filling")
    print("="*60)
    
    all_jobs, applications = await apply_to_company_jobs()
    
    print(f"\n📊 FINAL RESULTS")
    print("="*30)
    print(f"🔍 Total Jobs Found: {len(all_jobs)}")
    print(f"📝 Applications Prepared: {len(applications)}")
    
    # Save results
    with open('dashboard/company_portal_jobs.json', 'w') as f:
        json.dump(all_jobs, f, indent=2)
    
    with open('dashboard/company_applications.json', 'w') as f:
        json.dump(applications, f, indent=2)
    
    if applications:
        print(f"\n✅ APPLICATIONS PREPARED:")
        for app in applications:
            print(f"   • {app['title']} @ {app['company']}")
    
    print(f"\n💾 Results saved to dashboard/")
    print(f"🎉 Company portal automation complete!")

if __name__ == "__main__":
    asyncio.run(main())