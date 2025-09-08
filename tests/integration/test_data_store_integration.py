"""
Integration tests for Data Store with Journal Monitoring System - Milestone 6

These tests demonstrate the complete flow from journal monitoring to data storage,
showing how the data store integrates with existing components.
"""

import pytest
import asyncio
import time
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

from src.journal.monitor import JournalMonitor
from src.journal.events import EventProcessor  
from src.utils.data_store import DataStore, EventFilter, get_data_store, reset_data_store
from src.utils.config import EliteConfig


class TestDataStoreIntegration:
    """Integration tests for data store with journal monitoring system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.journal_path = Path(self.temp_dir)
        
        # Create test data store
        self.data_store = DataStore(max_events=100, cleanup_interval=60)
        
        # Create event processor
        self.event_processor = EventProcessor()
        
        # Reset global data store
        reset_data_store()
        
    def teardown_method(self):
        """Clean up after tests."""
        self.data_store.clear()
        reset_data_store()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_journal_file(self, filename: str, events: list) -> Path:
        """Create a test journal file with specified events."""
        journal_file = self.journal_path / filename
        
        with open(journal_file, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
        
        return journal_file
    
    def test_end_to_end_journal_to_data_store(self):
        """Test complete flow from journal file to data store."""
        # Create test journal events
        base_time = datetime.utcnow()
        test_events = [
            {
                "timestamp": (base_time - timedelta(minutes=10)).isoformat() + "Z",
                "event": "LoadGame",
                "Commander": "TestCMDR",
                "Ship": "Asp Explorer",
                "Credits": 1000000
            },
            {
                "timestamp": (base_time - timedelta(minutes=8)).isoformat() + "Z",
                "event": "FSDJump", 
                "StarSystem": "Sol",
                "StarPos": [0.0, 0.0, 0.0],
                "SystemAllegiance": "Federation",
                "SystemEconomy": "$economy_HighTech;",
                "SystemGovernment": "$government_Democracy;"
            },
            {
                "timestamp": (base_time - timedelta(minutes=5)).isoformat() + "Z",
                "event": "SupercruiseExit",
                "StarSystem": "Sol",
                "Body": "Earth"
            },
            {
                "timestamp": (base_time - timedelta(minutes=2)).isoformat() + "Z",
                "event": "Docked",
                "StationName": "Abraham Lincoln",
                "StationType": "Orbis"
            }
        ]
        
        # Create journal file
        journal_file = self.create_test_journal_file("Journal.2024-01-15T100000.01.log", test_events)
        
        # Process events through the complete pipeline
        processed_events = []
        
        # Read and process each event
        with open(journal_file, 'r') as f:
            for line in f:
                if line.strip():
                    raw_event = json.loads(line.strip())
                    processed_event = self.event_processor.process_event(raw_event)
                    processed_events.append(processed_event)
                    
                    # Store in data store
                    self.data_store.store_event(processed_event)
        
        # Verify events were processed and stored correctly
        assert len(processed_events) == 4
        
        # Check data store contents
        stored_events = self.data_store.query_events()
        assert len(stored_events) == 4
        
        # Verify event types were processed correctly
        event_types = [e.event_type for e in stored_events]
        assert "LoadGame" in event_types
        assert "FSDJump" in event_types
        assert "SupercruiseExit" in event_types
        assert "Docked" in event_types
        
        # Verify game state was updated correctly
        game_state = self.data_store.get_game_state()
        assert game_state.current_system == "Sol"
        assert game_state.current_station == "Abraham Lincoln"
        assert game_state.current_ship == "Asp Explorer"
        assert game_state.docked == True
        assert game_state.supercruise == False
        assert game_state.credits == 1000000
    
    def test_real_time_monitoring_with_data_store(self):
        """Test real-time journal monitoring integration with data store."""
        # Create initial journal file
        initial_events = [
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": "LoadGame",
                "Commander": "TestCMDR",
                "Ship": "Sidewinder"
            }
        ]
        
        journal_file = self.create_test_journal_file("Journal.2024-01-15T100000.01.log", initial_events)
        
        # Mock configuration to use our test directory
        with patch('src.utils.config.EliteConfig') as mock_config:
            mock_config_instance = Mock()
            mock_config_instance.journal_path = self.journal_path
            mock_config_instance.validate_paths.return_value = True
            mock_config.return_value = mock_config_instance
            
            # Create monitor with event callback to store events
            monitor = JournalMonitor()
            
            # Set up callback to integrate with data store
            def event_callback(event_data):
                processed_event = self.event_processor.process_event(event_data)
                self.data_store.store_event(processed_event)
            
            monitor.set_event_callback(event_callback)
            
            # Start monitoring in background
            async def run_monitoring_test():
                # Start monitoring
                await monitor.start()
                
                # Give monitor time to initialize
                await asyncio.sleep(0.1)
                
                # Add new event to journal file
                new_event = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "event": "FSDJump",
                    "StarSystem": "Alpha Centauri",
                    "StarPos": [1.0, 2.0, 3.0]
                }
                
                with open(journal_file, 'a') as f:
                    f.write(json.dumps(new_event) + '\n')
                    f.flush()
                
                # Give monitor time to process the new event
                await asyncio.sleep(0.2)
                
                # Stop monitoring
                await monitor.stop()
                
                # Verify events were captured and stored
                stored_events = self.data_store.query_events()
                assert len(stored_events) >= 1  # Should have at least the new event
                
                # Check that FSD jump event was processed
                fsd_events = self.data_store.get_events_by_type("FSDJump")
                assert len(fsd_events) >= 1
                
                # Verify game state was updated
                game_state = self.data_store.get_game_state()
                assert game_state.current_system == "Alpha Centauri"
                assert game_state.supercruise == True
            
            # Run the async test
            asyncio.run(run_monitoring_test())
    
    def test_performance_integration_large_journal(self):
        """Test performance with large journal files and data store."""
        # Create a large journal file with many events
        large_events = []
        base_time = datetime.utcnow()
        
        for i in range(500):  # Create 500 events
            event_time = base_time - timedelta(minutes=1000-i*2)  # Events over time
            
            if i % 10 == 0:
                event = {
                    "timestamp": event_time.isoformat() + "Z",
                    "event": "FSDJump",
                    "StarSystem": f"System{i}",
                    "StarPos": [float(i), float(i+1), float(i+2)]
                }
            elif i % 7 == 0:
                event = {
                    "timestamp": event_time.isoformat() + "Z",
                    "event": "Docked",
                    "StationName": f"Station{i}",
                    "StationType": "Coriolis"
                }
            else:
                event = {
                    "timestamp": event_time.isoformat() + "Z",
                    "event": "MaterialCollected",
                    "Name": f"Material{i % 20}",
                    "Count": 1
                }
            
            large_events.append(event)
        
        journal_file = self.create_test_journal_file("Journal.large.log", large_events)
        
        # Process all events and measure performance
        start_time = time.time()
        
        with open(journal_file, 'r') as f:
            for line in f:
                if line.strip():
                    raw_event = json.loads(line.strip())
                    processed_event = self.event_processor.process_event(raw_event)
                    self.data_store.store_event(processed_event)
        
        processing_time = time.time() - start_time
        
        # Verify performance requirements
        assert processing_time < 5.0  # Should process 500 events in under 5 seconds
        
        # Verify data store handled the load correctly
        stored_events = self.data_store.query_events()
        assert len(stored_events) <= 100  # Respects max_events limit
        
        # Verify statistics are accurate
        stats = self.data_store.get_statistics()
        assert stats['total_processed'] == 500
        assert stats['total_events'] <= 100
        
        # Test querying performance
        query_start = time.time()
        fsd_events = self.data_store.get_events_by_type("FSDJump")
        query_time = time.time() - query_start
        
        assert query_time < 0.1  # Queries should be very fast
        assert len(fsd_events) > 0  # Should have some FSD jump events
    
    def test_data_store_filtering_with_real_events(self):
        """Test data store filtering with realistic Elite Dangerous events."""
        # Create diverse realistic events
        base_time = datetime.utcnow()
        test_events = [
            # Exploration events
            {
                "timestamp": (base_time - timedelta(hours=2)).isoformat() + "Z",
                "event": "FSSDiscoveryScan",
                "SystemName": "HIP 22460",
                "BodyCount": 15
            },
            {
                "timestamp": (base_time - timedelta(hours=1, minutes=30)).isoformat() + "Z",
                "event": "Scan",
                "ScanType": "AutoScan",
                "BodyName": "HIP 22460 B",
                "StarType": "K"
            },
            # Trading events
            {
                "timestamp": (base_time - timedelta(hours=1)).isoformat() + "Z",
                "event": "MarketBuy",
                "Type": "palladium",
                "Count": 10,
                "BuyPrice": 13456,
                "TotalCost": 134560
            },
            {
                "timestamp": (base_time - timedelta(minutes=30)).isoformat() + "Z",
                "event": "MarketSell",
                "Type": "palladium", 
                "Count": 10,
                "SellPrice": 14200,
                "TotalSale": 142000
            },
            # Combat events
            {
                "timestamp": (base_time - timedelta(minutes=15)).isoformat() + "Z",
                "event": "Bounty",
                "Target": "federation_dropship_mkii",
                "VictimFaction": "Crimson State Group",
                "TotalReward": 124680
            },
            # Recent navigation
            {
                "timestamp": (base_time - timedelta(minutes=5)).isoformat() + "Z",
                "event": "FSDJump",
                "StarSystem": "Sol",
                "StarPos": [0.0, 0.0, 0.0]
            }
        ]
        
        journal_file = self.create_test_journal_file("Journal.realistic.log", test_events)
        
        # Process events
        with open(journal_file, 'r') as f:
            for line in f:
                if line.strip():
                    raw_event = json.loads(line.strip())
                    processed_event = self.event_processor.process_event(raw_event)
                    self.data_store.store_event(processed_event)
        
        # Test time-based filtering
        recent_events = self.data_store.get_recent_events(minutes=45)
        assert len(recent_events) == 3  # Last 3 events within 45 minutes
        
        # Test category filtering  
        from src.journal.events import EventCategory
        
        exploration_filter = EventFilter(categories={EventCategory.EXPLORATION})
        exploration_events = self.data_store.query_events(exploration_filter)
        assert len(exploration_events) == 2  # FSSDiscoveryScan and Scan
        
        trading_filter = EventFilter(categories={EventCategory.TRADING})
        trading_events = self.data_store.query_events(trading_filter)
        assert len(trading_events) == 2  # MarketBuy and MarketSell
        
        # Test system filtering
        sol_filter = EventFilter(system_names={"Sol"})
        sol_events = self.data_store.query_events(sol_filter)
        assert len(sol_events) == 1  # Only the FSDJump to Sol
        
        # Test time range filtering
        last_hour_filter = EventFilter(
            start_time=base_time - timedelta(hours=1),
            end_time=base_time
        )
        last_hour_events = self.data_store.query_events(last_hour_filter)
        assert len(last_hour_events) == 4  # Events in the last hour
    
    def test_global_data_store_integration(self):
        """Test integration with global data store singleton."""
        # Use global data store
        global_store = get_data_store()
        
        # Create test events
        test_events = [
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": "LoadGame",
                "Commander": "TestCMDR"
            },
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": "FSDJump",
                "StarSystem": "Test System"
            }
        ]
        
        # Process events through global store
        for event_data in test_events:
            processed_event = self.event_processor.process_event(event_data)
            global_store.store_event(processed_event)
        
        # Verify events are stored in global store
        events = global_store.query_events()
        assert len(events) == 2
        
        # Test that same instance is returned
        another_store = get_data_store()
        assert another_store is global_store
        
        # Verify events are still there
        events2 = another_store.query_events()
        assert len(events2) == 2
        
        # Test resetting global store
        reset_data_store()
        new_store = get_data_store()
        assert new_store is not global_store
        assert len(new_store.query_events()) == 0
    
    def test_memory_management_integration(self):
        """Test memory management with continuous event processing."""
        # Create data store with small max_events for testing
        small_store = DataStore(max_events=10, cleanup_interval=1)
        
        # Generate events continuously
        for i in range(50):  # Generate more than max_events
            event_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": "TestEvent",
                "Data": f"Event{i}"
            }
            
            processed_event = self.event_processor.process_event(event_data)
            small_store.store_event(processed_event)
            
            # Brief pause to allow cleanup if needed
            if i % 10 == 0:
                time.sleep(0.01)
        
        # Verify memory management worked
        events = small_store.query_events()
        assert len(events) <= 10  # Should not exceed max_events
        
        # Verify newest events are kept
        event_data_values = [e.raw_data.get('Data') for e in events]
        assert "Event49" in event_data_values  # Latest event should be kept
        assert "Event0" not in event_data_values  # Oldest should be removed
        
        # Verify statistics are accurate
        stats = small_store.get_statistics()
        assert stats['total_processed'] == 50
        assert stats['total_events'] <= 10
    
    def test_error_handling_integration(self):
        """Test error handling in the integrated system."""
        # Test with malformed journal events
        malformed_events = [
            '{"timestamp": "invalid_timestamp", "event": "TestEvent"}',
            '{"event": "MissingTimestamp"}',
            '{"timestamp": "2024-01-15T10:00:00Z"}',  # Missing event field
            'invalid json',
            '{"timestamp": "2024-01-15T10:00:00Z", "event": "ValidEvent"}'  # This should work
        ]
        
        journal_file = self.journal_path / "Journal.malformed.log"
        with open(journal_file, 'w') as f:
            for event in malformed_events:
                f.write(event + '\n')
        
        # Process events with error handling
        successful_events = 0
        
        with open(journal_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        raw_event = json.loads(line.strip())
                        processed_event = self.event_processor.process_event(raw_event)
                        self.data_store.store_event(processed_event)
                        successful_events += 1
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Expected for malformed events
                        continue
        
        # Verify only valid events were processed
        stored_events = self.data_store.query_events()
        assert len(stored_events) == successful_events
        assert successful_events >= 1  # At least the valid event should work
        
        # Verify system remains stable
        stats = self.data_store.get_statistics()
        assert stats['total_processed'] == successful_events
        assert stats['total_events'] == successful_events


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
