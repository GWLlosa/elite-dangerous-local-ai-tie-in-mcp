#!/usr/bin/env python3
"""
Elite Dangerous MCP Server - Dependency Checker (ASCII-only output)

Run from the project root directory.

Usage:
    python scripts/check_dependencies.py
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path


PACKAGE_IMPORT_MAP = {
    "python-dateutil": "dateutil",
    "pydantic-settings": "pydantic_settings",
    "pytest-asyncio": "pytest_asyncio",
    "pytest-cov": "pytest_cov",
}


def get_import_name(package_name: str) -> str:
    if package_name in PACKAGE_IMPORT_MAP:
        return PACKAGE_IMPORT_MAP[package_name]
    return package_name.replace("-", "_")


def print_header(title: str) -> None:
    print("\n" + ("=" * 50))
    print(f"[INFO] {title}")
    print("=" * 50)


def print_check(description: str, status: bool, details: str = "") -> None:
    tag = "[SUCCESS]" if status else "[FAILED]"
    print(f"{tag} {description}")
    if details:
        print(f"   {details}")


def check_python_version() -> bool:
    print_header("Python Environment Check")
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    py_ok = v.major == 3 and v.minor >= 9
    print_check(f"Python Version: {version_str}", py_ok, "Requires Python 3.9+" if not py_ok else "")
    print_check(f"Platform: {platform.system()} {platform.release()}", True)
    print_check(f"Python Executable: {sys.executable}", True)
    return py_ok


def check_virtual_environment() -> bool:
    print_header("Virtual Environment Check")
    venv_path = Path("venv")
    venv_exists = venv_path.exists()
    print_check("Virtual environment directory exists", venv_exists, "Run: python scripts/setup_dependencies.py" if not venv_exists else str(venv_path))

    is_activated = (hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))
    print_check("Virtual environment is activated", is_activated, "Activate with: venv\\Scripts\\Activate.ps1 (Windows) or source venv/bin/activate (Linux/Mac)" if not is_activated else "")

    pip_ok = False
    if is_activated:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
            pip_ok = result.returncode == 0
            pip_version = result.stdout.strip() if pip_ok else "Not found"
            print_check("Pip is available", pip_ok, pip_version)
        except Exception:
            print_check("Pip is available", False, "Failed to check pip")
            pip_ok = False
    return venv_exists and is_activated and pip_ok


def check_project_structure() -> bool:
    print_header("Project Structure Check")
    required_files = [
        "requirements.txt",
        "pyproject.toml",
        "README.md",
        "src/__init__.py",
    ]
    required_dirs = [
        "src",
        "tests",
        "tests/unit",
    ]

    ok = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_check(f"File: {file_path}", exists)
        ok = ok and exists
    for dir_path in required_dirs:
        exists = Path(dir_path).is_dir()
        print_check(f"Directory: {dir_path}", exists)
        ok = ok and exists
    return ok


def check_dependencies() -> tuple[bool, list[str]]:
    print_header("Python Package Dependencies Check")
    core_packages = [
        ("orjson", "High-performance JSON parsing"),
        ("watchdog", "File system monitoring"),
        ("pydantic", "Data validation and configuration"),
        ("aiofiles", "Async file operations"),
    ]
    test_packages = [
        ("pytest", "Testing framework"),
        ("pytest-asyncio", "Async testing support"),
        ("pytest-cov", "Coverage reporting"),
    ]
    dev_packages = [
        ("black", "Code formatting"),
        ("isort", "Import sorting"),
        ("flake8", "Code linting"),
        ("mypy", "Type checking"),
    ]

    all_packages = core_packages + test_packages + dev_packages
    missing: list[str] = []
    for package_name, description in all_packages:
        import_name = get_import_name(package_name)
        try:
            result = subprocess.run([sys.executable, "-c", f"import {import_name}"], capture_output=True, text=True)
            installed = result.returncode == 0
            if installed:
                try:
                    vr = subprocess.run(
                        [sys.executable, "-c", f"import {import_name}; print(getattr({import_name}, '__version__', 'unknown'))"],
                        capture_output=True,
                        text=True,
                    )
                    version = vr.stdout.strip() if vr.returncode == 0 else "unknown"
                except Exception:
                    version = "unknown"
                print_check(f"{package_name} ({description})", True, f"Version: {version}")
            else:
                print_check(f"{package_name} ({description})", False, "Not installed")
                missing.append(package_name)
        except Exception as e:
            print_check(f"{package_name} ({description})", False, f"Error: {e}")
            missing.append(package_name)
    return (len(missing) == 0, missing)


def check_git_repository() -> bool:
    print_header("Git Repository Check")
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        is_repo = result.returncode == 0
        print_check("Git repository", is_repo)
        if is_repo:
            branch_result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            if branch_result.returncode == 0:
                branch = branch_result.stdout.strip()
                print_check(f"Current branch: {branch}", True)
            status_lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            clean_repo = len(status_lines) == 0 or (len(status_lines) == 1 and status_lines[0] == "")
            print_check("Repository is clean", clean_repo, f"{len(status_lines)} uncommitted changes" if not clean_repo else "")
        return is_repo
    except FileNotFoundError:
        print_check("Git is installed", False, "Git command not found")
        return False
    except Exception as e:
        print_check("Git repository", False, f"Error: {e}")
        return False


def main() -> None:
    print("[INFO] Elite Dangerous MCP Server - Dependency Checker")
    print(f"[INFO] Checking system at: {Path.cwd()}")
    if not Path("src").exists() or not Path("requirements.txt").exists():
        print("\n[FAILED] Must be run from project root directory")
        print("   Current directory should contain 'src' folder and 'requirements.txt'")
        sys.exit(1)

    checks: list[tuple[str, bool]] = []
    python_ok = check_python_version(); checks.append(("Python Version", python_ok))
    venv_ok = check_virtual_environment(); checks.append(("Virtual Environment", venv_ok))
    structure_ok = check_project_structure(); checks.append(("Project Structure", structure_ok))
    deps_ok, missing_packages = check_dependencies(); checks.append(("Python Dependencies", deps_ok))
    git_ok = check_git_repository(); checks.append(("Git Repository", git_ok))

    print_header("Summary")
    all_passed = all(status for _, status in checks)
    for name, status in checks:
        print_check(name, status)

    print("\n" + ("=" * 50))
    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED")
        print("[INFO] Environment is ready for development and testing")
        print("[INFO] Next: python scripts/run_tests.py")
    else:
        print("[FAILED] SOME CHECKS FAILED")
        print("\n[INFO] Recommended actions:")
        if not python_ok:
            print("   - Install Python 3.9+ from https://python.org")
        if not venv_ok:
            print("   - Run: python scripts/setup_dependencies.py")
            print("   - Then activate the virtual environment")
        if not deps_ok and missing_packages:
            print(f"   - Install missing packages: {', '.join(missing_packages)}")
            print("   - Or run: python scripts/setup_dependencies.py")
        if not structure_ok:
            print("   - Ensure you are in the correct project directory")
            print("   - Re-clone the repository if files are missing")
        if not git_ok:
            print("   - Install Git from https://git-scm.com")
    print("=" * 50)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[FAILED] Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FAILED] Unexpected error: {e}")
        sys.exit(1)

