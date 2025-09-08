# Project Structure

## Current Directory Layout

```
ai-job-autopilot/
├── 📁 Root Files
│   ├── README.md                    # Main project documentation
│   ├── requirements.txt             # Python dependencies
│   ├── LICENSE                      # MIT license
│   ├── .env.example                # Environment template
│   ├── .gitignore                  # Git ignore patterns
│   ├── Dockerfile                   # Docker configuration
│   ├── docker-compose.yml          # Docker compose setup
│   └── PROJECT_STRUCTURE.md        # This file
│
├── 🤖 Core AI Components
│   ├── ai_question_answerer.py      # Multi-LLM question answering
│   ├── dynamic_resume_rewriter.py   # AI resume optimization
│   ├── smart_duplicate_detector.py  # Duplicate job detection
│   ├── intelligent_job_matcher.py   # AI job matching
│   └── advanced_resume_parser.py    # Resume parsing with AI
│
├── 🔧 Automation Engine
│   ├── enhanced_linkedin_autopilot.py  # Main LinkedIn automation
│   ├── universal_form_handler.py      # Universal form processing
│   ├── undetected_browser.py          # Stealth browser automation
│   ├── working_linkedin_apply.py      # LinkedIn application logic
│   ├── robust_linkedin_apply.py       # Robust application handling
│   ├── live_linkedin_apply.py         # Live LinkedIn automation
│   └── auto_form_filler.py           # Intelligent form filling
│
├── 🌐 Web Scrapers & Job Discovery
│   ├── universal_job_scraper.py       # Multi-platform scraper
│   ├── company_career_scraper.py     # Company portal scraper
│   ├── company_portal_scraper.py     # Portal-specific scraping
│   ├── google_job_scraper.py         # Google Jobs integration
│   └── smart_scraper/               # Platform-specific scrapers
│       ├── linkedin_scraper.py       # LinkedIn job scraping
│       ├── indeed_scraper.py         # Indeed integration
│       ├── glassdoor_scraper.py      # Glassdoor scraping
│       ├── monster_scraper.py        # Monster.com scraping
│       ├── angelist_scraper.py       # AngelList integration
│       └── job_scraper.py           # Base scraper class
│
├── 🖥️ User Interface
│   ├── ui/                          # Streamlit dashboards
│   │   ├── enhanced_dashboard.py     # Main dashboard
│   │   ├── ultimate_job_dashboard.py # Advanced dashboard
│   │   └── dashboard_ui.py          # Basic dashboard UI
│   ├── launch_autopilot.py          # CLI launcher
│   ├── launch_enhanced_autopilot.py # Enhanced CLI
│   └── launch_ultimate_autopilot.py # Ultimate CLI
│
├── ⚙️ Configuration & Management
│   ├── config_manager.py            # Configuration management
│   ├── notification_system.py       # Multi-channel notifications
│   ├── integration_layer.py         # System integration
│   ├── job_application_orchestrator.py # Application orchestration
│   └── config/                      # Configuration files
│       ├── main_config.yaml         # Main configuration
│       ├── user_profile.yaml        # User profile
│       └── job_preferences.yaml     # Job search settings
│
├── 🧪 Testing & Quality Assurance
│   ├── test_suite.py               # Main test suite
│   ├── integration_test_suite.py   # Integration tests
│   ├── comprehensive_test_suite.py # Full test coverage
│   ├── ui_automation_tests.py      # UI testing
│   ├── performance_load_testing.py # Performance tests
│   ├── ci_cd_testing_workflow.py   # CI/CD pipeline tests
│   ├── master_test_runner.py       # Test runner
│   ├── test_linkedin_login.py      # LinkedIn login tests
│   ├── validate_setup.py           # Setup validation
│   └── tests/                      # Test modules directory
│
├── 📊 Analytics & Monitoring
│   ├── scraping_analytics_monitor.py # Scraping analytics
│   ├── show_global_stats.py         # Global statistics
│   ├── proxy_rotation_system.py     # Proxy management
│   └── enhanced_mock_scenarios.py   # Mock testing scenarios
│
├── 📁 Organized Source Structure (New)
│   └── src/                         # Organized source code
│       ├── core/                    # Core functionality
│       ├── ai/                      # AI components
│       ├── automation/              # Automation modules
│       ├── scrapers/                # Scraping modules
│       ├── ui/                      # UI components
│       │   ├── components/          # Reusable UI components
│       │   └── pages/              # Dashboard pages
│       └── utils/                   # Utility functions
│
├── 📊 Data & Storage
│   ├── data/                        # Application data
│   │   ├── logs/                   # Log files
│   │   ├── profiles/               # User profiles
│   │   └── cache/                  # Cached data
│   └── ml_models/                  # ML models
│       └── jobbert_v3/            # JobBERT model files
│
├── 🔧 Additional Tools & Extensions
│   ├── parser/                      # Resume parsing utilities
│   ├── worker/                      # Background workers
│   ├── extensions/                  # Feature extensions
│   ├── backend/                     # Backend services
│   └── gcp_pipeline/               # Google Cloud Pipeline
│
├── 📚 Documentation & Scripts
│   ├── docs/                        # Documentation
│   ├── scripts/                     # Utility scripts
│   ├── SETUP.md                    # Setup instructions
│   ├── TESTING_SUITE_SUMMARY.md   # Testing documentation
│   ├── setup.sh                   # Linux/Mac setup script
│   ├── setup.bat                  # Windows setup script
│   └── run.sh                     # Run script
│
└── 🎯 Demo & Examples
    ├── demo_ultimate_features.py    # Feature demonstrations
    ├── simple_easy_apply_demo.py   # Simple demo
    ├── ultimate_job_autopilot.py   # Ultimate version
    └── perfect_job_autopilot.py    # Perfect version
```

## File Categories

### 🤖 AI & Machine Learning
- AI question answering and response generation
- Resume optimization and parsing
- Job matching and duplicate detection
- Semantic analysis and similarity scoring

### 🔧 Automation & Browser Control
- LinkedIn automation and form filling
- Stealth browser operations
- Universal form handling
- Multi-platform application automation

### 🌐 Web Scraping & Data Collection
- Multi-platform job scrapers
- Company portal integration
- Job discovery and data extraction
- Search result processing

### 🖥️ User Interface & Experience
- Streamlit dashboards and analytics
- Command-line interfaces
- Real-time monitoring and progress tracking
- Interactive configuration tools

### 🧪 Testing & Quality
- Comprehensive test suites
- Integration and end-to-end testing
- Performance and load testing
- Setup validation and diagnostics

### ⚙️ Configuration & Management
- Environment and credential management
- Notification systems
- System integration and orchestration
- User profile and preference management

## Recommended Migration Path

To improve the project organization:

1. **Gradually move core modules to `src/` structure**
2. **Consolidate similar functionality into packages**
3. **Implement proper module imports and dependencies**
4. **Update documentation and setup scripts**
5. **Maintain backward compatibility during migration**

## Best Practices

- Keep configuration files in `config/` directory
- Store data and logs in `data/` directory
- Use `src/` for organized source code
- Keep tests in `tests/` directory
- Document all major components
- Follow Python packaging conventions