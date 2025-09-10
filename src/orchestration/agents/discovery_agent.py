"""
Discovery Agent for AI Job Autopilot System
Handles job discovery, matching, and ranking based on candidate profiles.
"""

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup

from .base_agent import BaseAgent, ProcessingResult

class DiscoveryAgent(BaseAgent):
    """
    Specialized agent for discovering job opportunities and matching them 
    with candidate profiles using semantic analysis and ranking algorithms.
    """
    
    def _setup_agent_specific_config(self):
        """Setup Discovery Agent specific configurations."""
        self.job_sources = self.config.custom_settings.get('job_sources', [
            'linkedin', 'indeed', 'glassdoor', 'company_portals'
        ])
        self.semantic_matching = self.config.custom_settings.get('semantic_matching', True)
        self.salary_estimation = self.config.custom_settings.get('salary_estimation', True)
        self.max_jobs_per_search = self.config.custom_settings.get('max_jobs_per_search', 100)
        
        # Initialize job matching algorithms
        self.skill_weights = {
            'technical': 0.4,
            'soft_skills': 0.2,
            'industry_experience': 0.3,
            'education': 0.1
        }
        
        # Company tier mapping for salary estimation
        self.company_tiers = {
            'tier1': ['google', 'meta', 'amazon', 'apple', 'microsoft', 'netflix', 'openai', 'anthropic'],
            'tier2': ['salesforce', 'adobe', 'nvidia', 'tesla', 'spotify', 'slack', 'stripe'],
            'tier3': ['uber', 'airbnb', 'twitter', 'linkedin', 'dropbox', 'square']
        }
        
        self.logger.info("Discovery Agent configured with semantic matching and salary estimation")
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data specific to Discovery Agent."""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input must be a dictionary")
            return {'valid': False, 'errors': errors}
        
        # Check for required fields
        required_fields = ['candidate_profile', 'search_configuration']
        for field in required_fields:
            if field not in input_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate candidate profile
        candidate_profile = input_data.get('candidate_profile', {})
        if not candidate_profile.get('skills_analysis'):
            errors.append("Candidate profile must include skills analysis")
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Any) -> ProcessingResult:
        """Internal processing for job discovery and matching."""
        
        try:
            candidate_profile = input_data['candidate_profile']
            search_config = input_data['search_configuration']
            user_preferences = input_data.get('user_preferences', {})
            
            # Extract key candidate information
            candidate_info = await self._extract_candidate_info(candidate_profile)
            
            # Perform job search across multiple sources
            raw_jobs = await self._search_jobs(candidate_info, search_config)
            
            # Process and enrich job data
            enriched_jobs = await self._enrich_job_data(raw_jobs, candidate_info)
            
            # Perform semantic matching and ranking
            ranked_jobs = await self._rank_jobs(enriched_jobs, candidate_info, user_preferences)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(ranked_jobs, candidate_info)
            
            return ProcessingResult(
                success=True,
                result={
                    'candidate_profile': candidate_profile,
                    'ranked_jobs': ranked_jobs,
                    'total_jobs_found': len(ranked_jobs),
                    'top_matches': ranked_jobs[:10],
                    'search_insights': insights,
                    'match_statistics': self._calculate_match_statistics(ranked_jobs)
                },
                confidence=0.9,
                processing_time=0.0,
                metadata={
                    'jobs_processed': len(raw_jobs),
                    'sources_used': list(search_config.get('job_sources', self.job_sources)),
                    'semantic_matching_enabled': self.semantic_matching
                }
            )
            
        except Exception as e:
            self.logger.error(f"Discovery processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                result=None,
                confidence=0.0,
                processing_time=0.0,
                metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def _extract_candidate_info(self, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure candidate information for job matching."""
        
        skills_analysis = candidate_profile.get('skills_analysis', {})
        work_experience = candidate_profile.get('work_experience', [])
        education = candidate_profile.get('education', [])
        
        # Extract technical skills
        technical_skills = skills_analysis.get('technical_skills', [])
        if isinstance(technical_skills, list):
            tech_skills_list = [skill.get('skill', skill) if isinstance(skill, dict) else skill 
                              for skill in technical_skills]
        else:
            tech_skills_list = []
        
        # Calculate experience level
        experience_years = self._calculate_total_experience(work_experience)
        
        # Extract education level
        education_level = self._determine_education_level(education)
        
        # Extract industry experience
        industries = self._extract_industries(work_experience)
        
        return {
            'technical_skills': tech_skills_list,
            'soft_skills': skills_analysis.get('soft_skills', []),
            'experience_years': experience_years,
            'education_level': education_level,
            'industries': industries,
            'current_title': work_experience[0].get('title', '') if work_experience else '',
            'location': candidate_profile.get('personal_information', {}).get('location', ''),
            'preferred_roles': candidate_profile.get('preferred_roles', [])
        }
    
    def _calculate_total_experience(self, work_experience: List[Dict[str, Any]]) -> float:
        """Calculate total years of experience."""
        total_years = 0.0
        
        for job in work_experience:
            duration = job.get('duration', '')
            years = self._parse_duration_to_years(duration)
            total_years += years
        
        return min(total_years, 20.0)  # Cap at 20 years
    
    def _parse_duration_to_years(self, duration: str) -> float:
        """Parse duration string to years."""
        if not duration:
            return 0.0
        
        # Handle various duration formats
        duration_lower = duration.lower()
        
        # Extract years
        year_match = re.search(r'(\d+(?:\.\d+)?)\s*year', duration_lower)
        years = float(year_match.group(1)) if year_match else 0.0
        
        # Extract months and convert to years
        month_match = re.search(r'(\d+(?:\.\d+)?)\s*month', duration_lower)
        months = float(month_match.group(1)) if month_match else 0.0
        years += months / 12.0
        
        return years
    
    def _determine_education_level(self, education: List[Dict[str, Any]]) -> str:
        """Determine the highest education level."""
        if not education:
            return 'none'
        
        education_hierarchy = {
            'phd': 5, 'doctorate': 5, 'ph.d': 5,
            'master': 4, 'masters': 4, 'mba': 4, 'ms': 4, 'ma': 4,
            'bachelor': 3, 'bachelors': 3, 'bs': 3, 'ba': 3, 'be': 3, 'btech': 3,
            'associate': 2, 'diploma': 2,
            'high school': 1, 'secondary': 1
        }
        
        max_level = 0
        for edu in education:
            degree = edu.get('degree', '').lower()
            for keyword, level in education_hierarchy.items():
                if keyword in degree:
                    max_level = max(max_level, level)
                    break
        
        level_names = {5: 'doctorate', 4: 'masters', 3: 'bachelors', 2: 'associate', 1: 'high_school', 0: 'none'}
        return level_names.get(max_level, 'none')
    
    def _extract_industries(self, work_experience: List[Dict[str, Any]]) -> List[str]:
        """Extract industries from work experience."""
        industries = set()
        
        for job in work_experience:
            company = job.get('company', '').lower()
            description = job.get('description', '').lower()
            
            # Industry keywords mapping
            industry_keywords = {
                'technology': ['tech', 'software', 'ai', 'ml', 'data', 'cloud', 'saas'],
                'finance': ['bank', 'finance', 'fintech', 'trading', 'investment'],
                'healthcare': ['health', 'medical', 'pharma', 'biotech', 'hospital'],
                'e-commerce': ['ecommerce', 'retail', 'marketplace', 'shopping'],
                'consulting': ['consulting', 'advisory', 'strategy'],
                'education': ['education', 'learning', 'university', 'school']
            }
            
            for industry, keywords in industry_keywords.items():
                if any(keyword in company or keyword in description for keyword in keywords):
                    industries.add(industry)
        
        return list(industries) if industries else ['general']
    
    async def _search_jobs(self, candidate_info: Dict[str, Any], search_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for jobs across multiple sources."""
        
        all_jobs = []
        target_companies = search_config.get('target_companies', [])
        max_results = search_config.get('max_results', self.max_jobs_per_search)
        
        # Mock job data for demonstration (in real implementation, would call actual APIs)
        mock_jobs = await self._generate_mock_jobs(candidate_info, target_companies, max_results)
        all_jobs.extend(mock_jobs)
        
        return all_jobs[:max_results]
    
    async def _generate_mock_jobs(self, candidate_info: Dict[str, Any], target_companies: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Generate realistic mock job data for demonstration."""
        
        job_titles = [
            'Senior Software Engineer', 'Staff Software Engineer', 'Principal Engineer',
            'Lead Developer', 'Senior Full Stack Developer', 'Backend Engineer',
            'Frontend Engineer', 'DevOps Engineer', 'Site Reliability Engineer',
            'Data Scientist', 'Machine Learning Engineer', 'AI Research Scientist',
            'Product Manager', 'Technical Lead', 'Engineering Manager'
        ]
        
        locations = [
            'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX',
            'Boston, MA', 'Remote', 'Los Angeles, CA', 'Chicago, IL'
        ]
        
        all_companies = target_companies + [
            'TechCorp', 'InnovateTech', 'DataDynamics', 'CloudFirst', 'AIVentures',
            'StartupXYZ', 'ScaleUp Inc', 'NextGen Systems', 'FutureTech'
        ]
        
        jobs = []
        for i in range(min(max_results, 50)):  # Generate up to 50 jobs
            company = all_companies[i % len(all_companies)]
            title = job_titles[i % len(job_titles)]
            location = locations[i % len(locations)]
            
            # Determine company tier for salary estimation
            tier = 'tier3'  # default
            for tier_name, companies in self.company_tiers.items():
                if company.lower() in companies:
                    tier = tier_name
                    break
            
            # Generate salary based on experience and company tier
            base_salary = self._estimate_salary(candidate_info['experience_years'], tier, title)
            
            job = {
                'job_id': f"job_{i+1}",
                'title': title,
                'company': company,
                'location': location,
                'description': f"Exciting opportunity for {title} at {company}. We're looking for someone with experience in {', '.join(candidate_info['technical_skills'][:3])}.",
                'requirements': {
                    'required_skills': candidate_info['technical_skills'][:5],
                    'experience_years': max(0, candidate_info['experience_years'] - 2),
                    'education': 'bachelors'
                },
                'compensation_analysis': {
                    'base_salary_min': int(base_salary * 0.9),
                    'base_salary_max': int(base_salary * 1.1),
                    'equity': tier in ['tier1', 'tier2'],
                    'benefits': ['health', 'dental', '401k', 'pto']
                },
                'company_info': {
                    'size': 'large' if tier in ['tier1', 'tier2'] else 'medium',
                    'industry': candidate_info['industries'][0] if candidate_info['industries'] else 'technology',
                    'tier': tier
                },
                'location_details': {
                    'work_arrangement': 'remote' if 'remote' in location.lower() else 'hybrid',
                    'timezone': 'PST' if 'CA' in location else 'EST'
                },
                'posted_date': (datetime.now() - timedelta(days=i % 30)).isoformat(),
                'application_url': f"https://careers.{company.lower().replace(' ', '')}.com/jobs/{i+1}"
            }
            
            jobs.append(job)
        
        return jobs
    
    def _estimate_salary(self, experience_years: float, tier: str, title: str) -> int:
        """Estimate salary based on experience, company tier, and title."""
        
        # Base salary ranges by experience
        base_salaries = {
            'junior': 80000,  # 0-2 years
            'mid': 120000,    # 3-5 years
            'senior': 160000, # 6-10 years
            'staff': 220000,  # 11+ years
        }
        
        # Determine experience level
        if experience_years <= 2:
            exp_level = 'junior'
        elif experience_years <= 5:
            exp_level = 'mid'
        elif experience_years <= 10:
            exp_level = 'senior'
        else:
            exp_level = 'staff'
        
        base_salary = base_salaries[exp_level]
        
        # Apply company tier multipliers
        tier_multipliers = {
            'tier1': 1.4,
            'tier2': 1.2,
            'tier3': 1.0
        }
        
        # Apply title multipliers
        title_multipliers = {
            'principal': 1.3,
            'staff': 1.2,
            'senior': 1.1,
            'lead': 1.15,
            'manager': 1.25
        }
        
        title_lower = title.lower()
        title_multiplier = 1.0
        for keyword, multiplier in title_multipliers.items():
            if keyword in title_lower:
                title_multiplier = multiplier
                break
        
        final_salary = int(base_salary * tier_multipliers.get(tier, 1.0) * title_multiplier)
        
        return final_salary
    
    async def _enrich_job_data(self, jobs: List[Dict[str, Any]], candidate_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich job data with additional analysis."""
        
        enriched_jobs = []
        
        for job in jobs:
            enriched_job = job.copy()
            
            # Add skill matching analysis
            skill_match = self._calculate_skill_match(job, candidate_info)
            enriched_job['skill_match_analysis'] = skill_match
            
            # Add location compatibility
            location_score = self._calculate_location_compatibility(job, candidate_info)
            enriched_job['location_compatibility'] = location_score
            
            # Add career progression analysis
            career_fit = self._analyze_career_fit(job, candidate_info)
            enriched_job['career_progression'] = career_fit
            
            enriched_jobs.append(enriched_job)
        
        return enriched_jobs
    
    def _calculate_skill_match(self, job: Dict[str, Any], candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate skill matching score between job and candidate."""
        
        job_skills = set(skill.lower() for skill in job.get('requirements', {}).get('required_skills', []))
        candidate_skills = set(skill.lower() for skill in candidate_info.get('technical_skills', []))
        
        if not job_skills:
            return {'match_percentage': 50, 'matched_skills': [], 'missing_skills': []}
        
        matched_skills = job_skills.intersection(candidate_skills)
        missing_skills = job_skills.difference(candidate_skills)
        
        match_percentage = (len(matched_skills) / len(job_skills)) * 100
        
        return {
            'match_percentage': round(match_percentage, 1),
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'skill_overlap_count': len(matched_skills)
        }
    
    def _calculate_location_compatibility(self, job: Dict[str, Any], candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate location compatibility score."""
        
        job_location = job.get('location', '').lower()
        candidate_location = candidate_info.get('location', '').lower()
        
        # High compatibility for remote jobs
        if 'remote' in job_location:
            return {'score': 100, 'reason': 'Remote position'}
        
        # Check if locations match
        if candidate_location and candidate_location in job_location:
            return {'score': 100, 'reason': 'Same location'}
        
        # Default moderate compatibility
        return {'score': 70, 'reason': 'Relocation may be required'}
    
    def _analyze_career_fit(self, job: Dict[str, Any], candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze career progression fit."""
        
        job_title = job.get('title', '').lower()
        current_title = candidate_info.get('current_title', '').lower()
        experience_years = candidate_info.get('experience_years', 0)
        
        # Determine if this is a career progression
        progression_keywords = ['senior', 'lead', 'principal', 'staff', 'manager']
        
        current_seniority = 0
        job_seniority = 0
        
        for i, keyword in enumerate(progression_keywords):
            if keyword in current_title:
                current_seniority = i + 1
            if keyword in job_title:
                job_seniority = i + 1
        
        if job_seniority > current_seniority:
            progression_type = 'promotion'
        elif job_seniority == current_seniority:
            progression_type = 'lateral'
        else:
            progression_type = 'step_back'
        
        # Calculate experience fit
        required_experience = job.get('requirements', {}).get('experience_years', 0)
        experience_fit = min(100, (experience_years / max(required_experience, 1)) * 100)
        
        return {
            'progression_type': progression_type,
            'experience_fit_percentage': round(experience_fit, 1),
            'seniority_match': job_seniority == current_seniority,
            'growth_potential': job_seniority > current_seniority
        }
    
    async def _rank_jobs(self, jobs: List[Dict[str, Any]], candidate_info: Dict[str, Any], user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank jobs based on multiple criteria."""
        
        for job in jobs:
            score = await self._calculate_overall_score(job, candidate_info, user_preferences)
            job['match_percentage'] = score
            job['ranking_factors'] = self._explain_ranking(job, candidate_info)
        
        # Sort by match percentage (descending)
        ranked_jobs = sorted(jobs, key=lambda x: x.get('match_percentage', 0), reverse=True)
        
        return ranked_jobs
    
    async def _calculate_overall_score(self, job: Dict[str, Any], candidate_info: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """Calculate overall job match score."""
        
        # Get component scores
        skill_score = job.get('skill_match_analysis', {}).get('match_percentage', 50) / 100
        location_score = job.get('location_compatibility', {}).get('score', 70) / 100
        career_score = job.get('career_progression', {}).get('experience_fit_percentage', 70) / 100
        
        # Apply weights
        overall_score = (
            skill_score * self.skill_weights['technical'] * 100 +
            location_score * 0.2 * 100 +
            career_score * self.skill_weights['industry_experience'] * 100 +
            0.3 * 100  # Base score for other factors
        )
        
        # Apply user preferences
        if user_preferences:
            preference_bonus = self._calculate_preference_bonus(job, user_preferences)
            overall_score += preference_bonus
        
        return min(100, max(0, overall_score))
    
    def _calculate_preference_bonus(self, job: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """Calculate bonus score based on user preferences."""
        
        bonus = 0.0
        
        # Salary preferences
        min_salary = user_preferences.get('minimum_salary', 0)
        job_salary = job.get('compensation_analysis', {}).get('base_salary_min', 0)
        
        if job_salary >= min_salary:
            bonus += 5.0
        
        # Remote work preference
        if user_preferences.get('remote_only', False):
            work_arrangement = job.get('location_details', {}).get('work_arrangement', '')
            if work_arrangement == 'remote':
                bonus += 10.0
        
        # Company tier preference
        preferred_companies = user_preferences.get('preferred_companies', [])
        if job.get('company', '').lower() in [c.lower() for c in preferred_companies]:
            bonus += 8.0
        
        return bonus
    
    def _explain_ranking(self, job: Dict[str, Any], candidate_info: Dict[str, Any]) -> Dict[str, str]:
        """Explain why a job was ranked as it was."""
        
        factors = {}
        
        skill_match = job.get('skill_match_analysis', {}).get('match_percentage', 50)
        factors['skill_match'] = f"{skill_match}% skill match"
        
        location_score = job.get('location_compatibility', {}).get('score', 70)
        factors['location'] = job.get('location_compatibility', {}).get('reason', 'Standard location fit')
        
        career_fit = job.get('career_progression', {}).get('progression_type', 'lateral')
        factors['career_progression'] = f"Career progression: {career_fit}"
        
        return factors
    
    async def _generate_insights(self, ranked_jobs: List[Dict[str, Any]], candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from the job search results."""
        
        if not ranked_jobs:
            return {'message': 'No jobs found matching the criteria'}
        
        # Calculate statistics
        avg_salary = sum(
            job.get('compensation_analysis', {}).get('base_salary_min', 0)
            for job in ranked_jobs
        ) / len(ranked_jobs)
        
        # Top companies
        company_counts = {}
        for job in ranked_jobs:
            company = job.get('company', 'Unknown')
            company_counts[company] = company_counts.get(company, 0) + 1
        
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Most common skills
        all_skills = []
        for job in ranked_jobs:
            all_skills.extend(job.get('requirements', {}).get('required_skills', []))
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # High match jobs
        high_match_jobs = [job for job in ranked_jobs if job.get('match_percentage', 0) > 80]
        
        return {
            'total_jobs_analyzed': len(ranked_jobs),
            'high_match_jobs': len(high_match_jobs),
            'average_salary': int(avg_salary),
            'salary_range': {
                'min': min(job.get('compensation_analysis', {}).get('base_salary_min', 0) for job in ranked_jobs),
                'max': max(job.get('compensation_analysis', {}).get('base_salary_max', 0) for job in ranked_jobs)
            },
            'top_companies': [{'company': company, 'job_count': count} for company, count in top_companies],
            'most_requested_skills': [{'skill': skill, 'frequency': count} for skill, count in top_skills],
            'location_breakdown': self._analyze_locations(ranked_jobs),
            'recommendations': self._generate_search_recommendations(ranked_jobs, candidate_info)
        }
    
    def _analyze_locations(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze job locations."""
        
        location_counts = {}
        for job in jobs:
            location = job.get('location', 'Unknown')
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return location_counts
    
    def _generate_search_recommendations(self, jobs: List[Dict[str, Any]], candidate_info: Dict[str, Any]) -> List[str]:
        """Generate search recommendations based on results."""
        
        recommendations = []
        
        if len(jobs) < 10:
            recommendations.append("Consider broadening your search criteria to find more opportunities")
        
        # Skill gap analysis
        all_missing_skills = []
        for job in jobs[:20]:  # Top 20 jobs
            missing_skills = job.get('skill_match_analysis', {}).get('missing_skills', [])
            all_missing_skills.extend(missing_skills)
        
        if all_missing_skills:
            skill_frequency = {}
            for skill in all_missing_skills:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            
            most_missing = max(skill_frequency.items(), key=lambda x: x[1])
            recommendations.append(f"Consider learning {most_missing[0]} - it's required by {most_missing[1]} jobs")
        
        # Remote work opportunities
        remote_jobs = [job for job in jobs if 'remote' in job.get('location', '').lower()]
        if len(remote_jobs) > len(jobs) * 0.3:
            recommendations.append("Many remote opportunities available - consider applying to remote positions")
        
        return recommendations
    
    def _calculate_match_statistics(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate match statistics for the job results."""
        
        if not jobs:
            return {}
        
        match_scores = [job.get('match_percentage', 0) for job in jobs]
        
        return {
            'average_match': sum(match_scores) / len(match_scores),
            'highest_match': max(match_scores),
            'jobs_above_80': len([score for score in match_scores if score > 80]),
            'jobs_above_90': len([score for score in match_scores if score > 90]),
            'distribution': {
                'excellent': len([score for score in match_scores if score >= 90]),
                'good': len([score for score in match_scores if 80 <= score < 90]),
                'fair': len([score for score in match_scores if 60 <= score < 80]),
                'poor': len([score for score in match_scores if score < 60])
            }
        }