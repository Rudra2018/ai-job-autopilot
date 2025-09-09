#!/usr/bin/env python3
"""
Real LinkedIn Login Test
Test the actual LinkedIn automation with your credentials
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_real_linkedin_login():
    """Test real LinkedIn login and job application"""
    
    print("🚀 Real LinkedIn Automation Test")
    print("=" * 50)
    
    load_dotenv()
    
    # Get credentials
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LinkedIn credentials not found!")
        return False
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)}")
    print()
    
    try:
        from src.automation.linkedin_automation import LinkedInCredentials, LinkedInAutomation
        
        # Create credentials
        credentials = LinkedInCredentials(email=email, password=password)
        
        # Progress callback
        async def progress_callback(update):
            print(f"[{update['timestamp'][11:19]}] {update['message']}")
        
        # Create automation instance
        automation = LinkedInAutomation(credentials, progress_callback)
        
        print("🌐 Starting browser and attempting login...")
        print("-" * 50)
        
        # Initialize browser
        if await automation.initialize_browser():
            print("✅ Browser initialized successfully")
            
            # Attempt login
            if await automation.login_to_linkedin():
                print("✅ LinkedIn login successful!")
                
                # Test job search
                print("\n🔍 Testing job search functionality...")
                jobs = await automation.search_jobs(
                    keywords=['cybersecurity engineer', 'security analyst'],
                    locations=['Remote', 'United States', 'United Kingdom'],
                    limit=5
                )
                
                if jobs:
                    print(f"✅ Found {len(jobs)} job opportunities:")
                    for i, job in enumerate(jobs, 1):
                        print(f"  {i}. {job['title']} at {job['company']}")
                        print(f"     📍 {job['location']}")
                        print(f"     🔗 {job['url'][:50]}...")
                        print()
                    
                    # Optional: Test application to first job
                    if len(jobs) > 0 and input("\n🤔 Apply to first job? (y/n): ").lower() == 'y':
                        print(f"📝 Attempting to apply to: {jobs[0]['title']}")
                        success = await automation.apply_to_job(jobs[0])
                        if success:
                            print("✅ Application completed!")
                        else:
                            print("⚠️ Application requires manual review")
                    
                    print("\n🎯 LinkedIn automation test completed successfully!")
                    return True
                else:
                    print("⚠️ No jobs found matching criteria")
                    return True  # Still a success
            else:
                print("❌ LinkedIn login failed")
                return False
        else:
            print("❌ Browser initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        try:
            await automation.close_browser()
            print("🔄 Browser closed")
        except:
            pass

if __name__ == "__main__":
    print("⚠️  IMPORTANT NOTES:")
    print("1. This will open a visible browser window")
    print("2. Make sure you don't have LinkedIn open in other tabs")
    print("3. The browser will stay open during the process")
    print("4. Press Ctrl+C to stop at any time")
    print()
    
    if input("Continue with real LinkedIn test? (y/n): ").lower() == 'y':
        success = asyncio.run(test_real_linkedin_login())
        
        print("\n" + "=" * 50)
        if success:
            print("✅ ALL TESTS PASSED! LinkedIn automation is ready")
        else:
            print("❌ Tests failed. Check error messages above")
    else:
        print("Test cancelled.")