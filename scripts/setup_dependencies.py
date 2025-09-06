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
from typing import List, Tuple, Dict
import re


class SetupTracker:
    """Track setup progress and errors."""
    
    def __init__(self):
        self.errors: List[Tuple[str, str]] = []
        self.warnings: List[Tuple[str, str]] = []
        self.successes: List[str] = []
    
    def add_error(self, step: str, message: str):
        """Add an error to the tracker."""
        self.errors.append((step, message))
    
    def add_warning(self, step: str, message: str):
        """Add a warning to the tracker."""
        self.warnings.append((step, message))
    
    def add_success(self, step: str):
        """Add a success to the tracker."""
        self.successes.append(step)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_critical_errors(self) -> bool:
        """Check if there are critical errors that should stop setup."""
        critical_steps = ['Python Version Check', 'Virtual Environment Setup', 'Dependency Installation']
        return any(step in critical_steps for step, _ in self.errors)
    
    def print_summary(self):
        """Print a summary of the setup process."""
        print("\n" + "="*60)
        
        if self.has_errors():
            print("❌ SETUP FAILED!")
        else:
            print("🎉 SETUP COMPLETE!")
        
        print("="*60)
        
        if self.successes:
            print("\n✅ Successful Steps:")
            for success in self.successes:
                print(f"   • {success}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for step, message in self.warnings:
                print(f"   • {step}: {message}")
        
        if self.errors:
            print("\n❌ Errors:")
            for step, message in self.errors:
                print(f"   • {step}: {message}")
            
            print("\n📋 Troubleshooting:")
            print("   1. Ensure you have Python 3.9+ installed")
            print("   2. Try running the script again")
            print("   3. Check your internet connection for package downloads")
            print("   4. Manually install packages: pip install -r requirements.txt")
            print("   5. Check for dependency conflicts: pip check")
        else:
            print("\n📋 Next steps:")
            print("   1. Activate virtual environment (see instructions above)")
            print("   2. Run: python scripts/check_dependencies.py")
            print("   3. Run: python scripts/run_tests.py")
        
        print("="*60)


# Global setup tracker
setup_tracker = SetupTracker()


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


def run_command(cmd, description, check=True, capture_output=True):
    """Run a command and return success status."""
    print(f"  Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        result = subprocess.run(
            cmd, 
            check=False,  # Don't raise exception on non-zero exit
            capture_output=capture_output,
            text=True,
            shell=True if isinstance(cmd, str) else False
        )
        
        if result.returncode == 0:
            print_status(f"{description} - Success")
            if capture_output and result.stdout.strip():
                # Only show first few lines of output to avoid spam
                output_lines = result.stdout.strip().split('\n')
                if len(output_lines) <= 3:
                    print(f"    Output: {result.stdout.strip()}")
                else:
                    print(f"    Output: {output_lines[0]}... ({len(output_lines)} lines)")
            return True
        else:
            print_status(f"{description} - Failed", False)
            if capture_output:
                if result.stderr.strip():
                    print(f"    Error: {result.stderr.strip()}")
                if result.stdout.strip():
                    print(f"    Output: {result.stdout.strip()}")
            return False
            
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
        setup_tracker.add_success("Python Version Check")
        return True
    else:
        print_status(f"Python {version_str} is too old (requires 3.9+)", False)
        print("  Please install Python 3.9+ from https://python.org")
        setup_tracker.add_error("Python Version Check", f"Python {version_str} is too old (requires 3.9+)")
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
            setup_tracker.add_success("Virtual Environment Setup")
            return True
        else:
            print_status("Virtual environment appears corrupted, recreating", False)
            setup_tracker.add_warning("Virtual Environment Setup", "Corrupted venv detected, recreating")
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
        setup_tracker.add_error("Virtual Environment Setup", "Failed to create virtual environment")
        return False
    
    print_status("Virtual environment created successfully")
    setup_tracker.add_success("Virtual Environment Setup")
    return True


def get_venv_python():
    """Get path to Python executable in virtual environment."""
    venv_path = Path("venv")
    
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "python.exe")
    else:
        return str(venv_path / "bin" / "python")


def upgrade_pip():
    """Upgrade pip in virtual environment."""
    print_header("Pip Upgrade")
    
    venv_python = get_venv_python()
    
    if not Path(venv_python).exists():
        print_status("Virtual environment Python not found", False)
        setup_tracker.add_error("Pip Upgrade", "Virtual environment Python not found")
        return False
    
    print_step("Upgrading", "pip, setuptools, and wheel")
    success = run_command([
        venv_python, "-m", "pip", "install", "--upgrade", 
        "pip", "setuptools", "wheel"
    ], "Upgrade pip and tools")
    
    if success:
        setup_tracker.add_success("Pip Upgrade")
    else:
        setup_tracker.add_warning("Pip Upgrade", "Failed to upgrade pip")
    
    return success


def parse_requirements_file():
    """Parse requirements.txt to get list of required packages."""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        return []
    
    packages = []
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Extract package name (everything before >=, ==, etc.)
                package_name = re.split(r'[><=!]', line)[0].strip()
                if package_name:
                    packages.append((package_name, line))
    
    return packages


def check_package_installed(package_name, venv_python):
    """Check if a specific package is installed."""
    try:
        result = subprocess.run([
            venv_python, "-c", f"import {package_name.replace('-', '_')}; print('OK')"
        ], capture_output=True, text=True, check=False)
        return result.returncode == 0
    except:
        return False


