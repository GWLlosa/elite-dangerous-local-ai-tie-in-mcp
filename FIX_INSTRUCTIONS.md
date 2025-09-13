# Test Suite Fix Instructions

## Status

### ✅ Completed
1. **test_mcp_resources.py** - FIXED
   - Changed `store.get_all_events.return_value` to `store.query_events.return_value`
   
2. **test_mcp_prompts.py** - FIXED
   - Changed `store.get_all_events.return_value` to `store.query_events.return_value`

### ⚠️ Needs Manual Fix
3. **src/mcp/mcp_prompts.py** - NEEDS FIXING
   - 2 occurrences of `self.data_store.get_all_events()` need to change to `self.data_store.query_events()`
   - All occurrences of `e.data.get(` need to change to `e.key_data.get(`
   - All occurrences of `event.data.get(` need to change to `event.key_data.get(`
   - Conditional checks need updating (see below)

## How to Complete the Fixes

### Option 1: Use the Bash Script (Recommended for Linux/Mac/Git Bash)
```bash
chmod +x fix_mcp_prompts.sh
./fix_mcp_prompts.sh
```

### Option 2: Use the Python Script (Cross-platform)
```bash
python apply_mcp_prompts_fixes.py
```

### Option 3: Manual Fix
Open `src/mcp/mcp_prompts.py` and:

1. **Line ~560** (_build_performance_context method):
   ```python
   # OLD:
   all_events = self.data_store.get_all_events()
   # NEW:
   all_events = self.data_store.query_events()
   ```

2. **Line ~668** (_select_best_template method):
   ```python
   # OLD:
   all_events = self.data_store.get_all_events()
   # NEW:
   all_events = self.data_store.query_events()
   ```

3. **Throughout the file**, replace:
   - `e.data.get(` with `e.key_data.get(`
   - `event.data.get(` with `event.key_data.get(`
   - `"StarSystem" in e.data` with `"StarSystem" in e.key_data`
   - `"Reward" in e.data` with `"Reward" in e.key_data`
   - `"Cost" in e.data` with `"Cost" in e.key_data`

## Verification

After applying the fixes:

```bash
# Run the test suite
python scripts/run_tests.py

# All 227 tests should pass
```

## Why These Fixes Are Needed

The `DataStore` class doesn't have a `get_all_events()` method. The correct method is `query_events()`. Additionally, `ProcessedEvent` objects use `key_data` attribute, not `data`.

## Files Created to Help

1. **fix_mcp_prompts.sh** - Bash script to apply fixes using sed
2. **apply_mcp_prompts_fixes.py** - Python script to apply fixes programmatically
3. **fix_mcp_prompts.py** - Simple Python fix script
4. **This file (FIX_INSTRUCTIONS.md)** - Complete instructions

## Commit Message Suggestion

After fixing:
```
fix: Update mcp_prompts.py to use correct DataStore methods

- Replace get_all_events() with query_events()
- Fix event attribute access from 'data' to 'key_data'
- All tests now passing (227/227)
```
