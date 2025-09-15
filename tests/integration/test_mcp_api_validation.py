"""
Focused MCP API validation tests.

These tests validate the core MCP functionality with real journal data,
focusing on the methods that actually exist and testing the contextual
data integration that we just fixed.
"""

import pytest
import asyncio
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

from src.elite_mcp.mcp_tools import MCPTools
from src.utils.config import EliteConfig
from src.utils.data_store import DataStore
from src.journal.parser import JournalParser
from src.journal.events import EventProcessor


class TestMCPContextualData:
    """Test that MCP APIs return contextual data instead of placeholders."""

    @pytest.fixture(scope="class")
    def config(self):
        """Create test configuration."""
        journal_path = os.environ.get('TEST_JOURNAL_PATH',
                                     r'C:\Users\gwllo\Saved Games\Frontier Developments\Elite Dangerous')
        edcopilot_path = os.environ.get('TEST_EDCOPILOT_PATH',
                                       r'C:\Utilities\EDCoPilot\User custom files')

        # Skip tests if paths don't exist
        if not Path(journal_path).exists():
            pytest.skip(f"Journal path does not exist: {journal_path}")

        return EliteConfig(journal_path=journal_path, edcopilot_path=edcopilot_path)

    @pytest.fixture(scope="class")
    def loaded_data_store(self, config):
        """Create data store loaded with recent journal data."""
        data_store = DataStore()
        processor = EventProcessor()
        parser = JournalParser(config.journal_path)

        try:
            journal_files = parser.find_journal_files()
            if journal_files:
                # Load the most recent journal file
                latest_file = journal_files[-1]
                entries, _ = parser.read_journal_file(latest_file)

                # Process and store events
                for entry in entries[-50:]:  # Last 50 events for performance
                    try:
                        processed_event = processor.process_event(entry)
                        data_store.store_event(processed_event)
                    except Exception as e:
                        print(f"Warning: Could not process event: {e}")
                        continue

        except Exception as e:
            print(f"Warning: Could not load journal data: {e}")

        return data_store

    @pytest.fixture(scope="class")
    def mcp_tools(self, loaded_data_store):
        """Create MCP tools with loaded data."""
        return MCPTools(loaded_data_store)

    @pytest.mark.asyncio
    async def test_get_current_location_has_real_data(self, mcp_tools, loaded_data_store):
        """Test that current location returns real system names, not placeholders."""
        result = await mcp_tools.get_current_location()

        assert isinstance(result, dict), "Location should return a dictionary"

        current_system = result.get('current_system')
        if current_system:
            # Should not be placeholder values
            assert current_system != 'Unknown', "Should not return 'Unknown' as system name"
            assert current_system != 'Unknown System', "Should not return 'Unknown System'"
            assert '{SystemName}' not in current_system, "Should not contain template tokens"
            assert len(current_system) > 2, "System name should be substantial"

        # Test docked status makes sense
        docked = result.get('docked')
        if docked is not None:
            assert isinstance(docked, bool), "Docked status should be boolean"

    @pytest.mark.asyncio
    async def test_get_ship_status_has_real_data(self, mcp_tools, loaded_data_store):
        """Test that ship status returns real ship information."""
        result = await mcp_tools.get_ship_status()

        assert isinstance(result, dict), "Ship status should return a dictionary"

        ship_type = result.get('ship_type')
        if ship_type:
            assert ship_type != 'Unknown', "Should not return 'Unknown' as ship type"
            assert '{Ship}' not in ship_type, "Should not contain template tokens"

        ship_name = result.get('ship_name')
        if ship_name:
            assert '{ShipName}' not in ship_name, "Should not contain template tokens"
            assert len(ship_name) > 0, "Ship name should not be empty"

        # Status should be a dictionary
        status = result.get('status')
        if status:
            assert isinstance(status, dict), "Status should be a dictionary"

    @pytest.mark.asyncio
    async def test_search_events_returns_valid_structure(self, mcp_tools, loaded_data_store):
        """Test that event search returns properly structured data."""
        result = await mcp_tools.search_events(max_results=5)

        assert isinstance(result, dict), "Search results should be a dictionary"
        assert 'events' in result, "Should have events key"
        assert isinstance(result['events'], list), "Events should be a list"

        # Test event structure
        for event in result['events']:
            assert 'timestamp' in event, "Event should have timestamp"
            assert 'event_type' in event, "Event should have event_type"
            assert 'category' in event, "Event should have category"

            # Validate timestamp format
            timestamp = event['timestamp']
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {timestamp}")

    @pytest.mark.asyncio
    async def test_activity_summary_exploration(self, mcp_tools, loaded_data_store):
        """Test exploration activity summary."""
        result = await mcp_tools.get_activity_summary('exploration', time_range_hours=24)

        assert isinstance(result, dict), "Activity summary should be a dictionary"
        assert 'activity_type' in result, "Should include activity type"
        assert result['activity_type'] == 'exploration', "Activity type should match"

        # Should have numeric fields
        if 'bodies_scanned' in result:
            assert isinstance(result['bodies_scanned'], int), "Bodies scanned should be integer"
        if 'exploration_value' in result:
            assert isinstance(result['exploration_value'], (int, float)), "Exploration value should be numeric"

    @pytest.mark.asyncio
    async def test_journey_summary_has_valid_data(self, mcp_tools, loaded_data_store):
        """Test journey summary returns valid navigation data."""
        result = await mcp_tools.get_journey_summary(time_range_hours=24)

        assert isinstance(result, dict), "Journey summary should be a dictionary"
        assert 'total_jumps' in result, "Should include total jumps"
        assert 'systems_visited' in result, "Should include systems visited"
        assert 'total_distance' in result, "Should include total distance"

        # Validate data types
        assert isinstance(result['total_jumps'], int), "Total jumps should be integer"
        assert isinstance(result['systems_visited'], list), "Systems visited should be list"
        assert isinstance(result['total_distance'], (int, float)), "Distance should be numeric"

        # Systems visited should not contain placeholder values
        for system in result['systems_visited']:
            assert system != 'Unknown System', f"System '{system}' should not be placeholder"
            assert '{SystemName}' not in system, f"System '{system}' should not contain tokens"

    def test_generate_edcopilot_chatter_creates_contextual_content(self, mcp_tools, config):
        """Test that EDCoPilot generation creates contextual content, not placeholders."""
        if not Path(config.edcopilot_path).exists():
            pytest.skip(f"EDCoPilot path does not exist: {config.edcopilot_path}")

        result = mcp_tools.generate_edcopilot_chatter(chatter_type='space')

        assert isinstance(result, dict), "EDCoPilot result should be a dictionary"
        assert 'status' in result, "Should include status"

        if result['status'] == 'success':
            # Check generated files
            space_file = Path(config.edcopilot_path) / 'EDCoPilot.SpaceChatter.Custom.txt'
            if space_file.exists():
                content = space_file.read_text(encoding='utf-8')

                # Should not contain generic placeholders
                assert 'Unknown System' not in content, "Should not contain 'Unknown System' placeholder"
                assert 'Unknown' not in content or content.count('Unknown') < 5, "Should minimize 'Unknown' placeholders"
                assert '{SystemName}' not in content, "Should not contain {SystemName} tokens"
                assert '{Ship}' not in content, "Should not contain {Ship} tokens"
                assert '{Commander}' not in content, "Should not contain {Commander} tokens"

                # Should have substantial content
                lines = [line for line in content.split('\n') if line and not line.startswith('#')]
                assert len(lines) > 5, "Should have substantial chatter content"

    def test_get_edcopilot_status_validates_paths(self, mcp_tools, config):
        """Test EDCoPilot status validation."""
        result = mcp_tools.get_edcopilot_status()

        assert isinstance(result, dict), "EDCoPilot status should be a dictionary"
        assert 'edcopilot_path' in result, "Should include EDCoPilot path"

        # Path validation should be accurate
        expected_exists = Path(config.edcopilot_path).exists()
        if 'path_exists' in result:
            assert result['path_exists'] == expected_exists, "Path existence should be accurate"

    @pytest.mark.asyncio
    async def test_performance_metrics_structure(self, mcp_tools, loaded_data_store):
        """Test performance metrics return valid structure."""
        result = await mcp_tools.get_performance_metrics(time_range_hours=24)

        assert isinstance(result, dict), "Performance metrics should be a dictionary"

        # Should have numeric fields when present
        numeric_fields = ['credits_earned', 'credits_spent', 'net_worth_change']
        for field in numeric_fields:
            if field in result:
                assert isinstance(result[field], (int, float)), f"{field} should be numeric"

    def test_preview_edcopilot_chatter_returns_content(self, mcp_tools):
        """Test EDCoPilot preview functionality."""
        result = mcp_tools.preview_edcopilot_chatter(chatter_type='space')

        assert isinstance(result, dict), "Preview should return a dictionary"
        assert 'chatter_type' in result, "Should include chatter type"
        assert result['chatter_type'] == 'space', "Chatter type should match"

        if 'preview_content' in result:
            content = result['preview_content']
            assert isinstance(content, str), "Preview content should be string"
            if len(content) > 0:
                # Should not contain placeholder tokens in preview
                assert '{SystemName}' not in content, "Preview should not contain tokens"
                assert '{Ship}' not in content, "Preview should not contain tokens"


