"""
Edge Case Tests for Theme System

Tests boundary conditions, invalid inputs, and error scenarios for the Dynamic Multi-Crew Theme System.
"""

import pytest
import tempfile
import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open, Mock, AsyncMock

from src.edcopilot.theme_storage import ThemeStorage, ShipCrewConfig, CrewMemberTheme, CrewRole
from src.edcopilot.theme_generator import ThemeGenerator, TemplateValidator, ThemePromptContext
from src.edcopilot.theme_mcp_tools import ThemeMCPTools
from src.utils.data_store import DataStore


class TestThemeStorageEdgeCases:
    """Test edge cases and boundary conditions for theme storage."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ThemeStorage(storage_path=Path(temp_dir) / "edge_test_themes.json")

    def test_empty_string_inputs(self, temp_storage):
        """Test handling of empty string inputs."""
        # Empty theme name
        temp_storage.set_current_theme("", "valid_context")
        theme = temp_storage.get_current_theme()
        assert theme is not None
        assert theme["theme"] == ""

        # Empty context
        temp_storage.set_current_theme("valid_theme", "")
        theme = temp_storage.get_current_theme()
        assert theme["context"] == ""

        # Both empty
        temp_storage.set_current_theme("", "")
        theme = temp_storage.get_current_theme()
        assert theme["theme"] == ""
        assert theme["context"] == ""

    def test_very_long_strings(self, temp_storage):
        """Test handling of extremely long strings."""
        long_theme = "x" * 10000  # 10KB string
        long_context = "y" * 10000

        temp_storage.set_current_theme(long_theme, long_context)
        theme = temp_storage.get_current_theme()

        assert theme["theme"] == long_theme
        assert theme["context"] == long_context

    def test_unicode_and_special_characters(self, temp_storage):
        """Test handling of unicode and special characters."""
        unicode_theme = "测试主题 🚀 émoji café naïve"
        special_chars = "!@#$%^&*()[]{}|\\:;\"'<>?,./"

        temp_storage.set_current_theme(unicode_theme, special_chars)
        theme = temp_storage.get_current_theme()

        assert theme["theme"] == unicode_theme
        assert theme["context"] == special_chars

    def test_null_and_none_handling(self, temp_storage):
        """Test handling of None values."""
        # None values should be handled gracefully
        with pytest.raises((TypeError, ValueError)):
            temp_storage.set_current_theme(None, "context")

        with pytest.raises((TypeError, ValueError)):
            temp_storage.set_current_theme("theme", None)

    def test_invalid_ship_names(self, temp_storage):
        """Test handling of invalid ship names."""
        invalid_names = ["", "   ", "\n\t", "ship/with/slashes", "ship\\with\\backslashes"]

        for invalid_name in invalid_names:
            # Should not crash, but may normalize the name
            config = ShipCrewConfig(
                ship_name=invalid_name,
                crew_roles=["commander"],
                crew_themes={}
            )
            temp_storage.set_ship_config(config)

            # Should be able to retrieve it
            retrieved = temp_storage.get_ship_config(invalid_name)
            assert retrieved is not None

    def test_corrupted_storage_file_handling(self):
        """Test handling of corrupted storage files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "corrupted.json"

            # Create corrupted JSON file
            with open(storage_path, 'w') as f:
                f.write('{"invalid": json content}')

            # Should handle corruption gracefully and start fresh
            storage = ThemeStorage(storage_path=storage_path)
            storage.set_current_theme("test", "test")

            # Should work normally after corruption
            theme = storage.get_current_theme()
            assert theme is not None

    def test_permission_denied_handling(self):
        """Test handling of permission denied errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "readonly.json"

            # Create storage and save initial data
            storage = ThemeStorage(storage_path=storage_path)
            storage.set_current_theme("test", "test")

            # Make file read-only (simulate permission denied)
            storage_path.chmod(0o444)

            try:
                # Should handle permission errors gracefully
                storage.set_current_theme("new_theme", "new_context")
                # Operation might fail, but shouldn't crash
            except PermissionError:
                # This is acceptable behavior
                pass
            finally:
                # Restore permissions for cleanup
                storage_path.chmod(0o644)

    def test_maximum_crew_roles(self, temp_storage):
        """Test handling of maximum number of crew roles."""
        # Create ship with many crew roles
        many_roles = [f"role_{i}" for i in range(100)]

        config = ShipCrewConfig(
            ship_name="test_ship",
            crew_roles=many_roles,
            crew_themes={}
        )
        temp_storage.set_ship_config(config)

        retrieved = temp_storage.get_ship_config("test_ship")
        assert len(retrieved.crew_roles) == 100

    def test_boundary_history_limits(self, temp_storage):
        """Test boundary conditions for history limits."""
        # Add many history entries
        for i in range(1000):
            temp_storage.set_current_theme(f"theme_{i}", f"context_{i}")

        # Test various limit values
        assert len(temp_storage.get_theme_history(limit=0)) == 0
        assert len(temp_storage.get_theme_history(limit=1)) == 1
        assert len(temp_storage.get_theme_history(limit=1000)) == 1000
        assert len(temp_storage.get_theme_history(limit=9999)) == 1000  # Can't exceed actual count


class TestThemeGeneratorEdgeCases:
    """Test edge cases for theme generation."""

    @pytest.fixture
    def edge_generator(self):
        """Create generator for edge case testing."""
        storage = ThemeStorage()
        return ThemeGenerator(storage)

    def test_empty_template_list(self, edge_generator):
        """Test validation with empty template list."""
        result = edge_generator.validate_generated_templates([])
        assert result["success"] is False
        assert "No valid templates found" in result["error"]

    def test_template_with_malformed_syntax(self, edge_generator):
        """Test handling of severely malformed templates."""
        malformed_templates = [
            "|||||||||||",
            "condition:",
            "|no condition",
            "condition::|empty dialogue",
            "condition:Valid|",  # Empty dialogue
            "condition\nwith\nnewlines|dialogue",
            "condition with spaces but no colon|dialogue"
        ]

        result = edge_generator.validate_generated_templates(malformed_templates)
        # Should handle gracefully without crashing
        assert "valid_templates" in result
        assert "failed_templates" in result

    def test_extremely_long_templates(self, edge_generator):
        """Test handling of extremely long templates."""
        long_condition = "Docked" * 1000
        long_dialogue = "This is a very long dialogue. " * 1000

        long_template = f"condition:{long_condition}|{long_dialogue}"

        result = edge_generator.validate_generated_templates([long_template])
        # Should handle without memory issues
        assert "valid_templates" in result

    def test_prompt_generation_with_extreme_inputs(self, edge_generator):
        """Test prompt generation with extreme input values."""
        extreme_context = ThemePromptContext(
            theme="x" * 5000,  # Very long theme
            context="y" * 5000,  # Very long context
            crew_role="z" * 100,  # Long role name
            ship_name="w" * 200   # Long ship name
        )

        # Should not crash
        result = edge_generator.prompt_generator.generate_theme_prompt(extreme_context)
        assert "prompt" in result

    def test_chatter_entry_creation_with_invalid_types(self, edge_generator):
        """Test chatter entry creation with invalid chatter types."""
        from src.edcopilot.templates import ChatterType

        valid_templates = ["condition:Docked|Test dialogue"]

        # Should handle invalid enum values gracefully
        entries = edge_generator.create_chatter_entries_from_templates(
            valid_templates,
            chatter_type=None  # Invalid type
        )
        # Should fall back to default
        assert len(entries) > 0

    def test_concurrent_validation_operations(self, edge_generator):
        """Test concurrent template validation operations."""
        import threading
        import time

        results = []
        errors = []

        def validate_worker():
            try:
                templates = [f"condition:Docked|Thread test {i}" for i in range(100)]
                result = edge_generator.validate_generated_templates(templates)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Run multiple validation operations concurrently
        threads = [threading.Thread(target=validate_worker) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should complete without errors
        assert len(errors) == 0
        assert len(results) == 5

        for result in results:
            assert result["success"] is True


class TestThemeMCPToolsEdgeCases:
    """Test edge cases for MCP tools."""

    @pytest.fixture
    def edge_mcp_tools(self):
        """Create MCP tools for edge case testing."""
        data_store = DataStore()

        with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
            mock_generator_class.return_value = mock_generator

            return ThemeMCPTools(data_store)

    @pytest.mark.asyncio
    async def test_invalid_theme_parameters(self, edge_mcp_tools):
        """Test MCP tools with invalid parameters."""
        # Empty strings
        result = await edge_mcp_tools.set_edcopilot_theme("", "")
        assert result["success"] is True  # Should handle gracefully

        # Very long strings
        long_theme = "x" * 10000
        long_context = "y" * 10000
        result = await edge_mcp_tools.set_edcopilot_theme(long_theme, long_context)
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_ship_configuration(self, edge_mcp_tools):
        """Test ship configuration with invalid parameters."""
        # Empty ship name
        result = await edge_mcp_tools.configure_ship_crew(
            ship_name="",
            crew_roles=["commander"]
        )
        # Should handle gracefully
        assert "success" in result

        # Empty crew roles
        result = await edge_mcp_tools.configure_ship_crew(
            ship_name="test_ship",
            crew_roles=[]
        )
        # Should fall back to defaults
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_template_application_with_file_errors(self, edge_mcp_tools):
        """Test template application when file operations fail."""
        await edge_mcp_tools.set_edcopilot_theme("test", "test")

        valid_templates = ["condition:Docked|Test template"]

        # Mock file operations to fail
        with patch('src.edcopilot.theme_mcp_tools.load_config') as mock_config:
            mock_config.side_effect = Exception("File system error")

            result = await edge_mcp_tools.apply_generated_templates(
                generated_templates=valid_templates
            )

            # Should handle file errors gracefully
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_concurrent_mcp_operations(self, edge_mcp_tools):
        """Test concurrent MCP operations don't interfere."""
        async def theme_operation(operation_id):
            await edge_mcp_tools.set_edcopilot_theme(f"theme_{operation_id}", f"context_{operation_id}")
            return await edge_mcp_tools.get_theme_status()

        # Run many operations concurrently
        tasks = [theme_operation(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should complete without exceptions
        for result in results:
            assert not isinstance(result, Exception)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_reset_operations_edge_cases(self, edge_mcp_tools):
        """Test reset operations in edge cases."""
        # Reset when no themes are set
        result = await edge_mcp_tools.reset_theme()
        assert result["success"] is True

        # Reset with clear_ship_configs when no ships exist
        result = await edge_mcp_tools.reset_theme(clear_ship_configs=True)
        assert result["success"] is True

        # Set up some data and reset
        await edge_mcp_tools.set_edcopilot_theme("test", "test")
        await edge_mcp_tools.configure_ship_crew("test_ship", ["commander"])

        result = await edge_mcp_tools.reset_theme(clear_ship_configs=True)
        assert result["success"] is True

        # Verify everything is cleared
        status = await edge_mcp_tools.get_theme_status()
        assert status["current_theme"] is None

    @pytest.mark.asyncio
    async def test_preview_with_no_current_theme(self, edge_mcp_tools):
        """Test preview generation when no theme is set."""
        result = await edge_mcp_tools.preview_themed_content()

        # Should handle gracefully
        assert result["success"] is True
        assert "example_templates" in result

    @pytest.mark.asyncio
    async def test_backup_operations_edge_cases(self, edge_mcp_tools):
        """Test backup operations in edge cases."""
        # Backup when no themes exist
        result = await edge_mcp_tools.backup_current_themes()
        assert result["success"] is True
        assert result["themes_backed_up"] == 0

        # Backup EDCoPilot files when directory doesn't exist
        with patch('src.edcopilot.theme_mcp_tools.load_config') as mock_config:
            mock_config.return_value.edcopilot_path = Path("/nonexistent/path")

            result = await edge_mcp_tools.backup_edcopilot_files()
            # Should handle missing directory gracefully
            assert "success" in result


class TestThemeSystemResourceLimits:
    """Test behavior under resource constraints."""

    def test_memory_pressure_handling(self):
        """Test behavior under memory pressure."""
        # Create many storage instances to simulate memory pressure
        storages = []

        try:
            for i in range(100):
                with tempfile.TemporaryDirectory() as temp_dir:
                    storage = ThemeStorage(storage_path=Path(temp_dir) / f"storage_{i}.json")

                    # Add significant data to each
                    for j in range(50):
                        config = ShipCrewConfig(
                            ship_name=f"Ship_{i}_{j}",
                            crew_roles=["commander", "navigator", "engineer"] * 10,  # Lots of roles
                            crew_themes={}
                        )
                        storage.set_ship_config(config)

                    storages.append(storage)
        except MemoryError:
            # This is acceptable - we're testing limits
            pass

        # Should have created at least some storages
        assert len(storages) > 10

    def test_file_descriptor_limits(self):
        """Test behavior when approaching file descriptor limits."""
        # Simulate many concurrent file operations
        import threading
        import time

        def file_worker(worker_id):
            with tempfile.TemporaryDirectory() as temp_dir:
                storage = ThemeStorage(storage_path=Path(temp_dir) / f"worker_{worker_id}.json")

                for i in range(10):
                    storage.set_current_theme(f"theme_{i}", f"context_{i}")
                    time.sleep(0.001)  # Small delay

        # Run many workers concurrently
        threads = [threading.Thread(target=file_worker, args=(i,)) for i in range(50)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should complete without file descriptor exhaustion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
