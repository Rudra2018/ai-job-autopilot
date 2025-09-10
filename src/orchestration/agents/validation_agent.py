"""
✅ ValidationAgent: Comprehensive schema compliance and data validation
Ensures data quality, consistency, and compliance across all agent outputs with intelligent correction.
"""

import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import jsonschema
from jsonschema import validate, ValidationError, draft7_format_checker
import email_validator
import phonenumbers
from phonenumbers import NumberParseException
import openai
import anthropic

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base_agent import BaseAgent, ProcessingResult

class ValidationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ValidationCategory(Enum):
    SCHEMA_COMPLIANCE = "schema_compliance"
    DATA_FORMAT = "data_format"
    BUSINESS_LOGIC = "business_logic"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"

@dataclass
class ValidationIssue:
    category: ValidationCategory
    severity: ValidationSeverity
    field_path: str
    issue_type: str
    description: str
    current_value: Any
    suggested_fix: Optional[str] = None
    confidence: float = 0.0
    auto_correctable: bool = False

@dataclass
class ValidationResult:
    is_valid: bool
    overall_score: float
    issues: List[ValidationIssue]
    corrections_applied: List[Dict[str, Any]]
    validation_metadata: Dict[str, Any]

class ValidationAgent(BaseAgent):
    """
    ✅ ValidationAgent: Comprehensive schema compliance and data validation
    
    Goals:
    1. Validate all agent outputs against comprehensive schemas
    2. Ensure data format compliance (emails, phones, dates, URLs)
    3. Apply business logic validation rules
    4. Check data consistency across resume sections
    5. Assess data completeness and identify missing critical fields
    6. Provide intelligent auto-correction suggestions
    7. Generate validation reports with actionable insights
    8. Support custom validation rules and industry-specific requirements
    """
    
    def _setup_agent_specific_config(self):
        """Setup comprehensive validation configurations."""
        
        # Initialize AI models for intelligent validation
        self._initialize_ai_validation_models()
        
        # Load comprehensive validation schemas
        self.validation_schemas = self._load_validation_schemas()
        self.business_rules = self._load_business_validation_rules()
        self.format_validators = self._initialize_format_validators()
        
        # Validation configuration
        self.validation_config = {
            'strict_mode': False,  # Allow minor schema deviations
            'auto_correction': True,  # Apply intelligent corrections
            'confidence_threshold': 0.7,  # Minimum confidence for auto-correction
            'max_correction_attempts': 3,
            'preserve_original_data': True
        }
        
        # Severity thresholds
        self.severity_thresholds = {
            'critical_score': 0.3,  # Below this = critical issues
            'high_score': 0.5,
            'medium_score': 0.7,
            'low_score': 0.85
        }
        
        # Initialize validation metrics
        self.validation_metrics = {
            'total_validations': 0,
            'auto_corrections_applied': 0,
            'critical_issues_found': 0,
            'validation_success_rate': 0.0
        }
        
        self.logger.info("✅ ValidationAgent initialized with comprehensive validation capabilities")
    
    def _initialize_ai_validation_models(self):
        """Initialize AI models for intelligent validation and correction."""
        
        self.available_ai_models = []
        
        # OpenAI GPT for intelligent validation
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
            self.available_ai_models.append('gpt')
            self.logger.info("✅ OpenAI GPT initialized for validation")
        
        # Anthropic Claude for validation reasoning
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            self.available_ai_models.append('claude')
            self.logger.info("✅ Anthropic Claude initialized for validation")
        
        # Google Gemini for validation analysis
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if GEMINI_AVAILABLE and gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.available_ai_models.append('gemini')
            self.logger.info("✅ Google Gemini initialized for validation")
    
    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive validation schemas for all data types."""
        
        return {
            'resume_schema': {
                "type": "object",
                "properties": {
                    "personal_information": {
                        "type": "object",
                        "properties": {
                            "full_name": {"type": "string", "minLength": 2, "maxLength": 100},
                            "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
                            "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
                            "email": {"type": "string", "format": "email"},
                            "phone": {"type": "string", "pattern": "^[+]?[0-9\\s\\-\\(\\)\\.\\_]{7,20}$"},
                            "location": {
                                "type": "object",
                                "properties": {
                                    "city": {"type": "string", "minLength": 1},
                                    "state": {"type": "string", "minLength": 1},
                                    "country": {"type": "string", "minLength": 1},
                                    "postal_code": {"type": "string"}
                                }
                            },
                            "social_profiles": {
                                "type": "object",
                                "properties": {
                                    "linkedin_url": {"type": "string", "format": "uri"},
                                    "github_url": {"type": "string", "format": "uri"},
                                    "portfolio_url": {"type": "string", "format": "uri"}
                                }
                            }
                        },
                        "required": ["full_name"]
                    },
                    "work_experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "company_name": {"type": "string", "minLength": 1},
                                "position_title": {"type": "string", "minLength": 1},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "location": {"type": "string"},
                                "key_responsibilities": {
                                    "type": "array",
                                    "items": {"type": "string", "minLength": 1}
                                },
                                "achievements": {
                                    "type": "array",
                                    "items": {"type": "string", "minLength": 1}
                                },
                                "technologies_used": {
                                    "type": "array",
                                    "items": {"type": "string", "minLength": 1}
                                }
                            },
                            "required": ["company_name", "position_title"]
                        }
                    },
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "institution_name": {"type": "string", "minLength": 1},
                                "degree_name": {"type": "string", "minLength": 1},
                                "field_of_study": {"type": "string"},
                                "graduation_date": {"type": "string"},
                                "gpa": {"type": "string"}
                            },
                            "required": ["institution_name", "degree_name"]
                        }
                    },
                    "skills": {
                        "type": "object",
                        "properties": {
                            "technical_skills": {"type": "object"},
                            "soft_skills": {
                                "type": "array",
                                "items": {"type": "string", "minLength": 1}
                            },
                            "languages": {"type": "array"}
                        }
                    }
                },
                "required": ["personal_information"]
            },
            'skill_analysis_schema': {
                "type": "object",
                "properties": {
                    "analysis_id": {"type": "string", "minLength": 1},
                    "comprehensive_analysis": {
                        "type": "object",
                        "properties": {
                            "skill_profiles": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "skill_name": {"type": "string", "minLength": 1},
                                        "category": {"type": "string"},
                                        "consensus_confidence": {
                                            "type": "number",
                                            "minimum": 0.0,
                                            "maximum": 1.0
                                        },
                                        "market_demand_score": {
                                            "type": "number", 
                                            "minimum": 0.0,
                                            "maximum": 1.0
                                        }
                                    },
                                    "required": ["skill_name", "category", "consensus_confidence"]
                                }
                            }
                        }
                    }
                },
                "required": ["analysis_id", "comprehensive_analysis"]
            },
            'ocr_result_schema': {
                "type": "object",
                "properties": {
                    "extraction_id": {"type": "string", "minLength": 1},
                    "documents_processed": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "successful_extractions": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "combined_extracted_text": {
                        "type": "string",
                        "minLength": 1
                    },
                    "overall_confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["extraction_id", "combined_extracted_text", "overall_confidence"]
            }
        }
    
    def _load_business_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load business logic validation rules."""
        
        return {
            'date_consistency': [
                {
                    'rule': 'work_experience_dates_logical',
                    'description': 'Work experience start date must be before end date',
                    'severity': ValidationSeverity.HIGH,
                    'fields': ['work_experience[*].start_date', 'work_experience[*].end_date']
                },
                {
                    'rule': 'education_before_work',
                    'description': 'Education graduation should typically precede work experience',
                    'severity': ValidationSeverity.MEDIUM,
                    'fields': ['education[*].graduation_date', 'work_experience[*].start_date']
                }
            ],
            'experience_consistency': [
                {
                    'rule': 'experience_gap_reasonable',
                    'description': 'Gaps in work experience should be reasonable (< 2 years)',
                    'severity': ValidationSeverity.MEDIUM,
                    'fields': ['work_experience']
                },
                {
                    'rule': 'experience_progression',
                    'description': 'Career progression should show logical advancement',
                    'severity': ValidationSeverity.LOW,
                    'fields': ['work_experience']
                }
            ],
            'data_quality': [
                {
                    'rule': 'contact_info_completeness',
                    'description': 'At least email or phone must be provided',
                    'severity': ValidationSeverity.CRITICAL,
                    'fields': ['personal_information.email', 'personal_information.phone']
                },
                {
                    'rule': 'skills_not_empty',
                    'description': 'At least some skills should be identified',
                    'severity': ValidationSeverity.HIGH,
                    'fields': ['skills']
                }
            ]
        }
    
    def _initialize_format_validators(self) -> Dict[str, callable]:
        """Initialize format validation functions."""
        
        return {
            'email': self._validate_email,
            'phone': self._validate_phone,
            'url': self._validate_url,
            'date': self._validate_date,
            'year': self._validate_year,
            'name': self._validate_name,
            'text_quality': self._validate_text_quality
        }
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate validation agent input data."""
        
        if not isinstance(input_data, dict):
            return {'valid': False, 'errors': ['Input must be a dictionary']}
        
        if 'data_to_validate' not in input_data:
            return {'valid': False, 'errors': ['Missing data_to_validate field']}
        
        if 'validation_type' not in input_data:
            return {'valid': False, 'errors': ['Missing validation_type field']}
        
        valid_types = ['resume_data', 'skill_analysis', 'ocr_result', 'custom']
        if input_data['validation_type'] not in valid_types:
            return {
                'valid': False, 
                'errors': [f'validation_type must be one of: {", ".join(valid_types)}']
            }
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Dict[str, Any]) -> ProcessingResult:
        """Perform comprehensive validation with intelligent correction."""
        
        data_to_validate = input_data['data_to_validate']
        validation_type = input_data['validation_type']
        validation_options = input_data.get('validation_options', {})
        
        # Initialize validation results
        results = {
            'validation_id': f"validation_{int(time.time())}",
            'validation_type': validation_type,
            'timestamp': datetime.utcnow().isoformat(),
            'original_data_size': self._calculate_data_size(data_to_validate),
            'validation_results': {},
            'corrections_applied': [],
            'final_validation_report': {}
        }
        
        try:
            # Step 1: Schema Validation
            schema_validation = await self._perform_schema_validation(
                data_to_validate, validation_type, validation_options
            )
            results['validation_results']['schema_validation'] = schema_validation
            
            # Step 2: Format Validation
            format_validation = await self._perform_format_validation(
                data_to_validate, validation_options
            )
            results['validation_results']['format_validation'] = format_validation
            
            # Step 3: Business Logic Validation
            business_validation = await self._perform_business_logic_validation(
                data_to_validate, validation_type, validation_options
            )
            results['validation_results']['business_validation'] = business_validation
            
            # Step 4: Consistency Validation
            consistency_validation = await self._perform_consistency_validation(
                data_to_validate, validation_options
            )
            results['validation_results']['consistency_validation'] = consistency_validation
            
            # Step 5: Completeness Assessment
            completeness_assessment = await self._assess_data_completeness(
                data_to_validate, validation_type, validation_options
            )
            results['validation_results']['completeness_assessment'] = completeness_assessment
            
            # Step 6: Apply Intelligent Corrections
            if validation_options.get('auto_correct', self.validation_config['auto_correction']):
                correction_results = await self._apply_intelligent_corrections(
                    data_to_validate, results['validation_results'], validation_options
                )
                results['corrections_applied'] = correction_results['corrections']
                results['corrected_data'] = correction_results['corrected_data']
            
            # Step 7: Generate Final Validation Report
            final_report = await self._generate_validation_report(results)
            results['final_validation_report'] = final_report
            
            # Calculate overall validation score
            overall_score = self._calculate_overall_validation_score(results)
            
            # Update metrics
            self._update_validation_metrics(results)
            
            return ProcessingResult(
                success=True,
                result=results,
                confidence=overall_score,
                processing_time=0.0,  # Will be set by base class
                metadata={
                    'validation_type': validation_type,
                    'total_issues': len(final_report.get('all_issues', [])),
                    'critical_issues': len([i for i in final_report.get('all_issues', []) if i.get('severity') == 'critical']),
                    'corrections_applied': len(results['corrections_applied']),
                    'overall_validity': final_report.get('is_valid', False)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            return ProcessingResult(
                success=False,
                result={'error': str(e), 'validation_id': results['validation_id']},
                confidence=0.0,
                processing_time=0.0,
                metadata={'validation_failed': True}
            )
    
    async def _perform_schema_validation(self, data: Dict[str, Any], validation_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive schema validation."""
        
        schema_key = f"{validation_type}_schema"
        if schema_key not in self.validation_schemas:
            return {
                'is_valid': False,
                'issues': [{'type': 'schema_not_found', 'message': f'No schema found for {validation_type}'}]
            }
        
        schema = self.validation_schemas[schema_key]
        issues = []
        
        try:
            # Use jsonschema for validation
            validate(data, schema, format_checker=draft7_format_checker)
            is_valid = True
            
        except ValidationError as e:
            is_valid = False
            issues.append({
                'type': 'schema_violation',
                'field_path': '.'.join(str(p) for p in e.absolute_path),
                'message': e.message,
                'severity': 'high',
                'schema_path': '.'.join(str(p) for p in e.schema_path)
            })
        
        except Exception as e:
            is_valid = False
            issues.append({
                'type': 'schema_error',
                'message': f'Schema validation error: {str(e)}',
                'severity': 'critical'
            })
        
        return {
            'is_valid': is_valid,
            'issues': issues,
            'schema_used': schema_key,
            'validation_method': 'jsonschema'
        }
    
    async def _perform_format_validation(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive format validation."""
        
        issues = []
        
        # Recursively validate formats throughout the data structure
        await self._validate_formats_recursive(data, '', issues)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'total_fields_checked': self._count_validated_fields(data),
            'format_validators_used': list(self.format_validators.keys())
        }
    
    async def _validate_formats_recursive(self, data: Any, path: str, issues: List[Dict[str, Any]]):
        """Recursively validate formats in nested data structures."""
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check specific field formats based on field name
                if key == 'email' and isinstance(value, str):
                    if not self._validate_email(value):
                        issues.append({
                            'type': 'invalid_email',
                            'field_path': current_path,
                            'current_value': value,
                            'severity': 'high',
                            'message': f'Invalid email format: {value}'
                        })
                
                elif key == 'phone' and isinstance(value, str):
                    if not self._validate_phone(value):
                        issues.append({
                            'type': 'invalid_phone',
                            'field_path': current_path,
                            'current_value': value,
                            'severity': 'medium',
                            'message': f'Invalid phone format: {value}'
                        })
                
                elif key.endswith('_url') and isinstance(value, str):
                    if not self._validate_url(value):
                        issues.append({
                            'type': 'invalid_url',
                            'field_path': current_path,
                            'current_value': value,
                            'severity': 'medium',
                            'message': f'Invalid URL format: {value}'
                        })
                
                elif key.endswith('_date') and isinstance(value, str):
                    if not self._validate_date(value):
                        issues.append({
                            'type': 'invalid_date',
                            'field_path': current_path,
                            'current_value': value,
                            'severity': 'medium',
                            'message': f'Invalid date format: {value}'
                        })
                
                # Recurse into nested structures
                await self._validate_formats_recursive(value, current_path, issues)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                await self._validate_formats_recursive(item, current_path, issues)
    
    async def _perform_business_logic_validation(self, data: Dict[str, Any], validation_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform business logic validation."""
        
        issues = []
        
        # Apply business rules based on validation type
        if validation_type == 'resume_data':
            # Work experience date consistency
            work_exp_issues = await self._validate_work_experience_logic(data.get('work_experience', []))
            issues.extend(work_exp_issues)
            
            # Contact information completeness
            contact_issues = await self._validate_contact_completeness(data.get('personal_information', {}))
            issues.extend(contact_issues)
            
            # Education-work timeline consistency
            timeline_issues = await self._validate_education_work_timeline(
                data.get('education', []), data.get('work_experience', [])
            )
            issues.extend(timeline_issues)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'rules_applied': len(self.business_rules.get(validation_type, [])),
            'validation_method': 'business_logic'
        }
    
    async def _perform_consistency_validation(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform data consistency validation."""
        
        issues = []
        
        # Name consistency across sections
        name_issues = await self._validate_name_consistency(data)
        issues.extend(name_issues)
        
        # Skills mentioned in experience vs skills section
        skills_issues = await self._validate_skills_consistency(data)
        issues.extend(skills_issues)
        
        # Technology consistency across projects and experience
        tech_issues = await self._validate_technology_consistency(data)
        issues.extend(tech_issues)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'consistency_checks': ['name_consistency', 'skills_consistency', 'technology_consistency']
        }
    
    async def _assess_data_completeness(self, data: Dict[str, Any], validation_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data completeness and identify missing critical fields."""
        
        completeness_score = 0.0
        missing_critical = []
        missing_recommended = []
        
        if validation_type == 'resume_data':
            # Critical fields
            critical_fields = [
                'personal_information.full_name',
                'personal_information.email',
                'work_experience',
                'education'
            ]
            
            critical_present = 0
            for field_path in critical_fields:
                if self._field_exists(data, field_path):
                    critical_present += 1
                else:
                    missing_critical.append(field_path)
            
            # Recommended fields
            recommended_fields = [
                'personal_information.phone',
                'personal_information.location',
                'skills.technical_skills',
                'personal_information.social_profiles.linkedin_url'
            ]
            
            recommended_present = 0
            for field_path in recommended_fields:
                if self._field_exists(data, field_path):
                    recommended_present += 1
                else:
                    missing_recommended.append(field_path)
            
            # Calculate completeness score
            critical_weight = 0.7
            recommended_weight = 0.3
            
            critical_completeness = critical_present / len(critical_fields)
            recommended_completeness = recommended_present / len(recommended_fields)
            
            completeness_score = (
                critical_completeness * critical_weight + 
                recommended_completeness * recommended_weight
            )
        
        return {
            'completeness_score': completeness_score,
            'missing_critical': missing_critical,
            'missing_recommended': missing_recommended,
            'is_complete': len(missing_critical) == 0 and completeness_score >= 0.8
        }
    
    async def _apply_intelligent_corrections(self, data: Dict[str, Any], validation_results: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent corrections to validation issues."""
        
        corrections = []
        corrected_data = json.deepcopy(data)
        
        # Collect all issues that can be auto-corrected
        all_issues = []
        for validation_type, results in validation_results.items():
            if 'issues' in results:
                all_issues.extend(results['issues'])
        
        # Apply corrections based on issue type and severity
        for issue in all_issues:
            if issue.get('severity') in ['critical', 'high'] and 'field_path' in issue:
                correction = await self._attempt_intelligent_correction(
                    issue, corrected_data, options
                )
                if correction:
                    corrections.append(correction)
        
        return {
            'corrections': corrections,
            'corrected_data': corrected_data,
            'total_corrections': len(corrections)
        }
    
    async def _attempt_intelligent_correction(self, issue: Dict[str, Any], data: Dict[str, Any], options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to intelligently correct a validation issue."""
        
        issue_type = issue.get('type')
        field_path = issue.get('field_path')
        current_value = issue.get('current_value')
        
        correction = None
        
        try:
            if issue_type == 'invalid_email' and isinstance(current_value, str):
                # Try to fix common email issues
                corrected_email = self._attempt_email_correction(current_value)
                if corrected_email and corrected_email != current_value:
                    self._set_field_value(data, field_path, corrected_email)
                    correction = {
                        'field_path': field_path,
                        'issue_type': issue_type,
                        'original_value': current_value,
                        'corrected_value': corrected_email,
                        'correction_method': 'pattern_based',
                        'confidence': 0.8
                    }
            
            elif issue_type == 'invalid_phone' and isinstance(current_value, str):
                # Try to fix common phone number issues
                corrected_phone = self._attempt_phone_correction(current_value)
                if corrected_phone and corrected_phone != current_value:
                    self._set_field_value(data, field_path, corrected_phone)
                    correction = {
                        'field_path': field_path,
                        'issue_type': issue_type,
                        'original_value': current_value,
                        'corrected_value': corrected_phone,
                        'correction_method': 'format_normalization',
                        'confidence': 0.7
                    }
            
            elif issue_type == 'invalid_date' and isinstance(current_value, str):
                # Try to fix common date issues
                corrected_date = self._attempt_date_correction(current_value)
                if corrected_date and corrected_date != current_value:
                    self._set_field_value(data, field_path, corrected_date)
                    correction = {
                        'field_path': field_path,
                        'issue_type': issue_type,
                        'original_value': current_value,
                        'corrected_value': corrected_date,
                        'correction_method': 'date_parsing',
                        'confidence': 0.6
                    }
        
        except Exception as e:
            self.logger.warning(f"Failed to correct {issue_type} at {field_path}: {str(e)}")
        
        return correction
    
    # Format Validation Methods
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        try:
            email_validator.validate_email(email)
            return True
        except:
            # Fallback to regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_pattern, email) is not None
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        try:
            parsed_number = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(parsed_number)
        except NumberParseException:
            # Fallback to basic pattern matching
            phone_pattern = r'^[+]?[0-9\s\-\(\)\.\\_]{7,20}$'
            return re.match(phone_pattern, phone) is not None
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return re.match(url_pattern, url) is not None
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format."""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}$',        # YYYY-MM
            r'^\d{4}$',              # YYYY
            r'^(present|current)$'   # Special values
        ]
        return any(re.match(pattern, date_str.lower()) for pattern in date_patterns)
    
    def _validate_year(self, year_str: str) -> bool:
        """Validate year format."""
        try:
            year = int(year_str)
            return 1900 <= year <= 2030
        except ValueError:
            return False
    
    def _validate_name(self, name: str) -> bool:
        """Validate name format."""
        return len(name.strip()) >= 2 and re.match(r'^[a-zA-Z\s\-\.\']+$', name)
    
    def _validate_text_quality(self, text: str) -> bool:
        """Validate text quality (no excessive special characters, reasonable length)."""
        if not text or len(text.strip()) < 2:
            return False
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^\w\s\-\.\,\!\?\(\)]', text)) / len(text)
        return special_char_ratio < 0.3
    
    # Business Logic Validation Methods
    async def _validate_work_experience_logic(self, work_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate work experience business logic."""
        issues = []
        
        for i, job in enumerate(work_experience):
            start_date = job.get('start_date', '')
            end_date = job.get('end_date', '')
            
            if start_date and end_date and end_date.lower() not in ['present', 'current']:
                # Check if start date is before end date
                if not self._is_date_before(start_date, end_date):
                    issues.append({
                        'type': 'illogical_work_dates',
                        'field_path': f'work_experience[{i}]',
                        'severity': 'high',
                        'message': f'Start date ({start_date}) is after end date ({end_date})',
                        'current_value': {'start_date': start_date, 'end_date': end_date}
                    })
        
        return issues
    
    async def _validate_contact_completeness(self, personal_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate contact information completeness."""
        issues = []
        
        email = personal_info.get('email', '').strip()
        phone = personal_info.get('phone', '').strip()
        
        if not email and not phone:
            issues.append({
                'type': 'missing_contact_info',
                'field_path': 'personal_information',
                'severity': 'critical',
                'message': 'At least email or phone number must be provided',
                'current_value': {'email': email, 'phone': phone}
            })
        
        return issues
    
    async def _validate_education_work_timeline(self, education: List[Dict[str, Any]], work_experience: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate education and work experience timeline consistency."""
        issues = []
        
        # Get latest graduation year
        latest_grad_year = None
        for edu in education:
            grad_date = edu.get('graduation_date', '')
            if grad_date and self._validate_year(grad_date[:4]):
                year = int(grad_date[:4])
                if latest_grad_year is None or year > latest_grad_year:
                    latest_grad_year = year
        
        # Check if work experience starts reasonably after graduation
        if latest_grad_year:
            for i, job in enumerate(work_experience):
                start_date = job.get('start_date', '')
                if start_date and self._validate_year(start_date[:4]):
                    work_year = int(start_date[:4])
                    if work_year < latest_grad_year - 1:  # Allow 1 year tolerance
                        issues.append({
                            'type': 'work_before_graduation',
                            'field_path': f'work_experience[{i}].start_date',
                            'severity': 'medium',
                            'message': f'Work start year ({work_year}) is before graduation year ({latest_grad_year})',
                            'current_value': {'work_start': start_date, 'graduation': latest_grad_year}
                        })
        
        return issues
    
    # Consistency Validation Methods
    async def _validate_name_consistency(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate name consistency across sections."""
        issues = []
        
        personal_info = data.get('personal_information', {})
        full_name = personal_info.get('full_name', '').strip()
        first_name = personal_info.get('first_name', '').strip()
        last_name = personal_info.get('last_name', '').strip()
        
        if full_name and first_name and last_name:
            # Check if first and last name are consistent with full name
            expected_full = f"{first_name} {last_name}"
            if not self._names_similar(full_name.lower(), expected_full.lower()):
                issues.append({
                    'type': 'name_inconsistency',
                    'field_path': 'personal_information',
                    'severity': 'medium',
                    'message': f'Full name "{full_name}" does not match first "{first_name}" and last "{last_name}" names',
                    'current_value': {'full_name': full_name, 'first_name': first_name, 'last_name': last_name}
                })
        
        return issues
    
    async def _validate_skills_consistency(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate skills consistency between experience and skills sections."""
        issues = []
        
        # Extract skills from work experience
        work_skills = set()
        for job in data.get('work_experience', []):
            for tech in job.get('technologies_used', []):
                work_skills.add(tech.lower())
        
        # Extract skills from skills section
        skills_section = data.get('skills', {})
        declared_skills = set()
        
        if isinstance(skills_section, dict):
            for category, skills_list in skills_section.items():
                if isinstance(skills_list, list):
                    for skill in skills_list:
                        declared_skills.add(skill.lower())
                elif isinstance(skills_list, dict):
                    for subcategory, subskills in skills_list.items():
                        if isinstance(subskills, list):
                            for skill in subskills:
                                declared_skills.add(skill.lower())
        
        # Check for skills mentioned in experience but not in skills section
        undeclared_skills = work_skills - declared_skills
        if len(undeclared_skills) > 3:  # Only flag if significant discrepancy
            issues.append({
                'type': 'skills_not_declared',
                'field_path': 'skills',
                'severity': 'low',
                'message': f'Skills used in work experience but not declared in skills section: {list(undeclared_skills)[:5]}',
                'current_value': {'undeclared_count': len(undeclared_skills)}
            })
        
        return issues
    
    async def _validate_technology_consistency(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate technology consistency across projects and experience."""
        issues = []
        # Implementation would check technology mentions across different sections
        return issues
    
    # Correction Methods
    def _attempt_email_correction(self, email: str) -> Optional[str]:
        """Attempt to correct common email issues."""
        email = email.strip().lower()
        
        # Fix common typos
        corrections = {
            'gmail.co': 'gmail.com',
            'gmial.com': 'gmail.com',
            'yahoo.co': 'yahoo.com',
            'hotmail.co': 'hotmail.com',
            'outlook.co': 'outlook.com'
        }
        
        for typo, correction in corrections.items():
            if typo in email:
                email = email.replace(typo, correction)
        
        # Validate corrected email
        if self._validate_email(email):
            return email
        
        return None
    
    def _attempt_phone_correction(self, phone: str) -> Optional[str]:
        """Attempt to correct common phone number issues."""
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Add country code if missing (assume US)
        if len(cleaned) == 10 and not cleaned.startswith('+'):
            cleaned = '+1' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('1'):
            cleaned = '+' + cleaned
        
        # Format as standard international format
        if cleaned.startswith('+1') and len(cleaned) == 12:
            formatted = f"+1 ({cleaned[2:5]}) {cleaned[5:8]}-{cleaned[8:]}"
            return formatted
        
        return cleaned if self._validate_phone(cleaned) else None
    
    def _attempt_date_correction(self, date_str: str) -> Optional[str]:
        """Attempt to correct common date issues."""
        date_str = date_str.strip()
        
        # Handle common formats
        if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
            # Convert MM/DD/YYYY to YYYY-MM-DD
            parts = date_str.split('/')
            return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        
        elif re.match(r'^\d{4}/\d{1,2}$', date_str):
            # Convert YYYY/MM to YYYY-MM
            parts = date_str.split('/')
            return f"{parts[0]}-{parts[1].zfill(2)}"
        
        elif re.match(r'^\d{4}$', date_str):
            # Year only is fine
            return date_str
        
        return None
    
    # Helper Methods
    def _calculate_data_size(self, data: Any) -> Dict[str, int]:
        """Calculate data size metrics."""
        json_str = json.dumps(data, default=str)
        return {
            'total_characters': len(json_str),
            'total_fields': self._count_fields(data),
            'nested_levels': self._count_nested_levels(data)
        }
    
    def _count_fields(self, data: Any, count: int = 0) -> int:
        """Count total fields in nested data structure."""
        if isinstance(data, dict):
            count += len(data)
            for value in data.values():
                count = self._count_fields(value, count)
        elif isinstance(data, list):
            for item in data:
                count = self._count_fields(item, count)
        return count
    
    def _count_nested_levels(self, data: Any, level: int = 0) -> int:
        """Count maximum nested levels in data structure."""
        if isinstance(data, (dict, list)):
            max_child_level = level
            iterable = data.values() if isinstance(data, dict) else data
            for item in iterable:
                child_level = self._count_nested_levels(item, level + 1)
                max_child_level = max(max_child_level, child_level)
            return max_child_level
        return level
    
    def _count_validated_fields(self, data: Any) -> int:
        """Count fields that underwent format validation."""
        # This would count specific fields that were validated
        return self._count_fields(data)
    
    def _field_exists(self, data: Dict[str, Any], field_path: str) -> bool:
        """Check if a field path exists in the data structure."""
        try:
            parts = field_path.split('.')
            current = data
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return False
                else:
                    return False
            
            # Check if the final value is meaningful (not empty/null)
            if current is None:
                return False
            elif isinstance(current, str) and not current.strip():
                return False
            elif isinstance(current, (list, dict)) and not current:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _set_field_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set a field value using dot notation path."""
        try:
            parts = field_path.split('.')
            current = data
            
            for part in parts[:-1]:
                if isinstance(current, dict):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
            
            if isinstance(current, dict):
                current[parts[-1]] = value
                
        except Exception as e:
            self.logger.warning(f"Failed to set field {field_path}: {str(e)}")
    
    def _is_date_before(self, date1: str, date2: str) -> bool:
        """Check if date1 is before date2."""
        try:
            # Extract years for comparison
            year1 = int(date1[:4]) if len(date1) >= 4 else 0
            year2 = int(date2[:4]) if len(date2) >= 4 else 0
            
            if year1 != year2:
                return year1 < year2
            
            # If years are same, try to compare months
            if '-' in date1 and '-' in date2:
                month1 = int(date1.split('-')[1]) if len(date1.split('-')) > 1 else 1
                month2 = int(date2.split('-')[1]) if len(date2.split('-')) > 1 else 1
                return month1 <= month2
            
            return True  # If we can't determine, assume it's valid
            
        except (ValueError, IndexError):
            return True  # If parsing fails, assume it's valid
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar (allowing for middle names, initials, etc.)."""
        # Simple similarity check - in production, use more sophisticated matching
        name1_words = set(name1.split())
        name2_words = set(name2.split())
        
        # Check if there's significant overlap
        intersection = name1_words.intersection(name2_words)
        union = name1_words.union(name2_words)
        
        if not union:
            return False
        
        similarity = len(intersection) / len(union)
        return similarity >= 0.5  # At least 50% overlap
    
    async def _generate_validation_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        
        all_issues = []
        
        # Collect all issues from different validation stages
        for validation_type, validation_result in results['validation_results'].items():
            if 'issues' in validation_result:
                for issue in validation_result['issues']:
                    issue['validation_stage'] = validation_type
                    all_issues.append(issue)
        
        # Categorize issues by severity
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']
        medium_issues = [i for i in all_issues if i.get('severity') == 'medium']
        low_issues = [i for i in all_issues if i.get('severity') == 'low']
        
        # Determine overall validity
        is_valid = len(critical_issues) == 0 and len(high_issues) <= 2
        
        # Generate recommendations
        recommendations = await self._generate_validation_recommendations(all_issues)
        
        return {
            'is_valid': is_valid,
            'overall_score': self._calculate_overall_validation_score(results),
            'total_issues': len(all_issues),
            'issues_by_severity': {
                'critical': len(critical_issues),
                'high': len(high_issues),
                'medium': len(medium_issues),
                'low': len(low_issues)
            },
            'all_issues': all_issues,
            'validation_summary': {
                'schema_compliance': results['validation_results'].get('schema_validation', {}).get('is_valid', False),
                'format_validity': results['validation_results'].get('format_validation', {}).get('is_valid', False),
                'business_logic': results['validation_results'].get('business_validation', {}).get('is_valid', False),
                'consistency': results['validation_results'].get('consistency_validation', {}).get('is_valid', False),
                'completeness_score': results['validation_results'].get('completeness_assessment', {}).get('completeness_score', 0.0)
            },
            'recommendations': recommendations,
            'corrections_available': len(results.get('corrections_applied', [])) > 0
        }
    
    async def _generate_validation_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on validation issues."""
        
        recommendations = []
        
        # Group issues by type for targeted recommendations
        issue_types = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generate specific recommendations
        if 'missing_contact_info' in issue_types:
            recommendations.append("Add complete contact information (email and/or phone number)")
        
        if 'invalid_email' in issue_types:
            recommendations.append("Verify and correct email address format")
        
        if 'invalid_phone' in issue_types:
            recommendations.append("Standardize phone number format (international format recommended)")
        
        if 'illogical_work_dates' in issue_types:
            recommendations.append("Review work experience dates for logical consistency")
        
        if 'schema_violation' in issue_types:
            recommendations.append("Ensure all required fields are present and properly formatted")
        
        if 'skills_not_declared' in issue_types:
            recommendations.append("Add skills mentioned in work experience to the skills section")
        
        # General recommendations if no specific issues
        if not recommendations:
            recommendations.append("Data structure looks good - consider adding more detail for completeness")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _calculate_overall_validation_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall validation score (0.0 to 1.0)."""
        
        scores = []
        weights = []
        
        # Schema validation score
        schema_result = results['validation_results'].get('schema_validation', {})
        if schema_result.get('is_valid'):
            scores.append(1.0)
        else:
            scores.append(0.3)  # Severe penalty for schema violations
        weights.append(0.3)
        
        # Format validation score
        format_result = results['validation_results'].get('format_validation', {})
        if format_result.get('is_valid'):
            scores.append(1.0)
        else:
            # Penalty based on number of format issues
            num_issues = len(format_result.get('issues', []))
            scores.append(max(0.0, 1.0 - (num_issues * 0.2)))
        weights.append(0.25)
        
        # Business logic score
        business_result = results['validation_results'].get('business_validation', {})
        if business_result.get('is_valid'):
            scores.append(1.0)
        else:
            num_issues = len(business_result.get('issues', []))
            scores.append(max(0.0, 1.0 - (num_issues * 0.15)))
        weights.append(0.2)
        
        # Consistency score
        consistency_result = results['validation_results'].get('consistency_validation', {})
        if consistency_result.get('is_valid'):
            scores.append(1.0)
        else:
            num_issues = len(consistency_result.get('issues', []))
            scores.append(max(0.0, 1.0 - (num_issues * 0.1)))
        weights.append(0.15)
        
        # Completeness score
        completeness_result = results['validation_results'].get('completeness_assessment', {})
        completeness_score = completeness_result.get('completeness_score', 0.5)
        scores.append(completeness_score)
        weights.append(0.1)
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            overall_score = 0.0
        
        return round(min(max(overall_score, 0.0), 1.0), 3)
    
    def _update_validation_metrics(self, results: Dict[str, Any]):
        """Update validation metrics for monitoring."""
        
        self.validation_metrics['total_validations'] += 1
        self.validation_metrics['auto_corrections_applied'] += len(results.get('corrections_applied', []))
        
        # Count critical issues
        final_report = results.get('final_validation_report', {})
        critical_count = final_report.get('issues_by_severity', {}).get('critical', 0)
        self.validation_metrics['critical_issues_found'] += critical_count
        
        # Update success rate
        is_valid = final_report.get('is_valid', False)
        current_successes = self.validation_metrics.get('validation_success_rate', 0) * (self.validation_metrics['total_validations'] - 1)
        new_successes = current_successes + (1 if is_valid else 0)
        self.validation_metrics['validation_success_rate'] = new_successes / self.validation_metrics['total_validations']