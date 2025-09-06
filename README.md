# Elite Dangerous Local AI Tie-In MCP

A Model Context Protocol (MCP) server that provides real-time integration between Elite Dangerous and Claude Desktop, enabling AI-powered analysis of your gameplay data and dynamic generation of EDCoPilot custom content.

## Features

🚀 **Real-time Journal Monitoring**: Automatically monitors Elite Dangerous journal files for live gameplay events

🤖 **Claude Desktop Integration**: Provides MCP tools, resources, and prompts for AI-powered gameplay analysis

🎭 **EDCoPilot Integration**: Generates dynamic custom chatter, crew dialogue, and speech extensions based on your current game state

📊 **Comprehensive Analytics**: Track exploration progress, trading performance, combat statistics, and journey summaries

🔧 **Flexible Configuration**: Configurable paths, event limits, and integration options

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Elite Dangerous installed and running
- Claude Desktop application
- EDCoPilot (optional, for voice integration)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GWLlosa/elite-dangerous-local-ai-tie-in-mcp.git
   cd elite-dangerous-local-ai-tie-in-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Claude Desktop**:
   Add the following to your Claude Desktop configuration file:
   
   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
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

4. **Start Elite Dangerous**: Launch the game to begin generating journal data

5. **Restart Claude Desktop**: Required for MCP configuration changes to take effect

## Status

🚧 **Project Status**: Initial development phase (Milestone 1 completed)

This project is currently in active development following a structured 15-milestone implementation plan. 

**Completed**: ✅ Milestone 1 - Project structure and foundation
**Next**: 🔄 Milestone 2 - Configuration management system

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Elite Dangerous by Frontier Developments
- EDCoPilot by RazZaFraG
- Model Context Protocol by Anthropic
- Claude Desktop by Anthropic

---

**Note**: This project is not officially affiliated with Frontier Developments, Anthropic, or the EDCoPilot project. Elite Dangerous is a trademark of Frontier Developments plc.