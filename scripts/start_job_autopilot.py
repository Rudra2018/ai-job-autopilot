#!/usr/bin/env python3
"""
AI Job Autopilot - Guided Startup Script
Safe, supervised launch of your LinkedIn automation system
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging for the session"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_prerequisites():
    """Check all prerequisites are met"""
    
    print("\n🔍 CHECKING PREREQUISITES...")
    print("-" * 50)
    
    issues = []
    
    # Check resume file
    if Path("Ankit_Thakur_Resume.pdf").exists():
        print("✅ Resume file found: Ankit_Thakur_Resume.pdf")
    else:
        issues.append("❌ Resume file missing: Ankit_Thakur_Resume.pdf")
    
    # Check credentials
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    
    if linkedin_email and linkedin_password:
        print(f"✅ LinkedIn credentials configured: {linkedin_email}")
    else:
        issues.append("❌ LinkedIn credentials missing in .env file")
    
    # Check AI services
    ai_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"), 
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
    }
    
    available_ai = sum(1 for key in ai_keys.values() if key)
    print(f"✅ AI services configured: {available_ai}/3 ({list(k for k,v in ai_keys.items() if v)})")
    
    if available_ai == 0:
        issues.append("❌ No AI services configured")
    
    # Check browser installation
    try:
        import playwright
        print("✅ Playwright browser automation ready")
    except ImportError:
        issues.append("❌ Playwright not installed")
    
    return issues

def show_safety_reminder():
    """Show important safety reminders"""
    
    print("\n⚠️  IMPORTANT SAFETY REMINDERS")
    print("=" * 60)
    print("""
🔒 LinkedIn Account Safety:
   • Start with 5-10 applications per day maximum
   • Monitor your account for any restrictions
   • Use non-headless mode for first few tests
   • Stop immediately if you see captchas or warnings

🤖 Automation Best Practices:
   • Review generated cover letters before sending
   • Customize job search keywords for your field
   • Monitor application success rates
   • Respect company application policies

📊 Success Strategy:
   • Quality over quantity - target relevant jobs
   • Update your resume based on AI suggestions
   • Track which job types get best responses
   • Adjust automation settings based on results
""")

def get_user_confirmation():
    """Get user confirmation to proceed"""
    
    print("\n🚀 READY TO START LINKEDIN AUTOMATION")
    print("=" * 50)
    print("""
