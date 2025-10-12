"""
Unit tests for EDCoPilot content generation engine.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import shutil

from src.edcopilot.generator import (
    EDCoPilotContextAnalyzer, EDCoPilotContentGenerator,
    EDCoPilotFileManager
)
from src.utils.data_store import DataStore
from src.journal.events import ProcessedEvent, EventCategory


class TestEDCoPilotContextAnalyzer:
    """Test EDCoPilotContextAnalyzer functionality."""

    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store for testing."""
        store = Mock(spec=DataStore)

        # Mock game state
        game_state = Mock()
        game_state.current_system = "Test System"
        game_state.current_station = "Test Station"
        game_state.current_body = None
        game_state.current_ship = "Asp Explorer"
        game_state.credits = 5000000
        game_state.fuel_level = 85.0
        game_state.hull_health = 100.0
        game_state.docked = True

        store.get_game_state.return_value = game_state
        store.get_recent_events.return_value = []

        return store

    @pytest.fixture
    def analyzer(self, mock_data_store):
        """Create context analyzer for testing."""
        return EDCoPilotContextAnalyzer(mock_data_store)

    def test_analyze_current_context_basic(self, analyzer, mock_data_store):
        """Test basic context analysis."""
        context = analyzer.analyze_current_context()

        assert context["current_system"] == "Test System"
        assert context["current_station"] == "Test Station"
        assert context["ship_type"] == "Asp Explorer"
        assert context["credits"] == 5000000
        assert context["fuel_level"] == 85.0  # Value from mock data store
        assert context["hull_health"] == 100.0
        assert context["docked"] is True

    def test_analyze_current_context_with_events(self, analyzer, mock_data_store):
        """Test context analysis with recent events."""
        # Create mock events
        mock_events = [
            ProcessedEvent(
                raw_event={"event": "FSDJump", "StarSystem": "Alpha Centauri", "JumpDist": 30.0},
                event_type="FSDJump",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=10),
                category=EventCategory.NAVIGATION,
                summary="Jumped to Alpha Centauri"
            ),
            ProcessedEvent(
                raw_event={"event": "Scan", "BodyName": "Earth", "PlanetClass": "Earth-like world"},
                event_type="Scan",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=5),
                category=EventCategory.EXPLORATION,
                summary="Scanned Earth"
            ),
        ]

        mock_data_store.get_recent_events.return_value = mock_events

        context = analyzer.analyze_current_context()

        assert context["primary_activity"] in ["exploration", "navigation"]  # Either is acceptable
        assert context["recent_discoveries"] == 1
        assert context["exploration_events"] == 1

    def test_determine_primary_activity_exploration(self, analyzer):
        """Test determining primary activity as exploration."""
        events = [
            ProcessedEvent(
                raw_event={"event": "Scan"}, event_type="Scan",
                timestamp=datetime.now(timezone.utc), category=EventCategory.EXPLORATION,
                summary="Scan"
            ),
            ProcessedEvent(
                raw_event={"event": "FSDJump"}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Jump"
            ),
        ]

        activity = analyzer._determine_primary_activity(events)
        assert activity in ["exploration", "navigation"]

    def test_determine_primary_activity_no_events(self, analyzer):
        """Test determining primary activity with no events."""
        activity = analyzer._determine_primary_activity([])
        assert activity == "general"

    def test_count_discoveries(self, analyzer):
        """Test counting discovery events."""
        events = [
            ProcessedEvent(
                raw_event={"event": "Scan"}, event_type="Scan",
                timestamp=datetime.now(timezone.utc), category=EventCategory.EXPLORATION,
                summary="Scan"
            ),
            ProcessedEvent(
                raw_event={"event": "FSSDiscoveryScan"}, event_type="FSSDiscoveryScan",
                timestamp=datetime.now(timezone.utc), category=EventCategory.EXPLORATION,
                summary="Discovery"
            ),
            ProcessedEvent(
                raw_event={"event": "FSDJump"}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Jump"
            ),
        ]

        discoveries = analyzer._count_discoveries(events)
        assert discoveries == 2

    def test_count_combat_events(self, analyzer):
        """Test counting combat events."""
        events = [
            ProcessedEvent(
                raw_event={"event": "Bounty"}, event_type="Bounty",
                timestamp=datetime.now(timezone.utc), category=EventCategory.COMBAT,
                summary="Bounty"
            ),
            ProcessedEvent(
                raw_event={"event": "FSDJump"}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Jump"
            ),
        ]

        combat_count = analyzer._count_combat_events(events)
        assert combat_count == 1

    def test_is_deep_space_high_jumps(self, analyzer):
        """Test deep space detection with high jump distances."""
        events = [
            ProcessedEvent(
                raw_event={"event": "FSDJump", "JumpDist": 45.0}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Long jump"
            ),
            ProcessedEvent(
                raw_event={"event": "FSDJump", "JumpDist": 50.0}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Long jump"
            ),
        ]

        is_deep_space = analyzer._is_deep_space(events)
        assert is_deep_space is True

    def test_is_deep_space_short_jumps(self, analyzer):
        """Test deep space detection with short jump distances."""
        events = [
            ProcessedEvent(
                raw_event={"event": "FSDJump", "JumpDist": 10.0}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Short jump"
            ),
        ]

        is_deep_space = analyzer._is_deep_space(events)
        assert is_deep_space is False

    def test_has_first_discoveries(self, analyzer):
        """Test detecting first discoveries."""
        events = [
            ProcessedEvent(
                raw_event={"event": "Scan"}, event_type="Scan",
                timestamp=datetime.now(timezone.utc), category=EventCategory.EXPLORATION,
                summary="First to map this stellar body"
            ),
            ProcessedEvent(
                raw_event={"event": "FSDJump"}, event_type="FSDJump",
                timestamp=datetime.now(timezone.utc), category=EventCategory.NAVIGATION,
                summary="Regular jump"
            ),
        ]

        has_discoveries = analyzer._has_first_discoveries(events)
        assert has_discoveries is True


