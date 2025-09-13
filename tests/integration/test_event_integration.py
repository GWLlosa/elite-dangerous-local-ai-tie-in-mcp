"""
Integration tests for journal event processing with parser and monitor.

Tests the complete pipeline from journal file reading through event
categorization and summarization.
"""

import pytest
import json
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from src.journal import (
    JournalParser,
    JournalMonitor,
    EventProcessor,
    EventCategory,
    categorize_events,
    summarize_events,
    get_event_statistics
)


class TestJournalEventIntegration:
    """Test integration between journal parsing and event processing."""
    
    @pytest.fixture
    def sample_journal_content(self):
        """Create sample journal file content."""
        events = [
            {"timestamp": "2024-01-15T09:00:00Z", "event": "LoadGame", "Commander": "TestCmdr", "Ship": "AspExplorer"},
            {"timestamp": "2024-01-15T09:05:00Z", "event": "Location", "StarSystem": "Sol", "Docked": False},
            {"timestamp": "2024-01-15T09:10:00Z", "event": "FSDJump", "StarSystem": "Alpha Centauri", "JumpDist": 4.37},
            {"timestamp": "2024-01-15T09:15:00Z", "event": "Scan", "BodyName": "Proxima Centauri b", "PlanetClass": "Rocky body"},
            {"timestamp": "2024-01-15T09:20:00Z", "event": "Docked", "StationName": "Hutton Orbital", "StarSystem": "Alpha Centauri"},
            {"timestamp": "2024-01-15T09:25:00Z", "event": "MarketBuy", "Type": "Gold", "Count": 10, "BuyPrice": 9000, "TotalCost": 90000},
            {"timestamp": "2024-01-15T09:30:00Z", "event": "MissionAccepted", "Name": "Mission_Delivery", "Faction": "Federation", "Reward": 100000}
        ]
        return "\n".join(json.dumps(event) for event in events)
    
    @pytest.fixture
    def temp_journal_file(self, tmp_path, sample_journal_content):
        """Create a temporary journal file."""
        journal_file = tmp_path / "Journal.240115090000.01.log"
        journal_file.write_text(sample_journal_content)
        return journal_file
    
    def test_parse_and_process_events(self, tmp_path, temp_journal_file):
        """Test parsing journal file and processing events."""
        # Parse journal file
        parser = JournalParser(str(tmp_path))
        entries, _ = parser.read_journal_file(temp_journal_file)
        
        # Verify we got all entries
        assert len(entries) == 7
        
        # Process events
        processor = EventProcessor()
        processed_events = []
        
        for entry in entries:
            processed = processor.process_event(entry)
            processed_events.append(processed)
            
            # Verify each event is valid
            assert processed.is_valid
            assert processed.event_type == entry["event"]
        
        # Verify categorization
        assert processed_events[0].category == EventCategory.SYSTEM  # LoadGame
        assert processed_events[1].category == EventCategory.NAVIGATION  # Location
        assert processed_events[2].category == EventCategory.NAVIGATION  # FSDJump
        assert processed_events[3].category == EventCategory.EXPLORATION  # Scan
        assert processed_events[4].category == EventCategory.NAVIGATION  # Docked
        assert processed_events[5].category == EventCategory.TRADING  # MarketBuy
        assert processed_events[6].category == EventCategory.MISSION  # MissionAccepted
        
        # Verify summaries
        assert "loaded game" in processed_events[0].summary.lower()
        assert "Alpha Centauri" in processed_events[2].summary
        assert "Proxima Centauri b" in processed_events[3].summary
        assert "Hutton Orbital" in processed_events[4].summary
        assert "Gold" in processed_events[5].summary
        assert "Federation" in processed_events[6].summary
    
    def test_categorize_parsed_events(self, tmp_path, temp_journal_file):
        """Test categorizing events directly from parsed journal."""
        parser = JournalParser(str(tmp_path))
        entries, _ = parser.read_journal_file(temp_journal_file)
        
        # Categorize all events
        categorized = categorize_events(entries)
        
        # Verify categories
        assert len(categorized[EventCategory.SYSTEM]) == 1
        assert len(categorized[EventCategory.NAVIGATION]) == 3  # Location, FSDJump, Docked
        assert len(categorized[EventCategory.EXPLORATION]) == 1
        assert len(categorized[EventCategory.TRADING]) == 1
        assert len(categorized[EventCategory.MISSION]) == 1
        
        # Verify correct events in each category
        assert categorized[EventCategory.SYSTEM][0].event_type == "LoadGame"
        nav_types = [e.event_type for e in categorized[EventCategory.NAVIGATION]]
        assert set(nav_types) == {"Location", "FSDJump", "Docked"}
    
    def test_summarize_parsed_events(self, tmp_path, temp_journal_file):
        """Test generating summaries from parsed events."""
        parser = JournalParser(str(tmp_path))
        entries, _ = parser.read_journal_file(temp_journal_file)
        
        # Generate summaries
        summaries = summarize_events(entries, max_summaries=5)
        
        assert len(summaries) == 5
        
        # Check summaries contain expected content
        assert any("loaded game" in s.lower() for s in summaries)
        assert any("Alpha Centauri" in s for s in summaries)
        assert any("Proxima Centauri b" in s for s in summaries)
    
    def test_event_statistics_from_parsed(self, tmp_path, temp_journal_file):
        """Test generating statistics from parsed journal."""
        parser = JournalParser(str(tmp_path))
        entries, _ = parser.read_journal_file(temp_journal_file)
        
        stats = get_event_statistics(entries)
        
        # Verify statistics
        assert stats["total_events"] == 7
        assert stats["invalid_events"] == 0
        assert stats["categories"]["navigation"] == 3
        assert stats["categories"]["system"] == 1
        assert stats["event_types"]["FSDJump"] == 1
        assert stats["event_types"]["MissionAccepted"] == 1
        
        # Verify time range
        assert "2024-01-15T09:00:00" in stats["time_range"]["start"]
        assert "2024-01-15T09:30:00" in stats["time_range"]["end"]


