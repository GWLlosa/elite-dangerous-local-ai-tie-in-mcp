# Code Quality Lessons Learned

This document captures critical lessons learned from recent bugfixes and test failures to ensure future code generation gets it right the first time.

## EDCoPilot Chatter Generation Standards

### Grammar Specification Compliance
**CRITICAL**: All EDCoPilot chatter generation must follow the formal grammar specification

**Reference Document**: [`../docs/edcopilot-chatter-grammar.md`](../docs/edcopilot-chatter-grammar.md)

```python
# CORRECT ✅ - Follow grammar spec exactly
def generate_space_chatter(game_state):
    # Use proper token replacement
    content = "condition:Docked|Successfully docked at {StationName}. All systems secure."

    # Replace tokens with actual game data
    content = content.replace("{StationName}", game_state.current_station or "Station")

    return content

# WRONG ❌ - Invalid format
def generate_space_chatter(game_state):
    # Wrong delimiter format
    content = "[condition=Docked] Successfully docked at {StationName}"

    # Missing token replacement
    return content  # Will output literal "{StationName}"
```

**Key Requirements:**
1. **Format Validation**: All output must conform to grammar specification
2. **Token Replacement**: Replace ALL `{TokenName}` patterns with actual game data
3. **Condition Syntax**: Use `condition:ConditionName|` format for space chatter
4. **Conversation Format**: Use `[example]`/`[\example]` blocks for crew chatter
5. **File Headers**: Include proper comment headers with available tokens/conditions
6. **Error Prevention**: Validate against grammar before writing files

### Token Management
**CRITICAL**: Dynamic token replacement must handle missing data gracefully

```python
# CORRECT ✅ - Safe token replacement with fallbacks
def replace_tokens(content: str, game_state) -> str:
    replacements = {
        "{SystemName}": game_state.current_system or "Unknown System",
        "{StationName}": game_state.current_station or "Station",
        "{ShipName}": game_state.ship_name or "Ship",
        "{CommanderName}": game_state.commander_name or "Commander",
        "{Credits}": str(game_state.credits) if game_state.credits else "0"
    }

    for token, value in replacements.items():
        content = content.replace(token, value)

    return content

# WRONG ❌ - Will cause errors or None values in output
def replace_tokens(content: str, game_state) -> str:
    content = content.replace("{SystemName}", game_state.current_system)  # Could be None
    return content
```

**Best Practices:**
- Always provide fallback values for missing game data
- Test token replacement with empty game state
- Validate all tokens are replaced before output
- Use contextually appropriate fallbacks (not generic "Unknown")

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

## Critical Data Flow Issues

### Game State Population Bug (September 2025)

**CRITICAL**: Events can be stored successfully but game state fields may remain `None` due to improper data extraction.

#### The Problem
```python
# BUG: Events stored but game state not updated
data_store.store_event(processed_event)
recent_events = data_store.get_recent_events()  # ✅ Events found
game_state = data_store.get_game_state()       # ❌ Fields still None
```

**Root Cause**: The `_update_game_state()` method wasn't properly extracting data from `raw_event` fields into GameState attributes.

**Symptoms to Watch For**:
- MCP server logs show "Found X events" but "system: None, ship: None"
- EDCoPilot generates "Unknown System" instead of actual system names
- Context generation uses generic templates instead of real data
- Integration appears successful but output contains placeholders

#### Prevention Strategy

**ALWAYS Test End-to-End Data Flow**:
```python
# BAD ❌ - Only tests storage
def test_events_stored():
    data_store.store_event(event)
    assert len(data_store.get_recent_events()) > 0

# GOOD ✅ - Tests storage AND extraction
def test_events_populate_game_state():
    loadgame_event = ProcessedEvent(
        raw_event={"Commander": "Hadesfire", "Ship": "Mandalay"},
        event_type="LoadGame",
        # ... other params
    )
    data_store.store_event(loadgame_event)

    game_state = data_store.get_game_state()
    assert game_state.commander_name == "Hadesfire"  # Verify extraction works
    assert game_state.current_ship == "Mandalay"     # Not just that events exist
```

**Create Bug Reproduction Tests**:
```python
def test_game_state_remains_none_despite_loaded_events():
    """Reproduces the exact issue: events loaded but state fields None."""
    # Load events that should populate state
    data_store.store_event(location_event)
    data_store.store_event(loadgame_event)

    # Verify events are stored
    assert len(data_store.get_recent_events()) >= 2

    # This should FAIL until bug is fixed
    game_state = data_store.get_game_state()
    assert game_state.current_system is not None, "BUG: current_system not populated"
    assert game_state.commander_name is not None, "BUG: commander_name not populated"
```

#### Code Review Checklist
- [ ] Does `_update_game_state()` actually extract `raw_event` data into GameState fields?
- [ ] Are there tests that verify game state population, not just event storage?
- [ ] Do integration tests check that MCP tools receive populated data?
- [ ] Would this change cause EDCoPilot to generate generic vs contextual content?

#### Integration Testing Requirements
```python
# REQUIRED: Test the full pipeline
def test_edcopilot_uses_real_data():
    # Store events with real data
    data_store.store_event(location_event)  # Blae Drye SG-P b25-6
    data_store.store_event(ship_event)      # EXCELSIOR

    # Generate content
    generator = EDCoPilotGenerator(data_store)
    context = generator._build_context()

    # Verify real data appears, not placeholders
    assert "Blae Drye SG-P b25-6" in str(context), "Should use real system name"
    assert "EXCELSIOR" in str(context), "Should use real ship name"
    assert "Unknown System" not in str(context), "Should not contain placeholders"
```

### DataStore State Management
**CRITICAL**: Always verify that stored events actually populate the intended state fields.

```python
# PATTERN: Event storage methods that must update state
def _handle_load_game(self, event: ProcessedEvent) -> None:
    """LoadGame events must extract commander, ship, credits from raw_event."""
    key_data = event.key_data or {}
    # VERIFY: Does this actually populate GameState fields?
    self.game_state.commander_name = key_data.get("commander")
    self.game_state.current_ship = key_data.get("ship_type")

def _handle_location_update(self, event: ProcessedEvent) -> None:
    """Location events must extract system name from raw_event."""
    system_name = event.raw_event.get("StarSystem")  # Use raw_event, not key_data
    # VERIFY: Does this actually update current_system?
    self.game_state.current_system = system_name
```

This document should be referenced whenever generating or modifying code in this codebase to avoid repeating these common mistakes.