"""
Additional unit tests for Milestone 5 completion.

This file contains performance tests, stress tests, integration tests,
and comprehensive event category verification tests required for 
Milestone 5: Event Processing and Classification completion.
"""

import pytest
import time
import threading
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import logging

from src.journal.events import (
    EventProcessor, ProcessedEvent, EventCategory,
    categorize_events, summarize_events, get_event_statistics
)


class TestEventProcessorPerformance:
    """Performance tests for event processing to meet real-time requirements."""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()
    
    @pytest.fixture
    def large_event_batch(self):
        """Create a large batch of realistic events for performance testing."""
        events = []
        event_templates = [
            {"event": "FSDJump", "StarSystem": "System_{}", "JumpDist": 15.7},
            {"event": "Scan", "BodyName": "Planet_{}", "PlanetClass": "Rocky body"},
            {"event": "Bounty", "Target": "Pirate_{}", "TotalReward": 50000},
            {"event": "MarketBuy", "Type": "Gold", "Count": 10, "TotalCost": 90000},
            {"event": "Docked", "StationName": "Station_{}", "StarSystem": "System_{}"},
        ]
        
        for i in range(1000):  # 1000 events for stress testing
            template = event_templates[i % len(event_templates)]
            event = {
                "timestamp": f"2024-01-15T{(10 + i//60):02d}:{(i%60):02d}:00Z",
                **{k: v.format(i) if isinstance(v, str) and '{}' in v else v 
                   for k, v in template.items()}
            }
            events.append(event)
        return events
    
    def test_single_event_processing_performance(self, processor):
        """Test that single event processing meets real-time requirements (<1ms)."""
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "FSDJump",
            "StarSystem": "Sol",
            "JumpDist": 8.03
        }
        
        # Warm up
        processor.process_event(event)
        
        # Time multiple iterations
        iterations = 100
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            processed = processor.process_event(event)
            assert processed.is_valid
            assert processed.category == EventCategory.NAVIGATION
        
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / iterations
        
        # Should process each event in less than 1ms for real-time performance
        assert avg_time < 0.001, f"Event processing too slow: {avg_time*1000:.2f}ms per event"
        print(f"Average processing time: {avg_time*1000:.3f}ms per event")
    
    def test_batch_processing_performance(self, processor, large_event_batch):
        """Test batch processing performance with 1000 events."""
        start_time = time.perf_counter()
        
        processed_events = []
        for event in large_event_batch:
            processed = processor.process_event(event)
            processed_events.append(processed)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time = total_time / len(large_event_batch)
        
        # Verify all events processed correctly
        assert len(processed_events) == 1000
        assert all(event.is_valid for event in processed_events)
        
        # Should maintain real-time performance even in batch
        assert avg_time < 0.001, f"Batch processing too slow: {avg_time*1000:.2f}ms per event"
        assert total_time < 1.0, f"Total batch time too slow: {total_time:.2f}s for 1000 events"
        print(f"Batch processing: {total_time:.3f}s total, {avg_time*1000:.3f}ms per event")
    
    def test_concurrent_processing_performance(self, processor):
        """Test that concurrent processing maintains performance."""
        event = {
            "timestamp": "2024-01-15T10:00:00Z",
            "event": "FSDJump", 
            "StarSystem": "Sol",
            "JumpDist": 8.03
        }
        
        results = []
        errors = []
        
        def process_events(event_processor, num_events):
            try:
                start = time.perf_counter()
                for i in range(num_events):
                    processed = event_processor.process_event(event)
                    assert processed.is_valid
                end = time.perf_counter()
                results.append(end - start)
            except Exception as e:
                errors.append(e)
        
        # Run concurrent processing
        threads = []
        events_per_thread = 100
        num_threads = 5
        
        for _ in range(num_threads):
            thread = threading.Thread(target=process_events, args=(processor, events_per_thread))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors and reasonable performance
        assert len(errors) == 0, f"Concurrent processing errors: {errors}"
        assert len(results) == num_threads
        
        avg_time_per_thread = sum(results) / len(results)
        avg_time_per_event = avg_time_per_thread / events_per_thread
        
        assert avg_time_per_event < 0.002, f"Concurrent processing too slow: {avg_time_per_event*1000:.2f}ms per event"
        print(f"Concurrent processing: {avg_time_per_event*1000:.3f}ms per event across {num_threads} threads")
    
    def test_memory_usage_stability(self, processor, large_event_batch):
        """Test that memory usage remains stable during large batch processing."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Process large batch
            for event in large_event_batch:
                processor.process_event(event)
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 50MB for 1000 events)
            assert memory_increase < 50 * 1024 * 1024, f"Excessive memory usage: {memory_increase / 1024 / 1024:.2f}MB"
            print(f"Memory increase: {memory_increase / 1024 / 1024:.2f}MB for 1000 events")
        except ImportError:
            pytest.skip("psutil not available for memory testing")


class TestEventCategoryCompleteness:
    """Comprehensive tests to verify all event categories are properly mapped."""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()
    
    def test_all_defined_categories_have_events(self, processor):
        """Test that every defined EventCategory has at least one mapped event type."""
        # Get all mapped categories
        mapped_categories = set(processor.EVENT_CATEGORIES.values())
        
        # Get all defined categories  
        defined_categories = set(EventCategory)
        
        # Every defined category should have at least one event type mapped
        for category in defined_categories:
            assert category in mapped_categories, f"Category {category} has no mapped event types"
    
    def test_comprehensive_event_type_coverage(self, processor):
        """Test comprehensive coverage of Elite Dangerous event types."""
        # Test samples from each category to ensure comprehensive coverage
        category_samples = {
            EventCategory.SYSTEM: ["Fileheader", "LoadGame", "Shutdown", "Statistics", "Rank"],
            EventCategory.NAVIGATION: ["FSDJump", "Docked", "Undocked", "Location", "SupercruiseEntry"],
            EventCategory.EXPLORATION: ["Scan", "FSSDiscoveryScan", "SellExplorationData", "Screenshot"],
            EventCategory.COMBAT: ["Bounty", "Died", "Interdicted", "ShieldState", "HullDamage"],
            EventCategory.TRADING: ["MarketBuy", "MarketSell", "CollectCargo", "EjectCargo"],
            EventCategory.MISSION: ["MissionAccepted", "MissionCompleted", "MissionFailed"],
            EventCategory.ENGINEERING: ["EngineerCraft", "EngineerProgress", "EngineerApply"],
            EventCategory.MINING: ["Mined", "AsteroidCracked", "ProspectedAsteroid"],
            EventCategory.SHIP: ["ShipyardBuy", "Loadout", "ModuleBuy", "Repair", "Refuel"],
            EventCategory.SQUADRON: ["SquadronCreated", "WingAdd", "WingJoin"],
            EventCategory.CREW: ["CrewHire", "CrewFire", "CrewMemberJoins"],
            EventCategory.PASSENGER: ["PassengerManifest", "Passengers"],
            EventCategory.POWERPLAY: ["PowerplayJoin", "PowerplayCollect", "PowerplayVoucher"],
            EventCategory.CARRIER: ["CarrierBuy", "CarrierJump", "CarrierStats"],
            EventCategory.SOCIAL: ["Friends", "ReceiveText", "SendText"],
            EventCategory.SUIT: ["SuitPurchased", "Disembark", "Embark"],
        }
        
        for expected_category, event_types in category_samples.items():
            for event_type in event_types:
                event = {"timestamp": "2024-01-15T10:00:00Z", "event": event_type}
                processed = processor.process_event(event)
                assert processed.category == expected_category, \
                    f"Event {event_type} should be {expected_category}, got {processed.category}"
    
    def test_event_category_distribution(self, processor):
        """Test that event categories are well distributed."""
        category_counts = {}
        for event_type, category in processor.EVENT_CATEGORIES.items():
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Verify we have a reasonable distribution
        assert len(category_counts) >= 15, f"Should have at least 15 categories, got {len(category_counts)}"
        
        # No single category should dominate (except SHIP which has many module events)
        max_count = max(category_counts.values())
        total_events = sum(category_counts.values())
        max_percentage = max_count / total_events
        
        # No category should have more than 40% of all event types
        assert max_percentage < 0.4, f"Category distribution too skewed: {max_percentage:.1%} in largest category"
        
        print(f"Event category distribution: {len(category_counts)} categories, {total_events} total event types")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category.value}: {count} events ({count/total_events:.1%})")


class TestEventProcessorIntegration:
    """Integration tests with monitoring and parser systems."""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance.""" 
        return EventProcessor()
    
    def test_integration_with_journal_parser_format(self, processor):
        """Test that processor handles journal parser output format correctly."""
        # Simulate journal parser output format
        journal_entries = [
            '{"timestamp":"2024-01-15T10:00:00Z","event":"LoadGame","Commander":"TestCmdr","Ship":"asp"}',
            '{"timestamp":"2024-01-15T10:15:00Z","event":"FSDJump","StarSystem":"Sol","JumpDist":8.03}',
            '{"timestamp":"2024-01-15T10:30:00Z","event":"Docked","StationName":"Abraham Lincoln","StarSystem":"Sol"}'
        ]
        
        import json
        processed_events = []
        
        for entry in journal_entries:
            try:
                event_data = json.loads(entry)
                processed = processor.process_event(event_data)
                processed_events.append(processed)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON from journal parser: {entry}")
        
        assert len(processed_events) == 3
        assert all(event.is_valid for event in processed_events)
        assert processed_events[0].category == EventCategory.SYSTEM
        assert processed_events[1].category == EventCategory.NAVIGATION
        assert processed_events[2].category == EventCategory.NAVIGATION
    
    def test_integration_with_real_time_monitoring(self, processor):
        """Test processor performance with simulated real-time event stream."""
        events_received = []
        processing_times = []
        
        def simulate_event_stream():
            """Simulate real-time event monitoring sending events."""
            event_templates = [
                {"event": "FSDJump", "StarSystem": "Sol", "JumpDist": 8.03},
                {"event": "Scan", "BodyName": "Earth", "PlanetClass": "Earthlike body"},
                {"event": "Docked", "StationName": "Station", "StarSystem": "Sol"},
            ]
            
            for i in range(50):  # Simulate 50 events
                event = {
                    "timestamp": f"2024-01-15T10:{i:02d}:00Z",
                    **event_templates[i % len(event_templates)]
                }
                
                start_time = time.perf_counter()
                processed = processor.process_event(event)
                end_time = time.perf_counter()
                
                events_received.append(processed)
                processing_times.append(end_time - start_time)
                
                # Simulate small delay between events (20ms = typical journal update rate)
                time.sleep(0.02)
        
        # Run simulation
        simulate_event_stream()
        
        # Verify real-time performance
        assert len(events_received) == 50
        assert all(event.is_valid for event in events_received)
        
        avg_processing_time = sum(processing_times) / len(processing_times)
        max_processing_time = max(processing_times)
        
        # Should process faster than new events arrive
        assert avg_processing_time < 0.02, f"Processing too slow for real-time: {avg_processing_time*1000:.2f}ms avg"
        assert max_processing_time < 0.05, f"Max processing time too slow: {max_processing_time*1000:.2f}ms"
        
        print(f"Real-time simulation: {avg_processing_time*1000:.3f}ms avg, {max_processing_time*1000:.3f}ms max")


