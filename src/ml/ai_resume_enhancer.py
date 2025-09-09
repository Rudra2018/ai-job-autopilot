#!/usr/bin/env python3
"""
AI Resume Enhancer
Uses AI to enhance, analyze, and optimize parsed resume data for job matching
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import asyncio

# Import our enhanced resume parser
from src.core.enhanced_resume_parser import ParsedResume, EnhancedResumeParser

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Import multi-AI service
try:
    from src.ml.multi_ai_service import MultiAIService, enhance_resume_with_ai
    HAS_MULTI_AI = True
except ImportError:
    HAS_MULTI_AI = False

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    # Mock numpy for type hints
    class np:
        ndarray = None

@dataclass
class ResumeAnalysis:
    """AI analysis results for a resume"""
    overall_score: float = 0.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    ats_compatibility: float = 0.0
    estimated_experience_level: str = ""
    suitable_roles: List[str] = field(default_factory=list)
    skill_gaps: List[str] = field(default_factory=list)

@dataclass  
class JobMatchScore:
    """Job matching analysis"""
    overall_match: float = 0.0
    skill_match: float = 0.0
    experience_match: float = 0.0
    education_match: float = 0.0
    keyword_match: float = 0.0
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    matching_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnhancedResumeData:
    """Enhanced resume with AI analysis"""
    original_resume: ParsedResume = None
    analysis: ResumeAnalysis = field(default_factory=ResumeAnalysis)
    enhanced_summary: str = ""
    optimized_skills: List[str] = field(default_factory=list)
    suggested_improvements: Dict[str, str] = field(default_factory=dict)
    embeddings: Optional[np.ndarray] = None
    processing_metadata: Dict[str, Any] = field(default_factory=dict)

class AIResumeEnhancer:
    """AI-powered resume analysis and enhancement"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Multi-AI service if available
        if HAS_MULTI_AI:
            self.multi_ai_service = MultiAIService()
            self.ai_available = len(self.multi_ai_service.get_available_services()) > 0
        else:
            self.multi_ai_service = None
            self.ai_available = False
        
        # Legacy OpenAI support
        self.has_openai = HAS_OPENAI
        if HAS_OPENAI and openai_api_key:
            openai.api_key = openai_api_key
            self.openai_available = True
        else:
            self.openai_available = False
            
        # Initialize embeddings model if available
        self.embedding_model = None
        if HAS_EMBEDDINGS:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Loaded sentence transformer model")
            except Exception as e:
                self.logger.warning(f"Could not load embedding model: {e}")
        
        # Industry keywords and skills database
        self.skill_categories = self._load_skill_categories()
        self.industry_keywords = self._load_industry_keywords()
        
    def _load_skill_categories(self) -> Dict[str, List[str]]:
        """Load categorized skills database"""
        return {
            "programming": [
                "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
                "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL"
            ],
            "web_development": [
                "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express",
                "Django", "Flask", "Spring", "ASP.NET", "Laravel", "Next.js", "Nuxt.js"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "Data Analysis", "Statistics",
                "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
                "Jupyter", "Matplotlib", "Seaborn", "Tableau", "Power BI"
            ],
            "cloud_devops": [
                "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
                "Git", "CI/CD", "Terraform", "Ansible", "Linux", "Bash", "Monitoring"
            ],
            "mobile": [
                "iOS", "Android", "React Native", "Flutter", "Xamarin", "Swift",
                "Kotlin", "Objective-C", "Mobile UI/UX"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
                "SQL Server", "Cassandra", "ElasticSearch", "Neo4j"
            ]
        }
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keywords"""
        return {
            "technology": [
                "software development", "agile", "scrum", "microservices", "api",
                "automation", "testing", "debugging", "version control", "architecture"
            ],
            "data": [
                "analytics", "visualization", "modeling", "algorithms", "big data",
                "etl", "data pipeline", "business intelligence", "reporting"
            ],
            "management": [
                "leadership", "team management", "project management", "strategic planning",
                "stakeholder management", "budget management", "performance optimization"
            ]
        }
    
    def enhance_resume(self, resume: ParsedResume, target_job: Optional[str] = None) -> EnhancedResumeData:
        """Enhance resume with AI analysis (sync version)"""
        self.logger.info("Starting AI resume enhancement")
        
        enhanced_data = EnhancedResumeData()
        enhanced_data.original_resume = resume
        
        try:
            # Analyze resume
            enhanced_data.analysis = self._analyze_resume(resume)
            
            # Enhance summary if AI is available (sync version)
            if self.openai_available:
                enhanced_data.enhanced_summary = self._enhance_summary(resume, target_job)
            
            # Optimize skills
            enhanced_data.optimized_skills = self._optimize_skills(resume)
            
            # Generate improvement suggestions
            enhanced_data.suggested_improvements = self._generate_improvements(resume, enhanced_data.analysis)
            
            # Generate embeddings if model is available
            if self.embedding_model:
                enhanced_data.embeddings = self._generate_embeddings(resume)
            
            # Add processing metadata
            enhanced_data.processing_metadata = {
                "processing_time": datetime.now().isoformat(),
                "ai_features_used": {
                    "openai": self.openai_available,
                    "embeddings": self.embedding_model is not None
                },
                "target_job": target_job
            }
            
            self.logger.info("Resume enhancement completed successfully")
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Resume enhancement failed: {e}")
            enhanced_data.processing_metadata["error"] = str(e)
            return enhanced_data
    
    def _analyze_resume(self, resume: ParsedResume) -> ResumeAnalysis:
        """Analyze resume and generate insights"""
        analysis = ResumeAnalysis()
        
        # Calculate overall score based on completeness and quality
        analysis.overall_score = self._calculate_resume_score(resume)
        
        # Analyze strengths
        analysis.strengths = self._identify_strengths(resume)
        
        # Identify weaknesses
        analysis.weaknesses = self._identify_weaknesses(resume)
        
        # Generate improvement suggestions
        analysis.improvement_suggestions = self._generate_improvement_suggestions(resume)
        
        # Identify missing keywords
        analysis.missing_keywords = self._find_missing_keywords(resume)
        
        # Calculate ATS compatibility
        analysis.ats_compatibility = self._calculate_ats_compatibility(resume)
        
        # Estimate experience level
        analysis.estimated_experience_level = self._estimate_experience_level(resume)
        
        # Suggest suitable roles
        analysis.suitable_roles = self._suggest_suitable_roles(resume)
        
        # Identify skill gaps
        analysis.skill_gaps = self._identify_skill_gaps(resume)
        
        return analysis
    
    def _calculate_resume_score(self, resume: ParsedResume) -> float:
        """Calculate overall resume score"""
        score = 0.0
        
        # Contact information (20%)
        contact_score = 0.0
        if resume.contact_info.name:
            contact_score += 0.3
        if resume.contact_info.email:
            contact_score += 0.3
        if resume.contact_info.phone:
            contact_score += 0.2
        if resume.contact_info.linkedin:
            contact_score += 0.2
        score += contact_score * 0.2
        
        # Work experience (30%)
        if resume.work_experience:
            exp_score = min(len(resume.work_experience) * 0.3, 1.0)
            # Bonus for detailed descriptions
            avg_desc_length = sum(len(' '.join(exp.description)) for exp in resume.work_experience) / len(resume.work_experience)
            if avg_desc_length > 100:
                exp_score += 0.2
            score += min(exp_score, 1.0) * 0.3
        
        # Education (15%)
        if resume.education:
            score += min(len(resume.education) * 0.5, 1.0) * 0.15
        
        # Skills (20%)
        if resume.skills:
            skills_score = min(len(resume.skills) * 0.1, 1.0)
            score += skills_score * 0.2
        
        # Summary (10%)
        if resume.summary and len(resume.summary) > 50:
            score += 0.1
        
        # Additional sections (5%)
        bonus_score = 0.0
        if resume.projects:
            bonus_score += 0.02
        if resume.certifications:
            bonus_score += 0.02
        if resume.achievements:
            bonus_score += 0.01
        score += min(bonus_score, 0.05)
        
        return min(score, 1.0)
    
    def _identify_strengths(self, resume: ParsedResume) -> List[str]:
        """Identify resume strengths"""
        strengths = []
        
        if len(resume.work_experience) >= 3:
            strengths.append("Strong work experience with multiple roles")
        
        if resume.education and any('master' in edu.degree.lower() or 'phd' in edu.degree.lower() 
                                  for edu in resume.education if edu.degree):
            strengths.append("Advanced degree demonstrates commitment to learning")
        
        if len(resume.skills) >= 10:
            strengths.append("Comprehensive technical skills")
        
        if resume.certifications:
            strengths.append("Professional certifications validate expertise")
        
        if resume.projects:
            strengths.append("Personal/side projects show initiative and passion")
        
        if resume.contact_info.linkedin and resume.contact_info.github:
            strengths.append("Strong online professional presence")
        
        # Check for leadership indicators
        leadership_keywords = ["led", "managed", "directed", "supervised", "coordinated"]
        experience_text = " ".join(
            " ".join(exp.description) for exp in resume.work_experience
        ).lower()
        
        if any(keyword in experience_text for keyword in leadership_keywords):
            strengths.append("Demonstrates leadership experience")
        
        return strengths
    
    def _identify_weaknesses(self, resume: ParsedResume) -> List[str]:
        """Identify resume weaknesses"""
        weaknesses = []
        
        if not resume.contact_info.email:
            weaknesses.append("Missing email contact information")
        
        if not resume.contact_info.phone:
            weaknesses.append("Missing phone contact information")
        
        if not resume.summary or len(resume.summary) < 50:
            weaknesses.append("Missing or insufficient professional summary")
        
        if len(resume.work_experience) < 2:
            weaknesses.append("Limited work experience")
        
        if not resume.education:
            weaknesses.append("No education information provided")
        
        if len(resume.skills) < 5:
            weaknesses.append("Limited technical skills listed")
        
        # Check for employment gaps
        if self._has_employment_gaps(resume):
            weaknesses.append("Potential employment gaps detected")
        
        # Check for outdated skills
        outdated_skills = self._find_outdated_skills(resume.skills)
        if outdated_skills:
            weaknesses.append(f"Some outdated technologies: {', '.join(outdated_skills)}")
        
        return weaknesses
    
    def _generate_improvement_suggestions(self, resume: ParsedResume) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if not resume.summary:
            suggestions.append("Add a compelling professional summary highlighting your key achievements")
        
        if not resume.contact_info.linkedin:
            suggestions.append("Include your LinkedIn profile URL")
        
        # Analyze description quality
        for exp in resume.work_experience:
            if not exp.description or len(exp.description) < 2:
                suggestions.append(f"Add more detailed description for {exp.position} role")
        
        if not resume.projects:
            suggestions.append("Consider adding relevant projects to showcase your skills")
        
        if not resume.certifications:
            suggestions.append("Consider adding professional certifications relevant to your field")
        
        # Skills improvement
        skill_categories_found = self._categorize_skills(resume.skills)
        if len(skill_categories_found) < 3:
            suggestions.append("Diversify your skill set across different technology categories")
        
        return suggestions
    
    def _find_missing_keywords(self, resume: ParsedResume) -> List[str]:
        """Find missing industry keywords"""
        missing_keywords = []
        
        # Get all text from resume
        resume_text = self._get_resume_text(resume).lower()
        
        # Check for common industry keywords
        for industry, keywords in self.industry_keywords.items():
            found_keywords = [kw for kw in keywords if kw.lower() in resume_text]
            missing_from_industry = [kw for kw in keywords if kw.lower() not in resume_text]
            
            if len(found_keywords) > 0 and len(missing_from_industry) > 0:
                # If some keywords from industry found, suggest related missing ones
                missing_keywords.extend(missing_from_industry[:3])  # Limit to top 3
        
        return missing_keywords[:10]  # Limit total suggestions
    
    def _calculate_ats_compatibility(self, resume: ParsedResume) -> float:
        """Calculate ATS (Applicant Tracking System) compatibility score"""
        score = 0.0
        
        # Contact info in standard format
        if resume.contact_info.email and '@' in resume.contact_info.email:
            score += 0.15
        if resume.contact_info.phone:
            score += 0.15
        
        # Standard section headers
        sections_score = len(resume.sections_found) / 7  # Assuming 7 main sections
        score += sections_score * 0.2
        
        # Skills section present
        if resume.skills:
            score += 0.2
        
        # Work experience with dates
        if resume.work_experience:
            dated_experience = sum(1 for exp in resume.work_experience 
                                 if exp.start_date or exp.end_date)
            score += (dated_experience / len(resume.work_experience)) * 0.2
        
        # Education information
        if resume.education:
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_experience_level(self, resume: ParsedResume) -> str:
        """Estimate experience level"""
        if not resume.work_experience:
            return "Entry Level"
        
        experience_count = len(resume.work_experience)
        
        # Try to estimate years of experience
        total_years = 0
        current_year = datetime.now().year
        
        for exp in resume.work_experience:
            if exp.start_date and exp.end_date:
                try:
                    # Simple year extraction
                    start_year = int(re.search(r'20\d{2}|19\d{2}', exp.start_date).group())
                    if exp.end_date.lower() in ['present', 'current']:
                        end_year = current_year
                    else:
                        end_year = int(re.search(r'20\d{2}|19\d{2}', exp.end_date).group())
                    total_years += max(0, end_year - start_year)
                except:
                    pass
        
        if total_years == 0:
            # Fall back to counting positions
            if experience_count >= 4:
                return "Senior Level"
            elif experience_count >= 2:
                return "Mid Level"
            else:
                return "Entry Level"
        
        if total_years >= 8:
            return "Senior Level"
        elif total_years >= 3:
            return "Mid Level"
        else:
            return "Entry Level"
    
    def _suggest_suitable_roles(self, resume: ParsedResume) -> List[str]:
        """Suggest suitable job roles based on skills and experience"""
        roles = []
        
        # Analyze skills to determine potential roles
        skills_text = " ".join(resume.skills).lower()
        
        # Technical roles
        if any(skill in skills_text for skill in ['python', 'java', 'javascript', 'programming']):
            roles.append("Software Developer")
            
        if any(skill in skills_text for skill in ['react', 'angular', 'html', 'css']):
            roles.append("Frontend Developer")
            
        if any(skill in skills_text for skill in ['node.js', 'django', 'flask', 'api']):
            roles.append("Backend Developer")
            
        if any(skill in skills_text for skill in ['machine learning', 'data science', 'pandas', 'tensorflow']):
            roles.append("Data Scientist")
            
        if any(skill in skills_text for skill in ['aws', 'docker', 'kubernetes', 'devops']):
            roles.append("DevOps Engineer")
            
        # Management roles based on experience
        experience_text = " ".join(
            " ".join(exp.description) for exp in resume.work_experience
        ).lower()
        
        if any(word in experience_text for word in ['managed', 'led', 'directed', 'supervised']):
            roles.append("Technical Lead")
            roles.append("Engineering Manager")
        
        return roles[:5]  # Limit to top 5 suggestions
    
    def _identify_skill_gaps(self, resume: ParsedResume) -> List[str]:
        """Identify skill gaps based on current trends"""
        gaps = []
        
        current_skills = [skill.lower() for skill in resume.skills]
        
        # Check for modern tech stack gaps
        if not any(skill in current_skills for skill in ['docker', 'kubernetes', 'containerization']):
            gaps.append("Container technologies (Docker, Kubernetes)")
            
        if not any(skill in current_skills for skill in ['aws', 'azure', 'gcp', 'cloud']):
            gaps.append("Cloud platforms (AWS, Azure, GCP)")
            
        if not any(skill in current_skills for skill in ['git', 'version control']):
            gaps.append("Version control systems")
            
        if not any(skill in current_skills for skill in ['agile', 'scrum']):
            gaps.append("Agile methodologies")
            
        if not any(skill in current_skills for skill in ['testing', 'unit testing', 'tdd']):
            gaps.append("Testing frameworks and methodologies")
        
        return gaps[:5]
    
    def _has_employment_gaps(self, resume: ParsedResume) -> bool:
        """Check for employment gaps"""
        # Simple implementation - could be enhanced
        if len(resume.work_experience) < 2:
            return False
            
        # This is a simplified check - a real implementation would parse dates properly
        return False
    
    def _find_outdated_skills(self, skills: List[str]) -> List[str]:
        """Find potentially outdated skills"""
        outdated = []
        outdated_tech = ['flash', 'silverlight', 'internet explorer', 'vb6', 'perl', 'cobol']
        
        for skill in skills:
            if skill.lower() in outdated_tech:
                outdated.append(skill)
                
        return outdated
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different domains"""
        categorized = {}
        skills_lower = [skill.lower() for skill in skills]
        
        for category, category_skills in self.skill_categories.items():
            found_skills = []
            for skill in skills:
                if skill.lower() in [cs.lower() for cs in category_skills]:
                    found_skills.append(skill)
            if found_skills:
                categorized[category] = found_skills
                
        return categorized
    
    def _get_resume_text(self, resume: ParsedResume) -> str:
        """Get all text content from resume"""
        text_parts = []
        
        if resume.summary:
            text_parts.append(resume.summary)
            
        for exp in resume.work_experience:
            text_parts.extend(exp.description)
            
        text_parts.extend(resume.skills)
        
        return " ".join(text_parts)
    
    def _enhance_summary(self, resume: ParsedResume, target_job: Optional[str] = None) -> str:
        """Use AI to enhance professional summary"""
        if not self.openai_available:
            return resume.summary
            
        try:
            prompt = self._create_summary_enhancement_prompt(resume, target_job)
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"AI summary enhancement failed: {e}")
            return resume.summary
    
    def _create_summary_enhancement_prompt(self, resume: ParsedResume, target_job: Optional[str]) -> str:
        """Create prompt for AI summary enhancement"""
        context = f"""
        Based on this resume information, create a compelling professional summary:
        
        Experience: {len(resume.work_experience)} roles
        Skills: {', '.join(resume.skills[:10])}
        Education: {resume.education[0].degree if resume.education else 'Not specified'}
        Current Summary: {resume.summary or 'None provided'}
        """
        
        if target_job:
            context += f"\nTarget Job: {target_job}"
            
        prompt = context + """
        
        Create a concise, impactful professional summary (2-3 sentences) that:
        1. Highlights key strengths and experience level
        2. Mentions relevant skills
        3. Shows value proposition to employers
        4. Is ATS-friendly with industry keywords
        
        Professional Summary:"""
        
        return prompt
    
    def _optimize_skills(self, resume: ParsedResume) -> List[str]:
        """Optimize and enhance skills list"""
        optimized = set(resume.skills)
        
        # Group related skills
        skills_text = " ".join(resume.skills).lower()
        
        # Add missing related skills
        if 'python' in skills_text and 'pandas' not in skills_text:
            optimized.add('Pandas')
            
        if 'javascript' in skills_text and 'node.js' not in skills_text:
            optimized.add('Node.js')
            
        # Remove duplicates and variations
        final_skills = []
        skills_lower = set()
        
        for skill in optimized:
            skill_lower = skill.lower().strip()
            if skill_lower not in skills_lower:
                skills_lower.add(skill_lower)
                final_skills.append(skill.strip())
        
        return sorted(final_skills)
    
    def _generate_improvements(self, resume: ParsedResume, analysis: ResumeAnalysis) -> Dict[str, str]:
        """Generate specific improvement recommendations"""
        improvements = {}
        
        if analysis.overall_score < 0.7:
            improvements["overall"] = "Consider expanding work experience descriptions and adding more relevant skills"
            
        if not resume.summary:
            improvements["summary"] = "Add a compelling professional summary that highlights your expertise"
            
        if len(resume.skills) < 8:
            improvements["skills"] = "Expand your skills section with relevant technologies and tools"
            
        if analysis.ats_compatibility < 0.8:
            improvements["ats"] = "Improve ATS compatibility by using standard section headers and keyword optimization"
        
        return improvements
    
    async def enhance_resume_async(self, resume: ParsedResume, target_job: Optional[str] = None) -> EnhancedResumeData:
        """Async version of resume enhancement with multi-AI support"""
        self.logger.info("Starting async AI resume enhancement")
        
        enhanced_data = EnhancedResumeData()
        enhanced_data.original_resume = resume
        
        try:
            # Analyze resume
            enhanced_data.analysis = self._analyze_resume(resume)
            
            # Enhance summary with multi-AI service
            if self.ai_available and self.multi_ai_service:
                resume_dict = {
                    'contact_info': asdict(resume.contact_info),
                    'summary': resume.summary,
                    'work_experience': [asdict(exp) for exp in resume.work_experience],
                    'education': [asdict(edu) for edu in resume.education],
                    'skills': resume.skills
                }
                
                response = await self.multi_ai_service.enhance_resume_summary(resume_dict, target_job)
                if response.success:
                    enhanced_data.enhanced_summary = response.content
                    enhanced_data.processing_metadata["ai_provider"] = response.provider.value
                else:
                    enhanced_data.enhanced_summary = resume.summary
                    enhanced_data.processing_metadata["ai_error"] = response.error
            elif self.openai_available:
                enhanced_data.enhanced_summary = self._enhance_summary(resume, target_job)
            
            # Optimize skills
            enhanced_data.optimized_skills = self._optimize_skills(resume)
            
            # Generate improvement suggestions
            enhanced_data.suggested_improvements = self._generate_improvements(resume, enhanced_data.analysis)
            
            # Generate embeddings if model is available
            if self.embedding_model:
                enhanced_data.embeddings = self._generate_embeddings(resume)
            
            # Add processing metadata
            enhanced_data.processing_metadata.update({
                "processing_time": datetime.now().isoformat(),
                "ai_features_used": {
                    "multi_ai": self.ai_available,
                    "openai": self.openai_available,
                    "embeddings": self.embedding_model is not None
                },
                "target_job": target_job
            })
            
            self.logger.info("Async resume enhancement completed successfully")
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Async resume enhancement failed: {e}")
            enhanced_data.processing_metadata["error"] = str(e)
            return enhanced_data
    
    def _generate_embeddings(self, resume: ParsedResume) -> Optional[np.ndarray]:
        """Generate embeddings for resume content"""
        if not self.embedding_model:
            return None
            
        try:
            resume_text = self._get_resume_text(resume)
            embeddings = self.embedding_model.encode([resume_text])
            return embeddings[0]
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            return None
    
    def calculate_job_match(self, resume: ParsedResume, job_description: str) -> JobMatchScore:
        """Calculate how well a resume matches a job description"""
        match_score = JobMatchScore()
        
        resume_text = self._get_resume_text(resume).lower()
        job_text = job_description.lower()
        
        # Extract skills from job description
        job_skills = self._extract_skills_from_text(job_text)
        resume_skills = [skill.lower() for skill in resume.skills]
        
        # Calculate skill match
        matched_skills = [skill for skill in job_skills if skill.lower() in resume_skills]
        missing_skills = [skill for skill in job_skills if skill.lower() not in resume_skills]
        
        match_score.matched_skills = matched_skills
        match_score.missing_skills = missing_skills
        match_score.skill_match = len(matched_skills) / len(job_skills) if job_skills else 0.0
        
        # Simple keyword matching
        job_keywords = set(job_text.split())
        resume_keywords = set(resume_text.split())
        common_keywords = job_keywords.intersection(resume_keywords)
        
        match_score.keyword_match = len(common_keywords) / len(job_keywords) if job_keywords else 0.0
        
        # Overall match (weighted average)
        match_score.overall_match = (
            match_score.skill_match * 0.4 +
            match_score.keyword_match * 0.3 +
            0.3  # Base score for having a complete resume
        )
        
        return match_score
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        skills = set()
        
        # Check against known skills
        for category, category_skills in self.skill_categories.items():
            for skill in category_skills:
                if skill.lower() in text:
                    skills.add(skill)
        
        return list(skills)

