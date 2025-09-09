#!/usr/bin/env python3
"""
Simple Easy Apply Demo - Step by Step Process
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def demo_easy_apply():
    """Demonstrate Easy Apply step by step"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🔐 Step 1: Logging into LinkedIn...")
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_timeout(2000)
            
            await page.fill('input#username', email)
            await page.fill('input#password', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(8000)
            
            print("✅ Login successful!")
            
            print("\n🔍 Step 2: Searching for a specific Easy Apply job...")
            # Go to a known Easy Apply job (example URL - replace with actual)
            await page.goto('https://www.linkedin.com/jobs/search/?f_E=2%2C3%2C4&f_AL=true&keywords=security%20engineer&location=Germany')
            await page.wait_for_timeout(5000)
            
            print("📊 Finding Easy Apply jobs...")
            
            # Wait for job listings to load
            await page.wait_for_selector('[data-job-id]', timeout=10000)
            
            # Click on the first job
            first_job = page.locator('[data-job-id]').first
            await first_job.click()
            await page.wait_for_timeout(3000)
            
            # Get job details
            job_title = await page.locator('.job-details-jobs-unified-top-card__job-title h1').text_content()
            company = await page.locator('.job-details-jobs-unified-top-card__company-name a').text_content()
            
            print(f"💼 Found job: {job_title} @ {company}")
            
            print("\n⚡ Step 3: Looking for Easy Apply button...")
            easy_apply_button = page.locator('button[aria-label*="Easy Apply to"]')
            
            if await easy_apply_button.count() > 0:
                print("✅ Easy Apply button found!")
                
                print("\n🚀 Step 4: Starting Easy Apply process...")
                await easy_apply_button.click()
                await page.wait_for_timeout(3000)
                
                print("📝 Step 5: Filling application form...")
                
                # Fill phone number
                phone_input = page.locator('input[id*="phoneNumber"]')
                if await phone_input.count() > 0:
                    await phone_input.fill("+91 8717934430")
                    print("   📱 Phone number: ✅")
                
                # Upload resume
                file_input = page.locator('input[type="file"]')
                if await file_input.count() > 0:
                    resume_path = os.path.abspath("config/resume.pdf")
                    if os.path.exists(resume_path):
                        await file_input.set_input_files(resume_path)
                        print("   📄 Resume upload: ✅")
                        await page.wait_for_timeout(3000)
                
                print("\n🔄 Step 6: Progressing through application steps...")
                
                # Handle multiple steps
                for step in range(1, 4):
                    print(f"   Processing step {step}...")
                    
                    # Look for continue/next button
                    continue_button = page.locator('button[aria-label*="Continue"], button:has-text("Next")')
                    
                    if await continue_button.count() > 0:
                        await continue_button.click()
                        await page.wait_for_timeout(3000)
                        print(f"   Step {step}: ✅")
                    else:
                        break
                
                print("\n🎯 Step 7: Looking for submit button...")
                submit_button = page.locator('button[aria-label*="Submit application"]')
                
                if await submit_button.count() > 0:
                    print("✅ Submit button found!")
                    print("\n⚠️  PAUSING - Would you like me to actually submit? (Manual decision)")
                    print("   This would complete a real job application to:", job_title, "@", company)
                    
                    # Wait for manual decision (comment out the next line to auto-submit)
                    await page.wait_for_timeout(10000)
                    
                    # Uncomment to actually submit:
                    # await submit_button.click()
                    # await page.wait_for_timeout(5000)
                    # print("🎉 Application submitted successfully!")
                    
                else:
                    print("⚠️ Submit button not found - application may need additional steps")
            else:
                print("❌ No Easy Apply button found on this job")
            
            print(f"\n📊 Demo completed!")
            print("🔍 Check the browser window to see the current state")
            
            # Keep browser open for inspection
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🎯 LINKEDIN EASY APPLY DEMO")
    print("📋 This will demonstrate the Easy Apply process step by step")
    print("⚠️  Note: Will pause before actually submitting applications")
    print("="*70)
    
    asyncio.run(demo_easy_apply())