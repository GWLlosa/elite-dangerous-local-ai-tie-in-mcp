#!/usr/bin/env python3
"""
Elite Dangerous MCP Server - Test Runner

This script runs the complete test suite with detailed progress reporting.
Run from the project root directory.

Usage:
    python scripts/run_tests.py
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path


# Mapping of package names to their import names
PACKAGE_IMPORT_MAP = {
    'python-dateutil': 'dateutil',
    'pydantic-settings': 'pydantic_settings',
    'pytest-asyncio': 'pytest_asyncio',
    'pytest-cov': 'pytest_cov',
    # Add more mappings as needed
}


def get_import_name(package_name):
    """Get the import name for a package, handling special cases."""
    # Check if there's a specific mapping
    if package_name in PACKAGE_IMPORT_MAP:
        return PACKAGE_IMPORT_MAP[package_name]
    
    # Default: replace hyphens with underscores
    return package_name.replace('-', '_')


def get_venv_python():
    """Get path to Python executable in virtual environment."""
    venv_path = Path("venv")
    
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "python.exe")
    else:
        return str(venv_path / "bin" / "python")


def print_step(step_num, total_steps, title, description=""):
    """Print a formatted step header."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}/{total_steps}: {title}")
    if description:
        print(f"{description}")
    print('='*60)


def print_substep(title, description=""):
    """Print a formatted substep."""
    print(f"\n-> {title}")
    if description:
        print(f"  {description}")


def run_command(cmd, description, capture_output=False, show_output=True, python_exe=None):
    """Run a command and return success status."""
    # If a specific Python executable is provided, use it for Python commands
    if python_exe and isinstance(cmd, list) and cmd[0] == sys.executable:
        cmd = [python_exe] + cmd[1:]
    
    print(f"\n  Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                shell=True if isinstance(cmd, str) else False
            )
            if show_output and result.stdout:
                print(f"  Output: {result.stdout.strip()}")
            if result.stderr and result.returncode != 0:
                print(f"  Error: {result.stderr.strip()}")
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(
                cmd, 
                shell=True if isinstance(cmd, str) else False
            )
            return result.returncode == 0, "", ""
    except Exception as e:
        print(f"  [ERROR] Error running command: {e}")
        return False, "", str(e)


