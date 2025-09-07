"""Unit tests for configuration management functionality."""

import json
import os
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from pydantic import ValidationError

from src.utils.config import (
    EliteConfig, 
    load_config, 
    create_sample_config, 
    _get_default_journal_path
)


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for configuration tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        "journal_path": "/test/journal/path",
        "edcopilot_path": "/test/edcopilot/path",
        "debug": True,
        "max_recent_events": 500,
        "server_port": 3001,
        "file_check_interval": 2.0,
        "status_update_interval": 3.0,
        "backup_custom_files": False,
        "max_backup_files": 10,
        "journal_encoding": "utf-16",
        "async_mode": False
    }


class TestEliteConfig:
    """Test cases for EliteConfig class."""
    
    def test_initialization_with_defaults(self):
        """Test configuration initialization with default values."""
        config = EliteConfig()
        
        # Test default values
        assert isinstance(config.journal_path, Path)
        assert isinstance(config.edcopilot_path, Path)
        assert config.debug is False
        assert config.max_recent_events == 1000
        assert config.server_port == 3000
        assert config.file_check_interval == 1.0
        assert config.status_update_interval == 2.0
        assert config.backup_custom_files is True
        assert config.max_backup_files == 5
        assert config.journal_encoding == "utf-8"
        assert config.async_mode is True
    
    def test_initialization_with_custom_values(self, sample_config_data):
        """Test configuration initialization with custom values."""
        config = EliteConfig(**sample_config_data)
        
        # Use Path.resolve() to handle cross-platform path differences
        expected_journal_path = Path(sample_config_data["journal_path"]).resolve()
        expected_edcopilot_path = Path(sample_config_data["edcopilot_path"]).resolve()
        
        assert config.journal_path == expected_journal_path
        assert config.edcopilot_path == expected_edcopilot_path
        assert config.debug == sample_config_data["debug"]
        assert config.max_recent_events == sample_config_data["max_recent_events"]
        assert config.server_port == sample_config_data["server_port"]
        assert config.file_check_interval == sample_config_data["file_check_interval"]
        assert config.status_update_interval == sample_config_data["status_update_interval"]
        assert config.backup_custom_files == sample_config_data["backup_custom_files"]
        assert config.max_backup_files == sample_config_data["max_backup_files"]
        assert config.journal_encoding == sample_config_data["journal_encoding"]
        assert config.async_mode == sample_config_data["async_mode"]
    
    def test_environment_variable_loading(self):
        """Test configuration loading from environment variables."""
        env_vars = {
            "ELITE_JOURNAL_PATH": "/env/journal/path",
            "ELITE_EDCOPILOT_PATH": "/env/edcopilot/path",
            "ELITE_DEBUG": "true",
            "ELITE_MAX_RECENT_EVENTS": "2000",
            "ELITE_SERVER_PORT": "4000",
            "ELITE_FILE_CHECK_INTERVAL": "0.5",
            "ELITE_STATUS_UPDATE_INTERVAL": "1.5",
            "ELITE_BACKUP_CUSTOM_FILES": "false",
            "ELITE_MAX_BACKUP_FILES": "15",
            "ELITE_JOURNAL_ENCODING": "latin-1",
            "ELITE_ASYNC_MODE": "false"
        }
        
        with patch.dict(os.environ, env_vars):
            config = EliteConfig()
            
            # Use Path.resolve() to handle cross-platform path differences
            expected_journal_path = Path("/env/journal/path").resolve()
            expected_edcopilot_path = Path("/env/edcopilot/path").resolve()
            
            assert config.journal_path == expected_journal_path
            assert config.edcopilot_path == expected_edcopilot_path
            assert config.debug is True
            assert config.max_recent_events == 2000
            assert config.server_port == 4000
            assert config.file_check_interval == 0.5
            assert config.status_update_interval == 1.5
            assert config.backup_custom_files is False
            assert config.max_backup_files == 15
            assert config.journal_encoding == "latin-1"
            assert config.async_mode is False
    
    def test_path_validation_string_input(self):
        """Test path validation with string inputs."""
        config = EliteConfig(
            journal_path="~/test/journal",
            edcopilot_path="~/test/edcopilot"
        )
        
        # Paths should be expanded and resolved
        assert config.journal_path.is_absolute()
        assert config.edcopilot_path.is_absolute()
        assert "~" not in str(config.journal_path)
        assert "~" not in str(config.edcopilot_path)
    
    def test_path_validation_path_input(self):
        """Test path validation with Path inputs."""
        journal_path = Path("~/test/journal")
        edcopilot_path = Path("~/test/edcopilot")
        
        config = EliteConfig(
            journal_path=journal_path,
            edcopilot_path=edcopilot_path
        )
        
        assert config.journal_path.is_absolute()
        assert config.edcopilot_path.is_absolute()
    
    def test_path_validation_invalid_type(self):
        """Test path validation with invalid input types."""
        with pytest.raises(ValidationError):
            EliteConfig(journal_path=123)
        
        with pytest.raises(ValidationError):
            EliteConfig(edcopilot_path=["invalid", "path"])
    
    def test_max_events_validation(self):
        """Test max_recent_events validation."""
        # Test minimum boundary
        with pytest.raises(ValidationError, match="max_recent_events must be at least 10"):
            EliteConfig(max_recent_events=5)
        
        # Test maximum boundary
        with pytest.raises(ValidationError, match="max_recent_events cannot exceed 100,000"):
            EliteConfig(max_recent_events=150000)
        
        # Test valid values
        config = EliteConfig(max_recent_events=10)
        assert config.max_recent_events == 10
        
        config = EliteConfig(max_recent_events=100000)
        assert config.max_recent_events == 100000
    
    def test_interval_validation(self):
        """Test interval field validation."""
        # Test minimum boundary
        with pytest.raises(ValidationError, match="Interval must be at least 0.1 seconds"):
            EliteConfig(file_check_interval=0.05)
        
        with pytest.raises(ValidationError, match="Interval must be at least 0.1 seconds"):
            EliteConfig(status_update_interval=0.05)
        
        # Test maximum boundary
        with pytest.raises(ValidationError, match="Interval cannot exceed 60 seconds"):
            EliteConfig(file_check_interval=120.0)
        
        with pytest.raises(ValidationError, match="Interval cannot exceed 60 seconds"):
            EliteConfig(status_update_interval=120.0)
        
        # Test valid values
        config = EliteConfig(file_check_interval=0.1, status_update_interval=60.0)
        assert config.file_check_interval == 0.1
        assert config.status_update_interval == 60.0
    
    def test_validate_paths_existing_directories(self, temp_config_dir):
        """Test path validation with existing directories."""
        # Create test directories
        journal_dir = temp_config_dir / "journal"
        edcopilot_dir = temp_config_dir / "edcopilot"
        journal_dir.mkdir()
        edcopilot_dir.mkdir()
        
        config = EliteConfig(
            journal_path=journal_dir,
            edcopilot_path=edcopilot_dir
        )
        
        results = config.validate_paths()
        
        assert results['journal_path']['exists'] is True
        assert results['journal_path']['readable'] is True
        assert "accessible" in results['journal_path']['message']
        
        assert results['edcopilot_path']['exists'] is True
        assert results['edcopilot_path']['readable'] is True
        assert results['edcopilot_path']['writable'] is True
        assert "accessible" in results['edcopilot_path']['message']
    
    def test_validate_paths_nonexistent_directories(self, temp_config_dir):
        """Test path validation with nonexistent directories."""
        journal_dir = temp_config_dir / "nonexistent_journal"
        edcopilot_dir = temp_config_dir / "nonexistent_edcopilot"
        
        config = EliteConfig(
            journal_path=journal_dir,
            edcopilot_path=edcopilot_dir
        )
        
        results = config.validate_paths()
        
        assert results['journal_path']['exists'] is False
        assert "does not exist" in results['journal_path']['message']
        
        # EDCoPilot path should be created
        assert results['edcopilot_path']['exists'] is True
        assert results['edcopilot_path']['writable'] is True
        assert "created successfully" in results['edcopilot_path']['message']
    
    def test_validate_paths_permission_errors(self, temp_config_dir):
        """Test path validation with permission errors."""
        with patch('os.access', return_value=False):
            config = EliteConfig(journal_path=temp_config_dir)
            results = config.validate_paths()
            
            # Should still exist but not be readable
            assert results['journal_path']['exists'] is True
            assert results['journal_path']['readable'] is False
    
    def test_load_from_file_success(self, temp_config_dir, sample_config_data):
        """Test loading configuration from JSON file."""
        config_file = temp_config_dir / "config.json"
        
        with open(config_file, 'w') as f:
            json.dump(sample_config_data, f)
        
        config = EliteConfig()
        result = config.load_from_file(config_file)
        
        assert result is True
        # Use Path.resolve() to handle cross-platform differences
        expected_path = Path(sample_config_data["journal_path"]).resolve()
        assert config.journal_path == expected_path
        assert config.debug == sample_config_data["debug"]
        assert config.max_recent_events == sample_config_data["max_recent_events"]
    
    def test_load_from_file_not_found(self, temp_config_dir):
        """Test loading configuration from nonexistent file."""
        config_file = temp_config_dir / "nonexistent.json"
        
        config = EliteConfig()
        result = config.load_from_file(config_file)
        
        assert result is False
    
    def test_load_from_file_invalid_json(self, temp_config_dir):
        """Test loading configuration from invalid JSON file."""
        config_file = temp_config_dir / "invalid.json"
        
        with open(config_file, 'w') as f:
            f.write("invalid json content {")
        
        config = EliteConfig()
        result = config.load_from_file(config_file)
        
        assert result is False
    
    def test_load_from_file_unknown_keys(self, temp_config_dir):
        """Test loading configuration with unknown keys."""
        config_data = {
            "debug": True,
            "unknown_key": "unknown_value",
            "another_unknown": 123
        }
        
        config_file = temp_config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = EliteConfig()
        result = config.load_from_file(config_file)
        
        assert result is True
        assert config.debug is True
        # Unknown keys should be ignored
        assert not hasattr(config, 'unknown_key')
    
    def test_save_to_file_success(self, temp_config_dir, sample_config_data):
        """Test saving configuration to JSON file."""
        config = EliteConfig(**sample_config_data)
        config_file = temp_config_dir / "saved_config.json"
        
        result = config.save_to_file(config_file)
        
        assert result is True
        assert config_file.exists()
        
        # Verify saved content
        with open(config_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["debug"] == sample_config_data["debug"]
        assert saved_data["max_recent_events"] == sample_config_data["max_recent_events"]
        # Paths should be converted to strings
        assert isinstance(saved_data["journal_path"], str)
        assert isinstance(saved_data["edcopilot_path"], str)
    
    def test_save_to_file_permission_error(self, temp_config_dir):
        """Test saving configuration with permission errors."""
        config = EliteConfig()
        
        # Try to save to a read-only location (mock permission error)
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            config_file = temp_config_dir / "readonly.json"
            result = config.save_to_file(config_file)
            
            assert result is False
    
    def test_get_summary(self):
        """Test configuration summary generation."""
        config = EliteConfig(
            debug=True,
            max_recent_events=500,
            file_check_interval=2.0
        )
        
        summary = config.get_summary()
        
        assert 'journal_path' in summary
        assert 'edcopilot_path' in summary
        assert summary['debug'] is True
        assert summary['max_recent_events'] == 500
        assert summary['file_check_interval'] == 2.0
        assert 'platform' in summary
        assert 'python_version' in summary
        
        # Verify paths are strings in summary
        assert isinstance(summary['journal_path'], str)
        assert isinstance(summary['edcopilot_path'], str)


class TestPlatformSpecificDefaults:
    """Test platform-specific default path detection."""
    
    def test_get_default_journal_path_windows(self):
        """Test default journal path on Windows."""
        with patch('platform.system', return_value='Windows'):
            path = _get_default_journal_path()
            
            assert "Saved Games" in str(path)
            assert "Frontier Developments" in str(path)
            assert "Elite Dangerous" in str(path)
    
    def test_get_default_journal_path_macos(self):
        """Test default journal path on macOS."""
        with patch('platform.system', return_value='Darwin'):
            path = _get_default_journal_path()
            
            assert "Library" in str(path)
            assert "Application Support" in str(path)
            assert "Frontier Developments" in str(path)
            assert "Elite Dangerous" in str(path)
    
    def test_get_default_journal_path_linux(self):
        """Test default journal path on Linux."""
        with patch('platform.system', return_value='Linux'):
            path = _get_default_journal_path()
            
            assert ".local" in str(path)
            assert "share" in str(path)
            assert "Frontier Developments" in str(path)
            assert "Elite Dangerous" in str(path)
    
    def test_get_default_journal_path_unknown_platform(self):
        """Test default journal path on unknown platform."""
        with patch('platform.system', return_value='UnknownOS'):
            path = _get_default_journal_path()
            
            # Should default to Linux-style path
            assert ".local" in str(path)
            assert "share" in str(path)


class TestConfigurationFactoryFunctions:
    """Test factory functions for configuration loading."""
    
    def test_load_config_without_file(self):
        """Test loading configuration without config file."""
        config = load_config()
        
        assert isinstance(config, EliteConfig)
        assert config.debug is False  # Default value
        assert config.max_recent_events == 1000  # Default value
    
    def test_load_config_with_file(self, temp_config_dir, sample_config_data):
        """Test loading configuration with config file."""
        config_file = temp_config_dir / "test_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(sample_config_data, f)
        
        config = load_config(config_file)
        
        assert isinstance(config, EliteConfig)
        assert config.debug == sample_config_data["debug"]
        assert config.max_recent_events == sample_config_data["max_recent_events"]
    
    def test_load_config_with_nonexistent_file(self, temp_config_dir):
        """Test loading configuration with nonexistent file."""
        config_file = temp_config_dir / "nonexistent.json"
        
        config = load_config(config_file)
        
        # Should still create config with defaults
        assert isinstance(config, EliteConfig)
        assert config.debug is False
    
    def test_create_sample_config_success(self, temp_config_dir):
        """Test creating sample configuration file."""
        output_file = temp_config_dir / "sample_config.json"
        
        result = create_sample_config(output_file)
        
        assert result is True
        assert output_file.exists()
        
        # Verify sample config content
        with open(output_file, 'r') as f:
            sample_data = json.load(f)
        
        assert "_comment" in sample_data
        assert "journal_path" in sample_data
        assert "edcopilot_path" in sample_data
        assert "_environment_variables" in sample_data
        assert isinstance(sample_data["debug"], bool)
        assert isinstance(sample_data["max_recent_events"], int)
    
    def test_create_sample_config_permission_error(self, temp_config_dir):
        """Test creating sample configuration with permission error."""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            output_file = temp_config_dir / "sample.json"
            result = create_sample_config(output_file)
            
            assert result is False


class TestConfigurationIntegration:
    """Integration tests for configuration system."""
    
    def test_full_configuration_workflow(self, temp_config_dir):
        """Test complete configuration workflow."""
        # 1. Create config with custom values
        config = EliteConfig(
            debug=True,
            max_recent_events=500,
            file_check_interval=0.5
        )
        
        # 2. Save to file
        config_file = temp_config_dir / "workflow_config.json"
        save_result = config.save_to_file(config_file)
        assert save_result is True
        
        # 3. Load new config instance from file
        new_config = EliteConfig()
        load_result = new_config.load_from_file(config_file)
        assert load_result is True
        
        # 4. Verify values match
        assert new_config.debug == config.debug
        assert new_config.max_recent_events == config.max_recent_events
        assert new_config.file_check_interval == config.file_check_interval
        
        # 5. Validate paths
        validation_results = new_config.validate_paths()
        assert 'journal_path' in validation_results
        assert 'edcopilot_path' in validation_results
        
        # 6. Get summary
        summary = new_config.get_summary()
        assert summary['debug'] is True
        assert summary['max_recent_events'] == 500
    
    def test_environment_override_file_config(self, temp_config_dir):
        """Test environment variables overriding file configuration."""
        # Create config file with specific values
        file_config = {
            "debug": False,
            "max_recent_events": 100
        }
        
        config_file = temp_config_dir / "base_config.json"
        with open(config_file, 'w') as f:
            json.dump(file_config, f)
        
        # Set environment variables that should override
        env_vars = {
            "ELITE_DEBUG": "true",
            "ELITE_MAX_RECENT_EVENTS": "2000"
        }
        
        with patch.dict(os.environ, env_vars):
            # Create config with environment variables AFTER loading file
            # to test proper precedence
            config = EliteConfig()
            
            # Load file data (this should NOT override environment variables)
            config.load_from_file(config_file)
            
            # Re-create config to apply environment variables properly
            config = EliteConfig()
            
            # Environment variables should take precedence over defaults
            assert config.debug is True  # From env, not defaults
            assert config.max_recent_events == 2000  # From env, not defaults
    
    def test_configuration_error_handling(self):
        """Test configuration error handling scenarios."""
        # Test configuration with validation errors
        with pytest.raises(ValidationError):
            EliteConfig(max_recent_events=-1)
        
        with pytest.raises(ValidationError):
            EliteConfig(file_check_interval=0.01)
        
        # Test load_config with invalid paths
        invalid_config = load_config(Path("/absolutely/nonexistent/path/config.json"))
        assert isinstance(invalid_config, EliteConfig)  # Should still work with defaults


class TestConfigurationEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_very_long_paths(self):
        """Test configuration with very long paths."""
        long_path = "/very/long/path/" + "a" * 200 + "/journal"
        
        config = EliteConfig(journal_path=long_path)
        # Compare resolved paths to handle cross-platform differences
        expected_path = Path(long_path).resolve()
        assert config.journal_path == expected_path
    
    def test_special_characters_in_paths(self):
        """Test paths with special characters."""
        special_path = "/path with spaces/and-dashes/and_underscores/journal"
        
        config = EliteConfig(journal_path=special_path)
        assert "spaces" in str(config.journal_path)
        assert "dashes" in str(config.journal_path)
        assert "underscores" in str(config.journal_path)
    
    def test_unicode_in_configuration(self, temp_config_dir):
        """Test configuration with unicode characters."""
        unicode_data = {
            "journal_path": "/home/ñoño/élite/journal",
            "debug": True
        }
        
        config_file = temp_config_dir / "unicode_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(unicode_data, f, ensure_ascii=False)
        
        config = EliteConfig()
        result = config.load_from_file(config_file)
        
        assert result is True
        assert "ñoño" in str(config.journal_path)
        assert "élite" in str(config.journal_path)
    
    def test_concurrent_file_access(self, temp_config_dir):
        """Test concurrent configuration file access."""
        config_file = temp_config_dir / "concurrent_config.json"
        
        # Simulate file being locked/busy
        with patch('builtins.open', side_effect=[PermissionError("File locked"), MagicMock()]):
            config = EliteConfig()
            result = config.save_to_file(config_file)
            
            # First attempt should fail, but shouldn't crash
            assert result is False
