"""
Elite Dangerous Local AI Tie-In MCP Server

Main entry point for the Model Context Protocol server that provides integration
between Elite Dangerous, Claude Desktop, and EDCoPilot.
"""

import asyncio
import logging
import sys
import signal
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from .utils.config import EliteConfig
from .journal.monitor import JournalMonitor
from .journal.events import EventProcessor
from .utils.data_store import get_data_store, reset_data_store
from .mcp.mcp_tools import MCPTools
from .mcp.mcp_resources import MCPResources
from .mcp.mcp_prompts import MCPPrompts, PromptType


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
        self.app = FastMCP("Elite Dangerous MCP Server")
        
        # Initialize components
        self.journal_monitor: Optional[JournalMonitor] = None
        self.event_processor = EventProcessor()
        self.data_store = get_data_store()
        self.mcp_tools = MCPTools(self.data_store)
        self.mcp_resources = MCPResources(self.data_store)
        self.mcp_prompts = MCPPrompts(self.data_store)
        
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
            
            # Set up event callback to process and store events
            def on_journal_event(event_data_list, event_type: str):
                try:
                    for event_data in event_data_list:
                        # Process the event
                        processed_event = self.event_processor.process_event(event_data)
                        
                        # Store in data store
                        self.data_store.store_event(processed_event)
                        
                        logger.debug(f"Processed and stored event: {processed_event.event_type}")
                        
                except Exception as e:
                    logger.error(f"Error processing journal event: {e}")
            
            # Initialize journal monitor with required parameters
            self.journal_monitor = JournalMonitor(
                journal_path=self.config.journal_path,
                event_callback=on_journal_event
            )
            
            # Start monitoring
            started = await self.journal_monitor.start_monitoring()
            if not started:
                raise Exception("Journal monitoring failed to start")
                
            logger.info("Journal monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start journal monitoring: {e}")
            raise
    
    async def stop_journal_monitoring(self):
        """Stop journal monitoring gracefully."""
        if self.journal_monitor:
            try:
                logger.info("Stopping journal monitoring...")
                await self.journal_monitor.stop_monitoring()
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
            self.mcp_tools = MCPTools(self.data_store)
            self.mcp_resources = MCPResources(self.data_store)
            self.mcp_prompts = MCPPrompts(self.data_store)
            
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
            
            # Clear resource cache
            await self.mcp_resources.clear_cache()
            
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
    
    def setup_core_mcp_handlers(self):
        """Set up core MCP handlers for comprehensive data access."""
        
        # ==================== Location and Status Tools ====================
        
        @self.app.tool()
        async def get_current_location() -> Dict[str, Any]:
            """Get comprehensive current location information including system, station, and nearby systems."""
            return await self.mcp_tools.get_current_location()
        
        @self.app.tool()
        async def get_ship_status() -> Dict[str, Any]:
            """Get comprehensive ship status including type, modules, and condition."""
            return await self.mcp_tools.get_ship_status()
        
        # ==================== Event Search Tools ====================
        
        @self.app.tool()
        async def search_events(
            event_types: Optional[List[str]] = None,
            categories: Optional[List[str]] = None,
            time_range_minutes: Optional[int] = None,
            system_names: Optional[List[str]] = None,
            contains_text: Optional[str] = None,
            max_results: int = 100
        ) -> Dict[str, Any]:
            """
            Search for events with flexible filtering criteria.
            
            Args:
                event_types: List of event types to filter (e.g., ["FSDJump", "Docked"])
                categories: List of categories to filter (e.g., ["exploration", "combat"])
                time_range_minutes: Time range in minutes from now (e.g., 60 for last hour)
                system_names: Filter by system names (e.g., ["Sol", "Alpha Centauri"])
                contains_text: Text search in event data
                max_results: Maximum number of results to return (default 100)
            """
            return await self.mcp_tools.search_events(
                event_types=event_types,
                categories=categories,
                time_range_minutes=time_range_minutes,
                system_names=system_names,
                contains_text=contains_text,
                max_results=max_results
            )
        
        # ==================== Activity Summary Tools ====================
        
        @self.app.tool()
        async def get_activity_summary(
            activity_type: str,
            time_range_hours: int = 24
        ) -> Dict[str, Any]:
            """
            Get comprehensive summary of specific activity type.
            
            Args:
                activity_type: Type of activity - exploration, trading, combat, mining, missions, or engineering
                time_range_hours: Time range to analyze in hours (default 24)
            """
            return await self.mcp_tools.get_activity_summary(
                activity_type=activity_type,
                time_range_hours=time_range_hours
            )
        
        @self.app.tool()
        async def get_exploration_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """Get detailed exploration activity summary including scans, discoveries, and earnings."""
            return await self.mcp_tools.get_activity_summary("exploration", time_range_hours)
        
        @self.app.tool()
        async def get_trading_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """Get detailed trading activity summary including profits, commodities, and best trades."""
            return await self.mcp_tools.get_activity_summary("trading", time_range_hours)
        
        @self.app.tool()
        async def get_combat_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """Get detailed combat activity summary including bounties, kills, and combat bonds."""
            return await self.mcp_tools.get_activity_summary("combat", time_range_hours)
        
        @self.app.tool()
        async def get_mining_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """Get detailed mining activity summary including materials mined and asteroids cracked."""
            return await self.mcp_tools.get_activity_summary("mining", time_range_hours)
        
        @self.app.tool()
        async def get_mission_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """Get detailed mission activity summary including active and completed missions."""
            return await self.mcp_tools.get_activity_summary("missions", time_range_hours)
        
        @self.app.tool()
        async def get_engineering_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """Get detailed engineering activity summary including modifications and engineers visited."""
            return await self.mcp_tools.get_activity_summary("engineering", time_range_hours)
        
        # ==================== Journey and Navigation Tools ====================
        
        @self.app.tool()
        async def get_journey_summary(time_range_hours: int = 24) -> Dict[str, Any]:
            """
            Get comprehensive journey and navigation summary.
            
            Includes total jumps, distance traveled, systems visited, and route map.
            """
            return await self.mcp_tools.get_journey_summary(time_range_hours)
        
        # ==================== Performance and Statistics Tools ====================
        
        @self.app.tool()
        async def get_performance_metrics(time_range_hours: int = 24) -> Dict[str, Any]:
            """
            Get comprehensive performance metrics across all activities.
            
            Includes credits earned/spent, efficiency metrics, and achievements.
            """
            return await self.mcp_tools.get_performance_metrics(time_range_hours)
        
        # ==================== Specialized Query Tools ====================
        
        @self.app.tool()
        async def get_faction_standings() -> Dict[str, Any]:
            """Get current faction standings and reputation changes."""
            return await self.mcp_tools.get_faction_standings()
        
        @self.app.tool()
        async def get_material_inventory() -> Dict[str, Any]:
            """Get current material and cargo inventory with recent changes."""
            return await self.mcp_tools.get_material_inventory()
    
    def setup_mcp_resources(self):
        """Set up MCP resource handlers for structured data access."""
        
        @self.app.resource()
        async def list_resources() -> List[Dict[str, Any]]:
            """List all available MCP resources with metadata."""
            return self.mcp_resources.list_resources()
        
        @self.app.resource()
        async def get_resource(uri: str) -> Optional[Dict[str, Any]]:
            """
            Get resource data for the specified URI.
            
            Args:
                uri: Resource URI with optional query parameters
                
            Returns:
                Resource data or None if invalid URI
            """
            return await self.mcp_resources.get_resource(uri)
        
        @self.app.tool()
        async def refresh_resource_cache() -> Dict[str, str]:
            """Clear the resource cache to force fresh data retrieval."""
            try:
                await self.mcp_resources.clear_cache()
                return {"status": "success", "message": "Resource cache cleared successfully"}
            except Exception as e:
                logger.error(f"Error clearing resource cache: {e}")
                return {"status": "error", "message": str(e)}
        
        logger.info(f"Registered {len(self.mcp_resources.resources)} MCP resources")
    
    def setup_mcp_prompts(self):
        """Set up MCP prompt handlers for context-aware AI assistance."""
        
        @self.app.prompt()
        async def list_prompts() -> List[Dict[str, Any]]:
            """List all available prompt templates with metadata."""
            return self.mcp_prompts.list_prompts()
        
        @self.app.prompt()
        async def generate_prompt(
            prompt_name: str,
            custom_context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Generate a specific prompt with current game context.
            
            Args:
                prompt_name: Name of the prompt template
                custom_context: Optional custom context values to override defaults
                
            Returns:
                Generated prompt with metadata and context
            """
            return self.mcp_prompts.generate_prompt(prompt_name, custom_context)
        
        @self.app.prompt()
        async def generate_contextual_prompt(
            prompt_type: str,
            time_range_hours: int = 24
        ) -> Dict[str, Any]:
            """
            Generate the most relevant prompt for the specified type based on current context.
            
            Args:
                prompt_type: Type of prompt (exploration, trading, combat, mining, navigation, 
                           engineering, missions, performance, strategy, roleplay)
                time_range_hours: Time range for activity analysis (default 24)
                
            Returns:
                Generated prompt adapted to recent activity
            """
            try:
                # Convert string to PromptType enum
                prompt_type_enum = PromptType(prompt_type.lower())
                return self.mcp_prompts.generate_contextual_prompt(prompt_type_enum, time_range_hours)
            except ValueError:
                return {
                    "error": f"Invalid prompt type: {prompt_type}",
                    "valid_types": [t.value for t in PromptType]
                }
        
        @self.app.prompt()
        async def generate_adaptive_prompts(count: int = 3) -> List[Dict[str, Any]]:
            """
            Generate multiple adaptive prompts based on current game state and recent activity.
            
            Args:
                count: Number of prompts to generate (default 3)
                
            Returns:
                List of contextually relevant prompts
            """
            return self.mcp_prompts.generate_adaptive_prompts(count)
        
        @self.app.tool()
        async def analyze_activity_for_prompts() -> Dict[str, Any]:
            """
            Analyze recent activity to determine which prompt types would be most relevant.
            
            Returns:
                Analysis of recent activity with recommended prompt types
            """
            try:
                # Get activity analysis
                prompt_types = self.mcp_prompts._analyze_recent_activity()
                
                # Get recent event distribution
                recent_events = self.data_store.get_recent_events(minutes=120)
                category_counts = {}
                for event in recent_events:
                    cat = event.category.value
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                
                return {
                    "recommended_prompt_types": [pt.value for pt in prompt_types[:5]],
                    "recent_activity_distribution": category_counts,
                    "total_recent_events": len(recent_events),
                    "analysis_time_range_minutes": 120
                }
            except Exception as e:
                logger.error(f"Error analyzing activity: {e}")
                return {"error": str(e)}
        
        logger.info(f"Registered {len(self.mcp_prompts.templates)} prompt templates")


# Global server instance
_server: Optional[EliteDangerousServer] = None


async def create_server() -> EliteDangerousServer:
    """Create and configure the MCP server instance."""
    global _server
    
    if _server is None:
        _server = EliteDangerousServer()
        _server.setup_basic_mcp_handlers()
        _server.setup_core_mcp_handlers()  # Add core MCP tools
        _server.setup_mcp_resources()  # Add MCP resources
        _server.setup_mcp_prompts()  # Add MCP prompts
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
