#!/usr/bin/env python3
"""
Elite Dangerous MCP Server - Dependency Checker

This script checks if all dependencies are properly installed and configured.
Run from the project root directory.

Usage:
    python scripts/check_dependencies.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print('='*50)


def print_check(description, status, details=""):
    """Print a formatted check result."""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {description}")
    if details:
        print(f"   {details}")


def check_python_version():
    """Check Python version requirements."""
    print_header("Python Environment Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    # Check if Python 3.9+
    python_ok = version.major == 3 and version.minor >= 9
    print_check(f"Python Version: {version_str}", python_ok, 
                "Requires Python 3.9+" if not python_ok else "")
    
    # Check platform
    system = platform.system()
    print_check(f"Platform: {system} {platform.release()}", True)
    
    # Check executable location
    print_check(f"Python Executable: {sys.executable}", True)
    
    return python_ok


def check_virtual_environment():
    """Check virtual environment status."""
    print_header("Virtual Environment Check")
    
    # Check if venv exists
    venv_path = Path("venv")
    venv_exists = venv_path.exists()
    print_check("Virtual environment directory exists", venv_exists,
                "Run: python scripts/setup_dependencies.py" if not venv_exists else str(venv_path))
    
    # Check if virtual environment is activated
    is_activated = (hasattr(sys, 'real_prefix') or 
                   (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    print_check("Virtual environment is activated", is_activated,
                "Activate with: venv\\Scripts\\Activate.ps1 (Windows) or source venv/bin/activate (Linux/Mac)"
                if not is_activated else "")
    
    # Check pip in virtual environment
    if is_activated:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True)
            pip_ok = result.returncode == 0
            pip_version = result.stdout.strip() if pip_ok else "Not found"
            print_check("Pip is available", pip_ok, pip_version)
        except Exception:
            print_check("Pip is available", False, "Failed to check pip")
            pip_ok = False
    else:
        pip_ok = False
    
    return venv_exists and is_activated and pip_ok


def check_project_structure():
    """Check project directory structure."""
    print_header("Project Structure Check")
    
    required_files = [
        "requirements.txt",
        "pyproject.toml", 
        "README.md",
        "src/__init__.py"
    ]
    
    required_dirs = [
        "src",
        "src/journal",
        "src/utils",
        "tests",
        "tests/unit"
    ]
    
    all_good = True
    
    # Check files
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_check(f"File: {file_path}", exists)
        if not exists:
            all_good = False
    
    # Check directories
    for dir_path in required_dirs:
        exists = Path(dir_path).is_dir()
        print_check(f"Directory: {dir_path}", exists)
        if not exists:
            all_good = False
    
    return all_good


def check_dependencies():
    """Check if all required Python packages are installed."""
    print_header("Python Package Dependencies Check")
    
    # Core dependencies
    core_packages = [
        ("orjson", "High-performance JSON parsing"),
        ("watchdog", "File system monitoring"),
        ("pydantic", "Data validation and configuration"),
        ("aiofiles", "Async file operations")
    ]
    
    # Testing dependencies  
    test_packages = [
        ("pytest", "Testing framework"),
        ("pytest-asyncio", "Async testing support"),
        ("pytest-cov", "Coverage reporting")
    ]
    
    # Development dependencies
    dev_packages = [
        ("black", "Code formatting"),
        ("isort", "Import sorting"),
        ("flake8", "Code linting"),
        ("mypy", "Type checking")
    ]
    
    all_packages = core_packages + test_packages + dev_packages
    missing_packages = []
    
    for package_name, description in all_packages:
        try:
            result = subprocess.run([sys.executable, "-c", f"import {package_name}"], 
                                  capture_output=True, text=True)
            installed = result.returncode == 0
            
            if installed:
                # Try to get version
                try:
                    version_result = subprocess.run([sys.executable, "-c", 
                                                   f"import {package_name}; print(getattr({package_name}, '__version__', 'unknown'))"],
                                                  capture_output=True, text=True)
                    version = version_result.stdout.strip() if version_result.returncode == 0 else "unknown"
                except:
                    version = "unknown"
                
                print_check(f"{package_name} ({description})", True, f"Version: {version}")
            else:
                print_check(f"{package_name} ({description})", False, "Not installed")
                missing_packages.append(package_name)
                
        except Exception as e:
            print_check(f"{package_name} ({description})", False, f"Error: {e}")
            missing_packages.append(package_name)
    
    return len(missing_packages) == 0, missing_packages


def check_git_repository():
    """Check Git repository status."""
    print_header("Git Repository Check")
    
    # Check if we're in a git repository
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        is_git_repo = result.returncode == 0
        print_check("Git repository", is_git_repo)
        
        if is_git_repo:
            # Check current branch
            branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                         capture_output=True, text=True)
            if branch_result.returncode == 0:
                branch = branch_result.stdout.strip()
                print_check(f"Current branch: {branch}", True)
            
            # Check if there are uncommitted changes
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            clean_repo = len(status_lines) == 0 or (len(status_lines) == 1 and status_lines[0] == "")
            print_check("Repository is clean", clean_repo, 
                       f"{len(status_lines)} uncommitted changes" if not clean_repo else "")
        
        return is_git_repo
        
    except FileNotFoundError:
        print_check("Git is installed", False, "Git command not found")
        return False
    except Exception as e:
        print_check("Git repository", False, f"Error: {e}")
        return False


def main():
    """Main dependency checker function."""
    print("🔍 Elite Dangerous MCP Server - Dependency Checker")
    print(f"Checking system at: {Path.cwd()}")
    
    # Verify we're in the project root
    if not Path("src").exists() or not Path("requirements.txt").exists():
        print("\n❌ Error: Must be run from project root directory")
        print("   Current directory should contain 'src' folder and 'requirements.txt'")
        sys.exit(1)
    
    # Run all checks
    checks = []
    
    # Python version check
    python_ok = check_python_version()
    checks.append(("Python Version", python_ok))
    
    # Virtual environment check
    venv_ok = check_virtual_environment()
    checks.append(("Virtual Environment", venv_ok))
    
    # Project structure check
    structure_ok = check_project_structure()
    checks.append(("Project Structure", structure_ok))
    
    # Dependencies check
    deps_ok, missing_packages = check_dependencies()
    checks.append(("Python Dependencies", deps_ok))
    
    # Git repository check
    git_ok = check_git_repository()
    checks.append(("Git Repository", git_ok))
    
    # Summary
    print_header("Summary")
    
    all_passed = all(status for _, status in checks)
    
    for check_name, status in checks:
        print_check(check_name, status)
    
    print(f"\n{'='*50}")
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your environment is ready for development and testing")
        print("🚀 You can now run: python scripts/run_tests.py")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n📋 Recommended actions:")
        
        if not python_ok:
            print("   • Install Python 3.9+ from https://python.org")
        
        if not venv_ok:
            print("   • Run: python scripts/setup_dependencies.py")
            print("   • Then activate virtual environment")
        
        if not deps_ok and missing_packages:
            print(f"   • Install missing packages: {', '.join(missing_packages)}")
            print("   • Run: python scripts/setup_dependencies.py")
        
        if not structure_ok:
            print("   • Ensure you're in the correct project directory")
            print("   • Re-clone the repository if files are missing")
        
        if not git_ok:
            print("   • Install Git from https://git-scm.com")
    
    print(f"{'='*50}")
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
