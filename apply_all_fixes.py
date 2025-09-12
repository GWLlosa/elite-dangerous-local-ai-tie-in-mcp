#!/usr/bin/env python3
"""
Complete fix script for mcp_prompts.py and mcp_resources.py
"""

import os
import sys

def fix_file(file_path, fixes):
    """Apply fixes to a file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = 0
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            changes += 1
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return changes

def main():
    print("Applying fixes to MCP files...")
    print("=" * 60)
    
    # Fixes for mcp_prompts.py
    prompts_fixes = [
        # Main method fixes
        ('self.data_store.get_all_events()', 'self.data_store.query_events()'),
        
        # Data access fixes
        ('e.data.get(', 'e.key_data.get('),
        ('event.data.get(', 'event.key_data.get('),
        
        # Conditional fixes
        ('"StarSystem" in e.data', '"StarSystem" in e.key_data'),
        ('"Reward" in e.data', '"Reward" in e.key_data'),
        ('"Cost" in e.data', '"Cost" in e.key_data'),
        
        # Fix comprehensions to add safety checks
        ('for e in jump_events if "StarSystem" in e.key_data)',
         'for e in jump_events if e.key_data and "StarSystem" in e.key_data)'),
        ('for e in combat_zone_events if "StarSystem" in e.key_data)',
         'for e in combat_zone_events if e.key_data and "StarSystem" in e.key_data)'),
        ('for e in all_events if "Reward" in e.key_data)',
         'for e in all_events if e.key_data and "Reward" in e.key_data)'),
        ('for e in all_events if "Cost" in e.key_data)',
         'for e in all_events if e.key_data and "Cost" in e.key_data)'),
         
        # Additional safety for valuable_scans
        ('valuable_scans = [e for e in scan_events if e.key_data.get("TerraformState") or e.key_data.get("WasDiscovered") == False]',
         'valuable_scans = [e for e in scan_events if e.key_data and (e.key_data.get("TerraformState") or e.key_data.get("WasDiscovered") == False)]'),
    ]
    
    changes = fix_file('src/mcp/mcp_prompts.py', prompts_fixes)
    if changes:
        print(f"✅ Fixed src/mcp/mcp_prompts.py: {changes} changes applied")
    else:
        print(f"⚠️  src/mcp/mcp_prompts.py: No changes needed or file missing")
    
    # Fixes for mcp_resources.py
    resources_fixes = [
        # Main method fixes
        ('self.data_store.get_all_events()', 'self.data_store.query_events()'),
        
        # Data access fixes - be careful not to replace other 'data' references
        ('e.data', 'e.key_data'),
        ('event.data', 'event.key_data'),
    ]
    
    changes = fix_file('src/mcp/mcp_resources.py', resources_fixes)
    if changes:
        print(f"✅ Fixed src/mcp/mcp_resources.py: {changes} changes applied")
    else:
        print(f"⚠️  src/mcp/mcp_resources.py: No changes needed or file missing")
    
    print("=" * 60)
    print("\n✅ All fixes applied!")
    print("\nNext step: Run tests with:")
    print("  python scripts/run_tests.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
