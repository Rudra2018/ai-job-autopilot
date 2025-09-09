#!/usr/bin/env python3
"""
Auto-Application Engine - Handles automated job applications with AI-generated content
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class AutoApplicationEngine:
    def __init__(self):
        self.screening_questions = {
            'general': [
                "Why are you interested in this position?",
                "What makes you a good fit for this role?",
                "What are your salary expectations?",
                "When would you be available to start?",
                "Why do you want to work at our company?"
            ],
            'technical': [
                "Describe your experience with [skill]",
                "How do you approach problem-solving?",
                "Tell us about a challenging project you've worked on",
                "What technologies are you most excited about?",
                "How do you stay current with industry trends?"
            ],
            'security_specific': [
                "Describe your experience with penetration testing",
                "How do you approach vulnerability assessment?",
                "What security frameworks are you familiar with?",
                "How do you handle security incident response?",
                "Describe your experience with compliance standards"
            ]
        }
    
    def generate_screening_answers(self, questions: List[str], job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate AI-powered answers to screening questions"""
        answers = []
        
        for question in questions:
            answer = self.create_contextual_answer(question, job_data, user_profile)
            answers.append({
                'question': question,
                'answer': answer,
                'generated_at': datetime.now().isoformat()
            })
        
        return answers
    
    def create_contextual_answer(self, question: str, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Create contextual answer based on question type and user profile"""
        question_lower = question.lower()
        company = job_data.get('company', 'the company')
        title = job_data.get('title', 'this position')
        
        # Get user data
        skills = user_profile.get('skills', {})
        experience_years = user_profile.get('total_experience', {}).get('total_years', 0)
        industries = user_profile.get('industries', [])
        seniority = user_profile.get('seniority', {}).get('level', 'Professional')
        
        # Generate answer based on question type
        if 'why interested' in question_lower or 'why do you want' in question_lower:
            return self.generate_interest_answer(company, title, skills, industries, experience_years)
        
        elif 'good fit' in question_lower or 'why you' in question_lower:
            return self.generate_fit_answer(title, skills, experience_years, seniority)
        
        elif 'salary' in question_lower or 'compensation' in question_lower:
            return self.generate_salary_answer(experience_years, seniority)
        
        elif 'start' in question_lower or 'available' in question_lower:
            return "I'm excited about this opportunity and could start with standard two weeks' notice to ensure a smooth transition from my current responsibilities."
        
        elif 'experience with' in question_lower:
            skill = self.extract_skill_from_question(question)
            return self.generate_skill_experience_answer(skill, skills, experience_years)
        
        elif 'problem-solving' in question_lower or 'approach' in question_lower:
            return f"I approach problems systematically by first understanding the requirements, analyzing potential solutions, and implementing the most effective approach. My {experience_years} years of experience have taught me the importance of collaboration and thorough testing."
        
        elif 'challenging project' in question_lower:
            return self.generate_project_answer(skills, industries)
        
        else:
            return self.generate_generic_answer(question, skills, experience_years)
    
    def generate_interest_answer(self, company: str, title: str, skills: Dict, industries: List[str], years: int) -> str:
        """Generate answer for 'why interested' questions"""
        primary_skill = self.get_primary_skill(skills)
        industry = industries[0] if industries else "technology"
        
        return f"I'm excited about the {title} opportunity at {company} because it perfectly aligns with my {years}+ years of experience in {industry.lower()}. Your company's reputation for innovation and my expertise in {primary_skill} make this an ideal match where I can contribute meaningfully while continuing to grow professionally."
    
    def generate_fit_answer(self, title: str, skills: Dict, years: int, seniority: str) -> str:
        """Generate answer for 'good fit' questions"""
        top_skills = self.get_top_skills(skills, 3)
        
        return f"My {years} years of hands-on experience in {', '.join(top_skills)} directly align with the {title} requirements. As a {seniority} professional, I bring both technical expertise and the ability to collaborate effectively with cross-functional teams to deliver high-impact solutions."
    
    def generate_salary_answer(self, years: int, seniority: str) -> str:
        """Generate salary expectation answer"""
        if years >= 5 or seniority == 'Senior':
            range_text = "$140k-$180k"
        elif years >= 2:
            range_text = "$120k-$160k"
        else:
            range_text = "$100k-$140k"
        
        return f"Based on my {years} years of experience and market research for similar roles, I'm looking for a compensation package in the {range_text} range. I'm open to discussing the complete package including benefits and growth opportunities."
    
    def generate_skill_experience_answer(self, skill: str, skills: Dict, years: int) -> str:
        """Generate answer about specific skill experience"""
        if not skill:
            skill = self.get_primary_skill(skills)
        
        return f"I have {years}+ years of hands-on experience with {skill}. I've successfully applied it in various projects and continue to stay current with best practices and emerging trends in this area."
    
    def generate_project_answer(self, skills: Dict, industries: List[str]) -> str:
        """Generate answer about challenging projects"""
        primary_skill = self.get_primary_skill(skills)
        industry = industries[0] if industries else "technology"
        
        return f"One of my most challenging projects involved implementing {primary_skill} solutions in a {industry.lower()} environment. The project required careful planning, stakeholder collaboration, and innovative problem-solving to overcome technical constraints and deliver results on time."
    
    def generate_generic_answer(self, question: str, skills: Dict, years: int) -> str:
        """Generate generic contextual answer"""
        primary_skill = self.get_primary_skill(skills)
        
        return f"With {years} years of experience and expertise in {primary_skill}, I bring a proven track record of delivering results and contributing to team success. I'm always eager to take on new challenges and contribute to innovative solutions."
    
    def get_primary_skill(self, skills: Dict) -> str:
        """Get the primary skill from user's skill set"""
        for category, skill_list in skills.items():
            if skill_list:
                return skill_list[0]
        return "technology"
    
    def get_top_skills(self, skills: Dict, count: int = 3) -> List[str]:
        """Get top skills across all categories"""
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list)
        return all_skills[:count]
    
    def extract_skill_from_question(self, question: str) -> str:
        """Extract skill name from question text"""
        # Simple extraction - in real implementation, this would be more sophisticated
        if '[skill]' in question:
            return "relevant technologies"
        return ""
    
    def generate_cover_letter(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Generate customized cover letter for specific job"""
        company = job_data.get('company', 'the company')
        title = job_data.get('title', 'this position')
        job_description = job_data.get('job_description', '')
        
        # Get user data
        skills = user_profile.get('skills', {})
        years = user_profile.get('total_experience', {}).get('total_years', 0)
        industries = user_profile.get('industries', [])
        name = user_profile.get('personal_info', {}).get('full_name', 'Your Name')
        
        top_skills = self.get_top_skills(skills, 4)
        industry = industries[0] if industries else "technology"
        
        cover_letter = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {title} position at {company}. With {years}+ years of specialized experience in {industry.lower()}, I am excited about the opportunity to contribute to your team's continued success.

In my career, I have developed expertise in {', '.join(top_skills)} and have consistently delivered high-impact solutions. My background directly aligns with your requirements, particularly in areas such as {', '.join(top_skills[:2])}.

I am particularly drawn to {company} because of your reputation for innovation and commitment to excellence. The opportunity to work on challenging projects while contributing to meaningful solutions is exactly what I'm seeking in my next role.

I would welcome the opportunity to discuss how my technical expertise and passion for {industry.lower()} can contribute to {company}'s objectives. Thank you for considering my application.

Best regards,
{name}"""
        
        return cover_letter
    
    def simulate_application_submission(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the application submission process"""
        application_type = job_data.get('application_type', 'External Application')
        
        # Generate screening questions for this job
        questions = self.select_screening_questions(job_data, user_profile)
        
        # Generate answers
        screening_answers = self.generate_screening_answers(questions, job_data, user_profile)
        
        # Generate cover letter
        cover_letter = self.generate_cover_letter(job_data, user_profile)
        
        # Simulate processing time based on application type
        if application_type == 'Easy Apply':
            processing_time = round(random.uniform(1.0, 3.0), 1)
            success_rate = 0.95
        elif application_type == 'Company Portal':
            processing_time = round(random.uniform(3.0, 8.0), 1)
            success_rate = 0.85
        else:
            processing_time = round(random.uniform(5.0, 12.0), 1)
            success_rate = 0.75
        
        # Determine application status
        status = 'Applied' if random.random() < success_rate else 'Failed'
        
        return {
            'job_url': job_data.get('url', ''),
            'job_title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'status': status,
            'platform': self.determine_platform(job_data),
            'application_type': application_type,
            'screening_answers': screening_answers,
            'cover_letter': cover_letter,
            'applied_at': datetime.now().isoformat(),
            'processing_time': f"{processing_time} seconds",
            'estimated_response_time': self.estimate_response_time(application_type),
            'application_metadata': {
                'auto_generated': True,
                'questions_answered': len(screening_answers),
                'cover_letter_customized': True
            }
        }
    
    def select_screening_questions(self, job_data: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Select relevant screening questions for the job"""
        questions = []
        
        # Always include basic questions
        questions.extend(random.sample(self.screening_questions['general'], 2))
        
        # Add technical questions if relevant
        if any(skill in job_data.get('job_description', '').lower() for skill in ['technical', 'programming', 'development']):
            questions.extend(random.sample(self.screening_questions['technical'], 1))
        
        # Add security-specific questions if it's a security role
        if any(term in job_data.get('title', '').lower() for term in ['security', 'cyber', 'penetration']):
            questions.extend(random.sample(self.screening_questions['security_specific'], 1))
        
        return questions[:4]  # Limit to 4 questions
    
    def determine_platform(self, job_data: Dict[str, Any]) -> str:
        """Determine which platform the job is from"""
        url = job_data.get('url', '').lower()
        
        if 'linkedin' in url:
            return 'LinkedIn'
        elif 'indeed' in url:
            return 'Indeed'
        elif 'glassdoor' in url:
            return 'Glassdoor'
        else:
            return 'Company Portal'
    
    def estimate_response_time(self, application_type: str) -> str:
        """Estimate typical response time for different application types"""
        if application_type == 'Easy Apply':
            return "2-5 business days"
        elif application_type == 'Company Portal':
            return "5-10 business days"
        else:
            return "7-14 business days"
    
    def process_batch_applications(self, matched_jobs: List[Dict[str, Any]], user_profile: Dict[str, Any], max_applications: int = 5) -> Dict[str, Any]:
        """Process batch job applications"""
        applications = []
        
        # Select top jobs for application
        selected_jobs = matched_jobs[:max_applications]
        
        for job in selected_jobs:
            try:
                application_result = self.simulate_application_submission(job, user_profile)
                applications.append(application_result)
            except Exception as e:
                # Handle application failure
                applications.append({
                    'job_url': job.get('url', ''),
                    'job_title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'status': 'Failed',
                    'error': str(e),
                    'applied_at': datetime.now().isoformat()
                })
        
        # Calculate summary statistics
        successful_apps = len([app for app in applications if app['status'] == 'Applied'])
        failed_apps = len([app for app in applications if app['status'] == 'Failed'])
        
        return {
            'batch_status': 'completed',
            'applications': applications,
            'summary': {
                'total_attempted': len(applications),
                'successful': successful_apps,
                'failed': failed_apps,
                'success_rate': f"{(successful_apps/len(applications)*100):.1f}%" if applications else "0%",
                'total_processing_time': sum(float(app.get('processing_time', '0').split()[0]) for app in applications if 'processing_time' in app),
                'average_questions_per_app': sum(len(app.get('screening_answers', [])) for app in applications) / len(applications) if applications else 0
            },
            'processed_at': datetime.now().isoformat()
        }

# Global instance for use in Streamlit
auto_application_engine = AutoApplicationEngine()