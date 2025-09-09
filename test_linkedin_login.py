#!/usr/bin/env python3
"""
Test LinkedIn Authentication
Quick test to verify LinkedIn login is working properly
"""

import asyncio
import os
from dotenv import load_dotenv
from src.automation.linkedin_automation import LinkedInCredentials, LinkedInAutomation

async def test_linkedin_login():
    """Test LinkedIn login functionality"""
    
    load_dotenv()
    
    # Get credentials from environment
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LinkedIn credentials not found in .env file")
        return False
    
    print("🔍 Testing LinkedIn authentication...")
    print(f"Email: {email}")
    
    # Create credentials
    credentials = LinkedInCredentials(email=email, password=password)
    
    # Update callback for progress
    async def update_callback(update):
        print(f"[{update['timestamp'][:19]}] {update['message']}")
    
    # Create automation instance
    automation = LinkedInAutomation(credentials, update_callback)
    
    try:
        # Test browser initialization
        if await automation.initialize_browser():
            print("✅ Browser initialization successful")
            
            # Test login
            if await automation.login_to_linkedin():
                print("✅ LinkedIn login successful!")
                print("🎯 Authentication test passed - ready for job automation")
                
                # Quick job search test
                jobs = await automation.search_jobs(
                    keywords=['cybersecurity', 'security engineer'],
                    locations=['Remote', 'United States'],
                    limit=5
                )
                
                if jobs:
                    print(f"✅ Job search test passed - found {len(jobs)} jobs")
                    for i, job in enumerate(jobs[:3], 1):
                        print(f"  {i}. {job['title']} at {job['company']}")
                else:
                    print("⚠️ No jobs found in test search")
                
                return True
            else:
                print("❌ LinkedIn login failed")
                return False
        else:
            print("❌ Browser initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        await automation.close_browser()
        print("🔄 Browser closed")

if __name__ == "__main__":
    print("🚀 LinkedIn Authentication Test")
    print("=" * 40)
    
    success = asyncio.run(test_linkedin_login())
    
    print("=" * 40)
    if success:
        print("✅ All tests passed! LinkedIn automation is ready")
    else:
        print("❌ Tests failed. Check your credentials and connection")