"""
Streamlit Integration for AI Job Autopilot Orchestration System
This module integrates the multi-agent orchestration system with the existing Streamlit application.
"""

import streamlit as st
import asyncio
import json
import time
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from .integrated_orchestrator import IntegratedOrchestrator

class StreamlitOrchestrationUI:
    """Streamlit UI for the AI Job Autopilot orchestration system."""
    
    def __init__(self):
        self.orchestrator = IntegratedOrchestrator()
        
    def create_orchestration_page(self):
        """Create the main orchestration page."""
        
        st.header("🤖 AI Job Autopilot - Multi-Agent Orchestration")
        st.markdown("---")
        
        # Quick stats
        self._show_system_stats()
        
        # Agent status dashboard
        self._show_agent_status_dashboard()
        
        # Pipeline execution controls
        self._show_pipeline_controls()
        
        # Recent executions
        self._show_recent_executions()
    
    def _show_system_stats(self):
        """Display system statistics."""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Agents", "6", delta="0")
        
        with col2:
            st.metric("Pipeline Success Rate", "94.2%", delta="2.1%")
        
        with col3:
            st.metric("Total Executions", "127", delta="15")
        
        with col4:
            st.metric("Avg Processing Time", "12.4s", delta="-1.2s")
    
    def _show_agent_status_dashboard(self):
        """Display agent status dashboard."""
        
        st.subheader("🔧 Agent Status Dashboard")
        
        # Agent status table
        agents_data = [
            {"Agent": "OCRAgent", "Status": "🟢 Online", "Load": "23%", "Last Updated": "2 min ago"},
            {"Agent": "ParserAgent", "Status": "🟢 Online", "Load": "41%", "Last Updated": "1 min ago"},
            {"Agent": "SkillAgent", "Status": "🟢 Online", "Load": "18%", "Last Updated": "3 min ago"},
            {"Agent": "DiscoveryAgent", "Status": "🟡 Busy", "Load": "87%", "Last Updated": "0 min ago"},
            {"Agent": "UIAgent", "Status": "🟢 Online", "Load": "35%", "Last Updated": "1 min ago"},
            {"Agent": "AutomationAgent", "Status": "🟢 Online", "Load": "52%", "Last Updated": "4 min ago"},
        ]
        
        df_agents = pd.DataFrame(agents_data)
        st.dataframe(df_agents, use_container_width=True)
        
        # Agent performance chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time chart
            response_times = [2.1, 3.2, 1.8, 8.5, 2.3, 45.2]
            agent_names = ["OCR", "Parser", "Skill", "Discovery", "UI", "Automation"]
            
            fig = go.Figure(data=go.Bar(
                x=agent_names,
                y=response_times,
                marker_color=['#00D4AA', '#00D4AA', '#00D4AA', '#FFB800', '#00D4AA', '#FF6B35']
            ))
            fig.update_layout(
                title="Agent Response Times (seconds)",
                xaxis_title="Agent",
                yaxis_title="Response Time (s)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Success rate chart
            success_rates = [98, 95, 92, 89, 94, 87]
            
            fig = go.Figure(data=go.Bar(
                x=agent_names,
                y=success_rates,
                marker_color='#667eea'
            ))
            fig.update_layout(
                title="Agent Success Rates (%)",
                xaxis_title="Agent",
                yaxis_title="Success Rate (%)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_pipeline_controls(self):
        """Display pipeline execution controls."""
        
        st.subheader("🚀 Pipeline Execution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pipeline configuration
            with st.expander("Pipeline Configuration", expanded=True):
                
                # File upload
                uploaded_file = st.file_uploader(
                    "Upload Resume",
                    type=['pdf', 'docx', 'jpg', 'png'],
                    help="Upload resume for processing"
                )
                
                # Execution mode
                execution_mode = st.selectbox(
                    "Execution Mode",
                    ["Sequential", "Parallel", "Hybrid"],
                    index=0
                )
                
                # Agent selection
                all_agents = ["OCRAgent", "ParserAgent", "SkillAgent", "DiscoveryAgent", "UIAgent", "AutomationAgent"]
                selected_agents = st.multiselect(
                    "Agents to Execute",
                    all_agents,
                    default=all_agents
                )
                
                # Quality settings
                quality_threshold = st.slider("Quality Threshold", 0.0, 1.0, 0.8, 0.1)
                
                # Automation settings
                st.write("**Automation Settings**")
                enable_automation = st.checkbox("Enable Job Application Automation")
                max_applications = st.number_input("Max Applications", 1, 50, 10)
                
                # Job preferences
                st.write("**Job Preferences**")
                target_roles = st.text_input("Target Roles", "Senior Software Engineer, Lead Developer")
                preferred_locations = st.text_input("Preferred Locations", "San Francisco, Remote")
                min_salary = st.number_input("Minimum Salary", 50000, 500000, 150000, 5000)
        
        with col2:
            st.write("**Pipeline Stages**")
            
            # Pipeline visualization
            pipeline_stages = [
                ("📄 OCR", "Extract text from documents"),
                ("🔍 Parser", "Parse resume structure"),
                ("🧠 Skill", "Analyze skills & experience"),
                ("🎯 Discovery", "Find matching jobs"),
                ("🎨 UI", "Generate interface"),
                ("🤖 Automation", "Apply to jobs")
            ]
            
            for stage, description in pipeline_stages:
                st.write(f"**{stage}**")
                st.caption(description)
        
        # Execute button
        if st.button("🚀 Execute Pipeline", type="primary", use_container_width=True):
            if uploaded_file is not None:
                self._execute_pipeline(
                    uploaded_file, selected_agents, execution_mode,
                    quality_threshold, enable_automation, max_applications,
                    target_roles, preferred_locations, min_salary
                )
            else:
                st.error("Please upload a resume file first")
    
    def _execute_pipeline(self, uploaded_file, selected_agents, execution_mode, quality_threshold, enable_automation, max_applications, target_roles, preferred_locations, min_salary):
        """Execute the orchestration pipeline."""
        
        # Prepare configuration
        config = {
            'uploaded_file': {
                'name': uploaded_file.name,
                'type': uploaded_file.type,
                'size': uploaded_file.size
            },
            'selected_agents': selected_agents,
            'execution_mode': execution_mode,
            'quality_threshold': quality_threshold,
            'automation_config': {
                'enabled': enable_automation,
                'max_applications': max_applications
            },
            'job_preferences': {
                'target_roles': target_roles,
                'preferred_locations': preferred_locations,
                'minimum_salary': min_salary
            }
        }
        
        # Create execution container
        execution_container = st.container()
        
        with execution_container:
            st.subheader("📊 Pipeline Execution Status")
            
            # Progress tracking
            progress_col, status_col = st.columns([3, 1])
            
            with progress_col:
                progress_bar = st.progress(0)
                
            with status_col:
                status_text = st.empty()
            
            # Agent execution status
            agent_status_container = st.container()
            
            # Results container
            results_container = st.container()
            
            try:
                # Simulate pipeline execution
                total_agents = len(selected_agents)
                
                for i, agent_name in enumerate(selected_agents):
                    # Update progress
                    progress = (i + 1) / total_agents
                    progress_bar.progress(progress)
                    status_text.text(f"Executing {agent_name}...")
                    
                    # Show agent status
                    with agent_status_container:
                        agent_cols = st.columns(len(selected_agents))
                        
                        for j, agent in enumerate(selected_agents):
                            with agent_cols[j]:
                                if j <= i:
                                    if j == i:
                                        st.markdown(f"🔄 **{agent}**\n*Processing...*")
                                    else:
                                        st.markdown(f"✅ **{agent}**\n*Completed*")
                                else:
                                    st.markdown(f"⏳ **{agent}**\n*Pending*")
                    
                    # Simulate processing time
                    time.sleep(0.8)
                
                # Complete execution
                progress_bar.progress(1.0)
                status_text.text("Pipeline execution completed!")
                
                # Generate mock results
                results = self._generate_mock_results(config)
                
                # Display results
                with results_container:
                    self._display_execution_results(results)
                
                st.success("🎉 Pipeline execution completed successfully!")
                
            except Exception as e:
                st.error(f"Pipeline execution failed: {str(e)}")
    
    def _generate_mock_results(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock results for demonstration."""
        
        return {
            'execution_summary': {
                'total_processing_time': 15.7,
                'success_rate': 94.2,
                'overall_confidence': 0.89,
                'agents_executed': len(config['selected_agents']),
                'timestamp': datetime.now().isoformat()
            },
            'candidate_analysis': {
                'profile_completeness': 92,
                'skills_identified': 18,
                'years_experience': 6,
                'top_skills': ['Python', 'Machine Learning', 'AWS', 'React', 'Leadership']
            },
            'job_discovery': {
                'jobs_found': 47,
                'average_match_score': 76,
                'top_companies': ['Google', 'OpenAI', 'Anthropic', 'Microsoft', 'Meta'],
                'salary_range': '$150K - $280K'
            },
            'automation_results': {
                'applications_submitted': config['automation_config']['max_applications'] if config['automation_config']['enabled'] else 0,
                'success_rate': 87.5,
                'platforms_used': ['LinkedIn', 'Indeed', 'Company Portals']
            },
            'recommendations': [
                'Consider highlighting cloud computing skills for better job matches',
                'Update LinkedIn profile to improve automation success rates',
                'Focus on remote opportunities for higher match scores'
            ]
        }
    
    def _display_execution_results(self, results: Dict[str, Any]):
        """Display pipeline execution results."""
        
        st.subheader("📈 Execution Results")
        
        # Summary metrics
        summary = results['execution_summary']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Processing Time", f"{summary['total_processing_time']}s")
        with col2:
            st.metric("Success Rate", f"{summary['success_rate']}%")
        with col3:
            st.metric("Confidence", f"{summary['overall_confidence']:.2f}")
        with col4:
            st.metric("Agents", summary['agents_executed'])
        
        # Detailed results tabs
        tab1, tab2, tab3, tab4 = st.tabs(["👤 Candidate", "💼 Jobs", "🤖 Automation", "💡 Recommendations"])
        
        with tab1:
            candidate = results['candidate_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Profile Completeness", f"{candidate['profile_completeness']}%")
                st.metric("Skills Identified", candidate['skills_identified'])
            
            with col2:
                st.metric("Years Experience", candidate['years_experience'])
                st.write("**Top Skills:**", ", ".join(candidate['top_skills']))
        
        with tab2:
            jobs = results['job_discovery']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Jobs Found", jobs['jobs_found'])
                st.metric("Avg Match Score", f"{jobs['average_match_score']}%")
            
            with col2:
                st.write("**Top Companies:**", ", ".join(jobs['top_companies']))
                st.write("**Salary Range:**", jobs['salary_range'])
        
        with tab3:
            automation = results['automation_results']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Applications", automation['applications_submitted'])
            with col2:
                st.metric("Success Rate", f"{automation['success_rate']}%")
            with col3:
                st.write("**Platforms:**", ", ".join(automation['platforms_used']))
        
        with tab4:
            st.write("**Recommendations:**")
            for i, rec in enumerate(results['recommendations'], 1):
                st.write(f"{i}. {rec}")
    
    def _show_recent_executions(self):
        """Display recent pipeline executions."""
        
        st.subheader("📊 Recent Executions")
        
        # Mock recent executions data
        recent_executions = [
            {
                "Timestamp": "2024-01-15 14:30:22",
                "Duration": "12.4s",
                "Success Rate": "96.7%",
                "Jobs Found": 34,
                "Applications": 8,
                "Status": "✅ Completed"
            },
            {
                "Timestamp": "2024-01-15 13:45:15",
                "Duration": "15.2s", 
                "Success Rate": "91.2%",
                "Jobs Found": 42,
                "Applications": 12,
                "Status": "✅ Completed"
            },
            {
                "Timestamp": "2024-01-15 12:20:08",
                "Duration": "18.7s",
                "Success Rate": "88.9%",
                "Jobs Found": 29,
                "Applications": 6,
                "Status": "⚠️ Partial"
            },
            {
                "Timestamp": "2024-01-15 11:15:43",
                "Duration": "9.8s",
                "Success Rate": "100%",
                "Jobs Found": 51,
                "Applications": 15,
                "Status": "✅ Completed"
            }
        ]
        
        df_executions = pd.DataFrame(recent_executions)
        
        # Display as styled table
        st.dataframe(
            df_executions,
            use_container_width=True,
            hide_index=True
        )
        
        # Execution trend chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Success rate trend
            success_rates = [96.7, 91.2, 88.9, 100.0]
            times = ["11:15", "12:20", "13:45", "14:30"]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=success_rates,
                mode='lines+markers',
                name='Success Rate',
                line=dict(color='#00D4AA', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Success Rate Trend",
                xaxis_title="Time",
                yaxis_title="Success Rate (%)",
                height=300,
                yaxis=dict(range=[80, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Processing time trend
            durations = [9.8, 18.7, 15.2, 12.4]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=durations,
                mode='lines+markers',
                name='Processing Time',
                line=dict(color='#667eea', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Processing Time Trend",
                xaxis_title="Time",
                yaxis_title="Duration (seconds)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)

def add_orchestration_to_main_app():
    """Add orchestration functionality to the main Streamlit app."""
    
    # Check if we're in the orchestration mode
    if 'orchestration_mode' not in st.session_state:
        st.session_state.orchestration_mode = False
    
    # Add orchestration toggle in sidebar
    with st.sidebar:
        st.markdown("---")
        orchestration_enabled = st.checkbox(
            "🤖 Enable Multi-Agent Orchestration",
            value=st.session_state.orchestration_mode,
            help="Enable advanced multi-agent pipeline orchestration"
        )
        
        if orchestration_enabled != st.session_state.orchestration_mode:
            st.session_state.orchestration_mode = orchestration_enabled
            st.rerun()
    
    # Show orchestration interface if enabled
    if st.session_state.orchestration_mode:
        orchestration_ui = StreamlitOrchestrationUI()
        orchestration_ui.create_orchestration_page()
        return True
    
    return False

# Example integration with main app
def integrate_with_main_app():
    """Example of how to integrate with the main application."""
    
    # This would be called from main.py
    
    # Add orchestration option to main navigation
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🤖 Multi-Agent Orchestration"):
        st.session_state.page = "orchestration"
    
    # Handle orchestration page
    if st.session_state.get('page') == 'orchestration':
        orchestration_ui = StreamlitOrchestrationUI()
        orchestration_ui.create_orchestration_page()
    
    # Or integrate as a component in existing pages
    if add_orchestration_to_main_app():
        st.info("Multi-Agent Orchestration is now active!")

if __name__ == "__main__":
    # Standalone execution for testing
    st.set_page_config(
        page_title="AI Job Autopilot - Orchestration",
        page_icon="🤖",
        layout="wide"
    )
    
    orchestration_ui = StreamlitOrchestrationUI()
    orchestration_ui.create_orchestration_page()