#!/usr/bin/env python3
"""
Elite Dangerous MCP Server - Dependency Setup

This script sets up all dependencies for the project.
It is safe to run multiple times - it will only install what's missing.

Usage:
    python scripts/setup_dependencies.py

Requirements:
    - Python 3.9+ must be installed
    - Must be run from project root directory
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)


def print_step(step, description):
    """Print a formatted step."""
    print(f"\n→ {step}: {description}")


def print_status(message, success=True):
    """Print a status message."""
    icon = "✅" if success else "❌"
    print(f"  {icon} {message}")


def run_command(cmd, description, check=True):
    """Run a command and return success status."""
    print(f"  Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        result = subprocess.run(
            cmd, 
            check=False,  # Don't raise exception on non-zero exit
            capture_output=True,
            text=True,
            shell=True if isinstance(cmd, str) else False
        )
        
        if result.returncode == 0:
            print_status(f"{description} - Success")
            if result.stdout.strip():
                print(f"    Output: {result.stdout.strip()}")
            return True
        else:
            print_status(f"{description} - Failed", False)
            if result.stderr.strip():
                print(f"    Error: {result.stderr.strip()}")
            if check:
                return False
            return True  # Continue despite failure if check=False
            
    except Exception as e:
        print_status(f"{description} - Error: {e}", False)
        return False


def check_python_version():
    """Check if Python version is suitable."""
    print_header("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 9:
        print_status(f"Python {version_str} is suitable")
        return True
    else:
        print_status(f"Python {version_str} is too old (requires 3.9+)", False)
        print("  Please install Python 3.9+ from https://python.org")
        return False


def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist."""
    print_header("Virtual Environment Setup")
    
    venv_path = Path("venv")
    
    # Check if virtual environment already exists
    if venv_path.exists():
        print_status("Virtual environment already exists")
        
        # Check if it's a valid virtual environment
        if platform.system() == "Windows":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        if python_exe.exists():
            print_status("Virtual environment appears valid")
            return True
        else:
            print_status("Virtual environment appears corrupted, recreating", False)
            # Remove corrupted venv
            import shutil
            shutil.rmtree(venv_path)
    
    # Create virtual environment
    print_step("Creating", "New virtual environment")
    success = run_command([sys.executable, "-m", "venv", "venv"], 
                         "Create virtual environment")
    
    if not success:
        print_status("Failed to create virtual environment", False)
        print("  Ensure you have the 'venv' module available")
        return False
    
    print_status("Virtual environment created successfully")
    return True


def get_venv_python():
    """Get path to Python executable in virtual environment."""
    venv_path = Path("venv")
    
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "python.exe")
    else:
        return str(venv_path / "bin" / "python")


def get_venv_pip():
    """Get path to pip executable in virtual environment."""
    venv_path = Path("venv")
    
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "pip.exe")
    else:
        return str(venv_path / "bin" / "pip")


def upgrade_pip():
    """Upgrade pip in virtual environment."""
    print_header("Pip Upgrade")
    
    venv_python = get_venv_python()
    
    if not Path(venv_python).exists():
        print_status("Virtual environment Python not found", False)
        return False
    
    print_step("Upgrading", "pip, setuptools, and wheel")
    success = run_command([
        venv_python, "-m", "pip", "install", "--upgrade", 
        "pip", "setuptools", "wheel"
    ], "Upgrade pip and tools")
    
    return success


def install_requirements():
    """Install all requirements from requirements.txt."""
    print_header("Dependency Installation")
    
    venv_python = get_venv_python()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_status("requirements.txt not found", False)
        return False
    
    if not Path(venv_python).exists():
        print_status("Virtual environment Python not found", False)
        return False
    
    print_step("Installing", "All dependencies from requirements.txt")
    
    # First, try to install everything at once
    success = run_command([
        venv_python, "-m", "pip", "install", "-r", "requirements.txt"
    ], "Install all requirements", check=False)
    
    if success:
        print_status("All dependencies installed successfully")
        return True
    
    # If batch install failed, try installing core packages individually
    print_step("Retrying", "Installing core packages individually")
    
    core_packages = [
        "orjson>=3.10.0",
        "watchdog>=4.0.0", 
        "pydantic>=2.6.0",
        "aiofiles>=24.1.0",
        "pytest>=8.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0"
    ]
    
    all_success = True
    for package in core_packages:
        success = run_command([
            venv_python, "-m", "pip", "install", package
        ], f"Install {package.split('>=')[0]}", check=False)
        
        if not success:
            all_success = False
    
    # Try to install remaining packages (development tools)
    dev_packages = [
        "black>=24.0.0",
        "isort>=5.13.0", 
        "flake8>=7.0.0",
        "mypy>=1.8.0"
    ]
    
    print_step("Installing", "Development tools (optional)")
    for package in dev_packages:
        run_command([
            venv_python, "-m", "pip", "install", package
        ], f"Install {package.split('>=')[0]}", check=False)
    
    return all_success


