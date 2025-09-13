#!/usr/bin/env python3
"""
This script will fix mcp_prompts.py and show the changes.
Run from repository root.
"""

import os
import subprocess
import sys

def main():
    # First, let's check if we're in the right directory
    if not os.path.exists('src/mcp/mcp_prompts.py'):
        print("Error: src/mcp/mcp_prompts.py not found.")
        print("Please run this script from the repository root.")
        return 1
    
    print("Reading mcp_prompts.py...")
    with open('src/mcp/mcp_prompts.py', 'r') as f:
        lines = f.readlines()
    
    # Track what we're changing
    changes = []
    
    # Apply fixes line by line
    for i, line in enumerate(lines):
        original = line
        
        # Fix 1: get_all_events -> query_events
        if 'self.data_store.get_all_events()' in line:
            line = line.replace('self.data_store.get_all_events()', 'self.data_store.query_events()')
            changes.append(f"Line {i+1}: get_all_events() -> query_events()")
        
        # Fix 2: e.data -> e.key_data
        if 'e.data.get(' in line and 'e.key_data.get(' not in line:
            line = line.replace('e.data.get(', 'e.key_data.get(')
            changes.append(f"Line {i+1}: e.data -> e.key_data")
        
        # Fix 3: event.data -> event.key_data
        if 'event.data.get(' in line:
            line = line.replace('event.data.get(', 'event.key_data.get(')
            changes.append(f"Line {i+1}: event.data -> event.key_data")
        
        # Fix 4: Conditionals in comprehensions
        if '"StarSystem" in e.data' in line:
            line = line.replace('"StarSystem" in e.data', '"StarSystem" in e.key_data')
            # Also add safety check if it's in a comprehension
            if 'for e in' in line and 'if "StarSystem" in e.key_data)' in line:
                line = line.replace(
                    'if "StarSystem" in e.key_data)',
                    'if e.key_data and "StarSystem" in e.key_data)'
                )
            changes.append(f"Line {i+1}: Fixed StarSystem check")
        
        if '"Reward" in e.data' in line:
            line = line.replace('"Reward" in e.data', '"Reward" in e.key_data')
            # Add safety check
            if 'for e in all_events if "Reward" in e.key_data' in line:
                line = line.replace(
                    'if "Reward" in e.key_data',
                    'if e.key_data and "Reward" in e.key_data'
                )
            changes.append(f"Line {i+1}: Fixed Reward check")
        
        if '"Cost" in e.data' in line:
            line = line.replace('"Cost" in e.data', '"Cost" in e.key_data')
            # Add safety check
            if 'for e in all_events if "Cost" in e.key_data' in line:
                line = line.replace(
                    'if "Cost" in e.key_data',
                    'if e.key_data and "Cost" in e.key_data'
                )
            changes.append(f"Line {i+1}: Fixed Cost check")
        
        lines[i] = line
    
    # Write the fixed file
    print(f"\nApplying {len(changes)} fixes...")
    with open('src/mcp/mcp_prompts.py', 'w') as f:
        f.writelines(lines)
    
    # Show what was changed
    if changes:
        print("\nChanges made:")
        for change in changes:
            print(f"  - {change}")
    
    print("\n✅ File fixed successfully!")
    print("\nNow run: python scripts/run_tests.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
