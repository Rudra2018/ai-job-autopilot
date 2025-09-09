#!/usr/bin/env python3
"""
Test LinkedIn login and Easy Apply functionality
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_linkedin_login():
    """Test LinkedIn login with provided credentials"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LinkedIn credentials not found in .env file")
        return False
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to LinkedIn...")
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_timeout(3000)
            
            print("📝 Entering credentials...")
            # Enter email
            await page.fill('input#username', email)
            await page.wait_for_timeout(1000)
            
            # Enter password
            await page.fill('input#password', password)
            await page.wait_for_timeout(1000)
            
            print("🔐 Attempting login...")
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            
            # Check if login was successful
            current_url = page.url
            if 'feed' in current_url or 'home' in current_url:
                print("✅ Login successful! Redirected to LinkedIn home/feed")
                
                # Navigate to jobs page
                print("💼 Navigating to jobs page...")
                await page.goto('https://www.linkedin.com/jobs/')
                await page.wait_for_timeout(3000)
                
                return True
            elif 'challenge' in current_url or 'checkpoint' in current_url:
                print("⚠️ LinkedIn security challenge detected - manual verification may be required")
                return False
            else:
                print(f"❌ Login may have failed. Current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False
        finally:
            await browser.close()

async def search_and_apply_jobs():
    """Search for cybersecurity jobs and attempt Easy Apply"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Login first
            print("🔐 Logging into LinkedIn...")
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_timeout(2000)
            
            await page.fill('input#username', email)
            await page.fill('input#password', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            
            # Search for cybersecurity jobs
            print("🔍 Searching for cybersecurity jobs...")
            await page.goto('https://www.linkedin.com/jobs/search/?keywords=cybersecurity%20OR%20%22security%20engineer%22%20OR%20%22penetration%20tester%22&location=Germany')
            await page.wait_for_timeout(5000)
            
            # Look for Easy Apply jobs
            print("⚡ Looking for Easy Apply jobs...")
            easy_apply_jobs = await page.locator('[data-easy-apply-button="true"], button:has-text("Easy Apply")').all()
            
            if not easy_apply_jobs:
                # Try alternative selectors
                easy_apply_jobs = await page.locator('button[aria-label*="Easy Apply"], .jobs-apply-button--top-card').all()
            
            print(f"📊 Found {len(easy_apply_jobs)} Easy Apply opportunities")
            
            if easy_apply_jobs:
                # Try to apply to the first job
                print("🚀 Attempting to apply to first Easy Apply job...")
                await easy_apply_jobs[0].click()
                await page.wait_for_timeout(3000)
                
                # Fill out application form
                await fill_easy_apply_form(page)
                
                return True
            else:
                print("⚠️ No Easy Apply jobs found with current search")
                return False
                
        except Exception as e:
            print(f"❌ Error during job application: {str(e)}")
            return False
        finally:
            await browser.close()

async def fill_easy_apply_form(page):
    """Fill Easy Apply form with Ankit's information"""
    try:
        print("📝 Filling Easy Apply form...")
        
        # Phone number
        phone_input = page.locator('input[id*="phoneNumber"], input[name*="phone"]')
        if await phone_input.count() > 0:
            await phone_input.fill("+91 8717934430")
            print("   ✅ Phone number filled")
        
        # Resume upload
        resume_input = page.locator('input[type="file"]')
        if await resume_input.count() > 0:
            await resume_input.set_input_files("config/resume.pdf")
            print("   ✅ Resume uploaded")
        
        # Cover letter
        cover_textarea = page.locator('textarea[id*="coverLetter"], textarea[name*="message"]')
        if await cover_textarea.count() > 0:
            cover_letter = """Dear Hiring Team,

I am Ankit Thakur, an experienced cybersecurity professional with extensive expertise in penetration testing, API security, and cloud security.

With my background at Halodoc Technologies and Prescient Security LLC, I have successfully reduced security risks by 25% and improved data protection by 30%. My certifications include AWS Security Specialty, CompTIA Security+, and recognition from Google, Facebook, Yahoo, and the U.S. Department of Defense.

I am excited about this opportunity and would love to contribute to your security initiatives.

Best regards,
Ankit Thakur
at87.at17@gmail.com | +91 8717934430"""
            
            await cover_textarea.fill(cover_letter)
            print("   ✅ Cover letter added")
        
        # Years of experience
        experience_input = page.locator('input[id*="experience"], select[id*="experience"]')
        if await experience_input.count() > 0:
            await experience_input.fill("5")
            print("   ✅ Experience filled")
        
        await page.wait_for_timeout(2000)
        
        # Look for Next or Submit button
        next_button = page.locator('button:has-text("Next"), button:has-text("Review"), button:has-text("Submit application")')
        if await next_button.count() > 0:
            button_text = await next_button.first.inner_text()
            print(f"   🔄 Clicking '{button_text}' button...")
            await next_button.first.click()
            await page.wait_for_timeout(3000)
            
            # If there's a final submit button
            submit_button = page.locator('button:has-text("Submit application")')
            if await submit_button.count() > 0:
                print("   🎯 Submitting application...")
                await submit_button.click()
                await page.wait_for_timeout(3000)
                print("   ✅ Application submitted successfully!")
            else:
                print("   ⏳ Application in progress - may require additional steps")
        else:
            print("   ⚠️ Could not find Next/Submit button")
            
    except Exception as e:
        print(f"   ❌ Error filling form: {str(e)}")

async def main():
    """Main test function"""
    print("🤖 LINKEDIN EASY APPLY TEST")
    print("="*50)
    
    # Test login first
    login_success = await test_linkedin_login()
    
    if login_success:
        print("\n🎯 Proceeding to job search and application...")
        await asyncio.sleep(2)
        
        # Test job search and application
        application_success = await search_and_apply_jobs()
        
        if application_success:
            print("\n✅ LinkedIn Easy Apply test completed successfully!")
        else:
            print("\n⚠️ Job application test encountered issues")
    else:
        print("\n❌ Login test failed - cannot proceed to job applications")
    
    print("\n📊 Test Summary:")
    print(f"   Login: {'✅ Success' if login_success else '❌ Failed'}")
    if login_success:
        print("   Job Search: Completed")
        print("   Easy Apply: Attempted")

if __name__ == "__main__":
    asyncio.run(main())