def verify_installation():
    """Verify that all critical packages are installed."""
    print_header("Installation Verification")
    
    venv_python = get_venv_python()
    
    if not Path(venv_python).exists():
        print_status("Virtual environment Python not found", False)
        return False
    
    # Test critical imports
    critical_packages = [
        ("orjson", "High-performance JSON parsing"),
        ("watchdog", "File system monitoring"),
        ("pydantic", "Data validation"),
        ("pytest", "Testing framework"),
        ("pytest_asyncio", "Async testing"),
    ]
    
    all_good = True
    for package, description in critical_packages:
        success = run_command([
            venv_python, "-c", f"import {package}; print(f'{package} OK')"
        ], f"Test {package} import", check=False)
        
        if success:
            print_status(f"{package} ({description})")
        else:
            print_status(f"{package} ({description}) - Failed", False)
            all_good = False
    
    # Test project imports
    print_step("Testing", "Project imports")
    project_imports = [
        "src",
        "src.journal",
        "src.utils.config"
    ]
    
    for module in project_imports:
        success = run_command([
            venv_python, "-c", f"import {module}; print(f'{module} OK')"
        ], f"Test {module} import", check=False)
        
        if success:
            print_status(f"Project module: {module}")
        else:
            print_status(f"Project module: {module} - Failed", False)
            all_good = False
    
    return all_good


def create_activation_instructions():
    """Create instructions for activating the virtual environment."""
    print_header("Virtual Environment Activation")
    
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_status("Virtual environment not found", False)
        return
    
    print("📋 To activate the virtual environment:")
    print()
    
    if platform.system() == "Windows":
        print("   PowerShell:")
        print("   .\\venv\\Scripts\\Activate.ps1")
        print()
        print("   Command Prompt:")
        print("   venv\\Scripts\\activate.bat")
    else:
        print("   Bash/Zsh:")
        print("   source venv/bin/activate")
    
    print()
    print("📋 To deactivate the virtual environment:")
    print("   deactivate")
    print()
    print("📋 To run tests (with virtual environment activated):")
    print("   python scripts/run_tests.py")


def main():
    """Main setup function."""
    print("🔧 Elite Dangerous MCP Server - Dependency Setup")
    print(f"Setting up environment at: {Path.cwd()}")
    
    # Verify we're in the project root
    if not Path("src").exists() or not Path("requirements.txt").exists():
        print("\n❌ Error: Must be run from project root directory")
        print("   Current directory should contain 'src' folder and 'requirements.txt'")
        sys.exit(1)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        print("\n❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Upgrade pip
    if not upgrade_pip():
        print("\n⚠️  Warning: Failed to upgrade pip, continuing anyway")
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Critical error: Failed to install required dependencies")
        print("   Some core packages may be missing")
        print("   Try running again or install packages manually")
    
    # Verify installation
    if verify_installation():
        print_status("All critical dependencies verified")
    else:
        print_status("Some dependencies may be missing", False)
    
    # Show activation instructions
    create_activation_instructions()
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("✅ Virtual environment created and configured")
    print("✅ Dependencies installed")
    print("✅ Project imports working")
    print()
    print("📋 Next steps:")
    print("   1. Activate virtual environment (see instructions above)")
    print("   2. Run: python scripts/check_dependencies.py")
    print("   3. Run: python scripts/run_tests.py")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        print("   Try running the script again or install dependencies manually")
        sys.exit(1)
