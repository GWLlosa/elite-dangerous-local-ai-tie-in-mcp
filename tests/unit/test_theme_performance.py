"""
Performance Tests for Theme System

Tests performance characteristics and scalability of the Dynamic Multi-Crew Theme System.
"""

import pytest
import time
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock, AsyncMock

from src.edcopilot.theme_storage import ThemeStorage, ShipCrewConfig, CrewMemberTheme
from src.edcopilot.theme_generator import ThemeGenerator, TemplateValidator
from src.edcopilot.theme_mcp_tools import ThemeMCPTools
from src.utils.data_store import DataStore


class TestThemeStoragePerformance:
    """Test performance characteristics of theme storage operations."""

    @pytest.fixture
    def large_scale_storage(self):
        """Create storage with large dataset for performance testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = ThemeStorage(storage_path=Path(temp_dir) / "performance_themes.json")

            # Pre-populate with large dataset
            for i in range(100):
                ship_config = ShipCrewConfig(
                    ship_name=f"TestShip_{i}",
                    crew_roles=["commander", "navigator", "engineer", "science", "security", "comms"],
                    crew_themes={},  # Start with empty crew themes
                    overall_theme=f"test_theme_{i}",
                    overall_context=f"test_context_{i}"
                )
                storage.set_ship_config(ship_config)

                # Add crew member themes
                for role in ship_config.crew_roles:
                    storage.set_crew_member_theme(
                        ship_name=f"TestShip_{i}",
                        crew_role=role,
                        theme=f"role_theme_{role}_{i}",
                        context=f"role_context_{role}_{i}"
                    )

            yield storage

    def test_large_scale_ship_retrieval_performance(self, large_scale_storage):
        """Test performance of retrieving ship configs at scale."""
        start_time = time.time()

        # Retrieve all ship configs
        all_configs = large_scale_storage.get_all_ship_configs()

        end_time = time.time()
        elapsed = end_time - start_time

        assert len(all_configs) == 100
        assert elapsed < 0.1  # Should complete in under 100ms

    def test_large_scale_crew_member_operations(self, large_scale_storage):
        """Test performance of crew member operations at scale."""
        start_time = time.time()

        # Perform multiple crew member retrievals
        for i in range(50):
            ship_name = f"TestShip_{i}"
            for role in ["commander", "navigator", "engineer"]:
                theme = large_scale_storage.get_crew_member_theme(ship_name, role)
                assert theme is not None

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 0.2  # Should complete in under 200ms for 150 operations

    def test_theme_history_performance_with_large_dataset(self, large_scale_storage):
        """Test theme history retrieval performance."""
        # Add many theme history entries
        for i in range(500):
            large_scale_storage.set_current_theme(f"theme_{i}", f"context_{i}")

        start_time = time.time()
        history = large_scale_storage.get_theme_history(limit=100)
        end_time = time.time()
        elapsed = end_time - start_time

        assert len(history) == 100
        assert elapsed < 0.05  # Should be very fast

    def test_storage_persistence_performance(self, large_scale_storage):
        """Test performance of saving large datasets."""
        start_time = time.time()

        # Force save operation
        large_scale_storage._save_ship_configs()

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 0.5  # Should save large dataset in under 500ms


class TestThemeGeneratorPerformance:
    """Test performance characteristics of theme generation operations."""

    @pytest.fixture
    def performance_generator(self):
        """Create generator for performance testing."""
        storage = ThemeStorage()
        return ThemeGenerator(storage)

    def test_template_validation_performance(self, performance_generator):
        """Test validation performance with many templates."""
        # Create 1000 templates for validation
        templates = []
        for i in range(1000):
            if i % 3 == 0:
                templates.append(f"condition:Docked|Valid template {i}")
            elif i % 3 == 1:
                templates.append(f"condition:Supercruise|Another valid template {i}")
            else:
                templates.append(f"invalid_template_{i}")  # Some invalid ones

        start_time = time.time()
        result = performance_generator.validate_generated_templates(templates)
        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 2.0  # Should validate 1000 templates in under 2 seconds
        assert result["success"] is True  # Should succeed despite some invalid templates
        assert len(result["valid_templates"]) > 600  # Most should be valid

    def test_prompt_generation_performance(self, performance_generator):
        """Test prompt generation performance."""
        from src.edcopilot.theme_generator import ThemePromptContext

        start_time = time.time()

        # Generate many prompts
        for i in range(100):
            context = ThemePromptContext(
                theme=f"test_theme_{i}",
                context=f"test_context_{i}",
                crew_role="navigator",
                ship_name="Anaconda"
            )
            result = performance_generator.prompt_generator.generate_theme_prompt(context)
            assert "prompt" in result

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 1.0  # Should generate 100 prompts in under 1 second

    def test_chatter_entry_creation_performance(self, performance_generator):
        """Test performance of creating chatter entries from templates."""
        # Create many valid templates
        templates = [f"condition:Docked|Performance test template {i}" for i in range(500)]

        start_time = time.time()
        entries = performance_generator.create_chatter_entries_from_templates(templates)
        end_time = time.time()
        elapsed = end_time - start_time

        assert len(entries) == 500
        assert elapsed < 0.5  # Should create 500 entries in under 500ms


class TestThemeMCPToolsPerformance:
    """Test performance characteristics of MCP tools operations."""

    @pytest.fixture
    def performance_mcp_tools(self):
        """Create MCP tools for performance testing."""
        data_store = DataStore()

        with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
            mock_generator_class.return_value = mock_generator

            return ThemeMCPTools(data_store)

    @pytest.mark.asyncio
    async def test_multiple_theme_operations_performance(self, performance_mcp_tools):
        """Test performance of multiple theme operations."""
        start_time = time.time()

        # Perform many theme operations
        for i in range(50):
            await performance_mcp_tools.set_edcopilot_theme(f"theme_{i}", f"context_{i}")
            status = await performance_mcp_tools.get_theme_status()
            assert status["success"] is True

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 2.0  # Should complete 100 operations in under 2 seconds

    @pytest.mark.asyncio
    async def test_ship_configuration_batch_performance(self, performance_mcp_tools):
        """Test performance of configuring multiple ships."""
        ship_types = ["Anaconda", "Corvette", "Cutter", "Python", "Asp Explorer"] * 10

        start_time = time.time()

        for i, ship_type in enumerate(ship_types):
            await performance_mcp_tools.configure_ship_crew(
                ship_name=f"{ship_type}_{i}",
                crew_roles=["commander", "navigator", "engineer"]
            )

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 3.0  # Should configure 50 ships in under 3 seconds

    @pytest.mark.asyncio
    async def test_preview_generation_performance(self, performance_mcp_tools):
        """Test performance of preview generation."""
        await performance_mcp_tools.set_edcopilot_theme("performance_test", "testing context")

        start_time = time.time()

        # Generate many previews
        for i in range(20):
            result = await performance_mcp_tools.preview_themed_content()
            assert result["success"] is True

        end_time = time.time()
        elapsed = end_time - start_time

        assert elapsed < 1.0  # Should generate 20 previews in under 1 second


class TestThemeSystemMemoryUsage:
    """Test memory usage characteristics of the theme system."""

    def test_storage_memory_efficiency(self):
        """Test memory usage of theme storage with large datasets."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        with tempfile.TemporaryDirectory() as temp_dir:
            storage = ThemeStorage(storage_path=Path(temp_dir) / "memory_test.json")

            # Create large dataset
            for i in range(1000):
                ship_config = ShipCrewConfig(
                    ship_name=f"MemoryTestShip_{i}",
                    crew_roles=["commander", "navigator", "engineer", "science", "security", "comms"],
                    crew_themes={},  # Empty crew themes
                    overall_theme=f"memory_test_theme_{i}" * 10,  # Longer strings
                    overall_context=f"memory_test_context_{i}" * 10
                )
                storage.set_ship_config(ship_config)

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB for 1000 ships)
        assert memory_increase < 50 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_mcp_tools_memory_stability(self):
        """Test that MCP tools don't leak memory during extended use."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        data_store = DataStore()

        with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
            mock_generator_class.return_value = mock_generator

            tools = ThemeMCPTools(data_store)

        initial_memory = process.memory_info().rss

        # Perform many operations
        for i in range(200):
            await tools.set_edcopilot_theme(f"memory_test_{i}", f"context_{i}")
            await tools.get_theme_status()
            if i % 10 == 0:
                await tools.reset_theme()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory should not increase significantly (less than 20MB)
        assert memory_increase < 20 * 1024 * 1024


class TestThemeSystemConcurrency:
    """Test concurrent access and thread safety of theme system."""

    @pytest.mark.asyncio
    async def test_concurrent_theme_operations(self):
        """Test concurrent theme operations don't interfere."""
        data_store = DataStore()

        with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
            mock_generator_class.return_value = mock_generator

            tools = ThemeMCPTools(data_store)

        async def theme_worker(worker_id: int):
            """Worker function for concurrent testing."""
            for i in range(10):
                await tools.set_edcopilot_theme(f"worker_{worker_id}_theme_{i}", f"context_{i}")
                status = await tools.get_theme_status()
                assert status["success"] is True
                await asyncio.sleep(0.001)  # Small delay to allow interleaving

        # Run multiple workers concurrently
        tasks = [theme_worker(i) for i in range(5)]
        await asyncio.gather(*tasks)

        # Verify final state is consistent
        status = await tools.get_theme_status()
        assert status["success"] is True

    @pytest.mark.asyncio
    async def test_concurrent_ship_configuration(self):
        """Test concurrent ship configuration operations."""
        data_store = DataStore()

        with patch('src.edcopilot.theme_mcp_tools.EDCoPilotGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator.backup_files = AsyncMock(return_value={"success": True, "backups": []})
            mock_generator_class.return_value = mock_generator

            tools = ThemeMCPTools(data_store)

        async def configure_ships(ship_prefix: str):
            """Configure multiple ships concurrently."""
            for i in range(5):
                await tools.configure_ship_crew(
                    ship_name=f"{ship_prefix}_Ship_{i}",
                    crew_roles=["commander", "navigator", "engineer"]
                )

        # Run concurrent ship configurations
        tasks = [configure_ships(f"Fleet_{i}") for i in range(3)]
        await asyncio.gather(*tasks)

        # Verify all ships were configured
        storage = tools.theme_storage
        all_configs = storage.get_all_ship_configs()
        assert len(all_configs) >= 15  # 3 fleets * 5 ships each

if __name__ == "__main__":
    pytest.main([__file__, "-v"])