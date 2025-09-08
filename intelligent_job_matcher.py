#!/usr/bin/env python3
"""
Intelligent Job Matching Algorithm
AI-powered system to match candidate profiles with job requirements
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import re
import os

# ML and AI imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import torch
from transformers import pipeline, AutoTokenizer, AutoModel
import openai
from sentence_transformers import SentenceTransformer

# Import our custom classes
from advanced_resume_parser import ParsedResume, ResumeParser

@dataclass
class JobRequirement:
    id: str
    title: str
    company: str
    location: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str  # junior, mid, senior, lead
    education_required: str
    salary_range: Optional[Tuple[int, int]]
    job_type: str  # full-time, part-time, contract
    remote_friendly: bool
    industry: str
    company_size: str
    benefits: List[str]
    application_url: str
    source_platform: str
    posted_date: str

@dataclass
class MatchResult:
    job_id: str
    overall_score: float
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    location_match_score: float
    culture_fit_score: float
    salary_compatibility: float
    detailed_analysis: Dict[str, Any]
    recommendation: str
    missing_skills: List[str]
    matching_skills: List[str]
    confidence_level: str

class AIJobMatcher:
    """Advanced AI-powered job matching system"""
    
    def __init__(self):
        # Initialize AI models
        self.sentence_model = None
        self.skill_classifier = None
        self.openai_client = None
        
        # Initialize models
        self._initialize_models()
        
        # Skill importance weights
        self.skill_weights = {
            'cybersecurity': {'penetration testing': 0.9, 'vulnerability assessment': 0.85, 'incident response': 0.8},
            'programming_languages': {'python': 0.8, 'java': 0.7, 'javascript': 0.7},
            'cloud_platforms': {'aws': 0.9, 'azure': 0.85, 'gcp': 0.8},
            'data_science': {'machine learning': 0.9, 'deep learning': 0.85, 'statistics': 0.7}
        }
        
        # Experience level mappings
        self.experience_levels = {
            'junior': {'years': (0, 2), 'weight': 0.3},
            'mid': {'years': (2, 5), 'weight': 0.5},
            'senior': {'years': (5, 10), 'weight': 0.8},
            'lead': {'years': (8, 15), 'weight': 1.0}
        }
        
        # Location scoring factors
        self.location_factors = {
            'remote': 1.0,
            'hybrid': 0.8,
            'onsite_preferred': 0.6,
            'onsite_same_city': 0.9,
            'onsite_different_city': 0.4,
            'onsite_different_country': 0.2
        }
        
    def _initialize_models(self):
        """Initialize AI models for matching"""
        try:
            # Load sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Sentence transformer model loaded")
            
            # Initialize skill classification pipeline
            self.skill_classifier = pipeline(
                'zero-shot-classification',
                model='facebook/bart-large-mnli',
                device=0 if torch.cuda.is_available() else -1
            )
            print("✅ Skill classification model loaded")
            
            # Initialize OpenAI client if API key is available
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                openai.api_key = openai_api_key
                self.openai_client = openai
                print("✅ OpenAI client initialized")
            else:
                print("⚠️  OpenAI API key not found, some features may be limited")
                
        except Exception as e:
            print(f"⚠️  Error initializing models: {e}")
    
    def calculate_comprehensive_match(
        self, 
        resume: ParsedResume, 
        job: JobRequirement,
        user_preferences: Dict = None
    ) -> MatchResult:
        """Calculate comprehensive match score between resume and job"""
        
        # Default user preferences
        if not user_preferences:
            user_preferences = {
                'preferred_locations': ['Remote', 'Berlin', 'Munich'],
                'min_salary': 70000,
                'job_types': ['full-time'],
                'industries': ['Technology', 'Financial Services'],
                'company_sizes': ['Startup', 'Medium', 'Large']
            }
        
        print(f"🎯 Analyzing match for: {job.title} @ {job.company}")
        
        # Calculate individual match scores
        skill_score = self._calculate_skill_match(resume, job)
        experience_score = self._calculate_experience_match(resume, job)
        education_score = self._calculate_education_match(resume, job)
        location_score = self._calculate_location_match(resume, job, user_preferences)
        culture_score = self._calculate_culture_fit(resume, job)
        salary_score = self._calculate_salary_compatibility(resume, job, user_preferences)
        
        # Calculate weighted overall score
        weights = {
            'skills': 0.35,
            'experience': 0.25,
            'education': 0.10,
            'location': 0.15,
            'culture': 0.10,
            'salary': 0.05
        }
        
        overall_score = (
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            location_score * weights['location'] +
            culture_score * weights['culture'] +
            salary_score * weights['salary']
        )
        
        # Detailed analysis
        detailed_analysis = self._generate_detailed_analysis(resume, job, {
            'skill_score': skill_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'location_score': location_score,
            'culture_score': culture_score,
            'salary_score': salary_score
        })
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score, detailed_analysis)
        
        # Find matching and missing skills
        matching_skills = self._find_matching_skills(resume, job)
        missing_skills = self._find_missing_skills(resume, job)
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(overall_score, detailed_analysis)
        
        return MatchResult(
            job_id=job.id,
            overall_score=overall_score,
            skill_match_score=skill_score,
            experience_match_score=experience_score,
            education_match_score=education_score,
            location_match_score=location_score,
            culture_fit_score=culture_score,
            salary_compatibility=salary_score,
            detailed_analysis=detailed_analysis,
            recommendation=recommendation,
            missing_skills=missing_skills,
            matching_skills=matching_skills,
            confidence_level=confidence_level
        )
    
    def _calculate_skill_match(self, resume: ParsedResume, job: JobRequirement) -> float:
        """Calculate skill matching score using semantic similarity"""
        try:
            # Get all candidate skills
            candidate_skills = []
            for skill_category in resume.skills.values():
                candidate_skills.extend(skill_category)
            
            # Combine required and preferred job skills
            job_skills = job.required_skills + job.preferred_skills
            
            if not candidate_skills or not job_skills:
                return 0.0
            
            # Use sentence transformer for semantic similarity
            if self.sentence_model:
                # Create embeddings
                candidate_embeddings = self.sentence_model.encode(candidate_skills)
                job_embeddings = self.sentence_model.encode(job_skills)
                
                # Calculate similarity matrix
                similarity_matrix = cosine_similarity(candidate_embeddings, job_embeddings)
                
                # Calculate match score
                # For each required skill, find best matching candidate skill
                required_matches = []
                for i, job_skill in enumerate(job.required_skills):
                    if i < len(job_embeddings):
                        best_match = np.max(similarity_matrix[:, i])
                        required_matches.append(best_match)
                
                # Required skills have higher weight
                required_score = np.mean(required_matches) if required_matches else 0.0
                
                # Preferred skills
                preferred_matches = []
                for i, job_skill in enumerate(job.preferred_skills):
                    job_idx = i + len(job.required_skills)
                    if job_idx < len(job_embeddings):
                        best_match = np.max(similarity_matrix[:, job_idx])
                        preferred_matches.append(best_match)
                
                preferred_score = np.mean(preferred_matches) if preferred_matches else 0.0
                
                # Weighted combination (required skills more important)
                final_score = (required_score * 0.8 + preferred_score * 0.2)
                
                return min(final_score, 1.0)
            
            # Fallback to keyword matching
            return self._keyword_skill_match(candidate_skills, job_skills)
            
        except Exception as e:
            print(f"Error calculating skill match: {e}")
            return self._keyword_skill_match(candidate_skills, job_skills)
    
    def _keyword_skill_match(self, candidate_skills: List[str], job_skills: List[str]) -> float:
        """Fallback keyword-based skill matching"""
        if not candidate_skills or not job_skills:
            return 0.0
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matches = 0
        for job_skill in job_skills_lower:
            for candidate_skill in candidate_skills_lower:
                if job_skill in candidate_skill or candidate_skill in job_skill:
                    matches += 1
                    break
        
        return matches / len(job_skills)
    
    def _calculate_experience_match(self, resume: ParsedResume, job: JobRequirement) -> float:
        """Calculate experience level matching"""
        candidate_experience = resume.total_experience_years
        job_level = job.experience_level.lower()
        
        if job_level in self.experience_levels:
            required_range = self.experience_levels[job_level]['years']
            min_years, max_years = required_range
            
            if min_years <= candidate_experience <= max_years:
                return 1.0
            elif candidate_experience > max_years:
                # Over-qualified, slight penalty
                return max(0.7, 1.0 - (candidate_experience - max_years) * 0.05)
            else:
                # Under-qualified, larger penalty
                return max(0.0, candidate_experience / min_years * 0.8)
        
        return 0.5  # Default if level not recognized
    
    def _calculate_education_match(self, resume: ParsedResume, job: JobRequirement) -> float:
        """Calculate education matching score"""
        if not job.education_required or job.education_required.lower() == 'none':
            return 1.0
        
        if not resume.education:
            return 0.3  # Some penalty for missing education
        
        # Extract education levels
        candidate_degrees = [edu.degree.lower() for edu in resume.education]
        required_education = job.education_required.lower()
        
        # Education hierarchy
        education_hierarchy = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3, 'bs': 3, 'ba': 3,
            'master': 4, 'ms': 4, 'ma': 4, 'mba': 4,
            'phd': 5, 'doctorate': 5
        }
        
        # Get required level
        required_level = 0
        for edu_type, level in education_hierarchy.items():
            if edu_type in required_education:
                required_level = level
                break
        
        # Get candidate's highest level
        candidate_level = 0
        for degree in candidate_degrees:
            for edu_type, level in education_hierarchy.items():
                if edu_type in degree:
                    candidate_level = max(candidate_level, level)
        
        if candidate_level >= required_level:
            return 1.0
        elif candidate_level >= required_level - 1:
            return 0.8
        else:
            return 0.5
    
    def _calculate_location_match(
        self, 
        resume: ParsedResume, 
        job: JobRequirement, 
        preferences: Dict
    ) -> float:
        """Calculate location compatibility"""
        
        # If job is remote-friendly, high score
        if job.remote_friendly:
            return 1.0
        
        # Check if job location matches user preferences
        preferred_locations = preferences.get('preferred_locations', [])
        job_location = job.location.lower()
        
        for pref_location in preferred_locations:
            if pref_location.lower() in job_location or job_location in pref_location.lower():
                return 0.9
        
        # Check candidate's current location
        if resume.contact_info.location:
            candidate_location = resume.contact_info.location.lower()
            if candidate_location in job_location or job_location in candidate_location:
                return 0.8
        
        # Default for location mismatch
        return 0.3
    
    def _calculate_culture_fit(self, resume: ParsedResume, job: JobRequirement) -> float:
        """Calculate culture fit using company size, industry, etc."""
        score = 0.5  # Base score
        
        # Industry match
        if hasattr(resume, 'primary_domain') and resume.primary_domain:
            domain_industry_mapping = {
                'cybersecurity': ['Security', 'Financial Services', 'Technology'],
                'data_science': ['Technology', 'Healthcare', 'Finance'],
                'web_technologies': ['Technology', 'E-commerce', 'Media']
            }
            
            if resume.primary_domain in domain_industry_mapping:
                relevant_industries = domain_industry_mapping[resume.primary_domain]
                if job.industry in relevant_industries:
                    score += 0.3
        
        # Company size preference (can be extracted from work history)
        prev_companies = [exp.company for exp in resume.work_experience]
        if len(prev_companies) > 0:
            # Assume larger companies if person has worked at known big companies
            big_companies = ['Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix']
            has_big_company_exp = any(company in big_companies for company in prev_companies)
            
            if has_big_company_exp and job.company_size == 'Large':
                score += 0.2
            elif not has_big_company_exp and job.company_size in ['Startup', 'Small']:
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_salary_compatibility(
        self, 
        resume: ParsedResume, 
        job: JobRequirement, 
        preferences: Dict
    ) -> float:
        """Calculate salary compatibility"""
        min_salary = preferences.get('min_salary', 50000)
        
        if not job.salary_range:
            return 0.7  # Unknown salary, neutral score
        
        job_min, job_max = job.salary_range
        
        if job_max >= min_salary:
            return 1.0
        elif job_min >= min_salary * 0.8:
            return 0.8
        else:
            return 0.3
    
    def _generate_detailed_analysis(
        self, 
        resume: ParsedResume, 
        job: JobRequirement, 
        scores: Dict
    ) -> Dict[str, Any]:
        """Generate detailed analysis of the match"""
        
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'skill_gaps': [],
            'experience_assessment': '',
            'education_assessment': '',
            'location_notes': '',
            'overall_assessment': ''
        }
        
        # Analyze strengths
        if scores['skill_score'] > 0.8:
            analysis['strengths'].append("Excellent skill match with job requirements")
        elif scores['skill_score'] > 0.6:
            analysis['strengths'].append("Good skill match with some relevant experience")
        
        if scores['experience_score'] > 0.8:
            analysis['strengths'].append("Experience level aligns well with position")
        
        if scores['location_score'] > 0.8:
            analysis['strengths'].append("Location is compatible with job requirements")
        
        # Analyze weaknesses
        if scores['skill_score'] < 0.5:
            analysis['weaknesses'].append("Limited skill match with job requirements")
        
        if scores['experience_score'] < 0.5:
            analysis['weaknesses'].append("Experience level may not meet job requirements")
        
        if scores['education_score'] < 0.5:
            analysis['weaknesses'].append("Education requirements may not be fully met")
        
        # Generate recommendations
        if scores['skill_score'] < 0.7:
            analysis['recommendations'].append("Consider acquiring missing technical skills")
        
        if scores['experience_score'] < 0.7:
            analysis['recommendations'].append("Highlight relevant project experience")
        
        # Experience assessment
        experience_diff = resume.total_experience_years - self.experience_levels.get(
            job.experience_level.lower(), {'years': (0, 0)}
        )['years'][0]
        
        if experience_diff > 2:
            analysis['experience_assessment'] = "Over-qualified based on years of experience"
        elif experience_diff >= 0:
            analysis['experience_assessment'] = "Meets experience requirements"
        else:
            analysis['experience_assessment'] = "Below minimum experience requirements"
        
        # Overall assessment
        overall_score = sum(scores.values()) / len(scores)
        if overall_score > 0.8:
            analysis['overall_assessment'] = "Excellent match - highly recommended to apply"
        elif overall_score > 0.6:
            analysis['overall_assessment'] = "Good match - recommended to apply"
        elif overall_score > 0.4:
            analysis['overall_assessment'] = "Moderate match - consider applying with tailored application"
        else:
            analysis['overall_assessment'] = "Poor match - may not be suitable"
        
        return analysis
    
    def _generate_recommendation(self, overall_score: float, analysis: Dict) -> str:
        """Generate application recommendation"""
        if overall_score >= 0.8:
            return "HIGHLY RECOMMENDED: Apply immediately with standard application"
        elif overall_score >= 0.6:
            return "RECOMMENDED: Apply with tailored resume and cover letter"
        elif overall_score >= 0.4:
            return "CONSIDER: Apply only if genuinely interested and willing to learn"
        else:
            return "NOT RECOMMENDED: Focus on better-matching opportunities"
    
    def _find_matching_skills(self, resume: ParsedResume, job: JobRequirement) -> List[str]:
        """Find skills that match between resume and job"""
        candidate_skills = []
        for skill_category in resume.skills.values():
            candidate_skills.extend([skill.lower() for skill in skill_category])
        
        job_skills = [skill.lower() for skill in job.required_skills + job.preferred_skills]
        
        matching = []
        for job_skill in job_skills:
            for candidate_skill in candidate_skills:
                if job_skill in candidate_skill or candidate_skill in job_skill:
                    matching.append(job_skill)
                    break
        
        return matching
    
    def _find_missing_skills(self, resume: ParsedResume, job: JobRequirement) -> List[str]:
        """Find required skills that candidate is missing"""
        candidate_skills = []
        for skill_category in resume.skills.values():
            candidate_skills.extend([skill.lower() for skill in skill_category])
        
        missing = []
        for skill in job.required_skills:
            skill_lower = skill.lower()
            found = False
            for candidate_skill in candidate_skills:
                if skill_lower in candidate_skill or candidate_skill in skill_lower:
                    found = True
                    break
            if not found:
                missing.append(skill)
        
        return missing
    
    def _determine_confidence_level(self, score: float, analysis: Dict) -> str:
        """Determine confidence level in the match"""
        if score > 0.8 and len(analysis.get('weaknesses', [])) <= 1:
            return "HIGH"
        elif score > 0.6 and len(analysis.get('weaknesses', [])) <= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def batch_match_jobs(
        self, 
        resume: ParsedResume, 
        jobs: List[JobRequirement],
        user_preferences: Dict = None,
        top_n: int = 20
    ) -> List[MatchResult]:
        """Match resume against multiple jobs and return top matches"""
        
        print(f"🎯 Matching resume against {len(jobs)} jobs...")
        
        matches = []
        for i, job in enumerate(jobs):
            try:
                match_result = self.calculate_comprehensive_match(resume, job, user_preferences)
                matches.append(match_result)
                
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(jobs)} jobs")
                    
            except Exception as e:
                print(f"   ❌ Error matching job {job.id}: {e}")
                continue
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        print(f"✅ Completed matching. Top {min(top_n, len(matches))} results:")
        for i, match in enumerate(matches[:top_n]):
            print(f"   {i+1}. Score: {match.overall_score:.2%} - {match.recommendation}")
        
        return matches[:top_n]
    
    def generate_application_insights(self, match: MatchResult, resume: ParsedResume) -> Dict:
        """Generate insights for job application optimization"""
        insights = {
            'resume_optimization': [],
            'cover_letter_points': [],
            'interview_preparation': [],
            'skills_to_highlight': match.matching_skills,
            'skills_to_develop': match.missing_skills[:5],  # Top 5 missing skills
            'application_strategy': ''
        }
        
        # Resume optimization suggestions
        if match.skill_match_score < 0.7:
            insights['resume_optimization'].append("Emphasize relevant technical skills more prominently")
        
        if match.experience_match_score < 0.7:
            insights['resume_optimization'].append("Quantify achievements with specific metrics")
        
        # Cover letter points
        strengths = match.detailed_analysis.get('strengths', [])
        for strength in strengths:
            insights['cover_letter_points'].append(f"Highlight: {strength}")
        
        # Interview preparation
        if match.missing_skills:
            insights['interview_preparation'].append(
                f"Prepare to discuss how you would quickly learn: {', '.join(match.missing_skills[:3])}"
            )
        
        # Application strategy
        if match.overall_score >= 0.8:
            insights['application_strategy'] = "Apply with confidence using standard approach"
        elif match.overall_score >= 0.6:
            insights['application_strategy'] = "Customize application to emphasize matching qualifications"
        else:
            insights['application_strategy'] = "Consider reaching out to hiring manager or employee referral"
        
        return insights
    
    def save_match_results(self, matches: List[MatchResult], filename: str = None):
        """Save match results to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"job_matches_{timestamp}.json"
        
        output_dir = Path("data/job_matches")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        # Convert to dictionaries for JSON serialization
        matches_data = [asdict(match) for match in matches]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(matches_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Match results saved to: {filepath}")
        return str(filepath)

def load_sample_jobs() -> List[JobRequirement]:
    """Load sample job requirements for testing"""
    sample_jobs = [
        JobRequirement(
            id="job_001",
            title="Senior Cybersecurity Engineer",
            company="TechCorp Inc",
            location="Berlin, Germany",
            description="We are looking for an experienced cybersecurity professional...",
            required_skills=["penetration testing", "vulnerability assessment", "python", "network security"],
            preferred_skills=["aws", "kubernetes", "incident response"],
            experience_level="senior",
            education_required="bachelor",
            salary_range=(80000, 120000),
            job_type="full-time",
            remote_friendly=True,
            industry="Technology",
            company_size="Large",
            benefits=["health insurance", "flexible hours"],
            application_url="https://techcorp.com/careers/001",
            source_platform="company_website",
            posted_date="2024-01-15"
        ),
        JobRequirement(
            id="job_002",
            title="Cloud Security Architect",
            company="CloudFirst GmbH",
            location="Munich, Germany",
            description="Join our cloud security team...",
            required_skills=["aws", "azure", "cloud security", "terraform"],
            preferred_skills=["kubernetes", "python", "compliance"],
            experience_level="senior",
            education_required="bachelor",
            salary_range=(90000, 130000),
            job_type="full-time",
            remote_friendly=False,
            industry="Technology",
            company_size="Medium",
            benefits=["stock options", "training budget"],
            application_url="https://cloudfirst.com/jobs/002",
            source_platform="linkedin",
            posted_date="2024-01-10"
        )
    ]
    
    return sample_jobs

def main():
    """Demo function"""
    print("🎯 INTELLIGENT JOB MATCHING SYSTEM")
    print("🧠 AI-powered resume-to-job matching")
    print("="*50)
    
    # Initialize matcher
    matcher = AIJobMatcher()
    
    # Parse resume (you'll need to have a resume file)
    resume_path = "config/resume.pdf"
    if Path(resume_path).exists():
        parser = ResumeParser()
        resume = parser.parse_resume(resume_path)
        
        # Load sample jobs (in production, this would come from scrapers)
        jobs = load_sample_jobs()
        
        # User preferences
        preferences = {
            'preferred_locations': ['Remote', 'Berlin', 'Munich'],
            'min_salary': 80000,
            'job_types': ['full-time'],
            'industries': ['Technology', 'Cybersecurity'],
            'company_sizes': ['Medium', 'Large']
        }
        
        # Perform matching
        matches = matcher.batch_match_jobs(resume, jobs, preferences, top_n=10)
        
        # Display results
        print(f"\n📊 MATCHING RESULTS:")
        print("="*30)
        
        for i, match in enumerate(matches[:5]):
            print(f"\n{i+1}. Job ID: {match.job_id}")
            print(f"   Overall Score: {match.overall_score:.2%}")
            print(f"   Recommendation: {match.recommendation}")
            print(f"   Confidence: {match.confidence_level}")
            print(f"   Matching Skills: {', '.join(match.matching_skills[:3])}")
            print(f"   Missing Skills: {', '.join(match.missing_skills[:3])}")
        
        # Save results
        matcher.save_match_results(matches)
        
        # Generate application insights for top match
        if matches:
            top_match = matches[0]
            insights = matcher.generate_application_insights(top_match, resume)
            
            print(f"\n💡 APPLICATION INSIGHTS FOR TOP MATCH:")
            print(f"Strategy: {insights['application_strategy']}")
            print(f"Skills to Highlight: {', '.join(insights['skills_to_highlight'][:3])}")
            print(f"Skills to Develop: {', '.join(insights['skills_to_develop'])}")
        
    else:
        print(f"❌ Resume file not found: {resume_path}")
        print("💡 Please place your resume at config/resume.pdf")

if __name__ == "__main__":
    main()