class TestMonitorEventIntegration:
    """Test integration between journal monitoring and event processing."""
    
    @pytest.fixture
    def mock_event_processor(self):
        """Create a mock event processor to track calls."""
        processor = Mock(spec=EventProcessor)
        processor.process_event.return_value = Mock(
            is_valid=True,
            category=EventCategory.NAVIGATION,
            summary="Test event",
            event_type="TestEvent"
        )
        return processor
    
    @pytest.mark.asyncio
    async def test_monitor_with_event_processing(self, tmp_path):
        """Test monitoring with real-time event processing."""
        events_received = []
        processed_events = []
        processor = EventProcessor()
        
        async def handle_events(data, event_type):
            """Handle incoming events and process them."""
            events_received.append((data, event_type))
            
            if event_type == "journal_entry":
                for entry in data:
                    processed = processor.process_event(entry)
                    processed_events.append(processed)
        
        # Create monitor
        monitor = JournalMonitor(str(tmp_path), handle_events)
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor.start_monitoring())
        
        # Give monitor time to start
        await asyncio.sleep(0.1)
        
        # Create a journal file with events
        journal_file = tmp_path / "Journal.240115100000.01.log"
        events = [
            {"timestamp": "2024-01-15T10:00:00Z", "event": "LoadGame", "Commander": "TestCmdr"},
            {"timestamp": "2024-01-15T10:01:00Z", "event": "FSDJump", "StarSystem": "Sol", "JumpDist": 0}
        ]
        
        # Write events one by one
        with open(journal_file, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
                f.flush()
                await asyncio.sleep(0.05)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        monitor_task.cancel()
        
        # Verify events were received and processed
        assert len(events_received) > 0
        assert len(processed_events) > 0
        
        # Verify correct categorization
        for processed in processed_events:
            assert processed.is_valid
            if processed.event_type == "LoadGame":
                assert processed.category == EventCategory.SYSTEM
            elif processed.event_type == "FSDJump":
                assert processed.category == EventCategory.NAVIGATION
    
    @pytest.mark.asyncio
    async def test_monitor_status_json_processing(self, tmp_path):
        """Test Status.json monitoring with event processing."""
        status_updates = []
        
        async def handle_events(data, event_type):
            """Handle Status.json updates."""
            if event_type == "status_update":
                # Process as a special status event
                processor = EventProcessor()
                # Status.json doesn't have standard event format, so we wrap it
                status_event = {
                    "timestamp": datetime.now().isoformat() + "Z",
                    "event": "StatusUpdate",
                    **data
                }
                processed = processor.process_event(status_event)
                status_updates.append(processed)
        
        # Create monitor
        monitor = JournalMonitor(str(tmp_path), handle_events)
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor.start_monitoring())
        await asyncio.sleep(0.1)
        
        # Create Status.json
        status_file = tmp_path / "Status.json"
        status_data = {
            "Flags": 16777216,
            "Pips": [4, 8, 0],
            "FireGroup": 0,
            "GuiFocus": 0
        }
        
        # Write status update
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        monitor_task.cancel()
        
        # Verify status was processed
        assert len(status_updates) > 0
        assert status_updates[0].event_type == "StatusUpdate"


