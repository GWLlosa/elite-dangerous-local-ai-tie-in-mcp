"""
Basic tests for configuration management system.

This provides basic validation that the configuration system works correctly.
Full test suite will be implemented in Milestone 14.
"""

import os
import tempfile
from pathlib import Path

# Simple test function without pytest framework (for now)
def test_config_basic():
    """Test basic configuration loading and validation."""
    from src.utils.config import EliteConfig, load_config, create_sample_config
    
    print("🧪 Testing configuration management system...")
    
    # Test 1: Basic configuration creation
    print("  ✓ Testing basic config creation...")
    config = EliteConfig()
    assert config.max_recent_events == 1000
    assert config.debug is False
    assert isinstance(config.journal_path, Path)
    print("    ✅ Basic configuration created successfully")
    
    # Test 2: Environment variable override
    print("  ✓ Testing environment variable override...")
    os.environ['ELITE_DEBUG'] = 'true'
    os.environ['ELITE_MAX_RECENT_EVENTS'] = '2000'
    config_with_env = EliteConfig()
    assert config_with_env.debug is True
    assert config_with_env.max_recent_events == 2000
    print("    ✅ Environment variables override correctly")
    
    # Clean up environment
    os.environ.pop('ELITE_DEBUG', None)
    os.environ.pop('ELITE_MAX_RECENT_EVENTS', None)
    
    # Test 3: Configuration file creation and loading
    print("  ✓ Testing configuration file operations...")
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"
        sample_file = Path(temp_dir) / "sample_config.json"
        
        # Create sample config
        assert create_sample_config(sample_file) is True
        assert sample_file.exists()
        
        # Save and load config
        config = EliteConfig(debug=True, max_recent_events=500)
        assert config.save_to_file(config_file) is True
        assert config_file.exists()
        
        # Load config from file
        loaded_config = load_config(config_file)
        assert loaded_config.debug is True
        assert loaded_config.max_recent_events == 500
        
    print("    ✅ Configuration file operations work correctly")
    
    # Test 4: Path validation
    print("  ✓ Testing path validation...")
    config = EliteConfig()
    validation_results = config.validate_paths()
    assert 'journal_path' in validation_results
    assert 'edcopilot_path' in validation_results
    assert isinstance(validation_results['journal_path']['exists'], bool)
    assert isinstance(validation_results['edcopilot_path']['exists'], bool)
    print("    ✅ Path validation works correctly")
    
    # Test 5: Configuration summary
    print("  ✓ Testing configuration summary...")
    config = EliteConfig()
    summary = config.get_summary()
    assert 'journal_path' in summary
    assert 'edcopilot_path' in summary
    assert 'debug' in summary
    assert 'max_recent_events' in summary
    assert 'platform' in summary
    print("    ✅ Configuration summary generated correctly")
    
    print("🎉 All configuration tests passed!")
    return True


def test_server_integration():
    """Test server integration with configuration system."""
    from src.server import EliteDangerousLocalAITieInMCPServer
    
    print("🧪 Testing server integration with configuration...")
    
    # Test server initialization with default config
    try:
        server = EliteDangerousLocalAITieInMCPServer()
        assert server.config is not None
        assert hasattr(server.config, 'journal_path')
        assert hasattr(server.config, 'edcopilot_path')
        print("  ✅ Server initializes with configuration successfully")
    except Exception as e:
        print(f"  ❌ Server initialization failed: {e}")
        raise
    
    # Test server initialization with custom config file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.json"
        
        # Create test config
        from src.utils.config import EliteConfig
        test_config = EliteConfig(debug=True, max_recent_events=123)
        test_config.save_to_file(config_file)
        
        # Initialize server with custom config
        try:
            server = EliteDangerousLocalAITieInMCPServer(config_file=config_file)
            assert server.config.debug is True
            assert server.config.max_recent_events == 123
            print("  ✅ Server loads custom configuration correctly")
        except Exception as e:
            print(f"  ❌ Server custom config loading failed: {e}")
            raise
    
    print("🎉 Server integration tests passed!")
    return True


if __name__ == "__main__":
    """Run basic configuration tests."""
    try:
        print("=" * 50)
        print("Configuration Management System Tests")
        print("=" * 50)
        
        test_config_basic()
        print()
        test_server_integration()
        
        print()
        print("✅ All tests passed! Configuration system is working correctly.")
        print()
        print("Try these commands to test the configuration system:")
        print("  python -m src.server --help")
        print("  python -m src.server --create-sample-config sample.json")
        print("  python -m src.server --validate-config")
        print("  ELITE_DEBUG=true python -m src.server --validate-config")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)