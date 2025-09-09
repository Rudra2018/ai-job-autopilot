#!/usr/bin/env python3
"""
🤖 Multi-AI Resume Parser
Advanced resume parsing using GPT-4, Gemini Pro, and Claude for maximum accuracy
"""

import json
import logging
import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys - Configure these in your environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# AI Service Availability
OPENAI_AVAILABLE = False
GEMINI_PRO_AVAILABLE = False
ANTHROPIC_AVAILABLE = False

try:
    import openai
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        OPENAI_AVAILABLE = True
        logger.info("✅ OpenAI GPT-4 available")
    else:
        logger.warning("⚠️ OpenAI API key not provided")
except ImportError:
    logger.warning("⚠️ OpenAI not available - install with: pip install openai")

try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_PRO_AVAILABLE = True
        logger.info("✅ Gemini Pro available")
    else:
        logger.warning("⚠️ Gemini API key not provided")
except ImportError:
    logger.warning("⚠️ Gemini Pro not available")

try:
    import anthropic
    if ANTHROPIC_API_KEY:
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        ANTHROPIC_AVAILABLE = True
        logger.info("✅ Anthropic Claude available")
    else:
        logger.warning("⚠️ Anthropic API key not provided")
except ImportError:
    logger.warning("⚠️ Anthropic not available - install with: pip install anthropic")

def calculate_total_experience(experience: List[Dict]) -> float:
    """Calculate total years of experience from experience entries."""
    total_months = 0
    for exp in experience:
        months = exp.get("duration_months")
        if isinstance(months, (int, float)):
            total_months += months
    return round(total_months / 12, 2) if total_months else 0.0


