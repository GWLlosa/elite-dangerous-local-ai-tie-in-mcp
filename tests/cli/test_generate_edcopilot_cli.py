"""
Tests for the Headless EDCoPilot Generation CLI (Milestone 16).

Covers argument parsing, window resolution, dry-run behavior,
and a small smoke test writing to a temp directory.
"""

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scripts.generate_edcopilot import (
    parse_args, resolve_window, main as cli_main, generate_and_write,
)


pytestmark = [pytest.mark.cli]


def test_parse_args_defaults():
    args = parse_args([])
    assert args.hours is None
    assert args.theme == "Grizzled Veteran Space Captain"
    assert args.context == "Worn Hands, Endless Horizon"
    assert args.types is None
    assert args.edcopilot_themes_path is None


def test_parse_args_themes_path():
    args = parse_args(["--edcopilot-themes-path", "C:/themes"])
    assert args.edcopilot_themes_path == "C:/themes"


def test_resolve_window_hours():
    args = parse_args(["--hours", "12"])
    start_utc, end_utc = resolve_window(args)
    assert end_utc.tzinfo == timezone.utc
    assert start_utc.tzinfo == timezone.utc
    delta = (end_utc - start_utc).total_seconds()
    assert 11.5 * 3600 <= delta <= 12.5 * 3600


def test_resolve_window_from_to_local_to_utc():
    # Use only date to avoid timezone edge cases
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    args = parse_args(["--from", today, "--to", today])
    start_utc, end_utc = resolve_window(args)
    assert start_utc.tzinfo == timezone.utc
    assert end_utc.tzinfo == timezone.utc
    assert start_utc <= end_utc


def test_dry_run_writes_nothing(tmp_path: Path):
    journal_dir = tmp_path / "journals"
    output_dir = tmp_path / "out"
    journal_dir.mkdir()
    output_dir.mkdir()

    # Create a minimal journal file within the last 48 hours
    now = datetime.now(timezone.utc)
    fname = now.strftime("Journal.%Y%m%d%H%M%S.01.log")
    jf = journal_dir / fname
    with open(jf, "w", encoding="utf-8") as f:
        f.write('{"timestamp":"2024-09-06T12:00:00Z","event":"Fileheader"}\n')
        f.write('{"timestamp":"2024-09-06T12:01:00Z","event":"LoadGame","Commander":"Test"}\n')

    rc = cli_main([
        "--hours", "48",
        "--journal-path", str(journal_dir),
        "--output-dir", str(output_dir),
        "--dry-run",
    ])
    assert rc == 0
    # Nothing should be written in dry-run
    assert list(output_dir.glob("*") ) == []


def test_write_outputs_and_types_filter(tmp_path: Path):
    journal_dir = tmp_path / "journals"
    output_dir = tmp_path / "out"
    journal_dir.mkdir()
    output_dir.mkdir()

    # Create a minimal journal file
    now = datetime.now(timezone.utc)
    fname = now.strftime("Journal.%Y%m%d%H%M%S.01.log")
    jf = journal_dir / fname
    with open(jf, "w", encoding="utf-8") as f:
        f.write('{"timestamp":"2024-09-06T12:00:00Z","event":"Fileheader"}\n')
        f.write('{"timestamp":"2024-09-06T12:01:00Z","event":"LoadGame","Commander":"Test"}\n')

    # Write all types
    rc_all = cli_main([
        "--hours", "48",
        "--journal-path", str(journal_dir),
        "--output-dir", str(output_dir),
        "--overwrite",
    ])
    assert rc_all == 0
    all_files = list(output_dir.glob("*.txt"))
    assert len(all_files) >= 1

    # Now restrict to crew only in a new dir
    output_dir2 = tmp_path / "out2"
    output_dir2.mkdir()
    rc_crew = cli_main([
        "--hours", "48",
        "--journal-path", str(journal_dir),
        "--output-dir", str(output_dir2),
        "--types", "crew",
        "--overwrite",
    ])
    assert rc_crew == 0
    crew_files = list(output_dir2.glob("*.txt"))
    assert len(crew_files) >= 1
    # Ensure only CrewChatter present
    assert all("CrewChatter" in p.name for p in crew_files)


def test_cli_themes_path_flag_seeds_directory(tmp_path: Path):
    journal_dir = tmp_path / "journals"
    output_dir = tmp_path / "out"
    themes_dir = tmp_path / "themes"
    # Empty journal directory: seeding happens before journal ingest, so this
    # keeps the test independent of journal parsing.
    journal_dir.mkdir()
    output_dir.mkdir()

    rc = cli_main([
        "--hours", "48",
        "--journal-path", str(journal_dir),
        "--output-dir", str(output_dir),
        "--edcopilot-themes-path", str(themes_dir),
        "--dry-run",
    ])
    assert rc == 0
    # Themes directory was created and seeded from the bundled themes
    assert (themes_dir / "current_theme.json").exists()


def test_cli_themes_path_from_env_var(tmp_path: Path):
    journal_dir = tmp_path / "journals"
    output_dir = tmp_path / "out"
    themes_dir = tmp_path / "env_themes"
    journal_dir.mkdir()
    output_dir.mkdir()

    with patch.dict(os.environ, {"ELITE_EDCOPILOT_THEMES_PATH": str(themes_dir)}):
        rc = cli_main([
            "--hours", "48",
            "--journal-path", str(journal_dir),
            "--output-dir", str(output_dir),
            "--dry-run",
        ])
    assert rc == 0
    assert (themes_dir / "current_theme.json").exists()


def test_cli_flag_overrides_env_themes_path(tmp_path: Path):
    journal_dir = tmp_path / "journals"
    output_dir = tmp_path / "out"
    env_themes = tmp_path / "env_themes"
    cli_themes = tmp_path / "cli_themes"
    journal_dir.mkdir()
    output_dir.mkdir()

    with patch.dict(os.environ, {"ELITE_EDCOPILOT_THEMES_PATH": str(env_themes)}):
        rc = cli_main([
            "--hours", "48",
            "--journal-path", str(journal_dir),
            "--output-dir", str(output_dir),
            "--edcopilot-themes-path", str(cli_themes),
            "--dry-run",
        ])
    assert rc == 0
    assert (cli_themes / "current_theme.json").exists()
    assert not env_themes.exists()


def test_generate_and_write_accepts_theme_storage(tmp_path: Path):
    data_store = Mock()
    theme_storage = Mock()

    with patch("scripts.generate_edcopilot.EDCoPilotContentGenerator") as mock_gen:
        mock_gen.return_value.generate_contextual_chatter.return_value = {}
        generate_and_write(
            data_store,
            tmp_path,
            backup=True,
            overwrite=True,
            dry_run=True,
            selected_types=None,
            theme="t",
            context="c",
            theme_storage=theme_storage,
        )

    mock_gen.assert_called_once_with(data_store, tmp_path, theme_storage=theme_storage)

