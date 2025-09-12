#!/usr/bin/env python3
"""
Script to fix all issues in mcp_prompts.py.
Run this from the repository root.
"""

import sys
import os
import re

def apply_fixes():
    """Apply all necessary fixes to mcp_prompts.py."""
    
    file_path = 'src/mcp/mcp_prompts.py'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run this script from the repository root.")
        sys.exit(1)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track changes made
    changes_made = []
    
    # Fix 1: Replace get_all_events() with query_events()
    for i, line in enumerate(lines):
        if 'all_events = self.data_store.get_all_events()' in line:
            lines[i] = line.replace(
                'all_events = self.data_store.get_all_events()',
                'all_events = self.data_store.query_events()'
            )
            changes_made.append(f"Line {i+1}: Fixed get_all_events() -> query_events()")
    
    # Fix 2: Replace e.data with e.key_data throughout
    # This is more complex as we need to be careful not to replace other 'data' references
    
    replacements = [
        # Simple replacements
        ('e.data.get(', 'e.key_data.get('),
        ('event.data.get(', 'event.key_data.get('),
        
        # Conditional checks
        ('"StarSystem" in e.data', '"StarSystem" in e.key_data'),
        ('"StarSystem" in event.data', '"StarSystem" in event.key_data'),
        ('"Reward" in e.data', '"Reward" in e.key_data'),
        ('"Cost" in e.data', '"Cost" in e.key_data'),
        
        # Comprehensions and generators
        (' for e in jump_events if "StarSystem" in e.data)',
         ' for e in jump_events if e.key_data and "StarSystem" in e.key_data)'),
        (' for e in combat_zone_events if "StarSystem" in e.data)',
         ' for e in combat_zone_events if e.key_data and "StarSystem" in e.key_data)'),
        
        # Specific lines that need fixing
        ('e.data.get("TerraformState") or e.data.get("WasDiscovered")',
         'e.key_data and (e.key_data.get("TerraformState") or e.key_data.get("WasDiscovered"))'),
        
        # Additional fixes for safety checks
        ('for e in all_events if "Reward" in e.data',
         'for e in all_events if e.key_data and "Reward" in e.key_data'),
        ('for e in all_events if "Cost" in e.data',
         'for e in all_events if e.key_data and "Cost" in e.key_data'),
    ]
    
    for i, line in enumerate(lines):
        original_line = line
        for old_pattern, new_pattern in replacements:
            if old_pattern in line:
                line = line.replace(old_pattern, new_pattern)
                if line != original_line:
                    changes_made.append(f"Line {i+1}: Fixed data access pattern")
        lines[i] = line
    
    # Write the fixed file back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n" + "="*60)
    print("MCP Prompts Fix Applied Successfully!")
    print("="*60)
    print(f"\nTotal changes made: {len(changes_made)}")
    
    if changes_made:
        print("\nChanges applied:")
        for change in changes_made[:10]:  # Show first 10 changes
            print(f"  - {change}")
        if len(changes_made) > 10:
            print(f"  ... and {len(changes_made) - 10} more changes")
    
    print("\n" + "-"*60)
    print("Next steps:")
    print("1. Run the tests: python scripts/run_tests.py")
    print("2. Commit the changes if tests pass")
    print("-"*60)
    
    return len(changes_made)

if __name__ == '__main__':
    try:
        changes = apply_fixes()
        if changes > 0:
            print(f"\n✅ Successfully applied {changes} fixes to mcp_prompts.py")
        else:
            print("\n⚠️  No changes needed - file may already be fixed")
    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        sys.exit(1)
