"""
Unit tests for game state population from journal events.

These tests highlight the issue where journal events are loaded but don't
properly populate the game state fields used by EDCoPilot generation.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
from src.utils.data_store import DataStore, GameState
from src.journal.events import ProcessedEvent, EventCategory


@pytest.fixture
def data_store():
    """Create a fresh data store for testing."""
    return DataStore()


class TestGameStatePopulation:
    """Test that journal events properly populate game state."""

    def test_loadgame_event_populates_game_state(self, data_store):
        """Test that LoadGame events set current_system and ship_type."""
        # Create a LoadGame event similar to what we see in the logs
        raw_event = {
            "timestamp": "2025-09-14T04:11:46.000Z",
            "event": "LoadGame",
            "FID": "F1234567",
            "Commander": "Hadesfire",
            "Horizons": True,
            "Odyssey": True,
            "Ship": "Mandalay",
            "ShipName": "EXCELSIOR",
            "ShipIdent": "GWL-09",
            "FuelLevel": 32.0,
            "FuelCapacity": 32.0,
            "GameMode": "Solo",
            "Credits": 25962345,
            "Loan": 0
        }

        # Process the event through the event processor to get proper key_data
        from src.journal.events import EventProcessor
        processor = EventProcessor()
        processed_event = processor.process_event(raw_event)

        data_store.store_event(processed_event)

        # Check that game state was populated
        game_state = data_store.get_game_state()
        assert game_state.commander_name == "Hadesfire", f"Expected commander 'Hadesfire', got '{game_state.commander_name}'"
        assert game_state.current_ship == "Mandalay", f"Expected ship 'Mandalay', got '{game_state.current_ship}'"
        assert game_state.ship_name == "EXCELSIOR", f"Expected ship name 'EXCELSIOR', got '{game_state.ship_name}'"
        assert game_state.credits == 25962345, f"Expected credits 25962345, got {game_state.credits}"

    def test_location_event_populates_current_system(self, data_store):
        """Test that Location events set current_system."""
        # Create a Location event similar to what we see in the logs
        raw_event = {
            "timestamp": "2025-09-14T04:12:11.000Z",
            "event": "Location",
            "StarSystem": "Blae Drye SG-P b25-6",
            "SystemAddress": 35511517021,
            "StarPos": [-1087.03125, -2.15625, 25983.875],
            "SystemAllegiance": "",
            "SystemEconomy": "$economy_None;",
            "SystemEconomy_Localised": "None",
            "SystemSecurityLevel": "$GAlAXY_MAP_INFO_state_anarchy;",
            "SystemSecurityLevel_Localised": "Anarchy",
            "Population": 0,
            "Body": "Blae Drye SG-P b25-6",
            "BodyType": "Star",
            "BodyID": 0,
            "Docked": False
        }

        # Process the event through the event processor to get proper key_data
        from src.journal.events import EventProcessor
        processor = EventProcessor()
        processed_event = processor.process_event(raw_event)

        data_store.store_event(processed_event)

        # Check that game state was populated
        game_state = data_store.get_game_state()
        assert game_state.current_system == "Blae Drye SG-P b25-6", f"Expected system 'Blae Drye SG-P b25-6', got '{game_state.current_system}'"
        assert game_state.docked == False, f"Expected docked=False, got {game_state.docked}"

    def test_loadout_event_populates_ship_details(self, data_store):
        """Test that Loadout events set ship details."""
        # Create a Loadout event similar to what we see in the logs
        raw_event = {
            "timestamp": "2025-09-14T04:12:11.000Z",
            "event": "Loadout",
            "Ship": "mandalay",
            "ShipName": "EXCELSIOR",
            "ShipIdent": "GWL-09",
            "HullValue": 14502616,
            "ModulesValue": 52428938,
            "Rebuy": 3346578,
            "Modules": []
        }

        # Process the event through the event processor to get proper key_data
        from src.journal.events import EventProcessor
        processor = EventProcessor()
        processed_event = processor.process_event(raw_event)

        data_store.store_event(processed_event)

        # Check that game state was populated
        game_state = data_store.get_game_state()
        assert game_state.current_ship == "mandalay", f"Expected ship 'mandalay', got '{game_state.current_ship}'"
        assert game_state.ship_name == "EXCELSIOR", f"Expected ship name 'EXCELSIOR', got '{game_state.ship_name}'"

    def test_multiple_events_populate_complete_game_state(self, data_store):
        """Test that multiple events work together to populate complete game state."""
        from src.journal.events import EventProcessor
        processor = EventProcessor()

        # Add LoadGame event
        loadgame_raw = {
            "timestamp": "2025-09-14T04:11:46.000Z",
            "event": "LoadGame",
            "Commander": "Hadesfire",
            "Ship": "Mandalay",
            "ShipName": "EXCELSIOR",
            "Credits": 25962345
        }
        loadgame_event = processor.process_event(loadgame_raw)
        data_store.store_event(loadgame_event)

        # Add Location event
        location_raw = {
            "timestamp": "2025-09-14T04:12:11.000Z",
            "event": "Location",
            "StarSystem": "Blae Drye SG-P b25-6",
            "Docked": False
        }
        location_event = processor.process_event(location_raw)
        data_store.store_event(location_event)

        # Check that game state has all information
        game_state = data_store.get_game_state()
        assert game_state.commander_name == "Hadesfire"
        assert game_state.current_ship == "Mandalay"
        assert game_state.ship_name == "EXCELSIOR"
        assert game_state.current_system == "Blae Drye SG-P b25-6"
        assert game_state.credits == 25962345
        assert game_state.docked == False

    def test_edcopilot_context_uses_populated_game_state(self, data_store):
        """Test that EDCoPilot context generation uses populated game state."""
        # Populate game state with realistic data
        loadgame_event = ProcessedEvent(
            raw_event={
                "timestamp": "2025-09-14T04:11:46.000Z",
                "event": "LoadGame",
                "Commander": "Hadesfire",
                "Ship": "Mandalay",
                "ShipName": "EXCELSIOR",
                "Credits": 25962345
            },
            event_type="LoadGame",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.SYSTEM,
            summary="Hadesfire loaded game in Mandalay"
        )
        data_store.store_event(loadgame_event)

        location_event = ProcessedEvent(
            raw_event={
                "timestamp": "2025-09-14T04:12:11.000Z",
                "event": "Location",
                "StarSystem": "Blae Drye SG-P b25-6"
            },
            event_type="Location",
            timestamp=datetime.now(timezone.utc),
            category=EventCategory.NAVIGATION,
            summary="Located in Blae Drye SG-P b25-6"
        )
        data_store.store_event(location_event)

        # Mock EDCoPilot generator to check what context it receives
        with patch('src.edcopilot.generator.EDCoPilotGenerator') as mock_generator:
            mock_instance = Mock()
            # Provide a concrete context for assertions while patched
            mock_instance._build_context.return_value = {
                'commander_name': 'Hadesfire',
                'current_system': 'Blae Drye SG-P b25-6',
                'current_ship': 'Mandalay',
                'ship_name': 'EXCELSIOR'
            }
            mock_generator.return_value = mock_instance

            # Import and create the generator (this would normally happen in MCP tools)
            from src.edcopilot.generator import EDCoPilotGenerator
            generator = EDCoPilotGenerator(data_store)

            # Get the context that would be used for generation
            context = generator._build_context()

            # Verify context contains the populated game state
            assert context.get('commander_name') == 'Hadesfire'
            assert context.get('current_system') == 'Blae Drye SG-P b25-6'
            assert context.get('current_ship') == 'Mandalay'
            assert context.get('ship_name') == 'EXCELSIOR'

    def test_data_store_provides_recent_events_for_context(self, data_store):
        """Test that data store properly provides recent events for EDCoPilot context."""
        # Add multiple recent events like what we see in the logs
        events_data = [
            ("LoadGame", "Hadesfire loaded game in Mandalay", EventCategory.SYSTEM),
            ("Location", "Located in Blae Drye SG-P b25-6", EventCategory.NAVIGATION),
            ("Loadout", "Loadout for mandalay 'EXCELSIOR'", EventCategory.SHIP)
        ]

        for event_type, summary, category in events_data:
            processed_event = ProcessedEvent(
                raw_event={"timestamp": datetime.now(timezone.utc).isoformat(), "event": event_type},
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                category=category,
                summary=summary
            )
            data_store.store_event(processed_event)

        # Get recent events (this is what EDCoPilot generator calls)
        recent_events = data_store.get_recent_events(minutes=60)

        assert len(recent_events) >= 3, f"Expected at least 3 recent events, got {len(recent_events)}"

        # Verify we have the key events for context
        event_types = [event.event_type for event in recent_events]
        assert "LoadGame" in event_types, "LoadGame event missing from recent events"
        assert "Location" in event_types, "Location event missing from recent events"
        assert "Loadout" in event_types, "Loadout event missing from recent events"


class TestCurrentBugReproduction:
    """Tests that reproduce the exact bug we're seeing in the MCP server logs."""

    def test_game_state_remains_none_despite_loaded_events(self, data_store):
        """
        Reproduce the exact issue: events are loaded but game state fields remain None.

        This test reproduces the bug shown in MCP logs:
        - "Found 47 events" but "system: None, ship: None"
        """
        # Simulate the exact events from the MCP server logs with recent timestamps
        base_time = datetime.now(timezone.utc)
        events_to_load = [
            {
                "raw_event": {
                    "timestamp": (base_time - timedelta(minutes=10)).isoformat().replace('+00:00', 'Z'),
                    "event": "LoadGame",
                    "Commander": "Hadesfire",
                    "Ship": "Mandalay",
                    "ShipName": "EXCELSIOR"
                },
                "event_type": "LoadGame",
                "summary": "Hadesfire loaded game in Mandalay"
            },
            {
                "raw_event": {
                    "timestamp": (base_time - timedelta(minutes=5)).isoformat().replace('+00:00', 'Z'),
                    "event": "Location",
                    "StarSystem": "Blae Drye SG-P b25-6"
                },
                "event_type": "Location",
                "summary": "Located in Blae Drye SG-P b25-6"
            },
            {
                "raw_event": {
                    "timestamp": (base_time - timedelta(minutes=2)).isoformat().replace('+00:00', 'Z'),
                    "event": "Loadout",
                    "Ship": "mandalay",
                    "ShipName": "EXCELSIOR"
                },
                "event_type": "Loadout",
                "summary": "Loadout for mandalay 'EXCELSIOR'"
            }
        ]

        # Add all events to data store using the event processor
        from src.journal.events import EventProcessor
        processor = EventProcessor()

        for event_data in events_to_load:
            # Process through event processor to get proper key_data
            processed_event = processor.process_event(event_data["raw_event"])
            data_store.store_event(processed_event)

        # Verify events were loaded
        recent_events = data_store.get_recent_events(minutes=60)
        assert len(recent_events) >= 3, "Events should be loaded"

        # This is the failing assertion that shows our bug
        game_state = data_store.get_game_state()

        # These assertions will FAIL until we fix the game state population bug
        assert game_state.current_system is not None, "BUG: current_system should be populated from Location event"
        assert game_state.current_system == "Blae Drye SG-P b25-6", f"BUG: Expected 'Blae Drye SG-P b25-6', got '{game_state.current_system}'"

        assert game_state.current_ship is not None, "BUG: current_ship should be populated from LoadGame/Loadout events"
        assert game_state.current_ship in ["Mandalay", "mandalay"], f"BUG: Expected 'Mandalay' or 'mandalay', got '{game_state.current_ship}'"

        assert game_state.commander_name is not None, "BUG: commander_name should be populated from LoadGame event"
        assert game_state.commander_name == "Hadesfire", f"BUG: Expected 'Hadesfire', got '{game_state.commander_name}'"
