"""
Elite Dangerous Local AI Tie-In MCP Server

Main entry point for the Model Context Protocol server that provides integration
between Elite Dangerous, Claude Desktop, and EDCoPilot.
"""

import asyncio
import logging
import sys
import signal
import os
from pathlib import Path
from typing import Optional, Any, Dict, List
from contextlib import asynccontextmanager

# Add the project root directory to the Python path to fix relative imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to the project directory to ensure relative paths work
os.chdir(project_root)

from mcp.server.fastmcp import FastMCP

# Import modules using try/except to handle both relative and absolute imports
try:
    # Try relative imports first (when run as module)
    from .utils.config import EliteConfig
    from .journal.monitor import JournalMonitor
    from .journal.events import EventProcessor
    from .utils.data_store import get_data_store, reset_data_store
    from .elite_mcp.mcp_tools import MCPTools
    from .elite_mcp.mcp_resources import MCPResources
    from .elite_mcp.mcp_prompts import MCPPrompts
    from .edcopilot.theme_mcp_tools import ThemeMCPTools
except ImportError:
    # Fall back to absolute imports (when run as script)
    from src.utils.config import EliteConfig
    from src.journal.monitor import JournalMonitor
    from src.journal.events import EventProcessor
    from src.utils.data_store import get_data_store, reset_data_store
    from src.elite_mcp.mcp_tools import MCPTools
    from src.elite_mcp.mcp_resources import MCPResources
    from src.elite_mcp.mcp_prompts import MCPPrompts
    from src.edcopilot.theme_mcp_tools import ThemeMCPTools


# Configure logging
# When running as MCP server, avoid stdout logging to prevent JSON protocol interference
if len(sys.argv) > 0 and sys.argv[0].endswith('server.py') and '--mcp' not in sys.argv:
    # Running directly, use both stdout and file logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),  # Use stderr instead of stdout for MCP compatibility
            logging.FileHandler('elite_mcp_server.log')
        ]
    )
