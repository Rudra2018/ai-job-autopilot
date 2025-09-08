# 🤖 AI Job Autopilot

**AI-powered job application automation system with intelligent form filling and multi-platform support.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-OpenAI%20%7C%20Anthropic-purple?logo=openai)](https://openai.com)
[![Automation](https://img.shields.io/badge/Automation-Playwright%20%7C%20Selenium-orange?logo=selenium)](https://selenium.dev)

## ✨ **Key Features**

### 🧠 **AI Integration**
- **Multi-LLM Support**: OpenAI GPT-4 and Anthropic Claude integration
- **Smart Question Answering**: AI-powered responses to application questions
- **Resume Optimization**: Dynamic resume tailoring for job requirements
- **Duplicate Detection**: Prevents redundant applications using semantic analysis

### 🎯 **Automation Capabilities**
- **LinkedIn Easy Apply**: Automated LinkedIn job applications
- **Universal Form Handler**: Intelligent form field detection and completion
- **Multi-Platform Support**: LinkedIn, Indeed, Glassdoor, and company portals
- **Stealth Mode**: Human-like behavior simulation for undetected automation

### 📊 **Dashboard & Analytics**
- **Streamlit Dashboard**: Real-time application tracking and analytics
- **Performance Metrics**: Success rates, response tracking, detailed reports
- **Live Monitoring**: Session progress and application status updates

## 🚀 **Quick Start**

### 1. **Installation**
```bash
# Clone repository
git clone https://github.com/your-username/ai-job-autopilot.git
cd ai-job-autopilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. **Configuration**
Create a `.env` file in the project root:
```bash
# Required: AI Provider API Keys (at least one)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Required: LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# Optional: Email notifications
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_app_specific_password
```

### 3. **Launch**
```bash
# Start dashboard
streamlit run ui/enhanced_dashboard.py

# Or run CLI version
python launch_autopilot.py
```

## 🏗️ **Project Architecture**

```
ai-job-autopilot/
├── 🤖 Core AI Components
│   ├── ai_question_answerer.py      # Multi-LLM question answering
│   ├── dynamic_resume_rewriter.py   # AI resume optimization
│   ├── smart_duplicate_detector.py  # Duplicate job detection
│   └── intelligent_job_matcher.py   # AI job matching
│
├── 🔧 Automation Engine
│   ├── enhanced_linkedin_autopilot.py  # Main LinkedIn automation
│   ├── universal_form_handler.py      # Universal form processing
│   ├── undetected_browser.py          # Stealth browser automation
│   ├── working_linkedin_apply.py      # LinkedIn application logic
│   └── robust_linkedin_apply.py       # Robust application handling
│
├── 🌐 Web Scrapers
│   ├── smart_scraper/
│   │   ├── linkedin_scraper.py       # LinkedIn job scraping
│   │   ├── indeed_scraper.py         # Indeed integration
│   │   ├── glassdoor_scraper.py      # Glassdoor scraping
│   │   └── job_scraper.py           # Universal job scraper
│   └── universal_job_scraper.py      # Multi-platform scraper
│
├── 🖥️ User Interface
│   ├── ui/
│   │   ├── enhanced_dashboard.py     # Main Streamlit dashboard
│   │   ├── ultimate_job_dashboard.py # Advanced dashboard
│   │   └── dashboard_ui.py          # Basic dashboard UI
│   └── launch_autopilot.py          # CLI launcher
│
├── ⚙️ Configuration & Management
│   ├── config_manager.py            # Configuration management
│   ├── notification_system.py       # Multi-channel notifications
│   └── integration_layer.py         # System integration
│
├── 🧪 Testing Framework
│   ├── test_suite.py               # Main test suite
│   ├── integration_test_suite.py   # Integration tests
│   ├── comprehensive_test_suite.py # Full test coverage
│   └── tests/                      # Test modules
│
├── 📁 Configuration
│   ├── config/                     # Configuration files
│   ├── .env.example               # Environment template
│   └── requirements.txt           # Python dependencies
│
└── 📊 Additional Tools
    ├── parser/                     # Resume parsing utilities
    ├── worker/                     # Background workers
    └── extensions/                 # Feature extensions
```

## 🖥️ **Dashboard Features**

### **Main Dashboard**
- Real-time application tracking and metrics
- Interactive charts and performance analytics
- Session management (start/pause/resume/stop)
- System health monitoring

### **AI Question Answering**
- Test AI responses for different job contexts
- Switch between OpenAI and Anthropic models
- View cached responses and usage statistics

### **Resume Optimization**
- Upload and optimize resumes for specific jobs
- AI-powered similarity scoring
- Dynamic resume rewriting based on job requirements

### **Duplicate Detection**
- Semantic analysis to prevent redundant applications
- Application history management
- Intelligent job matching and filtering

### **Configuration Management**
- Secure credential storage
- AI provider settings
- Automation behavior controls

## 💻 **Usage Examples**

### **Basic LinkedIn Automation**
```bash
# Run LinkedIn job application automation
python enhanced_linkedin_autopilot.py

# Or use the launcher
python launch_autopilot.py
```

### **Using AI Question Answering**
```python
from ai_question_answerer import AIQuestionAnswerer

qa = AIQuestionAnswerer()
answer = qa.answer_question(
    "Why do you want this job?",
    job_context={"title": "Software Engineer", "company": "TechCorp"}
)
print(answer.answer)
```

### **Resume Optimization**
```python
from dynamic_resume_rewriter import DynamicResumeRewriter

rewriter = DynamicResumeRewriter()
optimized = rewriter.create_optimized_resume(
    job_title="Python Developer",
    company="Example Corp",
    job_description="Python development with Django and ML"
)
print(f"Similarity Score: {optimized.similarity_score:.1%}")
```

## ⚙️ **Configuration**

### **Environment Variables**
Create a `.env` file with the following variables:

```bash
# AI Provider API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# LinkedIn Credentials (required)
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# Email Notifications (optional)
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# Additional Settings (optional)
MAX_APPLICATIONS_PER_SESSION=10
APPLICATION_DELAY_SECONDS=30
ENABLE_STEALTH_MODE=true
```

### **YAML Configuration**
The system uses YAML files in the `config/` directory for advanced settings:

- `config/main_config.yaml` - Main configuration
- `config/user_profile.yaml` - User profile and preferences
- `config/job_preferences.yaml` - Job search parameters

## 🧪 **Testing**

Run the test suite to verify your installation:

```bash
# Run basic tests
python test_suite.py

# Run comprehensive tests
python comprehensive_test_suite.py

# Run integration tests
python integration_test_suite.py

# Test specific components
python -m pytest tests/ -v
```

## 🚨 **Troubleshooting**

### **Common Issues**
- **Browser fails to start**: Run `playwright install` to install browser dependencies
- **AI API errors**: Check your API keys in `.env` file
- **LinkedIn login issues**: Verify credentials and check for 2FA
- **Permission errors**: Ensure proper file permissions for config directory

### **Debug Mode**
Enable debug logging by setting:
```bash
export DEBUG=true
python enhanced_linkedin_autopilot.py
```

## 📜 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ **Disclaimer**

This tool is for personal job search automation. Users must:
- Respect platform terms of service
- Use accurate personal information
- Maintain professional standards
- Follow applicable laws and regulations

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/your-username/ai-job-autopilot/issues)
- **Documentation**: [Project Wiki](https://github.com/your-username/ai-job-autopilot/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-job-autopilot/discussions)

---

**⭐ Star this repository if it helps you land your dream job!**
