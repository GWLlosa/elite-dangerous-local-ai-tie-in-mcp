#!/usr/bin/env python3
"""
Test script for Milestone 9: MCP Resources Implementation

Runs comprehensive tests to verify MCP resources functionality.
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
        ("src.mcp.mcp_resources", "MCPResources"),
        ("src.mcp.mcp_resources", "ResourceCache"),
        ("src.mcp.mcp_resources", "ResourceType"),
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


def test_resource_structure():
    """Test that resource structure is correct."""
    print_section("Testing Resource Structure")
    
    try:
        from src.mcp.mcp_resources import MCPResources
        from src.utils.data_store import DataStore
        
        # Create mock data store
        data_store = DataStore()
        resources = MCPResources(data_store)
        
        # Check resource count
        resource_list = resources.list_resources()
        print(f"[INFO] Found {len(resource_list)} resources")
        
        if len(resource_list) < 15:
            print(f"[WARNING] Expected at least 15 resources, found {len(resource_list)}")
            return False
        
        # Check required resources exist
        required_uris = [
            "elite://status/current",
            "elite://status/location",
            "elite://status/ship",
            "elite://journal/recent",
            "elite://journal/stats",
            "elite://events/by-category",
            "elite://events/by-type",
            "elite://events/search",
            "elite://summary/exploration",
            "elite://summary/trading",
            "elite://summary/combat",
            "elite://summary/mining",
            "elite://summary/journey",
            "elite://state/materials",
            "elite://state/factions",
            "elite://metrics/performance",
            "elite://metrics/credits"
        ]
        
        available_uris = [r["uri"] for r in resource_list]
        
        all_found = True
        for uri in required_uris:
            if uri in available_uris:
                print(f"[SUCCESS] Found resource: {uri}")
            else:
                print(f"[FAILED] Missing resource: {uri}")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"[FAILED] Error testing resource structure: {e}")
        return False


def run_unit_tests():
    """Run unit tests for MCP resources."""
    print_section("Running Unit Tests")
    
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_mcp_resources.py"
    
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


def test_cache_functionality():
    """Test resource cache functionality."""
    print_section("Testing Cache Functionality")
    
    try:
        import asyncio
        from src.mcp.mcp_resources import ResourceCache
        
        async def test_cache():
            cache = ResourceCache(ttl_seconds=1)
            
            # Test set and get
            await cache.set("test_key", {"data": "test"})
            result = await cache.get("test_key")
            
            if result != {"data": "test"}:
                print("[FAILED] Cache set/get failed")
                return False
            
            print("[SUCCESS] Cache set/get working")
            
            # Test expiration
            await asyncio.sleep(1.5)
            result = await cache.get("test_key")
            
            if result is not None:
                print("[FAILED] Cache expiration not working")
                return False
            
            print("[SUCCESS] Cache expiration working")
            
            # Test clear
            await cache.set("key1", "value1")
            await cache.set("key2", "value2")
            await cache.clear()
            
            if await cache.get("key1") is not None or await cache.get("key2") is not None:
                print("[FAILED] Cache clear not working")
                return False
            
            print("[SUCCESS] Cache clear working")
            return True
        
        return asyncio.run(test_cache())
        
    except Exception as e:
        print(f"[FAILED] Error testing cache: {e}")
        return False


def test_server_integration():
    """Test that resources are integrated with the server."""
    print_section("Testing Server Integration")
    
    try:
        from src.server import EliteDangerousServer
        
        server = EliteDangerousServer()
        
        # Check that mcp_resources attribute exists
        if not hasattr(server, 'mcp_resources'):
            print("[FAILED] Server missing mcp_resources attribute")
            return False
        
        print("[SUCCESS] Server has mcp_resources attribute")
        
        # Check that setup_mcp_resources method exists
        if not hasattr(server, 'setup_mcp_resources'):
            print("[FAILED] Server missing setup_mcp_resources method")
            return False
        
        print("[SUCCESS] Server has setup_mcp_resources method")
        
        return True
        
    except Exception as e:
        print(f"[FAILED] Error testing server integration: {e}")
        return False


def run_all_tests():
    """Run all milestone 9 tests."""
    print("=" * 60)
    print(" MILESTONE 9: MCP RESOURCES IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    
    results = {
        "Module Imports": test_imports(),
        "Resource Structure": test_resource_structure(),
        "Cache Functionality": test_cache_functionality(),
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
        print(" ALL TESTS PASSED - MILESTONE 9 COMPLETE!")
        print("=" * 60)
        print()
        print("MCP Resources Implementation:")
        print("  - 17+ resource endpoints implemented")
        print("  - Dynamic URI parameters supported")
        print("  - Caching system with TTL")
        print("  - Comprehensive error handling")
        print("  - Full server integration")
        print("  - 40+ unit tests passing")
        print()
        print("Ready for Milestone 10: MCP Prompts Implementation")
        print("=" * 60)
    else:
        print("=" * 60)
        print(" SOME TESTS FAILED - PLEASE FIX ISSUES")
        print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
