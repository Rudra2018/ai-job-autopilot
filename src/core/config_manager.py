#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Advanced Configuration Management System
Centralized, secure, and intelligent configuration management
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    name: str
    api_key: str = ""
    model: str = ""
    max_tokens: int = 150
    temperature: float = 0.3
    enabled: bool = True
    priority: int = 1  # 1 = highest priority

@dataclass
class AutomationConfig:
    max_applications_per_session: int = 20
    delay_between_applications: tuple = (30, 90)
    max_questions_per_form: int = 10
    max_retries: int = 3
    enable_resume_optimization: bool = True
    enable_duplicate_detection: bool = True
    enable_ai_answers: bool = True
    enable_stealth_mode: bool = True

@dataclass
class BrowserConfig:
    headless: bool = False
    user_agent: str = ""
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "en-US"
    timezone: str = "America/New_York"
    profile_name: str = "default"
    enable_extensions: bool = False

@dataclass
class NotificationConfig:
    email_enabled: bool = False
    email_address: str = ""
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    desktop_enabled: bool = True

@dataclass
class JobPreferences:
    titles: List[str] = None
    locations: List[str] = None
    keywords: List[str] = None
    exclude_companies: List[str] = None
    exclude_keywords: List[str] = None
    salary_minimum: int = 0
    salary_maximum: int = 0
    experience_level: str = "mid"
    remote_preference: str = "hybrid"
    travel_willingness: str = "minimal"

@dataclass
class SecurityConfig:
    encrypt_sensitive_data: bool = True
    password_hash_rounds: int = 100000
    session_timeout: int = 3600  # seconds
    max_login_attempts: int = 3
    require_2fa: bool = False
    backup_configs: bool = True