class MultiAIResumeParser:
    """Advanced resume parser using multiple AI services for maximum accuracy"""

    def __init__(self):
        self.gpt_client = None
        self.gemini_model = None
        self.claude_client = None
        
        # Initialize available AI services
        if OPENAI_AVAILABLE:
            from openai import OpenAI
            self.gpt_client = OpenAI(api_key=OPENAI_API_KEY)
        
        if GEMINI_PRO_AVAILABLE:
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        if ANTHROPIC_AVAILABLE:
            self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def parse_resume_with_multi_ai(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume using multiple AI services for consensus and accuracy"""
        logger.info("🤖 Starting multi-AI resume parsing...")
        
        results = []
        parsing_methods = []
        
        # Parse with GPT-4
        if OPENAI_AVAILABLE and self.gpt_client:
            try:
                logger.info("🔵 Parsing with GPT-4...")
                gpt_result = self._parse_with_gpt4(resume_text)
                if gpt_result and 'error' not in gpt_result:
                    results.append(('gpt4', gpt_result))
                    parsing_methods.append('GPT-4')
                    logger.info("✅ GPT-4 parsing successful")
            except Exception as e:
                logger.warning(f"⚠️ GPT-4 parsing failed: {e}")
        
        # Parse with Gemini Pro
        if GEMINI_PRO_AVAILABLE and self.gemini_model:
            try:
                logger.info("🟡 Parsing with Gemini Pro...")
                gemini_result = self._parse_with_gemini_pro(resume_text)
                if gemini_result and 'error' not in gemini_result:
                    results.append(('gemini_pro', gemini_result))
                    parsing_methods.append('Gemini Pro')
                    logger.info("✅ Gemini Pro parsing successful")
            except Exception as e:
                logger.warning(f"⚠️ Gemini Pro parsing failed: {e}")
        
        # Parse with Claude (if available)
        if ANTHROPIC_AVAILABLE and self.claude_client:
            try:
                logger.info("🟣 Parsing with Claude...")
                claude_result = self._parse_with_claude(resume_text)
                if claude_result and 'error' not in claude_result:
                    results.append(('claude', claude_result))
                    parsing_methods.append('Claude')
                    logger.info("✅ Claude parsing successful")
            except Exception as e:
                logger.warning(f"⚠️ Claude parsing failed: {e}")
        
        # Merge and validate results
        if results:
            final_result = self._merge_ai_results(results)
            final_result['parsing_methods'] = parsing_methods
            final_result['confidence_score'] = len(results) * 25  # Higher confidence with more AI services
            logger.info(f"🎯 Multi-AI parsing completed with {len(results)} services")
            return final_result
        else:
            logger.error("❌ All AI parsing methods failed")
            return {'error': 'All AI parsing methods failed'}

    def _parse_with_gpt4(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume using GPT-4"""
        prompt = self._get_enhanced_parsing_prompt(resume_text)
        
        try:
            response = self.gpt_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert resume parser and career analyst. Extract information with maximum accuracy and provide intelligent insights. Always return valid JSON without any markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8000
            )
            
            result_text = response.choices[0].message.content
            return self._parse_json_response(result_text)
            
        except Exception as e:
            logger.error(f"GPT-4 parsing error: {e}")
            return {'error': f'GPT-4 parsing failed: {str(e)}'}

    def _parse_with_gemini_pro(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume using Gemini Pro"""
        prompt = self._get_enhanced_parsing_prompt(resume_text)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            if response and response.text:
                return self._parse_json_response(response.text)
            else:
                return {'error': 'Gemini Pro returned empty response'}
                
        except Exception as e:
            logger.error(f"Gemini Pro parsing error: {e}")
            return {'error': f'Gemini Pro parsing failed: {str(e)}'}

    def _parse_with_claude(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume using Claude"""
        if not ANTHROPIC_AVAILABLE:
            return {'error': 'Claude not available'}
            
        prompt = self._get_enhanced_parsing_prompt(resume_text)
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return self._parse_json_response(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Claude parsing error: {e}")
            return {'error': f'Claude parsing failed: {str(e)}'}

    def _get_enhanced_parsing_prompt(self, resume_text: str) -> str:
        """Get enhanced parsing prompt for AI models"""
        return f"""
        Analyze this resume with expert-level precision and extract ALL available information.
        
        RESUME TEXT:
        {resume_text}
        
        CRITICAL PARSING REQUIREMENTS:
        1. PERSONAL INFO: Extract name, email, phone, location, LinkedIn, GitHub, portfolio, visa status
        2. EXPERIENCE ANALYSIS: Calculate exact years/months of experience, identify seniority level, promotion patterns
        3. SKILLS INTELLIGENCE: Extract ALL skills (technical, soft, tools, frameworks, languages, cloud platforms)
        4. JOB TITLE INTELLIGENCE: Identify current role, career progression, relevant job titles, industry transitions  
        5. EDUCATION: Extract degrees, institutions, dates, GPA, relevant coursework, certifications, bootcamps
        6. PROJECTS: Identify personal/professional projects with technologies, impact metrics, team sizes
        7. ACHIEVEMENTS: Quantify accomplishments (percentages, dollar amounts, team sizes, performance metrics)
        8. CAREER INSIGHTS: Analyze career trajectory, specializations, industry focus, remote work experience
        
        INTELLIGENT ENHANCEMENTS:
        - Infer relevant job titles based on experience and skills matching current market demands
        - Calculate leadership experience and team management background with concrete examples
        - Identify technical proficiency levels for each skill based on years of experience and project complexity
        - Determine accurate salary range based on experience, skills, location, and current market rates
        - Analyze industry specialization and domain expertise with transferable skills identification
        - Detect career gaps and provide context (education, sabbatical, startup, etc.)
        - Identify potential career growth paths and skill gaps for target roles
        - Extract soft skills from achievement descriptions and leadership examples
        
        Return ONLY valid JSON in this exact structure:
        {{
            "personal_info": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "+1234567890",
                "location": "City, State/Country",
                "linkedin": "linkedin.com/in/username",
                "github": "github.com/username",
                "portfolio": "website.com"
            }},
            "career_analysis": {{
                "current_role": "Current Job Title",
                "seniority_level": "Junior/Mid/Senior/Staff/Principal/Executive",
                "years_of_experience": 5.5,
                "career_progression": ["Previous roles in chronological order"],
                "relevant_job_titles": ["Software Engineer", "Full Stack Developer", "Backend Engineer"],
                "leadership_experience": true,
                "management_experience": 2.5,
                "industry_specialization": ["FinTech", "Healthcare", "E-commerce"]
            }},
            "skills_analysis": {{
                "technical_skills": {{
                    "programming_languages": [
                        {{"skill": "Python", "proficiency": "Expert", "years": 5}},
                        {{"skill": "JavaScript", "proficiency": "Advanced", "years": 4}}
                    ],
                    "frameworks": [
                        {{"skill": "React", "proficiency": "Expert", "years": 3}},
                        {{"skill": "Django", "proficiency": "Advanced", "years": 4}}
                    ],
                    "tools": [
                        {{"skill": "Docker", "proficiency": "Advanced", "years": 3}},
                        {{"skill": "AWS", "proficiency": "Intermediate", "years": 2}}
                    ]
                }},
                "soft_skills": ["Leadership", "Communication", "Problem Solving"],
                "certifications": ["AWS Certified", "Google Cloud Professional"]
            }},
            "experience": [
                {{
                    "title": "Senior Software Engineer",
                    "company": "TechCorp Inc",
                    "location": "San Francisco, CA",
                    "duration": "Jan 2020 - Present",
                    "duration_months": 48,
                    "responsibilities": ["Led team of 5 engineers", "Architected microservices"],
                    "achievements": ["Improved performance by 40%", "Reduced costs by $2M annually"],
                    "technologies": ["Python", "React", "AWS", "Docker"],
                    "team_size": 5,
                    "is_leadership_role": true
                }}
            ],
            "education": [
                {{
                    "degree": "Master of Science in Computer Science",
                    "institution": "Stanford University",
                    "location": "Stanford, CA",
                    "graduation_date": "2018",
                    "gpa": "3.8/4.0",
                    "relevant_coursework": ["Machine Learning", "Distributed Systems"]
                }}
            ],
            "projects": [
                {{
                    "name": "E-commerce Platform",
                    "description": "Full-stack web application with 10k+ users",
                    "technologies": ["React", "Node.js", "MongoDB"],
                    "url": "github.com/user/project",
                    "impact": "Increased sales by 30%"
                }}
            ],
            "salary_estimate": {{
                "min": 120000,
                "max": 180000,
                "currency": "USD",
                "factors": ["5+ years experience", "Senior level", "Tech skills"]
            }},
            "job_search_insights": {{
                "target_companies": ["Google", "Microsoft", "Amazon", "Netflix"],
                "preferred_locations": ["San Francisco", "Seattle", "Remote"],
                "career_goals": "Technical Leadership, Staff Engineer, Engineering Manager",
                "strengths": ["Full-stack development", "Team leadership", "System design"],
                "growth_areas": ["Machine Learning", "DevOps", "Product Strategy"]
            }}
        }}
        """

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from AI models with robust error handling"""
        try:
            # Clean up response text
            response_text = response_text.strip()
            
            # Multiple JSON extraction strategies
            json_str = None
            
            # Strategy 1: Find JSON content between ```json and ```
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            
            # Strategy 2: Find content between ``` (without json specifier)
            if not json_str:
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
            
            # Strategy 3: Look for JSON object starting with { and ending with }
            if not json_str:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
            
            # Strategy 4: Use entire response as fallback
            if not json_str:
                json_str = response_text
            
            # Clean up common JSON formatting issues
            json_str = json_str.replace('```', '').replace('json', '', 1).strip()
            
            # Fix common JSON issues
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate result structure
            if not isinstance(result, dict):
                return {'error': 'Response is not a valid JSON object'}
            
            # Ensure required top-level keys exist
            required_keys = ['personal_info', 'career_analysis', 'skills_analysis']
            for key in required_keys:
                if key not in result:
                    result[key] = {}
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Failed JSON string: {json_str[:500] if json_str else 'None'}...")
            
            # Try to extract partial information using regex fallback
            return self._fallback_text_parsing(response_text)
            
        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return {'error': f'Response parsing failed: {str(e)}'}
    
    def _fallback_text_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback text parsing when JSON fails"""
        logger.info("🔧 Attempting fallback text parsing...")
        
        result = {
            'personal_info': {},
            'career_analysis': {},
            'skills_analysis': {'technical_skills': [], 'soft_skills': []},
            'experience': [],
            'education': [],
            'fallback_parsing': True
        }
        
        # Extract email using regex
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response_text)
        if email_match:
            result['personal_info']['email'] = email_match.group(0)
        
        # Extract phone number
        phone_match = re.search(r'[\+]?[1-9]?[0-9]{7,15}', response_text)
        if phone_match:
            result['personal_info']['phone'] = phone_match.group(0)
        
        # Extract years of experience
        exp_match = re.search(r'(\d+(?:\.\d+)?)\s*years?\s*(?:of\s*)?experience', response_text, re.IGNORECASE)
        if exp_match:
            result['career_analysis']['years_of_experience'] = float(exp_match.group(1))
        
        logger.info("⚠️ Used fallback parsing - results may be limited")
        return result

    def _merge_ai_results(self, results: List[tuple]) -> Dict[str, Any]:
        """Merge results from multiple AI services for best accuracy"""
        logger.info(f"🔗 Merging results from {len(results)} AI services...")
        
        if not results:
            return {'error': 'No results to merge'}
        
        # Start with the first result as base
        merged = results[0][1].copy()
        
        # Merge additional results with consensus logic
        for ai_name, result in results[1:]:
            try:
                # Personal info - use most complete
                if 'personal_info' in result:
                    self._merge_personal_info(merged.setdefault('personal_info', {}), result['personal_info'])
                
                # Career analysis - use highest confidence
                if 'career_analysis' in result:
                    self._merge_career_analysis(merged.setdefault('career_analysis', {}), result['career_analysis'])
                
                # Skills - merge all unique skills
                if 'skills_analysis' in result:
                    self._merge_skills_analysis(merged.setdefault('skills_analysis', {}), result['skills_analysis'])
                
                # Experience - use most detailed
                if 'experience' in result and len(result['experience']) > len(merged.get('experience', [])):
                    merged['experience'] = result['experience']
                
                # Education - merge all institutions
                if 'education' in result:
                    self._merge_education(merged.setdefault('education', []), result['education'])
                
                # Projects - merge unique projects
                if 'projects' in result:
                    self._merge_projects(merged.setdefault('projects', []), result['projects'])

            except Exception as e:
                logger.warning(f"Error merging {ai_name} results: {e}")

        # Ensure experience years are calculated if missing
        career = merged.setdefault('career_analysis', {})
        if not career.get('years_of_experience') and merged.get('experience'):
            career['years_of_experience'] = calculate_total_experience(merged['experience'])

        # Add metadata
        merged['parsed_with'] = 'multi_ai_enhanced'
        merged['parsing_timestamp'] = datetime.now().isoformat()
        merged['ai_services_used'] = [name for name, _ in results]

        logger.info("✅ Multi-AI merge completed successfully")
        return merged

    def _merge_personal_info(self, base: Dict, new: Dict):
        """Merge personal information, preferring non-empty values"""
        for key, value in new.items():
            if value and (not base.get(key) or len(str(value)) > len(str(base.get(key, '')))):
                base[key] = value

    def _merge_career_analysis(self, base: Dict, new: Dict):
        """Merge career analysis data"""
        # Use new values if they're more detailed or base is empty
        for key, value in new.items():
            if key == 'relevant_job_titles':
                # Merge unique job titles
                base_titles = set(base.get(key, []))
                new_titles = set(value) if isinstance(value, list) else set()
                base[key] = list(base_titles.union(new_titles))
            elif key == 'years_of_experience' and isinstance(value, (int, float)):
                # Use higher experience value
                base[key] = max(base.get(key, 0), value)
            elif value and not base.get(key):
                base[key] = value

    def _merge_skills_analysis(self, base: Dict, new: Dict):
        """Merge skills analysis with deduplication"""
        for category, skills in new.items():
            if category not in base:
                base[category] = skills
            elif isinstance(skills, list):
                # Merge lists and remove duplicates
                existing = set(base[category]) if isinstance(base[category], list) else set()
                new_skills = set(skills)
                base[category] = list(existing.union(new_skills))
            elif isinstance(skills, dict):
                # Merge skill dictionaries
                if category not in base:
                    base[category] = {}
                for skill_type, skill_list in skills.items():
                    if skill_type not in base[category]:
                        base[category][skill_type] = skill_list
                    elif isinstance(skill_list, list):
                        existing = base[category][skill_type] if isinstance(base[category][skill_type], list) else []
                        base[category][skill_type] = existing + [s for s in skill_list if s not in existing]

    def _merge_education(self, base: List, new: List):
        """Merge education entries"""
        existing_institutions = {edu.get('institution', '').lower() for edu in base}
        for edu in new:
            if edu.get('institution', '').lower() not in existing_institutions:
                base.append(edu)

    def _merge_projects(self, base: List, new: List):
        """Merge project entries"""
        existing_projects = {proj.get('name', '').lower() for proj in base}
        for proj in new:
            if proj.get('name', '').lower() not in existing_projects:
                base.append(proj)


# Global instance
multi_ai_parser = MultiAIResumeParser()

def parse_resume_with_multi_ai(resume_text: str) -> Dict[str, Any]:
    """Main function to parse resume with multiple AI services"""
    return multi_ai_parser.parse_resume_with_multi_ai(resume_text)

# Example usage
if __name__ == "__main__":
    sample_resume = """
    John Doe
    Senior Software Engineer
    john.doe@gmail.com | (555) 123-4567
    San Francisco, CA | linkedin.com/in/johndoe | github.com/johndoe
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 6+ years of experience in full-stack development, 
    leading teams, and architecting scalable solutions. Expert in Python, React, and AWS.
    
    EXPERIENCE
    Senior Software Engineer | TechCorp Inc | Jan 2020 - Present
    • Led a team of 5 engineers to develop microservices architecture
    • Improved system performance by 40% and reduced costs by $2M annually
    • Technologies: Python, React, AWS, Docker, Kubernetes
    
    Software Engineer | StartupXYZ | Jun 2018 - Dec 2019
    • Built full-stack web applications serving 50k+ users
    • Implemented CI/CD pipelines reducing deployment time by 60%
    • Technologies: JavaScript, Node.js, MongoDB, Jenkins
    
    EDUCATION
    Master of Science in Computer Science | Stanford University | 2018
    Bachelor of Science in Computer Science | UC Berkeley | 2016
    
    SKILLS
    Programming: Python, JavaScript, TypeScript, Java, Go
    Frameworks: React, Django, Express.js, Spring Boot
    Cloud: AWS, Google Cloud, Docker, Kubernetes
    Databases: PostgreSQL, MongoDB, Redis
    """
    
    result = parse_resume_with_multi_ai(sample_resume)
    print(json.dumps(result, indent=2))