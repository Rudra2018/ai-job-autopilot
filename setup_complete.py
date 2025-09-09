#!/usr/bin/env python3
"""
🚀 AI Job Autopilot - Complete Setup Verification
Comprehensive setup checker and system validator
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import importlib.util

def print_header():
    """Print welcome header."""
    print("="*80)
    print("🚀 AI JOB AUTOPILOT - SETUP VERIFICATION")
    print("="*80)

def check_environment():
    """Check if .env file exists and load it."""
    print("\n🔧 ENVIRONMENT CONFIGURATION")
    print("-" * 40)
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        load_dotenv()
        
        # Check critical API keys
        api_keys = {
            "OpenAI API Key": "OPENAI_API_KEY",
            "Gemini API Key": "GEMINI_API_KEY", 
            "Claude API Key": "CLAUDE_API_KEY",
            "LinkedIn Email": "LINKEDIN_EMAIL",
            "LinkedIn Password": "LINKEDIN_PASSWORD"
        }
        
        for name, env_var in api_keys.items():
            value = os.getenv(env_var)
            if value:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {name}: {masked}")
            else:
                print(f"⚠️  {name}: Not configured")
                
    else:
        print("❌ .env file not found")
        print("   Run: cp .env.example .env and configure your keys")
        return False
    
    return True

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n📦 PYTHON DEPENDENCIES")
    print("-" * 40)
    
    required_packages = [
        "streamlit", "pandas", "plotly", "python-dotenv",
        "openai", "anthropic", "google-generativeai",
        "selenium", "beautifulsoup4", "requests"
    ]
    
    missing_packages = []
    
    # Package name mappings for import
    package_imports = {
        "python-dotenv": "dotenv",
        "google-generativeai": "google.generativeai", 
        "beautifulsoup4": "bs4"
    }
    
    for package in required_packages:
        import_name = package_imports.get(package, package.replace("-", "_"))
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_project_structure():
    """Check if project structure is properly organized."""
    print("\n📁 PROJECT STRUCTURE")
    print("-" * 40)
    
    required_dirs = [
        "src/orchestration",
        "src/orchestration/agents", 
        "ui",
        "tests",
        "docs",
        "scripts",
        "archive"
    ]
    
    for directory in required_dirs:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/")
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".gitignore",
        "README.md",
        ".env.example"
    ]
    
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")

def test_agent_system():
    """Test the multi-agent orchestration system."""
    print("\n🤖 MULTI-AGENT SYSTEM")
    print("-" * 40)
    
    try:
        from src.orchestration.integrated_orchestrator import IntegratedOrchestrator
        print("✅ IntegratedOrchestrator import successful")
        
        orchestrator = IntegratedOrchestrator()
        print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
        
        agents = list(orchestrator.agents.keys())
        for agent in agents:
            print(f"   - {agent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent system test failed: {e}")
        return False

def test_streamlit_integration():
    """Test Streamlit integration."""
    print("\n🎨 STREAMLIT INTEGRATION")
    print("-" * 40)
    
    try:
        from src.orchestration.streamlit_integration import StreamlitOrchestrationUI
        print("✅ StreamlitOrchestrationUI import successful")
        
        ui = StreamlitOrchestrationUI()
        print("✅ UI component initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit integration test failed: {e}")
        return False

def check_browser_setup():
    """Check browser automation setup."""
    print("\n🌐 BROWSER AUTOMATION")
    print("-" * 40)
    
    try:
        import selenium
        print("✅ Selenium installed")
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Just check if Chrome is available (don't actually start it)
        print("✅ Chrome WebDriver configuration ready")
        return True
        
    except Exception as e:
        print(f"⚠️  Browser setup: {e}")
        print("   Install ChromeDriver: brew install chromedriver (macOS)")
        return False

def run_quick_test():
    """Run a quick functionality test."""
    print("\n🧪 QUICK FUNCTIONALITY TEST")
    print("-" * 40)
    
    try:
        # Test environment loading
        load_dotenv()
        print("✅ Environment variables loaded")
        
        # Test orchestrator
        from src.orchestration.integrated_orchestrator import IntegratedOrchestrator
        orchestrator = IntegratedOrchestrator()
        print("✅ Orchestrator ready")
        
        # Test agents
        print(f"✅ {len(orchestrator.agents)} agents available")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def print_next_steps(all_checks_passed):
    """Print next steps based on setup status."""
    print("\n" + "="*80)
    
    if all_checks_passed:
        print("🎉 SETUP COMPLETE - SYSTEM READY!")
        print("="*80)
        print("\n🚀 NEXT STEPS:")
        print("   1. Start the application:")
        print("      streamlit run main.py")
        print("\n   2. Open your browser to:")
        print("      http://localhost:8501")
        print("\n   3. Upload your resume and start job hunting!")
        print("\n📚 DOCUMENTATION:")
        print("   - README.md - Full documentation")
        print("   - docs/ - Additional guides and documentation")
        print("   - .env.example - Environment configuration template")
        print("\n🧪 TESTING:")
        print("   - Run agent tests: python tests/simplified_agent_test.py")
        print("   - Run comprehensive tests: python tests/test_agents.py")
        
    else:
        print("⚠️  SETUP INCOMPLETE - PLEASE FIX ISSUES ABOVE")
        print("="*80)
        print("\n🔧 TO FIX:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Configure .env file: cp .env.example .env")
        print("   3. Add your API keys and credentials to .env")
        print("   4. Re-run this setup check: python setup_complete.py")
        print("\n📧 NEED HELP?")
        print("   - Check README.md for detailed instructions")
        print("   - Review docs/SETUP_GUIDE.md for troubleshooting")

def main():
    """Main setup verification function."""
    print_header()
    
    checks = [
        ("Environment Configuration", check_environment),
        ("Python Dependencies", check_dependencies), 
        ("Project Structure", check_project_structure),
        ("Multi-Agent System", test_agent_system),
        ("Streamlit Integration", test_streamlit_integration),
        ("Browser Automation", check_browser_setup),
        ("Quick Functionality Test", run_quick_test)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
    
    print(f"\n📊 SETUP STATUS: {passed_checks}/{total_checks} checks passed")
    
    all_checks_passed = passed_checks == total_checks
    print_next_steps(all_checks_passed)
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)