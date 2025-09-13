# Elite Dangerous MCP Server - API Reference

Complete reference for all APIs, endpoints, and integration points.

## 📋 Table of Contents

1. [MCP Tools API](#mcp-tools-api)
2. [MCP Resources API](#mcp-resources-api)
3. [MCP Prompts API](#mcp-prompts-api)
4. [Data Store API](#data-store-api)
5. [Event Processing API](#event-processing-api)
6. [Configuration API](#configuration-api)
7. [Error Handling](#error-handling)
8. [Type Definitions](#type-definitions)

## 🔧 MCP Tools API

All MCP Tools are async functions that return structured data.

### Core Data Access

#### `server_status() -> Dict[str, Any]`
Returns current server operational status.

**Returns:**
```python
{
    "status": "running" | "starting" | "stopping" | "error",
    "events_processed": int,
    "uptime_seconds": float,
    "memory_usage": str,
    "journal_monitoring": bool,
    "last_event_time": str | None,
    "version": str
}
```

#### `get_recent_events(minutes: int = 60, category: str = None, event_type: str = None, limit: int = None) -> List[Dict]`
Retrieves recent journal events with filtering.

**Parameters:**
- `minutes`: Time range in minutes (default: 60)
- `category`: Event category filter (optional)
- `event_type`: Specific event type filter (optional)
- `limit`: Maximum number of events (optional)

**Returns:** List of ProcessedEvent dictionaries

#### `clear_data_store() -> Dict[str, str]`
Clears all stored events and resets game state.

**Returns:**
```python
{
    "status": "success",
    "message": "Data store cleared",
    "events_cleared": int
}
```

#### `get_current_location() -> Dict[str, Any]`
Gets current system and station information.

**Returns:**
```python
{
    "current_system": str,
    "current_station": str | None,
    "docked": bool,
    "coordinates": List[float],
    "system_population": int | None,
    "station_type": str | None,
    "last_updated": str
}
```

#### `get_current_ship() -> Dict[str, Any]`
Gets current ship status and configuration.

**Returns:**
```python
{
    "ship_type": str,
    "ship_name": str | None,
    "fuel_level": float,
    "fuel_capacity": float,
    "hull_health": float,
    "cargo_used": int,
    "cargo_capacity": int,
    "jump_range": float | None,
    "last_updated": str
}
```

### Activity Analysis

#### `get_exploration_summary(hours: int = 24) -> Dict[str, Any]`
Analyzes exploration activities.

**Parameters:**
- `hours`: Time range in hours (default: 24)

**Returns:**
```python
{
    "time_range_hours": int,
    "systems_visited": int,
    "bodies_scanned": int,
    "first_discoveries": int,
    "exploration_earnings": int,
    "distance_traveled": float,
    "scan_types": Dict[str, int],
    "most_valuable_discovery": str | None
}
```

#### `get_trading_summary(hours: int = 24) -> Dict[str, Any]`
Analyzes trading performance.

**Returns:**
```python
{
    "time_range_hours": int,
    "trades_completed": int,
    "total_profit": int,
    "profit_per_hour": int,
    "avg_profit_per_trade": int,
    "cargo_runs": int,
    "best_trade": Dict[str, Any] | None
}
```

#### `get_combat_summary(hours: int = 24) -> Dict[str, Any]`
Analyzes combat activities.

**Returns:**
```python
{
    "time_range_hours": int,
    "kills": int,
    "bounties_claimed": int,
    "bounty_earnings": int,
    "combat_bonds": int,
    "average_bounty": int,
    "ship_destroyed": bool,
    "damage_taken": float,
    "most_valuable_target": str | None
}
```

#### `search_events(query: str = None, category: str = None, event_type: str = None, system: str = None, hours: int = 24, limit: int = 100) -> List[Dict]`
Advanced event searching with multiple criteria.

**Parameters:**
- `query`: Text search in event summaries (optional)
- `category`: Event category filter (optional)
- `event_type`: Specific event type filter (optional)
- `system`: System name filter (optional)
- `hours`: Time range in hours (default: 24)
- `limit`: Maximum results (default: 100)

**Returns:** List of matching ProcessedEvent dictionaries

### AI Assistance

#### `list_available_prompts() -> List[Dict[str, str]]`
Lists all available AI prompt templates.

**Returns:**
```python
[
    {
        "id": str,
        "name": str,
        "description": str,
        "category": str
    },
    ...
]
```

#### `generate_analysis_prompt(activity_type: str, time_range_hours: int = 24) -> str`
Generates context-aware AI prompts.

**Parameters:**
- `activity_type`: Type of analysis (exploration, trading, combat, mining, missions, engineering, journey, performance, strategy)
- `time_range_hours`: Analysis time range (default: 24)

**Returns:** Generated prompt text

#### `list_available_resources() -> List[Dict[str, str]]`
Lists all available MCP resource endpoints.

**Returns:**
```python
[
    {
        "uri": str,
        "description": str,
        "parameters": List[str]
    },
    ...
]
```

#### `get_resource_data(uri: str) -> Dict[str, Any]`
Accesses MCP resource data by URI.

**Parameters:**
- `uri`: Resource URI (e.g., "elite://status/location")

**Returns:** Resource-specific data structure

#### `refresh_resource_cache() -> Dict[str, str]`
Clears MCP resource cache.

**Returns:**
```python
{
    "status": "success",
    "message": "Resource cache cleared"
}
```

## 📊 MCP Resources API

Resources are accessed via URI with query parameters.

### URI Format
```
elite://resource_type/resource_name?parameter=value
```

### Status Resources

#### `elite://status/location`
Current location and coordinates.

**Query Parameters:** None

**Returns:**
```python
{
    "current_system": str,
    "current_station": str | None,
    "docked": bool,
    "coordinates": List[float],
    "last_updated": str
}
```

#### `elite://status/ship`
Current ship status and configuration.

**Returns:**
```python
{
    "ship_type": str,
    "fuel_level": float,
    "hull_health": float,
    "cargo_used": int,
    "cargo_capacity": int
}
```

#### `elite://status/game`
Overall game state and session info.

**Returns:**
```python
{
    "session_start": str,
    "total_events": int,
    "game_mode": str | None,
    "commander_name": str | None
}
```

### Data Resources

#### `elite://journal/recent?minutes=60&limit=100`
Recent journal events.

**Query Parameters:**
- `minutes`: Time range (default: 60)
- `limit`: Maximum events (default: 100)

#### `elite://journal/stats`
Journal statistics and counts.

**Returns:**
```python
{
    "total_events": int,
    "events_by_category": Dict[str, int],
    "events_by_hour": List[int],
    "session_duration": float
}
```

#### `elite://events/by-category?category=exploration&hours=24`
Events filtered by category.

**Query Parameters:**
- `category`: Event category (required)
- `hours`: Time range (default: 24)

#### `elite://events/by-type?type=FSDJump&hours=24`
Events filtered by specific type.

**Query Parameters:**
- `type`: Event type (required)
- `hours`: Time range (default: 24)

### Summary Resources

#### `elite://summary/exploration?hours=24`
Exploration analysis and statistics.

**Query Parameters:**
- `hours`: Analysis time range (default: 24)

#### `elite://summary/trading?hours=12`
Trading performance analysis.

#### `elite://summary/combat?hours=6`
Combat statistics and earnings.

#### `elite://summary/journey?hours=48`
Journey and travel overview.

#### `elite://summary/mining?hours=24`
Mining activities and efficiency.

### Analytics Resources

#### `elite://metrics/performance?hours=24`
Performance metrics and efficiency.

**Returns:**
```python
{
    "time_range_hours": int,
    "credits_per_hour": float,
    "events_per_hour": float,
    "efficiency_score": float,
    "activity_breakdown": Dict[str, float]
}
```

#### `elite://metrics/credits?hours=12`
Credit flow and financial analysis.

**Returns:**
```python
{
    "time_range_hours": int,
    "credits_earned": int,
    "credits_spent": int,
    "net_change": int,
    "earnings_by_activity": Dict[str, int]
}
```

## 🤖 MCP Prompts API

### Template IDs
- `exploration_analysis`
- `trading_strategy`
- `combat_assessment`
- `mining_optimization`
- `mission_guidance`
- `engineering_progress`
- `journey_review`
- `performance_review`
- `strategic_planning`

### Prompt Generation

#### `generate_prompt(template_id: str, time_range_hours: int = 24) -> str`
Generates AI prompt from template with current context.

**Parameters:**
- `template_id`: Template identifier
- `time_range_hours`: Context time range (default: 24)

**Returns:** Generated prompt text with embedded game state

#### Individual Prompt Generators
```python
# Specific prompt generators
await generate_exploration_prompt(time_range_hours=24)
await generate_trading_prompt(time_range_hours=12)
await generate_combat_prompt(time_range_hours=6)
await generate_mining_prompt(time_range_hours=24)
await generate_mission_prompt(time_range_hours=12)
await generate_engineering_prompt(time_range_hours=48)
await generate_journey_prompt(time_range_hours=48)
await generate_performance_prompt(time_range_hours=24)
await generate_strategic_prompt(time_range_hours=72)
```

### Template Structure
```python
{
    "name": str,                    # Human-readable name
    "description": str,             # Template description
    "template": str,                # Prompt template with variables
    "variables": List[str],         # Required variables
    "category": str                 # Activity category
}
```

## 💾 Data Store API

Direct access to the underlying data storage system.

### Global Access
```python
from src.utils.data_store import get_data_store

data_store = get_data_store()
```

### Methods

#### `add_event(event: ProcessedEvent) -> None`
Adds a processed event to storage.

#### `get_recent_events(minutes: int = 60) -> List[ProcessedEvent]`
Gets events from specified time range.

#### `get_events_by_type(event_type: str, limit: int = None) -> List[ProcessedEvent]`
Gets events of specific type.

#### `get_events_by_category(category: EventCategory, limit: int = None) -> List[ProcessedEvent]`
Gets events by category.

#### `get_game_state() -> GameState`
Gets current game state object.

#### `clear_events() -> int`
Clears all stored events, returns count cleared.

#### `get_statistics() -> Dict[str, Any]`
Gets storage statistics and metrics.

### Game State Object
```python
{
    "current_system": str | None,
    "current_station": str | None,
    "current_ship": str | None,
    "docked": bool,
    "fuel_level": float,
    "hull_health": float,
    "credits": int,
    "cargo_used": int,
    "cargo_capacity": int,
    "coordinates": List[float],
    "last_updated": datetime
}
```

## 📝 Event Processing API

### ProcessedEvent Structure
```python
{
    "raw_event": Dict[str, Any],        # Original journal data
    "event_type": str,                  # Event type name
    "timestamp": datetime,              # Event timestamp
    "category": EventCategory,          # Event category
    "summary": str,                     # Human-readable summary
    "key_data": Dict[str, Any],         # Extracted key information
    "is_valid": bool,                   # Validation status
    "validation_errors": List[str]      # Validation error messages
}
```

### Event Categories
```python
class EventCategory(Enum):
    SYSTEM = "system"
    NAVIGATION = "navigation"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    TRADING = "trading"
    MISSION = "mission"
    ENGINEERING = "engineering"
    MINING = "mining"
    PASSENGER = "passenger"
    SQUADRON = "squadron"
    POWERPLAY = "powerplay"
    CREW = "crew"
    SOCIAL = "social"
    SHIP = "ship"
    SUIT = "suit"
    CARRIER = "carrier"
    OTHER = "other"
```

### Event Processor
```python
from src.journal.events import EventProcessor

processor = EventProcessor()

# Process raw event
processed = processor.process_event(raw_journal_event)

# Categorize event
category = processor.categorize_event("FSDJump")

# Generate summary
summary = processor.summarize_event(processed_event)
```

## ⚙️ Configuration API

### EliteConfig Class
```python
from src.utils.config import EliteConfig

config = EliteConfig()
```

### Configuration Properties
```python
config.journal_path: str            # Journal directory path
config.edcopilot_path: str | None   # EDCoPilot directory path
config.debug: bool                  # Debug mode flag
config.max_recent_events: int       # Event storage limit
config.log_level: str               # Logging level
```

### Methods
```python
config.validate_paths() -> bool     # Validate configured paths
config.get_journal_files() -> List[Path]  # Get journal file list
config.to_dict() -> Dict[str, Any]  # Export as dictionary
```

### Environment Variables
- `ELITE_JOURNAL_PATH`
- `ELITE_EDCOPILOT_PATH`
- `ELITE_DEBUG`
- `ELITE_MAX_RECENT_EVENTS`
- `ELITE_LOG_LEVEL`

## 🚨 Error Handling

### Exception Types

#### `EliteConfigError`
Configuration validation and loading errors.

#### `JournalParsingError`
Journal file parsing and validation errors.

#### `EventProcessingError`
Event processing and categorization errors.

#### `MCPServerError`
MCP server initialization and operation errors.

### Error Response Format
```python
{
    "error": str,                   # Error type
    "message": str,                 # Human-readable message
    "details": Dict[str, Any],      # Additional error details
    "timestamp": str,               # Error timestamp
    "context": Dict[str, Any]       # Execution context
}
```

### Error Handling Examples
```python
try:
    events = await get_recent_events(minutes=60)
except Exception as e:
    if "timeout" in str(e):
        # Handle timeout
        pass
    elif "not found" in str(e):
        # Handle missing data
        pass
    else:
        # Log unexpected error
        logger.error(f"Unexpected error: {e}")
```

## 📚 Type Definitions

### Common Types
```python
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# Event data structure
EventData = Dict[str, Any]

# Coordinate system
Coordinates = List[float]  # [x, y, z]

# Time range specification
TimeRange = int  # minutes or hours depending on context

# Event filter criteria
EventFilter = Dict[str, Any]
```

### Response Types
```python
# API response wrapper
class APIResponse:
    success: bool
    data: Any
    error: Optional[str]
    timestamp: datetime

# Resource response
class ResourceResponse:
    uri: str
    data: Dict[str, Any]
    cached: bool
    cache_time: datetime
```

### Function Signatures
```python
# Tool function type
ToolFunction = Callable[..., Awaitable[Dict[str, Any]]]

# Resource getter type
ResourceGetter = Callable[[str], Awaitable[Dict[str, Any]]]

# Prompt generator type
PromptGenerator = Callable[[str, int], Awaitable[str]]
```

---

**This API reference provides complete documentation for all programmatic interfaces. For usage examples, see the [Features Guide](FEATURES_GUIDE.md).**