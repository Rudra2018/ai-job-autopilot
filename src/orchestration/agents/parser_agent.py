"""
Parser Agent Implementation
Handles parsing of resume text into structured JSON format using multiple AI models.
"""

import asyncio
import json
import os
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
import openai
import anthropic
from .base_agent import BaseAgent, ProcessingResult

class ParserAgent(BaseAgent):
    """
    Parser Agent responsible for parsing resume content into structured JSON format.
    Uses multiple AI models for robust parsing with high accuracy.
    """
    
    def _setup_agent_specific_config(self):
        """Setup Parser-specific configurations."""
        
        self.ai_models = []
        
        # Initialize OpenAI
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
            self.ai_models.append('gpt-4o')
        
        # Initialize Anthropic
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            self.ai_models.append('claude-3.5-sonnet')
        
        if not self.ai_models:
            raise RuntimeError("No AI models available. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        
        self.logger.info(f"Available AI models: {self.ai_models}")
        
        # Define structured output schema
        self.resume_schema = self._get_resume_schema()
    
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
        """Parse resume text into structured format."""
        
        extracted_text = input_data['extracted_text']
        parsing_config = input_data.get('parsing_config', {})
        
        # Try parsing with multiple AI models
        preferred_models = parsing_config.get('ai_models', self.ai_models)
        
        parsing_results = []
        
        for model in preferred_models:
            if model not in self.ai_models:
                continue
            
            try:
                result = await self._parse_with_model(model, extracted_text, parsing_config)
                parsing_results.append(result)
                
                # If we get a high-confidence result, use it
                if result['confidence'] >= 0.9:
                    break
                    
            except Exception as e:
                self.logger.warning(f"Parsing with {model} failed: {str(e)}")
                continue
        
        if not parsing_results:
            raise Exception("All AI models failed to parse the resume")
        
        # Select best result
        best_result = max(parsing_results, key=lambda x: x['confidence'])
        
        # Post-process and validate the result
        final_result = await self._post_process_parsed_result(best_result, extracted_text)
        
        return ProcessingResult(
            success=True,
            result=final_result,
            confidence=final_result['confidence'],
            processing_time=0.0,  # Will be set by base class
            metadata={
                'models_tried': [r['model'] for r in parsing_results],
                'best_model': best_result['model'],
                'sections_parsed': len(final_result['structured_resume']),
                'text_length': len(extracted_text)
            }
        )
    
    async def _parse_with_model(self, model: str, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume using a specific AI model."""
        
        if model == 'gpt-4o':
            return await self._parse_with_openai(text, config)
        elif model == 'claude-3.5-sonnet':
            return await self._parse_with_anthropic(text, config)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    async def _parse_with_openai(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume using OpenAI GPT-4o."""
        
        system_prompt = """You are an expert resume parser. Extract information from the provided resume text and structure it according to the given JSON schema. 

        Instructions:
        1. Extract all relevant information accurately
        2. Maintain original formatting where appropriate
        3. Infer missing information when reasonable
        4. Use consistent date formats (YYYY-MM)
        5. Separate technical skills from soft skills
        6. Include confidence scores for each section
        
        Return only valid JSON that matches the schema."""
        
        user_prompt = f"""Parse the following resume text into structured JSON:

        Resume Text:
        {text}
        
        Schema:
        {json.dumps(self.resume_schema, indent=2)}
        
        Return the parsed data as JSON."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            parsed_data = self._extract_json_from_response(response_text)
            
            # Calculate confidence based on completeness
            confidence = self._calculate_parsing_confidence(parsed_data, text)
            
            return {
                'model': 'gpt-4o',
                'parsed_data': parsed_data,
                'confidence': confidence,
                'raw_response': response_text
            }
            
        except Exception as e:
            raise Exception(f"OpenAI parsing failed: {str(e)}")
    
    async def _parse_with_anthropic(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse resume using Anthropic Claude."""
        
        system_prompt = """You are an expert resume parser. Extract information from the provided resume text and structure it according to the given JSON schema. 

        Instructions:
        1. Extract all relevant information accurately
        2. Maintain original formatting where appropriate  
        3. Infer missing information when reasonable
        4. Use consistent date formats (YYYY-MM)
        5. Separate technical skills from soft skills
        6. Include confidence scores for each section
        
        Return only valid JSON that matches the schema."""
        
        user_prompt = f"""Parse the following resume text into structured JSON:

        Resume Text:
        {text}
        
        Schema:
        {json.dumps(self.resume_schema, indent=2)}
        
        Return the parsed data as JSON."""
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            parsed_data = self._extract_json_from_response(response_text)
            
            # Calculate confidence based on completeness
            confidence = self._calculate_parsing_confidence(parsed_data, text)
            
            return {
                'model': 'claude-3.5-sonnet',
                'parsed_data': parsed_data,
                'confidence': confidence,
                'raw_response': response_text
            }
            
        except Exception as e:
            raise Exception(f"Anthropic parsing failed: {str(e)}")
    
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
    
    def _calculate_parsing_confidence(self, parsed_data: Dict[str, Any], original_text: str) -> float:
        """Calculate confidence score for parsed data."""
        
        confidence_factors = []
        
        # Check personal information completeness
        personal_info = parsed_data.get('personal_information', {})
        if personal_info.get('full_name'):
            confidence_factors.append(0.2)
        if personal_info.get('email'):
            confidence_factors.append(0.1)
        if personal_info.get('phone'):
            confidence_factors.append(0.1)
        
        # Check work experience
        work_exp = parsed_data.get('work_experience', [])
        if work_exp:
            confidence_factors.append(0.3)
            if len(work_exp) >= 2:
                confidence_factors.append(0.1)
        
        # Check education
        education = parsed_data.get('education', [])
        if education:
            confidence_factors.append(0.2)
        
        # Check skills
        skills = parsed_data.get('skills', {})
        if skills.get('technical_skills') or skills.get('programming_languages'):
            confidence_factors.append(0.1)
        
        return min(sum(confidence_factors), 1.0)
    
    async def _post_process_parsed_result(self, parsing_result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Post-process parsed result for quality and consistency."""
        
        parsed_data = parsing_result['parsed_data']
        
        # Clean and validate data
        cleaned_data = self._clean_parsed_data(parsed_data)
        
        # Add metadata
        result = {
            'structured_resume': cleaned_data,
            'confidence': parsing_result['confidence'],
            'model_used': parsing_result['model'],
            'parsing_metadata': {
                'original_text_length': len(original_text),
                'sections_found': list(cleaned_data.keys()),
                'parsing_timestamp': datetime.utcnow().isoformat(),
                'schema_version': '1.0'
            },
            'quality_metrics': {
                'completeness_score': self._calculate_completeness_score(cleaned_data),
                'consistency_score': self._calculate_consistency_score(cleaned_data),
                'accuracy_indicators': self._get_accuracy_indicators(cleaned_data, original_text)
            }
        }
        
        return result
    
    def _clean_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
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