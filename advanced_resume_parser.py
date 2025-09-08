#!/usr/bin/env python3
"""
Advanced Resume Parser with AI-Powered Skill Extraction
Parses resumes and extracts comprehensive information using NLP and AI
"""

import os
import re
import json
import PyPDF2
import docx
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
import spacy
import openai
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import yaml
import pandas as pd
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from fuzzywuzzy import fuzz
import pdfplumber

@dataclass 
class ContactInfo:
    name: str
    email: str
    phone: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None

@dataclass
class Education:
    degree: str
    field: str
    institution: str
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None
    honors: List[str] = None

@dataclass
class WorkExperience:
    title: str
    company: str
    location: str
    start_date: str
    end_date: Optional[str]
    duration_months: int
    responsibilities: List[str]
    achievements: List[str]
    skills_used: List[str]

@dataclass
class Certification:
    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None

@dataclass
class ParsedResume:
    contact_info: ContactInfo
    summary: str
    skills: Dict[str, List[str]]  # categorized skills
    work_experience: List[WorkExperience]
    education: List[Education]
    certifications: List[Certification]
    projects: List[Dict]
    languages: List[str]
    awards: List[str]
    publications: List[str]
    raw_text: str
    file_path: str
    parsed_at: str
    
    # Derived insights
    total_experience_years: float
    seniority_level: str
    primary_domain: str
    skill_confidence_scores: Dict[str, float]

