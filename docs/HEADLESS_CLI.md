# Headless EDCoPilot Generation CLI

This CLI generates EDCoPilot chatter files without opening Claude Desktop. It parses Elite Dangerous journals over a time window, derives context, and writes grammar-friendly, ASCII-only files with backups.

## Command

```
python scripts/generate_edcopilot.py [options]
```

## Defaults
- Time window: last 7 days (interpreted in local time, converted to UTC)
- Theme: "Grizzled Veteran Space Captain"
- Context: "Worn Hands, Endless Horizon"
- Output: EDCoPilot path from config (override with `--output-dir`)
- Backups: on by default (see Backup Behavior)

## Options

Time window (mutually exclusive):
- `--hours N`  Generate for the last N hours
- `--from YYYY-MM-DD[THH:MM]` and optional `--to YYYY-MM-DD[THH:MM]`

Content:
- `--theme "..."`  Informational header in generated files (default above)
- `--context "..."`  Informational header in generated files (default above)
- `--types space,crew,deep-space`  Restrict output to selected chatter types (default: all)

Paths:
- `--journal-path PATH`  Override auto-detected journal directory
- `--edcopilot-path PATH`  Override EDCoPilot destination
- `--output-dir PATH`  Alternate output directory (testing)

Behavior:
- `--dry-run`  Show planned actions; do not write files
- `--no-backup`  Do not create backups before overwriting
- `--overwrite`  Allow replacing existing files
- `--limit-entries N`  Limit parsed entries (debug)
- `--log-level info|debug|warning|error`
- `--fail-on-warn`  Reserved for future grammar warning escalation

## Examples

- Generate with defaults (last 7 days, default theme/context):
```
python scripts/generate_edcopilot.py
```

- Last 12 hours with custom theme/context:
```
python scripts/generate_edcopilot.py --hours 12 --theme "Corporate Fixer" --context "Cold Calculus, Clean Ledger"
```

- Date range to an alternate output directory (dry run):
```
python scripts/generate_edcopilot.py --from 2025-09-10 --to "2025-09-13 18:00" --output-dir C:\temp\edc --dry-run
```

- Generate only Crew Chatter, overwrite if exists:
```
python scripts/generate_edcopilot.py --hours 48 --types crew --overwrite
```

## Backup Behavior

When a target file exists and backups are enabled (default):
- The current file is copied to `filename.backup.YYYYMMDD_HHMMSS.txt` before writing
- If `--no-backup` is provided, no backup is created
- If `--overwrite` is not provided and a file exists, it is skipped

## Notes

- Outputs are ASCII-only and include header comments with theme and context
- All internal timestamps/logging use UTC
- The CLI operates in direct mode (no MCP transport)
- Journal files are filtered by filename timestamp against the selected window

