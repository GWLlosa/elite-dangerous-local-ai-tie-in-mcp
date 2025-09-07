"""Configuration Management

Handles configuration loading, validation, and environment variable support
for the Elite Dangerous Local AI Tie-In MCP server.
"""

import logging
import os
import platform
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class EliteConfig(BaseSettings):
    """
    Configuration management for Elite Dangerous MCP server.
    
    Supports:
    - Environment variable loading with ELITE_ prefix
    - Platform-specific default paths
    - Path validation and existence checking
    - Configuration file loading and saving
    """
    
    model_config = SettingsConfigDict(
        env_prefix="ELITE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Core paths
    journal_path: Path = Field(
        default_factory=lambda: _get_default_journal_path(),
        description="Path to Elite Dangerous journal directory"
    )
    edcopilot_path: Path = Field(
        default=Path("C:/Utilities/EDCoPilot/User custom files"),
        description="Path to EDCoPilot custom files directory"
    )
    
    # Server configuration
    debug: bool = Field(default=False, description="Enable debug logging")
    max_recent_events: int = Field(default=1000, description="Maximum recent events to store")
    server_port: int = Field(default=3000, description="MCP server port (if needed)")
    
    # Monitoring configuration
    file_check_interval: float = Field(default=1.0, description="Journal file check interval (seconds)")
    status_update_interval: float = Field(default=2.0, description="Status.json check interval (seconds)")
    
    # EDCoPilot generation settings
    backup_custom_files: bool = Field(default=True, description="Backup EDCoPilot files before overwriting")
    max_backup_files: int = Field(default=5, description="Maximum backup files to keep")
    
    # Advanced settings
    journal_encoding: str = Field(default="utf-8", description="Journal file encoding")
    async_mode: bool = Field(default=True, description="Use async file operations")
    
    @field_validator('journal_path', mode='before')
    @classmethod
    def validate_journal_path(cls, v):
        """Validate and resolve journal path."""
        if isinstance(v, str):
            v = Path(v).expanduser().resolve()
        elif isinstance(v, Path):
            v = v.expanduser().resolve()
        else:
            raise ValueError("journal_path must be a string or Path object")
        
        logger.debug(f"Validated journal path: {v}")
        return v
    
    @field_validator('edcopilot_path', mode='before')
    @classmethod
    def validate_edcopilot_path(cls, v):
        """Validate and resolve EDCoPilot path."""
        if isinstance(v, str):
            v = Path(v).expanduser().resolve()
        elif isinstance(v, Path):
            v = v.expanduser().resolve()
        else:
            raise ValueError("edcopilot_path must be a string or Path object")
        
        logger.debug(f"Validated EDCoPilot path: {v}")
        return v
    
    @field_validator('max_recent_events')
    @classmethod
    def validate_max_events(cls, v):
        """Validate max recent events is reasonable."""
        if v < 10:
            raise ValueError("max_recent_events must be at least 10")
        if v > 100000:
            raise ValueError("max_recent_events cannot exceed 100,000")
        return v
    
    @field_validator('file_check_interval', 'status_update_interval')
    @classmethod
    def validate_intervals(cls, v):
        """Validate interval values are reasonable."""
        if v < 0.1:
            raise ValueError("Interval must be at least 0.1 seconds")
        if v > 60.0:
            raise ValueError("Interval cannot exceed 60 seconds")
        return v
    
    def validate_paths(self) -> dict:
        """
        Validate that configured paths exist and are accessible.
        
        Returns:
            dict: Validation results with status and messages
        """
        results = {
            'journal_path': {'exists': False, 'readable': False, 'writable': False, 'message': ''},
            'edcopilot_path': {'exists': False, 'readable': False, 'writable': False, 'message': ''}
        }
        
        # Validate journal path
        try:
            if self.journal_path.exists():
                results['journal_path']['exists'] = True
                results['journal_path']['readable'] = os.access(self.journal_path, os.R_OK)
                results['journal_path']['message'] = "Journal path exists and accessible"
                logger.info(f"Journal path validated: {self.journal_path}")
            else:
                results['journal_path']['message'] = f"Journal path does not exist: {self.journal_path}"
                logger.warning(f"Journal path not found: {self.journal_path}")
        except Exception as e:
            results['journal_path']['message'] = f"Error accessing journal path: {e}"
            logger.error(f"Journal path validation error: {e}")
        
        # Validate EDCoPilot path
        try:
            if self.edcopilot_path.exists():
                results['edcopilot_path']['exists'] = True
                results['edcopilot_path']['readable'] = os.access(self.edcopilot_path, os.R_OK)
                results['edcopilot_path']['writable'] = os.access(self.edcopilot_path, os.W_OK)
                results['edcopilot_path']['message'] = "EDCoPilot path exists and accessible"
                logger.info(f"EDCoPilot path validated: {self.edcopilot_path}")
            else:
                # Try to create EDCoPilot directory if it doesn't exist
                try:
                    self.edcopilot_path.mkdir(parents=True, exist_ok=True)
                    results['edcopilot_path']['exists'] = True
                    results['edcopilot_path']['writable'] = True
                    results['edcopilot_path']['message'] = "EDCoPilot path created successfully"
                    logger.info(f"Created EDCoPilot directory: {self.edcopilot_path}")
                except Exception as create_error:
                    results['edcopilot_path']['message'] = f"Cannot create EDCoPilot path: {create_error}"
                    logger.error(f"Failed to create EDCoPilot directory: {create_error}")
        except Exception as e:
            results['edcopilot_path']['message'] = f"Error accessing EDCoPilot path: {e}"
            logger.error(f"EDCoPilot path validation error: {e}")
        
        return results
    
    def load_from_file(self, config_file: Path) -> bool:
        """
        Load configuration from JSON file while preserving environment variable precedence.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            if not config_file.exists():
                logger.warning(f"Configuration file not found: {config_file}")
                return False
            
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Store current environment variable values to preserve precedence
            env_overrides = {}
            for field_name in self.model_fields.keys():
                env_var = f"ELITE_{field_name.upper()}"
                if env_var in os.environ:
                    env_overrides[field_name] = os.environ[env_var]
                    logger.debug(f"Preserving environment override: {field_name} = {env_overrides[field_name]}")
            
            # Update configuration with file data
            for key, value in config_data.items():
                if hasattr(self, key):
                    # Only update if not overridden by environment variable
                    if key not in env_overrides:
                        setattr(self, key, value)
                        logger.debug(f"Updated config from file: {key} = {value}")
                    else:
                        logger.debug(f"Skipping file value for {key}, environment variable takes precedence")
                else:
                    logger.warning(f"Unknown configuration key: {key}")
            
            # Re-apply environment variable overrides to ensure they take precedence
            for field_name, env_value in env_overrides.items():
                # Use pydantic's model reconstruction to apply proper validation
                current_value = getattr(self, field_name)
                logger.debug(f"Preserving environment override: {field_name} (keeping current value from env)")
            
            logger.info(f"Configuration loaded from: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
            return False
    
    def save_to_file(self, config_file: Path) -> bool:
        """
        Save current configuration to JSON file.
        
        Args:
            config_file: Path to save configuration
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure parent directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert configuration to dict for JSON serialization
            config_dict = {}
            for field_name, field_info in self.model_fields.items():
                value = getattr(self, field_name)
                if isinstance(value, Path):
                    config_dict[field_name] = str(value)
                else:
                    config_dict[field_name] = value
            
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_file}: {e}")
            return False
    
    def get_summary(self) -> dict:
        """
        Get a summary of current configuration.
        
        Returns:
            dict: Configuration summary
        """
        return {
            'journal_path': str(self.journal_path),
            'edcopilot_path': str(self.edcopilot_path),
            'debug': self.debug,
            'max_recent_events': self.max_recent_events,
            'file_check_interval': self.file_check_interval,
            'status_update_interval': self.status_update_interval,
            'backup_custom_files': self.backup_custom_files,
            'async_mode': self.async_mode,
            'platform': platform.system(),
            'python_version': platform.python_version()
        }


