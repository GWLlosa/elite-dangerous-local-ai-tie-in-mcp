#!/bin/bash

# Script to fix mcp_prompts.py
echo "Fixing mcp_prompts.py..."

FILE="src/mcp/mcp_prompts.py"

if [ ! -f "$FILE" ]; then
    echo "Error: $FILE not found. Run this script from the repository root."
    exit 1
fi

# Create backup
cp "$FILE" "${FILE}.backup"

# Apply fixes using sed
echo "Applying fixes..."

# Fix 1: Replace get_all_events() with query_events()
sed -i 's/self\.data_store\.get_all_events()/self.data_store.query_events()/g' "$FILE"

# Fix 2: Replace e.data with e.key_data
sed -i 's/e\.data\.get(/e.key_data.get(/g' "$FILE"
sed -i 's/event\.data\.get(/event.key_data.get(/g' "$FILE"

# Fix 3: Replace conditional checks
sed -i 's/"StarSystem" in e\.data/"StarSystem" in e.key_data/g' "$FILE"
sed -i 's/"Reward" in e\.data/"Reward" in e.key_data/g' "$FILE"
sed -i 's/"Cost" in e\.data/"Cost" in e.key_data/g' "$FILE"

# Fix 4: Fix comprehensions that check for data
sed -i 's/for e in jump_events if "StarSystem" in e\.data/for e in jump_events if e.key_data and "StarSystem" in e.key_data/g' "$FILE"
sed -i 's/for e in combat_zone_events if "StarSystem" in e\.data/for e in combat_zone_events if e.key_data and "StarSystem" in e.key_data/g' "$FILE"
sed -i 's/for e in all_events if "Reward" in e\.data/for e in all_events if e.key_data and "Reward" in e.key_data/g' "$FILE"
sed -i 's/for e in all_events if "Cost" in e\.data/for e in all_events if e.key_data and "Cost" in e.key_data/g' "$FILE"

# Additional safety fixes
sed -i 's/\be\.data\.get(/e.key_data.get(/g' "$FILE"

echo "✅ Fixes applied successfully!"
echo ""
echo "Backup saved as: ${FILE}.backup"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff src/mcp/mcp_prompts.py"
echo "2. Run tests: python scripts/run_tests.py"
echo "3. If tests pass, commit the changes"
echo ""
echo "To revert if needed: mv ${FILE}.backup $FILE"
