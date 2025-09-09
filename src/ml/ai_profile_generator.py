#!/usr/bin/env python3
"""
AI Profile Generator - Creates comprehensive user profiles from parsed resume data
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class AIProfileGenerator:
    def __init__(self):
        self.qa_templates = {
            'tell_me_about_yourself': {
                'structure': "I'm a {seniority} {primary_role} with {experience_years} years of experience in {primary_skills}. {key_achievements} {career_focus}",
                'variables': ['seniority', 'primary_role', 'experience_years', 'primary_skills', 'key_achievements', 'career_focus']
            },
            'why_good_fit': {
                'structure': "My {experience_years} years of experience in {relevant_skills} directly align with your requirements. {specific_achievements} {value_proposition}",
                'variables': ['experience_years', 'relevant_skills', 'specific_achievements', 'value_proposition']
            }
        }
    
    def generate_professional_summary(self, parsed_resume: Dict[str, Any]) -> str:
        """Generate AI-powered professional summary"""
        experience = parsed_resume.get('total_experience', {})
        years = experience.get('total_years', 0)
        seniority = parsed_resume.get('seniority', {}).get('level', 'Professional')
        skills = parsed_resume.get('skills', {})
        industries = parsed_resume.get('industries', [])
        
        # Get top skills across categories
        top_skills = []
        for category, skill_list in skills.items():
            if skill_list and category != 'soft_skills':
                top_skills.extend(skill_list[:2])  # Top 2 from each category
        
        primary_industry = industries[0] if industries else "Technology"
        
        summary = f"Accomplished {seniority} Professional with {years}+ years of specialized experience in {primary_industry.lower()}. "
        
        if top_skills:
            skills_text = ", ".join(top_skills[:4])
            summary += f"Expert in {skills_text} with proven track record of delivering high-impact solutions. "
        
        summary += f"Strong background in {', '.join(industries[:2])} with demonstrated ability to drive technical excellence and cross-functional collaboration."
        
        return summary
    
    def extract_skill_highlights(self, parsed_resume: Dict[str, Any]) -> List[str]:
        """Extract top 6 skill highlights"""
        skills = parsed_resume.get('skills', {})
        highlights = []
        
        # Priority order for skill categories
        priority_categories = ['cybersecurity', 'programming_languages', 'frameworks', 'tools', 'soft_skills']
        
        for category in priority_categories:
            category_skills = skills.get(category, [])
            for skill in category_skills:
                if len(highlights) < 6:
                    highlights.append(skill)
        
        # Fill remaining slots with any other skills
        for category, skill_list in skills.items():
            if category not in priority_categories:
                for skill in skill_list:
                    if len(highlights) < 6:
                        highlights.append(skill)
        
        return highlights
    
    def generate_career_objectives(self, parsed_resume: Dict[str, Any]) -> str:
        """Generate career objectives based on experience and skills"""
        seniority = parsed_resume.get('seniority', {})
        years = parsed_resume.get('total_experience', {}).get('total_years', 0)
        industries = parsed_resume.get('industries', [])
        level = seniority.get('level', 'Professional')
        
        if level == 'Senior' or years >= 5:
            objectives = f"Seeking senior leadership opportunities in {', '.join(industries[:2]).lower()} where I can leverage my proven expertise to drive strategic initiatives and mentor high-performing teams. "
            objectives += "Passionate about building scalable solutions and contributing to innovative projects that make meaningful impact at scale."
        elif level == 'Mid-Level' or years >= 2:
            objectives = f"Looking to advance to senior technical roles in {', '.join(industries[:2]).lower()} where I can expand my impact and take on greater technical challenges. "
            objectives += "Eager to contribute to cutting-edge projects while continuing professional growth in emerging technologies."
        else:
            objectives = f"Seeking growth opportunities in {', '.join(industries[:2]).lower()} to build expertise and contribute to impactful projects. "
            objectives += "Committed to continuous learning and professional development in a collaborative, innovation-focused environment."
        
        return objectives
    
    def generate_role_suggestions(self, parsed_resume: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate ideal job titles and target industries"""
        skills = parsed_resume.get('skills', {})
        seniority = parsed_resume.get('seniority', {}).get('level', 'Professional')
        industries = parsed_resume.get('industries', [])
        
        # Base role mapping
        role_mapping = {
            'cybersecurity': ['Security Engineer', 'Cybersecurity Analyst', 'Penetration Tester', 'Security Consultant'],
            'programming_languages': ['Software Engineer', 'Developer', 'Software Developer', 'Backend Engineer'],
            'frameworks': ['Full Stack Developer', 'Frontend Engineer', 'Web Developer', 'Application Developer']
        }
        
        suggested_roles = []
        
        # Generate roles based on skills
        for skill_category, skill_list in skills.items():
            if skill_list and skill_category in role_mapping:
                base_roles = role_mapping[skill_category]
                if seniority == 'Senior':
                    suggested_roles.extend([f"Senior {role}" for role in base_roles[:2]])
                    suggested_roles.extend([f"Lead {role}" for role in base_roles[:1]])
                elif seniority == 'Mid-Level':
                    suggested_roles.extend(base_roles[:2])
                    suggested_roles.extend([f"Senior {role}" for role in base_roles[:1]])
                else:
                    suggested_roles.extend([f"Junior {role}" for role in base_roles[:2]])
                    suggested_roles.extend(base_roles[:1])
        
        # Remove duplicates and limit
        unique_roles = list(set(suggested_roles))[:8]
        
        return {
            'ideal_job_titles': unique_roles,
            'target_industries': industries
        }
    
    def generate_qa_responses(self, parsed_resume: Dict[str, Any]) -> Dict[str, str]:
        """Generate responses to common recruiter questions"""
        experience = parsed_resume.get('total_experience', {})
        years = experience.get('total_years', 0)
        seniority = parsed_resume.get('seniority', {}).get('level', 'Professional')
        skills = parsed_resume.get('skills', {})
        industries = parsed_resume.get('industries', [])
        
        # Get primary skills for each category
        primary_skills = []
        for category, skill_list in skills.items():
            if skill_list:
                primary_skills.extend(skill_list[:2])
        
        responses = {}
        
        # Tell me about yourself
        responses['tell_me_about_yourself'] = f"I'm a {seniority} professional with {years}+ years of experience specializing in {', '.join(industries[:2]).lower()}. My expertise spans {', '.join(primary_skills[:4])}, and I have a proven track record of delivering high-impact solutions. I'm passionate about leveraging technology to solve complex problems and thrive in collaborative environments where I can contribute to innovative projects while continuing to grow professionally."
        
        # Why are you a good fit
        responses['why_good_fit'] = f"My {years} years of hands-on experience in {', '.join(primary_skills[:3])} directly align with your requirements. I bring a unique combination of technical depth and practical problem-solving skills, having worked across {', '.join(industries[:2]).lower()}. I'm particularly drawn to opportunities where I can apply my expertise in {primary_skills[0] if primary_skills else 'technology'} while contributing to meaningful projects that drive business impact."
        
        # Salary expectations
        if years >= 5:
            salary_range = "$140k-$180k"
        elif years >= 2:
            salary_range = "$100k-$140k"
        else:
            salary_range = "$80k-$120k"
        
        responses['salary_expectations'] = f"Based on my {years} years of experience and market research for similar roles, I'm looking for a compensation package in the {salary_range} range. I'm open to discussing the complete package including equity, benefits, and growth opportunities, as I'm most interested in finding the right fit where I can make a meaningful contribution."
        
        # Career goals
        if years >= 5:
            responses['career_goals'] = "My immediate goal is to take on senior technical leadership roles where I can drive strategic initiatives and mentor high-performing teams. Long-term, I aspire to become a recognized expert in my field and contribute to innovative solutions that have broad industry impact."
        else:
            responses['career_goals'] = f"I'm focused on continuing to grow my expertise in {', '.join(industries[:2]).lower()} while taking on increasingly challenging projects. My goal is to become a senior technical contributor who can lead complex initiatives and mentor others while staying current with emerging technologies."
        
        return responses
    
    def generate_cover_letter_template(self, parsed_resume: Dict[str, Any]) -> str:
        """Generate customizable cover letter template"""
        years = parsed_resume.get('total_experience', {}).get('total_years', 0)
        skills = parsed_resume.get('skills', {})
        industries = parsed_resume.get('industries', [])
        
        # Get top skills
        top_skills = []
        for category, skill_list in skills.items():
            if skill_list:
                top_skills.extend(skill_list[:2])
        
        template = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {{job_title}} position at {{company}}. With {years}+ years of experience in {', '.join(industries[:2]).lower()} and proven expertise in {', '.join(top_skills[:3])}, I am confident I would be a valuable addition to your team.