def _get_default_journal_path() -> Path:
    """
    Get platform-specific default Elite Dangerous journal path.
    
    Returns:
        Path: Default journal directory
    """
    system = platform.system().lower()
    
    if system == "windows":
        # Windows: %USERPROFILE%\\Saved Games\\Frontier Developments\\Elite Dangerous
        base_path = Path.home() / "Saved Games" / "Frontier Developments" / "Elite Dangerous"
    elif system == "darwin":  # macOS
        # macOS: ~/Library/Application Support/Frontier Developments/Elite Dangerous
        base_path = Path.home() / "Library" / "Application Support" / "Frontier Developments" / "Elite Dangerous"
    else:  # Linux and others
        # Linux: ~/.local/share/Frontier Developments/Elite Dangerous
        base_path = Path.home() / ".local" / "share" / "Frontier Developments" / "Elite Dangerous"
    
    logger.debug(f"Default journal path for {system}: {base_path}")
    return base_path


def load_config(config_file: Optional[Path] = None) -> EliteConfig:
    """
    Load configuration with optional file override.
    
    Args:
        config_file: Optional configuration file to load
        
    Returns:
        EliteConfig: Loaded configuration instance
    """
    try:
        # Create base configuration from environment and defaults
        config = EliteConfig()
        
        # Load from file if specified (environment variables will take precedence)
        if config_file and config_file.exists():
            config.load_from_file(config_file)
        
        # Validate paths
        validation_results = config.validate_paths()
        
        # Log validation summary
        for path_name, result in validation_results.items():
            if result['exists']:
                logger.info(f"✅ {path_name}: {result['message']}")
            else:
                logger.warning(f"⚠️  {path_name}: {result['message']}")
        
        logger.info("Configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


def create_sample_config(output_file: Path) -> bool:
    """
    Create a sample configuration file with documentation.
    
    Args:
        output_file: Path to save sample configuration
        
    Returns:
        bool: True if created successfully
    """
    try:
        sample_config = {
            "_comment": "Elite Dangerous Local AI Tie-In MCP Configuration",
            "_note": "All paths support environment variable expansion",
            "journal_path": str(_get_default_journal_path()),
            "edcopilot_path": "C:/Utilities/EDCoPilot/User custom files",
            "debug": False,
            "max_recent_events": 1000,
            "server_port": 3000,
            "file_check_interval": 1.0,
            "status_update_interval": 2.0,
            "backup_custom_files": True,
            "max_backup_files": 5,
            "journal_encoding": "utf-8",
            "async_mode": True,
            "_environment_variables": {
                "_note": "These can be set as environment variables with ELITE_ prefix",
                "ELITE_JOURNAL_PATH": "/path/to/elite/dangerous/journals",
                "ELITE_EDCOPILOT_PATH": "/path/to/edcopilot/custom/files",
                "ELITE_DEBUG": "true/false",
                "ELITE_MAX_RECENT_EVENTS": "1000"
            }
        }
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Sample configuration created: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create sample configuration: {e}")
        return False
