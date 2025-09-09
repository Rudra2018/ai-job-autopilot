#!/usr/bin/env python3
"""
Enhanced Resume Parser
Advanced resume parsing that works with extracted PDF text for maximum accuracy
"""

import re
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

# Optional email validation
try:
    import email_validator
    HAS_EMAIL_VALIDATOR = True
except ImportError:
    HAS_EMAIL_VALIDATOR = False

# Import our PDF extractor
from src.core.pdf_text_extractor import EnhancedPDFExtractor, ExtractionConfig, extract_pdf_text

class SectionType(Enum):
    """Resume section types"""
    CONTACT = "contact"
    SUMMARY = "summary" 
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    LANGUAGES = "languages"
    ACHIEVEMENTS = "achievements"
    REFERENCES = "references"

@dataclass
class ContactInfo:
    """Contact information structure"""
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    country: str = ""
    postal_code: str = ""

@dataclass
class WorkExperience:
    """Work experience entry"""
    company: str = ""
    position: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)

@dataclass
class Education:
    """Education entry"""
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    honors: List[str] = field(default_factory=list)
    relevant_coursework: List[str] = field(default_factory=list)

@dataclass
class Project:
    """Project entry"""
    name: str = ""
    description: str = ""
    technologies: List[str] = field(default_factory=list)
    url: str = ""
    start_date: str = ""
    end_date: str = ""
    achievements: List[str] = field(default_factory=list)

@dataclass
class Certification:
    """Certification entry"""
    name: str = ""
    issuer: str = ""
    date_issued: str = ""
    expiry_date: str = ""
    credential_id: str = ""
    url: str = ""

@dataclass
class ParsedResume:
    """Complete parsed resume structure"""
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    summary: str = ""
    work_experience: List[WorkExperience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    # Metadata
    raw_text: str = ""
    extraction_method: str = ""
    extraction_confidence: float = 0.0
    parsing_confidence: float = 0.0
    sections_found: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)

