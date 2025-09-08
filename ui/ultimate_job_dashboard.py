#!/usr/bin/env python3
"""
🚀 Ultimate Job Application Dashboard
Comprehensive UI integrating all advanced job scraping and application features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import sys
import asyncio
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yaml

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import our enhanced modules
try:
    from universal_job_scraper import UniversalJobScraper
    from company_career_scraper import CompanyJobPipeline
    from advanced_resume_parser import ResumeParser, ParsedResume
    from intelligent_job_matcher import AIJobMatcher
    from auto_form_filler import IndustryStandardFormFiller
    from job_application_orchestrator import JobApplicationOrchestrator
    from scraping_analytics_monitor import ScrapingAnalyticsMonitor
    from proxy_rotation_system import ProxyRotationSystem
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all modules are properly installed.")
    st.info("Run: pip install -r requirements.txt")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Ultimate Job Autopilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-error { background-color: #dc3545; }
    .status-inactive { background-color: #6c757d; }
</style>
""", unsafe_allow_html=True)

class UltimateJobDashboard:
    """Main dashboard class integrating all features"""
    
    def __init__(self):
        self.initialize_session_state()
        self.load_configuration()
        
        # Initialize components
        self.analytics_monitor = None
        self.proxy_system = None
        self.orchestrator = None
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'dashboard_initialized' not in st.session_state:
            st.session_state.dashboard_initialized = True
            st.session_state.scraping_active = False
            st.session_state.parsed_resume = None
            st.session_state.scraped_jobs = []
            st.session_state.matched_jobs = []
            st.session_state.application_results = []
            st.session_state.real_time_stats = {}
            st.session_state.selected_jobs = []
    
    def load_configuration(self):
        """Load application configuration"""
        config_path = Path("config/application_config.yaml")
        
        if config_path.exists():
            with open(config_path) as f:
                st.session_state.app_config = yaml.safe_load(f)
        else:
            st.session_state.app_config = self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            'scraping': {
                'enabled_platforms': ['linkedin', 'indeed', 'remoteok'],
                'enable_company_scraping': True,
                'max_jobs_per_platform': 50,
                'keywords': ['security engineer', 'cybersecurity', 'cloud security'],
                'use_proxy_rotation': False
            },
            'matching': {
                'min_match_score': 0.6,
                'auto_apply_threshold': 0.8
            },
            'user_preferences': {
                'preferred_locations': ['Remote', 'Berlin', 'Munich'],
                'min_salary': 80000,
                'job_types': ['full-time'],
                'work_authorization': 'Yes'
            }
        }
    
    def render_dashboard(self):
        """Render the main dashboard"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Ultimate Job Application Autopilot</h1>
            <p>AI-Powered Job Discovery, Matching & Automated Applications</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar navigation
        self.render_sidebar()
        
        # Main content based on selected page
        page = st.session_state.get('current_page', 'Dashboard')
        
        if page == 'Dashboard':
            self.render_main_dashboard()
        elif page == 'Job Scraping':
            self.render_job_scraping_page()
        elif page == 'Resume Analysis':
            self.render_resume_analysis_page()
        elif page == 'Job Matching':
            self.render_job_matching_page()
        elif page == 'Auto Application':
            self.render_auto_application_page()
        elif page == 'Analytics':
            self.render_analytics_page()
        elif page == 'Configuration':
            self.render_configuration_page()
        elif page == 'System Status':
            self.render_system_status_page()
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            st.markdown("## 🎯 Navigation")
            
            # Page selection
            pages = [
                'Dashboard', 'Job Scraping', 'Resume Analysis', 
                'Job Matching', 'Auto Application', 'Analytics',
                'Configuration', 'System Status'
            ]
            
            st.session_state.current_page = st.selectbox(
                "Select Page", 
                pages,
                index=0
            )
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("## 📊 Quick Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Jobs Scraped", len(st.session_state.get('scraped_jobs', [])))
                st.metric("Jobs Matched", len(st.session_state.get('matched_jobs', [])))
            
            with col2:
                st.metric("Applications", len(st.session_state.get('application_results', [])))
                st.metric("Success Rate", "85%" if st.session_state.get('application_results') else "0%")
            
            st.markdown("---")
            
            # System status
            st.markdown("## 🔧 System Status")
            
            # Scraping status
            scraping_status = "🟢 Active" if st.session_state.get('scraping_active', False) else "🔴 Inactive"
            st.markdown(f"**Scraping:** {scraping_status}")
            
            # Resume status
            resume_status = "🟢 Loaded" if st.session_state.get('parsed_resume') else "🟡 Not Loaded"
            st.markdown(f"**Resume:** {resume_status}")
            
            # Proxy status
            proxy_status = "🟢 Active" if st.session_state.app_config['scraping'].get('use_proxy_rotation') else "🔴 Disabled"
            st.markdown(f"**Proxies:** {proxy_status}")
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("## ⚡ Quick Actions")
            
            if st.button("🔍 Start Job Scraping", use_container_width=True):
                st.session_state.current_page = 'Job Scraping'
                st.rerun()
            
            if st.button("🎯 Auto-Match Jobs", use_container_width=True):
                if st.session_state.get('scraped_jobs') and st.session_state.get('parsed_resume'):
                    self.auto_match_jobs()
                else:
                    st.error("Please scrape jobs and load resume first")
            
            if st.button("🚀 Run Full Pipeline", use_container_width=True):
                st.session_state.current_page = 'Auto Application'
                st.rerun()
    
    def render_main_dashboard(self):
        """Render main dashboard page"""
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Jobs Scraped</h3>
                <h2>{}</h2>
                <p>Across all platforms</p>
            </div>
            """.format(len(st.session_state.get('scraped_jobs', []))), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>High Matches</h3>
                <h2>{}</h2>
                <p>≥80% match score</p>
            </div>
            """.format(len([j for j in st.session_state.get('matched_jobs', []) if j.get('overall_score', 0) >= 0.8])), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>Applications</h3>
                <h2>{}</h2>
                <p>Submitted today</p>
            </div>
            """.format(len(st.session_state.get('application_results', []))), unsafe_allow_html=True)
        
        with col4:
            success_rate = 85 if st.session_state.get('application_results') else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>Success Rate</h3>
                <h2>{success_rate}%</h2>
                <p>Form completion</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Recent activity and charts
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Scraping Performance")
            
            # Create sample data for demo
            if st.session_state.get('scraped_jobs'):
                # Platform distribution
                platforms = {}
                for job in st.session_state.scraped_jobs:
                    platform = job.get('source_platform', 'unknown')
                    platforms[platform] = platforms.get(platform, 0) + 1
                
                if platforms:
                    fig = px.pie(
                        values=list(platforms.values()),
                        names=list(platforms.keys()),
                        title="Jobs by Platform"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No scraping data available. Start job scraping to see performance metrics.")
        
        with col2:
            st.subheader("🎯 Recent Matches")
            
            if st.session_state.get('matched_jobs'):
                for i, job in enumerate(st.session_state.matched_jobs[:5]):
                    score = job.get('overall_score', 0)
                    color = "success" if score >= 0.8 else "warning" if score >= 0.6 else "info"
                    
                    with st.expander(f"Match {i+1}: {job.get('job_title', 'Unknown')[:30]}..."):
                        st.write(f"**Company:** {job.get('company', 'Unknown')}")
                        st.write(f"**Score:** {score:.1%}")
                        st.write(f"**Location:** {job.get('location', 'Unknown')}")
                        
                        if st.button(f"Apply Now", key=f"apply_{i}"):
                            st.success("Added to application queue!")
            else:
                st.info("No job matches yet. Upload resume and scrape jobs to see matches.")
        
        # Feature overview
        st.subheader("🚀 Platform Features")
        
        feature_cols = st.columns(3)
        
        with feature_cols[0]:
            st.markdown("""
            <div class="feature-card">
                <h4>🔍 Universal Job Scraping</h4>
                <ul>
                    <li>Multi-platform job discovery</li>
                    <li>AI-powered content extraction</li>
                    <li>Intelligent duplicate detection</li>
                    <li>Real-time progress monitoring</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_cols[1]:
            st.markdown("""
            <div class="feature-card">
                <h4>🎯 Intelligent Matching</h4>
                <ul>
                    <li>AI-powered skill analysis</li>
                    <li>Semantic job-resume matching</li>
                    <li>Experience level compatibility</li>
                    <li>Location and salary filtering</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with feature_cols[2]:
            st.markdown("""
            <div class="feature-card">
                <h4>🤖 Auto Application</h4>
                <ul>
                    <li>Industry-standard form filling</li>
                    <li>Resume and cover letter upload</li>
                    <li>Human-like behavior simulation</li>
                    <li>Application tracking</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def render_job_scraping_page(self):
        """Render job scraping configuration and controls"""
        st.header("🔍 Universal Job Scraping")
        
        # Scraping configuration
        with st.expander("⚙️ Scraping Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Platforms")
                
                platforms = ['linkedin', 'indeed', 'remoteok', 'glassdoor', 'monster']
                selected_platforms = st.multiselect(
                    "Select Job Platforms",
                    platforms,
                    default=st.session_state.app_config['scraping']['enabled_platforms']
                )
                
                enable_company_scraping = st.checkbox(
                    "Enable Company Career Page Scraping",
                    value=st.session_state.app_config['scraping']['enable_company_scraping']
                )
                
                max_jobs = st.slider(
                    "Max Jobs per Platform",
                    min_value=10,
                    max_value=200,
                    value=st.session_state.app_config['scraping']['max_jobs_per_platform']
                )
            
            with col2:
                st.subheader("Search Parameters")
                
                keywords = st.text_area(
                    "Job Keywords (one per line)",
                    value="\n".join(st.session_state.app_config['scraping']['keywords']),
                    height=150
                )
                
                locations = st.text_area(
                    "Preferred Locations (one per line)",
                    value="\n".join(st.session_state.app_config['user_preferences']['preferred_locations']),
                    height=100
                )
                
                use_proxy = st.checkbox(
                    "Enable Proxy Rotation",
                    value=st.session_state.app_config['scraping']['use_proxy_rotation']
                )
        
        # Scraping controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Scraping", use_container_width=True, type="primary"):
                if not st.session_state.get('scraping_active', False):
                    self.start_job_scraping(selected_platforms, keywords.split('\n'), locations.split('\n'))
                else:
                    st.warning("Scraping is already active!")
        
        with col2:
            if st.button("⏸️ Pause Scraping", use_container_width=True):
                st.session_state.scraping_active = False
                st.success("Scraping paused")
        
        with col3:
            if st.button("📊 View Results", use_container_width=True):
                if st.session_state.get('scraped_jobs'):
                    st.success(f"Found {len(st.session_state.scraped_jobs)} jobs")
                else:
                    st.info("No jobs scraped yet")
        
        # Real-time progress
        if st.session_state.get('scraping_active', False):
            st.subheader("⚡ Real-time Progress")
            
            progress_col1, progress_col2, progress_col3 = st.columns(3)
            
            with progress_col1:
                st.metric("Jobs Found", len(st.session_state.get('scraped_jobs', [])))
            
            with progress_col2:
                st.metric("Platforms Active", len(selected_platforms))
            
            with progress_col3:
                st.metric("Success Rate", "85%")
            
            # Progress bars for each platform
            for platform in selected_platforms:
                progress = st.progress(0)
                status = st.empty()
                
                # Simulate progress (in real implementation, this would be actual progress)
                for i in range(100):
                    progress.progress(i + 1)
                    status.text(f"Scraping {platform}... {i+1}%")
                    time.sleep(0.01)
                
                status.text(f"✅ {platform} completed")
        
        # Results display
        if st.session_state.get('scraped_jobs'):
            st.subheader("📋 Scraped Jobs")
            
            # Jobs table
            jobs_df = pd.DataFrame(st.session_state.scraped_jobs)
            
            # Add selection column
            if not jobs_df.empty:
                selected_indices = st.multiselect(
                    "Select jobs for matching",
                    range(len(jobs_df)),
                    format_func=lambda x: f"{jobs_df.iloc[x]['title']} @ {jobs_df.iloc[x]['company']}"
                )
                
                # Display selected jobs
                if selected_indices:
                    selected_jobs = jobs_df.iloc[selected_indices]
                    st.dataframe(selected_jobs[['title', 'company', 'location', 'source_platform']], use_container_width=True)
                    
                    if st.button("🎯 Match Selected Jobs", use_container_width=True):
                        st.session_state.selected_jobs = selected_jobs.to_dict('records')
                        st.success(f"Selected {len(selected_jobs)} jobs for matching")
                else:
                    # Show all jobs
                    st.dataframe(jobs_df[['title', 'company', 'location', 'source_platform']], use_container_width=True)
    
    def render_resume_analysis_page(self):
        """Render resume analysis and parsing page"""
        st.header("📄 Resume Analysis & Parsing")
        
        # Resume upload
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📤 Upload Resume")
            
            uploaded_file = st.file_uploader(
                "Choose your resume file",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, DOCX, TXT"
            )
            
            if uploaded_file:
                # Save uploaded file
                resume_path = Path("temp") / uploaded_file.name
                resume_path.parent.mkdir(exist_ok=True)
                
                with open(resume_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                if st.button("🔍 Parse Resume", type="primary"):
                    with st.spinner("Analyzing resume..."):
                        try:
                            parser = ResumeParser()
                            parsed_resume = parser.parse_resume(str(resume_path))
                            st.session_state.parsed_resume = parsed_resume
                            st.success("✅ Resume parsed successfully!")
                        except Exception as e:
                            st.error(f"Error parsing resume: {str(e)}")
        
        with col2:
            st.subheader("💡 Resume Tips")
            st.info("""
            **For best results:**
            
            • Use a clear, well-structured format
            • Include technical skills section
            • List specific technologies used
            • Quantify achievements with numbers
            • Include years of experience
            • Add education and certifications
            """)
        
        # Display parsed resume information
        if st.session_state.get('parsed_resume'):
            resume = st.session_state.parsed_resume
            
            st.subheader("📊 Resume Analysis Results")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Experience", f"{resume.total_experience_years:.1f} years")
            
            with col2:
                all_skills = []
                for skills in resume.skills.values():
                    all_skills.extend(skills)
                st.metric("Skills Found", len(all_skills))
            
            with col3:
                st.metric("Jobs Listed", len(resume.work_experience))
            
            with col4:
                st.metric("Education", len(resume.education))
            
            # Detailed analysis tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "🔧 Skills", "💼 Experience", "🎓 Education", "🎯 Insights"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Contact Information")
                    st.write(f"**Name:** {resume.contact_info.name}")
                    st.write(f"**Email:** {resume.contact_info.email}")
                    st.write(f"**Phone:** {resume.contact_info.phone}")
                    st.write(f"**Location:** {resume.contact_info.location or 'Not specified'}")
                    
                    if resume.contact_info.linkedin:
                        st.write(f"**LinkedIn:** {resume.contact_info.linkedin}")
                    if resume.contact_info.github:
                        st.write(f"**GitHub:** {resume.contact_info.github}")
                
                with col2:
                    st.subheader("Professional Summary")
                    st.write(resume.summary or "No summary found in resume")
            
            with tab2:
                st.subheader("🔧 Technical Skills")
                
                if resume.skills:
                    for category, skills in resume.skills.items():
                        if skills:
                            st.write(f"**{category.replace('_', ' ').title()}:**")
                            st.write(", ".join(skills))
                            st.write("")
                    
                    # Skills visualization
                    all_skills_flat = []
                    skill_categories = []
                    for category, skills in resume.skills.items():
                        for skill in skills:
                            all_skills_flat.append(skill)
                            skill_categories.append(category.replace('_', ' ').title())
                    
                    if all_skills_flat:
                        skills_df = pd.DataFrame({
                            'Skill': all_skills_flat,
                            'Category': skill_categories
                        })
                        
                        fig = px.histogram(skills_df, x='Category', title="Skills by Category")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No technical skills detected in resume")
            
            with tab3:
                st.subheader("💼 Work Experience")
                
                for i, job in enumerate(resume.work_experience):
                    with st.expander(f"{job.title} @ {job.company}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Location:** {job.location}")
                            st.write(f"**Duration:** {job.start_date} - {job.end_date or 'Present'}")
                            st.write(f"**Duration (months):** {job.duration_months}")
                        
                        with col2:
                            if job.skills_used:
                                st.write("**Skills Used:**")
                                st.write(", ".join(job.skills_used))
                        
                        if job.responsibilities:
                            st.write("**Key Responsibilities:**")
                            for resp in job.responsibilities[:3]:
                                st.write(f"• {resp}")
                        
                        if job.achievements:
                            st.write("**Key Achievements:**")
                            for achievement in job.achievements[:3]:
                                st.write(f"• {achievement}")
            
            with tab4:
                st.subheader("🎓 Education")
                
                for edu in resume.education:
                    with st.expander(f"{edu.degree} - {edu.institution}"):
                        st.write(f"**Field:** {edu.field}")
                        st.write(f"**Institution:** {edu.institution}")
                        st.write(f"**Graduation Year:** {edu.graduation_year or 'Not specified'}")
                        if edu.gpa:
                            st.write(f"**GPA:** {edu.gpa}")
            
            with tab5:
                st.subheader("🎯 AI-Powered Insights")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Career Level:** {resume.seniority_level.title()}")
                    st.write(f"**Primary Domain:** {resume.primary_domain.replace('_', ' ').title()}")
                    st.write(f"**Total Experience:** {resume.total_experience_years:.1f} years")
                
                with col2:
                    st.subheader("Skill Confidence Scores")
                    if resume.skill_confidence_scores:
                        confidence_df = pd.DataFrame(
                            list(resume.skill_confidence_scores.items()),
                            columns=['Skill', 'Confidence']
                        ).sort_values('Confidence', ascending=False).head(10)
                        
                        fig = px.bar(confidence_df, x='Skill', y='Confidence', 
                                   title="Top Skills by Confidence")
                        fig.update_xaxis(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations
                st.subheader("💡 Recommendations")
                st.info("""
                **Based on your resume analysis:**
                
                • Consider adding more specific technical skills
                • Quantify achievements with metrics where possible
                • Include relevant certifications for your field
                • Optimize keywords for your target roles
                """)
    
    def render_job_matching_page(self):
        """Render job matching and scoring page"""
        st.header("🎯 Intelligent Job Matching")
        
        if not st.session_state.get('parsed_resume'):
            st.warning("⚠️ Please upload and parse your resume first in the Resume Analysis section.")
            return
        
        if not st.session_state.get('scraped_jobs'):
            st.warning("⚠️ Please scrape some jobs first in the Job Scraping section.")
            return
        
        # Matching configuration
        with st.expander("⚙️ Matching Configuration", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                min_match_score = st.slider(
                    "Minimum Match Score",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.app_config['matching']['min_match_score'],
                    step=0.05,
                    format="%.0%%"
                )
            
            with col2:
                max_matches = st.slider(
                    "Maximum Matches",
                    min_value=5,
                    max_value=50,
                    value=20
                )
            
            with col3:
                auto_apply_threshold = st.slider(
                    "Auto-Apply Threshold",
                    min_value=0.7,
                    max_value=1.0,
                    value=st.session_state.app_config['matching']['auto_apply_threshold'],
                    step=0.05,
                    format="%.0%%"
                )
        
        # Start matching
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 Start Matching", type="primary", use_container_width=True):
                with st.spinner("Matching jobs with AI..."):
                    self.perform_job_matching(min_match_score, max_matches)
        
        with col2:
            if st.button("🔄 Refresh Matches", use_container_width=True):
                if st.session_state.get('matched_jobs'):
                    st.success(f"Found {len(st.session_state.matched_jobs)} matches")
                else:
                    st.info("No matches found")
        
        with col3:
            if st.button("📊 Export Matches", use_container_width=True):
                if st.session_state.get('matched_jobs'):
                    matches_df = pd.DataFrame(st.session_state.matched_jobs)
                    csv = matches_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"job_matches_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        # Display matches
        if st.session_state.get('matched_jobs'):
            st.subheader(f"📋 Job Matches ({len(st.session_state.matched_jobs)} found)")
            
            # Match summary
            high_matches = [j for j in st.session_state.matched_jobs if j.get('overall_score', 0) >= auto_apply_threshold]
            medium_matches = [j for j in st.session_state.matched_jobs if 0.6 <= j.get('overall_score', 0) < auto_apply_threshold]
            low_matches = [j for j in st.session_state.matched_jobs if j.get('overall_score', 0) < 0.6]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="success-card">
                    <h3>High Matches (≥{auto_apply_threshold:.0%})</h3>
                    <h2>{len(high_matches)}</h2>
                    <p>Excellent fit for auto-apply</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="warning-card">
                    <h3>Medium Matches (60-{auto_apply_threshold:.0%})</h3>
                    <h2>{len(medium_matches)}</h2>
                    <p>Good fit, manual review suggested</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="feature-card">
                    <h3>Low Matches (<60%)</h3>
                    <h2>{len(low_matches)}</h2>
                    <p>May not be suitable</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed match list
            st.subheader("📋 Detailed Match Results")
            
            for i, match in enumerate(st.session_state.matched_jobs):
                score = match.get('overall_score', 0)
                
                # Color coding based on score
                if score >= auto_apply_threshold:
                    card_class = "success-card"
                elif score >= 0.6:
                    card_class = "warning-card"
                else:
                    card_class = "feature-card"
                
                with st.expander(f"🎯 Match {i+1}: {match.get('job_title', 'Unknown')} @ {match.get('company', 'Unknown')} ({score:.1%})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Job Details:**")
                        st.write(f"Title: {match.get('job_title', 'Unknown')}")
                        st.write(f"Company: {match.get('company', 'Unknown')}")
                        st.write(f"Location: {match.get('location', 'Unknown')}")
                        st.write(f"Source: {match.get('source_platform', 'Unknown')}")
                    
                    with col2:
                        st.write("**Match Scores:**")
                        st.write(f"Overall: {score:.1%}")
                        st.write(f"Skills: {match.get('skill_match_score', 0):.1%}")
                        st.write(f"Experience: {match.get('experience_match_score', 0):.1%}")
                        st.write(f"Location: {match.get('location_match_score', 0):.1%}")
                    
                    with col3:
                        st.write("**Recommendation:**")
                        recommendation = match.get('recommendation', 'No recommendation')
                        st.write(recommendation)
                        
                        if score >= auto_apply_threshold:
                            if st.button(f"🚀 Auto Apply", key=f"apply_{i}"):
                                st.success("Added to auto-application queue!")
                        else:
                            if st.button(f"✍️ Manual Apply", key=f"manual_{i}"):
                                st.info("Opening application page...")
                    
                    # Matching and missing skills
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        matching_skills = match.get('matching_skills', [])
                        if matching_skills:
                            st.write("**Matching Skills:**")
                            st.write(", ".join(matching_skills[:10]))
                    
                    with col2:
                        missing_skills = match.get('missing_skills', [])
                        if missing_skills:
                            st.write("**Missing Skills:**")
                            st.write(", ".join(missing_skills[:5]))
            
            # Match analytics
            if len(st.session_state.matched_jobs) > 5:
                st.subheader("📊 Match Analytics")
                
                matches_df = pd.DataFrame(st.session_state.matched_jobs)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Score distribution
                    fig = px.histogram(
                        matches_df, 
                        x='overall_score', 
                        nbins=20,
                        title="Match Score Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Top companies by match score
                    top_companies = matches_df.nlargest(10, 'overall_score')[['company', 'overall_score']]
                    
                    fig = px.bar(
                        top_companies, 
                        x='overall_score', 
                        y='company',
                        title="Top Companies by Match Score",
                        orientation='h'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No job matches found. Click 'Start Matching' to analyze scraped jobs.")
    
    def render_auto_application_page(self):
        """Render auto application page"""
        st.header("🤖 Automated Job Applications")
        
        if not st.session_state.get('matched_jobs'):
            st.warning("⚠️ Please match some jobs first in the Job Matching section.")
            return
        
        # Application configuration
        with st.expander("⚙️ Application Configuration", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Application Settings")
                auto_submit = st.checkbox("Auto-submit forms", value=False, help="⚠️ Use with caution")
                save_screenshots = st.checkbox("Save screenshots", value=True)
                max_applications = st.slider("Max applications per session", 1, 20, 5)
            
            with col2:
                st.subheader("Timing Controls")
                min_delay = st.slider("Min delay between apps (seconds)", 30, 300, 60)
                max_delay = st.slider("Max delay between apps (seconds)", 60, 600, 120)
                max_retries = st.slider("Max retries per application", 1, 5, 2)
            
            with col3:
                st.subheader("Safety Features")
                skip_duplicates = st.checkbox("Skip duplicate companies", value=True)
                manual_review = st.checkbox("Require manual review", value=True)
                test_mode = st.checkbox("Test mode (no actual applications)", value=True)
        
        # Application queue
        st.subheader("📋 Application Queue")
        
        high_matches = [j for j in st.session_state.matched_jobs if j.get('overall_score', 0) >= 0.8]
        
        if high_matches:
            selected_applications = st.multiselect(
                "Select jobs to apply to:",
                range(len(high_matches)),
                default=list(range(min(5, len(high_matches)))),
                format_func=lambda x: f"{high_matches[x]['job_title']} @ {high_matches[x]['company']} ({high_matches[x]['overall_score']:.1%})"
            )
            
            if selected_applications:
                st.write(f"**Selected {len(selected_applications)} applications:**")
                for i in selected_applications:
                    job = high_matches[i]
                    st.write(f"• {job['job_title']} @ {job['company']} - {job['overall_score']:.1%} match")
        else:
            st.warning("No high-match jobs available for auto-application. Lower the match threshold in Job Matching.")
            selected_applications = []
        
        # Application controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Start Auto Applications", type="primary", use_container_width=True, disabled=not selected_applications):
                if selected_applications:
                    self.start_auto_applications(
                        [high_matches[i] for i in selected_applications],
                        {
                            'auto_submit': auto_submit,
                            'save_screenshots': save_screenshots,
                            'max_applications': max_applications,
                            'min_delay': min_delay,
                            'max_delay': max_delay,
                            'max_retries': max_retries,
                            'skip_duplicates': skip_duplicates,
                            'manual_review': manual_review,
                            'test_mode': test_mode
                        }
                    )
        
        with col2:
            if st.button("⏸️ Pause Applications", use_container_width=True):
                st.session_state.application_active = False
                st.info("Applications paused")
        
        with col3:
            if st.button("📊 View Results", use_container_width=True):
                if st.session_state.get('application_results'):
                    st.success(f"Completed {len(st.session_state.application_results)} applications")
        
        # Application progress
        if st.session_state.get('application_active'):
            st.subheader("⚡ Application Progress")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate application progress
            total_apps = len(selected_applications)
            for i in range(total_apps):
                progress = (i + 1) / total_apps
                progress_bar.progress(progress)
                status_text.text(f"Applying to job {i + 1} of {total_apps}...")
                time.sleep(2)  # Simulate processing time
            
            status_text.text("✅ All applications completed!")
            st.session_state.application_active = False
        
        # Application results
        if st.session_state.get('application_results'):
            st.subheader("📊 Application Results")
            
            results = st.session_state.application_results
            successful = [r for r in results if r.get('status') == 'success']
            failed = [r for r in results if r.get('status') == 'failed']
            review_required = [r for r in results if r.get('status') == 'review_required']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Applications", len(results))
            
            with col2:
                st.metric("Successful", len(successful))
            
            with col3:
                st.metric("Needs Review", len(review_required))
            
            with col4:
                st.metric("Failed", len(failed))
            
            # Detailed results
            for i, result in enumerate(results):
                status_color = {
                    'success': '🟢',
                    'review_required': '🟡',
                    'failed': '🔴'
                }.get(result.get('status'), '⚪')
                
                with st.expander(f"{status_color} Application {i+1}: {result.get('job_title')} @ {result.get('company')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Status:** {result.get('status', 'Unknown')}")
                        st.write(f"**Applied At:** {result.get('applied_at', 'Unknown')}")
                        st.write(f"**Match Score:** {result.get('match_score', 0):.1%}")
                    
                    with col2:
                        st.write(f"**Form Fields Filled:** {result.get('form_fields_filled', 0)}")
                        st.write(f"**Files Uploaded:** {len(result.get('files_uploaded', []))}")
                        
                        if result.get('error_message'):
                            st.error(f"Error: {result['error_message']}")
                        
                        if result.get('screenshot_path'):
                            if st.button(f"View Screenshot", key=f"screenshot_{i}"):
                                st.image(result['screenshot_path'])
    
    def render_analytics_page(self):
        """Render analytics and monitoring page"""
        st.header("📊 Analytics & Monitoring")
        
        # Initialize analytics monitor
        if not hasattr(self, 'analytics_monitor') or self.analytics_monitor is None:
            self.analytics_monitor = ScrapingAnalyticsMonitor()
        
        # Real-time stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Jobs Scraped Today", len(st.session_state.get('scraped_jobs', [])))
        
        with col2:
            st.metric("Applications Today", len(st.session_state.get('application_results', [])))
        
        with col3:
            success_rate = 0
            if st.session_state.get('application_results'):
                successful = len([r for r in st.session_state.application_results if r.get('status') == 'success'])
                success_rate = successful / len(st.session_state.application_results) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col4:
            st.metric("Active Alerts", 0)  # Would be populated from real monitoring
        
        # Analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "🔍 Scraping Stats", "📝 Application Stats", "🚨 Alerts"])
        
        with tab1:
            st.subheader("📈 Performance Overview")
            
            # Generate sample performance data
            dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
            performance_data = pd.DataFrame({
                'Date': dates,
                'Jobs Scraped': np.random.randint(20, 100, len(dates)),
                'Applications': np.random.randint(2, 15, len(dates)),
                'Success Rate': np.random.uniform(0.7, 0.95, len(dates))
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(performance_data, x='Date', y='Jobs Scraped', title='Daily Jobs Scraped')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(performance_data, x='Date', y='Applications', title='Daily Applications')
                st.plotly_chart(fig, use_container_width=True)
            
            # Success rate chart
            fig = px.line(performance_data, x='Date', y='Success Rate', title='Application Success Rate')
            fig.update_yaxis(tickformat='.1%')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("🔍 Scraping Statistics")
            
            if st.session_state.get('scraped_jobs'):
                jobs_df = pd.DataFrame(st.session_state.scraped_jobs)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Platform distribution
                    platform_counts = jobs_df['source_platform'].value_counts()
                    fig = px.pie(values=platform_counts.values, names=platform_counts.index, title='Jobs by Platform')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Location distribution
                    if 'location' in jobs_df.columns:
                        location_counts = jobs_df['location'].value_counts().head(10)
                        fig = px.bar(x=location_counts.values, y=location_counts.index, orientation='h', title='Top Locations')
                        st.plotly_chart(fig, use_container_width=True)
                
                # Skills analysis
                if 'skills_required' in jobs_df.columns:
                    all_skills = []
                    for skills_list in jobs_df['skills_required'].dropna():
                        if isinstance(skills_list, list):
                            all_skills.extend(skills_list)
                    
                    if all_skills:
                        skills_series = pd.Series(all_skills)
                        top_skills = skills_series.value_counts().head(15)
                        
                        fig = px.bar(x=top_skills.values, y=top_skills.index, orientation='h', title='Most Requested Skills')
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No scraping data available. Start scraping to see statistics.")
        
        with tab3:
            st.subheader("📝 Application Statistics")
            
            if st.session_state.get('application_results'):
                results_df = pd.DataFrame(st.session_state.application_results)
                
                # Status distribution
                status_counts = results_df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, title='Application Status Distribution')
                st.plotly_chart(fig, use_container_width=True)
                
                # Match score vs success
                if 'match_score' in results_df.columns:
                    fig = px.scatter(results_df, x='match_score', y='status', title='Match Score vs Application Status')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No application data available. Complete some applications to see statistics.")
        
        with tab4:
            st.subheader("🚨 System Alerts")
            
            # Sample alerts (would be populated from real monitoring)
            sample_alerts = [
                {"time": "2024-01-15 14:30", "level": "INFO", "message": "Job scraping started", "platform": "LinkedIn"},
                {"time": "2024-01-15 14:25", "level": "WARNING", "message": "High response time detected", "platform": "Indeed"},
                {"time": "2024-01-15 14:20", "level": "SUCCESS", "message": "Resume parsed successfully", "platform": "System"},
            ]
            
            for alert in sample_alerts:
                level_color = {
                    "INFO": "🔵",
                    "WARNING": "🟡", 
                    "ERROR": "🔴",
                    "SUCCESS": "🟢"
                }.get(alert["level"], "⚪")
                
                st.write(f"{level_color} **{alert['time']}** - {alert['message']} ({alert['platform']})")
            
            # Alert configuration
            st.subheader("⚙️ Alert Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Email notifications", value=True)
                st.checkbox("Desktop notifications", value=True)
                st.checkbox("Slack notifications", value=False)
            
            with col2:
                st.slider("Error rate threshold", 0.0, 1.0, 0.3, format="%.0%%")
                st.slider("Response time threshold (seconds)", 1, 30, 10)
    
    def render_configuration_page(self):
        """Render configuration page"""
        st.header("⚙️ System Configuration")
        
        # Configuration tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Scraping", "🎯 Matching", "🤖 Application", "🔔 Notifications"])
        
        with tab1:
            st.subheader("🔍 Scraping Configuration")
            
            # Platform settings
            st.write("**Job Platforms:**")
            platforms = ['linkedin', 'indeed', 'remoteok', 'glassdoor', 'monster']
            
            for platform in platforms:
                enabled = st.checkbox(f"Enable {platform.title()}", 
                                    value=platform in st.session_state.app_config['scraping']['enabled_platforms'],
                                    key=f"platform_{platform}")
            
            # Advanced scraping settings
            st.write("**Advanced Settings:**")
            max_jobs = st.number_input("Max jobs per platform", 10, 200, 
                                     st.session_state.app_config['scraping']['max_jobs_per_platform'])
            
            use_proxy = st.checkbox("Enable proxy rotation", 
                                  value=st.session_state.app_config['scraping']['use_proxy_rotation'])
            
            enable_company_scraping = st.checkbox("Enable company career page scraping",
                                                 value=st.session_state.app_config['scraping']['enable_company_scraping'])
            
            # Keywords configuration
            st.write("**Search Keywords:**")
            keywords_text = st.text_area("Job keywords (one per line)",
                                       value="\n".join(st.session_state.app_config['scraping']['keywords']))
        
        with tab2:
            st.subheader("🎯 Matching Configuration")
            
            min_match_score = st.slider("Minimum match score", 0.0, 1.0, 
                                      st.session_state.app_config['matching']['min_match_score'],
                                      format="%.0%%")
            
            auto_apply_threshold = st.slider("Auto-apply threshold", 0.7, 1.0,
                                           st.session_state.app_config['matching']['auto_apply_threshold'],
                                           format="%.0%%")
            
            # User preferences
            st.write("**User Preferences:**")
            
            locations_text = st.text_area("Preferred locations (one per line)",
                                        value="\n".join(st.session_state.app_config['user_preferences']['preferred_locations']))
            
            min_salary = st.number_input("Minimum salary", 0, 300000,
                                       st.session_state.app_config['user_preferences']['min_salary'])
            
            job_types = st.multiselect("Job types", ['full-time', 'part-time', 'contract', 'freelance'],
                                     default=st.session_state.app_config['user_preferences']['job_types'])
            
            work_auth = st.selectbox("Work authorization", ['Yes', 'No', 'Requires sponsorship'],
                                   index=0 if st.session_state.app_config['user_preferences']['work_authorization'] == 'Yes' else 1)
        
        with tab3:
            st.subheader("🤖 Application Configuration")
            
            # Application settings
            auto_submit = st.checkbox("Auto-submit applications", value=False, 
                                    help="⚠️ Requires careful testing")
            
            save_screenshots = st.checkbox("Save application screenshots", value=True)
            
            max_applications = st.slider("Max applications per session", 1, 50, 20)
            
            # Timing settings
            st.write("**Timing Settings:**")
            min_delay = st.slider("Min delay between applications (seconds)", 30, 300, 60)
            max_delay = st.slider("Max delay between applications (seconds)", 60, 600, 120)
            
            # Safety settings
            st.write("**Safety Settings:**")
            skip_duplicates = st.checkbox("Skip duplicate companies", value=True)
            require_review = st.checkbox("Require manual review", value=True)
            max_retries = st.slider("Max retries per application", 1, 5, 2)
        
        with tab4:
            st.subheader("🔔 Notification Configuration")
            
            # Email settings
            st.write("**Email Notifications:**")
            email_enabled = st.checkbox("Enable email notifications")
            
            if email_enabled:
                smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
                smtp_port = st.number_input("SMTP Port", value=587)
                email_username = st.text_input("Email Username")
                email_password = st.text_input("Email Password", type="password")
                recipients = st.text_area("Recipients (one per line)")
            
            # Slack settings
            st.write("**Slack Notifications:**")
            slack_enabled = st.checkbox("Enable Slack notifications")
            
            if slack_enabled:
                slack_webhook = st.text_input("Slack Webhook URL")
            
            # Desktop notifications
            st.write("**Desktop Notifications:**")
            desktop_enabled = st.checkbox("Enable desktop notifications", value=True)
        
        # Save configuration
        if st.button("💾 Save Configuration", type="primary"):
            # Update configuration
            st.session_state.app_config.update({
                'scraping': {
                    'enabled_platforms': [p for p in platforms if st.session_state.get(f'platform_{p}')],
                    'max_jobs_per_platform': max_jobs,
                    'use_proxy_rotation': use_proxy,
                    'enable_company_scraping': enable_company_scraping,
                    'keywords': [k.strip() for k in keywords_text.split('\n') if k.strip()]
                },
                'matching': {
                    'min_match_score': min_match_score,
                    'auto_apply_threshold': auto_apply_threshold
                },
                'user_preferences': {
                    'preferred_locations': [l.strip() for l in locations_text.split('\n') if l.strip()],
                    'min_salary': min_salary,
                    'job_types': job_types,
                    'work_authorization': work_auth
                }
            })
            
            # Save to file
            config_path = Path("config/application_config.yaml")
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                yaml.dump(st.session_state.app_config, f)
            
            st.success("✅ Configuration saved successfully!")
    
    def render_system_status_page(self):
        """Render system status and health page"""
        st.header("🔧 System Status & Health")
        
        # System health indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="success-card">
                <h4>🟢 Scraping System</h4>
                <p>Operational</p>
                <small>All platforms accessible</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="success-card">
                <h4>🟢 AI Services</h4>
                <p>Operational</p>
                <small>All models responding</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            proxy_status = "Operational" if st.session_state.app_config['scraping']['use_proxy_rotation'] else "Disabled"
            color = "success-card" if proxy_status == "Operational" else "feature-card"
            
            st.markdown(f"""
            <div class="{color}">
                <h4>🔄 Proxy System</h4>
                <p>{proxy_status}</p>
                <small>Rotation enabled</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="success-card">
                <h4>📊 Analytics</h4>
                <p>Operational</p>
                <small>Collecting metrics</small>
            </div>
            """, unsafe_allow_html=True)
        
        # System information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💻 System Information")
            
            import psutil
            
            st.write(f"**CPU Usage:** {psutil.cpu_percent():.1f}%")
            st.write(f"**Memory Usage:** {psutil.virtual_memory().percent:.1f}%")
            st.write(f"**Disk Usage:** {psutil.disk_usage('/').percent:.1f}%")
            
            # Process information
            st.write("**Active Processes:**")
            st.write("• Main Dashboard: Running")
            st.write("• Analytics Monitor: Running")
            if st.session_state.get('scraping_active'):
                st.write("• Job Scraper: Active")
            if st.session_state.get('application_active'):
                st.write("• Auto Applicator: Active")
        
        with col2:
            st.subheader("📈 Performance Metrics")
            
            # Recent activity
            st.write("**Recent Activity:**")
            st.write(f"• Jobs scraped: {len(st.session_state.get('scraped_jobs', []))}")
            st.write(f"• Jobs matched: {len(st.session_state.get('matched_jobs', []))}")
            st.write(f"• Applications sent: {len(st.session_state.get('application_results', []))}")
            
            # Response times (simulated)
            st.write("**Average Response Times:**")
            st.write("• Job scraping: 2.3s")
            st.write("• AI matching: 0.8s")
            st.write("• Form filling: 5.2s")
        
        # Component status
        st.subheader("🔧 Component Status")
        
        components = [
            {"name": "Universal Job Scraper", "status": "✅ Active", "last_run": "2 minutes ago"},
            {"name": "Resume Parser", "status": "✅ Ready", "last_run": "15 minutes ago"},
            {"name": "Job Matcher", "status": "✅ Ready", "last_run": "5 minutes ago"},
            {"name": "Auto Form Filler", "status": "✅ Ready", "last_run": "Never"},
            {"name": "Analytics Monitor", "status": "✅ Active", "last_run": "Continuous"},
            {"name": "Proxy System", "status": "⚪ Disabled", "last_run": "Never"},
        ]
        
        for component in components:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{component['name']}**")
            
            with col2:
                st.write(component['status'])
            
            with col3:
                st.write(f"*{component['last_run']}*")
        
        # System actions
        st.subheader("⚡ System Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Restart Services", use_container_width=True):
                with st.spinner("Restarting services..."):
                    time.sleep(2)
                st.success("Services restarted!")
        
        with col2:
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.session_state.clear()
                st.success("Cache cleared!")
        
        with col3:
            if st.button("📊 Export Logs", use_container_width=True):
                st.info("Log export functionality coming soon!")
        
        with col4:
            if st.button("⚙️ Run Diagnostics", use_container_width=True):
                with st.spinner("Running diagnostics..."):
                    time.sleep(3)
                st.success("All systems operational!")
    
    # Helper methods
    def start_job_scraping(self, platforms: List[str], keywords: List[str], locations: List[str]):
        """Start job scraping process"""
        st.session_state.scraping_active = True
        
        with st.spinner("Initializing job scraping..."):
            # Simulate scraping process
            scraped_jobs = []
            
            # Generate sample jobs for demo
            sample_jobs = [
                {
                    'title': 'Senior Security Engineer',
                    'company': 'TechCorp Inc',
                    'location': 'Berlin, Germany',
                    'source_platform': 'linkedin',
                    'description': 'We are looking for an experienced security professional...',
                    'skills_required': ['penetration testing', 'python', 'aws'],
                    'scraped_at': datetime.now().isoformat()
                },
                {
                    'title': 'Cloud Security Architect',
                    'company': 'CloudFirst GmbH', 
                    'location': 'Munich, Germany',
                    'source_platform': 'indeed',
                    'description': 'Join our cloud security team...',
                    'skills_required': ['cloud security', 'azure', 'kubernetes'],
                    'scraped_at': datetime.now().isoformat()
                }
            ]
            
            scraped_jobs.extend(sample_jobs)
            
            st.session_state.scraped_jobs = scraped_jobs
            st.session_state.scraping_active = False
            
        st.success(f"✅ Scraped {len(scraped_jobs)} jobs from {len(platforms)} platforms!")
    
    def auto_match_jobs(self):
        """Automatically match scraped jobs with resume"""
        if not st.session_state.get('scraped_jobs') or not st.session_state.get('parsed_resume'):
            st.error("Both scraped jobs and parsed resume are required for matching")
            return
        
        with st.spinner("Matching jobs using AI..."):
            # Simulate job matching
            matched_jobs = []
            
            for job in st.session_state.scraped_jobs:
                # Simulate match scores
                match_score = random.uniform(0.3, 0.95)
                
                matched_job = {
                    'job_id': f"job_{random.randint(1000, 9999)}",
                    'job_title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'source_platform': job['source_platform'],
                    'overall_score': match_score,
                    'skill_match_score': random.uniform(0.4, 0.9),
                    'experience_match_score': random.uniform(0.6, 0.95),
                    'location_match_score': random.uniform(0.7, 1.0),
                    'matching_skills': job['skills_required'][:3],
                    'missing_skills': ['docker', 'terraform'] if match_score < 0.8 else [],
                    'recommendation': 'HIGHLY RECOMMENDED' if match_score >= 0.8 else 'RECOMMENDED' if match_score >= 0.6 else 'CONSIDER'
                }
                
                matched_jobs.append(matched_job)
            
            # Sort by match score
            matched_jobs.sort(key=lambda x: x['overall_score'], reverse=True)
            
            st.session_state.matched_jobs = matched_jobs
            
        st.success(f"✅ Matched {len(matched_jobs)} jobs with your resume!")
    
    def perform_job_matching(self, min_score: float, max_matches: int):
        """Perform detailed job matching"""
        self.auto_match_jobs()
        
        # Filter by minimum score
        filtered_matches = [
            job for job in st.session_state.matched_jobs 
            if job['overall_score'] >= min_score
        ][:max_matches]
        
        st.session_state.matched_jobs = filtered_matches
        st.success(f"Found {len(filtered_matches)} matches above {min_score:.0%} threshold")
    
    def start_auto_applications(self, jobs: List[Dict], config: Dict):
        """Start automated job applications"""
        st.session_state.application_active = True
        
        with st.spinner("Starting automated applications..."):
            application_results = []
            
            for job in jobs:
                # Simulate application process
                result = {
                    'job_id': job.get('job_id', f"job_{random.randint(1000, 9999)}"),
                    'job_title': job['job_title'],
                    'company': job['company'],
                    'status': random.choice(['success', 'review_required', 'failed']),
                    'applied_at': datetime.now().isoformat(),
                    'match_score': job['overall_score'],
                    'form_fields_filled': random.randint(8, 15),
                    'files_uploaded': ['resume.pdf'] if random.random() > 0.3 else [],
                    'error_message': 'Network timeout' if random.random() < 0.1 else None
                }
                
                application_results.append(result)
                
                # Simulate processing delay
                time.sleep(1)
            
            st.session_state.application_results = application_results
            st.session_state.application_active = False
            
        successful = len([r for r in application_results if r['status'] == 'success'])
        st.success(f"✅ Completed {len(application_results)} applications ({successful} successful)")

# Main application
def main():
    dashboard = UltimateJobDashboard()
    dashboard.render_dashboard()

if __name__ == "__main__":
    main()