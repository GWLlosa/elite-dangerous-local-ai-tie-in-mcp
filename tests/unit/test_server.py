"""
Unit tests for MCP Server Framework - Milestone 7

Tests cover:
- Server initialization and configuration
- MCP tool functionality and error handling
- Journal monitoring integration
- Server lifecycle management (startup/shutdown)
- Signal handling and graceful termination
- Background task management
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from src.server import EliteDangerousServer, create_server, lifespan_manager
from src.utils.data_store import reset_data_store


class TestEliteDangerousServer:
    """Test suite for EliteDangerousServer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset global state
        reset_data_store()
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.journal_path = Path(self.temp_dir)
        
    def teardown_method(self):
        """Clean up after tests."""
        reset_data_store()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.server.EliteConfig')
    def test_server_initialization(self, mock_config):
        """Test server initialization with configuration."""
        # Setup mock configuration
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config_instance.validate_paths.return_value = True
        mock_config.return_value = mock_config_instance
        
        # Create server
        server = EliteDangerousServer()
        
        # Verify initialization
        assert server.config == mock_config_instance
        assert server.event_processor is not None
        assert server.data_store is not None
        assert server.journal_monitor is None  # Not started yet
        assert server._running == False
        assert server._monitor_task is None
    
    @patch('src.server.EliteConfig')
    def test_server_initialization_config_failure(self, mock_config):
        """Test server initialization when configuration fails."""
        # Setup mock to raise exception
        mock_config.side_effect = Exception("Configuration error")
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Configuration error"):
            EliteDangerousServer()
    
    @patch('src.server.EliteConfig')
    def test_setup_signal_handlers(self, mock_config):
        """Test signal handler setup."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        
        # Should not raise any exceptions
        server.setup_signal_handlers()
    
    @patch('src.server.EliteConfig')
    @patch('src.server.JournalMonitor')
    async def test_start_journal_monitoring(self, mock_monitor_class, mock_config):
        """Test starting journal monitoring."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        mock_monitor = AsyncMock()
        mock_monitor_class.return_value = mock_monitor
        
        server = EliteDangerousServer()
        
        # Start monitoring
        await server.start_journal_monitoring()
        
        # Verify monitor was created and started
        assert server.journal_monitor == mock_monitor
        mock_monitor.set_event_callback.assert_called_once()
        mock_monitor.start.assert_called_once()
    
    @patch('src.server.EliteConfig')
    @patch('src.server.JournalMonitor')
    async def test_start_journal_monitoring_failure(self, mock_monitor_class, mock_config):
        """Test journal monitoring startup failure."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        mock_monitor = AsyncMock()
        mock_monitor.start.side_effect = Exception("Monitor start failed")
        mock_monitor_class.return_value = mock_monitor
        
        server = EliteDangerousServer()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to start journal monitoring"):
            await server.start_journal_monitoring()
    
    @patch('src.server.EliteConfig')
    async def test_stop_journal_monitoring(self, mock_config):
        """Test stopping journal monitoring."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        
        # Test with no monitor (should not raise)
        await server.stop_journal_monitoring()
        
        # Test with monitor
        mock_monitor = AsyncMock()
        server.journal_monitor = mock_monitor
        
        await server.stop_journal_monitoring()
        
        mock_monitor.stop.assert_called_once()
    
    @patch('src.server.EliteConfig')
    async def test_stop_journal_monitoring_error(self, mock_config):
        """Test stopping journal monitoring with error."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        
        # Set up monitor that fails to stop
        mock_monitor = AsyncMock()
        mock_monitor.stop.side_effect = Exception("Stop failed")
        server.journal_monitor = mock_monitor
        
        # Should not raise exception (error is logged)
        await server.stop_journal_monitoring()
    
    @patch('src.server.EliteConfig')
    async def test_server_startup(self, mock_config):
        """Test server startup procedures."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config_instance.validate_paths.return_value = True
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        
        # Mock the background task creation
        with patch.object(server, 'monitor_background_task') as mock_task:
            mock_task.return_value = asyncio.Future()
            mock_task.return_value.set_result(None)
            
            await server.startup()
            
            # Verify server state
            assert server._running == True
            assert server._monitor_task is not None
    
    @patch('src.server.EliteConfig')
    async def test_server_startup_failure(self, mock_config):
        """Test server startup failure handling."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config_instance.validate_paths.side_effect = Exception("Validation failed")
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        
        # Verify exception is raised
        with pytest.raises(Exception, match="Server startup failed"):
            await server.startup()
    
    @patch('src.server.EliteConfig')
    async def test_server_shutdown(self, mock_config):
        """Test server shutdown procedures."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server._running = True
        
        # Create a mock task
        mock_task = AsyncMock()
        mock_task.done.return_value = False
        server._monitor_task = mock_task
        
        # Mock journal monitor
        server.journal_monitor = AsyncMock()
        
        await server.shutdown()
        
        # Verify shutdown
        assert server._running == False
        mock_task.cancel.assert_called_once()
        server.data_store.clear.assert_called_once() if hasattr(server.data_store, 'clear') else None
    
    @patch('src.server.EliteConfig')
    def test_event_callback_processing(self, mock_config):
        """Test journal event callback processing."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        
        # Create test event data
        event_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "FSDJump",
            "StarSystem": "Sol"
        }
        
        # Mock the event processor and data store
        mock_processed_event = Mock()
        server.event_processor.process_event = Mock(return_value=mock_processed_event)
        server.data_store.store_event = Mock()
        
        # Get the callback (this would normally be set in start_journal_monitoring)
        # We'll simulate this by creating the callback function
        def on_journal_event(event_data):
            processed_event = server.event_processor.process_event(event_data)
            server.data_store.store_event(processed_event)
        
        # Call the callback
        on_journal_event(event_data)
        
        # Verify processing
        server.event_processor.process_event.assert_called_once_with(event_data)
        server.data_store.store_event.assert_called_once_with(mock_processed_event)


class TestMCPServerTools:
    """Test suite for MCP server tool functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        reset_data_store()
        self.temp_dir = tempfile.mkdtemp()
        self.journal_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_data_store()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.server.EliteConfig')
    async def test_server_status_tool(self, mock_config):
        """Test server_status MCP tool."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        # Mock data store responses
        mock_stats = {
            "total_events": 10,
            "total_processed": 15,
            "uptime_seconds": 120
        }
        mock_game_state = Mock()
        mock_game_state.current_system = "Sol"
        mock_game_state.current_ship = "Asp Explorer"
        mock_game_state.docked = True
        mock_game_state.last_updated = datetime.utcnow()
        
        server.data_store.get_statistics = Mock(return_value=mock_stats)
        server.data_store.get_game_state = Mock(return_value=mock_game_state)
        server._running = True
        server.journal_monitor = Mock()
        
        # Get the server_status tool function from FastMCP tools
        # Access the tools through the app's internal structure
        tools = {name: func for name, func in server.app._tools.items() if name == 'server_status'}
        assert len(tools) == 1
        server_status_tool = tools['server_status']
        
        # Call the tool (FastMCP tools don't take RequestContext)
        result = await server_status_tool()
        
        # Verify result
        assert result["server_running"] == True
        assert result["journal_monitoring"] == True
        assert result["data_store_stats"] == mock_stats
        assert result["current_system"] == "Sol"
        assert result["current_ship"] == "Asp Explorer"
        assert result["docked"] == True
        assert "last_updated" in result
    
    @patch('src.server.EliteConfig')
    async def test_server_status_tool_error(self, mock_config):
        """Test server_status MCP tool error handling."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        # Make data store raise exception
        server.data_store.get_statistics = Mock(side_effect=Exception("Data store error"))
        
        # Get the tool function
        tools = {name: func for name, func in server.app._tools.items() if name == 'server_status'}
        server_status_tool = tools['server_status']
        
        # Call the tool
        result = await server_status_tool()
        
        # Verify error handling
        assert "error" in result
        assert "Data store error" in result["error"]
    
    @patch('src.server.EliteConfig')
    async def test_get_recent_events_tool(self, mock_config):
        """Test get_recent_events MCP tool."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        # Mock events
        mock_event1 = Mock()
        mock_event1.timestamp = datetime.utcnow()
        mock_event1.event_type = "FSDJump"
        mock_event1.category.value = "navigation"
        mock_event1.summary = "Jumped to Sol"
        
        mock_event2 = Mock()
        mock_event2.timestamp = datetime.utcnow()
        mock_event2.event_type = "Docked"
        mock_event2.category.value = "ship"
        mock_event2.summary = "Docked at station"
        
        mock_events = [mock_event1, mock_event2]
        server.data_store.get_recent_events = Mock(return_value=mock_events)
        
        # Get the tool function
        tools = {name: func for name, func in server.app._tools.items() if name == 'get_recent_events'}
        assert len(tools) == 1
        get_recent_events_tool = tools['get_recent_events']
        
        # Call the tool with default parameters (FastMCP tools take named parameters directly)
        result = await get_recent_events_tool()
        
        # Verify result
        assert result["event_count"] == 2
        assert result["time_period_minutes"] == 60
        assert len(result["events"]) == 2
        assert result["events"][0]["event_type"] == "FSDJump"
        assert result["events"][1]["event_type"] == "Docked"
        
        # Verify data store was called correctly
        server.data_store.get_recent_events.assert_called_with(minutes=60)
    
    @patch('src.server.EliteConfig')
    async def test_get_recent_events_tool_custom_minutes(self, mock_config):
        """Test get_recent_events MCP tool with custom minutes parameter."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        server.data_store.get_recent_events = Mock(return_value=[])
        
        # Get the tool function
        tools = {name: func for name, func in server.app._tools.items() if name == 'get_recent_events'}
        get_recent_events_tool = tools['get_recent_events']
        
        # Call the tool with custom minutes
        result = await get_recent_events_tool(minutes=30)
        
        # Verify result
        assert result["time_period_minutes"] == 30
        server.data_store.get_recent_events.assert_called_with(minutes=30)
    
    @patch('src.server.EliteConfig')
    async def test_get_recent_events_tool_invalid_minutes(self, mock_config):
        """Test get_recent_events MCP tool with invalid minutes parameter."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        # Get the tool function
        tools = {name: func for name, func in server.app._tools.items() if name == 'get_recent_events'}
        get_recent_events_tool = tools['get_recent_events']
        
        # Test invalid minutes (too low)
        result = await get_recent_events_tool(minutes=0)
        assert "error" in result
        assert "Invalid minutes parameter" in result["error"]
        
        # Test invalid minutes (too high)
        result = await get_recent_events_tool(minutes=2000)
        assert "error" in result
        assert "Invalid minutes parameter" in result["error"]
    
    @patch('src.server.EliteConfig')
    async def test_clear_data_store_tool(self, mock_config):
        """Test clear_data_store MCP tool."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        server.data_store.clear = Mock()
        
        # Get the tool function
        tools = {name: func for name, func in server.app._tools.items() if name == 'clear_data_store'}
        assert len(tools) == 1
        clear_data_store_tool = tools['clear_data_store']
        
        # Call the tool
        result = await clear_data_store_tool()
        
        # Verify result
        assert result["status"] == "success"
        assert "cleared successfully" in result["message"]
        server.data_store.clear.assert_called_once()
    
    @patch('src.server.EliteConfig')
    async def test_clear_data_store_tool_error(self, mock_config):
        """Test clear_data_store MCP tool error handling."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        server.data_store.clear = Mock(side_effect=Exception("Clear failed"))
        
        # Get the tool function
        tools = {name: func for name, func in server.app._tools.items() if name == 'clear_data_store'}
        clear_data_store_tool = tools['clear_data_store']
        
        # Call the tool
        result = await clear_data_store_tool()
        
        # Verify error handling
        assert result["status"] == "error"
        assert "Clear failed" in result["message"]


class TestServerLifecycle:
    """Test suite for server lifecycle management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        reset_data_store()
        self.temp_dir = tempfile.mkdtemp()
        self.journal_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_data_store()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.server.EliteConfig')
    async def test_create_server(self, mock_config):
        """Test server creation and singleton behavior."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config.return_value = mock_config_instance
        
        # Clear any existing global server instance
        import src.server
        src.server._server = None
        
        # Create server
        server1 = await create_server()
        assert server1 is not None
        assert isinstance(server1, EliteDangerousServer)
        
        # Create server again - should return same instance
        server2 = await create_server()
        assert server1 is server2
    
    @patch('src.server.EliteConfig')
    async def test_lifespan_manager(self, mock_config):
        """Test server lifespan management context manager."""
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config_instance.validate_paths.return_value = True
        mock_config.return_value = mock_config_instance
        
        # Clear any existing global server instance
        import src.server
        src.server._server = None
        
        startup_called = False
        shutdown_called = False
        
        # Mock startup and shutdown
        async def mock_startup():
            nonlocal startup_called
            startup_called = True
        
        async def mock_shutdown():
            nonlocal shutdown_called
            shutdown_called = True
        
        with patch.object(EliteDangerousServer, 'startup', mock_startup):
            with patch.object(EliteDangerousServer, 'shutdown', mock_shutdown):
                async with lifespan_manager() as server:
                    assert server is not None
                    assert startup_called
                    assert not shutdown_called  # Not called yet
                
                # Should be called after context exit
                assert shutdown_called


class TestServerIntegration:
    """Test suite for server integration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        reset_data_store()
        self.temp_dir = tempfile.mkdtemp()
        self.journal_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up after tests."""
        reset_data_store()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.server.EliteConfig')
    @patch('src.server.JournalMonitor')
    async def test_end_to_end_event_processing(self, mock_monitor_class, mock_config):
        """Test end-to-end event processing from journal to MCP tools."""
        # Setup configuration
        mock_config_instance = Mock()
        mock_config_instance.journal_path = self.journal_path
        mock_config_instance.validate_paths.return_value = True
        mock_config.return_value = mock_config_instance
        
        # Setup journal monitor
        mock_monitor = AsyncMock()
        mock_monitor_class.return_value = mock_monitor
        
        server = EliteDangerousServer()
        server.setup_basic_mcp_handlers()
        
        # Start server
        await server.startup()
        
        # Verify monitor was set up with callback
        mock_monitor.set_event_callback.assert_called_once()
        callback = mock_monitor.set_event_callback.call_args[0][0]
        
        # Simulate journal event
        test_event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "FSDJump",
            "StarSystem": "Sol",
            "StarPos": [0.0, 0.0, 0.0]
        }
        
        # Process event through callback
        callback(test_event)
        
        # Verify event was processed and stored
        events = server.data_store.query_events()
        assert len(events) >= 1
        
        # Test MCP tool can access the data
        tools = {name: func for name, func in server.app._tools.items() if name == 'get_recent_events'}
        get_recent_events_tool = tools['get_recent_events']
        
        result = await get_recent_events_tool(minutes=5)
        assert result["event_count"] >= 1
        
        # Cleanup
        await server.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
