# AGENTS Rules for This Repository

Scope: This file lives at the repository root and applies to the entire codebase. If nested AGENTS.md files exist, the mostspecific file (deepest directory) takes precedence for files in its scope.

Purpose: Give AI coding agents concise, enforceable rules for working in this repo. Follow these rules when reading, writing, or refactoring code, tests, and docs. Human/user instructions always take precedence over this file.

## Development Workflow
- Use feature branches and pull requests for all nontrivial work.
- Do not merge without explicit user approval after tests pass.
- Validate environment first: `python scripts/check_dependencies.py`.
- Run tests via: `python scripts/run_tests.py` (preferred) or `pytest`.
- Keep changes minimal, targeted, and aligned with existing style.

## Code Quality & Compatibility
- Python style: PEP 8 with type hints and helpful docstrings.
- Tests: Provide real assertions and aim for >90% coverage for new/changed code.
- Crossplatform: Code must run on Windows, Linux, and macOS.
- Error handling: Fail gracefully with clear messages; prefer structured error objects over `None` returns for error cases.
- Character encoding: Use ASCIIonly in Python code and program output (no emojis/smart quotes/extended Unicode). ASCII status tags like `[SUCCESS]`, `[FAILED]` are allowed.

## Input Semantics
- Empty string defaults: Treat empty strings (e.g., "") as selecting the default value when a parameter is optional. Only raise errors when a field is explicitly required and the value is `None`.
  - Example: ThemeMCPTools accepts "" for `theme`/`context` as defaults; `None` is invalid.

## Time & Datetime Rules
- All datetimes must be timezoneaware and in UTC.
  - WRONG: `datetime.utcnow()` (naive)
  - CORRECT: `from datetime import datetime, timezone; datetime.now(timezone.utc)`
  - When parsing or returning timestamps (e.g., file info, extracted journal timestamps), ensure timezone awareness. For parsed values, set `tzinfo=timezone.utc` if the source is known to be UTC.

## Elite Dangerous Data Model Rules
- ProcessedEvent
  - Constructor uses `raw_event` for the original event dict.
  - Access original fields via `event.raw_event`; access derived/important fields via `event.key_data`.
- JournalParser
  - `read_journal_file()` returns `(entries, position)`. Always unpack both.
- JournalMonitor
  - Must be constructed with required parameters, including `journal_path` and `event_callback`.

## DataStore API Usage
- Allowed methods include: `query_events(...)`, `get_events_by_type(event_type, limit)`, `get_events_by_category(category, limit)`, `get_recent_events(minutes)`, `get_game_state()`, `get_statistics()`.
- Do NOT call nonexistent methods like `get_all_events()`.
- When you have hours, convert to minutes before calling `get_recent_events`.

## MCP (Model Context Protocol) Rules
- FastMCP tools: Use the `@app.tool()` decorator to register tools.
- Do not rely on nonexistent `app.tools` collections.
- Resources: For unknown URIs, return structured error objects with helpful fields (e.g., `{"error": "...", "available_resources": [...]}`) - never return `None`.

## Template & Prompt Rules
- Variable detection must support formatted variables (e.g., `{credits:,}`, `{distance:.1f}`).
- When validating variables, consider both `{var}` and `{var:` patterns.

## EDCoPilot Chatter Generation
- Conform to the formal chatter grammar described in `docs/edcopilot-chatter-grammar.md`.
- Replace ALL `{TokenName}` placeholders with safe fallbacks when data is missing.
- Use `condition:Name|...` for spacechatter conditions and `[example]` / `[\example]` blocks for crew chatter, per grammar.

## Documentation
- Update or add docs relevant to the code you change.
- Maintain ASCII in code snippets and program output examples.

## Documentation Update Protocol (MANDATORY)
- When the user asks to "update the documentation" or to "add a rule":
  - Update all three in lockstep:
    - `AGENTS.md` (binding agent rules; repositorywide)
    - `.cursorrules` (portable mirror for Cursor)
    - `ai-directives/` (project context: goals, strategies, status, reports)
  - Place content correctly:
    - Normative rules/process -> `AGENTS.md` and `.cursorrules`
    - Rationale, status, milestones, lessons -> `ai-directives` (README or relevant file)
  - Keep `.cursorrules` wording aligned with `AGENTS.md` where applicable.
  - Add crosslinks to reduce duplication.
  - Commit with a clear `docs:` message describing the trifile update.

## Testing & Scripts
- Preferred scripts:
  - `python scripts/check_dependencies.py` - verifies environment.
  - `python scripts/run_tests.py` - runs full suite with coverage.
- Keep tests platformagnostic and deterministic. Mock external dependencies where appropriate.

## Prohibited / Common Mistakes
- Using `get_all_events()` or referencing `event.data`.
- Returning `None` for error cases in MCP resources.
- Creating naive datetimes.
- Depending on undocumented framework attributes (e.g., `app.tools`).
- Introducing nonASCII output in code or logs.

## Pull Request Checklist
- Feature branch created and pushed.
- Code follows rules above and existing style.
- Tests added/updated, pass locally; coverage maintained or improved.
- Docs updated (README/feature docs) if behavior or usage changed.
- Share test results with the user and wait for explicit approval before merge.


