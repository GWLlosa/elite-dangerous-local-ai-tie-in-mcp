#!/usr/bin/env python3
"""
Headless EDCoPilot Generation CLI (Milestone 16)

Generates EDCoPilot chatter files without opening Claude Desktop.
Parses Elite Dangerous journals for a time window, derives context,
and writes grammar-friendly, ASCII-only chatter files with backups.

Defaults:
- Time window: last 7 days (local time interpreted, converted to UTC)
- Theme: "Grizzled Veteran Space Captain" (informational)
- Context: "Worn Hands, Endless Horizon" (informational)

Usage examples:
- python scripts/generate_edcopilot.py
- python scripts/generate_edcopilot.py --hours 12 --theme "Corporate Fixer" --context "Cold Calculus, Clean Ledger"
- python scripts/generate_edcopilot.py --from "2025-09-10" --to "2025-09-13 18:00" --output-dir C:\\temp\\edc --dry-run
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Tuple, List, Optional

try:
    from src.utils.config import EliteConfig
    from src.utils.data_store import DataStore
    from src.journal.parser import JournalParser
    from src.journal.events import EventProcessor
    from src.edcopilot.generator import EDCoPilotContentGenerator
except ImportError:
    from ..src.utils.config import EliteConfig
    from ..src.utils.data_store import DataStore
    from ..src.journal.parser import JournalParser
    from ..src.journal.events import EventProcessor
    from ..src.edcopilot.generator import EDCoPilotContentGenerator


LOG = logging.getLogger("generate_edcopilot")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Headless EDCoPilot chatter generation (Direct mode)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Time window (mutually exclusive)
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--hours", type=int, help="Generate for the last N hours")
    g.add_argument("--from", dest="from_dt", type=str, help="Start datetime (local) YYYY-MM-DD[THH:MM]")
    parser.add_argument("--to", dest="to_dt", type=str, help="End datetime (local) YYYY-MM-DD[THH:MM]")

    # Content
    parser.add_argument("--theme", type=str, default="Grizzled Veteran Space Captain", help="Theme description (informational)")
    parser.add_argument("--context", type=str, default="Worn Hands, Endless Horizon", help="Context description (informational)")
    parser.add_argument(
        "--types",
        type=str,
        help="Comma-separated chatter types to generate: space,crew,deep-space (default: all)",
    )

    # Paths
    parser.add_argument("--journal-path", type=str, help="Override journal directory path")
    parser.add_argument("--edcopilot-path", type=str, help="Override EDCoPilot custom files path")
    parser.add_argument("--output-dir", type=str, help="Alternate output directory (testing)")

    # Behavior
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions; do not write files")
    parser.add_argument("--no-backup", action="store_true", help="Do not create backups before overwriting")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing files")
    parser.add_argument("--limit-entries", type=int, help="Limit number of parsed entries (debug)")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")
    parser.add_argument("--fail-on-warn", action="store_true", help="Treat validation warnings as errors")

    return parser.parse_args(argv)


def _parse_local_dt(s: str) -> datetime:
    # Accept YYYY-MM-DD or YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM
    s = s.strip().replace("T", " ")
    fmt = "%Y-%m-%d %H:%M" if (" " in s) else "%Y-%m-%d"
    dt = datetime.strptime(s, fmt)
    # Interpret as local time and convert to UTC
    return dt.astimezone().astimezone(timezone.utc)


def resolve_window(args: argparse.Namespace) -> Tuple[datetime, datetime]:
    now_utc = datetime.now(timezone.utc)
    if args.hours is not None:
        start_utc = now_utc - timedelta(hours=args.hours)
        return start_utc, now_utc
    if args.from_dt or args.to_dt:
        start_utc = _parse_local_dt(args.from_dt) if args.from_dt else (now_utc - timedelta(days=7))
        end_utc = _parse_local_dt(args.to_dt) if args.to_dt else now_utc
        if end_utc < start_utc:
            raise ValueError("End time must be after start time")
        return start_utc, end_utc
    # Default: last 7 days
    return now_utc - timedelta(days=7), now_utc


def ascii_only(s: str) -> str:
    try:
        return s.encode("ascii", "ignore").decode("ascii")
    except Exception:
        return ""


def _file_types_from_arg(types_arg: Optional[str]) -> Optional[List[str]]:
    if not types_arg:
        return None
    items = [t.strip().lower() for t in types_arg.split(",") if t.strip()]
    valid = {"space", "crew", "deep-space"}
    selected = [t for t in items if t in valid]
    return selected or None


def _allowed_filename(name: str, selected_types: Optional[List[str]]) -> bool:
    if not selected_types:
        return True
    mapping = {
        "space": "SpaceChatter",
        "crew": "CrewChatter",
        "deep-space": "DeepSpaceChatter",
    }
    for t in selected_types:
        if mapping[t] in name:
            return True
    return False


def ingest_journals(journal_path: Path, start_utc: datetime, end_utc: datetime, data_store: DataStore, limit_entries: Optional[int] = None) -> int:
    parser = JournalParser(journal_path)
    processor = EventProcessor()
    files = parser.find_journal_files(include_backups=True)

    # Compare by filename timestamp; convert UTC to naive for comparison
    start_naive = start_utc.replace(tzinfo=None)
    end_naive = end_utc.replace(tzinfo=None)

    count = 0
    for f in files:
        ts = parser._extract_timestamp_from_filename(f)
        if ts < start_naive or ts > end_naive:
            continue
        entries, _ = parser.read_journal_file(f)
        for e in entries:
            pe = processor.process_event(e)
            data_store.store_event(pe)
            count += 1
            if limit_entries and count >= limit_entries:
                return count
    return count


def generate_and_write(data_store: DataStore, output_dir: Path, backup: bool, overwrite: bool, dry_run: bool, selected_types: Optional[List[str]], theme: str, context: str) -> Dict[str, Path]:
    gen = EDCoPilotContentGenerator(data_store, output_dir)
    files = gen.generate_contextual_chatter()

    # Filter by types if provided
    files = {name: content for name, content in files.items() if _allowed_filename(name, selected_types)}

    written: Dict[str, Path] = {}
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    for name, content in files.items():
        # Add header lines with theme/context (comments in EDCoPilot files)
        header = [
            "# Generated by Elite Dangerous MCP Server (Headless CLI)",
            f"# Theme: {ascii_only(theme)}",
            f"# Context: {ascii_only(context)}",
            f"# Generated UTC: {timestamp}",
            "",
        ]
        ascii_content = ascii_only(content)
        final_content = "\n".join(header) + ascii_content

        target = output_dir / name
        if dry_run:
            LOG.info(f"[DRY-RUN] Would write {target}")
            continue

        # Ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Backup existing if requested (always copy, never move)
        if backup and target.exists():
            backup_name = f"{target.stem}.backup.{timestamp}{target.suffix}"
            backup_path = target.parent / backup_name
            import shutil
            try:
                shutil.copy2(target, backup_path)
                LOG.info(f"Backed up existing file to: {backup_path}")
            except Exception as e:
                LOG.warning(f"Backup failed for {target}: {e}")

        if target.exists() and not overwrite:
            LOG.warning(f"File exists and --overwrite not set. Skipping: {target}")
            continue

        # Write file
        with open(target, "w", encoding="utf-8") as f:
            f.write(final_content)
        written[name] = target
        LOG.info(f"Wrote {target}")

    return written


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")

    try:
        start_utc, end_utc = resolve_window(args)
    except Exception as e:
        LOG.error(f"Invalid time window: {e}")
        return 3

    # Load config
    config = EliteConfig()
    journal_path = Path(args.journal_path).expanduser() if args.journal_path else config.journal_path
    edcopilot_path = Path(args.edcopilot_path).expanduser() if args.edcopilot_path else config.edcopilot_path
    output_dir = Path(args.output_dir).expanduser() if args.output_dir else edcopilot_path

    LOG.info(f"Journal path: {journal_path}")
    LOG.info(f"Output dir: {output_dir}")
    LOG.info(f"Window (UTC): {start_utc.isoformat()} -> {end_utc.isoformat()}")
    LOG.info(f"Theme: {args.theme}")
    LOG.info(f"Context: {args.context}")

    # Ingest journals
    store = DataStore()
    try:
        total = ingest_journals(journal_path, start_utc, end_utc, store, args.limit_entries)
        LOG.info(f"Ingested {total} events in window")
    except Exception as e:
        LOG.error(f"Error ingesting journals: {e}")
        return 2

    # Generate and write
    types_selected = _file_types_from_arg(args.types)
    try:
        written = generate_and_write(
            store,
            output_dir,
            backup=(not args.no_backup),
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            selected_types=types_selected,
            theme=args.theme,
            context=args.context,
        )
    except Exception as e:
        LOG.error(f"Generation error: {e}")
        return 1

    if args.dry_run:
        LOG.info("Dry run complete. No files written.")
    else:
        LOG.info(f"Files written: {len(written)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
