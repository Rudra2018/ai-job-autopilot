#!/usr/bin/env python3
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
