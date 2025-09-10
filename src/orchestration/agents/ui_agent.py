"""
🎨 UIAgent: Frontend design & code agent for crafting stunning modern UI
Frontend design agent for creating production-ready, accessible, and visually stunning UI components.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, ProcessingResult

class UIAgent(BaseAgent):
    """
    🎨 UIAgent: Frontend design & code agent for crafting stunning modern UI
    
    Goals:
    1. Generate beautiful, responsive, animated UI components for the job automation platform
    2. Follow current best practices in modern frontend design:
       - Glassmorphism style (frosted background, soft blur, light shadows)
       - Responsive grid or flex layout (desktop, tablet, mobile)
       - Dark/Light mode support using CSS variables or theme hooks
       - Accessible typography (WCAG-compliant contrast, font sizing)
       - Smooth micro-interactions and transition animations
       - UI elements that support screen readers (ARIA labels, roles)
    3. Allow dynamic injection of content (via props or template placeholders)
    4. Must be modular, component-based, fully mobile responsive
    5. Adheres to design tokens and BEM or atomic class structure
    """
    
    def _setup_agent_specific_config(self):
        """Setup UI Agent specific configurations."""
        self.frameworks = self.config.custom_settings.get('frameworks', ['react', 'vue', 'vanilla'])
        self.design_system = self.config.custom_settings.get('design_system', 'glassmorphism')
        self.responsive_design = self.config.custom_settings.get('responsive_design', True)
        self.accessibility_compliance = self.config.custom_settings.get('accessibility_compliance', 'WCAG_2.1_AA')
        self.dark_mode_support = self.config.custom_settings.get('dark_mode_support', True)
        self.animation_support = self.config.custom_settings.get('animation_support', True)
        
        # Enhanced design system with dark/light mode support
        self.design_tokens = {
            'glassmorphism': {
                'light': {
                    'primary': '#6366f1',
                    'secondary': '#8b5cf6',
                    'accent': '#06b6d4',
                    'success': '#10b981',
                    'warning': '#f59e0b',
                    'error': '#ef4444',
                    'background_primary': 'rgba(255, 255, 255, 0.1)',
                    'background_secondary': 'rgba(255, 255, 255, 0.2)',
                    'surface_elevated': 'rgba(255, 255, 255, 0.25)',
                    'text_primary': '#1f2937',
                    'text_secondary': '#6b7280',
                    'text_tertiary': '#9ca3af',
                    'border_subtle': 'rgba(255, 255, 255, 0.2)',
                    'border_strong': 'rgba(255, 255, 255, 0.4)',
                    'shadow_light': '0 8px 32px rgba(31, 38, 135, 0.15)',
                    'shadow_medium': '0 12px 40px rgba(31, 38, 135, 0.25)',
                    'shadow_heavy': '0 16px 48px rgba(31, 38, 135, 0.35)',
                    'backdrop_blur': '12px'
                },
                'dark': {
                    'primary': '#818cf8',
                    'secondary': '#a78bfa',
                    'accent': '#22d3ee',
                    'success': '#34d399',
                    'warning': '#fbbf24',
                    'error': '#f87171',
                    'background_primary': 'rgba(17, 24, 39, 0.8)',
                    'background_secondary': 'rgba(31, 41, 55, 0.8)',
                    'surface_elevated': 'rgba(55, 65, 81, 0.8)',
                    'text_primary': '#f9fafb',
                    'text_secondary': '#d1d5db',
                    'text_tertiary': '#9ca3af',
                    'border_subtle': 'rgba(75, 85, 99, 0.3)',
                    'border_strong': 'rgba(107, 114, 128, 0.4)',
                    'shadow_light': '0 8px 32px rgba(0, 0, 0, 0.3)',
                    'shadow_medium': '0 12px 40px rgba(0, 0, 0, 0.4)',
                    'shadow_heavy': '0 16px 48px rgba(0, 0, 0, 0.5)',
                    'backdrop_blur': '16px'
                }
            }
        }
        
        # Typography system
        self.typography_scale = {
            'font_families': {
                'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                'mono': ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace'],
                'display': ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif']
            },
            'font_sizes': {
                'xs': '0.75rem',    # 12px
                'sm': '0.875rem',   # 14px
                'base': '1rem',     # 16px
                'lg': '1.125rem',   # 18px
                'xl': '1.25rem',    # 20px
                '2xl': '1.5rem',    # 24px
                '3xl': '1.875rem',  # 30px
                '4xl': '2.25rem',   # 36px
                '5xl': '3rem',      # 48px
                '6xl': '3.75rem'    # 60px
            },
            'font_weights': {
                'thin': 100,
                'light': 300,
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700,
                'extrabold': 800,
                'black': 900
            },
            'line_heights': {
                'none': 1,
                'tight': 1.25,
                'snug': 1.375,
                'normal': 1.5,
                'relaxed': 1.625,
                'loose': 2
            }
        }
        
        # Spacing system (8px base unit)
        self.spacing_scale = {
            '0': '0',
            'px': '1px',
            '0.5': '0.125rem',  # 2px
            '1': '0.25rem',     # 4px
            '1.5': '0.375rem',  # 6px
            '2': '0.5rem',      # 8px
            '2.5': '0.625rem',  # 10px
            '3': '0.75rem',     # 12px
            '3.5': '0.875rem',  # 14px
            '4': '1rem',        # 16px
            '5': '1.25rem',     # 20px
            '6': '1.5rem',      # 24px
            '7': '1.75rem',     # 28px
            '8': '2rem',        # 32px
            '9': '2.25rem',     # 36px
            '10': '2.5rem',     # 40px
            '12': '3rem',       # 48px
            '14': '3.5rem',     # 56px
            '16': '4rem',       # 64px
            '20': '5rem',       # 80px
            '24': '6rem',       # 96px
            '32': '8rem',       # 128px
            '40': '10rem',      # 160px
            '48': '12rem',      # 192px
            '56': '14rem',      # 224px
            '64': '16rem'       # 256px
        }
        
        # Animation system
        self.animation_presets = {
            'durations': {
                'fast': '150ms',
                'normal': '250ms',
                'slow': '350ms',
                'slower': '500ms'
            },
            'easings': {
                'ease_out': 'cubic-bezier(0.0, 0.0, 0.2, 1)',
                'ease_in': 'cubic-bezier(0.4, 0.0, 1, 1)',
                'ease_in_out': 'cubic-bezier(0.4, 0.0, 0.2, 1)',
                'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
                'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
            },
            'micro_interactions': {
                'hover_lift': 'transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.15);',
                'click_scale': 'transform: scale(0.98);',
                'fade_in': 'opacity: 0; transform: translateY(10px);',
                'slide_in': 'transform: translateX(-20px); opacity: 0;',
                'scale_in': 'transform: scale(0.9); opacity: 0;'
            }
        }
        
        self.component_templates = {
            'dashboard': 'dashboard_template',
            'job_cards': 'job_card_template',
            'application_tracker': 'tracker_template',
            'profile_viewer': 'profile_template',
            'analytics_panel': 'analytics_template'
        }
        
        self.logger.info("UI Agent configured with glassmorphism design system")
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data specific to UI Agent."""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input must be a dictionary")
            return {'valid': False, 'errors': errors}
        
        # Check for required fields
        required_fields = ['job_matches', 'candidate_profile', 'ui_specifications']
        for field in required_fields:
            if field not in input_data:
                errors.append(f"Missing required field: {field}")
        
        ui_specs = input_data.get('ui_specifications', {})
        if not ui_specs.get('components'):
            errors.append("UI specifications must include components list")
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Any) -> ProcessingResult:
        """Internal processing for UI component generation."""
        
        try:
            job_matches = input_data['job_matches']
            candidate_profile = input_data['candidate_profile']
            ui_specs = input_data['ui_specifications']
            
            # Generate UI components based on specifications
            components = await self._generate_components(job_matches, candidate_profile, ui_specs)
            
            # Generate responsive styles
            styles = await self._generate_styles(ui_specs)
            
            # Generate accessibility features
            accessibility = await self._generate_accessibility_features(ui_specs)
            
            # Generate interactive features
            interactions = await self._generate_interactions(job_matches, ui_specs)
            
            return ProcessingResult(
                success=True,
                result={
                    'generated_components': components,
                    'styles': styles,
                    'accessibility': accessibility,
                    'interactions': interactions,
                    'responsive': self.responsive_design,
                    'design_system': self.design_system,
                    'framework': ui_specs.get('framework', 'react')
                },
                confidence=0.95,
                processing_time=0.0,
                metadata={
                    'components_generated': len(components),
                    'framework_used': ui_specs.get('framework', 'react'),
                    'accessibility_level': self.accessibility_compliance
                }
            )
            
        except Exception as e:
            self.logger.error(f"UI generation failed: {str(e)}")
            return ProcessingResult(
                success=False,
                result=None,
                confidence=0.0,
                processing_time=0.0,
                metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def _generate_components(self, job_matches: List[Dict[str, Any]], 
                                 candidate_profile: Dict[str, Any], 
                                 ui_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI components based on specifications."""
        
        framework = ui_specs.get('framework', 'react')
        components_to_generate = ui_specs.get('components', [])
        
        generated_components = {}
        
        for component_type in components_to_generate:
            if component_type == 'dashboard':
                generated_components['dashboard'] = await self._generate_dashboard(job_matches, candidate_profile, framework)
            elif component_type == 'job_cards':
                generated_components['job_cards'] = await self._generate_job_cards(job_matches, framework)
            elif component_type == 'application_tracker':
                generated_components['application_tracker'] = await self._generate_application_tracker(job_matches, framework)
            elif component_type == 'profile_viewer':
                generated_components['profile_viewer'] = await self._generate_profile_viewer(candidate_profile, framework)
            elif component_type == 'analytics_panel':
                generated_components['analytics_panel'] = await self._generate_analytics_panel(job_matches, framework)
        
        return generated_components
    
    async def _generate_dashboard(self, job_matches: List[Dict[str, Any]], 
                                candidate_profile: Dict[str, Any], 
                                framework: str) -> Dict[str, str]:
        """Generate main dashboard component."""
        
        if framework == 'react':
            component_code = f'''
import React, {{ useState, useEffect }} from 'react';
import './Dashboard.css';

const Dashboard = () => {{
  const [stats, setStats] = useState({{
    totalJobs: {len(job_matches)},
    highMatches: {len([job for job in job_matches if job.get('match_percentage', 0) > 80])},
    applicationsSubmitted: 0,
    profileViews: 0
  }});

  const [jobMatches] = useState({json.dumps(job_matches[:5], indent=2)});

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1 className="dashboard-title">Job Search Dashboard</h1>
        <div className="profile-summary">
          <h2>{candidate_profile.get('personal_information', {}).get('full_name', 'Professional')}</h2>
          <p className="profile-tagline">
            {len(candidate_profile.get('skills_analysis', {}).get('technical_skills', []))} Technical Skills • 
            {candidate_profile.get('experience_years', 0)} Years Experience
          </p>
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="stats-section glass-card">
          <h3>Overview</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">{{stats.totalJobs}}</span>
              <span className="stat-label">Jobs Found</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{{stats.highMatches}}</span>
              <span className="stat-label">High Matches</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{{stats.applicationsSubmitted}}</span>
              <span className="stat-label">Applications</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{{stats.profileViews}}</span>
              <span className="stat-label">Profile Views</span>
            </div>
          </div>
        </div>

        <div className="top-matches glass-card">
          <h3>Top Job Matches</h3>
          <div className="job-matches-list">
            {{jobMatches.slice(0, 3).map((job, index) => (
              <div key={{index}} className="job-match-item">
                <div className="job-info">
                  <h4 className="job-title">{{job.title}}</h4>
                  <p className="job-company">{{job.company}}</p>
                  <span className="job-location">{{job.location}}</span>
                </div>
                <div className="match-score">
                  <div className="score-circle" style={{{{
                    background: `conic-gradient(#6366f1 ${{job.match_percentage * 3.6}}deg, #e5e7eb 0deg)`
                  }}}}>
                    <span>{{Math.round(job.match_percentage)}}%</span>
                  </div>
                </div>
              </div>
            ))}}
          </div>
        </div>

        <div className="skills-analysis glass-card">
          <h3>Skills Analysis</h3>
          <div className="skills-breakdown">
            <div className="skill-category">
              <h4>Top Skills</h4>
              <div className="skills-list">
                {[skill[:3] for skill in candidate_profile.get('skills_analysis', {}).get('technical_skills', [])]}
                {{JSON.stringify({[skill for skill in candidate_profile.get('skills_analysis', {}).get('technical_skills', [])][:5]}).slice(1, -1).split(',').map((skill, index) => (
                  <span key={{index}} className="skill-tag">{{skill.replace(/"/g, '')}}</span>
                ))}}
              </div>
            </div>
          </div>
        </div>

        <div className="recent-activity glass-card">
          <h3>Recent Activity</h3>
          <div className="activity-timeline">
            <div className="activity-item">
              <div className="activity-icon">📊</div>
              <div className="activity-content">
                <p>Job search completed</p>
                <span className="activity-time">{datetime.now().strftime("%H:%M")}</span>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon">✨</div>
              <div className="activity-content">
                <p>Profile optimized</p>
                <span className="activity-time">{(datetime.now()).strftime("%H:%M")}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}};

export default Dashboard;
'''
            
            css_code = '''
.dashboard-container {
  padding: 2rem;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-title {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 1rem;
  font-weight: 700;
}

.profile-summary h2 {
  color: white;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.profile-tagline {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #6366f1;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: rgba(0, 0, 0, 0.7);
  font-size: 0.9rem;
}

.job-match-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 1rem;
}

.job-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.job-company {
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.job-location {
  font-size: 0.8rem;
  color: #9ca3af;
}

.score-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 0.8rem;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.skill-tag {
  background: rgba(99, 102, 241, 0.2);
  color: #6366f1;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.activity-timeline {
  margin-top: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  margin-bottom: 0.75rem;
}

.activity-icon {
  font-size: 1.2rem;
  margin-right: 0.75rem;
}

.activity-content p {
  margin: 0;
  color: #1f2937;
  font-weight: 500;
}

.activity-time {
  font-size: 0.8rem;
  color: #6b7280;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-title {
    font-size: 2rem;
  }
}
'''
            
            return {
                'component': component_code,
                'styles': css_code,
                'type': 'react_component'
            }
        
        # Add other framework implementations here
        return {'component': '', 'styles': '', 'type': 'unsupported_framework'}
    
    async def _generate_job_cards(self, job_matches: List[Dict[str, Any]], framework: str) -> Dict[str, str]:
        """Generate job card components."""
        
        if framework == 'react':
            component_code = '''
import React from 'react';
import './JobCards.css';

const JobCard = ({ job, onApply, onSave }) => {
  const getMatchColor = (percentage) => {
    if (percentage >= 90) return '#10b981'; // green
    if (percentage >= 80) return '#f59e0b'; // yellow
    if (percentage >= 70) return '#ef4444'; // red
    return '#6b7280'; // gray
  };

  return (
    <div className="job-card glass-card">
      <div className="job-card-header">
        <div className="job-info">
          <h3 className="job-title">{job.title}</h3>
          <p className="job-company">{job.company}</p>
          <span className="job-location">{job.location}</span>
        </div>
        <div className="match-badge" style={{ borderColor: getMatchColor(job.match_percentage) }}>
          <span className="match-percentage" style={{ color: getMatchColor(job.match_percentage) }}>
            {Math.round(job.match_percentage)}%
          </span>
          <span className="match-label">Match</span>
        </div>
      </div>

      <div className="job-details">
        <div className="salary-info">
          <span className="salary-range">
            ${job.compensation_analysis?.base_salary_min?.toLocaleString()} - 
            ${job.compensation_analysis?.base_salary_max?.toLocaleString()}
          </span>
          {job.compensation_analysis?.equity && (
            <span className="equity-badge">+ Equity</span>
          )}
        </div>

        <div className="skills-section">
          <h4>Required Skills</h4>
          <div className="skills-list">
            {job.requirements?.required_skills?.slice(0, 5).map((skill, index) => (
              <span key={index} className="skill-tag">{skill}</span>
            ))}
          </div>
        </div>

        <div className="job-meta">
          <div className="meta-item">
            <span className="meta-label">Experience</span>
            <span className="meta-value">{job.requirements?.experience_years}+ years</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Posted</span>
            <span className="meta-value">
              {new Date(job.posted_date).toLocaleDateString()}
            </span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Work</span>
            <span className="meta-value">{job.location_details?.work_arrangement}</span>
          </div>
        </div>
      </div>

      <div className="job-card-actions">
        <button 
          className="btn btn-secondary"
          onClick={() => onSave(job.job_id)}
          aria-label={`Save job ${job.title} at ${job.company}`}
        >
          Save
        </button>
        <button 
          className="btn btn-primary"
          onClick={() => onApply(job.job_id)}
          aria-label={`Apply to ${job.title} at ${job.company}`}
        >
          Apply Now
        </button>
      </div>
    </div>
  );
};

const JobCards = ({ jobs, onApply, onSave }) => {
  return (
    <div className="job-cards-container">
      <div className="job-cards-grid">
        {jobs.map((job, index) => (
          <JobCard 
            key={job.job_id || index} 
            job={job} 
            onApply={onApply}
            onSave={onSave}
          />
        ))}
      </div>
    </div>
  );
};

export default JobCards;
'''
            
            css_code = '''
.job-cards-container {
  padding: 1rem;
}

.job-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.job-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.job-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.job-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.job-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.job-company {
  color: #6366f1;
  font-weight: 500;
  margin: 0 0 0.25rem 0;
}

.job-location {
  color: #6b7280;
  font-size: 0.9rem;
}

.match-badge {
  text-align: center;
  padding: 0.75rem;
  border: 2px solid;
  border-radius: 50%;
  min-width: 70px;
  height: 70px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
}

.match-percentage {
  font-size: 1.1rem;
  font-weight: bold;
  line-height: 1;
}

.match-label {
  font-size: 0.7rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.salary-info {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 10px;
}

.salary-range {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

.equity-badge {
  background: #10b981;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-size: 0.75rem;
  margin-left: 0.5rem;
  font-weight: 500;
}

.skills-section h4 {
  font-size: 0.9rem;
  color: #374151;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.skill-tag {
  background: rgba(99, 102, 241, 0.2);
  color: #6366f1;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.job-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.meta-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-value {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1f2937;
}

.job-card-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5856eb, #7c3aed);
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.8);
  color: #374151;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .job-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .job-card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .match-badge {
    margin-top: 0.5rem;
    align-self: flex-end;
  }
  
  .job-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .meta-item {
    flex-direction: row;
    justify-content: space-between;
  }
}
'''
            
            return {
                'component': component_code,
                'styles': css_code,
                'type': 'react_component'
            }
        
        return {'component': '', 'styles': '', 'type': 'unsupported_framework'}
    
    async def _generate_application_tracker(self, job_matches: List[Dict[str, Any]], framework: str) -> Dict[str, str]:
        """Generate application tracking component."""
        
        if framework == 'react':
            component_code = '''
import React, { useState } from 'react';
import './ApplicationTracker.css';

const ApplicationStatus = {
  SAVED: 'saved',
  APPLIED: 'applied',
  INTERVIEW: 'interview',
  OFFER: 'offer',
  REJECTED: 'rejected'
};

const ApplicationTracker = ({ applications = [] }) => {
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  const getStatusColor = (status) => {
    switch (status) {
      case ApplicationStatus.SAVED: return '#6b7280';
      case ApplicationStatus.APPLIED: return '#3b82f6';
      case ApplicationStatus.INTERVIEW: return '#f59e0b';
      case ApplicationStatus.OFFER: return '#10b981';
      case ApplicationStatus.REJECTED: return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case ApplicationStatus.SAVED: return '📋';
      case ApplicationStatus.APPLIED: return '📤';
      case ApplicationStatus.INTERVIEW: return '🗣️';
      case ApplicationStatus.OFFER: return '🎉';
      case ApplicationStatus.REJECTED: return '❌';
      default: return '📋';
    }
  };

  const filteredApplications = applications.filter(app => 
    filterStatus === 'all' || app.status === filterStatus
  );

  const sortedApplications = filteredApplications.sort((a, b) => {
    if (sortBy === 'date') {
      return new Date(b.appliedDate) - new Date(a.appliedDate);
    }
    if (sortBy === 'company') {
      return a.company.localeCompare(b.company);
    }
    return 0;
  });

  return (
    <div className="application-tracker">
      <div className="tracker-header">
        <h2>Application Tracker</h2>
        
        <div className="tracker-controls">
          <div className="filter-group">
            <label htmlFor="status-filter">Filter by Status:</label>
            <select 
              id="status-filter"
              value={filterStatus} 
              onChange={(e) => setFilterStatus(e.target.value)}
              className="control-select"
            >
              <option value="all">All Applications</option>
              <option value={ApplicationStatus.SAVED}>Saved</option>
              <option value={ApplicationStatus.APPLIED}>Applied</option>
              <option value={ApplicationStatus.INTERVIEW}>Interview</option>
              <option value={ApplicationStatus.OFFER}>Offer</option>
              <option value={ApplicationStatus.REJECTED}>Rejected</option>
            </select>
          </div>
          
          <div className="sort-group">
            <label htmlFor="sort-select">Sort by:</label>
            <select 
              id="sort-select"
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="control-select"
            >
              <option value="date">Date Applied</option>
              <option value="company">Company Name</option>
            </select>
          </div>
        </div>
      </div>

      <div className="applications-stats">
        <div className="stat-card">
          <span className="stat-number">{applications.length}</span>
          <span className="stat-label">Total Applications</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">
            {applications.filter(app => app.status === ApplicationStatus.INTERVIEW).length}
          </span>
          <span className="stat-label">Interviews</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">
            {applications.filter(app => app.status === ApplicationStatus.OFFER).length}
          </span>
          <span className="stat-label">Offers</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">
            {applications.length > 0 ? 
              Math.round((applications.filter(app => app.status === ApplicationStatus.OFFER).length / applications.length) * 100) 
              : 0}%
          </span>
          <span className="stat-label">Success Rate</span>
        </div>
      </div>

      <div className="applications-list">
        {sortedApplications.length === 0 ? (
          <div className="empty-state">
            <p>No applications found</p>
            <span>Start applying to jobs to see them here!</span>
          </div>
        ) : (
          sortedApplications.map((application, index) => (
            <div key={application.id || index} className="application-item glass-card">
              <div className="application-header">
                <div className="job-info">
                  <h3 className="job-title">{application.title}</h3>
                  <p className="company-name">{application.company}</p>
                  <span className="location">{application.location}</span>
                </div>
                
                <div className="status-section">
                  <div 
                    className="status-badge"
                    style={{ 
                      backgroundColor: getStatusColor(application.status),
                      color: 'white'
                    }}
                  >
                    <span className="status-icon">{getStatusIcon(application.status)}</span>
                    <span className="status-text">{application.status.toUpperCase()}</span>
                  </div>
                </div>
              </div>

              <div className="application-details">
                <div className="detail-item">
                  <span className="detail-label">Applied:</span>
                  <span className="detail-value">
                    {new Date(application.appliedDate || Date.now()).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="detail-item">
                  <span className="detail-label">Salary Range:</span>
                  <span className="detail-value">
                    ${application.salaryMin?.toLocaleString()} - ${application.salaryMax?.toLocaleString()}
                  </span>
                </div>
                
                {application.nextStep && (
                  <div className="detail-item">
                    <span className="detail-label">Next Step:</span>
                    <span className="detail-value next-step">{application.nextStep}</span>
                  </div>
                )}
              </div>

              <div className="application-actions">
                <button className="btn btn-outline">View Details</button>
                <button className="btn btn-outline">Update Status</button>
                {application.applicationUrl && (
                  <a 
                    href={application.applicationUrl} 
                    className="btn btn-primary"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Application
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ApplicationTracker;
'''
            
            css_code = '''
.application-tracker {
  padding: 1.5rem;
}

.tracker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.tracker-header h2 {
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 700;
}

.tracker-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-group, .sort-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label, .sort-group label {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
}

.control-select {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  min-width: 140px;
}

.applications-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: bold;
  color: #6366f1;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.empty-state p {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.application-item {
  padding: 1.5rem;
  transition: transform 0.2s ease;
}

.application-item:hover {
  transform: translateY(-2px);
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.job-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.company-name {
  color: #6366f1;
  font-weight: 500;
  margin: 0 0 0.25rem 0;
}

.location {
  color: #6b7280;
  font-size: 0.9rem;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.application-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-weight: 500;
  color: #6b7280;
  font-size: 0.9rem;
}

.detail-value {
  color: #1f2937;
  font-weight: 600;
}

.next-step {
  color: #f59e0b;
  font-style: italic;
}

.application-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  text-decoration: none;
  text-align: center;
}

.btn-outline {
  background: rgba(255, 255, 255, 0.8);
  color: #374151;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5856eb, #7c3aed);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .tracker-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tracker-controls {
    justify-content: space-between;
  }
  
  .application-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .application-details {
    grid-template-columns: 1fr;
  }
  
  .application-actions {
    flex-direction: column;
  }
}
'''
            
            return {
                'component': component_code,
                'styles': css_code,
                'type': 'react_component'
            }
        
        return {'component': '', 'styles': '', 'type': 'unsupported_framework'}
    
    async def _generate_profile_viewer(self, candidate_profile: Dict[str, Any], framework: str) -> Dict[str, str]:
        """Generate profile viewer component."""
        
        if framework == 'react':
            component_code = f'''
import React, {{ useState }} from 'react';
import './ProfileViewer.css';

const ProfileViewer = () => {{
  const [activeSection, setActiveSection] = useState('overview');
  
  const profile = {json.dumps(candidate_profile, indent=2)};

  const renderSkills = (skills) => {{
    if (Array.isArray(skills)) {{
      return skills.slice(0, 12).map((skill, index) => (
        <span key={{index}} className="skill-tag">
          {{typeof skill === 'object' ? skill.skill || skill.name : skill}}
        </span>
      ));
    }}
    return null;
  }};

  return (
    <div className="profile-viewer">
      <div className="profile-header glass-card">
        <div className="profile-avatar">
          <div className="avatar-circle">
            {{profile.personal_information?.full_name?.charAt(0) || 'P'}}
          </div>
        </div>
        
        <div className="profile-info">
          <h1 className="profile-name">
            {{profile.personal_information?.full_name || 'Professional'}}
          </h1>
          <p className="profile-title">
            {{profile.work_experience?.[0]?.title || 'Software Professional'}}
          </p>
          <div className="profile-meta">
            <span className="meta-item">
              📍 {{profile.personal_information?.location || 'Location'}}
            </span>
            <span className="meta-item">
              💼 {{profile.experience_years || 0}} years experience
            </span>
            <span className="meta-item">
              🎓 {{profile.education?.[0]?.degree || 'Education'}}
            </span>
          </div>
        </div>
      </div>

      <div className="profile-nav">
        <button 
          className={{`nav-button ${{activeSection === 'overview' ? 'active' : ''}}`}}
          onClick={{() => setActiveSection('overview')}}
        >
          Overview
        </button>
        <button 
          className={{`nav-button ${{activeSection === 'experience' ? 'active' : ''}}`}}
          onClick={{() => setActiveSection('experience')}}
        >
          Experience
        </button>
        <button 
          className={{`nav-button ${{activeSection === 'skills' ? 'active' : ''}}`}}
          onClick={{() => setActiveSection('skills')}}
        >
          Skills
        </button>
        <button 
          className={{`nav-button ${{activeSection === 'education' ? 'active' : ''}}`}}
          onClick={{() => setActiveSection('education')}}
        >
          Education
        </button>
      </div>

      <div className="profile-content">
        {{activeSection === 'overview' && (
          <div className="overview-section">
            <div className="glass-card">
              <h3>Professional Summary</h3>
              <p className="summary-text">
                {{profile.professional_summary || 
                  'Experienced professional with expertise in modern technologies and a track record of delivering high-quality solutions.'}}
              </p>
            </div>
            
            <div className="stats-grid">
              <div className="stat-item glass-card">
                <span className="stat-number">{{profile.work_experience?.length || 0}}</span>
                <span className="stat-label">Positions</span>
              </div>
              <div className="stat-item glass-card">
                <span className="stat-number">{{profile.skills_analysis?.technical_skills?.length || 0}}</span>
                <span className="stat-label">Skills</span>
              </div>
              <div className="stat-item glass-card">
                <span className="stat-number">{{profile.education?.length || 0}}</span>
                <span className="stat-label">Degrees</span>
              </div>
              <div className="stat-item glass-card">
                <span className="stat-number">{{profile.certifications?.length || 0}}</span>
                <span className="stat-label">Certifications</span>
              </div>
            </div>
          </div>
        )}}

        {{activeSection === 'experience' && (
          <div className="experience-section">
            {{profile.work_experience?.map((job, index) => (
              <div key={{index}} className="experience-item glass-card">
                <div className="experience-header">
                  <h3 className="job-title">{{job.title}}</h3>
                  <span className="job-duration">{{job.duration}}</span>
                </div>
                <p className="company-name">{{job.company}}</p>
                <p className="job-location">{{job.location}}</p>
                <div className="job-description">
                  <p>{{job.description}}</p>
                </div>
              </div>
            )) || (
              <div className="empty-state">
                <p>No work experience information available</p>
              </div>
            )}}
          </div>
        )}}

        {{activeSection === 'skills' && (
          <div className="skills-section">
            <div className="skills-category glass-card">
              <h3>Technical Skills</h3>
              <div className="skills-list">
                {{renderSkills(profile.skills_analysis?.technical_skills)}}
              </div>
            </div>
            
            {{profile.skills_analysis?.soft_skills && (
              <div className="skills-category glass-card">
                <h3>Soft Skills</h3>
                <div className="skills-list">
                  {{renderSkills(profile.skills_analysis.soft_skills)}}
                </div>
              </div>
            )}}
          </div>
        )}}

        {{activeSection === 'education' && (
          <div className="education-section">
            {{profile.education?.map((edu, index) => (
              <div key={{index}} className="education-item glass-card">
                <h3 className="degree">{{edu.degree}}</h3>
                <p className="institution">{{edu.institution}}</p>
                <div className="education-details">
                  <span className="graduation-year">{{edu.graduation_year}}</span>
                  {{edu.gpa && (
                    <span className="gpa">GPA: {{edu.gpa}}</span>
                  )}}
                </div>
                {{edu.relevant_coursework && (
                  <div className="coursework">
                    <h4>Relevant Coursework</h4>
                    <p>{{edu.relevant_coursework}}</p>
                  </div>
                )}}
              </div>
            )) || (
              <div className="empty-state">
                <p>No education information available</p>
              </div>
            )}}
          </div>
        )}}
      </div>
    </div>
  );
}};

export default ProfileViewer;
'''
            
            css_code = '''
.profile-viewer {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 2rem;
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: bold;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.profile-title {
  font-size: 1.2rem;
  color: #6366f1;
  font-weight: 500;
  margin: 0 0 1rem 0;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.meta-item {
  color: #6b7280;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.profile-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 0.5rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-button {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #6b7280;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #1f2937;
}

.nav-button.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.profile-content {
  min-height: 400px;
}

.overview-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.summary-text {
  line-height: 1.6;
  color: #374151;
  font-size: 1.05rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: bold;
  color: #6366f1;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
}

.experience-section, .education-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.experience-item, .education-item {
  padding: 1.5rem;
}

.experience-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.job-title, .degree {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.job-duration {
  color: #6366f1;
  font-weight: 500;
  font-size: 0.9rem;
}

.company-name, .institution {
  color: #6366f1;
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0.25rem 0;
}

.job-location {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0.25rem 0 1rem 0;
}

.job-description {
  line-height: 1.6;
  color: #374151;
}

.skills-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.skills-category {
  padding: 1.5rem;
}

.skills-category h3 {
  color: #1f2937;
  font-size: 1.2rem;
  margin: 0 0 1rem 0;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  background: rgba(99, 102, 241, 0.2);
  color: #6366f1;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  border: 1px solid rgba(99, 102, 241, 0.3);
  font-weight: 500;
}

.education-details {
  display: flex;
  gap: 2rem;
  margin: 0.5rem 0;
  color: #6b7280;
}

.coursework {
  margin-top: 1rem;
}

.coursework h4 {
  color: #374151;
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .profile-name {
    font-size: 2rem;
  }
  
  .profile-meta {
    justify-content: center;
  }
  
  .profile-nav {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .experience-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
'''
            
            return {
                'component': component_code,
                'styles': css_code,
                'type': 'react_component'
            }
        
        return {'component': '', 'styles': '', 'type': 'unsupported_framework'}
    
    async def _generate_analytics_panel(self, job_matches: List[Dict[str, Any]], framework: str) -> Dict[str, str]:
        """Generate analytics panel component."""
        
        if framework == 'react':
            # Calculate analytics data
            total_jobs = len(job_matches)
            high_matches = len([job for job in job_matches if job.get('match_percentage', 0) > 80])
            avg_salary = sum(job.get('compensation_analysis', {}).get('base_salary_min', 0) for job in job_matches) / total_jobs if total_jobs > 0 else 0
            
            component_code = f'''
import React, {{ useState }} from 'react';
import './AnalyticsPanel.css';

const AnalyticsPanel = () => {{
  const [activeMetric, setActiveMetric] = useState('overview');
  
  const analyticsData = {{
    totalJobs: {total_jobs},
    highMatches: {high_matches},
    averageSalary: {int(avg_salary)},
    matchRate: {round((high_matches / total_jobs * 100) if total_jobs > 0 else 0, 1)},
    trends: {{
      jobsThisWeek: 23,
      applicationsThisWeek: 8,
      responseRate: 15.2
    }}
  }};

  const chartData = [
    {{ name: '90-100%', value: {len([job for job in job_matches if job.get('match_percentage', 0) >= 90])}, color: '#10b981' }},
    {{ name: '80-89%', value: {len([job for job in job_matches if 80 <= job.get('match_percentage', 0) < 90])}, color: '#f59e0b' }},
    {{ name: '70-79%', value: {len([job for job in job_matches if 70 <= job.get('match_percentage', 0) < 80])}, color: '#3b82f6' }},
    {{ name: '60-69%', value: {len([job for job in job_matches if 60 <= job.get('match_percentage', 0) < 70])}, color: '#6b7280' }},
    {{ name: '<60%', value: {len([job for job in job_matches if job.get('match_percentage', 0) < 60])}, color: '#ef4444' }}
  ];

  const salaryDistribution = [
    {{ range: '$50k-$75k', count: {len([job for job in job_matches if 50000 <= job.get('compensation_analysis', {}).get('base_salary_min', 0) < 75000])}, percentage: 15 }},
    {{ range: '$75k-$100k', count: {len([job for job in job_matches if 75000 <= job.get('compensation_analysis', {}).get('base_salary_min', 0) < 100000])}, percentage: 25 }},
    {{ range: '$100k-$150k', count: {len([job for job in job_matches if 100000 <= job.get('compensation_analysis', {}).get('base_salary_min', 0) < 150000])}, percentage: 35 }},
    {{ range: '$150k-$200k', count: {len([job for job in job_matches if 150000 <= job.get('compensation_analysis', {}).get('base_salary_min', 0) < 200000])}, percentage: 20 }},
    {{ range: '$200k+', count: {len([job for job in job_matches if job.get('compensation_analysis', {}).get('base_salary_min', 0) >= 200000])}, percentage: 5 }}
  ];

  return (
    <div className="analytics-panel">
      <div className="analytics-header">
        <h2>Job Search Analytics</h2>
        <div className="date-range">
          Last 30 days
        </div>
      </div>

      <div className="metrics-nav">
        <button 
          className={{`metric-button ${{activeMetric === 'overview' ? 'active' : ''}}`}}
          onClick={{() => setActiveMetric('overview')}}
        >
          Overview
        </button>
        <button 
          className={{`metric-button ${{activeMetric === 'matches' ? 'active' : ''}}`}}
          onClick={{() => setActiveMetric('matches')}}
        >
          Match Analysis
        </button>
        <button 
          className={{`metric-button ${{activeMetric === 'salary' ? 'active' : ''}}`}}
          onClick={{() => setActiveMetric('salary')}}
        >
          Salary Insights
        </button>
        <button 
          className={{`metric-button ${{activeMetric === 'trends' ? 'active' : ''}}`}}
          onClick={{() => setActiveMetric('trends')}}
        >
          Trends
        </button>
      </div>

      <div className="analytics-content">
        {{activeMetric === 'overview' && (
          <div className="overview-metrics">
            <div className="kpi-grid">
              <div className="kpi-card glass-card">
                <div className="kpi-icon">🎯</div>
                <div className="kpi-content">
                  <span className="kpi-number">{{analyticsData.totalJobs}}</span>
                  <span className="kpi-label">Total Jobs Found</span>
                </div>
              </div>
              
              <div className="kpi-card glass-card">
                <div className="kpi-icon">⭐</div>
                <div className="kpi-content">
                  <span className="kpi-number">{{analyticsData.highMatches}}</span>
                  <span className="kpi-label">High Matches</span>
                </div>
              </div>
              
              <div className="kpi-card glass-card">
                <div className="kpi-icon">💰</div>
                <div className="kpi-content">
                  <span className="kpi-number">${{analyticsData.averageSalary.toLocaleString()}}</span>
                  <span className="kpi-label">Average Salary</span>
                </div>
              </div>
              
              <div className="kpi-card glass-card">
                <div className="kpi-icon">📈</div>
                <div className="kpi-content">
                  <span className="kpi-number">{{analyticsData.matchRate}}%</span>
                  <span className="kpi-label">Match Rate</span>
                </div>
              </div>
            </div>
            
            <div className="quick-insights glass-card">
              <h3>Quick Insights</h3>
              <div className="insights-list">
                <div className="insight-item">
                  <span className="insight-icon">🔥</span>
                  <span>{{analyticsData.highMatches}} jobs are excellent matches (80%+ compatibility)</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">💡</span>
                  <span>Average salary is {{analyticsData.averageSalary > 120000 ? 'above' : 'at'}} market rate</span>
                </div>
                <div className="insight-item">
                  <span className="insight-icon">📊</span>
                  <span>{{Math.round((analyticsData.highMatches / analyticsData.totalJobs) * 100)}}% of jobs exceed 80% match threshold</span>
                </div>
              </div>
            </div>
          </div>
        )}}

        {{activeMetric === 'matches' && (
          <div className="match-analysis">
            <div className="match-distribution glass-card">
              <h3>Match Score Distribution</h3>
              <div className="chart-container">
                <div className="bar-chart">
                  {{chartData.map((item, index) => (
                    <div key={{index}} className="bar-item">
                      <div 
                        className="bar"
                        style={{{{ 
                          height: `${{(item.value / Math.max(...chartData.map(d => d.value))) * 200}}px`,
                          backgroundColor: item.color
                        }}}}
                      ></div>
                      <span className="bar-value">{{item.value}}</span>
                      <span className="bar-label">{{item.name}}</span>
                    </div>
                  ))}}
                </div>
              </div>
            </div>
            
            <div className="match-insights glass-card">
              <h3>Match Quality Breakdown</h3>
              <div className="quality-metrics">
                <div className="quality-item">
                  <div className="quality-bar">
                    <div 
                      className="quality-fill excellent"
                      style={{{{ width: `${{(chartData[0].value / analyticsData.totalJobs) * 100}}%` }}}}
                    ></div>
                  </div>
                  <span className="quality-label">Excellent (90%+): {{chartData[0].value}} jobs</span>
                </div>
                
                <div className="quality-item">
                  <div className="quality-bar">
                    <div 
                      className="quality-fill good"
                      style={{{{ width: `${{(chartData[1].value / analyticsData.totalJobs) * 100}}%` }}}}
                    ></div>
                  </div>
                  <span className="quality-label">Good (80-89%): {{chartData[1].value}} jobs</span>
                </div>
                
                <div className="quality-item">
                  <div className="quality-bar">
                    <div 
                      className="quality-fill fair"
                      style={{{{ width: `${{(chartData[2].value / analyticsData.totalJobs) * 100}}%` }}}}
                    ></div>
                  </div>
                  <span className="quality-label">Fair (70-79%): {{chartData[2].value}} jobs</span>
                </div>
              </div>
            </div>
          </div>
        )}}

        {{activeMetric === 'salary' && (
          <div className="salary-analysis">
            <div className="salary-distribution glass-card">
              <h3>Salary Distribution</h3>
              <div className="salary-chart">
                {{salaryDistribution.map((item, index) => (
                  <div key={{index}} className="salary-item">
                    <div className="salary-range">{{item.range}}</div>
                    <div className="salary-bar">
                      <div 
                        className="salary-fill"
                        style={{{{ width: `${{item.percentage}}%` }}}}
                      ></div>
                    </div>
                    <div className="salary-count">{{item.count}} jobs</div>
                  </div>
                ))}}
              </div>
            </div>
            
            <div className="salary-insights glass-card">
              <h3>Salary Insights</h3>
              <div className="salary-stats">
                <div className="salary-stat">
                  <span className="stat-label">Median Salary</span>
                  <span className="stat-value">${{Math.round(analyticsData.averageSalary * 0.95).toLocaleString()}}</span>
                </div>
                <div className="salary-stat">
                  <span className="stat-label">Top 10% Range</span>
                  <span className="stat-value">${{Math.round(analyticsData.averageSalary * 1.4).toLocaleString()}}+</span>
                </div>
                <div className="salary-stat">
                  <span className="stat-label">Entry Level</span>
                  <span className="stat-value">${{Math.round(analyticsData.averageSalary * 0.6).toLocaleString()}}</span>
                </div>
              </div>
            </div>
          </div>
        )}}

        {{activeMetric === 'trends' && (
          <div className="trends-analysis">
            <div className="trends-cards">
              <div className="trend-card glass-card">
                <h4>This Week</h4>
                <div className="trend-metric">
                  <span className="trend-number">{{analyticsData.trends.jobsThisWeek}}</span>
                  <span className="trend-label">New Jobs</span>
                  <span className="trend-change positive">+12%</span>
                </div>
              </div>
              
              <div className="trend-card glass-card">
                <h4>Applications</h4>
                <div className="trend-metric">
                  <span className="trend-number">{{analyticsData.trends.applicationsThisWeek}}</span>
                  <span className="trend-label">Submitted</span>
                  <span className="trend-change positive">+25%</span>
                </div>
              </div>
              
              <div className="trend-card glass-card">
                <h4>Response Rate</h4>
                <div className="trend-metric">
                  <span className="trend-number">{{analyticsData.trends.responseRate}}%</span>
                  <span className="trend-label">Responses</span>
                  <span className="trend-change negative">-2%</span>
                </div>
              </div>
            </div>
            
            <div className="forecast glass-card">
              <h3>7-Day Forecast</h3>
              <p>Based on current trends, you're likely to find 15-20 new job matches this week, with 3-4 being high-quality matches above 85%.</p>
            </div>
          </div>
        )}}
      </div>
    </div>
  );
}};

export default AnalyticsPanel;
'''
            
            css_code = '''
.analytics-panel {
  padding: 1.5rem;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.analytics-header h2 {
  color: #1f2937;
  font-size: 1.75rem;
  font-weight: 700;
}

.date-range {
  color: #6b7280;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.metrics-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 0.5rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow-x: auto;
}

.metric-button {
  padding: 0.75rem 1.25rem;
  border: none;
  background: transparent;
  color: #6b7280;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  white-space: nowrap;
}

.metric-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #1f2937;
}

.metric-button.active {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
}

.kpi-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.kpi-content {
  display: flex;
  flex-direction: column;
}

.kpi-number {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  line-height: 1;
}

.kpi-label {
  color: #6b7280;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.quick-insights {
  padding: 1.5rem;
}

.quick-insights h3 {
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #374151;
}

.insight-icon {
  font-size: 1.2rem;
}

.match-distribution, .salary-distribution {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-container {
  margin-top: 1rem;
}

.bar-chart {
  display: flex;
  align-items: end;
  gap: 1rem;
  height: 250px;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.bar {
  min-height: 20px;
  width: 40px;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
}

.bar-value {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.9rem;
}

.bar-label {
  font-size: 0.8rem;
  color: #6b7280;
  text-align: center;
}

.quality-metrics {
  margin-top: 1rem;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.quality-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.quality-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.quality-fill.excellent { background: #10b981; }
.quality-fill.good { background: #f59e0b; }
.quality-fill.fair { background: #3b82f6; }

.quality-label {
  font-size: 0.9rem;
  color: #374151;
  min-width: 150px;
}

.salary-chart {
  margin-top: 1rem;
}

.salary-item {
  display: grid;
  grid-template-columns: 80px 1fr 60px;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.salary-range {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.9rem;
}

.salary-bar {
  height: 12px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.salary-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.salary-count {
  font-size: 0.8rem;
  color: #6b7280;
  text-align: right;
}

.salary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.salary-stat {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.trends-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.trend-card {
  padding: 1.5rem;
  text-align: center;
}

.trend-card h4 {
  color: #6b7280;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.trend-metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.trend-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f2937;
}

.trend-label {
  color: #6b7280;
  font-size: 0.9rem;
}

.trend-change {
  font-size: 0.8rem;
  font-weight: 600;
}

.trend-change.positive { color: #10b981; }
.trend-change.negative { color: #ef4444; }

.forecast {
  padding: 1.5rem;
  text-align: center;
}

.forecast h3 {
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.forecast p {
  color: #6b7280;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .metrics-nav {
    overflow-x: scroll;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .bar-chart {
    overflow-x: scroll;
    justify-content: flex-start;
  }
  
  .salary-item {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 0.5rem;
  }
  
  .trends-cards {
    grid-template-columns: 1fr;
  }
}
'''
            
            return {
                'component': component_code,
                'styles': css_code,
                'type': 'react_component'
            }
        
        return {'component': '', 'styles': '', 'type': 'unsupported_framework'}
    
    async def _generate_styles(self, ui_specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate global styles for the UI components."""
        
        color_scheme = self.color_schemes.get(self.design_system, self.color_schemes['glassmorphism'])
        
        global_styles = f'''
/* Global Styles for AI Job Autopilot */
:root {{
  --primary-color: {color_scheme['primary']};
  --secondary-color: {color_scheme['secondary']};
  --accent-color: {color_scheme['accent']};
  --background-color: {color_scheme['background']};
  --surface-color: {color_scheme['surface']};
  --text-primary: {color_scheme['text_primary']};
  --text-secondary: {color_scheme['text_secondary']};
  
  --border-radius-sm: 8px;
  --border-radius-md: 12px;
  --border-radius-lg: 20px;
  --border-radius-xl: 24px;
  
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 12px 40px rgba(0, 0, 0, 0.2);
  
  --transition-fast: 0.15s ease;
  --transition-normal: 0.2s ease;
  --transition-slow: 0.3s ease;
}}

* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 
               'Ubuntu', 'Cantarell', sans-serif;
  line-height: 1.6;
  color: var(--text-primary);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}}

/* Glassmorphism Base Styles */
.glass-card {{
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-lg);
  transition: var(--transition-normal);
}}

.glass-card:hover {{
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary);
}}

h1 {{ font-size: 2.5rem; }}
h2 {{ font-size: 2rem; }}
h3 {{ font-size: 1.5rem; }}
h4 {{ font-size: 1.25rem; }}
h5 {{ font-size: 1.125rem; }}
h6 {{ font-size: 1rem; }}

/* Buttons */
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--border-radius-md);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: var(--transition-normal);
  outline: none;
  position: relative;
  overflow: hidden;
}}

.btn:focus {{
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
}}

.btn:disabled {{
  opacity: 0.6;
  cursor: not-allowed;
}}

.btn-primary {{
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
}}

.btn-primary:hover:not(:disabled) {{
  background: linear-gradient(135deg, #5856eb, #7c3aed);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}}

.btn-secondary {{
  background: rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.3);
}}

.btn-secondary:hover:not(:disabled) {{
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}}

.btn-outline {{
  background: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}}

.btn-outline:hover:not(:disabled) {{
  background: var(--primary-color);
  color: white;
}}

/* Form Elements */
input, select, textarea {{
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius-md);
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: var(--transition-normal);
}}

input:focus, select:focus, textarea:focus {{
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  background: rgba(255, 255, 255, 0.2);
}}

input::placeholder, textarea::placeholder {{
  color: rgba(255, 255, 255, 0.6);
}}

/* Animations */
@keyframes fadeIn {{
  from {{
    opacity: 0;
    transform: translateY(10px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes slideInRight {{
  from {{
    opacity: 0;
    transform: translateX(20px);
  }}
  to {{
    opacity: 1;
    transform: translateX(0);
  }}
}}

@keyframes pulse {{
  0%, 100% {{
    opacity: 1;
  }}
  50% {{
    opacity: 0.7;
  }}
}}

/* Utility Classes */
.fade-in {{
  animation: fadeIn 0.5s ease-out;
}}

.slide-in-right {{
  animation: slideInRight 0.5s ease-out;
}}

.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}

.font-bold {{ font-weight: 700; }}
.font-semibold {{ font-weight: 600; }}
.font-medium {{ font-weight: 500; }}

.text-sm {{ font-size: 0.875rem; }}
.text-base {{ font-size: 1rem; }}
.text-lg {{ font-size: 1.125rem; }}
.text-xl {{ font-size: 1.25rem; }}

.mb-1 {{ margin-bottom: 0.25rem; }}
.mb-2 {{ margin-bottom: 0.5rem; }}
.mb-3 {{ margin-bottom: 0.75rem; }}
.mb-4 {{ margin-bottom: 1rem; }}
.mb-6 {{ margin-bottom: 1.5rem; }}
.mb-8 {{ margin-bottom: 2rem; }}

.mt-1 {{ margin-top: 0.25rem; }}
.mt-2 {{ margin-top: 0.5rem; }}
.mt-3 {{ margin-top: 0.75rem; }}
.mt-4 {{ margin-top: 1rem; }}
.mt-6 {{ margin-top: 1.5rem; }}
.mt-8 {{ margin-top: 2rem; }}

.p-1 {{ padding: 0.25rem; }}
.p-2 {{ padding: 0.5rem; }}
.p-3 {{ padding: 0.75rem; }}
.p-4 {{ padding: 1rem; }}
.p-6 {{ padding: 1.5rem; }}
.p-8 {{ padding: 2rem; }}

.flex {{ display: flex; }}
.flex-col {{ flex-direction: column; }}
.flex-row {{ flex-direction: row; }}
.items-center {{ align-items: center; }}
.items-start {{ align-items: flex-start; }}
.items-end {{ align-items: flex-end; }}
.justify-center {{ justify-content: center; }}
.justify-between {{ justify-content: space-between; }}
.justify-start {{ justify-content: flex-start; }}
.justify-end {{ justify-content: flex-end; }}

.grid {{ display: grid; }}
.gap-1 {{ gap: 0.25rem; }}
.gap-2 {{ gap: 0.5rem; }}
.gap-3 {{ gap: 0.75rem; }}
.gap-4 {{ gap: 1rem; }}
.gap-6 {{ gap: 1.5rem; }}
.gap-8 {{ gap: 2rem; }}

.w-full {{ width: 100%; }}
.h-full {{ height: 100%; }}

.rounded {{ border-radius: var(--border-radius-md); }}
.rounded-lg {{ border-radius: var(--border-radius-lg); }}
.rounded-full {{ border-radius: 9999px; }}

.shadow {{ box-shadow: var(--shadow-sm); }}
.shadow-md {{ box-shadow: var(--shadow-md); }}
.shadow-lg {{ box-shadow: var(--shadow-lg); }}
.shadow-xl {{ box-shadow: var(--shadow-xl); }}

/* Responsive Design */
@media (max-width: 1024px) {{
  .container {{
    padding-left: 1rem;
    padding-right: 1rem;
  }}
}}

@media (max-width: 768px) {{
  h1 {{ font-size: 2rem; }}
  h2 {{ font-size: 1.75rem; }}
  h3 {{ font-size: 1.25rem; }}
  
  .btn {{
    padding: 0.625rem 1.25rem;
    font-size: 0.875rem;
  }}
  
  .grid-cols-auto {{
    grid-template-columns: 1fr;
  }}
}}

@media (max-width: 640px) {{
  h1 {{ font-size: 1.75rem; }}
  h2 {{ font-size: 1.5rem; }}
  h3 {{ font-size: 1.125rem; }}
  
  .p-6 {{ padding: 1rem; }}
  .p-8 {{ padding: 1.5rem; }}
  
  .gap-6 {{ gap: 1rem; }}
  .gap-8 {{ gap: 1.5rem; }}
}}

/* Accessibility */
.sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}}

/* High contrast mode support */
@media (prefers-contrast: high) {{
  .glass-card {{
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #000;
  }}
  
  .btn-primary {{
    background: #000;
    border: 2px solid #000;
  }}
  
  .btn-secondary {{
    background: #fff;
    border: 2px solid #000;
    color: #000;
  }}
}}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {{
  * {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* Focus indicators for keyboard navigation */
.focus-visible {{
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}}

/* Print styles */
@media print {{
  body {{
    background: white !important;
    color: black !important;
  }}
  
  .glass-card {{
    background: white !important;
    border: 1px solid #ccc !important;
    box-shadow: none !important;
  }}
  
  .btn {{
    border: 1px solid #000 !important;
    background: white !important;
    color: black !important;
  }}
}}
'''
        
        return {
            'global': global_styles,
            'theme': self.design_system,
            'responsive': 'mobile-first',
            'accessibility': self.accessibility_compliance
        }
    
    async def _generate_accessibility_features(self, ui_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate accessibility features for the UI components."""
        
        return {
            'compliance_level': self.accessibility_compliance,
            'features': [
                'keyboard_navigation',
                'screen_reader_support', 
                'high_contrast_mode',
                'focus_indicators',
                'semantic_html',
                'aria_labels',
                'color_contrast_compliance'
            ],
            'keyboard_shortcuts': {
                'dashboard': {
                    'tab': 'Navigate between sections',
                    'space': 'Select/activate buttons',
                    'enter': 'Confirm actions',
                    'escape': 'Close modals/dropdowns'
                },
                'job_cards': {
                    'arrow_keys': 'Navigate between job cards',
                    'space': 'Select job card',
                    'enter': 'Apply to job',
                    's': 'Save job'
                },
                'application_tracker': {
                    'f': 'Focus filter dropdown',
                    'u': 'Update status',
                    'v': 'View details'
                }
            },
            'aria_implementation': {
                'roles': ['button', 'navigation', 'main', 'complementary'],
                'properties': ['aria-label', 'aria-describedby', 'aria-expanded'],
                'live_regions': ['aria-live', 'aria-atomic']
            }
        }
    
    async def _generate_interactions(self, job_matches: List[Dict[str, Any]], ui_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interactive features for the UI components."""
        
        return {
            'animations': {
                'page_transitions': 'fade_in_out',
                'card_hovers': 'lift_shadow',
                'button_clicks': 'scale_feedback',
                'loading_states': 'skeleton_shimmer'
            },
            'user_interactions': {
                'job_application': {
                    'one_click_apply': True,
                    'bulk_operations': True,
                    'save_for_later': True,
                    'quick_view': True
                },
                'filtering_sorting': {
                    'real_time_search': True,
                    'advanced_filters': True,
                    'sort_options': ['date', 'salary', 'match_score', 'company'],
                    'saved_searches': True
                },
                'customization': {
                    'theme_switching': True,
                    'layout_preferences': True,
                    'notification_settings': True
                }
            },
            'feedback_mechanisms': {
                'success_messages': 'toast_notifications',
                'error_handling': 'inline_validation',
                'progress_indicators': 'progress_bars',
                'loading_states': 'skeleton_screens'
            },
            'responsive_behaviors': {
                'mobile_gestures': ['swipe', 'pinch_zoom', 'pull_refresh'],
                'touch_targets': 'minimum_44px',
                'mobile_navigation': 'bottom_tab_bar'
            }
        }