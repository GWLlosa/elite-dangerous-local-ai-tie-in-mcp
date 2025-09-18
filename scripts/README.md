# Scripts Directory

This directory contains automation scripts for the Elite Dangerous Local AI Tie-In MCP project.

##  Available Scripts

### `setup_dependencies.py`
**Purpose**: Sets up all dependencies for the project  
**Usage**: `python scripts/setup_dependencies.py`  
**Features**:
- [OK] Creates virtual environment if missing
- [OK] Installs all required Python packages
- [OK] Verifies installation with import tests
- [OK] Safe to run multiple times
- [OK] Cross-platform compatible (Windows/Linux/Mac)

**When to use**: First time setup or when dependencies are missing

### `check_dependencies.py`
**Purpose**: Verifies all dependencies are properly installed  
**Usage**: `python scripts/check_dependencies.py`  
**Features**:
- [OK] Checks Python version (requires 3.9+)
- [OK] Verifies virtual environment status
- [OK] Validates project structure
- [OK] Tests all package imports
- [OK] Checks Git repository status

**When to use**: To diagnose dependency issues or verify environment

### `run_tests.py`
**Purpose**: Runs the complete test suite with detailed progress  
**Usage**: `python scripts/run_tests.py`  
**Features**:
- [OK] Step-by-step progress reporting
- [OK] Environment verification
- [OK] Individual component testing
- [OK] Complete test suite execution
- [OK] Coverage report generation
- [OK] Clear success/failure feedback

**When to use**: To validate all functionality is working correctly

### `generate_edcopilot.py`
**Purpose**: Headless EDCoPilot chatter generation without Claude Desktop  
**Usage**: `python scripts/generate_edcopilot.py [options]`  
**Defaults**:
- Time window: last 7 days
- Theme: "Grizzled Veteran Space Captain"
- Context: "Worn Hands, Endless Horizon"
**Examples**:
- `python scripts/generate_edcopilot.py`
- `python scripts/generate_edcopilot.py --hours 12 --theme "Corporate Fixer" --context "Cold Calculus, Clean Ledger"`
- `python scripts/generate_edcopilot.py --from "2025-09-10" --to "2025-09-13 18:00" --output-dir C:\\temp\\edc --dry-run`
**Notes**:
- Dates are provided in local time and converted to UTC internally
- ASCII-only output and backups are enforced by default
- See `docs/HEADLESS_CLI.md` for all options and examples

##  Quick Start Workflow

### For New Setup:
```powershell
# 1. Clone repository
git clone https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp.git
cd elite-dangerous-local-ai-tie-in-mcp

# 2. Setup dependencies
python scripts/setup_dependencies.py

# 3. Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# 4. Verify everything works
python scripts/run_tests.py
```

### For Troubleshooting:
```powershell
# Check what's wrong
python scripts/check_dependencies.py

# Fix any issues
python scripts/setup_dependencies.py

# Verify fix
python scripts/run_tests.py
```

##  Script Requirements

### Prerequisites:
- **Python 3.9+** installed on system
- **Git** installed (for repository operations)
- **Internet connection** (for downloading packages)

### Platform Support:
- [OK] **Windows 11** with PowerShell
- [OK] **Linux** (Ubuntu, etc.)
- [OK] **macOS**

##  Safety Features

All scripts include:
- [OK] **Pre-flight checks** to verify environment
- [OK] **Error handling** with helpful messages
- [OK] **Safe re-execution** - won't break existing setups
- [OK] **Clear progress reporting** with status indicators
- [OK] **Graceful failure** with recovery suggestions

##  Expected Output

### Successful Setup:
```
 SETUP COMPLETE!
[OK] Virtual environment created and configured
[OK] Dependencies installed
[OK] Project imports working
```

### Successful Dependency Check:
```
 ALL CHECKS PASSED!
[OK] Your environment is ready for development and testing
 You can now run: python scripts/run_tests.py
```

### Successful Test Run:
```
 ALL TESTS COMPLETED SUCCESSFULLY!
  Total execution time: 15.23 seconds
 Coverage report generated in: htmlcov/index.html
[OK] All implemented functionality verified and working
```

##  Troubleshooting

### Common Issues:

**"Virtual environment not activated"**
- Run: `python scripts/setup_dependencies.py`
- Then activate: `.\venv\Scripts\Activate.ps1` (Windows)

**"Module not found" errors**
- Run: `python scripts/check_dependencies.py`
- Then: `python scripts/setup_dependencies.py`

**"Permission denied" on Windows**
- Run PowerShell as Administrator
- Or set execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Python version too old**
- Install Python 3.9+ from https://python.org
- Ensure it's in your PATH

### Getting Help:
1. Run `python scripts/check_dependencies.py` for detailed diagnostics
2. Check the error messages - they include specific remediation steps
3. Ensure you're running from the project root directory
4. Verify Python 3.9+ is installed and accessible

##  Integration with Testing Guide

These scripts are referenced in the comprehensive testing guide located at:
- `docs/TESTING_GUIDE.md`

The testing guide provides detailed step-by-step instructions for manual setup, while these scripts provide automated alternatives for common tasks.

