# ChatGPT and Codex Integration

This guide explains how to use the Elite Dangerous Local AI Tie-In MCP server with ChatGPT-class models and developer tools so you get the same endtoend experience as the existing Claude Desktop integration.

Key idea: ChatGPT (OpenAI) models can be paired with an MCPcapable client (Continue, Cursor, Cline, etc.). These clients speak MCP and let the model call your local MCP tools/resources/prompts, just like Claude Desktop.

## Prerequisites
- Python 3.9+ with this repo set up and working
- The server runs with: `python src/server.py`
- OpenAI API key (for clients using ChatGPT models): set `OPENAI_API_KEY`
- Paths configured for your system (journal and optional EDCoPilot paths)

Environment variables commonly used by the server:

```
ELITE_JOURNAL_PATH      # Elite Dangerous journal directory
ELITE_EDCOPILOT_PATH    # (optional) EDCoPilot custom files directory
ELITE_DEBUG=false       # Enable extra logging when true
```

## Option 1: Continue (VS Code/JetBrains) with OpenAI models
Continue supports MCP servers and can use OpenAI models (ChatGPT) as the LLM provider.

1) Install Continue: https://continue.dev

2) Configure your OpenAI API key (in the Continue settings UI or `~/.continue/config.json`).

3) Add the MCP server configuration. Continue accepts the same `mcpServers` shape used by Claude Desktop. Create or edit `~/.continue/config.json` and add:

```json
{
  "mcpServers": {
    "elite-dangerous": {
      "command": "C:/path/to/elite-dangerous-local-ai-tie-in-mcp/venv/Scripts/python.exe",
      "args": ["C:/path/to/elite-dangerous-local-ai-tie-in-mcp/src/server.py"],
      "env": {
        "ELITE_JOURNAL_PATH": "C:/Users/YourUsername/Saved Games/Frontier Developments/Elite Dangerous",
        "ELITE_EDCOPILOT_PATH": "C:/Utilities/EDCoPilot/User custom files",
        "ELITE_DEBUG": "false"
      }
    }
  }
}
```

Notes:
- On macOS/Linux, point `command` to your venv Python: `.../venv/bin/python`.
- Adjust paths to match your system.

4) Restart Continue. Ask it something like:

```
What is my current Elite Dangerous status?
```

Continue will call MCP tools (e.g., `server_status`, `get_current_location`) to answer.

## Option 2: Cursor with MCP and OpenAI
Cursor supports MCP integrations and OpenAI models.

1) Install Cursor: https://www.cursor.com

2) In Cursor Settings, configure your OpenAI API key.

3) Add an MCP server pointing to this project:
- Settings -> MCP (or Integrations) -> Add Server
- Command: full path to your Python in the project venv
- Args: `src/server.py`
- Env: set `ELITE_JOURNAL_PATH` (and optional vars from above)

4) Restart Cursor and chat with:

```
Use the Elite Dangerous MCP tools to summarize my recent activity.
```

Cursor will invoke the MCP tools/resources to ground its response.

## Option 3: Cline (VS Code) with MCP
Cline is an opensource VS Code extension that supports MCP servers.

1) Install Cline: https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev

2) In VS Code settings (`settings.json`), add a section like:

```json
"cline.mcpServers": {
  "elite-dangerous": {
    "command": "C:/path/to/elite-dangerous-local-ai-tie-in-mcp/venv/Scripts/python.exe",
    "args": ["C:/path/to/elite-dangerous-local-ai-tie-in-mcp/src/server.py"],
    "env": {
      "ELITE_JOURNAL_PATH": "C:/Users/YourUsername/Saved Games/Frontier Developments/Elite Dangerous",
      "ELITE_EDCOPILOT_PATH": "C:/Utilities/EDCoPilot/User custom files",
      "ELITE_DEBUG": "false"
    }
  }
}
```

3) Restart VS Code. Ask Cline to use the Elite Dangerous MCP tools.

## Option 4: Generic MCP Inspector (for validation)
If you want to validate the server outside any IDE, you can use a generic MCP inspector/debug client. One popular option is the MCP Inspector app provided by the MCP community. After installing it, configure a new server with:

- Command: Python from your project venv
- Args: `src/server.py`
- Env: variables from Prerequisites

Then list tools/resources and try `server_status`.

## Usage Tips
- Natural language works best: What system am I docked at? or Summarize my last 24 hours of activity.
- Ask the client to use the Elite Dangerous MCP tools/resources if it needs a hint.
- Useful tools include: `server_status`, `get_current_location`, `get_current_ship`, `get_recent_events`.
- Prompts layer: ask for generate an exploration analysis prompt for the last 24 hours.

## Troubleshooting
- If the client cannot connect:
  - Verify the Python path and `src/server.py` path are correct.
  - Ensure the venv is created and dependencies are installed: `pip install -r requirements.txt`.
  - Check the log file in the project root: `elite_mcp_server.log`.
  - Confirm `ELITE_JOURNAL_PATH` points to your actual Elite Dangerous journal folder.

- If tools return empty data:
  - Start Elite Dangerous or place recent journal files in the configured folder.
  - Set `ELITE_DEBUG=true` temporarily and review logs.

## About ChatGPT Desktop
As of this writing, the official ChatGPT desktop/web clients do not expose a native MCP server configuration the way Claude Desktop does. To achieve equivalent capabilities with ChatGPT models, use an MCPcapable client (Continue, Cursor, Cline, etc.) configured to use OpenAI as the model provider. This gives you Claudelevel MCP functionality with ChatGPT models.


