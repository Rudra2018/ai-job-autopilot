#!/usr/bin/env python3
"""
🚀 Ultimate Job Application Autopilot Launcher
Launch the complete AI-powered job application system
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚀 ULTIMATE JOB APPLICATION AUTOPILOT 🚀                 ║
║                                                              ║
║    AI-Powered Job Discovery, Matching & Auto-Application    ║
║    ════════════════════════════════════════════════════     ║
║                                                              ║
║    ✅ Universal job scraping (LinkedIn, Indeed, RemoteOK)    ║
║    ✅ Company career page discovery                          ║
║    ✅ Advanced resume parsing with AI                        ║
║    ✅ Intelligent job-resume matching                        ║
║    ✅ Industry-standard form filling                         ║
║    ✅ Proxy rotation & anti-detection                        ║
║    ✅ Real-time analytics & monitoring                       ║
║    ✅ Modern dashboard UI                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit', 'pandas', 'plotly', 'playwright', 'openai',
        'transformers', 'torch', 'scikit-learn', 'pdfplumber', 
        'python-docx', 'aiohttp', 'psutil', 'pyyaml', 'spacy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                *missing_packages
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("💡 Try running: pip install -r requirements.txt")
            return False
    else:
        print("✅ All dependencies are installed!")
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    directories = [
        'data/scraped_jobs',
        'data/parsed_resumes',
        'data/job_matches',
        'data/sessions',
        'data/analytics',
        'data/company_jobs',
        'data/proxy_stats',
        'logs',
        'screenshots',
        'temp',
        'config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully!")

def check_configuration():
    """Check configuration files"""
    print("⚙️  Checking configuration...")
    
    config_files = {
        'config/user_profile.yaml': 'User profile and preferences',
        'config/resume.pdf': 'Resume file (optional)',
        '.env': 'Environment variables (API keys)'
    }
    
    missing_configs = []
    
    for config_file, description in config_files.items():
        if not Path(config_file).exists():
            missing_configs.append((config_file, description))
    
    if missing_configs:
        print("⚠️  Some configuration files are missing:")
        for config_file, description in missing_configs:
            print(f"   • {config_file}: {description}")
        
        print("\n💡 The system will use defaults or prompt for configuration.")
    else:
        print("✅ All configuration files found!")
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching Ultimate Job Dashboard...")
    print("📊 Dashboard will open in your browser automatically")
    print("🔗 URL: http://localhost:8501")
    print("\n⚡ Dashboard Features:")
    print("   • Universal job scraping")
    print("   • Resume analysis & parsing")
    print("   • AI-powered job matching")
    print("   • Automated form filling")
    print("   • Real-time analytics")
    print("   • System monitoring")
    print("\n" + "="*60)
    
    try:
        dashboard_path = Path("ui/ultimate_job_dashboard.py")
        if dashboard_path.exists():
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', 
                str(dashboard_path), '--server.headless', 'false'
            ])
        else:
            print("❌ Dashboard file not found!")
            print("💡 Make sure ui/ultimate_job_dashboard.py exists")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return False

def launch_cli_mode():
    """Launch CLI mode for automated operation"""
    print("⚡ Launching CLI Orchestrator...")
    
    try:
        from src.ml.job_application_orchestrator import JobApplicationOrchestrator
        
        async def run_pipeline():
            orchestrator = JobApplicationOrchestrator()
            session = await orchestrator.run_complete_pipeline()
            
            print(f"\n🎉 PIPELINE COMPLETED!")
            print(f"📊 Session Results:")
            print(f"   🔍 Jobs scraped: {session.session_stats['total_scraped_jobs']}")
            print(f"   🎯 Jobs matched: {session.session_stats['total_matched_jobs']}")
            print(f"   ✅ Applications: {session.session_stats['total_applied_jobs']}")
            print(f"   📈 Success rate: {session.session_stats['success_rate_percent']}%")
            print(f"   ⏱️  Duration: {session.session_stats['session_duration_minutes']} min")
            
            return session
        
        return asyncio.run(run_pipeline())
        
    except Exception as e:
        print(f"❌ Error in CLI mode: {e}")
        return None

def show_help():
    """Show help information"""
    help_text = """
🆘 HELP & USAGE

Available Commands:
  python launch_ultimate_autopilot.py [option]

Options:
  dashboard    Launch interactive dashboard (default)
  cli         Run automated pipeline in CLI mode
  help        Show this help message
  test        Run system tests
  setup       Setup and configure the system

Examples:
  python launch_ultimate_autopilot.py dashboard
  python launch_ultimate_autopilot.py cli
  
Quick Start:
  1. Place your resume in config/resume.pdf
  2. Configure your preferences in config/user_profile.yaml
  3. Set API keys in .env file (optional for basic features)
  4. Run: python launch_ultimate_autopilot.py

Features:
  • Scrapes jobs from LinkedIn, Indeed, RemoteOK, and company sites
  • Uses AI to match jobs with your skills and experience
  • Automatically fills and submits job applications
  • Provides real-time monitoring and analytics
  • Includes proxy rotation and anti-detection measures

Support:
  • Check logs/ directory for detailed error information
  • Review README.md for comprehensive documentation
  • Ensure all dependencies are installed: pip install -r requirements.txt

For more information, visit: https://github.com/your-repo/ai-job-autopilot
"""
    print(help_text)

def run_tests():
    """Run system tests"""
    print("🧪 Running system tests...")
    
    try:
        from tests.test_suite import run_all_tests
        results = run_all_tests()
        
        if results['success']:
            print("✅ All tests passed!")
        else:
            print(f"❌ {results['failed']} tests failed")
            
        return results['success']
        
    except ImportError:
        print("⚠️  Test suite not found, running basic checks...")
        
        # Basic checks
        checks = {
            "Dependencies": check_dependencies(),
            "Directories": True,
            "Configuration": check_configuration()
        }
        
        all_passed = all(checks.values())
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        return all_passed

def main():
    """Main launcher function"""
    print_banner()
    
    # Get command line argument
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dashboard'
    
    if mode == 'help':
        show_help()
        return
    
    # Setup system
    print(f"🔧 Initializing Ultimate Job Autopilot...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run checks
    if not check_dependencies():
        print("❌ Dependency check failed. Please install required packages.")
        return
    
    setup_directories()
    check_configuration()
    
    print("\n" + "="*60)
    
    # Launch based on mode
    if mode == 'dashboard' or mode == 'ui':
        launch_dashboard()
    elif mode == 'cli' or mode == 'auto':
        session = launch_cli_mode()
        if session:
            print(f"💾 Session data saved to: data/sessions/{session.session_id}/")
    elif mode == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    elif mode == 'setup':
        print("✅ Setup completed! You can now run the system.")
    else:
        print(f"❌ Unknown mode: {mode}")
        print("💡 Available modes: dashboard, cli, help, test, setup")
        show_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🔍 Check logs/ directory for detailed error information")
        sys.exit(1)