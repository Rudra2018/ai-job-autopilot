#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Smart Duplicate Detection System
Prevents duplicate job applications using intelligent matching algorithms
"""

import os
import json
import logging
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobApplication:
    job_id: str
    job_title: str
    company: str
    job_url: str
    application_date: str
    job_description: str = ""
    location: str = ""
    salary_range: str = ""
    job_source: str = ""  # LinkedIn, Indeed, etc.
    application_status: str = "applied"  # applied, rejected, interviewed, etc.
    similarity_score: float = 0.0
    duplicate_of: str = ""  # ID of original job if this is a duplicate

@dataclass
class DuplicateMatch:
    job1_id: str
    job2_id: str
    similarity_score: float
    match_type: str  # exact, high_similarity, potential
    matching_factors: List[str]
    confidence: float

class SmartDuplicateDetector:
    def __init__(self, applications_db_path: str = "data/job_applications.json"):
        self.db_path = Path(applications_db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Load existing applications
        self.applications = self._load_applications()
        
        # Initialize semantic similarity model
        try:
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Similarity model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load similarity model: {e}")
            self.similarity_model = None
        
        # Similarity thresholds
        self.thresholds = {
            "exact_match": 0.95,
            "high_similarity": 0.85,
            "potential_duplicate": 0.70,
            "title_similarity": 0.8,
            "company_similarity": 0.9
        }
        
        # Common job title variations
        self.title_synonyms = {
            "software engineer": ["developer", "programmer", "software developer", "engineer"],
            "data scientist": ["data analyst", "ml engineer", "ai engineer"],
            "product manager": ["pm", "product owner", "product lead"],
            "frontend": ["front-end", "front end", "ui", "client-side"],
            "backend": ["back-end", "back end", "server-side", "api"],
            "fullstack": ["full-stack", "full stack", "full-stack developer"],
            "senior": ["sr", "lead", "principal"],
            "junior": ["jr", "entry level", "associate"]
        }
        
        # Company name variations and aliases
        self.company_aliases = self._load_company_aliases()
    
    def _load_applications(self) -> Dict[str, JobApplication]:
        """Load job applications from database"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    applications = {}
                    for job_id, app_data in data.items():
                        applications[job_id] = JobApplication(**app_data)
                    return applications
            return {}
        except Exception as e:
            logger.error(f"Error loading applications database: {e}")
            return {}
    
    def _save_applications(self):
        """Save applications to database"""
        try:
            data = {}
            for job_id, app in self.applications.items():
                data[job_id] = asdict(app)
            
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving applications database: {e}")
    
    def _load_company_aliases(self) -> Dict[str, List[str]]:
        """Load company name aliases and variations"""
        return {
            "google": ["alphabet", "google llc", "google inc"],
            "meta": ["facebook", "meta platforms", "facebook inc"],
            "amazon": ["amazon web services", "aws", "amazon.com"],
            "microsoft": ["msft", "microsoft corporation"],
            "apple": ["apple inc", "apple computer"],
            "netflix": ["netflix inc", "netflix.com"],
            "tesla": ["tesla inc", "tesla motors"],
            "uber": ["uber technologies", "uber inc"],
            "airbnb": ["airbnb inc", "airbnb.com"]
        }
    
    def generate_job_id(self, job_title: str, company: str, job_url: str = "") -> str:
        """Generate unique job ID"""
        # Use URL if available, otherwise use title + company
        if job_url:
            # Extract job ID from common job board URLs
            job_id = self._extract_job_id_from_url(job_url)
            if job_id:
                return job_id
        
        # Fallback: create hash from title + company
        content = f"{job_title.lower().strip()}_{company.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_job_id_from_url(self, url: str) -> Optional[str]:
        """Extract job ID from job board URLs"""
        if not url:
            return None
        
        # LinkedIn job URLs
        linkedin_match = re.search(r'linkedin.com/jobs/view/(\d+)', url)
        if linkedin_match:
            return f"linkedin_{linkedin_match.group(1)}"
        
        # Indeed job URLs
        indeed_match = re.search(r'indeed.com/.*jk=([a-f0-9]+)', url)
        if indeed_match:
            return f"indeed_{indeed_match.group(1)}"
        
        # Glassdoor job URLs
        glassdoor_match = re.search(r'glassdoor.com/.*jobListingId=(\d+)', url)
        if glassdoor_match:
            return f"glassdoor_{glassdoor_match.group(1)}"
        
        # Generic fallback - use domain + path hash
        parsed = urlparse(url)
        if parsed.netloc:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            domain = parsed.netloc.replace('www.', '')
            return f"{domain}_{url_hash}"
        
        return None
    
    def normalize_job_title(self, title: str) -> str:
        """Normalize job title for better matching"""
        title = title.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ["looking for", "hiring", "urgent", "immediate"]
        suffixes_to_remove = ["- remote", "- hybrid", "(remote)", "(hybrid)"]
        
        for prefix in prefixes_to_remove:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        for suffix in suffixes_to_remove:
            if title.endswith(suffix):
                title = title[:-len(suffix)].strip()
        
        # Replace synonyms
        for canonical, synonyms in self.title_synonyms.items():
            for synonym in synonyms:
                title = title.replace(synonym, canonical)
        
        return title
    
    def normalize_company_name(self, company: str) -> str:
        """Normalize company name for better matching"""
        company = company.lower().strip()
        
        # Remove common suffixes
        suffixes = ["inc", "inc.", "llc", "ltd", "corp", "corporation", "company", "co."]
        for suffix in suffixes:
            if company.endswith(suffix):
                company = company[:-len(suffix)].strip()
        
        # Check aliases
        for canonical, aliases in self.company_aliases.items():
            if company in aliases or company == canonical:
                return canonical
        
        return company
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        # Use sequence matcher for basic similarity
        basic_similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # Use semantic similarity if model available
        if self.similarity_model:
            try:
                embeddings = self.similarity_model.encode([text1, text2])
                semantic_similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                # Combine both similarities
                return (basic_similarity + semantic_similarity) / 2
            except Exception as e:
                logger.warning(f"Semantic similarity calculation failed: {e}")
        
        return basic_similarity
    
    def find_duplicates(self, job_application: JobApplication) -> List[DuplicateMatch]:
        """Find potential duplicates for a given job application"""
        duplicates = []
        
        for existing_id, existing_app in self.applications.items():
            if existing_id == job_application.job_id:
                continue
            
            # Calculate various similarity metrics
            title_similarity = self.calculate_text_similarity(
                self.normalize_job_title(job_application.job_title),
                self.normalize_job_title(existing_app.job_title)
            )
            
            company_similarity = self.calculate_text_similarity(
                self.normalize_company_name(job_application.company),
                self.normalize_company_name(existing_app.company)
            )
            
            # URL similarity (if both have URLs)
            url_similarity = 0.0
            if job_application.job_url and existing_app.job_url:
                url_similarity = self.calculate_text_similarity(
                    job_application.job_url, existing_app.job_url
                )
            
            # Job description similarity (if available)
            desc_similarity = 0.0
            if job_application.job_description and existing_app.job_description:
                desc_similarity = self.calculate_text_similarity(
                    job_application.job_description[:500],
                    existing_app.job_description[:500]
                )
            
            # Determine match type and overall confidence
            matching_factors = []
            overall_similarity = 0.0
            
            # Exact URL match
            if (job_application.job_url and existing_app.job_url and 
                job_application.job_url == existing_app.job_url):
                match_type = "exact"
                overall_similarity = 1.0
                matching_factors.append("identical_url")
            
            # High similarity match
            elif (title_similarity >= self.thresholds["title_similarity"] and 
                  company_similarity >= self.thresholds["company_similarity"]):
                match_type = "high_similarity"
                overall_similarity = (title_similarity + company_similarity) / 2
                matching_factors.extend(["title_match", "company_match"])
                
                if desc_similarity > 0.7:
                    matching_factors.append("description_match")
                    overall_similarity = (overall_similarity + desc_similarity) / 2
            
            # Potential duplicate
            elif (title_similarity >= self.thresholds["potential_duplicate"] and 
                  company_similarity >= self.thresholds["potential_duplicate"]):
                match_type = "potential"
                overall_similarity = (title_similarity + company_similarity) / 2
                matching_factors.extend(["similar_title", "similar_company"])
            
            else:
                continue  # No significant similarity
            
            # Create duplicate match
            if overall_similarity >= self.thresholds["potential_duplicate"]:
                duplicate = DuplicateMatch(
                    job1_id=job_application.job_id,
                    job2_id=existing_id,
                    similarity_score=overall_similarity,
                    match_type=match_type,
                    matching_factors=matching_factors,
                    confidence=overall_similarity
                )
                duplicates.append(duplicate)
        
        # Sort by similarity score (highest first)
        duplicates.sort(key=lambda x: x.similarity_score, reverse=True)
        return duplicates
    
    def check_if_duplicate(self, 
                          job_title: str, 
                          company: str, 
                          job_url: str = "",
                          job_description: str = "") -> Tuple[bool, Optional[DuplicateMatch]]:
        """
        Check if a job is a duplicate of an existing application
        
        Returns:
            Tuple of (is_duplicate, duplicate_match_if_found)
        """
        
        # Create temporary job application for comparison
        temp_job = JobApplication(
            job_id=self.generate_job_id(job_title, company, job_url),
            job_title=job_title,
            company=company,
            job_url=job_url,
            job_description=job_description,
            application_date=datetime.now().isoformat()
        )
        
        # Find duplicates
        duplicates = self.find_duplicates(temp_job)
        
        if duplicates:
            best_match = duplicates[0]  # Highest similarity
            
            # Determine if it's a definitive duplicate
            is_duplicate = (
                best_match.match_type == "exact" or
                best_match.similarity_score >= self.thresholds["high_similarity"]
            )
            
            return is_duplicate, best_match
        
        return False, None
    
    def add_application(self, 
                       job_title: str, 
                       company: str, 
                       job_url: str = "",
                       job_description: str = "",
                       location: str = "",
                       salary_range: str = "",
                       job_source: str = "") -> Tuple[bool, JobApplication]:
        """
        Add a job application to the database
        
        Returns:
            Tuple of (was_added, job_application)
            was_added is False if it's a duplicate
        """
        
        # Check for duplicates first
        is_duplicate, duplicate_match = self.check_if_duplicate(
            job_title, company, job_url, job_description
        )
        
        if is_duplicate and duplicate_match:
            logger.info(f"Duplicate detected: {job_title} at {company}")
            logger.info(f"Similar to existing application: {duplicate_match.job2_id}")
            logger.info(f"Similarity: {duplicate_match.similarity_score:.3f}")
            
            # Return the existing application
            existing_app = self.applications[duplicate_match.job2_id]
            return False, existing_app
        
        # Create new job application
        job_id = self.generate_job_id(job_title, company, job_url)
        
        new_application = JobApplication(
            job_id=job_id,
            job_title=job_title,
            company=company,
            job_url=job_url,
            job_description=job_description,
            location=location,
            salary_range=salary_range,
            job_source=job_source,
            application_date=datetime.now().isoformat(),
            application_status="applied"
        )
        
        # Mark potential duplicates
        if duplicate_match and duplicate_match.similarity_score >= self.thresholds["potential_duplicate"]:
            new_application.duplicate_of = duplicate_match.job2_id
            new_application.similarity_score = duplicate_match.similarity_score
        
        # Add to database
        self.applications[job_id] = new_application
        self._save_applications()
        
        logger.info(f"Added new application: {job_title} at {company} (ID: {job_id})")
        return True, new_application
    
    def update_application_status(self, job_id: str, status: str):
        """Update application status"""
        if job_id in self.applications:
            self.applications[job_id].application_status = status
            self._save_applications()
            logger.info(f"Updated application {job_id} status to: {status}")
    
    def get_application_stats(self) -> Dict:
        """Get application statistics"""
        if not self.applications:
            return {"total_applications": 0}
        
        stats = {
            "total_applications": len(self.applications),
            "by_status": {},
            "by_company": {},
            "by_source": {},
            "duplicates_detected": 0,
            "recent_applications": 0  # Last 7 days
        }
        
        recent_cutoff = datetime.now() - timedelta(days=7)
        
        for app in self.applications.values():
            # Status stats
            status = app.application_status
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Company stats
            company = app.company
            stats["by_company"][company] = stats["by_company"].get(company, 0) + 1
            
            # Source stats
            source = app.job_source or "unknown"
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            
            # Duplicates
            if app.duplicate_of:
                stats["duplicates_detected"] += 1
            
            # Recent applications
            try:
                app_date = datetime.fromisoformat(app.application_date.replace('Z', '+00:00'))
                if app_date >= recent_cutoff:
                    stats["recent_applications"] += 1
            except:
                pass
        
        return stats
    
    def get_potential_duplicates(self) -> List[DuplicateMatch]:
        """Get all potential duplicates in the database"""
        all_duplicates = []
        
        processed_pairs = set()
        
        for app in self.applications.values():
            duplicates = self.find_duplicates(app)
            for dup in duplicates:
                # Avoid duplicate pairs (A->B and B->A)
                pair_key = tuple(sorted([dup.job1_id, dup.job2_id]))
                if pair_key not in processed_pairs:
                    all_duplicates.append(dup)
                    processed_pairs.add(pair_key)
        
        # Sort by similarity score
        all_duplicates.sort(key=lambda x: x.similarity_score, reverse=True)
        return all_duplicates
    
    def cleanup_old_applications(self, days_old: int = 30):
        """Remove applications older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        to_remove = []
        for job_id, app in self.applications.items():
            try:
                app_date = datetime.fromisoformat(app.application_date.replace('Z', '+00:00'))
                if app_date < cutoff_date and app.application_status in ["rejected", "no_response"]:
                    to_remove.append(job_id)
            except:
                continue
        
        for job_id in to_remove:
            del self.applications[job_id]
            logger.info(f"Removed old application: {job_id}")
        
        if to_remove:
            self._save_applications()
            logger.info(f"Cleaned up {len(to_remove)} old applications")


def main():
    """Demo the Smart Duplicate Detector"""
    print("🤖 Smart Duplicate Detector Demo")
    print("=" * 50)
    
    # Initialize detector
    detector = SmartDuplicateDetector()
    
    # Sample job applications
    sample_jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "Google",
            "url": "https://linkedin.com/jobs/view/12345",
            "description": "We are looking for a senior software engineer with Python and React experience."
        },
        {
            "title": "Sr. Software Developer",  # Similar to above
            "company": "Alphabet",  # Same as Google
            "url": "https://careers.google.com/jobs/123",
            "description": "Senior developer position requiring Python and React skills."
        },
        {
            "title": "Frontend Engineer",
            "company": "Meta",
            "url": "https://linkedin.com/jobs/view/67890",
            "description": "Frontend engineer role working with React and TypeScript."
        },
        {
            "title": "React Developer",  # Different but related
            "company": "Facebook",  # Same as Meta
            "url": "",
            "description": "React developer position for social media platform."
        }
    ]
    
    print("\\nAdding sample job applications...")
    for i, job in enumerate(sample_jobs, 1):
        print(f"\\n{i}. Adding: {job['title']} at {job['company']}")
        
        was_added, application = detector.add_application(
            job_title=job['title'],
            company=job['company'],
            job_url=job['url'],
            job_description=job['description'],
            job_source="demo"
        )
        
        if was_added:
            print(f"   ✅ Added successfully (ID: {application.job_id})")
        else:
            print(f"   ❌ Duplicate detected! Similar to: {application.job_id}")
            print(f"   Similarity score: {application.similarity_score:.3f}")
    
    # Show statistics
    print(f"\\n📊 Application Statistics:")
    stats = detector.get_application_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Show potential duplicates
    print(f"\\n🔍 Potential Duplicates Found:")
    duplicates = detector.get_potential_duplicates()
    for i, dup in enumerate(duplicates, 1):
        app1 = detector.applications[dup.job1_id]
        app2 = detector.applications[dup.job2_id]
        print(f"   {i}. {app1.job_title} at {app1.company}")
        print(f"      ↔️  {app2.job_title} at {app2.company}")
        print(f"      Similarity: {dup.similarity_score:.3f} ({dup.match_type})")
        print(f"      Factors: {', '.join(dup.matching_factors)}")
        print()


if __name__ == "__main__":
    main()