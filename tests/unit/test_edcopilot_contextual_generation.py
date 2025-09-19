"""
Unit tests for EDCoPilot contextual chatter generation.

This test file captures the current failure where generated chatter does not
contain specific references to actual gameplay events and system names.
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from src.edcopilot.generator import EDCoPilotContentGenerator, EDCoPilotContextAnalyzer
from src.utils.data_store import DataStore, GameState
from src.journal.events import ProcessedEvent, EventCategory


class TestEDCoPilotContextualGeneration:
    """Test contextual chatter generation with real game data."""

    def setup_method(self):
        """Set up test fixtures with realistic Elite Dangerous data."""
        # Create temporary directory for EDCoPilot files
        self.temp_dir = tempfile.mkdtemp()
        self.edcopilot_path = Path(self.temp_dir)

        # Create mock data store with realistic Elite Dangerous data
        self.data_store = Mock(spec=DataStore)

        # Set up realistic game state (based on actual journal data)
        self.game_state = GameState()
        self.game_state.current_system = "Blae Drye IC-S d5-15"
        self.game_state.current_ship = "Mandalay EXCELSIOR"
        self.game_state.current_station = None
        self.game_state.docked = False
        self.game_state.credits = 2500000

        # Create realistic processed events from journal data
        self.recent_events = [
            ProcessedEvent(
                raw_event={
                    "event": "FSDJump",
                    "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat() + "Z",
                    "StarSystem": "Blae Drye IC-S d5-15",
                    "JumpDist": 45.2,
                    "FuelUsed": 2.1
                },
                event_type="FSDJump",
                timestamp=datetime.now() - timedelta(minutes=15),
                category=EventCategory.EXPLORATION,
                summary="Jumped to Blae Drye IC-S d5-15"
            ),
            ProcessedEvent(
                raw_event={
                    "event": "Scan",
                    "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat() + "Z",
                    "BodyName": "Blae Drye IC-S d5-15 A 2",
                    "TerraformState": "Terraformable",
                    "PlanetClass": "High metal content body"
                },
                event_type="Scan",
                timestamp=datetime.now() - timedelta(minutes=10),
                category=EventCategory.EXPLORATION,
                summary="Discovered terraformable world Blae Drye IC-S d5-15 A 2"
            ),
            ProcessedEvent(
                raw_event={
                    "event": "SAAScanComplete",
                    "timestamp": (datetime.now() - timedelta(minutes=8)).isoformat() + "Z",
                    "BodyName": "Blae Drye IC-S d5-15 A 2"
                },
                event_type="SAAScanComplete",
                timestamp=datetime.now() - timedelta(minutes=8),
                category=EventCategory.EXPLORATION,
                summary="First to map Blae Drye IC-S d5-15 A 2"
            )
        ]

        # Configure mock data store
        self.data_store.get_game_state.return_value = self.game_state
        self.data_store.get_recent_events.return_value = self.recent_events

        # Create generator
        self.generator = EDCoPilotContentGenerator(self.data_store, self.edcopilot_path)
        self.context_analyzer = EDCoPilotContextAnalyzer(self.data_store)

    def test_context_analyzer_extracts_specific_system_names(self):
        """Test that context analyzer extracts actual system names from events."""
        context = self.context_analyzer.analyze_current_context()

        # Should extract the actual current system name
        assert context['current_system'] == "Blae Drye IC-S d5-15"

        # Should identify exploration as primary activity
        assert context['primary_activity'] == 'exploration'

        # Should count recent discoveries
        assert context['recent_discoveries'] > 0

    def test_context_analyzer_identifies_ship_name(self):
        """Test that context analyzer extracts actual ship name."""
        context = self.context_analyzer.analyze_current_context()

        # Should extract the actual ship name from game state
        assert context['ship_type'] == "Mandalay EXCELSIOR"

    def test_generated_chatter_contains_specific_system_references(self):
        """Test that generated chatter contains references to actual visited systems."""
        # CURRENT FAILURE: This test should pass but currently fails
        files = self.generator.generate_contextual_chatter()

        # Check that space chatter contains the specific system name
        space_chatter = files.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Should use proper token format, not hardcoded system names
        assert "<SystemName>" in space_chatter, \
            f"Generated chatter should use <SystemName> token, but content was:\n{space_chatter[:500]}..."

        # Should NOT contain hardcoded system names (proper token usage)
        assert "Blae Drye IC-S d5-15" not in space_chatter, \
            "Chatter should use tokens, not hardcoded system names"

    def test_generated_chatter_contains_ship_name_references(self):
        """Test that generated chatter contains references to the actual ship."""
        # CURRENT FAILURE: This test should pass but currently fails
        files = self.generator.generate_contextual_chatter()

        space_chatter = files.get('EDCoPilot.SpaceChatter.Custom.txt', '')
        crew_chatter = files.get('EDCoPilot.CrewChatter.Custom.txt', '')

        # Should use proper token format, not hardcoded ship names
        combined_chatter = space_chatter + crew_chatter
        assert "<ShipName>" in combined_chatter or "<CommanderName>" in combined_chatter, \
            f"Generated chatter should use proper tokens, but content was:\n{combined_chatter[:500]}..."

        # Should NOT contain hardcoded ship names (proper token usage)
        assert "EXCELSIOR" not in combined_chatter and "Mandalay" not in combined_chatter, \
            "Chatter should use tokens, not hardcoded ship names"

    def test_generated_chatter_contains_discovery_references(self):
        """Test that generated chatter references actual discoveries made."""
        # CURRENT FAILURE: This test should pass but currently fails
        files = self.generator.generate_contextual_chatter()

        space_chatter = files.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Should reference the terraformable world discovery
        assert any(keyword in space_chatter for keyword in [
            "terraformable", "discovery", "discoveries", "first to map"
        ]), f"Generated chatter should reference recent discoveries, but content was:\n{space_chatter[:500]}..."

    def test_generated_chatter_contains_exploration_context(self):
        """Test that exploration-focused chatter is generated for exploration activities."""
        files = self.generator.generate_contextual_chatter()

        space_chatter = files.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Should contain exploration-specific dialogue
        exploration_keywords = [
            "exploration", "scanning", "discovered", "astronomical",
            "stellar", "cartography", "survey"
        ]

        assert any(keyword in space_chatter.lower() for keyword in exploration_keywords), \
            f"Generated chatter should contain exploration-specific content, but content was:\n{space_chatter[:500]}..."

    def test_chatter_uses_actual_context_not_tokens(self):
        """Test that generated chatter uses actual values instead of placeholder tokens."""
        # CURRENT FAILURE: This is the core issue being captured
        files = self.generator.generate_contextual_chatter()

        for filename, content in files.items():
            # Should not contain unresolved tokens
            problematic_tokens = ["{SystemName}", "{ShipName}", "{BodyName}"]
            for token in problematic_tokens:
                assert token not in content, \
                    f"File {filename} should not contain unresolved token {token}. Content:\n{content[:500]}..."

    def test_context_enhancement_modifies_templates(self):
        """Test that context enhancement actually adds specific content to templates."""
        # Generate base templates
        base_files = self.generator.template_manager.generate_all_templates()

        # Generate contextual templates
        contextual_files = self.generator.generate_contextual_chatter()

        # Contextual files should be different (longer) than base templates
        for filename in base_files.keys():
            if filename in contextual_files:
                base_length = len(base_files[filename])
                contextual_length = len(contextual_files[filename])

                assert contextual_length >= base_length, \
                    f"Contextual {filename} should be enhanced with additional content, " \
                    f"but was {contextual_length} chars vs {base_length} chars base"

    def test_multiple_activity_types_generate_different_content(self):
        """Test that different activity types (exploration vs trading) generate different content."""
        # Test exploration context (current setup)
        exploration_files = self.generator.generate_contextual_chatter()

        # Change to trading activity
        trading_events = [
            ProcessedEvent(
                raw_event={
                    "event": "MarketBuy",
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat() + "Z",
                    "Type": "Gold",
                    "Count": 100,
                    "TotalCost": 500000
                },
                event_type="MarketBuy",
                timestamp=datetime.now() - timedelta(minutes=5),
                category=EventCategory.TRADING,
                summary="Bought 100 tons of Gold"
            )
        ]

        self.data_store.get_recent_events.return_value = trading_events
        trading_files = self.generator.generate_contextual_chatter()

        # Content should be different for different activities
        exploration_content = exploration_files.get('EDCoPilot.SpaceChatter.Custom.txt', '')
        trading_content = trading_files.get('EDCoPilot.SpaceChatter.Custom.txt', '')

        # Should have different content for different activity types
        assert exploration_content != trading_content, \
            "Different activity types should generate different contextual content"


class TestEDCoPilotIntegrationWithMCPTool:
    """Integration tests for the MCP tool that calls the generator."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.edcopilot_path = Path(self.temp_dir)

    @patch('src.utils.config.EliteConfig')
    def test_mcp_tool_generates_files_with_actual_content(self, mock_config):
        """Test that the MCP tool generates files with actual contextual content."""
        from src.elite_mcp.mcp_tools import MCPTools

        # Set up mock config
        mock_config_instance = Mock()
        mock_config_instance.edcopilot_path = self.edcopilot_path
        mock_config.return_value = mock_config_instance

        # Set up mock data store with realistic data
        data_store = Mock(spec=DataStore)
        game_state = GameState()
        game_state.current_system = "Blae Drye TG-P b25-6"
        game_state.current_ship = "Mandalay EXCELSIOR"
        game_state.docked = False

        recent_events = [
            ProcessedEvent(
                raw_event={
                    "event": "FSDJump",
                    "timestamp": datetime.now().isoformat() + "Z",
                    "StarSystem": "Blae Drye TG-P b25-6",
                    "JumpDist": 52.3
                },
                event_type="FSDJump",
                timestamp=datetime.now(),
                category=EventCategory.EXPLORATION,
                summary="Jumped to complex multi-star system"
            )
        ]

        data_store.get_game_state.return_value = game_state
        data_store.get_recent_events.return_value = recent_events

        # Create MCP tools instance
        mcp_tools = MCPTools(data_store)

        # Call the MCP tool
        result = mcp_tools.generate_edcopilot_chatter("all")

        # Verify the result structure
        assert result['status'] == 'success'
        assert len(result['files_generated']) == 3

        # Verify actual files were created
        for filename in result['files_generated']:
            file_path = self.edcopilot_path / filename
            assert file_path.exists(), f"File {filename} should have been created"

            content = file_path.read_text()
            # CURRENT FAILURE: Should contain actual system name
            assert "Blae Drye" in content or len(content) > 100, \
                f"File {filename} should contain contextual content, but was:\n{content[:200]}..."


if __name__ == '__main__':
    pytest.main([__file__, '-v'])