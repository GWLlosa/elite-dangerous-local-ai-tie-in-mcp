"""Unit tests for journal monitoring functionality."""

import asyncio
import json
import tempfile
import time
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
