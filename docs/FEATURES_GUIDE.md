# Elite Dangerous MCP Server - Features Guide

This comprehensive guide covers all features available in the Elite Dangerous MCP Server, including detailed usage examples and integration instructions.

## 📋 Table of Contents

1. [MCP Tools](#mcp-tools-15-available)
2. [MCP Resources](#mcp-resources-17-dynamic-endpoints)
3. [MCP Prompts](#mcp-prompts-9-context-aware-templates)
4. [EDCoPilot Integration](#edcopilot-integration)
5. [Dynamic Theme System (Planned)](#dynamic-theme-system-planned)
6. [Background Services](#background-services)
7. [Claude Desktop Integration](#claude-desktop-integration)
8. [Development API](#development-api)
9. [Configuration Options](#configuration-options)
10. [Troubleshooting](#troubleshooting)

## 🔧 MCP Tools (15+ Available)

MCP Tools provide function-based access to Elite Dangerous data through Claude Desktop or direct API calls.

### Core Data Access Tools

#### `server_status`
Get current server status and operational statistics.

**Usage in Claude:**
```
"What's the status of my Elite Dangerous MCP server?"
```

**API Usage:**
```python
status = await server.server_status()
print(f"Status: {status['status']}")
print(f"Events processed: {status['events_processed']}")
print(f"Uptime: {status['uptime_seconds']} seconds")
```

**Returns:**
```json
{
  "status": "running",
  "events_processed": 1247,
  "uptime_seconds": 3600,
  "memory_usage": "45.2 MB",
  "journal_monitoring": true,
  "last_event_time": "2025-09-13T14:30:00Z"
}
```

#### `get_recent_events`
Retrieve recent journal events with flexible filtering options.

**Parameters:**
- `minutes` (optional): Time range in minutes (default: 60)
- `category` (optional): Event category filter
- `event_type` (optional): Specific event type filter
- `limit` (optional): Maximum number of events

**Usage in Claude:**
```
"Show me my recent exploration events from the last 2 hours"
"Get my recent trading activity"
"What combat events happened in the last 30 minutes?"
```

**API Usage:**
```python
# Recent exploration events
events = await get_recent_events(minutes=120, category="exploration")

# Recent FSD jumps
jumps = await get_recent_events(event_type="FSDJump", limit=10)

# All recent events
all_events = await get_recent_events(minutes=30)
```

#### `get_current_location`
Get current system, station, and coordinate information.

**Usage in Claude:**
```
"Where am I currently located in Elite Dangerous?"
"What system and station am I at?"
```

**API Usage:**
```python
location = await get_current_location()
```

**Returns:**
```json
{
  "current_system": "Sol",
  "current_station": "Abraham Lincoln",
  "docked": true,
  "coordinates": [0, 0, 0],
  "system_population": 22780919008,
  "station_type": "Orbis",
  "last_updated": "2025-09-13T14:30:00Z"
}
```

#### `get_current_ship`
Get current ship information including status and configuration.

**Usage in Claude:**
```
"What ship am I flying and what's its current status?"
"How much fuel and cargo space do I have?"
```

**API Usage:**
```python
ship = await get_current_ship()
```

**Returns:**
```json
{
  "ship_type": "Python",
  "ship_name": "Explorer's Pride",
  "fuel_level": 32.0,
  "fuel_capacity": 32.0,
  "hull_health": 100.0,
  "cargo_used": 15,
  "cargo_capacity": 284,
  "jump_range": 30.5,
  "last_updated": "2025-09-13T14:30:00Z"
}
```

### Activity Analysis Tools

#### `get_exploration_summary`
Analyze exploration activities and progress.

**Parameters:**
- `hours` (optional): Time range in hours (default: 24)

**Usage in Claude:**
```
"Summarize my exploration progress from the last day"
"How many systems have I explored in the last 12 hours?"
```

**API Usage:**
```python
exploration = await get_exploration_summary(hours=24)
```

**Returns:**
```json
{
  "time_range_hours": 24,
  "systems_visited": 15,
  "bodies_scanned": 47,
  "first_discoveries": 3,
  "exploration_earnings": 2847500,
  "distance_traveled": 245.7,
  "scan_types": {
    "detailed": 28,
    "basic": 19
  },
  "most_valuable_discovery": "Earth-like World - 1.2M CR"
}
```

#### `get_trading_summary`
Analyze trading performance and profitability.

**Parameters:**
- `hours` (optional): Time range in hours (default: 24)

**Usage in Claude:**
```
"How's my trading performance today?"
"What's my profit per hour from trading?"
```

**API Usage:**
```python
trading = await get_trading_summary(hours=12)
```

**Returns:**
```json
{
  "time_range_hours": 12,
  "trades_completed": 8,
  "total_profit": 5247000,
  "profit_per_hour": 437250,
  "avg_profit_per_trade": 655875,
  "cargo_runs": 12,
  "best_trade": {
    "commodity": "Gold",
    "profit": 1250000,
    "route": "Sol to Alpha Centauri"
  }
}
```

#### `get_combat_summary`
Analyze combat activities and earnings.

**Parameters:**
- `hours` (optional): Time range in hours (default: 24)

**Usage in Claude:**
```
"Summarize my combat activities and earnings"
"How many bounties have I claimed recently?"
```

**API Usage:**
```python
combat = await get_combat_summary(hours=6)
```

**Returns:**
```json
{
  "time_range_hours": 6,
  "kills": 12,
  "bounties_claimed": 8,
  "bounty_earnings": 3500000,
  "combat_bonds": 1200000,
  "average_bounty": 437500,
  "ship_destroyed": false,
  "damage_taken": 25,
  "most_valuable_target": "Elite Anaconda - 850k CR"
}
```

#### `search_events`
Advanced event searching with multiple filter criteria.

**Parameters:**
- `query` (optional): Text search in event summaries
- `category` (optional): Event category
- `event_type` (optional): Specific event type
- `system` (optional): System name filter
- `hours` (optional): Time range
- `limit` (optional): Result limit

**Usage in Claude:**
```
"Search for all events containing 'pirate' in the last 4 hours"
"Find all market sell events in the Sol system"
```

**API Usage:**
```python
# Search for combat events
combat_events = await search_events(category="combat", hours=24)

# Search for specific commodity trades
gold_trades = await search_events(query="Gold", category="trading")
```

### AI Assistance Tools

#### `list_available_prompts`
List all available AI prompt templates.

**Usage in Claude:**
```
"What AI analysis prompts are available?"
"Show me all prompt templates"
```

**API Usage:**
```python
prompts = await list_available_prompts()
```

**Returns:**
```json
[
  {
    "id": "exploration_analysis",
    "name": "Exploration Analysis",
    "description": "Analyze recent exploration activities and provide strategic recommendations",
    "category": "exploration"
  },
  {
    "id": "trading_strategy",
    "name": "Trading Strategy",
    "description": "Evaluate trading performance and suggest optimization strategies",
    "category": "trading"
  }
]
```

#### `generate_analysis_prompt`
Generate context-aware AI prompts for any activity type.

**Parameters:**
- `activity_type`: Type of analysis (exploration, trading, combat, mining, etc.)
- `time_range_hours` (optional): Analysis time range (default: 24)

**Usage in Claude:**
```
"Generate an exploration analysis prompt for the last 24 hours"
"Create a trading strategy prompt based on my recent activities"
```

**API Usage:**
```python
# Generate exploration prompt
exploration_prompt = await generate_analysis_prompt("exploration", 24)

# Generate combat analysis
combat_prompt = await generate_analysis_prompt("combat", 12)
```

## 📊 MCP Resources (17+ Dynamic Endpoints)

MCP Resources provide URI-based access to structured data with query parameter support.

### Status Resources

#### `elite://status/location`
Current location and coordinate information.

**Usage in Claude:**
```
"Get my current location from the location resource"
```

**API Usage:**
```python
location = await get_resource_data("elite://status/location")
```

#### `elite://status/ship`
Current ship status and configuration.

**API Usage:**
```python
ship = await get_resource_data("elite://status/ship")
```

#### `elite://status/game`
Overall game state and session information.

**API Usage:**
```python
game_state = await get_resource_data("elite://status/game")
```

### Data Resources

#### `elite://journal/recent?minutes=60`
Recent journal events with time filtering.

**Query Parameters:**
- `minutes`: Time range in minutes (default: 60)
- `limit`: Maximum number of events

**API Usage:**
```python
# Last 30 minutes of events
recent = await get_resource_data("elite://journal/recent?minutes=30")

# Last 100 events from past 2 hours
events = await get_resource_data("elite://journal/recent?minutes=120&limit=100")
```

#### `elite://journal/stats`
Journal statistics and event counts.

**API Usage:**
```python
stats = await get_resource_data("elite://journal/stats")
```

#### `elite://events/by-category?category=exploration`
Events filtered by category.

**Categories:** exploration, trading, combat, mining, missions, engineering, navigation, system, social, ship, passenger, powerplay, carrier, crew, squadron, suit, other

**API Usage:**
```python
# Get exploration events
exploration = await get_resource_data("elite://events/by-category?category=exploration")

# Get trading events
trading = await get_resource_data("elite://events/by-category?category=trading")
```

#### `elite://events/by-type?type=FSDJump`
Events filtered by specific type.

**API Usage:**
```python
# Get all FSD jumps
jumps = await get_resource_data("elite://events/by-type?type=FSDJump")

# Get market sell events
sales = await get_resource_data("elite://events/by-type?type=MarketSell")
```

### Activity Summary Resources

#### `elite://summary/exploration?hours=24`
Comprehensive exploration analysis.

**Query Parameters:**
- `hours`: Analysis time range (default: 24)

**API Usage:**
```python
exploration = await get_resource_data("elite://summary/exploration?hours=48")
```

#### `elite://summary/trading?hours=12`
Trading performance analysis.

**API Usage:**
```python
trading = await get_resource_data("elite://summary/trading?hours=12")
```

#### `elite://summary/combat?hours=6`
Combat statistics and analysis.

**API Usage:**
```python
combat = await get_resource_data("elite://summary/combat?hours=6")
```

#### `elite://summary/journey?hours=48`
Journey and travel analysis.

**API Usage:**
```python
journey = await get_resource_data("elite://summary/journey?hours=48")
```

### Analytics Resources

#### `elite://metrics/performance?hours=24`
Performance metrics and efficiency analysis.

**API Usage:**
```python
performance = await get_resource_data("elite://metrics/performance?hours=24")
```

#### `elite://metrics/credits?hours=12`
Credit flow and financial analysis.

**API Usage:**
```python
credits = await get_resource_data("elite://metrics/credits?hours=12")
```

## 🤖 MCP Prompts (9 Context-Aware Templates)

MCP Prompts generate AI-assistance prompts tailored to your current game state and recent activities.

### Available Prompt Templates

#### Exploration Analysis (`exploration_analysis`)
Analyzes recent exploration activities and provides strategic recommendations.

**Usage in Claude:**
```
"Generate an exploration analysis prompt for my recent activities"
```

**Includes:**
- Systems visited and bodies scanned
- First discoveries and earnings
- Equipment and ship loadout assessment
- Optimization recommendations

#### Trading Strategy (`trading_strategy`)
Evaluates trading performance and suggests optimization strategies.

**Usage in Claude:**
```
"Create a trading strategy prompt based on my current performance"
```

**Includes:**
- Trade route analysis
- Profit optimization suggestions
- Market opportunity identification
- Cargo and ship optimization

#### Combat Assessment (`combat_assessment`)
Analyzes combat performance and tactical effectiveness.

**Usage in Claude:**
```
"Generate a combat assessment prompt for my recent battles"
```

**Includes:**
- Combat statistics and earnings
- Ship loadout effectiveness
- Tactical recommendations
- Risk assessment

#### Mining Optimization (`mining_optimization`)
Reviews mining activities and suggests efficiency improvements.

**Includes:**
- Mining yield analysis
- Equipment optimization
- Location recommendations
- Profit maximization strategies

#### Mission Guidance (`mission_guidance`)
Provides mission planning and completion strategies.

**Includes:**
- Active mission status
- Completion strategies
- Risk/reward analysis
- Route optimization

#### Engineering Progress (`engineering_progress`)
Tracks engineering upgrades and material requirements.

**Includes:**
- Current upgrade status
- Material inventory
- Engineer relationships
- Upgrade priorities

#### Journey Review (`journey_review`)
Analyzes travel patterns and route efficiency.

**Includes:**
- Route analysis
- Jump range optimization
- Fuel efficiency
- Exploration opportunities

#### Performance Review (`performance_review`)
Comprehensive gameplay performance analysis.

**Includes:**
- Overall progression metrics
- Activity effectiveness
- Goal achievement tracking
- Future recommendations

## 🎭 EDCoPilot Integration

The Elite Dangerous MCP Server provides comprehensive integration with EDCoPilot voice software, enabling dynamic generation of custom chatter files based on your current gameplay state.

### EDCoPilot MCP Tools

#### `generate_edcopilot_chatter`
Generates contextual chatter files based on current game state.

**Usage in Claude:**
```
"Generate EDCoPilot chatter for my current situation"
```

**Parameters:**
- `chatter_type` (optional): "space", "crew", "deepspace", or "all"
- `context_override` (optional): Custom context for generation

**Returns:**
- Generation status and file locations
- Entry count and context analysis
- Backup file information

#### `get_edcopilot_status`
Check EDCoPilot integration configuration and file status.

**Usage in Claude:**
```
"Check my EDCoPilot integration status"
```

**Returns:**
```json
{
  "status": "available",
  "edcopilot_path": "C:/Utilities/EDCoPilot/User custom files",
  "path_exists": true,
  "custom_files": {
    "space_chatter": "EDCoPilot.SpaceChatter.Custom.txt",
    "crew_chatter": "EDCoPilot.CrewChatter.Custom.txt",
    "deep_space": "EDCoPilot.DeepSpaceChatter.Custom.txt"
  },
  "game_context": {
    "current_system": "Sol",
    "docked": true,
    "ship": "Anaconda",
    "primary_activity": "exploration"
  }
}
```

#### `backup_edcopilot_files`
Create timestamped backups of existing EDCoPilot custom files.

**Usage in Claude:**
```
"Backup my current EDCoPilot files before generating new content"
```

#### `preview_edcopilot_chatter`
Preview generated content without writing files.

**Usage in Claude:**
```
"Show me a preview of what EDCoPilot chatter would be generated"
```

### Chatter Types

#### Space Chatter
General ship operations and navigation dialogue.

**Example Content:**
```
condition:InSupercruise|Entering {SystemName}, Commander. Scanning for points of interest.
condition:Docked|Successfully docked at {StationName}. All systems secure.
condition:FuelLow|Fuel reserves at {FuelPercent}%. Recommend refueling soon, Commander.
```

#### Crew Chatter
Professional crew member reports and updates.

**Example Content:**
```
condition:InSupercruise|Navigation officer reports jump calculations complete, Commander.
condition:Docked|Engineering reports all systems nominal. Power distribution at peak efficiency.
condition:UnderAttack|All hands, red alert! Hostile contacts on approach vector!
```

#### Deep Space Chatter
Special dialogue for deep space exploration (>5000 LY from Sol/Colonia).

**Example Content:**
```
condition:DeepSpace|We're {DistanceFromSol} light years from home. The isolation is profound.
condition:DeepSpace&Exploring|Out here in the void, every star is a beacon of hope in the cosmic darkness.
```

### Context-Aware Generation

The system analyzes your recent gameplay to generate appropriate chatter:

- **Exploration Focus**: Enhanced discovery and scanning dialogue
- **Trading Focus**: Market analysis and cargo management chatter
- **Combat Focus**: Tactical updates and threat assessments
- **Low Fuel**: Urgent fuel management warnings
- **Current Location**: References to actual systems and stations

## 🎪 Dynamic Theme System (Planned)

*Milestone 11.5 - Planned Enhancement*

The upcoming Dynamic Theme System will transform EDCoPilot integration from static templates to AI-powered, personalized dialogue generation.

### Planned Features

#### Theme-Based Personality
Set overall character themes that influence all dialogue:
- **Space Pirate**: "Entering {SystemName}. Raise the Jolly Roger, matey!"
- **Corporate Executive**: "Entering {SystemName}. Analyzing market opportunities."
- **Military Veteran**: "Jump complete to {SystemName}. These old bones have seen enough combat."

#### Ship-Specific Multi-Crew
Realistic crew compositions based on ship size:
- **Small Ships (1-2 crew)**: Intimate, personal dialogue
- **Medium Ships (3-4 crew)**: Professional team operations
- **Large Ships (5+ crew)**: Full bridge crew with specialized roles

#### Individual Crew Personalities
Each crew member gets their own theme and background:
- **Navigator**: "By-the-book military officer, 30-year veteran"
- **Science Officer**: "Excited researcher on first deep space mission"
- **Engineer**: "Gruff Scottish mechanic with 40 years experience"

#### Dynamic AI Generation
- Leverages existing Claude Desktop connection
- No additional API keys or session management required
- Unlimited theme possibilities through AI generation
- Maintains all token functionality for game data integration

### Planned MCP Tools

#### `set_edcopilot_theme`
Set overall personality theme with context.

**Usage:**
```
"Set my EDCoPilot theme to space pirate who owes money to the Space Mafia"
```

#### `configure_ship_crew`
Set up crew composition for specific ships.

**Usage:**
```
"Configure my Anaconda with a 6-person bridge crew"
```

#### `set_crew_member_theme`
Assign individual personalities to crew members.

**Usage:**
```
"Make my navigator a by-the-book officer and my engineer a quirky inventor"
```

See `docs/milestones/MILESTONE_11_5_PLANNED.md` for complete specification.

## 🔄 Background Services

**Includes:**
- Overall statistics
- Efficiency metrics
- Credit earnings analysis
- Improvement recommendations

#### Strategic Planning (`strategic_planning`)
Long-term goal planning and achievement strategies.

**Includes:**
- Goal assessment
- Progress tracking
- Resource requirements
- Strategic recommendations

### Prompt Generation API

#### Generate Specific Prompts
```python
# Generate exploration analysis
exploration_prompt = await generate_exploration_prompt(time_range_hours=24)

# Generate trading strategy
trading_prompt = await generate_trading_prompt(time_range_hours=12)

# Generate combat assessment
combat_prompt = await generate_combat_prompt(time_range_hours=6)
```

#### Generic Prompt Generation
```python
# Use generate_analysis_prompt for any type
prompt = await generate_analysis_prompt("mining", 24)
```

## 🔄 Background Services

The MCP server runs several background services automatically:

### Journal Monitoring
- **Function**: Real-time monitoring of Elite Dangerous journal files
- **Features**: File rotation detection, position tracking, automatic reconnection
- **Performance**: <1ms event processing latency

### Event Processing
- **Function**: Classification and summarization of journal events
- **Features**: 130+ event types across 17 categories
- **Performance**: Real-time processing with concurrent handling

### State Tracking
- **Function**: Maintains current game state (location, ship, status)
- **Features**: Automatic state updates, historical tracking
- **Performance**: Instant state queries

### Memory Management
- **Function**: Automatic cleanup and memory optimization
- **Features**: Configurable event limits, garbage collection
- **Performance**: Optimized for long-running sessions

## 🖥️ Claude Desktop Integration

### Configuration
Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "elite-dangerous": {
      "command": "python",
      "args": ["C:/path/to/elite-dangerous-local-ai-tie-in-mcp/src/server.py"],
      "env": {
        "ELITE_JOURNAL_PATH": "C:/Users/YourName/Saved Games/Frontier Developments/Elite Dangerous",
        "ELITE_DEBUG": "false"
      }
    }
  }
}
```

### Natural Language Queries

Once configured, you can interact naturally with Claude:

#### Basic Information
- "What's my current ship and location?"
- "How much fuel do I have?"
- "What's my recent activity?"

#### Analysis Requests
- "Analyze my exploration progress"
- "How profitable was my trading today?"
- "Summarize my combat performance"

#### Strategic Planning
- "Help me plan an exploration route"
- "Suggest trading optimizations"
- "Create a mission completion strategy"

#### Data Access
- "Show me recent FSD jumps"
- "What materials have I collected?"
- "List my engineering progress"

## 💻 Development API

### Direct Server Usage
```python
from src.server import EliteDangerousServer

# Initialize (starts monitoring automatically)
server = EliteDangerousServer()

# Access components directly
data_store = server.data_store
mcp_tools = server.mcp_tools
mcp_resources = server.mcp_resources
mcp_prompts = server.mcp_prompts
```

### Data Store Access
```python
from src.utils.data_store import get_data_store

data_store = get_data_store()

# Get current state
game_state = data_store.get_game_state()

# Get recent events
events = data_store.get_recent_events(minutes=60)

# Query by category
exploration = data_store.get_events_by_category("exploration")
```

### Event Processing
```python
from src.journal.events import EventProcessor

processor = EventProcessor()

# Process raw journal event
processed = processor.process_event({
    "event": "FSDJump",
    "timestamp": "2025-09-13T14:30:00Z",
    "StarSystem": "Sol"
})
```

## ⚙️ Configuration Options

### Environment Variables
- `ELITE_JOURNAL_PATH`: Journal directory path (auto-detected if not set)
- `ELITE_EDCOPILOT_PATH`: EDCoPilot custom files directory
- `ELITE_DEBUG`: Enable debug logging (true/false)
- `ELITE_MAX_RECENT_EVENTS`: Event storage limit (default: 10000)

### Configuration File
Create `config.json` in project root:

```json
{
  "journal_path": "/path/to/elite/journals",
  "edcopilot_path": "/path/to/edcopilot/custom/files",
  "debug": false,
  "max_recent_events": 10000,
  "log_level": "INFO"
}
```

## 🔧 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check environment
python scripts/check_environment.py

# Verify dependencies
python scripts/setup_dependencies.py

# Check logs
tail -f elite_mcp_server.log
```

#### Missing Data
```bash
# Verify journal path
python -c "from src.utils.config import EliteConfig; print(EliteConfig().journal_path)"

# Check file permissions
ls -la "path/to/elite/journals/"

# Test journal parsing
python scripts/test_journal_parsing.py
```

#### Claude Desktop Connection
1. Verify configuration file syntax
2. Check server startup in logs
3. Restart Claude Desktop
4. Test with basic queries

#### Performance Issues
```python
# Clear resource cache
await refresh_resource_cache()

# Check memory usage
status = await server_status()
print(f"Memory: {status['memory_usage']}")

# Reduce event limit
export ELITE_MAX_RECENT_EVENTS=5000
```

### Diagnostic Commands
```bash
# Full system check
python scripts/run_tests.py

# Environment validation
python scripts/check_environment.py

# Server status
curl http://localhost:8000/health  # If HTTP endpoint enabled
```

### Log Analysis
```bash
# View recent logs
tail -f elite_mcp_server.log

# Search for errors
grep "ERROR" elite_mcp_server.log

# Monitor in real-time
tail -f elite_mcp_server.log | grep "INFO\|ERROR\|WARNING"
```

---

**This comprehensive features guide covers all capabilities of the Elite Dangerous MCP Server. For additional help, see the main [README](../README.md) or [Testing Guide](TESTING_GUIDE.md).**