def install_requirements():
    """Install all requirements from requirements.txt."""
    print_header("Dependency Installation")
    
    venv_python = get_venv_python()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_status("requirements.txt not found", False)
        setup_tracker.add_error("Dependency Installation", "requirements.txt not found")
        return False
    
    if not Path(venv_python).exists():
        print_status("Virtual environment Python not found", False)
        setup_tracker.add_error("Dependency Installation", "Virtual environment Python not found")
        return False
    
    # Parse requirements to know what packages we expect
    required_packages = parse_requirements_file()
    print(f"  Found {len(required_packages)} packages in requirements.txt")
    
    print_step("Installing", "All dependencies from requirements.txt")
    
    # Try to install everything at once
    success = run_command([
        venv_python, "-m", "pip", "install", "-r", "requirements.txt"
    ], "Install all requirements")
    
    # Now verify what actually got installed
    print_step("Verifying", "Package installation")
    
    missing_packages = []
    installed_packages = []
    
    for package_name, requirement_line in required_packages:
        if check_package_installed(package_name, venv_python):
            installed_packages.append(package_name)
            print_status(f"{package_name} - Installed")
        else:
            missing_packages.append((package_name, requirement_line))
            print_status(f"{package_name} - Missing", False)
    
    print(f"  ✅ Installed: {len(installed_packages)} packages")
    print(f"  ❌ Missing: {len(missing_packages)} packages")
    
    # If packages are missing, try to install them individually
    if missing_packages:
        print_step("Retrying", "Installing missing packages individually")
        
        remaining_failures = []
        for package_name, requirement_line in missing_packages:
            print(f"  Attempting to install: {package_name}")
            install_success = run_command([
                venv_python, "-m", "pip", "install", requirement_line
            ], f"Install {package_name}")
            
            # Verify it actually got installed
            if install_success and check_package_installed(package_name, venv_python):
                print_status(f"{package_name} - Successfully installed")
                installed_packages.append(package_name)
            else:
                print_status(f"{package_name} - Failed to install", False)
                remaining_failures.append(package_name)
        
        if remaining_failures:
            setup_tracker.add_error("Dependency Installation", 
                                   f"Failed to install: {', '.join(remaining_failures)}")
            
            # Run pip check to see if there are dependency conflicts
            print_step("Checking", "Dependency conflicts")
            run_command([venv_python, "-m", "pip", "check"], "Check dependencies", check=False)
            
            return False
    
    if success and not missing_packages:
        print_status("All dependencies installed successfully")
        setup_tracker.add_success("Dependency Installation")
        return True
    elif missing_packages:
        setup_tracker.add_error("Dependency Installation", "Some packages failed to install")
        return False
    else:
        setup_tracker.add_success("Dependency Installation")
        return True


def verify_installation():
    """Verify that all critical packages are installed."""
    print_header("Installation Verification")
    
    venv_python = get_venv_python()
    
    if not Path(venv_python).exists():
        print_status("Virtual environment Python not found", False)
        setup_tracker.add_error("Installation Verification", "Virtual environment Python not found")
        return False
    
    # Get all required packages from requirements.txt
    required_packages = parse_requirements_file()
    
    # Test critical imports
    critical_imports = [
        ("orjson", "High-performance JSON parsing"),
        ("watchdog", "File system monitoring"),
        ("pydantic", "Data validation"),
        ("pydantic_settings", "Pydantic settings support"),
        ("pytest", "Testing framework"),
        ("pytest_asyncio", "Async testing"),
        ("pytest_cov", "Coverage reporting"),
    ]
    
    package_failures = []
    for package, description in critical_imports:
        success = run_command([
            venv_python, "-c", f"import {package}; print(f'{package} OK')"
        ], f"Test {package} import", check=False)
        
        if success:
            print_status(f"{package} ({description})")
        else:
            print_status(f"{package} ({description}) - Failed", False)
            package_failures.append(package)
    
    # Test project imports
    print_step("Testing", "Project imports")
    project_imports = [
        "src",
        "src.journal",
        "src.utils.config"
    ]
    
    project_failures = []
    for module in project_imports:
        success = run_command([
            venv_python, "-c", f"import {module}; print(f'{module} OK')"
        ], f"Test {module} import", check=False)
        
        if success:
            print_status(f"Project module: {module}")
        else:
            print_status(f"Project module: {module} - Failed", False)
            project_failures.append(module)
    
    # Add errors to tracker
    if package_failures:
        setup_tracker.add_error("Installation Verification", 
                               f"Failed package imports: {', '.join(package_failures)}")
    
    if project_failures:
        setup_tracker.add_error("Installation Verification", 
                               f"Failed project imports: {', '.join(project_failures)}")
    
    if not package_failures and not project_failures:
        setup_tracker.add_success("Installation Verification")
        return True
    
    return False


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
        setup_tracker.add_error("Directory Check", "Not in project root directory")
        setup_tracker.print_summary()
        sys.exit(1)
    
    # Check Python version
    if not check_python_version():
        setup_tracker.print_summary()
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        setup_tracker.print_summary()
        sys.exit(1)
    
    # Upgrade pip
    upgrade_pip()  # Continue even if this fails
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Critical error: Failed to install required dependencies")
        setup_tracker.print_summary()
        sys.exit(1)
    
    # Verify installation
    verify_installation()  # Continue even if some verifications fail
    
    # Show activation instructions
    create_activation_instructions()
    
    # Final summary
    setup_tracker.print_summary()
    
    # Exit with appropriate code
    if setup_tracker.has_errors():
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        setup_tracker.add_error("Setup Process", "Interrupted by user")
        setup_tracker.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        setup_tracker.add_error("Setup Process", f"Unexpected error: {e}")
        setup_tracker.print_summary()
        sys.exit(1)