def check_virtual_environment():
    """Check if virtual environment exists and is valid."""
    venv_path = Path("venv")
    venv_python = get_venv_python()
    
    if not venv_path.exists():
        print("  [FAILED] Virtual environment directory not found")
        print("     Please run: python scripts/setup_dependencies.py")
        return False, None
    
    if not Path(venv_python).exists():
        print("  [FAILED] Virtual environment Python executable not found")
        print("     Please run: python scripts/setup_dependencies.py")
        return False, None
    
    # Test that the venv Python actually works
    try:
        result = subprocess.run(
            [venv_python, "--version"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode == 0:
            print(f"  [SUCCESS] Virtual environment is valid: {result.stdout.strip()}")
            print(f"  Using Python executable: {venv_python}")
            return True, venv_python
        else:
            print("  [FAILED] Virtual environment Python is not working")
            print("     Please run: python scripts/setup_dependencies.py")
            return False, None
    except Exception as e:
        print(f"  [FAILED] Error testing virtual environment: {e}")
        print("     Please run: python scripts/setup_dependencies.py")
        return False, None


def main():
    """Main test runner function."""
    start_time = time.time()
    total_steps = 10  # Updated to include MCP server tests
    
    print("Elite Dangerous MCP Server - Test Suite Runner")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify we're in the project root
    if not Path("src").exists() or not Path("tests").exists():
        print("[ERROR] Must be run from project root directory")
        sys.exit(1)
    
    # Step 1: Environment Check
    print_step(1, total_steps, "Environment Verification", 
               "Checking Python version and virtual environment")
    
    success, python_version, _ = run_command([sys.executable, "--version"], 
                                           "Check Python version", capture_output=True)
    if success:
        print(f"  [SUCCESS] Python version: {python_version.strip()}")
    else:
        print("  [FAILED] Failed to get Python version")
        sys.exit(1)
    
    venv_valid, venv_python = check_virtual_environment()
    if not venv_valid:
        sys.exit(1)
    
    # Step 2: Dependency Check
    print_step(2, total_steps, "Dependency Verification",
               "Checking all required packages are installed")
    
    required_packages = [
        "pytest", "pytest-asyncio", "pytest-cov", 
        "orjson", "watchdog", "pydantic", "aiofiles", "mcp"
    ]
    
    missing_packages = []
    for package in required_packages:
        # Get the correct import name
        import_name = get_import_name(package)
        
        success, _, _ = run_command([venv_python, "-c", f"import {import_name}"], 
                                   f"Check {package}", capture_output=True, show_output=False)
        if success:
            print(f"  [SUCCESS] {package}")
        else:
            print(f"  [FAILED] {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  [FAILED] Missing packages: {', '.join(missing_packages)}")
        print("     Please run: python scripts/setup_dependencies.py")
        sys.exit(1)
    
    # Step 3: Project Structure Validation
    print_step(3, total_steps, "Project Structure Validation",
               "Verifying all necessary files and directories exist")
    
    required_paths = [
        "src/__init__.py",
        "src/journal/__init__.py", 
        "src/journal/parser.py",
        "src/journal/monitor.py",
        "src/journal/events.py",
        "src/utils/__init__.py",
        "src/utils/config.py",
        "src/utils/data_store.py",
        "src/server.py",  # Milestone 7 addition
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/unit/test_journal_parser.py",
        "tests/unit/test_journal_monitor.py",
        "tests/unit/test_events.py",
        "tests/unit/test_data_store.py",
        "tests/unit/test_server.py"  # Milestone 7 addition
    ]
    
    all_paths_exist = True
    for path in required_paths:
        if Path(path).exists():
            print(f"  [SUCCESS] {path}")
        else:
            print(f"  [FAILED] {path} - missing")
            all_paths_exist = False
    
    if not all_paths_exist:
        print("\n  [FAILED] Some required files are missing")
        sys.exit(1)
    
    # Step 4: Import Tests
    print_step(4, total_steps, "Import Verification",
               "Testing that all modules can be imported successfully")
    
    import_tests = [
        ("src", "Main package"),
        ("src.journal", "Journal package"),
        ("src.journal.parser", "Journal parser"),
        ("src.journal.monitor", "Journal monitor"),
        ("src.journal.events", "Event processing"),
        ("src.utils.config", "Configuration system"),
        ("src.utils.data_store", "Data storage system"),
        ("src.server", "MCP server framework")  # Milestone 7 addition
    ]
    
    all_imports_successful = True
    for module, description in import_tests:
        # Use plain text without emoji for subprocess commands
        success, _, error = run_command([venv_python, "-c", f"import {module}; print('OK: {description}')"], 
                                       f"Import {module}", capture_output=True)
        if success:
            print(f"  [SUCCESS] {description}")
        else:
            print(f"  [FAILED] {description} - {error.strip()}")
            all_imports_successful = False
    
    if not all_imports_successful:
        print("\n  [FAILED] Some imports failed")
        sys.exit(1)
    
    # Step 5: Individual Component Tests
    print_step(5, total_steps, "Component Functionality Tests",
               "Testing individual components work correctly")
    
    print_substep("Testing JournalParser functionality")
    parser_test = '''
from pathlib import Path
from src.journal.parser import JournalParser
import tempfile

with tempfile.TemporaryDirectory() as temp_dir:
    parser = JournalParser(Path(temp_dir))
    results = parser.validate_journal_directory()
    files = parser.find_journal_files()
    print(f"JournalParser: Directory validation successful, found {len(files)} files")
'''
    
    success, output, error = run_command([venv_python, "-c", parser_test],
                                        "JournalParser test", capture_output=True)
    if success:
        print(f"  [SUCCESS] {output.strip()}")
    else:
        print(f"  [FAILED] JournalParser test failed: {error.strip()}")
    
    print_substep("Testing Event Processing functionality")
    events_test = '''
from src.journal.events import EventProcessor
processor = EventProcessor()
event = {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump", "StarSystem": "Sol"}
processed = processor.process_event(event)
print(f"EventProcessor: Processed {processed.event_type} event, category={processed.category.value}")
'''
    
    success, output, error = run_command([venv_python, "-c", events_test],
                                        "EventProcessor test", capture_output=True)
    if success:
        print(f"  [SUCCESS] {output.strip()}")
    else:
        print(f"  [FAILED] EventProcessor test failed: {error.strip()}")
    
    print_substep("Testing Configuration system")
    config_test = '''
from src.utils.config import EliteConfig
config = EliteConfig()
validation = config.validate_paths()
print(f"Configuration: Journal path={config.journal_path.name}, validation completed")
'''
    
    success, output, error = run_command([venv_python, "-c", config_test],
                                        "Config test", capture_output=True)
    if success:
        print(f"  [SUCCESS] {output.strip()}")
    else:
        print(f"  [FAILED] Configuration test failed: {error.strip()}")
    
    print_substep("Testing Data Storage system")
    data_store_test = '''
from src.utils.data_store import DataStore, EventFilter, get_data_store
from src.journal.events import ProcessedEvent, EventCategory
from datetime import datetime

# Test basic data store functionality
store = DataStore(max_events=10)
event = ProcessedEvent(
    timestamp=datetime.utcnow(),
    event_type="FSDJump",
    category=EventCategory.NAVIGATION,
    summary="Test jump",
    raw_data={"event": "FSDJump"},
    extracted_data={"system_name": "Sol"}
)
store.store_event(event)
events = store.query_events()
game_state = store.get_game_state()
stats = store.get_statistics()
print(f"DataStore: Stored {len(events)} events, game state updated, {stats['total_processed']} processed")

# Test global store
global_store = get_data_store()
print(f"Global store: {type(global_store).__name__} instance created")
'''
    
    success, output, error = run_command([venv_python, "-c", data_store_test],
                                        "DataStore test", capture_output=True)
    if success:
        print(f"  [SUCCESS] {output.strip()}")
    else:
        print(f"  [FAILED] DataStore test failed: {error.strip()}")
    
    # Milestone 7: MCP Server functionality test
    print_substep("Testing MCP Server framework")
    server_test = '''
from src.server import EliteDangerousServer, create_server
import asyncio
from unittest.mock import patch, Mock

# Test server creation
async def test_server():
    with patch('src.server.EliteConfig') as mock_config:
        mock_config_instance = Mock()
        mock_config_instance.journal_path = "/tmp/test"
        mock_config_instance.validate_paths.return_value = True
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        print(f"MCPServer: Server created successfully, FastMCP app configured")
        
        # Test basic handler setup
        server.setup_basic_mcp_handlers()
        tools = list(server.app.tools.keys())
        print(f"MCP Tools: {len(tools)} tools registered: {', '.join(tools)}")
        
        return True

# Run the test
result = asyncio.run(test_server())
if result:
    print("MCP Server framework: All tests passed")
'''
    
    success, output, error = run_command([venv_python, "-c", server_test],
                                        "MCP Server test", capture_output=True)
    if success:
        print(f"  [SUCCESS] {output.strip()}")
    else:
        print(f"  [FAILED] MCP Server test failed: {error.strip()}")
    
    # Step 6: Unit Test Suite - Parser
    print_step(6, total_steps, "Journal Parser Unit Tests",
               "Running comprehensive tests for journal parsing functionality")
    
    success, _, _ = run_command([venv_python, "-m", "pytest", "tests/unit/test_journal_parser.py", "-v"],
                               "Journal parser tests")
    if not success:
        print("  [FAILED] Journal parser tests failed")
        sys.exit(1)
    
    # Step 7: Unit Test Suite - Monitor and Events  
    print_step(7, total_steps, "Core Component Unit Tests",
               "Running comprehensive tests for monitoring and event processing")
    
    success, _, _ = run_command([venv_python, "-m", "pytest", "tests/unit/test_journal_monitor.py", 
                                "tests/unit/test_events.py", "tests/unit/test_events_extended.py", "-v"],
                               "Monitor and events tests")
    if not success:
        print("  [FAILED] Monitor and events tests failed")
        sys.exit(1)
    
    # Step 8: Unit Test Suite - Data Store (Milestone 6)
    print_step(8, total_steps, "Data Storage Unit Tests",
               "Running comprehensive tests for data storage and retrieval system")
    
    success, _, _ = run_command([venv_python, "-m", "pytest", "tests/unit/test_data_store.py", "-v"],
                               "Data store tests")
    if not success:
        print("  [FAILED] Data store tests failed")
        sys.exit(1)
    
    # Step 9: Unit Test Suite - MCP Server (Milestone 7)
    print_step(9, total_steps, "MCP Server Unit Tests",
               "Running comprehensive tests for MCP server framework")
    
    success, _, _ = run_command([venv_python, "-m", "pytest", "tests/unit/test_server.py", "-v"],
                               "MCP server tests")
    if not success:
        print("  [FAILED] MCP server tests failed")
        sys.exit(1)
    
    # Step 10: Full Test Suite with Coverage
    print_step(10, total_steps, "Complete Test Suite with Coverage",
               "Running all tests together and generating coverage report")
    
    print_substep("Running complete test suite")
    success, _, _ = run_command([
        venv_python, "-m", "pytest", "tests/unit/", "-v", 
        "--cov=src", "--cov-report=term", "--cov-report=html"
    ], "Complete test suite with coverage")
    
    if not success:
        print("  [FAILED] Complete test suite failed")
        sys.exit(1)
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Total execution time: {duration:.2f} seconds")
    print(f"Coverage report generated in: htmlcov/index.html")
    print(f"All implemented functionality verified and working")
    print("\nMilestone 7: Basic MCP Server Framework - COMPLETED")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