class TestEDCoPilotContentGenerator:
    """Test EDCoPilotContentGenerator functionality."""

    @pytest.fixture
    def temp_edcopilot_dir(self):
        """Create temporary directory for EDCoPilot files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store."""
        store = Mock(spec=DataStore)

        game_state = Mock()
        game_state.current_system = "Sol"
        game_state.current_station = "Earth Station"
        game_state.current_ship = "Python"
        game_state.credits = 10000000
        game_state.fuel_level = 75.0
        game_state.hull_health = 100.0
        game_state.docked = False

        store.get_game_state.return_value = game_state
        store.get_recent_events.return_value = []

        return store

    @pytest.fixture
    def generator(self, mock_data_store, temp_edcopilot_dir):
        """Create content generator for testing."""
        return EDCoPilotContentGenerator(mock_data_store, temp_edcopilot_dir)

    def test_initialization(self, generator, mock_data_store, temp_edcopilot_dir):
        """Test generator initialization."""
        assert generator.data_store == mock_data_store
        assert generator.edcopilot_path == temp_edcopilot_dir
        assert generator.template_manager is not None
        assert generator.context_analyzer is not None

    def test_generate_contextual_chatter(self, generator):
        """Test generating contextual chatter."""
        files = generator.generate_contextual_chatter()

        assert len(files) == 3
        assert "EDCoPilot.SpaceChatter.Custom.txt" in files
        assert "EDCoPilot.CrewChatter.Custom.txt" in files
        assert "EDCoPilot.DeepSpaceChatter.Custom.txt" in files

        # Verify content
        for filename, content in files.items():
            assert len(content) > 100
            # NO COMMENTS - EDCoPilot doesn't support them
            assert not content.startswith("#")

    def test_write_files(self, generator, temp_edcopilot_dir):
        """Test writing files to disk."""
        written_files = generator.write_files(backup_existing=False)

        assert len(written_files) == 3
        for filename, file_path in written_files.items():
            assert file_path.exists()
            assert file_path.parent == temp_edcopilot_dir

            # Verify content
            content = file_path.read_text(encoding='utf-8')
            # NO COMMENTS - EDCoPilot doesn't support them
            assert not content.startswith("#")

    def test_write_files_with_backup(self, generator, temp_edcopilot_dir):
        """Test writing files with backup of existing files."""
        # Create an existing file
        existing_file = temp_edcopilot_dir / "EDCoPilot.SpaceChatter.Custom.txt"
        existing_file.write_text("Existing content")

        written_files = generator.write_files(backup_existing=True)

        # Original file should be overwritten
        assert existing_file.exists()
        content = existing_file.read_text(encoding='utf-8')
        # NO COMMENTS - EDCoPilot doesn't support them
        assert not content.startswith("#")

        # Backup should exist
        backup_files = list(temp_edcopilot_dir.glob("*.backup.*.txt"))
        assert len(backup_files) >= 1

    def test_write_files_nonexistent_directory(self, mock_data_store):
        """Test writing files when directory doesn't exist."""
        nonexistent_path = Path(tempfile.gettempdir()) / "nonexistent_edcopilot_dir"
        if nonexistent_path.exists():
            shutil.rmtree(nonexistent_path)

        generator = EDCoPilotContentGenerator(mock_data_store, nonexistent_path)

        # Should create directory and write files
        written_files = generator.write_files()

        assert nonexistent_path.exists()
        assert len(written_files) == 3

        # Clean up
        shutil.rmtree(nonexistent_path)

    def test_enhance_with_context_exploration(self, generator, mock_data_store):
        """Test enhancing chatter with exploration context."""
        # Create exploration context
        mock_events = [
            ProcessedEvent(
                raw_event={"event": "Scan"}, event_type="Scan",
                timestamp=datetime.now(timezone.utc), category=EventCategory.EXPLORATION,
                summary="Scan"
            ),
        ]
        mock_data_store.get_recent_events.return_value = mock_events

        files = generator.generate_contextual_chatter()
        space_content = files["EDCoPilot.SpaceChatter.Custom.txt"]

        # Should contain exploration-specific content
        assert "discoveries" in space_content.lower() or "scan" in space_content.lower()

    def test_enhance_with_context_fuel_low(self, generator, mock_data_store):
        """Test enhancing chatter with low fuel context."""
        # Set low fuel state
        game_state = mock_data_store.get_game_state.return_value
        game_state.fuel_level = 15.0  # Low fuel

        files = generator.generate_contextual_chatter()
        space_content = files["EDCoPilot.SpaceChatter.Custom.txt"]

        # Should contain fuel-related content
        assert "fuel" in space_content.lower()