class TestEventProcessingPipeline:
    """Test complete event processing pipeline from file to statistics."""
    
    def test_complete_pipeline(self, tmp_path):
        """Test complete pipeline from journal files to statistics."""
        # Create multiple journal files
        events_day1 = [
            {"timestamp": "2024-01-15T09:00:00Z", "event": "LoadGame", "Commander": "TestCmdr"},
            {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump", "StarSystem": "Sol", "JumpDist": 0},
            {"timestamp": "2024-01-15T11:00:00Z", "event": "Scan", "BodyName": "Earth"},
            {"timestamp": "2024-01-15T12:00:00Z", "event": "Shutdown"}
        ]
        
        events_day2 = [
            {"timestamp": "2024-01-16T09:00:00Z", "event": "LoadGame", "Commander": "TestCmdr"},
            {"timestamp": "2024-01-16T10:00:00Z", "event": "Bounty", "Target": "pirate", "TotalReward": 50000},
            {"timestamp": "2024-01-16T11:00:00Z", "event": "MarketSell", "Type": "Gold", "Count": 10, "TotalSale": 100000},
            {"timestamp": "2024-01-16T12:00:00Z", "event": "MissionCompleted", "Faction": "Federation", "Reward": 200000}
        ]
        
        # Write journal files
        journal1 = tmp_path / "Journal.240115090000.01.log"
        journal1.write_text("\n".join(json.dumps(e) for e in events_day1))
        
        journal2 = tmp_path / "Journal.240116090000.01.log"
        journal2.write_text("\n".join(json.dumps(e) for e in events_day2))
        
        # Parse all journal files
        parser = JournalParser(str(tmp_path))
        all_entries = []
        
        journal_files = parser.find_journal_files()
        assert len(journal_files) == 2
        
        for journal_file in journal_files:
            entries, _ = parser.read_journal_file(journal_file)
            all_entries.extend(entries)
        
        # Process and categorize all events
        categorized = categorize_events(all_entries)
        
        # Generate statistics
        stats = get_event_statistics(all_entries)
        
        # Verify complete pipeline results
        assert stats["total_events"] == 8
        assert stats["categories"]["system"] == 3  # 2 LoadGame + 1 Shutdown
        assert stats["categories"]["navigation"] == 1  # FSDJump
        assert stats["categories"]["exploration"] == 1  # Scan
        assert stats["categories"]["combat"] == 1  # Bounty
        assert stats["categories"]["trading"] == 1  # MarketSell
        assert stats["categories"]["mission"] == 1  # MissionCompleted
        
        # Verify event type counts
        assert stats["event_types"]["LoadGame"] == 2
        assert stats["event_types"]["Bounty"] == 1
        
        # Generate summaries
        summaries = summarize_events(all_entries, max_summaries=3)
        assert len(summaries) == 3
        
        # Verify we can track across multiple days
        time_range = stats["time_range"]
        assert "2024-01-15" in time_range["start"]
        assert "2024-01-16" in time_range["end"]
    
    def test_pipeline_with_invalid_events(self, tmp_path):
        """Test pipeline handles invalid events gracefully."""
        # Create journal with mixed valid/invalid events
        events = [
            {"timestamp": "2024-01-15T09:00:00Z", "event": "LoadGame", "Commander": "TestCmdr"},
            {"invalid": "data"},  # Missing required fields
            {"timestamp": "invalid", "event": "Test"},  # Invalid timestamp
            {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump", "StarSystem": "Sol"},
            {},  # Empty event
            {"timestamp": "2024-01-15T11:00:00Z", "event": "Shutdown"}
        ]
        
        journal = tmp_path / "Journal.240115090000.01.log"
        journal.write_text("\n".join(json.dumps(e) for e in events))
        
        # Parse and process
        parser = JournalParser(str(tmp_path))
        entries, _ = parser.read_journal_file(journal)
        
        # Process all events
        processor = EventProcessor()
        valid_count = 0
        invalid_count = 0
        
        for entry in entries:
            processed = processor.process_event(entry)
            if processed.is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        # Verify handling of invalid events
        assert valid_count == 3  # LoadGame, FSDJump, Shutdown
        assert invalid_count == 3  # The invalid entries
        
        # Verify statistics handle invalid events
        stats = get_event_statistics(entries)
        assert stats["total_events"] == 6
        assert stats["invalid_events"] == 3
    
    def test_pipeline_performance(self, tmp_path):
        """Test pipeline performance with large number of events."""
        # Create journal with many events
        events = []
        for i in range(1000):
            event_type = ["FSDJump", "Scan", "Docked", "MarketBuy", "Bounty"][i % 5]
            events.append({
                "timestamp": f"2024-01-15T{9 + (i // 60):02d}:{i % 60:02d}:00Z",
                "event": event_type,
                "StarSystem": f"System{i}",
                "BodyName": f"Body{i}",
                "StationName": f"Station{i}",
                "Type": f"Commodity{i}",
                "Target": f"Target{i}"
            })
        
        journal = tmp_path / "Journal.240115090000.01.log"
        journal.write_text("\n".join(json.dumps(e) for e in events))
        
        # Time the processing
        import time
        start_time = time.time()
        
        # Parse and process
        parser = JournalParser(str(tmp_path))
        entries, _ = parser.read_journal_file(journal)
        
        # Categorize all events
        categorized = categorize_events(entries)
        
        # Generate statistics
        stats = get_event_statistics(entries)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance and correctness
        assert len(entries) == 1000
        assert stats["total_events"] == 1000
        assert processing_time < 2.0  # Should process 1000 events in under 2 seconds
        
        # Verify categorization is correct
        assert stats["categories"]["navigation"] == 400  # FSDJump + Docked
        assert stats["categories"]["exploration"] == 200  # Scan
        assert stats["categories"]["trading"] == 200  # MarketBuy
        assert stats["categories"]["combat"] == 200  # Bounty
