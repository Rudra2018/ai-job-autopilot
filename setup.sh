#!/bin/bash
# 🤖 AI Job Autopilot - Automated Setup Script
# This script sets up the complete AI Job Autopilot system

set -e  # Exit on any error

echo "🚀 AI JOB AUTOPILOT - AUTOMATED SETUP"
echo "====================================="
echo

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python 3.8+ is installed
print_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
python3 -m venv .venv
print_status "Virtual environment created"

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip
print_status "Pip upgraded"

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt
print_status "Python dependencies installed"

# Install Playwright browsers
print_info "Installing Playwright browsers..."
playwright install
print_status "Playwright browsers installed"

# Download AI model
print_info "Downloading JobBERT-v3 AI model..."
mkdir -p ml_models
python -c "
from sentence_transformers import SentenceTransformer
import os
os.makedirs('ml_models', exist_ok=True)
model = SentenceTransformer('TechWolf/JobBERT-v3')
model.save('ml_models/jobbert_v3')
print('✅ JobBERT-v3 model downloaded and saved')
"
print_status "AI model downloaded"

# Create necessary directories
print_info "Creating project directories..."
mkdir -p config
mkdir -p dashboard
mkdir -p data
mkdir -p screenshots
mkdir -p logs
mkdir -p ui/components
print_status "Project directories created"

# Copy environment template
if [ ! -f .env ]; then
    print_info "Creating environment file..."
    cp .env.example .env
    print_status "Environment file created from template"
else
    print_warning "Environment file already exists"
fi

# Create example user profile if it doesn't exist
if [ ! -f config/user_profile.yaml ]; then
    print_info "Creating example user profile..."
    cat > config/user_profile.yaml << 'EOF'
# 🤖 AI Job Autopilot - User Profile Configuration
name: "Your Name"
email: "your@email.com"
phone: "+1-234-567-8900"
resume_path: "config/resume.pdf"

job_preferences:
  titles:
    - "Security Engineer" 
    - "Penetration Tester"
    - "Application Security Engineer"
    - "Cloud Security Engineer"
    - "Cybersecurity Analyst"
    - "Information Security Engineer"
    - "DevSecOps Engineer"
    - "Security Consultant"
    - "Ethical Hacker"
    - "Security Architect"
  
  locations:
    - "Berlin, Germany"
    - "London, UK" 
    - "New York, NY"
    - "San Francisco, CA"
    - "Remote"
    - "Amsterdam, Netherlands"
    - "Zurich, Switzerland"
  
  keywords:
    - "penetration testing"
    - "cybersecurity"
    - "cloud security"
    - "application security"
    - "vulnerability assessment"
    - "security architecture"
    - "incident response"
    - "security automation"
  
  automation:
    easy_apply: true
    max_applications_per_day: 50
    target_match_threshold: 3.0
EOF
    print_status "Example user profile created"
else
    print_warning "User profile already exists"
fi

# Set executable permissions for Python scripts
print_info "Setting executable permissions..."
chmod +x *.py
chmod +x setup.sh
print_status "Permissions set"

# Final setup confirmation
echo
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo
print_status "AI Job Autopilot is ready to use!"
echo
print_info "Next steps:"
echo "1. 📝 Edit .env file with your credentials"
echo "2. 📄 Add your resume to config/resume.pdf"
echo "3. ⚙️  Update config/user_profile.yaml with your preferences"
echo "4. 🚀 Run: python ultimate_job_autopilot.py"
echo "5. 📊 View dashboard: python -m streamlit run ui/dashboard_ui.py"
echo
print_warning "Remember to:"
echo "• Never commit .env file with real credentials"
echo "• Test with a small number of applications first"
echo "• Respect platform rate limits and terms of service"
echo
echo "💼 Happy Job Hunting! 🚀"