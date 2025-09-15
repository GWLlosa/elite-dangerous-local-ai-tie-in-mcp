"""
Integration Tests for Theme System

Tests end-to-end workflows and integration between theme system components.
"""

import pytest
import tempfile
import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from src.edcopilot.theme_storage import ThemeStorage, ShipCrewConfig, CrewMemberTheme
from src.edcopilot.theme_generator import ThemeGenerator, ThemePromptContext
from src.edcopilot.theme_mcp_tools import ThemeMCPTools
from src.utils.data_store import DataStore
from src.utils.config import EliteConfig


class TestThemeSystemIntegration:
    """Test integration between all theme system components."""

    @pytest.fixture
    async def integrated_system(self):
        """Create fully integrated theme system for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration
            config = EliteConfig(
                edcopilot_path=Path(temp_dir) / "edcopilot_files"
            )
            config.edcopilot_path.mkdir(parents=True, exist_ok=True)

            # Initialize components
            data_store = DataStore()
            storage = ThemeStorage(storage_path=Path(temp_dir) / "themes.json")
            generator = ThemeGenerator(storage)

            # Mock EDCoPilotGenerator for testing
            with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
                mock_generator = MagicMock()
                mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
                mock_generator_class.return_value = mock_generator

                mcp_tools = ThemeMCPTools(data_store)

                # Override storage in MCP tools for testing
                mcp_tools.theme_storage = storage
                mcp_tools.theme_generator = generator

            yield {
                'config': config,
                'data_store': data_store,
                'storage': storage,
                'generator': generator,
                'mcp_tools': mcp_tools
            }

    @pytest.mark.asyncio
    async def test_complete_theme_workflow(self, integrated_system):
        """Test complete theme workflow from setup to file generation."""
        mcp_tools = integrated_system['mcp_tools']
        config = integrated_system['config']

        # Step 1: Set up initial theme
        result = await mcp_tools.set_edcopilot_theme(
            theme="space_explorer",
            context="veteran pilot exploring the galaxy"
        )
        assert result["success"] is True

        # Step 2: Configure ship crew
        result = await mcp_tools.configure_ship_crew(
            ship_name="Deep Explorer",
            crew_roles=["commander", "navigator", "science", "engineer"]
        )
        assert result["success"] is True
        assert result["crew_count"] >= 4

        # Step 3: Set individual crew member themes
        result = await mcp_tools.set_crew_member_theme(
            ship_name="Deep Explorer",
            crew_role="navigator",
            theme="analytical_navigator",
            context="former military navigator with precision focus"
        )
        assert result["success"] is True

        # Step 4: Generate themed prompt for Claude Desktop
        result = await mcp_tools.generate_themed_templates_prompt()
        assert result["success"] is True
        assert "prompt" in result
        assert "space_explorer" in result["prompt"]

        # Step 5: Simulate applying generated templates
        test_templates = [
            "condition:Docked|Docking successful, Commander. All systems nominal for our exploration mission.",
            "condition:Supercruise|Maintaining supercruise. Shall I plot our next exploration target?",
            "condition:FuelLow|Fuel reserves running low. Recommend seeking nearest fuel star.",
            "condition:Scanned|Stellar cartographic data updated. Another system catalogued for science."
        ]

        with patch('src.edcopilot.theme_mcp_tools.load_config') as mock_config:
            mock_config.return_value = config

            result = await mcp_tools.apply_generated_templates(
                generated_templates=test_templates
            )

        assert result["success"] is True
        assert len(result["files_written"]) > 0

        # Step 6: Verify themes are preserved
        status = await mcp_tools.get_theme_status()
        assert status["current_theme"]["theme"] == "space_explorer"
        assert status["ship_count"] >= 1

    @pytest.mark.asyncio
    async def test_multi_ship_theme_coordination(self, integrated_system):
        """Test managing themes across multiple ships."""
        mcp_tools = integrated_system['mcp_tools']

        # Set up multiple ships with different themes
        ships = [
            ("Explorer Vessel", "scientific_expedition", "research mission to distant nebula"),
            ("Combat Patrol", "military_squadron", "frontier defense patrol"),
            ("Trading Hauler", "merchant_convoy", "profitable trade route operation"),
            ("Racing Viper", "speed_enthusiasts", "competitive racing team")
        ]

        for ship_name, theme, context in ships:
            # Configure ship
            await mcp_tools.configure_ship_crew(ship_name=ship_name)

            # Set ship-specific theme
            await mcp_tools.set_edcopilot_theme(theme, context)

            # Set crew member themes for this ship
            crew_themes = {
                "commander": (f"{theme}_leader", f"experienced {theme.replace('_', ' ')} commander"),
                "navigator": (f"{theme}_nav", f"navigation specialist for {theme.replace('_', ' ')} operations"),
                "engineer": (f"{theme}_tech", f"technical expert in {theme.replace('_', ' ')} systems")
            }

            for role, (role_theme, role_context) in crew_themes.items():
                await mcp_tools.set_crew_member_theme(
                    ship_name=ship_name,
                    crew_role=role,
                    theme=role_theme,
                    context=role_context
                )

        # Verify all ships are configured
        storage = integrated_system['storage']
        all_ships = storage.get_all_ship_configs()
        assert len(all_ships) == 4

        # Test theme coordination across ships
        for ship_name, expected_theme, _ in ships:
            ship_config = storage.get_ship_config(ship_name)
            assert ship_config is not None
            assert ship_config.ship_name == ship_name

    @pytest.mark.asyncio
    async def test_theme_persistence_across_sessions(self, integrated_system):
        """Test that themes persist across system restarts."""
        mcp_tools = integrated_system['mcp_tools']
        storage = integrated_system['storage']

        # Set up complex theme configuration
        await mcp_tools.set_edcopilot_theme("persistent_theme", "test persistence")
        await mcp_tools.configure_ship_crew("Persistence Test Ship", ["commander", "navigator"])

        # Add crew member themes
        await mcp_tools.set_crew_member_theme(
            ship_name="Persistence Test Ship",
            crew_role="commander",
            theme="persistent_commander",
            context="command persistence test"
        )

        # Force save
        storage._save_ship_configs()
        storage._save_current_theme()
        storage._save_theme_history()

        # Simulate system restart by creating new instances
        new_storage = ThemeStorage(storage_path=storage.storage_path)
        new_generator = ThemeGenerator(new_storage)
        new_mcp_tools = ThemeMCPTools(integrated_system['data_store'])
        new_mcp_tools.theme_storage = new_storage
        new_mcp_tools.theme_generator = new_generator

        # Verify themes persisted
        status = await new_mcp_tools.get_theme_status()
        assert status["current_theme"]["theme"] == "persistent_theme"

        ship_config = new_storage.get_ship_config("Persistence Test Ship")
        assert ship_config is not None

        commander_theme = new_storage.get_crew_member_theme("Persistence Test Ship", "commander")
        assert commander_theme.theme == "persistent_commander"

    @pytest.mark.asyncio
    async def test_error_recovery_and_rollback(self, integrated_system):
        """Test error recovery and rollback mechanisms."""
        mcp_tools = integrated_system['mcp_tools']

        # Set up initial valid state
        await mcp_tools.set_edcopilot_theme("stable_theme", "stable context")
        await mcp_tools.configure_ship_crew("Test Ship", ["commander"])

        # Create backup
        backup_result = await mcp_tools.backup_current_themes()
        assert backup_result["success"] is True

        # Simulate operation that might fail
        with patch.object(mcp_tools.theme_generator, 'validate_generated_templates') as mock_validate:
            mock_validate.side_effect = Exception("Simulated validation error")

            result = await mcp_tools.apply_generated_templates([
                "condition:Docked|Test template"
            ])

            # Should handle error gracefully
            assert result["success"] is False
            assert "error" in result

        # Verify original state is preserved
        status = await mcp_tools.get_theme_status()
        assert status["current_theme"]["theme"] == "stable_theme"

    @pytest.mark.asyncio
    async def test_real_time_theme_updates(self, integrated_system):
        """Test real-time theme updates and notifications."""
        mcp_tools = integrated_system['mcp_tools']
        data_store = integrated_system['data_store']

        # Set up initial state
        await mcp_tools.set_edcopilot_theme("initial_theme", "initial context")

        # Simulate game state changes that might affect themes
        game_state_updates = [
            {"ship_name": "New Ship Detected", "location": "Jameson Memorial"},
            {"activity": "exploration", "system": "Distant System"},
            {"status": "docked", "station": "Research Station"}
        ]

        for update in game_state_updates:
            # Update data store
            for key, value in update.items():
                data_store.update_field(key, value)

            # Verify theme system can adapt
            status = await mcp_tools.get_theme_status()
            assert status["success"] is True

    @pytest.mark.asyncio
    async def test_performance_under_load(self, integrated_system):
        """Test system performance under high load."""
        mcp_tools = integrated_system['mcp_tools']

        # Simulate high-frequency theme operations
        operations = []

        async def theme_operation_burst():
            """Perform burst of theme operations."""
            for i in range(20):
                await mcp_tools.set_edcopilot_theme(f"burst_theme_{i}", f"context_{i}")
                if i % 5 == 0:
                    await mcp_tools.configure_ship_crew(f"Ship_{i}", ["commander", "navigator"])
                await asyncio.sleep(0.001)  # Small delay

        # Run multiple bursts concurrently
        start_time = asyncio.get_event_loop().time()
        await asyncio.gather(*[theme_operation_burst() for _ in range(5)])
        end_time = asyncio.get_event_loop().time()

        elapsed = end_time - start_time
        assert elapsed < 5.0  # Should complete within reasonable time

        # Verify system is still responsive
        status = await mcp_tools.get_theme_status()
        assert status["success"] is True

    @pytest.mark.asyncio
    async def test_integration_with_elite_dangerous_events(self, integrated_system):
        """Test integration with Elite Dangerous game events."""
        mcp_tools = integrated_system['mcp_tools']
        data_store = integrated_system['data_store']

        # Set up theme that should adapt to game events
        await mcp_tools.set_edcopilot_theme("adaptive_explorer", "responds to exploration events")

        # Simulate Elite Dangerous events
        elite_events = [
            {
                "event": "FSDJump",
                "StarSystem": "Wolf 359",
                "StarClass": "M",
                "SystemFaction": {"Name": "Independent"}
            },
            {
                "event": "Scan",
                "ScanType": "Detailed",
                "BodyName": "Wolf 359 A",
                "PlanetClass": "Rocky body"
            },
            {
                "event": "Docked",
                "StationName": "Jameson Memorial",
                "StationType": "Orbis"
            }
        ]

        for event in elite_events:
            # Update data store with event data
            for key, value in event.items():
                data_store.update_field(key, value)

            # Generate preview to see how theme adapts
            preview = await mcp_tools.preview_themed_content()
            assert preview["success"] is True

            # Preview should contain some context from the events
            assert len(preview["example_templates"]) > 0

    @pytest.mark.asyncio
    async def test_theme_validation_pipeline(self, integrated_system):
        """Test the complete theme validation pipeline."""
        mcp_tools = integrated_system['mcp_tools']
        generator = integrated_system['generator']

        # Set up theme
        await mcp_tools.set_edcopilot_theme("validation_test", "comprehensive validation")

        # Test prompt generation
        prompt_result = await mcp_tools.generate_themed_templates_prompt()
        assert prompt_result["success"] is True

        # Test validation with various template qualities
        test_cases = [
            # Valid templates
            ["condition:Docked|Welcome to the station, Commander."],
            # Mixed valid and invalid
            [
                "condition:Docked|Valid docking message",
                "invalid format template",
                "condition:Supercruise|Valid supercruise message"
            ],
            # All invalid
            ["invalid1", "invalid2", "invalid3"],
            # Edge cases
            ["condition:Docked|", "condition:|Empty condition", "|No condition"]
        ]

        for templates in test_cases:
            result = generator.validate_generated_templates(templates)

            # Should handle all cases without crashing
            assert "success" in result
            assert "valid_templates" in result
            assert "failed_templates" in result
            assert "validation_summary" in result

    @pytest.mark.asyncio
    async def test_backup_and_restore_workflow(self, integrated_system):
        """Test complete backup and restore workflow."""
        mcp_tools = integrated_system['mcp_tools']
        config = integrated_system['config']

        # Set up complex theme state
        await mcp_tools.set_edcopilot_theme("backup_test", "testing backup system")
        await mcp_tools.configure_ship_crew("Backup Ship", ["commander", "navigator", "engineer"])

        for role in ["commander", "navigator", "engineer"]:
            await mcp_tools.set_crew_member_theme(
                ship_name="Backup Ship",
                crew_role=role,
                theme=f"backup_{role}",
                context=f"backup context for {role}"
            )

        # Create backup
        backup_result = await mcp_tools.backup_current_themes()
        assert backup_result["success"] is True
        assert backup_result["themes_backed_up"] > 0

        # Backup EDCoPilot files
        with patch('src.edcopilot.theme_mcp_tools.load_config') as mock_config:
            mock_config.return_value = config

            # Create some test files first
            test_files = ["space_chatter.txt", "crew_chatter.txt", "deepspace_chatter.txt"]
            for filename in test_files:
                test_file = config.edcopilot_path / filename
                test_file.write_text("test content")

            backup_files_result = await mcp_tools.backup_edcopilot_files()
            assert backup_files_result["success"] is True

        # Modify state
        await mcp_tools.reset_theme(clear_ship_configs=True)

        # Verify state is cleared
        status = await mcp_tools.get_theme_status()
        assert status["current_theme"] is None
        assert status["ship_count"] == 0

        # In a real scenario, you would restore from backup here
        # For this test, we verify the backup captured the right data
        assert backup_result["backup_path"] is not None
        assert backup_result["timestamp"] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])