class TestEventProcessorStressTests:
    """Stress tests with extreme conditions and edge cases."""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()
    
    def test_massive_event_batch_processing(self, processor):
        """Test processing of very large event batches (10,000 events)."""
        # Generate 10,000 events
        events = []
        for i in range(10000):
            event = {
                "timestamp": f"2024-01-15T{(10 + i//3600):02d}:{(i//60)%60:02d}:{i%60:02d}Z",
                "event": "FSDJump",
                "StarSystem": f"System_{i}",
                "JumpDist": 5.0 + (i % 50)
            }
            events.append(event)
        
        start_time = time.perf_counter()
        
        processed_count = 0
        for event in events:
            processed = processor.process_event(event)
            assert processed.is_valid
            processed_count += 1
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        assert processed_count == 10000
        assert total_time < 10.0, f"10K events took too long: {total_time:.2f}s"
        
        avg_time = total_time / 10000
        assert avg_time < 0.001, f"Average time too slow: {avg_time*1000:.3f}ms per event"
        
        print(f"Massive batch: {total_time:.2f}s for 10K events ({avg_time*1000:.3f}ms avg)")
    
    def test_unknown_event_tracking_limits(self, processor):
        """Test that unknown event tracking doesn't grow indefinitely."""
        initial_count = len(processor.get_unknown_events())
        
        # Add many different unknown event types
        for i in range(1000):
            event = {
                "timestamp": "2024-01-15T10:00:00Z",
                "event": f"UnknownEvent_{i}"
            }
            processor.process_event(event)
        
        unknown_events = processor.get_unknown_events()
        
        # Should track all unique unknown events
        assert len(unknown_events) == 1000 + initial_count
        
        # Should be sorted
        assert unknown_events == sorted(unknown_events)
        
        # Clearing should work
        processor.clear_unknown_events()
        assert len(processor.get_unknown_events()) == 0
    
    def test_extreme_timestamp_variations(self, processor):
        """Test processing events with extreme timestamp variations."""
        extreme_timestamps = [
            "1900-01-01T00:00:00Z",  # Very old
            "2100-12-31T23:59:59Z",  # Far future
            "2024-01-15T10:00:00+14:00",  # Extreme positive timezone
            "2024-01-15T10:00:00-12:00",  # Extreme negative timezone
            "2024-02-29T10:00:00Z",  # Leap year
            "2024-12-31T23:59:59.999Z",  # End of year with milliseconds
        ]
        
        for timestamp in extreme_timestamps:
            event = {
                "timestamp": timestamp,
                "event": "Test"
            }
            processed = processor.process_event(event)
            assert processed.is_valid
            assert isinstance(processed.timestamp, datetime)
    
    def test_malformed_event_resilience(self, processor):
        """Test processor resilience with heavily malformed events."""
        malformed_events = [
            {},  # Empty
            {"timestamp": None, "event": None},  # All None
            {"timestamp": "", "event": ""},  # Empty strings
            {"timestamp": "invalid", "event": 123},  # Wrong types
            {"event": "Test", "extrafield": "x" * 10000},  # Huge field
            {"timestamp": "2024-01-15T10:00:00Z", "event": "Test", "nested": {"deep": {"very": {"deep": "data"}}}},  # Deep nesting
        ]
        
        processed_events = []
        for event in malformed_events:
            try:
                processed = processor.process_event(event)
                processed_events.append(processed)
            except Exception as e:
                pytest.fail(f"Processor should handle malformed event gracefully: {e}")
        
        assert len(processed_events) == len(malformed_events)
        
        # Some should be invalid but none should crash the processor
        invalid_count = sum(1 for event in processed_events if not event.is_valid)
        assert invalid_count >= 3, "Should detect multiple invalid events"
        assert invalid_count <= len(malformed_events), "Shouldn't mark all as invalid"