class SkillsDatabase:
    """Comprehensive skills database with categorization"""
    
    def __init__(self):
        self.skills_db = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 
                'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r',
                'matlab', 'perl', 'shell', 'bash', 'powershell', 'vba'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express',
                'django', 'flask', 'spring', 'asp.net', 'laravel', 'rails',
                'jquery', 'bootstrap', 'sass', 'less', 'webpack', 'gulp'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb',
                'oracle', 'sql server', 'sqlite', 'neo4j', 'elasticsearch',
                'influxdb', 'firebase', 'couchdb', 'mariadb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean',
                'linode', 'vultr', 'cloudflare', 'netlify', 'vercel'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
                'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'helm',
                'prometheus', 'grafana', 'elk stack', 'nagios', 'zabbix'
            ],
            'cybersecurity': [
                'penetration testing', 'vulnerability assessment', 'ethical hacking',
                'incident response', 'threat modeling', 'risk assessment',
                'security architecture', 'network security', 'cloud security',
                'application security', 'malware analysis', 'digital forensics',
                'compliance', 'gdpr', 'hipaa', 'sox', 'iso 27001', 'nist',
                'owasp', 'sans', 'cissp', 'ceh', 'oscp', 'cissp', 'cism'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'data mining', 'statistics',
                'data visualization', 'pandas', 'numpy', 'scikit-learn',
                'tensorflow', 'pytorch', 'keras', 'opencv', 'nlp',
                'computer vision', 'reinforcement learning', 'big data',
                'hadoop', 'spark', 'kafka', 'airflow', 'jupyter'
            ],
            'mobile_development': [
                'ios', 'android', 'react native', 'flutter', 'xamarin',
                'cordova', 'ionic', 'swift', 'objective-c', 'kotlin', 'java'
            ],
            'project_management': [
                'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma',
                'pmp', 'prince2', 'jira', 'confluence', 'trello', 'asana',
                'monday.com', 'basecamp', 'slack', 'microsoft teams'
            ],
            'design_tools': [
                'photoshop', 'illustrator', 'figma', 'sketch', 'invision',
                'adobe xd', 'after effects', 'premiere pro', 'canva',
                'ux design', 'ui design', 'user research', 'wireframing',
                'prototyping', 'usability testing'
            ],
            'business_analysis': [
                'business analysis', 'requirements gathering', 'process improvement',
                'stakeholder management', 'gap analysis', 'use cases',
                'user stories', 'acceptance criteria', 'process mapping',
                'visio', 'lucidchart', 'bizagi'
            ]
        }
        
        # Flatten for search
        self.all_skills = []
        for category, skills in self.skills_db.items():
            self.all_skills.extend(skills)
        
        # Load AI models for skill extraction
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            print("⚠️  SpaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Skill extraction pipeline
        try:
            self.skill_classifier = pipeline(
                'zero-shot-classification',
                model='facebook/bart-large-mnli',
                device=0 if torch.cuda.is_available() else -1
            )
        except:
            print("⚠️  BART model not available, using fallback method")
            self.skill_classifier = None

class ResumeParser:
    """Advanced resume parser with AI-powered extraction"""
    
    def __init__(self):
        self.skills_db = SkillsDatabase()
        
        # Common patterns for extraction
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[1-9]?[0-9]{7,15}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w\-_]+')
        self.github_pattern = re.compile(r'github\.com/[\w\-_]+')
        self.url_pattern = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?')
        
        # Date patterns
        self.date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|\w+)',
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\w+)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|\w+)'
        ]
        
        # Experience indicators
        self.experience_indicators = [
            'experience', 'work history', 'professional experience',
            'employment', 'career', 'work experience'
        ]
        
        # Education indicators
        self.education_indicators = [
            'education', 'academic', 'qualifications', 'degrees',
            'university', 'college', 'school'
        ]
        
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        text = ""
        
        if file_path.suffix.lower() == '.pdf':
            text = self._extract_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self._extract_from_docx(file_path)
        elif file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return text.strip()
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF using multiple methods"""
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
                text = ""
        
        return text
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting from DOCX: {e}")
            return ""
    
    def parse_resume(self, file_path: str) -> ParsedResume:
        """Parse resume and extract all information"""
        print(f"📄 Parsing resume: {Path(file_path).name}")
        
        # Extract text
        raw_text = self.extract_text_from_file(file_path)
        
        if not raw_text.strip():
            raise ValueError("Could not extract text from resume")
        
        # Extract different sections
        contact_info = self._extract_contact_info(raw_text)
        summary = self._extract_summary(raw_text)
        skills = self._extract_skills(raw_text)
        work_experience = self._extract_work_experience(raw_text)
        education = self._extract_education(raw_text)
        certifications = self._extract_certifications(raw_text)
        projects = self._extract_projects(raw_text)
        languages = self._extract_languages(raw_text)
        awards = self._extract_awards(raw_text)
        publications = self._extract_publications(raw_text)
        
        # Calculate derived insights
        total_experience = self._calculate_total_experience(work_experience)
        seniority_level = self._determine_seniority_level(total_experience, skills, work_experience)
        primary_domain = self._determine_primary_domain(skills, work_experience)
        skill_confidence = self._calculate_skill_confidence(skills, work_experience, raw_text)
        
        parsed_resume = ParsedResume(
            contact_info=contact_info,
            summary=summary,
            skills=skills,
            work_experience=work_experience,
            education=education,
            certifications=certifications,
            projects=projects,
            languages=languages,
            awards=awards,
            publications=publications,
            raw_text=raw_text,
            file_path=str(file_path),
            parsed_at=datetime.now().isoformat(),
            total_experience_years=total_experience,
            seniority_level=seniority_level,
            primary_domain=primary_domain,
            skill_confidence_scores=skill_confidence
        )
        
        print(f"✅ Resume parsed successfully:")
        print(f"   👤 Name: {contact_info.name}")
        print(f"   📧 Email: {contact_info.email}")
        print(f"   🎯 Domain: {primary_domain}")
        print(f"   📊 Experience: {total_experience:.1f} years ({seniority_level})")
        print(f"   🔧 Skills: {len(self._flatten_skills(skills))} identified")
        
        return parsed_resume
    
    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information"""
        lines = text.split('\n')[:10]  # Usually in first few lines
        
        # Extract name (usually first significant line)
        name = ""
        for line in lines:
            line = line.strip()
            if line and not self._is_header_line(line) and len(line.split()) <= 4:
                # Check if it looks like a name
                if re.match(r'^[A-Za-z\s.,-]+$', line) and not any(char.isdigit() for char in line):
                    name = line
                    break
        
        # Extract email
        email_matches = self.email_pattern.findall(text)
        email = email_matches[0] if email_matches else ""
        
        # Extract phone
        phone_matches = self.phone_pattern.findall(text)
        phone = ""
        for match in phone_matches:
            # Clean and validate phone number
            clean_phone = re.sub(r'[^\d+]', '', match)
            if len(clean_phone) >= 10:
                phone = match
                break
        
        # Extract LinkedIn
        linkedin_matches = self.linkedin_pattern.findall(text)
        linkedin = f"https://{linkedin_matches[0]}" if linkedin_matches else None
        
        # Extract GitHub
        github_matches = self.github_pattern.findall(text)
        github = f"https://{github_matches[0]}" if github_matches else None
        
        # Extract other URLs (portfolio)
        url_matches = self.url_pattern.findall(text)
        portfolio = None
        for url in url_matches:
            if 'linkedin' not in url and 'github' not in url:
                portfolio = url
                break
        
        # Extract location (usually near contact info)
        location = self._extract_location(text)
        
        return ContactInfo(
            name=name or "Unknown",
            email=email,
            phone=phone,
            linkedin=linkedin,
            github=github,
            portfolio=portfolio,
            location=location
        )
    
    def _is_header_line(self, line: str) -> bool:
        """Check if line is a header/section indicator"""
        headers = ['resume', 'cv', 'curriculum vitae', 'professional', 'summary', 'experience']
        return any(header in line.lower() for header in headers)
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location information"""
        # Common location patterns
        location_patterns = [
            r'(?:^|\n)\s*([A-Za-z\s,]+(?:USA|US|United States|Germany|UK|Canada|India|Singapore))\s*(?:\n|$)',
            r'(?:^|\n)\s*([A-Za-z\s,]+,\s*[A-Z]{2,3})\s*(?:\n|$)',  # City, State/Country
            r'(?:Location|Address|Based in):?\s*([A-Za-z\s,]+)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                if len(location.split()) <= 5:  # Reasonable location length
                    return location
        
        return None
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary/objective"""
        # Common summary section headers
        summary_headers = [
            'summary', 'objective', 'profile', 'about', 'overview',
            'professional summary', 'career objective', 'personal statement'
        ]
        
        lines = text.split('\n')
        summary = ""
        in_summary = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if this line starts a summary section
            if any(header in line_lower for header in summary_headers) and len(line.strip()) < 50:
                in_summary = True
                continue
            
            # If we're in summary section, collect text
            if in_summary:
                # Stop if we hit another section header
                if (line.strip().isupper() and len(line.strip()) < 30) or \
                   any(section in line_lower for section in ['experience', 'education', 'skills', 'projects']):
                    break
                
                if line.strip():
                    summary += line.strip() + " "
                
                # Stop after collecting reasonable amount
                if len(summary) > 500:
                    break
        
        return summary.strip()
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract and categorize skills using multiple methods"""
        categorized_skills = {category: [] for category in self.skills_db.skills_db.keys()}
        
        text_lower = text.lower()
        
        # Method 1: Direct matching against skills database
        for category, skills_list in self.skills_db.skills_db.items():
            for skill in skills_list:
                if skill.lower() in text_lower:
                    # Use fuzzy matching for better accuracy
                    words = text_lower.split()
                    for word_group in [' '.join(words[i:i+len(skill.split())]) for i in range(len(words))]:
                        if fuzz.ratio(skill.lower(), word_group) > 85:
                            if skill not in categorized_skills[category]:
                                categorized_skills[category].append(skill)
        
        # Method 2: Extract from skills section specifically
        skills_section_text = self._extract_section_content(text, ['skills', 'technical skills', 'core competencies'])
        if skills_section_text:
            # Parse comma-separated or bullet-pointed skills
            skill_lines = re.split(r'[,•\n\-]', skills_section_text)
            
            for line in skill_lines:
                line = line.strip()
                if line and len(line) < 50:  # Reasonable skill length
                    # Try to categorize this skill
                    self._categorize_extracted_skill(line, categorized_skills)
        
        # Method 3: AI-powered skill extraction (if available)
        if self.skills_db.skill_classifier:
            ai_skills = self._ai_extract_skills(text)
            for skill in ai_skills:
                self._categorize_extracted_skill(skill, categorized_skills)
        
        # Remove empty categories and duplicates
        for category in categorized_skills:
            categorized_skills[category] = list(set(categorized_skills[category]))
        
        return {k: v for k, v in categorized_skills.items() if v}
    
    def _extract_section_content(self, text: str, section_headers: List[str]) -> str:
        """Extract content from a specific section"""
        lines = text.split('\n')
        content = ""
        in_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line starts the target section
            if any(header in line_lower for header in section_headers) and len(line.strip()) < 50:
                in_section = True
                continue
            
            # If we're in the section, collect content
            if in_section:
                # Stop if we hit another major section
                other_sections = ['experience', 'education', 'projects', 'awards', 'certifications']
                if any(section in line_lower for section in other_sections) and len(line.strip()) < 30:
                    break
                
                if line.strip():
                    content += line + "\n"
        
        return content.strip()
    
    def _categorize_extracted_skill(self, skill: str, categorized_skills: Dict[str, List[str]]):
        """Categorize an extracted skill"""
        skill_lower = skill.lower().strip()
        
        # Direct matching
        for category, skills_list in self.skills_db.skills_db.items():
            for known_skill in skills_list:
                if fuzz.ratio(skill_lower, known_skill.lower()) > 80:
                    if skill not in categorized_skills[category]:
                        categorized_skills[category].append(skill)
                    return
        
        # If no direct match, add to general category based on context
        if re.search(r'\b(python|java|javascript|c\+\+|php|ruby)\b', skill_lower):
            categorized_skills['programming_languages'].append(skill)
        elif re.search(r'\b(aws|azure|cloud|docker|kubernetes)\b', skill_lower):
            categorized_skills['cloud_platforms'].append(skill)
        elif re.search(r'\b(security|cyber|penetration|vulnerability)\b', skill_lower):
            categorized_skills['cybersecurity'].append(skill)
    
    def _ai_extract_skills(self, text: str) -> List[str]:
        """Use AI to extract skills from text"""
        try:
            # Create candidate labels from our skills database
            all_skills = self.skills_db.all_skills[:100]  # Limit for performance
            
            # Extract skills using zero-shot classification
            result = self.skills_db.skill_classifier(text, all_skills, multi_label=True)
            
            # Return skills with high confidence
            extracted_skills = []
            for label, score in zip(result['labels'], result['scores']):
                if score > 0.1:  # Confidence threshold
                    extracted_skills.append(label)
            
            return extracted_skills[:20]  # Limit results
            
        except Exception as e:
            print(f"AI skill extraction failed: {e}")
            return []
    
    def _extract_work_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience information"""
        experience_section = self._extract_section_content(text, self.experience_indicators)
        
        if not experience_section:
            return []
        
        experiences = []
        
        # Split into individual job entries (usually separated by significant gaps)
        job_blocks = re.split(r'\n\s*\n', experience_section)
        
        for block in job_blocks:
            if not block.strip():
                continue
            
            experience = self._parse_job_block(block)
            if experience:
                experiences.append(experience)
        
        return experiences
    
    def _parse_job_block(self, block: str) -> Optional[WorkExperience]:
        """Parse individual job experience block"""
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return None
        
        # First line usually contains title and/or company
        title_line = lines[0]
        
        # Extract title and company
        title, company = self._extract_title_company(title_line, lines)
        
        if not title or not company:
            return None
        
        # Extract dates
        date_info = self._extract_job_dates(block)
        
        # Extract location
        location = self._extract_job_location(lines)
        
        # Extract responsibilities and achievements
        responsibilities, achievements = self._extract_job_details(lines[1:])
        
        # Extract skills used in this role
        skills_used = self._extract_job_skills(block)
        
        return WorkExperience(
            title=title,
            company=company,
            location=location,
            start_date=date_info.get('start_date', ''),
            end_date=date_info.get('end_date'),
            duration_months=date_info.get('duration_months', 0),
            responsibilities=responsibilities,
            achievements=achievements,
            skills_used=skills_used
        )
    
    def _extract_title_company(self, title_line: str, all_lines: List[str]) -> Tuple[str, str]:
        """Extract job title and company from the first line(s)"""
        # Common patterns:
        # "Software Engineer at Google"
        # "Senior Developer | Microsoft"
        # "Data Scientist - Netflix"
        # Or sometimes on separate lines
        
        title = ""
        company = ""
        
        # Pattern 1: Title [at|@|-|,] Company
        patterns = [
            r'^(.+?)\s+(?:at|@)\s+(.+)$',
            r'^(.+?)\s*[-|]\s*(.+)$',
            r'^(.+?),\s*(.+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, title_line, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                company = match.group(2).strip()
                break
        
        # If not found, check if title and company are on separate lines
        if not title and len(all_lines) >= 2:
            title = title_line
            company = all_lines[1]
        
        # Clean up
        title = re.sub(r'^(role|position):\s*', '', title, flags=re.IGNORECASE).strip()
        company = re.sub(r'^(company|employer):\s*', '', company, flags=re.IGNORECASE).strip()
        
        return title, company
    
    def _extract_job_dates(self, text: str) -> Dict:
        """Extract start date, end date, and duration from job text"""
        date_info = {
            'start_date': '',
            'end_date': None,
            'duration_months': 0
        }
        
        # Common date patterns
        patterns = [
            r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|present|current)',
            r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)',
            r'(\d{1,2}/\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|present|current)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                start, end = matches[0]
                date_info['start_date'] = start
                if end.lower() not in ['present', 'current']:
                    date_info['end_date'] = end
                
                # Calculate duration (rough estimate)
                try:
                    start_year = int(re.search(r'\d{4}', start).group())
                    if date_info['end_date']:
                        end_year = int(re.search(r'\d{4}', date_info['end_date']).group())
                    else:
                        end_year = datetime.now().year
                    
                    date_info['duration_months'] = (end_year - start_year) * 12
                except:
                    pass
                
                break
        
        return date_info
    
    def _extract_job_location(self, lines: List[str]) -> str:
        """Extract job location"""
        # Look for location patterns in first few lines
        for line in lines[:3]:
            # Common location indicators
            if re.search(r'\b(Remote|USA|UK|Germany|India|Singapore|New York|San Francisco|London|Berlin)\b', line, re.IGNORECASE):
                return line.strip()
        
        return "Not specified"
    
    def _extract_job_details(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """Extract responsibilities and achievements"""
        responsibilities = []
        achievements = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Clean bullet points
            line = re.sub(r'^[•\-\*]\s*', '', line)
            
            # Identify achievements (contain numbers, percentages, or achievement keywords)
            achievement_indicators = [
                r'\d+%', r'\$\d+', r'\d+x', r'increased', r'improved', r'reduced',
                r'achieved', r'delivered', r'exceeded', r'optimized', r'successful'
            ]
            
            if any(re.search(indicator, line, re.IGNORECASE) for indicator in achievement_indicators):
                achievements.append(line)
            else:
                responsibilities.append(line)
        
        return responsibilities, achievements
    
    def _extract_job_skills(self, text: str) -> List[str]:
        """Extract skills mentioned in job description"""
        skills = []
        text_lower = text.lower()
        
        # Check against skills database
        for skill in self.skills_db.all_skills:
            if skill.lower() in text_lower:
                skills.append(skill)
        
        return skills[:10]  # Limit to most relevant
    
    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information"""
        education_section = self._extract_section_content(text, self.education_indicators)
        
        if not education_section:
            return []
        
        education_list = []
        
        # Split into individual education entries
        edu_blocks = re.split(r'\n\s*\n', education_section)
        
        for block in edu_blocks:
            if not block.strip():
                continue
            
            education = self._parse_education_block(block)
            if education:
                education_list.append(education)
        
        return education_list
    
    def _parse_education_block(self, block: str) -> Optional[Education]:
        """Parse individual education block"""
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Extract degree and field
        degree_line = lines[0]
        degree, field = self._extract_degree_field(degree_line)
        
        # Extract institution
        institution = ""
        for line in lines[1:]:
            if not re.search(r'\d{4}', line):  # Not a year line
                institution = line
                break
        
        # Extract graduation year
        graduation_year = None
        year_pattern = r'\b(19|20)\d{2}\b'
        for line in lines:
            year_match = re.search(year_pattern, line)
            if year_match:
                graduation_year = year_match.group()
                break
        
        # Extract GPA
        gpa = None
        gpa_pattern = r'gpa[:\s]*([0-9.]+)'
        for line in lines:
            gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
            if gpa_match:
                gpa = gpa_match.group(1)
                break
        
        return Education(
            degree=degree or "Unknown",
            field=field or "Unknown",
            institution=institution or "Unknown",
            graduation_year=graduation_year,
            gpa=gpa,
            honors=[]
        )
    
    def _extract_degree_field(self, degree_line: str) -> Tuple[str, str]:
        """Extract degree type and field of study"""
        # Common degree patterns
        degree_patterns = [
            r'(Bachelor|Master|PhD|MBA|BS|MS|BA|MA|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc)\s+(?:of|in)?\s*(.+)',
            r'(Bachelor\'s|Master\'s)\s+(?:degree\s+)?(?:in\s+)?(.+)',
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, degree_line, re.IGNORECASE)
            if match:
                degree = match.group(1)
                field = match.group(2).strip()
                return degree, field
        
        # If no pattern matches, assume the whole line is the degree
        return degree_line, ""
    
    def _extract_certifications(self, text: str) -> List[Certification]:
        """Extract certification information"""
        cert_section = self._extract_section_content(text, ['certifications', 'certificates', 'licenses'])
        
        certifications = []
        
        if cert_section:
            # Parse certification entries
            cert_lines = cert_section.split('\n')
            for line in cert_lines:
                line = line.strip()
                if line and len(line) > 5:
                    # Try to extract cert name and issuer
                    cert = self._parse_certification_line(line)
                    if cert:
                        certifications.append(cert)
        
        # Also look for common certifications in the full text
        common_certs = [
            'CISSP', 'CISM', 'CISA', 'CEH', 'OSCP', 'Security+', 'Network+',
            'AWS Certified', 'Azure Certified', 'Google Cloud Certified',
            'PMP', 'Scrum Master', 'Agile', 'PRINCE2'
        ]
        
        for cert_name in common_certs:
            if cert_name.lower() in text.lower():
                cert = Certification(name=cert_name, issuer="", issue_date=None)
                if cert not in certifications:  # Avoid duplicates
                    certifications.append(cert)
        
        return certifications
    
    def _parse_certification_line(self, line: str) -> Optional[Certification]:
        """Parse individual certification line"""
        # Remove bullet points
        line = re.sub(r'^[•\-\*]\s*', '', line)
        
        # Common patterns: "Cert Name - Issuer (Year)"
        patterns = [
            r'(.+?)\s*[-–]\s*(.+?)\s*\((\d{4})\)',
            r'(.+?)\s*[-–]\s*(.+)',
            r'(.+)'  # Just the certification name
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                name = match.group(1).strip()
                issuer = match.group(2).strip() if match.lastindex >= 2 else ""
                year = match.group(3) if match.lastindex >= 3 else None
                
                return Certification(
                    name=name,
                    issuer=issuer,
                    issue_date=year
                )
        
        return None
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects_section = self._extract_section_content(text, ['projects', 'personal projects', 'key projects'])
        
        projects = []
        
        if projects_section:
            # Split into project blocks
            project_blocks = re.split(r'\n\s*\n', projects_section)
            
            for block in project_blocks:
                if not block.strip():
                    continue
                
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if lines:
                    project_name = lines[0]
                    description = ' '.join(lines[1:]) if len(lines) > 1 else ""
                    
                    # Extract technologies used
                    technologies = self._extract_job_skills(block)
                    
                    projects.append({
                        'name': project_name,
                        'description': description,
                        'technologies': technologies
                    })
        
        return projects
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract spoken languages"""
        languages_section = self._extract_section_content(text, ['languages', 'language skills'])
        
        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Mandarin', 'Japanese', 'Korean', 'Arabic', 'Hindi',
            'Russian', 'Dutch', 'Swedish', 'Norwegian', 'Danish'
        ]
        
        found_languages = []
        
        search_text = languages_section if languages_section else text
        
        for language in common_languages:
            if language.lower() in search_text.lower():
                found_languages.append(language)
        
        return found_languages
    
    def _extract_awards(self, text: str) -> List[str]:
        """Extract awards and honors"""
        awards_section = self._extract_section_content(text, ['awards', 'honors', 'achievements', 'recognition'])
        
        awards = []
        
        if awards_section:
            lines = awards_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5:
                    # Remove bullet points
                    line = re.sub(r'^[•\-\*]\s*', '', line)
                    awards.append(line)
        
        return awards
    
    def _extract_publications(self, text: str) -> List[str]:
        """Extract publications"""
        pub_section = self._extract_section_content(text, ['publications', 'papers', 'research'])
        
        publications = []
        
        if pub_section:
            lines = pub_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:
                    # Remove bullet points
                    line = re.sub(r'^[•\-\*]\s*', '', line)
                    publications.append(line)
        
        return publications
    
    def _calculate_total_experience(self, work_experience: List[WorkExperience]) -> float:
        """Calculate total years of experience"""
        total_months = sum(exp.duration_months for exp in work_experience)
        return total_months / 12.0
    
    def _determine_seniority_level(self, experience_years: float, skills: Dict, work_experience: List[WorkExperience]) -> str:
        """Determine seniority level based on experience and skills"""
        if experience_years < 2:
            return "junior"
        elif experience_years < 5:
            return "mid"
        elif experience_years < 10:
            return "senior"
        else:
            return "lead"
    
    def _determine_primary_domain(self, skills: Dict, work_experience: List[WorkExperience]) -> str:
        """Determine primary domain/field"""
        # Score different domains based on skills and experience
        domain_scores = {}
        
        for category, skill_list in skills.items():
            if skill_list:
                domain_scores[category] = len(skill_list)
        
        # Boost based on job titles
        for exp in work_experience:
            title_lower = exp.title.lower()
            if 'security' in title_lower or 'cyber' in title_lower:
                domain_scores['cybersecurity'] = domain_scores.get('cybersecurity', 0) + 3
            elif 'data' in title_lower:
                domain_scores['data_science'] = domain_scores.get('data_science', 0) + 3
            elif 'mobile' in title_lower or 'ios' in title_lower or 'android' in title_lower:
                domain_scores['mobile_development'] = domain_scores.get('mobile_development', 0) + 3
        
        if not domain_scores:
            return "general"
        
        return max(domain_scores, key=domain_scores.get)
    
    def _calculate_skill_confidence(self, skills: Dict, work_experience: List[WorkExperience], text: str) -> Dict[str, float]:
        """Calculate confidence scores for each skill"""
        skill_confidence = {}
        
        all_skills = self._flatten_skills(skills)
        
        for skill in all_skills:
            confidence = 0.5  # Base confidence
            
            # Boost if mentioned in work experience
            for exp in work_experience:
                if skill.lower() in exp.title.lower():
                    confidence += 0.3
                if skill.lower() in ' '.join(exp.responsibilities + exp.achievements).lower():
                    confidence += 0.2
            
            # Boost if mentioned multiple times
            skill_count = text.lower().count(skill.lower())
            confidence += min(skill_count * 0.1, 0.3)
            
            skill_confidence[skill] = min(confidence, 1.0)
        
        return skill_confidence
    
    def _flatten_skills(self, skills: Dict[str, List[str]]) -> List[str]:
        """Flatten categorized skills into a single list"""
        all_skills = []
        for skill_list in skills.values():
            all_skills.extend(skill_list)
        return all_skills
    
    def save_parsed_resume(self, parsed_resume: ParsedResume, output_dir: str = "data/parsed_resumes"):
        """Save parsed resume to file"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"parsed_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_path / filename
        
        # Convert to dict for JSON serialization
        resume_dict = asdict(parsed_resume)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(resume_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Parsed resume saved to: {filepath}")
        return str(filepath)

def main():
    """Demo function"""
    parser = ResumeParser()
    
    # Example usage
    resume_path = "config/resume.pdf"  # Update with actual path
    
    if Path(resume_path).exists():
        try:
            parsed_resume = parser.parse_resume(resume_path)
            parser.save_parsed_resume(parsed_resume)
            
            print(f"\n📊 PARSING SUMMARY:")
            print(f"   👤 Name: {parsed_resume.contact_info.name}")
            print(f"   📧 Email: {parsed_resume.contact_info.email}")
            print(f"   🎯 Domain: {parsed_resume.primary_domain}")
            print(f"   📈 Experience: {parsed_resume.total_experience_years:.1f} years")
            print(f"   🏆 Level: {parsed_resume.seniority_level}")
            print(f"   🔧 Skills: {len(parser._flatten_skills(parsed_resume.skills))}")
            print(f"   💼 Jobs: {len(parsed_resume.work_experience)}")
            print(f"   🎓 Education: {len(parsed_resume.education)}")
            
        except Exception as e:
            print(f"❌ Error parsing resume: {e}")
    else:
        print(f"❌ Resume file not found: {resume_path}")
        print("💡 Please place your resume at config/resume.pdf")

if __name__ == "__main__":
    main()