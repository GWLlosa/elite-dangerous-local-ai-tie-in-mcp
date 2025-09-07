"""
Unit tests for Elite Dangerous journal event processing and classification.

Tests cover event categorization, summarization, validation, and statistics
generation with comprehensive coverage of all major event types.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch
import logging

from src.journal.events import (
    EventProcessor, ProcessedEvent, EventCategory,
    categorize_events, summarize_events, get_event_statistics
)


class TestEventProcessor:
    """Test EventProcessor class functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()
    
    @pytest.fixture
    def sample_events(self):
        """Create sample events for testing."""
        return {
            "fsd_jump": {
                "timestamp": "2024-01-15T10:30:00Z",
                "event": "FSDJump",
                "StarSystem": "Sol",
                "JumpDist": 8.03,
                "FuelUsed": 2.5,
                "FuelLevel": 30.0
            },
            "docked": {
                "timestamp": "2024-01-15T10:45:00Z",
                "event": "Docked",
                "StationName": "Abraham Lincoln",
                "StarSystem": "Sol",
                "StationType": "Coriolis"
            },
            "scan": {
                "timestamp": "2024-01-15T11:00:00Z",
                "event": "Scan",
                "BodyName": "Earth",
                "PlanetClass": "Earthlike body",
                "DistanceFromArrivalLS": 499.2,
                "TerraformState": "Terraformable",
                "Landable": False
            },
            "bounty": {
                "timestamp": "2024-01-15T11:15:00Z",
                "event": "Bounty",
                "Target": "pirate",
                "VictimFaction": "Anarchists",
                "TotalReward": 50000
            },
            "market_buy": {
                "timestamp": "2024-01-15T11:30:00Z",
                "event": "MarketBuy",
                "Type": "Gold",
                "Count": 10,
                "BuyPrice": 9000,
                "TotalCost": 90000
            },
            "mission_accepted": {
                "timestamp": "2024-01-15T11:45:00Z",
                "event": "MissionAccepted",
                "Name": "Mission_Delivery",
                "Faction": "Federation",
                "Reward": 100000,
                "Expiry": "2024-01-16T11:45:00Z"
            },
            "engineer_craft": {
                "timestamp": "2024-01-15T12:00:00Z",
                "event": "EngineerCraft",
                "Engineer": "Felicity Farseer",
                "Slot": "FrameShiftDrive",
                "BlueprintName": "FSD_LongRange",
                "Level": 3
            },
            "loadgame": {
                "timestamp": "2024-01-15T09:00:00Z",
                "event": "LoadGame",
                "Commander": "TestCommander",
                "Ship": "AspExplorer"
            },
            "location": {
                "timestamp": "2024-01-15T09:05:00Z",
                "event": "Location",
                "StarSystem": "Sol",
                "Body": "Earth",
                "Docked": True,
                "StationName": "Abraham Lincoln"
            },
            "unknown": {
                "timestamp": "2024-01-15T12:30:00Z",
                "event": "NewUnknownEvent",
                "CustomData": "test"
            },
            "invalid_timestamp": {
                "timestamp": "invalid-timestamp",
                "event": "TestEvent"
            },
            "missing_event": {
                "timestamp": "2024-01-15T13:00:00Z",
                "data": "test"
            },
            "missing_timestamp": {
                "event": "TestEvent",
                "data": "test"
            }
        }
    
    def test_process_navigation_event(self, processor, sample_events):
        """Test processing of navigation events."""
        # Test FSD Jump
        event = sample_events["fsd_jump"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "FSDJump"
        assert processed.category == EventCategory.NAVIGATION
        assert processed.summary == "Jumped to Sol (8.03ly)"
        assert processed.key_data["system"] == "Sol"
        assert processed.key_data["distance"] == 8.03
        assert processed.key_data["fuel_used"] == 2.5
        assert processed.is_valid
        
        # Test Docked
        event = sample_events["docked"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "Docked"
        assert processed.category == EventCategory.NAVIGATION
        assert processed.summary == "Docked at Abraham Lincoln in Sol"
        assert processed.key_data["station"] == "Abraham Lincoln"
        assert processed.key_data["system"] == "Sol"
    
    def test_process_exploration_event(self, processor, sample_events):
        """Test processing of exploration events."""
        event = sample_events["scan"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "Scan"
        assert processed.category == EventCategory.EXPLORATION
        assert processed.summary == "Scanned Earth - Earthlike body (terraformable)"
        assert processed.key_data["body_name"] == "Earth"
        assert processed.key_data["terraformable"] is True
        assert processed.key_data["landable"] is False
    
    def test_process_combat_event(self, processor, sample_events):
        """Test processing of combat events."""
        event = sample_events["bounty"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "Bounty"
        assert processed.category == EventCategory.COMBAT
        assert processed.summary == "Collected bounty on pirate for 50,000 credits"
        assert processed.key_data["target"] == "pirate"
        assert processed.key_data["reward"] == 50000
    
    def test_process_trading_event(self, processor, sample_events):
        """Test processing of trading events."""
        event = sample_events["market_buy"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "MarketBuy"
        assert processed.category == EventCategory.TRADING
        assert processed.summary == "Bought 10t of Gold for 90,000 credits"
        assert processed.key_data["commodity"] == "Gold"
        assert processed.key_data["count"] == 10
        assert processed.key_data["total"] == 90000
    
    def test_process_mission_event(self, processor, sample_events):
        """Test processing of mission events."""
        event = sample_events["mission_accepted"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "MissionAccepted"
        assert processed.category == EventCategory.MISSION
        assert processed.summary == "Accepted mission from Federation for 100,000 credits"
        assert processed.key_data["faction"] == "Federation"
        assert processed.key_data["reward"] == 100000
    
    def test_process_engineering_event(self, processor, sample_events):
        """Test processing of engineering events."""
        event = sample_events["engineer_craft"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "EngineerCraft"
        assert processed.category == EventCategory.ENGINEERING
        assert processed.summary == "Felicity Farseer applied FSD_LongRange level 3 to FrameShiftDrive"
        assert processed.key_data["engineer"] == "Felicity Farseer"
        assert processed.key_data["level"] == 3
    
    def test_process_system_event(self, processor, sample_events):
        """Test processing of system events."""
        # Test LoadGame
        event = sample_events["loadgame"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "LoadGame"
        assert processed.category == EventCategory.SYSTEM
        assert processed.summary == "TestCommander loaded game in AspExplorer"
        
        # Test Location
        event = sample_events["location"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "Location"
        assert processed.category == EventCategory.NAVIGATION
        assert processed.summary == "Located at Abraham Lincoln in Sol"
        assert processed.key_data["docked"] is True
    
    def test_process_unknown_event(self, processor, sample_events):
        """Test processing of unknown event types."""
        event = sample_events["unknown"]
        processed = processor.process_event(event)
        
        assert processed.event_type == "NewUnknownEvent"
        assert processed.category == EventCategory.OTHER
        assert processed.summary == "NewUnknownEvent event occurred"
        assert processed.is_valid
        
        # Check that unknown event was tracked
        assert "NewUnknownEvent" in processor.get_unknown_events()
    
    def test_event_validation(self, processor, sample_events):
        """Test event validation."""
        # Test invalid timestamp
        event = sample_events["invalid_timestamp"]
        processed = processor.process_event(event)
        
        assert processed.is_valid  # Should still be valid, just use current time
        assert processed.event_type == "TestEvent"
        
        # Test missing event field
        event = sample_events["missing_event"]
        processed = processor.process_event(event)
        
        assert not processed.is_valid
        assert "Missing required field: 'event'" in processed.validation_errors
        
        # Test missing timestamp field
        event = sample_events["missing_timestamp"]
        processed = processor.process_event(event)
        
        assert not processed.is_valid
        assert "Missing required field: 'timestamp'" in processed.validation_errors
    
    def test_timestamp_parsing(self, processor):
        """Test timestamp parsing with various formats."""
        # Test with Z suffix
        event = {
            "timestamp": "2024-01-15T10:30:00Z",
            "event": "Test"
        }
        processed = processor.process_event(event)
        assert processed.timestamp.year == 2024
        assert processed.timestamp.month == 1
        assert processed.timestamp.day == 15
        
        # Test with timezone
        event = {
            "timestamp": "2024-01-15T10:30:00+00:00",
            "event": "Test"
        }
        processed = processor.process_event(event)
        assert processed.timestamp.year == 2024
        
        # Test with invalid timestamp (should use current time)
        with patch('src.journal.events.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            event = {
                "timestamp": "",
                "event": "Test"
            }
            processed = processor.process_event(event)
            assert processed.timestamp == mock_now
    
    def test_clear_unknown_events(self, processor, sample_events):
        """Test clearing unknown events list."""
        # Process an unknown event
        processor.process_event(sample_events["unknown"])
        assert len(processor.get_unknown_events()) > 0
        
        # Clear and verify
        processor.clear_unknown_events()
        assert len(processor.get_unknown_events()) == 0
    
    def test_all_event_categories_mapped(self, processor):
        """Test that all major event types are properly categorized."""
        # Sample of event types from each category
        test_mappings = {
            "Fileheader": EventCategory.SYSTEM,
            "FSDJump": EventCategory.NAVIGATION,
            "Scan": EventCategory.EXPLORATION,
            "Bounty": EventCategory.COMBAT,
            "MarketBuy": EventCategory.TRADING,
            "MissionAccepted": EventCategory.MISSION,
            "EngineerCraft": EventCategory.ENGINEERING,
            "AsteroidCracked": EventCategory.MINING,
            "ShipyardBuy": EventCategory.SHIP,
            "SquadronCreated": EventCategory.SQUADRON,
            "CrewHire": EventCategory.CREW,
            "PassengerManifest": EventCategory.PASSENGER,
            "PowerplayJoin": EventCategory.POWERPLAY,
            "CarrierJump": EventCategory.CARRIER,
            "Friends": EventCategory.SOCIAL,
            "SuitPurchased": EventCategory.SUIT,
            "UnknownEventType": EventCategory.OTHER
        }
        
        for event_type, expected_category in test_mappings.items():
            event = {"timestamp": "2024-01-15T10:00:00Z", "event": event_type}
            processed = processor.process_event(event)
            assert processed.category == expected_category, f"Event {event_type} should be {expected_category}"


class TestEventFunctions:
    """Test module-level event processing functions."""
    
    @pytest.fixture
    def mixed_events(self):
        """Create a mix of events for testing."""
        return [
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "event": "LoadGame",
                "Commander": "TestCmdr"
            },
            {
                "timestamp": "2024-01-15T10:15:00Z",
                "event": "FSDJump",
                "StarSystem": "Alpha Centauri",
                "JumpDist": 4.37
            },
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "event": "Scan",
                "BodyName": "Proxima Centauri b"
            },
            {
                "timestamp": "2024-01-15T10:45:00Z",
                "event": "Bounty",
                "Target": "pirate",
                "TotalReward": 25000
            },
            {
                "timestamp": "2024-01-15T11:00:00Z",
                "event": "MarketSell",
                "Type": "Painite",
                "Count": 5,
                "SellPrice": 50000,
                "TotalSale": 250000
            },
            {
                "timestamp": "2024-01-15T11:15:00Z",
                "event": "UnknownEvent",
                "Data": "test"
            }
        ]
    
    def test_categorize_events(self, mixed_events):
        """Test event categorization function."""
        categorized = categorize_events(mixed_events)
        
        # Check all categories exist
        assert all(cat in categorized for cat in EventCategory)
        
        # Check correct categorization
        assert len(categorized[EventCategory.SYSTEM]) == 1
        assert len(categorized[EventCategory.NAVIGATION]) == 1
        assert len(categorized[EventCategory.EXPLORATION]) == 1
        assert len(categorized[EventCategory.COMBAT]) == 1
        assert len(categorized[EventCategory.TRADING]) == 1
        assert len(categorized[EventCategory.OTHER]) == 1
        
        # Check event details
        system_event = categorized[EventCategory.SYSTEM][0]
        assert system_event.event_type == "LoadGame"
        
        nav_event = categorized[EventCategory.NAVIGATION][0]
        assert nav_event.event_type == "FSDJump"
        assert nav_event.key_data["system"] == "Alpha Centauri"
    
    def test_summarize_events(self, mixed_events):
        """Test event summarization function."""
        summaries = summarize_events(mixed_events, max_summaries=3)
        
        # Check we get correct number of summaries
        assert len(summaries) == 3
        
        # Check format includes timestamp and summary
        assert "[10:00:00]" in summaries[0]
        assert "loaded game" in summaries[0].lower()
        
        assert "[10:15:00]" in summaries[1]
        assert "Alpha Centauri" in summaries[1]
        
        assert "[10:30:00]" in summaries[2]
        assert "Proxima Centauri b" in summaries[2]
    
    def test_summarize_events_with_limit(self, mixed_events):
        """Test event summarization respects max limit."""
        summaries = summarize_events(mixed_events, max_summaries=2)
        assert len(summaries) == 2
        
        summaries = summarize_events(mixed_events, max_summaries=10)
        assert len(summaries) == len(mixed_events)
    
    def test_get_event_statistics(self, mixed_events):
        """Test event statistics generation."""
        stats = get_event_statistics(mixed_events)
        
        # Check basic stats
        assert stats["total_events"] == 6
        assert stats["invalid_events"] == 0
        
        # Check category counts
        assert stats["categories"]["system"] == 1
        assert stats["categories"]["navigation"] == 1
        assert stats["categories"]["exploration"] == 1
        assert stats["categories"]["combat"] == 1
        assert stats["categories"]["trading"] == 1
        assert stats["categories"]["other"] == 1
        
        # Check event type counts
        assert stats["event_types"]["LoadGame"] == 1
        assert stats["event_types"]["FSDJump"] == 1
        assert stats["event_types"]["UnknownEvent"] == 1
        
        # Check time range
        assert stats["time_range"]["start"] == "2024-01-15T10:00:00"
        assert stats["time_range"]["end"] == "2024-01-15T11:15:00"
        
        # Check unknown events
        assert "UnknownEvent" in stats["unknown_events"]
    
    def test_get_event_statistics_empty(self):
        """Test statistics generation with empty event list."""
        stats = get_event_statistics([])
        
        assert stats["total_events"] == 0
        assert stats["categories"] == {}
        assert stats["event_types"] == {}
        assert stats["invalid_events"] == 0
        assert stats["time_range"] is None
    
    def test_get_event_statistics_with_invalid(self):
        """Test statistics with invalid events."""
        events = [
            {"timestamp": "2024-01-15T10:00:00Z", "event": "Valid"},
            {"timestamp": "2024-01-15T10:15:00Z"},  # Missing event
            {"event": "NoTimestamp"},  # Missing timestamp
            {"data": "NotAnEvent"}  # Missing both
        ]
        
        stats = get_event_statistics(events)
        
        assert stats["total_events"] == 4
        assert stats["invalid_events"] == 3
        assert stats["event_types"]["Valid"] == 1
        assert stats["event_types"]["Unknown"] == 3  # Invalid events default to "Unknown"


class TestComplexEventScenarios:
    """Test complex event processing scenarios."""
    
    def test_died_event_processing(self):
        """Test processing of death events with different killers."""
        processor = EventProcessor()
        
        # Killed by NPC
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Died",
            "KillerName": "Pirate Lord",
            "KillerShip": "Anaconda",
            "CombatRank": 5
        }
        processed = processor.process_event(event)
        
        assert processed.category == EventCategory.COMBAT
        assert processed.summary == "Destroyed by Pirate Lord flying Anaconda"
        assert processed.key_data["killer"] == "Pirate Lord"
        assert processed.key_data["killer_ship"] == "Anaconda"
        
        # Killed without ship info
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Died",
            "KillerName": "Station Defenses"
        }
        processed = processor.process_event(event)
        assert processed.summary == "Destroyed by Station Defenses"
    
    def test_exploration_data_sale(self):
        """Test processing of exploration data sale events."""
        processor = EventProcessor()
        
        # Multi-sell event
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "MultiSellExplorationData",
            "TotalEarnings": 5000000,
            "Bonus": 1000000,
            "Systems": ["Sol", "Alpha Centauri", "Proxima Centauri"],
            "Discovered": 42
        }
        processed = processor.process_event(event)
        
        assert processed.category == EventCategory.EXPLORATION
        assert processed.summary == "Sold exploration data for 5,000,000 credits"
        assert processed.key_data["value"] == 5000000
        assert processed.key_data["bonus"] == 1000000
        assert len(processed.key_data["systems"]) == 3
        assert processed.key_data["discovered"] == 42
    
    def test_location_event_variations(self):
        """Test different location event variations."""
        processor = EventProcessor()
        
        # Docked at station
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Location",
            "StarSystem": "Sol",
            "Body": "Earth",
            "Docked": True,
            "StationName": "Abraham Lincoln"
        }
        processed = processor.process_event(event)
        assert processed.summary == "Located at Abraham Lincoln in Sol"
        
        # In space
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Location",
            "StarSystem": "Sol",
            "Docked": False
        }
        processed = processor.process_event(event)
        assert processed.summary == "Located in Sol"
        
        # On planet surface
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Location",
            "StarSystem": "Sol",
            "Body": "Earth",
            "Docked": False
        }
        processed = processor.process_event(event)
        assert processed.summary == "Located in Sol"
    
    def test_scan_event_variations(self):
        """Test different scan event variations."""
        processor = EventProcessor()
        
        # Scan terraformable landable planet
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Scan",
            "BodyName": "Test Planet",
            "PlanetClass": "High metal content body",
            "DistanceFromArrivalLS": 100,
            "TerraformState": "Terraformable",
            "Landable": True
        }
        processed = processor.process_event(event)
        assert "terraformable, landable" in processed.summary
        
        # Scan star
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Scan",
            "BodyName": "Test Star",
            "StarType": "G",
            "DistanceFromArrivalLS": 0
        }
        processed = processor.process_event(event)
        assert processed.key_data["body_type"] == "G"
        assert processed.key_data["terraformable"] is False
        assert processed.key_data["landable"] is False
    
    def test_ship_events(self):
        """Test ship-related events."""
        processor = EventProcessor()
        
        # Ship purchase
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "ShipyardBuy",
            "ShipType": "AspExplorer",
            "ShipPrice": 6661153
        }
        processed = processor.process_event(event)
        assert processed.category == EventCategory.SHIP
        assert processed.summary == "Purchased AspExplorer for 6,661,153 credits"
        
        # Loadout event
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "Loadout",
            "Ship": "AspExplorer",
            "ShipName": "Wanderer",
            "ShipIdent": "ABC-123",
            "HullValue": 5000000
        }
        processed = processor.process_event(event)
        assert processed.summary == "Loadout for AspExplorer 'Wanderer'"
        assert processed.key_data["ship_name"] == "Wanderer"
    
    def test_trading_events(self):
        """Test trading event variations."""
        processor = EventProcessor()
        
        # Market sell
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "MarketSell",
            "Type": "Painite",
            "Count": 100,
            "SellPrice": 80000,
            "TotalSale": 8000000
        }
        processed = processor.process_event(event)
        assert processed.category == EventCategory.TRADING
        assert processed.summary == "Sold 100t of Painite for 8,000,000 credits"
        assert processed.key_data["commodity"] == "Painite"
    
    def test_mission_events(self):
        """Test mission event processing."""
        processor = EventProcessor()
        
        # Mission completed
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "MissionCompleted",
            "Name": "Mission_Delivery",
            "Faction": "Federation",
            "Reward": 500000
        }
        processed = processor.process_event(event)
        assert processed.category == EventCategory.MISSION
        assert processed.summary == "Completed mission for Federation, earned 500,000 credits"


class TestEventProcessorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_malformed_json_handling(self):
        """Test handling of malformed events."""
        processor = EventProcessor()
        
        # Completely empty event
        event = {}
        processed = processor.process_event(event)
        assert not processed.is_valid
        assert len(processed.validation_errors) == 2  # Missing event and timestamp
        
        # Event with None values
        event = {
            "timestamp": None,
            "event": None
        }
        processed = processor.process_event(event)
        assert processed.event_type == "Unknown"
    
    def test_event_with_extra_fields(self):
        """Test that extra fields don't break processing."""
        processor = EventProcessor()
        
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "FSDJump",
            "StarSystem": "Sol",
            "JumpDist": 8.03,
            "ExtraField1": "test",
            "ExtraField2": 123,
            "ExtraField3": {"nested": "data"}
        }
        processed = processor.process_event(event)
        
        assert processed.is_valid
        assert processed.category == EventCategory.NAVIGATION
        assert processed.key_data["system"] == "Sol"
    
    def test_concurrent_unknown_events(self):
        """Test tracking multiple unknown events."""
        processor = EventProcessor()
        
        unknown_types = ["Unknown1", "Unknown2", "Unknown3"]
        for event_type in unknown_types:
            event = {
                "timestamp": "2024-01-15T10:00:00Z",
                "event": event_type
            }
            processor.process_event(event)
        
        unknown_list = processor.get_unknown_events()
        assert len(unknown_list) == 3
        assert all(t in unknown_list for t in unknown_types)
    
    def test_logging_of_unknown_events(self, caplog):
        """Test that unknown events are logged."""
        processor = EventProcessor()
        
        with caplog.at_level(logging.DEBUG):
            event = {
                "timestamp": "2024-01-15T10:00:00Z",
                "event": "CompletelyNewEvent"
            }
            processor.process_event(event)
            
            assert "Unknown event type encountered: CompletelyNewEvent" in caplog.text
    
    def test_timestamp_timezone_handling(self):
        """Test handling of different timezone formats."""
        processor = EventProcessor()
        
        # Test various timezone formats
        formats = [
            "2024-01-15T10:00:00Z",
            "2024-01-15T10:00:00+00:00",
            "2024-01-15T10:00:00-05:00",
            "2024-01-15T10:00:00+01:00"
        ]
        
        for timestamp in formats:
            event = {
                "timestamp": timestamp,
                "event": "Test"
            }
            processed = processor.process_event(event)
            assert processed.is_valid
            assert isinstance(processed.timestamp, datetime)