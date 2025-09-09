#!/usr/bin/env python3
"""
Fast LinkedIn Easy Apply Test - Optimized for Speed
"""

import asyncio
import os
from dotenv import load_dotenv
from src.automation.linkedin_automation import LinkedInCredentials, LinkedInAutomation

async def test_fast_apply():
    """Test fast Easy Apply with time tracking"""
    
    import time
    start_time = time.time()
    
    print("⚡ Fast LinkedIn Easy Apply Test")
    print("=" * 50)
    
    load_dotenv()
    
    credentials = LinkedInCredentials(
        email=os.getenv('LINKEDIN_EMAIL'),
        password=os.getenv('LINKEDIN_PASSWORD')
    )
    
    async def progress_callback(update):
        elapsed = time.time() - start_time
        print(f"[{elapsed:5.1f}s] {update['message']}")
    
    automation = LinkedInAutomation(credentials, progress_callback)
    
    try:
        # Quick login
        print("🚀 Fast initialization...")
        if not await automation.initialize_browser():
            return False
        
        if not await automation.login_to_linkedin():
            return False
        
        # Search for just one job quickly
        print("\n⚡ Quick job search...")
        jobs = await automation.search_jobs(['cybersecurity engineer'], ['Remote'], limit=5)
        
        if not jobs:
            print("❌ No jobs found!")
            return False
        
        # Apply to first job with timing
        job = jobs[0]
        print(f"\n⚡ Fast apply to: {job['title'][:50]}...")
        
        apply_start = time.time()
        success = await automation.apply_to_job(job)
        apply_time = time.time() - apply_start
        
        total_time = time.time() - start_time
        
        print(f"\n📊 Performance Results:")
        print(f"   Apply Time: {apply_time:.1f} seconds")
        print(f"   Total Time: {total_time:.1f} seconds")
        print(f"   Success: {'✅' if success else '⚠️'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
        
    finally:
        await automation.close_browser()

if __name__ == "__main__":
    success = asyncio.run(test_fast_apply())
    print(f"\n{'✅ FAST' if success else '❌ SLOW'} test completed!")