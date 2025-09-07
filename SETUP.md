# 🚀 AI Job Autopilot - Detailed Setup Guide

This comprehensive guide will help you set up and configure the AI Job Autopilot system for automated job applications.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup (Automated)](#quick-setup-automated)
- [Manual Setup](#manual-setup)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment Options](#deployment-options)
- [Troubleshooting](#troubleshooting)

---

## ⚡ Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Stable broadband connection

### Required Accounts & API Keys
- **OpenAI API Key** (GPT-4o for intelligent matching)
- **Google API Key** (Gemini for enhanced capabilities)
- **Gmail Account** (with App Password)
- **LinkedIn Account** (for Easy Apply automation)
- **Anthropic API Key** (optional, for Claude fallback)

---

## 🚀 Quick Setup (Automated)

### Option 1: Linux/macOS
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-job-autopilot.git
cd ai-job-autopilot

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### Option 2: Windows
```batch
# Clone the repository
git clone https://github.com/yourusername/ai-job-autopilot.git
cd ai-job-autopilot

# Run automated setup
setup.bat
```

### Option 3: Docker
```bash
# Clone and run with Docker
git clone https://github.com/yourusername/ai-job-autopilot.git
cd ai-job-autopilot
docker-compose up -d
```

---

## 🛠️ Manual Setup

If you prefer manual installation or the automated setup fails:

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ai-job-autopilot.git
cd ai-job-autopilot
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 4. Download AI Model
```bash
# Download JobBERT-v3 model
python -c "
from sentence_transformers import SentenceTransformer
import os
os.makedirs('ml_models', exist_ok=True)
model = SentenceTransformer('TechWolf/JobBERT-v3')
model.save('ml_models/jobbert_v3')
"
```

### 5. Create Project Structure
```bash
# Create necessary directories
mkdir -p config dashboard data screenshots logs ui/components
```

---

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# Required: LLM API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
GOOGLE_API_KEY=AIza-your-google-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Required: Email Configuration
GMAIL_ADDRESS=your.professional.email@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password

# Required: LinkedIn Credentials
LINKEDIN_EMAIL=your.linkedin.email@gmail.com
LINKEDIN_PASSWORD=your-linkedin-password

# Optional: Automation Settings
PLAYWRIGHT_HEADLESS=false
MAX_APPLICATIONS_PER_DAY=50
LOG_LEVEL=INFO
```

### 2. User Profile Configuration

Create/edit `config/user_profile.yaml`:

```yaml
name: "Your Full Name"
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
    # EMEA
    - "London, UK"
    - "Amsterdam, Netherlands"
    - "Dublin, Ireland"
    - "Zurich, Switzerland"
    - "Paris, France"
    
    # Germany
    - "Berlin, Germany"
    - "Munich, Germany"
    - "Frankfurt, Germany"
    - "Hamburg, Germany"
    
    # USA
    - "New York, NY"
    - "San Francisco, CA"
    - "Seattle, WA"
    - "Austin, TX"
    - "Remote"
  
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
```

### 3. Add Your Resume

Place your resume in the config folder:
```bash
# Copy your resume (PDF format recommended)
cp /path/to/your/resume.pdf config/resume.pdf
```

---

## 🧪 Testing

### 1. Test Basic Setup
```bash
# Test Python imports
python -c "
import streamlit
import playwright
import openai
from sentence_transformers import SentenceTransformer
print('✅ All imports successful')
"
```

### 2. Test AI Model
```bash
# Test JobBERT-v3 model
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('ml_models/jobbert_v3')
embedding = model.encode('Security Engineer')
print(f'✅ AI model working, embedding shape: {embedding.shape}')
"
```

### 3. Test Dashboard
```bash
# Launch dashboard
python -m streamlit run ui/dashboard_ui.py
```
Visit http://localhost:8501 to verify the dashboard loads.

### 4. Test LinkedIn Login
```bash
# Test LinkedIn authentication (use with caution)
python -c "
from perfect_job_autopilot import test_linkedin_login
test_linkedin_login()
"
```

---

## 🚀 Deployment Options

### Local Development
```bash
# Run complete autopilot
python ultimate_job_autopilot.py

# Run LinkedIn-focused automation
python perfect_job_autopilot.py

# Launch dashboard
python -m streamlit run ui/dashboard_ui.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Google Cloud Platform
```bash
# Deploy to Cloud Run
gcloud builds submit --config cloudbuild/cloudbuild.yaml

# Set up scheduled runs
gcloud scheduler jobs create http autopilot-job \
    --schedule="0 9 * * 1-5" \
    --uri="https://your-app.run.app/autopilot"
```

### GitHub Actions
Create `.github/workflows/autopilot.yml`:
```yaml
name: AI Job Autopilot
on:
  schedule:
    - cron: '0 9 * * 1-5'  # Weekdays at 9 AM
  workflow_dispatch:

jobs:
  autopilot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      - name: Run Autopilot
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          LINKEDIN_EMAIL: ${{ secrets.LINKEDIN_EMAIL }}
          LINKEDIN_PASSWORD: ${{ secrets.LINKEDIN_PASSWORD }}
        run: python ultimate_job_autopilot.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Python/Pip Issues
```bash
# Update Python and pip
python --version  # Should be 3.8+
pip install --upgrade pip

# If using multiple Python versions
python3 -m venv .venv
python3 -m pip install -r requirements.txt
```

#### 2. Playwright Installation Problems
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install --with-deps

# For Linux, install system dependencies
sudo apt-get install -y \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libxss1 libasound2 libgtk-3-0
```

#### 3. AI Model Download Issues
```bash
# Clear cache and re-download
rm -rf ml_models/jobbert_v3
python -c "
from sentence_transformers import SentenceTransformer
import os
os.makedirs('ml_models', exist_ok=True)
model = SentenceTransformer('TechWolf/JobBERT-v3')
model.save('ml_models/jobbert_v3')
"
```

#### 4. LinkedIn Login Problems
- **2FA Issues**: Complete 2FA manually on first run
- **Security Challenges**: Use a trusted device/network
- **Rate Limiting**: Reduce `max_applications_per_day`
- **Captcha**: Run with `PLAYWRIGHT_HEADLESS=false` to solve manually

#### 5. Form Filling Failures
```bash
# Test with debug mode
PLAYWRIGHT_HEADLESS=false python perfect_job_autopilot.py

# Check browser console for errors
# Update selectors in universal_form_handler.py
```

#### 6. API Rate Limits
```bash
# Reduce request frequency
# Add delays in .env file
REQUEST_DELAY_SECONDS=10
MAX_APPLICATIONS_PER_DAY=25
```

### Getting Help

1. **Check Logs**: Look in `logs/` directory for detailed error messages
2. **GitHub Issues**: Report bugs at repository issues page  
3. **Documentation**: Read all markdown files in the repository
4. **Community**: Join Discord server for community support

### Performance Optimization

#### Speed Up Setup
```bash
# Use pip cache for faster installs
pip install --cache-dir .pip-cache -r requirements.txt

# Pre-download models
python -c "
import concurrent.futures
from sentence_transformers import SentenceTransformer
def download_model(name):
    return SentenceTransformer(name)
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.submit(download_model, 'TechWolf/JobBERT-v3')
"
```

#### Optimize for Production
```bash
# Use production-optimized settings
PLAYWRIGHT_HEADLESS=true
LOG_LEVEL=WARNING
MAX_CONCURRENT_SESSIONS=1
REQUEST_DELAY_SECONDS=3
```

---

## ✅ Verification Checklist

Before running the system, ensure:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] Playwright browsers installed (`playwright install`)
- [ ] `.env` file configured with real credentials
- [ ] `config/user_profile.yaml` updated with your information
- [ ] `config/resume.pdf` contains your actual resume
- [ ] AI model downloaded to `ml_models/jobbert_v3/`
- [ ] Dashboard accessible at http://localhost:8501
- [ ] LinkedIn login credentials work
- [ ] All required directories exist

## 🎯 Next Steps

Once setup is complete:

1. **Test Run**: Start with a small test (`MAX_APPLICATIONS_PER_DAY=5`)
2. **Monitor Results**: Watch dashboard and log files
3. **Adjust Settings**: Fine-tune based on success rates
4. **Scale Up**: Gradually increase application limits
5. **Schedule Automation**: Set up cron jobs or cloud schedules

**Happy Job Hunting! 🚀**