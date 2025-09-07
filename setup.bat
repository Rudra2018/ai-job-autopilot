@echo off
REM 🤖 AI Job Autopilot - Windows Setup Script
REM This script sets up the complete AI Job Autopilot system on Windows

echo 🚀 AI JOB AUTOPILOT - AUTOMATED SETUP (Windows)
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment
echo ℹ️  Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

REM Activate virtual environment
echo ℹ️  Activating virtual environment...
call .venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
echo ℹ️  Upgrading pip...
python -m pip install --upgrade pip
echo ✅ Pip upgraded

REM Install Python dependencies
echo ℹ️  Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

REM Install Playwright browsers
echo ℹ️  Installing Playwright browsers...
playwright install
echo ✅ Playwright browsers installed

REM Download AI model
echo ℹ️  Downloading JobBERT-v3 AI model...
if not exist ml_models mkdir ml_models
python -c "from sentence_transformers import SentenceTransformer; import os; os.makedirs('ml_models', exist_ok=True); model = SentenceTransformer('TechWolf/JobBERT-v3'); model.save('ml_models/jobbert_v3'); print('✅ JobBERT-v3 model downloaded')"
echo ✅ AI model downloaded

REM Create necessary directories
echo ℹ️  Creating project directories...
if not exist config mkdir config
if not exist dashboard mkdir dashboard
if not exist data mkdir data
if not exist screenshots mkdir screenshots
if not exist logs mkdir logs
if not exist ui\components mkdir ui\components
echo ✅ Project directories created

REM Copy environment template
if not exist .env (
    echo ℹ️  Creating environment file...
    copy .env.example .env
    echo ✅ Environment file created from template
) else (
    echo ⚠️  Environment file already exists
)

REM Create example user profile
if not exist config\user_profile.yaml (
    echo ℹ️  Creating example user profile...
    (
    echo # 🤖 AI Job Autopilot - User Profile Configuration
    echo name: "Your Name"
    echo email: "your@email.com" 
    echo phone: "+1-234-567-8900"
    echo resume_path: "config/resume.pdf"
    echo.
    echo job_preferences:
    echo   titles:
    echo     - "Security Engineer"
    echo     - "Penetration Tester" 
    echo     - "Application Security Engineer"
    echo     - "Cloud Security Engineer"
    echo     - "Cybersecurity Analyst"
    echo.
    echo   locations:
    echo     - "Berlin, Germany"
    echo     - "London, UK"
    echo     - "New York, NY"
    echo     - "Remote"
    echo.
    echo   automation:
    echo     easy_apply: true
    echo     max_applications_per_day: 50
    echo     target_match_threshold: 3.0
    ) > config\user_profile.yaml
    echo ✅ Example user profile created
) else (
    echo ⚠️  User profile already exists
)

echo.
echo 🎉 SETUP COMPLETE!
echo ==================
echo.
echo ✅ AI Job Autopilot is ready to use!
echo.
echo ℹ️  Next steps:
echo 1. 📝 Edit .env file with your credentials
echo 2. 📄 Add your resume to config/resume.pdf
echo 3. ⚙️  Update config/user_profile.yaml with your preferences
echo 4. 🚀 Run: python ultimate_job_autopilot.py
echo 5. 📊 View dashboard: python -m streamlit run ui/dashboard_ui.py
echo.
echo ⚠️  Remember to:
echo • Never commit .env file with real credentials
echo • Test with a small number of applications first
echo • Respect platform rate limits and terms of service
echo.
echo 💼 Happy Job Hunting! 🚀
pause