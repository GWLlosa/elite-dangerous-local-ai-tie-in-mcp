#!/usr/bin/env python3
"""
Final fix script for mcp_prompts.py.
This will apply all necessary fixes to make tests pass.
"""

import os
import sys

def apply_all_fixes():
    """Apply all fixes to mcp_prompts.py."""
    
    file_path = 'src/mcp/mcp_prompts.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run this from the repository root.")
        return False
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Applying fixes to mcp_prompts.py...")
    
    # Fix 1: Replace get_all_events() with query_events()
    original_count = content.count('get_all_events')
    content = content.replace(
        'self.data_store.get_all_events()',
        'self.data_store.query_events()'
    )
    print(f"  ✅ Fixed {original_count} occurrences of get_all_events()")
    
    # Fix 2: Replace e.data.get( with e.key_data.get(
    # Count before replacement
    data_get_count = content.count('e.data.get(')
    content = content.replace('e.data.get(', 'e.key_data.get(')
    print(f"  ✅ Fixed {data_get_count} occurrences of e.data.get()")
    
    # Fix 3: Replace event.data.get( with event.key_data.get(
    event_data_count = content.count('event.data.get(')
    content = content.replace('event.data.get(', 'event.key_data.get(')
    print(f"  ✅ Fixed {event_data_count} occurrences of event.data.get()")
    
    # Fix 4: Fix conditional checks in comprehensions
    # This is more complex as we need to handle the full context
    
    # Fix "StarSystem" checks
    content = content.replace(
        'for e in jump_events if "StarSystem" in e.data)',
        'for e in jump_events if e.key_data and "StarSystem" in e.key_data)'
    )
    
    content = content.replace(
        'for e in combat_zone_events if "StarSystem" in e.data)',
        'for e in combat_zone_events if e.key_data and "StarSystem" in e.key_data)'
    )
    
    # Fix "Reward" and "Cost" checks
    content = content.replace(
        'for e in all_events if "Reward" in e.data)',
        'for e in all_events if e.key_data and "Reward" in e.key_data)'
    )
    
    content = content.replace(
        'for e in all_events if "Cost" in e.data)',
        'for e in all_events if e.key_data and "Cost" in e.key_data)'
    )
    
    print("  ✅ Fixed conditional checks in comprehensions")
    
    # Fix 5: Handle the specific line with OR condition for discoveries
    # This is a tricky one that needs special handling
    content = content.replace(
        'valuable_scans = [e for e in scan_events if e.key_data.get("TerraformState") or e.key_data.get("WasDiscovered") == False]',
        'valuable_scans = [e for e in scan_events if e.key_data and (e.key_data.get("TerraformState") or e.key_data.get("WasDiscovered") == False)]'
    )
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ All fixes applied successfully!")
    print("\nNext steps:")
    print("1. Run tests: python scripts/run_tests.py")
    print("2. If tests pass, commit the changes:")
    print("   git add src/mcp/mcp_prompts.py")
    print("   git commit -m 'fix: Update mcp_prompts.py to use correct DataStore methods'")
    
    return True

if __name__ == '__main__':
    success = apply_all_fixes()
    sys.exit(0 if success else 1)
