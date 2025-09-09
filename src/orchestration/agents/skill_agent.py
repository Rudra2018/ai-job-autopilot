"""
Skill Agent Implementation
Handles skill extraction and analysis from parsed resume data using NLP models.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import spacy
    SPACY_AVAILABLE = True
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    nlp = None

from .base_agent import BaseAgent, ProcessingResult

class SkillAgent(BaseAgent):
    """
    Skill Agent responsible for extracting and analyzing skills from parsed resume data.
    Uses NLP models to identify technical skills, soft skills, and calculate experience.
    """
    
    def _setup_agent_specific_config(self):
        """Setup Skill Agent specific configurations."""
        
        if not SPACY_AVAILABLE:
            self.logger.warning("spaCy not available, using basic skill extraction")
        
        # Load skill taxonomies and patterns
        self.technical_skills_patterns = self._load_technical_skill_patterns()
        self.soft_skills_patterns = self._load_soft_skill_patterns()
        self.industry_terms = self._load_industry_terms()
        self.skill_synonyms = self._load_skill_synonyms()
        
        # Experience calculation patterns
        self.experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?(.+)',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?(.+)',
            r'(.+)\s+for\s+(\d+)\+?\s*years?',
            r'(.+)\s+since\s+(\d{4})',
            r'(\d{4})\s*-\s*(?:present|current|\d{4})\s*:?\s*(.+)'
        ]
        
        self.logger.info("Skill Agent initialized with NLP capabilities")
    
    def _load_technical_skill_patterns(self) -> Dict[str, List[str]]:
        """Load technical skill patterns and categories."""
        
        return {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
                'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
                'html', 'css', 'bash', 'shell', 'powershell'
            ],
            'frameworks_libraries': [
                'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
                'spring', 'spring boot', 'hibernate', 'jquery', 'bootstrap',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'sqlite', 'oracle', 'sql server', 'cassandra', 'dynamodb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean',
                'kubernetes', 'docker', 'jenkins', 'terraform', 'ansible'
            ],
            'tools_technologies': [
                'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
                'slack', 'teams', 'zoom', 'figma', 'sketch', 'photoshop',
                'illustrator', 'unity', 'unreal', 'blender'
            ]
        }
    
    def _load_soft_skill_patterns(self) -> List[str]:
        """Load soft skill patterns."""
        
        return [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'critical thinking', 'creativity', 'adaptability', 'time management',
            'project management', 'collaboration', 'negotiation', 'presentation',
            'public speaking', 'mentoring', 'coaching', 'training', 'teaching',
            'analytical thinking', 'strategic planning', 'decision making'
        ]
    
    def _load_industry_terms(self) -> Dict[str, List[str]]:
        """Load industry-specific terminology."""
        
        return {
            'software_engineering': [
                'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'microservices',
                'api', 'rest', 'graphql', 'mvc', 'mvp', 'solid principles'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'neural networks', 'nlp',
                'computer vision', 'data mining', 'big data', 'analytics',
                'statistics', 'regression', 'classification', 'clustering'
            ],
            'product_management': [
                'product roadmap', 'user stories', 'acceptance criteria',
                'market research', 'user experience', 'product strategy',
                'stakeholder management', 'go-to-market', 'kpi', 'metrics'
            ]
        }
    
    def _load_skill_synonyms(self) -> Dict[str, List[str]]:
        """Load skill synonyms for better matching."""
        
        return {
            'javascript': ['js', 'ecmascript', 'es6', 'es2015'],
            'python': ['py'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'user interface': ['ui', 'frontend', 'front-end'],
            'user experience': ['ux'],
            'database': ['db', 'data storage'],
            'application programming interface': ['api'],
            'continuous integration': ['ci'],
            'continuous deployment': ['cd']
        }
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate skill extraction input data."""
        
        if not isinstance(input_data, dict):
            return {'valid': False, 'errors': ['Input must be a dictionary']}
        
        if 'resume_data' not in input_data:
            return {'valid': False, 'errors': ['Missing resume_data field']}
        
        resume_data = input_data['resume_data']
        if not isinstance(resume_data, dict):
            return {'valid': False, 'errors': ['resume_data must be a dictionary']}
        
        # Check for required sections
        required_sections = ['personal_information', 'work_experience']
        missing_sections = [s for s in required_sections if s not in resume_data]
        
        if missing_sections:
            return {
                'valid': False, 
                'errors': [f'Missing required sections: {", ".join(missing_sections)}']
            }
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Dict[str, Any]) -> ProcessingResult:
        """Extract and analyze skills from resume data."""
        
        resume_data = input_data['resume_data']
        extraction_config = input_data.get('extraction_config', {})
        
        # Extract skills from different resume sections
        extracted_skills = await self._extract_skills_comprehensive(resume_data, extraction_config)
        
        # Calculate experience for each skill
        skills_with_experience = await self._calculate_skill_experience(extracted_skills, resume_data)
        
        # Assess skill strengths
        skills_with_strength = await self._assess_skill_strengths(skills_with_experience, resume_data)
        
        # Organize and categorize skills
        final_results = await self._organize_skill_results(skills_with_strength, resume_data)
        
        # Calculate overall metrics
        overall_confidence = self._calculate_overall_confidence(final_results)
        
        return ProcessingResult(
            success=True,
            result=final_results,
            confidence=overall_confidence,
            processing_time=0.0,  # Will be set by base class
            metadata={
                'total_skills_found': len(final_results.get('all_skills', [])),
                'technical_skills_count': len(final_results.get('technical_skills', [])),
                'soft_skills_count': len(final_results.get('soft_skills', [])),
                'nlp_method': 'spacy' if SPACY_AVAILABLE else 'pattern_matching'
            }
        )
    
    async def _extract_skills_comprehensive(self, resume_data: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills from all resume sections."""
        
        all_skills = []
        
        # Extract from explicit skills section
        if 'skills' in resume_data:
            skills_section = resume_data['skills']
            
            for category, skills_list in skills_section.items():
                if isinstance(skills_list, list):
                    for skill in skills_list:
                        if skill and skill.strip():
                            all_skills.append({
                                'name': skill.strip(),
                                'source': 'skills_section',
                                'category': category,
                                'confidence': 0.9,
                                'contexts': [f'Listed in {category}']
                            })
        
        # Extract from work experience descriptions
        work_experience = resume_data.get('work_experience', [])
        for i, job in enumerate(work_experience):
            job_skills = self._extract_skills_from_job_description(job, i)
            all_skills.extend(job_skills)
        
        # Extract from project descriptions
        projects = resume_data.get('projects', [])
        for i, project in enumerate(projects):
            project_skills = self._extract_skills_from_project(project, i)
            all_skills.extend(project_skills)
        
        # Extract from professional summary
        prof_summary = resume_data.get('professional_summary', {})
        if isinstance(prof_summary, dict) and prof_summary.get('summary'):
            summary_skills = self._extract_skills_from_text(
                prof_summary['summary'], 'professional_summary'
            )
            all_skills.extend(summary_skills)
        
        # Deduplicate and merge skills
        deduplicated_skills = self._deduplicate_skills(all_skills)
        
        return deduplicated_skills
    
    def _extract_skills_from_job_description(self, job: Dict[str, Any], job_index: int) -> List[Dict[str, Any]]:
        """Extract skills from job description and achievements."""
        
        skills = []
        job_text = ""
        
        # Combine job description and achievements
        if job.get('description'):
            job_text += job['description'] + " "
        
        if job.get('achievements'):
            job_text += " ".join(job['achievements']) + " "
        
        if job.get('technologies'):
            for tech in job['technologies']:
                skills.append({
                    'name': tech.strip(),
                    'source': 'work_experience',
                    'category': 'technical',
                    'confidence': 0.85,
                    'contexts': [f"Used at {job.get('company', 'Unknown Company')}"],
                    'job_context': {
                        'company': job.get('company'),
                        'position': job.get('position'),
                        'start_date': job.get('start_date'),
                        'end_date': job.get('end_date')
                    }
                })
        
        if job_text:
            text_skills = self._extract_skills_from_text(
                job_text, 
                'work_experience',
                additional_context={
                    'company': job.get('company'),
                    'position': job.get('position'),
                    'dates': f"{job.get('start_date', '')} - {job.get('end_date', '')}"
                }
            )
            skills.extend(text_skills)
        
        return skills
    
    def _extract_skills_from_project(self, project: Dict[str, Any], project_index: int) -> List[Dict[str, Any]]:
        """Extract skills from project descriptions."""
        
        skills = []
        
        # Extract from technologies list
        if project.get('technologies'):
            for tech in project['technologies']:
                skills.append({
                    'name': tech.strip(),
                    'source': 'projects',
                    'category': 'technical',
                    'confidence': 0.8,
                    'contexts': [f"Used in project: {project.get('name', 'Unknown Project')}"],
                    'project_context': {
                        'name': project.get('name'),
                        'description': project.get('description')
                    }
                })
        
        # Extract from project description
        if project.get('description'):
            desc_skills = self._extract_skills_from_text(
                project['description'],
                'projects',
                additional_context={'project_name': project.get('name')}
            )
            skills.extend(desc_skills)
        
        return skills
    
    def _extract_skills_from_text(self, text: str, source: str, additional_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract skills from free text using NLP and pattern matching."""
        
        skills = []
        text_lower = text.lower()
        
        # Use spaCy if available
        if SPACY_AVAILABLE and nlp:
            skills.extend(self._extract_with_spacy(text, source, additional_context))
        
        # Pattern-based extraction for technical skills
        for category, skill_list in self.technical_skills_patterns.items():
            for skill in skill_list:
                skill_variations = [skill] + self.skill_synonyms.get(skill, [])
                
                for variation in skill_variations:
                    # Use word boundaries to avoid partial matches
                    pattern = rf'\b{re.escape(variation.lower())}\b'
                    if re.search(pattern, text_lower):
                        skills.append({
                            'name': skill,  # Use canonical name
                            'source': source,
                            'category': 'technical',
                            'subcategory': category,
                            'confidence': 0.7,
                            'contexts': [f"Mentioned in {source}"],
                            'matched_text': variation,
                            'additional_context': additional_context or {}
                        })
                        break  # Only match once per skill
        
        # Extract soft skills
        for soft_skill in self.soft_skills_patterns:
            pattern = rf'\b{re.escape(soft_skill.lower())}\b'
            if re.search(pattern, text_lower):
                skills.append({
                    'name': soft_skill,
                    'source': source,
                    'category': 'soft_skill',
                    'confidence': 0.6,
                    'contexts': [f"Mentioned in {source}"],
                    'additional_context': additional_context or {}
                })
        
        # Extract industry terms
        for industry, terms in self.industry_terms.items():
            for term in terms:
                pattern = rf'\b{re.escape(term.lower())}\b'
                if re.search(pattern, text_lower):
                    skills.append({
                        'name': term,
                        'source': source,
                        'category': 'industry_term',
                        'industry': industry,
                        'confidence': 0.65,
                        'contexts': [f"Mentioned in {source}"],
                        'additional_context': additional_context or {}
                    })
        
        return skills
    
    def _extract_with_spacy(self, text: str, source: str, additional_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract skills using spaCy NLP."""
        
        skills = []
        doc = nlp(text)
        
        # Extract named entities that might be skills
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'LANGUAGE']:  # Organizations, products, languages
                entity_text = ent.text.lower().strip()
                
                # Check if it's a known technical skill
                if self._is_technical_skill(entity_text):
                    skills.append({
                        'name': entity_text,
                        'source': source,
                        'category': 'technical',
                        'confidence': 0.75,
                        'contexts': [f"NLP entity extraction from {source}"],
                        'spacy_label': ent.label_,
                        'additional_context': additional_context or {}
                    })
        
        # Extract noun phrases that might be technical skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if self._is_technical_skill(chunk_text):
                skills.append({
                    'name': chunk_text,
                    'source': source,
                    'category': 'technical',
                    'confidence': 0.65,
                    'contexts': [f"Noun phrase extraction from {source}"],
                    'extraction_method': 'noun_phrase',
                    'additional_context': additional_context or {}
                })
        
        return skills
    
    def _is_technical_skill(self, text: str) -> bool:
        """Check if text represents a technical skill."""
        
        # Check against known technical skills
        for category, skills in self.technical_skills_patterns.items():
            if text in skills:
                return True
            
            # Check synonyms
            for skill in skills:
                if text in self.skill_synonyms.get(skill, []):
                    return True
        
        # Additional heuristics for technical skills
        technical_indicators = [
            '.js', '.py', '.java', '.cpp', '.cs',  # File extensions
            'api', 'sdk', 'framework', 'library', 'database'
        ]
        
        return any(indicator in text for indicator in technical_indicators)
    
    def _deduplicate_skills(self, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate skills and merge contexts."""
        
        skill_map = defaultdict(lambda: {
            'contexts': [],
            'sources': set(),
            'confidence_scores': [],
            'additional_data': []
        })
        
        # Group skills by normalized name
        for skill in skills:
            normalized_name = self._normalize_skill_name(skill['name'])
            skill_data = skill_map[normalized_name]
            
            # Merge contexts
            skill_data['contexts'].extend(skill.get('contexts', []))
            skill_data['sources'].add(skill['source'])
            skill_data['confidence_scores'].append(skill['confidence'])
            
            # Keep first occurrence as base
            if 'base_skill' not in skill_data:
                skill_data['base_skill'] = skill
            
            # Collect additional data
            for key in ['job_context', 'project_context', 'additional_context']:
                if key in skill:
                    skill_data['additional_data'].append({key: skill[key]})
        
        # Create deduplicated skills
        deduplicated = []
        for normalized_name, data in skill_map.items():
            base_skill = data['base_skill']
            
            # Calculate merged confidence
            avg_confidence = sum(data['confidence_scores']) / len(data['confidence_scores'])
            
            # Boost confidence if skill appears in multiple sources
            source_bonus = min(0.2, (len(data['sources']) - 1) * 0.1)
            final_confidence = min(0.95, avg_confidence + source_bonus)
            
            deduplicated_skill = {
                **base_skill,
                'name': normalized_name,
                'confidence': final_confidence,
                'contexts': list(set(data['contexts'])),  # Remove duplicate contexts
                'sources': list(data['sources']),
                'mention_count': len(data['confidence_scores']),
                'additional_data': data['additional_data']
            }
            
            deduplicated.append(deduplicated_skill)
        
        return deduplicated
    
    def _normalize_skill_name(self, skill_name: str) -> str:
        """Normalize skill name for deduplication."""
        
        # Convert to lowercase and strip
        normalized = skill_name.lower().strip()
        
        # Handle common variations
        normalizations = {
            'js': 'javascript',
            'py': 'python',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'ui': 'user interface',
            'ux': 'user experience',
            'api': 'application programming interface',
            'db': 'database'
        }
        
        return normalizations.get(normalized, normalized)
    
    async def _calculate_skill_experience(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate years of experience for each skill."""
        
        skills_with_experience = []
        
        for skill in skills:
            experience_data = self._calculate_experience_for_skill(skill, resume_data)
            
            skill_with_exp = {
                **skill,
                'experience_analysis': experience_data
            }
            
            skills_with_experience.append(skill_with_exp)
        
        return skills_with_experience
    
    def _calculate_experience_for_skill(self, skill: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate experience for a specific skill."""
        
        experience_periods = []
        total_years = 0.0
        
        # Check work experience
        work_experience = resume_data.get('work_experience', [])
        for job in work_experience:
            if self._skill_mentioned_in_job(skill, job):
                job_duration = self._calculate_job_duration(job)
                if job_duration > 0:
                    experience_periods.append({
                        'source': 'work_experience',
                        'company': job.get('company'),
                        'position': job.get('position'),
                        'duration_years': job_duration,
                        'start_date': job.get('start_date'),
                        'end_date': job.get('end_date')
                    })
                    total_years += job_duration
        
        # Check projects
        projects = resume_data.get('projects', [])
        for project in projects:
            if self._skill_mentioned_in_project(skill, project):
                # Estimate project duration (default to 0.25 years if not specified)
                project_duration = 0.25
                experience_periods.append({
                    'source': 'projects',
                    'project_name': project.get('name'),
                    'duration_years': project_duration,
                    'estimated': True
                })
                total_years += project_duration
        
        # Handle overlapping periods (rough estimation)
        adjusted_years = self._adjust_for_overlapping_experience(experience_periods)
        
        return {
            'total_years': round(adjusted_years, 1),
            'continuous_years': round(adjusted_years, 1),  # Simplified for now
            'experience_periods': experience_periods,
            'confidence': 0.8 if experience_periods else 0.3,
            'calculation_method': 'job_duration_analysis'
        }
    
    def _skill_mentioned_in_job(self, skill: Dict[str, Any], job: Dict[str, Any]) -> bool:
        """Check if skill is mentioned in job context."""
        
        skill_name = skill['name'].lower()
        
        # Check technologies list
        if job.get('technologies'):
            for tech in job['technologies']:
                if skill_name in tech.lower():
                    return True
        
        # Check job description
        job_text = ""
        if job.get('description'):
            job_text += job['description'] + " "
        if job.get('achievements'):
            job_text += " ".join(job['achievements'])
        
        return skill_name in job_text.lower()
    
    def _skill_mentioned_in_project(self, skill: Dict[str, Any], project: Dict[str, Any]) -> bool:
        """Check if skill is mentioned in project context."""
        
        skill_name = skill['name'].lower()
        
        # Check technologies list
        if project.get('technologies'):
            for tech in project['technologies']:
                if skill_name in tech.lower():
                    return True
        
        # Check project description
        if project.get('description'):
            return skill_name in project['description'].lower()
        
        return False
    
    def _calculate_job_duration(self, job: Dict[str, Any]) -> float:
        """Calculate job duration in years."""
        
        start_date = job.get('start_date', '')
        end_date = job.get('end_date', 'present')
        
        if not start_date:
            return 0.0
        
        try:
            # Parse start date
            start_year = self._extract_year_from_date(start_date)
            if not start_year:
                return 0.0
            
            # Parse end date
            if end_date.lower() in ['present', 'current']:
                end_year = datetime.now().year
            else:
                end_year = self._extract_year_from_date(end_date)
                if not end_year:
                    end_year = datetime.now().year
            
            duration_years = end_year - start_year
            return max(0.1, duration_years)  # Minimum 0.1 years
            
        except Exception:
            return 0.5  # Default estimate
    
    def _extract_year_from_date(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        
        if not date_str:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'(\d{4})', str(date_str))
        if year_match:
            year = int(year_match.group(1))
            if 1900 <= year <= 2030:  # Reasonable year range
                return year
        
        return None
    
    def _adjust_for_overlapping_experience(self, periods: List[Dict[str, Any]]) -> float:
        """Adjust total experience for overlapping periods."""
        
        # Simple approach: reduce total by 10% if multiple overlapping periods
        total_years = sum(period['duration_years'] for period in periods)
        
        if len(periods) > 1:
            # Assume some overlap, reduce by 10%
            return total_years * 0.9
        
        return total_years
    
    async def _assess_skill_strengths(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess skill strengths based on various factors."""
        
        skills_with_strength = []
        
        for skill in skills:
            strength_assessment = self._assess_individual_skill_strength(skill, resume_data)
            
            skill_with_strength = {
                **skill,
                'strength_assessment': strength_assessment
            }
            
            skills_with_strength.append(skill_with_strength)
        
        return skills_with_strength
    
    def _assess_individual_skill_strength(self, skill: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess strength of an individual skill."""
        
        factors = {
            'mention_frequency': min(1.0, skill.get('mention_count', 1) / 5.0),  # Max at 5 mentions
            'source_diversity': min(1.0, len(skill.get('sources', [])) / 3.0),  # Max at 3 sources
            'experience_years': 0.0,
            'context_quality': 0.0,
            'skill_prominence': 0.0
        }
        
        # Experience factor
        exp_analysis = skill.get('experience_analysis', {})
        total_years = exp_analysis.get('total_years', 0)
        if total_years > 0:
            factors['experience_years'] = min(1.0, total_years / 5.0)  # Max at 5 years
        
        # Context quality (explicit vs implicit mention)
        if 'skills_section' in skill.get('sources', []):
            factors['context_quality'] = 1.0
        elif 'work_experience' in skill.get('sources', []):
            factors['context_quality'] = 0.8
        else:
            factors['context_quality'] = 0.6
        
        # Skill prominence (technical skills get higher weight)
        if skill.get('category') == 'technical':
            factors['skill_prominence'] = 0.9
        elif skill.get('category') == 'soft_skill':
            factors['skill_prominence'] = 0.7
        else:
            factors['skill_prominence'] = 0.6
        
        # Calculate weighted strength score
        weights = {
            'mention_frequency': 0.2,
            'source_diversity': 0.2,
            'experience_years': 0.3,
            'context_quality': 0.2,
            'skill_prominence': 0.1
        }
        
        strength_score = sum(
            factors[factor] * weights[factor] 
            for factor in factors
        )
        
        # Determine proficiency level
        if strength_score >= 0.8:
            proficiency_level = 'expert'
        elif strength_score >= 0.6:
            proficiency_level = 'advanced'
        elif strength_score >= 0.4:
            proficiency_level = 'intermediate'
        else:
            proficiency_level = 'beginner'
        
        return {
            'strength_score': round(strength_score, 2),
            'proficiency_level': proficiency_level,
            'assessment_factors': factors,
            'confidence': 0.75
        }
    
    async def _organize_skill_results(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize skills into final structured results."""
        
        # Categorize skills
        categorized_skills = {
            'technical_skills': [],
            'soft_skills': [],
            'industry_terms': [],
            'all_skills': skills
        }
        
        for skill in skills:
            category = skill.get('category', 'unknown')
            
            if category == 'technical':
                categorized_skills['technical_skills'].append(skill)
            elif category == 'soft_skill':
                categorized_skills['soft_skills'].append(skill)
            elif category == 'industry_term':
                categorized_skills['industry_terms'].append(skill)
        
        # Sort skills by strength
        for category in ['technical_skills', 'soft_skills', 'industry_terms']:
            categorized_skills[category].sort(
                key=lambda x: x.get('strength_assessment', {}).get('strength_score', 0),
                reverse=True
            )
        
        # Generate summary statistics
        summary_stats = self._generate_skill_summary_stats(skills)
        
        # Create final results
        results = {
            'extraction_id': f"skill_analysis_{int(time.time())}",
            'candidate_id': resume_data.get('personal_information', {}).get('full_name', 'unknown'),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'skills_summary': summary_stats,
            'categorized_skills': categorized_skills,
            'top_skills': self._get_top_skills(skills, 10),
            'skill_gaps': self._identify_potential_gaps(skills, resume_data),
            'recommendations': self._generate_skill_recommendations(skills, resume_data)
        }
        
        return results
    
    def _generate_skill_summary_stats(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for skills."""
        
        total_skills = len(skills)
        technical_skills = sum(1 for skill in skills if skill.get('category') == 'technical')
        soft_skills = sum(1 for skill in skills if skill.get('category') == 'soft_skill')
        
        # Average experience
        exp_years = [
            skill.get('experience_analysis', {}).get('total_years', 0)
            for skill in skills
        ]
        avg_experience = sum(exp_years) / len(exp_years) if exp_years else 0
        
        # Average strength
        strengths = [
            skill.get('strength_assessment', {}).get('strength_score', 0)
            for skill in skills
        ]
        avg_strength = sum(strengths) / len(strengths) if strengths else 0
        
        return {
            'total_skills_identified': total_skills,
            'technical_skills_count': technical_skills,
            'soft_skills_count': soft_skills,
            'average_experience_years': round(avg_experience, 1),
            'average_strength_score': round(avg_strength, 2),
            'skills_with_experience': sum(1 for y in exp_years if y > 0),
            'expert_level_skills': sum(
                1 for skill in skills 
                if skill.get('strength_assessment', {}).get('proficiency_level') == 'expert'
            )
        }
    
    def _get_top_skills(self, skills: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Get top N skills by strength score."""
        
        sorted_skills = sorted(
            skills,
            key=lambda x: x.get('strength_assessment', {}).get('strength_score', 0),
            reverse=True
        )
        
        return sorted_skills[:limit]
    
    def _identify_potential_gaps(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> List[str]:
        """Identify potential skill gaps based on role and industry."""
        
        # This is a simplified gap analysis
        # In practice, this would be more sophisticated
        
        skill_names = [skill['name'].lower() for skill in skills]
        common_gaps = []
        
        # Check for common technical skills
        essential_tech_skills = [
            'git', 'sql', 'api', 'testing', 'debugging',
            'project management', 'agile', 'communication'
        ]
        
        for essential_skill in essential_tech_skills:
            if essential_skill not in skill_names:
                common_gaps.append(essential_skill)
        
        return common_gaps[:5]  # Return top 5 gaps
    
    def _generate_skill_recommendations(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for skill development."""
        
        recommendations = []
        
        # Check skill diversity
        technical_count = sum(1 for skill in skills if skill.get('category') == 'technical')
        soft_skills_count = sum(1 for skill in skills if skill.get('category') == 'soft_skill')
        
        if technical_count < 10:
            recommendations.append("Consider highlighting more technical skills from your experience")
        
        if soft_skills_count < 5:
            recommendations.append("Add more soft skills to demonstrate well-rounded capabilities")
        
        # Check for experience gaps
        skills_without_exp = [
            skill for skill in skills 
            if skill.get('experience_analysis', {}).get('total_years', 0) == 0
        ]
        
        if len(skills_without_exp) > len(skills) * 0.5:
            recommendations.append("Provide more context about your experience with listed skills")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _calculate_overall_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the skill analysis."""
        
        all_skills = results.get('all_skills', [])
        if not all_skills:
            return 0.0
        
        # Average confidence of individual skills
        skill_confidences = [skill.get('confidence', 0) for skill in all_skills]
        avg_skill_confidence = sum(skill_confidences) / len(skill_confidences)
        
        # Boost confidence based on number of skills found
        skill_count_factor = min(1.0, len(all_skills) / 20.0)  # Max boost at 20 skills
        
        # Boost confidence based on experience data availability
        skills_with_exp = sum(
            1 for skill in all_skills 
            if skill.get('experience_analysis', {}).get('total_years', 0) > 0
        )
        experience_factor = skills_with_exp / len(all_skills) if all_skills else 0
        
        overall_confidence = (
            avg_skill_confidence * 0.5 +
            skill_count_factor * 0.3 +
            experience_factor * 0.2
        )
        
        return round(overall_confidence, 2)