"""
✍️ CoverLetterAgent: AI-powered personalized cover letter generation
Creates compelling, tailored cover letters using multi-model reasoning and professional writing strategies.
"""

import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import openai
import anthropic

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base_agent import BaseAgent, ProcessingResult

class CoverLetterStyle(Enum):
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    STARTUP = "startup"
    ACADEMIC = "academic"
    CONSULTING = "consulting"

class CoverLetterTone(Enum):
    FORMAL = "formal"
    CONVERSATIONAL = "conversational"
    CONFIDENT = "confident"
    HUMBLE = "humble"
    ENTHUSIASTIC = "enthusiastic"
    ANALYTICAL = "analytical"

@dataclass
class JobRequirement:
    skill: str
    importance: str  # critical, important, preferred
    category: str    # technical, soft_skill, experience
    confidence_match: float

@dataclass
class CoverLetterSection:
    section_name: str
    content: str
    reasoning: str
    key_points: List[str]
    confidence: float

class CoverLetterAgent(BaseAgent):
    """
    ✍️ CoverLetterAgent: AI-powered personalized cover letter generation
    
    Goals:
    1. Generate highly personalized cover letters based on resume and job description
    2. Match candidate qualifications with job requirements intelligently
    3. Use multiple AI models for diverse writing perspectives and quality
    4. Apply professional writing best practices and industry-specific language
    5. Generate multiple variants with different styles and tones
    6. Ensure ATS-friendly formatting and keyword optimization
    7. Provide reasoning and suggestions for customization
    8. Support multiple languages and cultural contexts
    """
    
    def _setup_agent_specific_config(self):
        """Setup comprehensive cover letter generation configurations."""
        
        # Initialize AI models for diverse writing capabilities
        self._initialize_writing_models()
        
        # Load writing templates and strategies
        self.letter_templates = self._load_cover_letter_templates()
        self.writing_strategies = self._load_writing_strategies()
        self.industry_knowledge = self._load_industry_writing_styles()
        
        # Cover letter generation configuration
        self.generation_config = {
            'max_length': 400,          # Maximum words
            'min_length': 250,          # Minimum words
            'paragraph_count': 4,       # Introduction, Body x2, Conclusion
            'keyword_density_target': 0.02,  # 2% keyword density
            'readability_target': 'college',  # Reading level
            'tone_consistency': 0.85    # Tone consistency threshold
        }
        
        # Multi-model ensemble weights for different aspects
        self.model_weights = {
            'content_generation': {'gpt': 0.4, 'claude': 0.4, 'gemini': 0.2},
            'style_refinement': {'claude': 0.5, 'gpt': 0.3, 'gemini': 0.2},
            'technical_accuracy': {'gpt': 0.5, 'claude': 0.3, 'gemini': 0.2},
            'creativity_boost': {'gemini': 0.4, 'claude': 0.4, 'gpt': 0.2}
        }
        
        # Quality assessment criteria
        self.quality_criteria = {
            'relevance_match': 0.25,        # How well it matches job requirements
            'skill_alignment': 0.20,        # How well candidate skills are highlighted
            'writing_quality': 0.20,        # Grammar, flow, professionalism
            'personalization': 0.15,        # Specific to company/role
            'keyword_optimization': 0.10,   # ATS-friendly keywords
            'uniqueness': 0.10              # Stands out from templates
        }
        
        self.logger.info("✍️ CoverLetterAgent initialized with multi-model writing capabilities")
    
    def _initialize_writing_models(self):
        """Initialize AI models optimized for professional writing."""
        
        self.available_writing_models = []
        
        # OpenAI GPT for structured professional writing
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
            self.available_writing_models.append('gpt')
            self.logger.info("✅ OpenAI GPT initialized for cover letter writing")
        
        # Anthropic Claude for nuanced, human-like writing
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            self.available_writing_models.append('claude')
            self.logger.info("✅ Anthropic Claude initialized for cover letter writing")
        
        # Google Gemini for creative and diverse writing perspectives
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if GEMINI_AVAILABLE and gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.available_writing_models.append('gemini')
            self.logger.info("✅ Google Gemini initialized for cover letter writing")
        
        if not self.available_writing_models:
            raise RuntimeError("No AI models available for cover letter generation")
    
    def _load_cover_letter_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load professional cover letter templates and structures."""
        
        return {
            'professional': {
                'structure': ['opening_hook', 'value_proposition', 'evidence_paragraph', 'closing_call_to_action'],
                'opening_strategies': [
                    'mention_mutual_connection',
                    'reference_company_news',
                    'highlight_unique_achievement',
                    'state_compelling_value_prop'
                ],
                'body_strategies': [
                    'quantified_achievements',
                    'relevant_project_example',
                    'skill_requirement_match',
                    'problem_solving_story'
                ],
                'closing_strategies': [
                    'confident_next_steps',
                    'value_reinforcement',
                    'enthusiasm_expression',
                    'interview_request'
                ]
            },
            'technical': {
                'structure': ['technical_hook', 'expertise_showcase', 'project_deep_dive', 'technical_culture_fit'],
                'focus_areas': [
                    'technical_stack_alignment',
                    'architecture_experience',
                    'problem_solving_approach',
                    'continuous_learning',
                    'open_source_contributions'
                ]
            },
            'executive': {
                'structure': ['strategic_vision', 'leadership_impact', 'business_results', 'strategic_alignment'],
                'focus_areas': [
                    'business_transformation',
                    'team_leadership_scale',
                    'revenue_impact',
                    'strategic_initiatives',
                    'industry_expertise'
                ]
            },
            'creative': {
                'structure': ['creative_hook', 'portfolio_highlight', 'creative_process', 'brand_alignment'],
                'focus_areas': [
                    'creative_vision',
                    'portfolio_achievements',
                    'brand_understanding',
                    'innovative_solutions',
                    'collaborative_creativity'
                ]
            }
        }
    
    def _load_writing_strategies(self) -> Dict[str, List[str]]:
        """Load advanced writing strategies and techniques."""
        
        return {
            'persuasion_techniques': [
                'social_proof',           # Mention recognizable companies/achievements
                'authority_positioning',  # Establish credibility and expertise
                'scarcity_mindset',      # Unique value proposition
                'reciprocity',           # Offer value to the company
                'commitment_consistency', # Align with company values
                'liking_rapport'         # Build personal connection
            ],
            'storytelling_frameworks': [
                'star_method',           # Situation, Task, Action, Result
                'challenge_solution',    # Problem faced and solution provided
                'before_after_bridge',   # Current state, desired state, bridge
                'hero_journey',          # Overcoming challenges to achieve success
                'value_story'           # Demonstrating core values through action
            ],
            'persuasive_language': [
                'action_oriented_verbs', # Led, transformed, achieved, delivered
                'quantified_results',   # Specific numbers and percentages
                'industry_keywords',    # Role-specific terminology
                'future_focused',       # What you'll bring to the role
                'collaborative_tone'    # Team-oriented language
            ],
            'attention_grabbers': [
                'surprising_statistic',
                'thoughtful_question', 
                'bold_statement',
                'relevant_quote',
                'industry_insight',
                'personal_anecdote'
            ]
        }
    
    def _load_industry_writing_styles(self) -> Dict[str, Dict[str, Any]]:
        """Load industry-specific writing styles and conventions."""
        
        return {
            'technology': {
                'tone': 'analytical_confident',
                'key_themes': ['innovation', 'scalability', 'efficiency', 'user_experience', 'technical_excellence'],
                'language_style': 'technical_precise',
                'emphasis_areas': ['problem_solving', 'technical_skills', 'project_impact', 'team_collaboration']
            },
            'finance': {
                'tone': 'formal_authoritative',
                'key_themes': ['risk_management', 'roi', 'strategic_planning', 'analytical_rigor', 'compliance'],
                'language_style': 'formal_precise',
                'emphasis_areas': ['quantitative_results', 'analytical_skills', 'attention_to_detail', 'strategic_thinking']
            },
            'healthcare': {
                'tone': 'compassionate_professional',
                'key_themes': ['patient_care', 'safety', 'compliance', 'innovation', 'collaboration'],
                'language_style': 'professional_caring',
                'emphasis_areas': ['patient_outcomes', 'regulatory_knowledge', 'team_collaboration', 'continuous_improvement']
            },
            'consulting': {
                'tone': 'confident_analytical',
                'key_themes': ['strategic_thinking', 'problem_solving', 'client_value', 'expertise', 'results'],
                'language_style': 'strategic_persuasive',
                'emphasis_areas': ['client_impact', 'analytical_skills', 'communication', 'business_acumen']
            },
            'startup': {
                'tone': 'enthusiastic_adaptable',
                'key_themes': ['growth', 'innovation', 'agility', 'impact', 'entrepreneurship'],
                'language_style': 'dynamic_conversational',
                'emphasis_areas': ['adaptability', 'growth_mindset', 'initiative', 'versatility']
            }
        }
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate cover letter generation input data."""
        
        if not isinstance(input_data, dict):
            return {'valid': False, 'errors': ['Input must be a dictionary']}
        
        required_fields = ['resume_data', 'job_description']
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            return {'valid': False, 'errors': [f'Missing required fields: {", ".join(missing_fields)}']}
        
        # Validate resume data structure
        resume_data = input_data['resume_data']
        if not isinstance(resume_data, dict) or 'personal_information' not in resume_data:
            return {'valid': False, 'errors': ['resume_data must contain personal_information']}\n        \n        # Validate job description\n        job_description = input_data['job_description']\n        if not isinstance(job_description, (str, dict)) or not job_description:\n            return {'valid': False, 'errors': ['job_description must be non-empty string or dict']}\n        \n        return {'valid': True, 'errors': []}\n    \n    async def _process_internal(self, input_data: Dict[str, Any]) -> ProcessingResult:\n        \"\"\"Generate personalized cover letters using multi-model AI approach.\"\"\"\n        \n        resume_data = input_data['resume_data']\n        job_description = input_data['job_description']\n        generation_options = input_data.get('generation_options', {})\n        \n        # Initialize generation results\n        results = {\n            'generation_id': f\"cover_letter_{int(time.time())}\",\n            'candidate_name': resume_data.get('personal_information', {}).get('full_name', 'Unknown'),\n            'generation_timestamp': datetime.utcnow().isoformat(),\n            'job_analysis': {},\n            'cover_letter_variants': [],\n            'generation_metadata': {},\n            'quality_assessment': {}\n        }\n        \n        try:\n            # Step 1: Analyze job requirements and extract key information\n            job_analysis = await self._analyze_job_requirements(\n                job_description, generation_options\n            )\n            results['job_analysis'] = job_analysis\n            \n            # Step 2: Match candidate qualifications with job requirements\n            qualification_match = await self._match_qualifications_to_job(\n                resume_data, job_analysis, generation_options\n            )\n            results['qualification_match'] = qualification_match\n            \n            # Step 3: Determine optimal writing style and tone\n            writing_strategy = await self._determine_writing_strategy(\n                job_analysis, resume_data, generation_options\n            )\n            results['writing_strategy'] = writing_strategy\n            \n            # Step 4: Generate multiple cover letter variants using different models\n            cover_letter_variants = await self._generate_cover_letter_variants(\n                resume_data, job_analysis, qualification_match, writing_strategy, generation_options\n            )\n            results['cover_letter_variants'] = cover_letter_variants\n            \n            # Step 5: Apply quality assessment and ranking\n            quality_assessment = await self._assess_cover_letter_quality(\n                cover_letter_variants, job_analysis, qualification_match\n            )\n            results['quality_assessment'] = quality_assessment\n            \n            # Step 6: Generate personalization suggestions\n            personalization_suggestions = await self._generate_personalization_suggestions(\n                cover_letter_variants, job_analysis, resume_data\n            )\n            results['personalization_suggestions'] = personalization_suggestions\n            \n            # Step 7: Select best variant and provide alternatives\n            final_selection = await self._select_and_rank_variants(\n                cover_letter_variants, quality_assessment, generation_options\n            )\n            results['final_selection'] = final_selection\n            \n            # Calculate overall confidence\n            overall_confidence = self._calculate_generation_confidence(results)\n            \n            return ProcessingResult(\n                success=True,\n                result=results,\n                confidence=overall_confidence,\n                processing_time=0.0,  # Will be set by base class\n                metadata={\n                    'variants_generated': len(cover_letter_variants),\n                    'models_used': len(self.available_writing_models),\n                    'job_match_score': qualification_match.get('overall_match_score', 0),\n                    'best_variant_quality': final_selection.get('top_variant', {}).get('quality_score', 0),\n                    'writing_style': writing_strategy.get('recommended_style'),\n                    'personalization_level': 'high' if len(personalization_suggestions) > 5 else 'medium'\n                }\n            )\n            \n        except Exception as e:\n            self.logger.error(f\"Cover letter generation failed: {str(e)}\")\n            return ProcessingResult(\n                success=False,\n                result={'error': str(e), 'generation_id': results['generation_id']},\n                confidence=0.0,\n                processing_time=0.0,\n                metadata={'generation_failed': True}\n            )\n    \n    async def _analyze_job_requirements(self, job_description: Any, options: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Analyze job requirements using AI to extract key information.\"\"\"\n        \n        # Convert job description to string if it's a dict\n        if isinstance(job_description, dict):\n            job_text = json.dumps(job_description, indent=2)\n        else:\n            job_text = str(job_description)\n        \n        analysis_results = {}\n        \n        # Use multiple models for comprehensive analysis\n        for model in self.available_writing_models:\n            try:\n                model_analysis = await self._analyze_job_with_model(model, job_text, options)\n                analysis_results[model] = model_analysis\n            except Exception as e:\n                self.logger.warning(f\"Job analysis failed with {model}: {str(e)}\")\n        \n        # Synthesize results from all models\n        synthesized_analysis = await self._synthesize_job_analysis(analysis_results)\n        \n        return synthesized_analysis\n    \n    async def _analyze_job_with_model(self, model: str, job_text: str, options: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Analyze job requirements using a specific AI model.\"\"\"\n        \n        prompt = f\"\"\"Analyze this job description and extract key information for cover letter writing:\n\n{job_text}\n\nProvide analysis in JSON format with:\n1. company_info: {{name, industry, size, culture, values}}\n2. role_details: {{title, level, department, reporting_structure}}\n3. required_qualifications: [{{skill, importance_level, category}}]\n4. preferred_qualifications: [{{skill, importance_level, category}}]\n5. key_responsibilities: [responsibility descriptions]\n6. compensation_benefits: {{salary_range, benefits, perks}}\n7. application_keywords: [important keywords for ATS]\n8. company_tone: {{formal/casual, innovative/traditional, etc.}}\n9. unique_selling_points: [what makes this role/company attractive]\n10. red_flags: [potential concerns or challenges]\n\nFocus on information that would help write a compelling, targeted cover letter.\"\"\"\n        \n        if model == 'gpt':\n            return await self._analyze_with_gpt(prompt)\n        elif model == 'claude':\n            return await self._analyze_with_claude(prompt)\n        elif model == 'gemini':\n            return await self._analyze_with_gemini(prompt)\n    \n    async def _analyze_with_gpt(self, prompt: str) -> Dict[str, Any]:\n        \"\"\"Analyze job requirements using OpenAI GPT.\"\"\"\n        \n        response = await self.openai_client.chat.completions.create(\n            model=\"gpt-4\",\n            messages=[\n                {\"role\": \"system\", \"content\": \"You are an expert job market analyst and professional writer specializing in cover letter strategy.\"},\n                {\"role\": \"user\", \"content\": prompt}\n            ],\n            temperature=0.3,\n            max_tokens=2000\n        )\n        \n        response_text = response.choices[0].message.content\n        return self._parse_job_analysis_response(response_text, 'gpt')\n    \n    async def _analyze_with_claude(self, prompt: str) -> Dict[str, Any]:\n        \"\"\"Analyze job requirements using Anthropic Claude.\"\"\"\n        \n        response = await self.anthropic_client.messages.create(\n            model=\"claude-3-sonnet-20240229\",\n            max_tokens=2000,\n            temperature=0.3,\n            messages=[\n                {\"role\": \"user\", \"content\": prompt}\n            ]\n        )\n        \n        response_text = response.content[0].text\n        return self._parse_job_analysis_response(response_text, 'claude')\n    \n    async def _analyze_with_gemini(self, prompt: str) -> Dict[str, Any]:\n        \"\"\"Analyze job requirements using Google Gemini.\"\"\"\n        \n        response = await self.gemini_model.generate_content_async(\n            prompt,\n            generation_config={\n                'temperature': 0.3,\n                'top_p': 0.8,\n                'max_output_tokens': 2000\n            }\n        )\n        \n        response_text = response.text\n        return self._parse_job_analysis_response(response_text, 'gemini')\n    \n    def _parse_job_analysis_response(self, response_text: str, model_name: str) -> Dict[str, Any]:\n        \"\"\"Parse AI model response for job analysis.\"\"\"\n        \n        try:\n            # Try to extract JSON from response\n            json_start = response_text.find('{')\n            json_end = response_text.rfind('}') + 1\n            \n            if json_start != -1 and json_end > json_start:\n                json_str = response_text[json_start:json_end]\n                parsed_data = json.loads(json_str)\n                parsed_data['analysis_model'] = model_name\n                return parsed_data\n        except Exception as e:\n            self.logger.warning(f\"Failed to parse {model_name} job analysis response: {e}\")\n        \n        # Fallback: basic text analysis\n        return {\n            'analysis_model': model_name,\n            'raw_analysis': response_text,\n            'parsing_error': True,\n            'fallback_keywords': self._extract_keywords_from_text(response_text)\n        }\n    \n    async def _synthesize_job_analysis(self, analysis_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:\n        \"\"\"Synthesize job analysis results from multiple models.\"\"\"\n        \n        synthesized = {\n            'company_info': {},\n            'role_details': {},\n            'required_qualifications': [],\n            'preferred_qualifications': [],\n            'key_responsibilities': [],\n            'application_keywords': [],\n            'company_tone': 'professional',\n            'unique_selling_points': [],\n            'models_consulted': list(analysis_results.keys()),\n            'synthesis_confidence': 0.0\n        }\n        \n        # Merge company information\n        for model_result in analysis_results.values():\n            if not model_result.get('parsing_error') and 'company_info' in model_result:\n                company_info = model_result['company_info']\n                for key, value in company_info.items():\n                    if value and key not in synthesized['company_info']:\n                        synthesized['company_info'][key] = value\n        \n        # Combine keywords from all models\n        all_keywords = set()\n        for model_result in analysis_results.values():\n            if 'application_keywords' in model_result:\n                keywords = model_result['application_keywords']\n                if isinstance(keywords, list):\n                    all_keywords.update(keywords)\n            elif 'fallback_keywords' in model_result:\n                all_keywords.update(model_result['fallback_keywords'])\n        \n        synthesized['application_keywords'] = list(all_keywords)\n        \n        # Calculate synthesis confidence based on model agreement\n        synthesized['synthesis_confidence'] = self._calculate_synthesis_confidence(analysis_results)\n        \n        return synthesized\n    \n    def _calculate_synthesis_confidence(self, analysis_results: Dict[str, Dict[str, Any]]) -> float:\n        \"\"\"Calculate confidence in synthesized job analysis.\"\"\"\n        \n        successful_analyses = sum(1 for result in analysis_results.values() if not result.get('parsing_error'))\n        total_analyses = len(analysis_results)\n        \n        if total_analyses == 0:\n            return 0.0\n        \n        base_confidence = successful_analyses / total_analyses\n        \n        # Boost confidence if multiple models provided consistent information\n        if successful_analyses >= 2:\n            base_confidence = min(0.95, base_confidence + 0.2)\n        \n        return round(base_confidence, 2)\n    \n    def _extract_keywords_from_text(self, text: str) -> List[str]:\n        \"\"\"Extract potential keywords from text as fallback.\"\"\"\n        \n        # Simple keyword extraction - in production use more sophisticated NLP\n        keywords = []\n        \n        # Common job-related terms\n        job_terms = [\n            'experience', 'skills', 'requirements', 'qualifications', 'responsibilities',\n            'leadership', 'management', 'development', 'analysis', 'communication',\n            'collaboration', 'innovation', 'growth', 'strategy', 'results'\n        ]\n        \n        text_lower = text.lower()\n        for term in job_terms:\n            if term in text_lower:\n                keywords.append(term)\n        \n        return keywords[:10]  # Return top 10 keywords\n    \n    async def _match_qualifications_to_job(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Match candidate qualifications with job requirements.\"\"\"\n        \n        # Extract candidate qualifications\n        candidate_qualifications = self._extract_candidate_qualifications(resume_data)\n        \n        # Extract job requirements\n        job_requirements = self._extract_job_requirements(job_analysis)\n        \n        # Perform matching analysis\n        matches = []\n        for requirement in job_requirements:\n            best_match = self._find_best_qualification_match(requirement, candidate_qualifications)\n            if best_match:\n                matches.append({\n                    'requirement': requirement,\n                    'candidate_qualification': best_match,\n                    'match_strength': self._calculate_match_strength(requirement, best_match),\n                    'how_to_highlight': self._suggest_highlight_strategy(requirement, best_match)\n                })\n        \n        # Calculate overall match score\n        overall_match_score = self._calculate_overall_match_score(matches, job_requirements)\n        \n        return {\n            'qualification_matches': matches,\n            'overall_match_score': overall_match_score,\n            'strengths': [m for m in matches if m['match_strength'] >= 0.8],\n            'moderate_matches': [m for m in matches if 0.5 <= m['match_strength'] < 0.8],\n            'gaps': [req for req in job_requirements if not any(m['requirement'] == req for m in matches)],\n            'unique_value_props': self._identify_unique_value_propositions(resume_data, job_analysis)\n        }\n    \n    def _extract_candidate_qualifications(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:\n        \"\"\"Extract candidate qualifications from resume data.\"\"\"\n        \n        qualifications = []\n        \n        # Skills\n        skills = resume_data.get('skills', {})\n        if isinstance(skills, dict):\n            for category, skill_list in skills.items():\n                if isinstance(skill_list, list):\n                    for skill in skill_list:\n                        qualifications.append({\n                            'type': 'skill',\n                            'category': category,\n                            'name': skill,\n                            'source': 'skills_section'\n                        })\n                elif isinstance(skill_list, dict):\n                    for subcategory, subskills in skill_list.items():\n                        if isinstance(subskills, list):\n                            for skill in subskills:\n                                qualifications.append({\n                                    'type': 'skill',\n                                    'category': f\"{category}.{subcategory}\",\n                                    'name': skill,\n                                    'source': 'skills_section'\n                                })\n        \n        # Work experience\n        for job in resume_data.get('work_experience', []):\n            # Add position titles as qualifications\n            if job.get('position_title'):\n                qualifications.append({\n                    'type': 'experience',\n                    'category': 'position',\n                    'name': job['position_title'],\n                    'context': job.get('company_name', ''),\n                    'duration': f\"{job.get('start_date', '')} - {job.get('end_date', '')}\",\n                    'source': 'work_experience'\n                })\n            \n            # Add technologies as qualifications\n            for tech in job.get('technologies_used', []):\n                qualifications.append({\n                    'type': 'skill',\n                    'category': 'technical',\n                    'name': tech,\n                    'context': f\"Used at {job.get('company_name', '')}\",\n                    'source': 'work_experience'\n                })\n        \n        # Education\n        for edu in resume_data.get('education', []):\n            qualifications.append({\n                'type': 'education',\n                'category': 'degree',\n                'name': edu.get('degree_name', ''),\n                'context': edu.get('institution_name', ''),\n                'field': edu.get('field_of_study', ''),\n                'source': 'education'\n            })\n        \n        # Certifications\n        for cert in resume_data.get('certifications', []):\n            qualifications.append({\n                'type': 'certification',\n                'category': 'professional',\n                'name': cert.get('certification_name', ''),\n                'issuer': cert.get('issuing_organization', ''),\n                'source': 'certifications'\n            })\n        \n        return qualifications\n    \n    def _extract_job_requirements(self, job_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:\n        \"\"\"Extract job requirements from job analysis.\"\"\"\n        \n        requirements = []\n        \n        # Required qualifications\n        for req in job_analysis.get('required_qualifications', []):\n            if isinstance(req, dict):\n                requirements.append({\n                    'name': req.get('skill', ''),\n                    'importance': req.get('importance_level', 'required'),\n                    'category': req.get('category', 'unknown'),\n                    'type': 'required'\n                })\n            elif isinstance(req, str):\n                requirements.append({\n                    'name': req,\n                    'importance': 'required',\n                    'category': 'unknown',\n                    'type': 'required'\n                })\n        \n        # Preferred qualifications\n        for pref in job_analysis.get('preferred_qualifications', []):\n            if isinstance(pref, dict):\n                requirements.append({\n                    'name': pref.get('skill', ''),\n                    'importance': pref.get('importance_level', 'preferred'),\n                    'category': pref.get('category', 'unknown'),\n                    'type': 'preferred'\n                })\n            elif isinstance(pref, str):\n                requirements.append({\n                    'name': pref,\n                    'importance': 'preferred',\n                    'category': 'unknown',\n                    'type': 'preferred'\n                })\n        \n        return requirements\n    \n    def _find_best_qualification_match(self, requirement: Dict[str, Any], qualifications: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:\n        \"\"\"Find the best matching qualification for a job requirement.\"\"\"\n        \n        requirement_name = requirement['name'].lower()\n        best_match = None\n        best_score = 0.0\n        \n        for qual in qualifications:\n            qual_name = qual['name'].lower()\n            \n            # Exact match\n            if requirement_name == qual_name:\n                return qual\n            \n            # Partial match\n            if requirement_name in qual_name or qual_name in requirement_name:\n                score = max(len(requirement_name) / len(qual_name), len(qual_name) / len(requirement_name))\n                if score > best_score:\n                    best_score = score\n                    best_match = qual\n            \n            # Keyword match\n            req_words = set(requirement_name.split())\n            qual_words = set(qual_name.split())\n            intersection = req_words.intersection(qual_words)\n            if intersection:\n                score = len(intersection) / max(len(req_words), len(qual_words))\n                if score > best_score and score > 0.3:\n                    best_score = score\n                    best_match = qual\n        \n        return best_match if best_score > 0.3 else None\n    \n    def _calculate_match_strength(self, requirement: Dict[str, Any], qualification: Dict[str, Any]) -> float:\n        \"\"\"Calculate match strength between requirement and qualification.\"\"\"\n        \n        req_name = requirement['name'].lower()\n        qual_name = qualification['name'].lower()\n        \n        # Exact match\n        if req_name == qual_name:\n            return 1.0\n        \n        # Calculate similarity\n        req_words = set(req_name.split())\n        qual_words = set(qual_name.split())\n        \n        if not req_words or not qual_words:\n            return 0.0\n        \n        intersection = req_words.intersection(qual_words)\n        union = req_words.union(qual_words)\n        \n        jaccard_similarity = len(intersection) / len(union) if union else 0.0\n        \n        # Boost score for work experience context\n        if qualification.get('source') == 'work_experience':\n            jaccard_similarity = min(1.0, jaccard_similarity + 0.2)\n        \n        return round(jaccard_similarity, 2)\n    \n    def _suggest_highlight_strategy(self, requirement: Dict[str, Any], qualification: Dict[str, Any]) -> str:\n        \"\"\"Suggest how to highlight the qualification match in the cover letter.\"\"\"\n        \n        if qualification.get('source') == 'work_experience':\n            return f\"Highlight experience with {qualification['name']} at {qualification.get('context', 'previous role')}\"\n        elif qualification.get('source') == 'skills_section':\n            return f\"Emphasize proficiency in {qualification['name']} from skills section\"\n        elif qualification.get('source') == 'education':\n            return f\"Mention {qualification['name']} from academic background at {qualification.get('context', 'university')}\"\n        elif qualification.get('source') == 'certifications':\n            return f\"Reference {qualification['name']} certification from {qualification.get('issuer', 'certification body')}\"\n        else:\n            return f\"Include relevant experience with {qualification['name']}\"\n    \n    def _calculate_overall_match_score(self, matches: List[Dict[str, Any]], requirements: List[Dict[str, Any]]) -> float:\n        \"\"\"Calculate overall match score between candidate and job.\"\"\"\n        \n        if not requirements:\n            return 0.0\n        \n        total_weight = 0.0\n        weighted_score = 0.0\n        \n        for req in requirements:\n            # Weight required qualifications higher than preferred\n            weight = 1.0 if req.get('type') == 'required' else 0.5\n            total_weight += weight\n            \n            # Find matching score\n            match = next((m for m in matches if m['requirement'] == req), None)\n            if match:\n                weighted_score += match['match_strength'] * weight\n        \n        return round(weighted_score / total_weight if total_weight > 0 else 0.0, 2)\n    \n    def _identify_unique_value_propositions(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> List[str]:\n        \"\"\"Identify unique value propositions that set candidate apart.\"\"\"\n        \n        unique_props = []\n        \n        # Look for unique combinations of skills\n        skills = resume_data.get('skills', {})\n        if isinstance(skills, dict) and skills.get('technical_skills'):\n            tech_skills = skills['technical_skills']\n            if isinstance(tech_skills, dict):\n                skill_areas = list(tech_skills.keys())\n                if len(skill_areas) >= 3:\n                    unique_props.append(f\"Cross-functional expertise spanning {', '.join(skill_areas[:3])}\")\n        \n        # Look for leadership + technical combination\n        has_leadership = any('leadership' in str(skill).lower() for skill_list in skills.values() if isinstance(skill_list, list) for skill in skill_list)\n        has_technical = bool(skills.get('technical_skills'))\n        if has_leadership and has_technical:\n            unique_props.append(\"Rare combination of technical expertise and proven leadership capabilities\")\n        \n        # Look for industry transitions\n        work_exp = resume_data.get('work_experience', [])\n        if len(work_exp) >= 2:\n            companies = [job.get('company_name', '') for job in work_exp]\n            # This would analyze company industries in production\n            unique_props.append(\"Diverse industry experience bringing fresh perspectives\")\n        \n        # Look for educational background + experience alignment\n        education = resume_data.get('education', [])\n        if education:\n            degrees = [edu.get('field_of_study', '') for edu in education]\n            if degrees:\n                unique_props.append(f\"Strong academic foundation in {degrees[0]} with practical industry application\")\n        \n        return unique_props[:3]  # Return top 3 unique value propositions\n    \n    async def _determine_writing_strategy(self, job_analysis: Dict[str, Any], resume_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Determine optimal writing strategy based on job and candidate analysis.\"\"\"\n        \n        # Determine industry and company culture\n        company_info = job_analysis.get('company_info', {})\n        industry = company_info.get('industry', 'technology').lower()\n        company_tone = job_analysis.get('company_tone', 'professional')\n        \n        # Map to writing style\n        style_mapping = {\n            'technology': CoverLetterStyle.TECHNICAL,\n            'finance': CoverLetterStyle.PROFESSIONAL,\n            'healthcare': CoverLetterStyle.PROFESSIONAL,\n            'consulting': CoverLetterStyle.CONSULTING,\n            'startup': CoverLetterStyle.STARTUP,\n            'creative': CoverLetterStyle.CREATIVE,\n            'academic': CoverLetterStyle.ACADEMIC\n        }\n        \n        recommended_style = style_mapping.get(industry, CoverLetterStyle.PROFESSIONAL)\n        \n        # Determine tone based on company culture\n        tone_mapping = {\n            'formal': CoverLetterTone.FORMAL,\n            'casual': CoverLetterTone.CONVERSATIONAL,\n            'innovative': CoverLetterTone.ENTHUSIASTIC,\n            'traditional': CoverLetterTone.FORMAL,\n            'analytical': CoverLetterTone.ANALYTICAL\n        }\n        \n        recommended_tone = tone_mapping.get(company_tone, CoverLetterTone.CONFIDENT)\n        \n        # Select persuasion strategies\n        persuasion_strategies = self._select_persuasion_strategies(\n            job_analysis, resume_data, recommended_style\n        )\n        \n        # Select storytelling framework\n        storytelling_framework = self._select_storytelling_framework(\n            job_analysis, resume_data, recommended_style\n        )\n        \n        return {\n            'recommended_style': recommended_style.value,\n            'recommended_tone': recommended_tone.value,\n            'industry_context': industry,\n            'company_culture': company_tone,\n            'persuasion_strategies': persuasion_strategies,\n            'storytelling_framework': storytelling_framework,\n            'length_target': self.generation_config['max_length'],\n            'keyword_density_target': self.generation_config['keyword_density_target']\n        }\n    \n    def _select_persuasion_strategies(self, job_analysis: Dict[str, Any], resume_data: Dict[str, Any], style: CoverLetterStyle) -> List[str]:\n        \"\"\"Select appropriate persuasion strategies based on context.\"\"\"\n        \n        strategies = []\n        \n        # Always include authority positioning if candidate has relevant experience\n        work_exp = resume_data.get('work_experience', [])\n        if work_exp:\n            strategies.append('authority_positioning')\n        \n        # Social proof if worked at recognizable companies\n        if any(job.get('company_name', '') for job in work_exp):\n            strategies.append('social_proof')\n        \n        # Reciprocity - always offer value\n        strategies.append('reciprocity')\n        \n        # Style-specific strategies\n        if style in [CoverLetterStyle.STARTUP, CoverLetterStyle.CREATIVE]:\n            strategies.append('commitment_consistency')\n        \n        if style in [CoverLetterStyle.TECHNICAL, CoverLetterStyle.CONSULTING]:\n            strategies.append('scarcity_mindset')  # Unique technical expertise\n        \n        return strategies\n    \n    def _select_storytelling_framework(self, job_analysis: Dict[str, Any], resume_data: Dict[str, Any], style: CoverLetterStyle) -> str:\n        \"\"\"Select appropriate storytelling framework.\"\"\"\n        \n        # Technical roles prefer STAR method\n        if style == CoverLetterStyle.TECHNICAL:\n            return 'star_method'\n        \n        # Executive roles prefer challenge-solution\n        if style == CoverLetterStyle.EXECUTIVE:\n            return 'challenge_solution'\n        \n        # Creative roles prefer hero journey\n        if style == CoverLetterStyle.CREATIVE:\n            return 'hero_journey'\n        \n        # Default to value story\n        return 'value_story'\n    \n    # Placeholder methods for remaining functionality\n    async def _generate_cover_letter_variants(self, resume_data, job_analysis, qualification_match, writing_strategy, options) -> List[Dict[str, Any]]:\n        \"\"\"Generate multiple cover letter variants using different AI models.\"\"\"\n        \n        variants = []\n        \n        # Generate variant with each available model\n        for model in self.available_writing_models:\n            try:\n                variant = await self._generate_variant_with_model(\n                    model, resume_data, job_analysis, qualification_match, writing_strategy, options\n                )\n                variants.append(variant)\n            except Exception as e:\n                self.logger.warning(f\"Variant generation failed with {model}: {str(e)}\")\n        \n        return variants\n    \n    async def _generate_variant_with_model(self, model, resume_data, job_analysis, qualification_match, writing_strategy, options) -> Dict[str, Any]:\n        \"\"\"Generate a cover letter variant using a specific AI model.\"\"\"\n        \n        # Create comprehensive prompt\n        prompt = self._create_cover_letter_prompt(\n            resume_data, job_analysis, qualification_match, writing_strategy\n        )\n        \n        # Generate with specific model\n        if model == 'gpt':\n            content = await self._generate_with_gpt(prompt, writing_strategy)\n        elif model == 'claude':\n            content = await self._generate_with_claude(prompt, writing_strategy)\n        elif model == 'gemini':\n            content = await self._generate_with_gemini(prompt, writing_strategy)\n        \n        return {\n            'variant_id': f\"{model}_variant_{int(time.time())}\",\n            'model_used': model,\n            'content': content,\n            'style': writing_strategy['recommended_style'],\n            'tone': writing_strategy['recommended_tone'],\n            'word_count': len(content.split()),\n            'generation_timestamp': datetime.utcnow().isoformat()\n        }\n    \n    def _create_cover_letter_prompt(self, resume_data, job_analysis, qualification_match, writing_strategy) -> str:\n        \"\"\"Create comprehensive prompt for cover letter generation.\"\"\"\n        \n        candidate_name = resume_data.get('personal_information', {}).get('full_name', 'Candidate')\n        company_name = job_analysis.get('company_info', {}).get('name', 'the company')\n        role_title = job_analysis.get('role_details', {}).get('title', 'the position')\n        \n        # Extract top qualification matches\n        strengths = qualification_match.get('strengths', [])[:3]\n        strength_text = '\\n'.join([f\"- {s['requirement']['name']}: {s['how_to_highlight']}\" for s in strengths])\n        \n        prompt = f\"\"\"Write a compelling, professional cover letter for {candidate_name} applying to {role_title} at {company_name}.\n\nSTYLE: {writing_strategy['recommended_style']}\nTONE: {writing_strategy['recommended_tone']}\nLENGTH: {writing_strategy['length_target']} words maximum\n\nCOVER LETTER STRUCTURE:\n1. Opening Hook: Start with an engaging opening that captures attention\n2. Value Proposition: Clearly state what you bring to the role\n3. Evidence Paragraph: Provide specific examples and achievements\n4. Closing Call to Action: End with confidence and next steps\n\nKEY QUALIFICATIONS TO HIGHLIGHT:\n{strength_text}\n\nWRITING GUIDELINES:\n- Use {writing_strategy['storytelling_framework']} framework\n- Apply persuasion strategies: {', '.join(writing_strategy['persuasion_strategies'])}\n- Include relevant keywords naturally\n- Show enthusiasm for the role and company\n- Quantify achievements where possible\n- Maintain professional tone throughout\n- End with a strong call to action\n\nEnsure the letter is:\n- Highly personalized and specific\n- ATS-friendly with relevant keywords\n- Professional yet engaging\n- Focused on value to the employer\n- Free of generic template language\n\nGenerate only the cover letter content, no additional commentary.\"\"\"\n        \n        return prompt\n    \n    async def _generate_with_gpt(self, prompt: str, writing_strategy: Dict[str, Any]) -> str:\n        \"\"\"Generate cover letter content using OpenAI GPT.\"\"\"\n        \n        response = await self.openai_client.chat.completions.create(\n            model=\"gpt-4\",\n            messages=[\n                {\"role\": \"system\", \"content\": \"You are an expert professional writer specializing in compelling cover letters that get results.\"},\n                {\"role\": \"user\", \"content\": prompt}\n            ],\n            temperature=0.7,  # Higher creativity for writing\n            max_tokens=800\n        )\n        \n        return response.choices[0].message.content.strip()\n    \n    async def _generate_with_claude(self, prompt: str, writing_strategy: Dict[str, Any]) -> str:\n        \"\"\"Generate cover letter content using Anthropic Claude.\"\"\"\n        \n        response = await self.anthropic_client.messages.create(\n            model=\"claude-3-sonnet-20240229\",\n            max_tokens=800,\n            temperature=0.7,\n            messages=[\n                {\"role\": \"user\", \"content\": prompt}\n            ]\n        )\n        \n        return response.content[0].text.strip()\n    \n    async def _generate_with_gemini(self, prompt: str, writing_strategy: Dict[str, Any]) -> str:\n        \"\"\"Generate cover letter content using Google Gemini.\"\"\"\n        \n        response = await self.gemini_model.generate_content_async(\n            prompt,\n            generation_config={\n                'temperature': 0.7,\n                'top_p': 0.9,\n                'max_output_tokens': 800\n            }\n        )\n        \n        return response.text.strip()\n    \n    # Placeholder methods for quality assessment and final selection\n    async def _assess_cover_letter_quality(self, variants, job_analysis, qualification_match) -> Dict[str, Any]:\n        \"\"\"Assess quality of generated cover letter variants.\"\"\"\n        return {'assessment_method': 'comprehensive_scoring', 'variants_assessed': len(variants)}\n    \n    async def _generate_personalization_suggestions(self, variants, job_analysis, resume_data) -> List[str]:\n        \"\"\"Generate suggestions for personalizing the cover letter.\"\"\"\n        return [\n            \"Research recent company news or achievements to mention\",\n            \"Find mutual connections on LinkedIn to reference\",\n            \"Tailor opening paragraph to specific role requirements\",\n            \"Include quantified achievements relevant to the position\",\n            \"Customize closing to reflect company culture and values\"\n        ]\n    \n    async def _select_and_rank_variants(self, variants, quality_assessment, options) -> Dict[str, Any]:\n        \"\"\"Select and rank cover letter variants by quality.\"\"\"\n        return {\n            'top_variant': variants[0] if variants else {},\n            'ranking_method': 'quality_scoring',\n            'alternatives': variants[1:3] if len(variants) > 1 else []\n        }\n    \n    def _calculate_generation_confidence(self, results: Dict[str, Any]) -> float:\n        \"\"\"Calculate overall confidence in cover letter generation.\"\"\"\n        \n        confidence_factors = []\n        \n        # Job analysis confidence\n        job_analysis = results.get('job_analysis', {})\n        if job_analysis.get('synthesis_confidence'):\n            confidence_factors.append(job_analysis['synthesis_confidence'])\n        \n        # Qualification match score\n        qual_match = results.get('qualification_match', {})\n        if qual_match.get('overall_match_score'):\n            confidence_factors.append(qual_match['overall_match_score'])\n        \n        # Variant generation success\n        variants = results.get('cover_letter_variants', [])\n        if variants:\n            generation_success = len(variants) / len(self.available_writing_models)\n            confidence_factors.append(generation_success)\n        \n        # Default baseline\n        confidence_factors.append(0.7)\n        \n        return round(sum(confidence_factors) / len(confidence_factors), 2)