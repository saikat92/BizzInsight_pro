"""
Configuration Management Module for Business Intelligence System
Handles application settings, environment variables, and configuration persistence
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    type: str = "sqlite"
    path: str = "data/database/business.db"
    host: str = "localhost"
    port: int = 5432
    name: str = "business_intelligence"
    username: str = ""
    password: str = ""
    pool_size: int = 5
    echo_sql: bool = False
    auto_backup: bool = True
    backup_interval_hours: int = 24
    
    def get_connection_string(self) -> str:
        """Get database connection string"""
        if self.type == "sqlite":
            return f"sqlite:///{self.path}"
        elif self.type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.type == "mysql":
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
        else:
            raise ValueError(f"Unsupported database type: {self.type}")


@dataclass
class UIConfig:
    """User Interface configuration settings"""
    theme: str = "dark"
    font_family: str = "Segoe UI"
    font_size: int = 11
    window_width: int = 1400
    window_height: int = 800
    max_recent_files: int = 10
    language: str = "en"
    animations_enabled: bool = True
    tooltips_enabled: bool = True
    confirm_exit: bool = True
    auto_save_interval: int = 300  # seconds
    
    def get_font_spec(self) -> Dict[str, Any]:
        """Get font specification dictionary"""
        return {
            "family": self.font_family,
            "size": self.font_size,
            "h1": {"size": font_size + 17, "weight": "bold"},
            "h2": {"size": font_size + 9, "weight": "bold"},
            "h3": {"size": font_size + 3, "weight": "bold"},
            "body": {"size": font_size, "weight": "normal"},
            "small": {"size": font_size - 1, "weight": "normal"},
        }


@dataclass
class MLConfig:
    """Machine Learning configuration settings"""
    model_storage_path: str = "src/ml/models/"
    training_data_path: str = "data/ml/training/"
    test_size: float = 0.2
    random_state: int = 42
    cross_validation_folds: int = 5
    auto_retrain_days: int = 7
    default_algorithm: str = "random_forest"
    feature_scaling: bool = True
    hyperparameter_tuning: bool = True
    
    # Algorithm-specific configurations
    random_forest: Dict[str, Any] = field(default_factory=lambda: {
        "n_estimators": 100,
        "max_depth": None,
        "min_samples_split": 2,
    })
    
    linear_regression: Dict[str, Any] = field(default_factory=lambda: {
        "fit_intercept": True,
    })
    
    gradient_boosting: Dict[str, Any] = field(default_factory=lambda: {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 3,
    })


@dataclass
class ReportConfig:
    """Report generation configuration"""
    default_format: str = "pdf"
    output_directory: str = "reports/"
    company_name: str = "Business Intelligence Inc."
    company_logo: Optional[str] = None
    header_color: str = "#1a237e"
    footer_text: str = "Confidential - For Internal Use Only"
    auto_generate_daily: bool = False
    include_charts: bool = True
    include_recommendations: bool = True
    
    # Email configuration for report distribution
    email_enabled: bool = False
    email_recipients: list = field(default_factory=list)
    email_subject: str = "Business Intelligence Report"
    email_body_template: str = "Attached is the latest business intelligence report."


@dataclass
class SecurityConfig:
    """Security and authentication configuration"""
    encryption_enabled: bool = True
    encryption_key_path: str = "config/keys/"
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    password_policy: Dict[str, Any] = field(default_factory=lambda: {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True,
    })
    
    # API security
    api_key_enabled: bool = False
    api_key_header: str = "X-API-Key"
    cors_allowed_origins: list = field(default_factory=lambda: ["http://localhost:3000"])


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    query_timeout_seconds: int = 30
    max_workers: int = 4
    batch_size: int = 1000
    compression_enabled: bool = True
    lazy_loading: bool = True
    
    # Memory management
    max_memory_mb: int = 1024
    auto_cleanup_interval_hours: int = 1


@dataclass
class NotificationConfig:
    """Notification and alert configuration"""
    enabled: bool = True
    sound_enabled: bool = True
    desktop_notifications: bool = True
    email_notifications: bool = False
    
    # Alert thresholds
    sales_alert_threshold: float = 10000.0
    inventory_alert_threshold: int = 10
    error_alert_threshold: int = 5
    
    # Notification channels
    slack_webhook: Optional[str] = None
    teams_webhook: Optional[str] = None
    telegram_bot_token: Optional[str] = None


@dataclass
class ApplicationConfig:
    """Main application configuration container"""
    # Core configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    reports: ReportConfig = field(default_factory=ReportConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    
    # Application metadata
    app_name: str = "Business Intelligence System"
    app_version: str = "1.0.0"
    app_description: str = "Comprehensive Business Intelligence Platform"
    developer_mode: bool = False
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Path configurations
    base_dir: str = field(default_factory=lambda: os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    data_dir: str = "data/"
    logs_dir: str = "logs/"
    temp_dir: str = "temp/"
    
    def __post_init__(self):
        """Initialize paths relative to base directory"""
        # Convert relative paths to absolute
        self.base_dir = os.path.abspath(self.base_dir)
        self.data_dir = os.path.join(self.base_dir, self.data_dir)
        self.logs_dir = os.path.join(self.base_dir, self.logs_dir)
        self.temp_dir = os.path.join(self.base_dir, self.temp_dir)
        
        # Update nested paths
        self.database.path = os.path.join(self.base_dir, self.database.path)
        self.ml.model_storage_path = os.path.join(self.base_dir, self.ml.model_storage_path)
        self.ml.training_data_path = os.path.join(self.base_dir, self.ml.training_data_path)
        self.reports.output_directory = os.path.join(self.base_dir, self.reports.output_directory)
        self.security.encryption_key_path = os.path.join(self.base_dir, self.security.encryption_key_path)


class ConfigManager:
    """
    Configuration manager for loading, saving, and managing application settings
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Configuration file name (supports .json, .yaml, .yml)
        """
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_file = os.path.join(self.base_dir, config_file)
        self.config: Optional[ApplicationConfig] = None
        
        # Create necessary directories
        self._create_directories()
        
        # Load configuration
        self.load_config()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            os.path.join(self.base_dir, "data"),
            os.path.join(self.base_dir, "logs"),
            os.path.join(self.base_dir, "temp"),
            os.path.join(self.base_dir, "config"),
            os.path.join(self.base_dir, "reports"),
            os.path.join(self.base_dir, "src/ml/models"),
            os.path.join(self.base_dir, "data/ml/training"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _config_to_dict(self, config: ApplicationConfig) -> Dict[str, Any]:
        """Convert config object to dictionary"""
        config_dict = asdict(config)
        
        # Remove base_dir from serialization to avoid absolute paths
        if 'base_dir' in config_dict:
            del config_dict['base_dir']
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> ApplicationConfig:
        """Convert dictionary to config object"""
        # Handle nested configurations
        db_config = DatabaseConfig(**config_dict.get('database', {}))
        ui_config = UIConfig(**config_dict.get('ui', {}))
        ml_config = MLConfig(**config_dict.get('ml', {}))
        report_config = ReportConfig(**config_dict.get('reports', {}))
        security_config = SecurityConfig(**config_dict.get('security', {}))
        performance_config = PerformanceConfig(**config_dict.get('performance', {}))
        notification_config = NotificationConfig(**config_dict.get('notifications', {}))
        
        # Create main config
        app_config = ApplicationConfig(
            database=db_config,
            ui=ui_config,
            ml=ml_config,
            reports=report_config,
            security=security_config,
            performance=performance_config,
            notifications=notification_config,
            app_name=config_dict.get('app_name', 'Business Intelligence System'),
            app_version=config_dict.get('app_version', '1.0.0'),
            app_description=config_dict.get('app_description', 'Comprehensive Business Intelligence Platform'),
            developer_mode=config_dict.get('developer_mode', False),
            debug_mode=config_dict.get('debug_mode', False),
            log_level=config_dict.get('log_level', 'INFO'),
        )
        
        return app_config
    
    def load_config(self) -> ApplicationConfig:
        """
        Load configuration from file or create default
        
        Returns:
            ApplicationConfig: Loaded configuration
        """
        try:
            if os.path.exists(self.config_file):
                # Determine file type
                if self.config_file.endswith(('.yaml', '.yml')):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config_dict = yaml.safe_load(f)
                else:  # Assume JSON
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config_dict = json.load(f)
                
                self.config = self._dict_to_config(config_dict)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                # Create default configuration
                self.config = ApplicationConfig()
                self.save_config()
                logger.info(f"Created default configuration at {self.config_file}")
        
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Fallback to default
            self.config = ApplicationConfig()
        
        return self.config
    
    def save_config(self, config: Optional[ApplicationConfig] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration to save (uses current if None)
        
        Returns:
            bool: True if successful
        """
        try:
            if config is None:
                config = self.config
            
            config_dict = self._config_to_dict(config)
            
            # Determine file type
            if self.config_file.endswith(('.yaml', '.yml')):
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            else:  # Save as JSON
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_config(self) -> ApplicationConfig:
        """Get current configuration"""
        if self.config is None:
            self.load_config()
        return self.config
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """
        Update a specific configuration value
        
        Args:
            section: Configuration section (e.g., 'database', 'ui')
            key: Configuration key
            value: New value
        
        Returns:
            bool: True if successful
        """
        try:
            config_dict = self._config_to_dict(self.config)
            
            if section in config_dict:
                if key in config_dict[section]:
                    config_dict[section][key] = value
                    
                    # Update config object
                    self.config = self._dict_to_config(config_dict)
                    
                    # Save to file
                    self.save_config()
                    logger.info(f"Updated config: {section}.{key} = {value}")
                    return True
                else:
                    logger.error(f"Key '{key}' not found in section '{section}'")
            else:
                logger.error(f"Section '{section}' not found in configuration")
            
            return False
        
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self.config = ApplicationConfig()
            self.save_config()
            logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting configuration: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to a different location
        
        Args:
            export_path: Path to export configuration
        
        Returns:
            bool: True if successful
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            config_dict = self._config_to_dict(self.config)
            
            if export_path.endswith(('.yaml', '.yml')):
                with open(export_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            else:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a file
        
        Args:
            import_path: Path to configuration file
        
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(import_path):
                logger.error(f"Import file not found: {import_path}")
                return False
            
            # Load imported config
            if import_path.endswith(('.yaml', '.yml')):
                with open(import_path, 'r', encoding='utf-8') as f:
                    config_dict = yaml.safe_load(f)
            else:
                with open(import_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
            
            # Validate structure
            required_sections = ['database', 'ui', 'ml']
            for section in required_sections:
                if section not in config_dict:
                    logger.error(f"Invalid configuration: missing '{section}' section")
                    return False
            
            # Update current config
            self.config = self._dict_to_config(config_dict)
            self.save_config()
            
            logger.info(f"Configuration imported from {import_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get or create global configuration manager
    
    Returns:
        ConfigManager: Global configuration manager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> ApplicationConfig:
    """
    Get current application configuration
    
    Returns:
        ApplicationConfig: Current configuration
    """
    return get_config_manager().get_config()


def save_config(config: Optional[ApplicationConfig] = None) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration to save (uses current if None)
    
    Returns:
        bool: True if successful
    """
    return get_config_manager().save_config(config)


def update_config(section: str, key: str, value: Any) -> bool:
    """
    Update a specific configuration value
    
    Args:
        section: Configuration section
        key: Configuration key
        value: New value
    
    Returns:
        bool: True if successful
    """
    return get_config_manager().update_config(section, key, value)


def load_config() -> ApplicationConfig:
    """
    Load configuration from file
    
    Returns:
        ApplicationConfig: Loaded configuration
    """
    return get_config_manager().load_config()


def validate_config() -> Dict[str, Any]:
    """
    Validate current configuration
    
    Returns:
        Dict[str, Any]: Validation results with issues
    """
    config = get_config()
    issues = {}
    
    # Check database configuration
    if config.database.type == "sqlite":
        db_dir = os.path.dirname(config.database.path)
        if not os.path.exists(db_dir):
            issues['database'] = f"Database directory does not exist: {db_dir}"
    
    # Check file paths
    paths_to_check = [
        ("logs_dir", config.logs_dir),
        ("temp_dir", config.temp_dir),
        ("ml_models", config.ml.model_storage_path),
    ]
    
    for name, path in paths_to_check:
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                issues[name] = f"Cannot create directory {path}: {e}"
    
    # Validate ML configuration
    if config.ml.test_size <= 0 or config.ml.test_size >= 1:
        issues['ml'] = "test_size must be between 0 and 1"
    
    return issues


# Convenience functions for common configuration access
def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().database


def get_ui_config() -> UIConfig:
    """Get UI configuration"""
    return get_config().ui


def get_ml_config() -> MLConfig:
    """Get ML configuration"""
    return get_config().ml


def get_report_config() -> ReportConfig:
    """Get report configuration"""
    return get_config().reports


def create_default_config_file() -> str:
    """
    Create a default configuration file
    
    Returns:
        str: Path to created configuration file
    """
    config = ApplicationConfig()
    config_dict = asdict(config)
    
    # Remove absolute paths
    if 'base_dir' in config_dict:
        del config_dict['base_dir']
    
    config_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config.json"
    )
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=4, ensure_ascii=False)
    
    return config_file


if __name__ == "__main__":
    # Test the configuration module
    config = load_config()
    print(f"App Name: {config.app_name}")
    print(f"Version: {config.app_version}")
    print(f"Database: {config.database.type} at {config.database.path}")
    print(f"UI Theme: {config.ui.theme}")
    
    # Validate configuration
    issues = validate_config()
    if issues:
        print("Configuration issues found:")
        for key, issue in issues.items():
            print(f"  {key}: {issue}")
    else:
        print("Configuration is valid!")