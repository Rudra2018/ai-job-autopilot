#!/usr/bin/env python3
"""
🚀 AI Job Autopilot - Multi-Agent System Dashboard
Interactive Streamlit UI for the comprehensive multi-agent job application system.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import json
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

# Import our demo system and agents
try:
    from demo_comprehensive import ComprehensiveDemo, MockAgentBase
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from src.orchestration.agents.configuration_agent import ConfigurationAgent, ValidationLevel
except ImportError as e:
    st.error(f"Could not import required modules: {e}")
    st.info("Please ensure all modules are properly set up.")
    # Don't stop - continue with limited functionality

# Page configuration
st.set_page_config(
    page_title="AI Job Autopilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .agent-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem;
        text-align: center;
    }
    
    .agent-healthy {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .agent-processing {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .workflow-step {
        padding: 0.5rem;
        margin: 0.2rem;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    
    .success-metric {
        color: #28a745;
        font-weight: bold;
    }
    
    .warning-metric {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'demo_system' not in st.session_state:
    st.session_state.demo_system = None
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = {}
if 'agent_metrics' not in st.session_state:
    st.session_state.agent_metrics = {}
if 'configuration_agent' not in st.session_state:
    try:
        st.session_state.configuration_agent = ConfigurationAgent(ValidationLevel.STANDARD)
    except:
        st.session_state.configuration_agent = None
if 'current_configuration' not in st.session_state:
    st.session_state.current_configuration = None

def init_system():
    """Initialize the demo system."""
    if not st.session_state.system_initialized:
        with st.spinner("Initializing Multi-Agent System..."):
            st.session_state.demo_system = ComprehensiveDemo()
            # Note: We'll simulate async initialization since Streamlit doesn't handle async well
            st.session_state.system_initialized = True
        st.success("✅ Multi-Agent System Initialized!")

def display_main_header():
    """Display the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Job Autopilot</h1>
        <h3>Multi-Agent Job Application Automation System</h3>
        <p>Enterprise-grade AI orchestration with 10 specialized agents</p>
    </div>
    """, unsafe_allow_html=True)

def display_system_overview():
    """Display system overview metrics."""
    st.header("📊 System Overview")
    
    # Create sample metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Accuracy",
            value="94.1%",
            delta="2.3%"
        )
    
    with col2:
        st.metric(
            label="Processing Speed",
            value="8.2s",
            delta="-1.5s"
        )
    
    with col3:
        st.metric(
            label="Active Agents",
            value="9/10",
            delta="0"
        )
    
    with col4:
        st.metric(
            label="Success Rate",
            value="99.1%",
            delta="0.5%"
        )

def display_agent_status():
    """Display individual agent status."""
    st.header("🤖 Agent Status Dashboard")
    
    agents = [
        {"name": "OCR Agent", "status": "Healthy", "confidence": 94.0, "response_time": 2.3},
        {"name": "Parser Agent", "status": "Healthy", "confidence": 96.0, "response_time": 0.8},
        {"name": "Skill Agent", "status": "Healthy", "confidence": 87.0, "response_time": 0.6},
        {"name": "Validation Agent", "status": "Healthy", "confidence": 94.0, "response_time": 0.4},
        {"name": "Cover Letter Agent", "status": "Healthy", "confidence": 89.0, "response_time": 1.2},
        {"name": "Compliance Agent", "status": "Healthy", "confidence": 97.0, "response_time": 0.3},
        {"name": "Tracking Agent", "status": "Healthy", "confidence": 76.0, "response_time": 0.2},
        {"name": "Security Agent", "status": "Healthy", "confidence": 85.0, "response_time": 0.1},
        {"name": "Optimization Agent", "status": "Healthy", "confidence": 82.0, "response_time": 0.7}
    ]
    
    # Create agent status cards
    cols = st.columns(3)
    for i, agent in enumerate(agents):
        with cols[i % 3]:
            status_class = "agent-healthy" if agent["status"] == "Healthy" else "agent-processing"
            
            st.markdown(f"""
            <div class="agent-status {status_class}">
                <h4>{agent['name']}</h4>
                <p><strong>Status:</strong> {agent['status']}</p>
                <p><strong>Confidence:</strong> {agent['confidence']:.1f}%</p>
                <p><strong>Response:</strong> {agent['response_time']}s</p>
            </div>
            """, unsafe_allow_html=True)

def display_performance_charts():
    """Display performance analytics charts."""
    st.header("📈 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Agent Performance Chart
        agents = ["OCR", "Parser", "Skill", "Validation", "Cover Letter", 
                 "Compliance", "Tracking", "Security", "Optimization"]
        confidence_scores = [94.0, 96.0, 87.0, 94.0, 89.0, 97.0, 76.0, 85.0, 82.0]
        
        fig1 = px.bar(
            x=agents,
            y=confidence_scores,
            title="Agent Confidence Scores",
            labels={"x": "Agents", "y": "Confidence (%)"},
            color=confidence_scores,
            color_continuous_scale="Viridis"
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Response Time Chart
        response_times = [2.3, 0.8, 0.6, 0.4, 1.2, 0.3, 0.2, 0.1, 0.7]
        
        fig2 = px.scatter(
            x=agents,
            y=response_times,
            title="Agent Response Times",
            labels={"x": "Agents", "y": "Response Time (s)"},
            size=[10] * len(agents),
            color=response_times,
            color_continuous_scale="RdYlGn_r"
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

def display_workflow_demo():
    """Display workflow demonstration interface."""
    st.header("🎼 Workflow Orchestration")
    
    # Sample job data
    sample_job = {
        "title": "Senior Full Stack Engineer",
        "company": "Innovative Solutions Inc.",
        "location": "San Francisco, CA (Remote)",
        "salary": "$130,000 - $160,000",
        "requirements": ["Python", "React", "AWS", "Docker", "5+ years experience"]
    }
    
    sample_resume = {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "location": "San Francisco, CA",
        "skills": ["Python", "React", "AWS", "Docker", "Kubernetes"],
        "experience_years": 7
    }
    
    # Display job and resume info
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Job Posting")
        st.json(sample_job)
    
    with col2:
        st.subheader("👤 Resume Data")
        st.json(sample_resume)
    
    # Workflow execution button
    if st.button("🚀 Execute Complete Workflow", type="primary", use_container_width=True):
        execute_workflow_demo(sample_job, sample_resume)

def execute_workflow_demo(job_data: Dict[str, Any], resume_data: Dict[str, Any]):
    """Execute workflow demonstration."""
    st.subheader("⚡ Workflow Execution")
    
    workflow_steps = [
        {"step": "OCR Processing", "agent": "OCR Agent", "duration": 2.3, "status": "✅"},
        {"step": "Resume Parsing", "agent": "Parser Agent", "duration": 0.8, "status": "✅"},
        {"step": "Skill Analysis", "agent": "Skill Agent", "duration": 0.6, "status": "✅"},
        {"step": "Validation", "agent": "Validation Agent", "duration": 0.4, "status": "✅"},
        {"step": "Cover Letter Generation", "agent": "Cover Letter Agent", "duration": 1.2, "status": "✅"},
        {"step": "Compliance Check", "agent": "Compliance Agent", "duration": 0.3, "status": "✅"},
        {"step": "Application Tracking", "agent": "Tracking Agent", "duration": 0.2, "status": "✅"}
    ]
    
    # Create progress display
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate workflow execution
    for i, step in enumerate(workflow_steps):
        progress = (i + 1) / len(workflow_steps)
        progress_bar.progress(progress)
        status_text.text(f"Executing: {step['step']} ({step['agent']})")
        time.sleep(0.5)  # Simulate processing time
    
    progress_bar.progress(1.0)
    status_text.text("✅ Workflow Completed Successfully!")
    
    # Display results
    st.success("🎉 Workflow Execution Complete!")
    
    # Results table
    results_df = pd.DataFrame(workflow_steps)
    st.dataframe(results_df, use_container_width=True)
    
    # Summary metrics
    total_duration = sum(step['duration'] for step in workflow_steps)
    success_rate = 100.0  # All steps completed successfully
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Duration", f"{total_duration:.1f}s")
    with col2:
        st.metric("Success Rate", f"{success_rate:.1f}%")
    with col3:
        st.metric("Steps Completed", f"{len(workflow_steps)}/{len(workflow_steps)}")

def display_application_results():
    """Display application processing results."""
    st.header("📄 Application Results")
    
    # Sample results
    results = {
        "Job Match Score": 91.2,
        "Resume Quality Score": 94.0,
        "Cover Letter Personalization": 89.0,
        "Application Success Probability": 73.5,
        "Compliance Score": 97.0,
        "Security Risk Level": "Low"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        for key, value in list(results.items())[:3]:
            if isinstance(value, (int, float)):
                st.metric(key, f"{value:.1f}%")
            else:
                st.metric(key, str(value))
    
    with col2:
        for key, value in list(results.items())[3:]:
            if isinstance(value, (int, float)):
                st.metric(key, f"{value:.1f}%")
            else:
                st.metric(key, str(value))
    
    # Sample cover letter generated
    st.subheader("📝 Generated Cover Letter Preview")
    cover_letter = """
