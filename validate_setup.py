#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Setup Validation Script
Validates that all components are properly configured before GitHub deployment
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "\033[92m✅",
        "warning": "\033[93m⚠️ ",
        "error": "\033[91m❌",
        "info": "\033[94mℹ️ "
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['info'])} {message}{reset}")

def check_file_exists(file_path, required=True):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print_status(f"Found: {file_path}", "success")
        return True
    else:
        status = "error" if required else "warning"
        print_status(f"Missing: {file_path}", status)
        return False

def check_directory_exists(dir_path):
    """Check if a directory exists"""
    if os.path.exists(dir_path):
        print_status(f"Directory exists: {dir_path}", "success")
        return True
    else:
        print_status(f"Directory missing: {dir_path}", "warning")
        return False

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        importlib.import_module(package_name)
        print_status(f"Package installed: {package_name}", "success")
        return True
    except ImportError:
        print_status(f"Package missing: {package_name}", "error")
        return False

def validate_setup():
    """Run comprehensive setup validation"""
    print("🚀 AI JOB AUTOPILOT - SETUP VALIDATION")
    print("=" * 50)
    
    validation_passed = True
    
    # Check essential files
    print("\\n📄 ESSENTIAL FILES")
    print("-" * 20)
    essential_files = [
        "README.md",
        "SETUP.md", 
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "LICENSE",
        "setup.sh",
        "setup.bat",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    for file_path in essential_files:
        if not check_file_exists(file_path):
            validation_passed = False
    
    # Check core Python files
    print("\\n🐍 CORE PYTHON FILES")
    print("-" * 25)
    core_files = [
        "ultimate_job_autopilot.py",
        "perfect_job_autopilot.py", 
        "universal_form_handler.py",
        "demo_ultimate_features.py"
    ]
    
    for file_path in core_files:
        if not check_file_exists(file_path):
            validation_passed = False
    
    # Check directories
    print("\\n📁 DIRECTORIES")
    print("-" * 15)
    directories = [
        "config",
        "dashboard", 
        "ui",
        "worker",
        "smart_scraper",
        "ml_models",
        "extensions",
        "tests"
    ]
    
    for directory in directories:
        check_directory_exists(directory)
    
    # Check Python packages
    print("\\n📦 PYTHON PACKAGES")
    print("-" * 20)
    packages = [
        "streamlit",
        "playwright",
        "openai",
        "sentence_transformers",
        "transformers",
        "pdfplumber",
        "docx",  # python-docx imports as 'docx'
        "yaml",  # PyYAML imports as 'yaml'
        "dotenv",  # python-dotenv imports as 'dotenv'
        "requests",
        "bs4"  # beautifulsoup4 imports as 'bs4'
    ]
    
    for package in packages:
        if not check_python_package(package):
            validation_passed = False
    
    # Check configuration files
    print("\\n⚙️  CONFIGURATION")
    print("-" * 17)
    config_files = [
        ("config/user_profile.yaml", False),
        ("config/resume.pdf", False),
        (".env", False)
    ]
    
    for file_path, required in config_files:
        check_file_exists(file_path, required)
    
    # Check Python version
    print("\\n🐍 PYTHON VERSION")
    print("-" * 17)
    python_version = sys.version_info
    if python_version >= (3, 8):
        print_status(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}", "success")
    else:
        print_status(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires 3.8+", "error")
        validation_passed = False
    
    # Check if playwright browsers are installed
    print("\\n🎭 PLAYWRIGHT BROWSERS")
    print("-" * 23)
    try:
        result = subprocess.run(["playwright", "install", "--dry-run"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Playwright browsers ready", "success")
        else:
            print_status("Playwright browsers may need installation", "warning")
    except FileNotFoundError:
        print_status("Playwright not found - run: playwright install", "error")
        validation_passed = False
    
    # Check git repository
    print("\\n📝 GIT REPOSITORY")
    print("-" * 16)
    if os.path.exists(".git"):
        print_status("Git repository initialized", "success")
        
        # Check git status
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print_status("Uncommitted changes present", "warning")
            else:
                print_status("Working directory clean", "success")
        except:
            print_status("Could not check git status", "warning")
    else:
        print_status("Not a git repository", "warning")
    
    # Final validation result
    print("\\n🎯 VALIDATION RESULT")
    print("=" * 20)
    
    if validation_passed:
        print_status("ALL ESSENTIAL COMPONENTS VALIDATED ✅", "success")
        print_status("Ready for GitHub deployment! 🚀", "success")
        
        print("\\n📋 NEXT STEPS:")
        print("1. git add .")
        print("2. git commit -m 'Initial AI Job Autopilot release'")
        print("3. git push origin main")
        print("4. Create GitHub repository and push")
        print("5. Update README.md with actual repository URL")
        
    else:
        print_status("VALIDATION FAILED - Fix issues above", "error")
        print_status("Run setup.sh or setup.bat first", "info")
        return False
    
    return validation_passed

if __name__ == "__main__":
    success = validate_setup()
    sys.exit(0 if success else 1)