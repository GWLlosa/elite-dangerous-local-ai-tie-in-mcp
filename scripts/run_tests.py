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
from pathlib import Path


def print_step(step_num, total_steps, title, description=""):
    """Print a formatted step header."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}/{total_steps}: {title}")
    if description:
        print(f"{description}")
    print('='*60)


def print_substep(title, description=""):
    """Print a formatted substep."""
    print(f"\n→ {title}")
    if description:
        print(f"  {description}")


def run_command(cmd, description, capture_output=False, show_output=True):
    """Run a command and return success status."""
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
        print(f"  ❌ Error running command: {e}")
        return False, "", str(e)


def check_virtual_environment():
    """Check if virtual environment is activated."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("  ✅ Virtual environment is activated")
        return True
    else:
        print("  ❌ Virtual environment is not activated")
        print("     Please run: python scripts/setup_dependencies.py")
        return False


def main():
    """Main test runner function."""
    start_time = time.time()
    total_steps = 8
    
    print("🚀 Elite Dangerous MCP Server - Test Suite Runner")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify we're in the project root
    if not Path("src").exists() or not Path("tests").exists():
        print("❌ Error: Must be run from project root directory")
        sys.exit(1)
    
    # Step 1: Environment Check
    print_step(1, total_steps, "Environment Verification", 
               "Checking Python version and virtual environment")
    
    success, python_version, _ = run_command([sys.executable, "--version"], 
                                           "Check Python version", capture_output=True)
    if success:
        print(f"  ✅ Python version: {python_version.strip()}")
    else:
        print("  ❌ Failed to get Python version")
        sys.exit(1)
    
    if not check_virtual_environment():
        sys.exit(1)
    
    # Step 2: Dependency Check
    print_step(2, total_steps, "Dependency Verification",
               "Checking all required packages are installed")
    
    required_packages = [
        "pytest", "pytest-asyncio", "pytest-cov", 
        "orjson", "watchdog", "pydantic", "aiofiles"
    ]
    
    missing_packages = []
    for package in required_packages:
        success, _, _ = run_command([sys.executable, "-c", f"import {package}"], 
                                   f"Check {package}", capture_output=True, show_output=False)
        if success:
            print(f"  ✅ {package}")
        else:
            print(f"  ❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  ❌ Missing packages: {', '.join(missing_packages)}")
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
        "src/utils/__init__.py",
        "src/utils/config.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/unit/test_journal_parser.py",
        "tests/unit/test_journal_monitor.py"
    ]
    
    all_paths_exist = True
    for path in required_paths:
        if Path(path).exists():
            print(f"  ✅ {path}")
        else:
            print(f"  ❌ {path} - missing")
            all_paths_exist = False
    
    if not all_paths_exist:
        print("\n  ❌ Some required files are missing")
        sys.exit(1)
    
    # Step 4: Import Tests
    print_step(4, total_steps, "Import Verification",
               "Testing that all modules can be imported successfully")
    
    import_tests = [
        ("src", "Main package"),
        ("src.journal", "Journal package"),
        ("src.journal.parser", "Journal parser"),
        ("src.journal.monitor", "Journal monitor"),
        ("src.utils.config", "Configuration system")
    ]
    
    all_imports_successful = True
    for module, description in import_tests:
        success, _, error = run_command([sys.executable, "-c", f"import {module}; print('✅ {description}')"], 
                                       f"Import {module}", capture_output=True)
        if success:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - {error.strip()}")
            all_imports_successful = False
    
    if not all_imports_successful:
        print("\n  ❌ Some imports failed")
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
    
    success, output, error = run_command([sys.executable, "-c", parser_test],
                                        "JournalParser test", capture_output=True)
    if success:
        print(f"  ✅ {output.strip()}")
    else:
        print(f"  ❌ JournalParser test failed: {error.strip()}")
    
    print_substep("Testing Configuration system")
    config_test = '''
from src.utils.config import EliteConfig
config = EliteConfig()
validation = config.validate_paths()
print(f"Configuration: Journal path={config.journal_path.name}, validation completed")
'''
    
    success, output, error = run_command([sys.executable, "-c", config_test],
                                        "Config test", capture_output=True)
    if success:
        print(f"  ✅ {output.strip()}")
    else:
        print(f"  ❌ Configuration test failed: {error.strip()}")
    
    # Step 6: Unit Test Suite - Parser
    print_step(6, total_steps, "Journal Parser Unit Tests",
               "Running comprehensive tests for journal parsing functionality")
    
    success, _, _ = run_command([sys.executable, "-m", "pytest", "tests/unit/test_journal_parser.py", "-v"],
                               "Journal parser tests")
    if not success:
        print("  ❌ Journal parser tests failed")
        sys.exit(1)
    
    # Step 7: Unit Test Suite - Monitor  
    print_step(7, total_steps, "Journal Monitor Unit Tests",
               "Running comprehensive tests for real-time monitoring functionality")
    
    success, _, _ = run_command([sys.executable, "-m", "pytest", "tests/unit/test_journal_monitor.py", "-v"],
                               "Journal monitor tests")
    if not success:
        print("  ❌ Journal monitor tests failed")
        sys.exit(1)
    
    # Step 8: Full Test Suite with Coverage
    print_step(8, total_steps, "Complete Test Suite with Coverage",
               "Running all tests together and generating coverage report")
    
    print_substep("Running complete test suite")
    success, _, _ = run_command([
        sys.executable, "-m", "pytest", "tests/unit/", "-v", 
        "--cov=src", "--cov-report=term", "--cov-report=html"
    ], "Complete test suite with coverage")
    
    if not success:
        print("  ❌ Complete test suite failed")
        sys.exit(1)
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"⏱️  Total execution time: {duration:.2f} seconds")
    print(f"📊 Coverage report generated in: htmlcov/index.html")
    print(f"✅ All milestones 1-4 functionality verified")
    print("\n🚀 Ready for Milestone 5: Event Processing and Classification")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
