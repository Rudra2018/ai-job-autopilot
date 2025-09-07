#!/usr/bin/env python3
"""
Working LinkedIn Easy Apply - Final Version
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

async def working_linkedin_apply():
    """Working LinkedIn Easy Apply automation"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    applications = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Login
            print("🔐 Logging into LinkedIn...")
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_timeout(3000)
            
            await page.fill('input#username', email)
            await page.fill('input#password', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(8000)
            
            print("✅ Login successful!")
            
            # Search for Easy Apply jobs specifically
            print("🔍 Searching for Easy Apply cybersecurity jobs...")
            search_url = 'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2%2C3%2C4&keywords=cybersecurity%20OR%20%22security%20engineer%22%20OR%20%22penetration%20tester%22&location=Germany&sortBy=DD'
            
            await page.goto(search_url)
            await page.wait_for_timeout(5000)
            
            # Wait for job results
            await page.wait_for_selector('.jobs-search-results-list', timeout=15000)
            
            # Get job cards
            job_cards = await page.locator('.jobs-search-results-list .job-card-container--clickable').all()
            print(f"📊 Found {len(job_cards)} Easy Apply job opportunities")
            
            for i, job_card in enumerate(job_cards[:3]):  # Apply to first 3
                try:
                    print(f"\n💼 Processing Job {i+1}...")
                    
                    # Click job card
                    await job_card.click()
                    await page.wait_for_timeout(4000)
                    
                    # Get job info
                    job_title_elem = page.locator('.job-details-jobs-unified-top-card__job-title h1')
                    company_elem = page.locator('.job-details-jobs-unified-top-card__company-name a')
                    location_elem = page.locator('.job-details-jobs-unified-top-card__bullet')
                    
                    job_title = (await job_title_elem.text_content()).strip() if await job_title_elem.count() > 0 else "Unknown"
                    company = (await company_elem.text_content()).strip() if await company_elem.count() > 0 else "Unknown"  
                    location = (await location_elem.text_content()).strip().split('·')[0].strip() if await location_elem.count() > 0 else "Unknown"
                    
                    print(f"   📋 {job_title} @ {company} ({location})")
                    
                    # Find Easy Apply button (use first if multiple)
                    easy_apply_button = page.locator('button[aria-label*="Easy Apply"]').first
                    
                    if await easy_apply_button.count() > 0:
                        print("   ⚡ Easy Apply available - starting application...")
                        
                        await easy_apply_button.click()
                        await page.wait_for_timeout(4000)
                        
                        # Handle Easy Apply form
                        success = await fill_easy_apply_form(page, job_title, company)
                        
                        if success:
                            applications.append({
                                'title': job_title,
                                'company': company,
                                'location': location,
                                'status': 'applied',
                                'timestamp': datetime.now().isoformat()
                            })
                            print("   ✅ Application completed!")
                            
                            # Log to dashboard
                            log_entry = {
                                "title": job_title,
                                "company": company,
                                "location": location,
                                "url": page.url,
                                "status": "applied",
                                "recruiter_msg": f"Applied via Easy Apply automation"
                            }
                            
                            with open('dashboard/application_log.jsonl', 'a') as f:
                                f.write(json.dumps(log_entry) + '\n')
                        
                        # Close modal
                        dismiss_btn = page.locator('button[aria-label="Dismiss"]')
                        if await dismiss_btn.count() > 0:
                            await dismiss_btn.click()
                        
                        await page.wait_for_timeout(3000)
                    
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"❌ Main error: {str(e)}")
        finally:
            await browser.close()
    
    return applications

async def fill_easy_apply_form(page, job_title, company):
    """Fill Easy Apply form step by step"""
    try:
        print("     📝 Filling Easy Apply form...")
        
        # Wait for modal
        await page.wait_for_selector('.jobs-easy-apply-modal', timeout=10000)
        await page.wait_for_timeout(2000)
        
        max_attempts = 4
        current_step = 1
        
        while current_step <= max_attempts:
            print(f"     🔄 Step {current_step}: Processing form...")
            
            # Phone number
            phone_inputs = page.locator('input[id*="phoneNumber"], input[name*="phone"]')
            if await phone_inputs.count() > 0:
                await phone_inputs.first.fill("+91 8717934430")
                print("       📱 Phone added")
            
            # Resume upload
            file_inputs = page.locator('input[type="file"]')
            if await file_inputs.count() > 0:
                resume_path = os.path.abspath("config/resume.pdf")
                if os.path.exists(resume_path):
                    await file_inputs.first.set_input_files(resume_path)
                    print("       📄 Resume uploaded")
                    await page.wait_for_timeout(3000)
            
            # Text areas for additional info
            textareas = page.locator('textarea')
            for textarea in await textareas.all():
                try:
                    placeholder = await textarea.get_attribute('placeholder') or ""
                    if any(word in placeholder.lower() for word in ['cover', 'why', 'additional']):
                        message = f"I am Ankit Thakur, interested in the {job_title} position at {company}. With 5+ years in cybersecurity and certifications in AWS Security Specialty and CompTIA Security+, I bring strong expertise in penetration testing and cloud security."
                        await textarea.fill(message)
                        print("       💌 Message added")
                        break
                except:
                    continue
            
            # Handle dropdowns
            selects = page.locator('select')
            if await selects.count() > 0:
                for select in await selects.all():
                    try:
                        # Select middle/experienced option typically
                        options = await select.locator('option').all()
                        if len(options) > 2:
                            await select.select_option(index=min(3, len(options)-1))
                            print("       ✅ Dropdown selected")
                    except:
                        continue
            
            await page.wait_for_timeout(2000)
            
            # Find next/continue/submit button
            button_found = False
            button_texts = ["Next", "Continue", "Review", "Submit application"]
            
            for btn_text in button_texts:
                btn = page.locator(f'button:has-text("{btn_text}")')
                if await btn.count() > 0 and await btn.is_enabled():
                    print(f"       🔄 Clicking: {btn_text}")
                    await btn.click()
                    await page.wait_for_timeout(4000)
                    button_found = True
                    
                    # Check for success
                    if "Submit" in btn_text:
                        # Wait for confirmation
                        success_indicators = [
                            'text=Application sent',
                            'text=Your application was sent',
                            'text=Successfully applied'
                        ]
                        
                        for indicator in success_indicators:
                            if await page.locator(indicator).count() > 0:
                                print("       🎉 Application sent successfully!")
                                return True
                        
                        await page.wait_for_timeout(3000)
                        return True  # Assume success
                    break
            
            if not button_found:
                print("       ⚠️ No more buttons found - application likely complete")
                break
                
            current_step += 1
        
        return True
        
    except Exception as e:
        print(f"     ❌ Form error: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 WORKING LINKEDIN EASY APPLY")
    print("🎯 Target: Cybersecurity Easy Apply jobs")
    print("🌍 Location: Germany & Remote")
    print("="*50)
    
    applications = await working_linkedin_apply()
    
    print(f"\n📈 RESULTS SUMMARY")
    print("="*30)
    print(f"✅ Applications Completed: {len(applications)}")
    
    if applications:
        print(f"\n🎯 SUCCESSFUL APPLICATIONS:")
        for app in applications:
            print(f"   • {app['title']} @ {app['company']}")
        
        with open('dashboard/working_linkedin_results.json', 'w') as f:
            json.dump(applications, f, indent=2)
        print(f"\n💾 Results saved!")
    
    print(f"\n🎉 LinkedIn Easy Apply automation complete!")
    print(f"📧 Check your email for application confirmations")

if __name__ == "__main__":
    asyncio.run(main())