In my current role, I have successfully {{key_achievement_1}} and {{key_achievement_2}}. My background in {', '.join(top_skills[:4])} directly aligns with your requirements, particularly your need for {{job_specific_requirement}}.

I am particularly drawn to {{company}} because of {{company_specific_interest}}. Your commitment to {{company_value}} resonates with my professional values and career aspirations.

I would welcome the opportunity to discuss how my technical skills and passion for {industries[0].lower() if industries else 'technology'} can contribute to your team's continued success.

Best regards,
{{full_name}}"""
        
        return template
    
    def generate_complete_profile(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete AI user profile"""
        return {
            'generation_status': 'success',
            'generated_at': datetime.now().isoformat(),
            'profile_data': {
                'professional_summary': self.generate_professional_summary(parsed_resume),
                'skill_highlights': self.extract_skill_highlights(parsed_resume),
                'career_objectives': self.generate_career_objectives(parsed_resume),
                'role_suggestions': self.generate_role_suggestions(parsed_resume),
                'qa_responses': self.generate_qa_responses(parsed_resume),
                'cover_letter_template': self.generate_cover_letter_template(parsed_resume)
            },
            'personalization_score': self.calculate_personalization_score(parsed_resume),
            'profile_completeness': self.assess_profile_completeness(parsed_resume)
        }
    
    def calculate_personalization_score(self, parsed_resume: Dict[str, Any]) -> float:
        """Calculate how personalized the profile is based on available data"""
        score = 0.0
        max_score = 10.0
        
        # Check data availability
        if parsed_resume.get('personal_info', {}).get('full_name'):
            score += 1.0
        if parsed_resume.get('experiences'):
            score += 2.0
        if parsed_resume.get('total_experience', {}).get('total_years', 0) > 0:
            score += 1.5
        if parsed_resume.get('skills', {}):
            score += 2.0
        if parsed_resume.get('industries'):
            score += 1.5
        if parsed_resume.get('seniority', {}).get('level'):
            score += 2.0
        
        return min(score / max_score * 100, 100)  # Convert to percentage
    
    def assess_profile_completeness(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall profile completeness"""
        required_sections = ['personal_info', 'experiences', 'skills', 'seniority']
        present_sections = []
        missing_sections = []
        
        for section in required_sections:
            if parsed_resume.get(section):
                present_sections.append(section)
            else:
                missing_sections.append(section)
        
        completeness = len(present_sections) / len(required_sections) * 100
        
        return {
            'completeness_percentage': completeness,
            'present_sections': present_sections,
            'missing_sections': missing_sections,
            'recommendations': self.get_improvement_recommendations(missing_sections)
        }
    
    def get_improvement_recommendations(self, missing_sections: List[str]) -> List[str]:
        """Get recommendations for improving profile completeness"""
        recommendations = []
        
        if 'personal_info' in missing_sections:
            recommendations.append("Add complete contact information")
        if 'experiences' in missing_sections:
            recommendations.append("Include detailed work experience with dates")
        if 'skills' in missing_sections:
            recommendations.append("List technical and soft skills")
        if 'seniority' in missing_sections:
            recommendations.append("Clarify experience level and role seniority")
        
        return recommendations

# Global instance for use in Streamlit
profile_generator = AIProfileGenerator()