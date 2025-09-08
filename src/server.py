"""
Elite Dangerous Local AI Tie-In MCP Server

Main entry point for the Model Context Protocol server that provides integration
between Elite Dangerous, Claude Desktop, and EDCoPilot.
"""

import asyncio
import logging
import sys
import signal
from typing import Optional, Any, Dict
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from .utils.config import EliteConfig
from .journal.monitor import JournalMonitor
from .journal.events import EventProcessor
from .utils.data_store import get_data_store, reset_data_store


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('elite_mcp_server.log')
    ]
)

logger = logging.getLogger(__name__)


class EliteDangerousServer:
    """
    MCP server for Elite Dangerous integration.
    
    Provides real-time journal monitoring, event processing, and data storage
    with MCP protocol support for AI assistant integration.
    """
    
    def __init__(self):
        """Initialize the MCP server with configuration and components."""
        logger.info("Initializing Elite Dangerous MCP Server")
        
        # Initialize configuration
        try:
            self.config = EliteConfig()
            logger.info(f"Configuration loaded: journal_path={self.config.journal_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
        
        # Initialize MCP server
        self.app = FastMCP("Elite Dangerous MCP Server", version="1.0.0")
        
        # Initialize components
        self.journal_monitor: Optional[JournalMonitor] = None
        self.event_processor = EventProcessor()
        self.data_store = get_data_store()
        
        # Server state
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        logger.info("Server initialization completed")
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_journal_monitoring(self):
        """Start journal monitoring in background task."""
        try:
            logger.info("Starting journal monitoring...")
            
            # Initialize journal monitor
            self.journal_monitor = JournalMonitor()
            
            # Set up event callback to process and store events
            def on_journal_event(event_data: Dict[str, Any]):
                try:
                    # Process the event
                    processed_event = self.event_processor.process_event(event_data)
                    
                    # Store in data store
                    self.data_store.store_event(processed_event)
                    
                    logger.debug(f"Processed and stored event: {processed_event.event_type}")
                    
                except Exception as e:
                    logger.error(f"Error processing journal event: {e}")
            
            self.journal_monitor.set_event_callback(on_journal_event)
            
            # Start monitoring
            await self.journal_monitor.start()
            logger.info("Journal monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start journal monitoring: {e}")
            raise
    
    async def stop_journal_monitoring(self):
        """Stop journal monitoring gracefully."""
        if self.journal_monitor:
            try:
                logger.info("Stopping journal monitoring...")
                await self.journal_monitor.stop()
                logger.info("Journal monitoring stopped")
            except Exception as e:
                logger.error(f"Error stopping journal monitoring: {e}")
    
    async def monitor_background_task(self):
        """Background task for journal monitoring."""
        try:
            await self.start_journal_monitoring()
            
            # Keep monitoring while server is running
            while self._running:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("Background monitoring task cancelled")
        except Exception as e:
            logger.error(f"Background monitoring task error: {e}")
        finally:
            await self.stop_journal_monitoring()
    
    async def startup(self):
        """Server startup procedures."""
        logger.info("Starting Elite Dangerous MCP Server...")
        
        try:
            # Validate configuration
            if not self.config.validate_paths():
                logger.warning("Configuration validation failed - some paths may not exist")
            
            # Clear any existing data store state
            reset_data_store()
            self.data_store = get_data_store()
            
            # Set running flag
            self._running = True
            
            # Start background monitoring
            self._monitor_task = asyncio.create_task(self.monitor_background_task())
            
            logger.info("Server startup completed successfully")
            
        except Exception as e:
            logger.error(f"Server startup failed: {e}")
            raise
    
    async def shutdown(self):
        """Server shutdown procedures."""
        logger.info("Shutting down Elite Dangerous MCP Server...")
        
        try:
            # Stop running
            self._running = False
            
            # Cancel and wait for background task
            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Stop journal monitoring
            await self.stop_journal_monitoring()
            
            # Clear data store
            self.data_store.clear()
            
            logger.info("Server shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during server shutdown: {e}")
    
    def setup_basic_mcp_handlers(self):
        """Set up basic MCP handlers for server functionality."""
        
        @self.app.tool()
        async def server_status() -> Dict[str, Any]:
            """Get current server status and statistics."""
            try:
                stats = self.data_store.get_statistics()
                game_state = self.data_store.get_game_state()
                
                return {
                    "server_running": self._running,
                    "journal_monitoring": self.journal_monitor is not None,
                    "data_store_stats": stats,
                    "current_system": game_state.current_system,
                    "current_ship": game_state.current_ship,
                    "docked": game_state.docked,
                    "last_updated": game_state.last_updated.isoformat() if game_state.last_updated else None
                }
            except Exception as e:
                logger.error(f"Error getting server status: {e}")
                return {"error": str(e)}
        
        @self.app.tool()
        async def get_recent_events(minutes: int = 60) -> Dict[str, Any]:
            """Get recent journal events from the specified time period."""
            try:
                if minutes <= 0 or minutes > 1440:  # Max 24 hours
                    return {"error": "Invalid minutes parameter (must be 1-1440)"}
                
                events = self.data_store.get_recent_events(minutes=minutes)
                
                return {
                    "event_count": len(events),
                    "time_period_minutes": minutes,
                    "events": [
                        {
                            "timestamp": event.timestamp.isoformat(),
                            "event_type": event.event_type,
                            "category": event.category.value,
                            "summary": event.summary
                        }
                        for event in events
                    ]
                }
            except Exception as e:
                logger.error(f"Error getting recent events: {e}")
                return {"error": str(e)}
        
        @self.app.tool()
        async def clear_data_store() -> Dict[str, str]:
            """Clear all stored journal events and reset game state."""
            try:
                self.data_store.clear()
                logger.info("Data store cleared by user request")
                return {"status": "success", "message": "Data store cleared successfully"}
            except Exception as e:
                logger.error(f"Error clearing data store: {e}")
                return {"status": "error", "message": str(e)}


# Global server instance
_server: Optional[EliteDangerousServer] = None


async def create_server() -> EliteDangerousServer:
    """Create and configure the MCP server instance."""
    global _server
    
    if _server is None:
        _server = EliteDangerousServer()
        _server.setup_basic_mcp_handlers()
        _server.setup_signal_handlers()
    
    return _server


@asynccontextmanager
async def lifespan_manager():
    """Manage server lifecycle with proper startup and shutdown."""
    server = await create_server()
    
    try:
        await server.startup()
        yield server
    finally:
        await server.shutdown()


async def main():
    """Main entry point for the MCP server."""
    try:
        async with lifespan_manager() as server:
            # Run the MCP server
            await server.app.run()
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def run_server():
    """Convenience function to run the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