# Convenience functions
def enhance_resume_from_pdf(pdf_path: str, openai_api_key: Optional[str] = None) -> EnhancedResumeData:
    """Complete pipeline: PDF -> Text -> Parse -> AI Enhancement"""
    # Parse resume
    parser = EnhancedResumeParser()
    resume = parser.parse_resume(pdf_path)
    
    # Enhance with AI
    enhancer = AIResumeEnhancer(openai_api_key)
    enhanced = enhancer.enhance_resume(resume)
    
    return enhanced

def analyze_resume_for_job(pdf_path: str, job_description: str, openai_api_key: Optional[str] = None) -> Tuple[EnhancedResumeData, JobMatchScore]:
    """Analyze resume against specific job description"""
    enhanced_data = enhance_resume_from_pdf(pdf_path, openai_api_key)
    
    enhancer = AIResumeEnhancer(openai_api_key)
    match_score = enhancer.calculate_job_match(enhanced_data.original_resume, job_description)
    
    return enhanced_data, match_score

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        resume_file = sys.argv[1]
        
        # Parse and enhance resume
        enhanced = enhance_resume_from_pdf(resume_file)
        
        print("=== Resume Analysis ===")
        print(f"Overall Score: {enhanced.analysis.overall_score:.2f}")
        print(f"ATS Compatibility: {enhanced.analysis.ats_compatibility:.2f}")
        print(f"Experience Level: {enhanced.analysis.estimated_experience_level}")
        
        print("\n=== Strengths ===")
        for strength in enhanced.analysis.strengths:
            print(f"• {strength}")
        
        print("\n=== Improvement Areas ===")
        for weakness in enhanced.analysis.weaknesses:
            print(f"• {weakness}")
        
        print("\n=== Suggested Roles ===")
        for role in enhanced.analysis.suitable_roles:
            print(f"• {role}")
            
    else:
        print("Usage: python ai_resume_enhancer.py <resume_file.pdf>")