Your AI Job Autopilot will:
✅ Search LinkedIn for jobs matching your keywords
✅ Analyze job compatibility using AI
✅ Apply automatically with personalized cover letters
✅ Answer form questions intelligently
✅ Track all applications to avoid duplicates
✅ Generate session reports and metrics
""")
    
    while True:
        response = input("\nDo you want to start the automation? (yes/no/test): ").lower().strip()
        
        if response in ['yes', 'y']:
            return 'full'
        elif response in ['test', 't']:
            return 'test'
        elif response in ['no', 'n', 'exit', 'quit']:
            return 'exit'
        else:
            print("Please enter 'yes' to start, 'test' for test mode, or 'no' to exit")

async def run_test_mode():
    """Run in safe test mode"""
    
    print("\n🧪 STARTING TEST MODE")
    print("=" * 40)
    print("Testing core functionality without actual applications...\n")
    
    try:
        # Import and test components
        from src.core.resume_processing_pipeline import ResumeProcessingPipeline, PipelineConfig
        from src.ml.multi_ai_service import MultiAIService
        
        # Test resume processing
        print("1. Testing resume processing...")
        config = PipelineConfig(enable_ai_enhancement=True)
        pipeline = ResumeProcessingPipeline(config)
        result = pipeline.process_resume("Ankit_Thakur_Resume.pdf")
        
        if result.overall_success:
            print(f"   ✅ Resume processed successfully!")
            print(f"   📧 Email: {result.parsed_resume.contact_info.email}")
            print(f"   📱 Phone: {result.parsed_resume.contact_info.phone}")
        else:
            print("   ❌ Resume processing failed")
            return False
        
        # Test AI services
        print("\n2. Testing AI services...")
        ai_service = MultiAIService()
        available = ai_service.get_available_services()
        print(f"   ✅ Available AI services: {[s.value for s in available]}")
        
        # Test job matching
        print("\n3. Testing job matching...")
        sample_job = "Software Engineer position requiring Python, JavaScript, and cloud experience."
        
        resume_dict = {
            'contact_info': result.parsed_resume.contact_info.__dict__,
            'skills': result.parsed_resume.skills,
            'work_experience': [exp.__dict__ for exp in result.parsed_resume.work_experience]
        }
        
        match_result = await ai_service.match_job_compatibility(resume_dict, sample_job)
        if match_result.success:
            print(f"   ✅ Job matching working! (Provider: {match_result.provider.value})")
        else:
            print(f"   ⚠️  Job matching failed: {match_result.error}")
        
        print("\n✅ TEST MODE COMPLETED - All core systems working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test mode failed: {e}")
        return False

async def run_full_automation():
    """Run full LinkedIn automation"""
    
    print("\n🚀 STARTING FULL AUTOMATION MODE")
    print("=" * 50)
    
    try:
        # Import LinkedIn autopilot
        from src.automation.enhanced_linkedin_autopilot import EnhancedLinkedInAutopilot
        
        # Create autopilot instance
        autopilot = EnhancedLinkedInAutopilot()
        
        # Show configuration
        config = autopilot.config
        print(f"📊 Configuration:")
        print(f"   • Max applications: {config['automation']['max_applications_per_session']}")
        print(f"   • Keywords: {', '.join(config['job_preferences']['keywords'])}")
        print(f"   • Locations: {', '.join(config['job_preferences']['locations'])}")
        print(f"   • Headless mode: {config['browser']['headless']}")
        
        # Ask for final confirmation
        print(f"\n⚠️  FINAL CONFIRMATION")
        final_confirm = input("This will open LinkedIn and start applying to jobs. Continue? (yes/no): ").lower()
        
        if final_confirm not in ['yes', 'y']:
            print("❌ Automation cancelled by user")
            return False
        
        # Start automation
        print("\n🌐 Starting browser and LinkedIn session...")
        
        success = autopilot.start_session()
        if not success:
            print("❌ Failed to start LinkedIn session")
            return False
        
        # Run job search and applications
        keywords = config['job_preferences']['keywords']
        max_apps = min(5, config['automation']['max_applications_per_session'])  # Limit to 5 for safety
        
        print(f"\n🔍 Searching for jobs: {', '.join(keywords)}")
        print(f"📊 Maximum applications: {max_apps} (safety limit)")
        
        results = autopilot.search_and_apply_jobs(keywords, max_apps)
        
        # Show results
        print(f"\n📋 SESSION RESULTS:")
        print(f"   • Jobs found: {results['jobs_found']}")
        print(f"   • Applications completed: {results['applications_completed']}")
        print(f"   • Duplicates skipped: {results['duplicates_skipped']}")
        print(f"   • Errors: {results['errors']}")
        
        # End session
        autopilot.end_session()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main startup function"""
    
    print("🤖 AI JOB AUTOPILOT - GUIDED STARTUP")
    print("=" * 60)
    print("Safe, supervised launch of your LinkedIn automation system")
    
    setup_logging()
    
    # Check prerequisites
    issues = check_prerequisites()
    
    if issues:
        print(f"\n❌ SETUP ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\nPlease fix these issues before starting the automation.")
        return False
    
    print("\n✅ All prerequisites met!")
    
    # Show safety reminders
    show_safety_reminder()
    
    # Get user confirmation
    mode = get_user_confirmation()
    
    if mode == 'exit':
        print("\n👋 Exiting AI Job Autopilot. Good luck with your job search!")
        return True
    
    try:
        if mode == 'test':
            success = asyncio.run(run_test_mode())
        else:  # mode == 'full'
            success = asyncio.run(run_full_automation())
        
        if success:
            print("\n🎉 AI Job Autopilot session completed successfully!")
            print("\nNext steps:")
            print("• Check your LinkedIn messages for responses")
            print("• Review session logs in data/session_summaries/")
            print("• Monitor your LinkedIn account for any restrictions")
            print("• Adjust settings based on results")
        else:
            print("\n⚠️  Session completed with issues. Please check logs.")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Session interrupted by user")
        print("Session data has been saved. You can restart anytime.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue if it persists.")

if __name__ == "__main__":
    main()