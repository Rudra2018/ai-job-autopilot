#!/usr/bin/env python3
"""
🚀 AI Job Autopilot - Main Application
Professional AI-powered job application system with multi-agent orchestration
"""

import sys
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import orchestration system
try:
    from src.orchestration import StreamlitOrchestrationUI, add_orchestration_to_main_app
    ORCHESTRATION_AVAILABLE = True
except ImportError as e:
    print(f"Orchestration system not available: {e}")
    ORCHESTRATION_AVAILABLE = False

def initialize_ankit_profile():
    """Initialize Ankit Thakur's professional profile"""
    if 'ankit_profile' not in st.session_state:
        st.session_state.ankit_profile = {
            "personal_info": {
                "full_name": os.getenv("USER_FULL_NAME", "Ankit Thakur"),
                "email": os.getenv("USER_EMAIL", "ankit.thakur@gmail.com"),
                "phone": os.getenv("USER_PHONE", "+91 98765 43210"),
                "location": os.getenv("USER_LOCATION", "Bangalore, India"),
                "linkedin": os.getenv("USER_LINKEDIN_URL", "linkedin.com/in/ankitthakur"),
                "github": os.getenv("USER_GITHUB_URL", "github.com/ankitthakur")
            },
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp India",
                    "duration": "2021-Present",
                    "location": "Bangalore, India",
                    "description": "Full-stack development with Python, React, AWS"
                },
                {
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "duration": "2019-2021", 
                    "location": "Remote",
                    "description": "Backend development with Django and PostgreSQL"
                }
            ],
            "skills": {
                "programming": ["Python", "JavaScript", "TypeScript", "Java"],
                "frameworks": ["React", "Django", "Node.js", "FastAPI"],
                "cloud": ["AWS", "Docker", "Kubernetes"],
                "databases": ["PostgreSQL", "MongoDB", "Redis"]
            },
            "education": [
                {
                    "degree": "B.Tech Computer Science",
                    "institution": "Indian Institute of Technology",
                    "year": "2019"
                }
            ],
            "years_experience": float(os.getenv("YEARS_EXPERIENCE", "5.5")),
            "seniority_level": os.getenv("SENIORITY_LEVEL", "Senior")
        }
    
    # Default credentials setup
    if 'default_credentials' not in st.session_state:
        preferred_locations = os.getenv("PREFERRED_LOCATIONS", "Remote,Bangalore,Hyderabad,Pune").split(",")
        target_job_titles = os.getenv("TARGET_JOB_TITLES", "Senior Software Engineer,Full Stack Developer,Backend Engineer,Python Developer,Tech Lead").split(",")
        
        st.session_state.default_credentials = {
            "linkedin_email": os.getenv("LINKEDIN_EMAIL", "ankit.thakur@gmail.com"),
            "linkedin_password": os.getenv("LINKEDIN_PASSWORD", ""),
            "indeed_email": os.getenv("INDEED_EMAIL", "ankit.thakur@gmail.com"), 
            "indeed_password": os.getenv("INDEED_PASSWORD", ""),
            "job_preferences": {
                "preferred_locations": preferred_locations,
                "job_titles": target_job_titles,
                "min_salary": int(os.getenv("MINIMUM_SALARY", "1500000")),
                "job_type": os.getenv("PREFERRED_WORK_TYPE", "Full-time"),
                "remote_preferred": os.getenv("PREFERRED_WORK_TYPE", "Remote") == "Remote"
            }
        }

