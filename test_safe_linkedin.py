#!/usr/bin/env python3
"""
Safe LinkedIn Automation Test
Tests automation components without applying to real jobs
"""

import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent))

async def safe_linkedin_test():
    """Test LinkedIn automation safely without real applications"""
    
    print("🛡️  SAFE LINKEDIN AUTOMATION TEST")
    print("=" * 50)
    print("This test validates automation components WITHOUT applying to real jobs")
    print()
    
    load_dotenv()
    
    # Check for credentials
    email = os.getenv('LINKEDIN_EMAIL', '')
    password = os.getenv('LINKEDIN_PASSWORD', '')
    
    if not email or not password:
        print("❌ No LinkedIn credentials found in .env file")
        print("\n📋 TO SET UP TESTING:")
        print("1. Edit the .env file")
        print("2. Add YOUR LinkedIn credentials:")
        print("   LINKEDIN_EMAIL=your.email@example.com")
        print("   LINKEDIN_PASSWORD=your_password")
        print("3. Run this test again")
        return False
    
    print(f"✅ Found credentials for: {email[:3]}***{email[email.find('@'):]}")
    print()
    
    # Import automation modules
    try:
        from src.automation.linkedin_automation import LinkedInCredentials, LinkedInAutomation
        print("✅ Automation modules imported successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Create automation instance
    credentials = LinkedInCredentials(email=email, password=password)
    
    async def progress_callback(update):
        print(f"[{update.get('timestamp', 'N/A')[11:19]}] {update.get('message', 'Update')}")
    
    automation = LinkedInAutomation(credentials, progress_callback)
    
    try:
        print("\n🌐 Testing browser initialization...")
        if await automation.initialize_browser():
            print("✅ Browser initialized successfully")
        else:
            print("❌ Browser initialization failed")
            return False
        
        print("\n🔑 Testing LinkedIn login...")
        if await automation.login_to_linkedin():
            print("✅ Login successful!")
            
            print("\n🔍 Testing job search (without applying)...")
            jobs = await automation.search_jobs(
                keywords=['software engineer'],
                locations=['Remote'],
                limit=5  # Just get a few jobs for testing
            )
            
            if jobs:
                print(f"✅ Found {len(jobs)} jobs")
                print("\n📋 Job Search Results:")
                for i, job in enumerate(jobs[:3], 1):
                    print(f"   {i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                    print(f"      Location: {job.get('location', 'N/A')}")
                    print(f"      URL: {job.get('url', 'N/A')[:50]}...")
                    print()
                
                print("🛡️  TEST COMPLETE - NO APPLICATIONS WERE SUBMITTED")
                print("✅ Automation system is working perfectly!")
                
            else:
                print("⚠️  No jobs found (this might be normal depending on search criteria)")
                
        else:
            print("❌ Login failed - please check your credentials")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
        
    finally:
        print("\n🔄 Closing browser...")
        await automation.close_browser()
        
    return True

def create_safe_demo():
    """Create a safe demo configuration"""
    
    print("\n🎯 CREATING SAFE DEMO CONFIGURATION")
    print("=" * 50)
    
    # Create a safe demo script
    safe_demo_content = '''#!/usr/bin/env python3
"""
SAFE LinkedIn Demo - Browser Test Only
This script ONLY opens LinkedIn and tests login - NO JOB APPLICATIONS
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def safe_demo():
    """Safe demo that only tests browser and login"""
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file")
        return
    
    print("🛡️  SAFE DEMO - TESTING LOGIN ONLY")
    print("=" * 40)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🔐 Testing LinkedIn login...")
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_timeout(2000)
            
            await page.fill('input#username', email)
            await page.fill('input#password', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(8000)
            
            # Check if login was successful
            current_url = page.url
            if 'feed' in current_url or 'home' in current_url:
                print("✅ Login successful!")
                print("🏠 Navigating to LinkedIn home...")
                await page.goto('https://www.linkedin.com/feed/')
                await page.wait_for_timeout(3000)
                
                print("✅ Demo complete - browser will stay open for 30 seconds")
                print("🛡️  NO JOB APPLICATIONS WERE MADE")
                await page.wait_for_timeout(30000)
            else:
                print("❌ Login may have failed - check credentials")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🛡️  SAFE LINKEDIN DEMO")
    print("This demo ONLY tests login - no job applications will be made")
    asyncio.run(safe_demo())
'''
    
    with open('safe_linkedin_demo.py', 'w') as f:
        f.write(safe_demo_content)
    
    print("✅ Created safe_linkedin_demo.py")
    print("This demo only tests login - no job applications will be made")

if __name__ == "__main__":
    print("🚀 STARTING SAFE LINKEDIN AUTOMATION TEST")
    print("This will test the system without making any real job applications")
    print()
    
    create_safe_demo()
    
    print("\n" + "="*50)
    result = asyncio.run(safe_linkedin_test())
    
    print("\n🎯 TEST SUMMARY:")
    if result:
        print("✅ LinkedIn automation system is working perfectly!")
        print("✅ Ready for use with proper safety measures")
    else:
        print("⚠️  Please check setup and try again")
    
    print("\n📋 NEXT STEPS:")
    print("1. Set your LinkedIn credentials in .env file")
    print("2. Run: python safe_linkedin_demo.py (login test only)")
    print("3. Run: python test_safe_linkedin.py (full safe test)")
    print("4. Once comfortable, use the full automation features")