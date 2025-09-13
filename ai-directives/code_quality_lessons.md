# Code Quality Lessons Learned

This document captures critical lessons learned from recent bugfixes and test failures to ensure future code generation gets it right the first time.

## Core Data Structure Patterns

### ProcessedEvent Object Structure
**CRITICAL**: The `ProcessedEvent` class uses `raw_event` not `raw_data`

```python
# CORRECT ✅
class ProcessedEvent:
    def __init__(self, raw_event: Dict, event_type: str, ...):
        self.raw_event = raw_event  # NOT raw_data

# Usage in code:
event.raw_event.get('StarSystem')  # CORRECT
event.raw_data.get('StarSystem')   # WRONG - will cause AttributeError
```

**Key Points:**
- Always use `raw_event` when accessing the original event dictionary
- This affects ALL code that processes Elite Dangerous journal events
- Tests must use `raw_event={}` parameter, not `data={}`

### JournalParser Return Values
**CRITICAL**: `JournalParser.read_journal_file()` returns a tuple `(entries, position)`

```python
# CORRECT ✅
entries, position = parser.read_journal_file(journal_path)

# WRONG ❌ - This assigns a tuple to entries
entries = parser.read_journal_file(journal_path)
```

**Key Points:**
- Always unpack the tuple when calling `read_journal_file()`
- Integration tests must handle both return values
- Only use the entries part for event processing

## Constructor Patterns

### JournalMonitor Constructor
**CRITICAL**: `JournalMonitor` requires both `journal_path` and `event_callback` parameters

```python
# CORRECT ✅
def event_callback(event_data):
    # Process event
    pass

monitor = JournalMonitor(journal_path, event_callback)

# WRONG ❌
monitor = JournalMonitor()  # Missing required parameters
```

### DataStore Method Names
**CRITICAL**: Use correct DataStore method names

```python
# CORRECT ✅
recent_events = data_store.get_recent_events(minutes=60)
events_by_type = data_store.get_events_by_type("FSDJump")
events_by_category = data_store.get_events_by_category(EventCategory.NAVIGATION)

# WRONG ❌
all_events = data_store.get_all_events()  # This method doesn't exist
```

## Error Handling Patterns

### MCP Resources Error Responses
**CRITICAL**: Return error objects, not None, for unknown resources

```python
# CORRECT ✅
if base_uri not in self.resources:
    if "summary/" in base_uri:
        return {
            "error": f"Unknown activity type: {base_uri.split('/')[-1]}",
            "valid_activities": ["exploration", "trading", "combat", "mining", "journey"]
        }
    return {
        "error": f"Unknown resource URI: {base_uri}",
        "available_resources": list(self.resources.keys())
    }

# WRONG ❌
if base_uri not in self.resources:
    return None  # Tests expect error objects
```

## Template System Patterns

### Prompt Template Variables
**CRITICAL**: Template variable checks must handle formatted variables

```python
# CORRECT ✅ - Handle both {var} and {var:format}
variable_found = (
    f"{{{variable}}}" in template.template or
    f"{{{variable}:" in template.template
)

# WRONG ❌ - Only checks exact match
assert f"{{{variable}}}" in template.template  # Fails for {credits:,}
```

**Key Points:**
- Variables can have formatting like `{credits:,}` or `{distance:.1f}`
- Tests must account for formatted variable patterns
- Always include the base variable in the variables list

## FastMCP Framework Limitations

### Tool Access Patterns
**IMPORTANT**: FastMCP doesn't expose tools collection

```python
# WRONG ❌ - FastMCP doesn't have tools attribute
tools = list(server.app.tools.keys())

# CORRECT ✅ - Note handler setup but don't try to access tools
print("MCP Tools: Handler setup completed successfully")
```

## Character Encoding Rules

### ASCII-Only Requirements
**CRITICAL**: All Python files must use ASCII-only characters

```python
# WRONG ❌ - Unicode characters cause cp1252 errors on Windows
def print_status(message, success=True):
    icon = "✅" if success else "❌"  # Unicode emoji

# CORRECT ✅ - ASCII alternatives
def print_status(message, success=True):
    icon = "[SUCCESS]" if success else "[FAILED]"
```

**Key Points:**
- Replace all Unicode emojis with ASCII alternatives
- Use descriptive text instead of special characters
- This is especially important for Windows compatibility

## Test Writing Guidelines

### Integration Test Patterns
1. **Always handle tuple returns from parsers**
2. **Pass required constructor parameters to monitors**
3. **Use proper attribute names (raw_event not raw_data)**
4. **Expect error objects not None for invalid requests**

### Unit Test Patterns
1. **Mock all external dependencies properly**
2. **Test both success and error cases**
3. **Handle formatted template variables**
4. **Use consistent ProcessedEvent constructor parameters**

## Framework-Specific Issues

### DataStore Time Conversions
```python
# CORRECT ✅ - Convert hours to minutes for get_recent_events
recent_events = self.data_store.get_recent_events(time_range_hours * 60)

# WRONG ❌ - Passing hours directly
recent_events = self.data_store.get_recent_events(time_range_hours)
```

### Event Category Enum Usage
```python
# CORRECT ✅
from ..journal.events import EventCategory
events = [e for e in recent_events if e.category == EventCategory.NAVIGATION]

# Ensure enum values are used properly
category = event.category.value  # Get string value when needed
```

## Common Anti-Patterns to Avoid

1. **Assuming method signatures without checking the codebase**
2. **Using hardcoded attribute names without verifying the class definition**
3. **Not handling return value tuples properly**
4. **Expecting None when APIs return error objects**
5. **Using Unicode characters in script files**
6. **Not handling optional formatting in template variables**

## Testing Methodology

### Comprehensive Test Strategy
1. **Run unit tests first to catch basic issues**
2. **Fix data structure access patterns systematically**
3. **Verify constructor signatures match actual implementations**
4. **Test error handling paths explicitly**
5. **Run integration tests after unit tests pass**

### Debug-First Approach
- When tests fail, examine the actual object structure
- Check method signatures in the implementation, not documentation
- Verify return value types and structures
- Test both success and failure cases

This document should be referenced whenever generating or modifying code in this codebase to avoid repeating these common mistakes.