class AdvancedConfigManager:
    """Advanced configuration management with encryption and validation"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.main_config_path = self.config_dir / "main_config.yaml"
        self.sensitive_config_path = self.config_dir / "sensitive.enc"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self._encryption_key = None
        self._config_cache = {}
        
        # Default configurations
        self.default_config = self._create_default_config()
        
        # Load existing configuration
        self._load_configuration()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration structure"""
        return {
            "version": "2.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            
            "ai_providers": {
                "openai": asdict(AIProviderConfig(
                    name="openai",
                    model="gpt-3.5-turbo",
                    priority=1
                )),
                "anthropic": asdict(AIProviderConfig(
                    name="anthropic",
                    model="claude-3-haiku-20240307",
                    priority=2
                )),
                "google": asdict(AIProviderConfig(
                    name="google",
                    model="gemini-pro",
                    priority=3
                ))
            },
            
            "automation": asdict(AutomationConfig()),
            "browser": asdict(BrowserConfig()),
            "notifications": asdict(NotificationConfig()),
            "job_preferences": asdict(JobPreferences(
                titles=["Software Engineer", "Python Developer", "Full Stack Developer"],
                locations=["San Francisco, CA", "New York, NY", "Remote"],
                keywords=["python", "react", "javascript", "aws", "docker"]
            )),
            "security": asdict(SecurityConfig()),
            
            "linkedin": {
                "email": "",
                "password": "",  # Will be encrypted
                "profile_url": "",
                "premium_account": False
            },
            
            "email": {
                "address": "",
                "app_password": "",  # Will be encrypted
                "signature": "Best regards,\n{name}"
            },
            
            "user_profile": {
                "name": "",
                "email": "",
                "phone": "",
                "resume_path": "config/resume.pdf",
                "cover_letter_template": "config/cover_letter_template.txt",
                "linkedin_profile": "",
                "github_profile": "",
                "portfolio_url": ""
            }
        }
    
    def _get_encryption_key(self, password: str = None) -> bytes:
        """Generate or retrieve encryption key"""
        if self._encryption_key:
            return self._encryption_key
        
        # Use password or default for encryption
        if not password:
            password = os.getenv("CONFIG_PASSWORD", "ai_job_autopilot_default_key_2025")
        
        # Generate key from password
        password_bytes = password.encode()
        salt = b'ai_job_autopilot_salt_2025'  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        self._encryption_key = key
        return key
    
    def _encrypt_data(self, data: str, password: str = None) -> str:
        """Encrypt sensitive data"""
        key = self._get_encryption_key(password)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def _decrypt_data(self, encrypted_data: str, password: str = None) -> str:
        """Decrypt sensitive data"""
        try:
            key = self._get_encryption_key(password)
            fernet = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ""
    
    def _load_configuration(self):
        """Load configuration from files"""
        try:
            # Load main configuration
            if self.main_config_path.exists():
                with open(self.main_config_path, 'r') as f:
                    main_config = yaml.safe_load(f)
                    self._config_cache.update(main_config or {})
            else:
                self._config_cache = self.default_config.copy()
            
            # Load sensitive configuration
            self._load_sensitive_config()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._config_cache = self.default_config.copy()
    
    def _load_sensitive_config(self):
        """Load encrypted sensitive configuration"""
        try:
            if self.sensitive_config_path.exists():
                with open(self.sensitive_config_path, 'r') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self._decrypt_data(encrypted_data)
                if decrypted_data:
                    sensitive_config = json.loads(decrypted_data)
                    
                    # Merge sensitive data into main config
                    for section, data in sensitive_config.items():
                        if section in self._config_cache:
                            if isinstance(self._config_cache[section], dict):
                                self._config_cache[section].update(data)
                            else:
                                self._config_cache[section] = data
                        else:
                            self._config_cache[section] = data
        
        except Exception as e:
            logger.warning(f"Could not load sensitive configuration: {e}")
    
    def _save_configuration(self):
        """Save configuration to files"""
        try:
            # Update timestamp
            self._config_cache["updated_at"] = datetime.now().isoformat()
            
            # Create backup
            if self._config_cache.get("security", {}).get("backup_configs", True):
                self._create_backup()
            
            # Separate sensitive and non-sensitive data
            sensitive_data = {}
            non_sensitive_data = self._config_cache.copy()
            
            # Extract sensitive fields
            sensitive_fields = [
                ("linkedin", "password"),
                ("email", "app_password"),
                ("ai_providers", "*", "api_key")  # API keys in all providers
            ]
            
            for field_path in sensitive_fields:
                if len(field_path) == 2:
                    section, key = field_path
                    if section in non_sensitive_data and key in non_sensitive_data[section]:
                        if section not in sensitive_data:
                            sensitive_data[section] = {}
                        sensitive_data[section][key] = non_sensitive_data[section][key]
                        non_sensitive_data[section][key] = "[ENCRYPTED]"
                
                elif len(field_path) == 3 and field_path[1] == "*":
                    section, wildcard, key = field_path
                    if section in non_sensitive_data:
                        if section not in sensitive_data:
                            sensitive_data[section] = {}
                        for subsection, subdata in non_sensitive_data[section].items():
                            if isinstance(subdata, dict) and key in subdata:
                                if subsection not in sensitive_data[section]:
                                    sensitive_data[section][subsection] = {}
                                sensitive_data[section][subsection][key] = subdata[key]
                                non_sensitive_data[section][subsection][key] = "[ENCRYPTED]"
            
            # Save non-sensitive configuration
            with open(self.main_config_path, 'w') as f:
                yaml.dump(non_sensitive_data, f, default_flow_style=False, sort_keys=False)
            
            # Save encrypted sensitive configuration
            if sensitive_data:
                encrypted_data = self._encrypt_data(json.dumps(sensitive_data, indent=2))
                with open(self.sensitive_config_path, 'w') as f:
                    f.write(encrypted_data)
            
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def _create_backup(self):
        """Create configuration backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"config_backup_{timestamp}.yaml"
            
            # Save non-sensitive backup
            backup_data = {k: v for k, v in self._config_cache.items() if not self._is_sensitive_field(k)}
            
            with open(backup_path, 'w') as f:
                yaml.dump(backup_data, f, default_flow_style=False)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("config_backup_*.yaml"))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    old_backup.unlink()
            
            logger.info(f"Configuration backup created: {backup_path}")
            
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if a field contains sensitive data"""
        sensitive_keywords = ["password", "key", "token", "secret", "credential"]
        return any(keyword in field_name.lower() for keyword in sensitive_keywords)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'automation.max_applications')"""
        try:
            keys = key_path.split('.')
            value = self._config_cache
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.warning(f"Error getting config value '{key_path}': {e}")
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            config = self._config_cache
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the value
            config[keys[-1]] = value
            
            logger.info(f"Configuration updated: {key_path}")
            
        except Exception as e:
            logger.error(f"Error setting config value '{key_path}': {e}")
            raise
    
    def get_ai_provider_config(self, provider_name: str) -> Optional[AIProviderConfig]:
        """Get AI provider configuration"""
        provider_data = self.get(f"ai_providers.{provider_name}")
        if provider_data:
            return AIProviderConfig(**provider_data)
        return None
    
    def set_ai_provider_config(self, provider_name: str, config: AIProviderConfig):
        """Set AI provider configuration"""
        self.set(f"ai_providers.{provider_name}", asdict(config))
    
    def get_automation_config(self) -> AutomationConfig:
        """Get automation configuration"""
        automation_data = self.get("automation", {})
        return AutomationConfig(**automation_data)
    
    def set_automation_config(self, config: AutomationConfig):
        """Set automation configuration"""
        self.set("automation", asdict(config))
    
    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration"""
        browser_data = self.get("browser", {})
        return BrowserConfig(**browser_data)
    
    def set_browser_config(self, config: BrowserConfig):
        """Set browser configuration"""
        self.set("browser", asdict(config))
    
    def get_job_preferences(self) -> JobPreferences:
        """Get job preferences"""
        job_data = self.get("job_preferences", {})
        return JobPreferences(**job_data)
    
    def set_job_preferences(self, preferences: JobPreferences):
        """Set job preferences"""
        self.set("job_preferences", asdict(preferences))
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate configuration and return any issues"""
        issues = {}
        
        # Validate AI providers
        ai_providers = self.get("ai_providers", {})
        for provider, config in ai_providers.items():
            provider_issues = []
            
            if not config.get("api_key"):
                provider_issues.append("API key not configured")
            
            if not config.get("model"):
                provider_issues.append("Model not specified")
            
            if config.get("max_tokens", 0) <= 0:
                provider_issues.append("Invalid max_tokens value")
            
            if provider_issues:
                issues[f"ai_providers.{provider}"] = provider_issues
        
        # Validate automation settings
        automation = self.get("automation", {})
        automation_issues = []
        
        if automation.get("max_applications_per_session", 0) <= 0:
            automation_issues.append("Invalid max_applications_per_session")
        
        delay_range = automation.get("delay_between_applications", (0, 0))
        if not isinstance(delay_range, (list, tuple)) or len(delay_range) != 2 or delay_range[0] >= delay_range[1]:
            automation_issues.append("Invalid delay_between_applications range")
        
        if automation_issues:
            issues["automation"] = automation_issues
        
        # Validate LinkedIn credentials
        linkedin = self.get("linkedin", {})
        linkedin_issues = []
        
        if not linkedin.get("email"):
            linkedin_issues.append("LinkedIn email not configured")
        
        if not linkedin.get("password"):
            linkedin_issues.append("LinkedIn password not configured")
        
        if linkedin_issues:
            issues["linkedin"] = linkedin_issues
        
        # Validate job preferences
        job_prefs = self.get("job_preferences", {})
        job_issues = []
        
        if not job_prefs.get("titles"):
            job_issues.append("No job titles specified")
        
        if not job_prefs.get("locations"):
            job_issues.append("No locations specified")
        
        if job_issues:
            issues["job_preferences"] = job_issues
        
        return issues
    
    def export_configuration(self, export_path: str, include_sensitive: bool = False) -> bool:
        """Export configuration to file"""
        try:
            export_data = self._config_cache.copy()
            
            if not include_sensitive:
                # Remove sensitive data
                sensitive_patterns = ["password", "key", "token", "secret"]
                export_data = self._remove_sensitive_data(export_data, sensitive_patterns)
            
            export_file = Path(export_path)
            
            if export_file.suffix.lower() == '.json':
                with open(export_file, 'w') as f:
                    json.dump(export_data, f, indent=2)
            else:
                with open(export_file, 'w') as f:
                    yaml.dump(export_data, f, default_flow_style=False)
            
            logger.info(f"Configuration exported to: {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_configuration(self, import_path: str, merge: bool = True) -> bool:
        """Import configuration from file"""
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                logger.error(f"Import file not found: {import_file}")
                return False
            
            # Load import data
            if import_file.suffix.lower() == '.json':
                with open(import_file, 'r') as f:
                    import_data = json.load(f)
            else:
                with open(import_file, 'r') as f:
                    import_data = yaml.safe_load(f)
            
            if merge:
                # Merge with existing configuration
                self._deep_merge(self._config_cache, import_data)
            else:
                # Replace configuration
                self._config_cache = import_data
            
            logger.info(f"Configuration imported from: {import_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False
    
    def _remove_sensitive_data(self, data: Dict, sensitive_patterns: List[str]) -> Dict:
        """Remove sensitive data from configuration"""
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                result[key] = "[REMOVED]"
            elif isinstance(value, dict):
                result[key] = self._remove_sensitive_data(value, sensitive_patterns)
            else:
                result[key] = value
        
        return result
    
    def _deep_merge(self, dict1: Dict, dict2: Dict):
        """Deep merge two dictionaries"""
        for key, value in dict2.items():
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                self._deep_merge(dict1[key], value)
            else:
                dict1[key] = value
    
    def save(self):
        """Save current configuration to files"""
        self._save_configuration()
    
    def reload(self):
        """Reload configuration from files"""
        self._load_configuration()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config_cache = self.default_config.copy()
        logger.info("Configuration reset to defaults")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display"""
        return {
            "version": self.get("version"),
            "created_at": self.get("created_at"),
            "updated_at": self.get("updated_at"),
            "ai_providers_count": len(self.get("ai_providers", {})),
            "job_titles_count": len(self.get("job_preferences.titles", [])),
            "locations_count": len(self.get("job_preferences.locations", [])),
            "automation_enabled": self.get("automation.enable_ai_answers", False),
            "linkedin_configured": bool(self.get("linkedin.email")),
            "config_valid": len(self.validate_configuration()) == 0
        }


