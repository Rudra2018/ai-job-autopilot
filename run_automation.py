#!/usr/bin/env python3
"""
AI Job Autopilot - Production Runner
Direct execution of LinkedIn automation with safety checks
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup production logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('automation.log'),
            logging.StreamHandler()
        ]
    )

async def run_linkedin_automation():
    """Run LinkedIn automation in production mode"""
    
    print("🚀 STARTING AI JOB AUTOPILOT - PRODUCTION MODE")
    print("=" * 60)
    
    try:
        # Import and initialize
        from src.automation.enhanced_linkedin_autopilot import EnhancedLinkedInAutopilot
        
        print("🔧 Initializing LinkedIn autopilot...")
        autopilot = EnhancedLinkedInAutopilot()
        
        # Show configuration
        config = autopilot.config
        print(f"\n📊 CONFIGURATION:")
        print(f"   📧 LinkedIn: {config['linkedin']['email']}")
        print(f"   🎯 Keywords: {', '.join(config['job_preferences']['keywords'])}")
        print(f"   📍 Locations: {', '.join(config['job_preferences']['locations'])}")
        print(f"   📊 Max applications: 5 (safety limit)")  # Override for safety
        print(f"   🤖 AI features: All enabled")
        
        print(f"\n🌐 Starting browser session...")
        
        # Start the automation session
        success = autopilot.start_session()
        
        if not success:
            print("❌ Failed to start LinkedIn session")
            print("This could be due to:")
            print("• LinkedIn security measures")
            print("• Browser automation detection")
            print("• Network connectivity issues")
            print("\n💡 Try running in non-headless mode first:")
            print("   Edit config/enhanced_config.yaml and set headless: false")
            return False
        
        print("✅ LinkedIn session started successfully!")
        
        # Get job search keywords
        keywords = config['job_preferences']['keywords']
        max_applications = 5  # Start conservative for safety
        
        print(f"\n🔍 Searching for jobs with keywords: {', '.join(keywords)}")
        print(f"📊 Safety limit: {max_applications} applications maximum")
        
        # Run job search and applications
        results = autopilot.search_and_apply_jobs(keywords, max_applications)
        
        # Display results
        print(f"\n📋 SESSION COMPLETED!")
        print("=" * 40)
        print(f"📊 Jobs found: {results['jobs_found']}")
        print(f"✅ Applications completed: {results['applications_completed']}")
        print(f"🚫 Duplicates skipped: {results['duplicates_skipped']}")
        print(f"❌ Errors encountered: {results['errors']}")
        
        # Get session summary
        summary = autopilot.get_session_summary()
        
        print(f"\n📈 SESSION STATISTICS:")
        print(f"   Duration: {summary['duration_minutes']:.1f} minutes")
        print(f"   Applications attempted: {summary['applications_attempted']}")
        print(f"   Applications completed: {summary['applications_completed']}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        print(f"   Questions answered: {summary['questions_answered']}")
        print(f"   Resumes optimized: {summary['resumes_optimized']}")
        
        # End session properly
        autopilot.end_session()
        
        if results['applications_completed'] > 0:
            print(f"\n🎉 SUCCESS! Applied to {results['applications_completed']} jobs!")
            print(f"📬 Check your LinkedIn messages for responses")
            print(f"📊 Session data saved for analysis")
        else:
            print(f"\n⚠️  No applications completed this session")
            print(f"This could be due to:")
            print(f"• All suitable jobs already applied to (duplicate detection)")
            print(f"• No jobs matching your criteria found")
            print(f"• LinkedIn interface changes")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"• Monitor your LinkedIn account")
        print(f"• Check for messages from recruiters")
        print(f"• Review session logs in automation.log")
        print(f"• Run again tomorrow for more applications")
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n🛑 Session interrupted by user")
        print(f"Shutting down safely...")
        return False
        
    except Exception as e:
        print(f"\n❌ Automation failed: {e}")
        print(f"This might be due to:")
        print(f"• LinkedIn security measures")
        print(f"• Browser automation detection") 
        print(f"• Network connectivity issues")
        print(f"• LinkedIn interface changes")
        
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"1. Try running in non-headless mode")
        print(f"2. Check your LinkedIn account manually")
        print(f"3. Verify your login credentials")
        print(f"4. Try again in a few hours")
        
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution function"""
    
    setup_logging()
    
    # Check prerequisites
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    if not linkedin_email:
        print("❌ LinkedIn credentials not found in .env file")
        return
    
    # Show safety disclaimer
    print(f"""
⚠️  IMPORTANT SAFETY NOTICE:
• This automation is for educational/personal use only
• Start with 5-10 applications per day maximum
• Monitor your LinkedIn account for restrictions
• Stop if you encounter captchas or warnings
• Respect LinkedIn's terms of service

🤖 Your AI Job Autopilot will:
✅ Search for relevant jobs automatically
✅ Apply with personalized cover letters
✅ Answer form questions using AI
✅ Track applications to avoid duplicates
✅ Generate detailed session reports
""")
    
    print(f"🚀 Starting automation in 3 seconds...")
    import time
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    
    # Run the automation
    success = asyncio.run(run_linkedin_automation())
    
    if success:
        print(f"\n🎉 AI Job Autopilot session completed successfully!")
    else:
        print(f"\n⚠️  Session completed with issues - check logs for details")

if __name__ == "__main__":
    main()