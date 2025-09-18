# Milestone 16: Headless EDCoPilot Generation CLI

Status: Planned
Owner: AI + Maintainer review

## Objective
Provide a headless Python CLI that generates EDCoPilot chatter files without opening Claude Desktop. The CLI reads Elite Dangerous journals, derives game context, and writes grammar-valid, ASCII-only chatter files. Defaults are safe and user-friendly.

## Why
- Automate generation in batch/CI without Claude Desktop.
- Deterministic direct mode using project internals.
- Optional future enhancements (not in v1): API-assisted creativity, MCP client mode.

## Scope (v1)
- Script: `scripts/generate_edcopilot.py`
- Direct Mode only: import repo modules to parse/process/generate.
- Inputs:
  - Time window (local -> UTC):
    - `--from YYYY-MM-DD[THH:MM]` and `--to YYYY-MM-DD[THH:MM]`, or
    - `--hours N` (default: 7 days if not provided)
  - Content:
    - `--theme` (default: "Grizzled Veteran Space Captain")
    - `--context` (default: "Worn Hands, Endless Horizon")
    - `--types` (optional; default: all available chatter types)
  - Paths:
    - `--edcopilot-path` (defaults from config)
    - `--journal-path` (optional override)
    - `--output-dir` (optional alternate target for testing)
  - Behavior:
    - `--dry-run`, `--no-backup`, `--overwrite`, `--limit-entries N`, `--log-level info|debug`, `--fail-on-warn`
- Outputs:
  - ASCII-only files; EDCoPilot grammar validated; backups as `[name].bak.[YYYYMMDD-HHMMSSZ]` unless `--no-backup`.
  - UTC timestamps in logs and backups.

## Data Flow
1. Resolve time window (assume local inputs; convert to UTC internally).
2. Discover and parse journal files overlapping the window (by filename timestamp and/or mtime).
3. Process entries to ProcessedEvent; store in DataStore.
4. Analyze context from DataStore (existing analyzer).
5. Generate chatter files using EDCoPilot generator + template validator.
6. Write atomically with backups; respect `--dry-run`, `--output-dir`, `--overwrite`.

## Validation & Safety
- Grammar validation must pass; `--fail-on-warn` to escalate warnings to errors.
- ASCII-only content; UTC datetimes; structured error messages.
- Exit codes: 0 success; 1 validation; 2 IO/path/config; 3 arg errors.

## Testing Plan
- Unit tests:
  - Arg parsing: mutual exclusion (`--hours` vs `--from/--to`); defaults (7 days, theme, context).
  - Local->UTC conversion correctness.
  - Backup naming format; `--no-backup`; `--overwrite` gating.
  - `--dry-run` produces no writes and logs planned actions.
  - `--types` filters output set correctly.
  - `--output-dir` redirects writes.
  - `--fail-on-warn` behavior.
- Integration tests:
  - Use mock journals for a small window; generate to a temp dir; verify files and grammar pass.
  - Edge cases: empty window, invalid paths, missing journals.

## Documentation (Tri-file Protocol)
- AGENTS.md: add rules for this CLI (ASCII-only, UTC, grammar pass, backups, safe defaults).
- .cursorrules: mirror essential rules succinctly.
- ai-directives/README.md: add milestone summary and link to this plan.
- Root README + docs/FEATURES_GUIDE.md + scripts/README.md: add "Headless EDCoPilot Generation" usage section.

## Non-goals (v1)
- Anthropic API enhancement mode.
- MCP protocol client mode.

## Risks & Mitigations
- Journal coverage vs window: discover by filename timestamp; fall back to mtime.
- Performance: direct parsing is performant; `--limit-entries` available for debug.
- Windows path quirks: use existing config/path validation helpers and clear errors.

## Acceptance Criteria
- CLI runs with defaults (last 7 days, default theme/context), producing files that validate.
- All new tests pass locally and in CI; existing tests unaffected.
- Docs updated per tri-file protocol; examples are accurate and ASCII-only.

