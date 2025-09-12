#!/usr/bin/env python3
"""
Script to fix the mcp_prompts.py file issues.
Run this from the repository root.
"""

import re

def fix_mcp_prompts():
    """Fix the issues in mcp_prompts.py."""
    
    # Read the file
    with open('src/mcp/mcp_prompts.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Replace get_all_events() with query_events()
    content = content.replace(
        'all_events = self.data_store.get_all_events()',
        'all_events = self.data_store.query_events()'
    )
    
    # Fix 2: Replace e.data with e.key_data in event processing
    # This needs to be done carefully to not replace other 'data' references
    
    # Pattern to match e.data.get or event.data.get
    patterns = [
        (r'\be\.data\.get\(', 'e.key_data.get('),
        (r'\bevent\.data\.get\(', 'event.key_data.get('),
        (r'"StarSystem" in e\.data', '"StarSystem" in e.key_data'),
        (r'"StarSystem" in event\.data', '"StarSystem" in event.key_data'),
        (r'"Reward" in e\.data', '"Reward" in e.key_data'),
        (r'"Cost" in e\.data', '"Cost" in e.key_data'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write the fixed file
    with open('src/mcp/mcp_prompts.py', 'w') as f:
        f.write(content)
    
    print("Fixed mcp_prompts.py:")
    print("- Replaced get_all_events() with query_events() (2 occurrences)")
    print("- Replaced e.data with e.key_data throughout the file")
    print("\nPlease run the tests to verify: python scripts/run_tests.py")

if __name__ == '__main__':
    fix_mcp_prompts()