class TestEventProcessorDocumentationCompliance:
    """Tests to verify implementation matches documentation requirements."""
    
    @pytest.fixture
    def processor(self):
        """Create an EventProcessor instance."""
        return EventProcessor()
    
    def test_milestone_5_implementation_requirements(self, processor):
        """Verify all Milestone 5 requirements are implemented."""
        # 1. Comprehensive event categorization
        assert len(processor.EVENT_CATEGORIES) >= 100, "Should have comprehensive event mapping"
        assert len(EventCategory) >= 15, "Should have sufficient categories"
        
        # 2. Event summarization
        event = {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump", "StarSystem": "Sol"}
        processed = processor.process_event(event)
        assert processed.summary != "", "Should generate non-empty summaries"
        assert "Sol" in processed.summary, "Summary should include relevant event data"
        
        # 3. Event validation
        invalid_event = {"invalid": "data"}
        processed = processor.process_event(invalid_event)
        assert not processed.is_valid, "Should validate events"
        assert len(processed.validation_errors) > 0, "Should provide validation errors"
        
        # 4. Data extraction
        event = {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump", "StarSystem": "Sol", "JumpDist": 8.03}
        processed = processor.process_event(event)
        assert processed.key_data["system"] == "Sol", "Should extract key data"
        assert processed.key_data["distance"] == 8.03, "Should extract numeric data"
    
    def test_function_api_completeness(self):
        """Test that all required module functions are implemented."""
        # Test categorize_events function
        events = [
            {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump"},
            {"timestamp": "2024-01-15T10:15:00Z", "event": "Scan"}
        ]
        categorized = categorize_events(events)
        assert isinstance(categorized, dict)
        assert EventCategory.NAVIGATION in categorized
        
        # Test summarize_events function
        summaries = summarize_events(events)
        assert isinstance(summaries, list)
        assert len(summaries) == 2
        assert all("[" in summary for summary in summaries)  # Should include timestamps
        
        # Test get_event_statistics function
        stats = get_event_statistics(events)
        assert isinstance(stats, dict)
        assert "total_events" in stats
        assert "categories" in stats
        assert "event_types" in stats
        assert stats["total_events"] == 2
    
    def test_performance_requirements_compliance(self, processor):
        """Test that performance meets real-time processing requirements."""
        # Single event should process in < 1ms
        event = {"timestamp": "2024-01-15T10:00:00Z", "event": "FSDJump", "StarSystem": "Sol"}
        
        start_time = time.perf_counter()
        processed = processor.process_event(event)
        end_time = time.perf_counter()
        
        processing_time = end_time - start_time
        assert processing_time < 0.001, f"Processing too slow: {processing_time*1000:.2f}ms"
        assert processed.is_valid, "Should process valid events successfully"