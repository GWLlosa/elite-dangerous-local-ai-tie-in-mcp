# Scripts Directory

This directory contains automation scripts for the Elite Dangerous Local AI Tie-In MCP project.

## 🔧 Available Scripts

### `setup_dependencies.py`
**Purpose**: Sets up all dependencies for the project  
**Usage**: `python scripts/setup_dependencies.py`  
**Features**:
- ✅ Creates virtual environment if missing
- ✅ Installs all required Python packages
- ✅ Verifies installation with import tests
- ✅ Safe to run multiple times
- ✅ Cross-platform compatible (Windows/Linux/Mac)

**When to use**: First time setup or when dependencies are missing

### `check_dependencies.py`
**Purpose**: Verifies all dependencies are properly installed  
**Usage**: `python scripts/check_dependencies.py`  
**Features**:
- ✅ Checks Python version (requires 3.9+)
- ✅ Verifies virtual environment status
- ✅ Validates project structure
- ✅ Tests all package imports
- ✅ Checks Git repository status

**When to use**: To diagnose dependency issues or verify environment

### `run_tests.py`
**Purpose**: Runs the complete test suite with detailed progress  
**Usage**: `python scripts/run_tests.py`  
**Features**:
- ✅ Step-by-step progress reporting
- ✅ Environment verification
- ✅ Individual component testing
- ✅ Complete test suite execution
- ✅ Coverage report generation
- ✅ Clear success/failure feedback

**When to use**: To validate all functionality is working correctly

## 🚀 Quick Start Workflow

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

## 📋 Script Requirements

### Prerequisites:
- **Python 3.9+** installed on system
- **Git** installed (for repository operations)
- **Internet connection** (for downloading packages)

### Platform Support:
- ✅ **Windows 11** with PowerShell
- ✅ **Linux** (Ubuntu, etc.)
- ✅ **macOS**

## 🛡️ Safety Features

All scripts include:
- ✅ **Pre-flight checks** to verify environment
- ✅ **Error handling** with helpful messages
- ✅ **Safe re-execution** - won't break existing setups
- ✅ **Clear progress reporting** with status indicators
- ✅ **Graceful failure** with recovery suggestions

## 📊 Expected Output

### Successful Setup:
```
🎉 SETUP COMPLETE!
✅ Virtual environment created and configured
✅ Dependencies installed
✅ Project imports working
```

### Successful Dependency Check:
```
🎉 ALL CHECKS PASSED!
✅ Your environment is ready for development and testing
🚀 You can now run: python scripts/run_tests.py
```

### Successful Test Run:
```
🎉 ALL TESTS COMPLETED SUCCESSFULLY!
⏱️  Total execution time: 15.23 seconds
📊 Coverage report generated in: htmlcov/index.html
✅ All milestones 1-4 functionality verified
```

## 🔍 Troubleshooting

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

## 🎯 Integration with Testing Guide

These scripts are referenced in the comprehensive testing guide located at:
- `docs/TESTING_GUIDE.md`

The testing guide provides detailed step-by-step instructions for manual setup, while these scripts provide automated alternatives for common tasks.
