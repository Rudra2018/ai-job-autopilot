#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Dynamic Resume Rewriting System
Automatically rewrites resumes to match specific job descriptions using AI
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import hashlib
import openai
import anthropic
import google.generativeai as genai
from dataclasses import dataclass, asdict
import PyPDF2
import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResumeVersion:
    job_title: str
    company: str
    original_resume_path: str
    optimized_resume_path: str
    job_description: str
    similarity_score: float
    keywords_added: List[str]
    sections_modified: List[str]
    creation_timestamp: str
    ai_provider: str

class DynamicResumeRewriter:
    def __init__(self, base_resume_path: str = "config/resume.pdf"):
        self.base_resume_path = Path(base_resume_path)
        self.output_dir = Path("data/optimized_resumes")
        self.output_dir.mkdir(exist_ok=True)
        
        self.versions_cache_path = Path("data/resume_versions.json")
        self.versions_cache = self._load_versions_cache()
        
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        self._initialize_ai_clients()
        
        # Initialize JobBERT for semantic similarity
        try:
            self.jobbert_model = SentenceTransformer('TechWolf/JobBERT-v3')
            logger.info("JobBERT model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load JobBERT model: {e}")
            self.jobbert_model = None
        
        # Resume sections and their importance weights
        self.section_weights = {
            "summary": 0.25,
            "experience": 0.35,
            "skills": 0.20,
            "education": 0.10,
            "projects": 0.10
        }
        
        # Common ATS keywords by category
        self.ats_keywords = {
            "technical_skills": [
                "Python", "JavaScript", "Java", "React", "Node.js", "AWS", "Docker", 
                "Kubernetes", "SQL", "MongoDB", "Git", "CI/CD", "Agile", "Scrum"
            ],
            "soft_skills": [
                "leadership", "communication", "problem-solving", "teamwork", 
                "analytical", "creative", "adaptable", "collaborative"
            ],
            "action_verbs": [
                "developed", "implemented", "designed", "optimized", "managed", 
                "led", "created", "improved", "automated", "delivered"
            ]
        }
    
    def _load_versions_cache(self) -> Dict:
        """Load resume versions cache"""
        try:
            if self.versions_cache_path.exists():
                with open(self.versions_cache_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading versions cache: {e}")
            return {}
    
    def _save_versions_cache(self):
        """Save resume versions cache"""
        try:
            with open(self.versions_cache_path, 'w') as f:
                json.dump(self.versions_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving versions cache: {e}")
    
    def _initialize_ai_clients(self):
        """Initialize AI clients for multiple providers"""
        try:
            # OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")
        
            # Anthropic
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Anthropic client initialized")
            
            # Google Gemini
            google_key = os.getenv("GOOGLE_API_KEY")
            if google_key:
                genai.configure(api_key=google_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("Google Gemini client initialized")
                
        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")
    
    def extract_resume_text(self, resume_path: Path) -> str:
        """Extract text from resume (PDF or DOCX)"""
        try:
            if resume_path.suffix.lower() == '.pdf':
                return self._extract_pdf_text(resume_path)
            elif resume_path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_docx_text(resume_path)
            else:
                logger.error(f"Unsupported resume format: {resume_path.suffix}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting resume text: {e}")
            return ""
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF resume"""
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\\n"
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
        
        try:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\\n"
                return text
        except Exception as e:
            logger.error(f"PyPDF2 also failed: {e}")
            return ""
    
    def _extract_docx_text(self, docx_path: Path) -> str:
        """Extract text from DOCX resume"""
        try:
            doc = Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""
    
    def analyze_job_description(self, job_description: str) -> Dict:
        """Analyze job description to extract key requirements"""
        
        # Extract keywords using simple heuristics
        keywords = []
        requirements = []
        
        # Common patterns for requirements
        req_patterns = [
            "required", "must have", "experience with", "proficient in",
            "knowledge of", "familiar with", "expertise in"
        ]
        
        lines = job_description.lower().split('\\n')
        for line in lines:
            for pattern in req_patterns:
                if pattern in line:
                    requirements.append(line.strip())
            
            # Extract potential keywords (common tech terms)
            for category, terms in self.ats_keywords.items():
                for term in terms:
                    if term.lower() in line and term not in keywords:
                        keywords.append(term)
        
        return {
            "keywords": keywords,
            "requirements": requirements,
            "length": len(job_description.split()),
            "key_phrases": self._extract_key_phrases(job_description)
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from job description"""
        # Simple key phrase extraction
        phrases = []
        
        # Look for common job-related phrases
        common_phrases = [
            "software development", "data analysis", "machine learning",
            "cloud computing", "web development", "database management",
            "project management", "team leadership", "agile methodology"
        ]
        
        text_lower = text.lower()
        for phrase in common_phrases:
            if phrase in text_lower:
                phrases.append(phrase)
        
        return phrases
    
    def calculate_resume_job_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity between resume and job description"""
        try:
            if not self.jobbert_model:
                return 0.5  # Default similarity if model not available
            
            # Generate embeddings
            resume_embedding = self.jobbert_model.encode([resume_text])
            job_embedding = self.jobbert_model.encode([job_description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.5
    
    def generate_optimized_resume_content(self, 
                                        original_resume: str, 
                                        job_description: str, 
                                        job_analysis: Dict) -> Dict:
        """Generate optimized resume content using AI"""
        
        prompt = f"""
You are an expert ATS-optimized resume writer. Your task is to rewrite a resume to better match a specific job description while maintaining truthfulness and authenticity.

ORIGINAL RESUME:
{original_resume[:2000]}...

JOB DESCRIPTION:
{job_description[:1500]}...

KEY REQUIREMENTS IDENTIFIED:
{', '.join(job_analysis.get('keywords', [])[:15])}

INSTRUCTIONS:
1. Rewrite the resume to better align with the job requirements
2. Incorporate relevant keywords naturally (don't keyword stuff)
3. Emphasize experience and skills that match the job
4. Improve ATS readability with clear formatting
5. Maintain truthfulness - only enhance existing experience
6. Use strong action verbs and quantifiable achievements
7. Optimize the summary/objective section for this specific role

SECTIONS TO OPTIMIZE:
- Professional Summary (2-3 lines, role-specific)
- Key Skills (prioritize job-relevant skills)
- Work Experience (emphasize relevant responsibilities)
- Projects (highlight applicable projects)

OUTPUT FORMAT:
Return a JSON object with optimized sections:
{{
    "summary": "Optimized professional summary",
    "skills": ["skill1", "skill2", "skill3", ...],
    "experience_improvements": [
        {{
            "original": "Original bullet point",
            "optimized": "ATS-optimized version with keywords"
        }}
    ],
    "keywords_added": ["keyword1", "keyword2", ...],
    "sections_modified": ["summary", "skills", "experience"]
}}

Generate the optimized resume content:"""

        # Try different AI providers
        result = None
        
        # Try OpenAI first
        if not result and self.openai_client:
            result = self._query_openai_for_resume(prompt)
        
        # Try Anthropic as backup
        if not result and self.anthropic_client:
            result = self._query_anthropic_for_resume(prompt)
        
        # Try Gemini as second backup
        if not result and self.gemini_client:
            result = self._query_gemini_for_resume(prompt)
        
        # Fallback optimization
        if not result:
            result = self._generate_fallback_optimization(original_resume, job_analysis)
        
        return result
    
    def _query_openai_for_resume(self, prompt: str) -> Optional[Dict]:
        """Query OpenAI for resume optimization"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert ATS resume optimizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            # Try to parse JSON
            if content.startswith('{'):
                return json.loads(content)
            
            return None
        except Exception as e:
            logger.error(f"OpenAI resume query error: {e}")
            return None
    
    def _query_anthropic_for_resume(self, prompt: str) -> Optional[Dict]:
        """Query Anthropic for resume optimization"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            # Try to parse JSON
            if content.startswith('{'):
                return json.loads(content)
            
            return None
        except Exception as e:
            logger.error(f"Anthropic resume query error: {e}")
            return None
    
    def _query_gemini_for_resume(self, prompt: str) -> Optional[Dict]:
        """Query Gemini for resume optimization"""
        try:
            response = self.gemini_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2000,
                    temperature=0.3,
                )
            )
            
            content = response.text.strip()
            # Try to parse JSON
            if content.startswith('{'):
                return json.loads(content)
            
            return None
        except Exception as e:
            logger.error(f"Gemini resume query error: {e}")
            return None
    
    def _generate_fallback_optimization(self, original_resume: str, job_analysis: Dict) -> Dict:
        """Generate basic optimization when AI fails"""
        keywords = job_analysis.get('keywords', [])[:10]
        
        return {
            "summary": f"Experienced professional with expertise in {', '.join(keywords[:3])} seeking to contribute to innovative projects.",
            "skills": keywords,
            "experience_improvements": [
                {
                    "original": "Worked on various projects",
                    "optimized": f"Developed and implemented solutions using {', '.join(keywords[:2])}"
                }
            ],
            "keywords_added": keywords,
            "sections_modified": ["summary", "skills"]
        }
    
    def create_optimized_resume(self, 
                              job_title: str, 
                              company: str, 
                              job_description: str) -> ResumeVersion:
        """
        Main method to create an optimized resume for a specific job
        
        Args:
            job_title: The job title to optimize for
            company: The company name
            job_description: Full job description text
            
        Returns:
            ResumeVersion object with optimization details
        """
        
        logger.info(f"Creating optimized resume for {job_title} at {company}")
        
        # Check if we already have an optimized version
        job_hash = hashlib.md5(f"{job_title}_{company}_{job_description}".encode()).hexdigest()
        if job_hash in self.versions_cache:
            logger.info("Using cached optimized resume")
            cached_data = self.versions_cache[job_hash]
            return ResumeVersion(**cached_data)
        
        # Extract original resume text
        original_text = self.extract_resume_text(self.base_resume_path)
        if not original_text:
            raise ValueError(f"Could not extract text from resume: {self.base_resume_path}")
        
        # Analyze job description
        job_analysis = self.analyze_job_description(job_description)
        logger.info(f"Found {len(job_analysis['keywords'])} relevant keywords")
        
        # Generate optimized content using AI
        optimization_result = self.generate_optimized_resume_content(
            original_text, job_description, job_analysis
        )
        
        # Calculate similarity scores
        similarity_score = self.calculate_resume_job_similarity(original_text, job_description)
        
        # Create optimized resume file (for now, create a text summary)
        optimized_filename = f"resume_{company}_{job_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        optimized_path = self.output_dir / optimized_filename
        
        # Write optimized content to file
        self._write_optimized_resume_file(optimized_path, optimization_result, original_text)
        
        # Create ResumeVersion object
        resume_version = ResumeVersion(
            job_title=job_title,
            company=company,
            original_resume_path=str(self.base_resume_path),
            optimized_resume_path=str(optimized_path),
            job_description=job_description[:500] + "..." if len(job_description) > 500 else job_description,
            similarity_score=similarity_score,
            keywords_added=optimization_result.get('keywords_added', []),
            sections_modified=optimization_result.get('sections_modified', []),
            creation_timestamp=datetime.now().isoformat(),
            ai_provider="openai" if self.openai_client else "fallback"
        )
        
        # Cache the result
        self.versions_cache[job_hash] = asdict(resume_version)
        self._save_versions_cache()
        
        logger.info(f"Created optimized resume: {optimized_path}")
        logger.info(f"Similarity score: {similarity_score:.3f}")
        logger.info(f"Keywords added: {len(optimization_result.get('keywords_added', []))}")
        
        return resume_version
    
    def _write_optimized_resume_file(self, file_path: Path, optimization: Dict, original_text: str):
        """Write the optimized resume content to a file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=== OPTIMIZED RESUME ===\\n\\n")
                
                # Professional Summary
                f.write("PROFESSIONAL SUMMARY:\\n")
                f.write(f"{optimization.get('summary', 'Professional with relevant experience')}\\n\\n")
                
                # Key Skills
                f.write("KEY SKILLS:\\n")
                skills = optimization.get('skills', [])
                for skill in skills[:15]:  # Top 15 skills
                    f.write(f"• {skill}\\n")
                f.write("\\n")
                
                # Experience Improvements
                f.write("EXPERIENCE IMPROVEMENTS:\\n")
                improvements = optimization.get('experience_improvements', [])
                for i, improvement in enumerate(improvements[:5], 1):
                    f.write(f"{i}. {improvement.get('optimized', 'Enhanced experience point')}\\n")
                f.write("\\n")
                
                # Optimization Details
                f.write("=== OPTIMIZATION DETAILS ===\\n")
                f.write(f"Keywords Added: {', '.join(optimization.get('keywords_added', []))}\\n")
                f.write(f"Sections Modified: {', '.join(optimization.get('sections_modified', []))}\\n\\n")
                
                # Original resume excerpt
                f.write("=== ORIGINAL RESUME EXCERPT ===\\n")
                f.write(original_text[:1000] + "..." if len(original_text) > 1000 else original_text)
                
        except Exception as e:
            logger.error(f"Error writing optimized resume file: {e}")
    
    def get_optimization_statistics(self) -> Dict:
        """Get statistics about resume optimizations"""
        if not self.versions_cache:
            return {"total_versions": 0}
        
        companies = {}
        avg_similarity = 0
        total_keywords = 0
        
        for version_data in self.versions_cache.values():
            # Count by company
            company = version_data.get('company', 'unknown')
            companies[company] = companies.get(company, 0) + 1
            
            # Average similarity
            avg_similarity += version_data.get('similarity_score', 0)
            
            # Total keywords
            total_keywords += len(version_data.get('keywords_added', []))
        
        num_versions = len(self.versions_cache)
        
        return {
            "total_versions": num_versions,
            "companies": companies,
            "average_similarity_score": avg_similarity / num_versions if num_versions > 0 else 0,
            "total_keywords_added": total_keywords,
            "cache_file": str(self.versions_cache_path),
            "output_directory": str(self.output_dir)
        }
    
    def list_optimized_resumes(self) -> List[Dict]:
        """List all optimized resume versions"""
        versions = []
        for version_data in self.versions_cache.values():
            versions.append({
                "job_title": version_data.get('job_title'),
                "company": version_data.get('company'),
                "similarity_score": version_data.get('similarity_score'),
                "keywords_count": len(version_data.get('keywords_added', [])),
                "creation_date": version_data.get('creation_timestamp', '').split('T')[0],
                "file_path": version_data.get('optimized_resume_path')
            })
        
        # Sort by creation date (newest first)
        versions.sort(key=lambda x: x.get('creation_date', ''), reverse=True)
        return versions


def main():
    """Demo the Dynamic Resume Rewriter"""
    print("🤖 Dynamic Resume Rewriter Demo")
    print("=" * 50)
    
    # Initialize the rewriter
    rewriter = DynamicResumeRewriter()
    
    # Sample job description
    job_description = """
    We are seeking a Senior Software Engineer to join our growing engineering team. 
    The ideal candidate will have 5+ years of experience in Python, React, and cloud technologies.
    
    Responsibilities:
    - Design and develop scalable web applications using Python and React
    - Work with AWS services including EC2, S3, and Lambda
    - Collaborate with cross-functional teams in an Agile environment
    - Implement CI/CD pipelines and automated testing
    - Mentor junior developers and contribute to technical decisions
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 5+ years of software development experience
    - Strong proficiency in Python, JavaScript, React
    - Experience with AWS cloud services
    - Knowledge of Docker, Kubernetes preferred
    - Excellent communication and problem-solving skills
    """
    
    print("\\nCreating optimized resume...")
    try:
        resume_version = rewriter.create_optimized_resume(
            job_title="Senior Software Engineer",
            company="TechCorp Inc",
            job_description=job_description
        )
        
        print(f"✅ Optimized resume created!")
        print(f"   File: {resume_version.optimized_resume_path}")
        print(f"   Similarity Score: {resume_version.similarity_score:.3f}")
        print(f"   Keywords Added: {len(resume_version.keywords_added)}")
        print(f"   Sections Modified: {', '.join(resume_version.sections_modified)}")
        print(f"   AI Provider: {resume_version.ai_provider}")
        
        # Show statistics
        print(f"\\nOptimization Statistics:")
        stats = rewriter.get_optimization_statistics()
        for key, value in stats.items():
            if key != "companies":
                print(f"  {key}: {value}")
        
        # List all versions
        print(f"\\nAll Optimized Versions:")
        versions = rewriter.list_optimized_resumes()
        for i, version in enumerate(versions, 1):
            print(f"  {i}. {version['job_title']} at {version['company']} (Score: {version['similarity_score']:.3f})")
            
    except Exception as e:
        print(f"❌ Error creating optimized resume: {e}")
        logger.error(f"Demo error: {e}")


if __name__ == "__main__":
    main()