def main():
    """Demo the Advanced Config Manager"""
    print("🤖 Advanced Configuration Manager Demo")
    print("=" * 50)
    
    # Initialize config manager
    config_manager = AdvancedConfigManager()
    
    # Display current configuration summary
    print("\n📊 Configuration Summary:")
    summary = config_manager.get_config_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Test configuration validation
    print("\n🔍 Configuration Validation:")
    issues = config_manager.validate_configuration()
    
    if issues:
        print("   ⚠️ Issues found:")
        for section, section_issues in issues.items():
            print(f"     {section}:")
            for issue in section_issues:
                print(f"       - {issue}")
    else:
        print("   ✅ Configuration is valid!")
    
    # Test getting and setting values
    print("\n🧪 Testing Get/Set Operations:")
    
    # Get current max applications
    current_max = config_manager.get("automation.max_applications_per_session", 20)
    print(f"   Current max applications: {current_max}")
    
    # Set new value
    config_manager.set("automation.max_applications_per_session", 25)
    new_max = config_manager.get("automation.max_applications_per_session")
    print(f"   Updated max applications: {new_max}")
    
    # Test AI provider configuration
    print("\n🤖 AI Provider Configuration:")
    openai_config = config_manager.get_ai_provider_config("openai")
    if openai_config:
        print(f"   OpenAI Model: {openai_config.model}")
        print(f"   OpenAI Priority: {openai_config.priority}")
        print(f"   OpenAI Enabled: {openai_config.enabled}")
    
    # Save configuration
    print("\n💾 Saving configuration...")
    config_manager.save()
    print("   ✅ Configuration saved successfully!")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    main()