class TestMCPDataIntegrity:
    """Test data integrity and consistency in MCP responses."""

    @pytest.fixture(scope="class")
    def simple_data_store(self):
        """Create a data store with known test data."""
        data_store = DataStore()
        processor = EventProcessor()

        # Create known test events
        test_events = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "event": "LoadGame",
                "Commander": "TestCommander",
                "Ship": "Python",
                "ShipName": "Test Ship",
                "Credits": 1000000
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "event": "Location",
                "StarSystem": "Test System",
                "Docked": False
            }
        ]

        for event_data in test_events:
            processed_event = processor.process_event(event_data)
            data_store.store_event(processed_event)

        return data_store

    @pytest.fixture
    def test_mcp_tools(self, simple_data_store):
        """Create MCP tools with test data."""
        return MCPTools(simple_data_store)

    @pytest.mark.asyncio
    async def test_location_consistency(self, test_mcp_tools):
        """Test that location data is consistent."""
        result = await test_mcp_tools.get_current_location()

        current_system = result.get('current_system')
        if current_system:
            assert current_system == 'Test System', f"Expected 'Test System', got '{current_system}'"

    @pytest.mark.asyncio
    async def test_ship_data_consistency(self, test_mcp_tools):
        """Test that ship data is consistent."""
        result = await test_mcp_tools.get_ship_status()

        ship_type = result.get('ship_type')
        ship_name = result.get('ship_name')

        if ship_type:
            assert ship_type == 'Python', f"Expected 'Python', got '{ship_type}'"
        if ship_name:
            assert ship_name == 'Test Ship', f"Expected 'Test Ship', got '{ship_name}'"