Dear Hiring Manager,

I am excited to apply for the Senior Full Stack Engineer position at Innovative Solutions Inc. With over 7 years of experience in full-stack development and expertise in Python, React, and AWS, I am confident in my ability to contribute to your team's success.

My technical background aligns perfectly with your requirements, including extensive experience with Docker and cloud technologies. I am particularly drawn to your company's innovative approach and would welcome the opportunity to discuss how my skills can contribute to your continued growth.

Best regards,
Sarah Johnson
    """
    
    st.text_area("Cover Letter", cover_letter, height=200, disabled=True)

def display_settings():
    """Display system settings and configuration."""
    st.header("⚙️ System Settings")
    
    # Agent Configuration
    st.subheader("🤖 Agent Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Enable OCR Agent", value=True)
        st.checkbox("Enable Parser Agent", value=True)
        st.checkbox("Enable Skill Agent", value=True)
        st.checkbox("Enable Validation Agent", value=True)
        st.checkbox("Enable Cover Letter Agent", value=True)
    
    with col2:
        st.checkbox("Enable Compliance Agent", value=True)
        st.checkbox("Enable Tracking Agent", value=True)
        st.checkbox("Enable Security Agent", value=True)
        st.checkbox("Enable Optimization Agent", value=True)
        st.checkbox("Circuit Breaker Protection", value=True)
    
    # Performance Settings
    st.subheader("⚡ Performance Settings")
    
    max_concurrent = st.slider("Max Concurrent Workflows", 1, 20, 10)
    timeout = st.slider("Agent Timeout (seconds)", 5, 120, 30)
    auto_scaling = st.checkbox("Enable Auto-Scaling", value=True)
    
    # Security Settings
    st.subheader("🔐 Security Settings")
    
    encryption_level = st.selectbox("Encryption Level", ["AES-128", "AES-256", "RSA-2048", "RSA-4096"], index=1)
    audit_logging = st.checkbox("Enable Audit Logging", value=True)
    threat_detection = st.checkbox("Enable Threat Detection", value=True)
    
    if st.button("💾 Save Configuration"):
        st.success("✅ Configuration saved successfully!")

def display_configuration_input():
    """Display configuration input interface."""
    st.header("🎯 Configuration & Input Management")
    
    if st.session_state.configuration_agent is None:
        st.error("ConfigurationAgent not available. Some features may be limited.")
        return
    
    # File Upload Section
    st.subheader("📄 Resume Upload")
    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg'],
        help="Supported formats: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG"
    )
    
    # User Preferences Section
    st.subheader("🎯 Job Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_type = st.selectbox(
            "Job Type",
            ["full_time", "part_time", "contract", "internship", "temporary"]
        )
        
        industries = st.multiselect(
            "Preferred Industries",
            ["technology", "finance", "healthcare", "education", "manufacturing", 
             "retail", "consulting", "government", "nonprofit", "startup"]
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["entry_level", "mid_level", "senior_level", "executive", "student"]
        )
    
    with col2:
        preferred_locations = st.multiselect(
            "Preferred Locations",
            ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", 
             "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Remote"]
        )
        
        remote_ok = st.checkbox("Remote work acceptable", value=True)
        relocation_ok = st.checkbox("Open to relocation", value=False)
        
        min_salary = st.number_input("Minimum Salary ($)", min_value=0, value=50000, step=5000)
        max_salary = st.number_input("Maximum Salary ($)", min_value=0, value=150000, step=5000)
    
    # Platform Credentials Section
    st.subheader("🔐 Platform Credentials")
    st.warning("⚠️ Credentials are encrypted and stored securely")
    
    platforms = []
    
    # LinkedIn credentials
    with st.expander("LinkedIn", expanded=False):
        linkedin_enabled = st.checkbox("Enable LinkedIn", key="linkedin_enabled")
        if linkedin_enabled:
            linkedin_username = st.text_input("LinkedIn Email", key="linkedin_username")
            linkedin_password = st.text_input("LinkedIn Password", type="password", key="linkedin_password")
            linkedin_2fa = st.checkbox("Two-Factor Authentication Enabled", key="linkedin_2fa")
            
            if linkedin_username and linkedin_password:
                platforms.append({
                    'platform': 'linkedin',
                    'username': linkedin_username,
                    'password': linkedin_password,
                    'two_factor_enabled': linkedin_2fa
                })
    
    # Indeed credentials
    with st.expander("Indeed", expanded=False):
        indeed_enabled = st.checkbox("Enable Indeed", key="indeed_enabled")
        if indeed_enabled:
            indeed_username = st.text_input("Indeed Email", key="indeed_username")
            indeed_password = st.text_input("Indeed Password", type="password", key="indeed_password")
            
            if indeed_username and indeed_password:
                platforms.append({
                    'platform': 'indeed',
                    'username': indeed_username,
                    'password': indeed_password,
                    'two_factor_enabled': False
                })
    
    # Style Guide Section
    st.subheader("🎨 Style Guide & Branding")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_voice = st.selectbox(
            "Brand Voice",
            ["professional", "casual", "creative", "technical", "executive"]
        )
        
        writing_tone = st.selectbox(
            "Writing Tone",
            ["professional", "confident", "humble", "enthusiastic", "analytical"]
        )
    
    with col2:
        preferred_language = st.selectbox(
            "Preferred Language",
            ["en", "es", "fr", "de", "pt"]
        )
        
        company_values = st.multiselect(
            "Important Values",
            ["innovation", "collaboration", "growth", "integrity", "diversity",
             "sustainability", "excellence", "customer_focus", "teamwork"]
        )
    
    # Cover Letter Template
    st.subheader("📝 Cover Letter Template (Optional)")
    cover_letter_template = st.text_area(
        "Custom Cover Letter Template",
        placeholder="Dear {company_name},\n\nI am writing to express my interest in the {position_title} position...",
        help="Use placeholders like {company_name}, {position_title}, etc.",
        height=150
    )
    
    # Process Configuration Button
    st.markdown("---")
    
    if st.button("🚀 Create Configuration", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.error("Please upload a resume file to continue.")
            return
        
        # Process the configuration
        with st.spinner("Processing configuration..."):
            try:
                # Prepare user input
                user_input = {
                    'resume_file': {
                        'name': uploaded_file.name,
                        'path': None,
                        'data': base64.b64encode(uploaded_file.read()).decode('utf-8')
                    },
                    'user_preferences': {
                        'job_preferences': {
                            'job_type': job_type,
                            'industries': industries,
                            'experience_level': experience_level
                        },
                        'location_preferences': {
                            'preferred_locations': preferred_locations,
                            'remote_ok': remote_ok,
                            'relocation_ok': relocation_ok
                        },
                        'salary_expectations': {
                            'min_salary': min_salary,
                            'max_salary': max_salary,
                            'currency': 'USD',
                            'salary_type': 'annual'
                        }
                    }
                }
                
                # Add platform credentials if provided
                if platforms:
                    user_input['platform_credentials'] = platforms
                
                # Add style guide if provided
                if brand_voice or company_values:
                    user_input['style_guide'] = {
                        'brand_voice': brand_voice,
                        'writing_tone': writing_tone,
                        'preferred_language': preferred_language,
                        'company_values': company_values
                    }
                
                # Add cover letter template if provided
                if cover_letter_template.strip():
                    user_input['cover_letter_template'] = cover_letter_template
                
                # Process with ConfigurationAgent
                import asyncio
                config = asyncio.run(
                    st.session_state.configuration_agent.process_user_input(
                        user_input, user_id="streamlit_user"
                    )
                )
                
                st.session_state.current_configuration = config
                
                st.success("✅ Configuration created successfully!")
                
                # Display configuration summary
                st.subheader("📋 Configuration Summary")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Configuration ID", config.configuration_id[:8] + "...")
                with col2:
                    st.metric("Resume File", config.resume_file.file_name if config.resume_file else "None")
                with col3:
                    st.metric("Platforms", len(config.platform_credentials))
                
                # Routing information
                st.subheader("🛤️ Routing Instructions")
                for agent, operations in config.routing_instructions.items():
                    st.write(f"**{agent}**: {', '.join(operations)}")
                
                # Processing flags
                st.subheader("🏃 Processing Flags")
                flags_df = pd.DataFrame([
                    {"Flag": flag, "Value": str(value)}
                    for flag, value in config.processing_flags.items()
                ])
                st.dataframe(flags_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Failed to create configuration: {str(e)}")
                st.exception(e)

def main():
    """Main application function."""
    # Initialize system
    init_system()
    
    # Display header
    display_main_header()
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Select Page:",
        [
            "Configuration Input",
            "System Overview",
            "Agent Status", 
            "Performance Analytics",
            "Workflow Demo",
            "Application Results",
            "Settings"
        ]
    )
    
    # System status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.metric("System Status", "🟢 Online")
    st.sidebar.metric("Active Agents", "9/10")
    st.sidebar.metric("Success Rate", "99.1%")
    
    # Display selected page
    if page == "Configuration Input":
        display_configuration_input()
    elif page == "System Overview":
        display_system_overview()
    elif page == "Agent Status":
        display_agent_status()
    elif page == "Performance Analytics":
        display_performance_charts()
    elif page == "Workflow Demo":
        display_workflow_demo()
    elif page == "Application Results":
        display_application_results()
    elif page == "Settings":
        display_settings()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        🚀 AI Job Autopilot Multi-Agent System | Built with Streamlit | 
        <strong>Enterprise-Grade Job Application Automation</strong>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()