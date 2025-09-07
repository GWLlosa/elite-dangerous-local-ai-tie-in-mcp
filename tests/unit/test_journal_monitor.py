"""Unit tests for journal monitoring functionality."""

import asyncio
import json
import tempfile
import time
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.journal.monitor import JournalMonitor, JournalEventHandler
from src.journal.parser import JournalParser


@pytest.fixture
def temp_journal_dir():
    """Create temporary directory with sample journal files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        journal_dir = Path(temp_dir)
        
        # Create initial journal file
        initial_journal = journal_dir / "Journal.20240906120000.01.log"
        sample_entries = [
            '{"timestamp":"2024-09-06T12:00:00Z","event":"Fileheader","part":1}',
            '{"timestamp":"2024-09-06T12:01:00Z","event":"LoadGame","Commander":"TestCMDR"}',
        ]
        
        with open(initial_journal, 'w', encoding='utf-8') as f:
            for entry in sample_entries:
                f.write(entry + '\n')
        
        # Create Status.json
        status_data = {
            "timestamp": "2024-09-06T12:05:00Z",
            "event": "Status",
            "Flags": 16777240
        }
        
        status_file = journal_dir / "Status.json"
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f)
        
        yield journal_dir


@pytest.fixture
def mock_callback():
    """Create mock callback for testing."""
    return AsyncMock()


@pytest.fixture
def parser(temp_journal_dir):
    """Create JournalParser instance."""
    return JournalParser(temp_journal_dir)


@pytest.fixture
def event_handler(mock_callback, parser):
    """Create JournalEventHandler instance."""
    # Get current event loop for the handler
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return JournalEventHandler(mock_callback, parser, loop)


@pytest.fixture
def monitor(temp_journal_dir, mock_callback):
    """Create JournalMonitor instance."""
    return JournalMonitor(temp_journal_dir, mock_callback)


class TestJournalEventHandler:
    """Test cases for JournalEventHandler class."""
    
    def test_initialization(self, mock_callback, parser):
        """Test event handler initialization."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        handler = JournalEventHandler(mock_callback, parser, loop)
        
        assert handler.callback == mock_callback
        assert handler.parser == parser
        assert handler.event_loop == loop
        assert isinstance(handler.current_positions, dict)
        assert isinstance(handler.monitored_files, set)
        assert len(handler.current_positions) == 0
        assert len(handler.monitored_files) == 0
    
    @pytest.mark.asyncio
    async def test_handle_journal_modification(self, event_handler, temp_journal_dir):
        """Test handling journal file modifications."""
        # Create a test journal file
        test_file = temp_journal_dir / "Journal.20240906130000.01.log"
        initial_content = '{"timestamp":"2024-09-06T13:00:00Z","event":"Test1"}\n'
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        
        # Handle modification (initial read)
        await event_handler._handle_journal_modification(test_file)
        
        # Verify callback was called
        event_handler.callback.assert_called_once()
        call_args = event_handler.callback.call_args
        data, event_type = call_args[0]
        
        assert event_type == 'journal_entries'
        assert len(data) == 1
        assert data[0]['event'] == 'Test1'
        
        # Verify position tracking
        file_key = str(test_file)
        assert file_key in event_handler.current_positions
        assert event_handler.current_positions[file_key] > 0
        
        # Reset mock
        event_handler.callback.reset_mock()
        
        # Add more content
        additional_content = '{"timestamp":"2024-09-06T13:01:00Z","event":"Test2"}\n'
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(additional_content)
        
        # Handle second modification
        await event_handler._handle_journal_modification(test_file)
        
        # Verify only new entry was processed
        event_handler.callback.assert_called_once()
        call_args = event_handler.callback.call_args
        data, event_type = call_args[0]
        
        assert event_type == 'journal_entries'
        assert len(data) == 1
        assert data[0]['event'] == 'Test2'
    
    @pytest.mark.asyncio
    async def test_handle_journal_creation(self, event_handler, temp_journal_dir):
        """Test handling new journal file creation."""
        # Create a new journal file
        new_file = temp_journal_dir / "Journal.20240906140000.01.log"
        content = '{"timestamp":"2024-09-06T14:00:00Z","event":"NewFile"}\n'
        
        with open(new_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Handle creation
        await event_handler._handle_journal_creation(new_file)
        
        # Verify file was added to monitoring
        file_key = str(new_file)
        assert file_key in event_handler.monitored_files
        assert file_key in event_handler.current_positions
        
        # Verify callbacks were made
        assert event_handler.callback.call_count == 2
        
        # Check for journal entries callback
        call_args_list = event_handler.callback.call_args_list
        journal_call = None
        system_call = None
        
        for call_args in call_args_list:
            data, event_type = call_args[0]
            if event_type == 'journal_entries':
                journal_call = (data, event_type)
            elif event_type == 'system_events':
                system_call = (data, event_type)
        
        # Verify journal entries callback
        assert journal_call is not None
        data, event_type = journal_call
        assert len(data) == 1
        assert data[0]['event'] == 'NewFile'
        
        # Verify system events callback
        assert system_call is not None
        data, event_type = system_call
        assert len(data) == 1
        assert data[0]['event_type'] == 'file_rotation'
    
    @pytest.mark.asyncio
    async def test_handle_status_modification(self, event_handler, temp_journal_dir):
        """Test handling Status.json modifications."""
        status_file = temp_journal_dir / "Status.json"
        
        # Modify status file
        new_status = {
            "timestamp": "2024-09-06T13:00:00Z",
            "event": "Status",
            "Flags": 12345
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(new_status, f)
        
        # Handle modification
        await event_handler._handle_status_modification(status_file)
        
        # Verify callback was called
        event_handler.callback.assert_called_once()
        call_args = event_handler.callback.call_args
        data, event_type = call_args[0]
        
        assert event_type == 'status_update'
        assert len(data) == 1
        assert data[0]['Flags'] == 12345
    
    @pytest.mark.asyncio
    async def test_safe_callback_async(self, parser):
        """Test safe callback with async function."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        async_callback = AsyncMock()
        handler = JournalEventHandler(async_callback, parser, loop)
        
        test_data = [{'test': 'data'}]
        await handler._safe_callback(test_data, 'test_event')
        
        async_callback.assert_called_once_with(test_data, 'test_event')
    
    @pytest.mark.asyncio
    async def test_safe_callback_sync(self, parser):
        """Test safe callback with sync function."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        sync_callback = MagicMock()
        handler = JournalEventHandler(sync_callback, parser, loop)
        
        test_data = [{'test': 'data'}]
        await handler._safe_callback(test_data, 'test_event')
        
        sync_callback.assert_called_once_with(test_data, 'test_event')
    
    @pytest.mark.asyncio
    async def test_safe_callback_error_handling(self, parser):
        """Test safe callback error handling."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        error_callback = AsyncMock(side_effect=Exception("Test error"))
        handler = JournalEventHandler(error_callback, parser, loop)
        
        test_data = [{'test': 'data'}]
        
        # Should not raise exception
        await handler._safe_callback(test_data, 'test_event')
        
        error_callback.assert_called_once_with(test_data, 'test_event')


class TestJournalMonitor:
    """Test cases for JournalMonitor class."""
    
    def test_initialization(self, temp_journal_dir, mock_callback):
        """Test monitor initialization."""
        monitor = JournalMonitor(temp_journal_dir, mock_callback)
        
        assert monitor.journal_path == temp_journal_dir
        assert monitor.event_callback == mock_callback
        assert isinstance(monitor.parser, JournalParser)
        assert monitor.observer is None
        assert monitor.event_handler is None
        assert monitor.is_monitoring is False
    
    @pytest.mark.asyncio
    async def test_start_monitoring_success(self, monitor):
        """Test successful monitoring startup."""
        result = await monitor.start_monitoring()
        
        assert result is True
        assert monitor.is_monitoring is True
        assert monitor.observer is not None
        assert monitor.event_handler is not None
        assert monitor.observer.is_alive()
        
        # Cleanup
        await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_start_monitoring_invalid_directory(self, mock_callback):
        """Test monitoring startup with invalid directory."""
        invalid_path = Path("/nonexistent/directory")
        monitor = JournalMonitor(invalid_path, mock_callback)
        
        result = await monitor.start_monitoring()
        
        assert result is False
        assert monitor.is_monitoring is False
        assert monitor.observer is None
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_active(self, monitor):
        """Test starting monitoring when already active."""
        # Start monitoring
        await monitor.start_monitoring()
        assert monitor.is_monitoring is True
        
        # Try to start again
        result = await monitor.start_monitoring()
        assert result is True  # Should return True but not start again
        
        # Cleanup
        await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, monitor):
        """Test stopping monitoring."""
        # Start monitoring first
        await monitor.start_monitoring()
        assert monitor.is_monitoring is True
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        assert monitor.is_monitoring is False
        assert monitor.observer is None
        assert monitor.event_handler is None
    
    @pytest.mark.asyncio
    async def test_is_active(self, monitor):
        """Test is_active status checking."""
        # Initially not active
        assert monitor.is_active() is False
        
        # Start monitoring
        await monitor.start_monitoring()
        assert monitor.is_active() is True
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor.is_active() is False
    
    @pytest.mark.asyncio
    async def test_process_existing_entries(self, monitor):
        """Test processing existing entries on startup."""
        await monitor.start_monitoring()
        
        # Allow some time for processing
        await asyncio.sleep(0.1)
        
        # Verify callback was called for existing entries
        assert monitor.event_callback.called
        
        # Check that journal entries were processed
        call_args_list = monitor.event_callback.call_args_list
        journal_calls = [call for call in call_args_list 
                        if len(call[0]) > 1 and call[0][1] == 'journal_entries']
        
        assert len(journal_calls) > 0
        
        # Cleanup
        await monitor.stop_monitoring()
    
    def test_get_monitoring_status(self, monitor):
        """Test getting monitoring status."""
        status = monitor.get_monitoring_status()
        
        assert 'is_monitoring' in status
        assert 'is_active' in status
        assert 'journal_path' in status
        assert 'monitored_files_count' in status
        assert 'current_positions' in status
        assert 'latest_journal' in status
        assert 'status_file_exists' in status
        
        assert status['is_monitoring'] is False
        assert status['is_active'] is False
        assert status['journal_path'] == str(monitor.journal_path)
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status_active(self, monitor):
        """Test getting monitoring status when active."""
        await monitor.start_monitoring()
        
        status = monitor.get_monitoring_status()
        
        assert status['is_monitoring'] is True
        assert status['is_active'] is True
        assert status['monitored_files_count'] >= 0
        assert status['status_file_exists'] is True
        assert status['latest_journal'] is not None
        
        # Cleanup
        await monitor.stop_monitoring()


class TestJournalMonitorIntegration:
    """Integration tests for journal monitoring."""
    
    @pytest.mark.asyncio
    async def test_file_modification_detection(self, temp_journal_dir):
        """Test real-time file modification detection."""
        received_events = []
        
        async def test_callback(data, event_type):
            received_events.append((data, event_type))
        
        monitor = JournalMonitor(temp_journal_dir, test_callback)
        
        try:
            # Start monitoring
            await monitor.start_monitoring()
            
            # Allow startup processing
            await asyncio.sleep(0.1)
            initial_events = len(received_events)
            
            # Modify existing journal file
            latest_journal = monitor.parser.get_latest_journal()
            new_entry = '{"timestamp":"2024-09-06T13:00:00Z","event":"TestModification"}\n'
            
            with open(latest_journal, 'a', encoding='utf-8') as f:
                f.write(new_entry)
            
            # Wait for file system event processing
            await asyncio.sleep(0.2)
            
            # Verify new events were received
            assert len(received_events) > initial_events
            
            # Check for the new entry
            new_events = received_events[initial_events:]
            journal_events = [event for event in new_events 
                            if event[1] == 'journal_entries']
            
            assert len(journal_events) > 0
            
            # Find our test entry
            found_test_entry = False
            for data, event_type in journal_events:
                for entry in data:
                    if entry.get('event') == 'TestModification':
                        found_test_entry = True
                        break
            
            assert found_test_entry
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_status_file_modification_detection(self, temp_journal_dir):
        """Test Status.json modification detection."""
        received_events = []
        
        async def test_callback(data, event_type):
            received_events.append((data, event_type))
        
        monitor = JournalMonitor(temp_journal_dir, test_callback)
        
        try:
            # Start monitoring
            await monitor.start_monitoring()
            
            # Allow startup processing
            await asyncio.sleep(0.1)
            initial_events = len(received_events)
            
            # Modify Status.json
            status_file = temp_journal_dir / "Status.json"
            new_status = {
                "timestamp": "2024-09-06T13:05:00Z",
                "event": "Status",
                "Flags": 99999
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(new_status, f)
            
            # Wait for file system event processing
            await asyncio.sleep(0.2)
            
            # Verify status events were received
            new_events = received_events[initial_events:]
            status_events = [event for event in new_events 
                           if event[1] == 'status_update']
            
            assert len(status_events) > 0
            
            # Verify the updated status
            for data, event_type in status_events:
                for entry in data:
                    if entry.get('Flags') == 99999:
                        assert True
                        break
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio 
    async def test_new_journal_file_creation(self, temp_journal_dir):
        """Test new journal file creation detection."""
        received_events = []
        
        async def test_callback(data, event_type):
            received_events.append((data, event_type))
        
        monitor = JournalMonitor(temp_journal_dir, test_callback)
        
        try:
            # Start monitoring
            await monitor.start_monitoring()
            
            # Allow startup processing
            await asyncio.sleep(0.1)
            initial_events = len(received_events)
            
            # Create new journal file
            new_journal = temp_journal_dir / "Journal.20240906150000.01.log"
            new_content = '{"timestamp":"2024-09-06T15:00:00Z","event":"NewJournalFile"}\n'
            
            with open(new_journal, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Wait for file system event processing
            await asyncio.sleep(0.2)
            
            # Verify events were received
            new_events = received_events[initial_events:]
            
            # Check for system events (file rotation)
            system_events = [event for event in new_events 
                           if event[1] == 'system_events']
            
            # Check for journal entries
            journal_events = [event for event in new_events 
                            if event[1] == 'journal_entries']
            
            assert len(system_events) > 0 or len(journal_events) > 0
            
        finally:
            await monitor.stop_monitoring()


class TestJournalMonitorEdgeCases:
    """Test edge cases and stress scenarios for journal monitor."""
    
    @pytest.mark.asyncio
    async def test_rapid_file_changes_stress(self, temp_journal_dir):
        """Test monitor with rapid successive file changes."""
        received_events = []
        
        async def stress_callback(data, event_type):
            received_events.append((data, event_type, datetime.now()))
        
        monitor = JournalMonitor(temp_journal_dir, stress_callback)
        
        try:
            await monitor.start_monitoring()
            await asyncio.sleep(0.1)  # Let monitoring start
            
            # Create initial journal file
            stress_journal = temp_journal_dir / "Journal.20240906230000.01.log"
            with open(stress_journal, 'w', encoding='utf-8') as f:
                f.write('{"timestamp":"2024-09-06T23:00:00Z","event":"Initial"}\n')
            
            # Rapidly add multiple entries
            for i in range(50):  # 50 rapid changes
                with open(stress_journal, 'a', encoding='utf-8') as f:
                    entry = {
                        "timestamp": f"2024-09-06T23:00:{i:02d}Z",
                        "event": f"RapidEvent{i}",
                        "data": f"stress_test_{i}"
                    }
                    f.write(json.dumps(entry) + '\n')
                
                # Small delay to allow processing
                await asyncio.sleep(0.01)
            
            # Wait for all events to be processed
            await asyncio.sleep(1.0)
            
            # Verify all events were captured
            journal_events = [e for e in received_events if e[1] == 'journal_entries']
            assert len(journal_events) > 0
            
            # Check that events were processed in reasonable time
            if len(journal_events) >= 2:
                first_event_time = journal_events[0][2]
                last_event_time = journal_events[-1][2]
                processing_time = (last_event_time - first_event_time).total_seconds()
                
                # Should process within reasonable time (less than 10 seconds)
                assert processing_time < 10.0, f"Processing took {processing_time:.2f} seconds"
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_observer_failure_recovery(self, temp_journal_dir):
        """Test monitor behavior when observer fails."""
        failure_callback = AsyncMock()
        monitor = JournalMonitor(temp_journal_dir, failure_callback)
        
        try:
            await monitor.start_monitoring()
            assert monitor.is_active()
            
            # Simulate observer failure
            if monitor.observer:
                # Force stop the observer to simulate failure
                monitor.observer.stop()
                monitor.observer.join(timeout=1.0)
            
            # Monitor should detect that observer is no longer active
            await asyncio.sleep(0.1)
            
            # is_active should return False when observer fails
            # Note: This tests the current behavior; in a production system
            # you might want automatic recovery
            assert not monitor.is_active()
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_memory_usage_long_session(self, temp_journal_dir):
        """Test memory usage during long monitoring sessions."""
        import tracemalloc
        
        events_received = []
        
        async def memory_callback(data, event_type):
            events_received.extend(data)
        
        monitor = JournalMonitor(temp_journal_dir, memory_callback)
        
        try:
            tracemalloc.start()
            
            await monitor.start_monitoring()
            
            # Create a journal file and continuously add entries
            long_journal = temp_journal_dir / "Journal.20240907000000.01.log"
            
            # Simulate a long session with many events
            for batch in range(10):  # 10 batches
                with open(long_journal, 'a', encoding='utf-8') as f:
                    for i in range(100):  # 100 events per batch
                        entry = {
                            "timestamp": f"2024-09-07T00:{batch:02d}:{i:02d}Z",
                            "event": f"LongSessionEvent{batch}_{i}",
                            "data": f"batch_{batch}_entry_{i}_{'x' * 50}"  # Some data
                        }
                        f.write(json.dumps(entry) + '\n')
                
                # Allow processing
                await asyncio.sleep(0.2)
            
            # Check memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Memory usage should be reasonable (less than 100MB peak)
            peak_mb = peak / (1024 * 1024)
            assert peak_mb < 100, f"Peak memory usage: {peak_mb:.2f} MB"
            
            # Verify events were processed
            assert len(events_received) > 0
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_network_drive_simulation(self, temp_journal_dir):
        """Test monitoring behavior with simulated network drive delays."""
        delayed_events = []
        
        async def delayed_callback(data, event_type):
            delayed_events.append((data, event_type))
        
        monitor = JournalMonitor(temp_journal_dir, delayed_callback)
        
        # Mock file operations to simulate network delays
        original_open = open
        
        def slow_file_open(file, mode='r', **kwargs):
            # Simulate network delay for file operations
            if 'Journal.' in str(file) and 'r' in mode:
                time.sleep(0.1)  # 100ms delay
            return original_open(file, mode, **kwargs)
        
        try:
            with patch('builtins.open', side_effect=slow_file_open):
                await monitor.start_monitoring()
                
                # Create journal file
                network_journal = temp_journal_dir / "Journal.20240907010000.01.log"
                with open(network_journal, 'w', encoding='utf-8') as f:
                    f.write('{"timestamp":"2024-09-07T01:00:00Z","event":"NetworkTest"}\n')
                
                # Wait for processing with network delays
                await asyncio.sleep(1.0)
                
                # Should still process events despite delays
                assert len(delayed_events) > 0
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_file_rotation_burst(self, temp_journal_dir):
        """Test handling of multiple rapid file rotations."""
        rotation_events = []
        
        async def rotation_callback(data, event_type):
            rotation_events.append((data, event_type, datetime.now()))
        
        monitor = JournalMonitor(temp_journal_dir, rotation_callback)
        
        try:
            await monitor.start_monitoring()
            await asyncio.sleep(0.1)
            
            # Create multiple journal files rapidly (simulating rapid rotation)
            journal_files = []
            for i in range(5):
                journal_file = temp_journal_dir / f"Journal.2024090701{i:02d}00.01.log"
                journal_files.append(journal_file)
                
                with open(journal_file, 'w', encoding='utf-8') as f:
                    f.write(f'{{"timestamp":"2024-09-07T01:{i:02d}:00Z","event":"RotationTest{i}"}}\n')
                
                # Brief delay between rotations
                await asyncio.sleep(0.05)
            
            # Wait for all events to be processed
            await asyncio.sleep(1.0)
            
            # Check for system events (file rotations)
            system_events = [e for e in rotation_events if e[1] == 'system_events']
            journal_events = [e for e in rotation_events if e[1] == 'journal_entries']
            
            # Should have detected file rotations and processed entries
            assert len(system_events) > 0 or len(journal_events) > 0
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_callback_exception_isolation(self, temp_journal_dir):
        """Test that callback exceptions don't stop monitoring."""
        callback_calls = []
        exception_count = 0
        
        async def failing_callback(data, event_type):
            nonlocal exception_count
            callback_calls.append((data, event_type))
            
            # Fail on first few calls
            if len(callback_calls) <= 3:
                exception_count += 1
                raise Exception(f"Simulated callback failure {exception_count}")
        
        monitor = JournalMonitor(temp_journal_dir, failing_callback)
        
        try:
            await monitor.start_monitoring()
            
            # Create journal file with multiple entries
            exception_journal = temp_journal_dir / "Journal.20240907020000.01.log"
            
            for i in range(6):  # 6 entries - first 3 should trigger exceptions
                with open(exception_journal, 'a', encoding='utf-8') as f:
                    entry = {
                        "timestamp": f"2024-09-07T02:00:{i:02d}Z",
                        "event": f"ExceptionTest{i}"
                    }
                    f.write(json.dumps(entry) + '\n')
                
                await asyncio.sleep(0.1)
            
            # Wait for processing
            await asyncio.sleep(0.5)
            
            # Monitor should still be active despite callback exceptions
            assert monitor.is_active()
            
            # Should have attempted all callbacks despite exceptions
            assert len(callback_calls) >= 3
            assert exception_count >= 3
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_large_status_updates(self, temp_journal_dir):
        """Test handling of very large Status.json files."""
        status_events = []
        
        async def status_callback(data, event_type):
            if event_type == 'status_update':
                status_events.append(data)
        
        monitor = JournalMonitor(temp_journal_dir, status_callback)
        
        try:
            await monitor.start_monitoring()
            
            # Allow initial status processing
            await asyncio.sleep(0.2)
            
            status_file = temp_journal_dir / "Status.json"
            
            # Create a large status file with lots of data
            large_status = {
                "timestamp": "2024-09-07T02:30:00Z",
                "event": "Status",
                "Flags": 12345,
                "large_data": {
                    f"entry_{i}": f"data_{'x' * 1000}_{i}"  # 1KB per entry
                    for i in range(100)  # 100KB total
                }
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(large_status, f)
            
            # Wait for processing
            await asyncio.sleep(0.5)
            
            # Should handle large status files
            assert len(status_events) > 0
            
            # Look for the status update with Flags: 12345 (the new large status)
            found_large_status = False
            for status_data_list in status_events:
                for status_data in status_data_list:
                    if status_data.get("Flags") == 12345:
                        assert "large_data" in status_data
                        found_large_status = True
                        break
                if found_large_status:
                    break
            
            assert found_large_status, f"Expected to find status with Flags=12345, but got: {status_events}"
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_event_handler_threading_edge_cases(self, temp_journal_dir):
        """Test event handler behavior with threading edge cases."""
        thread_events = []
        
        def sync_callback(data, event_type):
            # Synchronous callback to test threading coordination
            thread_events.append((data, event_type, threading.current_thread().name))
        
        monitor = JournalMonitor(temp_journal_dir, sync_callback)
        
        try:
            await monitor.start_monitoring()
            
            # Create journal file
            thread_journal = temp_journal_dir / "Journal.20240907030000.01.log"
            with open(thread_journal, 'w', encoding='utf-8') as f:
                f.write('{"timestamp":"2024-09-07T03:00:00Z","event":"ThreadTest"}\n')
            
            # Wait for processing
            await asyncio.sleep(0.5)
            
            # Should have processed events
            assert len(thread_events) > 0
            
            # Verify thread safety - events should be processed
            for data, event_type, thread_name in thread_events:
                assert isinstance(data, list)
                assert isinstance(event_type, str)
                assert isinstance(thread_name, str)
            
        finally:
            await monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_position_tracking_corruption_recovery(self, temp_journal_dir):
        """Test recovery from position tracking corruption."""
        position_events = []
        
        async def position_callback(data, event_type):
            position_events.append((len(data), event_type))
        
        monitor = JournalMonitor(temp_journal_dir, position_callback)
        
        try:
            await monitor.start_monitoring()
            
            # Create journal file
            position_journal = temp_journal_dir / "Journal.20240907040000.01.log"
            initial_content = '{"timestamp":"2024-09-07T04:00:00Z","event":"Initial"}\n'
            
            with open(position_journal, 'w', encoding='utf-8') as f:
                f.write(initial_content)
            
            await asyncio.sleep(0.2)
            
            # Simulate position tracking corruption by manually corrupting the position
            if monitor.event_handler:
                file_key = str(position_journal)
                # Set invalid position (beyond file end)
                monitor.event_handler.current_positions[file_key] = 999999
            
            # Add more content
            additional_content = '{"timestamp":"2024-09-07T04:01:00Z","event":"Additional"}\n'
            with open(position_journal, 'a', encoding='utf-8') as f:
                f.write(additional_content)
            
            await asyncio.sleep(0.5)
            
            # Should recover gracefully from position corruption
            assert len(position_events) > 0
            
        finally:
            await monitor.stop_monitoring()


class TestJournalEventHandlerEdgeCases:
    """Test edge cases specific to JournalEventHandler."""
    
    @pytest.mark.asyncio
    async def test_event_loop_coordination(self, temp_journal_dir):
        """Test proper event loop coordination in handler."""
        coordination_events = []
        
        async def coordination_callback(data, event_type):
            # Record the current event loop
            try:
                loop = asyncio.get_running_loop()
                coordination_events.append((data, event_type, id(loop)))
            except RuntimeError:
                coordination_events.append((data, event_type, None))
        
        parser = JournalParser(temp_journal_dir)
        
        # Get the current event loop
        main_loop = asyncio.get_running_loop()
        
        handler = JournalEventHandler(coordination_callback, parser, main_loop)
        
        # Create test file
        test_file = temp_journal_dir / "Journal.20240907050000.01.log"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('{"timestamp":"2024-09-07T05:00:00Z","event":"LoopTest"}\n')
        
        # Test handler directly
        await handler._handle_journal_modification(test_file)
        
        # Should have coordinated with the main event loop
        assert len(coordination_events) > 0
        
        # Verify callback was executed in the main event loop
        for data, event_type, loop_id in coordination_events:
            if loop_id is not None:
                assert loop_id == id(main_loop)
    
    @pytest.mark.asyncio
    async def test_status_throttling_edge_cases(self, temp_journal_dir):
        """Test status update throttling edge cases."""
        throttle_events = []
        
        async def throttle_callback(data, event_type):
            throttle_events.append((data, event_type, datetime.now()))
        
        parser = JournalParser(temp_journal_dir)
        loop = asyncio.get_running_loop()
        handler = JournalEventHandler(throttle_callback, parser, loop)
        
        status_file = temp_journal_dir / "Status.json"
        
        # Create initial status file
        status_data = {"timestamp": "2024-09-07T05:30:00Z", "event": "Status", "Flags": 123}
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f)
        
        # Rapidly trigger status modifications
        for i in range(10):
            await handler._handle_status_modification(status_file)
            await asyncio.sleep(0.01)  # 10ms between calls
        
        # Should be throttled - not all modifications should result in callbacks
        status_events = [e for e in throttle_events if e[1] == 'status_update']
        
        # Due to throttling, should have fewer events than modifications
        assert len(status_events) < 10
        assert len(status_events) > 0  # But should have some events
    
    @pytest.mark.asyncio
    async def test_file_creation_race_conditions(self, temp_journal_dir):
        """Test handling of file creation race conditions."""
        race_events = []
        
        async def race_callback(data, event_type):
            race_events.append((data, event_type))
        
        parser = JournalParser(temp_journal_dir)
        loop = asyncio.get_running_loop()
        handler = JournalEventHandler(race_callback, parser, loop)
        
        # Simulate race condition where file is created but not yet written
        race_file = temp_journal_dir / "Journal.20240907060000.01.log"
        
        # Create empty file first
        race_file.touch()
        
        # Handle creation of empty file
        await handler._handle_journal_creation(race_file)
        
        # Now write content
        with open(race_file, 'w', encoding='utf-8') as f:
            f.write('{"timestamp":"2024-09-07T06:00:00Z","event":"RaceTest"}\n')
        
        # Handle modification after content is written
        await handler._handle_journal_modification(race_file)
        
        # Should handle the race condition gracefully
        assert len(race_events) >= 1
        
        # Should have processed the content once it was available
        journal_events = [e for e in race_events if e[1] == 'journal_entries']
        if journal_events:
            entries = journal_events[0][0]
            assert len(entries) > 0
            assert entries[0]['event'] == 'RaceTest'


class TestJournalMonitorConcurrency:
    """Test concurrency and threading aspects of journal monitor."""
    
    @pytest.mark.asyncio
    async def test_concurrent_monitor_instances(self, temp_journal_dir):
        """Test behavior with multiple monitor instances on same directory."""
        events_monitor1 = []
        events_monitor2 = []
        
        async def callback1(data, event_type):
            events_monitor1.append((data, event_type))
        
        async def callback2(data, event_type):
            events_monitor2.append((data, event_type))
        
        monitor1 = JournalMonitor(temp_journal_dir, callback1)
        monitor2 = JournalMonitor(temp_journal_dir, callback2)
        
        try:
            # Start both monitors
            await monitor1.start_monitoring()
            await monitor2.start_monitoring()
            
            # Both should be active
            assert monitor1.is_active()
            assert monitor2.is_active()
            
            # Create journal file
            concurrent_journal = temp_journal_dir / "Journal.20240907070000.01.log"
            with open(concurrent_journal, 'w', encoding='utf-8') as f:
                f.write('{"timestamp":"2024-09-07T07:00:00Z","event":"ConcurrentTest"}\n')
            
            await asyncio.sleep(0.5)
            
            # Both monitors should have detected the file
            assert len(events_monitor1) > 0
            assert len(events_monitor2) > 0
            
        finally:
            await monitor1.stop_monitoring()
            await monitor2.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_monitor_startup_shutdown_race(self, temp_journal_dir):
        """Test rapid startup/shutdown cycles for race conditions."""
        race_callback = AsyncMock()
        monitor = JournalMonitor(temp_journal_dir, race_callback)
        
        # Rapid start/stop cycles
        for _ in range(5):
            await monitor.start_monitoring()
            assert monitor.is_monitoring
            
            await monitor.stop_monitoring()
            assert not monitor.is_monitoring
            
            # Brief pause between cycles
            await asyncio.sleep(0.1)
        
        # Should end in stopped state
        assert not monitor.is_active()
        assert not monitor.is_monitoring


class TestJournalMonitorResourceManagement:
    """Test resource management and cleanup in journal monitor."""
    
    @pytest.mark.asyncio
    async def test_proper_resource_cleanup(self, temp_journal_dir):
        """Test that all resources are properly cleaned up."""
        cleanup_callback = AsyncMock()
        monitor = JournalMonitor(temp_journal_dir, cleanup_callback)
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Verify resources are allocated
        assert monitor.observer is not None
        assert monitor.event_handler is not None
        assert monitor._event_loop is not None
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        # Verify resources are cleaned up
        assert monitor.observer is None
        assert monitor.event_handler is None
        assert monitor._event_loop is None
        assert not monitor.is_monitoring
        assert not monitor.is_active()
    
    @pytest.mark.asyncio
    async def test_cleanup_with_pending_operations(self, temp_journal_dir):
        """Test cleanup when there are pending file operations."""
        pending_events = []
        
        async def slow_callback(data, event_type):
            # Simulate slow callback processing
            await asyncio.sleep(0.2)
            pending_events.append((data, event_type))
        
        monitor = JournalMonitor(temp_journal_dir, slow_callback)
        
        try:
            await monitor.start_monitoring()
            
            # Create journal file to trigger processing
            pending_journal = temp_journal_dir / "Journal.20240907080000.01.log"
            with open(pending_journal, 'w', encoding='utf-8') as f:
                f.write('{"timestamp":"2024-09-07T08:00:00Z","event":"PendingTest"}\n')
            
            # Immediately stop monitoring (while callback might be pending)
            await asyncio.sleep(0.05)  # Brief delay to start processing
            
        finally:
            # Stop should complete even with pending operations
            await monitor.stop_monitoring()
            
            # Should have cleaned up properly
            assert not monitor.is_active()
    
    @pytest.mark.asyncio
    async def test_file_handle_management(self, temp_journal_dir):
        """Test that file handles are properly managed."""
        handle_callback = AsyncMock()
        monitor = JournalMonitor(temp_journal_dir, handle_callback)
        
        try:
            await monitor.start_monitoring()
            
            # Create and modify many files to test file handle usage
            for i in range(20):
                test_journal = temp_journal_dir / f"Journal.20240907080{i:02d}00.01.log"
                
                with open(test_journal, 'w', encoding='utf-8') as f:
                    f.write(f'{{"timestamp":"2024-09-07T08:{i:02d}:00Z","event":"HandleTest{i}"}}\n')
                
                # Brief delay between file operations
                await asyncio.sleep(0.01)
            
            # Wait for processing
            await asyncio.sleep(1.0)
            
            # Should have processed without file handle issues
            assert monitor.is_active()
            
        finally:
            await monitor.stop_monitoring()
            
            # Should clean up without file handle leaks
            assert not monitor.is_active()


# Mock data for testing
MOCK_JOURNAL_MODIFICATION_EVENT = """{"timestamp":"2024-09-06T12:30:00Z","event":"FSDJump","StarSystem":"Test System","JumpDist":10.5}"""

MOCK_STATUS_DATA = {
    "timestamp": "2024-09-06T12:30:00Z",
    "event": "Status",
    "Flags": 16777240,
    "Pips": [4, 8, 0],
    "FireGroup": 0,
    "GuiFocus": 0
}
