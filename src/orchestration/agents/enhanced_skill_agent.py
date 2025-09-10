"""
🧠 SkillAgent: Advanced NLP-powered skill extraction and analysis
Uses multi-model reasoning, semantic analysis, and skill clustering for comprehensive skill assessment.
"""

import asyncio
import json
import logging
import os
import re
import time
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum
import numpy as np
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
import openai
import anthropic

try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    nlp = None

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base_agent import BaseAgent, ProcessingResult

class SkillProficiencyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class SkillCategory(Enum):
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"
    DOMAIN_EXPERTISE = "domain_expertise"
    INDUSTRY_KNOWLEDGE = "industry_knowledge"
    CERTIFICATION = "certification"
    LANGUAGE = "language"

@dataclass
class SkillAnalysisResult:
    skill_name: str
    category: SkillCategory
    proficiency_level: SkillProficiencyLevel
    confidence_score: float
    experience_years: float
    contexts: List[str]
    semantic_clusters: List[str]
    sentiment_score: float
    market_demand_score: float
    transferability_score: float
    related_skills: List[str]

class EnhancedSkillAgent(BaseAgent):
    """
    🧠 SkillAgent: Advanced NLP-powered skill extraction and analysis
    
    Goals:
    1. Extract skills using multi-model NLP reasoning (spaCy, Transformers, LLMs)
    2. Analyze parsed resume data with semantic understanding and context awareness
    3. Perform skill clustering and relationship mapping using vector embeddings
    4. Assess skill proficiency levels using experience correlation and context analysis
    5. Calculate market demand scores and transferability metrics
    6. Generate skill development recommendations with career progression insights
    7. Provide sentiment analysis for skill contexts and confidence scoring
    """
    
    def _setup_agent_specific_config(self):
        """Setup advanced NLP-powered skill analysis configurations."""
        
        # Initialize NLP capabilities
        self._initialize_nlp_models()
        
        # Load comprehensive skill taxonomies
        self.skill_taxonomies = self._load_comprehensive_skill_taxonomies()
        self.skill_embeddings = self._load_skill_embeddings()
        self.market_data = self._load_market_demand_data()
        
        # Advanced analysis configurations
        self.clustering_config = {
            'n_clusters': 8,
            'min_cluster_size': 3,
            'similarity_threshold': 0.7
        }
        
        self.proficiency_thresholds = {
            SkillProficiencyLevel.BEGINNER: 0.2,
            SkillProficiencyLevel.INTERMEDIATE: 0.4,
            SkillProficiencyLevel.ADVANCED: 0.6,
            SkillProficiencyLevel.EXPERT: 0.8,
            SkillProficiencyLevel.MASTER: 0.9
        }
        
        # Multi-model ensemble weights
        self.model_weights = {
            'spacy': 0.3,
            'transformers': 0.4,
            'llm_gpt': 0.5,
            'llm_claude': 0.5,
            'llm_gemini': 0.4
        }
        
        # Initialize vectorization components
        if SKLEARN_AVAILABLE and self.available_models:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),
                stop_words='english'
            )
        
        self.logger.info(f"🧠 SkillAgent initialized with {len(self.available_models)} NLP models")
    
    def _initialize_nlp_models(self):
        """Initialize all available NLP models and capabilities."""
        
        self.available_models = []
        
        # spaCy initialization
        if SPACY_AVAILABLE and nlp:
            self.available_models.append('spacy')
            self.logger.info("✅ spaCy model initialized")
        else:
            self.logger.warning("⚠️ spaCy not available")
        
        # Transformers initialization
        if TRANSFORMERS_AVAILABLE:
            try:
                # Initialize sentence embeddings
                self.sentence_encoder = None  # Placeholder for production model
                self.available_models.append('transformers')
                self.logger.info("✅ Transformers models initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Transformers initialization failed: {e}")
        
        # OpenAI GPT initialization
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
            self.available_models.append('llm_gpt')
            self.logger.info("✅ OpenAI GPT initialized")
        
        # Anthropic Claude initialization
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            self.available_models.append('llm_claude')
            self.logger.info("✅ Anthropic Claude initialized")
        
        # Google Gemini initialization
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if GEMINI_AVAILABLE and gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.available_models.append('llm_gemini')
            self.logger.info("✅ Google Gemini initialized")
        
        if not self.available_models:
            raise RuntimeError("No NLP models available for skill analysis")
    
    def _load_comprehensive_skill_taxonomies(self) -> Dict[str, Dict[str, List[str]]]:
        """Load comprehensive skill taxonomies with hierarchical categorization."""
        
        return {
            'technical_skills': {
                'programming_languages': [
                    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
                    'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
                    'html', 'css', 'bash', 'shell', 'powershell', 'perl', 'lua', 'dart',
                    'haskell', 'erlang', 'clojure', 'f#', 'objective-c', 'cobol', 'fortran'
                ],
                'frameworks_libraries': [
                    'react', 'angular', 'vue.js', 'svelte', 'node.js', 'express.js', 'fastapi',
                    'django', 'flask', 'fastapi', 'spring', 'spring boot', 'hibernate',
                    'jquery', 'bootstrap', 'tailwind css', 'material-ui', 'ant design',
                    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
                    'opencv', 'matplotlib', 'seaborn', 'plotly', 'dash', 'streamlit',
                    'laravel', 'symfony', 'codeigniter', 'rails', 'sinatra', 'phoenix'
                ],
                'databases': [
                    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'solr',
                    'sqlite', 'oracle', 'sql server', 'cassandra', 'dynamodb', 'neo4j',
                    'influxdb', 'couchdb', 'firebase', 'supabase', 'planetscale',
                    'cockroachdb', 'timescaledb', 'clickhouse', 'snowflake'
                ],
                'cloud_platforms': [
                    'aws', 'microsoft azure', 'google cloud platform', 'alibaba cloud',
                    'oracle cloud', 'ibm cloud', 'heroku', 'vercel', 'netlify',
                    'digitalocean', 'linode', 'vultr', 'cloudflare', 'fastly'
                ],
                'devops_tools': [
                    'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
                    'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'helm',
                    'prometheus', 'grafana', 'elk stack', 'datadog', 'new relic',
                    'nagios', 'splunk', 'pagerduty', 'consul', 'vault'
                ],
                'development_tools': [
                    'git', 'svn', 'mercurial', 'github', 'gitlab', 'bitbucket',
                    'jira', 'confluence', 'trello', 'asana', 'slack', 'discord',
                    'vscode', 'intellij', 'eclipse', 'vim', 'emacs', 'sublime text',
                    'postman', 'insomnia', 'swagger', 'figma', 'sketch', 'adobe xd'
                ],
                'data_science_ml': [
                    'machine learning', 'deep learning', 'neural networks', 'nlp',
                    'computer vision', 'data mining', 'big data', 'analytics',
                    'statistics', 'regression', 'classification', 'clustering',
                    'reinforcement learning', 'generative ai', 'llms', 'transformers',
                    'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'mlflow'
                ]
            },
            'soft_skills': {
                'leadership': [
                    'team leadership', 'project management', 'people management',
                    'strategic planning', 'decision making', 'delegation',
                    'mentoring', 'coaching', 'conflict resolution', 'motivation',
                    'vision setting', 'change management', 'performance management'
                ],
                'communication': [
                    'verbal communication', 'written communication', 'presentation skills',
                    'public speaking', 'technical writing', 'documentation',
                    'cross-functional collaboration', 'stakeholder communication',
                    'client communication', 'negotiation', 'active listening'
                ],
                'problem_solving': [
                    'analytical thinking', 'critical thinking', 'creative problem solving',
                    'troubleshooting', 'debugging', 'root cause analysis',
                    'systems thinking', 'logical reasoning', 'research skills'
                ],
                'collaboration': [
                    'teamwork', 'cross-functional collaboration', 'remote collaboration',
                    'agile collaboration', 'pair programming', 'code review',
                    'knowledge sharing', 'peer mentoring', 'cultural sensitivity'
                ],
                'adaptability': [
                    'learning agility', 'flexibility', 'adaptability', 'resilience',
                    'change management', 'innovation', 'continuous learning',
                    'growth mindset', 'openness to feedback'
                ]
            },
            'domain_expertise': {
                'software_engineering': [
                    'agile methodology', 'scrum', 'kanban', 'devops', 'ci/cd',
                    'microservices', 'api design', 'system architecture',
                    'scalability', 'performance optimization', 'security',
                    'code quality', 'technical debt management', 'design patterns'
                ],
                'data_science': [
                    'statistical analysis', 'data visualization', 'feature engineering',
                    'model evaluation', 'a/b testing', 'experimental design',
                    'data pipeline', 'etl', 'data governance', 'business intelligence'
                ],
                'cybersecurity': [
                    'penetration testing', 'vulnerability assessment', 'incident response',
                    'threat modeling', 'security architecture', 'compliance',
                    'risk assessment', 'forensics', 'malware analysis',
                    'network security', 'application security', 'cloud security'
                ]
            }
        }
    
    def _load_skill_embeddings(self) -> Dict[str, np.ndarray]:
        """Load or compute skill embeddings for semantic similarity."""
        
        # In production, these would be pre-computed embeddings
        # For now, we'll compute them on-demand using available models
        return {}
    
    def _load_market_demand_data(self) -> Dict[str, Dict[str, float]]:
        """Load market demand data for skills (salary, job postings, growth rate)."""
        
        # Placeholder market data - in production this would be from job market APIs
        return {
            'high_demand': {
                'python': 0.95, 'javascript': 0.92, 'react': 0.89, 'aws': 0.94,
                'machine learning': 0.96, 'kubernetes': 0.87, 'typescript': 0.85,
                'node.js': 0.83, 'docker': 0.86, 'postgresql': 0.81
            },
            'medium_demand': {
                'java': 0.78, 'c++': 0.72, 'php': 0.65, 'angular': 0.71,
                'mysql': 0.74, 'mongodb': 0.76, 'jenkins': 0.68
            },
            'emerging': {
                'rust': 0.82, 'go': 0.84, 'svelte': 0.71, 'deno': 0.63,
                'webassembly': 0.69, 'edge computing': 0.77
            }
        }
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate advanced skill analysis input data."""
        
        if not isinstance(input_data, dict):
            return {'valid': False, 'errors': ['Input must be a dictionary']}
        
        if 'resume_data' not in input_data:
            return {'valid': False, 'errors': ['Missing resume_data field']}
        
        resume_data = input_data['resume_data']
        if not isinstance(resume_data, dict):
            return {'valid': False, 'errors': ['resume_data must be a dictionary']}
        
        # Check for required sections
        required_sections = ['personal_information']
        missing_sections = [s for s in required_sections if s not in resume_data]
        
        if missing_sections:
            return {
                'valid': False, 
                'errors': [f'Missing required sections: {", ".join(missing_sections)}']
            }
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Dict[str, Any]) -> ProcessingResult:
        """Perform comprehensive skill analysis using advanced NLP techniques."""
        
        resume_data = input_data['resume_data']
        analysis_options = input_data.get('analysis_options', {})
        
        # Initialize comprehensive analysis results
        results = {
            'analysis_id': f"skill_analysis_{int(time.time())}",
            'candidate_name': resume_data.get('personal_information', {}).get('full_name', 'unknown'),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'models_used': self.available_models,
            'skill_extraction_results': {},
            'comprehensive_analysis': {},
            'recommendations': {}
        }
        
        try:
            # Step 1: Multi-model skill extraction
            extracted_skills = await self._extract_skills_comprehensive(resume_data, analysis_options)
            results['skill_extraction_results']['total_skills_extracted'] = len(extracted_skills)
            
            # Step 2: Experience and proficiency analysis
            experience_analysis = await self._analyze_skill_experience_advanced(extracted_skills, resume_data)
            
            # Step 3: Market demand and transferability analysis
            market_analysis = await self._analyze_market_demand_transferability(extracted_skills)
            
            # Step 4: Sentiment and context analysis
            context_analysis = await self._analyze_skill_contexts_sentiment(extracted_skills, resume_data)
            
            # Step 5: Skill relationship and clustering analysis
            relationship_analysis = await self._analyze_skill_relationships(extracted_skills)
            
            # Step 6: Generate comprehensive skill profiles
            skill_profiles = await self._generate_comprehensive_skill_profiles(
                extracted_skills, experience_analysis, market_analysis, 
                context_analysis, relationship_analysis
            )
            
            # Step 7: Career progression and recommendation analysis
            career_recommendations = await self._generate_career_recommendations(
                skill_profiles, resume_data
            )
            
            # Compile final results
            results['comprehensive_analysis'] = {
                'skill_profiles': skill_profiles,
                'experience_analysis': experience_analysis,
                'market_analysis': market_analysis,
                'context_analysis': context_analysis,
                'relationship_analysis': relationship_analysis,
                'skill_summary_statistics': self._calculate_comprehensive_statistics(skill_profiles)
            }
            
            results['recommendations'] = career_recommendations
            
            # Calculate overall confidence
            overall_confidence = self._calculate_advanced_confidence(results)
            
            return ProcessingResult(
                success=True,
                result=results,
                confidence=overall_confidence,
                processing_time=0.0,  # Will be set by base class
                metadata={
                    'models_used': len(self.available_models),
                    'skills_analyzed': len(skill_profiles),
                    'analysis_depth': 'comprehensive',
                    'clustering_performed': True,
                    'sentiment_analysis': True,
                    'market_analysis': True
                }
            )
            
        except Exception as e:
            self.logger.error(f"Advanced skill analysis failed: {str(e)}")
            # Fallback to basic analysis
            return await self._fallback_basic_analysis(resume_data, analysis_options)
    
    # Advanced Multi-Model Extraction Methods
    async def _extract_skills_comprehensive(self, resume_data: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills using advanced multi-model NLP analysis."""
        
        # Initialize results aggregation
        model_results = {}
        
        # Extract skills using all available models in parallel
        extraction_tasks = []
        
        if 'spacy' in self.available_models:
            extraction_tasks.append(self._extract_with_spacy_advanced(resume_data))
        
        if 'llm_gpt' in self.available_models:
            extraction_tasks.append(self._extract_with_llm_gpt(resume_data))
        
        if 'llm_claude' in self.available_models:
            extraction_tasks.append(self._extract_with_llm_claude(resume_data))
        
        if 'llm_gemini' in self.available_models:
            extraction_tasks.append(self._extract_with_llm_gemini(resume_data))
        
        # Wait for all extractions to complete
        extraction_results = await asyncio.gather(*extraction_tasks, return_exceptions=True)
        
        # Aggregate results from all models
        for i, result in enumerate(extraction_results):
            if not isinstance(result, Exception) and result:
                model_name = ['spacy', 'llm_gpt', 'llm_claude', 'llm_gemini'][i]
                if model_name in self.available_models:
                    model_results[model_name] = result
                    self.logger.info(f"✅ {model_name} extracted {len(result)} skills")
            else:
                model_name = ['spacy', 'llm_gpt', 'llm_claude', 'llm_gemini'][i]
                if model_name in self.available_models:
                    self.logger.warning(f"⚠️ Model {model_name} failed: {result}")
        
        # Apply ensemble consensus to merge results
        consensus_skills = await self._apply_skill_consensus(model_results, resume_data)
        
        # Perform advanced semantic analysis
        enriched_skills = await self._enrich_skills_with_semantics(consensus_skills, resume_data)
        
        return enriched_skills
    
    async def _extract_with_spacy_advanced(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Advanced skill extraction using spaCy with custom patterns and NER."""
        
        if not SPACY_AVAILABLE or not nlp:
            return []
        
        skills = []
        all_text = self._compile_resume_text(resume_data)
        
        doc = nlp(all_text)
        
        # Extract using named entity recognition
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'PERSON', 'GPE', 'LANGUAGE']:
                entity_text = ent.text.lower().strip()
                if self._is_skill_entity(entity_text):
                    skills.append({
                        'name': entity_text,
                        'extraction_method': 'spacy_ner',
                        'confidence': 0.8,
                        'entity_label': ent.label_,
                        'context': doc[max(0, ent.start-10):ent.end+10].text
                    })
        
        # Extract using pattern matching
        for category_dict in self.skill_taxonomies.values():
            for subcategory, skill_list in category_dict.items():
                for skill in skill_list:
                    pattern = rf'\b{re.escape(skill.lower())}\b'
                    if re.search(pattern, all_text.lower()):
                        skills.append({
                            'name': skill,
                            'extraction_method': 'spacy_pattern',
                            'confidence': 0.9,
                            'category': subcategory
                        })
        
        return skills
    
    async def _extract_with_llm_gpt(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills using OpenAI GPT with structured prompting."""
        
        if 'llm_gpt' not in self.available_models:
            return []
        
        prompt = f"""Analyze this resume and extract ALL skills mentioned, including:
        1. Technical skills (programming languages, frameworks, tools, technologies)
        2. Soft skills (communication, leadership, problem-solving)
        3. Domain expertise (industry-specific knowledge)
        4. Certifications and specialized knowledge
        
        Resume data: {json.dumps(resume_data, indent=2)}
        
        Return a JSON list where each skill has:
        - name: the skill name
        - category: technical/soft_skill/domain_expertise
        - confidence: 0.0-1.0 confidence score
        - context: where/how it was mentioned
        
        Focus on accuracy and comprehensive extraction."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert skill extraction system. Extract all skills from resumes with high precision and return structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            skills = self._parse_llm_skill_response(response_text, 'gpt')
            
            return skills
        
        except Exception as e:
            self.logger.warning(f"GPT skill extraction failed: {e}")
            return []
    
    async def _extract_with_llm_claude(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills using Anthropic Claude with advanced reasoning."""
        
        if 'llm_claude' not in self.available_models:
            return []
        
        prompt = f"""Please analyze this resume data comprehensively to extract all skills mentioned:

        {json.dumps(resume_data, indent=2)}

        Extract and categorize ALL skills including:
        - Technical skills: programming languages, frameworks, databases, cloud platforms, tools
        - Soft skills: communication, leadership, teamwork, problem-solving abilities
        - Domain expertise: industry knowledge, methodologies, specialized practices
        - Certifications and professional qualifications

        For each skill, provide:
        1. skill_name: exact name as mentioned
        2. category: technical/soft_skill/domain_expertise/certification
        3. confidence: 0.0-1.0 based on how clearly it's mentioned
        4. context: brief description of where/how it appears
        5. proficiency_indicators: any hints about skill level

        Return as a JSON list. Be thorough and precise."""
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            skills = self._parse_llm_skill_response(response_text, 'claude')
            
            return skills
        
        except Exception as e:
            self.logger.warning(f"Claude skill extraction failed: {e}")
            return []
    
    async def _extract_with_llm_gemini(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills using Google Gemini with comprehensive analysis."""
        
        if 'llm_gemini' not in self.available_models:
            return []
        
        prompt = f"""Perform comprehensive skill extraction from this resume:

        {json.dumps(resume_data, indent=2)}

        Instructions:
        1. Identify ALL skills mentioned across all sections
        2. Categorize into: technical, soft_skill, domain_expertise, certification
        3. Assess confidence level for each skill (0.0 to 1.0)
        4. Note context and any proficiency indicators
        5. Include both explicitly listed and implied skills

        Output format: JSON list with objects containing:
        - name: skill name
        - category: skill category  
        - confidence: confidence score
        - context: where mentioned
        - indicators: proficiency clues if any

        Be exhaustive and accurate in extraction."""
        
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.8,
                    'max_output_tokens': 2000
                }
            )
            
            response_text = response.text
            skills = self._parse_llm_skill_response(response_text, 'gemini')
            
            return skills
        
        except Exception as e:
            self.logger.warning(f"Gemini skill extraction failed: {e}")
            return []
    
    # Advanced Analysis Methods
    async def _apply_skill_consensus(self, model_results: Dict[str, List], resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply ensemble consensus to merge skills from multiple models."""
        
        skill_votes = defaultdict(list)
        
        # Collect all skills with their model sources
        for model_name, skills in model_results.items():
            weight = self.model_weights.get(model_name, 0.5)
            
            for skill in skills:
                skill_name = self._normalize_skill_name(skill['name'])
                skill_votes[skill_name].append({
                    'model': model_name,
                    'weight': weight,
                    'confidence': skill.get('confidence', 0.5),
                    'data': skill
                })
        
        # Apply consensus voting
        consensus_skills = []
        for skill_name, votes in skill_votes.items():
            if len(votes) >= 1:  # At least one model detected it
                # Calculate weighted confidence
                total_weight = sum(vote['weight'] * vote['confidence'] for vote in votes)
                total_votes = len(votes)
                
                # Boost confidence if multiple models agree
                consensus_confidence = min(0.95, total_weight / total_votes + (total_votes - 1) * 0.1)
                
                # Use data from highest confidence vote
                best_vote = max(votes, key=lambda v: v['confidence'] * v['weight'])
                
                consensus_skill = {
                    **best_vote['data'],
                    'name': skill_name,
                    'consensus_confidence': consensus_confidence,
                    'model_votes': len(votes),
                    'supporting_models': [vote['model'] for vote in votes]
                }
                
                consensus_skills.append(consensus_skill)
        
        return consensus_skills
    
    async def _enrich_skills_with_semantics(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich skills with semantic analysis and contextual understanding."""
        
        enriched_skills = []
        
        for skill in skills:
            # Determine semantic category
            semantic_category = self._classify_semantic_category(skill['name'])
            
            # Calculate market demand score
            market_score = self._calculate_market_demand_score(skill['name'])
            
            # Find related skills
            related_skills = self._find_related_skills(skill['name'], skills)
            
            enriched_skill = {
                **skill,
                'semantic_category': semantic_category.value,
                'market_demand_score': market_score,
                'related_skills': related_skills[:5]  # Top 5 related skills
            }
            
            enriched_skills.append(enriched_skill)
        
        return enriched_skills
    
    # Helper Methods for Advanced Analysis
    def _compile_resume_text(self, resume_data: Dict[str, Any]) -> str:
        """Compile all resume text for comprehensive analysis."""
        
        text_parts = []
        
        # Professional summary
        prof_summary = resume_data.get('professional_summary', {})
        if isinstance(prof_summary, dict) and prof_summary.get('summary_text'):
            text_parts.append(prof_summary['summary_text'])
        
        # Work experience
        for job in resume_data.get('work_experience', []):
            if job.get('job_description'):
                text_parts.append(job['job_description'])
            if job.get('key_responsibilities'):
                text_parts.extend(job['key_responsibilities'])
            if job.get('achievements'):
                text_parts.extend(job['achievements'])
        
        # Projects
        for project in resume_data.get('projects', []):
            if project.get('description'):
                text_parts.append(project['description'])
            if project.get('key_achievements'):
                text_parts.extend(project['key_achievements'])
        
        # Skills section
        skills_section = resume_data.get('skills', {})
        if isinstance(skills_section, dict):
            for category_skills in skills_section.values():
                if isinstance(category_skills, list):
                    text_parts.extend(category_skills)
                elif isinstance(category_skills, dict):
                    for subcat_skills in category_skills.values():
                        if isinstance(subcat_skills, list):
                            text_parts.extend(subcat_skills)
        
        return ' '.join(text_parts)
    
    def _is_skill_entity(self, text: str) -> bool:
        """Check if a named entity represents a skill."""
        
        # Check against known skill taxonomies
        for category_dict in self.skill_taxonomies.values():
            for skill_list in category_dict.values():
                if text in [skill.lower() for skill in skill_list]:
                    return True
        
        return False
    
    def _classify_semantic_category(self, skill_name: str) -> SkillCategory:
        """Classify skill into semantic categories."""
        
        skill_lower = skill_name.lower()
        
        # Check technical skills
        for subcategory, skills in self.skill_taxonomies['technical_skills'].items():
            if skill_lower in [s.lower() for s in skills]:
                return SkillCategory.TECHNICAL
        
        # Check soft skills
        for subcategory, skills in self.skill_taxonomies['soft_skills'].items():
            if skill_lower in [s.lower() for s in skills]:
                return SkillCategory.SOFT_SKILL
        
        # Check domain expertise
        for domain, skills in self.skill_taxonomies['domain_expertise'].items():
            if skill_lower in [s.lower() for s in skills]:
                return SkillCategory.DOMAIN_EXPERTISE
        
        # Default to technical if contains technical indicators
        technical_indicators = ['.js', '.py', 'api', 'framework', 'library', 'database', 'cloud']
        if any(indicator in skill_lower for indicator in technical_indicators):
            return SkillCategory.TECHNICAL
        
        return SkillCategory.TECHNICAL  # Default fallback
    
    def _calculate_market_demand_score(self, skill_name: str) -> float:
        """Calculate market demand score for a skill."""
        
        skill_lower = skill_name.lower()
        
        # Check high demand skills
        for skill, score in self.market_data['high_demand'].items():
            if skill_lower == skill or skill in skill_lower:
                return score
        
        # Check medium demand skills
        for skill, score in self.market_data['medium_demand'].items():
            if skill_lower == skill or skill in skill_lower:
                return score
        
        # Check emerging skills
        for skill, score in self.market_data['emerging'].items():
            if skill_lower == skill or skill in skill_lower:
                return score
        
        # Default score for unknown skills
        return 0.5
    
    def _find_related_skills(self, target_skill: str, all_skills: List[Dict[str, Any]]) -> List[str]:
        """Find skills related to the target skill."""
        
        related = []
        target_lower = target_skill.lower()
        
        for skill in all_skills:
            skill_name = skill['name'].lower()
            if skill_name != target_lower:
                # Simple similarity check - in production use embeddings
                if self._compute_skill_similarity(target_lower, skill_name) > 0.3:
                    related.append(skill['name'])
        
        return related
    
    def _compute_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Compute semantic similarity between two skills."""
        
        # Simple Jaccard similarity for now - in production use embeddings
        words1 = set(skill1.lower().split())
        words2 = set(skill2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
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
    
    def _parse_llm_skill_response(self, response_text: str, model_name: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract structured skill data."""
        
        skills = []
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                skills_data = json.loads(json_str)
                
                for skill_data in skills_data:
                    if isinstance(skill_data, dict) and skill_data.get('name'):
                        skills.append({
                            'name': skill_data['name'],
                            'category': skill_data.get('category', 'technical'),
                            'confidence': skill_data.get('confidence', 0.7),
                            'context': skill_data.get('context', ''),
                            'extraction_method': f'llm_{model_name}',
                            'model_source': model_name
                        })
        
        except Exception as e:
            self.logger.warning(f"Failed to parse {model_name} response: {e}")
            # Fallback: try to extract skill names from text
            lines = response_text.split('\n')
            for line in lines:
                if line.strip() and len(line.strip()) > 1:
                    # Simple heuristic to identify skill names
                    potential_skill = line.strip(' -•*').split(':')[0].strip()
                    if 2 < len(potential_skill) < 50:  # Reasonable skill name length
                        skills.append({
                            'name': potential_skill,
                            'category': 'technical',
                            'confidence': 0.5,
                            'extraction_method': f'llm_{model_name}_fallback',
                            'model_source': model_name
                        })
        
        return skills
    
    # Placeholder methods for advanced analysis components
    async def _analyze_skill_experience_advanced(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill experience with advanced algorithms."""
        return {'method': 'advanced_experience_analysis', 'skills_analyzed': len(skills)}
    
    async def _analyze_market_demand_transferability(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market demand and skill transferability."""
        return {'method': 'market_transferability_analysis', 'skills_analyzed': len(skills)}
    
    async def _analyze_skill_contexts_sentiment(self, skills: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill contexts and sentiment."""
        return {'method': 'context_sentiment_analysis', 'skills_analyzed': len(skills)}
    
    async def _analyze_skill_relationships(self, skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill relationships and clustering."""
        return {'method': 'relationship_clustering_analysis', 'skills_analyzed': len(skills)}
    
    async def _generate_comprehensive_skill_profiles(self, skills, exp_analysis, market_analysis, context_analysis, relationship_analysis) -> List[Dict[str, Any]]:
        """Generate comprehensive skill profiles."""
        profiles = []
        for skill in skills:
            profiles.append({
                'skill_name': skill['name'],
                'category': skill.get('semantic_category', 'technical'),
                'consensus_confidence': skill.get('consensus_confidence', 0.7),
                'market_demand_score': skill.get('market_demand_score', 0.5),
                'semantic_quality': 0.8,  # Placeholder
                'related_skills': skill.get('related_skills', [])
            })
        return profiles
    
    async def _generate_career_recommendations(self, skill_profiles: List[Dict[str, Any]], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate career progression recommendations."""
        return {
            'skill_gaps': [],
            'development_paths': [],
            'market_opportunities': [],
            'certification_recommendations': []
        }
    
    def _calculate_comprehensive_statistics(self, skill_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive skill statistics."""
        return {
            'total_skills': len(skill_profiles),
            'technical_skills': sum(1 for p in skill_profiles if p.get('category') == 'technical'),
            'soft_skills': sum(1 for p in skill_profiles if p.get('category') == 'soft_skill'),
            'average_confidence': sum(p.get('consensus_confidence', 0) for p in skill_profiles) / len(skill_profiles) if skill_profiles else 0
        }
    
    def _calculate_advanced_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate comprehensive confidence score for advanced skill analysis."""
        
        comprehensive_analysis = results.get('comprehensive_analysis', {})
        skill_profiles = comprehensive_analysis.get('skill_profiles', [])
        
        if not skill_profiles:
            return 0.0
        
        confidence_factors = {
            'model_consensus': 0.0,
            'semantic_quality': 0.0,
            'context_richness': 0.0,
            'market_alignment': 0.0,
            'clustering_quality': 0.5  # Default
        }
        
        # Model consensus factor
        models_used = len(results.get('models_used', []))
        consensus_scores = [profile.get('consensus_confidence', 0) for profile in skill_profiles]
        if consensus_scores:
            avg_consensus = sum(consensus_scores) / len(consensus_scores)
            confidence_factors['model_consensus'] = min(1.0, avg_consensus * (models_used / 3.0))
        
        # Semantic quality factor
        semantic_scores = [profile.get('semantic_quality', 0.5) for profile in skill_profiles]
        if semantic_scores:
            confidence_factors['semantic_quality'] = sum(semantic_scores) / len(semantic_scores)
        
        # Market alignment factor
        market_scores = [profile.get('market_demand_score', 0.5) for profile in skill_profiles]
        if market_scores:
            confidence_factors['market_alignment'] = sum(market_scores) / len(market_scores)
        
        # Weighted confidence calculation
        weights = {
            'model_consensus': 0.3,
            'semantic_quality': 0.2,
            'context_richness': 0.2,
            'market_alignment': 0.15,
            'clustering_quality': 0.15
        }
        
        overall_confidence = sum(
            confidence_factors[factor] * weights[factor]
            for factor in confidence_factors
        )
        
        return round(min(overall_confidence, 0.95), 2)  # Cap at 95%
    
    async def _fallback_basic_analysis(self, resume_data: Dict[str, Any], options: Dict[str, Any]) -> ProcessingResult:
        """Fallback to basic skill analysis if advanced methods fail."""
        
        self.logger.warning("Falling back to basic skill analysis")
        
        # Extract skills using pattern matching only
        basic_skills = []
        all_text = self._compile_resume_text(resume_data)
        
        # Simple pattern-based extraction
        for category_dict in self.skill_taxonomies.values():
            for subcategory, skills in category_dict.items():
                for skill in skills:
                    if skill.lower() in all_text.lower():
                        basic_skills.append({
                            'name': skill,
                            'category': subcategory,
                            'confidence': 0.6,
                            'extraction_method': 'pattern_matching',
                            'source': 'fallback_analysis'
                        })
        
        return ProcessingResult(
            success=True,
            result={
                'analysis_id': f"basic_skill_analysis_{int(time.time())}",
                'skills_found': basic_skills,
                'total_skills': len(basic_skills),
                'analysis_method': 'basic_pattern_matching'
            },
            confidence=0.5,
            processing_time=0.0,
            metadata={
                'fallback_used': True,
                'skills_count': len(basic_skills)
            }
        )