class EnhancedResumeParser:
    """Enhanced resume parser with text preprocessing and AI assistance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize PDF extractor
        self.pdf_extractor = EnhancedPDFExtractor(
            ExtractionConfig(
                clean_text=True,
                use_ocr_fallback=True,
                prefer_method="auto"
            )
        )
        
        # Compiled regex patterns for better performance
        self._compile_patterns()
        
        # Section headers patterns
        self.section_patterns = {
            SectionType.CONTACT: [
                r'contact\s+information', r'personal\s+information', r'contact\s+details'
            ],
            SectionType.SUMMARY: [
                r'summary', r'profile', r'objective', r'professional\s+summary',
                r'career\s+objective', r'professional\s+profile', r'about\s+me'
            ],
            SectionType.EXPERIENCE: [
                r'experience', r'work\s+experience', r'professional\s+experience',
                r'employment', r'career\s+history', r'work\s+history'
            ],
            SectionType.EDUCATION: [
                r'education', r'academic\s+background', r'educational\s+background',
                r'qualifications', r'academic\s+qualifications'
            ],
            SectionType.SKILLS: [
                r'skills', r'technical\s+skills', r'core\s+competencies',
                r'key\s+skills', r'competencies', r'technologies'
            ],
            SectionType.PROJECTS: [
                r'projects', r'key\s+projects', r'notable\s+projects',
                r'personal\s+projects', r'academic\s+projects'
            ],
            SectionType.CERTIFICATIONS: [
                r'certifications', r'certificates', r'professional\s+certifications',
                r'licenses', r'credentials'
            ],
            SectionType.LANGUAGES: [
                r'languages', r'language\s+skills', r'linguistic\s+skills'
            ],
            SectionType.ACHIEVEMENTS: [
                r'achievements', r'accomplishments', r'awards', r'honors',
                r'recognition'
            ]
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'),
            re.compile(r'\+?([0-9]{1,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})'),
            re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
        ]
        
        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)', re.IGNORECASE
        )
        
        # GitHub URL pattern  
        self.github_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)', re.IGNORECASE
        )
        
        # Date patterns
        self.date_patterns = [
            re.compile(r'\b(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/(19|20)\d{2}\b'),
            re.compile(r'\b(19|20)\d{2}\b'),
            re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(19|20)\d{2}\b', re.IGNORECASE),
            re.compile(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(19|20)\d{2}\b', re.IGNORECASE)
        ]
        
        # Skills pattern
        self.skills_pattern = re.compile(
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|SQL|HTML|CSS|React|Angular|Vue|Node\.js|Django|Flask|'
            r'AWS|Azure|Docker|Kubernetes|Git|Linux|Windows|macOS|Agile|Scrum|'
            r'Machine Learning|AI|Data Science|Analytics|Pandas|NumPy|TensorFlow|PyTorch)\b', 
            re.IGNORECASE
        )
    
    def parse_resume(self, file_path: str) -> ParsedResume:
        """Parse resume from PDF file"""
        import time
        start_time = time.time()
        
        try:
            # Step 1: Extract text from PDF
            self.logger.info(f"Extracting text from PDF: {file_path}")
            extraction_result = self.pdf_extractor.extract_text(file_path)
            
            if not extraction_result.text.strip():
                raise ValueError("No text could be extracted from PDF")
            
            # Step 2: Parse the extracted text
            self.logger.info("Parsing extracted text")
            parsed_resume = self._parse_text(extraction_result.text)
            
            # Step 3: Add metadata
            parsed_resume.raw_text = extraction_result.text
            parsed_resume.extraction_method = extraction_result.method
            parsed_resume.extraction_confidence = extraction_result.confidence
            parsed_resume.processing_time = time.time() - start_time
            
            # Calculate overall parsing confidence
            parsed_resume.parsing_confidence = self._calculate_parsing_confidence(parsed_resume)
            
            self.logger.info(f"Resume parsing completed in {parsed_resume.processing_time:.2f}s")
            return parsed_resume
            
        except Exception as e:
            self.logger.error(f"Resume parsing failed: {e}")
            
            # Return empty result with error
            error_resume = ParsedResume()
            error_resume.errors.append(str(e))
            error_resume.processing_time = time.time() - start_time
            return error_resume
    
    def parse_text(self, text: str) -> ParsedResume:
        """Parse resume from raw text"""
        return self._parse_text(text)
    
    def _parse_text(self, text: str) -> ParsedResume:
        """Internal method to parse text into resume structure"""
        resume = ParsedResume()
        
        # Preprocess text
        text = self._preprocess_text(text)
        
        # Identify sections
        sections = self._identify_sections(text)
        resume.sections_found = list(sections.keys())
        
        # Parse each section
        if SectionType.CONTACT.value in sections:
            resume.contact_info = self._parse_contact_info(sections[SectionType.CONTACT.value])
        else:
            # Try to extract contact info from entire text
            resume.contact_info = self._parse_contact_info(text)
        
        if SectionType.SUMMARY.value in sections:
            resume.summary = self._parse_summary(sections[SectionType.SUMMARY.value])
        
        if SectionType.EXPERIENCE.value in sections:
            resume.work_experience = self._parse_work_experience(sections[SectionType.EXPERIENCE.value])
        
        if SectionType.EDUCATION.value in sections:
            resume.education = self._parse_education(sections[SectionType.EDUCATION.value])
        
        if SectionType.SKILLS.value in sections:
            resume.skills = self._parse_skills(sections[SectionType.SKILLS.value])
        else:
            # Try to extract skills from entire text
            resume.skills = self._extract_skills_from_text(text)
        
        if SectionType.PROJECTS.value in sections:
            resume.projects = self._parse_projects(sections[SectionType.PROJECTS.value])
        
        if SectionType.CERTIFICATIONS.value in sections:
            resume.certifications = self._parse_certifications(sections[SectionType.CERTIFICATIONS.value])
        
        if SectionType.LANGUAGES.value in sections:
            resume.languages = self._parse_languages(sections[SectionType.LANGUAGES.value])
        
        if SectionType.ACHIEVEMENTS.value in sections:
            resume.achievements = self._parse_achievements(sections[SectionType.ACHIEVEMENTS.value])
        
        return resume
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better parsing"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = re.sub(r'\bEducat10n\b', 'Education', text, flags=re.IGNORECASE)
        text = re.sub(r'\bExper1ence\b', 'Experience', text, flags=re.IGNORECASE)
        text = re.sub(r'\bSk111s\b', 'Skills', text, flags=re.IGNORECASE)
        
        # Normalize bullet points
        text = re.sub(r'[•·▪▫◦‣⁃]', '•', text)
        
        return text.strip()
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract different resume sections"""
        sections = {}
        text_lower = text.lower()
        
        # Find section boundaries
        section_boundaries = []
        
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(r'\b' + pattern + r'\b', text_lower))
                for match in matches:
                    section_boundaries.append({
                        'start': match.start(),
                        'section': section_type.value,
                        'text': match.group()
                    })
        
        # Sort by position in text
        section_boundaries.sort(key=lambda x: x['start'])
        
        # Extract section content
        for i, boundary in enumerate(section_boundaries):
            start = boundary['start']
            
            # Find end position (start of next section or end of text)
            if i + 1 < len(section_boundaries):
                end = section_boundaries[i + 1]['start']
            else:
                end = len(text)
            
            # Extract section content
            section_text = text[start:end].strip()
            
            # Remove section header
            lines = section_text.split('\n')
            if lines:
                # Skip the header line
                section_content = '\n'.join(lines[1:]).strip()
                sections[boundary['section']] = section_content
        
        return sections
    
    def _parse_contact_info(self, text: str) -> ContactInfo:
        """Parse contact information from text"""
        contact = ContactInfo()
        
        # Extract email
        email_match = self.email_pattern.search(text)
        if email_match:
            contact.email = email_match.group()
        
        # Extract phone
        for pattern in self.phone_patterns:
            phone_match = pattern.search(text)
            if phone_match:
                contact.phone = phone_match.group()
                break
        
        # Extract LinkedIn
        linkedin_match = self.linkedin_pattern.search(text)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()
        
        # Extract GitHub
        github_match = self.github_pattern.search(text)
        if github_match:
            contact.github = github_match.group()
        
        # Extract name (usually first line or near contact info)
        lines = text.strip().split('\n')
        if lines:
            # Try first line as name
            first_line = lines[0].strip()
            if len(first_line.split()) >= 2 and not any(char.isdigit() for char in first_line):
                contact.name = first_line
        
        # Extract address components
        self._parse_address(text, contact)
        
        return contact
    
    def _parse_address(self, text: str, contact: ContactInfo):
        """Parse address information"""
        # Simple address parsing - can be enhanced
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for city, state pattern
            city_state_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})?', line)
            if city_state_match:
                contact.city = city_state_match.group(1).strip()
                contact.state = city_state_match.group(2)
                if city_state_match.group(3):
                    contact.postal_code = city_state_match.group(3)
            
            # Look for country
            countries = ['USA', 'United States', 'Canada', 'UK', 'United Kingdom', 'Germany', 'France']
            for country in countries:
                if country.lower() in line.lower():
                    contact.country = country
                    break
    
    def _parse_summary(self, text: str) -> str:
        """Parse professional summary"""
        # Clean up summary text
        lines = text.strip().split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('•') and len(line) > 20:
                summary_lines.append(line)
        
        return ' '.join(summary_lines)
    
    def _parse_work_experience(self, text: str) -> List[WorkExperience]:
        """Parse work experience section"""
        experiences = []
        
        # Split by potential job entries (look for company/position patterns)
        entries = self._split_experience_entries(text)
        
        for entry in entries:
            experience = WorkExperience()
            lines = entry.strip().split('\n')
            
            if not lines:
                continue
            
            # First line usually contains company and position
            first_line = lines[0].strip()
            self._parse_job_header(first_line, experience)
            
            # Parse dates
            date_info = self._extract_employment_dates(entry)
            experience.start_date = date_info.get('start', '')
            experience.end_date = date_info.get('end', '')
            
            # Parse description and achievements
            description_lines = []
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    description_lines.append(line[1:].strip())
                elif line and not self._is_date_line(line):
                    description_lines.append(line)
            
            experience.description = description_lines
            
            # Extract technologies
            experience.technologies = self._extract_technologies(entry)
            
            if experience.company or experience.position:
                experiences.append(experience)
        
        return experiences
    
    def _split_experience_entries(self, text: str) -> List[str]:
        """Split work experience text into individual job entries"""
        # Simple splitting by double newlines or pattern recognition
        entries = re.split(r'\n\s*\n', text)
        
        # Filter out very short entries
        return [entry for entry in entries if len(entry.strip()) > 50]
    
    def _parse_job_header(self, header: str, experience: WorkExperience):
        """Parse job header line to extract company and position"""
        # Common patterns: "Position at Company", "Company - Position", etc.
        
        if ' at ' in header:
            parts = header.split(' at ')
            if len(parts) == 2:
                experience.position = parts[0].strip()
                experience.company = parts[1].strip()
        elif ' - ' in header:
            parts = header.split(' - ')
            if len(parts) >= 2:
                experience.company = parts[0].strip()
                experience.position = parts[1].strip()
        elif '|' in header:
            parts = header.split('|')
            if len(parts) >= 2:
                experience.position = parts[0].strip()
                experience.company = parts[1].strip()
        else:
            # Assume it's the company name
            experience.company = header.strip()
    
    def _extract_employment_dates(self, text: str) -> Dict[str, str]:
        """Extract employment dates from text"""
        dates = {}
        
        # Look for date ranges
        date_range_pattern = re.compile(
            r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*[-–]\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)',
            re.IGNORECASE
        )
        
        match = date_range_pattern.search(text)
        if match:
            dates['start'] = match.group(1)
            dates['end'] = match.group(2)
        
        return dates
    
    def _is_date_line(self, line: str) -> bool:
        """Check if line contains date information"""
        for pattern in self.date_patterns:
            if pattern.search(line):
                return True
        return False
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technologies/tools from text"""
        technologies = set()
        
        # Use skills pattern to find technologies
        matches = self.skills_pattern.findall(text)
        technologies.update(matches)
        
        return list(technologies)
    
    def _parse_education(self, text: str) -> List[Education]:
        """Parse education section"""
        education_list = []
        
        # Split by potential education entries
        entries = re.split(r'\n\s*\n', text)
        
        for entry in entries:
            if len(entry.strip()) < 20:
                continue
                
            education = Education()
            lines = entry.strip().split('\n')
            
            # First line usually contains degree and institution
            if lines:
                first_line = lines[0].strip()
                self._parse_education_header(first_line, education)
            
            # Extract dates
            date_info = self._extract_education_dates(entry)
            education.start_date = date_info.get('start', '')
            education.end_date = date_info.get('end', '')
            
            # Extract GPA if present
            gpa_match = re.search(r'GPA[:\s]*([0-9.]+)', entry, re.IGNORECASE)
            if gpa_match:
                education.gpa = gpa_match.group(1)
            
            if education.institution or education.degree:
                education_list.append(education)
        
        return education_list
    
    def _parse_education_header(self, header: str, education: Education):
        """Parse education header to extract degree and institution"""
        # Common patterns
        if ' in ' in header and ' at ' in header:
            # "Bachelor of Science in Computer Science at University"
            parts = header.split(' at ')
            if len(parts) == 2:
                degree_part = parts[0].strip()
                education.institution = parts[1].strip()
                
                if ' in ' in degree_part:
                    degree_parts = degree_part.split(' in ')
                    education.degree = degree_parts[0].strip()
                    education.field_of_study = degree_parts[1].strip()
                else:
                    education.degree = degree_part
        elif ',' in header:
            parts = header.split(',')
            if len(parts) >= 2:
                education.degree = parts[0].strip()
                education.institution = parts[1].strip()
        else:
            education.institution = header.strip()
    
    def _extract_education_dates(self, text: str) -> Dict[str, str]:
        """Extract education dates"""
        dates = {}
        
        # Look for graduation year
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            dates['end'] = year_match.group()
        
        return dates
    
    def _parse_skills(self, text: str) -> List[str]:
        """Parse skills section"""
        skills = set()
        
        # Split by common separators
        skill_text = re.sub(r'[•\-\n]', ',', text)
        potential_skills = [s.strip() for s in skill_text.split(',')]
        
        for skill in potential_skills:
            skill = skill.strip()
            if skill and len(skill) > 1 and len(skill) < 50:
                skills.add(skill)
        
        # Also extract using pattern matching
        pattern_skills = self._extract_skills_from_text(text)
        skills.update(pattern_skills)
        
        return list(skills)
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills using pattern matching"""
        skills = set()
        matches = self.skills_pattern.findall(text)
        skills.update(matches)
        return list(skills)
    
    def _parse_projects(self, text: str) -> List[Project]:
        """Parse projects section"""
        projects = []
        
        entries = re.split(r'\n\s*\n', text)
        
        for entry in entries:
            if len(entry.strip()) < 30:
                continue
                
            project = Project()
            lines = entry.strip().split('\n')
            
            if lines:
                project.name = lines[0].strip()
                
                # Parse description
                desc_lines = []
                for line in lines[1:]:
                    line = line.strip()
                    if line and not line.startswith('Technologies:'):
                        desc_lines.append(line)
                
                project.description = ' '.join(desc_lines)
                
                # Extract technologies
                project.technologies = self._extract_technologies(entry)
            
            if project.name:
                projects.append(project)
        
        return projects
    
    def _parse_certifications(self, text: str) -> List[Certification]:
        """Parse certifications section"""
        certifications = []
        
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10:
                cert = Certification()
                cert.name = line
                certifications.append(cert)
        
        return certifications
    
    def _parse_languages(self, text: str) -> List[str]:
        """Parse languages section"""
        languages = []
        
        # Split by common separators
        lang_text = re.sub(r'[•\-\n]', ',', text)
        potential_langs = [l.strip() for l in lang_text.split(',')]
        
        for lang in potential_langs:
            lang = lang.strip()
            if lang and len(lang) > 1:
                languages.append(lang)
        
        return languages
    
    def _parse_achievements(self, text: str) -> List[str]:
        """Parse achievements section"""
        achievements = []
        
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                achievements.append(line[1:].strip())
            elif line and len(line) > 10:
                achievements.append(line)
        
        return achievements
    
    def _calculate_parsing_confidence(self, resume: ParsedResume) -> float:
        """Calculate confidence score for parsed resume"""
        confidence = 0.0
        
        # Base confidence from extraction
        confidence += resume.extraction_confidence * 0.3
        
        # Contact info completeness
        contact_fields = [resume.contact_info.name, resume.contact_info.email, 
                         resume.contact_info.phone]
        contact_score = sum(1 for field in contact_fields if field) / len(contact_fields)
        confidence += contact_score * 0.2
        
        # Sections found
        section_score = len(resume.sections_found) / len(SectionType)
        confidence += section_score * 0.2
        
        # Content richness
        content_score = 0.0
        if resume.work_experience:
            content_score += 0.3
        if resume.education:
            content_score += 0.2
        if resume.skills:
            content_score += 0.2
        if resume.summary:
            content_score += 0.1
        
        confidence += content_score * 0.3
        
        return min(confidence, 1.0)

# Convenience functions
def parse_resume_from_pdf(pdf_path: str) -> ParsedResume:
    """Quick function to parse resume from PDF"""
    parser = EnhancedResumeParser()
    return parser.parse_resume(pdf_path)

def parse_resume_from_text(text: str) -> ParsedResume:
    """Quick function to parse resume from text"""
    parser = EnhancedResumeParser()
    return parser.parse_text(text)

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        resume_file = sys.argv[1]
        
        parser = EnhancedResumeParser()
        result = parser.parse_resume(resume_file)
        
        print(f"Parsing Confidence: {result.parsing_confidence:.2f}")
        print(f"Extraction Method: {result.extraction_method}")
        print(f"Sections Found: {', '.join(result.sections_found)}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        
        print("\n--- Parsed Resume ---")
        print(json.dumps(asdict(result), indent=2, default=str))
    else:
        print("Usage: python enhanced_resume_parser.py <resume_file.pdf>")