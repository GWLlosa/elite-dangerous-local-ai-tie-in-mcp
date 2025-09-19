"""
Unit tests for Theme MCP Tools

Tests the MCP tools for the Dynamic Multi-Crew Theme System,
including theme management, crew configuration, and AI integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile

from src.edcopilot.theme_mcp_tools import ThemeMCPTools
from src.edcopilot.theme_storage import ThemeStorage, ShipCrewConfig, CrewMemberTheme
from src.utils.data_store import DataStore, GameState


class TestThemeMCPTools:
    """Test Theme MCP Tools functionality."""

    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store."""
        data_store = Mock(spec=DataStore)
        game_state = Mock(spec=GameState)
        game_state.current_ship = "Anaconda"
        game_state.current_system = "Sol"
        game_state.commander_name = "Test Commander"
        data_store.get_game_state.return_value = game_state
        return data_store

    @pytest.fixture
    def temp_storage_path(self):
        """Create temporary storage path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def theme_tools(self, mock_data_store, temp_storage_path):
        """Create ThemeMCPTools with temporary storage."""
        with patch('src.edcopilot.theme_mcp_tools.ThemeStorage') as mock_storage_class:
            # Create real storage instance in temp directory
            real_storage = ThemeStorage(temp_storage_path)
            mock_storage_class.return_value = real_storage

            with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
                mock_generator = Mock()
                mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
                mock_generator_class.return_value = mock_generator

                tools = ThemeMCPTools(mock_data_store)
                tools.theme_storage = real_storage  # Use real storage for tests
                return tools

    # ==================== Core Theme Management Tests ====================

    @pytest.mark.asyncio
    async def test_set_edcopilot_theme(self, theme_tools):
        """Test setting EDCoPilot theme."""
        result = await theme_tools.set_edcopilot_theme(
            theme="space pirate",
            context="owes debt to Space Mafia"
        )

        assert result["success"] is True
        assert result["theme"] == "space pirate"
        assert result["context"] == "owes debt to Space Mafia"
        assert "next_steps" in result

        # Verify theme was stored
        stored_theme = theme_tools.theme_storage.get_current_theme()
        assert stored_theme is not None
        assert stored_theme["theme"] == "space pirate"

    @pytest.mark.asyncio
    async def test_set_edcopilot_theme_validation(self, theme_tools):
        """Test theme setting validation."""
        # Empty strings are treated as defaults (allowed)
        result = await theme_tools.set_edcopilot_theme("", "context")
        assert result["success"] is True

        result = await theme_tools.set_edcopilot_theme("theme", "")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_set_edcopilot_theme_with_immediate_application(self, theme_tools):
        """Test theme setting with immediate application."""
        result = await theme_tools.set_edcopilot_theme(
            theme="corporate executive",
            context="ambitious trader",
            apply_immediately=True
        )

        assert result["success"] is True
        assert "immediate_application" in result
        assert result["immediate_application"]["success"] is True

    @pytest.mark.asyncio
    async def test_get_theme_status(self, theme_tools):
        """Test getting theme status."""
        # Set a theme first
        await theme_tools.set_edcopilot_theme("test theme", "test context")

        result = await theme_tools.get_theme_status()

        assert "current_theme" in result
        assert "ship_configurations" in result
        assert "storage_info" in result
        assert "system_status" in result
        assert result["system_status"] == "operational"

    @pytest.mark.asyncio
    async def test_reset_theme(self, theme_tools):
        """Test resetting theme."""
        # Set theme and ship config
        await theme_tools.set_edcopilot_theme("test", "test")
        await theme_tools.configure_ship_crew("Anaconda", ["commander", "navigator"])

        # Reset theme only
        result = await theme_tools.reset_theme(clear_ship_configs=False)
        assert result["success"] is True

        # Theme should be cleared, ship configs should remain
        theme = theme_tools.theme_storage.get_current_theme()
        assert theme is None
        ship_configs = theme_tools.theme_storage.get_all_ship_configs()
        assert len(ship_configs) > 0

        # Reset with ship configs
        await theme_tools.set_edcopilot_theme("test2", "test2")
        result = await theme_tools.reset_theme(clear_ship_configs=True)
        assert result["success"] is True
        assert "ship_configs_cleared" in result

        ship_configs = theme_tools.theme_storage.get_all_ship_configs()
        assert len(ship_configs) == 0

    # ==================== AI Prompt Generation Tests ====================

    @pytest.mark.asyncio
    async def test_generate_themed_templates_prompt(self, theme_tools):
        """Test generating AI prompt for themed templates."""
        # Set current theme
        await theme_tools.set_edcopilot_theme("space pirate", "treasure hunter")

        result = await theme_tools.generate_themed_templates_prompt()

        assert result["success"] is True
        assert "prompt" in result
        assert "theme" in result
        assert "context" in result
        assert result["theme"] == "space pirate"

        prompt = result["prompt"]
        assert "space pirate" in prompt
        assert "treasure hunter" in prompt
        assert "EDCoPilot" in prompt
        assert "{SystemName}" in prompt

    @pytest.mark.asyncio
    async def test_generate_themed_templates_prompt_with_overrides(self, theme_tools):
        """Test prompt generation with parameter overrides."""
        result = await theme_tools.generate_themed_templates_prompt(
            theme="military veteran",
            context="retired officer",
            crew_role="navigator",
            ship_name="Python",
            chatter_type="crew"
        )

        assert result["success"] is True
        assert result["theme"] == "military veteran"
        assert result["context"] == "retired officer"
        assert result["crew_role"] == "navigator"
        assert result["ship_name"] == "Python"

    @pytest.mark.asyncio
    async def test_generate_themed_templates_prompt_no_theme(self, theme_tools):
        """Test prompt generation without theme set."""
        result = await theme_tools.generate_themed_templates_prompt()

        assert result["success"] is False
        assert "No theme specified" in result["error"]

    @pytest.mark.asyncio
    async def test_apply_generated_templates(self, theme_tools):
        """Test applying templates generated by Claude Desktop."""
        # Set up theme
        await theme_tools.set_edcopilot_theme("pirate", "test")

        # Mock load_config to return test path
        with patch('src.edcopilot.theme_mcp_tools.load_config') as mock_config:
            mock_config.return_value.edcopilot_path = Path(tempfile.mkdtemp())

            # Valid templates
            templates = [
                "condition:InSupercruise|Entering {SystemName}. Raise the Jolly Roger, matey!",
                "condition:Docked|Anchored at {StationName}. Time to see what treasure this port holds!",
                "condition:FuelLow|Fuel reserves at {FuelPercent}%. Need to find fuel, ye scurvy dog!"
            ]

            result = await theme_tools.apply_generated_templates(
                generated_templates=templates,
                chatter_type="space"
            )

            assert result["success"] is True
            assert result["templates_applied"] == 3
            assert result["chatter_type"] == "space"
            assert "files_written" in result
            assert "validation_summary" in result

    @pytest.mark.asyncio
    async def test_apply_generated_templates_validation_failure(self, theme_tools):
        """Test applying invalid templates."""
        invalid_templates = [
            "invalid template format",
            "condition:BadCondition|Invalid condition",
            "missing|condition prefix"
        ]

        result = await theme_tools.apply_generated_templates(
            generated_templates=invalid_templates
        )

        assert result["success"] is False
        assert "no valid templates" in result["error"].lower()
        assert "validation_details" in result

    # ==================== Ship and Crew Management Tests ====================

    @pytest.mark.asyncio
    async def test_configure_ship_crew(self, theme_tools):
        """Test configuring ship crew."""
        result = await theme_tools.configure_ship_crew(
            ship_name="Anaconda",
            crew_roles=["commander", "navigator", "science", "engineer"]
        )

        assert result["success"] is True
        assert result["ship_name"] == "Anaconda"
        assert result["crew_count"] == 6  # Anaconda default has 6 crew members
        assert "commander" in result["crew_roles"]

        # Verify ship config was stored
        ship_config = theme_tools.theme_storage.get_ship_config("Anaconda")
        assert ship_config is not None
        assert ship_config.ship_name == "Anaconda"
        assert len(ship_config.crew_roles) == 6  # Anaconda default configuration

    @pytest.mark.asyncio
    async def test_configure_ship_crew_auto(self, theme_tools):
        """Test auto-configuring ship crew based on ship type."""
        result = await theme_tools.configure_ship_crew(
            ship_name="Sidewinder",
            auto_configure=True
        )

        assert result["success"] is True
        assert result["ship_name"] == "Sidewinder"
        # Sidewinder should have only commander
        assert result["crew_count"] == 1
        assert result["crew_roles"] == ["commander"]

    @pytest.mark.asyncio
    async def test_configure_ship_crew_validation(self, theme_tools):
        """Test ship crew configuration validation."""
        result = await theme_tools.configure_ship_crew("")
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_set_crew_member_theme(self, theme_tools):
        """Test setting individual crew member theme."""
        result = await theme_tools.set_crew_member_theme(
            ship_name="Python",
            crew_role="navigator",
            theme="by-the-book officer",
            context="30-year navy veteran",
            voice_preference="MICROSOFT_MALE",
            personality_traits=["precise", "professional"]
        )

        assert result["success"] is True
        assert result["ship_name"] == "Python"
        assert result["crew_role"] == "navigator"
        assert result["theme"] == "by-the-book officer"

        # Verify crew theme was stored
        crew_theme = theme_tools.theme_storage.get_crew_member_theme("Python", "navigator")
        assert crew_theme is not None
        assert crew_theme.theme == "by-the-book officer"
        assert crew_theme.voice_preference == "MICROSOFT_MALE"
        assert crew_theme.personality_traits == ["precise", "professional"]

    @pytest.mark.asyncio
    async def test_set_crew_member_theme_validation(self, theme_tools):
        """Test crew member theme validation."""
        result = await theme_tools.set_crew_member_theme("", "navigator", "theme", "context")
        assert result["success"] is False
        assert "required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_generate_crew_setup_prompt(self, theme_tools):
        """Test generating crew setup prompt."""
        result = await theme_tools.generate_crew_setup_prompt(
            ship_name="Anaconda",
            overall_theme="space pirates",
            overall_context="rebel crew",
            crew_roles=["commander", "navigator", "engineer"]
        )

        assert result["success"] is True
        assert "prompt" in result
        assert result["ship_name"] == "Anaconda"
        assert result["overall_theme"] == "space pirates"

        prompt = result["prompt"]
        assert "Anaconda" in prompt
        assert "space pirates" in prompt
        assert "commander" in prompt
        assert "json" in prompt.lower()

    @pytest.mark.asyncio
    async def test_generate_crew_setup_prompt_auto_roles(self, theme_tools):
        """Test crew setup prompt with auto-detected roles."""
        result = await theme_tools.generate_crew_setup_prompt(
            ship_name="Asp Explorer",
            overall_theme="exploration team",
            overall_context="deep space mission"
        )

        assert result["success"] is True
        # Asp Explorer should auto-configure with 4 crew members
        assert len(result["crew_roles"]) == 4
        assert "science" in result["crew_roles"]  # Asp Explorer should include science officer

    # ==================== Preview and Validation Tests ====================

    @pytest.mark.asyncio
    async def test_preview_themed_content(self, theme_tools):
        """Test previewing themed content."""
        await theme_tools.set_edcopilot_theme("space pirate", "treasure hunter")

        result = await theme_tools.preview_themed_content()

        assert result["success"] is True
        assert result["theme"] == "space pirate"
        assert result["context"] == "treasure hunter"
        assert "example_templates" in result

        examples = result["example_templates"]
        assert len(examples) > 0
        # Should contain pirate-themed examples
        assert any("matey" in example.lower() or "arrr" in example.lower() for example in examples)

    @pytest.mark.asyncio
    async def test_preview_themed_content_with_crew_role(self, theme_tools):
        """Test preview with specific crew role."""
        await theme_tools.set_edcopilot_theme("military", "tactical unit")

        result = await theme_tools.preview_themed_content(crew_role="navigator")

        assert result["success"] is True
        assert result["crew_role"] == "navigator"

        examples = result["example_templates"]
        # Should have example templates (role-specific customization may vary)
        assert len(examples) > 0
        assert all(isinstance(example, str) for example in examples)

    @pytest.mark.asyncio
    async def test_preview_themed_content_no_theme(self, theme_tools):
        """Test preview without theme set."""
        result = await theme_tools.preview_themed_content()

        assert result["success"] is False
        assert "No theme specified" in result["error"]

    # ==================== Utility and Management Tests ====================

    @pytest.mark.asyncio
    async def test_backup_current_themes(self, theme_tools):
        """Test backing up current theme configuration."""
        # Set up theme and ship config
        await theme_tools.set_edcopilot_theme("test theme", "test context")
        await theme_tools.configure_ship_crew("TestShip", ["commander", "navigator"])

        result = await theme_tools.backup_current_themes()

        assert result["success"] is True
        assert "backup_name" in result
        assert "current_theme" in result
        assert result["ship_configs_count"] == 1

        # Verify backup was created as preset
        backup_name = result["backup_name"]
        preset = theme_tools.theme_storage.load_preset(backup_name)
        assert preset is not None

    @pytest.mark.asyncio
    async def test_backup_current_themes_empty(self, theme_tools):
        """Test backing up when no themes are set."""
        result = await theme_tools.backup_current_themes()

        assert result["success"] is True
        assert result.get("themes_backed_up", 0) == 0

    @pytest.mark.asyncio
    async def test_backup_edcopilot_files(self, theme_tools):
        """Test backing up EDCoPilot files."""
        result = await theme_tools.backup_edcopilot_files()

        assert result["success"] is True
        # Should delegate to edcopilot_generator.backup_files()

    # ==================== Error Handling Tests ====================

    @pytest.mark.asyncio
    async def test_error_handling(self, theme_tools):
        """Test error handling in MCP tools."""
        # Test with storage exception
        with patch.object(theme_tools.theme_storage, 'set_current_theme', side_effect=Exception("Storage error")):
            result = await theme_tools.set_edcopilot_theme("test", "test")
            assert result["success"] is False
            assert "Storage error" in result["error"]

    @pytest.mark.asyncio
    async def test_theme_examples_generation(self, theme_tools):
        """Test generation of theme-specific examples."""
        # Test different theme types
        themes_to_test = [
            ("space pirate", ["matey", "arrr", "treasure"]),
            ("corporate executive", ["profit", "market", "efficiency"]),
            ("military veteran", ["tactical", "mission", "operational"]),
            ("generic theme", ["theme"])
        ]

        for theme, expected_keywords in themes_to_test:
            examples = theme_tools._generate_theme_examples(theme, "test context")
            assert len(examples) > 0

            # Check that at least one example contains expected keywords
            examples_text = " ".join(examples).lower()
            if theme != "generic theme":
                assert any(keyword in examples_text for keyword in expected_keywords), \
                    f"Theme '{theme}' should contain keywords {expected_keywords}"

    @pytest.mark.asyncio
    async def test_integration_with_current_ship(self, theme_tools, mock_data_store):
        """Test integration with current ship from game state."""
        # Set current ship in game state
        mock_data_store.get_game_state.return_value.current_ship = "Federal Corvette"

        # Generate prompt without specifying ship
        await theme_tools.set_edcopilot_theme("military", "federal navy")
        result = await theme_tools.generate_themed_templates_prompt()

        assert result["success"] is True
        # Should use current ship from game state
        assert result["ship_name"] == "Federal Corvette"
