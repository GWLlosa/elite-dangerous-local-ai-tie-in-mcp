#!/usr/bin/env python3
"""
Test script for Milestone 10: MCP Prompts Implementation

Runs comprehensive tests to verify MCP prompts functionality.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_section(title):
    """Print a formatted section header."""
    print()
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)


def test_imports():
    """Test that all required modules can be imported."""
    print_section("Testing Module Imports")
    
    modules_to_test = [
        ("src.mcp.mcp_prompts", "MCPPrompts"),
        ("src.mcp.mcp_prompts", "PromptTemplate"),
        ("src.mcp.mcp_prompts", "PromptType"),
        ("src.server", "EliteDangerousServer"),
    ]
    
    all_passed = True
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"[SUCCESS] {module_name}.{class_name} imported successfully")
            else:
                print(f"[FAILED] {class_name} not found in {module_name}")
                all_passed = False
        except ImportError as e:
            print(f"[FAILED] Could not import {module_name}: {e}")
            all_passed = False
    
    return all_passed


def test_prompt_templates():
    """Test that prompt templates are correctly defined."""
    print_section("Testing Prompt Templates")
    
    try:
        from src.mcp.mcp_prompts import MCPPrompts
        from src.utils.data_store import DataStore
        
        # Create mock data store
        data_store = DataStore()
        prompts = MCPPrompts(data_store)
        
        # Check template count
        template_count = len(prompts.templates)
        print(f"[INFO] Found {template_count} prompt templates")
        
        if template_count < 9:
            print(f"[WARNING] Expected at least 9 templates, found {template_count}")
            return False
        
        # Check required templates exist
        required_templates = [
            "exploration_analysis",
            "trading_strategy",
            "combat_assessment", 
            "mining_optimization",
            "mission_guidance",
            "engineering_progress",
            "journey_review",
            "performance_review",
            "strategic_planning"
        ]
        
        all_found = True
        for template_id in required_templates:
            if template_id in prompts.templates:
                template = prompts.templates[template_id]
                print(f"[SUCCESS] Found template: {template_id} - {template.name}")
                
                # Validate template structure
                if not template.name or not template.description or not template.template:
                    print(f"[FAILED] Template {template_id} has missing content")
                    all_found = False
                elif len(template.template) < 100:
                    print(f"[FAILED] Template {template_id} content too short")
                    all_found = False
                elif not template.variables:
                    print(f"[FAILED] Template {template_id} has no variables")
                    all_found = False
            else:
                print(f"[FAILED] Missing template: {template_id}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"[FAILED] Error testing prompt templates: {e}")
        return False


def test_prompt_generation():
    """Test actual prompt generation functionality."""
    print_section("Testing Prompt Generation")
    
    try:
        import asyncio
        from src.mcp.mcp_prompts import MCPPrompts
        from src.utils.data_store import DataStore
        from unittest.mock import Mock
        from datetime import datetime, timezone
        
        async def test_generation():
            # Create mock data store with test data
            data_store = Mock(spec=DataStore)
            
            # Mock game state
            game_state = Mock()
            game_state.current_system = "Sol"
            game_state.current_ship = "Python"
            game_state.credits = 1000000
            game_state.hull_health = 100.0
            game_state.fuel_level = 32.0
            game_state.ranks = {"Combat": "Elite", "Trade": "Tycoon", "Explore": "Pioneer"}
            game_state.last_updated = datetime.now(timezone.utc)
            data_store.get_game_state.return_value = game_state
            
            # Mock events
            data_store.get_all_events.return_value = []
            data_store.get_events_by_type.return_value = []
            
            prompts = MCPPrompts(data_store)
            
            # Test each template
            templates_to_test = [
                "exploration_analysis",
                "trading_strategy",
                "combat_assessment"
            ]
            
            all_passed = True
            for template_id in templates_to_test:
                try:
                    result = await prompts.generate_prompt(template_id, 24)
                    
                    if isinstance(result, str) and len(result) > 100:
                        print(f"[SUCCESS] Generated prompt for {template_id} ({len(result)} chars)")
                        
                        # Check that it contains game state info
                        if "Sol" in result and "Python" in result:
                            print(f"[SUCCESS] Prompt contains game state context")
                        else:
                            print(f"[WARNING] Prompt may be missing game context")
                    else:
                        print(f"[FAILED] Invalid prompt generated for {template_id}")
                        all_passed = False
                        
                except Exception as e:
                    print(f"[FAILED] Error generating prompt for {template_id}: {e}")
                    all_passed = False
            
            return all_passed
        
        return asyncio.run(test_generation())
        
    except Exception as e:
        print(f"[FAILED] Error testing prompt generation: {e}")
        return False


def test_server_integration():
    """Test that prompts are integrated with the server."""
    print_section("Testing Server Integration")
    
    try:
        from src.server import EliteDangerousServer
        
        server = EliteDangerousServer()
        
        # Check that mcp_prompts attribute exists
        if not hasattr(server, 'mcp_prompts'):
            print("[FAILED] Server missing mcp_prompts attribute")
            return False
        
        print("[SUCCESS] Server has mcp_prompts attribute")
        
        # Check that setup_mcp_prompts method exists
        if not hasattr(server, 'setup_mcp_prompts'):
            print("[FAILED] Server missing setup_mcp_prompts method")
            return False
        
        print("[SUCCESS] Server has setup_mcp_prompts method")
        
        # Check MCPPrompts instance
        if server.mcp_prompts is None:
            print("[FAILED] Server mcp_prompts is None")
            return False
        
        print("[SUCCESS] Server has valid mcp_prompts instance")
        
        return True
        
    except Exception as e:
        print(f"[FAILED] Error testing server integration: {e}")
        return False


def test_prompt_list_functionality():
    """Test prompt listing functionality."""
    print_section("Testing Prompt List Functionality")
    
    try:
        from src.mcp.mcp_prompts import MCPPrompts
        from src.utils.data_store import DataStore
        
        # Create mock data store
        data_store = DataStore()
        prompts = MCPPrompts(data_store)
        
        # Test list_available_prompts
        prompt_list = prompts.list_available_prompts()
        
        if not isinstance(prompt_list, list):
            print("[FAILED] list_available_prompts should return a list")
            return False
        
        if len(prompt_list) == 0:
            print("[FAILED] No prompts returned from list_available_prompts")
            return False
        
        print(f"[SUCCESS] Found {len(prompt_list)} available prompts")
        
        # Check structure of prompt definitions
        for i, prompt in enumerate(prompt_list[:3]):  # Check first 3
            required_fields = ["id", "name", "description", "variables", "type"]
            for field in required_fields:
                if field not in prompt:
                    print(f"[FAILED] Prompt {i} missing field: {field}")
                    return False
            
            print(f"[SUCCESS] Prompt {i}: {prompt['name']} ({prompt['type']})")
        
        return True
        
    except Exception as e:
        print(f"[FAILED] Error testing prompt list functionality: {e}")
        return False


def run_unit_tests():
    """Run unit tests for MCP prompts."""
    print_section("Running Unit Tests")
    
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_mcp_prompts.py"
    
    if not test_file.exists():
        print(f"[FAILED] Test file not found: {test_file}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("[SUCCESS] All unit tests passed")
            return True
        else:
            print("[FAILED] Some unit tests failed")
            return False
            
    except Exception as e:
        print(f"[FAILED] Error running unit tests: {e}")
        return False


def test_prompt_types():
    """Test prompt type classification."""
    print_section("Testing Prompt Type Classification")
    
    try:
        from src.mcp.mcp_prompts import MCPPrompts, PromptType
        from src.utils.data_store import DataStore
        
        data_store = DataStore()
        prompts = MCPPrompts(data_store)
        
        # Test prompt type mapping
        type_tests = [
            ("exploration_analysis", PromptType.EXPLORATION.value),
            ("trading_strategy", PromptType.TRADING.value),
            ("combat_assessment", PromptType.COMBAT.value),
            ("mining_optimization", PromptType.MINING.value),
            ("mission_guidance", PromptType.MISSIONS.value),
            ("engineering_progress", PromptType.ENGINEERING.value),
            ("journey_review", PromptType.JOURNEY.value),
            ("performance_review", PromptType.PERFORMANCE.value),
            ("strategic_planning", PromptType.STRATEGY.value)
        ]
        
        all_passed = True
        for template_id, expected_type in type_tests:
            actual_type = prompts._get_prompt_type(template_id)
            if actual_type == expected_type:
                print(f"[SUCCESS] {template_id} -> {actual_type}")
            else:
                print(f"[FAILED] {template_id}: expected {expected_type}, got {actual_type}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"[FAILED] Error testing prompt types: {e}")
        return False


def run_all_tests():
    """Run all milestone 10 tests."""
    print("=" * 60)
    print(" MILESTONE 10: MCP PROMPTS IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    results = {
        "Module Imports": test_imports(),
        "Prompt Templates": test_prompt_templates(),
        "Prompt Generation": test_prompt_generation(),
        "Server Integration": test_server_integration(),
        "Prompt List Functionality": test_prompt_list_functionality(),
        "Prompt Type Classification": test_prompt_types(),
        "Unit Tests": run_unit_tests()
    }
    
    print_section("TEST RESULTS SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("=" * 60)
        print(" ALL TESTS PASSED - MILESTONE 10 COMPLETE!")
        print("=" * 60)
        print()
        print("MCP Prompts Implementation:")
        print("  - 9+ context-aware prompt templates")
        print("  - Dynamic prompt generation based on game state")
        print("  - Template system with variable substitution")
        print("  - Integration with data store for real-time context")
        print("  - Comprehensive error handling and validation")
        print("  - Full server integration with MCP tools")
        print("  - 35+ unit tests covering all functionality")
        print()
        print("Features Implemented:")
        print("  - Exploration analysis prompts")
        print("  - Trading strategy recommendations")
        print("  - Combat assessment and tactics")
        print("  - Mining optimization guidance")
        print("  - Mission performance analysis")
        print("  - Engineering progress tracking")
        print("  - Journey and navigation reviews")
        print("  - Performance metrics and efficiency")
        print("  - Strategic planning assistance")
        print()
        print("Ready for Milestone 11: EDCoPilot File Templates")
        print("=" * 60)
    else:
        print("=" * 60)
        print(" SOME TESTS FAILED - PLEASE FIX ISSUES")
        print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
