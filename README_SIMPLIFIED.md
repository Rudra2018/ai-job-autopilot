# 🚀 AI Job Autopilot - Simplified Version

**Easy-to-use automated job application system with resume upload and intelligent matching.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 **What's New in the Simplified Version**

### ✅ **Simplified Setup**
- **No Complex Configuration**: No more `.env` files or complex YAML configs
- **Resume Upload Interface**: Just drag and drop your resume to get started
- **Automatic Parsing**: Extracts name, skills, experience, and contact info automatically
- **One-Click Launch**: Simple `python run.py` to start the application

### 🎨 **Modern UI**
- **Clean Streamlit Interface**: Beautiful, responsive web interface
- **Real-time Progress**: Live updates on job searches and applications
- **Interactive Dashboard**: Visual metrics and status monitoring
- **Mobile-Friendly**: Works on desktop and mobile browsers

### 🚀 **Quick Start (3 Steps)**

1. **Install Dependencies**
   ```bash
   pip install streamlit pandas plotly requests beautifulsoup4 selenium PyPDF2 python-docx
   ```

2. **Launch Application**
   ```bash
   python run.py
   ```
   Or manually:
   ```bash
   streamlit run main.py
   ```

3. **Upload Resume & Start**
   - Open http://localhost:8501 in your browser
   - Upload your resume (PDF, DOCX, or TXT)
   - Set job preferences
   - Click "Start Job Hunt"

## 📋 **Core Features**

### 📄 **Smart Resume Processing**
- **Multiple Format Support**: PDF, DOCX, and TXT files
- **Automatic Extraction**: Skills, experience, education, contact info
- **Fallback Processing**: Works even with complex resume layouts
- **Profile Management**: Saves your parsed profile for future use

### 🎯 **Job Preferences**
- **Job Titles**: Multiple role types (Software Engineer, Developer, etc.)
- **Locations**: Remote, specific cities, or flexible locations
- **Experience Level**: Entry, Mid, Senior, Executive
- **Salary Range**: Customizable salary expectations
- **Job Type**: Full-time, Part-time, Contract, Remote

### 🤖 **Automation Features**
- **Multi-Platform Search**: LinkedIn, Indeed, Glassdoor
- **Rate Limiting**: Configurable application limits to avoid detection
- **Smart Delays**: Human-like timing between actions
- **Progress Tracking**: Real-time status updates and statistics

## 💻 **System Requirements**

- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum
- **Storage**: 500MB free space
- **Browser**: Chrome/Chromium for web automation
- **Internet**: Stable connection for job board access

## 📦 **Installation Options**

### **Basic Installation (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd ai-job-autopilot

# Install core dependencies
pip install streamlit pandas plotly requests beautifulsoup4 selenium PyPDF2 python-docx

# Launch the application
python run.py
```

### **Full Installation (All Features)**
```bash
# Install all dependencies (including optional AI features)
pip install -r requirements.txt

# For AI-enhanced features, you can optionally configure:
# - OpenAI API key (for GPT-based optimization)
# - Anthropic API key (for Claude assistance)
# - Google API key (for Gemini features)
```

## 🎮 **How to Use**

### **Step 1: Setup Profile**
1. Launch the application with `python run.py`
2. Open your browser to http://localhost:8501
3. Upload your resume using the sidebar file uploader
4. Click "Parse Resume" to extract your information
5. Review and adjust the extracted details if needed

### **Step 2: Configure Preferences**
1. Set your desired job titles (comma-separated)
2. Choose preferred locations
3. Select experience level and job type
4. Set salary range using the slider
5. Configure automation settings (optional)

### **Step 3: Start Job Hunting**
1. Click "Start Job Hunt" in the sidebar
2. Monitor progress in real-time on the dashboard
3. View found jobs and application status
4. Pause or stop automation as needed

## 📊 **Dashboard Features**

### **Profile Summary**
- Your parsed contact information
- Skills overview
- Job preferences display

### **Live Statistics**
- Jobs found counter
- Applications sent tracker
- Success rate metrics
- Real-time activity log

### **Progress Monitoring**
- Current automation status
- Search progress indicator
- Platform-specific results
- Error reporting and handling

## ⚙️ **Configuration**

The simplified version uses a JSON-based configuration system that's automatically managed through the UI:

- **user_config.json**: Stores your profile and preferences
- **No .env files**: All configuration through the web interface
- **Auto-save**: Changes are saved automatically
- **Reset option**: Easy profile reset if needed

## 🔧 **Advanced Features (Optional)**

### **AI Enhancement**
If you want AI-powered features, you can configure API keys in the UI:
- **Resume optimization** based on job descriptions
- **Smart application answers** for common questions
- **Job matching intelligence** for better targeting

### **Custom Automation**
- **Rate limiting**: Prevent platform restrictions
- **Custom delays**: Mimic human behavior
- **Platform selection**: Choose which job boards to use
- **Notification system**: Email alerts for applications

## 📁 **File Structure**
```
ai-job-autopilot/
├── main.py                          # Main application entry
├── run.py                           # Quick launcher script
├── requirements.txt                 # Essential dependencies
├── ui/
│   └── modern_job_autopilot_ui.py  # Modern Streamlit UI
├── simplified_resume_parser.py      # Resume parsing without complex deps
├── simple_config.py                # JSON-based configuration
└── user_config.json               # Your profile data (auto-generated)
```

## 🚨 **Removed Complexity**

### **What We Simplified**
- ❌ Complex `.env` files → ✅ Simple UI configuration
- ❌ YAML configuration files → ✅ JSON auto-save
- ❌ Manual setup steps → ✅ One-click launch
- ❌ Heavy AI dependencies → ✅ Optional advanced features
- ❌ Complex CLI interfaces → ✅ Modern web UI

### **Files Removed**
- `demo_*.py` - Demo files
- `ci_cd_*.py` - CI/CD configurations
- `test_*.py` - Complex test suites
- `.env` files - Environment configurations
- Multiple launcher scripts - Consolidated to one

## 🛠️ **Troubleshooting**

### **Common Issues**
1. **Import Errors**: Install missing dependencies with pip
2. **Browser Issues**: Ensure Chrome/Chromium is installed
3. **Resume Parsing**: Try different file formats (PDF works best)
4. **Port Conflicts**: App runs on http://localhost:8501

### **Getting Help**
- Check the browser console for error messages
- Review the terminal output for detailed logs
- Ensure all required dependencies are installed
- Try restarting the application

## 🔄 **Migration from Complex Version**

If you were using the previous complex version:
1. **Backup** your old `.env` and config files
2. **Run the new version** with `python run.py`
3. **Upload your resume** to auto-populate profile
4. **Set preferences** using the UI instead of config files
5. **Your old configurations** are automatically backed up as `.env.backup`

## 📝 **Contributing**

We welcome contributions! The simplified version focuses on:
- **User experience improvements**
- **Resume parsing enhancements**
- **Additional job board integrations**
- **UI/UX refinements**

## 📄 **License**

MIT License - See LICENSE file for details.

---

**🎉 Enjoy your simplified, automated job hunting experience!**

For questions or support, please open an issue on the repository.