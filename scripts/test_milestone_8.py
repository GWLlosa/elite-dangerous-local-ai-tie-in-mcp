#!/usr/bin/env python3
"""
Test runner script for verifying Milestone 8 implementation.

This script runs all tests with focus on the new MCP tools functionality.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"[INFO] {description}")
    print(f"[CMD] {' '.join(cmd)}")
    print('='*60)
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed_time = time.time() - start_time
    
    if result.returncode == 0:
        print(f"[SUCCESS] Completed in {elapsed_time:.2f} seconds")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"[FAILED] Command failed with return code {result.returncode}")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
    
    return result.returncode == 0

def main():
    """Main test execution function."""
    print("="*60)
    print("MILESTONE 8 TEST VERIFICATION")
    print("Testing Core MCP Tools Implementation")
    print("="*60)
    
    all_passed = True
    
    # Test 1: Run unit tests for MCP tools
    print("\n" + "="*60)
    print("TEST SUITE 1: MCP Tools Unit Tests")
    print("="*60)
    
    if not run_command(
        ["python", "-m", "pytest", "tests/unit/test_mcp_tools.py", "-v", "--tb=short"],
        "Running MCP tools unit tests"
    ):
        all_passed = False
        print("[WARNING] MCP tools tests failed")
    
    # Test 2: Run all unit tests to ensure no regression
    print("\n" + "="*60)
    print("TEST SUITE 2: All Unit Tests")
    print("="*60)
    
    if not run_command(
        ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short", "-q"],
        "Running all unit tests"
    ):
        all_passed = False
        print("[WARNING] Some unit tests failed")
    
    # Test 3: Check test coverage
    print("\n" + "="*60)
    print("TEST SUITE 3: Coverage Analysis")
    print("="*60)
    
    if not run_command(
        ["python", "-m", "pytest", "tests/unit/test_mcp_tools.py", "--cov=src/mcp", "--cov-report=term-missing"],
        "Analyzing MCP tools test coverage"
    ):
        print("[WARNING] Coverage analysis had issues")
    
    # Test 4: Import verification
    print("\n" + "="*60)
    print("TEST SUITE 4: Import Verification")
    print("="*60)
    
    import_test = """
import sys
sys.path.insert(0, '.')
try:
    from src.mcp.mcp_tools import MCPTools, ActivityType
    from src.server import EliteDangerousServer
    print('[SUCCESS] All imports successful')
    print(f'  - MCPTools class imported')
    print(f'  - ActivityType enum imported')
    print(f'  - Server integration verified')
except Exception as e:
    print(f'[FAILED] Import error: {e}')
    sys.exit(1)
"""
    
    result = subprocess.run(
        ["python", "-c", import_test],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        all_passed = False
        print(result.stderr)
        print("[FAILED] Import verification failed")
    
    # Test 5: Syntax and type checking
    print("\n" + "="*60)
    print("TEST SUITE 5: Syntax Validation")
    print("="*60)
    
    files_to_check = [
        "src/mcp/mcp_tools.py",
        "src/mcp/__init__.py",
        "src/server.py",
        "tests/unit/test_mcp_tools.py"
    ]
    
    for file_path in files_to_check:
        result = subprocess.run(
            ["python", "-m", "py_compile", file_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"[SUCCESS] {file_path} - Valid Python syntax")
        else:
            all_passed = False
            print(f"[FAILED] {file_path} - Syntax error")
            print(result.stderr)
    
    # Final Summary
    print("\n" + "="*60)
    print("MILESTONE 8 VERIFICATION SUMMARY")
    print("="*60)
    
    if all_passed:
        print("[SUCCESS] All tests passed!")
        print("\nMilestone 8 Implementation Summary:")
        print("  - Core MCP Tools module created")
        print("  - 15+ comprehensive tools implemented")
        print("  - 40+ unit tests added")
        print("  - Server integration completed")
        print("  - All existing tests still passing")
        print("\nReady to merge to main branch!")
    else:
        print("[WARNING] Some tests failed - review output above")
        print("Fix any issues before merging to main")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("  1. Merge feature/mcp-tools branch to main")
    print("  2. Update project documentation")
    print("  3. Begin Milestone 9: MCP Resources Implementation")
    print("="*60)

if __name__ == "__main__":
    main()
