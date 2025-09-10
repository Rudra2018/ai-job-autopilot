"""
📝 ParserAgent: Multi-model resume parsing with ensemble reasoning
Advanced AI-powered agent for parsing resumes using GPT-4o, Claude 3.5, and Gemini Pro in ensemble mode.
"""

import asyncio
import json
import os
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import openai
import anthropic
import hashlib
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base_agent import BaseAgent, ProcessingResult

class ParsingConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ModelResult:
    model_name: str
    parsed_data: Dict[str, Any]
    confidence: float
    processing_time: float
    errors: List[str]
    warnings: List[str]

class ParserAgent(BaseAgent):
    """
    📝 ParserAgent: Multi-model resume parsing with ensemble reasoning
    
    Goals:
    1. Use GPT-4o, Claude 3.5, and Gemini Pro in ensemble mode to parse resumes
    2. Accept raw text, PDF, or JSON input from OCRAgent
    3. Extract comprehensive structured information with confidence scoring
    4. Normalize dates, locations, and job titles using industry standards
    5. Handle incomplete or inconsistent resumes gracefully with intelligent fallbacks
    6. Reconcile model disagreements using voting and consensus mechanisms
    """
    
    def _setup_agent_specific_config(self):
        """Setup Parser-specific configurations with multi-model ensemble."""
        
        self.available_models = []
        self.model_configs = {}
        
        # Initialize OpenAI GPT-4o
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
            self.available_models.append('gpt-4o')
            self.model_configs['gpt-4o'] = {
                'max_tokens': 4000,
                'temperature': 0.1,
                'top_p': 0.9
            }
            self.logger.info("✅ OpenAI GPT-4o initialized")
        
        # Initialize Anthropic Claude 3.5
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            self.available_models.append('claude-3.5-sonnet')
            self.model_configs['claude-3.5-sonnet'] = {
                'max_tokens': 4000,
                'temperature': 0.1
            }
            self.logger.info("✅ Anthropic Claude 3.5 Sonnet initialized")
        
        # Initialize Google Gemini Pro
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if GEMINI_AVAILABLE and gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.available_models.append('gemini-pro')
            self.model_configs['gemini-pro'] = {
                'temperature': 0.1,
                'top_p': 0.8,
                'top_k': 40
            }
            self.logger.info("✅ Google Gemini Pro initialized")
        
        if not self.available_models:
            raise RuntimeError("No AI models available. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY.")
        
        # Ensemble configuration
        self.consensus_threshold = 0.7
        self.min_models_agreement = 2
        self.confidence_weights = {
            'gpt-4o': 1.0,
            'claude-3.5-sonnet': 1.0,
            'gemini-pro': 0.9
        }
        
        # Define comprehensive structured output schema
        self.resume_schema = self._get_comprehensive_resume_schema()
        
        # Data normalization settings
        self.normalization_enabled = True
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %Y', '%b %Y', 
            '%Y', '%m/%Y', '%Y-%m', 'Present', 'Current'
        ]
        
        self.logger.info(f"📝 ParserAgent initialized with {len(self.available_models)} models: {self.available_models}")
    
    def _get_comprehensive_resume_schema(self) -> Dict[str, Any]:
        """Define the comprehensive structured resume schema for multi-model ensemble."""
        
        return {
            "type": "object",
            "properties": {
                "personal_information": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string", "description": "Full name of the candidate"},
                        "first_name": {"type": "string", "description": "First name extracted separately"},
                        "last_name": {"type": "string", "description": "Last name extracted separately"},
                        "email": {"type": "string", "format": "email", "description": "Primary email address"},
                        "alternative_emails": {"type": "array", "items": {"type": "string"}, "description": "Additional email addresses"},
                        "phone": {"type": "string", "description": "Primary phone number"},
                        "alternative_phones": {"type": "array", "items": {"type": "string"}, "description": "Additional phone numbers"},
                        "location": {
                            "type": "object",
                            "properties": {
                                "full_address": {"type": "string", "description": "Complete address if available"},
                                "city": {"type": "string", "description": "City name"},
                                "state": {"type": "string", "description": "State/Province"},
                                "country": {"type": "string", "description": "Country name"},
                                "postal_code": {"type": "string", "description": "ZIP/Postal code"},
                                "coordinates": {
                                    "type": "object",
                                    "properties": {
                                        "latitude": {"type": "number"},
                                        "longitude": {"type": "number"}
                                    }
                                }
                            }
                        },
                        "social_profiles": {
                            "type": "object",
                            "properties": {
                                "linkedin_url": {"type": "string", "format": "uri"},
                                "github_url": {"type": "string", "format": "uri"},
                                "portfolio_url": {"type": "string", "format": "uri"},
                                "personal_website": {"type": "string", "format": "uri"},
                                "twitter_handle": {"type": "string"},
                                "stackoverflow_profile": {"type": "string", "format": "uri"},
                                "medium_profile": {"type": "string", "format": "uri"}
                            }
                        },
                        "preferred_name": {"type": "string", "description": "How they prefer to be addressed"},
                        "nationality": {"type": "string", "description": "Nationality if mentioned"},
                        "work_authorization": {"type": "string", "description": "Work authorization status"}
                    },
                    "required": ["full_name"]
                },
                "professional_summary": {
                    "type": "object",
                    "properties": {
                        "summary_text": {"type": "string", "description": "Professional summary or objective"},
                        "career_objective": {"type": "string", "description": "Career objective if different from summary"},
                        "years_experience": {"type": "number", "description": "Total years of professional experience"},
                        "experience_level": {"type": "string", "enum": ["entry", "junior", "mid", "senior", "lead", "principal", "executive"], "description": "Experience level classification"},
                        "key_strengths": {"type": "array", "items": {"type": "string"}, "description": "Key professional strengths"},
                        "career_highlights": {"type": "array", "items": {"type": "string"}, "description": "Major career achievements"},
                        "industry_focus": {"type": "array", "items": {"type": "string"}, "description": "Industry domains of expertise"},
                        "functional_areas": {"type": "array", "items": {"type": "string"}, "description": "Functional areas of expertise"}
                    }
                },
                "work_experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company_name": {"type": "string", "description": "Company name"},
                            "company_industry": {"type": "string", "description": "Industry of the company"},
                            "company_size": {"type": "string", "description": "Company size if mentioned"},
                            "position_title": {"type": "string", "description": "Job title/position"},
                            "employment_type": {"type": "string", "enum": ["full-time", "part-time", "contract", "freelance", "internship", "temporary"], "description": "Type of employment"},
                            "start_date": {"type": "string", "description": "Start date (normalized format)"},
                            "end_date": {"type": "string", "description": "End date or 'present' if current"},
                            "duration": {"type": "string", "description": "Duration calculated or mentioned"},
                            "location": {
                                "type": "object",
                                "properties": {
                                    "city": {"type": "string"},
                                    "state": {"type": "string"},
                                    "country": {"type": "string"},
                                    "remote": {"type": "boolean", "description": "Whether the position was remote"}
                                }
                            },
                            "job_description": {"type": "string", "description": "Overall job description"},
                            "key_responsibilities": {"type": "array", "items": {"type": "string"}, "description": "Key responsibilities and duties"},
                            "achievements": {"type": "array", "items": {"type": "string"}, "description": "Quantifiable achievements and accomplishments"},
                            "technologies_used": {"type": "array", "items": {"type": "string"}, "description": "Technologies, tools, and frameworks used"},
                            "team_size": {"type": "string", "description": "Team size managed or worked with"},
                            "reporting_structure": {"type": "string", "description": "Reporting relationships"},
                            "promoted_from": {"type": "string", "description": "Previous role if promoted internally"},
                            "reason_for_leaving": {"type": "string", "description": "Reason for leaving if mentioned"}
                        },
                        "required": ["company_name", "position_title"]
                    }
                },
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "institution_name": {"type": "string", "description": "Name of educational institution"},
                            "institution_type": {"type": "string", "enum": ["university", "college", "community_college", "vocational", "online", "bootcamp"], "description": "Type of institution"},
                            "degree_type": {"type": "string", "enum": ["bachelor", "master", "doctorate", "associate", "certificate", "diploma", "professional"], "description": "Type of degree"},
                            "degree_name": {"type": "string", "description": "Full degree name"},
                            "field_of_study": {"type": "string", "description": "Major/field of study"},
                            "minor": {"type": "string", "description": "Minor field if applicable"},
                            "concentration": {"type": "string", "description": "Concentration or specialization"},
                            "graduation_date": {"type": "string", "description": "Graduation date"},
                            "expected_graduation": {"type": "string", "description": "Expected graduation if current student"},
                            "gpa": {"type": "string", "description": "GPA if mentioned"},
                            "gpa_scale": {"type": "string", "description": "GPA scale (e.g., 4.0, 10.0)"},
                            "honors_awards": {"type": "array", "items": {"type": "string"}, "description": "Academic honors and awards"},
                            "relevant_coursework": {"type": "array", "items": {"type": "string"}, "description": "Relevant courses taken"},
                            "thesis_dissertation": {"type": "string", "description": "Thesis or dissertation title"},
                            "advisor": {"type": "string", "description": "Academic advisor if mentioned"},
                            "location": {
                                "type": "object",
                                "properties": {
                                    "city": {"type": "string"},
                                    "state": {"type": "string"},
                                    "country": {"type": "string"}
                                }
                            },
                            "accreditation": {"type": "string", "description": "Accreditation information"}
                        },
                        "required": ["institution_name", "degree_name"]
                    }
                },
                "skills": {
                    "type": "object",
                    "properties": {
                        "technical_skills": {
                            "type": "object",
                            "properties": {
                                "programming_languages": {"type": "array", "items": {"type": "string"}, "description": "Programming languages with proficiency levels"},
                                "frameworks_libraries": {"type": "array", "items": {"type": "string"}, "description": "Frameworks and libraries"},
                                "databases": {"type": "array", "items": {"type": "string"}, "description": "Database technologies"},
                                "cloud_platforms": {"type": "array", "items": {"type": "string"}, "description": "Cloud platforms and services"},
                                "devops_tools": {"type": "array", "items": {"type": "string"}, "description": "DevOps and deployment tools"},
                                "development_tools": {"type": "array", "items": {"type": "string"}, "description": "Development environments and tools"},
                                "operating_systems": {"type": "array", "items": {"type": "string"}, "description": "Operating systems"},
                                "web_technologies": {"type": "array", "items": {"type": "string"}, "description": "Web technologies (HTML, CSS, etc.)"},
                                "mobile_technologies": {"type": "array", "items": {"type": "string"}, "description": "Mobile development technologies"},
                                "data_science_ml": {"type": "array", "items": {"type": "string"}, "description": "Data science and ML tools"},
                                "testing_tools": {"type": "array", "items": {"type": "string"}, "description": "Testing frameworks and tools"},
                                "version_control": {"type": "array", "items": {"type": "string"}, "description": "Version control systems"},
                                "methodologies": {"type": "array", "items": {"type": "string"}, "description": "Development methodologies"}
                            }
                        },
                        "soft_skills": {"type": "array", "items": {"type": "string"}, "description": "Interpersonal and soft skills"},
                        "languages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "language": {"type": "string", "description": "Language name"},
                                    "proficiency": {"type": "string", "enum": ["native", "fluent", "advanced", "intermediate", "basic"], "description": "Proficiency level"},
                                    "certifications": {"type": "array", "items": {"type": "string"}, "description": "Language certifications"}
                                }
                            }
                        },
                        "domain_expertise": {"type": "array", "items": {"type": "string"}, "description": "Domain-specific expertise areas"}
                    }
                },
                "certifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "certification_name": {"type": "string", "description": "Name of certification"},
                            "issuing_organization": {"type": "string", "description": "Organization that issued the certification"},
                            "issue_date": {"type": "string", "description": "Date certification was issued"},
                            "expiry_date": {"type": "string", "description": "Expiration date if applicable"},
                            "credential_id": {"type": "string", "description": "Credential ID or number"},
                            "verification_url": {"type": "string", "format": "uri", "description": "URL for verification"},
                            "certification_type": {"type": "string", "enum": ["professional", "technical", "academic", "vendor", "industry"], "description": "Type of certification"},
                            "renewal_required": {"type": "boolean", "description": "Whether renewal is required"},
                            "continuing_education_hours": {"type": "number", "description": "CE hours required for maintenance"}
                        },
                        "required": ["certification_name", "issuing_organization"]
                    }
                },
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Name of the project"},
                            "project_type": {"type": "string", "enum": ["personal", "professional", "academic", "open_source", "client"], "description": "Type of project"},
                            "description": {"type": "string", "description": "Detailed project description"},
                            "role": {"type": "string", "description": "Your role in the project"},
                            "start_date": {"type": "string", "description": "Project start date"},
                            "end_date": {"type": "string", "description": "Project end date"},
                            "duration": {"type": "string", "description": "Project duration"},
                            "technologies_used": {"type": "array", "items": {"type": "string"}, "description": "Technologies and tools used"},
                            "team_size": {"type": "string", "description": "Size of project team"},
                            "key_achievements": {"type": "array", "items": {"type": "string"}, "description": "Key achievements and outcomes"},
                            "challenges_overcome": {"type": "array", "items": {"type": "string"}, "description": "Challenges faced and overcome"},
                            "project_url": {"type": "string", "format": "uri", "description": "Live project URL"},
                            "repository_url": {"type": "string", "format": "uri", "description": "Source code repository URL"},
                            "demo_video_url": {"type": "string", "format": "uri", "description": "Demo video URL"},
                            "awards_recognition": {"type": "array", "items": {"type": "string"}, "description": "Awards or recognition received"}
                        },
                        "required": ["project_name", "description"]
                    }
                },
                "publications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Publication title"},
                            "authors": {"type": "array", "items": {"type": "string"}, "description": "List of authors"},
                            "publication_venue": {"type": "string", "description": "Journal, conference, or venue"},
                            "publication_date": {"type": "string", "description": "Date of publication"},
                            "publication_type": {"type": "string", "enum": ["journal", "conference", "workshop", "book", "chapter", "patent"], "description": "Type of publication"},
                            "doi": {"type": "string", "description": "DOI if available"},
                            "url": {"type": "string", "format": "uri", "description": "URL to publication"},
                            "abstract": {"type": "string", "description": "Publication abstract"},
                            "keywords": {"type": "array", "items": {"type": "string"}, "description": "Publication keywords"}
                        },
                        "required": ["title", "publication_venue"]
                    }
                },
                "awards_honors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "award_name": {"type": "string", "description": "Name of award or honor"},
                            "issuing_organization": {"type": "string", "description": "Organization that gave the award"},
                            "date_received": {"type": "string", "description": "Date award was received"},
                            "description": {"type": "string", "description": "Description of the award"},
                            "award_type": {"type": "string", "enum": ["academic", "professional", "community", "recognition", "achievement"], "description": "Type of award"},
                            "monetary_value": {"type": "string", "description": "Monetary value if applicable"}
                        },
                        "required": ["award_name", "issuing_organization"]
                    }
                },
                "volunteer_experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "organization": {"type": "string", "description": "Volunteer organization"},
                            "role": {"type": "string", "description": "Volunteer role or position"},
                            "start_date": {"type": "string", "description": "Start date"},
                            "end_date": {"type": "string", "description": "End date"},
                            "description": {"type": "string", "description": "Description of volunteer work"},
                            "skills_used": {"type": "array", "items": {"type": "string"}, "description": "Skills utilized"},
                            "impact": {"type": "string", "description": "Impact or outcomes achieved"},
                            "hours_contributed": {"type": "number", "description": "Total hours contributed"}
                        },
                        "required": ["organization", "role"]
                    }
                },
                "additional_information": {
                    "type": "object",
                    "properties": {
                        "interests_hobbies": {"type": "array", "items": {"type": "string"}, "description": "Personal interests and hobbies"},
                        "professional_memberships": {"type": "array", "items": {"type": "string"}, "description": "Professional associations and memberships"},
                        "security_clearance": {"type": "string", "description": "Security clearance level if applicable"},
                        "military_service": {
                            "type": "object",
                            "properties": {
                                "branch": {"type": "string"},
                                "rank": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "discharge_type": {"type": "string"},
                                "specialties": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "references_available": {"type": "boolean", "description": "Whether references are available upon request"},
                        "relocation_willingness": {"type": "string", "description": "Willingness to relocate"},
                        "remote_work_preference": {"type": "string", "description": "Remote work preferences"},
                        "salary_expectations": {"type": "string", "description": "Salary expectations if mentioned"},
                        "availability": {"type": "string", "description": "Availability to start"},
                        "visa_status": {"type": "string", "description": "Visa or work authorization status"}
                    }
                }
            },
            "required": ["personal_information"]
        }
    
    def _get_resume_schema(self) -> Dict[str, Any]:
        """Define the structured resume schema."""
        
        return {
            "type": "object",
            "properties": {
                "personal_information": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "location": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string"},
                                "state": {"type": "string"},
                                "country": {"type": "string"}
                            }
                        },
                        "linkedin_url": {"type": "string"},
                        "github_url": {"type": "string"},
                        "portfolio_url": {"type": "string"}
                    },
                    "required": ["full_name"]
                },
                "professional_summary": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "years_experience": {"type": "number"},
                        "key_skills": {"type": "array", "items": {"type": "string"}},
                        "career_level": {"type": "string", "enum": ["entry", "mid", "senior", "executive"]}
                    }
                },
                "work_experience": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "position": {"type": "string"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                            "location": {"type": "string"},
                            "description": {"type": "string"},
                            "achievements": {"type": "array", "items": {"type": "string"}},
                            "technologies": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["company", "position"]
                    }
                },
                "education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "institution": {"type": "string"},
                            "degree": {"type": "string"},
                            "field_of_study": {"type": "string"},
                            "graduation_year": {"type": "string"},
                            "gpa": {"type": "string"},
                            "honors": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["institution", "degree"]
                    }
                },
                "skills": {
                    "type": "object",
                    "properties": {
                        "technical_skills": {"type": "array", "items": {"type": "string"}},
                        "programming_languages": {"type": "array", "items": {"type": "string"}},
                        "frameworks": {"type": "array", "items": {"type": "string"}},
                        "tools": {"type": "array", "items": {"type": "string"}},
                        "soft_skills": {"type": "array", "items": {"type": "string"}},
                        "languages": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "certifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "issuer": {"type": "string"},
                            "date": {"type": "string"},
                            "expiry_date": {"type": "string"},
                            "credential_id": {"type": "string"}
                        },
                        "required": ["name", "issuer"]
                    }
                },
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "technologies": {"type": "array", "items": {"type": "string"}},
                            "url": {"type": "string"},
                            "github_url": {"type": "string"}
                        },
                        "required": ["name", "description"]
                    }
                }
            },
            "required": ["personal_information"]
        }
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate parser input data."""
        
        if not isinstance(input_data, dict):
            return {'valid': False, 'errors': ['Input must be a dictionary']}
        
        if 'extracted_text' not in input_data:
            return {'valid': False, 'errors': ['Missing extracted_text field']}
        
        extracted_text = input_data['extracted_text']
        if not isinstance(extracted_text, str) or not extracted_text.strip():
            return {'valid': False, 'errors': ['extracted_text must be a non-empty string']}
        
        if len(extracted_text.strip()) < 50:
            return {'valid': False, 'errors': ['extracted_text too short - minimum 50 characters required']}
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Dict[str, Any]) -> ProcessingResult:
        """Parse resume text using multi-model ensemble with consensus mechanisms."""
        
        extracted_text = input_data['extracted_text']
        processing_options = input_data.get('processing_options', {})
        
        # Initialize processing results
        import time
        results = {
            'extraction_id': f"parse_{int(time.time())}",
            'models_attempted': 0,
            'successful_models': 0,
            'model_results': [],
            'consensus_data': {},
            'final_structured_resume': {},
            'ensemble_confidence': 0.0,
            'disagreement_areas': [],
            'processing_metadata': {}
        }
        
        # Get preferred models from options or use all available
        preferred_models = processing_options.get('models', self.available_models)
        enable_ensemble = processing_options.get('enable_ensemble', True)
        
        # Process with multiple models in parallel
        model_tasks = []
        for model_name in preferred_models:
            if model_name in self.available_models:
                task = self._parse_with_single_model(model_name, extracted_text, processing_options)
                model_tasks.append((model_name, task))
        
        # Wait for all models to complete
        model_results = []
        for model_name, task in model_tasks:
            try:
                results['models_attempted'] += 1
                result = await task
                result.model_name = model_name
                model_results.append(result)
                results['successful_models'] += 1
                
                self.logger.info(f"✅ {model_name} parsing completed with confidence: {result.confidence}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ {model_name} parsing failed: {str(e)}")
                # Create error result
                error_result = ModelResult(
                    model_name=model_name,
                    parsed_data={},
                    confidence=0.0,
                    processing_time=0.0,
                    errors=[str(e)],
                    warnings=[]
                )
                model_results.append(error_result)
        
        if not any(r.confidence > 0 for r in model_results):
            raise Exception("All AI models failed to parse the resume")
        
        results['model_results'] = model_results
        
        # Apply ensemble logic if multiple successful models and ensemble enabled
        if enable_ensemble and sum(1 for r in model_results if r.confidence > 0) >= 2:
            ensemble_result = await self._apply_ensemble_consensus(model_results, extracted_text)
            results['consensus_data'] = ensemble_result['consensus_data']
            results['final_structured_resume'] = ensemble_result['merged_data']
            results['ensemble_confidence'] = ensemble_result['consensus_confidence']
            results['disagreement_areas'] = ensemble_result['disagreements']
            
        else:
            # Use single best model result
            best_model = max([r for r in model_results if r.confidence > 0], key=lambda x: x.confidence)
            results['final_structured_resume'] = best_model.parsed_data
            results['ensemble_confidence'] = best_model.confidence
            results['consensus_data'] = {'single_model_used': best_model.model_name}
        
        # Post-process and validate
        processed_result = await self._post_process_ensemble_result(results, extracted_text)
        
        return ProcessingResult(
            success=True,
            result=processed_result,
            confidence=processed_result['final_confidence'],
            processing_time=0.0,  # Will be set by base class
            metadata={
                'models_attempted': results['models_attempted'],
                'successful_models': results['successful_models'],
                'ensemble_enabled': enable_ensemble,
                'consensus_areas': len(results.get('consensus_data', {})),
                'disagreement_count': len(results.get('disagreement_areas', [])),
                'text_length': len(extracted_text)
            }
        )
    
    async def _parse_with_single_model(self, model: str, text: str, options: Dict[str, Any]) -> ModelResult:
        """Parse resume using a single AI model with comprehensive error handling."""
        
        start_time = time.time()
        
        try:
            if model == 'gpt-4o':
                result_data = await self._parse_with_openai(text, options)
            elif model == 'claude-3.5-sonnet':
                result_data = await self._parse_with_anthropic(text, options)
            elif model == 'gemini-pro':
                result_data = await self._parse_with_gemini(text, options)
            else:
                raise ValueError(f"Unsupported model: {model}")
            
            processing_time = time.time() - start_time
            
            # Calculate confidence score
            confidence = self._calculate_model_confidence(result_data, text)
            
            # Validate and clean data
            cleaned_data = self._validate_and_clean_model_output(result_data)
            
            return ModelResult(
                model_name=model,
                parsed_data=cleaned_data,
                confidence=confidence,
                processing_time=processing_time,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Model {model} failed: {str(e)}")
            
            return ModelResult(
                model_name=model,
                parsed_data={},
                confidence=0.0,
                processing_time=processing_time,
                errors=[str(e)],
                warnings=[]
            )
    
    async def _parse_with_openai(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume using OpenAI GPT-4o with enhanced prompting."""
        
        system_prompt = """You are an expert resume parser specializing in comprehensive information extraction. 
        
        CRITICAL INSTRUCTIONS:
        1. Extract ALL information present in the resume text with maximum accuracy
        2. Follow the provided JSON schema EXACTLY - include all fields even if empty
        3. Normalize dates to YYYY-MM format (use 'present' for current positions)
        4. Separate technical skills into appropriate categories (languages, frameworks, databases, etc.)
        5. Extract soft skills, domain expertise, and methodologies separately
        6. Include location details, work authorization, and remote work preferences if mentioned
        7. Parse education with all available details including GPA, honors, coursework
        8. Extract projects with technologies, roles, and achievements
        9. Include certifications with expiry dates and credential IDs
        10. Return ONLY valid JSON - no additional text or formatting
        
        QUALITY REQUIREMENTS:
        - Ensure schema compliance for all extracted data
        - Maintain data consistency across all sections
        - Extract quantifiable achievements and metrics wherever possible
        - Include industry context and domain expertise"""
        
        user_prompt = f"""Parse this resume text into the comprehensive JSON structure:

        RESUME TEXT:
        {text}
        
        JSON SCHEMA:
        {json.dumps(self.resume_schema, indent=2)}
        
        RESPONSE: Return only the JSON data structure matching the schema above."""
        
        response = await self.openai_client.chat.completions.create(
            model=options.get('openai_model', 'gpt-4o'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.model_configs['gpt-4o']['temperature'],
            max_tokens=self.model_configs['gpt-4o']['max_tokens'],
            top_p=self.model_configs['gpt-4o']['top_p']
        )
        
        response_text = response.choices[0].message.content.strip()
        parsed_data = self._extract_json_from_response(response_text)
        
        return parsed_data
    
    async def _parse_with_anthropic(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume using Anthropic Claude 3.5 Sonnet with enhanced analysis."""
        
        system_prompt = """You are an expert resume parser with deep understanding of professional document structures and career progression patterns.
        
        PARSING OBJECTIVES:
        1. Perform comprehensive extraction of ALL resume information with highest accuracy
        2. Follow the JSON schema precisely - every field matters for downstream processing
        3. Apply intelligent inference for missing data based on context and industry standards
        4. Normalize all dates to YYYY-MM format (use 'present' for ongoing positions)
        5. Categorize technical skills with precision (separate languages, frameworks, databases, cloud platforms)
        6. Extract soft skills and domain expertise with nuanced understanding
        7. Parse education details comprehensively including honors, coursework, thesis information
        8. Identify all projects with complete technology stacks and quantifiable outcomes
        9. Extract certifications with full lifecycle information (issue date, expiry, renewal requirements)
        10. Capture professional context including industry focus, team sizes, reporting structures
        
        QUALITY STANDARDS:
        - Ensure complete schema compliance
        - Maintain internal data consistency
        - Extract quantifiable metrics and achievements
        - Preserve semantic relationships between sections
        - Return ONLY the JSON structure - no additional commentary"""
        
        user_prompt = f"""Analyze and parse this resume text into the comprehensive JSON structure:

        RESUME CONTENT:
        {text}
        
        TARGET JSON SCHEMA:
        {json.dumps(self.resume_schema, indent=2)}
        
        OUTPUT: Provide only the complete JSON data structure matching the schema."""
        
        response = await self.anthropic_client.messages.create(
            model=options.get('claude_model', 'claude-3-5-sonnet-20241022'),
            max_tokens=self.model_configs['claude-3.5-sonnet']['max_tokens'],
            temperature=self.model_configs['claude-3.5-sonnet']['temperature'],
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response_text = response.content[0].text.strip()
        parsed_data = self._extract_json_from_response(response_text)
        
        return parsed_data
    
    async def _parse_with_gemini(self, text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume using Google Gemini Pro with advanced reasoning."""
        
        prompt = f"""You are an expert resume parsing system with advanced natural language understanding capabilities.
        
        MISSION: Transform unstructured resume text into comprehensive structured data with maximum accuracy and completeness.
        
        CORE REQUIREMENTS:
        1. Extract every piece of relevant information from the resume text
        2. Structure data according to the provided JSON schema with complete field coverage
        3. Apply intelligent normalization for dates, locations, and professional titles
        4. Categorize technical skills with industry-standard precision
        5. Extract soft skills and domain expertise with contextual understanding
        6. Parse educational background with comprehensive detail capture
        7. Identify projects with complete technology stacks and measurable outcomes
        8. Extract certifications including full lifecycle and verification details
        9. Capture career progression patterns and professional context
        10. Maintain perfect schema compliance - return only valid JSON
        
        RESUME TEXT TO PARSE:
        {text}
        
        JSON SCHEMA TO FOLLOW:
        {json.dumps(self.resume_schema, indent=2)}
        
        INSTRUCTION: Generate the complete JSON structure following the schema exactly. Include all fields, even if empty. Return only the JSON data."""
        
        response = await self.gemini_model.generate_content_async(
            prompt,
            generation_config={
                'temperature': self.model_configs['gemini-pro']['temperature'],
                'top_p': self.model_configs['gemini-pro']['top_p'],
                'top_k': self.model_configs['gemini-pro']['top_k'],
                'max_output_tokens': 4000
            }
        )
        
        response_text = response.text.strip()
        parsed_data = self._extract_json_from_response(response_text)
        
        return parsed_data
    
    async def _apply_ensemble_consensus(self, model_results: List[ModelResult], original_text: str) -> Dict[str, Any]:
        """Apply ensemble consensus mechanisms to reconcile model disagreements."""
        
        # Filter successful results
        successful_results = [r for r in model_results if r.confidence > 0 and r.parsed_data]
        
        if len(successful_results) < 2:
            # Not enough models for consensus, return best single result
            best_result = max(successful_results, key=lambda x: x.confidence)
            return {
                'merged_data': best_result.parsed_data,
                'consensus_confidence': best_result.confidence,
                'consensus_data': {'single_model_fallback': best_result.model_name},
                'disagreements': []
            }
        
        # Initialize consensus data structures
        consensus_data = {}
        disagreements = []
        field_votes = {}
        
        # Apply weighted voting for each major section
        major_sections = [
            'personal_information', 'professional_summary', 'work_experience',
            'education', 'skills', 'certifications', 'projects', 'publications',
            'awards_honors', 'volunteer_experience', 'additional_information'
        ]
        
        merged_data = {}
        
        for section in major_sections:
            section_results = []
            section_weights = []
            
            for result in successful_results:
                if section in result.parsed_data and result.parsed_data[section]:
                    section_results.append(result.parsed_data[section])
                    # Apply confidence weight based on model performance
                    model_weight = self.confidence_weights.get(result.model_name, 0.8)
                    section_weights.append(result.confidence * model_weight)
                else:
                    section_results.append(None)
                    section_weights.append(0.0)
            
            # Apply consensus logic for this section
            if section == 'personal_information':
                merged_data[section] = await self._merge_personal_information(section_results, section_weights)
            elif section == 'work_experience':
                merged_data[section] = await self._merge_work_experience(section_results, section_weights)
            elif section == 'education':
                merged_data[section] = await self._merge_education(section_results, section_weights)
            elif section == 'skills':
                merged_data[section] = await self._merge_skills(section_results, section_weights)
            elif section in ['certifications', 'projects', 'awards_honors', 'volunteer_experience']:
                merged_data[section] = await self._merge_array_sections(section_results, section_weights)
            else:
                merged_data[section] = await self._merge_object_sections(section_results, section_weights)
            
            # Check for disagreements
            section_disagreement = self._check_section_disagreement(section, section_results, section_weights)
            if section_disagreement:
                disagreements.append(section_disagreement)
        
        # Calculate overall consensus confidence
        total_confidence = 0.0
        confidence_count = 0
        
        for result in successful_results:
            model_weight = self.confidence_weights.get(result.model_name, 0.8)
            total_confidence += result.confidence * model_weight
            confidence_count += model_weight
        
        consensus_confidence = total_confidence / confidence_count if confidence_count > 0 else 0.0
        
        # Apply minimum consensus threshold
        if consensus_confidence < self.consensus_threshold:
            # Consensus too low, use best single model
            best_result = max(successful_results, key=lambda x: x.confidence * self.confidence_weights.get(x.model_name, 0.8))
            return {
                'merged_data': best_result.parsed_data,
                'consensus_confidence': best_result.confidence,
                'consensus_data': {'low_consensus_fallback': best_result.model_name},
                'disagreements': disagreements
            }
        
        return {
            'merged_data': merged_data,
            'consensus_confidence': consensus_confidence,
            'consensus_data': {
                'models_used': [r.model_name for r in successful_results],
                'consensus_method': 'weighted_voting',
                'confidence_weights': {r.model_name: self.confidence_weights.get(r.model_name, 0.8) for r in successful_results}
            },
            'disagreements': disagreements
        }
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON data from AI model response."""
        
        # Try to find JSON in the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response[json_start:json_end]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            fixed_json = self._fix_common_json_issues(json_str)
            return json.loads(fixed_json)
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues."""
        
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unescaped quotes in strings
        json_str = re.sub(r'(?<!\\)"(?=.*")', r'\\"', json_str)
        
        # Remove comments
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str
    
    def _calculate_model_confidence(self, parsed_data: Dict[str, Any], original_text: str) -> float:
        """Calculate comprehensive confidence score for model parsing results."""
        
        confidence_components = {
            'data_completeness': 0.0,
            'schema_compliance': 0.0,
            'data_accuracy': 0.0,
            'internal_consistency': 0.0
        }
        
        # Data completeness scoring (40% of total confidence)
        completeness_score = self._score_data_completeness(parsed_data)
        confidence_components['data_completeness'] = completeness_score * 0.4
        
        # Schema compliance scoring (25% of total confidence)
        compliance_score = self._score_schema_compliance(parsed_data)
        confidence_components['schema_compliance'] = compliance_score * 0.25
        
        # Data accuracy scoring (25% of total confidence)
        accuracy_score = self._score_data_accuracy(parsed_data, original_text)
        confidence_components['data_accuracy'] = accuracy_score * 0.25
        
        # Internal consistency scoring (10% of total confidence)
        consistency_score = self._score_internal_consistency(parsed_data)
        confidence_components['internal_consistency'] = consistency_score * 0.1
        
        total_confidence = sum(confidence_components.values())
        return min(total_confidence, 1.0)
    
    def _score_data_completeness(self, data: Dict[str, Any]) -> float:
        """Score data completeness based on key sections and fields."""
        
        completeness_weights = {
            'personal_information': 0.25,
            'work_experience': 0.30,
            'education': 0.20,
            'skills': 0.15,
            'certifications': 0.05,
            'projects': 0.05
        }
        
        total_score = 0.0
        
        # Personal information completeness
        personal_info = data.get('personal_information', {})
        personal_score = 0.0
        if personal_info.get('full_name'): personal_score += 0.4
        if personal_info.get('email'): personal_score += 0.2
        if personal_info.get('phone'): personal_score += 0.2
        if personal_info.get('location'): personal_score += 0.2
        total_score += personal_score * completeness_weights['personal_information']
        
        # Work experience completeness
        work_exp = data.get('work_experience', [])
        if work_exp:
            exp_score = min(len(work_exp) / 3.0, 1.0)  # Normalize to max 3 positions
            # Bonus for detailed experience entries
            detailed_entries = sum(1 for exp in work_exp if 
                                 exp.get('company_name') and exp.get('position_title') and 
                                 exp.get('start_date') and exp.get('key_responsibilities'))
            if detailed_entries > 0:
                exp_score *= (1.0 + detailed_entries * 0.1)
            total_score += min(exp_score, 1.0) * completeness_weights['work_experience']
        
        # Education completeness
        education = data.get('education', [])
        if education:
            edu_score = min(len(education) / 2.0, 1.0)  # Normalize to max 2 degrees
            total_score += edu_score * completeness_weights['education']
        
        # Skills completeness
        skills = data.get('skills', {})
        if skills:
            skill_categories = ['technical_skills', 'soft_skills', 'languages']
            present_categories = sum(1 for cat in skill_categories if 
                                   skills.get(cat) and len(skills[cat]) > 0)
            skill_score = present_categories / len(skill_categories)
            total_score += skill_score * completeness_weights['skills']
        
        # Other sections
        for section in ['certifications', 'projects']:
            section_data = data.get(section, [])
            if section_data and len(section_data) > 0:
                total_score += completeness_weights[section]
        
        return min(total_score, 1.0)
    
    def _score_schema_compliance(self, data: Dict[str, Any]) -> float:
        """Score how well the data conforms to the expected schema."""
        
        compliance_issues = 0
        total_checks = 0
        
        # Check required fields presence
        if not data.get('personal_information', {}).get('full_name'):
            compliance_issues += 1
        total_checks += 1
        
        # Check data types for key fields
        work_exp = data.get('work_experience', [])
        if isinstance(work_exp, list):
            for exp in work_exp:
                if not isinstance(exp, dict):
                    compliance_issues += 1
                elif not (exp.get('company_name') and exp.get('position_title')):
                    compliance_issues += 1
                total_checks += 1
        else:
            compliance_issues += 1
            total_checks += 1
        
        # Check education data types
        education = data.get('education', [])
        if isinstance(education, list):
            for edu in education:
                if not isinstance(edu, dict):
                    compliance_issues += 1
                elif not (edu.get('institution_name') and edu.get('degree_name')):
                    compliance_issues += 1
                total_checks += 1
        else:
            compliance_issues += 1
            total_checks += 1
        
        if total_checks == 0:
            return 0.0
        
        return 1.0 - (compliance_issues / total_checks)
    
    def _score_data_accuracy(self, data: Dict[str, Any], original_text: str) -> float:
        """Score data accuracy by checking against original text."""
        
        original_lower = original_text.lower()
        accuracy_score = 0.0
        checks = 0
        
        # Check personal information accuracy
        personal_info = data.get('personal_information', {})
        
        # Name accuracy
        full_name = personal_info.get('full_name', '')
        if full_name:
            name_parts = [part.lower() for part in full_name.split() if len(part) > 1]
            found_parts = sum(1 for part in name_parts if part in original_lower)
            if name_parts:
                accuracy_score += (found_parts / len(name_parts)) * 0.3
            checks += 1
        
        # Email accuracy
        email = personal_info.get('email', '')
        if email and email.lower() in original_lower:
            accuracy_score += 0.2
        checks += 1
        
        # Company names accuracy
        work_exp = data.get('work_experience', [])
        if work_exp:
            company_matches = 0
            for exp in work_exp:
                company = exp.get('company_name', '').lower()
                if company and len(company) > 2 and company in original_lower:
                    company_matches += 1
            if work_exp:
                accuracy_score += (company_matches / len(work_exp)) * 0.3
        checks += 1
        
        # Institution names accuracy
        education = data.get('education', [])
        if education:
            institution_matches = 0
            for edu in education:
                institution = edu.get('institution_name', '').lower()
                if institution and len(institution) > 3 and institution in original_lower:
                    institution_matches += 1
            if education:
                accuracy_score += (institution_matches / len(education)) * 0.2
        checks += 1
        
        return accuracy_score if checks > 0 else 0.0
    
    def _score_internal_consistency(self, data: Dict[str, Any]) -> float:
        """Score internal data consistency within the parsed result."""
        
        consistency_score = 1.0
        
        # Check date consistency in work experience
        work_exp = data.get('work_experience', [])
        for exp in work_exp:
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            if start_date and end_date and end_date != 'present':
                try:
                    # Basic date format validation
                    if len(start_date) >= 4 and len(end_date) >= 4:
                        start_year = int(start_date[:4])
                        end_year = int(end_date[:4])
                        if start_year > end_year:
                            consistency_score -= 0.1
                except ValueError:
                    consistency_score -= 0.05
        
        # Check education graduation year consistency
        education = data.get('education', [])
        grad_years = []
        for edu in education:
            grad_year = edu.get('graduation_date', '')
            if grad_year and len(grad_year) >= 4:
                try:
                    year = int(grad_year[:4])
                    grad_years.append(year)
                except ValueError:
                    pass
        
        # Check if graduation years are reasonable
        if len(grad_years) > 1:
            grad_years.sort()
            for i in range(1, len(grad_years)):
                if grad_years[i] - grad_years[i-1] > 10:  # Unusual gap
                    consistency_score -= 0.05
        
        return max(consistency_score, 0.0)
    
    def _validate_and_clean_model_output(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean raw model output for consistency."""
        
        cleaned_data = {}
        
        # Clean and validate each major section
        if 'personal_information' in raw_data:
            cleaned_data['personal_information'] = self._clean_personal_information(raw_data['personal_information'])
        
        if 'work_experience' in raw_data:
            cleaned_data['work_experience'] = self._clean_work_experience(raw_data['work_experience'])
        
        if 'education' in raw_data:
            cleaned_data['education'] = self._clean_education(raw_data['education'])
        
        if 'skills' in raw_data:
            cleaned_data['skills'] = self._clean_skills(raw_data['skills'])
        
        # Copy other sections with basic cleaning
        for section in ['professional_summary', 'certifications', 'projects', 'publications', 
                       'awards_honors', 'volunteer_experience', 'additional_information']:
            if section in raw_data:
                cleaned_data[section] = raw_data[section]
        
        return cleaned_data
    
    async def _post_process_ensemble_result(self, ensemble_results: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Post-process ensemble parsing results with comprehensive validation."""
        
        final_resume = ensemble_results['final_structured_resume']
        ensemble_confidence = ensemble_results['ensemble_confidence']
        
        # Apply final data cleaning and normalization
        cleaned_data = self._apply_final_data_cleaning(final_resume)
        
        # Generate comprehensive metadata and quality metrics
        result = {
            'structured_resume': cleaned_data,
            'final_confidence': ensemble_confidence,
            'parsing_metadata': {
                'extraction_id': ensemble_results['extraction_id'],
                'models_attempted': ensemble_results['models_attempted'],
                'successful_models': ensemble_results['successful_models'],
                'ensemble_method_used': ensemble_results.get('consensus_data', {}).get('consensus_method'),
                'original_text_length': len(original_text),
                'sections_extracted': list(cleaned_data.keys()),
                'parsing_timestamp': datetime.utcnow().isoformat(),
                'schema_version': '2.0'
            },
            'quality_metrics': {
                'data_completeness': self._calculate_completeness_score(cleaned_data),
                'data_consistency': self._calculate_consistency_score(cleaned_data),
                'accuracy_indicators': self._get_accuracy_indicators(cleaned_data, original_text),
                'consensus_quality': {
                    'disagreement_count': len(ensemble_results.get('disagreement_areas', [])),
                    'consensus_confidence': ensemble_confidence,
                    'model_agreement_rate': self._calculate_model_agreement_rate(ensemble_results)
                }
            },
            'model_performance': {
                'individual_results': [{
                    'model': result.model_name,
                    'confidence': result.confidence,
                    'processing_time': result.processing_time,
                    'errors': result.errors,
                    'warnings': result.warnings
                } for result in ensemble_results['model_results']],
                'ensemble_summary': ensemble_results.get('consensus_data', {})
            },
            'disagreement_analysis': ensemble_results.get('disagreement_areas', [])
        }
        
        return result
    
    # Ensemble Consensus Methods
    async def _merge_personal_information(self, section_results: List, weights: List[float]) -> Dict[str, Any]:
        """Merge personal information using weighted consensus."""
        
        merged_info = {}
        valid_results = [(result, weight) for result, weight in zip(section_results, weights) if result and weight > 0]
        
        if not valid_results:
            return {}
        
        # Merge basic fields with highest confidence
        basic_fields = ['full_name', 'first_name', 'last_name', 'email', 'phone', 'preferred_name']
        
        for field in basic_fields:
            field_values = [(result.get(field), weight) for result, weight in valid_results if result.get(field)]
            if field_values:
                # Use highest weighted value
                best_value = max(field_values, key=lambda x: x[1])[0]
                merged_info[field] = best_value
        
        # Merge location with intelligent consensus
        location_data = [result.get('location', {}) for result, _ in valid_results if result.get('location')]
        if location_data:
            merged_info['location'] = self._merge_location_data(location_data, weights)
        
        # Merge social profiles by combining all unique URLs
        social_profiles = {}
        for result, weight in valid_results:
            profiles = result.get('social_profiles', {})
            for platform, url in profiles.items():
                if url and (platform not in social_profiles or weight > weights[0]):
                    social_profiles[platform] = url
        
        if social_profiles:
            merged_info['social_profiles'] = social_profiles
        
        # Merge other fields with preference for completeness
        other_fields = ['alternative_emails', 'alternative_phones', 'nationality', 'work_authorization']
        for field in other_fields:
            values = [result.get(field) for result, _ in valid_results if result.get(field)]
            if values:
                # Prefer most complete/detailed value
                if isinstance(values[0], list):
                    merged_info[field] = list(set([item for sublist in values for item in sublist]))
                else:
                    merged_info[field] = max(values, key=len)
        
        return merged_info
    
    async def _merge_work_experience(self, section_results: List, weights: List[float]) -> List[Dict[str, Any]]:
        """Merge work experience using intelligent matching and consensus."""
        
        valid_results = [(result, weight) for result, weight in zip(section_results, weights) if result and weight > 0]
        
        if not valid_results:
            return []
        
        # Collect all unique positions by company and title
        all_positions = []
        position_signatures = set()
        
        for experiences, weight in valid_results:
            if isinstance(experiences, list):
                for exp in experiences:
                    if isinstance(exp, dict):
                        company = exp.get('company_name', '').lower().strip()
                        position = exp.get('position_title', '').lower().strip()
                        start_date = exp.get('start_date', '').strip()
                        
                        # Create signature for deduplication
                        signature = f"{company}|{position}|{start_date}"
                        
                        if signature not in position_signatures and company and position:
                            position_signatures.add(signature)
                            all_positions.append((exp, weight))
        
        # Sort by start date (most recent first)
        def extract_year(date_str):
            if not date_str:
                return 0
            try:
                return int(date_str[:4]) if len(date_str) >= 4 else 0
            except (ValueError, IndexError):
                return 0
        
        all_positions.sort(key=lambda x: extract_year(x[0].get('start_date', '')), reverse=True)
        
        # Return deduplicated and sorted positions
        return [pos[0] for pos in all_positions]
    
    async def _merge_education(self, section_results: List, weights: List[float]) -> List[Dict[str, Any]]:
        """Merge education using intelligent matching and consensus."""
        
        valid_results = [(result, weight) for result, weight in zip(section_results, weights) if result and weight > 0]
        
        if not valid_results:
            return []
        
        # Collect all unique education entries
        all_education = []
        education_signatures = set()
        
        for education_list, weight in valid_results:
            if isinstance(education_list, list):
                for edu in education_list:
                    if isinstance(edu, dict):
                        institution = edu.get('institution_name', '').lower().strip()
                        degree = edu.get('degree_name', '').lower().strip()
                        field = edu.get('field_of_study', '').lower().strip()
                        
                        # Create signature for deduplication
                        signature = f"{institution}|{degree}|{field}"
                        
                        if signature not in education_signatures and institution and degree:
                            education_signatures.add(signature)
                            all_education.append((edu, weight))
        
        # Sort by graduation date (most recent first)
        def extract_graduation_year(edu_entry):
            grad_date = edu_entry.get('graduation_date', '')
            if not grad_date:
                return 0
            try:
                return int(grad_date[:4]) if len(grad_date) >= 4 else 0
            except (ValueError, IndexError):
                return 0
        
        all_education.sort(key=lambda x: extract_graduation_year(x[0]), reverse=True)
        
        return [edu[0] for edu in all_education]
    
    async def _merge_skills(self, section_results: List, weights: List[float]) -> Dict[str, Any]:
        """Merge skills using comprehensive deduplication and categorization."""
        
        valid_results = [(result, weight) for result, weight in zip(section_results, weights) if result and weight > 0]
        
        if not valid_results:
            return {}
        
        merged_skills = {
            'technical_skills': {},
            'soft_skills': [],
            'languages': [],
            'domain_expertise': []
        }
        
        # Merge technical skills
        technical_categories = [
            'programming_languages', 'frameworks_libraries', 'databases', 'cloud_platforms',
            'devops_tools', 'development_tools', 'operating_systems', 'web_technologies',
            'mobile_technologies', 'data_science_ml', 'testing_tools', 'version_control', 'methodologies'
        ]
        
        merged_technical = {}
        
        for category in technical_categories:
            all_items = set()
            for skills_data, weight in valid_results:
                if isinstance(skills_data, dict):
                    technical_skills = skills_data.get('technical_skills', {})
                    if isinstance(technical_skills, dict):
                        items = technical_skills.get(category, [])
                        if isinstance(items, list):
                            all_items.update([item.strip() for item in items if item.strip()])
            
            if all_items:
                merged_technical[category] = sorted(list(all_items))
        
        merged_skills['technical_skills'] = merged_technical
        
        # Merge other skill categories
        for skill_type in ['soft_skills', 'domain_expertise']:
            all_skills = set()
            for skills_data, weight in valid_results:
                if isinstance(skills_data, dict):
                    skills = skills_data.get(skill_type, [])
                    if isinstance(skills, list):
                        all_skills.update([skill.strip() for skill in skills if skill.strip()])
            
            merged_skills[skill_type] = sorted(list(all_skills))
        
        # Merge languages with proficiency levels
        language_dict = {}
        for skills_data, weight in valid_results:
            if isinstance(skills_data, dict):
                languages = skills_data.get('languages', [])
                if isinstance(languages, list):
                    for lang in languages:
                        if isinstance(lang, dict):
                            lang_name = lang.get('language', '').strip()
                            proficiency = lang.get('proficiency', '')
                            if lang_name:
                                if lang_name not in language_dict or proficiency:
                                    language_dict[lang_name] = lang
                        elif isinstance(lang, str) and lang.strip():
                            lang_name = lang.strip()
                            if lang_name not in language_dict:
                                language_dict[lang_name] = {'language': lang_name, 'proficiency': 'intermediate'}
        
        merged_skills['languages'] = list(language_dict.values())
        
        return merged_skills
    
    async def _merge_array_sections(self, section_results: List, weights: List[float]) -> List[Dict[str, Any]]:
        """Generic merger for array-based sections like certifications, projects, etc."""
        
        valid_results = [(result, weight) for result, weight in zip(section_results, weights) if result and weight > 0]
        
        if not valid_results:
            return []
        
        # Combine all items from all models
        all_items = []
        seen_signatures = set()
        
        for items_list, weight in valid_results:
            if isinstance(items_list, list):
                for item in items_list:
                    if isinstance(item, dict):
                        # Create a signature based on key identifying fields
                        name = item.get('name') or item.get('certification_name') or item.get('project_name') or item.get('award_name') or item.get('title') or ''
                        org = item.get('issuer') or item.get('issuing_organization') or item.get('organization') or item.get('publication_venue') or ''
                        
                        signature = f"{name.lower().strip()}|{org.lower().strip()}"
                        
                        if signature not in seen_signatures and name:
                            seen_signatures.add(signature)
                            all_items.append(item)
        
        return all_items
    
    async def _merge_object_sections(self, section_results: List, weights: List[float]) -> Dict[str, Any]:
        """Generic merger for object-based sections like professional_summary, additional_information."""
        
        valid_results = [(result, weight) for result, weight in zip(section_results, weights) if result and weight > 0]
        
        if not valid_results:
            return {}
        
        # Use highest weighted result as base, then merge in additional fields
        best_result, _ = max(valid_results, key=lambda x: x[1])
        merged_object = dict(best_result) if isinstance(best_result, dict) else {}
        
        # Merge in additional fields from other results
        for result, weight in valid_results:
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in merged_object or not merged_object[key]:
                        merged_object[key] = value
                    elif isinstance(value, list) and isinstance(merged_object[key], list):
                        # Combine lists and deduplicate
                        combined = list(set(merged_object[key] + value))
                        merged_object[key] = combined
        
        return merged_object
    
    def _merge_location_data(self, location_list: List[Dict], weights: List[float]) -> Dict[str, Any]:
        """Merge location data with intelligent field consolidation."""
        
        merged_location = {}
        
        # Priority order for location fields
        location_fields = ['full_address', 'city', 'state', 'country', 'postal_code']
        
        for field in location_fields:
            values = [loc.get(field) for loc in location_list if loc.get(field)]
            if values:
                # Use the most complete/longest value
                merged_location[field] = max(values, key=len)
        
        return merged_location
    
    def _check_section_disagreement(self, section_name: str, results: List, weights: List[float]) -> Optional[Dict[str, Any]]:
        """Check for significant disagreements between models in a section."""
        
        valid_results = [(result, weight) for result, weight in zip(results, weights) if result and weight > 0]
        
        if len(valid_results) < 2:
            return None
        
        disagreement = {
            'section': section_name,
            'disagreement_type': None,
            'confidence_spread': 0.0,
            'model_variations': [],
            'resolution_method': None
        }
        
        # Analyze disagreement patterns
        if section_name == 'personal_information':
            # Check for name variations
            names = [result.get('full_name', '') for result, _ in valid_results if result.get('full_name')]
            if len(set(names)) > 1:
                disagreement['disagreement_type'] = 'name_variation'
                disagreement['model_variations'] = names
        
        elif section_name == 'work_experience':
            # Check for different numbers of positions
            position_counts = [len(result) if isinstance(result, list) else 0 for result, _ in valid_results]
            if max(position_counts) - min(position_counts) > 1:
                disagreement['disagreement_type'] = 'position_count_mismatch'
                disagreement['model_variations'] = position_counts
        
        # Calculate confidence spread
        confidences = [weight for _, weight in valid_results]
        if confidences:
            disagreement['confidence_spread'] = max(confidences) - min(confidences)
        
        # Only return if significant disagreement found
        if disagreement['disagreement_type'] or disagreement['confidence_spread'] > 0.3:
            disagreement['resolution_method'] = 'weighted_voting'
            return disagreement
        
        return None
    
    def _calculate_model_agreement_rate(self, ensemble_results: Dict[str, Any]) -> float:
        """Calculate the agreement rate between models."""
        
        model_results = ensemble_results.get('model_results', [])
        successful_models = [r for r in model_results if r.confidence > 0]
        
        if len(successful_models) < 2:
            return 1.0
        
        disagreements = len(ensemble_results.get('disagreement_areas', []))
        total_sections = len(ensemble_results.get('final_structured_resume', {}))
        
        if total_sections == 0:
            return 0.0
        
        agreement_rate = 1.0 - (disagreements / total_sections)
        return max(agreement_rate, 0.0)
    
    # Enhanced Data Cleaning Methods
    def _clean_personal_information(self, personal_info: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate personal information with comprehensive normalization."""
        
        if not isinstance(personal_info, dict):
            return {}
        
        cleaned = {}
        
        # Clean name fields
        for name_field in ['full_name', 'first_name', 'last_name', 'preferred_name']:
            value = personal_info.get(name_field, '')
            if isinstance(value, str) and value.strip():
                cleaned[name_field] = ' '.join(value.strip().split())
        
        # Clean contact information
        email = personal_info.get('email', '')
        if isinstance(email, str) and '@' in email:
            cleaned['email'] = email.strip().lower()
        
        # Clean phone number
        phone = personal_info.get('phone', '')
        if isinstance(phone, str) and phone.strip():
            # Remove non-digit characters except +
            cleaned_phone = re.sub(r'[^\d+]', '', phone.strip())
            if len(cleaned_phone) >= 7:  # Minimum phone length
                cleaned['phone'] = cleaned_phone
        
        # Clean location
        location = personal_info.get('location', {})
        if isinstance(location, dict):
            cleaned_location = {}
            for loc_field in ['full_address', 'city', 'state', 'country', 'postal_code']:
                value = location.get(loc_field, '')
                if isinstance(value, str) and value.strip():
                    cleaned_location[loc_field] = value.strip()
            if cleaned_location:
                cleaned['location'] = cleaned_location
        
        # Clean social profiles
        social_profiles = personal_info.get('social_profiles', {})
        if isinstance(social_profiles, dict):
            cleaned_social = {}
            for platform, url in social_profiles.items():
                if isinstance(url, str) and url.strip():
                    clean_url = url.strip()
                    if clean_url.startswith(('http://', 'https://')):
                        cleaned_social[platform] = clean_url
                    elif clean_url.startswith('www.'):
                        cleaned_social[platform] = f"https://{clean_url}"
            if cleaned_social:
                cleaned['social_profiles'] = cleaned_social
        
        # Copy other fields with basic cleaning
        for field in ['alternative_emails', 'alternative_phones', 'nationality', 'work_authorization']:
            value = personal_info.get(field)
            if value:
                if isinstance(value, list):
                    cleaned_list = [item.strip() for item in value if isinstance(item, str) and item.strip()]
                    if cleaned_list:
                        cleaned[field] = cleaned_list
                elif isinstance(value, str) and value.strip():
                    cleaned[field] = value.strip()
        
        return cleaned
    
    def _clean_work_experience(self, work_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate work experience with enhanced normalization."""
        
        if not isinstance(work_experience, list):
            return []
        
        cleaned_experiences = []
        
        for exp in work_experience:
            if not isinstance(exp, dict) or not exp.get('company_name') or not exp.get('position_title'):
                continue
            
            cleaned_exp = {
                'company_name': exp['company_name'].strip(),
                'position_title': exp['position_title'].strip()
            }
            
            # Clean dates
            for date_field in ['start_date', 'end_date']:
                date_value = exp.get(date_field, '')
                if isinstance(date_value, str) and date_value.strip():
                    cleaned_exp[date_field] = self._normalize_date(date_value)
            
            # Clean location
            location = exp.get('location')
            if isinstance(location, dict):
                cleaned_location = {}
                for loc_field in ['city', 'state', 'country']:
                    value = location.get(loc_field, '')
                    if isinstance(value, str) and value.strip():
                        cleaned_location[loc_field] = value.strip()
                if location.get('remote') is not None:
                    cleaned_location['remote'] = bool(location['remote'])
                if cleaned_location:
                    cleaned_exp['location'] = cleaned_location
            elif isinstance(location, str) and location.strip():
                cleaned_exp['location'] = {'city': location.strip()}
            
            # Clean text fields
            for text_field in ['job_description', 'employment_type', 'duration', 'team_size', 'reporting_structure', 'promoted_from', 'reason_for_leaving']:
                value = exp.get(text_field, '')
                if isinstance(value, str) and value.strip():
                    cleaned_exp[text_field] = value.strip()
            
            # Clean array fields
            for array_field in ['key_responsibilities', 'achievements', 'technologies_used']:
                value = exp.get(array_field, [])
                if isinstance(value, list):
                    cleaned_array = [item.strip() for item in value if isinstance(item, str) and item.strip()]
                    if cleaned_array:
                        cleaned_exp[array_field] = cleaned_array
            
            # Clean industry and company info
            for field in ['company_industry', 'company_size']:
                value = exp.get(field, '')
                if isinstance(value, str) and value.strip():
                    cleaned_exp[field] = value.strip()
            
            cleaned_experiences.append(cleaned_exp)
        
        return cleaned_experiences
    
    def _clean_education(self, education: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate education with comprehensive field normalization."""
        
        if not isinstance(education, list):
            return []
        
        cleaned_education = []
        
        for edu in education:
            if not isinstance(edu, dict) or not edu.get('institution_name') or not edu.get('degree_name'):
                continue
            
            cleaned_edu = {
                'institution_name': edu['institution_name'].strip(),
                'degree_name': edu['degree_name'].strip()
            }
            
            # Clean basic fields
            for field in ['field_of_study', 'minor', 'concentration', 'gpa', 'gpa_scale', 'thesis_dissertation', 'advisor', 'accreditation']:
                value = edu.get(field, '')
                if isinstance(value, str) and value.strip():
                    cleaned_edu[field] = value.strip()
            
            # Clean dates
            for date_field in ['graduation_date', 'expected_graduation']:
                date_value = edu.get(date_field, '')
                if isinstance(date_value, str) and date_value.strip():
                    cleaned_edu[date_field] = self._normalize_year(date_value)
            
            # Clean enum fields
            if edu.get('institution_type') in ['university', 'college', 'community_college', 'vocational', 'online', 'bootcamp']:
                cleaned_edu['institution_type'] = edu['institution_type']
            
            if edu.get('degree_type') in ['bachelor', 'master', 'doctorate', 'associate', 'certificate', 'diploma', 'professional']:
                cleaned_edu['degree_type'] = edu['degree_type']
            
            # Clean arrays
            for array_field in ['honors_awards', 'relevant_coursework']:
                value = edu.get(array_field, [])
                if isinstance(value, list):
                    cleaned_array = [item.strip() for item in value if isinstance(item, str) and item.strip()]
                    if cleaned_array:
                        cleaned_edu[array_field] = cleaned_array
            
            # Clean location
            location = edu.get('location', {})
            if isinstance(location, dict):
                cleaned_location = {}
                for loc_field in ['city', 'state', 'country']:
                    value = location.get(loc_field, '')
                    if isinstance(value, str) and value.strip():
                        cleaned_location[loc_field] = value.strip()
                if cleaned_location:
                    cleaned_edu['location'] = cleaned_location
            
            cleaned_education.append(cleaned_edu)
        
        return cleaned_education
    
    def _clean_skills(self, skills: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and organize skills with comprehensive categorization."""
        
        if not isinstance(skills, dict):
            return {}
        
        cleaned_skills = {}
        
        # Clean technical skills
        technical_skills = skills.get('technical_skills', {})
        if isinstance(technical_skills, dict):
            cleaned_technical = {}
            
            technical_categories = [
                'programming_languages', 'frameworks_libraries', 'databases', 'cloud_platforms',
                'devops_tools', 'development_tools', 'operating_systems', 'web_technologies',
                'mobile_technologies', 'data_science_ml', 'testing_tools', 'version_control', 'methodologies'
            ]
            
            for category in technical_categories:
                skills_list = technical_skills.get(category, [])
                if isinstance(skills_list, list):
                    cleaned_list = [skill.strip() for skill in skills_list if isinstance(skill, str) and skill.strip()]
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_skills = []
                    for skill in cleaned_list:
                        if skill.lower() not in seen:
                            seen.add(skill.lower())
                            unique_skills.append(skill)
                    
                    if unique_skills:
                        cleaned_technical[category] = unique_skills
            
            if cleaned_technical:
                cleaned_skills['technical_skills'] = cleaned_technical
        
        # Clean other skill arrays
        for skill_category in ['soft_skills', 'domain_expertise']:
            skills_list = skills.get(skill_category, [])
            if isinstance(skills_list, list):
                cleaned_list = [skill.strip() for skill in skills_list if isinstance(skill, str) and skill.strip()]
                # Remove duplicates
                unique_skills = list(dict.fromkeys(cleaned_list))
                if unique_skills:
                    cleaned_skills[skill_category] = unique_skills
        
        # Clean languages
        languages = skills.get('languages', [])
        if isinstance(languages, list):
            cleaned_languages = []
            for lang in languages:
                if isinstance(lang, dict):
                    lang_name = lang.get('language', '').strip()
                    proficiency = lang.get('proficiency', '').strip()
                    if lang_name:
                        cleaned_lang = {'language': lang_name}
                        if proficiency in ['native', 'fluent', 'advanced', 'intermediate', 'basic']:
                            cleaned_lang['proficiency'] = proficiency
                        else:
                            cleaned_lang['proficiency'] = 'intermediate'  # Default
                        
                        certifications = lang.get('certifications', [])
                        if isinstance(certifications, list):
                            clean_certs = [cert.strip() for cert in certifications if isinstance(cert, str) and cert.strip()]
                            if clean_certs:
                                cleaned_lang['certifications'] = clean_certs
                        
                        cleaned_languages.append(cleaned_lang)
                elif isinstance(lang, str) and lang.strip():
                    cleaned_languages.append({
                        'language': lang.strip(),
                        'proficiency': 'intermediate'
                    })
            
            if cleaned_languages:
                cleaned_skills['languages'] = cleaned_languages
        
        return cleaned_skills
    
    def _apply_final_data_cleaning(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply final comprehensive data cleaning and validation."""
        
        cleaned_data = {}
        
        # Clean each major section
        if 'personal_information' in resume_data:
            cleaned_data['personal_information'] = self._clean_personal_information(resume_data['personal_information'])
        
        if 'work_experience' in resume_data:
            cleaned_data['work_experience'] = self._clean_work_experience(resume_data['work_experience'])
        
        if 'education' in resume_data:
            cleaned_data['education'] = self._clean_education(resume_data['education'])
        
        if 'skills' in resume_data:
            cleaned_data['skills'] = self._clean_skills(resume_data['skills'])
        
        # Clean other sections with basic validation
        for section in ['professional_summary', 'certifications', 'projects', 'publications', 'awards_honors', 'volunteer_experience', 'additional_information']:
            if section in resume_data and resume_data[section]:
                cleaned_data[section] = resume_data[section]
        
        return cleaned_data
    
    def _legacy_clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize parsed data."""
        
        cleaned = {}
        
        # Clean personal information
        if 'personal_information' in data:
            personal = data['personal_information']
            cleaned['personal_information'] = {
                'full_name': self._clean_name(personal.get('full_name', '')),
                'email': self._clean_email(personal.get('email', '')),
                'phone': self._clean_phone(personal.get('phone', '')),
                'location': personal.get('location', {}),
                'linkedin_url': self._clean_url(personal.get('linkedin_url', '')),
                'github_url': self._clean_url(personal.get('github_url', '')),
                'portfolio_url': self._clean_url(personal.get('portfolio_url', ''))
            }
        
        # Clean work experience
        if 'work_experience' in data and isinstance(data['work_experience'], list):
            cleaned['work_experience'] = []
            for exp in data['work_experience']:
                if isinstance(exp, dict) and exp.get('company') and exp.get('position'):
                    cleaned_exp = {
                        'company': exp['company'].strip(),
                        'position': exp['position'].strip(),
                        'start_date': self._normalize_date(exp.get('start_date', '')),
                        'end_date': self._normalize_date(exp.get('end_date', '')),
                        'location': exp.get('location', '').strip(),
                        'description': exp.get('description', '').strip(),
                        'achievements': [a.strip() for a in exp.get('achievements', []) if a.strip()],
                        'technologies': [t.strip() for t in exp.get('technologies', []) if t.strip()]
                    }
                    cleaned['work_experience'].append(cleaned_exp)
        
        # Clean education
        if 'education' in data and isinstance(data['education'], list):
            cleaned['education'] = []
            for edu in data['education']:
                if isinstance(edu, dict) and edu.get('institution') and edu.get('degree'):
                    cleaned_edu = {
                        'institution': edu['institution'].strip(),
                        'degree': edu['degree'].strip(),
                        'field_of_study': edu.get('field_of_study', '').strip(),
                        'graduation_year': self._normalize_year(edu.get('graduation_year', '')),
                        'gpa': edu.get('gpa', '').strip(),
                        'honors': [h.strip() for h in edu.get('honors', []) if h.strip()]
                    }
                    cleaned['education'].append(cleaned_edu)
        
        # Clean skills
        if 'skills' in data:
            skills = data['skills']
            cleaned['skills'] = {
                'technical_skills': [s.strip() for s in skills.get('technical_skills', []) if s.strip()],
                'programming_languages': [s.strip() for s in skills.get('programming_languages', []) if s.strip()],
                'frameworks': [s.strip() for s in skills.get('frameworks', []) if s.strip()],
                'tools': [s.strip() for s in skills.get('tools', []) if s.strip()],
                'soft_skills': [s.strip() for s in skills.get('soft_skills', []) if s.strip()],
                'languages': [s.strip() for s in skills.get('languages', []) if s.strip()]
            }
        
        # Copy other sections as-is with basic cleaning
        for key in ['professional_summary', 'certifications', 'projects']:
            if key in data:
                cleaned[key] = data[key]
        
        return cleaned
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize name."""
        if not name:
            return ""
        return ' '.join(name.strip().split())
    
    def _clean_email(self, email: str) -> str:
        """Clean and validate email."""
        if not email:
            return ""
        email = email.strip().lower()
        if '@' in email and '.' in email:
            return email
        return ""
    
    def _clean_phone(self, phone: str) -> str:
        """Clean and normalize phone number."""
        if not phone:
            return ""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        return cleaned if cleaned else ""
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL."""
        if not url:
            return ""
        url = url.strip()
        if url.startswith(('http://', 'https://')):
            return url
        elif url.startswith('www.'):
            return f"https://{url}"
        return ""
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format to YYYY-MM."""
        if not date_str:
            return ""
        
        # Handle common formats
        date_str = date_str.strip().lower()
        
        if date_str in ['present', 'current', 'now']:
            return 'present'
        
        # Try to extract year and month
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = year_match.group(1)
            month_match = re.search(r'(\d{1,2})', date_str)
            if month_match:
                month = month_match.group(1).zfill(2)
                return f"{year}-{month}"
            return year
        
        return date_str
    
    def _normalize_year(self, year_str: str) -> str:
        """Normalize year format to YYYY."""
        if not year_str:
            return ""
        
        year_match = re.search(r'(\d{4})', str(year_str))
        if year_match:
            return year_match.group(1)
        
        return str(year_str).strip()
    
    def _calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """Calculate completeness score for parsed data."""
        
        required_sections = ['personal_information', 'work_experience', 'education', 'skills']
        present_sections = sum(1 for section in required_sections if section in data and data[section])
        
        return present_sections / len(required_sections)
    
    def _calculate_consistency_score(self, data: Dict[str, Any]) -> float:
        """Calculate consistency score for parsed data."""
        
        # This is a simplified consistency check
        # In practice, this would be more sophisticated
        
        consistency_checks = []
        
        # Check if name is present in personal info
        personal_info = data.get('personal_information', {})
        if personal_info.get('full_name'):
            consistency_checks.append(True)
        else:
            consistency_checks.append(False)
        
        # Check if work experience has reasonable date ranges
        work_exp = data.get('work_experience', [])
        for exp in work_exp:
            if exp.get('start_date') and exp.get('company') and exp.get('position'):
                consistency_checks.append(True)
            else:
                consistency_checks.append(False)
        
        return sum(consistency_checks) / len(consistency_checks) if consistency_checks else 0.5
    
    def _get_accuracy_indicators(self, data: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Get accuracy indicators for parsed data."""
        
        indicators = {
            'name_found_in_text': False,
            'email_found_in_text': False,
            'phone_found_in_text': False,
            'companies_mentioned_count': 0
        }
        
        original_lower = original_text.lower()
        
        # Check if personal info is found in original text
        personal_info = data.get('personal_information', {})
        
        if personal_info.get('full_name'):
            name_parts = personal_info['full_name'].lower().split()
            if all(part in original_lower for part in name_parts):
                indicators['name_found_in_text'] = True
        
        if personal_info.get('email') and personal_info['email'].lower() in original_lower:
            indicators['email_found_in_text'] = True
        
        # Count companies mentioned
        work_exp = data.get('work_experience', [])
        for exp in work_exp:
            company = exp.get('company', '').lower()
            if company and company in original_lower:
                indicators['companies_mentioned_count'] += 1
        
        return indicators