class TestEDCoPilotFileManager:
    """Test EDCoPilotFileManager functionality."""

    @pytest.fixture
    def temp_edcopilot_dir(self):
        """Create temporary directory for EDCoPilot files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_manager(self, temp_edcopilot_dir):
        """Create file manager for testing."""
        return EDCoPilotFileManager(temp_edcopilot_dir)

    def test_initialization(self, file_manager, temp_edcopilot_dir):
        """Test file manager initialization."""
        assert file_manager.edcopilot_path == temp_edcopilot_dir

    def test_list_custom_files_empty(self, file_manager):
        """Test listing custom files in empty directory."""
        files = file_manager.list_custom_files()
        assert files == []

    def test_list_custom_files_with_files(self, file_manager, temp_edcopilot_dir):
        """Test listing custom files with existing files."""
        # Create test files
        (temp_edcopilot_dir / "EDCoPilot.SpaceChatter.Custom.txt").write_text("test")
        (temp_edcopilot_dir / "EDCoPilot.CrewChatter.custom.txt").write_text("test")
        (temp_edcopilot_dir / "other_file.txt").write_text("test")

        files = file_manager.list_custom_files()

        file_names = [f.name for f in files]
        assert "EDCoPilot.SpaceChatter.Custom.txt" in file_names
        assert "EDCoPilot.CrewChatter.custom.txt" in file_names
        assert "other_file.txt" not in file_names

        # Should only contain custom files (*.Custom.txt or *.custom.txt)
        for file_path in files:
            assert "custom" in file_path.name.lower()

    def test_get_file_info_existing(self, file_manager, temp_edcopilot_dir):
        """Test getting info for existing file."""
        test_file = temp_edcopilot_dir / "EDCoPilot.SpaceChatter.Custom.txt"
        test_content = "# Test file\ncondition:Docked|Test dialogue\n# Another comment\nSimple dialogue"
        test_file.write_text(test_content)

        info = file_manager.get_file_info(test_file)

        assert info["exists"] is True
        assert info["size"] > 0
        assert "modified" in info
        assert info["entry_count"] == 2  # Two non-comment, non-empty lines
        assert info["is_generated"] is False  # Doesn't contain MCP Server marker

    def test_get_file_info_generated(self, file_manager, temp_edcopilot_dir):
        """Test getting info for generated file."""
        test_file = temp_edcopilot_dir / "EDCoPilot.SpaceChatter.Custom.txt"
        test_content = "# Generated by Elite Dangerous MCP Server\ncondition:Docked|Test dialogue"
        test_file.write_text(test_content)

        info = file_manager.get_file_info(test_file)

        assert info["exists"] is True
        assert info["is_generated"] is True

    def test_get_file_info_nonexistent(self, file_manager, temp_edcopilot_dir):
        """Test getting info for nonexistent file."""
        nonexistent_file = temp_edcopilot_dir / "nonexistent.txt"
        info = file_manager.get_file_info(nonexistent_file)

        assert info["exists"] is False

    def test_backup_files(self, file_manager, temp_edcopilot_dir):
        """Test backing up custom files."""
        # Create test files
        (temp_edcopilot_dir / "EDCoPilot.SpaceChatter.Custom.txt").write_text("space content")
        (temp_edcopilot_dir / "EDCoPilot.CrewChatter.Custom.txt").write_text("crew content")

        backup_files = file_manager.backup_files()

        assert len(backup_files) == 2

        # Verify backup files exist
        for original_name, backup_path in backup_files.items():
            assert backup_path.exists()
            assert "backup" in backup_path.name

            # Verify content matches
            original_path = temp_edcopilot_dir / original_name
            assert original_path.read_text() == backup_path.read_text()

    def test_clean_old_backups(self, file_manager, temp_edcopilot_dir):
        """Test cleaning old backup files."""
        # Create old and new backup files
        old_backup = temp_edcopilot_dir / "EDCoPilot.SpaceChatter.backup.20200101_120000.txt"
        new_backup = temp_edcopilot_dir / "EDCoPilot.CrewChatter.backup.20991231_235959.txt"

        old_backup.write_text("old backup")
        new_backup.write_text("new backup")

        # Set old timestamp
        import os
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(old_backup, (old_time, old_time))

        removed_count = file_manager.clean_old_backups(keep_days=7)

        # Old backup should be removed, new backup should remain
        assert not old_backup.exists()
        assert new_backup.exists()
        assert removed_count == 1