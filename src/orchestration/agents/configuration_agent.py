#!/usr/bin/env python3
"""
🎯 ConfigurationAgent: User Input Validation & Routing System
Entry point agent for handling all user inputs, validation, and routing to downstream agents.
"""

import asyncio
import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import aiofiles
import base64
import mimetypes
import logging
from PIL import Image
import io

# File type validation
SUPPORTED_RESUME_FORMATS = {'.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
SUPPORTED_IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
SUPPORTED_DOCUMENT_FORMATS = {'.pdf', '.docx', '.doc', '.txt'}

class InputType(Enum):
    """Types of inputs the configuration agent handles."""
    RESUME_FILE = "resume_file"
    USER_PREFERENCES = "user_preferences"
    PLATFORM_CREDENTIALS = "platform_credentials"
    STYLE_GUIDE = "style_guide"
    COVER_LETTER_TEMPLATE = "cover_letter_template"

class ValidationLevel(Enum):
    """Validation strictness levels."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

class FileType(Enum):
    """Supported file types."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    TIFF = "tiff"
    BMP = "bmp"

@dataclass
class ResumeFile:
    """Resume file metadata and validation results."""
    file_path: str
    file_name: str
    file_type: FileType
    file_size: int
    content_hash: str
    validation_status: bool
    validation_errors: List[str]
    metadata: Dict[str, Any]
    uploaded_at: datetime

@dataclass
class UserPreferences:
    """Structured user preferences."""
    job_preferences: Dict[str, Any]
    location_preferences: Dict[str, Any]
    salary_expectations: Dict[str, Any]
    platform_preferences: Dict[str, Any]
    automation_settings: Dict[str, Any]
    notification_settings: Dict[str, Any]
    privacy_settings: Dict[str, Any]

@dataclass
class PlatformCredentials:
    """Platform credentials with encryption metadata."""
    platform: str
    username: str
    encrypted_credential_id: str
    credential_type: str
    two_factor_enabled: bool
    additional_data: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]

@dataclass
class StyleGuide:
    """Branding and style guide information."""
    brand_voice: str
    writing_tone: str
    preferred_language: str
    formatting_preferences: Dict[str, Any]
    company_values: List[str]
    personal_brand: Dict[str, Any]
    custom_templates: Dict[str, str]

@dataclass
class ConfigurationPackage:
    """Complete validated configuration package."""
    configuration_id: str
    user_id: str
    resume_file: Optional[ResumeFile]
    user_preferences: UserPreferences
    platform_credentials: List[PlatformCredentials]
    style_guide: Optional[StyleGuide]
    cover_letter_template: Optional[str]
    validation_level: ValidationLevel
    created_at: datetime
    routing_instructions: Dict[str, List[str]]
    processing_flags: Dict[str, bool]

