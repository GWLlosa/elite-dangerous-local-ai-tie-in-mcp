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

# 3. Activate virtual environment (Windows)
.\venv\Scripts\Activate.ps1

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
   python scripts/check_dependencies.py
   ```

See the [Testing Guide](docs/TESTING_GUIDE.md) for detailed setup and verification instructions.

## 🧪 Testing and Development

### Available Scripts
- **`scripts/setup_dependencies.py`** - Automated environment setup
- **`scripts/check_dependencies.py`** - Verify environment and dependencies
- **`scripts/run_tests.py`** - Run complete test suite with progress reporting

### Running Tests
```bash
# Quick test run
python scripts/run_tests.py

# Manual test execution
pytest tests/unit/ -v --cov=src
```

### Documentation
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing instructions
- **[Scripts Documentation](scripts/README.md)** - Automation script details

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
- `ELITE_JOURNAL_PATH` - Path to Elite Dangerous journal directory
- `ELITE_EDCOPILOT_PATH` - Path to EDCoPilot custom files directory
- `ELITE_DEBUG` - Enable debug logging (true/false)
- `ELITE_MAX_RECENT_EVENTS` - Maximum recent events to store (default: 1000)

## 📊 Project Status

**Current Status**: Active development - Milestones 1-4 completed

### ✅ Completed Milestones:
1. **Project Structure** - Complete foundation and build system
2. **Configuration Management** - Environment variables and path validation
3. **Journal File Discovery** - File parsing and discovery with comprehensive tests  
4. **Real-time Monitoring** - File system watching with position tracking

### 🔄 Next Milestones:
5. **Event Processing** - Journal event classification and summarization
6. **Data Storage** - In-memory event storage and retrieval
7. **MCP Server Framework** - Core MCP tools, resources, and prompts

### Test Coverage:
- **47+ unit tests** with >96% code coverage
- **Real-time monitoring** tested with file system operations
- **Configuration system** validated across platforms
- **Journal parsing** tested with mock Elite Dangerous data

## 🎯 Usage Example

Once fully implemented, the system will provide:

```python
# Real-time journal monitoring
monitor = JournalMonitor(journal_path, callback)
await monitor.start_monitoring()

# Event processing and analysis  
events = processor.get_recent_events('exploration', hours=24)
summary = processor.generate_summary(events)

# EDCoPilot integration
generator.create_contextual_chatter(current_location, recent_events)
```

## Contributing

1. **Check Tests**: Run `python scripts/run_tests.py` to verify functionality
2. **Fork the repository**
3. **Create a feature branch**: `git checkout -b feature/amazing-feature`
4. **Add tests** for new functionality
5. **Ensure tests pass**: All tests must pass before submitting
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Workflow
- Use the automation scripts for setup: `scripts/setup_dependencies.py`
- Run tests frequently: `python scripts/run_tests.py`
- Check dependencies: `python scripts/check_dependencies.py`
- Follow the [Testing Guide](docs/TESTING_GUIDE.md) for detailed procedures

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Elite Dangerous** by Frontier Developments
- **EDCoPilot** by RazZaFraG  
- **Model Context Protocol** by Anthropic
- **Claude Desktop** by Anthropic

---

**Note**: This project is not officially affiliated with Frontier Developments, Anthropic, or the EDCoPilot project. Elite Dangerous is a trademark of Frontier Developments plc.
