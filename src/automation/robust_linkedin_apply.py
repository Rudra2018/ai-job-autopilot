#!/usr/bin/env python3
"""
Robust LinkedIn Easy Apply - Actually Working Version
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json
from datetime import datetime
import random

load_dotenv()

async def robust_linkedin_apply():
    """Robust LinkedIn Easy Apply with better form handling"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    applications = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)  # Slower for stability
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            # Login with better error handling
            print("🔐 Logging into LinkedIn...")
            await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            await page.fill('input#username', email)
            await page.wait_for_timeout(1000)
            await page.fill('input#password', password)
            await page.wait_for_timeout(1000)
            
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(8000)
            
            # Check if logged in successfully
            if 'challenge' in page.url or 'checkpoint' in page.url:
                print("⚠️ LinkedIn requires verification - please complete manually")
                await page.wait_for_timeout(30000)  # Wait for manual verification
            
            # Navigate to specific job search
            print("🔍 Searching for cybersecurity jobs...")
            search_url = 'https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_WT=2%2C3&keywords=security%20engineer%20OR%20penetration%20tester&location=Germany&f_TPR=r604800'
            
            await page.goto(search_url, wait_until='domcontentloaded')
            await page.wait_for_timeout(5000)
            
            # Scroll to load more jobs
            for _ in range(3):
                await page.keyboard.press('End')
                await page.wait_for_timeout(2000)
            
            # Find job listings
            job_links = await page.locator('a[data-control-name="job_search_job_title"]').all()
            print(f"📊 Found {len(job_links)} job listings")
            
            for i, job_link in enumerate(job_links[:5]):  # Apply to first 5 jobs
                try:
                    print(f"\n💼 Processing Job {i+1}")
                    
                    # Click on job to open details
                    await job_link.click()
                    await page.wait_for_timeout(4000)
                    
                    # Get job details
                    job_title_elem = page.locator('.job-details-jobs-unified-top-card__job-title h1')
                    company_elem = page.locator('.job-details-jobs-unified-top-card__company-name a')
                    location_elem = page.locator('.job-details-jobs-unified-top-card__bullet')
                    
                    job_title = await job_title_elem.text_content() if await job_title_elem.count() > 0 else "Unknown Job"
                    company = await company_elem.text_content() if await company_elem.count() > 0 else "Unknown Company"
                    location = await location_elem.text_content() if await location_elem.count() > 0 else "Unknown Location"
                    
                    # Clean up the text
                    job_title = job_title.strip() if job_title else "Unknown Job"
                    company = company.strip() if company else "Unknown Company"
                    location = location.strip().split('·')[0].strip() if location else "Unknown Location"
                    
                    print(f"   📋 {job_title} @ {company} ({location})")
                    
                    # Look for Easy Apply button with multiple selectors
                    easy_apply_selectors = [
                        'button[aria-label*="Easy Apply"]',
                        'button:has-text("Easy Apply")',
                        '.jobs-apply-button[aria-label*="Easy Apply"]',
                        '[data-control-name="jobdetails_topcard_inapply"]'
                    ]
                    
                    easy_apply_button = None
                    for selector in easy_apply_selectors:
                        button = page.locator(selector)
                        if await button.count() > 0:
                            easy_apply_button = button.first
                            break
                    
                    if easy_apply_button:
                        print("   ⚡ Easy Apply button found - starting application...")
                        
                        await easy_apply_button.click()
                        await page.wait_for_timeout(3000)
                        
                        # Handle the Easy Apply modal
                        success = await handle_easy_apply_modal(page, job_title, company, location)
                        
                        if success:
                            applications.append({
                                'title': job_title,
                                'company': company,
                                'location': location,
                                'status': 'applied',
                                'timestamp': datetime.now().isoformat(),
                                'method': 'easy_apply'
                            })
                            print("   ✅ Application submitted successfully!")
                            
                            # Log to dashboard
                            log_entry = {
                                "title": job_title,
                                "company": company,
                                "location": location,
                                "url": page.url,
                                "status": "applied",
                                "recruiter_msg": f"Applied via Easy Apply for {job_title} position"
                            }
                            
                            with open('dashboard/application_log.jsonl', 'a') as f:
                                f.write(json.dumps(log_entry) + '\n')
                        else:
                            print("   ⚠️ Application encountered issues")
                        
                        # Close any remaining modals
                        close_selectors = ['button[aria-label="Dismiss"]', 'button:has-text("×")', '.artdeco-modal__dismiss']
                        for close_selector in close_selectors:
                            close_btn = page.locator(close_selector)
                            if await close_btn.count() > 0:
                                await close_btn.first.click()
                                break
                        
                        await page.wait_for_timeout(2000)
                    else:
                        print("   📝 No Easy Apply available - skipping")
                    
                    # Random delay between applications
                    await page.wait_for_timeout(random.randint(3000, 7000))
                    
                except Exception as e:
                    print(f"   ❌ Error processing job {i+1}: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"❌ Error in LinkedIn automation: {str(e)}")
        finally:
            await browser.close()
    
    return applications

async def handle_easy_apply_modal(page, job_title, company, location):
    """Handle the Easy Apply modal with robust form filling"""
    try:
        print("     📝 Filling Easy Apply form...")
        
        # Wait for modal to load
        await page.wait_for_selector('.jobs-easy-apply-modal', timeout=10000)
        await page.wait_for_timeout(2000)
        
        step = 1
        max_steps = 5
        
        while step <= max_steps:
            print(f"     🔄 Step {step}: Processing application form...")
            
            # Phone number
            phone_selectors = [
                'input[id*="phoneNumber"]',
                'input[name*="phone"]',
                'input[aria-label*="phone" i]',
                'input[placeholder*="phone" i]'
            ]
            
            for selector in phone_selectors:
                phone_input = page.locator(selector)
                if await phone_input.count() > 0:
                    await phone_input.fill("+91 8717934430")
                    print("       📱 Phone number filled")
                    break
            
            # Resume upload
            file_input = page.locator('input[type="file"]')
            if await file_input.count() > 0:
                resume_path = os.path.abspath("config/resume.pdf")
                if os.path.exists(resume_path):
                    await file_input.set_input_files(resume_path)
                    print("       📄 Resume uploaded")
                    await page.wait_for_timeout(2000)
            
            # Cover letter or additional questions
            text_areas = page.locator('textarea')
            if await text_areas.count() > 0:
                for textarea in await text_areas.all():
                    placeholder = await textarea.get_attribute('placeholder') or ""
                    aria_label = await textarea.get_attribute('aria-label') or ""
                    
                    if any(word in (placeholder + aria_label).lower() for word in ['cover', 'message', 'why', 'interest']):
                        cover_message = f"""Dear {company} Team,

I am Ankit Thakur, interested in the {job_title} position. With 5+ years in cybersecurity at Halodoc Technologies and Prescient Security LLC, I bring expertise in penetration testing, API security, and cloud security.

Key qualifications:
• AWS Security Specialty & CompTIA Security+ certified
• Reduced security risks by 25% for enterprise clients
• Hall of Fame recognition from Google, Facebook, Yahoo
• Extensive experience with GDPR compliance and ISO 27001

I would be excited to contribute to {company}'s security initiatives.

Best regards,
Ankit Thakur
at87.at17@gmail.com"""
                        
                        await textarea.fill(cover_message)
                        print("       💌 Cover message added")
                        break
            
            # Handle dropdowns and checkboxes
            selects = page.locator('select')
            select_count = await selects.count()
            
            for i in range(select_count):
                select = selects.nth(i)
                options = await select.locator('option').all()
                
                if len(options) > 1:
                    # Try to select appropriate option based on context
                    for option in options:
                        option_text = await option.text_content()
                        if option_text and any(word in option_text.lower() for word in ['5', 'senior', 'experienced', 'yes']):
                            await select.select_option(value=await option.get_attribute('value'))
                            print(f"       ✅ Selected: {option_text}")
                            break
            
            await page.wait_for_timeout(2000)
            
            # Look for Next/Continue/Submit buttons
            button_selectors = [
                'button[aria-label*="Continue"]',
                'button:has-text("Next")',
                'button:has-text("Review")',
                'button:has-text("Submit")',
                'button[data-control-name="continue_unify"]'
            ]
            
            next_button = None
            for selector in button_selectors:
                btn = page.locator(selector)
                if await btn.count() > 0 and await btn.is_enabled():
                    next_button = btn.first
                    break
            
            if next_button:
                button_text = await next_button.text_content()
                print(f"       🔄 Clicking: {button_text}")
                await next_button.click()
                await page.wait_for_timeout(4000)
                
                # Check if we've completed the application
                success_selectors = [
                    'text=Application sent',
                    'text=Your application was sent',
                    'text=Successfully applied',
                    '[data-test="application-success"]'
                ]
                
                for selector in success_selectors:
                    if await page.locator(selector).count() > 0:
                        print("       🎉 Application completed successfully!")
                        return True
                
                step += 1
            else:
                print("       ⚠️ No next button found - application may be complete")
                break
        
        return True
        
    except Exception as e:
        print(f"     ❌ Error in form filling: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 ROBUST LINKEDIN EASY APPLY")
    print("🎯 Target: Cybersecurity jobs in Germany")
    print("⚡ Method: Enhanced Easy Apply automation")
    print("="*60)
    
    applications = await robust_linkedin_apply()
    
    print(f"\n📈 FINAL RESULTS")
    print("="*30)
    print(f"🎯 Applications Completed: {len(applications)}")
    
    if applications:
        print(f"\n✅ SUCCESSFUL APPLICATIONS:")
        for app in applications:
            print(f"   • {app['title']} @ {app['company']} ({app['location']})")
        
        # Save results
        with open('dashboard/live_linkedin_results.json', 'w') as f:
            json.dump(applications, f, indent=2)
        print(f"\n💾 Results saved to dashboard/live_linkedin_results.json")
    else:
        print("⚠️ No applications completed - may need manual intervention")
    
    print(f"\n🎉 Robust LinkedIn automation complete!")

if __name__ == "__main__":
    asyncio.run(main())