else:
    # Running as MCP server, only use file logging to avoid JSON protocol interference
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
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
    
    async def load_historical_data(self, hours_back: int = 24):
        """Load historical journal data from recent files."""
        try:
            logger.info(f"Loading historical data from last {hours_back} hours...")

            from src.journal.parser import JournalParser
            from datetime import datetime, timedelta

            # Initialize journal parser
            journal_parser = JournalParser(self.config.journal_path)

            # Find recent journal files
            all_files = journal_parser.find_journal_files()
            cutoff_time = datetime.now() - timedelta(hours=hours_back)

            recent_files = []
            for file_path in all_files:
                file_timestamp = journal_parser._extract_timestamp_from_filename(file_path)
                if file_timestamp > cutoff_time:
                    recent_files.append(file_path)

            logger.info(f"Found {len(recent_files)} recent journal files to process")

            events_loaded = 0
            for file_path in recent_files:
                try:
                    # Read and process all events from this file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_no, line in enumerate(f, 1):
                            try:
                                # Parse journal entry
                                event_data = journal_parser.parse_journal_entry(line)
                                if event_data:
                                    # Process the event
                                    processed_event = self.event_processor.process_event(event_data)

                                    # Store in data store
                                    self.data_store.store_event(processed_event)
                                    events_loaded += 1

                            except Exception as e:
                                logger.debug(f"Error processing line {line_no} in {file_path.name}: {e}")

                except Exception as e:
                    logger.warning(f"Error reading historical file {file_path.name}: {e}")

            logger.info(f"Loaded {events_loaded} historical events from {len(recent_files)} files")

        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            # Don't raise - this is not critical for server operation

    async def start_journal_monitoring(self):
        """Start journal monitoring in background task."""
        try:
            logger.info("Starting journal monitoring...")

            # Load historical data first
            await self.load_historical_data(hours_back=24)

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
            self.theme_tools = ThemeMCPTools(self.data_store)
            
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

        # ==================== EDCoPilot Integration Tools ====================

        @self.app.tool()
        async def generate_edcopilot_chatter(chatter_type: str = "all") -> Dict[str, Any]:
            """
            Generate EDCoPilot custom chatter files based on current game state.

            Args:
                chatter_type: Type of chatter to generate ("space", "crew", "deepspace", or "all")

            Returns:
                Status of file generation with details
            """
            return self.mcp_tools.generate_edcopilot_chatter(chatter_type)

        @self.app.tool()
        async def get_edcopilot_status() -> Dict[str, Any]:
            """
            Get status of EDCoPilot integration and existing custom files.

            Returns:
                Status of EDCoPilot integration and file information
            """
            return self.mcp_tools.get_edcopilot_status()

        @self.app.tool()
        async def backup_edcopilot_files() -> Dict[str, Any]:
            """
            Create backups of all existing EDCoPilot custom files.

            Returns:
                Status of backup operation
            """
            return self.mcp_tools.backup_edcopilot_files()

        @self.app.tool()
        async def preview_edcopilot_chatter(chatter_type: str = "space") -> Dict[str, Any]:
            """
            Preview EDCoPilot chatter content without writing files.

            Args:
                chatter_type: Type of chatter to preview ("space", "crew", "deepspace")

            Returns:
                Preview of generated chatter content
            """
            return self.mcp_tools.preview_edcopilot_chatter(chatter_type)

        # ==================== Dynamic Theme System Tools ====================

        @self.app.tool()
        async def set_edcopilot_theme(
            theme: str,
            context: str,
            apply_immediately: bool = False
        ) -> Dict[str, Any]:
            """
            Set overall EDCoPilot theme with context for AI-powered dialogue generation.

            Args:
                theme: Theme identifier (e.g., "space pirate", "corporate executive", "military veteran")
                context: Theme context (e.g., "owes debt to Space Mafia", "ambitious trader")
                apply_immediately: Whether to apply theme to current ship immediately

            Returns:
                Theme setting status and next steps guidance
            """
            return await self.theme_tools.set_edcopilot_theme(theme, context, apply_immediately)

        @self.app.tool()
        async def get_theme_status() -> Dict[str, Any]:
            """
            Get current theme system status and configuration.

            Returns:
                Complete theme system status including current themes and ship configurations
            """
            return await self.theme_tools.get_theme_status()

        @self.app.tool()
        async def generate_themed_templates_prompt(
            theme: Optional[str] = None,
            context: Optional[str] = None,
            crew_role: Optional[str] = None,
            ship_name: Optional[str] = None,
            chatter_type: str = "space"
        ) -> Dict[str, Any]:
            """
            Generate AI prompt for Claude Desktop to create themed dialogue templates.

            Args:
                theme: Theme override (uses current theme if None)
                context: Context override (uses current context if None)
                crew_role: Specific crew role for targeted generation
                ship_name: Ship name for context
                chatter_type: Type of chatter ("space", "crew", "deepspace")

            Returns:
                AI prompt and generation instructions for Claude Desktop
            """
            return await self.theme_tools.generate_themed_templates_prompt(
                theme, context, crew_role, ship_name, chatter_type
            )

        @self.app.tool()
        async def apply_generated_templates(
            generated_templates: List[str],
            chatter_type: str = "space",
            ship_name: Optional[str] = None,
            crew_role: Optional[str] = None,
            create_backup: bool = True
        ) -> Dict[str, Any]:
            """
            Validate and apply templates generated by Claude Desktop.

            Args:
                generated_templates: List of template strings from Claude Desktop
                chatter_type: Type of chatter ("space", "crew", "deepspace")
                ship_name: Ship name for ship-specific application
                crew_role: Crew role for role-specific application
                create_backup: Whether to create backup before applying

            Returns:
                Validation results and application status
            """
            return await self.theme_tools.apply_generated_templates(
                generated_templates, chatter_type, ship_name, crew_role, create_backup
            )

        @self.app.tool()
        async def configure_ship_crew(
            ship_name: str,
            crew_roles: Optional[List[str]] = None,
            auto_configure: bool = True
        ) -> Dict[str, Any]:
            """
            Configure crew composition for a specific ship.

            Args:
                ship_name: Name of the ship to configure
                crew_roles: List of crew roles (auto-detected if None)
                auto_configure: Whether to auto-configure based on ship type

            Returns:
                Crew configuration status
            """
            return await self.theme_tools.configure_ship_crew(ship_name, crew_roles, auto_configure)

        @self.app.tool()
        async def set_crew_member_theme(
            ship_name: str,
            crew_role: str,
            theme: str,
            context: str,
            voice_preference: Optional[str] = None,
            personality_traits: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Set theme for individual crew member.

            Args:
                ship_name: Name of the ship
                crew_role: Role of the crew member
                theme: Theme for this crew member
                context: Context for this crew member
                voice_preference: Optional voice preference
                personality_traits: Optional personality traits

            Returns:
                Crew member theme setting status
            """
            return await self.theme_tools.set_crew_member_theme(
                ship_name, crew_role, theme, context, voice_preference, personality_traits
            )

        @self.app.tool()
        async def generate_crew_setup_prompt(
            ship_name: str,
            overall_theme: str,
            overall_context: str,
            crew_roles: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Generate prompt for Claude Desktop to set up multi-crew themes.

            Args:
                ship_name: Name of the ship
                overall_theme: Overall theme for the crew
                overall_context: Overall context for the crew
                crew_roles: List of crew roles (auto-detected if None)

            Returns:
                Crew setup prompt for Claude Desktop
            """
            return await self.theme_tools.generate_crew_setup_prompt(
                ship_name, overall_theme, overall_context, crew_roles
            )

        @self.app.tool()
        async def preview_themed_content(
            theme: Optional[str] = None,
            context: Optional[str] = None,
            crew_role: Optional[str] = None,
            ship_name: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Preview what themed content would look like without applying.

            Args:
                theme: Theme override (uses current theme if None)
                context: Context override (uses current context if None)
                crew_role: Specific crew role for preview
                ship_name: Ship name for context

            Returns:
                Preview content and examples
            """
            return await self.theme_tools.preview_themed_content(theme, context, crew_role, ship_name)

        @self.app.tool()
        async def reset_theme(clear_ship_configs: bool = False) -> Dict[str, Any]:
            """
            Reset theme configuration to defaults.

            Args:
                clear_ship_configs: Whether to clear all ship configurations

            Returns:
                Reset operation status
            """
            return await self.theme_tools.reset_theme(clear_ship_configs)

        @self.app.tool()
        async def backup_current_themes() -> Dict[str, Any]:
            """
            Create backup of current theme configuration.

            Returns:
                Backup operation status
            """
            return await self.theme_tools.backup_current_themes()
    
    def setup_mcp_resources(self):
        """Set up MCP resource handlers for structured data access."""
        
        @self.app.tool()
        async def list_available_resources() -> Dict[str, Any]:
            """List all available MCP resources with metadata."""
            try:
                resources = self.mcp_resources.list_resources()
                return {
                    "available_resources": resources,
                    "total_count": len(resources),
                    "resource_types": list(set(r.get("type", "unknown") for r in resources))
                }
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return {"error": str(e)}
        
        @self.app.tool()
        async def get_resource_data(uri: str) -> Dict[str, Any]:
            """
            Get resource data for the specified URI.
            
            Args:
                uri: Resource URI with optional query parameters (e.g., 'elite://status/current')
                
            Returns:
                Resource data or error message
            """
            try:
                resource_data = await self.mcp_resources.get_resource(uri)
                if resource_data is None:
                    return {"error": f"Resource not found: {uri}"}
                return {
                    "uri": uri,
                    "data": resource_data,
                    "timestamp": resource_data.get("timestamp") if isinstance(resource_data, dict) else None
                }
            except Exception as e:
                logger.error(f"Error getting resource {uri}: {e}")
                return {"error": str(e)}
        
        @self.app.tool()
        async def refresh_resource_cache() -> Dict[str, str]:
            """Clear the resource cache to force fresh data retrieval."""
            try:
                await self.mcp_resources.clear_cache()
                return {"status": "success", "message": "Resource cache cleared successfully"}
            except Exception as e:
                logger.error(f"Error clearing resource cache: {e}")
                return {"status": "error", "message": str(e)}
        
        logger.info(f"Registered {len(self.mcp_resources.resources)} MCP resources as tools")

    def setup_mcp_prompts(self):
        """Set up MCP prompt handlers for context-aware AI assistance."""
        
        @self.app.tool()
        async def list_available_prompts() -> Dict[str, Any]:
            """List all available prompt templates with descriptions and metadata."""
            try:
                prompts = self.mcp_prompts.list_available_prompts()
                return {
                    "available_prompts": prompts,
                    "total_count": len(prompts),
                    "prompt_types": list(set(p["type"] for p in prompts))
                }
            except Exception as e:
                logger.error(f"Error listing prompts: {e}")
                return {"error": str(e)}
        
        @self.app.tool()
        async def generate_analysis_prompt(
            analysis_type: str,
            time_range_hours: int = 24
        ) -> Dict[str, Any]:
            """
            Generate a context-aware analysis prompt for Elite Dangerous activities.
            
            Args:
                analysis_type: Type of analysis - exploration, trading, combat, mining, missions, engineering, journey, performance, strategic
                time_range_hours: Time range to analyze in hours (default 24)
            """
            try:
                # Map analysis types to template IDs
                template_mapping = {
                    "exploration": "exploration_analysis",
                    "trading": "trading_strategy", 
                    "combat": "combat_assessment",
                    "mining": "mining_optimization",
                    "missions": "mission_guidance",
                    "engineering": "engineering_progress",
                    "journey": "journey_review",
                    "performance": "performance_review",
                    "strategic": "strategic_planning",
                    "strategy": "strategic_planning"
                }
                
                template_id = template_mapping.get(analysis_type.lower())
                if not template_id:
                    available_types = ", ".join(template_mapping.keys())
                    return {
                        "error": f"Invalid analysis type: {analysis_type}",
                        "available_types": available_types
                    }
                
                # Generate the prompt
                prompt = await self.mcp_prompts.generate_prompt(template_id, time_range_hours)
                
                return {
                    "analysis_type": analysis_type,
                    "time_range_hours": time_range_hours,
                    "prompt": prompt,
                    "template_id": template_id
                }
                
            except Exception as e:
                logger.error(f"Error generating analysis prompt: {e}")
                return {"error": str(e)}
        
        @self.app.tool()
        async def generate_exploration_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware exploration analysis prompt."""
            return await self.generate_analysis_prompt("exploration", time_range_hours)
        
        @self.app.tool()
        async def generate_trading_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware trading strategy prompt."""
            return await self.generate_analysis_prompt("trading", time_range_hours)
        
        @self.app.tool()
        async def generate_combat_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware combat assessment prompt."""
            return await self.generate_analysis_prompt("combat", time_range_hours)
        
        @self.app.tool()
        async def generate_mining_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware mining optimization prompt."""
            return await self.generate_analysis_prompt("mining", time_range_hours)
        
        @self.app.tool()
        async def generate_mission_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware mission guidance prompt."""
            return await self.generate_analysis_prompt("missions", time_range_hours)
        
        @self.app.tool()
        async def generate_engineering_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware engineering progress prompt."""
            return await self.generate_analysis_prompt("engineering", time_range_hours)
        
        @self.app.tool()
        async def generate_journey_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware journey review prompt."""
            return await self.generate_analysis_prompt("journey", time_range_hours)
        
        @self.app.tool()
        async def generate_performance_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware performance review prompt."""
            return await self.generate_analysis_prompt("performance", time_range_hours)
        
        @self.app.tool()
        async def generate_strategic_prompt(time_range_hours: int = 24) -> Dict[str, Any]:
            """Generate context-aware strategic planning prompt."""
            return await self.generate_analysis_prompt("strategic", time_range_hours)
        
        @self.app.tool()
        async def generate_custom_prompt(
            template_id: str,
            time_range_hours: int = 24
        ) -> Dict[str, Any]:
            """
            Generate a prompt using a specific template ID.
            
            Args:
                template_id: Specific template identifier
                time_range_hours: Time range to analyze in hours
            """
            try:
                available_templates = list(self.mcp_prompts.templates.keys())
                if template_id not in available_templates:
                    return {
                        "error": f"Invalid template ID: {template_id}",
                        "available_templates": available_templates
                    }
                
                prompt = await self.mcp_prompts.generate_prompt(template_id, time_range_hours)
                
                return {
                    "template_id": template_id,
                    "time_range_hours": time_range_hours,
                    "prompt": prompt
                }
                
            except Exception as e:
                logger.error(f"Error generating custom prompt: {e}")
                return {"error": str(e)}
        
        logger.info(f"Registered {len(self.mcp_prompts.templates)} MCP prompt templates")


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
        # Create and set up the server
        server = await create_server()

        # Start server components but don't run the app yet
        await server.startup()

        try:
            # Run the MCP server - this will handle its own event loop
            await server.app.run()
        finally:
            # Clean shutdown
            await server.shutdown()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise  # Re-raise instead of sys.exit to avoid issues in MCP context


def run_server():
    """Convenience function to run the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


# For FastMCP servers, we need to run the app directly without asyncio wrappers
async def run_mcp_server():
    """Run the FastMCP server directly."""
    server = await create_server()
    await server.startup()
    try:
        await server.app.run()
    finally:
        await server.shutdown()

def main():
    """Main server entry point."""
    # Setup asyncio for our background tasks
    async def setup_server():
        server = await create_server()
        await server.startup()
        return server

    # Create and start the server components in asyncio context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        server = loop.run_until_complete(setup_server())

        # Now run FastMCP in the main thread
        # This will handle MCP protocol on stdin/stdout
        server.app.run()

    finally:
        # Cleanup
        async def cleanup():
            await server.shutdown()
        loop.run_until_complete(cleanup())
        loop.close()

if __name__ == "__main__":
    try:
        logger.info("Starting Elite Dangerous MCP Server...")
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
