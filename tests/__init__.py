"""
Test Suite for Elite Dangerous Local AI Tie-In MCP

This package contains unit tests, integration tests, and mock data for testing
the Elite Dangerous MCP server functionality.

Test Structure:
- unit/: Unit tests for individual components
- integration/: Integration tests for end-to-end functionality  
- mock_data/: Sample Elite Dangerous journal files and test data

The comprehensive test suite will be implemented in Milestone 14.
"""

# Test package version
__version__ = "0.1.0"

# Test configuration
TEST_DATA_DIR = "tests/mock_data"
MOCK_JOURNAL_DIR = "tests/mock_data/journals"
MOCK_EDCOPILOT_DIR = "tests/mock_data/edcopilot"

# Test utilities will be added in Milestone 14
__all__ = [
    "TEST_DATA_DIR",
    "MOCK_JOURNAL_DIR", 
    "MOCK_EDCOPILOT_DIR",
]