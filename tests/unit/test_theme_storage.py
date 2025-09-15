"""
Unit tests for Theme Storage System

Tests the theme storage and persistence functionality for the
Dynamic Multi-Crew Theme System.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from src.edcopilot.theme_storage import (
    ThemeStorage, CrewMemberTheme, ShipCrewConfig, CrewRole
)


class TestCrewMemberTheme:
    """Test CrewMemberTheme data class."""

    def test_crew_member_theme_creation(self):
        """Test basic crew member theme creation."""
        theme = CrewMemberTheme(
            role="navigator",
            theme="by-the-book officer",
            context="30-year veteran"
        )

        assert theme.role == "navigator"
        assert theme.theme == "by-the-book officer"
        assert theme.context == "30-year veteran"
        assert theme.voice_preference is None
        assert theme.personality_traits is None

    def test_crew_member_theme_with_optional_fields(self):
        """Test crew member theme with all optional fields."""
        theme = CrewMemberTheme(
            role="engineer",
            theme="gruff mechanic",
            context="40 years experience",
            voice_preference="CEREPROC_SCOTTISH",
            personality_traits=["gruff", "experienced", "reliable"]
        )

        assert theme.voice_preference == "CEREPROC_SCOTTISH"
        assert theme.personality_traits == ["gruff", "experienced", "reliable"]

    def test_crew_member_theme_serialization(self):
        """Test crew member theme to/from dict conversion."""
        theme = CrewMemberTheme(
            role="science",
            theme="excited researcher",
            context="first deep space mission",
            personality_traits=["curious", "enthusiastic"]
        )

        # Test to_dict
        theme_dict = theme.to_dict()
        assert theme_dict["role"] == "science"
        assert theme_dict["theme"] == "excited researcher"
        assert theme_dict["personality_traits"] == ["curious", "enthusiastic"]

        # Test from_dict
        restored_theme = CrewMemberTheme.from_dict(theme_dict)
        assert restored_theme.role == theme.role
        assert restored_theme.theme == theme.theme
        assert restored_theme.personality_traits == theme.personality_traits


class TestShipCrewConfig:
    """Test ShipCrewConfig data class."""

    def test_ship_crew_config_creation(self):
        """Test basic ship crew config creation."""
        config = ShipCrewConfig(
            ship_name="Anaconda",
            crew_roles=["commander", "navigator", "engineer"],
            crew_themes={}
        )

        assert config.ship_name == "Anaconda"
        assert config.crew_roles == ["commander", "navigator", "engineer"]
        assert config.crew_themes == {}
        assert config.last_updated is not None

    def test_ship_crew_config_with_themes(self):
        """Test ship crew config with crew themes."""
        nav_theme = CrewMemberTheme("navigator", "military officer", "veteran")
        eng_theme = CrewMemberTheme("engineer", "gruff mechanic", "experienced")

        config = ShipCrewConfig(
            ship_name="Asp Explorer",
            crew_roles=["commander", "navigator", "engineer"],
            crew_themes={
                "navigator": nav_theme,
                "engineer": eng_theme
            },
            overall_theme="exploration team",
            overall_context="deep space exploration mission"
        )

        assert len(config.crew_themes) == 2
        assert config.crew_themes["navigator"].theme == "military officer"
        assert config.overall_theme == "exploration team"

    def test_ship_crew_config_serialization(self):
        """Test ship crew config serialization."""
        nav_theme = CrewMemberTheme("navigator", "officer", "veteran")
        config = ShipCrewConfig(
            ship_name="Python",
            crew_roles=["commander", "navigator"],
            crew_themes={"navigator": nav_theme}
        )

        # Test to_dict
        config_dict = config.to_dict()
        assert config_dict["ship_name"] == "Python"
        assert "last_updated" in config_dict
        assert "crew_themes" in config_dict
        assert config_dict["crew_themes"]["navigator"]["role"] == "navigator"

        # Test from_dict
        restored_config = ShipCrewConfig.from_dict(config_dict)
        assert restored_config.ship_name == config.ship_name
        assert restored_config.crew_roles == config.crew_roles
        assert restored_config.crew_themes["navigator"].theme == nav_theme.theme


class TestThemeStorage:
    """Test ThemeStorage system."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ThemeStorage(Path(temp_dir))

    def test_theme_storage_initialization(self, temp_storage):
        """Test theme storage initialization."""
        storage = temp_storage
        assert storage.storage_path.exists()
        assert storage._current_theme is None
        assert storage._ship_configs == {}

    def test_set_current_theme(self, temp_storage):
        """Test setting current theme."""
        storage = temp_storage
        storage.set_current_theme("space pirate", "owes debt to Space Mafia")

        theme = storage.get_current_theme()
        assert theme is not None
        assert theme["theme"] == "space pirate"
        assert theme["context"] == "owes debt to Space Mafia"
        assert "set_time" in theme
        assert "theme_id" in theme

    def test_clear_current_theme(self, temp_storage):
        """Test clearing current theme."""
        storage = temp_storage
        storage.set_current_theme("corporate", "ambitious executive")

        theme = storage.get_current_theme()
        assert theme is not None

        storage.clear_current_theme()
        theme = storage.get_current_theme()
        assert theme is None

    def test_theme_persistence(self, temp_storage):
        """Test theme persistence across storage instances."""
        storage1 = temp_storage
        storage1.set_current_theme("military veteran", "retired officer")

        # Create new storage instance with same path
        storage2 = ThemeStorage(storage1.storage_path)
        theme = storage2.get_current_theme()

        assert theme is not None
        assert theme["theme"] == "military veteran"
        assert theme["context"] == "retired officer"

    def test_ship_config_management(self, temp_storage):
        """Test ship configuration management."""
        storage = temp_storage

        # Create ship config
        config = ShipCrewConfig(
            ship_name="Anaconda",
            crew_roles=["commander", "navigator", "engineer"],
            crew_themes={}
        )

        # Set ship config
        storage.set_ship_config(config)

        # Get ship config
        retrieved_config = storage.get_ship_config("Anaconda")
        assert retrieved_config is not None
        assert retrieved_config.ship_name == "Anaconda"
        assert retrieved_config.crew_roles == ["commander", "navigator", "engineer"]

        # Get all configs
        all_configs = storage.get_all_ship_configs()
        assert "Anaconda" in all_configs

        # Remove ship config
        removed = storage.remove_ship_config("Anaconda")
        assert removed is True

        # Verify removal
        retrieved_config = storage.get_ship_config("Anaconda")
        assert retrieved_config is None

    def test_crew_member_theme_management(self, temp_storage):
        """Test crew member theme management."""
        storage = temp_storage

        # Set crew member theme
        storage.set_crew_member_theme(
            ship_name="Asp Explorer",
            crew_role="navigator",
            theme="precise officer",
            context="military background",
            voice_preference="MICROSOFT_MALE",
            personality_traits=["precise", "professional"]
        )

        # Get crew member theme
        crew_theme = storage.get_crew_member_theme("Asp Explorer", "navigator")
        assert crew_theme is not None
        assert crew_theme.theme == "precise officer"
        assert crew_theme.context == "military background"
        assert crew_theme.voice_preference == "MICROSOFT_MALE"
        assert crew_theme.personality_traits == ["precise", "professional"]

        # Verify ship config was created
        ship_config = storage.get_ship_config("Asp Explorer")
        assert ship_config is not None
        assert "navigator" in ship_config.crew_roles
        assert "navigator" in ship_config.crew_themes

    def test_default_crew_for_ship(self):
        """Test default crew configuration for different ship types."""
        # Small ship
        sidewinder_crew = ThemeStorage.get_default_crew_for_ship("Sidewinder")
        assert len(sidewinder_crew) == 1
        assert CrewRole.COMMANDER.value in sidewinder_crew

        # Medium ship
        asp_crew = ThemeStorage.get_default_crew_for_ship("Asp Explorer")
        assert len(asp_crew) == 4
        assert CrewRole.COMMANDER.value in asp_crew
        assert CrewRole.NAVIGATOR.value in asp_crew
        assert CrewRole.SCIENCE_OFFICER.value in asp_crew

        # Large ship
        anaconda_crew = ThemeStorage.get_default_crew_for_ship("Anaconda")
        assert len(anaconda_crew) >= 5
        assert CrewRole.COMMANDER.value in anaconda_crew
        assert CrewRole.NAVIGATOR.value in anaconda_crew
        assert CrewRole.SECURITY_CHIEF.value in anaconda_crew

        # Unknown ship (should default to medium)
        unknown_crew = ThemeStorage.get_default_crew_for_ship("Unknown Ship")
        assert len(unknown_crew) == 3
        assert CrewRole.COMMANDER.value in unknown_crew

    def test_theme_history(self, temp_storage):
        """Test theme history tracking."""
        storage = temp_storage

        # Set theme to trigger history entry
        storage.set_current_theme("pirate", "treasure hunter")

        # Get history
        history = storage.get_theme_history()
        assert len(history) > 0

        # Should have theme_set entry
        theme_entries = [entry for entry in history if entry["action"] == "theme_set"]
        assert len(theme_entries) == 1
        assert theme_entries[0]["data"]["theme"] == "pirate"

        # Clear theme to trigger another history entry
        storage.clear_current_theme()

        history = storage.get_theme_history()
        clear_entries = [entry for entry in history if entry["action"] == "theme_cleared"]
        assert len(clear_entries) == 1

    def test_preset_management(self, temp_storage):
        """Test theme preset management."""
        storage = temp_storage

        # Create ship config
        ship_config = ShipCrewConfig(
            ship_name="Python",
            crew_roles=["commander", "engineer"],
            crew_themes={}
        )
        storage.set_ship_config(ship_config)

        # Save preset
        storage.save_preset(
            name="pirate_crew",
            theme="space pirate",
            context="rebel crew",
            ship_configs={"Python": ship_config}
        )

        # Load preset
        preset = storage.load_preset("pirate_crew")
        assert preset is not None
        assert preset["theme"] == "space pirate"
        assert preset["context"] == "rebel crew"
        assert "ship_configs" in preset

        # Get all presets
        all_presets = storage.get_all_presets()
        assert "pirate_crew" in all_presets

        # Remove preset
        removed = storage.remove_preset("pirate_crew")
        assert removed is True

        # Verify removal
        preset = storage.load_preset("pirate_crew")
        assert preset is None

    def test_create_default_ship_config(self, temp_storage):
        """Test creating default ship configuration."""
        storage = temp_storage

        # Create default config for Anaconda
        config = storage.create_default_ship_config("Anaconda")
        assert config.ship_name == "Anaconda"
        assert len(config.crew_roles) >= 5
        assert CrewRole.COMMANDER.value in config.crew_roles
        assert config.crew_themes == {}

        # Create default config for Sidewinder
        config = storage.create_default_ship_config("Sidewinder")
        assert config.ship_name == "Sidewinder"
        assert len(config.crew_roles) == 1
        assert config.crew_roles[0] == CrewRole.COMMANDER.value

    def test_storage_info(self, temp_storage):
        """Test storage information retrieval."""
        storage = temp_storage

        # Add some data
        storage.set_current_theme("test", "test context")
        storage.set_crew_member_theme("TestShip", "navigator", "officer", "veteran")

        # Get storage info
        info = storage.get_storage_info()
        assert "storage_path" in info
        assert info["current_theme"] is True
        assert info["ship_configs_count"] == 1
        assert info["history_entries"] > 0

    def test_clear_all_data(self, temp_storage):
        """Test clearing all theme data."""
        storage = temp_storage

        # Add data
        storage.set_current_theme("test", "test")
        storage.set_crew_member_theme("TestShip", "navigator", "officer", "veteran")
        storage.save_preset("test_preset", "test", "test")

        # Verify data exists
        assert storage.get_current_theme() is not None
        assert len(storage.get_all_ship_configs()) > 0
        assert len(storage.get_all_presets()) > 0

        # Clear all data
        storage.clear_all_data()

        # Verify data is cleared
        assert storage.get_current_theme() is None
        assert len(storage.get_all_ship_configs()) == 0
        assert len(storage.get_all_presets()) == 0