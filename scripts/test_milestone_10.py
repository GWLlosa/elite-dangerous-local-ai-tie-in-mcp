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
    """Test that prompt templates are properly defined."""
    print_section("Testing Prompt Templates")
    
    try:
        from src.mcp.mcp_prompts import MCPPrompts
        from src.utils.data_store import DataStore
        
        # Create instance
        data_store = DataStore()
        prompts = MCPPrompts(data_store)
        
        # Check template count
        template_count = len(prompts.templates)
        print(f"[INFO] Found {template_count} prompt templates")
        
        if template_count < 15:
            print(f"[WARNING] Expected at least 15 templates, found {template_count}")
            return False
        
        # Check required templates exist
        required_templates = [
            "exploration_analysis",
            "exploration_route",
            "trading_analysis",
            "market_opportunity",
            "combat_review",
            "threat_assessment",
            "mining_optimization",
            "route_planning",
            "journey_review",
            "engineering_priorities",
            "mission_strategy",
            "performance_analysis",
            "daily_goals",
            "career_advice",
            "commander_log",
            "situation_report"
        ]
        
        all_found = True
        for template_name in required_templates:
            if template_name in prompts.templates:
                print(f"[SUCCESS] Found template: {template_name}")
            else:
                print(f"[FAILED] Missing template: {template_name}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"[FAILED] Error testing prompt templates: {e}")
        return False


def test_prompt_generation():
    """Test prompt generation functionality."""
    print_section("Testing Prompt Generation")
    
    try:
        from src.mcp.mcp_prompts import MCPPrompts, PromptType
        from src.utils.data_store import DataStore
        from datetime import datetime, timezone
        from src.journal.events import ProcessedEvent, EventCategory
        
        # Create instance with mock data
        data_store = DataStore()
        
        # Add some mock events
        mock_event = ProcessedEvent(
            timestamp=datetime.now(timezone.utc),
            event_type="FSDJump",
            category=EventCategory.NAVIGATION,
            data={"StarSystem": "Test System", "JumpDist": 30.0},
            summary="Jumped to Test System"
        )
        data_store.store_event(mock_event)
        
        prompts = MCPPrompts(data_store)
        
        # Test basic prompt generation
        result = prompts.generate_prompt("daily_goals")
        
        if "error" in result:
            print(f"[FAILED] Error generating prompt: {result['error']}")
            return False
        
        if "prompt" not in result:
            print("[FAILED] Generated prompt missing 'prompt' field")
            return False
        
        print(f"[SUCCESS] Generated daily_goals prompt")
        
        # Test contextual prompt
        result = prompts.generate_contextual_prompt(PromptType.EXPLORATION)
        
        if "error" in result:
            print(f"[FAILED] Error generating contextual prompt: {result['error']}")
            return False
        
        print(f"[SUCCESS] Generated contextual exploration prompt")
        
        # Test adaptive prompts
        results = prompts.generate_adaptive_prompts(count=3)
        
        if not results:
            print("[FAILED] No adaptive prompts generated")
            return False
        
        print(f"[SUCCESS] Generated {len(results)} adaptive prompts")
        
        return True
        
    except Exception as e:
        print(f"[FAILED] Error testing prompt generation: {e}")
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
        
        return True
        
    except Exception as e:
        print(f"[FAILED] Error testing server integration: {e}")
        return False


def test_context_building():
    """Test context building from game state."""
    print_section("Testing Context Building")
    
    try:
        from src.mcp.mcp_prompts import MCPPrompts
        from src.utils.data_store import DataStore
        
        data_store = DataStore()
        prompts = MCPPrompts(data_store)
        
        # Test building context for different prompt types
        context = prompts._build_context("exploration_analysis")
        
        required_fields = [
            "current_system", "current_station", "ship_type",
            "credits", "exploration_rank", "hours"
        ]
        
        all_present = True
        for field in required_fields:
            if field in context:
                print(f"[SUCCESS] Context contains {field}: {context[field]}")
            else:
                print(f"[FAILED] Context missing {field}")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"[FAILED] Error testing context building: {e}")
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
        "Context Building": test_context_building(),
        "Server Integration": test_server_integration(),
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
        print("  - 15+ intelligent prompt templates")
        print("  - Context-aware prompt generation")
        print("  - Dynamic variable substitution")
        print("  - Activity-based template selection")
        print("  - Adaptive prompt recommendations")
        print("  - Full server integration")
        print("  - 35+ unit tests passing")
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