def main():
    """Main application entry point"""
    # Set page config first
    try:
        st.set_page_config(
            page_title="AI Job Autopilot - Ankit Thakur",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except:
        pass  # Already configured
    
    # Initialize Ankit's profile
    initialize_ankit_profile()
    
    # Check for required dependencies
    missing_deps = []
    required_modules = ['streamlit', 'pandas', 'plotly']
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    if missing_deps:
        st.error(f"Missing required dependencies: {', '.join(missing_deps)}")
        st.info("Install with: pip install streamlit pandas plotly")
        st.code("pip install streamlit pandas plotly")
        return
    
    # Display header
    st.markdown("""
    # 🚀 AI Job Autopilot - Ankit Thakur's Profile
    Professional AI-powered job application system with multi-agent orchestration
    """)
    
    # Check for orchestration mode
    if ORCHESTRATION_AVAILABLE:
        orchestration_enabled = add_orchestration_to_main_app()
        if orchestration_enabled:
            return  # Orchestration UI takes over
    
    # Priority order: Premium UI -> Enhanced Dashboard -> AI Dashboard
    ui_loaded = False
    
    # Try Premium UI first (most feature-complete)
    if not ui_loaded:
        try:
            from ui.premium_ui import main as run_premium_ui
            st.success("✅ Loading Premium AI Dashboard...")
            run_premium_ui()
            ui_loaded = True
        except ImportError as e:
            st.warning(f"Premium UI not available: {e}")
        except Exception as e:
            st.error(f"Premium UI error: {e}")
    
    # Fallback to Enhanced Dashboard
    if not ui_loaded:
        try:
            from ui.enhanced_dashboard import main as run_enhanced_ui
            st.info("📊 Loading Enhanced Dashboard...")
            run_enhanced_ui()
            ui_loaded = True
        except ImportError as e:
            st.warning(f"Enhanced Dashboard not available: {e}")
        except Exception as e:
            st.error(f"Enhanced Dashboard error: {e}")
    
    # Fallback to AI Dashboard
    if not ui_loaded:
        try:
            from ui.ai_job_dashboard import main as run_ai_dashboard
            st.info("🤖 Loading AI Dashboard...")
            run_ai_dashboard()
            ui_loaded = True
        except ImportError as e:
            st.warning(f"AI Dashboard not available: {e}")
        except Exception as e:
            st.error(f"AI Dashboard error: {e}")
    
    # Final fallback - basic interface
    if not ui_loaded:
        st.error("⚠️ No dashboard modules available")
        st.markdown("""
        ## 📋 Profile Summary
        **Name:** Ankit Thakur  
        **Email:** ankit.thakur@gmail.com  
        **Experience:** 5.5 years  
        **Role:** Senior Software Engineer  
        **Skills:** Python, JavaScript, React, Django, AWS
        
        ## 🔧 Setup Required
        Install dependencies:
        ```bash
        pip install streamlit pandas plotly
        ```
        
        ## 📁 Available UI Modules
        - `ui/premium_ui.py` - Premium Dashboard
        - `ui/enhanced_dashboard.py` - Enhanced Dashboard  
        - `ui/ai_job_dashboard.py` - AI Dashboard
        """)
        
        # Basic profile display
        profile = st.session_state.ankit_profile
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Personal Information")
            personal = profile["personal_info"]
            st.write(f"**Name:** {personal['full_name']}")
            st.write(f"**Email:** {personal['email']}")
            st.write(f"**Phone:** {personal['phone']}")
            st.write(f"**Location:** {personal['location']}")
        
        with col2:
            st.subheader("💼 Experience")
            st.write(f"**Years:** {profile['years_experience']}")
            st.write(f"**Level:** {profile['seniority_level']}")
            st.write(f"**Current Role:** {profile['experience'][0]['title']}")
            st.write(f"**Company:** {profile['experience'][0]['company']}")
        
        # Skills
        st.subheader("🛠️ Technical Skills")
        skills = profile["skills"]
        for category, skill_list in skills.items():
            st.write(f"**{category.title()}:** {', '.join(skill_list)}")
        
        # Job preferences
        st.subheader("🎯 Job Preferences")
        prefs = st.session_state.default_credentials["job_preferences"]
        st.write(f"**Preferred Roles:** {', '.join(prefs['job_titles'])}")
        st.write(f"**Locations:** {', '.join(prefs['preferred_locations'])}")
        st.write(f"**Salary:** ₹{prefs['min_salary']:,} per annum")
        st.write(f"**Remote Work:** {'Yes' if prefs['remote_preferred'] else 'No'}")
        
        st.info("💡 Install the required dependencies to access the full AI-powered dashboard!")
    
    return ui_loaded

if __name__ == "__main__":
    main()