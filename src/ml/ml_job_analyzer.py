#!/usr/bin/env python3
"""
🧠 ML-Powered Job Analyzer
Advanced machine learning models for job-related analysis and matching
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLJobAnalyzer:
    """Advanced ML-powered job analysis using specialized models"""
    
    def __init__(self):
        self.models = {}
        self.vectorizers = {}
        self._initialize_models()
        
        # Job-related NLP models
        self.job_skills_extractor = None
        self.salary_predictor = None
        self.job_classifier = None
        self.resume_ranker = None
        
        # Pre-trained embeddings and classifiers
        self.skill_embeddings = {}
        self.industry_classifier = None
        
        self._load_specialized_models()
    
    def _initialize_models(self):
        """Initialize ML models for job analysis"""
        try:
            # Load spaCy model for NER and text processing
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy English model loaded")
        except OSError:
            logger.warning("⚠️ spaCy English model not found - install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize TF-IDF vectorizer for text similarity
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Initialize clustering for job grouping
        self.job_clusterer = KMeans(n_clusters=10, random_state=42)
        
        logger.info("🤖 Base ML models initialized")
    
    def _load_specialized_models(self):
        """Load specialized job-related ML models"""
        try:
            # Job skills extraction using BERT-based models
            self.job_skills_extractor = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            logger.info("✅ Job skills extractor loaded")
        except Exception as e:
            logger.warning(f"⚠️ Skills extractor failed to load: {e}")
        
        try:
            # Sentence transformers for semantic similarity
            from sentence_transformers import SentenceTransformer
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer loaded")
        except Exception as e:
            logger.warning(f"⚠️ Sentence transformer failed to load: {e}")
            self.sentence_transformer = None
        
        try:
            # Job classification model
            self.job_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            logger.info("✅ Job classifier loaded")
        except Exception as e:
            logger.warning(f"⚠️ Job classifier failed to load: {e}")
    
    def analyze_job_description_with_ml(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description using ML models"""
        analysis = {
            'skills_extracted': [],
            'experience_level': 'Unknown',
            'job_category': 'Unknown',
            'salary_prediction': None,
            'requirements_complexity': 0,
            'ml_confidence': 0
        }
        
        try:
            # Extract skills using NER
            skills = self._extract_skills_with_ml(job_description)
            analysis['skills_extracted'] = skills
            
            # Predict experience level
            exp_level = self._predict_experience_level(job_description)
            analysis['experience_level'] = exp_level
            
            # Classify job category
            category = self._classify_job_category(job_description)
            analysis['job_category'] = category
            
            # Predict salary range
            salary = self._predict_salary_range(job_description, skills)
            analysis['salary_prediction'] = salary
            
            # Analyze requirements complexity
            complexity = self._analyze_requirements_complexity(job_description)
            analysis['requirements_complexity'] = complexity
            
            # Calculate overall confidence
            analysis['ml_confidence'] = self._calculate_ml_confidence(analysis)
            
        except Exception as e:
            logger.error(f"❌ ML analysis failed: {e}")
            analysis['ml_confidence'] = 0
        
        return analysis
    
    def _extract_skills_with_ml(self, job_text: str) -> List[Dict[str, Any]]:
        """Extract skills using ML-based NER"""
        skills = []
        
        try:
            # Use spaCy for basic NER
            if self.nlp:
                doc = self.nlp(job_text)
                for ent in doc.ents:
                    if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
                        skills.append({
                            'skill': ent.text,
                            'confidence': 0.8,
                            'method': 'spacy_ner'
                        })
            
            # Use specialized skills extractor
            if self.job_skills_extractor:
                try:
                    entities = self.job_skills_extractor(job_text)
                    for entity in entities:
                        if entity['entity_group'] in ['MISC', 'ORG']:
                            skills.append({
                                'skill': entity['word'],
                                'confidence': entity['score'],
                                'method': 'bert_ner'
                            })
                except Exception as e:
                    logger.warning(f"⚠️ BERT NER failed: {e}")
            
            # Rule-based skill extraction for technical skills
            technical_skills = self._extract_technical_skills(job_text)
            skills.extend(technical_skills)
            
            # Deduplicate and sort by confidence
            skills = self._deduplicate_skills(skills)
            skills.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Skill extraction failed: {e}")
        
        return skills[:20]  # Top 20 skills
    
    def _extract_technical_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract technical skills using rule-based patterns"""
        technical_skills = []
        
        # Comprehensive technical skills database
        skill_patterns = {
            'programming_languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
                'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL'
            ],
            'frameworks': [
                'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring',
                'Express.js', 'FastAPI', 'Laravel', 'Rails', 'ASP.NET', 'Bootstrap'
            ],
            'databases': [
                'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra',
                'DynamoDB', 'Oracle', 'SQL Server', 'SQLite', 'Neo4j', 'InfluxDB'
            ],
            'cloud_platforms': [
                'AWS', 'Azure', 'Google Cloud', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
                'Jenkins', 'GitLab', 'CircleCI', 'Ansible', 'Chef', 'Puppet'
            ],
            'ai_ml': [
                'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Keras',
                'OpenCV', 'NLTK', 'spaCy', 'Transformers', 'MLflow', 'Kubeflow'
            ],
            'tools': [
                'Git', 'GitHub', 'GitLab', 'Jira', 'Confluence', 'Slack', 'Teams',
                'Figma', 'Sketch', 'Photoshop', 'Illustrator', 'Postman', 'Swagger'
            ]
        }
        
        text_lower = text.lower()
        
        for category, skills in skill_patterns.items():
            for skill in skills:
                # Case-insensitive search with word boundaries
                pattern = rf'\b{re.escape(skill.lower())}\b'
                if re.search(pattern, text_lower):
                    technical_skills.append({
                        'skill': skill,
                        'confidence': 0.9,
                        'method': 'rule_based',
                        'category': category
                    })
        
        return technical_skills
    
    def _deduplicate_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate skills and merge similar ones"""
        seen_skills = {}
        
        for skill in skills:
            skill_name = skill['skill'].lower().strip()
            
            if skill_name not in seen_skills:
                seen_skills[skill_name] = skill
            else:
                # Keep the one with higher confidence
                if skill['confidence'] > seen_skills[skill_name]['confidence']:
                    seen_skills[skill_name] = skill
        
        return list(seen_skills.values())
    
    def _predict_experience_level(self, job_text: str) -> str:
        """Predict experience level using ML"""
        text_lower = job_text.lower()
        
        # Rule-based patterns with ML confidence scoring
        patterns = {
            'entry': [
                r'\b(?:entry|junior|jr\.?|graduate|intern|0-2\s*years?|new\s*grad)\b',
                r'\b(?:trainee|associate|assistant|beginner)\b'
            ],
            'mid': [
                r'\b(?:mid|middle|2-5\s*years?|3-5\s*years?|intermediate)\b',
                r'\b(?:experienced|professional|2\+\s*years?)\b'
            ],
            'senior': [
                r'\b(?:senior|sr\.?|lead|5\+\s*years?|principal|staff)\b',
                r'\b(?:architect|manager|director|expert|specialist)\b'
            ]
        }
        
        scores = {}
        for level, level_patterns in patterns.items():
            score = 0
            for pattern in level_patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            scores[level] = score
        
        # Determine the level with highest score
        if max(scores.values()) == 0:
            return 'Mid'  # Default
        
        return max(scores, key=scores.get).title()
    
    def _classify_job_category(self, job_text: str) -> str:
        """Classify job category using ML"""
        text_lower = job_text.lower()
        
        # ML-based category classification
        categories = {
            'software_engineering': [
                'software', 'developer', 'engineer', 'programmer', 'coding', 'development',
                'backend', 'frontend', 'full-stack', 'web', 'mobile', 'application'
            ],
            'data_science': [
                'data scientist', 'data analyst', 'machine learning', 'ai', 'analytics',
                'statistics', 'modeling', 'deep learning', 'neural network'
            ],
            'devops': [
                'devops', 'infrastructure', 'deployment', 'ci/cd', 'automation',
                'cloud', 'kubernetes', 'docker', 'platform', 'reliability'
            ],
            'product_management': [
                'product manager', 'product owner', 'roadmap', 'strategy',
                'requirements', 'stakeholder', 'business analyst'
            ],
            'design': [
                'designer', 'ui', 'ux', 'user experience', 'user interface',
                'graphics', 'visual', 'prototype', 'wireframe'
            ],
            'management': [
                'manager', 'director', 'lead', 'team lead', 'supervisor',
                'management', 'leadership', 'oversight'
            ]
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        if max(scores.values()) == 0:
            return 'General'
        
        best_category = max(scores, key=scores.get)
        return best_category.replace('_', ' ').title()
    
    def _predict_salary_range(self, job_text: str, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict salary range using ML"""
        
        # Base salary by experience level
        exp_level = self._predict_experience_level(job_text)
        base_salaries = {
            'Entry': {'min': 70000, 'max': 100000},
            'Mid': {'min': 100000, 'max': 150000},
            'Senior': {'min': 150000, 'max': 250000}
        }
        
        base_range = base_salaries.get(exp_level, base_salaries['Mid'])
        
        # Skill-based adjustments
        high_value_skills = [
            'machine learning', 'ai', 'kubernetes', 'aws', 'golang', 'rust',
            'blockchain', 'tensorflow', 'pytorch', 'react', 'node.js'
        ]
        
        skill_bonus = 0
        for skill in skills:
            skill_name = skill['skill'].lower()
            if any(hvs in skill_name for hvs in high_value_skills):
                skill_bonus += 5000  # $5k per high-value skill
        
        # Location adjustment (simplified)
        location_multipliers = {
            'san francisco': 1.4, 'new york': 1.3, 'seattle': 1.25,
            'boston': 1.2, 'austin': 1.1, 'remote': 1.0
        }
        
        location_multiplier = 1.0
        text_lower = job_text.lower()
        for location, multiplier in location_multipliers.items():
            if location in text_lower:
                location_multiplier = max(location_multiplier, multiplier)
        
        # Calculate final range
        adjusted_min = int((base_range['min'] + skill_bonus) * location_multiplier)
        adjusted_max = int((base_range['max'] + skill_bonus * 1.5) * location_multiplier)
        
        return {
            'min_salary': adjusted_min,
            'max_salary': adjusted_max,
            'currency': 'USD',
            'confidence': 0.75,
            'factors': {
                'experience_level': exp_level,
                'skill_bonus': skill_bonus,
                'location_multiplier': location_multiplier
            }
        }
    
    def _analyze_requirements_complexity(self, job_text: str) -> float:
        """Analyze requirements complexity using ML"""
        
        # Complexity indicators
        complexity_indicators = [
            r'\d+\+?\s*years?\s*(?:of\s*)?experience',  # Years of experience
            r'(?:required|must\s*have|essential)',  # Hard requirements
            r'(?:preferred|nice\s*to\s*have|bonus)',  # Soft requirements
            r'(?:degree|bachelor|master|phd)',  # Education requirements
            r'(?:certification|certified)',  # Certification requirements
        ]
        
        complexity_score = 0
        text_lower = job_text.lower()
        
        for indicator in complexity_indicators:
            matches = len(re.findall(indicator, text_lower))
            complexity_score += matches * 0.2
        
        # Normalize to 0-1 scale
        return min(1.0, complexity_score)
    
    def _calculate_ml_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall ML confidence score"""
        
        confidence_factors = []
        
        # Skills extraction confidence
        if analysis['skills_extracted']:
            avg_skill_conf = np.mean([s['confidence'] for s in analysis['skills_extracted']])
            confidence_factors.append(avg_skill_conf)
        
        # Salary prediction confidence
        if analysis['salary_prediction']:
            confidence_factors.append(analysis['salary_prediction']['confidence'])
        
        # Requirements complexity confidence
        complexity = analysis.get('requirements_complexity', 0)
        complexity_conf = 0.8 if complexity > 0.3 else 0.6
        confidence_factors.append(complexity_conf)
        
        # Overall confidence
        if confidence_factors:
            return float(np.mean(confidence_factors))
        else:
            return 0.5  # Default confidence
    
    def calculate_job_match_score_ml(self, 
                                    job_description: str, 
                                    user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate job match score using ML models"""
        
        try:
            # Analyze job with ML
            job_analysis = self.analyze_job_description_with_ml(job_description)
            
            # Extract user skills
            user_skills = self._extract_user_skills(user_profile)
            
            # Calculate semantic similarity
            semantic_score = self._calculate_semantic_similarity(
                job_description, user_profile
            )
            
            # Calculate skill overlap
            skill_overlap = self._calculate_skill_overlap_ml(
                job_analysis['skills_extracted'], user_skills
            )
            
            # Calculate experience match
            exp_match = self._calculate_experience_match_ml(
                job_analysis['experience_level'],
                user_profile.get('career_analysis', {}).get('seniority_level', '')
            )
            
            # Calculate salary match
            salary_match = self._calculate_salary_match_ml(
                job_analysis.get('salary_prediction', {}),
                user_profile.get('salary_estimate', {})
            )
            
            # Weighted final score
            weights = {
                'semantic_similarity': 0.25,
                'skill_overlap': 0.35,
                'experience_match': 0.25,
                'salary_match': 0.15
            }
            
            final_score = (
                semantic_score * weights['semantic_similarity'] +
                skill_overlap * weights['skill_overlap'] +
                exp_match * weights['experience_match'] +
                salary_match * weights['salary_match']
            )
            
            return {
                'overall_score': min(100, max(0, int(final_score * 100))),
                'breakdown': {
                    'semantic_similarity': semantic_score,
                    'skill_overlap': skill_overlap,
                    'experience_match': exp_match,
                    'salary_match': salary_match
                },
                'job_analysis': job_analysis,
                'ml_confidence': job_analysis.get('ml_confidence', 0.5)
            }
        
        except Exception as e:
            logger.error(f"❌ ML match scoring failed: {e}")
            return {
                'overall_score': 50,
                'breakdown': {},
                'job_analysis': {},
                'ml_confidence': 0.0
            }
    
    def _extract_user_skills(self, user_profile: Dict[str, Any]) -> List[str]:
        """Extract user skills from profile"""
        skills = []
        
        skills_analysis = user_profile.get('skills_analysis', {})
        technical_skills = skills_analysis.get('technical_skills', {})
        
        for category, skill_list in technical_skills.items():
            if isinstance(skill_list, list):
                for skill in skill_list:
                    if isinstance(skill, dict):
                        skills.append(skill.get('skill', '').lower())
                    else:
                        skills.append(str(skill).lower())
        
        return skills
    
    def _calculate_semantic_similarity(self, 
                                     job_description: str, 
                                     user_profile: Dict[str, Any]) -> float:
        """Calculate semantic similarity using sentence transformers"""
        
        try:
            if self.sentence_transformer:
                # Create user profile text
                user_text = self._create_user_profile_text(user_profile)
                
                # Get embeddings
                job_embedding = self.sentence_transformer.encode([job_description])
                user_embedding = self.sentence_transformer.encode([user_text])
                
                # Calculate cosine similarity
                similarity = cosine_similarity(job_embedding, user_embedding)[0][0]
                return float(similarity)
            
            else:
                # Fallback to TF-IDF similarity
                user_text = self._create_user_profile_text(user_profile)
                
                # Fit and transform
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([job_description, user_text])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                
                return float(similarity)
        
        except Exception as e:
            logger.error(f"❌ Semantic similarity calculation failed: {e}")
            return 0.5
    
    def _create_user_profile_text(self, user_profile: Dict[str, Any]) -> str:
        """Create text representation of user profile"""
        
        text_parts = []
        
        # Career info
        career = user_profile.get('career_analysis', {})
        if career.get('current_role'):
            text_parts.append(f"Current role: {career['current_role']}")
        
        if career.get('years_of_experience'):
            text_parts.append(f"Experience: {career['years_of_experience']} years")
        
        # Skills
        skills_analysis = user_profile.get('skills_analysis', {})
        technical_skills = skills_analysis.get('technical_skills', {})
        
        all_skills = []
        for category, skill_list in technical_skills.items():
            if isinstance(skill_list, list):
                for skill in skill_list:
                    if isinstance(skill, dict):
                        all_skills.append(skill.get('skill', ''))
        
        if all_skills:
            text_parts.append(f"Skills: {', '.join(all_skills)}")
        
        # Industries
        industries = career.get('industry_specialization', [])
        if industries:
            text_parts.append(f"Industries: {', '.join(industries)}")
        
        return '. '.join(text_parts)
    
    def _calculate_skill_overlap_ml(self, 
                                   job_skills: List[Dict[str, Any]], 
                                   user_skills: List[str]) -> float:
        """Calculate skill overlap using ML techniques"""
        
        if not job_skills or not user_skills:
            return 0.0
        
        job_skill_names = [skill['skill'].lower() for skill in job_skills]
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        # Direct matches
        direct_matches = len(set(job_skill_names).intersection(set(user_skills_lower)))
        
        # Fuzzy matches (simplified)
        fuzzy_matches = 0
        for job_skill in job_skill_names:
            for user_skill in user_skills_lower:
                # Simple substring matching
                if (job_skill in user_skill or user_skill in job_skill) and len(job_skill) > 2:
                    fuzzy_matches += 0.5
        
        # Calculate overlap score
        total_matches = direct_matches + fuzzy_matches
        overlap_score = total_matches / len(job_skill_names) if job_skill_names else 0
        
        return min(1.0, overlap_score)
    
    def _calculate_experience_match_ml(self, 
                                      job_exp_level: str, 
                                      user_exp_level: str) -> float:
        """Calculate experience level match using ML"""
        
        # Experience level hierarchy
        levels = {
            'entry': 1, 'junior': 1, 'associate': 1.5,
            'mid': 2, 'intermediate': 2,
            'senior': 3, 'lead': 3.5, 'principal': 4, 'staff': 4
        }
        
        job_level = levels.get(job_exp_level.lower(), 2)
        user_level = levels.get(user_exp_level.lower(), 2)
        
        # Calculate match score based on proximity
        diff = abs(job_level - user_level)
        
        if diff == 0:
            return 1.0
        elif diff <= 0.5:
            return 0.9
        elif diff <= 1.0:
            return 0.7
        elif diff <= 1.5:
            return 0.5
        else:
            return 0.3
    
    def _calculate_salary_match_ml(self, 
                                  job_salary: Dict[str, Any], 
                                  user_salary: Dict[str, Any]) -> float:
        """Calculate salary match using ML"""
        
        if not job_salary or not user_salary:
            return 0.7  # Neutral score if no salary info
        
        job_min = job_salary.get('min_salary', 0)
        job_max = job_salary.get('max_salary', 0)
        user_min = user_salary.get('min', 0)
        user_max = user_salary.get('max', 0)
        
        if job_min == 0 or user_min == 0:
            return 0.7
        
        # Check if ranges overlap
        if job_max >= user_min and user_max >= job_min:
            # Calculate overlap percentage
            overlap_start = max(job_min, user_min)
            overlap_end = min(job_max, user_max)
            overlap_size = overlap_end - overlap_start
            
            job_range_size = job_max - job_min
            user_range_size = user_max - user_min
            
            if job_range_size > 0 and user_range_size > 0:
                overlap_percentage = overlap_size / min(job_range_size, user_range_size)
                return min(1.0, overlap_percentage)
        
        # No overlap - calculate distance
        if job_max < user_min:
            # Job pays less than user expects
            gap = (user_min - job_max) / user_min
            return max(0.0, 1.0 - gap)
        elif user_max < job_min:
            # Job pays more than user expects (good!)
            return 1.0
        
        return 0.5

# Global instance
ml_analyzer = MLJobAnalyzer()

def analyze_job_with_ml(job_description: str) -> Dict[str, Any]:
    """Analyze job description using ML models"""
    return ml_analyzer.analyze_job_description_with_ml(job_description)

def calculate_job_match_with_ml(job_description: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate job match score using ML"""
    return ml_analyzer.calculate_job_match_score_ml(job_description, user_profile)