# Elite Dangerous Local AI Tie-In MCP

A Model Context Protocol (MCP) server that provides real-time integration between Elite Dangerous and Claude Desktop, enabling AI-powered analysis of your gameplay data and dynamic generation of EDCoPilot custom content.

## Features

🚀 **Real-time Journal Monitoring**: Automatically monitors Elite Dangerous journal files for live gameplay events

🤖 **Claude Desktop Integration**: Provides MCP tools, resources, and prompts for AI-powered gameplay analysis

🎭 **EDCoPilot Integration**: Generates dynamic custom chatter, crew dialogue, and speech extensions based on your current game state

📊 **Comprehensive Analytics**: Track exploration progress, trading performance, combat statistics, and journey summaries

🔧 **Flexible Configuration**: Configurable paths, event limits, and integration options

## 🚀 Quick Start

### Automated Setup (Recommended)

For the fastest setup experience, use our automation scripts:

```powershell
# 1. Clone the repository
git clone https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp.git
cd elite-dangerous-local-ai-tie-in-mcp

# 2. Set up all dependencies automatically
python scripts/setup_dependencies.py

# 3. Verify environment setup
python scripts/check_environment.py

# 4. Run tests to verify everything works
python scripts/run_tests.py
```

### Prerequisites

- **Python 3.9+** (Python 3.11+ recommended)
- **Git** for version control
- **Elite Dangerous** installed and running
- **Claude Desktop** application
- **EDCoPilot** (optional, for voice integration)

### Manual Installation

If you prefer manual setup:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp.git
   cd elite-dangerous-local-ai-tie-in-mcp
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate     # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python scripts/check_environment.py
   ```

See the [Testing Guide](docs/TESTING_GUIDE.md) for detailed setup and verification instructions.

## 🧪 Testing and Development

### Available Scripts
- **`scripts/setup_dependencies.py`** - Automated environment setup with package verification
- **`scripts/check_environment.py`** - Comprehensive environment validation
- **`scripts/run_tests.py`** - Run complete test suite with coverage reporting

### Running Tests
```bash
# Quick test run with coverage
python scripts/run_tests.py

# Manual test execution
pytest tests/ -v --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
```

### Test Coverage
- **194+ tests** passing with **86% code coverage**
- **Real-time monitoring** validated with mock journal events
- **Event processing** tested with 130+ event types
- **Data storage** verified with concurrent access patterns
- **MCP server** tested with comprehensive unit tests

### Documentation
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing instructions
- **[Scripts Documentation](scripts/README.md)** - Automation script details
- **[AI Directives](ai-directives/README.md)** - Development guidelines for AI assistants

## Configuration

### Claude Desktop Integration

Add the following to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "elite-dangerous": {
      "command": "python",
      "args": ["path/to/elite-dangerous-local-ai-tie-in-mcp/src/server.py"],
      "env": {
        "ELITE_JOURNAL_PATH": "/path/to/elite/dangerous/journals",
        "ELITE_EDCOPILOT_PATH": "C:/Utilities/EDCoPilot/User custom files",
        "ELITE_DEBUG": "false"
      }
    }
  }
}
```

### Environment Variables
- `ELITE_JOURNAL_PATH` - Path to Elite Dangerous journal directory (auto-detected if not set)
- `ELITE_EDCOPILOT_PATH` - Path to EDCoPilot custom files directory
- `ELITE_DEBUG` - Enable debug logging (true/false)
- `ELITE_MAX_RECENT_EVENTS` - Maximum recent events to store (default: 10000)

## 📊 Project Status

**Current Status**: Active development - Milestones 1-7 completed ✅

### ✅ Completed Milestones:
1. **Project Structure** - Complete foundation and build system
2. **Configuration Management** - Environment variables and path validation
3. **Journal File Discovery** - File parsing with comprehensive tests  
4. **Real-time Monitoring** - File system watching with position tracking
5. **Event Processing** - 130+ event types across 17 categories
6. **Data Storage** - In-memory storage with thread safety and game state tracking
7. **MCP Server Framework** - FastMCP integration with background monitoring

### 🔄 In Progress:
8. **Core MCP Tools** - Implementation of primary MCP tools for game queries
9. **MCP Resources** - Dynamic resource exposure based on game state
10. **MCP Prompts** - Context-aware prompts for gameplay scenarios

### 🎯 Upcoming Milestones:
11. **EDCoPilot Integration** - Dynamic custom chatter generation
12. **Analytics Dashboard** - Comprehensive gameplay statistics
13. **Performance Optimization** - Caching and efficiency improvements
14. **Documentation & Polish** - User guides and API documentation
15. **Release Preparation** - Final testing and deployment packaging

## 🛠️ MCP Server Features

### Available Tools
- **`server_status`** - Get current server status and statistics
- **`get_recent_events`** - Retrieve recent journal events with filtering
- **`clear_data_store`** - Clear stored events and reset game state

### Background Services
- **Journal Monitoring** - Automatic real-time journal file watching
- **Event Processing** - Classification and summarization of game events
- **State Tracking** - Current ship, location, and game mode tracking
- **Automatic Cleanup** - Memory management for long-running sessions

## 🎯 Usage Examples

### Starting the MCP Server
```bash
# Direct server startup
python src/server.py

# Or configure in Claude Desktop (see Configuration section)
```

### Querying Game State (via Claude Desktop)
Once the server is running and connected to Claude Desktop, you can ask:
- "What's my current location in Elite Dangerous?"
- "Show me my recent exploration discoveries"
- "Summarize my trading activity from the last hour"
- "What happened in my last combat encounter?"

### Development API Example
```python
from src.server import EliteDangerousServer
from src.journal.monitor import JournalMonitor

# Server automatically starts monitoring on initialization
server = EliteDangerousServer()

# Access server tools
status = await server.server_status()
events = await server.get_recent_events(minutes=60, category="exploration")

# Get current game state
state = server.data_store.get_game_state()
print(f"Current System: {state.current_system}")
print(f"Ship: {state.current_ship}")
```

## Contributing

1. **Check Tests**: Run `python scripts/run_tests.py` to verify functionality
2. **Fork the repository**
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`
4. **Add tests** for new functionality (maintain >90% coverage)
5. **Ensure tests pass**: All tests must pass before submitting
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Workflow
- Use the automation scripts for setup: `scripts/setup_dependencies.py`
- Run tests frequently: `python scripts/run_tests.py`
- Check environment: `python scripts/check_environment.py`
- Follow the [AI Directives](ai-directives/README.md) for consistency
- Create session reports for knowledge preservation

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Elite Dangerous** by Frontier Developments
- **EDCoPilot** by RazZaFraG  
- **Model Context Protocol** by Anthropic
- **Claude Desktop** by Anthropic

---

**Note**: This project is not officially affiliated with Frontier Developments, Anthropic, or the EDCoPilot project. Elite Dangerous is a trademark of Frontier Developments plc.