class ConfigurationAgent:
    """
    Configuration agent for handling user inputs and routing.
    
    Features:
    - Multi-format file validation and preprocessing
    - Secure credential handling with encryption
    - Comprehensive input validation and sanitization
    - Intelligent routing to downstream agents
    - Schema compliance enforcement
    - Audit logging for all configurations
    - Error recovery and user feedback
    """
    
    def __init__(self, 
                 validation_level: ValidationLevel = ValidationLevel.STANDARD,
                 enable_encryption: bool = True,
                 audit_logging: bool = True):
        """Initialize the configuration agent."""
        self.validation_level = validation_level
        self.enable_encryption = enable_encryption
        self.audit_logging = audit_logging
        
        self.logger = self._setup_logging()
        self.configurations = {}
        self.validation_rules = self._load_validation_rules()
        self.schema_definitions = self._load_schema_definitions()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger("ConfigurationAgent")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different input types."""
        return {
            'resume_file': {
                'max_size_mb': 10,
                'required_formats': list(SUPPORTED_RESUME_FORMATS),
                'min_content_length': 100,
                'security_scan': True
            },
            'user_preferences': {
                'required_fields': ['job_type', 'preferred_locations'],
                'optional_fields': ['salary_min', 'salary_max', 'remote_ok'],
                'validation_schema': 'user_preferences_v1'
            },
            'platform_credentials': {
                'supported_platforms': ['linkedin', 'indeed', 'glassdoor', 'company_portal'],
                'require_encryption': True,
                'audit_access': True,
                'security_validation': True
            },
            'style_guide': {
                'supported_tones': ['professional', 'casual', 'creative', 'technical'],
                'supported_languages': ['en', 'es', 'fr', 'de', 'pt'],
                'max_template_size': 5000
            }
        }
    
    def _load_schema_definitions(self) -> Dict[str, Any]:
        """Load JSON schema definitions for validation."""
        return {
            'user_preferences_v1': {
                "type": "object",
                "properties": {
                    "job_preferences": {
                        "type": "object",
                        "properties": {
                            "job_type": {"type": "string"},
                            "industries": {"type": "array", "items": {"type": "string"}},
                            "experience_level": {"type": "string"},
                            "company_size": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["job_type"]
                    },
                    "location_preferences": {
                        "type": "object",
                        "properties": {
                            "preferred_locations": {"type": "array", "items": {"type": "string"}},
                            "remote_ok": {"type": "boolean"},
                            "relocation_ok": {"type": "boolean"},
                            "travel_ok": {"type": "boolean"}
                        },
                        "required": ["preferred_locations"]
                    },
                    "salary_expectations": {
                        "type": "object",
                        "properties": {
                            "min_salary": {"type": "number", "minimum": 0},
                            "max_salary": {"type": "number", "minimum": 0},
                            "currency": {"type": "string"},
                            "salary_type": {"type": "string", "enum": ["hourly", "annual", "contract"]}
                        }
                    }
                },
                "required": ["job_preferences", "location_preferences"]
            }
        }
    
    async def process_user_input(self,
                               user_input: Dict[str, Any],
                               user_id: str = None) -> ConfigurationPackage:
        """
        Process and validate all user inputs, creating a configuration package.
        
        Args:
            user_input: Raw user input containing files, preferences, credentials
            user_id: Unique user identifier
            
        Returns:
            ConfigurationPackage: Validated and structured configuration
        """
        start_time = datetime.now()
        configuration_id = str(uuid.uuid4())
        user_id = user_id or str(uuid.uuid4())
        
        try:
            self.logger.info(f"Processing user input for configuration: {configuration_id}")
            
            # Initialize configuration components
            resume_file = None
            user_preferences = None
            platform_credentials = []
            style_guide = None
            cover_letter_template = None
            routing_instructions = {}
            processing_flags = {}
            
            # Process resume file if provided
            if 'resume_file' in user_input:
                resume_file = await self._process_resume_file(
                    user_input['resume_file'], configuration_id
                )
                routing_instructions['OCRAgent'] = ['process_document']
                routing_instructions['ParserAgent'] = ['parse_resume']
                processing_flags['requires_ocr'] = True
            
            # Process user preferences
            if 'user_preferences' in user_input:
                user_preferences = await self._process_user_preferences(
                    user_input['user_preferences']
                )
                routing_instructions['DiscoveryAgent'] = ['find_jobs']
                processing_flags['requires_job_search'] = True
            else:
                # Create default preferences if not provided
                user_preferences = self._create_default_preferences()
            
            # Process platform credentials
            if 'platform_credentials' in user_input:
                platform_credentials = await self._process_platform_credentials(
                    user_input['platform_credentials'], configuration_id
                )
                routing_instructions['SecurityAgent'] = ['store_credentials']
                processing_flags['requires_authentication'] = True
            
            # Process style guide
            if 'style_guide' in user_input:
                style_guide = await self._process_style_guide(
                    user_input['style_guide']
                )
                routing_instructions['CoverLetterAgent'] = ['apply_style_guide']
                routing_instructions['UIAgent'] = ['apply_branding']
                processing_flags['has_custom_branding'] = True
            
            # Process cover letter template
            if 'cover_letter_template' in user_input:
                cover_letter_template = await self._process_cover_letter_template(
                    user_input['cover_letter_template']
                )
                routing_instructions['CoverLetterAgent'] = routing_instructions.get('CoverLetterAgent', [])
                routing_instructions['CoverLetterAgent'].append('use_template')
                processing_flags['has_custom_template'] = True
            
            # Create configuration package
            configuration = ConfigurationPackage(
                configuration_id=configuration_id,
                user_id=user_id,
                resume_file=resume_file,
                user_preferences=user_preferences,
                platform_credentials=platform_credentials,
                style_guide=style_guide,
                cover_letter_template=cover_letter_template,
                validation_level=self.validation_level,
                created_at=datetime.now(timezone.utc),
                routing_instructions=routing_instructions,
                processing_flags=processing_flags
            )
            
            # Store configuration
            self.configurations[configuration_id] = configuration
            
            # Audit logging
            if self.audit_logging:
                await self._create_audit_log(configuration_id, "configuration_created", True)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Configuration created successfully: {configuration_id} in {processing_time:.2f}s")
            
            return configuration
            
        except Exception as e:
            if self.audit_logging:
                await self._create_audit_log(configuration_id, "configuration_failed", False, str(e))
            
            self.logger.error(f"Failed to process user input: {e}")
            raise
    
    async def _process_resume_file(self,
                                 file_input: Union[str, bytes, Dict[str, Any]],
                                 configuration_id: str) -> ResumeFile:
        """Process and validate resume file."""
        try:
            # Handle different input formats
            if isinstance(file_input, dict):
                file_path = file_input.get('path')
                file_name = file_input.get('name')
                file_data = file_input.get('data')  # Base64 encoded data
            elif isinstance(file_input, str):
                file_path = file_input
                file_name = Path(file_input).name
                file_data = None
            else:
                raise ValueError("Invalid file input format")
            
            # Validate file extension
            file_extension = Path(file_name).suffix.lower()
            if file_extension not in SUPPORTED_RESUME_FORMATS:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Determine file type
            file_type = FileType(file_extension.lstrip('.'))
            
            # Get file size and content hash
            if file_data:
                # Handle base64 encoded data
                file_content = base64.b64decode(file_data)
                file_size = len(file_content)
            else:
                # Handle file path
                file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
                async with aiofiles.open(file_path, 'rb') as f:
                    file_content = await f.read()
            
            # Validate file size
            max_size = self.validation_rules['resume_file']['max_size_mb'] * 1024 * 1024
            if file_size > max_size:
                raise ValueError(f"File size {file_size} exceeds maximum {max_size}")
            
            # Calculate content hash
            content_hash = hashlib.sha256(file_content).hexdigest()
            
            # Validate file content
            validation_errors = []
            validation_status = True
            
            # Basic content validation
            if file_size < 100:  # Minimum file size
                validation_errors.append("File appears to be empty or corrupted")
                validation_status = False
            
            # Image-specific validation
            if file_extension in SUPPORTED_IMAGE_FORMATS:
                try:
                    image = Image.open(io.BytesIO(file_content))
                    # Check image dimensions
                    if image.width < 200 or image.height < 200:
                        validation_errors.append("Image resolution too low for OCR")
                        validation_status = False
                except Exception as e:
                    validation_errors.append(f"Invalid image file: {str(e)}")
                    validation_status = False
            
            # Security scan (basic malware detection)
            if self.validation_rules['resume_file']['security_scan']:
                security_issues = await self._scan_file_security(file_content, file_type)
                validation_errors.extend(security_issues)
                if security_issues:
                    validation_status = False
            
            # Create metadata
            metadata = {
                'mime_type': mimetypes.guess_type(file_name)[0],
                'encoding': 'utf-8' if file_extension == '.txt' else 'binary',
                'processing_priority': 'high' if file_extension in SUPPORTED_IMAGE_FORMATS else 'standard',
                'ocr_required': file_extension in SUPPORTED_IMAGE_FORMATS,
                'preprocessing_required': True
            }
            
            resume_file = ResumeFile(
                file_path=file_path or f"temp_{configuration_id}_{file_name}",
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                content_hash=content_hash,
                validation_status=validation_status,
                validation_errors=validation_errors,
                metadata=metadata,
                uploaded_at=datetime.now(timezone.utc)
            )
            
            self.logger.info(f"Resume file processed: {file_name} ({file_size} bytes)")
            return resume_file
            
        except Exception as e:
            self.logger.error(f"Failed to process resume file: {e}")
            raise
    
    async def _process_user_preferences(self, preferences: Dict[str, Any]) -> UserPreferences:
        """Process and validate user preferences."""
        try:
            # Validate against schema
            await self._validate_against_schema(preferences, 'user_preferences_v1')
            
            # Extract and structure preferences
            job_preferences = preferences.get('job_preferences', {})
            location_preferences = preferences.get('location_preferences', {})
            salary_expectations = preferences.get('salary_expectations', {})
            
            # Process platform preferences
            platform_preferences = preferences.get('platform_preferences', {
                'preferred_platforms': ['linkedin', 'indeed'],
                'auto_apply': False,
                'daily_application_limit': 10,
                'application_schedule': 'business_hours'
            })
            
            # Process automation settings
            automation_settings = preferences.get('automation_settings', {
                'auto_cover_letter': True,
                'auto_follow_up': False,
                'personalization_level': 'standard',
                'quality_over_quantity': True
            })
            
            # Process notification settings
            notification_settings = preferences.get('notification_settings', {
                'email_notifications': True,
                'application_confirmations': True,
                'response_alerts': True,
                'weekly_summary': True
            })
            
            # Process privacy settings
            privacy_settings = preferences.get('privacy_settings', {
                'data_retention_days': 365,
                'share_analytics': False,
                'encrypt_sensitive_data': True,
                'audit_trail': True
            })
            
            user_preferences = UserPreferences(
                job_preferences=job_preferences,
                location_preferences=location_preferences,
                salary_expectations=salary_expectations,
                platform_preferences=platform_preferences,
                automation_settings=automation_settings,
                notification_settings=notification_settings,
                privacy_settings=privacy_settings
            )
            
            self.logger.info("User preferences processed successfully")
            return user_preferences
            
        except Exception as e:
            self.logger.error(f"Failed to process user preferences: {e}")
            raise
    
    async def _process_platform_credentials(self,
                                          credentials: List[Dict[str, Any]],
                                          configuration_id: str) -> List[PlatformCredentials]:
        """Process and encrypt platform credentials."""
        try:
            processed_credentials = []
            
            for cred in credentials:
                platform = cred.get('platform', '').lower()
                username = cred.get('username', '')
                password = cred.get('password', '')
                credential_type = cred.get('type', 'login_password')
                
                # Validate platform
                supported_platforms = self.validation_rules['platform_credentials']['supported_platforms']
                if platform not in supported_platforms:
                    self.logger.warning(f"Unsupported platform: {platform}")
                    continue
                
                # Validate required fields
                if not username or not password:
                    raise ValueError(f"Missing credentials for platform: {platform}")
                
                # Encrypt credential (simulate - would use SecurityAgent in production)
                if self.enable_encryption:
                    encrypted_credential_id = await self._encrypt_credential(
                        password, configuration_id, platform
                    )
                else:
                    encrypted_credential_id = f"unencrypted_{uuid.uuid4()}"
                
                # Process additional data
                additional_data = {
                    'login_url': cred.get('login_url'),
                    'security_questions': cred.get('security_questions', {}),
                    'backup_codes': cred.get('backup_codes', []),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
                platform_cred = PlatformCredentials(
                    platform=platform,
                    username=username,
                    encrypted_credential_id=encrypted_credential_id,
                    credential_type=credential_type,
                    two_factor_enabled=cred.get('two_factor_enabled', False),
                    additional_data=additional_data,
                    created_at=datetime.now(timezone.utc),
                    expires_at=None  # Could set expiration based on platform policy
                )
                
                processed_credentials.append(platform_cred)
            
            self.logger.info(f"Processed {len(processed_credentials)} platform credentials")
            return processed_credentials
            
        except Exception as e:
            self.logger.error(f"Failed to process platform credentials: {e}")
            raise
    
    async def _process_style_guide(self, style_input: Dict[str, Any]) -> StyleGuide:
        """Process style guide and branding information."""
        try:
            # Validate tone
            brand_voice = style_input.get('brand_voice', 'professional')
            writing_tone = style_input.get('writing_tone', 'professional')
            
            supported_tones = self.validation_rules['style_guide']['supported_tones']
            if writing_tone not in supported_tones:
                self.logger.warning(f"Unsupported tone: {writing_tone}, using 'professional'")
                writing_tone = 'professional'
            
            # Validate language
            preferred_language = style_input.get('preferred_language', 'en')
            supported_languages = self.validation_rules['style_guide']['supported_languages']
            if preferred_language not in supported_languages:
                self.logger.warning(f"Unsupported language: {preferred_language}, using 'en'")
                preferred_language = 'en'
            
            # Process formatting preferences
            formatting_preferences = style_input.get('formatting_preferences', {
                'font_family': 'Arial, sans-serif',
                'font_size': '11pt',
                'line_spacing': '1.2',
                'margins': 'standard',
                'color_scheme': 'professional'
            })
            
            # Process company values
            company_values = style_input.get('company_values', [])
            if not isinstance(company_values, list):
                company_values = []
            
            # Process personal brand
            personal_brand = style_input.get('personal_brand', {
                'key_strengths': [],
                'unique_value_proposition': '',
                'career_objective': '',
                'personal_mission': ''
            })
            
            # Process custom templates
            custom_templates = style_input.get('custom_templates', {})
            max_template_size = self.validation_rules['style_guide']['max_template_size']
            
            for template_name, template_content in custom_templates.items():
                if len(template_content) > max_template_size:
                    self.logger.warning(f"Template {template_name} exceeds size limit, truncating")
                    custom_templates[template_name] = template_content[:max_template_size]
            
            style_guide = StyleGuide(
                brand_voice=brand_voice,
                writing_tone=writing_tone,
                preferred_language=preferred_language,
                formatting_preferences=formatting_preferences,
                company_values=company_values,
                personal_brand=personal_brand,
                custom_templates=custom_templates
            )
            
            self.logger.info("Style guide processed successfully")
            return style_guide
            
        except Exception as e:
            self.logger.error(f"Failed to process style guide: {e}")
            raise
    
    async def _process_cover_letter_template(self, template_input: Union[str, Dict[str, Any]]) -> str:
        """Process cover letter template."""
        try:
            if isinstance(template_input, str):
                template_content = template_input
            elif isinstance(template_input, dict):
                template_content = template_input.get('content', '')
            else:
                raise ValueError("Invalid template input format")
            
            # Validate template content
            if not template_content.strip():
                raise ValueError("Empty cover letter template")
            
            max_size = self.validation_rules['style_guide']['max_template_size']
            if len(template_content) > max_size:
                self.logger.warning(f"Cover letter template exceeds size limit, truncating")
                template_content = template_content[:max_size]
            
            # Basic template validation (check for placeholder variables)
            required_placeholders = ['{company_name}', '{position_title}']
            missing_placeholders = [p for p in required_placeholders if p not in template_content]
            
            if missing_placeholders:
                self.logger.warning(f"Template missing recommended placeholders: {missing_placeholders}")
            
            self.logger.info("Cover letter template processed successfully")
            return template_content
            
        except Exception as e:
            self.logger.error(f"Failed to process cover letter template: {e}")
            raise
    
    async def _validate_against_schema(self, data: Dict[str, Any], schema_name: str):
        """Validate data against JSON schema."""
        try:
            if schema_name not in self.schema_definitions:
                raise ValueError(f"Schema not found: {schema_name}")
            
            schema = self.schema_definitions[schema_name]
            
            # Basic schema validation (would use jsonschema library in production)
            if 'required' in schema:
                for required_field in schema['required']:
                    if required_field not in data:
                        raise ValueError(f"Missing required field: {required_field}")
            
            self.logger.debug(f"Data validated against schema: {schema_name}")
            
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            raise
    
    def _create_default_preferences(self) -> UserPreferences:
        """Create default user preferences."""
        return UserPreferences(
            job_preferences={
                'job_type': 'full_time',
                'industries': [],
                'experience_level': 'mid_level',
                'company_size': ['startup', 'medium', 'large']
            },
            location_preferences={
                'preferred_locations': ['remote'],
                'remote_ok': True,
                'relocation_ok': False,
                'travel_ok': False
            },
            salary_expectations={
                'min_salary': 50000,
                'max_salary': 150000,
                'currency': 'USD',
                'salary_type': 'annual'
            },
            platform_preferences={
                'preferred_platforms': ['linkedin', 'indeed'],
                'auto_apply': False,
                'daily_application_limit': 10,
                'application_schedule': 'business_hours'
            },
            automation_settings={
                'auto_cover_letter': True,
                'auto_follow_up': False,
                'personalization_level': 'standard',
                'quality_over_quantity': True
            },
            notification_settings={
                'email_notifications': True,
                'application_confirmations': True,
                'response_alerts': True,
                'weekly_summary': True
            },
            privacy_settings={
                'data_retention_days': 365,
                'share_analytics': False,
                'encrypt_sensitive_data': True,
                'audit_trail': True
            }
        )
    
    async def _encrypt_credential(self, credential: str, configuration_id: str, platform: str) -> str:
        """Encrypt credential and return identifier."""
        # Simulate encryption process (would integrate with SecurityAgent)
        credential_hash = hashlib.sha256(f"{credential}{configuration_id}{platform}".encode()).hexdigest()
        encrypted_id = f"encrypted_{credential_hash[:16]}"
        
        # In production, this would call SecurityAgent.store_credential()
        self.logger.debug(f"Credential encrypted for platform: {platform}")
        return encrypted_id
    
    async def _scan_file_security(self, file_content: bytes, file_type: FileType) -> List[str]:
        """Basic security scan for uploaded files."""
        security_issues = []
        
        try:
            # Check file size (already done, but double-check for security)
            if len(file_content) > 50 * 1024 * 1024:  # 50MB absolute limit
                security_issues.append("File size exceeds security limits")
            
            # Basic malware signature detection (simplified)
            malware_signatures = [
                b'eval(',
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'onload=',
                b'onerror='
            ]
            
            for signature in malware_signatures:
                if signature in file_content.lower():
                    security_issues.append(f"Potentially malicious content detected")
                    break
            
            # File type consistency check
            if file_type in [FileType.PDF, FileType.DOCX, FileType.DOC]:
                # Check file header matches extension
                pdf_header = file_content[:4] == b'%PDF'
                docx_header = file_content[:2] == b'PK' and b'word/' in file_content[:1000]
                
                if file_type == FileType.PDF and not pdf_header:
                    security_issues.append("File header doesn't match PDF format")
                elif file_type in [FileType.DOCX, FileType.DOC] and not docx_header and not file_content.startswith(b'\xd0\xcf\x11\xe0'):
                    security_issues.append("File header doesn't match document format")
            
        except Exception as e:
            security_issues.append(f"Security scan error: {str(e)}")
        
        return security_issues
    
    async def _create_audit_log(self,
                              configuration_id: str,
                              operation: str,
                              success: bool,
                              details: str = None):
        """Create audit log entry."""
        if not self.audit_logging:
            return
        
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'configuration_id': configuration_id,
            'operation': operation,
            'success': success,
            'details': details,
            'agent': 'ConfigurationAgent'
        }
        
        # In production, this would write to a secure audit log
        self.logger.info(f"Audit: {operation} - {'SUCCESS' if success else 'FAILED'}")
    
    async def get_configuration(self, configuration_id: str) -> Optional[ConfigurationPackage]:
        """Retrieve configuration by ID."""
        return self.configurations.get(configuration_id)
    
    async def list_configurations(self, user_id: str = None) -> List[ConfigurationPackage]:
        """List configurations, optionally filtered by user."""
        if user_id:
            return [config for config in self.configurations.values() if config.user_id == user_id]
        return list(self.configurations.values())
    
    async def delete_configuration(self, configuration_id: str) -> bool:
        """Delete configuration and associated data."""
        try:
            if configuration_id in self.configurations:
                config = self.configurations[configuration_id]
                
                # Audit logging
                await self._create_audit_log(configuration_id, "configuration_deleted", True)
                
                del self.configurations[configuration_id]
                self.logger.info(f"Configuration deleted: {configuration_id}")
                return True
            
            return False
            
        except Exception as e:
            await self._create_audit_log(configuration_id, "configuration_delete_failed", False, str(e))
            self.logger.error(f"Failed to delete configuration: {e}")
            return False
    
    def get_routing_instructions(self, configuration: ConfigurationPackage) -> Dict[str, List[str]]:
        """Get routing instructions for downstream agents."""
        return configuration.routing_instructions
    
    def get_processing_flags(self, configuration: ConfigurationPackage) -> Dict[str, bool]:
        """Get processing flags for workflow optimization."""
        return configuration.processing_flags
    
    async def export_configuration(self, configuration_id: str, format_type: str = "json") -> Optional[str]:
        """Export configuration in specified format."""
        try:
            config = self.configurations.get(configuration_id)
            if not config:
                return None
            
            if format_type == "json":
                # Convert to serializable format
                config_dict = asdict(config)
                
                # Handle datetime and enum serialization
                def serialize_objects(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, Enum):
                        return obj.value
                    elif hasattr(obj, '__dict__'):
                        return obj.__dict__
                    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
                
                return json.dumps(config_dict, default=serialize_objects, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return None

if __name__ == "__main__":
    async def demo():
        """Demonstration of ConfigurationAgent capabilities."""
        agent = ConfigurationAgent(validation_level=ValidationLevel.STANDARD)
        
        # Sample user input (using base64 data instead of file path for demo)
        sample_pdf_content = b"%PDF-1.4 Sample resume content for John Doe" + b"x" * 500  # Simulate PDF content
        sample_pdf_b64 = base64.b64encode(sample_pdf_content).decode('utf-8')
        
        user_input = {
            'resume_file': {
                'name': 'john_doe_resume.pdf',
                'path': None,  # Using base64 data instead
                'data': sample_pdf_b64
            },
            'user_preferences': {
                'job_preferences': {
                    'job_type': 'full_time',
                    'industries': ['technology', 'finance'],
                    'experience_level': 'senior'
                },
                'location_preferences': {
                    'preferred_locations': ['San Francisco', 'New York', 'Remote'],
                    'remote_ok': True,
                    'relocation_ok': False
                },
                'salary_expectations': {
                    'min_salary': 120000,
                    'max_salary': 180000,
                    'currency': 'USD',
                    'salary_type': 'annual'
                }
            },
            'platform_credentials': [
                {
                    'platform': 'linkedin',
                    'username': 'john.doe@email.com',
                    'password': 'secure_password_123',
                    'two_factor_enabled': True
                }
            ],
            'style_guide': {
                'brand_voice': 'professional',
                'writing_tone': 'confident',
                'preferred_language': 'en',
                'company_values': ['innovation', 'collaboration', 'growth']
            }
        }
        
        print("🎯 ConfigurationAgent Demo")
        print("=" * 50)
        
        try:
            # Process user input
            config = await agent.process_user_input(user_input, user_id="demo_user_123")
            
            print(f"✅ Configuration created: {config.configuration_id}")
            print(f"📄 Resume file: {config.resume_file.file_name if config.resume_file else 'None'}")
            print(f"🎯 Job preferences: {config.user_preferences.job_preferences['job_type']}")
            print(f"🔐 Credentials: {len(config.platform_credentials)} platforms")
            print(f"🎨 Style guide: {config.style_guide.writing_tone if config.style_guide else 'None'}")
            
            print(f"\n🛤️  Routing Instructions:")
            for agent_name, operations in config.routing_instructions.items():
                print(f"   • {agent_name}: {', '.join(operations)}")
            
            print(f"\n🏃 Processing Flags:")
            for flag, value in config.processing_flags.items():
                print(f"   • {flag}: {value}")
            
            # Export configuration
            exported = await agent.export_configuration(config.configuration_id)
            if exported:
                print(f"\n📦 Configuration exported successfully ({len(exported)} characters)")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    asyncio.run(demo())