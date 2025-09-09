#!/usr/bin/env python3
"""
Job Discovery Engine - Simulates intelligent job discovery and matching
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class JobDiscoveryEngine:
    def __init__(self):
        self.job_templates = {
            'cybersecurity': [
                {
                    'title_templates': ['Security Engineer', 'Cybersecurity Analyst', 'Penetration Tester', 'Security Consultant'],
                    'companies': ['CyberSecure Inc', 'InfoGuard Technologies', 'SecureNet Solutions', 'CyberDefense Corp'],
                    'requirements': ['penetration testing', 'vulnerability assessment', 'security frameworks', 'compliance'],
                    'salary_ranges': [(120, 160), (140, 180), (100, 140), (130, 170)]
                }
            ],
            'software_development': [
                {
                    'title_templates': ['Software Engineer', 'Full Stack Developer', 'Backend Engineer', 'Frontend Engineer'],
                    'companies': ['TechFlow Inc', 'DevCorp Solutions', 'CodeCraft Technologies', 'BuildSoft Systems'],
                    'requirements': ['programming', 'software development', 'api development', 'cloud technologies'],
                    'salary_ranges': [(110, 150), (120, 160), (95, 135), (105, 145)]
                }
            ],
            'healthcare_tech': [
                {
                    'title_templates': ['Healthcare Software Engineer', 'Medical Technology Specialist', 'Health Data Analyst'],
                    'companies': ['MedTech Solutions', 'HealthCare Innovations', 'Digital Health Corp', 'MedSecure Technologies'],
                    'requirements': ['healthcare compliance', 'medical software', 'patient data security', 'HIPAA'],
                    'salary_ranges': [(130, 170), (125, 165), (115, 155), (135, 175)]
                }
            ]
        }
        
        self.locations = [
            'Remote, USA', 'San Francisco, CA', 'New York, NY', 'Austin, TX', 
            'Seattle, WA', 'Boston, MA', 'Remote, Worldwide', 'Denver, CO'
        ]
        
        self.application_types = ['Easy Apply', 'Company Portal', 'External Application', 'Direct Application']
    
    def match_jobs_to_profile(self, user_profile: Dict[str, Any], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match jobs based on user profile and preferences"""
        matched_jobs = []
        
        # Get user skills and industries
        skills = user_profile.get('skills', {})
        industries = user_profile.get('industries', [])
        seniority = user_profile.get('seniority', {}).get('level', 'Mid-Level')
        
        # Determine job categories based on user profile
        job_categories = self.determine_job_categories(skills, industries)
        
        # Generate jobs for each category
        for category in job_categories:
            jobs = self.generate_jobs_for_category(category, preferences, seniority)
            matched_jobs.extend(jobs)
        
        # Sort by match score and return top matches
        matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_jobs[:10]  # Return top 10 matches
    
    def determine_job_categories(self, skills: Dict[str, List[str]], industries: List[str]) -> List[str]:
        """Determine which job categories to search based on skills and industries"""
        categories = []
        
        # Map industries to job categories
        if any(ind.lower() in ['cybersecurity', 'security'] for ind in industries):
            categories.append('cybersecurity')
        
        if any(ind.lower() in ['healthcare', 'medical'] for ind in industries):
            categories.append('healthcare_tech')
        
        # Check skills for software development
        if skills.get('programming_languages') or skills.get('frameworks'):
            categories.append('software_development')
        
        # Default to cybersecurity if user has security skills
        if skills.get('cybersecurity') and 'cybersecurity' not in categories:
            categories.append('cybersecurity')
        
        # Ensure at least one category
        if not categories:
            categories = ['software_development']
        
        return categories
    
    def generate_jobs_for_category(self, category: str, preferences: Dict[str, Any], seniority: str) -> List[Dict[str, Any]]:
        """Generate job listings for a specific category"""
        jobs = []
        templates = self.job_templates.get(category, self.job_templates['software_development'])
        
        for template in templates:
            # Generate 2-3 jobs per template
            for i in range(random.randint(2, 4)):
                job = self.create_job_from_template(template, preferences, seniority, category)
                jobs.append(job)
        
        return jobs
    
    def create_job_from_template(self, template: Dict, preferences: Dict, seniority: str, category: str) -> Dict[str, Any]:
        """Create a job posting from template"""
        # Select random elements from template
        title_base = random.choice(template['title_templates'])
        company = random.choice(template['companies'])
        requirements = template['requirements']
        salary_range = random.choice(template['salary_ranges'])
        
        # Adjust title based on seniority
        if seniority == 'Senior':
            title = f"Senior {title_base}" if not title_base.startswith('Senior') else title_base
        elif seniority == 'Leadership':
            title = f"Lead {title_base}" if not title_base.startswith('Lead') else title_base
        else:
            title = title_base
        
        # Filter location based on preferences
        preferred_location = preferences.get('preferred_location', 'Remote, USA')
        if 'remote' in preferred_location.lower():
            location = random.choice(['Remote, USA', 'Remote, Worldwide', preferred_location])
        else:
            location = preferred_location
        
        # Adjust salary based on preferences
        min_salary = preferences.get('min_salary_k', 100) * 1000
        adjusted_salary = (max(salary_range[0] * 1000, min_salary), salary_range[1] * 1000)
        
        # Calculate match score
        match_score = self.calculate_match_score(requirements, preferences, seniority)
        
        # Generate job URL
        company_slug = company.lower().replace(' ', '').replace(',', '')
        job_url = f"https://{company_slug}.com/careers/{title.lower().replace(' ', '-')}-{random.randint(1000, 9999)}"
        
        # Determine application type
        app_type = random.choice(self.application_types)
        if 'linkedin' in job_url or random.random() > 0.6:
            app_type = 'Easy Apply'
        
        return {
            'job_id': f"{category}_{random.randint(1000, 9999)}",
            'title': title,
            'company': company,
            'location': location,
            'salary_range': f"${adjusted_salary[0]//1000}k - ${adjusted_salary[1]//1000}k",
            'match_score': match_score,
            'application_type': app_type,
            'url': job_url,
            'posted_date': (datetime.now() - timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d'),
            'job_description': self.generate_job_description(title, company, requirements),
            'requirements_matched': random.randint(6, 10),
            'requirements_total': 10,
            'company_size': random.choice(['10-50', '50-200', '200-1000', '1000-5000', '5000+']),
            'industry': category.replace('_', ' ').title()
        }
    
    def calculate_match_score(self, requirements: List[str], preferences: Dict, seniority: str) -> int:
        """Calculate job match score based on various factors"""
        base_score = 75
        
        # Salary match bonus
        min_salary = preferences.get('min_salary_k', 100)
        if min_salary <= 120:
            base_score += 10
        elif min_salary <= 140:
            base_score += 5
        
        # Location preference bonus
        preferred_location = preferences.get('preferred_location', '').lower()
        if 'remote' in preferred_location:
            base_score += 8
        
        # Seniority alignment
        if seniority == 'Senior':
            base_score += 5
        
        # Add some randomness for realistic variation
        variation = random.randint(-5, 10)
        final_score = min(100, max(60, base_score + variation))
        
        return final_score
    
    def generate_job_description(self, title: str, company: str, requirements: List[str]) -> str:
        """Generate realistic job description"""
        description = f"Join {company} as a {title} and make a significant impact on our growing team. "
        description += f"We are looking for a talented professional with expertise in {', '.join(requirements[:3])}. "
        description += "\n\nKey Responsibilities:\n"
        description += f"• Lead initiatives in {requirements[0] if requirements else 'technology'}\n"
        description += f"• Collaborate with cross-functional teams on {requirements[1] if len(requirements) > 1 else 'projects'}\n"
        description += f"• Implement best practices for {requirements[2] if len(requirements) > 2 else 'development'}\n"
        description += "\n\nRequirements:\n"
        description += "• 3+ years of relevant experience\n"
        description += f"• Strong background in {', '.join(requirements)}\n"
        description += "• Excellent communication and collaboration skills\n"
        
        return description
    
    def simulate_job_discovery(self, user_profile: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to simulate complete job discovery process"""
        
        # Simulate search parameters
        search_params = {
            'keywords': self.extract_search_keywords(user_profile),
            'location': preferences.get('preferred_location', 'Remote, USA'),
            'salary_min': preferences.get('min_salary_k', 100) * 1000,
            'job_type': preferences.get('job_type', 'Full-time'),
            'experience_level': user_profile.get('seniority', {}).get('level', 'Mid-Level')
        }
        
        # Generate matched jobs
        matched_jobs = self.match_jobs_to_profile(user_profile, preferences)
        
        # Simulate platform statistics
        platform_stats = {
            'linkedin': {
                'total_found': random.randint(200, 400),
                'easy_apply_available': random.randint(100, 200),
                'search_time': round(random.uniform(2.0, 4.0), 1)
            },
            'indeed': {
                'total_found': random.randint(150, 300),
                'direct_apply_available': random.randint(80, 150),
                'search_time': round(random.uniform(1.5, 3.5), 1)
            },
            'company_portals': {
                'total_found': random.randint(50, 150),
                'direct_applications': random.randint(50, 150),
                'search_time': round(random.uniform(5.0, 15.0), 1)
            }
        }
        
        return {
            'discovery_status': 'success',
            'search_parameters': search_params,
            'total_jobs_found': sum(stats['total_found'] for stats in platform_stats.values()),
            'matched_jobs': matched_jobs,
            'platform_statistics': platform_stats,
            'search_performance': {
                'total_search_time': sum(stats['search_time'] for stats in platform_stats.values()),
                'platforms_searched': len(platform_stats),
                'average_match_score': sum(job['match_score'] for job in matched_jobs) / len(matched_jobs) if matched_jobs else 0
            },
            'discovered_at': datetime.now().isoformat()
        }
    
    def extract_search_keywords(self, user_profile: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords for job search"""
        keywords = []
        
        # Add skills as keywords
        skills = user_profile.get('skills', {})
        for category, skill_list in skills.items():
            keywords.extend(skill_list[:2])  # Top 2 from each category
        
        # Add industries
        industries = user_profile.get('industries', [])
        keywords.extend(industries)
        
        # Add seniority level
        seniority = user_profile.get('seniority', {}).get('level', '')
        if seniority:
            keywords.append(seniority)
        
        return keywords[:10]  # Return top 10 keywords

# Global instance for use in Streamlit
job_discovery_engine = JobDiscoveryEngine()